"""Apply the user's .28 editing maps, preserving IDs except fully erased tiles.

State colours are authoritative. Reconcile competing province geometry within
each state; detached pieces and new narrow scraps join bordering provinces.
All processing is offline. No province receives a population field.
"""
from pathlib import Path
from collections import Counter,defaultdict
import copy,json,math,shutil
import numpy as np
from PIL import Image
from scipy.ndimage import find_objects,label,distance_transform_edt,binary_dilation,binary_opening
from scipy.spatial import cKDTree
R=Path(__file__).resolve().parents[1];D=R/'tools/cartography/edits_0229';W,H=16384,8192
AREA=(6371.0088*2*np.pi/W)*(6371.0088*np.pi/H)*np.cos((np.arange(H)+.5)/H*np.pi-np.pi/2)
Image.MAX_IMAGE_PIXELS=None
def read(n):return json.loads((R/n).read_text())
def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def save_png(path,rgb):
 temp=path.with_suffix('.prepare.png');Image.fromarray(rgb).save(temp)
 with Image.open(temp)as im:
  im.load();assert np.array_equal(np.asarray(im),rgb)
 temp.replace(path)
def allocate(total,weights):
 weights=np.asarray(weights,float);exact=weights/weights.sum()*int(total);v=np.floor(exact).astype(np.int64);v[np.argsort(-(exact-v),kind='stable')[:int(total-v.sum())]]+=1;return v
def transport(rows,cols):
 """Integer table with exact source category and destination resident totals."""
 rows=np.array(rows,np.int64);cols=np.array(cols,np.int64);assert rows.sum()==cols.sum()
 if not rows.sum():return np.zeros((len(rows),len(cols)),np.int64)
 exact=np.outer(rows.astype(float),cols)/rows.sum();out=np.floor(exact).astype(np.int64);rd=rows-out.sum(1);cd=cols-out.sum(0)
 for flat in np.argsort(-(exact-out).ravel(),kind='stable'):
  i,j=np.unravel_index(flat,out.shape)
  if rd[i]>0 and cd[j]>0:out[i,j]+=1;rd[i]-=1;cd[j]-=1
 while rd.any():
  available=(rd[:,None]>0)&(cd[None,:]>0)
  score=np.where(available,exact-out,-np.inf);i,j=np.unravel_index(np.argmax(score),out.shape)
  assert available[i,j];out[i,j]+=1;rd[i]-=1;cd[j]-=1
 assert not rd.any() and not cd.any();return out
def repair(cell,mask,lock,edited):
 """Repair within each original land component; retain real island groups."""
 structure=np.array([[0,1,0],[1,1,1],[0,1,0]],bool)
 islands,_=label(mask,structure);changed=0
 for iteration in range(12):
  did=0
  for pid in np.unique(cell[mask]):
   if not pid:continue
   yy,xx=np.nonzero(cell==pid);t,b=max(0,yy.min()-1),min(cell.shape[0],yy.max()+2);l,r=max(0,xx.min()-1),min(cell.shape[1],xx.max()+2)
   sub=cell[t:b,l:r];part=sub==pid;components,n=label(part,structure)
   best={}
   for c in range(1,n+1):
    sel=components==c;island=int(islands[t:b,l:r][sel][0]);size=int(sel.sum());anchored=bool(np.any(lock[t:b,l:r][sel]==pid));score=(anchored,size)
    if island not in best or score>best[island][0]:best[island]=(score,c)
   keep={v[1]for v in best.values()}
   for c in range(1,n+1):
    if c in keep:continue
    fragment=components==c;ring=binary_dilation(fragment,structure)&~fragment
    ns=sub[ring&mask[t:b,l:r]];ns=ns[(ns>0)&(ns!=pid)]
    if not ns.size:continue
    vals,cnts=np.unique(ns,return_counts=True);dest=int(vals[np.argmax(cnts)]);sub[fragment]=dest;did+=int(fragment.sum())
  changed+=did
  if not did:break
 # Remove small new one-pixel peninsulas at changed state/province edges,
 # retaining every province's interior anchor and natural coast exceptions.
 near=binary_dilation(edited,structure,iterations=2)
 for pid in np.unique(cell[mask]):
  part=cell==pid
  if not np.any(part&near):continue
  core=binary_opening(part,structure);scraps=part&~core&near
  pieces,n=label(scraps,structure)
  for c in range(1,n+1):
   piece=pieces==c
   if piece.sum()>6 or np.any(lock[piece]==pid):continue
   # A coastal/island narrow feature is geography, not a fitting sliver.
   ring=binary_dilation(piece,structure)&~piece
   if np.any(ring&~mask):continue
   ns=cell[ring];ns=ns[(ns>0)&(ns!=pid)]
   if not ns.size:continue
   vals,cnts=np.unique(ns,return_counts=True);dest=int(vals[np.argmax(cnts)])
   trial=part&~piece
   if label(trial,structure)[1]>label(part,structure)[1]:continue
   cell[piece]=dest;changed+=int(piece.sum())
 return cell,changed
