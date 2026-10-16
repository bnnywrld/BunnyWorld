"""Prepared close-view coast windows, streamed on selection (never camera travel)."""
from pathlib import Path
import json,zlib,struct
import numpy as np
from scipy.ndimage import find_objects,map_coordinates
from shapely.geometry import Polygon,box
from shapely.strtree import STRtree
from build_display_0212 import ROOT,OUT,W,H,atlas,rings,segments,distance,inside,encode

def build():
 a=atlas();s=np.load(ROOT/'tools/cartography/grouped_atlas_022r2.npz')['regions'];world=json.loads((ROOT/'data/world.json').read_text());ps=json.loads((ROOT/'data/provinces.json').read_text())
 paths=rings(a>0);model=segments(paths,True);tree=STRtree([Polygon(p) for p in paths]);blob=(OUT/'coast_distance.bwd').read_bytes();cw,ch=struct.unpack('<II',blob[:8]);coarse=np.frombuffer(zlib.decompress(blob[8:]),np.uint8).reshape(ch,cw)
 index={'states':{},'provinces':{}}
 with (OUT/'local_coasts.bwd').open('wb') as f:
  for scope,arr,records in [('states',s,world['regions']),('provinces',a,ps)]:
   boxes=find_objects(arr,max_label=int(arr.max()))
   for j,key in enumerate(records):
    bb=boxes[int(key)-1];top=max(0,bb[0].start-5);bottom=min(H,bb[0].stop+5);left=max(0,bb[1].start-5);right=min(W,bb[1].stop+5)
    if right-left>W*.55 or not np.any(a[top:bottom,left:right]==0):continue
    origin=np.array([left,top],float);extent=np.array([right-left,bottom-top],float);step=max(.25,max(extent)/512);width=int(np.ceil(extent[0]/step));height=int(np.ceil(extent[1]/step));extent=np.array([width,height])*step
    yy,xx=np.meshgrid(top+(np.arange(height)+.5)*step,left+(np.arange(width)+.5)*step,indexing='ij')
    rough=map_coordinates(coarse,[yy/2-.5,xx/2-.5],order=1,mode='nearest');band=(rough>8)&(rough<247)
    if not band.any():continue
    chosen=tree.query(box(left,top,left+extent[0],top+extent[1]));local=[paths[int(k)] for k in chosen]
    land=inside(local,(height,width),origin,step);data=np.where(land,255,0).astype(np.uint8)
    points=np.column_stack([xx[band],yy[band]]);data[band]=encode(np.abs(distance(points,model,step,True))*np.where(land[band],1.,-1.))
    packed=zlib.compress(data.tobytes(),7);record=(origin/[W,H]).tolist()+(extent/[W,H]).tolist()+[f.tell(),len(packed),width,height];f.write(packed);index[scope][key]=record
    if j%500==0:print('LOCAL_COAST',scope,j,flush=True)
 (OUT/'local_coasts.json').write_text(json.dumps(index,separators=(',',':')));print('LOCAL_COAST_COMPLETE',len(index['states']),len(index['provinces']),flush=True)
if __name__=='__main__':build()
