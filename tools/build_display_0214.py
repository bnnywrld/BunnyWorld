"""Prepare merged-State and sea SDFs. Shared SDF samples drive fill and line.
Exact categorical IDs and camera-motion geometry remain unchanged.
"""
from pathlib import Path
import json,zlib,struct,io
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt,find_objects
from build_display_0212 import ROOT,OUT,W,H,tile,protect_anchor,atlas
Image.MAX_IMAGE_PIXELS=None
w=json.loads((ROOT/'data/world.json').read_text());ps=json.loads((ROOT/'data/provinces.json').read_text());a=atlas();lookup=np.zeros(65536,np.uint16)
for p in ps.values():lookup[p['id']]=p['region']
s=lookup[a];index=json.loads((OUT/'selection_distance.json').read_text());index['version']='0.2.0.14';index['seas']={}
# Append prepared tiles instead of recomputing unchanged province masks.
f=io.BytesIO((OUT/'selection_distance.bwd').read_bytes());f.seek(0,2)
with f:
 for sid in [363,1826,732,1568,894,1813,687]:
  yy,xx=np.nonzero(s==sid);top,left=int(yy.min()),int(xx.min());mask=s[top:int(yy.max())+1,left:int(xx.max())+1]==sid
  rect,data=tile(mask,top,left,1536);data=protect_anchor(data,rect,w['regions'][str(sid)]['map_center']);b=zlib.compress(data.tobytes(),6);index['states'][str(sid)]=rect+[f.tell(),len(b),data.shape[1],data.shape[0]];f.write(b);print('STATE_FIELD',sid,flush=True)
 for sid in [738,1753,926,928,1814,685]:index['states'].pop(str(sid),None)
 rgb=np.asarray(Image.open(ROOT/'assets/sea_ids.png'));sea=rgb[:,:,0].astype(np.uint16)+rgb[:,:,1].astype(np.uint16)*256;zero=sea==0
 distances,nearest=distance_transform_edt(zero,return_indices=True);edge=zero&(distances<=2.5);sea[edge]=sea[nearest[0][edge],nearest[1][edge]];del distances,nearest,zero,edge
 records=json.loads((ROOT/'data/sea_regions.json').read_text());boxes=find_objects(sea,max_label=int(sea.max()))
 for key in records:
  sid=int(key);bb=boxes[sid-1]
  if bb is None:continue
  top,left=bb[0].start*2,bb[1].start*2;part=np.repeat(np.repeat(sea[bb]==sid,2,axis=0),2,axis=1)
  # Keep dateline regions in a compact wrapped window.
  if part.shape[1]>W*.55:
   cols=np.flatnonzero(part.any(axis=0))+left;gaps=np.diff(np.r_[cols,cols[0]+W]);g=int(gaps.argmax());left=int(cols[(g+1)%len(cols)]);width=W-int(gaps[g])+1
   part=np.repeat(sea[bb[0],((np.arange(width)+left)//2)%(W//2)]==sid,2,axis=0)
  rect,data=tile(part,top,left,1536);b=zlib.compress(data.tobytes(),6);index['seas'][key]=rect+[f.tell(),len(b),data.shape[1],data.shape[0]];f.write(b);print('SEA_FIELD',key,flush=True)
 (OUT/'selection_distance.bwd').write_bytes(f.getvalue())
(OUT/'selection_distance.json').write_text(json.dumps(index,separators=(',',':')))
print('DISPLAY_0214_READY',len(index['states']),len(index['provinces']),len(index['seas']),flush=True)
