"""Bounded State corrections over 0.2.0.14; no general province redesign."""
from pathlib import Path
from collections import Counter,defaultdict
import copy,json,io,math
from rasterio.features import rasterize
from rasterio.transform import Affine
import numpy as np
from scipy.ndimage import distance_transform_edt,find_objects
from PIL import Image
R=Path(__file__).resolve().parents[1];B=R.parent/'baseline_0214';W,H=16384,8192
Image.MAX_IMAGE_PIXELS=None
read=lambda n:json.loads((B/n).read_text())
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,separators=(',',':')))
w=read('data/world.json');ps=read('data/provinces.json');cities=read('data/cities.json');urban=read('data/urban_population.json');scene=read('data/urban_scenery.json')
a=np.load(R/'tools/cartography/province_atlas_0210.npz')['provinces'];old=a.copy();oldps=copy.deepcopy(ps)
report={'version':'0.2.0.15','state_merges':[],'province_dissolutions':[],'names':[],'general_province_redesign':False}
before=Counter()
for s in w['regions'].values():before[s['owner']]+=s['population']
def merge(source,target,name):
 s=w['regions'].pop(str(source));t=w['regions'][str(target)];assert s['owner']==t['owner'];t['population']+=s['population'];t['name']=name
 for k,v in s['buildings'].items():t['buildings'][k]=t['buildings'].get(k,0)+v
 for key in ['cores','claims','geographic_divisions','geographic_codes']:t[key]=sorted(set(t.get(key,[])+s.get(key,[])))
 for p in ps.values():
  if p['region']==source:p['region']=target
 for c in w['countries'].values():
  if c['capital']==source:c['capital']=target
 report['state_merges'].append({'removed':source,'target':target,'name':name})
merge(1485,1484,'Channel Islands');merge(1751,1797,'Southern Syria');merge(1084,1044,'Krasnoyarsk Krai')
# Audit finding: one old gameplay State combined southern Sumatra and western
# Java across the Sunda Strait. Separate the real ADM1 unions using existing
# province footprints; no province boundaries are redrawn.
source=w['regions']['487'];new=copy.deepcopy(source);new.update(id=1827,name='Western Java');new['provinces']=[]
yy,xx=np.nonzero(np.isin(a,source['provinces']));top,left=int(yy.min()),int(xx.min());bottom,right=int(yy.max())+1,int(xx.max())+1
features=json.loads((R/'tools/cartography/geographic_subdivisions.geojson').read_text())['features'];java_codes={f['properties']['adm1_code']for f in features if f['properties'].get('admin')=='Indonesia'and (f['properties'].get('name_en')or f['properties'].get('name'))in {'Banten','Jakarta','West Java'}};java=[f['geometry']for f in features if f['properties'].get('adm1_code')in java_codes]
reference=rasterize([(g,1)for g in java],out_shape=(bottom-top,right-left),transform=Affine(360/W,0,left/W*360-180,0,-180/H,90-top/H*180),dtype='uint8')
for pid in source['provinces']:
 mask=a[top:bottom,left:right]==pid
 if reference[mask].mean()>.5:new['provinces'].append(pid);ps[str(pid)]['region']=1827
