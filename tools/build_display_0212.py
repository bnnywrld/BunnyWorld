"""Offline display-only assets. Never writes simulation/picking maps.
Smooths the same native atlas contours used by existing border ribbons.
SDFs describe coverage, not province IDs; each selection uploads one small tile.
"""
from pathlib import Path
import json,struct,zlib,hashlib
import numpy as np
from PIL import Image,ImageFont,ImageDraw
from scipy.ndimage import find_objects,binary_dilation,label
from scipy.spatial import cKDTree
from skimage.measure import find_contours
from shapely.geometry import LineString,Polygon
from rasterio.features import rasterize
from rasterio.transform import Affine
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/display'
from map_dimensions import W,H
Image.MAX_IMAGE_PIXELS=None

def rings(mask,top=0,left=0):
 result=[]
 for c in find_contours(np.pad(mask,1),.5,fully_connected='high'):
  p=np.column_stack([c[:,1]+left-1,c[:,0]+top-1]);p=np.asarray(LineString(p).simplify(.8,preserve_topology=False).coords)
  if len(p)>=6:
   a=p[:-1]*.75+p[1:]*.25;b=p[:-1]*.25+p[1:]*.75
   q=np.empty((len(a)*2,2));q[::2]=a;q[1::2]=b;p=np.vstack([p[:1],q,p[-1:]])
  if len(p)>2:result.append(p)
 return result

def segments(paths,wrap=False):
 a=np.concatenate([p[:-1] for p in paths]);b=np.concatenate([p[1:] for p in paths]);v=b-a;good=np.sum(v*v,axis=1)>1e-12
 if wrap:good &= ~((np.maximum(a[:,0],b[:,0])<.01)|(np.minimum(a[:,0],b[:,0])>W-1.01)|(np.maximum(a[:,1],b[:,1])<.01)|(np.minimum(a[:,1],b[:,1])>H-1.01))
 a=a[good];b=b[good];v=b-a
 lengths=np.linalg.norm(v,axis=1);counts=np.maximum(1,np.ceil(lengths/.6).astype(int));ids=np.repeat(np.arange(len(a)),counts)
 start=np.repeat(np.cumsum(counts)-counts,counts);t=(np.arange(len(ids))-start+.5)/counts[ids]
 points=a[ids]+v[ids]*t[:,None]
 if wrap:
  original=len(points);edge=(points[:,0]<24)|(points[:,0]>W-24)
  shift=np.where(points[edge,0]<24,W,-W)
  points=np.vstack([points,points[edge]+np.column_stack([shift,np.zeros(len(shift))])]);ids=np.concatenate([ids,ids[edge]])
 return a,v,ids,cKDTree(points)

def distance(points,model,step=1.,wrap=False):
 a,v,ids,tree=model;_,j=tree.query(points,k=4,workers=2);si=ids[j];aa=a[si];vv=v[si]
 d=points[:,None,:]-aa
 if wrap:d[:,:,0]=(d[:,:,0]+W/2)%W-W/2
 t=np.clip(np.sum(d*vv,axis=2)/np.sum(vv*vv,axis=2),0,1);delta=d-vv*t[:,:,None];d2=np.sum(delta*delta,axis=2);best=d2.argmin(axis=1);ii=np.arange(len(points));norm=np.sqrt(d2[ii,best]);cross=vv[ii,best,1]*d[ii,best,0]-vv[ii,best,0]*d[ii,best,1]
 # Native contours orient land on the left in x/y image coordinates.
 return np.where(cross<=0,norm,-norm)/step

def encode(d):return np.clip(np.rint(127.5+d*24),0,255).astype(np.uint8)

def inside(paths,shape,origin,step,supersample=1):
 # GDAL evaluates at pixel centers. PIL's inclusive polygon fill biases the
 # coast outward by a texel, visible as ledges at close zoom.
 ordered=[]
 for p in paths:
  area=np.sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])/2
  if abs(area)>1e-8:ordered.append((abs(area),area,p))
 if not ordered:return np.zeros(shape,bool)
 shapes=[(Polygon(p),1 if area>0 else 0) for _,area,p in sorted(ordered,key=lambda x:-x[0])]
 return rasterize(shapes,out_shape=shape,transform=Affine(step,0,origin[0],0,step,origin[1]),dtype='uint8')>0

