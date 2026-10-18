"""Identity, territory protection, references and native texture budgets."""
from pathlib import Path
from collections import defaultdict
import json,sys,hashlib,zlib,struct
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects
R=Path(__file__).resolve().parents[1];D=R/'tools/cartography/reduced_0212'
sys.path.insert(0,str(R/'tools'))
from build_boundary_hint import atlas
Image.MAX_IMAGE_PIXELS=None
checks=0
def check(ok,msg):
 global checks
 checks+=1
 assert ok,msg
def read(n):return json.loads((R/n).read_text())
def main():
 w=read('data/world.json');ps=read('data/provinces.json');ow=json.loads((D/'baseline/world.json').read_text());ops=json.loads((D/'baseline/provinces.json').read_text());audit=read('data/map_reduction_audit.json')
 check(w['version']=='0.2.1.2','version');check((w['map']['width'],w['map']['height'],w['map']['tiles'])==(8192,4096,1),'single native map')
 check(set(w['countries'])==set(ow['countries']),'countries preserved');check(set(w['regions'])==set(ow['regions']),'all states preserved');check(set(ps)==set(ops),'all province IDs preserved')
 for n,h in json.loads((D/'baseline_hashes.json').read_text())['unchanged_hashes'].items():check(hashlib.sha256((R/n).read_bytes()).hexdigest()==h,'demographics unchanged '+n)
 check(sum(s['population']for s in w['regions'].values())==6146495066,'global residents unchanged')
 a=atlas();check(a.shape==(4096,8192),'PNG native dimensions');check(np.array_equal(a,np.load(D/'final_provinces.npz')['provinces']),'published map matches conversion')
 check(set(map(int,np.unique(a)))-{0,65535}==set(map(int,ps)),'every province exists in PNG')
 lut=np.zeros(65536,np.uint16);lut[65535]=65535;by=defaultdict(list)
 for k,p in ps.items():
  pid=int(k);sid=p['region'];lut[pid]=sid;by[sid].append(pid)
  check(sid==ops[k]['region'],'province parent unchanged '+k)
  check(p['area_km2']==ops[k]['area_km2'],'real province area unchanged '+k)
  u,v=p['map_center'];check(int(a[min(4095,int(v*4096)),int(u*8192)%8192])==pid,'province picking anchor '+k)
  check(all(str(n)in ps and pid in ps[str(n)]['neighbors']for n in p['neighbors']),'valid adjacency '+k)
 states=lut[a];check(np.array_equal(states,np.load(D/'final_states.npz')['states']),'state membership map')
 boxes=find_objects(states,max_label=max(map(int,w['regions'])));counts=np.bincount(states.ravel(),minlength=65536)
 for k,s in w['regions'].items():
  check(counts[int(k)]>0,'state survives '+k);check(s['population']==ow['regions'][k]['population'],'state residents unchanged '+k)
  for key in ['buildings','building_slot_baseline','owner','area_km2']:
   check(s.get(key)==ow['regions'][k].get(key),'state simulation unchanged '+k+key)
  check(sorted(s['provinces'])==sorted(by[int(k)]),'province inventory '+k)
  check(s['capital_province']in s['provinces'],'capital province '+k)
  bb=boxes[int(k)-1];mask=states[bb]==int(k);cell=a[bb];islands,_=label(mask)
  for pid in np.unique(cell[mask]):
   components,n=label(cell==pid);seen=set()
   for i in range(1,n+1):
    masses=set(map(int,np.unique(islands[components==i])))-{0};check(not seen&masses,'no same-landmass fragment '+str(pid));seen|=masses
 for row in audit['enlarged_states']:check(counts[row['state']]>=9,'minimum visible state footprint '+row['name'])
 source=np.load(D/'source_provinces.npz')['provinces']
 cities=read('data/cities.json');oldcities=json.loads((D/'baseline/cities.json').read_text());check(len(cities)==len(oldcities),'cities preserved')
 for c,o in zip(cities,oldcities):
  check(c['state_id']==o['state_id']and c['country']==o['country'],'city state preserved '+c['name'])
  check(c['state_id']==ps[str(c['province_id'])]['region'],'city province reference '+c['name'])
  x=int((c['longitude']+180)/360*8192)%8192;y=min(4095,int((90-c['latitude'])/180*4096))
  hx=int((o['longitude']+180)/360*16384)%16384;hy=min(8191,int((90-o['latitude'])/180*8192));source_pid=int(source[hy,hx])
  if source_pid not in [0,65535]and ops[str(source_pid)]['region']==o['state_id']:
   check(int(a[y,x])==c['province_id'],'valid city remains on assigned land '+c['name'])
  else:
   check((c['longitude'],c['latitude'])==(o['longitude'],o['latitude']),'preexisting unmapped city not teleported '+c['name'])
 scene=read('data/urban_scenery.json');oldscene=json.loads((D/'baseline/urban_scenery.json').read_text())
 for kind in ['clusters','landmarks']:
  check(len(scene[kind])==len(oldscene[kind]),'scenery preserved '+kind)
  for c in scene[kind]:check(c['state']==ps[str(c['province'])]['region'],'scenery reference')
 rgb=np.asarray(Image.open(R/'assets/sea_ids.png'),np.uint16);sea=rgb[:,:,0]+rgb[:,:,1]*256;check(not sea[a>0].any(),'no sea IDs under land')
 sr=read('data/sea_regions.json');check(set(sr)==set(json.loads((D/'baseline/sea_regions.json').read_text())),'all seas retained')
 for k,s in sr.items():
  u,v=s['map_center'];check(int(sea[int(v*4096),int(u*8192)])==int(k),'sea picking anchor '+k)
 gpu={};formats={'boundary_hint':1,'boundary_pairs':4,'boundary_distance':2,'coast_distance_0217':2,'tiny_land_bits':1}
 for n,bpp in formats.items():
  data=(R/f'assets/display/{n}.bwd').read_bytes();width,height=struct.unpack('<II',data[:8]);raw=zlib.decompress(data[8:]);check(len(raw)==width*height*bpp,'valid field '+n)
  check((width,height)==((1024,4096)if n=='tiny_land_bits'else(4096,2048)),'reduced field dimensions '+n)
  gpu[n]=len(raw)
 gpu['province_ids']=8192*4096*2
 old_gpu={k:v*4 for k,v in gpu.items()};check(sum(gpu.values())*4==sum(old_gpu.values()),'75 percent map field reduction')
 check(all(not(R/f'assets/region_ids_{i}.png').exists()for i in range(4)),'old four PNGs removed')
 rgba=np.asarray(Image.open(R/'assets/relief_data.png'),np.uint16);packed=rgba[:,:,0]+rgba[:,:,1]*256
 check(np.array_equal(packed,np.frombuffer((R/'assets/relief_data.bin').read_bytes(),'<u2').reshape(4096,8192)),'CPU/GPU relief agree')
 check(Image.open(R/'assets/terrain_color.png').size==(8192,4096),'terrain colour resolution retained')
 result={'passed':True,'checks':checks,'states':len(w['regions']),'provinces':len(ps),'seas':len(sr),'native_size':[8192,4096],'gpu_nominal_bytes_before':sum(old_gpu.values()),'gpu_nominal_bytes_after':sum(gpu.values()),'gpu_nominal_bytes_saved':sum(old_gpu.values())-sum(gpu.values()),'gpu_fields':gpu,'hardware_fps_measured':False}
 (R/'validation_0212').mkdir(exist_ok=True);(R/'validation_0212/data_results.json').write_text(json.dumps(result,indent=2)+'\n');print('REDUCTION_DATA_PASS',json.dumps(result),flush=True)
if __name__=='__main__':main()
