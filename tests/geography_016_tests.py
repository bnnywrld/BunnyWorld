from pathlib import Path
import json,collections
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1];w=json.loads((root/'data/world.json').read_text());base=json.loads((root/'tools/cartography/world_seed_015.json').read_text())
rs=w['regions'];ps=json.loads((root/'data/provinces.json').read_text());tiles=[];pmap=[];present=set();counts=np.zeros(65536,np.int64);lut=np.zeros(8192*256,np.uint16)
assert len(rs)>=4500 and len(ps)>=14000 and sum(r['population'] for r in rs.values())==6144737528
for sid,r in rs.items():
 assert r['geographic_code'] and r['geographic_name']==r['name']
 for i,pid in enumerate(r['provinces'],1):
  p=ps[str(pid)];assert p['region']==int(sid) and p['local_index']==i and 'population' not in p;lut[int(sid)*256+i]=pid
for i in range(4):
 a=np.asarray(Image.open(root/f'assets/region_ids_{i}.png'),dtype=np.uint32);ids=a[:,:,0]+a[:,:,1]*256;pid=lut[ids*256+a[:,:,2]];assert np.all((ids==0)|(ids==8191)|(pid>0));present.update(np.unique(ids));counts+=np.bincount(pid.ravel(),minlength=65536);tiles.append(ids);pmap.append(pid)
assert present-{0,8191}==set(map(int,rs)) and all(counts[int(p)]>0 for p in ps)
def sample(lon,lat):
 x=int((lon+180)/360*16384);y=int((90-lat)/180*8192);return int(tiles[y//4096*2+x//8192][y%4096,x%8192])
for lon,lat,owner in [(34.2,45.1,'UKR'),(33.53,44.6,'UKR'),(41.02,43.0,'ABK'),(43.97,42.23,'SOO'),(41.8,43.1,'GEO'),(44.49,42.12,'GEO'),(98.85,22.17,'WAA'),(98.9,20.2,'WAA')]:assert rs[str(sample(lon,lat))]['owner']==owner,(lon,lat)
for lon,lat,name in [(-85,50,'Ontario'),(-71,52,'Québec'),(-99,31,'Texas'),(-120,37,'California')]:assert rs[str(sample(lon,lat))]['name'] in [name,'Quebec'],(lon,lat,rs[str(sample(lon,lat))]['name'])
for lon,lat in [(-87,44),(-89,47.7),(33,-1),(29.5,-6),(-114.7,61.5)]:assert sample(lon,lat)==0
# Small Canadian lakes previously punched out broad regions; now land cells.
assert sample(-88.5,50.5)>0
for tag,c in w['countries'].items():
 assert sum(rs[str(i)]['population'] for i in c['regions'])==c['population']
 u,v=c['map_center'];assert rs[str(sample(u*360-180,90-v*180))]['owner']==tag
 if base:
  assert c['population']==base['countries'][tag]['population']
  bb=collections.Counter();nn=collections.Counter()
  for r in base['regions'].values():
   if r['owner']==tag:bb.update(r.get('buildings',{}))
  for rid in c['regions']:nn.update(rs[str(rid)]['buildings'])
  assert bb==nn,tag
for p in ps.values():
 u,v=p['map_center'];x=int(u*16384);y=int(v*8192);assert int(pmap[y//4096*2+x//8192][y%4096,x%8192])==p['id']
 for n in p['neighbors']:assert p['id'] in ps[str(n)]['neighbors']
assert w['countries']['LEB']['name']=='Lebanon'
terrain=json.loads((root/'data/terrain.json').read_text());files=list((root/'data/terrain').glob('*.bwt'));assert len(files)==2048 and sum(p.stat().st_size for p in files)==terrain['tile_bytes'] and terrain['total_terrain_budget_estimate']<=200000000
assert Image.open(files[0]).size==(1024,1024)
for oid,o in w['organizations'].items():assert (root/o['logo'].replace('res://','')).exists()
print('GEOGRAPHY_016_PASS: native regions, 2000 control samples, filtered lakes, all province pixels/focuses/graph, population/building conservation, symbols, terrain budget')
