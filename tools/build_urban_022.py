"""Build immutable 2000 urban accounting and lightweight representative scenery.
Run after prepare_population_022.py. No population growth is simulated here.
"""
from pathlib import Path
from collections import defaultdict
import hashlib, json, math, random
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import find_objects
from micro_geometry import MicroGeometry

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'tools/cartography'
world=json.load(open(ROOT/'data/world.json'))
provinces=json.load(open(ROOT/'data/provinces.json'))
cities=json.load(open(ROOT/'data/cities.json'))
names=json.load(open(SRC/'urban_names_022.json'))
source=json.load(open(SRC/'population_022_source.json'))
prepared=np.load(SRC/'population_022.npz')
raw=prepared['total'];dense=prepared['dense'];xyz=prepared['xyz']
atlas_path=SRC/'province_atlas_022r2.npz'
atlas=np.load(atlas_path if atlas_path.exists() else SRC/'province_atlas_021.npz')['provinces'];H,W=atlas.shape
micro=MicroGeometry(ROOT) if (ROOT/'data/microstate_geometry.json').exists() else None
boxes=find_objects(atlas,max_label=65535)

def unit(lon,lat):
    a,b=map(math.radians,[lon,lat]);return np.array([math.cos(b)*math.sin(a),math.sin(b),math.cos(b)*math.cos(a)])
def coords(p):
    return [math.degrees(math.atan2(p[0],p[2])),math.degrees(math.asin(float(np.clip(p[1]/max(np.linalg.norm(p),1e-12),-1,1))))]
def pid_at(lon,lat):
    identity=int(atlas[min(H-1,max(0,int((90-lat)/180*H))),int((lon+180)/360*W)%W])
    return micro.resolve(lon,lat,identity) if micro else identity
def province_point(p):
    q=xyz[p['id']]
    if dense[p['id']]>0 and np.linalg.norm(q)>0: return q/np.linalg.norm(q)
    u,v=p['map_center'];return unit(u*360-180,90-v*180)

# Reconstitute point-to-province links from accepted annotations, including
# shoreline points that were snapped during 0.1.10. Same names in different
# countries are distinct records.
by_city=defaultdict(list)
for p in provinces.values():
    for name in p['cities']:by_city[(world['regions'][str(p['region'])]['owner'],name)].append(p['id'])
placed=[]
relinked=[]
for city in cities:
    ids=by_city[(city['country'],city['name'])]
    if not ids:
        pid=pid_at(city['longitude'],city['latitude'])
        if str(pid) in provinces:
            # Natural Earth country names describe modern geography, whereas
            # this scenario has separate controllers such as Kurdistan/Aceh.
            # The province, not that point label, owns the resident population.
            p=provinces[str(pid)];owner=world['regions'][str(p['region'])]['owner']
            city.setdefault('geographic_country_reference',city['country'])
            relinked.append({'city':city['name'],'reference_country':city['country'],'starting_controller':owner})
            city['country']=owner
            if city['name'] not in p['cities']:p['cities'].append(city['name'])
            by_city[(owner,city['name'])].append(pid);ids=[pid]
    if not ids:
        city['province_id']=0;city['urban_group']='';city['population_2000']=None;continue
    point=unit(city['longitude'],city['latitude'])
    pid=min(ids,key=lambda p:np.linalg.norm(province_point(provinces[str(p)])-point))
    city['province_id']=pid
    city['point']=point
    city['urban_index']=len(placed)
    placed.append(city)
parent=list(range(len(placed)))
def find(i):
    while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
    return i
def union(a,b):parent[find(b)]=find(a)
same=defaultdict(list)
for i,c in enumerate(placed):same[c['province_id']].append(i)
for ids in same.values():
    for j in ids[1:]:union(ids[0],j)
curated={}
for area in names['metropolitan_areas']:
    ids=[i for i,c in enumerate(placed) if c['country']==area['country'] and c['name'] in area['cities']]
    if not ids:continue
    for j in ids[1:]:union(ids[0],j)
    curated[ids[0]]=area['name']
sets=defaultdict(list)
for i in range(len(placed)):sets[find(i)].append(i)
groups={};city_group={}
for indices in sets.values():
    members=[placed[i] for i in indices]
    principal=max(members,key=lambda c:c.get('population_rank',0))
    established=next((name for i,name in curated.items() if find(i)==find(indices[0])),None)
    group_id='urban_%05d'%min(c['province_id'] for c in members)
    group_name=established or (principal['name']+' metropolitan area' if len(members)>1 else principal['name'])
    groups[group_id]={'id':group_id,'name':group_name,'name_basis':'established metropolitan name' if established else ('descriptive metropolitan name' if len(members)>1 else 'city name'), 'country_at_start':principal['country'],'cities':[c['name'] for c in members],'provinces':[], 'population_2000':0,'settlement_population_2000':0,'representative_buildings':0}
    for c in members:city_group[c['urban_index']]=group_id;c['urban_group']=group_id

