"""Final-ID coverage: analytic polyline distances, half-float fields and no stale
coast windows. All preprocessing is offline; camera movement changes uniforms.
"""
from pathlib import Path
import json,io,zlib,struct,hashlib,sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image
from scipy.ndimage import find_objects,distance_transform_edt,binary_dilation,gaussian_filter
from skimage.measure import find_contours
from build_display_0212 import inside,segments,distance
from display_shape_0215 import smooth
R=Path(__file__).resolve().parents[1];OUT=R/'assets/display';W,H=16384,8192;Image.MAX_IMAGE_PIXELS=None

def paths_for(mask,top,left):
 paths=[]
 for c in find_contours(np.pad(mask,1),.5,fully_connected='high'):
  p=smooth(np.column_stack([c[:,1]+left-.5,c[:,0]+top-.5]))
  if len(p)>3:paths.append(p)
 return paths

def field(mask,top,left,limit=1536,paths=None,distance_model=None):
 paths=paths_for(mask,top,left)if paths is None else paths
 hh,ww=mask.shape;origin=np.array([left-5.,top-5.]);step=max(.25,float(max(hh+10,ww+10))/limit);width,height=np.ceil(np.array([ww+10,hh+10])/step).astype(int);extent=np.array([width,height])*step
 cover=inside(paths,(int(height),int(width)),origin,step);rough=np.where(cover,distance_transform_edt(cover)-.5,.5-distance_transform_edt(~cover));band=np.abs(rough)<9
 raw=np.where(cover,1.,0.).astype('<f2')
 if paths and band.any():
  yy,xx=np.nonzero(band);points=np.column_stack([origin[0]+(xx+.5)*step,origin[1]+(yy+.5)*step]);model=distance_model if distance_model is not None else segments(paths)
  for start in range(0,len(points),60000):
   end=start+60000;dist=np.abs(distance(points[start:end],model,step));sg=np.where(cover[yy[start:end],xx[start:end]],1.,-1.);raw[yy[start:end],xx[start:end]]=np.clip(.5+dist*sg/16,0,1)
 return (origin/[W,H]).tolist()+(extent/[W,H]).tolist(),raw

