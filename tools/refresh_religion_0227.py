"""Apply audited regional patterns and consistent exclusive religion labels."""
from collections import defaultdict
from build_demographics_0227 import read,write,norm
from curation_0227 import RELIGION_NATIONAL,RELIGION_CONTROLLER,REGIONAL_RELIGION

def canonical(shares):
 merged=defaultdict(float);aliases={'Christian':'Christian (unspecified)','Other Christian':'Christian (other)','Lutheran':'Protestant'}
 for name,value in shares.items():merged[aliases.get(name,name)]+=value
 return norm(merged)
def main():
 import copy
 w=read('data/world.json');d=read('data/demographics.json');sd=read('data/state_demographics.json');r=read('data/demographics_0227_report.json');count=0
 for tag,p in d['profiles'].items():
  if p['iso3']in RELIGION_NATIONAL:p['metrics']['religion'].update(shares=norm(RELIGION_NATIONAL[p['iso3']]),source='Curated historical national estimate; tools/curation_0227.py',year=2000,status='educated historical estimate')
  if tag in RELIGION_CONTROLLER:p['metrics']['religion'].update(shares=norm(RELIGION_CONTROLLER[tag]),source='Curated historical controller-area estimate; tools/curation_0227.py',year=2000,status='educated controller-area estimate')
 for k,s in w['regions'].items():
  tag=s['owner'];m=copy.deepcopy(d['profiles'][tag]['metrics']['religion']);choices=[x for x in REGIONAL_RELIGION if x[0]==tag and x[1].casefold()in s['name'].casefold()]
  if choices:
   _,pattern,shares=max(choices,key=lambda x:len(x[1]));m.update(shares=norm(shares),source='Historical regional pattern: '+pattern+'; curated circa-2000 estimate',year=2000,status='educated regional estimate; not a local census observation',reference='tools/curation_0227.py and documentation/DEMOGRAPHICS_0227.md');count+=1
  else:m['status']='historical country/controller proxy; no unsupported local religious variation added'
  m['benchmark_year']=m['year'];m['year']=2000;m['shares']=canonical(m['shares']);sd['states'][k]['metrics']['religion']=m
 for p in d['profiles'].values():p['metrics']['religion']['shares']=canonical(p['metrics']['religion']['shares'])
 r['religion_regional_overrides']=count
 write('data/demographics.json',d);write('data/state_demographics.json',sd);write('data/demographics_0227_report.json',r);print('REGIONAL_RELIGION_ESTIMATES',count)
if __name__=='__main__':main()
