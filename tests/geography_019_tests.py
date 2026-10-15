"""Full ID-grid and area/city/ocean regression checks for rebuilt geography."""
from pathlib import Path
import json,runpy,struct
import numpy as np
from PIL import Image
from scipy.ndimage import label
ROOT=Path(__file__).resolve().parents[1];Image.MAX_IMAGE_PIXELS=None
runpy.run_path(str(ROOT/'tests/geography_017_tests.py'))
w=json.load(open(ROOT/'data/world.json'));ps=json.load(open(ROOT/'data/provinces.json'));a=np.load(ROOT/'tools/cartography/grouped_atlas_019.npz')['regions'];pmap=np.load(ROOT/'tools/cartography/province_atlas_019.npz')['provinces'];report=json.load(open(ROOT/'data/update_019_report.json'))
assert w['scenario_id']=='bunny_world_2000_0_1_9'
assert all(c['starting_stats']['political_power']==100 for col in ['countries','country_registry'] for c in w[col].values())
assert all(0<len(r['provinces'])<=255 for r in w['regions'].values())
assert len(ps)>14000 and report['provinces']['city_provinces']>1500
# Every physical map pixel agrees with the discrete click/ownership atlas.
lookup=np.zeros(65536,np.uint16)
for p in ps.values():lookup[p['id']]=p['region']
assert np.array_equal(lookup[pmap][(a>0)&(a<8191)],a[(a>0)&(a<8191)])
city_names={p.get('name') for p in ps.values() if p['kind']=='city'}
assert {'Tokyo','Mexico City','New York','Paris','London','Beijing','Warsaw'}<=city_names
rural=np.array([p['area_km2'] for p in ps.values() if p['kind']=='rural' and p['area_km2']>=2500])
assert 6000<np.median(rural)<14000
assert np.percentile(rural,90)<22000
for p in ps.values():assert p['area_km2']>0
rgb=np.asarray(Image.open(ROOT/'assets/sea_ids.png'),np.uint16);sea=rgb[:,:,0]+rgb[:,:,1]*256
water=a[1::2,1::2]==0;components,_=label(water,np.ones((3,3),np.uint8));sizes=np.bincount(components.ravel());sizes[0]=0;ocean=components==np.argmax(sizes)
assert np.all(sea[~ocean]==0) and np.all(sea[ocean]>0)
def water_id(lon,lat):return int(sea[min(4095,int((90-lat)/180*4096)),int((lon+180)/360*8192)%8192])
for lon,lat in [(-87,44),(-89,47.7),(33,-1),(29.5,-6),(-114.7,61.5),(51,41),(108,53)]:assert water_id(lon,lat)==0,(lon,lat,water_id(lon,lat))
for lon in [-170,-90,0,90,170]:assert water_id(lon,88)==237
seas=json.load(open(ROOT/'data/sea_regions.json'));assert all(s.get('naval_terrain')!='lake' for s in seas.values())
for name in ['land','sea','province']:
    assert (ROOT/f'assets/{name}_boundaries.res').stat().st_size>1000
    mesh=(ROOT/f'tools/cartography/{name}_boundaries_019.bin').read_bytes();nv,ni=struct.unpack_from('<II',mesh)
    vertices=np.frombuffer(mesh,dtype='<f4',count=nv*3,offset=8).reshape(-1,3)
    indices=np.frombuffer(mesh,dtype='<i4',count=ni,offset=8+nv*52).reshape(-1,3)[::2]
    mids=(vertices[indices[:,0]]+vertices[indices[:,2]])*.5
    # Bound spherical chord error to <0.04 source texel, including the pole.
    assert np.min(np.linalg.norm(mids,axis=1))>1.000070,(name,'long spherical border chord')
print('GEOGRAPHY_019_PASS',len(ps),'provinces',len(city_names),'city provinces; rural area percentiles',np.percentile(rural,[10,50,90]).round().tolist(),'ocean zones',len(seas))
