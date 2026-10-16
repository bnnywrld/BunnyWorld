"""Rebuild the approved State/capital/scenery changes from saved 0.2.0.13."""
from pathlib import Path
from collections import defaultdict,Counter
import json,copy,zipfile,math
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];B=R.parent/'baseline_0213/data';S=R.parent/'sources_0214';Image.MAX_IMAGE_PIXELS=None
read=lambda n:json.loads((B/n).read_text())
def write(n,v):(R/'data'/n).write_text(json.dumps(v,ensure_ascii=False,separators=(',',':')))
LEVELS={'infrastructure','internet_station','air_base','radar_station','rail_terminal','anti_air_building','stronghold_network'}
w=read('world.json');ps=read('provinces.json');cities=read('cities.json');scene=read('urban_scenery.json');urban=read('urban_population.json');before=Counter()
for r in w['regions'].values():before[r['owner']]+=r['population']
remap={738:732,1753:1568,926:894,928:894,1814:1813,685:687}
for old,new in remap.items():
 a=w['regions'][str(new)];b=w['regions'].pop(str(old));assert a['owner']==b['owner'];a['population']+=b['population'];a['provinces']+=b['provinces']
 for k,n in b.get('buildings',{}).items():a.setdefault('buildings',{})[k]=a.get('buildings',{}).get(k,0)+n
 for key in ['cores','claims']:a[key]=sorted(set(a.get(key,[])+b.get(key,[])))
 for pid in b['provinces']:ps[str(pid)]['region']=new
 for c in w['countries'].values():
  if c.get('capital')==old:c['capital']=new
w['regions']['1813']['name']='North Sumatra';w['regions']['687']['name']='Chișinău–Bălți'
a=w['regions']['363'];mainland=[p for p in a['provinces']if p!=3865];new=copy.deepcopy(a);new.update(id=1826,name='Southwest Finland',provinces=mainland);weights=[ps[str(p)].get('population_2000',0)for p in a['provinces']];total=sum(weights);share=ps['3865'].get('population_2000',0)/total if total else ps['3865']['area_km2']/a['area_km2'];keep=int(round(a['population']*share));new['population']=a['population']-keep;a['population']=keep;a['provinces']=[3865];a['name']='Åland';w['regions']['1826']=new
for pid in mainland:ps[str(pid)]['region']=1826
for r in w['regions'].values():
 r['area_km2']=round(sum(ps[str(p)]['area_km2']for p in r['provinces']),3);r['map_center']=ps[str(max(r['provinces'],key=lambda p:ps[str(p)]['area_km2']))]['map_center'];r['neighbors']=[]
 for i,pid in enumerate(r['provinces'],1):
  p=ps[str(pid)];p['local_index']=6 if pid==3865 else i;p['name']=r['name']+' · Province '+str(p['local_index'])
 for k in r.get('buildings',{}):
  if k in LEVELS:r['buildings'][k]=min(10,int(r['buildings'][k]))
 r['building_slot_baseline']=max(sum(n for k,n in r.get('buildings',{}).items()if k not in LEVELS),4+int(4*math.sqrt(r['population']/100000)))
for p in ps.values():
 for n in p.get('neighbors',[]):
  s=ps[str(n)]['region']
  if s!=p['region']and s not in w['regions'][str(p['region'])]['neighbors']:w['regions'][str(p['region'])]['neighbors'].append(s)
 for key in ['population','population_2000','population_scope','urban_group']:p.pop(key,None)
atlas=np.load(R/'tools/cartography/province_atlas_0210.npz')['provinces'];H,W=atlas.shape
lookup=np.zeros(65536,np.uint16)
for p in ps.values():lookup[p['id']]=p['region']
def pid_at(lon,lat):return int(atlas[min(H-1,max(0,int((90-lat)/180*H))),int((lon+180)/360*W)%W])
def state_at(lon,lat):return int(lookup[pid_at(lon,lat)])
by=defaultdict(list)
for c in cities:
 sid=state_at(c['longitude'],c['latitude'])
 for k in ['population_2000','population_scope']:c.pop(k,None)
 if sid:by[sid].append(c)
for zip_path in [S/'cities500.zip']+sorted((S/'countries').glob('*.zip')):
 with zipfile.ZipFile(zip_path)as z:
  for raw in z.open(next(n for n in z.namelist()if n.endswith('.txt')and 'readme'not in n.lower())):
   f=raw.decode('utf-8').rstrip().split('\t')
   if len(f)<19 or f[6]!="P":continue
   lon,lat=float(f[5]),float(f[4]);sid=state_at(lon,lat)
   if not sid:continue
   c={'name':f[1],'longitude':lon,'latitude':lat,'population_rank':int(f[14]),'capital':False,'country':w['regions'][str(sid)]['owner'],'province_id':pid_at(lon,lat),'source':'GeoNames cities500, 2026-10-16; settlement rank only'};by[sid].append(c)