def tile(mask,top,left,max_size):
 paths=rings(mask,top,left);hh,ww=mask.shape;pad=5
 origin=np.array([left-pad,top-pad],float);extent=np.array([ww+2*pad,hh+2*pad],float)
 scale=max(1.,max(extent)/max_size);width=int(np.ceil(extent[0]/scale));height=int(np.ceil(extent[1]/scale));extent=np.array([width,height])*scale
 yy,xx=np.meshgrid(origin[1]+(np.arange(height)+.5)*scale,origin[0]+(np.arange(width)+.5)*scale,indexing='ij');points=np.column_stack([xx.ravel(),yy.ravel()])
 signed=np.where(inside(paths,(height,width),origin,scale),1.,-1.)
 data=encode(np.abs(distance(points,segments(paths),scale)).reshape(height,width)*signed)
 return (origin/np.array([W,H])).tolist()+(extent/np.array([W,H])).tolist(),data

def protect_anchor(data,rect,uv):
 # Keep subpixel/very thin selected regions visible. This is only a visual
 # footprint; ownership, polygon IDs and picking remain the exact source map.
 h,w=data.shape;u,v,su,sv=rect;x=((uv[0]-u)%1)/su*w-.5;y=(uv[1]-v)/sv*h-.5
 if not(0<=x<w-1 and 0<=y<h-1):return data
 ix,iy=int(np.floor(x)),int(np.floor(y));fx,fy=x-ix,y-iy;q=data[iy:iy+2,ix:ix+2].astype(float)
 value=(q[0,0]*(1-fx)+q[0,1]*fx)*(1-fy)+(q[1,0]*(1-fx)+q[1,1]*fx)*fy
 if value>130:return data
 yy,xx=np.meshgrid(np.arange(max(0,iy-2),min(h,iy+4)),np.arange(max(0,ix-2),min(w,ix+4)),indexing='ij')
 patch=encode(.85-np.hypot(xx-x,yy-y));data[yy,xx]=np.maximum(data[yy,xx],patch)
 return data

def atlas():
 from build_boundary_hint import atlas as canonical_atlas
 a=canonical_atlas()
 return a

