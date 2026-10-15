"""Independent coordinate probes plus complete runtime geography consistency."""
from pathlib import Path
from collections import Counter, defaultdict
import json, sys
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography'
Image.MAX_IMAGE_PIXELS=None
w=json.load(open(ROOT/'data/world.json'));ps=json.load(open(ROOT/'data/provinces.json'))
old=json.load(open(ROOT/'.geography_0208_baseline/data/world.json'))
a=np.load(SRC/'grouped_atlas_022r2.npz')['regions'];p=np.load(SRC/'province_atlas_0208.npz')['provinces'];H,W=a.shape
checks=0;failures=[]
def check(ok,message):
 global checks
 checks+=1
 if not ok:failures.append(message);print('FAIL',message,flush=True)
def state(lon,lat):
 return w['regions'].get(str(int(a[min(H-1,int((90-lat)/180*H)),int((lon+180)/360*W)%W])),{})
def probe(label,lon,lat,owner,name):
 s=state(lon,lat);check(s.get('owner')==owner and s.get('name')==name,label+': '+str((s.get('owner'),s.get('name'))))
probes=[
 ('Tokyo',139.70,35.68,'JAP','Kanto'),('Yokohama',139.64,35.44,'JAP','Kanto'),
 ('Hiroshima',132.46,34.39,'JAP','Chugoku'),('Yamaguchi',131.47,34.18,'JAP','Chugoku'),
 ('Kyoto',135.77,35.01,'JAP','Kansai'),('Nagoya',136.91,35.18,'JAP','Tokai'),
 ('Aarhus',10.20,56.16,'DEN','Central Denmark'),('Aalborg hinterland',9.85,57.10,'DEN','North Denmark'),
 ('Bornholm',14.72,55.10,'DEN','Bornholm'),
 ('Rhode Island',-71.41,41.82,'USA','Rhode Island'),('Connecticut',-72.68,41.76,'USA','Connecticut'),
 ('Massachusetts',-71.06,42.36,'USA','Massachusetts'),('Maryland',-76.61,39.29,'USA','Maryland'),
 ('Delaware',-75.56,39.16,'USA','Delaware'),('Washington DC',-77.04,38.90,'USA','Washington, D.C.'),
 ('Sydney',151.21,-33.87,'AST','New South Wales'),('Brisbane',153.03,-27.47,'AST','Queensland'),
 ('Melbourne',144.96,-37.81,'AST','Victoria'),('Adelaide',138.60,-34.93,'AST','South Australia'),
 ('Perth',115.86,-31.95,'AST','Western Australia'),('Canberra',149.13,-35.28,'AST','Australian Capital Territory'),
 ('Darwin',130.84,-12.46,'AST','Northern Territory'),('Hobart',147.33,-42.88,'AST','Tasmania'),
 ('Izmir',27.14,38.42,'TUR','Izmir'),('Edirne',26.55,41.67,'TUR','Thrace'),
 ('Asian Canakkale',26.45,40.10,'TUR','Balikesir'),
 ('Greater London',-.12,51.51,'ENG','Greater London'),('Dover',1.31,51.13,'ENG','Southeast England'),
 ('Cardiff',-3.18,51.48,'ENG','Wales'),('Hereford',-2.72,52.06,'ENG','West Midlands'),
 ('Scilly',-6.30,49.93,'ENG','Cornwall'),
 ('La Rioja',-2.45,42.46,'SPR','La Rioja'),('Bilbao',-2.93,43.26,'SPR','Basque Country'),
 ('Burgos',-3.70,42.34,'SPR','Castile and León'),
 ('Cluj',23.59,46.77,'ROM','Northern Transylvania'),('Bacau',26.91,46.57,'ROM','Moldavia'),
 ('Constanta',28.63,44.18,'ROM','Dobruja'),
 ('Dobrich',27.83,43.57,'BUL','South Dobruja'),('Burgas',27.46,42.50,'BUL','Southern Bulgaria'),
 ('Varna',27.91,43.21,'BUL','Varna'),
 ('Cairo',31.24,30.05,'EGY','Cairo'),('Northern Sinai',33.75,30.90,'EGY','Sinai'),
 ('Southern Sinai',34.10,28.70,'EGY','Sinai'),
 ('West Eritrea',37.50,15.20,'ERI','Western Eritrea'),('East Eritrea',39.3,15.50,'ERI','Eastern Eritrea'),
 ('West Gabon',10.0,0.0,'GAB','Western Gabon'),('East Gabon',13.0,0.0,'GAB','Eastern Gabon'),
 ('Hargeisa',44.06,9.56,'SML','Somaliland'),('Tskhinvali',43.97,42.23,'SOO','South Ossetia'),
 ('Dili',125.58,-8.56,'IND','Timor-Leste'),('Oecusse interior',124.30,-9.30,'IND','Timor-Leste'),
 ('Gangneung',128.88,37.75,'KOR','Gangwon'),('Seoul',126.98,37.57,'KOR','Gyeonggi'),
 ('Busan',129.07,35.18,'KOR','South Gyeongsang'),
 ('Taipei',121.56,25.04,'TAI','Northern Taiwan'),('Kaohsiung',120.30,22.63,'TAI','Southern Taiwan'),
 ('Havana',-82.37,23.11,'CUB','Western Cuba'),('Camaguey',-77.92,21.38,'CUB','Central Cuba'),
 ('Santiago',-75.83,20.02,'CUB','Eastern Cuba'),
 ('Banja Luka',17.19,44.77,'BOS','Republika Srpska'),('Brcko',18.76,44.87,'BOS','Brčko District')]