added=0
for key,r in w['regions'].items():
 candidates=by[int(key)]
 if candidates:
  c=max(candidates,key=lambda c:c.get('population_rank',0));pid=pid_at(c['longitude'],c['latitude']);uv=[(c['longitude']+180)/360,(90-c['latitude'])/180];source=c.get('source','Existing mapped settlement; relative population rank')
  if not any(x['name']==c['name']and state_at(x['longitude'],x['latitude'])==int(key)for x in cities):cities.append(c);added+=1
  for marker in cities:
   if marker['name']==c['name']and state_at(marker['longitude'],marker['latitude'])==int(key):marker['state_capital']=True;marker['state_id']=int(key)
  name=c['name']
 else:pid=max(r['provinces'],key=lambda p:ps[str(p)]['area_km2']);uv=ps[str(pid)]['map_center'];source='Administrative anchor: no mapped settlement in this small/remote territory';name=r['name']+' Centre'
 r.update(state_capital=name,capital_province=pid,capital_uv=uv,capital_source=source,capital_is_settlement=bool(candidates))
for c in scene['clusters']:
 c['state']=ps[str(c['province'])]['region'];c.pop('population_2000',None)
 # Retain centre and nearest lots, then compact their offsets.
 c['instances'].sort(key=lambda p:((p[0]-c['longitude'])*math.cos(math.radians(c['latitude'])))**2+(p[1]-c['latitude'])**2)
 for p in c['instances']:p[0]=round(c['longitude']+(p[0]-c['longitude'])*.88,7);p[1]=round(c['latitude']+(p[1]-c['latitude'])*.88,7)
by_clusters=defaultdict(list)
for c in scene['clusters']:by_clusters[c['state']].append(c)
next_id=max(c['id']for c in scene['clusters'])+1;new_clusters=0
for sid,r in w['regions'].items():
 if not r['capital_is_settlement']:continue
 lon=r['capital_uv'][0]*360-180;lat=90-r['capital_uv'][1]*180
 near=[c for c in by_clusters[int(sid)]if((c['longitude']-lon)*math.cos(math.radians(lat)))**2+(c['latitude']-lat)**2<.12**2]
 if not near:
  instances=[]
  for x,y in [(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1)]:
   a=lon+x*.009/max(.1,math.cos(math.radians(lat)));b=lat+y*.009
   if state_at(a,b)==int(sid):instances.append([a,b,20.,24.+len(instances)*4.,0.,0])
  c={'id':next_id,'state':int(sid),'province':r['capital_province'],'group':'state_capital_'+sid,'name':r['state_capital'],'longitude':lon,'latitude':lat,'category':'State capital','instances':instances};next_id+=1;scene['clusters'].append(c);by_clusters[int(sid)].append(c);near=[c];new_clusters+=1
 cap=min(near,key=lambda c:(c['longitude']-lon)**2+(c['latitude']-lat)**2);cap['state_capital_priority']=True
for sid,clusters in by_clusters.items():
 weights=[max(1,len(c['instances']))*(1.2 if c.get('state_capital_priority')else 1.)for c in clusters]
 for c,weight in zip(clusters,weights):c['state_visual_weight']=weight/sum(weights)
original=sum(len(c['instances'])for c in read('urban_scenery.json')['clusters']);target=round(original*.75);counts=np.array([len(c['instances'])for c in scene['clusters']]);exact=counts/counts.sum()*target;quota=np.floor(exact).astype(int)
for i in np.argsort(-(exact-quota))[:target-int(quota.sum())]:quota[i]+=1
for c,n in zip(scene['clusters'],quota):c['instances']=c['instances'][:int(n)]
for g in urban.get('groups',{}).values():
 for k in ['population_2000','settlement_population_2000','representative_buildings']:g.pop(k,None)
urban['states']={k:{'population_2000':r['population']}for k,r in w['regions'].items()};urban['source']={'method':'State-only population. City ranks/visual weights are not local demographic counts.'}
w['scenario_id']='bunny_world_2000_0_2_0_14';after=Counter()
for r in w['regions'].values():after[r['owner']]+=r['population']
assert before==after
for tag,c in w["countries"].items():c["regions"]=sorted(r["id"]for r in w["regions"].values()if r["owner"]==tag)
for n,v in [('world.json',w),('provinces.json',ps),('cities.json',cities),('urban_scenery.json',scene),('urban_population.json',urban)]:write(n,v)
idx=np.zeros((256,256,3),np.uint8)
for p in ps.values():pid=p['id'];sid=p['region'];idx[pid//256,pid%256]=[sid&255,sid>>8,p['local_index']]
Image.fromarray(idx).save(R/'assets/province_index.png')
report={'version':'0.2.0.14','reconstructed_from':'0.2.0.13','states':len(w['regions']),'provinces':len(ps),'merges':remap,'aland_kept_original_province':3865,'mainland_state':1826,'settlement_capitals':sum(r['capital_is_settlement']for r in w['regions'].values()),'administrative_anchors':sum(not r['capital_is_settlement']for r in w['regions'].values()),'added_city_markers':added,'added_capital_clusters':new_clusters,'scenery_before':original,'scenery_after':target,'compaction':.88,'country_populations_conserved':True,'dynamic_city_growth':False};write('geography_0214_report.json',report);print(report)