def coverage():
 a=atlas();ps=json.loads((ROOT/'data/provinces.json').read_text());world=json.loads((ROOT/'data/world.json').read_text());lookup=np.zeros(65536,np.uint16)
 for key,p in ps.items():lookup[int(key)]=int(p['region'])
 # Unclaimed Antarctica is land too.
 lookup[65535]=8191
 states=lookup[a];land=a>0
 # Coast SDF: native contour distances, sampled at half native resolution.
 print('DISPLAY_COAST contours',flush=True);paths=rings(land);model=segments(paths,True)
 low=land[::2,::2]|land[1::2,::2]|land[::2,1::2]|land[1::2,1::2]
 high=land[::2,::2]&land[1::2,::2]&land[::2,1::2]&land[1::2,1::2]
 edge=low!=high;edge[:,1:]|=low[:,1:]!=low[:,:-1];edge[1:]|=low[1:]!=low[:-1];edge[:,0]|=low[:,0]!=low[:,-1]
 display_land=inside(paths,(H//2,W//2),np.array([0.,0.]),2.,2)
 band=binary_dilation(np.pad(edge,((0,0),(8,8)),mode='wrap'),iterations=6)[:,8:-8];yy,xx=np.nonzero(band);coast=np.where(display_land,255,0).astype(np.uint8)
 for start in range(0,len(xx),100000):
  x=xx[start:start+100000];y=yy[start:start+100000];coast[y,x]=encode(np.abs(distance(np.column_stack([(x+.5)*2,(y+.5)*2]),model,2,True))*np.where(display_land[y,x],1.,-1.))
 (OUT/'coast_distance.bwd').write_bytes(struct.pack('<II',W//2,H//2)+zlib.compress(coast.tobytes(),9));del model,paths,low,high,band,coast
 index={'version':1,'native_size':[W,H],'distance_encoding':{'zero':127.5,'units_per_pixel':24},'states':{},'provinces':{}}
 with (OUT/'selection_distance.bwd').open('wb') as file:
  for scope,arr,records,limit in [('states',states,world['regions'],1024),('provinces',a,ps,512)]:
   boxes=find_objects(arr,max_label=int(arr.max()))
   for j,key in enumerate(records):
    sid=int(key);box=boxes[sid-1]
    if box is None:continue
    top=box[0].start;left=box[1].start;part=arr[box]==sid
    if part.shape[1]>W*.55:
     cols=np.flatnonzero(part.any(axis=0))+left;gaps=np.diff(np.r_[cols,cols[0]+W]);gap=int(gaps.argmax());left=int(cols[(gap+1)%len(cols)]);width=W-int(gaps[gap])+1
     part=arr[top:box[0].stop,(np.arange(width)+left)%W]==sid
    rect,data=tile(part,top,left,limit);data=protect_anchor(data,rect,records[key]["map_center"]);blob=zlib.compress(data.tobytes(),7);offset=file.tell();file.write(blob);index[scope][key]=rect+[offset,len(blob),data.shape[1],data.shape[0]]
    if j%250==0:print('DISPLAY_SELECTION',scope,j,'/',len(records),flush=True)
 (OUT/'selection_distance.json').write_text(json.dumps(index,separators=(',',':')))
 print('DISPLAY_COVERAGE_COMPLETE',flush=True)

def tiny_islands():
 # A bit per original atlas pixel preserves small real land components that
 # cannot be represented by the lower-resolution coast SDF. No IDs change.
 land=atlas()>0;components,count=label(land,np.ones((3,3),bool));sizes=np.bincount(components.ravel());small=(sizes[components]<=16)&land
 packed=np.packbits(small,axis=1,bitorder='little')
 (OUT/'tiny_land_bits.bwd').write_bytes(struct.pack('<II',W//8,H)+zlib.compress(packed.tobytes(),9))
 print('TINY_LAND_BITS_COMPLETE',int(small.sum()),'native pixels',flush=True)

def font():
 world=json.loads((ROOT/'data/world.json').read_text());letters=sorted(set(''.join(c['name'].upper() for c in world['countries'].values()))-{' '})
 source='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';f=ImageFont.truetype(source,64);im=Image.new('RGBA',(1024,1024));draw=ImageDraw.Draw(im);x=y=4;row=0;glyphs={}
 for c in letters:
  l,t,r,b=f.getbbox(c,anchor='ls',stroke_width=1);w=r-l+4;h=b-t+4
  if x+w>1020:x=4;y+=row+4;row=0
  assert y+h<1024
  draw.text((x-l+2,y-t+2),c,font=f,anchor='ls',fill=(255,255,255,255),stroke_width=1,stroke_fill=(12,21,23,190))
  glyphs[c]={'uv':[x/1024,y/1024,w/1024,h/1024],'box':[l-2,t-2,w,h],'advance':f.getlength(c)};x+=w+4;row=max(row,h)
 glyphs[' ']={'advance':f.getlength(' ')};im.save(OUT/'country_glyphs.png');(OUT/'country_glyphs.json').write_text(json.dumps({'font_size':64,'tracking':4.2,'glyphs':glyphs},ensure_ascii=False,separators=(',',':')))
 (OUT/'FONT_LICENSE.txt').write_text(Path('/usr/share/doc/fonts-dejavu-core/copyright').read_text())
 print('DISPLAY_FONT_COMPLETE',len(letters),flush=True)
if __name__=='__main__':
 OUT.mkdir(exist_ok=True,parents=True);font();coverage();tiny_islands()
 from build_local_coasts_0212 import build as build_local_coasts
 build_local_coasts()
 files=[p for p in OUT.iterdir() if p.is_file() and p.name!='BUNDLE.json' and not p.name.endswith('.import')]
 bundle={'version':'0.2.0.12','geography_version':'0.2.0.10','files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}}
 (OUT/'BUNDLE.json').write_text(json.dumps(bundle,indent=2)+'\n')
