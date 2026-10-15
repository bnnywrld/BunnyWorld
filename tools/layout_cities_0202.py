"""Deterministic street blocks, displayed-footprint spacing and landmark plazas.
All placements are offline. Runtime only toggles prepared batched meshes.
"""
from pathlib import Path
from collections import defaultdict
import math,json,random,itertools
import numpy as np
from micro_geometry import MicroGeometry
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1]
scene=json.load(open(ROOT/'data/urban_scenery.json'));account=json.load(open(ROOT/'data/urban_population.json'))
world=json.load(open(ROOT/'data/world.json'));provs=json.load(open(ROOT/'data/provinces.json'))
atlas=np.load(ROOT/'tools/cartography/province_atlas_0203.npz')['provinces'];H,W=atlas.shape;micro=MicroGeometry(ROOT)
def pid_at(lon,lat):
    p=int(atlas[min(H-1,max(0,int((90-lat)/180*H))),int((lon+180)/360*W)%W]);return micro.resolve(lon,lat,p)
def country(p):return world['regions'][str(provs[str(p)]['region'])]['owner'] if p else None
def unit(lon,lat):
    a,b=map(math.radians,[lon,lat]);return np.array([math.cos(b)*math.sin(a),math.sin(b),math.cos(b)*math.cos(a)])*6371
# Dense course samples provide a conservative buffer for the visible ribbons.
river_points=[]
for feature in json.load(open(ROOT/'tools/cartography/rivers_0201.geojson'))['features']:
    prop=feature['properties']
    if float(prop.get('scalerank',10) or 0)>6 or prop.get('featurecla')!='River':continue
    geometry=feature['geometry'];lines=geometry['coordinates'] if geometry['type']=='MultiLineString' else [geometry['coordinates']]
    for line in lines:
        for a,b in zip(line[:-1],line[1:]):
            a=np.array(a[:2],float);b=np.array(b[:2],float)
            if abs(b[0]-a[0])>180:continue
            length=np.linalg.norm((b-a)*np.array([math.cos(math.radians((a[1]+b[1])*.5)),1]))*111.195
            n=max(1,int(math.ceil(length/.15)));t=np.arange(n+1)/n;q=a[None,:]+(b-a)[None,:]*t[:,None]
            lon,lat=np.deg2rad(q[:,0]),np.deg2rad(q[:,1]);river_points.append(np.column_stack([np.cos(lat)*np.sin(lon),np.sin(lat),np.cos(lat)*np.cos(lon)])*6371)
river_tree=cKDTree(np.concatenate(river_points));del river_points
cells=defaultdict(list);spacing=.25;cell_size=2.5
def key(p):return tuple(np.floor(p/cell_size).astype(int))
def nearby(p,radius):
    k=key(p);reach=max(1,math.ceil((radius+2)/cell_size))
    for d in itertools.product(range(-reach,reach+1),repeat=3):
        yield from cells[tuple(k[i]+d[i] for i in range(3))]
def free(p,r):return all(np.linalg.norm(p-q)>=r+s+spacing for q,s in grounds) and all(np.linalg.norm(p-q)>=r+s+spacing for q,s in nearby(p,r))
def reserve(p,r):cells[key(p)].append((p,r))
model_radius={'lattice':.34,'liberty':.35,'clock':.26,'pyramids':1.95,'colosseum':.92,'opera':1.0,'christ':.40}
grounds=[]
for l in scene['landmarks']:
    l['horizontal_scale']=.60;r=max(100,l['height_m'])*54/1000*model_radius[l['model']]*.60+.45
    l['display_footprint_radius_km']=r;point=unit(l['longitude'],l['latitude']);grounds.append((point,r));reserve(point,r)
for group in account['groups'].values():group['representative_buildings']=0
lots=sorted(itertools.product(range(-26,27),repeat=2),key=lambda q:(q[0]*q[0]+q[1]*q[1],q))
total=0;skipped=[]
for cluster_number,c in enumerate(scene['clusters']):
    if cluster_number%200==0:print('LAYOUT_PROGRESS',cluster_number,len(scene['clusters']),flush=True)
    quota=len(c['instances']);rng=random.Random(int(c['id'])+2002);lon,lat=c['longitude'],c['latitude'];owner=country(c['province']);angle=(int(c['group'].split('_')[-1])%17)*.037
    buildings=[]
    for gx,gy in lots:
        if len(buildings)>=quota:break
        # Empty lots and larger gaps every four blocks create streets/plazas.
        if (gx*7+gy*11)%37==0 and gx*gx+gy*gy>4:continue
        e=gx*1.75+math.floor(gx/4)*.55;n=gy*1.75+math.floor(gy/4)*.55
        east=e*math.cos(angle)-n*math.sin(angle);north=e*math.sin(angle)+n*math.cos(angle)
        a=lon+east/(111.195*max(.1,math.cos(math.radians(lat))));b=lat+north/111.195
        if pid_at(a,b)!=c['province']:continue
        a=round(a,6);b=round(b,6);width=round(rng.uniform(17,27),1);radius=width*36*1.4/1000/math.sqrt(2);point=unit(a,b)
        if river_tree.query(point)[0]<radius+1.9:continue
        if not free(point,radius):continue
        # Test footprint corners against physical land and starting ownership.
        valid=True
        for x,y in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            aa=a+x*radius/(111.195*max(.1,math.cos(math.radians(b))));bb=b+y*radius/111.195
            if country(pid_at(aa,bb))!=owner:valid=False;break
        if not valid:continue
        tall=c['category'] in ['Large city','Metropolis','Megacity'] and len(buildings)%4==0
        height=rng.uniform(65,200) if tall else rng.uniform(14,55)
        buildings.append([round(a,6),round(b,6),round(width,1),round(height,1),round(angle,3),int(tall)])
        # Round before reserving, matching exactly the rendered footprint.
        reserve(unit(buildings[-1][0],buildings[-1][1]),buildings[-1][2]*36*1.4/1000/math.sqrt(2))
    c['instances']=buildings;account['groups'][c['group']]['representative_buildings']+=len(buildings);total+=len(buildings)
    if len(buildings)<quota:skipped.append({'cluster':c['id'],'target':quota,'placed':len(buildings)})
scene.update(version='0.2.0.3',building_cap=2048,cluster_cap=96,display_size_multiplier=3.0)
report={'version':'0.2.0.3','representative_buildings':total,'clusters':len(scene['clusters']),'landmarks':len(grounds),'minimum_displayed_gap_km':spacing,'capacity_limited_clusters':skipped,'layout':'Shared street-block orientation, avenues and empty plazas; landmark grounds reserved','river_clearance_km':1.9,'runtime_regeneration':False}
for name,data in [('urban_scenery',scene),('urban_population',account),('city_layout_0202',report)]:
    (ROOT/'data'/f'{name}.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
print('CITY_LAYOUT_COMPLETE',total,len(skipped),flush=True)
