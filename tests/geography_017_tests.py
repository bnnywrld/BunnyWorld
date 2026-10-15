from pathlib import Path
import json,collections,wave
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1];Image.MAX_IMAGE_PIXELS=None
w=json.loads((root/'data/world.json').read_text());base=json.loads((root/'tools/cartography/world_seed_015.json').read_text())
rs=w['regions'];ps=json.loads((root/'data/provinces.json').read_text());seas=json.loads((root/'data/sea_regions.json').read_text())
assert 1000<=len(rs)<=1500 and len(w['countries'])==223 and sum(r['population'] for r in rs.values())==6144737528
assert len(seas)>=113
lut=np.zeros(8192*256,np.uint16);tiles=[];pmap=[];present=set();counts=np.zeros(65536,np.int64)
for sid,r in rs.items():
    assert r['source_states'] and r['geographic_divisions'] and isinstance(r['cores'],list)
    assert set(r['cores']+r['claims'])<=set(w['country_registry'])
    assert len(r['cores'])==len(set(r['cores'])) and len(r['claims'])==len(set(r['claims']))
    for i,pid in enumerate(r['provinces'],1):
        p=ps[str(pid)];assert p['region']==int(sid) and p['local_index']==i and 'population' not in p;lut[int(sid)*256+i]=pid
for i in range(4):
    a=np.asarray(Image.open(root/f'assets/region_ids_{i}.png'),np.uint32);ids=a[:,:,0]+a[:,:,1]*256;pid=lut[ids*256+a[:,:,2]]
    assert np.all((ids==0)|(ids==8191)|(pid>0));present.update(np.unique(ids));counts+=np.bincount(pid.ravel(),minlength=65536);tiles.append(ids);pmap.append(pid)
assert present-{0,8191}==set(map(int,rs)) and all(counts[int(p)]>0 for p in ps)
def sample(lon,lat):
    x=int((lon+180)/360*16384)%16384;y=min(8191,int((90-lat)/180*8192));return int(tiles[y//4096*2+x//8192][y%4096,x%8192])
for lon,lat,owner in [(34.2,45.1,'UKR'),(33.53,44.6,'UKR'),(41.02,43.0,'ABK'),(43.97,42.23,'SOO'),(41.8,43.1,'GEO'),(44.49,42.12,'GEO'),(98.85,22.17,'WAA'),(98.9,20.2,'WAA')]:assert rs[str(sample(lon,lat))]['owner']==owner
for lon,lat,name in [(-85,50,'Ontario'),(-71,52,'Eastern Quebec'),(-76,49,'Western Quebec'),(-73,58,'Ungava'),(-99,31,'Texas'),(-120,37,'California'),(139.75,35.68,'Kanto'),(116.4,39.9,'Beijing'),(98.85,22.17,'Northern Wa'),(98.9,20.2,'South Wa')]:assert rs[str(sample(lon,lat))]['name']==name,(lon,lat,rs[str(sample(lon,lat))]['name'])
for lon,lat in [(-87,44),(-89,47.7),(33,-1),(29.5,-6),(-114.7,61.5)]:assert sample(lon,lat)==0
for tag,c in w['countries'].items():
    assert sum(rs[str(i)]['population'] for i in c['regions'])==c['population']==base['countries'][tag]['population']
    u,v=c['map_center'];assert rs[str(sample(u*360-180,90-v*180))]['owner']==tag
    old=collections.Counter();new=collections.Counter()
    for r in base['regions'].values():
        if r['owner']==tag:old.update(r.get('buildings',{}))
    for rid in c['regions']:new.update(rs[str(rid)]['buildings'])
    assert old==new,tag
for p in ps.values():
    u,v=p['map_center'];x=int(u*16384);y=int(v*8192);assert int(pmap[y//4096*2+x//8192][y%4096,x%8192])==p['id']
    for neighbor in p['neighbors']:assert p['id'] in ps[str(neighbor)]['neighbors']
for c in seas.values():
    u,v=c['map_center'];assert sample(u*360-180,90-v*180)==0
    assert 'owner' not in c and 'population' not in c
    for n in c['neighbors']:assert c['id'] in seas[str(n)]['neighbors']
terrain=json.loads((root/'data/terrain.json').read_text());files=list((root/'data/terrain').glob('*.bwt'))
assert len(files)==2048 and sum(p.stat().st_size for p in files)==terrain['tile_bytes'] and terrain['total_terrain_budget_estimate']<=200000000
assert terrain['urban_footprints']>1000 and Image.open(root/'assets/urban_density.png').getextrema()[1]>200
for file in (root/'assets/sounds').glob('*.wav'):
    with wave.open(str(file)) as audio:assert audio.getnchannels()==1 and audio.getframerate()==44100 and 0<audio.getnframes()/44100<.3
for oid,o in w['organizations'].items():assert (root/o['logo'].replace('res://','')).exists()
for name in ['land','sea']:assert (root/f'assets/{name}_boundaries.res').stat().st_size>1000
print('GEOGRAPHY_017_PASS: grouped areas, protected geography, all region/province pixels and focuses, conserved totals, cores/claims, water, terrain/cities, sounds and meshes')
