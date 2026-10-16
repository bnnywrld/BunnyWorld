"""Single map build entry point. Province PNG IDs + data/provinces.json are
canonical. State membership is resolved from JSON, never an old grouped raster.
Ownership is intentionally NOT an input to any prepared visual shape.
Usage: python tools/build_map.py [--check] [--godot /path/to/godot]
"""
from pathlib import Path
import argparse,json,hashlib,zlib,io,subprocess,shutil,sys,re
R=Path(__file__).resolve().parents[1];OUT=R/'assets/display'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inputs(ps):
 return {'tiles':{f'assets/region_ids_{i}.png':sha(R/f'assets/region_ids_{i}.png')for i in range(4)},'membership':sorted([[int(k),int(v['region'])]for k,v in ps.items()]),'microstate':sha(R/'data/microstate_geometry.json')}
def sea_pack():
 target=OUT/'sea_coverage.json'
 if target.exists():return
 old=json.loads((OUT/'selection_distance.json').read_text());blob=(OUT/old['data_file']).read_bytes();out=io.BytesIO();records={}
 for k,r in old['seas'].items():
  raw=zlib.decompress(blob[r[4]:r[4]+r[5]]);assert len(raw)==r[6]*r[7]*2
  b=zlib.compress(raw,6);records[k]=r[:4]+[out.tell(),len(b),r[6],r[7]];out.write(b)
 (OUT/'sea_coverage.bwd').write_bytes(out.getvalue());target.write_text(json.dumps({'format':'RH','data_file':'sea_coverage.bwd','seas':records},separators=(',',':')))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');ap.add_argument('--godot');ap.add_argument('--force',action='store_true');args=ap.parse_args()
 ps=json.loads((R/'data/provinces.json').read_text());world=json.loads((R/'data/world.json').read_text());version=re.search(r'config/version="([^"]+)"',(R/'project.godot').read_text()).group(1);source=inputs(ps);cp=OUT/'map_contract.json';old=json.loads(cp.read_text())if cp.exists()else{}
 members={}
 for k,p in ps.items():members.setdefault(str(p['region']),[]).append(int(k))
 for sid,s in world['regions'].items():
  assert sorted(s['provinces'])==sorted(members.get(sid,[])),f'State {sid}: membership lists disagree'
 assert all(str(p['region'])in world['regions']for p in ps.values())
 if args.check:
  assert old.get('inputs')==source,'Map topology changed. Run python tools/build_map.py --godot <Godot executable>'
  for n,h in old['resources'].items():assert sha(R/n)==h,f'Map resource mismatch: {n}'
  print('MAP_BUILD_CONTRACT_PASS',len(ps),'provinces; ownership-independent',flush=True);return
 import numpy as np
 from PIL import Image
 from build_boundary_hint import atlas,build as build_hint
 from build_boundary_field import build as build_field
 Image.MAX_IMAGE_PIXELS=None
 resource_mismatch=bool(old)and any(not(R/n).is_file()or sha(R/n)!=h for n,h in old.get('resources',{}).items())
 changed=args.force or bool(old)and old.get('inputs')!=source or resource_mismatch
 if changed:
  godot=args.godot or shutil.which('godot')or shutil.which('godot4')
  assert godot,'Geography changed: supply --godot <Godot 4.5.1 executable> to rebuild all dependent resources.'
  a=atlas();ids=set(np.unique(a))- {0,65535};assert ids==set(map(int,ps)),'Raster province IDs differ from data/provinces.json'
  lut=np.zeros(65536,np.uint16);lut[65535]=8191
  for p in ps.values():lut[p['id']]=p['region']
  # Derive adjacency from canonical pixels too. Old neighbor tables must
  # never decide which current edges exist after a merge or split.
  neighbors={k:set()for k in ps};state_neighbors={k:set()for k in world['regions']}
  for top in range(0,8192,128):
   for left,right in [(a[top:top+128,:-1],a[top:top+128,1:]),(a[top:min(8191,top+128)],a[top+1:min(8192,top+129)])]:
    valid=(left>0)&(right>0)&(left!=right)&(left!=65535)&(right!=65535)
    codes=np.minimum(left[valid],right[valid]).astype(np.uint32)*65536+np.maximum(left[valid],right[valid])
    for code in np.unique(codes):
     l,r=divmod(int(code),65536);neighbors[str(l)].add(r);neighbors[str(r)].add(l);sl,sr=ps[str(l)]['region'],ps[str(r)]['region']
     if sl!=sr:state_neighbors[str(sl)].add(sr);state_neighbors[str(sr)].add(sl)
  for k,p in ps.items():p['neighbors']=sorted(neighbors[k])
  for k,state in world['regions'].items():state['neighbors']=sorted(state_neighbors[k])
  (R/'data/provinces.json').write_text(json.dumps(ps,separators=(',',':'),ensure_ascii=False))
  (R/'data/world.json').write_text(json.dumps(world,separators=(',',':'),ensure_ascii=False))
  np.savez_compressed(R/'tools/cartography/map_provinces.npz',provinces=a)
  np.savez_compressed(R/'tools/cartography/grouped_atlas_022r2.npz',regions=lut[a])
  # Every derivative is rebuilt together; no per-area correction switches.
  subprocess.run([sys.executable,str(R/'tools/build_map_boundaries.py')],cwd=R,check=True)
  subprocess.run([godot,'--headless','--path',str(R),'--script','res://tools/compile_boundaries.gd'],cwd=R,check=True)
  subprocess.run([sys.executable,str(R/'tools/build_display_0217.py'),'--coast-only','--atlas-path',str(R/'tools/cartography/map_provinces.npz'),'--skip-legacy-shade'],cwd=R,check=True)
 if changed or not (OUT/'boundary_hint.bwd').exists():build_hint()
 if changed or not (OUT/'boundary_distance.bwd').exists():build_field()
 sea_pack()
 # The compatibility PNG is an output too, not an independent authority.
 lut=np.zeros((256,256,3),np.uint8);lut[255,255,:2]=[255,31]
 for p in ps.values():i=int(p['id']);sid=int(p['region']);lut[i//256,i%256]=[sid&255,sid>>8,int(p.get('local_index',0))&255]
 old_png=np.asarray(Image.open(R/'assets/province_index.png').convert('RGB'))
 if not np.array_equal(old_png,lut):Image.fromarray(lut).save(R/'assets/province_index.png')
 resources=['assets/display/boundary_hint.bwd','assets/display/boundary_pairs.bwd','assets/display/boundary_distance.bwd','assets/display/sea_coverage.json','assets/display/sea_coverage.bwd','assets/display/coast_distance_0217.bwd','assets/display/local_coasts.json','assets/display/local_coasts.bwd','assets/land_boundaries.res','assets/province_boundaries.res','assets/micro_boundaries.res']
 decoded=[hashlib.sha256(Image.open(R/f'assets/region_ids_{i}.png').convert('RGB').tobytes()).hexdigest()for i in range(4)]
 contract={'schema':1,'version':version,'geography_version':world['version'],'province_count':len(ps),'state_count':len(world['regions']),'inputs':source,'membership':source['membership'],'decoded_tiles':decoded,'resources':{n:sha(R/n)for n in resources},'ownership_baked':False,'land_selection_masks':False,'coverage':'Shared smoothed curve distances and live province-pair membership; cubic junction fallback'}
 cp.write_text(json.dumps(contract,separators=(',',':'))+'\n')
 active=resources+['assets/display/map_contract.json','assets/display/country_glyphs.png','assets/display/country_glyphs.json','assets/display/FONT_LICENSE.txt','assets/display/tiny_land_bits.bwd']
 bundle={'version':version,'geography_version':world['version'],'files':{n:sha(R/n)for n in active}}
 (OUT/'BUNDLE.json').write_text(json.dumps(bundle,indent=2)+'\n')
 geo_path=R/'data/geography_bundle.json'
 if geo_path.exists():
  geo=json.loads(geo_path.read_text());geo['files']={n:sha(R/n)for n in geo['files']};geo_path.write_text(json.dumps(geo,indent=2)+'\n')
 if changed:
  subprocess.run([sys.executable,str(R/'tools/package_repository_geography.py')],cwd=R,check=True)
 print('MAP_BUILD_READY',len(ps),'provinces; dynamic State/country coverage',flush=True)
if __name__=='__main__':main()