assert new['provinces'] and len(new['provinces'])<len(source['provinces'])
ratio=sum(ps[str(pid)]['area_km2']for pid in new['provinces'])/sum(ps[str(pid)]['area_km2']for pid in source['provinces']);new['population']=int(round(source['population']*ratio));source['population']-=new['population']
for k,n in source['buildings'].items():new['buildings'][k]=int(round(n*ratio));source['buildings'][k]-=new['buildings'][k]
source['provinces']=[pid for pid in source['provinces']if pid not in new['provinces']];source['name']='South Sumatra–Lampung'
source.update(geographic_divisions=['Lampung','South Sumatra'],geographic_codes=['IDN-1229','IDN-1230'])
new.update(geographic_divisions=['Banten','Jakarta','West Java'],geographic_codes=sorted(java_codes));w['regions']['1827']=new
new['map_center']=ps[str(max(new['provinces'],key=lambda pid:ps[str(pid)]['area_km2']))]['map_center'];source['map_center']=ps[str(max(source['provinces'],key=lambda pid:ps[str(pid)]['area_km2']))]['map_center']
report['state_splits']=[{'source':487,'created':1827,'names':['South Sumatra–Lampung','Western Java'],'java_provinces':new['provinces'],'basis':'Separate real ADM1 unions on Sumatra and Java; existing province geometry retained.','population_allocation':'Retained total apportioned by existing province area; demographic refinement deferred.'}]
del reference,yy,xx
# Dissolve the actual strip pixels into closest same-controller adjacent
# provinces. This removes the strip topology, including obsolete selection IDs.
b13=json.loads((R.parent/'baseline_0213/data/world.json').read_text())
strip_ids=b13['regions']['738']['provinces']+b13['regions']['1753']['provinces']+read('data/world.json')['regions']['1751']['provinces']
owners=np.zeros(65536,np.uint16)
for key,p in ps.items():owners[int(key)]=w['countries'][w['regions'][str(p['region'])]['owner']]['index']
for pid in strip_ids:
 yy,xx=np.nonzero(a==pid);top=max(0,int(yy.min())-20);bottom=min(H,int(yy.max())+21);left=max(0,int(xx.min())-20);right=min(W,int(xx.max())+21)
 view=a[top:bottom,left:right];valid=(owners[view]==owners[pid])&(~np.isin(view,strip_ids))&(view>0)
 assert valid.any()
 _,indices=distance_transform_edt(~valid,return_indices=True);mask=view==pid;replacement=view[indices[0][mask],indices[1][mask]];view[mask]=replacement
 report['province_dissolutions'].append({'removed':pid,'into':sorted(map(int,np.unique(replacement))),'pixels':len(replacement)})
 ps.pop(str(pid))
renames={255:'Western and Southern Bohemia',256:'Northeastern Bohemia',257:'Moravia–Silesia',258:'Central Bohemia–Vysočina',570:'Jambyl–Turkistan',571:'Akmola–Kostanay–North Kazakhstan',574:'Karaganda–Kyzylorda',4:'Herat',345:'Southern Estonia',346:'Harju–Lääne–Pärnu',347:'Eastern Estonia',670:'San Luis Potosí–Zacatecas',724:'Kebbi–Niger',728:'Sokoto–Zamfara',729:'Kano–Kaduna–Katsina',1124:'Kassala–Al Qadarif',1129:'Khartoum–White Nile',1217:'Central Tunisia',1389:'Al Hudaydah–Al Mahwit–Raymah',361:'Kainuu–Northern Ostrobothnia',1466:'Devon and Cornwall'}
for sid,name in renames.items():
 s=w['regions'][str(sid)];report['names'].append({'id':sid,'country':s['owner'],'before':s['name'],'after':name,'basis':s.get('geographic_divisions',[])});s['name']=name
for key in ['geographic_divisions','geographic_codes']:
 w['regions']['687'][key]=sorted(set(w['regions']['687'].get(key,[])+b13['regions']['685'].get(key,[])))
w['regions']['1466'].update(geographic_divisions=['Cornwall','Devon','Isles of Scilly','Plymouth','Torbay'],geographic_codes=['GBR-2110','GBR-2048','GBR-5988','GBR-2141','GBR-2142'])
# These two records were previously cloned wholesale; retain only relevant
# geographic provenance, so audits don't describe mainland Finland as Åland.
w['regions']['363'].update(geographic_divisions=['Åland'],geographic_codes=['ALD'])
w['regions']['1826'].update(geographic_divisions=['Finland Proper'],geographic_codes=['FIN-3191'])
area_row=(6371.0088**2)*np.deg2rad(360/W)*(np.sin(np.deg2rad(90-np.arange(H)*180/H))-np.sin(np.deg2rad(90-(np.arange(H)+1)*180/H)))
for s in w['regions'].values():s['provinces']=[];s['neighbors']=[]
boxes=find_objects(a,max_label=max(map(int,ps)))
for key,p in ps.items():
 pid=int(key);bb=boxes[pid-1];assert bb is not None
 y,x=np.nonzero(a[bb]==pid);y+=bb[0].start;x+=bb[1].start
 p['area_km2']=round(float(area_row[y].sum()),3)
 if any(pid in row['into']for row in report['province_dissolutions']):
  j=int(np.argmin((y-y.mean())**2+((x-x.mean())*math.cos(math.radians(90-y.mean()/H*180)))**2));p['map_center']=[float((x[j]+.5)/W),float((y[j]+.5)/H)]
 p['neighbors']=[];w['regions'][str(p['region'])]['provinces'].append(pid)
