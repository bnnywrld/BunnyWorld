"""Reconnect runtime records after geography replacement.

Only minimal bookkeeping is transferred. This is deliberately not a new
demographic model or a claim of new local population accuracy.
"""
from pathlib import Path
from collections import defaultdict
import copy,json,math
import numpy as np
from scipy.spatial import cKDTree
from build_geography_0206 import ROOT,SRC,BASE,W,H,alloc,write,xyz

world=json.load(open(ROOT/'data/world.json'));ps=json.load(open(ROOT/'data/provinces.json'))
cities=json.load(open(ROOT/'data/cities.json'));baseline_cities=json.load(open(BASE/'cities.json'))
old_account=json.load(open(BASE/'urban_population.json'))
atlas=np.load(SRC/'province_atlas_0206.npz')['provinces']
micro=json.load(open(ROOT/'data/microstate_geometry.json'))
world['regions'][str(micro['state'])]['map_center']=micro['center_uv']
world['countries'][micro['country']]['map_center']=micro['center_uv']
ps[str(micro['province'])]['map_center']=micro['center_uv']

def pid_at(lon,lat,owner=None):
    x=int((lon+180)/360*W)%W;y=min(H-1,max(0,int((90-lat)/180*H)))
    if abs(lon-(micro['center_uv'][0]*360-180))<.006 and abs(lat-(90-micro['center_uv'][1]*180))<.006:
        from shapely.geometry import Point,Polygon
        if Polygon(micro['polygon_uv']).covers(Point((lon+180)/360,(90-lat)/180)):return micro['province']
    p=int(atlas[y,x])
    if p and (not owner or world['regions'][str(ps[str(p)]['region'])]['owner']==owner):return p
    # Coordinates of coastal scenery can lie a few kilometres offshore. Retain
    # its old controller and snap the reference only; do not move graphics.
    yy,xx=np.mgrid[max(0,y-12):min(H,y+13),max(0,x-12):min(W,x+13)]
    ids=atlas[yy,xx];valid=(ids>0)
    if owner:
        valid&=np.array([world['regions'].get(str(ps.get(str(int(i)),{}).get('region',0)),{}).get('owner')==owner for i in ids.ravel()]).reshape(ids.shape)
    if valid.any():
        d=np.where(valid,(yy-y)**2+(xx-x)**2,np.inf);j=np.unravel_index(np.argmin(d),d.shape);return int(ids[j])
    return p

old_city={(c['country'],c['name']):c for c in baseline_cities}
province_city=defaultdict(list)
for c in cities:
    pid=pid_at(c['longitude'],c['latitude'],c['country'])
    c['province_id']=pid
    if pid:province_city[pid].append(c)
groups={}
for key,p in ps.items():
    pid=int(key);cc=province_city[pid];p['cities']=[c['name'] for c in cc]
    principal=max(cc,key=lambda c:c.get('population_rank',0)) if cc else None
    old=old_city.get((principal['country'],principal['name']),{}) if principal else {}
    gid=old.get('urban_group','') if principal else ''
    if principal and not gid:gid='geographic_city_%05d'%pid
    if gid and gid not in groups:
        groups[gid]=copy.deepcopy(old_account['groups'].get(gid,{'id':gid,'name':principal['name'],'country_at_start':principal['country'],'cities':[]}))
        groups[gid].update(provinces=[],population_2000=0,settlement_population_2000=0,representative_buildings=0)
    p['urban_group']=gid;p['kind']='city' if gid else 'rural'
    for c in cc:c['urban_group']=gid
    if gid:groups[gid]['provinces'].append(pid)

# Existing scenery is retained and relinked to new IDs at its real coordinates.
scene_path=BASE/'urban_scenery.json'
if not scene_path.exists():scene_path.write_bytes((ROOT/'data/urban_scenery.json').read_bytes())
scene=json.load(open(scene_path));oldps=json.load(open(BASE/'provinces.json'));oldworld=json.load(open(BASE/'world.json'))
for kind in ['clusters','landmarks']:
    for record in scene[kind]:
        oldpid=str(record['province']);tag=oldworld['regions'][str(oldps[oldpid]['region'])]['owner']
        pid=pid_at(record['longitude'],record['latitude'],tag)
        if not pid:raise ValueError(('unlinked scenery',record['name']))
        record['province']=pid
        gid=ps[str(pid)]['urban_group']
        if not gid:
            oldgid=record.get('group','')
            if oldgid in old_account['groups']:
                gid=oldgid
                if gid not in groups:
                    groups[gid]=copy.deepcopy(old_account['groups'][gid]);groups[gid].update(provinces=[],population_2000=0,settlement_population_2000=0,representative_buildings=0)
                ps[str(pid)]['urban_group']=gid;ps[str(pid)]['kind']='city';groups[gid]['provinces'].append(pid)
        record['group']=gid
        if kind=='clusters' and gid:groups[gid]['representative_buildings']+=len(record['instances'])
        if kind=='landmarks':record['country']=world['regions'][str(ps[str(pid)]['region'])]['owner']

account={'epoch':2000,'source':{'method':'Temporary area allocation of retained scenario totals; local demographic refinement deferred in 0.2.0.6.'},'groups':groups,'states':{},'growth_enabled':False,'country_reconciliation_factors':{},'population_scope':'Temporary geometry-patch bookkeeping, not revised local demographic estimates.'}
for key,state in world['regions'].items():
    ids=state['provinces'];values=alloc(state['population'],[ps[str(i)]['area_km2'] for i in ids])
    urban=[];shared=[]
    for pid,pop in zip(ids,values):
        p=ps[str(pid)];p['population_2000']=int(pop)
        gid=p['urban_group']
        if gid:
            urban.append(pid);groups[gid]['population_2000']+=int(pop)
        else:shared.append(pid)
    urbanpop=sum(ps[str(i)]['population_2000'] for i in urban)
    account['states'][key]={'state':int(key),'population_2000':state['population'],'urban_provinces':urban,'shared_provinces':shared,'urban_population_2000':urbanpop,'shared_population_2000':state['population']-urbanpop,'raw_grid_population':0,'state_reconciliation_factor':1,'fallback_area_allocation':True}
for c in cities:c['population_2000']=ps[str(c['province_id'])]['population_2000'] if c['province_id'] else None
for g in groups.values():g['settlement_population_2000']=g['population_2000'];g['provinces']=sorted(set(g['provinces']))
scene['version']='0.2.0.6'
write('world',world);write('provinces',ps);write('cities',cities);write('urban_population',account);write('urban_scenery',scene)
print('GEOGRAPHIC_LINKS_COMPLETE',len(ps),'provinces',len(cities),'cities',len(groups),'retained city groups',flush=True)
