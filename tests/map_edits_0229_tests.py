"""Validate edited geometry, references, conservation and rebuilt derivatives."""
from pathlib import Path
from collections import Counter,defaultdict
import sys,json,zlib,hashlib,struct
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects
R=Path(__file__).resolve().parents[1];D=R/'tools/cartography/edits_0229';B=D/'baseline';sys.path.insert(0,str(R/'tools'))
from build_boundary_hint import atlas
checks=0
def check(ok,msg):
 global checks
 checks+=1
 assert ok,msg
def read(n):return json.loads((R/n).read_text())
def old(n):return json.loads((B/(n+'.json')).read_text())
def main():
 w,ps,sd,audit=map(read,['data/world.json','data/provinces.json','data/state_demographics.json','data/map_edit_audit_0229.json']);before=old('world');oldps=old('provinces');oldsd=old('state_demographics')
 check(w['version']=='0.2.0.29','release');check((len(w['countries']),len(w['regions']),len(ps))==(224,1261,13198),'counts');check(set(oldps)-set(ps)=={'10465','12585'},'only fully erased province IDs removed');check(set(ps)<=set(oldps),'no new IDs')
 check(set(w['regions'])==set(before['regions']),'all states retained');check(sum(s['population']for s in w['regions'].values())==6146495066,'population conserved')
 check(set(sd['states'])==set(w['regions']),'complete profiles');by=defaultdict(list)
 for k,p in ps.items():
  check(int(k)==p['id']and str(p['region'])in w['regions'],'valid province '+k);by[p['region']].append(p['id']);check('population'not in p and 'population_2000'not in p,'no province residents '+k);check(p['area_km2']>0,'positive area '+k)
  check(all(str(n)in ps and p['id']in ps[str(n)]['neighbors']for n in p['neighbors']),'valid symmetric province adjacency '+k)
 for k,s in w['regions'].items():
  check(s['owner']==before['regions'][k]['owner'],'state ownership retained '+k);check(s['buildings']==before['regions'][k]['buildings']and s['building_slot_baseline']==before['regions'][k]['building_slot_baseline'],'buildings and slots retained '+k)
  check(sorted(s['provinces'])==sorted(by[s['id']])and bool(s['provinces']),'state membership '+k);check(s['capital_province']in s['provinces'],'state capital '+k);check(s['id']in w['countries'][s['owner']]['regions'],'country reference '+k)
  check(all(str(n)in w['regions']and s['id']in w['regions'][str(n)]['neighbors']for n in s['neighbors']),'state adjacency '+k)
  p=sd['states'][k];ages=np.array(p['age_single_year']);check(len(ages)==101 and np.isfinite(ages).all()and np.all(ages>=0)and abs(ages.sum()-1)<1e-8,'ages '+k);check(abs(ages[25:].sum()-p['adult25_share'])<1e-8,'adult denominator '+k);check(p['population_2000']==s['population'],'population profile '+k)
  for name,m in p['metrics'].items():check(m['shares']and abs(sum(m['shares'].values())-1)<1e-8 and all(v>=0 for v in m['shares'].values()),'shares '+k+name)
  if k not in audit['expected_demographics']:check(p==oldsd['states'][k],'unaffected profile unchanged '+k)
 for tag,c in w['countries'].items():check(c['population']==sum(s['population']for s in w['regions'].values()if s['owner']==tag)and sorted(c['regions'])==sorted(s['id']for s in w['regions'].values()if s['owner']==tag)and c['capital']in c['regions'],'country totals/references '+tag)
 a=atlas();lut=np.zeros(65536,np.uint16);lut[65535]=65535
 for p in ps.values():lut[p['id']]=p['region']
 for i in range(4):
  d=np.load(D/f'tile_{i}.npz');t,l=i//2*4096,i%2*8192;part=a[t:t+4096,l:l+8192];check(np.array_equal(lut[part],d['states']),'exact user-authoritative state pixels '+str(i));check(np.array_equal(part>0,d['old_provinces']>0),'coastline retained '+str(i));check(np.array_equal(part==65535,d['old_provinces']==65535),'Antarctica retained '+str(i))
 check(set(map(int,np.unique(a)))-{0,65535}==set(map(int,ps)),'all IDs present')
 for k,p in ps.items():
  u,v=p['map_center'];check(int(a[min(8191,int(v*8192)),int(u*16384)%16384])==p['id'],'interior anchor '+k)
 # Validate 4-connected pieces on each state landmass for every fitted state.
 states=lut[a];boxes=find_objects(states,max_label=65535);structure=np.array([[0,1,0],[1,1,1],[0,1,0]],bool)
 for row in audit['repairs']:
  sid=row['state'];bb=boxes[sid-1];mask=states[bb]==sid;islands,_=label(mask,structure);cell=a[bb]
  for pid in w['regions'][str(sid)]['provinces']:
   pieces,n=label(cell==pid,structure);groups=Counter()
   for j in range(1,n+1):groups[int(islands[pieces==j][0])]+=1
   check(all(count==1 for count in groups.values()),'no same-landmass scraps '+str(pid))
 cities=read('data/cities.json');oc=old('cities');check(len(cities)==len(oc),'all cities retained')
 for c,o in zip(cities,oc):
  check(str(c['province_id'])in ps and c['state_id']==ps[str(c['province_id'])]['region'],'city reference '+c['name']);check(c['country']==w['regions'][str(c['state_id'])]['owner'],'city controller '+c['name']);check((c['longitude'],c['latitude'])==(o['longitude'],o['latitude']),'city coordinates '+c['name'])
 scene=read('data/urban_scenery.json');os=old('urban_scenery');weights=Counter()
 for kind in ['clusters','landmarks']:
  check(len(scene[kind])==len(os[kind]),'scenery count '+kind)
  for c,o in zip(scene[kind],os[kind]):
   check(c['state']==ps[str(c['province'])]['region'],'scenery reference');check((c['longitude'],c['latitude'])==(o['longitude'],o['latitude']),'scenery coordinates')
   if kind=='clusters':check(c['instances']==o['instances'],'retained instance geometry');weights[c['state']]+=c['state_visual_weight']
 check(all(abs(v-1)<1e-6 for v in weights.values()),'scenery weights')
 for g in read('data/urban_population.json')['groups'].values():check(all(str(p)in ps for p in g['provinces']),'urban group references')
 rgb=np.asarray(Image.open(R/'assets/sea_ids.png'),np.uint16);sea=rgb[:,:,0]+rgb[:,:,1]*256;check(np.array_equal(sea,np.load(D/'sea.npz')['seas']),'exact user sea pixels')
 sr=read('data/sea_regions.json');coverage=read('assets/display/sea_coverage.json');check(set(sr)==set(old('sea_regions'))and set(sr)==set(coverage['seas']),'all seas retained and covered');check(coverage['source_sha256']==hashlib.sha256((R/'assets/sea_ids.png').read_bytes()).hexdigest(),'sea highlight source registered')
 pack=(R/'assets/display/sea_coverage.bwd').read_bytes()
 for k,s in sr.items():
  u,v=s['map_center'];check(int(sea[int(v*4096),int(u*8192)])==int(k),'sea anchor '+k);check(all(str(n)in sr and int(k)in sr[str(n)]['neighbors']for n in s['neighbors']),'sea adjacency '+k)
  rec=coverage['seas'][k];raw=zlib.decompress(pack[rec[4]:rec[4]+rec[5]]);f=np.frombuffer(raw,'<f2');check(len(raw)==rec[6]*rec[7]*2 and np.isfinite(f).all()and np.all((f>=0)&(f<=1)),'sea coverage data '+k)
 for name in ['boundary_pairs','boundary_distance']:
  blob=(R/f'assets/display/{name}.bwd').read_bytes();ww,hh=struct.unpack('<II',blob[:8]);raw=zlib.decompress(blob[8:]);check((ww,hh)==(8192,4096),'boundary field size')
  if name=='boundary_pairs':
   p=np.frombuffer(raw,np.uint8).reshape(hh,ww,4);l=p[:,:,0].astype(np.uint16)+p[:,:,1].astype(np.uint16)*256;r=p[:,:,2].astype(np.uint16)+p[:,:,3].astype(np.uint16)*256;check((set(map(int,np.unique(l)))|set(map(int,np.unique(r))))<=set(map(int,ps))|{0,65535},'no stale pairs')
  else:check(np.isfinite(np.frombuffer(raw,'<f2')).all(),'finite boundary distances')
 # Every categorical same-state neighbour pair must have a drawable edge.
 present=set();blob=(R/'tools/cartography/province_boundaries_021.bin').read_bytes();nv,ni=struct.unpack('<II',blob[:8]);colors=np.frombuffer(blob,dtype='<f4',count=nv*4,offset=8+nv*(12+16)).reshape(-1,4);ids=np.rint(colors*255).astype(np.uint32);left=ids[:,0]+ids[:,1]*256;right=ids[:,2]+ids[:,3]*256;present=set(map(int,np.unique(np.minimum(left,right)*65536+np.maximum(left,right))))
 expected={min(p['id'],n)*65536+max(p['id'],n)for p in ps.values()for n in p['neighbors']if p['region']==ps[str(n)]['region']};check(expected<=present,'all internal edges represented')
 result={'passed':True,'checks':checks,'countries':224,'states':1261,'provinces':13198,'sea_regions':len(sr),'population':6146495066,'exact_edited_state_pixels':True,'exact_edited_sea_pixels':True,'same_landmass_fragment_check':'4-connected on all fitted states','new_provinces':0,'removed_provinces':audit['removed_provinces'],'native_windows_tested':False}
 (R/'validation_0229').mkdir(exist_ok=True);(R/'validation_0229/data_results.json').write_text(json.dumps(result,indent=2));print('MAP_EDITS_0229_DATA_PASS',checks,flush=True)
if __name__=='__main__':main()
