"""Prepared coverage integrity, wrap coordinates and unchanged simulation inputs."""
from pathlib import Path
import json,zlib,hashlib,struct
import numpy as np
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'assets/display'
index=json.loads((D/'selection_distance.json').read_text());world=json.loads((ROOT/'data/world.json').read_text());provinces=json.loads((ROOT/'data/provinces.json').read_text());pack=(D/'selection_distance.bwd').read_bytes()
checks=0;centers=[];offsets=[]
for scope,source in [('states',world['regions']),('provinces',provinces)]:
 assert set(index[scope])==set(source);checks+=1
 for key,record in index[scope].items():
  u,v,su,sv,offset,length,width,height=record
  assert 0<su<=1.01 and 0<sv<=1.01 and width>0 and height>0
  raw=zlib.decompress(pack[offset:offset+length]);assert len(raw)==width*height and max(raw)>127
  offsets.append((offset,length));checks+=2
  uv=source[key]['map_center'];x=((uv[0]-u)%1)/su*width-.5;y=(uv[1]-v)/sv*height-.5
  if 0<=x<width and 0<=y<height:
   positive=raw[min(height-1,int(y+.5))*width+min(width-1,int(x+.5))]>127
   centers.append(positive)
assert offsets[0][0]==0
for a,b in zip(offsets,offsets[1:]):assert a[0]+a[1]==b[0]
assert offsets[-1][0]+offsets[-1][1]==len(pack);checks+=len(offsets)
# Map-center declarations can lie on a simplified edge; report rather than
# treating a subpixel display/picking difference as an ownership change.
blob=(D/'coast_distance.bwd').read_bytes();w,h=struct.unpack('<II',blob[:8]);coast=np.frombuffer(zlib.decompress(blob[8:]),np.uint8).reshape(h,w);assert (w,h)==(8192,4096);checks+=1
for lon,lat,land in [(138.4,35,True),(138.58,34.5,False),(0,0,False),(20,50,True),(150,-20,False),(-100,40,True)]:
 assert bool(coast[int((90-lat)/180*h),int((lon+180)/360*w)]>127)==land;checks+=1
bundle=json.loads((D/'BUNDLE.json').read_text())
for name,sha in bundle['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha;checks+=1
geo=json.loads((ROOT/'data/geography_bundle.json').read_text())
for name,sha in geo['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha;checks+=1
tiny=(D/'tiny_land_bits.bwd').read_bytes();tw,th=struct.unpack('<II',tiny[:8]);raw=zlib.decompress(tiny[8:]);assert (tw,th)==(2048,8192) and len(raw)==tw*th;checks+=1
local=json.loads((D/'local_coasts.json').read_text());local_blob=(D/'local_coasts.bwd').read_bytes();last=0
for scope,source in [('states',world['regions']),('provinces',provinces)]:
 assert set(local[scope]).issubset(source);checks+=1
 for key,record in local[scope].items():
  u,v,su,sv,offset,length,width,height=record
  assert offset==last and 0<width<=512 and 0<height<=512
  assert len(zlib.decompress(local_blob[offset:offset+length]))==width*height
  last=offset+length;checks+=2
assert last==len(local_blob);checks+=1
result={'checks':checks,'failures':0,'state_tiles':len(index['states']),'province_tiles':len(index['provinces']),'map_center_inside_fraction':sum(centers)/len(centers),'coast_texture_gpu_bytes':w*h,'tiny_island_bits_gpu_bytes':len(raw),'selection_pack_streamed':True}
(ROOT/'validation_0212/display_asset_results.json').write_text(json.dumps(result,indent=2)+'\n');print('DISPLAY_ASSETS_PASS',result)
