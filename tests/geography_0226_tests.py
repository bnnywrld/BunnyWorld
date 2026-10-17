"""Regression checks for .26 whole-province geography and preserved scenario totals."""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from review_states_0226 import components
checks=0
def read(n):return json.loads((R/n).read_text())
def old(n):return subprocess.check_output(['git','show','aeacb59:'+n],cwd=R)
def check(ok,label):
 global checks
 checks+=1
 assert ok,label
def inventory(w,tag):
 b=Counter();slots=pop=0
 for s in w['regions'].values():
  if s['owner']==tag:b.update(s['buildings']);slots+=s['building_slot_baseline'];pop+=s['population']
 return pop,dict(b),slots

def main():
 w,ps=read('data/world.json'),read('data/provinces.json');before,op=json.loads(old('data/world.json')),json.loads(old('data/provinces.json'))
 report=read('data/geography_0226_report.json');changed=set(report['changed_states']);targets={'CHI':44,'SYR':14,'RAJ':44,'MOR':11,'PAK':11,'COL':8}
 check((len(w['countries']),len(w['regions']),len(ps))==(224,1264,13308),'counts')
 check(w['version']=='0.2.0.26'and w['scenario_id']=='bunny_world_2000_0_2_0_26','new scenario')
 check(set(ps)==set(op),'province IDs')
 membership=defaultdict(list)
 for k,p in ps.items():
  membership[p['region']].append(p['id']);check(p['region']in map(int,w['regions']),'no orphan province '+k)
  check(w['regions'][str(p['region'])]['owner']==before['regions'][str(op[k]['region'])]['owner'],'ownership retained '+k)
  check({x:v for x,v in p.items()if x not in ['region','local_index','name']}=={x:v for x,v in op[k].items()if x not in ['region','local_index','name']},'province geometry/buildings/adjacency retained '+k)
  if before['regions'][str(op[k]['region'])]['owner']not in targets:check(p==op[k],'excluded province unchanged '+k)
 for t,c in w['countries'].items():
  check(inventory(w,t)==inventory(before,t),'population, buildings, slots retained '+t)
  check(c['regions']==sorted(s['id']for s in w['regions'].values()if s['owner']==t),'country list '+t)
  check(c['capital']in c['regions'],'national capital '+t)
  if t in targets:check(len(c['regions'])==targets[t],'target count '+t)
  else:check(c==before['countries'][t],'excluded country unchanged '+t)
 check(sum(s['population']for s in w['regions'].values())==6144737528,'global population')
 d=read('data/demographics.json')['profiles'];urban=read('data/urban_population.json')['states']
 check(set(urban)==set(w['regions']),'urban coverage')
 for k,s in w['regions'].items():
  ids=s['provinces'];check(ids and sorted(ids)==sorted(membership[s['id']]),'nonempty exact membership '+k)
  check(len({ps[str(i)]['local_index']for i in ids})==len(ids),'local indices '+k)
  check(s['capital_province']in ids,'state capital in state '+k)
  check(s['id']not in changed or (s['population']>0 and s['demographic_profile']in d),'complete population/profile '+k)
  check(urban[k]['population_2000']==s['population'],'urban population '+k)
  check(all(str(n)in w['regions']and s['id']in w['regions'][str(n)]['neighbors']for n in s['neighbors']),'symmetric adjacency '+k)
  if s['owner']not in targets:check({x:v for x,v in s.items()if x!='neighbors'}=={x:v for x,v in before['regions'][k].items()if x!='neighbors'},'excluded state geography unchanged '+k)
 for c in read('data/cities.json'):
  if str(c.get('province_id'))in ps and 'state_id'in c:check(c['state_id']==ps[str(c['province_id'])]['region'],'city reference '+c['name'])
 for kind in ['clusters','landmarks']:
  for c in read('data/urban_scenery.json')[kind]:check(c['state']==ps[str(c['province'])]['region'],'scenery reference')
 for row in read('data/protected_territories_0210.json')['territories']:check(all(str(i)in w['regions']for i in row['states']),'protected references')
 for i in range(4):
  name=f'assets/region_ids_{i}.png';check(hashlib.sha256((R/name).read_bytes()).digest()==hashlib.sha256(old(name)).digest(),'canonical tile byte identical '+str(i))
 check(w['map']['antarctica_province_id']==65535 and w['map']['antarctica_region_id']==8191,'Antarctica retained')
 check(len(w['countries']['MIC']['regions'])==1 and len(w['countries']['PAP']['regions'])==4,'Micronesia and four Papua states')
 check(ps['12397']['region']==1735 and ps['13026']['region']==1707 and ps['13037']['region']==1707,'Mariana and Hawaii unions')
 # Only genuine inherited island components may remain disconnected.
 allowed={s['id']for s in w['regions'].values()if s['name']in ['Pearl River Delta','Saurashtra–Kutch','Caribe']}
 for sid in changed:
  s=w['regions'][str(sid)];parts=components(s['provinces'],ps)
  check(len(parts)==1 or sid in allowed,'connected mainland '+str(sid))
 check(all('geometry'not in g for p in read('data/state_plan_0226.json')['plans']for g in p['groups']),'no redistributed reference polygons')
 result={'passed':True,'checks':checks,'countries':224,'states':1264,'land_provinces':13308,'new_states':29,'global_population':6144737528,'country_totals_preserved':True,'canonical_province_tiles_byte_identical':True,'excluded_country_geography_preserved':True,'disconnected_groups':'Only retained Pearl River Delta coastal island, Diu in Saurashtra–Kutch, and approved Colombian Caribbean islands/banks.'}
 out=R/'validation_0226';out.mkdir(exist_ok=True);(out/'geography_results.json').write_text(json.dumps(result,indent=2)+'\n');print('GEOGRAPHY_0226_PASS',result)
if __name__=='__main__':main()
