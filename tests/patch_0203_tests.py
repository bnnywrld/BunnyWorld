"""Independent accounting, map lookup, geography and displayed-scenery checks."""
from pathlib import Path
from collections import Counter
import json,math,sys
import numpy as np
from PIL import Image
from scipy.ndimage import label
from scipy.spatial import cKDTree
from shapely.geometry import LineString,box
from shapely.strtree import STRtree
ROOT=Path(__file__).resolve().parents[1];Image.MAX_IMAGE_PIXELS=None
def read(n):return json.load(open(ROOT/'data'/f'{n}.json'))
w,p,u,s=map(read,['world','provinces','urban_population','urban_scenery'])
assert w['scenario_id']=='bunny_world_2000_0_2_0_3' and len(w['countries'])==223 and len(w['regions'])==1233
assert sum(r['population'] for r in w['regions'].values())==6144737528
assert len([r for r in w['regions'].values() if 'quebec' in r['name'].lower()])==1
if len(sys.argv)>1:
 old=json.load(open(Path(sys.argv[1])/'data/world.json'))
 for tag in w['countries']:
  for field in ['population','buildings']:
   def aggregate(world):
    rows=[r for r in world['regions'].values() if r['owner']==tag]
    return sum(r[field] for r in rows) if field=='population' else sum((Counter(r[field]) for r in rows),Counter())
   assert aggregate(w)==aggregate(old),(tag,field)
atlas=np.load(ROOT/'tools/cartography/province_atlas_0203.npz')['provinces'];states=np.load(ROOT/'tools/cartography/grouped_atlas_022r2.npz')['regions'];H,W=atlas.shape
lookup=np.zeros(65536,np.uint16)
for key,v in p.items():
 assert int(key)==v['id'] and v['area_km2']>0
 lookup[v['id']]=v['region'];assert v['id'] in w['regions'][str(v['region'])]['provinces']
 for n in v['neighbors']:assert v['id'] in p[str(n)]['neighbors']
 assert isinstance(v['population_2000'],int) and v['population_2000']>=0
