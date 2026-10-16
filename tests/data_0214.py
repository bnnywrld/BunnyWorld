"""Release integrity checks; run from repository root."""
from pathlib import Path
from collections import Counter, defaultdict
import json, zlib, math
R=Path(__file__).resolve().parents[1]
read=lambda p:json.loads((R/p).read_text())
w=read('data/world.json');ps=read('data/provinces.json');report=read('data/geography_0214_report.json')
assert len(w['regions'])==1355 and len(ps)==13594
assert not set(report['merges']).intersection(w['regions'])
assert w['regions']['363']['provinces']==[3865] and ps['3865']['local_index']==6
assert set(w['regions']['1826']['provinces'])=={3858,3860,3861,3863,3864}
levels={'infrastructure','internet_station','air_base','radar_station','rail_terminal','anti_air_building','stronghold_network'}
seen=[];totals=Counter()
for key,r in w['regions'].items():
 assert r['capital_province'] in r['provinces'] and r['state_capital']
 seen+=r['provinces'];totals[r['owner']]+=r['population']
 for pid in r['provinces']:assert ps[str(pid)]['region']==int(key)
 for k,n in r['buildings'].items():assert n>=0 and (k not in levels or n<=10)
 assert r['building_slot_baseline']>=sum(n for k,n in r['buildings'].items() if k not in levels)
assert len(seen)==len(set(seen))==len(ps)
assert sum(totals.values())==6144737528
assert all(totals[tag]==c['population'] for tag,c in w['countries'].items())
assert all('population_2000' not in p and 'population' not in p for p in ps.values())
scene=read('data/urban_scenery.json');weights=defaultdict(float)
assert sum(len(c['instances']) for c in scene['clusters'])==85643
for c in scene['clusters']:weights[c['state']]+=c['state_visual_weight']
assert all(abs(v-1)<1e-6 for v in weights.values())
index=read('assets/display/selection_distance.json');b=(R/'assets/display/selection_distance.bwd').read_bytes()
assert set(index['states'])==set(w['regions']) and set(index['provinces'])==set(ps)
assert set(index['seas'])==set(read('data/sea_regions.json'))
records=0
for scope in ['states','provinces','seas']:
 for key,r in index[scope].items():
  assert len(zlib.decompress(b[r[4]:r[4]+r[5]]))==r[6]*r[7],(scope,key)
  records+=1
result={'passed':True,'states':1355,'provinces':13594,'validated_mask_records':records,'decorative_buildings':85643,'capital_settlements':report['settlement_capitals'],'administrative_anchors':report['administrative_anchors'],'country_population_conservation':True}
(R/'validation_0214/data_results.json').write_text(json.dumps(result,indent=2));print(result)
