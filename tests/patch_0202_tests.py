"""Regression against accepted 0.2.0.1 geography/accounts and displayed footprints."""
from pathlib import Path
from collections import Counter
import json,struct,math,sys
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image
from shapely.geometry import LineString,box
from shapely.strtree import STRtree
ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.load(open(ROOT/'data'/f'{name}.json'))
w,p,u,s=map(read,['world','provinces','urban_population','urban_scenery'])
baseline=json.load(open(ROOT/'tests/baseline_0201_invariants.json'))
assert w['scenario_id']=='bunny_world_2000_0_2_0_2'
assert 13000<=len(p)<=13500 and len(w['regions'])==1235 and len(w['countries'])==223
assert w['countries']==baseline['countries'],'country data changed'
for sid,r in w['regions'].items():
    for key,value in baseline['states'][sid].items():assert r[key]==value,(sid,key)
assert sum(r['population'] for r in w['regions'].values())==6144737528
atlas=np.load(ROOT/'tools/cartography/province_atlas_0202.npz')['provinces'];states=np.load(ROOT/'tools/cartography/grouped_atlas_022r2.npz')['regions'];H,W=atlas.shape
lookup=np.zeros(65536,np.uint16)
for v in p.values():
    lookup[v['id']]=v['region'];assert v['source_md_province']>0
    assert v['id'] in w['regions'][str(v['region'])]['provinces']
    for neighbor in v['neighbors']:assert v['id'] in p[str(neighbor)]['neighbors']
assert set(np.unique(atlas))=={0}|set(int(k) for k in p)
for top in range(0,H,256):assert np.array_equal(lookup[atlas[top:top+256]],states[top:top+256])
Image.MAX_IMAGE_PIXELS=None
for i in range(4):
    a=np.array(Image.open(ROOT/'assets'/f'region_ids_{i}.png'),np.uint16);decoded=a[:,:,0]+a[:,:,1]*256
    assert np.array_equal(decoded,atlas[i//2*(H//2):(i//2+1)*(H//2),i%2*(W//2):(i%2+1)*(W//2)])
index=np.array(Image.open(ROOT/'assets/province_index.png'),np.uint16).reshape(65536,3);assert np.array_equal(index[:-1,0]+index[:-1,1]*256,lookup[:-1])
items=np.array([b for c in s['clusters'] for b in c['instances']],dtype=float)
assert 100000<=len(items)<=130000 and s['building_cap']==2048 and s['cluster_cap']==96
def points(lon,lat):
    a,b=np.deg2rad(lon),np.deg2rad(lat);return np.column_stack([np.cos(b)*np.sin(a),np.sin(b),np.cos(b)*np.cos(a)])*6371
xyz=points(items[:,0],items[:,1]);radii=items[:,2]*36*1.4/1000/math.sqrt(2)
tree=cKDTree(xyz);pairs=tree.query_pairs(2*radii.max()+.25,output_type='ndarray')
if len(pairs):assert np.all(np.linalg.norm(xyz[pairs[:,0]]-xyz[pairs[:,1]],axis=1)>=radii[pairs[:,0]]+radii[pairs[:,1]]+.2498),'building footprints overlap'
for l in s['landmarks']:
    q=points(np.array([l['longitude']]),np.array([l['latitude']]))[0];radius=l['display_footprint_radius_km'];near=tree.query_ball_point(q,radius+radii.max()+.25)
    if near:assert np.all(np.linalg.norm(xyz[near]-q,axis=1)>=radii[near]+radius+.2498),l['name']
# Independent exact-segment distance check, rather than the generator's dense
# sample tree, verifies displayed footprints clear the mapped river courses.
segments=[];ends=[]
for f in json.load(open(ROOT/'tools/cartography/rivers_0201.geojson'))['features']:
    prop=f['properties']
    if float(prop.get('scalerank',10) or 0)>6 or prop.get('featurecla')!='River':continue
    geometry=f['geometry'];lines=geometry['coordinates'] if geometry['type']=='MultiLineString' else [geometry['coordinates']]
    for line in lines:
        for a,b in zip(line[:-1],line[1:]):
            if abs(a[0]-b[0])<=180:segments.append(LineString([a[:2],b[:2]]));ends.append([a[:2],b[:2]])
ends=np.array(ends);metric=np.column_stack([np.cos(np.deg2rad(items[:,1]))*111.195,np.full(len(items),111.195)])
span=(radii+.8)[:,None]/metric
boxes=[box(lon-d[0],lat-d[1],lon+d[0],lat+d[1]) for (lon,lat),d in zip(items[:,:2],span)]
bi,ri=STRtree(segments).query(boxes)
if len(bi):
    a=(ends[ri,0]-items[bi,:2])*metric[bi];b=(ends[ri,1]-items[bi,:2])*metric[bi];delta=b-a
    t=np.clip(-np.sum(a*delta,axis=1)/np.maximum(np.sum(delta*delta,axis=1),1e-12),0,1)
    distance=np.linalg.norm(a+delta*t[:,None],axis=1)
    bad=np.flatnonzero(distance<radii[bi]+.7)
    if len(bad):
        for j in bad[:8]:print('RIVER_CLEARANCE_FAILURE',items[bi[j],:4],distance[j],radii[bi[j]],ends[ri[j]],flush=True)
    assert not len(bad),'building footprints overlap a mapped river'
budget=Counter()
for c in s['clusters']:budget[c['group']]+=len(c['instances'])
for gid,g in u['groups'].items():assert budget[gid]==g['representative_buildings']
for filename,size,length in [('terrain_materials.bwm',2048,2796216),('terrain_materials_high.bwm',4096,11184824)]:
    raw=(ROOT/'assets/materials'/filename).read_bytes();assert struct.unpack_from('<I',raw)[0]==8;at=4
    for _ in range(8):
        assert struct.unpack_from('<IIII',raw,at)==(size,size,17,length);at+=16+length
    assert at==len(raw)
relief=read('relief');assert relief['height_exaggeration']==8 and relief['land_lift_meters']<100
rgba=np.array(Image.open(ROOT/'assets/relief_data.png'));land=np.load(ROOT/'tools/cartography/physical_land_0202.npz')['land']
values=np.fromfile(ROOT/'assets/relief_data.bin',dtype='<u2').reshape(4096,8192)
assert np.array_equal(values,rgba[:,:,0].astype(np.uint16)+rgba[:,:,1].astype(np.uint16)*256)
assert not np.any(values[~land]);assert .009<values.max()/65535*.016<.010
for lon in [-45,0,60]:
    y,x=int(170/180*4096),int((lon+180)/360*8192);assert land[y,x] and rgba[y,x,3]>127 and values[y,x]>0
assert len(read('waterways')['rivers'])>=300
print('PATCH_0202_TESTS_PASS',len(p),'provinces',len(items),'buildings; baseline geography/accounts preserved; footprint clearance and independent Antarctic coverage verified')