for row in probes:probe(*row)
check(w['version']=='0.2.0.8' and w['scenario_id'].endswith('0_2_0_8'),'fresh scenario identity')
us_states=set('Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming'.split('|'))
check(us_states.issubset({s['name'] for s in w['regions'].values() if s['owner']=='USA'}),'all 50 US states separately named')
check(sum(s['owner']=='FRA' and -6<s['map_center'][0]*360-180<11 and 41<90-s['map_center'][1]*180<52 for s in w['regions'].values())==22,'France has 22 European states matching MD European allocation')
check(set(w['countries'])==set(old['countries']),'all starting countries retained')
check(sum(s['population'] for s in w['regions'].values())==sum(s['population'] for s in old['regions'].values()),'world population conserved')
before=Counter();after=Counter();bb=Counter();ab=Counter()
for s in old['regions'].values():before[s['owner']]+=s['population'];bb.update(s['buildings'])
for s in w['regions'].values():after[s['owner']]+=s['population'];ab.update(s['buildings'])
check(bb==ab,'world state buildings conserved')
check(all(before[t]==after[t] for t in before if t not in ['GEO','SOO','PUN','SML']),'country totals retained outside explicit controller corrections')
for tags in [('GEO','SOO'),('PUN','SML')]:check(sum(before[t] for t in tags)==sum(after[t] for t in tags),'controller-correction population conserved '+str(tags))
parent=np.zeros(65536,np.uint16)
for k,q in ps.items():parent[int(k)]=q['region']
bad=0;uncovered=0
for top in range(0,H,128):
 q=a[top:top+128];r=p[top:top+128];land=(q>0)&(q<8191)
 bad+=int(np.count_nonzero(land&(parent[r]!=q)));uncovered+=int(np.count_nonzero(land&(r==0)))
check(bad==0 and uncovered==0,'every land pixel has a province in its state')
check(set(map(int,np.unique(a)))-{0,8191}==set(map(int,w['regions'])),'state IDs exactly match footprints')
check(set(map(int,np.unique(p)))-{0}==set(map(int,ps)),'province IDs exactly match footprints')
check(max(map(int,ps))<65535 and max(map(int,w['regions']))<8191,'renderer ID capacity')
urban=json.load(open(ROOT/'data/urban_population.json'))
for k,s in w['regions'].items():
 check(bool(s['provinces']) and bool(s['name'].strip()),'populated named state '+k)
 u,v=s['map_center'];check(int(a[int(v*H),int(u*W)])==int(k),'state focus '+k)
 check(all(ps[str(pid)]['region']==int(k) for pid in s['provinces']),'state province list '+k)
 check(sum(ps[str(pid)]['population_2000'] for pid in s['provinces'])==s['population'],'province population '+k)
 check(urban['states'][k]['population_2000']==s['population'],'urban state account '+k)
