"""Complete 2000 regional estimates; deterministic, sourced and auditable.
Run once against .26. Population grid must be registered to current provinces.
"""
from pathlib import Path
from collections import defaultdict,Counter
import copy,csv,hashlib,json,math
import numpy as np
from curation_0227 import *
R=Path(__file__).resolve().parents[1];D=R/'tools/sources_0227'
def read(n):return json.loads((R/n).read_text())
def write(n,x): (R/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def norm(d):
 a={k:max(0,float(v))for k,v in d.items()if float(v)>0};total=sum(a.values());assert total>0
 return {k:v/total for k,v in a.items()}
def allocation(total,weights):
 a=np.array(weights,float);a=a/a.sum()*total;b=np.floor(a).astype(np.int64);b[np.argsort(-(a-b),kind='stable')[:int(total-b.sum())]]+=1;return list(map(int,b))
def fit(rows,weights,target):
 a=np.asarray(rows,float);w=np.maximum(np.asarray(weights,float),1e-9);a=np.maximum(a,1e-12);a/=a.sum(1)[:,None];target=np.asarray(target,float);target/=target.sum()
 for _ in range(100):
  mean=np.average(a,axis=0,weights=w);a*=target/np.maximum(mean,1e-30);a/=a.sum(1)[:,None]
 return a

def main():
 w=read('data/world.json');assert w['version']=='0.2.0.26';old=copy.deepcopy(w);ps=read('data/provinces.json');base=read('data/demographics.json');grid=read('data/population_grid_0227.json')
 for n,h in grid['registration']['province_tiles_sha256'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h
 p=copy.deepcopy(base['profiles']);education_rows={x['WBcode']:x for x in csv.DictReader(open(R/'tools/sources_020/barro_lee_25plus.csv'))if x['year']=='2000'and x['sex']=='MF'and x['agefrom']=='25'}
 # Correct missing country records / proxy boundaries without changing geography.
 for tag,peer,iso in [('NAU','FIJ','NRU'),('TIM','PAP','TLS')]:
  p[tag]=copy.deepcopy(p[peer]);p[tag].update(iso3=iso,source_country=w['countries'][tag]['name'],proxy=True);p[tag]['age_note']='Year-2000 regional peer age estimate: '+peer
 p['SSU']['iso3']='SSD';p['BAH']['iso3']='BHS';p['SHA']['iso3']='ESH'
 for tag,peer in [('BAH','BAR'),('SHA','MOR')]:
  p[tag]['age_single_year']=copy.deepcopy(p[peer]['age_single_year']);p[tag]['age_note']='Year-2000 regional peer age estimate: '+peer
 # Replace national education with exact 2000 Barro-Lee completed attainment where available.
 for tag,profile in p.items():
  row=education_rows.get(profile['iso3']);meta=profile['metrics']['education']
  if row:
   lu,lp,lpc,ls,lsc,lh,lhc=[float(row[k])for k in ['lu','lp','lpc','ls','lsc','lh','lhc']]
   meta.update(shares=norm({'Below primary':lu+lp-lpc,'Primary':lpc+ls-lsc,'Secondary':lsc+lh-lhc,'Tertiary':lhc}),source='Barro-Lee 2013 dataset, 2000, MF, age 25+; highest completed level',year=2000,status='national modeled educational-attainment benchmark')
  # Complete every missing religion profile using explicit historical estimates.
  if profile['iso3']in RELIGION_NATIONAL:
   profile['metrics']['religion'].update(shares=norm(RELIGION_NATIONAL[profile['iso3']]),source='Curated historical national estimate; see documentation/DEMOGRAPHICS_0227.md',year=2000,status='educated estimate; religious identity categories are exclusive scenario groups',reference='Historical context in tools/curation_0227.py; exact percentages are estimates, not census observations.')
  if tag in RELIGION_CONTROLLER:profile['metrics']['religion']['shares']=norm(RELIGION_CONTROLLER[tag]);profile['metrics']['religion']['status']='educated controller-area estimate for 2000'
 for tag,profile in p.items():
  edu=profile['metrics']['education']
  if edu['shares'].get('Unknown'):
   peer=EDUCATION_PROXIES.get(tag,'')
   if peer in p and not p[peer]['metrics']['education']['shares'].get('Unknown'):shares=p[peer]['metrics']['education']['shares'];note='historical regional peer '+peer
   else:shares={'Below primary':.4,'Primary':.36,'Secondary':.2,'Tertiary':.04};note='broad 2000 development estimate'
   edu.update(shares=norm(shares),source=note,year=2000,status='educated national proxy; regional estimates are not observations')
  edu['shares']=norm({k:edu['shares'].get(k,0)for k in ['Below primary','Primary','Secondary','Tertiary']})
  assert not profile['metrics']['religion']['shares'].get('Unknown'),('unfilled religion',tag)
  age=np.array(profile['age_single_year'],float);assert len(age)==101 and age.sum()>0;profile['age_single_year']=(age/age.sum()).tolist()
 pop={};pop_source={};dense={}
 for k,s in w['regions'].items():
  n=sum(grid['provinces'][str(i)]['population']for i in s['provinces']);pop[k]=max(0,round(n));pop_source[k]='GHSL 2000 current-province grid sum';dense[k]=sum(grid['provinces'][str(i)]['dense_population']for i in s['provinces'])/max(n,1)
  if s['name']in SMALL_POPULATION and (SMALL_POPULATION[s['name']]>0 or n<20):
   pop[k]=SMALL_POPULATION[s['name']];pop_source[k]='Curated 2000 small-territory resident estimate; excludes transient military personnel'
 # Official US census population for the 50 states, DC and Puerto Rico.
 us=D/'us_population_2000.xls';benchmarks=[]
 if us.exists():
  import xlrd
  sheet=xlrd.open_workbook(us).sheet_by_index(0);facts={str(sheet.cell_value(i,0)).strip():round(sheet.cell_value(i,1))for i in range(sheet.nrows)if isinstance(sheet.cell_value(i,1),(float,int))and sheet.cell_value(i,1)>0}
  for k,s in w['regions'].items():
   name='District of Columbia'if s['name']=='Washington, D.C.'else s['name']
   if s['owner']=='USA'and name in facts:pop[k]=facts[name];pop_source[k]='U.S. Census 2000 resident population, April 1; accepted state footprint';benchmarks.append({'states':[int(k)],'population':pop[k],'source':'https://www.census.gov/data/tables/2000/dec/2000-resident-population.html'})
 # National models validate scale; no blind national rescaling across disputed or overseas borders.
 wdi=read('tools/sources_0227/SP.POP.TOTL.json');national={x['countryiso3code']:x['value']for x in wdi[1]if x['value']is not None}
 # Match complete small island country counts where coarse cells are least reliable.
 for tag,isos in [('NAU',['NRU']),('TIM',['TLS']),('MIC',['FSM','PLW']),('TUL',['TUV']),('MLD',['MDV']),('SIN',['SGP']),('MAC',['MAC']),('HKG',['HKG']),('MLT',['MLT'])]:
  ids=[str(i)for i in w['countries'][tag]['regions']];target=sum(national.get(iso,0)for iso in isos)
  if target:
   values=allocation(round(target),[max(pop[k],1)for k in ids])
   for k,v in zip(ids,values):pop[k]=v;pop_source[k]='World Bank WDI year 2000 national benchmark ('+' + '.join(isos)+'); grid shares within country'
   benchmarks.append({'country':tag,'population':round(target),'source':'https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?date=2000&format=json&per_page=20000'})
 states={};by_tag=defaultdict(list)
 for k,s in w['regions'].items():by_tag[s['owner']].append(k)
 participation={};unemployment={}
 for tag in by_tag:
  profile=p[tag];act=profile['metrics'].get('activity',{}).get('shares',{});part=act.get('Employed',0)+act.get('Unemployed',0)
  participation[tag]=part if part>0 else .60;unemployment[tag]=act.get('Unemployed',0)/part if part>0 else .08
 for tag,ids in by_tag.items():
  profile=p[tag];weights=[max(pop[k],1)for k in ids];baseline=np.asarray(profile['age_single_year']);mean_urban=np.average([dense[k]for k in ids],weights=weights);scores=[];religions=[]
  for k in ids:
   s=w['regions'][k];capital=s['id']==w['countries'][tag]['capital'];context=1.
   for name,value in EDUCATION_CONTEXT.get(tag,{}).items():
    if name.casefold()in s['name'].casefold():context=value;break
   score=float(np.clip((dense[k]-mean_urban)*.9+(.18 if capital and len(ids)>1 else 0)+math.log(context),-.7,.7));scores.append(score)
   religion=copy.deepcopy(profile['metrics']['religion']);matches=[x for x in REGIONAL_RELIGION if x[0]==tag and x[1].casefold()in s['name'].casefold()]
   if matches:
    _,pattern,values=max(matches,key=lambda x:len(x[1]));religion.update(shares=norm(values),source='Historical regional pattern: '+pattern+'; curated circa-2000 estimate',year=2000,status='educated regional estimate; not a local census observation',reference='tools/curation_0227.py and documentation/DEMOGRAPHICS_0227.md')
   else:
    religion['status']='regional proxy from '+str(religion.get('source','national reference'))+'; no unsupported local religious variation added'
   religion['benchmark_year']=religion['year'];religion['year']=2000
   religions.append(religion)
  # Rich rural areas often age; in younger countries rural fertility raises child shares.
  rich=float(baseline[:18].sum())<.30
  direction=np.array([(-.35 if age<18 else (.55 if age<45 else (.05 if age<65 else -.7)))if rich else (-.65 if age<18 else (.45 if age<65 else -.1))for age in range(101)])
  ages=fit([baseline*np.exp(direction*score)for score in scores],weights,baseline)
  edu_keys=['Below primary','Primary','Secondary','Tertiary'];edu=norm(profile['metrics']['education']['shares']);ev=np.array([edu.get(x,0)for x in edu_keys]);ev=ev/ev.sum()
  adult_weights=[max(pop[k],1)*float(ages[i,25:].sum())for i,k in enumerate(ids)]
  education=fit([ev*np.exp(np.array([-1.,-.35,.4,1.2])*score)for score in scores],adult_weights,ev)
  for i,k in enumerate(ids):
   s=w['regions'][k];age=ages[i];retirement=profile.get('retirement_age',65);age_shares={'Underage':float(age[:18].sum()),'Working age':float(age[18:retirement].sum()),'Retired':float(age[retirement:].sum())}
   met={'age':{'shares':age_shares,'source':'World Bank / UN 2000 country cohorts; settlement-context regional model','year':2000,'status':'educated regional estimate, reconciled to country age benchmark','reference':profile.get('age_note','Existing 2000 WDI single-age interpolation')},'religion':religions[i],'education':{'shares':dict(zip(edu_keys,map(float,education[i]))),'source':profile['metrics']['education']['source'],'year':2000,'benchmark_year':profile['metrics']['education']['year'],'status':'educated regional allocation; adults 25+; nationally reconciled','reference':'Urban settlement share, national-capital role and explicit regional education context. '+profile['metrics']['education'].get('status','')}}
   part=float(np.clip(participation[tag]+.045*scores[i],.25,.9));u=float(np.clip(unemployment[tag]*(1+.35*scores[i]),.005,.45))
   states[k]={'state':int(k),'country_at_start':tag,'population_2000':pop[k],'population_source':pop_source[k],'age_single_year':list(map(float,age)),'adult25_share':float(age[25:].sum()),'retirement_age':retirement,'metrics':met,'workforce':{'participation_rate':part,'unemployment_rate':u,'source':'2000 WDI / ILO national rates where present; educated regional variation','year':2000,'status':'modeled 18-to-retirement workforce using 15+ participation benchmark; not observed regional unemployment','benchmark_available':profile['metrics'].get('activity',{}).get('shares',{}).get('Unknown')!=1},'context':{'dense_settlement_population_share':dense[k],'education_context_score':scores[i],'national_capital':s['id']==w['countries'][tag]['capital']}}
   s['population']=pop[k];s['population_source']=pop_source[k];s['workforce']=copy.deepcopy(states[k]['workforce'])
 # Calibrate employment rates to national benchmarks with correct denominators.
 for tag,ids in by_tag.items():
  workers=np.array([pop[k]*sum(states[k]['age_single_year'][18:p[tag].get('retirement_age',65)])for k in ids]);rates=np.array([states[k]['workforce']['participation_rate']for k in ids]);ur=np.array([states[k]['workforce']['unemployment_rate']for k in ids])
  if workers.sum()>0:
   for _ in range(30):rates=np.clip(rates*participation[tag]/max(np.average(rates,weights=workers),1e-20),.2,.95)
   lf=workers*rates
   for _ in range(30):ur=np.clip(ur*unemployment[tag]/max(np.average(ur,weights=lf),1e-20),.001,.6)
  for k,part,u in zip(ids,rates,ur):
   states[k]['workforce'].update(participation_rate=float(part),unemployment_rate=float(u));w['regions'][k]['workforce']=copy.deepcopy(states[k]['workforce'])
 for tag,c in w['countries'].items():c['population']=sum(w['regions'][str(sid)]['population']for sid in c['regions'])
 urban=read('data/urban_population.json');urban['states']={k:{'population_2000':s['population']}for k,s in w['regions'].items()};urban['source']={'method':'State population is GHSL 2000 on current geography, with documented census/small-country benchmarks. Province/city populations are not simulated.'}
 w.update(version='0.2.0.27',scenario_id='bunny_world_2000_0_2_0_27');w['map']['urban_population']='Registered GHSL 2000 state populations; sourced census and small-country benchmarks; state-specific age/education estimates and historical regional religion estimates.'
 source={'version':2,'year':2000,'states':states,'method':'Complete regional estimates: national demographic benchmarks plus deterministic settlement context and curated regional religious/education patterns. No random state-ID noise. Education denominator 25+; workforce denominator age 18 to current retirement.'}
 base.update(version=2,profiles=p,local_method=source['method'],activity_denominator='Workforce figures stored separately; unemployment is a share of labour force, participation is a share of modeled working-age residents.')
 report={'version':'0.2.0.27','baseline_geography':{'province_json_sha256':hashlib.sha256((R/'data/provinces.json').read_bytes()).hexdigest(),'state_ownership_membership_sha256':hashlib.sha256(json.dumps(sorted([[s['id'],s['owner'],s['provinces']]for s in old['regions'].values()])).encode()).hexdigest()},'states':len(states),'countries':len(w['countries']),'population_before':sum(s['population']for s in old['regions'].values()),'population_after':sum(pop.values()),'population_grid':{k:v for k,v in grid.items()if k!='provinces'},'benchmarks':benchmarks,'country_changes':[{'tag':t,'name':c['name'],'before':old['countries'][t]['population'],'after':c['population'],'wdi_2000_reference':national.get(p[t]['iso3']),'wdi_scope_note':'Reference may exclude overseas territories or include separate scenario controllers; no blind reconciliation across mismatching borders.'}for t,c in w['countries'].items()],'population_source_counts':dict(Counter(pop_source.values())),'religion_regional_overrides':sum('educated regional estimate'in s['metrics']['religion']['status']for s in states.values()),'national_profiles_completed':True,'province_membership_changed':False,'demography_fully_simulated':False}
 for n,x in [('data/world.json',w),('data/demographics.json',base),('data/state_demographics.json',source),('data/urban_population.json',urban),('data/demographics_0227_report.json',report)]:write(n,x)
 for n in ['project.godot','export_presets.cfg']:
  path=R/n;path.write_text(path.read_text().replace('0.2.0.26','0.2.0.27').replace('State Detail','Population and Demographics'))
 info=read('BUILD_INFO.json');info.update(version='0.2.0.27',baseline_version='0.2.0.26',geography_version='0.2.0.27',display_version='0.2.0.27',scenario_id=w['scenario_id'],population=report['population_after'],changes=['Year-2000 population grid registered to current provinces, census and small-country benchmarks','Complete per-state age, education and religion estimates with provenance','Separate labour-force participation and unemployment figures; three demographic charts'],validation={'pending':True});write('BUILD_INFO.json',info)
 restore=read('ASSET_RESTORE.json');restore['version']='0.2.0.27';write('ASSET_RESTORE.json',restore)
 geo=read('data/geography_bundle.json');geo.update(version='0.2.0.27',scenario=w['scenario_id']);write('data/geography_bundle.json',geo)
 print('DEMOGRAPHICS_0227_DATA_READY',len(states),'states',report['population_after'],'residents',flush=True)
if __name__=='__main__':main()