def demographics(w,sd,oldw,olds,states):
 rt=json.loads((D/'runtime_before.json').read_text());flows=defaultdict(Counter);transfer=Counter()
 for top in range(0,H,128):
  a,b=olds[top:top+128],states[top:top+128];m=(a!=b)&(a>0)&(a!=65535)&(b>0)&(b!=65535)
  yy,xx=np.nonzero(m);code=a[m].astype(np.uint32)*65536+b[m];v,inv=np.unique(code,return_inverse=True);areas=np.bincount(inv,weights=AREA[top+yy])
  for c,area in zip(v,areas):transfer[divmod(int(c),65536)]+=float(area)
 affected={x for pair in transfer for x in pair};totals=np.zeros(65536)
 for top in range(0,H,128):totals+=np.bincount(olds[top:top+128].ravel(),weights=np.broadcast_to(AREA[top:top+128,None],olds[top:top+128].shape).ravel(),minlength=65536)
 for sid in affected:
  destinations={b:area for (a,b),area in transfer.items()if a==sid};destinations[sid]=max(0,totals[sid]-sum(destinations.values()));ids=sorted(destinations);nums=allocate(oldw['regions'][str(sid)]['population'],[destinations[i]for i in ids])
  for i,n in zip(ids,nums):flows[sid][i]=int(n)
 sums={sid:{'pop':0,'bands':np.zeros(4,np.int64),'single':np.zeros(101),'religion':Counter(),'education':Counter(),'work':np.zeros(3,np.int64)}for sid in affected}
 expected={}
 for sid in sorted(affected):
  p=sd['states'][str(sid)];m=rt['states'][str(sid)];total=oldw['regions'][str(sid)]['population'];ids=sorted(flows[sid]);cols=[flows[sid][i]for i in ids]
  ac=m['metrics']['age']['counts'];adult=int(m['metrics']['education']['denominator']);bands=[int(ac['Underage']),total-int(ac['Underage'])-adult,adult-int(ac['Retired']),int(ac['Retired'])];bt=transport(bands,cols)
  rc=m['metrics']['religion']['counts'];rk=sorted(rc);relig=transport([int(rc[k])for k in rk],cols)
  ec=m['metrics']['education']['counts'];ek=sorted(ec);edu=transport([int(ec[k])for k in ek],bt[2]+bt[3])
  wc=m['workforce'];work=transport([int(wc[k])for k in ['employed','unemployed','outside_labour_force']],bt[1]+bt[2])
  for j,dest in enumerate(ids):
   target=sums[dest];target['pop']+=cols[j];target['bands']+=bt[:,j];target['work']+=work[:,j];target['religion'].update({k:int(relig[i,j])for i,k in enumerate(rk)});target['education'].update({k:int(edu[i,j])for i,k in enumerate(ek)})
   singles=np.array(p['age_single_year'],float)
   for i,(lo,hi)in enumerate([(0,18),(18,25),(25,65),(65,101)]):
    sub=singles[lo:hi];target['single'][lo:hi]+=sub/max(sub.sum(),1e-30)*bt[i,j]
 for sid,target in sums.items():
  total=target['pop'];p=sd['states'][str(sid)];s=w['regions'][str(sid)];oldpop=oldw['regions'][str(sid)]['population'];bands=target['bands'];adult=int(bands[2]+bands[3]);working=int(bands[1]+bands[2]);employed,unemployed,inactive=map(int,target['work']);labour=employed+unemployed
  if flows[sid]==Counter({sid:oldpop}) and not any(flows[other].get(sid,0)for other in affected if other!=sid):continue
  p['age_single_year']=(target['single']/total).tolist()if total else p['age_single_year'];p['adult25_share']=adult/max(total,1);p['population_2000']=total;p['population_source']='Conserved .28 residents; edited-boundary transfers estimated from source-state land area'
  for kind,counts,denom in [('religion',target['religion'],total),('education',target['education'],adult)]:
   p['metrics'][kind]['shares']={k:v/max(denom,1)for k,v in counts.items()};p['metrics'][kind].update(source='Conserved source-state demographic counts; edited-boundary area estimate',status='Year-2000 modeled transfer; no new census measurement',reference='data/map_edit_audit_0229.json')
  p['metrics']['age']['shares']={'Underage':int(bands[0])/max(total,1),'Working age':working/max(total,1),'Retired':int(bands[3])/max(total,1)}
  p['workforce'].update(participation_rate=labour/max(working,1),unemployment_rate=unemployed/max(labour,1),source='Conserved source-state workforce counts across edited boundaries')
  p.pop('merge_audit',None);s.update(population=total,population_source=p['population_source'],workforce=copy.deepcopy(p['workforce']))
  expected[str(sid)]={'population':total,'age':{'Underage':int(bands[0]),'Working age':working,'Retired':int(bands[3])},'religion':dict(target['religion']),'education':dict(target['education']),'adult25':adult,'workforce':{'working_age':working,'labour_force':labour,'employed':employed,'unemployed':unemployed,'outside_labour_force':inactive}}
 return {'transferred_land_km2':[{'from':a,'to':b,'area_km2':round(area,4),'residents':flows[a][b]}for (a,b),area in sorted(transfer.items())],'expected_demographics':expected}