def main():
 w=json.loads((R/'data/world.json').read_text());ps=json.loads((R/'data/provinces.json').read_text());atlas_path=Path(sys.argv[sys.argv.index('--atlas-path')+1])if '--atlas-path'in sys.argv else R/'tools/cartography/province_atlas_0217.npz';a=np.load(atlas_path)['provinces'];lut=np.zeros(65536,np.uint16)
 for p in ps.values():lut[p['id']]=p['region']
 s=lut[a];old_index={}if '--coast-only'in sys.argv else json.loads((OUT/'selection_distance.json').read_text());oldpack=b''if '--coast-only'in sys.argv else (OUT/old_index.get('data_file','selection_distance.bwd')).read_bytes();pack=io.BytesIO();index={'version':'0.2.0.17','geography_sha256':hashlib.sha256((R/'data/provinces.json').read_bytes()).hexdigest(),'format':'RH','data_file':'selection_distance_0217.bwd','native_size':[W,H],'distance_encoding':{'zero':.5,'units_per_texel':.0625},'states':{},'provinces':{},'seas':{}}
 if '--coast-only'not in sys.argv:
  for scope,arr,records,limit in [('states',s,w['regions'],1536),('provinces',a,ps,1024)]:
   boxes=find_objects(arr,max_label=max(map(int,records)))
   def prepare(key):
    sid=int(key);bb=boxes[sid-1];assert bb is not None,(scope,key);t,l=bb[0].start,bb[1].start;part=arr[bb]==sid
    if part.shape[1]>W*.55:
     cols=np.flatnonzero(part.any(0))+l;gaps=np.diff(np.r_[cols,cols[0]+W]);gap=int(gaps.argmax());l=int(cols[(gap+1)%len(cols)]);part=arr[bb[0],(np.arange(W-int(gaps[gap])+1)+l)%W]==sid
    rect,data=field(part,t,l,limit);return key,rect,data.shape,zlib.compress(data.tobytes(),6)
   with ThreadPoolExecutor(max_workers=3)as executor:
    for j,(key,rect,shape,b)in enumerate(executor.map(prepare,records)):
     index[scope][key]=rect+[pack.tell(),len(b),shape[1],shape[0]];pack.write(b)
     if j%500==0:print('ANALYTIC_FIELDS',scope,j,flush=True)
  # Sea geometry did not change. Convert existing fields to the explicit new
  # format; land clipping comes from the corrected current coast field below.
  for key,r in old_index['seas'].items():
   source=zlib.decompress(oldpack[r[4]:r[4]+r[5]]);data=np.frombuffer(source,'<f2')if old_index.get('format')=='RH'else np.frombuffer(source,np.uint8).astype(np.float32)/255.;b=zlib.compress(data.astype('<f2').tobytes(),6);index['seas'][key]=r[:4]+[pack.tell(),len(b),r[6],r[7]];pack.write(b)
  b=pack.getvalue();(OUT/'selection_distance_0217.bwd').write_bytes(b);(OUT/'selection_distance.json').write_text(json.dumps(index,separators=(',',':')));print('SELECTION_READY',len(b),flush=True)
 # Rebuild coast distance from FINAL land, independently of selected State or
 # province. Old per-State windows are retired, eliminating stale merge masks.
 land=(a>0);del a,s
 # Include unassigned Antarctic land from the exact source raster.
 for i in range(4):
  rgb=np.asarray(Image.open(R/f'assets/region_ids_{i}.png'));t,l=i//2*4096,i%2*8192;land[t:t+4096,l:l+8192]|=(rgb[:,:,0]==255)&(rgb[:,:,1]==255)
 paths=paths_for(land,0,0);model=segments(paths,True)
 low=land[::2,::2]|land[1::2,::2]|land[::2,1::2]|land[1::2,1::2];high=land[::2,::2]&land[1::2,::2]&land[::2,1::2]&land[1::2,1::2];edge=low!=high;edge[:,1:]|=low[:,1:]!=low[:,:-1];edge[1:]|=low[1:]!=low[:-1];band=binary_dilation(np.pad(edge,((0,0),(10,10)),mode='wrap'),iterations=8)[:,10:-10]
 coarse=inside(paths,(H//2,W//2),np.array([0.,0.]),2);yy,xx=np.nonzero(band);out=np.where(coarse,1.,0.).astype('<f2')
 for start in range(0,len(xx),60000):
  x,y=xx[start:start+60000],yy[start:start+60000];points=np.column_stack([(x+.5)*2,(y+.5)*2]);d=np.abs(distance(points,model,2,True));sign=np.where(coarse[y,x],1.,-1.);out[y,x]=np.clip(.5+d*sign/16,0,1)
 (OUT/'coast_distance_0217.bwd').write_bytes(struct.pack('<II',W//2,H//2)+zlib.compress(out.tobytes(),8));print('GLOBAL_COAST_READY',flush=True)
 # Close views need sub-native coast samples. Prepare one bounded window per
 # State with coastline, from the same global contours, including all islands.
 from shapely.geometry import Polygon,box
 from shapely.strtree import STRtree
 tree=STRtree([Polygon(p)for p in paths]);local_index={'version':'0.2.0.17','format':'RH','states':{},'provinces':{},'rebuilt_states':[]};localpack=io.BytesIO()
 grouped=np.load(R/'tools/cartography/grouped_atlas_022r2.npz')['regions'];boxes=find_objects(grouped,max_label=8191)
 for j,key in enumerate(w['regions']):
  bb=boxes[int(key)-1];t=max(0,bb[0].start-6);b=min(H,bb[0].stop+6);l=max(0,bb[1].start-6);r=min(W,bb[1].stop+6)
  if r-l>W*.55 or not np.any(~land[t:b,l:r]):continue
  picked=tree.query(box(l-3,t-3,r+3,b+3));localpaths=[paths[int(k)]for k in picked]
  if not localpaths:continue
  rect,data=field(land[t:b,l:r],t,l,1536,localpaths,model);blob=zlib.compress(data.tobytes(),6);local_index['states'][key]=rect+[localpack.tell(),len(blob),data.shape[1],data.shape[0]];localpack.write(blob);local_index['rebuilt_states'].append(int(key))
  if j%300==0:print('CURRENT_COAST_WINDOWS',j,flush=True)
 (OUT/'local_coasts.bwd').write_bytes(localpack.getvalue());(OUT/'local_coasts.json').write_text(json.dumps(local_index,separators=(',',':')))
 if '--skip-legacy-shade'in sys.argv:return
 # Legacy output retained for older offline tools only; no runtime consumer.
 # Recompute the continuous physical country band from current ownership.
 own=np.zeros(8192,np.uint16)
 for key,r in w['regions'].items():own[int(key)]=w['countries'][r['owner']]['index']
 owner=own[grouped[1::2,1::2]];edge=np.zeros_like(owner,bool)
 for axis in [0,1]:
  other=np.roll(owner,1,axis);edge|=(owner>0)&(owner!=other)
 d=distance_transform_edt(~edge);shade=np.clip(1-d/5.,0,1);shade=gaussian_filter(shade,.8);shade[owner==0]=0
 data=np.rint(shade*255).astype(np.uint8);(OUT/'country_border_shade.bwd').write_bytes(struct.pack('<II',W//2,H//2)+zlib.compress(data.tobytes(),8));print('DISPLAY_0217_READY',len(index['states']),len(index['provinces']),len(local_index['states']),flush=True)
if __name__=='__main__':main()