for tag,c in w['countries'].items():
 check(set(c['regions'])=={int(k) for k,s in w['regions'].items() if s['owner']==tag},'country state list '+tag)
 check(w['regions'][str(c['capital'])]['owner']==tag,'capital owner '+tag)
for k,q in ps.items():
 u,v=q['map_center'];check(int(p[int(v*H),int(u*W)])==int(k),'province focus '+k)
 check(all(int(k) in ps[str(n)]['neighbors'] for n in q['neighbors']),'symmetric neighbors '+k)
for c in json.load(open(ROOT/'data/cities.json')):
 pid=c['province_id'];check(str(pid) in ps and w['regions'][str(ps[str(pid)]['region'])]['owner']==c['country'],'city link '+c['name'])
for kind,items in json.load(open(ROOT/'data/urban_scenery.json')).items():
 if kind not in ['clusters','landmarks']:continue
 for q in items:check(str(q['province']) in ps and q['group'] in urban['groups'],'scenery link '+q.get('name',''))
for i in range(4):
 rgb=np.asarray(Image.open(ROOT/'assets'/f'region_ids_{i}.png'),np.uint16);encoded=rgb[:,:,0]+rgb[:,:,1]*256
 y,x=i//2*4096,i%2*8192;q=p[y:y+4096,x:x+8192].copy();q[a[y:y+4096,x:x+8192]==8191]=65535
 check(np.array_equal(encoded,q),'runtime province tile '+str(i))
rgb=np.asarray(Image.open(ROOT/'assets/province_index.png'),np.uint16).reshape(-1,3)
check(all(int(rgb[int(k),0])+int(rgb[int(k),1])*256==q['region'] for k,q in ps.items()),'runtime province-to-state lookup')
for tag in ['BHU','BLZ','ELS','COM','SML','SOO']:check(len(w['countries'][tag]['regions'])==1,'explicit one-state rule '+tag)
for tag,n in [('TAI',6),('NRY',8),('LBA',15),('PAP',7),('ERI',2),('GAB',2)]:check(len(w['countries'][tag]['regions'])==n,'authored state allocation '+tag)
for tag,name in [('FRA','Mayotte'),('FRA','New Caledonia'),('FRA','French Guiana'),('USA','United States Virgin Islands'),('HOL','Aruba, Curaçao and Bonaire')]:
 check(sum(s['owner']==tag and s['name']==name for s in w['regions'].values())==1,'single territory state '+name)
check(not any('Scilly' in s['name'] for s in w['regions'].values()),'Scilly integrated into Cornwall')
check(not any("People's Republic" in s['name'] for s in w['regions'].values() if s['owner']=='UKR'),'neutral 2000 Ukrainian state names')
report=json.load(open(ROOT/'data/geography_0208_report.json'))
for q in report['karelia_transfers']:check(ps[str(q['province_id'])]['region']==1043,'requested Karelia province '+str(q['old_local_index']))
check(len(ps)<13221*1.04,'land province count within four percent of MD')
boxes=find_objects(a,max_label=8191);disconnected=[]
for k,s in w['regions'].items():
 bb=boxes[int(k)-1];land,_=label(a[bb]==int(k),np.ones((3,3),bool));view=p[bb]
 for pid in s['provinces']:
  parts,n=label(view==pid,np.ones((3,3),bool))
  if n<2:continue
  sizes=np.bincount(parts.ravel());pb=find_objects(parts);seen=set()
  for j in range(1,n+1):
   if sizes[j]<8:continue
   yy,xx=np.nonzero(parts[pb[j-1]]==j);component=int(land[yy[0]+pb[j-1][0].start,xx[0]+pb[j-1][1].start])
   if component in seen:disconnected.append(pid)
   seen.add(component)
check(not disconnected,'no substantial disconnected province pieces on the same landmass: '+str(sorted(set(disconnected))))
out={'checks':checks,'failures':failures,'states':len(w['regions']),'provinces':len(ps),'independent_coordinate_probes':len(probes)}
(ROOT/'validation_0208').mkdir(exist_ok=True);(ROOT/'validation_0208/geography_results.json').write_text(json.dumps(out,indent=2))
print('GEOGRAPHY_0208_TESTS',json.dumps(out),flush=True)
sys.exit(bool(failures))