assert set(np.unique(atlas))=={0}|set(map(int,p))
for top in range(0,H,256):assert np.array_equal(lookup[atlas[top:top+256]],states[top:top+256])
for i in range(4):
 raw=np.array(Image.open(ROOT/'assets'/f'region_ids_{i}.png'),np.uint16)
 assert np.array_equal(raw[:,:,0]+raw[:,:,1]*256,atlas[i//2*(H//2):(i//2+1)*(H//2),i%2*(W//2):(i%2+1)*(W//2)])
for sid,r in w['regions'].items():
 assert sum(p[str(pid)]['population_2000'] for pid in r['provinces'])==r['population'],sid
for gid,g in u['groups'].items():assert sum(p[str(pid)]['population_2000'] for pid in g['provinces'])==g['population_2000']
for name,tag in [('Hong Kong','HKG'),('Macau','MAC')]:
 c=next(c for c in read('cities') if c['name']==name);assert c['province_id'] and c['country']==tag and c['urban_group']
 assert any(c['province_id']==q['province'] and q['instances'] for q in s['clusters']),name
def state_at(lon,lat):return int(states[int((90-lat)/180*H),int((lon+180)/360*W)%W])
assert state_at(124.5,-9.8)==1169,'West Timor is on Timor'
assert state_at(126.0,-8.8)==1210,'Timor Leste is on Timor'
assert state_at(139,-5)==628,'Papua must not be labelled Timor'
assert state_at(20.2,60.2)==104,'Åland must retain its island identity'
# The archipelago must not share its physical connected component with Turku.
land=np.load(ROOT/'tools/cartography/physical_land_0202.npz')['land']
bb=np.s_[int((90-62)/180*4096):int((90-59)/180*4096),int((18+180)/360*8192):int((24+180)/360*8192)]
components,_=label(land[bb])
def component(lon,lat):return int(components[int((90-lat)/180*4096)-bb[0].start,int((lon+180)/360*8192)-bb[1].start])
island=component(19.95,60.2);mainland=component(22.3,60.5)
assert island>0 and mainland>0 and island!=mainland,'Åland joined to mainland'
report=read('geography_0203_report');assert sum(q['merged_cells'] for q in report['sparse_merges'])>=100
assert {q['area'] for q in report['state_repairs']} >= {'Egypt','Niger','Saudi Arabia and Rub al Khali','Transnistria and Moldova','Southern Vietnam','Indonesia island-chain identities'}
# Buildings and monuments use their displayed, enlarged footprints.
items=np.array([b for c in s['clusters'] for b in c['instances']],float)
lon,lat=np.deg2rad(items[:,0]),np.deg2rad(items[:,1]);xyz=np.column_stack([np.cos(lat)*np.sin(lon),np.sin(lat),np.cos(lat)*np.cos(lon)])*6371
radii=items[:,2]*36*1.4/1000/math.sqrt(2);tree=cKDTree(xyz);pairs=tree.query_pairs(2*radii.max()+.25,output_type='ndarray')
if len(pairs):assert np.all(np.linalg.norm(xyz[pairs[:,0]]-xyz[pairs[:,1]],axis=1)>=radii[pairs[:,0]]+radii[pairs[:,1]]+.2498)
for l in s['landmarks']:
 a,b=map(math.radians,[l['longitude'],l['latitude']]);q=np.array([math.cos(b)*math.sin(a),math.sin(b),math.cos(b)*math.cos(a)])*6371
 near=tree.query_ball_point(q,l['display_footprint_radius_km']+radii.max()+.25)
 if near:assert np.all(np.linalg.norm(xyz[near]-q,axis=1)>=radii[near]+l['display_footprint_radius_km']+.2498)
# Independently test exact river segments, rather than reusing the generator's
# sampled tree. Geographic widths/banks have an additional clearance margin.
segments=[];ends=[]
for f in json.load(open(ROOT/'tools/cartography/rivers_0201.geojson'))['features']:
 prop=f['properties']
 if float(prop.get('scalerank',10) or 0)>6 or prop.get('featurecla')!='River':continue
 geom=f['geometry'];lines=geom['coordinates'] if geom['type']=='MultiLineString' else [geom['coordinates']]
 for line in lines:
  for a,b in zip(line[:-1],line[1:]):
   if abs(a[0]-b[0])<=180:segments.append(LineString([a[:2],b[:2]]));ends.append([a[:2],b[:2]])
ends=np.array(ends);metric=np.column_stack([np.cos(np.deg2rad(items[:,1]))*111.195,np.full(len(items),111.195)])
span=(radii+1.9)[:,None]/metric
boxes=[box(lon-d[0],lat-d[1],lon+d[0],lat+d[1]) for (lon,lat),d in zip(items[:,:2],span)]
bi,ri=STRtree(segments).query(boxes)
if len(bi):
 a=(ends[ri,0]-items[bi,:2])*metric[bi];b=(ends[ri,1]-items[bi,:2])*metric[bi];delta=b-a
 t=np.clip(-np.sum(a*delta,axis=1)/np.maximum(np.sum(delta*delta,axis=1),1e-12),0,1)
 distance=np.linalg.norm(a+delta*t[:,None],axis=1)
 assert np.all(distance>=radii[bi]+1.79),'displayed building footprint intrudes on mapped river clearance'
sys.path.insert(0,str(ROOT/'tools'))
from micro_geometry import MicroGeometry
micro=MicroGeometry(ROOT)
for c in s['clusters']:
 for b in c['instances']:
  raw=int(atlas[int((90-b[1])/180*H),int((b[0]+180)/360*W)%W])
  assert micro.resolve(b[0],b[1],raw)==c['province'],c['name']
rgba=np.array(Image.open(ROOT/'assets/relief_data.png'));values=np.fromfile(ROOT/'assets/relief_data.bin',dtype='<u2').reshape(4096,8192)
assert np.array_equal(values,rgba[:,:,0].astype(np.uint16)+rgba[:,:,1].astype(np.uint16)*256)
assert not values[~land].any()
band=np.array(Image.open(ROOT/'assets/border_fade.png'));assert band.max()==255 and np.count_nonzero(band==0)>band.size*.70
assert not u['growth_enabled'] and not s['growth_enabled'] and s['building_cap']==2048 and s['cluster_cap']==96
print('PATCH_0203_TESTS_PASS',len(p),'provinces',len(items),'buildings; country accounts, every province estimate, lookup coverage, island separation and displayed footprint clearance')
