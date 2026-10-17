"""Native geometry, live references, conservation and complete-profile audit."""
from pathlib import Path
from collections import Counter,defaultdict
import json,math,sys,zlib,hashlib,struct
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects,distance_transform_edt
R=Path(__file__).resolve().parents[1];B=R/'tools/cartography/baseline_0227';sys.path.insert(0,str(R/'tools'))
from build_boundary_hint import atlas
checks=0
def check(ok,label):
 global checks
 checks+=1
 assert ok,label
def read(p):return json.loads((R/p).read_text())
def inventories(w):
 out={}
 for tag in w['countries']:
  b=Counter();slots=pop=0
  for s in w['regions'].values():
   if s['owner']==tag:b.update(s['buildings']);slots+=s['building_slot_baseline'];pop+=s['population']
  out[tag]=(pop,dict(b),slots)
 return out
def main():
 w,ps,sd,plan=map(read,['data/world.json','data/provinces.json','data/state_demographics.json','data/province_plan_0228.json']);old=json.loads((B/'world.json').read_text());oldps=json.loads((B/'provinces.json').read_text());oldsd=json.loads((B/'state_demographics.json').read_text());merges={int(k):v for k,v in plan['merges'].items()}
 check(w['version']=='0.2.0.28','version');check((len(w['countries']),len(w['regions']),len(ps))==(224,1261,13200),'counts');check(inventories(w)==inventories(old),'country population/buildings/slots conserved');check(sum(s['population']for s in w['regions'].values())==6146495066,'global population');check(len(w['countries']['LEB']['regions'])==1 and 461 in w['countries']['HEZ']['regions'],'Lebanon and Hezbollah');check(not {622,623,1758}&set(map(int,w['regions'])),'merged IDs removed')
 check(set(sd['states'])==set(w['regions']),'all state profiles');by=defaultdict(list)
 for k,p in ps.items():
  check(int(k)==p['id']and str(p['region'])in w['regions'],'valid province '+k);by[p['region']].append(p['id'])
  check('population'not in p and 'population_2000'not in p,'state-only population '+k)
  check(p['area_km2']>0,'positive area '+k)
  check(all(str(n)in ps and p['id']in ps[str(n)]['neighbors']for n in p['neighbors']),'symmetric valid adjacency '+k)
 for k,s in w['regions'].items():
  check(sorted(s['provinces'])==sorted(by[s['id']])and len(s['provinces'])==plan['budgets'][k],'exact reviewed membership '+k)
  check(s['capital_province']in s['provinces'],'capital '+k);check(s['id']in w['countries'][s['owner']]['regions'],'country reference '+k)
  check(all(str(n)in w['regions']and s['id']in w['regions'][str(n)]['neighbors']for n in s['neighbors']),'state adjacency '+k)
  p=sd['states'][k];ages=np.array(p['age_single_year']);check(len(ages)==101 and np.isfinite(ages).all()and np.all(ages>=0)and abs(ages.sum()-1)<1e-8,'ages '+k);check(abs(ages[25:].sum()-p['adult25_share'])<1e-8,'adult denominator '+k)
  check(p['population_2000']==s['population'],'profile population '+k)
  for key,m in p['metrics'].items():check(m['shares']and abs(sum(m['shares'].values())-1)<1e-8 and all(v>=0 for v in m['shares'].values()),'complete shares '+k+key)
  if k not in ['624','1750']:check(p==oldsd['states'][k],'unchanged profile '+k)
 for tag,c in w['countries'].items():check(sorted(c['regions'])==sorted(s['id']for s in w['regions'].values()if s['owner']==tag)and c['capital']in c['regions'],'country list '+tag)
 check(len(ps)<=math.floor(plan['md_global_land']*1.15),'global performance ceiling')
 for row in plan['states']:check(row['planned']<=row['cap'],'allocation cap '+str(row['state']))
 a=atlas();oldatlas=np.load(B/'provinces.npz')['provinces'];lut=np.zeros(65536,np.uint16);oldlut=np.zeros_like(lut);lut[65535]=oldlut[65535]=8191
 for p in ps.values():lut[p['id']]=p['region']
 for p in oldps.values():oldlut[p['id']]=merges.get(p['region'],p['region'])
 ids=set()
 for top in range(0,8192,128):
  aa=a[top:top+128];oo=oldatlas[top:top+128];check(np.array_equal(lut[aa],oldlut[oo]),'exact accepted state/coast/Antarctica footprint '+str(top));ids.update(map(int,np.unique(aa)))
 check(ids-{0,65535}==set(map(int,ps)),'every ID represented and no orphans')
 for k,p in ps.items():
  u,v=p['map_center'];check(int(a[min(8191,int(v*8192)),int(u*16384)%16384])==p['id'],'pickable anchor '+k)
 for c in read('data/cities.json'):
  check(str(c['province_id'])in ps and c['state_id']==ps[str(c['province_id'])]['region'],'city reference '+c['name'])
  check(w['regions'][str(c['state_id'])]['owner']==c['country'],'city controller '+c['name'])
 scene=read('data/urban_scenery.json');oldscene=json.loads((B/'urban_scenery.json').read_text());weights=Counter()
 for kind in ['clusters','landmarks']:
  check(len(scene[kind])==len(oldscene[kind]),'scenery count '+kind)
  for c,b in zip(scene[kind],oldscene[kind]):
   check(c['state']==ps[str(c['province'])]['region'],'scenery reference')
   check((c['longitude'],c['latitude'])==(b['longitude'],b['latitude']),'scenery location')
   if kind=='clusters':check(c['instances']==b['instances'],'decorative instances retained');weights[c['state']]+=c['state_visual_weight']
 check(all(abs(v-1)<1e-6 for v in weights.values()),'scenery weight sums')
 urban=read('data/urban_population.json');check(set(urban['states'])==set(w['regions']),'urban state references')
 for k,s in w['regions'].items():check(urban['states'][k]['population_2000']==s['population'],'urban state total '+k)
 for g in urban['groups'].values():check(all(str(p)in ps for p in g['provinces']),'city group province references')
 for t in read('data/protected_territories_0210.json')['territories']:check(all(str(s)in w['regions']for s in t['states']),'protected references')
 coast=read('assets/display/local_coasts.json');check(set(coast['states'])<=set(w['regions']) and '624'in coast['states'],'current local coast states');check(all(str(k)in ps for k in coast.get('provinces',{})),'current local coast province keys')
 index=np.asarray(Image.open(R/'assets/province_index.png'))
 for p in ps.values():q=index[p['id']//256,p['id']%256];check(int(q[0])+int(q[1])*256==p['region'],'index membership '+str(p['id']))
 # Validate every accepted distance-field half-plane against the final IDs,
 # including areas currently offscreen. Ambiguous junctions use fallback.
 fields={}
 for name,bpp,dtype,channels in [('boundary_pairs',4,np.uint8,4),('boundary_distance',2,'<f2',1)]:
  raw=(R/f'assets/display/{name}.bwd').read_bytes();width,height=struct.unpack_from('<II',raw);decoded=zlib.decompress(raw[8:]);check((width,height)==(8192,4096)and len(decoded)==width*height*bpp,'field dimensions '+name);fields[name]=np.frombuffer(decoded,dtype).reshape((height,width,channels)if channels>1 else(height,width))
 for top in range(0,4096,64):
  pairs=fields['boundary_pairs'][top:top+64];dist=fields['boundary_distance'][top:top+64];p=pairs[:,:,0].astype(np.uint16)+pairs[:,:,1].astype(np.uint16)*256;q=pairs[:,:,2].astype(np.uint16)+pairs[:,:,3].astype(np.uint16)*256
  check(int(p.max())<=len(ps)and int(q.max())<=len(ps),'no orphan boundary pair IDs '+str(top));check(np.isfinite(dist).all(),'finite distances '+str(top));valid=(p>0)&(np.abs(dist)>1.5);expected=np.where(dist>0,p,q);actual=a[top*2+1:(top+64)*2:2,1::2];check(np.array_equal(expected[valid],actual[valid]),'current oriented coverage '+str(top))
 del fields
 # Every same-state raster neighbor must have a drawn mesh edge.
 binary=(R/'tools/cartography/province_boundaries_021.bin').read_bytes();nv,ni=struct.unpack_from('<II',binary);colors=np.frombuffer(binary,'<f4',nv*4,8+nv*(12+16)).reshape(-1,4);ids=np.rint(colors*255).astype(np.uint32);pairs=set((int(l),int(r))for l,r in zip(ids[:,0]+ids[:,1]*256,ids[:,2]+ids[:,3]*256));expected={(p['id'],n)for p in ps.values()for n in p['neighbors']if p['id']<n and p['region']==ps[str(n)]['region']};check(expected<=pairs,'every internal border rendered')
 # Record inherited narrow-island/city exceptions; compactness is not clickability.
 exceptions=[];fragments=[];island_groups=[];state_parts={};boxes=find_objects(a,max_label=65535);state_boxes=find_objects(lut[a],max_label=8191)
 for k,p in ps.items():
  bb=boxes[p['id']-1];mask=a[bb]==p['id'];lat=90-p['map_center'][1]*180;dy=math.pi*6371.0088/8192;dx=dy*max(.01,math.cos(math.radians(lat)));width=float(distance_transform_edt(np.pad(mask,1),sampling=(dy,dx)).max()*2)
  pieces,n=label(mask,np.ones((3,3),np.uint8))
  if n>1:
   sid=p['region'];sb=state_boxes[sid-1]
   if sid not in state_parts:state_parts[sid]=label(lut[a[sb]]==sid,np.ones((3,3),np.uint8))[0]
   seen=set()
   for part in range(1,n+1):
    yy,xx=np.nonzero(pieces==part);island=int(state_parts[sid][yy[0]+bb[0].start-sb[0].start,xx[0]+bb[1].start-sb[1].start])
    if island in seen:fragments.append({'province':p['id'],'state':sid,'pixels':int((pieces==part).sum())})
    seen.add(island)
   island_groups.append({'province':p['id'],'state':sid,'island_components':n})
  if width<8:exceptions.append({'province':p['id'],'state':p['region'],'name':p['name'],'area_km2':p['area_km2'],'inscribed_width_km':round(width,3),'kind':p['kind'],'reason':'Existing narrow state/island or city footprint; not enlarged for clicking'})
 out={'passed':not fragments,'checks':checks+1,'countries':224,'states':1261,'land_provinces':len(ps),'global_population':6146495066,'exact_state_coast_antarctica_preservation':True,'country_totals_preserved':True,'all_internal_borders_present':len(expected),'narrow_footprint_exceptions':len(exceptions),'province_population_fields':False,'same_landmass_fragment_provinces':len(fragments),'archipelago_province_groups':len(island_groups)}
 (R/'validation_0228').mkdir(exist_ok=True);write=lambda f,d:(R/f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');write('validation_0228/data_results.json',out);write('data/province_width_exceptions_0228.json',exceptions);write('data/province_connectivity_0228.json',{'same_landmass_fragments':fragments,'island_groups':island_groups});check(not fragments,'no disconnected scraps on same landmass');print('PROVINCES_0228_DATA_PASS',out)
if __name__=='__main__':main()
