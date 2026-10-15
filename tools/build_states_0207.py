"""Budget geographic ADM1 unions by MD country counts; reserve disputed boundaries.

Existing geographic controller/coast coverage is retained. MD is used for
counts, names and density hints, never for the geometry of a boundary.
"""
from collections import Counter,defaultdict
from pathlib import Path
import json,math,re
import numpy as np
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from scipy.ndimage import find_objects,label,distance_transform_edt
from scipy.spatial import cKDTree
from build_geography_0206 import ROOT,SRC,BASE,W,H,AREA,center,xyz,pairs,alloc,write,FEATURES

VERSION='0.2.0.7'

def main():
 ref=json.load(open(ROOT/'data/md_geography_reference.json'))
 # Raw ADM1 intersections retained from 0.2.0.6, before gameplay grouping.
 raw=np.load(SRC/'admin_atlas_0206.npz')['admin']
 old=np.load(BASE/'states.npz')['regions'];base=json.load(open(BASE/'world.json'))
 oldowner=np.zeros(8192,np.uint16)
 for k,s in base['regions'].items():oldowner[int(k)]=base['countries'][s['owner']]['index']
 countries={c['index']:t for t,c in base['countries'].items()}
 ne=rasterize([(f['geometry'],i+1) for i,f in enumerate(FEATURES)],out_shape=(H,W),transform=from_bounds(-180,-90,180,90,W,H),dtype='uint16')
 # Match raw intersection IDs to the source ADM1 label using sample votes.
 votes=defaultdict(Counter)
 for top in range(0,H,128):
  a=raw[top:top+128:3,::3];b=ne[top:top+128:3,::3];m=(a>0)&(b>0)
  v,n=np.unique(a[m].astype(np.uint32)*8192+b[m],return_counts=True)
  for k,q in zip(v,n):votes[int(k//8192)][int(k%8192)]+=int(q)
 boxes=find_objects(raw);info={}
 for rid,bb in enumerate(boxes,1):
  if bb is None:continue
  yy,xx=np.nonzero(raw[bb]==rid);yy+=bb[0].start;xx+=bb[1].start
  mid=len(xx)//2;tag=countries[int(oldowner[old[yy[mid],xx[mid]]])]
  aid=votes[rid].most_common(1)[0][0] if votes[rid] else int(ne[yy[mid],xx[mid]])
  p=FEATURES[aid-1]['properties'] if aid else {}
  previous=base['regions'][str(int(old[yy[mid],xx[mid]]))]
  name=p.get('name_en') or p.get('name') or previous['name']
  info[rid]={'owner':tag,'name':name,'group':p.get('region') or name,'code':p.get('adm1_code') or 'scenario:'+str(rid)}
 del ne,boxes
 disputes=json.load(open(SRC/'disputed_areas.geojson'))['features']
 d=rasterize([(f['geometry'],i+1) for i,f in enumerate(disputes)],out_shape=(H,W),transform=from_bounds(-180,-90,180,90,W,H),dtype='uint16',all_touched=True)
 d[raw==0]=0
 # Coast/generalisation differences must not reserve a foreign sliver as a
 # new disputed State. Keep the dominant accepted controller, plus substantial
 # secondary intersections (a genuine split across existing controllers).
 owner_by_raw=np.zeros(8192,np.uint16)
 for rid,u in info.items():owner_by_raw[rid]=base['countries'][u['owner']]['index']
 inter=Counter()
 for top in range(0,H,128):
  q=d[top:top+128];c=owner_by_raw[raw[top:top+128]];m=q>0
  values,counts=np.unique(q[m].astype(np.uint32)*512+c[m],return_counts=True)
  inter.update({int(v):int(n) for v,n in zip(values,counts)})
 dominant={};totals=Counter()
 for code,n in inter.items():
  di,ci=divmod(code,512);totals[di]+=n
  if di not in dominant or n>inter[dominant[di]]:dominant[di]=code
 bad=[code for code,n in inter.items() if code!=dominant[code//512] and n<totals[code//512]*.15]
 for top in range(0,H,128):
  q=d[top:top+128];c=owner_by_raw[raw[top:top+128]];q[np.isin(q.astype(np.uint32)*512+c,bad)]=0
 # Generalized coastlines leave narrow unclaimed fringes around some
 # otherwise wholly protected territories. A >95% cover identifies that
 # cartographic fringe; fill only unassigned protection pixels, never another
 # protected territory or a different country's footprint.
 country_pixels=Counter()
 for top in range(0,H,128):
  c=owner_by_raw[raw[top:top+128]];v,n=np.unique(c[c>0],return_counts=True);country_pixels.update({int(k):int(q) for k,q in zip(v,n)})
 fill_country={}
 for code,n in inter.items():
  di,ci=divmod(code,512)
  if ci and n>country_pixels[ci]*.95:fill_country[ci]=di
 for ci,di in fill_country.items():
  for top in range(0,H,128):
   q=d[top:top+128];c=owner_by_raw[raw[top:top+128]];q[(c==ci)&(q==0)]=di
 # Belize's broad claim and its nested Sapodilla Cayes claim form one
 # protected Southern Belize State under the strict one-plus-one budget.
 # Both source territory identities remain in the catalog and state metadata.
 # This is a geographic claim grouping, not an exception to the country cap.
 nested_aliases={'B80':'B51','B95':'B96','B79':'B98','B99':'B98'}
 dispute_index={f['properties']['BRK_A3']:i+1 for i,f in enumerate(disputes)}
 for child,parent_code in nested_aliases.items():d[d==dispute_index[child]]=dispute_index[parent_code]
 # Stable composite IDs retain every intersection with a controller and a
 # protected territory. Overlapping inner features take precedence spatially.
 codes=set()
 for top in range(0,H,128):
  r=raw[top:top+128];q=d[top:top+128];m=r>0;codes.update(map(int,np.unique(r[m].astype(np.uint32)+q[m].astype(np.uint32)*8192)))
 codeids={c:i+1 for i,c in enumerate(sorted(codes))};lookup=np.zeros((len(disputes)+1,8192),np.uint16)
 for code,i in codeids.items():lookup[code//8192,code%8192]=i
 tokens=lookup[d,raw];tokens[old==8191]=8191
 del raw,lookup,d
 units={};sizes={};centers={};boxes=find_objects(tokens,max_label=8190)
 for code,i in codeids.items():
  rid=code%8192;di=code//8192;bb=boxes[i-1];yy,xx=np.nonzero(tokens[bb]==i);yy+=bb[0].start;xx+=bb[1].start
  point,lon,lat=center(yy,xx);sizes[i]=float(AREA[yy].sum());centers[i]=xyz(np.array([lon]),np.array([lat]))[0]
  u=dict(info[rid]);u.update(dispute=di,raw=rid,point=point);units[i]=u
 print('RAW_UNITS',len(units),'PROTECTED',sum(bool(u['dispute']) for u in units.values()),flush=True)
 # MD geographical state centres give grouping/naming hints only.
 mdcentres=defaultdict(list)
 for s in base['regions'].values():
  u,v=s['map_center']
  for sid in s['source_states']:
   if str(sid) in ref['states'] and ref['states'][str(sid)]['owner']==s['owner']:
    mdcentres[s['owner']].append((sid,xyz(np.array([u*360-180]),np.array([90-v*180]))[0]))
 for i,u in units.items():
  choices=mdcentres[u['owner']]
  u['md_hint']=min(choices,key=lambda x:np.linalg.norm(x[1]-centers[i]))[0] if choices else 0
 parent={i:i for i in units};members={i:[i] for i in units}
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 def merge(a,b):
  if sizes[a]<sizes[b]:a,b=b,a
  parent[b]=a;total=sizes[a]+sizes[b];centers[a]=(centers[a]*sizes[a]+centers[b]*sizes[b])/total
  sizes[a]=total;members[a]+=members.pop(b);return a
 edges=pairs(np.where(tokens==8191,0,tokens));bycountry=defaultdict(list)
 for i,u in units.items():bycountry[u['owner']].append(i)
 countryreport=[];splits=[]
 for tag,ids in sorted(bycountry.items()):
  md=ref['countries'][tag]['states'];cap=md*120//100;current=set(ids);area=sum(sizes[i] for i in ids)
  # +1 is used only for a small country with a protected area or a strong
  # native-administrative reason (e.g. Greenland's national park).
  protected={units[i]['dispute'] for i in ids if units[i]['dispute']}
  minimum_groups=len(protected)+(any(not units[i]['dispute'] for i in ids))
  extra=0;reason=''
  small=md<=6 or area<45000
  if small and (minimum_groups>cap or (tag=='GRN' and len(current)==cap+1)):
   extra=1;reason='Separate important Natural Earth protected territory' if tag!='GRN' else 'Retain Northeast Greenland National Park as a distinct native geographic unit'
  cap+=extra
  if minimum_groups>cap:
   raise ValueError(('Protected territory count exceeds authorized country cap',tag,md,cap,minimum_groups,[disputes[j-1]['properties']['BRK_NAME'] for j in protected]))
  target=max(md,min(cap,len(current)))
  while len(current)>target:
   border=Counter()
   for (x,y),n in edges.items():
    a,b=root(x),root(y)
    if a==b or a not in current or b not in current:continue
    if units[a]['dispute']!=units[b]['dispute']:continue
    border[tuple(sorted([a,b]))]+=n
   if border:
    def score(ab):
     a,b=ab
     hints_a={units[i]['md_hint'] for i in members[a]};hints_b={units[i]['md_hint'] for i in members[b]}
     groups_a={units[i]['group'] for i in members[a]};groups_b={units[i]['group'] for i in members[b]}
     affinity=(.15 if hints_a==hints_b else .35 if groups_a==groups_b else 1.)
     return min(sizes[a],sizes[b])*affinity/(border[ab]**.45)
    a,b=min(border,key=score)
   else:
    # Detached islands with the same protection identity may form a coherent
    # archipelago State, rather than causing an unlimited island exception.
    possible=[i for i in current if sum(units[j]['dispute']==units[i]['dispute'] for j in current)>1]
    if not possible:raise ValueError(('No legal grouping remains',tag))
    a=min(possible,key=lambda i:sizes[i]);b=min((i for i in current if i!=a and units[i]['dispute']==units[a]['dispute']),key=lambda i:np.linalg.norm(centers[i]-centers[a]))
   current.remove(a);current.remove(b);current.add(merge(a,b))
  countryreport.append({'country':tag,'name':base['countries'][tag]['name'],'md_states':md,'minimum':md,'normal_maximum':md*120//100,'allowed_maximum':cap,'small_country_exception':bool(extra),'exception_reason':reason,'raw_geographic_pieces':len(ids),'states_before_splits':len(current),'states':max(md,len(current)),'md_land_provinces':ref['countries'][tag]['land_provinces']})
  print('STATE_BUDGET',tag,len(ids),'->',max(md,len(current)),'MD',md,'CAP',cap,flush=True)
 lut=np.zeros(8192,np.uint16);lut[8191]=8191
 for i in units:lut[i]=root(i)
 states=lut[tokens];del tokens
 # Countries with fewer ADM1 units than MD get terrain-aware subdivisions of
 # a large native unit. The source ADM1 boundary remains an outer boundary.
 from skimage.segmentation import watershed
 from scipy.ndimage import gaussian_filter
 elevation=np.load(SRC/'etopo_021.npz')['meters']
 current=set(members);nextid=max(units)+1
 for row in countryreport:
  tag=row['country'];ids={i for i in current if units[i]['owner']==tag}
  while len(ids)<row['minimum']:
   viable=[i for i in ids if sizes[i]>100] or list(ids);sid=max(viable,key=lambda i:sizes[i]);yy,xx=np.nonzero(states==sid)
   # Split at the longest local east/west or north/south extent, seeded by
   # distinct MD-name reference locations when available. No MD edges used.
   lon=(xx+.5)/W*360-180;lat=90-(yy+.5)/H*180;u=units[sid];v=centers[sid]
   lon0=math.degrees(math.atan2(v[0],v[2]));lat0=math.degrees(math.asin(v[1]/np.linalg.norm(v)))
   from pyproj import Transformer
   proj=Transformer.from_crs('EPSG:4326',f'+proj=laea +lat_0={lat0} +lon_0={lon0} +datum=WGS84 +units=km',always_xy=True)
   px,py=proj.transform(lon,lat);axis=px if np.ptp(px)>np.ptp(py) else py;order=np.argsort(axis)
   aidx,bidx=int(order[len(order)//5]),int(order[len(order)*4//5])
   # At atlas resolution, terrain-gradient watershed gives a coherent cut.
   y0,y1=int(yy.min()),int(yy.max())+1;x0,x1=int(xx.min()),int(xx.max())+1;mask=states[y0:y1,x0:x1]==sid
   z=elevation[np.clip((np.arange(y0,y1)*elevation.shape[0]//H),0,elevation.shape[0]-1)[:,None],np.clip((np.arange(x0,x1)*elevation.shape[1]//W),0,elevation.shape[1]-1)]
   zz=gaussian_filter(z.astype(float),1.2);cost=1+np.hypot(*np.gradient(zz))/100
   markers=np.zeros(mask.shape,np.int32);markers[yy[aidx]-y0,xx[aidx]-x0]=1;markers[yy[bidx]-y0,xx[bidx]-x0]=2
   grown=watershed(cost,markers,mask=mask,connectivity=2)
   # Watershed components without seeds are assigned in metric space to one
   # of the two substantial pieces; separate islands remain valid groups.
   cc=grown[yy-y0,xx-x0];empty=cc==0
   cc[empty]=np.where((px[empty]-px[aidx])**2+(py[empty]-py[aidx])**2<(px[empty]-px[bidx])**2+(py[empty]-py[bidx])**2,1,2)
   if min(np.count_nonzero(cc==1),np.count_nonzero(cc==2))<2:raise ValueError(('Unsplittable State',tag,sid))
   nid=nextid;nextid+=1;states[yy[cc==2],xx[cc==2]]=nid
   units[nid]=dict(u);members[nid]=members[sid][:];units[sid]=dict(u)
   # Prefer a distinct, relevant MD regional name for the new subdivision.
   split_names=[];seen_names=set()
   for code in [1,2]:
    y,x=yy[cc==code],xx[cc==code];pt,lo,la=center(y,x);vv=xyz(np.array([lo]),np.array([la]))[0]
    choice=min(mdcentres[tag],key=lambda q:np.linalg.norm(q[1]-vv));name=ref['states'][str(choice[0])]['name']
    split_names.append(name);seen_names.add(name)
   if len(seen_names)<2:
    split_names=[('Western ' if axis is px else 'Southern ')+u['name'],('Eastern ' if axis is px else 'Northern ')+u['name']]
   for j,code in [(sid,1),(nid,2)]:
    y,x=yy[cc==code],xx[cc==code];sizes[j]=float(AREA[y].sum());pt,lo,la=center(y,x);centers[j]=xyz(np.array([lo]),np.array([la]))[0];units[j]['point']=pt;units[j]['split_name']=split_names[code-1]
   current.add(nid);ids.add(nid);splits.append({'country':tag,'source_administrative_name':u['name'],'names':split_names,'reason':'Reach the strict MD minimum without copying MD cartography'})
 del elevation
 # Compact IDs and reconstruct metadata and retained accounting from the
 # final categorical atlas, not from pre-merge records.
 ids=sorted(current,key=lambda i:(units[i]['owner'],i));compact={i:j+1 for j,i in enumerate(ids)}
 lut=np.zeros(max(max(ids),8191)+1,np.uint16);lut[8191]=8191
 for i,j in compact.items():lut[i]=j
 states=lut[states];records={};overlap=defaultdict(Counter)
 for top in range(0,H,128):
  a=states[top:top+128];b=old[top:top+128];m=(a>0)&(a<8191);v,n=np.unique(a[m].astype(np.uint32)*8192+b[m],return_counts=True)
  for k,q in zip(v,n):overlap[int(k//8192)][int(k%8192)]+=int(q)
 boxes=find_objects(states,max_label=8190)
 protected_count=Counter((units[i]['owner'],units[i]['dispute']) for i in compact if units[i]['dispute'])
 for i,sid in compact.items():
  u=units[i];bb=boxes[sid-1];yy,xx=np.nonzero(states[bb]==sid);yy+=bb[0].start;xx+=bb[1].start;pt,_,_=center(yy,xx)
  mids=members[i];divisions=sorted({units[j]['name'] for j in mids});hints={units[j]['md_hint'] for j in mids};group={units[j]['group'] for j in mids}
  if u.get('split_name'):name=u['split_name']
  elif u['dispute'] and protected_count[(u['owner'],u['dispute'])]==1:name=disputes[u['dispute']-1]['properties']['BRK_NAME']
  elif u['dispute'] and len({units[j]['raw'] for j in mids})>1:name=disputes[u['dispute']-1]['properties']['BRK_NAME']
  elif len(divisions)==1:name=divisions[0]
  elif len(hints)==1 and str(next(iter(hints))) in ref['states']:name=ref['states'][str(next(iter(hints)))]['name']
  elif len(group)==1:name=next(iter(group))
  else:name=' / '.join(units[j]['name'] for j in sorted(mids,key=lambda j:-sizes[j])[:2])
  if u['owner']=='BLZ':name='Southern Belize' if u['dispute'] else 'Northern Belize'
  if u['dispute'] and disputes[u['dispute']-1]['properties']['BRK_A3']=='B96':name='Danube disputed islands'
  oldids=sorted(overlap[sid]);total=sum(overlap[sid].values());rights=[j for j in oldids if overlap[sid][j]>=total*.1];prev=base['regions'][str(max(oldids,key=overlap[sid].get))]
  p=disputes[u['dispute']-1]['properties'] if u['dispute'] else {}
  records[str(sid)]={'id':sid,'name':name,'owner':u['owner'],'population':0,'buildings':{},'provinces':[],
   'cores':sorted({t for j in rights for t in base['regions'][str(j)]['cores']}),'claims':sorted({t for j in rights for t in base['regions'][str(j)]['claims']}),
   'source_states':sorted({v for j in oldids for v in base['regions'][str(j)]['source_states']}),
   'geographic_divisions':divisions,'geographic_codes':sorted({units[j]['code'] for j in mids}),'map_center':pt,'area_km2':round(float(AREA[yy].sum()),2),'demographic_profile':prev.get('demographic_profile',u['owner']),
   'protected_territory':p.get('BRK_A3',''),'protected_territory_name':p.get('BRK_NAME',''),'protected_territories':([p['BRK_A3']]+[c for c,par in nested_aliases.items() if par==p['BRK_A3']]) if p else [],'population_source':'Retained scenario totals; local demographic refinement deferred.'}
 old_to_new=defaultdict(list)
 for sid,counts in overlap.items():
  for oid,n in counts.items():old_to_new[oid].append((sid,n))
 for oid,targets in old_to_new.items():
  previous=base['regions'][str(oid)];weights=[n for s,n in targets]
  for (sid,_),pop in zip(targets,alloc(previous['population'],weights)):records[str(sid)]['population']+=int(pop)
  for building,value in previous['buildings'].items():
   for (sid,_),amount in zip(targets,alloc(int(value),weights)):
    if amount:records[str(sid)]['buildings'][building]=records[str(sid)]['buildings'].get(building,0)+int(amount)
 for tag,c in base['countries'].items():
  owned=[int(k) for k,s in records.items() if s['owner']==tag];u,v=c['map_center'];at=int(states[min(H-1,int(v*H)),int(u*W)%W])
  if at not in owned:at=max(owned,key=lambda j:records[str(j)]['population'])
  c.update(regions=sorted(owned),capital=at,map_center=records[str(at)]['map_center'])
 base['regions']=records;base['version']=VERSION;base['scenario_id']='bunny_world_2000_0_2_0_7'
 base['map'].update(cartography='Geographic ADM1 unions under MD country budgets, with protected Natural Earth disputed boundaries.',regional_boundary_accuracy='Natural Earth geographic boundaries; MD counts/names only. Protected territory geometry reserved for future scenarios without activating later disputes in 2000.',province_geometry='Independent terrain-aware geometry; original MD land counts and smoothed geographic density hints.')
 micro=json.load(open(ROOT/'data/microstate_geometry.json'));micro['state']=next(int(k) for k,s in records.items() if s['owner']==micro['country']);u,v=micro['center_uv'];x,y=int(u*W),int(v*H);near=states[y-5:y+6,x-5:x+6];near=near[(near>0)&(near!=micro['state'])];micro['host_state']=int(np.bincount(near).argmax());write('microstate_geometry',micro)
 write('world',base);np.savez_compressed(SRC/'grouped_atlas_022r2.npz',regions=states)
 for row in countryreport:row['states']=len(base['countries'][row['country']]['regions'])
 territory=[]
 # Catalog every source feature, including tiny marine features that have no
 # land pixels in the accepted map. Never invent ownership or land there.
 for j,f in enumerate(disputes):
  p=f['properties'];sids=[int(k) for k,s in records.items() if p['BRK_A3'] in s['protected_territories']]
  territory.append({'code':p['BRK_A3'],'name':p['BRK_NAME'],'classification':p['featurecla'],'states':sids,'boundary_reserved':bool(sids),'start_status':'Retain existing 2000 scenario cores/claims and owner; source notes do not activate later disputes.','source_note':p.get('NOTE_BRK'),'coverage_note':'' if sids else 'No separate land footprint at the accepted map resolution, or entirely covered by a more specific nested territory; retained in source catalog.'})
 write('protected_territories_0207',{'source':'Natural Earth 1:10m Admin-0 breakaway and disputed areas, 99 source features','territories':territory})
 write('geography_0207_report',{'version':VERSION,'states':len(records),'countries':len(base['countries']),'country_budgets':countryreport,'native_splits':splits,'source':'Natural Earth geographic subdivisions and disputed-area polygons; original MD history budgets','md_land_target':ref['counts']['land'],'demographics':'Deferred; existing country totals retained'})
 print('STATES_0207_COMPLETE',len(records),'splits',len(splits),'territories with land',sum(bool(t['states']) for t in territory),flush=True)

if __name__=='__main__':main()
