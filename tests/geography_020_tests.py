from pathlib import Path
import json,collections,struct
import numpy as np
from PIL import Image
from scipy.ndimage import label
ROOT=Path(__file__).resolve().parents[1];Image.MAX_IMAGE_PIXELS=None
w=json.load(open(ROOT/'data/world.json'));rs=w['regions'];ps=json.load(open(ROOT/'data/provinces.json'));base=json.load(open(ROOT/'tools/cartography/world_seed_015.json'));report=json.load(open(ROOT/'data/update_020_report.json'))
a=np.load(ROOT/'tools/cartography/grouped_atlas_020.npz')['regions'];pmap=np.load(ROOT/'tools/cartography/province_atlas_020.npz')['provinces'];idx=np.asarray(Image.open(ROOT/'assets/province_index.png'),np.uint16);lut=(idx[:,:,0]+idx[:,:,1]*256).ravel()
assert len(rs)==1235 and len(w['countries'])==223 and w['scenario_id']=='bunny_world_2000_0_1_10'
assert 40000<len(ps)<65535 and sum(r['population'] for r in rs.values())==6144737528
assert report['provinces']['largest_state_province_count']>800
counts=np.zeros(65536,np.int64)
for i in range(4):
    rgb=np.asarray(Image.open(ROOT/f'assets/region_ids_{i}.png'),np.uint16);ids=rgb[:,:,0]+rgb[:,:,1]*256;sl=np.s_[i//2*4096:(i//2+1)*4096,i%2*8192:(i%2+1)*8192]
    assert np.array_equal(lut[ids],a[sl]);expected=pmap[sl].copy();expected[a[sl]==8191]=65535;assert np.array_equal(ids,expected)
    counts+=np.bincount(ids.ravel(),minlength=65536)
for sid,r in rs.items():
    assert set(r['cores']+r['claims'])<=set(w['country_registry'])
    for local,pid in enumerate(r['provinces'],1):assert ps[str(pid)]['region']==int(sid) and ps[str(pid)]['local_index']==local
for p in ps.values():
    assert counts[p['id']]>0 and p['area_km2']>0
    u,v=p['map_center'];assert int(pmap[min(8191,int(v*8192)),int(u*16384)%16384])==p['id']
    for n in p['neighbors']:assert p['id'] in ps[str(n)]['neighbors']
for tag,c in w['countries'].items():
    assert sum(rs[str(rid)]['population'] for rid in c['regions'])==c['population']==base['countries'][tag]['population']
    before=collections.Counter();after=collections.Counter()
    for r in base['regions'].values():
        if r['owner']==tag:before.update(r.get('buildings',{}))
    for rid in c['regions']:after.update(rs[str(rid)]['buildings'])
    assert before==after,(tag,before,after)
    u,v=c['map_center'];assert rs[str(int(a[min(8191,int(v*8192)),int(u*16384)%16384]))]['owner']==tag
    assert c['starting_stats']['political_power']==100
substantial=np.array([p['area_km2'] for p in ps.values() if p['area_km2']>=1000]);city=np.array([p['area_km2'] for p in ps.values() if p['kind']=='city' and p['area_km2']>=1000])
assert 2400<np.median(substantial)<3600 and np.percentile(substantial,90)<5000
assert 2000<np.median(city)<4000
assert {'Tokyo','Mexico City','New York','Paris','London','Beijing','Warsaw'}<={c for p in ps.values() for c in p['cities']}
assert report['provinces']['per_country']['KOR']['median_area_km2']<4000
assert report['provinces']['per_country']['LUX']['count']==1
islands=report['islands'];north=rs[str(islands['north_chishima_state'])];south=rs[str(islands['south_chishima_state'])];sak=rs[str(islands['karafuto_state'])]
assert north['name']=='North Chishima Islands' and south['name']=='South Chishima Islands'
assert north['source_states']==[690] and south['source_states']==[1168] and sak['source_states']==[691]
assert north['population']==1759 and south['population']==12813 and sak['population']==517809
rights=json.load(open(ROOT/'tools/cartography/md_state_rights.json'))
for r in [north,south,sak]:
    q=rights[str(r['source_states'][0])];assert r['cores']==q['cores'] and r['claims']==q['claims']
for rid in [north['id'],south['id']]:
    yy,xx=np.nonzero(a==rid);lon=(xx+.5)/16384*360-180;lat=90-(yy+.5)/8192*180
    assert not np.any((lon<145)&(lat>45.5))
    assert np.all(lat>=45.5) if rid==north['id'] else np.all(lat<45.5)
def sample(lon,lat):return int(a[min(8191,int((90-lat)/180*8192)),int((lon+180)/360*16384)%16384])
assert sample(142.74,46.95)==sak['id']
for lon,lat,owner in [(34.2,45.1,'UKR'),(33.53,44.6,'UKR'),(41.02,43.0,'ABK'),(43.97,42.23,'SOO'),(41.8,43.1,'GEO'),(44.49,42.12,'GEO'),(98.85,22.17,'WAA'),(98.9,20.2,'WAA')]:assert rs[str(sample(lon,lat))]['owner']==owner
rgb=np.asarray(Image.open(ROOT/'assets/sea_ids.png'),np.uint16);sea=rgb[:,:,0]+rgb[:,:,1]*256;water=a[1::2,1::2]==0;components,_=label(water,np.ones((3,3),np.uint8));sizes=np.bincount(components.ravel());sizes[0]=0;ocean=components==np.argmax(sizes)
assert np.all(sea[~ocean]==0) and np.all(sea[ocean]>0)
seas=json.load(open(ROOT/'data/sea_regions.json'));assert len(seas)==118
for name in ['land','sea','province']:
    assert (ROOT/f'assets/{name}_boundaries.res').stat().st_size>1000
    blob=(ROOT/f'tools/cartography/{name}_boundaries_020.bin').read_bytes();nv,ni=struct.unpack_from('<II',blob);vertices=np.frombuffer(blob,'<f4',nv*3,8).reshape(-1,3);indices=np.frombuffer(blob,'<i4',ni,8+nv*52).reshape(-1,3)[::2];mid=(vertices[indices[:,0]]+vertices[indices[:,2]])*.5;assert np.min(np.linalg.norm(mid,axis=1))>1.000070
print('GEOGRAPHY_020_PASS',len(ps),'provinces; common cell percentiles',np.percentile(substantial,[10,50,90]).round().tolist(),'city median',round(float(np.median(city))),'Karafuto/Chishima rights and conservation pass')
