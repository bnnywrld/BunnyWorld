from pathlib import Path
import json,runpy,collections
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];Image.MAX_IMAGE_PIXELS=None
w=json.load(open(ROOT/'data/world.json'));rs=w['regions'];ps=json.load(open(ROOT/'data/provinces.json'));old=json.load(open(ROOT/'tools/cartography/province_seed_020.json'));base=json.load(open(ROOT/'tools/cartography/world_seed_020.json'))
a=np.load(ROOT/'tools/cartography/grouped_atlas_020.npz')['regions'];pmap=np.load(ROOT/'tools/cartography/province_atlas_021.npz')['provinces'];index=np.asarray(Image.open(ROOT/'assets/province_index.png'),np.uint16);lut=(index[:,:,0]+index[:,:,1]*256).ravel();counts=np.zeros(65536,np.int64)
assert len(ps)==40031 and len(rs)==1235 and w['scenario_id']=='bunny_world_2000_0_2_0'
assert sum(r['population'] for r in rs.values())==6144737528
for i in range(4):
    rgb=np.asarray(Image.open(ROOT/f'assets/region_ids_{i}.png'),np.uint16);ids=rgb[:,:,0]+rgb[:,:,1]*256;sl=np.s_[i//2*4096:(i//2+1)*4096,i%2*8192:(i%2+1)*8192]
    assert np.array_equal(lut[ids],a[sl]);expected=pmap[sl].copy();expected[a[sl]==8191]=65535;assert np.array_equal(ids,expected);counts+=np.bincount(ids.ravel(),minlength=65536)
for sid,r in rs.items():
    original=base['regions'][sid]
    for field in ['owner','population','buildings','cores','claims','source_states']:assert r[field]==original[field],(sid,field)
    for i,pid in enumerate(r['provinces'],1):assert ps[str(pid)]['local_index']==i and ps[str(pid)]['region']==int(sid)
for p in ps.values():
    assert counts[p['id']]>0
    u,v=p['map_center'];assert pmap[min(8191,int(v*8192)),int(u*16384)%16384]==p['id']
    for n in p['neighbors']:assert p['id'] in ps[str(n)]['neighbors']
for k,p in old.items():
    if p['cities']:
        assert k in ps
        assert ps[k]['area_km2']==p['area_km2'] and ps[k]['cities']==p['cities']
report=json.load(open(ROOT/'data/remote_provinces_021_report.json'))
assert report['per_country']['GRN']=={'before':734,'after':290} and report['per_country']['KOR']=={'before':38,'after':38}
assert report['per_country']['LUX']=={'before':1,'after':1}
# GPU lossless channels must agree with the CPU elevation field exactly.
texture=np.asarray(Image.open(ROOT/'assets/relief_data.png'),np.uint16);gpu=texture[:,:,0]+texture[:,:,1]*256;cpu=np.fromfile(ROOT/'assets/relief_data.bin','<u2').reshape(4096,8192);assert np.array_equal(gpu,cpu)
assert cpu.max()/65535*.008<.008 and cpu.max()/65535*.008>.004
land=a[1::2,1::2]>0;assert np.all(cpu[~land]==0)
meters=np.load(ROOT/'tools/cartography/etopo_021.npz')['meters']
def elev(lon,lat):return float(meters[min(4095,int((90-lat)/180*4096)),int((lon+180)/360*8192)%8192])
assert elev(86.8,28.0)>4000 and elev(80.5,31)>4000 and elev(-40,73)>2000
assert elev(-140,0)<-1000
for name in ['land','sea','province']:assert (ROOT/f'assets/{name}_boundaries.res').stat().st_size>1000
print('GEOGRAPHY_021_PASS: all IDs/focuses/adjacency, preserved cities/rights/demographics, 5076 remote-cell reduction, lossless CPU/GPU relief and geographic elevation anchors')
