"""Geographic placement, budgets, historical epoch and accounting invariants."""
from pathlib import Path
from collections import Counter
import json, numpy as np,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from micro_geometry import MicroGeometry
def read(name):return json.loads((ROOT/'data'/f'{name}.json').read_text())
w,p,u,s=map(read,['world','provinces','urban_population','urban_scenery'])
a=np.load(ROOT/'tools/cartography/province_atlas_022r2.npz')['provinces'];H,W=a.shape
micro=MicroGeometry(ROOT)
assert w['scenario_id']=='bunny_world_2000_0_2_0_2' and u['epoch']==2000
assert not u['growth_enabled'] and not s['growth_enabled']
assert 13000<=len(p)<=13500 and len(w['regions'])==1235 and len(w['countries'])==223
assert len(s['landmarks'])==8
all_urban=[];all_shared=[]
country_before=Counter();country_after=Counter()
for sid,state in u['states'].items():
    r=w['regions'][sid]
    city_ids=state['urban_provinces'];rural_ids=state['shared_provinces']
    assert sorted(city_ids+rural_ids)==sorted(r['provinces'])
    assert set(city_ids).isdisjoint(rural_ids)
    assert sum(p[str(pid)]['population_2000'] for pid in city_ids)==state['urban_population_2000']
    assert state['urban_population_2000']+state['shared_population_2000']==r['population']
    assert state['shared_population_2000']>=0
    all_urban+=city_ids;all_shared+=rural_ids
    country_before[r['owner']]+=r['population_before_022'];country_after[r['owner']]+=r['population']
assert country_before==country_after
assert sum(country_after.values())==6144737528
assert len(all_urban)==len(set(all_urban)) and len(all_shared)==len(set(all_shared))
assert len(all_urban)+len(all_shared)==len(p)
group_ids=[];budget=Counter();scene_ids=set()
for group in u['groups'].values():
    ids=group['provinces'];group_ids+=ids
    assert sum(p[str(pid)]['population_2000'] for pid in ids)==group['population_2000']
    assert group['representative_buildings']<=400
    for pid in ids:
        assert p[str(pid)]['urban_group']==group['id'] and p[str(pid)]['name']
assert sorted(group_ids)==sorted(all_urban)
for scene in s['clusters']:
    assert scene['id'] not in scene_ids;scene_ids.add(scene['id'])
    assert p[str(scene['province'])]['urban_group']==scene['group']
    budget[scene['group']]+=len(scene['instances'])
    for lon,lat,width,height,angle,kind in scene['instances']:
        pid=int(a[min(H-1,max(0,int((90-lat)/180*H))),int((lon+180)/360*W)%W])
        pid=micro.resolve(lon,lat,pid)
        assert pid==scene['province'],('building on water / outside province',scene['id'],lon,lat,pid)
        assert 0<width<100 and 0<height<400
for gid,g in u['groups'].items():assert budget[gid]==g['representative_buildings']
for landmark in s['landmarks']:
    assert landmark['opened']<=4000 and str(landmark['province']) in p
    assert w['regions'][str(p[str(landmark['province'])]['region'])]['owner']==landmark['country']
    assert -180<=landmark['longitude']<=180 and -90<=landmark['latitude']<=90
for city in read('cities'):
    if city.get('province_id'):
        assert city['population_2000']==p[str(city['province_id'])]['population_2000']
        assert city['urban_group']==p[str(city['province_id'])]['urban_group']
        assert city['country']==w['regions'][str(p[str(city['province_id'])]['region'])]['owner']
assert all(c.get('province_id') for c in read('cities')), 'every represented settlement is linked'
print('URBAN_DATA_TESTS_PASS:',len(all_urban),'urban provinces;',len(u['groups']),'groups;',sum(budget.values()),'buildings; country totals conserved; all buildings on correct land')
