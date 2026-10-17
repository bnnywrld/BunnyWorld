"""Bounded subpixel contour smoothing; never trims long geometric corners."""
import numpy as np
from shapely.geometry import LineString
def smooth(points):
 p=np.asarray(LineString(points).simplify(.45,preserve_topology=False).coords)
 if len(p)<4:return p
 closed=np.linalg.norm(p[0]-p[-1])<1e-5
 q=p[:-1] if closed else p
 result=[]
 for i,v in enumerate(q):
  if not closed and i in [0,len(q)-1]:result.append(v);continue
  before=q[(i-1)%len(q)]-v;after=q[(i+1)%len(q)]-v;lb=np.linalg.norm(before);la=np.linalg.norm(after)
  if min(lb,la)<1e-8:continue
  cosine=np.dot(before,after)/(lb*la)
  if min(lb,la)>3 and cosine>-.65:
   result.append(v) # Real long straight-boundary corner, including right angles.
  else:
   result.extend([v+before/lb*min(.45,lb*.20),v+after/la*min(.45,la*.20)])
 if closed:result.append(result[0])
 return np.asarray(result)

def smooth_internal(points):
 """Round generated internal corners; pin coast/state junction endpoints.

 Never used for inherited administrative, country or coastal contours. Keep
 displacement bounded to 1.25 identity texels so picking/fill share geometry.
 """
 p=np.asarray(LineString(points).simplify(.8,preserve_topology=False).coords)
 if len(p)<3:return p
 closed=np.linalg.norm(p[0]-p[-1])<1e-5;q=p[:-1]if closed else p
 result=[]
 for i,v in enumerate(q):
  if not closed and i in [0,len(q)-1]:result.append(v);continue
  before=q[(i-1)%len(q)]-v;after=q[(i+1)%len(q)]-v
  lb,la=np.linalg.norm(before),np.linalg.norm(after)
  if min(lb,la)<1e-8:result.append(v);continue
  # A short quadratic Bezier rounds even long artificial right-angle runs.
  b=v+before/lb*min(1.25,lb*.24);a=v+after/la*min(1.25,la*.24)
  for t in [0.,.5,1.]:result.append((1-t)**2*b+2*(1-t)*t*v+t*t*a)
 if closed:result.append(result[0])
 return np.asarray(LineString(result).simplify(.18,preserve_topology=False).coords)
