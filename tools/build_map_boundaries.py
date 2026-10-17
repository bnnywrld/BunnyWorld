"""Rebuild State and internal province lines together from current IDs."""
import json,numpy as np
from build_boundaries_021 import ROOT,contours,mesh
w=json.loads((ROOT/'data/world.json').read_text());ps=json.loads((ROOT/'data/provinces.json').read_text());a=np.load(ROOT/'tools/cartography/map_provinces.npz')['provinces'];s=np.load(ROOT/'tools/cartography/grouped_atlas_022r2.npz')['regions']
def ensure_edges(arr,paths,expected,kind):
 present={tuple(sorted((p[2],p[3])))for p in paths};missing=expected-present
 if not missing:return paths,0
 codes=np.array([l*65536+r for l,r in missing],np.uint32);count=0;hh,ww=arr.shape
 for top in range(0,hh,128):
  for vertical,l,r in [(True,arr[top:top+128,:-1],arr[top:top+128,1:]),(False,arr[top:min(hh-1,top+128)],arr[top+1:min(hh,top+129)])]:
   code=np.minimum(l,r).astype(np.uint32)*65536+np.maximum(l,r);yy,xx=np.nonzero(np.isin(code,codes))
   for y,x in zip(yy,xx):
    pair=tuple(sorted((int(l[y,x]),int(r[y,x]))));y+=top
    if vertical:px=np.array([x+.5,x+.5]);py=np.array([y-.5,y+.5])
    else:px=np.array([x-.5,x+.5]);py=np.array([y+.5,y+.5])
    paths.append((px/ww,py/hh,pair[0],pair[1],kind));count+=1
 assert expected<={tuple(sorted((p[2],p[3])))for p in paths}
 return paths,count
paths=contours(s,sorted(map(int,w['regions']))+[8191],1)
expected={tuple(sorted((int(k),n)))for k,r in w['regions'].items()for n in r['neighbors']}
paths,extra=ensure_edges(s,paths,expected,0)
report={'land':mesh(paths,'land_boundaries_021'),'land_short_edge_segments_restored':extra}
del paths,s
paths=contours(a,sorted(map(int,ps)),1);paths=[(x,y,l,r,2)for x,y,l,r,_ in paths if r>0 and str(r)in ps and ps[str(l)]['region']==ps[str(r)]['region']]
expected={(p['id'],n)for p in ps.values()for n in p['neighbors']if p['id']<n and p['region']==ps[str(n)]['region']}
paths,extra=ensure_edges(a,paths,expected,2);report['province_short_edge_segments_restored']=extra
report['province']=mesh(paths,'province_boundaries_021');(ROOT/'data/boundaries_build_report.json').write_text(json.dumps(report,indent=2));print('BOUNDARIES_0215_READY',report,flush=True)
