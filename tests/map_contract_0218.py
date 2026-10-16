"""Spatial checks on the actual prepared field, plus unchanged map data.
Run from any directory: python tests/map_contract_0218.py
"""
from pathlib import Path
import json,zlib,struct,hashlib
import numpy as np
from scipy.ndimage import distance_transform_edt,map_coordinates
import sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from build_boundary_hint import atlas
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((R/n).read_text())
def field(n,dtype,channels=1):
 b=(R/'assets/display'/n).read_bytes();w,h=struct.unpack('<II',b[:8]);v=np.frombuffer(zlib.decompress(b[8:]),dtype);assert v.size==w*h*channels;return v.reshape(h,w,channels)if channels>1 else v.reshape(h,w)
w=read('data/world.json');ps=read('data/provinces.json');contract=read('assets/display/map_contract.json')
assert len(ps)==13312 and len(w['regions'])==1305 and len(w['countries'])==227
assert sha(R/'data/provinces.json')=='a358f697663d9d168bd99e88c163d4be56c0395bb8cbf17d312354397213620c'
assert sha(R/'data/world.json')=='072f8067bf7c383717612e272156f55ada69fa3918cb29d1b20d692623371208'
assert sum(s['population']for s in w['regions'].values())==6144737528
assert contract['ownership_baked']is False and contract['land_selection_masks']is False
pq=field('boundary_pairs.bwd',np.uint8,4);d=field('boundary_distance.bwd','<f2').astype(np.float32);assert np.isfinite(d).all()and abs(d).max()<=16
pa=pq[:,:,0].astype(np.uint16)+pq[:,:,1].astype(np.uint16)*256;pb=pq[:,:,2].astype(np.uint16)+pq[:,:,3].astype(np.uint16)*256
valid=set(map(int,ps))|{0}
for top in range(0,4096,256):assert set(np.unique(pa[top:top+256]))<=valid and set(np.unique(pb[top:top+256]))<=valid
coast_index=read('assets/display/local_coasts.json');coast_bytes=(R/'assets/display/local_coasts.bwd').read_bytes();global_coast=field('coast_distance_0217.bwd','<f2').astype(np.float32)
source=atlas();lut=np.zeros(65536,np.uint16)
for p in ps.values():lut[p['id']]=p['region']
results=[]
for sid,extra in [(1813,[]),(253,[]),(1569,[]),(1568,[]),(1811,[]),(1813,[486])]:
 mapping=lut.copy()
 for other in extra:mapping[mapping==other]=sid
 ids=np.flatnonzero(mapping==sid);yy,xx=np.nonzero(np.isin(source,ids));t,b,l,r=yy.min()-4,yy.max()+5,xx.min()-4,xx.max()+5
 src=source[t:b,l:r];want=mapping[src]==sid;depth=distance_transform_edt(want);outside=distance_transform_edt(~want)
 y,x=np.mgrid[t:b,l:r];fx=(x+.5)/2-.5;fy=(y+.5)/2-.5;ix=np.floor(fx).astype(int);iy=np.floor(fy).astype(int)
 a=pa[iy,ix];bb=pb[iy,ix];agree=(a==pa[iy,ix+1])&(a==pa[iy+1,ix])&(a==pa[iy+1,ix+1])&(bb==pb[iy,ix+1])&(bb==pb[iy+1,ix])&(bb==pb[iy+1,ix+1])&((a>0)|(bb>0))
 signed=map_coordinates(d,[fy,fx],order=1,mode='nearest');pred=(mapping[a]==sid)&(signed>=0)|(mapping[bb]==sid)&(signed<=0);pred=np.where(agree,pred,want)
 # Coastal pairs use the single authoritative land/coast field, just as
 # physical terrain and shore ink do; no second independent coastal clip.
 cv=map_coordinates(global_coast,[fy,fx],order=1,mode='nearest')
 if str(sid)in coast_index['states']:
  rec=coast_index['states'][str(sid)];im=np.frombuffer(zlib.decompress(coast_bytes[rec[4]:rec[4]+rec[5]]),'<f2').reshape(rec[7],rec[6]).astype(float)
  u=(x+.5)/16384;v=(y+.5)/8192;cx=(u-rec[0])/rec[2];cy=(v-rec[1])/rec[3];inside=(cx>=0)&(cx<=1)&(cy>=0)&(cy<=1)
  local=map_coordinates(im,[cy*rec[7]-.5,cx*rec[6]-.5],order=1,mode='nearest');cv=np.where(inside,local,cv)
 coastal=agree&((a==0)|(bb==0));pred=np.where(coastal,((mapping[a]==sid)|(mapping[bb]==sid))&(cv>.5),pred)
 missing=int(np.sum(want&(depth>2)&~pred));ghost=int(np.sum(~want&(outside>2)&pred))
 if missing or ghost:
  bad=(want&(depth>2)&~pred)|(~want&(outside>2)&pred)
  for by,bx in zip(*np.nonzero(bad)):
   print('BAD',sid,'at',int(x[by,bx]),int(y[by,bx]),'source',int(src[by,bx]),'pair',int(a[by,bx]),int(bb[by,bx]),'distance',float(signed[by,bx]),'depth',float(depth[by,bx]),float(outside[by,bx]),flush=True)
 assert missing==0 and ghost==0,(sid,extra,missing,ghost)
 results.append({'state':sid,'merge_with':extra,'missing_deep_interior_cells':missing,'ghost_exterior_cells':ghost})
# Ownership changes only alter classification of the same province pairs.
own=np.zeros(8192,np.uint16)
for k,s in w['regions'].items():own[int(k)]=w['countries'][s['owner']]['index']
sa=lut[pa];sb=lut[pb];before=(own[sa]!=own[sb])&(own[sa]>0)&(own[sb]>0);own[1813]=w['countries']['JAP']['index'];after=(own[sa]!=own[sb])&(own[sa]>0)&(own[sb]>0);changed=int(np.sum(before!=after));assert changed>0
out={'passed':True,'geography_unchanged_from_0217':True,'countries':227,'states':1305,'provinces':13312,'spatial_cases':results,'national_classification_cells_changed_on_transfer':changed,'distance_field_finite':True,'universal_fields_gpu_bytes':201326592,'hint_gpu_bytes':33554432,'native_windows_tested':False}
target=R/'validation_0218/data_results.json';target.parent.mkdir(exist_ok=True);target.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