# Expand a large city's group into neighboring populated cells without changing
# province geometry. Use dense 2000 residents, a bounded city catchment and the
# nearest city of the same starting country. Do not absorb empty countryside.
trees={}
for country in sorted(set(c['country'] for c in placed)):
    members=[c for c in placed if c['country']==country]
    trees[country]=(cKDTree([c['point'] for c in members]),members)
seed_groups={pid:city_group[indices[0]] for pid,indices in same.items()}
for p in provinces.values():
    pid=p['id'];gid=seed_groups.get(pid)
    if not gid and dense[pid]>=20000 and dense[pid]>=raw[pid]*.12:
        owner=world['regions'][str(p['region'])]['owner']
        if owner in trees:
            tree,members=trees[owner];d,i=tree.query(province_point(p));c=members[int(i)]
            rank=float(c.get('population_rank',0));radius=70 if rank>=10000000 else 45 if rank>=1000000 else 22
            if d*6371<=radius:gid=city_group[c['urban_index']]
    p['kind']='city' if gid else 'rural'
    p['urban_group']=gid or ''
    if gid:groups[gid]['provinces'].append(pid)
    else:
        p.pop('population_2000',None);p.pop('name',None)

def allocate(total,weights):
    weights=np.maximum(np.array(weights,dtype=float),0)
    if weights.sum()==0:weights=np.ones_like(weights)
    exact=weights/weights.sum()*total;result=np.floor(exact).astype(np.int64)
    count=int(total-result.sum())
    order=np.argsort(-(exact-result),kind='stable')
    result[order[:count]]+=1
    assert int(result.sum())==total
    return result

state_accounting={};normalization=[]
country_parts={};country_factors={};population_changes=[]
for r in world['regions'].values():
    ids=r['provinces'];weights=[raw[pid] for pid in ids]
    if sum(weights)==0:weights=[provinces[str(pid)]['area_km2'] for pid in ids]
    country_parts.update(dict(zip(ids,map(int,allocate(int(r['population']),weights)))))
for owner in sorted(set(r['owner'] for r in world['regions'].values())):
    states=[r for r in world['regions'].values() if r['owner']==owner]
    country_factors[owner]=sum(r['population'] for r in states)/max(sum(raw[pid] for r in states for pid in r['provinces']),1)
for sid,r in world['regions'].items():
    ids=r['provinces'];urban_ids=[pid for pid in ids if provinces[str(pid)]['urban_group']]
    rural_ids=[pid for pid in ids if not provinces[str(pid)]['urban_group']]
    weights=[raw[pid] for pid in ids]
    if sum(weights)==0:weights=[provinces[str(pid)]['area_km2'] for pid in ids]
    parts={pid:country_parts[pid] for pid in ids}
    factor=int(r['population'])/max(sum(raw[pid] for pid in ids),1)
    for pid in ids:provinces[str(pid)]['population_2000']=parts[pid]
    for pid in urban_ids:
        p=provinces[str(pid)];p['population_2000']=parts[pid]
        p['settlement_population_2000']=min(parts[pid],round(dense[pid]*factor))
        p['population_basis']='2000 resident-grid estimate, reconciled to state total; includes countryside'
        group=groups[p['urban_group']]
        group['population_2000']+=parts[pid]
        group['settlement_population_2000']+=p['settlement_population_2000']
    shared=sum(parts[pid] for pid in rural_ids)
    state_accounting[sid]={'state':int(sid),'population_2000':int(r['population']),'urban_provinces':urban_ids,'shared_provinces':rural_ids,'urban_population_2000':sum(parts[pid] for pid in urban_ids),'shared_population_2000':shared,'raw_grid_population':round(sum(raw[pid] for pid in ids),2),'state_reconciliation_factor':round(factor,6),'fallback_area_allocation':sum(raw[pid] for pid in ids)==0}
    normalization.append({'state':int(sid),'name':r['name'],'factor':round(factor,4)})