def main():
 w,ps,sd=map(read,['data/world.json','data/provinces.json','data/state_demographics.json']);assert w['version']=='0.2.0.28';oldw=copy.deepcopy(w);oldps=copy.deepcopy(ps)
 B=D/'baseline';B.mkdir(exist_ok=True)
 for n in ['world','provinces','state_demographics','cities','urban_scenery','urban_population','sea_regions']:
  shutil.copy2(R/f'data/{n}.json',B/f'{n}.json')
 a=np.zeros((H,W),np.uint16);states=a.copy();olda=a.copy();olds=a.copy();edited=np.zeros((H,W),bool)
 for i in range(4):
  d=np.load(D/f'tile_{i}.npz');t,l=i//2*4096,i%2*8192;bb=np.s_[t:t+4096,l:l+8192];a[bb]=d['provinces'];states[bb]=d['states'];olda[bb]=d['old_provinces'];olds[bb]=d['old_states'];edited[bb]=(a[bb]!=olda[bb])|(states[bb]!=olds[bb])
 # This edit set preserves every coast pixel. Future coastline edits require
 # an explicit precedence decision and sea/terrain consistency reconciliation.
 assert np.array_equal(a>0,olda>0)and np.array_equal(states>0,olds>0)
 lut=np.zeros(65536,np.uint16);lut[65535]=65535
 removed=sorted(set(map(int,oldps))-set(map(int,np.unique(a))))
 assert removed==[10465,12585]
 for pid in removed:del ps[str(pid)]
 overlaps=Counter()
 for top in range(0,H,128):
  p,s=a[top:top+128],states[top:top+128];m=(p>0)&(p!=65535);v,c=np.unique(p[m].astype(np.uint32)*65536+s[m],return_counts=True);overlaps.update({divmod(int(x),65536):int(y)for x,y in zip(v,c)})
 bypid=defaultdict(list)
 for (pid,sid),n in overlaps.items():bypid[pid].append((n,sid))
 membership=[]
 for k,p in ps.items():
  pid=int(k);sid=max(bypid[pid],key=lambda x:(x[0],x[1]==p['region']))[1];assert str(sid)in w['regions'];lut[pid]=sid
  if sid!=p['region']:membership.append({'province':pid,'from':p['region'],'to':sid});p['region']=sid
 valid=(lut[a]==states)&(a>0);a[~valid]=0;a[states==65535]=65535
 boxes=find_objects(states,max_label=65535);repair_rows=[]
 touched=(set(map(int,np.unique(states[edited])))|set(map(int,np.unique(olds[edited]))))-{0,65535}
 for sid in sorted(touched):
  bb=boxes[sid-1];mask=states[bb]==sid;cell=a[bb].copy();candidates=mask&(cell>0);assert candidates.any(),f'No retained province for state {sid}'
  _,nearest=distance_transform_edt(~candidates,return_indices=True);missing=mask&~candidates;cell[missing]=cell[tuple(nearest[:,missing])]
  lock=np.zeros_like(cell)
  for pid in np.unique(cell[mask]):
   dist=distance_transform_edt(cell==pid);pos=np.unravel_index(dist.argmax(),dist.shape);lock[pos]=pid
  cell,repairs=repair(cell,mask,lock,edited[bb]);a[bb][mask]=cell[mask]
  repair_rows.append({'state':sid,'name':w['regions'][str(sid)]['name'],'fitted_pixels':int(missing.sum()),'fragment_sliver_pixels':repairs});print('FIT',sid,int(missing.sum()),repairs,flush=True)
 assert np.all(a[states>0]>0)and np.array_equal(lut[a],states)
 assert set(map(int,np.unique(a)))-{0,65535}==set(map(int,ps))
 audit=demographics(w,sd,oldw,olds,states);audit.update(version='0.2.0.29',baseline_version='0.2.0.28',removed_provinces=[{'id':pid,'name':oldps[str(pid)]['name']}for pid in removed],membership_changes=membership,repairs=repair_rows,state_priority=True,coast_unchanged=True,new_provinces=0)
 # Refresh area and guaranteed interior focus for every changed province.
 changed_ids=(set(map(int,np.unique(a[edited])))|set(map(int,np.unique(olda[edited]))))-{0,65535};changed_ids-=set(removed)
 boxesp=find_objects(a,max_label=65535)
 for sid,s in w['regions'].items():s['provinces']=sorted(p['id']for p in ps.values()if p['region']==int(sid))
 for k,p in ps.items():
  pid=int(k);bb=boxesp[pid-1];mask=a[bb]==pid
  if pid in changed_ids or any(x['state']==p['region']for x in repair_rows):
   yy,xx=np.nonzero(mask);p['area_km2']=round(float(AREA[yy+bb[0].start].sum()),3)
   dist=distance_transform_edt(mask);iy,ix=np.unravel_index(dist.argmax(),mask.shape);p['map_center']=[(ix+bb[1].start+.5)/W,(iy+bb[0].start+.5)/H]
   p['geometry_source']='User .28 colour-map edits; state-priority fitting and connected-neighbour fragment repair'
  if p['region']!=oldps[k]['region']:
   s=w['regions'][str(p['region'])]
   if ' · Province 'in p['name']:p['name']=s['name']+' · Province '+str(p['id'])
 for sid,s in w['regions'].items():
  s['area_km2']=round(sum(ps[str(i)]['area_km2']for i in s['provinces']),3)
  for j,pid in enumerate(s['provinces'],1):ps[str(pid)]['local_index']=j
 # Relink geographical points to the edited state at their real coordinates.
 trees={};coords={}
 def nearest(lon,lat,sid=None):
  x=int((lon+180)/360*W)%W;y=min(H-1,max(0,int((90-lat)/180*H)));pid=int(a[y,x])
  if pid not in [0,65535] and (sid is None or ps[str(pid)]['region']==sid):return pid
  assert sid is not None
  if sid not in trees:
   bb=boxes[sid-1];yy,xx=np.nonzero(states[bb]==sid);yy+=bb[0].start;xx+=bb[1].start
   step=max(1,len(yy)//250000);yy=yy[::step];xx=xx[::step];lo=(xx+.5)/W*2*np.pi-np.pi;la=np.pi/2-(yy+.5)/H*np.pi;coords[sid]=(yy,xx);trees[sid]=cKDTree(np.column_stack([np.cos(la)*np.sin(lo),np.sin(la),np.cos(la)*np.cos(lo)]))
  lo,la=math.radians(lon),math.radians(lat);j=trees[sid].query([math.cos(la)*math.sin(lo),math.sin(la),math.cos(la)*math.cos(lo)])[1];yy,xx=coords[sid];return int(a[yy[j],xx[j]])
 cities=read('data/cities.json');scene=read('data/urban_scenery.json');urban=read('data/urban_population.json');citychanges=[]
 for p in ps.values():p['cities']=[]
 for c in cities:
  oldpid=c['province_id'];oldsid=c['state_id'];pid=nearest(c['longitude'],c['latitude'],None)if int(a[min(H-1,int((90-c['latitude'])/180*H)),int((c['longitude']+180)/360*W)%W])not in [0,65535]else nearest(c['longitude'],c['latitude'],oldsid);sid=ps[str(pid)]['region']
  if pid!=oldpid or sid!=oldsid:citychanges.append({'city':c['name'],'from_province':oldpid,'to_province':pid,'from_state':oldsid,'to_state':sid})
  c.update(province_id=pid,state_id=sid,country=w['regions'][str(sid)]['owner']);ps[str(pid)]['cities'].append(c['name'])
  if c.get('urban_group'):ps[str(pid)]['urban_group']=c['urban_group']
  if c.get('population_rank',0)>=1000000:ps[str(pid)]['kind']='city'
 for group in urban['groups'].values():group['provinces']=[]
 for c in cities:
  if c.get('urban_group')in urban['groups']:urban['groups'][c['urban_group']]['provinces'].append(c['province_id'])
 weights=Counter()
 for kind in ['clusters','landmarks']:
  for c in scene[kind]:
   oldsid=c['state'];x=int((c['longitude']+180)/360*W)%W;y=min(H-1,int((90-c['latitude'])/180*H));pid=nearest(c['longitude'],c['latitude'],None if int(a[y,x])not in [0,65535]else oldsid);sid=ps[str(pid)]['region'];c.update(province=pid,state=sid)
   if kind=='clusters':weights[sid]+=len(c['instances'])
   else:c['country']=w['regions'][str(sid)]['owner']
   if c.get('group')in urban['groups']:urban['groups'][c['group']]['provinces'].append(pid)
 for c in scene['clusters']:c['state_visual_weight']=len(c['instances'])/max(1,weights[c['state']])
 for g in urban['groups'].values():g['provinces']=sorted(set(g['provinces']))
 for p in ps.values():p['cities']=sorted(set(p['cities']))
 for sid,s in w['regions'].items():
  uv=s.get('capital_uv',s['map_center']);pid=nearest(uv[0]*360-180,90-uv[1]*180,int(sid));s['capital_province']=pid
  # Preserve stable capital coordinates when still within this state.
  if pid not in s['provinces']:raise AssertionError(sid)
  if s['capital_province']!=oldw['regions'][sid]['capital_province']or int(sid)in touched:s['map_center']=ps[str(pid)]['map_center']
 for tag,c in w['countries'].items():
  c['regions']=sorted(s['id']for s in w['regions'].values()if s['owner']==tag);c['population']=sum(w['regions'][str(i)]['population']for i in c['regions']);c['map_center']=w['regions'][str(c['capital'])]['map_center']
 audit['country_population_changes']={tag:{'before':oldw['countries'][tag]['population'],'after':c['population']}for tag,c in w['countries'].items()if c['population']!=oldw['countries'][tag]['population']};audit['city_reference_changes']=citychanges
 assert sum(s['population']for s in w['regions'].values())==sum(s['population']for s in oldw['regions'].values())
 w.update(version='0.2.0.29',scenario_id='bunny_world_2000_0_2_0_29');scene['version']='0.2.0.29';urban['states']={sid:{'population_2000':s['population']}for sid,s in w['regions'].items()}
 for i in range(4):
  t,l=i//2*4096,i%2*8192;part=a[t:t+4096,l:l+8192];rgb=np.zeros((*part.shape,3),np.uint8);rgb[:,:,0]=part&255;rgb[:,:,1]=part>>8;save_png(R/f'assets/region_ids_{i}.png',rgb)
 sea=np.load(D/'sea.npz')['seas'];rgb=np.zeros((*sea.shape,3),np.uint8);rgb[:,:,0]=sea&255;rgb[:,:,1]=sea>>8;save_png(R/'assets/sea_ids.png',rgb)
 np.savez_compressed(D/'final_provinces.npz',provinces=a);np.savez_compressed(D/'final_states.npz',states=states)
 for n,data in [('world',w),('provinces',ps),('state_demographics',sd),('cities',cities),('urban_scenery',scene),('urban_population',urban),('map_edit_audit_0229',audit)]:write('data/'+n+'.json',data)
 for n in ['project.godot','export_presets.cfg']:
  p=R/n;p.write_text(p.read_text().replace('0.2.0.28','0.2.0.29'))
 p=R/'scripts/world_state.gd';p.write_text(p.read_text().replace('const SAVE_VERSION := 16','const SAVE_VERSION := 17'))
 print('EDITS_0229_APPLIED',len(ps),'provinces',len(w['regions']),'states',len(citychanges),'city reference updates',flush=True)
if __name__=='__main__':main()
