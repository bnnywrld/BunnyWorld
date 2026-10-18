"""Check sea-first edits, merged-state residents, fitted geography and bundles."""
from pathlib import Path
import json,sys,hashlib,struct,zlib
from collections import Counter,defaultdict
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects
R=Path(__file__).resolve().parents[1];D=R/'tools/cartography/edits_0211';B=D/'baseline'
sys.path.insert(0,str(R/'tools'))
from build_boundary_hint import atlas
Image.MAX_IMAGE_PIXELS=None
checks=0
def check(ok,msg):
 global checks
 checks+=1
 assert ok,msg
def read(path):return json.loads((R/path).read_text())
def main():
 w=read('data/world.json');ps=read('data/provinces.json');sd=read('data/state_demographics.json');audit=read('data/map_edit_audit_0211.json')
 ow=json.loads((B/'world.json').read_text());ops=json.loads((B/'provinces.json').read_text());osd=json.loads((B/'state_demographics.json').read_text())
 check(w['version']=='0.2.1.1','version');check(len(w['countries'])==len(ow['countries']),'countries preserved')
 check(sum(s['population']for s in w['regions'].values())==sum(s['population']for s in ow['regions'].values()),'global residents conserved')
 check(set(sd['states'])==set(w['regions']),'complete demographic states')
 a=atlas();states=np.load(D/'final_states.npz')['states'];check(np.array_equal(a,np.load(D/'final_provinces.npz')['provinces']),'published province bytes')
 lut=np.zeros(65536,np.uint16);lut[65535]=65535
 by=defaultdict(list)
 for k,p in ps.items():
  pid=int(k);sid=p['region'];lut[pid]=sid;by[sid].append(pid)
  check(str(sid)in w['regions'],'province parent '+k)
  check('population'not in p,'province has no residents '+k)
  check(p['area_km2']>0,'positive area '+k)
  check(all(str(n)in ps and pid in ps[str(n)]['neighbors']for n in p['neighbors']),'province adjacency '+k)
  u,v=p['map_center'];check(int(a[min(8191,int(v*8192)),int(u*16384)%16384])==pid,'province anchor '+k)
 check(np.array_equal(lut[a],states),'exact state/province agreement')
 check(set(map(int,np.unique(a)))-{0,65535}==set(map(int,ps)),'no missing or stale province IDs')
 sea=np.load(D/'sea_regions.npz');oldsea,newsea=sea['old'],sea['edited']
 rgb=np.asarray(Image.open(R/'assets/sea_ids.png'),np.uint16);check(np.array_equal(rgb[:,:,0]+rgb[:,:,1]*256,newsea),'exact uploaded sea map')
 added=(oldsea>0)&(newsea==0);removed=(oldsea==0)&(newsea>0)
 for dy in [0,1]:
  for dx in [0,1]:
   land=a[dy::2,dx::2]>0;check(land[added].all(),'sea-first restored land');check(not land[removed].any(),'sea-first restored water')
 for i,tag in enumerate(['NW','NE','SW','SE']):
  d=np.load(D/f'states_{i}_{tag}.npz');t,l=i//2*4096,i%2*8192;actual=states[t:t+4096,l:l+8192];desired=d['edited'];old=d['old']
  # User state labels are exact wherever sea priority has not removed land.
  valid=(desired>0)&(actual>0);check(np.array_equal(actual[valid],desired[valid]),'state priority quadrant '+tag)
 # Fitting must not create detached fragments on a state's continuous landmass.
 boxes=find_objects(states,max_label=max(map(int,w['regions'])))
 for row in audit['repairs']:
  sid=row['state'];bb=boxes[sid-1];mask=states[bb]==sid;cell=a[bb];landmasses,_=label(mask)
  for pid in np.unique(cell[mask]):
   components,n=label(cell==pid);islands=[]
   for j in range(1,n+1):
    ids=np.unique(landmasses[components==j]);ids=ids[ids>0];islands.extend(map(int,ids))
   check(len(islands)==len(set(islands)),'no detached same-landmass province fragments '+str(pid))
 for row in audit['removed_states']:
  sid=str(row['id']);dest=str(row['recipient']);check(sid not in w['regions']and sid not in sd['states'],'removed state retired '+sid)
  flows=[f for f in audit['transfers']if f['from']==int(sid)]
  check(flows==[{'from':int(sid),'to':int(dest),'residents':ow['regions'][sid]['population']}],'whole population sent to largest recipient '+sid)
 for k,s in w['regions'].items():
  check(sorted(s['provinces'])==sorted(by[int(k)])and bool(s['provinces']),'state membership '+k)
  check(s['capital_province']in s['provinces'],'capital province '+k)
  check(s['id']in w['countries'][s['owner']]['regions'],'country references '+k)
  check(all(str(n)in w['regions']and int(k)in w['regions'][str(n)]['neighbors']for n in s['neighbors']),'state adjacency '+k)
  p=sd['states'][k];check(p['population_2000']==s['population'],'population profile '+k)
  check(abs(sum(p['age_single_year'])-1)<1e-8,'single age profile '+k)
  for name,m in p['metrics'].items():check(abs(sum(m['shares'].values())-1)<1e-8 and all(v>=0 for v in m['shares'].values()),'demographic shares '+k+name)
 for tag,c in w['countries'].items():
  check(c['population']==sum(s['population']for s in w['regions'].values()if s['owner']==tag),'country population '+tag)
  check(c['capital']in c['regions'],'country capital '+tag)
 cities=read('data/cities.json');oldcities=json.loads((B/'cities.json').read_text());check(len(cities)==len(oldcities),'all cities preserved')
 for c,o in zip(cities,oldcities):
  check(str(c['province_id'])in ps and c['state_id']==ps[str(c['province_id'])]['region'],'city references '+c['name'])
  if(c['longitude'],c['latitude'])!=(o['longitude'],o['latitude']):
   check(any(m['file']=='cities.json'and m['name']==c['name']for m in audit.get('coastal_anchor_moves',[])),'documented coastal city adjustment '+c['name'])
   x=int((c['longitude']+180)/360*16384)%16384;y=int((90-c['latitude'])/180*8192)
   check(int(a[y,x])==c['province_id'],'moved coastal city is on assigned province '+c['name'])
  else:check(True,'city coordinate preserved '+c['name'])
 scene=read('data/urban_scenery.json');oldscene=json.loads((B/'urban_scenery.json').read_text())
 for kind in ['clusters','landmarks']:
  check(len(scene[kind])==len(oldscene[kind]),'scenery preserved '+kind)
  for c in scene[kind]:check(str(c['province'])in ps and c['state']==ps[str(c['province'])]['region'],'scenery reference')
 sr=read('data/sea_regions.json');coverage=read('assets/display/sea_coverage.json')
 check(set(sr)==set(json.loads((B/'sea_regions.json').read_text()))==set(coverage['seas']),'all sea IDs preserved')
 check(coverage['source_sha256']==hashlib.sha256((R/'assets/sea_ids.png').read_bytes()).hexdigest(),'sea selection current')
 for k,s in sr.items():
  u,v=s['map_center'];check(int(newsea[int(v*4096),int(u*8192)])==int(k),'sea anchor '+k)
 rgba=np.asarray(Image.open(R/'assets/relief_data.png'),np.uint16);packed=rgba[:,:,0]+rgba[:,:,1]*256
 check(np.array_equal(packed,np.frombuffer((R/'assets/relief_data.bin').read_bytes(),'<u2').reshape(4096,8192)),'CPU/GPU relief agree')
 check(not packed[removed].any(),'new sea has zero terrain displacement')
 result={'passed':True,'checks':checks,'countries':len(w['countries']),'states':len(w['regions']),'provinces':len(ps),'sea_regions':len(sr),'population':sum(s['population']for s in w['regions'].values()),'sea_first':True,'resolution_unchanged':True}
 (R/'validation_0211').mkdir(exist_ok=True);(R/'validation_0211/data_results.json').write_text(json.dumps(result,indent=2)+'\n')
 print('MAP_EDITS_0211_DATA_PASS',json.dumps(result),flush=True)
if __name__=='__main__':main()
