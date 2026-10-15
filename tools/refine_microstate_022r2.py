"""Replace the oversized Vatican raster patch with a subpixel vector footprint.

The coarse atlas retains one identity pixel for tooling. Runtime picking and
colouring resolve that pixel to the enclosing Italian province unless the
actual reference polygon contains the point. The same polygon draws borders.
"""
from pathlib import Path
import json, math
from collections import Counter
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt,find_objects
from shapely.geometry import shape
from pyproj import Geod

ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography'
world=json.load(open(ROOT/'data/world.json'));ps=json.load(open(ROOT/'data/provinces.json'))
atlas=np.load(SRC/'province_atlas_021.npz')['provinces'].copy();H,W=atlas.shape
state=next(s for s in world['regions'].values() if s['owner']=='HLS')
assert len(state['provinces'])==1
pid=state['provinces'][0];sid=state['id']
feature=json.load(open(SRC/'vatican_reference_022r2.geojson'))['features'][0]
polygon=shape(feature['geometry']).simplify(.00002,preserve_topology=True)
ring=list(polygon.exterior.coords)[:-1]
assert 3<=len(ring)<=64
center=polygon.representative_point();lon,lat=center.x,center.y
u,v=(lon+180)/360,(90-lat)/180
owner=np.zeros(65536,np.int32)
for p in ps.values():owner[p['id']]=1 if world['regions'][str(p['region'])]['owner']=='ITA' else 0
ys,xs=np.nonzero(atlas==pid)
t,b=max(0,int(ys.min())-24),min(H,int(ys.max())+25)
l,r=max(0,int(xs.min())-24),min(W,int(xs.max())+25)
tile=atlas[t:b,l:r];valid=owner[tile]==1
near=distance_transform_edt(~valid,return_distances=False,return_indices=True)
replacement=tile[near[0],near[1]]
atlas[ys,xs]=replacement[ys-t,xs-l]
x,y=int(u*W),int(v*H)
host=int(atlas[y,x]);host_state=ps[str(host)]['region']
assert world['regions'][str(host_state)]['owner']=='ITA'
atlas[y,x]=pid

# Recompute only changed province areas/focus points; metadata IDs are stable.
changed={pid,*map(int,np.unique(replacement[ys-t,xs-l]))}
weights=np.cos((np.arange(H)+.5)/H*math.pi-math.pi/2)*(40075.017/W)**2
boxes=find_objects(atlas,max_label=65535)
for identity in changed:
    p=ps[str(identity)];bb=boxes[identity-1]
    yy,xx=np.nonzero(atlas[bb]==identity);yy+=bb[0].start;xx+=bb[1].start
    p['area_km2']=round(float(weights[yy].sum()),2)
    uv=p['map_center'];px=min(W-1,int(uv[0]*W));py=min(H-1,int(uv[1]*H))
    if int(atlas[py,px])!=identity:
        j=np.argmin((xx-px)**2+(yy-py)**2);p['map_center']=[(float(xx[j])+.5)/W,(float(yy[j])+.5)/H]
ps[str(pid)]['map_center']=[u,v]
ps[str(pid)]['atlas_identity_area_km2']=ps[str(pid)]['area_km2']
ps[str(pid)]['reference_polygon_area_km2']=abs(Geod(ellps='WGS84').geometry_area_perimeter(polygon)[0])/1e6
ps[str(pid)]['area_km2']=.44
ps[str(pid)]['area_source']='Vatican State official geography, 0.44 km2; display polygon is an approximate geoBoundaries reference.'
state['map_center']=[u,v];world['countries']['HLS']['map_center']=[u,v]

# Only changed local cells need new graph connections.
for p in ps.values():p['neighbors']=[] if p['id'] in changed else [n for n in p['neighbors'] if n not in changed]
edges=set()
for identity in changed:
    bb=boxes[identity-1]
    tile=atlas[max(0,bb[0].start-1):min(H,bb[0].stop+1),max(0,bb[1].start-1):min(W,bb[1].stop+1)]
    for a,b in [(tile[:,:-1],tile[:,1:]),(tile[:-1],tile[1:])]:
        mask=(a>0)&(b>0)&(a<65535)&(b<65535)&(a!=b)&((a==identity)|(b==identity))
        edges.update(zip(map(int,a[mask]),map(int,b[mask])))
for a,b in edges:
    if b not in ps[str(a)]['neighbors']:ps[str(a)]['neighbors'].append(b)
    if a not in ps[str(b)]['neighbors']:ps[str(b)]['neighbors'].append(a)
for p in ps.values():p['neighbors']=sorted(set(p['neighbors']))
record={'name':'Vatican City','country':'HLS','province':pid,'state':sid,'host_province':host,'host_state':host_state,'polygon_uv':[[(a+180)/360,(90-b)/180] for a,b in ring],'center_uv':[u,v],'nominal_area_km2':.44,'reference_polygon_area_km2':ps[str(pid)]['reference_polygon_area_km2'],'source':'geoBoundaries gbOpen VAT ADM0; public-domain source attributed in bundled metadata','official_area_source':'https://vaticanstate.va/en/state-and-government/general-informations/geography.html','method':'Subpixel vector override for colour/picking/borders. One atlas identity pixel is resolved to its Italian host outside the polygon.'}
(ROOT/'data/microstate_geometry.json').write_text(json.dumps(record,indent=2))
np.savez_compressed(SRC/'province_atlas_022r2.npz',provinces=atlas)
lookup=np.zeros(65536,np.uint16)
for p in ps.values():lookup[p['id']]=p['region']
lookup[65535]=8191
regions=lookup[atlas]
np.savez_compressed(SRC/'grouped_atlas_022r2.npz',regions=regions)
for i in range(4):
    a=atlas[i//2*4096:(i//2+1)*4096,i%2*8192:(i%2+1)*8192]
    Image.fromarray(np.stack([(a&255).astype(np.uint8),(a>>8).astype(np.uint8),np.zeros_like(a,np.uint8)],-1)).save(ROOT/f'assets/region_ids_{i}.png',optimize=True)
world['scenario_id']='bunny_world_2000_0_1_12_r2'
world['map']['microstate_geometry']='Vatican exact-scale vector reference for display and picking; one coarse identity pixel is masked outside its reference polygon.'
(ROOT/'data/world.json').write_text(json.dumps(world,ensure_ascii=False,separators=(',',':')))
(ROOT/'data/provinces.json').write_text(json.dumps(ps,ensure_ascii=False,separators=(',',':')))
report={'previous_atlas_pixels':len(xs),'identity_pixels':1,'nominal_area_km2':.44,'reference_vertices':len(ring),'restored_host_provinces':sorted(changed-{pid}),'province_count':len(ps),'state_count':len(world['regions'])}
(ROOT/'data/microstate_022r2_report.json').write_text(json.dumps(report,indent=2))
print('MICROSTATE_022R2_PASS',report,flush=True)
