"""Increase representative skylines while preserving population, group and province IDs."""
from pathlib import Path
from collections import Counter
import json,math,random,sys
import numpy as np
from micro_geometry import MicroGeometry
ROOT=Path(__file__).resolve().parents[1]
s=json.loads((ROOT/'data/urban_scenery.json').read_text());u=json.loads((ROOT/'data/urban_population.json').read_text())
a=np.load(ROOT/'tools/cartography/province_atlas_022r2.npz')['provinces'];H,W=a.shape;micro=MicroGeometry(ROOT)
def pid_at(lon,lat):return micro.resolve(lon,lat,int(a[min(H-1,max(0,int((90-lat)/180*H))),int((lon+180)/360*W)%W]))
count=Counter()
for c in s['clusters']:
    rng=random.Random(c['id']+201001);old=c['instances'];factor=4 if c['category'] in ['Town','City'] else 5
    new=[]
    for item in old:
        new.append(item)
        for j in range(factor-1):
            lon,lat=item[:2];chosen=(lon,lat)
            for attempt in range(80):
                angle=rng.random()*math.tau;radius=(1.6 if factor==4 else 4.8)*math.sqrt(rng.random())
                x=lon+math.cos(angle)*radius/(111.195*max(.1,math.cos(math.radians(lat))))
                y=lat+math.sin(angle)*radius/111.195
                if pid_at(x,y)==c['province']:chosen=(x,y);break
            tall=item[5]==1 and j%2==0
            height=item[3]*rng.uniform(.75,1.12) if tall else rng.uniform(14,55)
            new.append([round(chosen[0],6),round(chosen[1],6),round(rng.uniform(22,44),1),round(height,1),round(rng.random()*math.tau,3),int(tall)])
    c['instances']=new;count[c['group']]+=len(new)
for gid,g in u['groups'].items():
    g['representative_buildings']=count[gid]
    assert count[gid]<=200
s.update(building_cap=1024,cluster_cap=64,display_size_multiplier=3.0,version='0.2.0.1')
for name,data in [('urban_scenery',s),('urban_population',u)]:
    (ROOT/'data'/f'{name}.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
print('SCENERY_EXPANDED buildings=',sum(count.values()),'max_group=',max(count.values()),flush=True)
