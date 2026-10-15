"""Reproducible 0.2.0 national demographic estimates and bounded MD finances.
Offline when tools/sources_020 already contains the downloaded references.
"""
import json,re,sys,hashlib,unicodedata,csv
from pathlib import Path
from zipfile import ZipFile
from collections import defaultdict,Counter
from import_md import parse,Block,at_start
ROOT=Path(__file__).resolve().parents[1]; SOURCES=ROOT/'tools/sources_020'
world=json.loads((ROOT/'data/world.json').read_text())
def norm(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
wb=json.loads((SOURCES/'countries.json').read_text())[1]
wb_by_name={norm(c['name']):c['id'] for c in wb}; wb_by_iso={c['id']:c for c in wb}
ALIASES={'ALG':'DZA','AST':'AUS','AUS':'AUT','BAN':'BGD','BOS':'BIH','BRM':'MMR','BRU':'BRN','BUL':'BGR','CAM':'CMR','CBD':'KHM','CDI':'CIV','CHA':'TCD','CNG':'COG','COS':'CRI','CRO':'HRV','DEN':'DNK','DRC':'COD','EGU':'GNQ','ELS':'SLV','ENG':'GBR','FAO':'FRO','FIJ':'FJI','FYR':'MKD','GAH':'GHA','GAM':'GMB','GER':'DEU','GRA':'GRD','GRE':'GRC','GUA':'GTM','GUB':'GNB','GUI':'GIN','HAI':'HTI','HOL':'NLD','ICE':'ISL','IND':'IDN','IRE':'IRL','JAP':'JPN','KOR':'KOR','KUW':'KWT','LAT':'LVA','LBA':'LBY','LEB':'LBN','LIT':'LTU','MAC':'MAC','MAD':'MDG','MAY':'MYS','MIC':'FSM','MLD':'MDV','MLV':'MDA','MLW':'MWI','MRT':'MUS','NEP':'NPL','NIG':'NGA','NKO':'PRK','NRY':'NOR','OMA':'OMN','PAP':'PNG','PER':'IRN','PHI':'PHL','POR':'PRT','PRU':'PER','RAJ':'IND','ROM':'ROU','SAF':'ZAF','SAO':'STP','SER':'SRB','SIA':'THA','SIN':'SGP','SLO':'SVK','SLV':'SVN','SOV':'RUS','SPR':'ESP','SRI':'LKA','STK':'KNA','STL':'LCA','STV':'VCT','SWA':'SWZ','SWI':'CHE','TNZ':'TZA','TRK':'TKM','URG':'URY','VER':'CPV','VIE':'VNM','KOS':'XKX','GRN':'GRL','TAI':'TWN','HLS':None}
PARENT={'ABK':'GEO','ACE':'IDN','AFR':'SLE','AIA':'SOM','CHE':'RUS','HAM':'PSE','HEZ':'LBN','IEK':'IRQ','JUB':'SOM','KAC':'MMR','KAR':'MMR','KUR':'IRQ','LUR':'LBR','MLC':'COD','NCY':'CYP','NKR':'ARM','NPM':'NPL','PAL':'PSE','PMR':'MDA','PUK':'IRQ','PUN':'SOM','RCD':'COD','SHA':None,'SHN':'MMR','SML':'SOM','SNA':'SOM','SOO':'GEO','SSU':'SDN','SWS':'SOM','TAL':'AFG','TML':'LKA','UNI':'AGO','WAA':'MMR'}
def iso_for(tag,c):
 if tag in ALIASES:return ALIASES[tag],False
 if tag in PARENT:return PARENT[tag],True
 return wb_by_name.get(norm(c['name']),tag if tag in wb_by_iso else None),False
series={}
for p in SOURCES.glob('*.json'):
 if p.name in ['sample_wdi.json','countries.json']:continue
 try:
  raw=json.loads(p.read_text())
  if 'data' in raw:series[p.stem]={}
  else:continue
  for row in raw['data'][1]:
   if row['value'] is not None:series[p.stem].setdefault(row['countryiso3code'],{})[int(row['date'])]=float(row['value'])
 except Exception:continue
def val(code,iso,nearest=False):
 values=series.get(code,{}).get(iso,{})
 if 2000 in values:return values[2000],2000
 if nearest and values:
  year=min(values,key=lambda x:(abs(x-2000),x));return values[year],year
 return None,None
def block_metric(shares,source,year=2000,status='national estimate',raw=''):
 total=sum(shares.values())
 if total<=0:shares={'Unknown':1.0}
 elif total>1.005:shares={k:v/total for k,v in shares.items()}
 elif total<.99999:shares['Other / unspecified']=shares.get('Other / unspecified',0)+1-total
 return {'shares':shares,'source':source,'year':year,'status':status,'reference':raw}
text=(SOURCES/'factbook_2000.txt').read_text()
fb={name:part for name,part in re.findall(r'@([^:\n]+):People\n(.*?)(?=\n@)',text,re.S)}
fbnorm={norm(k):k for k in fb}
FB_ALIASES={'BOS':'Bosnia and Herzegovina','BRM':'Burma','CDI':"Cote d'Ivoire",'CNG':'Congo, Republic of the','DRC':'Congo, Democratic Republic of the','FYR':'Macedonia','KOR':'Korea, South','NKO':'Korea, North','TAI':'Taiwan','HLS':'Holy See (Vatican City)','MAC':'Macau','SER':'Serbia and Montenegro','MNT':'Serbia and Montenegro','MLV':'Moldova','SAO':'Sao Tome and Principe','VER':'Cape Verde','SWA':'Swaziland','SOV':'Russia','PER':'Iran','HAM':'Gaza Strip','PAL':'West Bank'}
religion_labels=[('Shinto / Buddhist',['shinto and buddhist']),('Catholic',['roman catholic','catholic']),('Orthodox',['orthodox']),('Protestant',['protestant','anglican','presbyterian','methodist','lutheran']),('Christian (unspecified)',['christian']),('Sunni',['sunni']),('Shia',['shia','shi\'a','shiite']),('Muslim (unspecified)',['muslim','islam']),('Hindu',['hindu']),('Buddhist',['buddhist']),('Jewish',['jewish','judaism']),('Shinto',['shinto']),('Sikh',['sikh']),('Nonreligious',['none','nonreligious','atheist','unaffiliated']),('Traditional / folk',['animist','indigenous','traditional','tribal']),('Other / unspecified',['other'])]
def rel_label(s):
 s=s.lower()
 for label,keys in religion_labels:
  if any(k in s for k in keys):return label
 return 'Other / unspecified'
def religion(tag,c,iso,proxy):
 name=FB_ALIASES.get(tag,c['name'])
 if proxy and iso in wb_by_iso:name=wb_by_iso[iso]['name']
 name=fbnorm.get(norm(name),name)
 part=fb.get(name,'')
 m=re.search(r'Religions:\s*(.*?)(?=\n\n)',part,re.S)
 if not m:return block_metric({'Unknown':1},'CIA World Factbook 2000; no numeric coverage',status='unavailable')
 raw=' '.join(m[1].split()); yr=re.findall(r'\b(19\d\d|2000)\b',raw);year=int(yr[-1]) if yr else 2000
 # Remove parenthetical subcategories so nested percentages are not counted twice.
 clean=re.sub(r'\([^()]*\)','',raw)
 shares=defaultdict(float)
 for segment in re.split(r'[,;]',clean):
  match=re.search(r'(.+?)\s+(\d+(?:\.\d+)?)\s*%',segment)
  if match and not re.search(r'\d\s*[-–]\s*\d',segment):shares[rel_label(match[1])]+=float(match[2])/100
 # Count-based entries can be used against the source's own population, not game totals.
 if not shares:
  pop=re.search(r'Population:\s*([\d,]+)',part)
  if pop:
   denom=float(pop[1].replace(',',''))
   for seg in re.split(r'[,;]',re.sub(r'(?<=\d),(?=\d{3})','',clean)):
    match=re.search(r'(.+?)\s+(\d[\d,]*(?:\.\d+)?)\s*(million)?',seg)
    if match:shares[rel_label(match[1])]+=float(match[2].replace(',',''))*(1e6 if match[3] else 1)/denom
 if sum(shares.values())>1.05:return block_metric({'Unknown':1},'CIA World Factbook 2000; overlapping affiliations',year,'unavailable',raw)
 if not shares:return block_metric({'Unknown':1},'CIA World Factbook 2000; no numeric shares',year,'unavailable',raw)
 return block_metric(dict(shares),f'CIA World Factbook 2000: {name}',year,'parent-country proxy' if proxy else 'historical estimate; partial categories possible',raw)
barro={row['WBcode']:row for row in csv.DictReader((SOURCES/'barro_lee_25plus.csv').open()) if row['year']=='2000'}
profiles={};coverage=Counter()
for tag,c in world['countries'].items():
 iso,proxy=iso_for(tag,c); country=wb_by_iso.get(iso,{})
 region=country.get('region',{}).get('id','');regioniso={'EAS':'EAS','ECS':'ECS','LCN':'LCN','MEA':'MEA','NAC':'NAC','SAS':'SAS','SSF':'SSF'}.get(region,'WLD')
 p={'iso3':iso,'source_country':country.get('name',c['name']),'proxy':proxy,'retirement_age':65,'retirement_note':'65-year scenario baseline; country-specific retirement laws follow in 0.2.2','metrics':{}}
 ages=[];f,_=val('SP.POP.TOTL.FE.ZS',iso);f=.5 if f is None else f/100
 for age in [f'{a:02}{a+4:02}' for a in range(0,80,5)]+['80UP']:
  female,_=val(f'SP.POP.{age}.FE.5Y',iso);male,_=val(f'SP.POP.{age}.MA.5Y',iso)
  ages.append(None if female is None or male is None else (female*f+male*(1-f))/100)
 if any(a is None for a in ages):
  name=FB_ALIASES.get(tag,c['name']);part=fb.get(fbnorm.get(norm(name),name),'')
  bands=[re.search(pattern,part) for pattern in [r'0-14 years:\s*([\d.]+)%',r'15-64 years:\s*([\d.]+)%',r'65 years and over:\s*([\d.]+)%']]
  if all(bands):
   young,middle,old=[float(m[1])/100 for m in bands]
   ages=[young/3]*3+[middle/10]*10+[old/4]*4
   p['age_fallback']='CIA World Factbook 2000; uniform within broad source age bands'
 if all(a is not None for a in ages):
  tot=sum(ages);ages=[x/tot for x in ages]; single=[]
  for x in ages[:16]:single.extend([x/5]*5)
  single.extend([ages[16]/21]*21)
  p['age_single_year']=single;p['metrics']['age']=block_metric({'Underage':sum(single[:18]),'Working age':sum(single[18:65]),'Retired':sum(single[65:])},'World Bank WDI / UN population estimates',status='parent-country proxy' if proxy else '2000 estimate; uniform within 5-year cohorts')
  p['adult25_share']=sum(single[25:])
  if 'age_fallback' in p:p['metrics']['age']['source']=p['age_fallback'];p['metrics']['age']['status']='modeled age-band interpolation'
 else:
  p['age_single_year']=[];p['adult25_share']=None;p['metrics']['age']=block_metric({'Unknown':1},'World Bank WDI; no year-2000 coverage',status='unavailable')
 p['metrics']['religion']=religion(tag,c,iso,proxy)
 edu=[];ys=[];edu_iso=iso;edu_status='national estimate'
 for code in ['SE.PRM.CUAT.ZS','SE.SEC.CUAT.UP.ZS','SE.TER.CUAT.ST.ZS']:
  x,y=val(code,iso,True);edu.append(x);ys.append(y)
 if any(x is None for x in edu):
  edu=[];ys=[];edu_iso=regioniso;edu_status='regional proxy estimate'
  for code in ['SE.PRM.CUAT.ZS','SE.SEC.CUAT.UP.ZS','SE.TER.CUAT.ST.ZS']:
   x,y=val(code,regioniso,True);edu.append(x);ys.append(y)
 if all(x is not None for x in edu) and edu[0]>=edu[1]>=edu[2]:
  a,b,d=[x/100 for x in edu];p['metrics']['education']=block_metric({'Below primary':1-a,'Primary':a-b,'Secondary':b-d,'Tertiary':d},'World Bank WDI / UNESCO UIS: '+str(edu_iso),','.join(map(str,ys)),edu_status+'; attainment age 25+')
 else:p['metrics']['education']=block_metric({'Unknown':1},'World Bank WDI / UNESCO UIS; incomplete attainment data',status='unavailable')
 if p['metrics']['education']['status']=='unavailable' and iso in barro:
  row=barro[iso];u,primary,pc,secondary,sc,higher,hc=[float(row[k])/100 for k in ['lu','lp','lpc','ls','lsc','lh','lhc']]
  shares={'Below primary':u+max(0,primary-pc),'Primary':pc+max(0,secondary-sc),'Secondary':sc+max(0,higher-hc),'Tertiary':hc}
  p['metrics']['education']=block_metric(shares,'Barro-Lee Educational Attainment v2.2 / 2000: '+str(iso),2000,('parent-country proxy; ' if proxy else '')+'modeled attainment age 25+', 'Highest completed level; incomplete next-level schooling assigned to preceding completed level.')
 participation,year=val('SL.TLF.CACT.ZS',iso);unemployed,_=val('SL.UEM.TOTL.ZS',iso)
 if participation is not None and unemployed is not None:
  a,b=participation/100,unemployed/100
  p['metrics']['activity']=block_metric({'Employed':a*(1-b),'Unemployed':a*b,'Outside labor force':1-a},'World Bank WDI / ILO modeled estimates',2000,'model for working-age group using 15+ participation; '+('parent-country proxy' if proxy else 'national rates'))
 else:p['metrics']['activity']=block_metric({'Unknown':1},'World Bank WDI / ILO; no year-2000 coverage',status='unavailable')
 for key,v in p['metrics'].items():coverage[key+('_available' if v['status']!='unavailable' else '_unknown')]+=1
 profiles[tag]=p
# Bound financial history: only unconditional supported country-history assignments.
archive=Path(sys.argv[1]);z=ZipFile(archive);financial={};diag=[]
for name in z.namelist():
 m=re.search(r'(?:^|/)history/countries/([A-Z0-9]{3})\b',name)
 if not m or m[1] not in world['countries']:continue
 try:history=Block(at_start(parse(z.read(name).decode('utf-8-sig',errors='replace'))))
 except Exception as e:diag.append({'file':name,'error':str(e)});continue
 vals={}
 def walk(block):
  for key,op,value in block.items:
   if key in ['effect'] and isinstance(value,Block):walk(value)
   if key=='set_variable' and isinstance(value,Block):
    if value.get('var') is not None:k=value.get('var');v=value.get('value')
    else:
     entries=[(k,v) for k,o,v in value.items if k and not isinstance(v,Block)]
     if len(entries)!=1:continue
     k,v=entries[0]
    if k in ['treasury','debt','gdp_per_capita']:
     try:vals[k]=float(v)
     except (ValueError,TypeError):pass
 walk(history)
 financial[m[1]]={'source_file':name,'variables':vals}
 c=world['countries'][m[1]]
 for k in ['treasury','debt']:
  if k in vals:c['starting_stats'][k+'_usd']=vals[k]*1e9
 if 'gdp_per_capita' in vals:c['starting_stats']['gdp_per_capita_usd']=vals['gdp_per_capita']*1000
for sid,r in world['regions'].items():r['demographic_profile']=r['owner']
world['scenario_id']='bunny_world_2000_0_2_0';world['version']='0.2.0'
world['finance_source']={'filename':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'treasury_debt_unit':'billion USD','gdp_per_capita_unit':'thousand USD','method':'supported unconditional declarations through 2000-01-01; scripted startup effects not executed'}
(ROOT/'data/world.json').write_text(json.dumps(world,ensure_ascii=False,separators=(',',':')))
data={'version':1,'year':2000,'profiles':profiles,'coverage':dict(coverage),'age_method':'uniform distribution within five-year source cohorts; age 80+ spread over 80–100; three visible age groups','local_method':'national profiles assigned to original State owners; local shares are proxies, not local census estimates','education_denominator':'population aged 25+','activity_denominator':'working-age population; projected from 15+ participation rates','sources':['https://api.worldbank.org/v2/','https://www.gutenberg.org/ebooks/3672','https://barrolee.github.io/BarroLeeDataSet/Data.html'],'retirement_baseline':65}
(ROOT/'data/demographics.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
report={'coverage':dict(coverage),'financial_countries':len(financial),'treasury_available':sum('treasury' in x['variables'] for x in financial.values()),'debt_available':sum('debt' in x['variables'] for x in financial.values()),'financial_history':financial,'diagnostics':diag,'limitations':['No yearly population evolution in 0.2.0','65 is a gameplay retirement baseline, not a researched law for every country','WDI attainment supplemented with Barro-Lee 2000 estimates; remaining gaps unknown','Factbook shares may be partial or refer to earlier survey years','Local demographic profiles use national or parent-country proxies']}
(ROOT/'data/foundation_020_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps({k:v for k,v in report.items() if k not in ['financial_history','diagnostics']},indent=2))
