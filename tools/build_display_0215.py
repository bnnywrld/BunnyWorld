"""Prepare all selection masks from current picking IDs; bounded smoothing.
EDT runs on prepared contour coverage, with no per-camera geography decoding.
"""
from pathlib import Path
import io,json,zlib,sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.ndimage import find_objects,distance_transform_edt,label
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
from skimage.measure import find_contours
from build_display_0212 import ROOT,OUT,W,H,inside,encode,protect_anchor
from display_shape_0215 import smooth
def field(mask,top,left,limit):
 paths=[]
 for c in find_contours(np.pad(mask,1),.5,fully_connected='high'):
  p=np.column_stack([c[:,1]+left-1,c[:,0]+top-1]);p=smooth(p)
  if len(p)>3:paths.append(p)
 hh,ww=mask.shape;origin=np.array([left-5,top-5],float);extent=np.array([ww+10,hh+10],float);step=max(.5,float(max(extent))/limit)
 width,height=np.ceil(extent/step).astype(int);extent=np.array([width,height])*step
 cover=inside(paths,(int(height),int(width)),origin,step)
 # Distances refer to the half-way contour between adjacent coverage cells.
 d=np.where(cover,distance_transform_edt(cover)-.5,.5-distance_transform_edt(~cover));data=encode(d)
 rect=(origin/[W,H]).tolist()+(extent/[W,H]).tolist();return rect,data
def main():
 ps=json.loads((ROOT/'data/provinces.json').read_text());world=json.loads((ROOT/'data/world.json').read_text());a=np.load(ROOT/'tools/cartography/province_atlas_0215.npz')['provinces'];lut=np.zeros(65536,np.uint16)
 for p in ps.values():lut[p['id']]=p['region']
 states=lut[a];old=json.loads((OUT/'selection_distance.json').read_text());oldpack=(OUT/'selection_distance.bwd').read_bytes();index={'version':'0.2.0.15','native_size':[W,H],'distance_encoding':{'zero':127.5,'units_per_pixel':24},'states':{},'provinces':{},'seas':{}};pack=io.BytesIO()
 jobs=[] if '--seas-only'in sys.argv else [('states',states,world['regions'],1024)]if '--states-only'in sys.argv else [('states',states,world['regions'],1024),('provinces',a,ps,512)]
 if '--states-only'in sys.argv:
  for key,r in old['provinces'].items():
   b=oldpack[r[4]:r[4]+r[5]];index['provinces'][key]=r[:4]+[pack.tell(),len(b),r[6],r[7]];pack.write(b)
 if not jobs:
  for scope in ['states','provinces']:
   for key,r in old[scope].items():
    b=oldpack[r[4]:r[4]+r[5]];index[scope][key]=r[:4]+[pack.tell(),len(b),r[6],r[7]];pack.write(b)
 for scope,arr,records,limit in jobs:
  boxes=find_objects(arr,max_label=max(map(int,records)))
  def prepare(key):
   sid=int(key);bb=boxes[sid-1];assert bb is not None,(scope,sid)
   top,left=bb[0].start,bb[1].start;part=arr[bb]==sid
   if part.shape[1]>W*.55:
    cols=np.flatnonzero(part.any(axis=0))+left;gaps=np.diff(np.r_[cols,cols[0]+W]);g=int(gaps.argmax());left=int(cols[(g+1)%len(cols)]);width=W-int(gaps[g])+1;part=arr[bb[0],(np.arange(width)+left)%W]==sid
   rect,data=field(part,top,left,limit);data=protect_anchor(data,rect,records[key]['map_center'])
   if scope=='states':
    components,count=label(part,np.ones((3,3),bool))
    if count>1:
     component_boxes=find_objects(components)
     for component,box in enumerate(component_boxes,1):
      yy,xx=np.nonzero(components[box]==component)
      if len(xx)<2:continue
      j=int(np.argmin((xx-xx.mean())**2+(yy-yy.mean())**2));uv=[((xx[j]+box[1].start+left+.5)/W)%1,(yy[j]+box[0].start+top+.5)/H];data=protect_anchor(data,rect,uv)
   blob=zlib.compress(data.tobytes(),6);return key,rect,blob,data.shape
  with ThreadPoolExecutor(max_workers=3)as executor:
   for j,(key,rect,blob,shape)in enumerate(executor.map(prepare,records)):
    index[scope][key]=rect+[pack.tell(),len(blob),shape[1],shape[0]];pack.write(blob)
    if j%500==0:print('FIELDS',scope,j,flush=True)
 # Selected sea regions use the same bounded contour rule as land.
 rgb=np.asarray(Image.open(ROOT/'assets/sea_ids.png'));sea=rgb[:,:,0].astype(np.uint16)+rgb[:,:,1].astype(np.uint16)*256;zero=sea==0
 dist,nearest=distance_transform_edt(zero,return_indices=True);edge=zero&(dist<=2.5);sea[edge]=sea[nearest[0][edge],nearest[1][edge]];del rgb,zero,dist,nearest,edge
 boxes=find_objects(sea,max_label=int(sea.max()))
 for key in json.loads((ROOT/'data/sea_regions.json').read_text()):
  sid=int(key);bb=boxes[sid-1];top,left=bb[0].start*2,bb[1].start*2;part=np.repeat(np.repeat(sea[bb]==sid,2,axis=0),2,axis=1)
  if part.shape[1]>W*.55:
   cols=np.flatnonzero(part.any(axis=0))+left;gaps=np.diff(np.r_[cols,cols[0]+W]);g=int(gaps.argmax());left=int(cols[(g+1)%len(cols)]);width=W-int(gaps[g])+1;part=np.repeat(sea[bb[0],((np.arange(width)+left)//2)%(W//2)]==sid,2,axis=0)
  rect,data=field(part,top,left,1536);b=zlib.compress(data.tobytes(),6);index['seas'][key]=rect+[pack.tell(),len(b),data.shape[1],data.shape[0]];pack.write(b)
 data=pack.getvalue();(OUT/'selection_distance.bwd').write_bytes(data);assert (OUT/'selection_distance.bwd').stat().st_size==len(data)
 (OUT/'selection_distance.json').write_text(json.dumps(index,separators=(',',':')))
 print('FIELDS_READY',len(data),len(index['states']),len(index['provinces']),flush=True)
if __name__=='__main__':main()
