"""Derive sea neighbours, interior anchors and highlight fields from sea IDs.

All windows use the same native coordinate space as the land/coast shaders.
The source hash is checked by the shared map build, including sea-only edits.
"""
from pathlib import Path
import json,hashlib,io,zlib
import numpy as np
from PIL import Image
from scipy.ndimage import find_objects,distance_transform_edt
from build_display_0217 import field
from map_dimensions import W,H
R=Path(__file__).resolve().parents[1];OUT=R/'assets/display'
def build():
 source=R/'assets/sea_ids.png';rgb=np.asarray(Image.open(source).convert('RGB'),np.uint16);a=rgb[:,:,0]+rgb[:,:,1]*256;hh,ww=a.shape
 records=json.loads((R/'data/sea_regions.json').read_text());assert set(map(int,np.unique(a)))-{0}==set(map(int,records))
 neighbours={k:set()for k in records}
 for l,r in [(a[:,:-1],a[:,1:]),(a[:-1],a[1:]),(a[:,-1:],a[:,:1])]:
  valid=(l!=r)&(l>0)&(r>0);codes=np.minimum(l[valid],r[valid]).astype(np.uint32)*65536+np.maximum(l[valid],r[valid])
  for code in np.unique(codes):
   x,y=divmod(int(code),65536);neighbours[str(x)].add(y);neighbours[str(y)].add(x)
 for k,rec in records.items():
  for passage in rec.get('passages',[]):
   other=int(passage['neighbor']);assert str(other)in records;neighbours[k].add(other);neighbours[str(other)].add(int(k))
 boxes=find_objects(a,max_label=max(map(int,records)));pack=io.BytesIO();index={'format':'RH','data_file':'sea_coverage.bwd','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'native_size':[W,H],'seas':{}}
 for j,(key,rec)in enumerate(records.items()):
  sid=int(key);bb=boxes[sid-1];t,l=bb[0].start,bb[1].start;mask=a[bb]==sid
  dist=distance_transform_edt(mask);y,x=np.unravel_index(dist.argmax(),mask.shape);rec['map_center']=[(l+x+.5)/ww,(t+y+.5)/hh];rec['neighbors']=sorted(neighbours[key])
  # Wrap a seam-spanning region to its shortest longitudinal window.
  if mask.shape[1]>ww*.55:
   cols=np.flatnonzero(mask.any(0))+l;gaps=np.diff(np.r_[cols,cols[0]+ww]);gap=int(gaps.argmax());l=int(cols[(gap+1)%len(cols)]);mask=a[bb[0],(np.arange(ww-int(gaps[gap])+1)+l)%ww]==sid
  factor=W//ww;assert W==ww*factor and H==hh*factor;native=np.repeat(np.repeat(mask,factor,axis=0),factor,axis=1);rect,data=field(native,t*factor,l*factor,1536);blob=zlib.compress(data.tobytes(),6);index['seas'][key]=rect+[pack.tell(),len(blob),data.shape[1],data.shape[0]];pack.write(blob)
  if j%20==0:print('SEA_COVERAGE',j,len(records),flush=True)
 (R/'data/sea_regions.json').write_text(json.dumps(records,separators=(',',':'),ensure_ascii=False)+'\n');(OUT/'sea_coverage.bwd').write_bytes(pack.getvalue());(OUT/'sea_coverage.json').write_text(json.dumps(index,separators=(',',':'))+'\n')
 print('SEA_COVERAGE_READY',len(records),len(pack.getvalue()),flush=True)
if __name__=='__main__':build()