# Name large-city pieces from real district/locality anchors. Since the game
# cells are deliberately larger than municipal districts, use "area" and
# disclose the coverage rather than imply these are census polygons.
for group in groups.values():
    anchors=names['districts'].get(group['name'],[])
    for pid in group['provinces']:
        p=provinces[str(pid)]
        if len(group['provinces'])==1:p['name']=group['name'];p['urban_role']='city / metropolitan province'
        else:
            point=province_point(p)
            if len(p['cities'])>1:
                members=[c for c in placed if c['province_id']==pid]
                label='–'.join(c['name'] for c in sorted(members,key=lambda c:c.get('population_rank',0),reverse=True)[:2])
            elif anchors:
                a=min(anchors,key=lambda a:np.linalg.norm(unit(a[0],a[1])-point));label=a[2]
            else:
                members=[c for c in placed if c['urban_group']==group['id']]
                label=min(members,key=lambda c:np.linalg.norm(c['point']-point))['name']
            p['name']=group['name']+' — '+label+' area'
            p['urban_role']='district / locality coverage'
        p['name_basis']=group['name_basis']
        p['district_boundary_note']='Game province coverage; surrounding countryside belongs to this urban province.'

def tier(pop):
    if pop>=10000000:return 'Megacity',32+min(8,int((pop-10000000)/3000000))
    if pop>=5000000:return 'Metropolis',16+min(8,int((pop-5000000)/625000))
    if pop>=1000000:return 'Large city',8+min(8,int((pop-1000000)/500000))
    if pop>=100000:return 'City',4+min(4,int((pop-100000)/225000))
    return 'Town',2

# Allocate each group's very small visual budget across distinct populated
# provinces, not once per city marker (which would multiply metro skylines).
scene=[]
for group in groups.values():
    category,budget=tier(group['settlement_population_2000']);budget*=8 if category in ['Town','City'] else 10;group['category']=category
    ids=group['provinces'];weights=[provinces[str(pid)]['settlement_population_2000'] for pid in ids]
    if not sum(weights):weights=[provinces[str(pid)]['population_2000'] for pid in ids]
    quotas=allocate(budget,weights)
    for pid,count in zip(ids,quotas):
        if not count:continue
        p=provinces[str(pid)];point=province_point(p)
        members=sorted([c for c in placed if c['province_id']==pid],key=lambda c:c.get('population_rank',0),reverse=True)[:int(count)]
        sites=[(c['longitude'],c['latitude'],max(1,float(c.get('population_rank',1)))) for c in members] or [(*coords(point),1)]
        site_counts=allocate(int(count)-len(sites),[s[2] for s in sites])+1
        for site_index,((lon,lat,_),site_count) in enumerate(zip(sites,site_counts)):
            if pid_at(lon,lat)!=pid:
                bb=boxes[pid-1];y,x=np.nonzero(atlas[bb]==pid);y+=bb[0].start;x+=bb[1].start
                xx=(x+.5)/W*360-180;yy=90-(y+.5)/H*180
                delta=(xx-lon+180)%360-180
                j=np.argmin((np.cos(np.deg2rad(lat))*delta)**2+(yy-lat)**2)
                lon,lat=float(xx[j]),float(yy[j])
            rng=random.Random(pid*2000+site_index*122+22);instances=[]
            economy=float(world['countries'].get(group['country_at_start'],{}).get('starting_stats',{}).get('gdp_per_capita_usd',0))
            spread=1.4 if category in ['Town','City'] else 3.5
            for i in range(int(site_count)):
                chosen=None
                for attempt in range(80):
                    angle=rng.random()*math.tau;radius=spread*math.sqrt(rng.random())
                    a=lon+math.cos(angle)*radius/(111.195*max(.1,math.cos(math.radians(lat))))
                    b=lat+math.sin(angle)*radius/111.195
                    if pid_at(a,b)==pid:chosen=(a,b);break
                if chosen is None:chosen=(lon,lat)
                tall=category in ['Large city','Metropolis','Megacity'] and economy>=4000 and i%4==0
                height=rng.uniform(65,190) if tall else rng.uniform(12,48)
                if group['country_at_start'] in ['JAP','KOR','CHI'] and category=='Megacity' and i%5==0:height=rng.uniform(80,200)
                instances.append([round(chosen[0],6),round(chosen[1],6),round(rng.uniform(22,44),1),round(height,1),round(rng.random()*math.tau,3),1 if tall else 0])
            scene.append({'id':pid*100+site_index,'province':pid,'group':group['id'],'name':p['name'],'longitude':lon,'latitude':lat,'category':category,'population_2000':p['population_2000'],'instances':instances})
            group['representative_buildings']+=len(instances)
    assert group['representative_buildings']<=400
for city in cities:
    if not city.get('province_id'):continue
    p=provinces[str(city['province_id'])];city['population_2000']=p['population_2000'];city['population_scope']='Whole containing game province, shared by markers in that province'
    city.pop('point',None);city.pop('urban_index',None)