edges=set()
for top in range(0,H,128):
 for l,r in [(a[top:top+128,:-1],a[top:top+128,1:]),(a[top:min(H-1,top+128)],a[top+1:min(H,top+129)])]:
  mask=(l>0)&(r>0)&(l!=r);values=np.minimum(l[mask],r[mask]).astype(np.uint32)*65536+np.maximum(l[mask],r[mask]);edges.update(divmod(int(c),65536)for c in np.unique(values))
for l,r in edges:
 if str(l)not in ps or str(r)not in ps:continue
 ps[str(l)]['neighbors'].append(r);ps[str(r)]['neighbors'].append(l)
 sl,sr=ps[str(l)]['region'],ps[str(r)]['region']
 if sl!=sr:w['regions'][str(sl)]['neighbors'].append(sr);w['regions'][str(sr)]['neighbors'].append(sl)
levels={'infrastructure','internet_station','air_base','radar_station','rail_terminal','anti_air_building','stronghold_network'}
for s in w['regions'].values():
 s['provinces'].sort();s['neighbors']=sorted(set(s['neighbors']));s['area_km2']=round(sum(ps[str(pid)]['area_km2']for pid in s['provinces']),3)
 for i,pid in enumerate(s['provinces'],1):
  p=ps[str(pid)];p['local_index']=6 if pid==3865 else i;p['name']=s['name']+' · Province '+str(p['local_index']);p['neighbors'].sort()
 for k in s['buildings']:
  if k in levels:s['buildings'][k]=min(10,s['buildings'][k])
 s['building_slot_baseline']=max(sum(n for k,n in s['buildings'].items()if k not in levels),4+int(4*math.sqrt(s['population']/100000)))
lookup=np.zeros(65536,np.uint16)
for p in ps.values():lookup[p['id']]=p['region']
def at(lon,lat):return int(a[min(H-1,max(0,int((90-lat)/180*H))),int((lon+180)/360*W)%W])
by=defaultdict(list)
for c in cities:
 pid=at(c['longitude'],c['latitude']);c['province_id']=pid
 for key in ['state_capital','state_id']:c.pop(key,None)
 if str(pid)in ps:by[ps[str(pid)]['region']].append(c)
for sid,s in w['regions'].items():
 choices=by[int(sid)]
 if choices:
  c=max(choices,key=lambda q:q.get('population_rank',0));c.update(state_capital=True,state_id=int(sid));s.update(state_capital=c['name'],capital_province=c['province_id'],capital_uv=[(c['longitude']+180)/360,(90-c['latitude'])/180],capital_is_settlement=True)
 else:
  pid=max(s['provinces'],key=lambda p:ps[str(p)]['area_km2']);s.update(state_capital=s['name']+' Centre',capital_province=pid,capital_uv=ps[str(pid)]['map_center'],capital_is_settlement=False)
  s['capital_source']='Administrative anchor: no resolved settlement'
report['national_capital_repairs']=[]
capital_candidates=defaultdict(list)
for marker in cities:
 if marker.get('capital'):capital_candidates[marker['country']].append(marker)
preferred={'USA':'Washington,  D.C.','IND':'Jakarta','SAF':'Pretoria','BOL':'La Paz'}
for city in cities:
 if not city.get('capital') or str(city['province_id'])not in ps:continue
 if len(capital_candidates[city['country']])>1 and city['name']!=preferred.get(city['country']):continue
 sid=ps[str(city['province_id'])]['region'];tag=city['country']
 if tag not in w['countries']or w['regions'][str(sid)]['owner']!=tag:continue
 c=w['countries'][tag]
 if c['capital']!=sid:report['national_capital_repairs'].append({'country':tag,'city':city['name'],'before':c['capital'],'after':sid})
 c['capital']=sid;c['map_center']=[(city['longitude']+180)/360,(90-city['latitude'])/180]
