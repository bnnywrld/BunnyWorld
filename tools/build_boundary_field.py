"""Universal smooth boundary field: province pair + oriented curve distance.
Never contains State or country ownership. All lines/fills use the same field.
"""
from pathlib import Path
import json,struct,zlib
import numpy as np
from scipy.ndimage import maximum_filter
from build_boundary_hint import atlas
from build_boundaries_021 import contours
from build_display_0212 import segments
R=Path(__file__).resolve().parents[1];O=R/'assets/display';W,H=16384,8192

def build():
 a=atlas();ps=json.loads((R/'data/provinces.json').read_text())
 paths=contours(a,sorted(map(int,ps)),1,province=True)
 curves=[];pairs=[]
 for x,y,p,q,kind in paths:
  if q==65535:continue
  xy=np.column_stack([x*W+.5,y*H+.5]);good=np.sum(np.diff(xy,axis=0)**2,axis=1)>1e-12
  curves.append(xy)
  pairs.extend([(p,q)]*int(good.sum()))
 model=segments(curves,True);aa,v,ids,tree=model;pair=np.asarray(pairs,np.uint16)
 # Apply the same world-edge exclusion as the wrapped segment index.
 raw_a=np.concatenate([p[:-1]for p in curves]);raw_b=np.concatenate([p[1:]for p in curves]);good=np.sum((raw_b-raw_a)**2,axis=1)>1e-12;raw_a=raw_a[good];raw_b=raw_b[good]
 good=~((np.maximum(raw_a[:,0],raw_b[:,0])<.01)|(np.minimum(raw_a[:,0],raw_b[:,0])>W-1.01)|(np.maximum(raw_a[:,1],raw_b[:,1])<.01)|(np.minimum(raw_a[:,1],raw_b[:,1])>H-1.01));pair=pair[good]
 assert len(aa)==len(pair),(len(aa),len(pair))
 edge=np.zeros(a.shape,np.uint8);e=a!=np.roll(a,1,axis=1);edge[e]=1;edge[np.roll(e,-1,axis=1)]=1
 e=a[1:]!=a[:-1];edge[1:][e]=1;edge[:-1][e]=1
 band=np.maximum.reduce([edge[::2,::2],edge[1::2,::2],edge[::2,1::2],edge[1::2,1::2]])
 band=maximum_filter(band,size=7,mode=('nearest','wrap'))>0;yy,xx=np.nonzero(band)
 out=np.full((H//2,W//2),16.,dtype='<f2');outpairs=np.zeros((H//2,W//2,4),np.uint8)
 mismatch=0;checked=0;rejected=0
 for start in range(0,len(xx),50000):
  x,y=xx[start:start+50000],yy[start:start+50000];points=np.column_stack([(x+.5)*2,(y+.5)*2])
  _,j=tree.query(points,k=4,workers=2);si=ids[j];va=v[si];d=points[:,None,:]-aa[si];d[:,:,0]=(d[:,:,0]+W/2)%W-W/2
  t=np.clip(np.sum(d*va,axis=2)/np.sum(va*va,axis=2),0,1);delta=d-va*t[:,:,None];d2=np.sum(delta*delta,axis=2);best=d2.argmin(1);rows=np.arange(len(points));idx=si[rows,best]
  norm=np.sqrt(d2[rows,best]);cross=va[rows,best,1]*d[rows,best,0]-va[rows,best,0]*d[rows,best,1]
  signed=np.where(cross<=0,norm,-norm);pq=pair[idx]
  real=a[y*2+1,x*2+1];test=(norm>1.5);expected=np.where(signed>0,pq[:,0],pq[:,1]);unsafe=test&(real!=expected)
  # A nearest segment's extended half-plane is not a polygon classifier
  # beyond endpoints, narrow islands or multi-region junctions. Do not use
  # that pair there: fall back to current categorical membership instead.
  rejected+=int(unsafe.sum());valid=~unsafe
  out[y,x]=np.clip(signed,-16,16)
  encoded=np.column_stack([pq[:,0]&255,pq[:,0]>>8,pq[:,1]&255,pq[:,1]>>8]);encoded[unsafe]=0
  outpairs[y,x]=encoded
  checked+=int((test&valid).sum());mismatch+=int(np.sum(test&valid&(real!=expected)))
  if start%500000==0:print('BOUNDARY_FIELD',start,'/',len(xx),flush=True)
 # A reversed contour is a correctness error, not a cosmetic discrepancy.
 assert mismatch==0,(mismatch,checked)
 for name,im in [('boundary_pairs.bwd',outpairs),('boundary_distance.bwd',out)]:
  data=struct.pack('<II',W//2,H//2)+zlib.compress(im.tobytes(),8);(O/name).write_bytes(data);print('READY',name,len(data),flush=True)
 return {'sampled_cells':len(xx),'oriented_distance_checks':checked,'orientation_errors_in_accepted_samples':mismatch,'ambiguous_samples_using_categorical_fallback':rejected,'gpu_bytes':out.nbytes+outpairs.nbytes,'curve_paths':len(curves)}
if __name__=='__main__':
 report=build();target=R/'validation_0218/boundary_field.json';target.parent.mkdir(exist_ok=True);target.write_text(json.dumps(report,indent=2))