landmarks=[
    {'id':'eiffel','name':'Eiffel Tower','longitude':2.2945,'latitude':48.8584,'height_m':324,'model':'lattice','color':'977456','opened':1889},
    {'id':'liberty','name':'Statue of Liberty','longitude':-74.0445,'latitude':40.6892,'height_m':93,'model':'liberty','color':'79b4a0','opened':1886},
    {'id':'big_ben','name':'Big Ben','longitude':-.1246,'latitude':51.5007,'height_m':96,'model':'clock','color':'c6ad7d','opened':1859},
    {'id':'tokyo_tower','name':'Tokyo Tower','longitude':139.7454,'latitude':35.6586,'height_m':333,'model':'lattice','color':'e66336','opened':1958},
    {'id':'pyramids','name':'Pyramids of Giza','longitude':31.1342,'latitude':29.9792,'height_m':139,'model':'pyramids','color':'d5b67b','opened':-2500},
    {'id':'colosseum','name':'Colosseum','longitude':12.4922,'latitude':41.8902,'height_m':48,'model':'colosseum','color':'c4aa8a','opened':80},
    {'id':'opera','name':'Sydney Opera House','longitude':151.2153,'latitude':-33.8568,'height_m':65,'model':'opera','color':'e6e4da','opened':1973},
    {'id':'christ','name':'Christ the Redeemer','longitude':-43.2105,'latitude':-22.9519,'height_m':38,'model':'christ','color':'d2d5cf','opened':1931}
]
for l in landmarks:
    l['country']={'eiffel':'FRA','liberty':'USA','big_ben':'ENG','tokyo_tower':'JAP','pyramids':'EGY','colosseum':'ITA','opera':'AST','christ':'BRA'}[l['id']]
    l['province']=pid_at(l['longitude'],l['latitude'])
    if str(l['province']) not in provinces or world['regions'][str(provinces[str(l['province'])]['region'])]['owner']!=l['country']:
        # Small islands can be water at game scale; keep the true monument
        # coordinate and its own tiny pedestal instead of moving it inland.
        near=[p for p in provinces.values() if p['urban_group'] and world['regions'][str(p['region'])]['owner']==l['country']]
        l['province']=min(near,key=lambda p:np.linalg.norm(province_point(p)-unit(l['longitude'],l['latitude'])))['id']
    l['group']=provinces[str(l['province'])]['urban_group']
    l['coordinate_basis']='Approximate monument location; display size exaggerated for close-range readability'

source['method']='Sum year-2000 resident-grid cells by game province coverage; reconcile shares within each State to its accepted scenario total. Reserve small zero-grid island populations. Retain an individual estimate for every province; city groups are aggregate views.'
source['accuracy']='Modelled year-2000 estimates reconciled to State totals, not municipal census counts. Game provinces include countryside and do not reproduce district boundaries.'
accounting={'epoch':2000,'source':source,'groups':groups,'states':state_accounting,'growth_enabled':False,'country_reconciliation_factors':country_factors,'population_scope':'Entire urban game province, including surrounding countryside; all rural provinces also hold individual estimates reconciled within each State.'}
report={'version':'0.2.0.3','city_groups':len(groups),'urban_provinces':sum(p['kind']=='city' for p in provinces.values()),'district_provinces':sum(p.get('urban_role')=='district / locality coverage' for p in provinces.values()),'scene_clusters':len(scene),'representative_buildings':sum(len(s['instances']) for s in scene),'landmarks':len(landmarks),'population_total':sum(r['population'] for r in world['regions'].values()),'urban_province_population':sum(s['urban_population_2000'] for s in state_accounting.values()),'shared_population':sum(s['shared_population_2000'] for s in state_accounting.values()),'highest_reconciliation_factors':sorted(normalization,key=lambda v:v['factor'],reverse=True)[:20]}
world['scenario_id']='bunny_world_2000_0_2_0_3';world['schema_version']=9
report['state_population_reallocations']=len(population_changes)
report['country_totals_preserved']=True
report['city_controller_links_corrected']=relinked
report['cities_placed']=sum(bool(c.get('province_id')) for c in cities)
world['map']['urban_population']='GHSL 2000 grid-weighted estimates for every province, reconciled to State totals; city/metropolitan groups are aggregate views.'
for name,data in [('world',world),('provinces',provinces),('cities',cities),('urban_population',accounting),('urban_scenery',{'clusters':scene,'landmarks':landmarks,'version':'0.2.0.3','display_size_multiplier':3.0,'building_cap':2048,'cluster_cap':96,'fade_start_distance':1.18,'fade_full_distance':1.08,'growth_enabled':False}),('urban_022_report',report)]:
    (ROOT/'data'/f'{name}.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'),default=lambda v:v.item()))
print('URBAN_022_COMPLETE',json.dumps(report),flush=True)