for tag,c in w['countries'].items():c['regions']=sorted(s['id']for s in w['regions'].values()if s['owner']==tag)
for kind in ['clusters','landmarks']:
 for c in scene[kind]:
  pid=at(c['longitude'],c['latitude'])
  if str(pid)in ps:c['province']=pid;c['state']=ps[str(pid)]['region']
by_scene=defaultdict(list)
for c in scene['clusters']:by_scene[c['state']].append(c)
for sid,clusters in by_scene.items():
 s=w['regions'][str(sid)];lon=s['capital_uv'][0]*360-180;lat=90-s['capital_uv'][1]*180
 capital=min(clusters,key=lambda c:((c['longitude']-lon)*math.cos(math.radians(lat)))**2+(c['latitude']-lat)**2)
 weights=[]
 for c in clusters:c['state_capital_priority']=c is capital;weights.append(max(1,len(c['instances']))*(1.2 if c is capital else 1))
 for c,v in zip(clusters,weights):c['state_visual_weight']=v/sum(weights)
for g in urban.get('groups',{}).values():g['provinces']=[p for p in g.get('provinces',[])if str(p)in ps]
urban['states']={k:{'population_2000':s['population']}for k,s in w['regions'].items()}
catalog=read('data/protected_territories_0210.json');catalog['version']='0.2.0.15'
for row in catalog['territories']:
 row['states']=sorted(set(1484 if sid==1485 else 1797 if sid==1751 else sid for sid in row['states']))
 if 'UNDOF'in row['name']or 'Demilitarized'in row['name']:row['boundary_reserved']=False;row['policy']='User-authorized strip dissolution in 0.2.0.15'
w['version']='0.2.0.15';w['scenario_id']='bunny_world_2000_0_2_0_15';scene['version']='0.2.0.15'
after=Counter()
for s in w['regions'].values():after[s['owner']]+=s['population']
assert before==after
for name,d in [('world',w),('provinces',ps),('cities',cities),('urban_population',urban),('urban_scenery',scene),('protected_territories_0210',catalog)]:write('data/'+name+'.json',d)
def npz(name,**values):
 b=io.BytesIO();np.savez_compressed(b,**values);(R/name).write_bytes(b.getvalue())
npz('tools/cartography/province_atlas_0215.npz',provinces=a)
states=lookup[a]
for i in range(4):
 y,x=i//2*4096,i%2*8192;rgb=np.asarray(Image.open(R/f'assets/region_ids_{i}.png'));mask=(rgb[:,:,0]==255)&(rgb[:,:,1]==255);states[y:y+4096,x:x+8192][mask]=8191
npz('tools/cartography/grouped_atlas_022r2.npz',regions=states)
index=np.zeros((256,256,3),np.uint8)
for p in ps.values():index[p['id']//256,p['id']%256]=[p['region']&255,p['region']>>8,p['local_index']]
index[255,255]=[255,31,0];Image.fromarray(index).save(R/'assets/province_index.png')
for i in range(4):
 y,x=i//2*4096,i%2*8192;v=a[y:y+4096,x:x+8192].copy()
 oldrgb=np.asarray(Image.open(R/f'assets/region_ids_{i}.png'));antarctica=(oldrgb[:,:,0]==255)&(oldrgb[:,:,1]==255);v[antarctica]=65535
 rgb=np.stack([(v&255).astype(np.uint8),(v>>8).astype(np.uint8),np.zeros_like(v,np.uint8)],-1);buff=io.BytesIO();Image.fromarray(rgb).save(buff,format='PNG');(R/f'assets/region_ids_{i}.png').write_bytes(buff.getvalue())
report.update(states=len(w['regions']),provinces=len(ps),province_pixels_changed=int(np.count_nonzero(old!=a)),country_populations_conserved=before==after,turku={'latitude':60.45148,'longitude':22.26869,'status':'Existing coordinates match GeoNames 633679; do not move to an invented position.'})
write('data/geography_0215_report.json',report);print(json.dumps(report,ensure_ascii=False),flush=True)
