from pathlib import Path
from collections import defaultdict
import hashlib,json,math
import numpy as np
R=Path(__file__).resolve().parents[1];checks=0
def read(n):return json.loads((R/n).read_text())
def check(value,label):
 global checks
 checks+=1
 assert value,label
def main():
 w=read('data/world.json');sd=read('data/state_demographics.json')['states'];p=read('data/demographics.json')['profiles'];r=read('data/demographics_0227_report.json');by=defaultdict(list)
 check((len(w['countries']),len(w['regions']),len(read('data/provinces.json')))==(224,1264,13308),'counts')
 check(set(sd)==set(w['regions']),'complete coverage');check(set(w['countries'])<=set(p),'national coverage')
 check(hashlib.sha256((R/'data/provinces.json').read_bytes()).hexdigest()==r['baseline_geography']['province_json_sha256'],'unchanged province data')
 fingerprint=hashlib.sha256(json.dumps(sorted([[s['id'],s['owner'],s['provinces']]for s in w['regions'].values()])).encode()).hexdigest();check(fingerprint==r['baseline_geography']['state_ownership_membership_sha256'],'unchanged membership/ownership')
 for n,h in r['population_grid']['registration']['province_tiles_sha256'].items():check(hashlib.sha256((R/n).read_bytes()).hexdigest()==h,'unchanged tile '+n)
 for k,s in w['regions'].items():
  d=sd[k];by[s['owner']].append(k);check(s['population']==d['population_2000']and s['population']>=0,'population '+k);age=np.array(d['age_single_year']);check(len(age)==101 and np.isfinite(age).all()and np.all(age>=0)and abs(age.sum()-1)<1e-8,'age '+k);check(abs(d['adult25_share']-age[25:].sum())<1e-10,'adult25 '+k);check(set(d['metrics'])=={'age','religion','education'},'three metrics '+k)
  for key,m in d['metrics'].items():
   a=m['shares'];check(a and 'Unknown'not in a and a.get('Other / unspecified',0)<.99 and all(math.isfinite(v)and v>=0 for v in a.values())and abs(sum(a.values())-1)<1e-8,'shares '+key+k);check(m['source']and m['status']and m['year']==2000,'provenance '+key+k)
  for key in ['participation_rate','unemployment_rate']:check(0<=s['workforce'][key]<=1 and s['workforce'][key]==d['workforce'][key],'workforce '+key+k)
 for tag,ids in by.items():
  check(w['countries'][tag]['population']==sum(w['regions'][k]['population']for k in ids),'country sum '+tag);weights=np.array([max(w['regions'][k]['population'],1)for k in ids]);a=np.array([sd[k]['age_single_year']for k in ids]);check(np.max(np.abs(np.average(a,weights=weights,axis=0)-p[tag]['age_single_year']))<1e-6,'age reconciliation '+tag);ad=weights*np.array([sd[k]['adult25_share']for k in ids]);keys=['Below primary','Primary','Secondary','Tertiary'];edu=np.array([[sd[k]['metrics']['education']['shares'][x]for x in keys]for k in ids]);target=np.array([p[tag]['metrics']['education']['shares'][x]for x in keys]);check(np.max(np.abs(np.average(edu,weights=ad,axis=0)-target))<1e-6,'education reconciliation '+tag)
 def state(t,n):return next(sd[k]for k,s in w['regions'].items()if s['owner']==t and s['name']==n)
 check(state('RAJ','Delhi')['metrics']['education']['shares']['Tertiary']>state('RAJ','Bihar')['metrics']['education']['shares']['Tertiary'],'Delhi vs Bihar')
 check(state('CHI','Beijing')['metrics']['education']['shares']['Tertiary']>state('CHI','Tibet')['metrics']['education']['shares']['Tertiary'],'Beijing vs Tibet')
 check(state('SYR','As-Suwayda')['metrics']['religion']['shares']['Druze']>.7,'Druze geography')
 check(state('NIG','Borno')['metrics']['religion']['shares']['Sunni']>.7 and state('NIG','Biafra')['metrics']['religion']['shares']['Christian (unspecified)']>.8,'Nigeria geography')
 check(w['regions']['1687']['population']==33871648,'California 2000 census')
 check(r['religion_regional_overrides']>=210,'regional religion coverage')
 check(sum(s['population']for s in w['regions'].values())==r['population_after'],'world population')
 check(state('USA','Hawally')['population_2000']>400000 and state('USA','Hawally')['metrics']['religion']['shares']['Sunni']>.5,'inhabited foreign footprint')
 check(state('FRA','Mayotte')['metrics']['religion']['shares']['Sunni']>.9,'Mayotte local religion')
 out={'passed':True,'checks':checks,'states':1264,'countries':224,'population':r['population_after'],'religion_regional_estimates':r['religion_regional_overrides'],'province_data_and_tiles_unchanged':True,'all_states_complete':True,'regional_values_are_estimates':True};(R/'validation_0227').mkdir(exist_ok=True);(R/'validation_0227/data_results.json').write_text(json.dumps(out,indent=2)+'\n');print('DATA_PASS',out)
if __name__=='__main__':main()
