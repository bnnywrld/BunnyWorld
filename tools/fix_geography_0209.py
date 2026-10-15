"""Second authored geography pass, based on the delivered 0.2.0.8 source.

Offline preparation only. Reuses the established intersection, accounting,
connectivity and runtime texture preparation algorithms from 0.2.0.8.
"""
from pathlib import Path
from collections import Counter,defaultdict
import copy,json,math,shutil
import numpy as np
from PIL import Image
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from scipy.ndimage import find_objects,label,binary_dilation,gaussian_filter
from scipy.spatial import cKDTree
from skimage.graph import MCP_Geometric
from skimage.segmentation import watershed
from pyproj import Transformer
from fix_geography_0208 import ROOT,SRC,W,H,AREA,read,write,alloc,focus,xyz,mapping

VERSION='0.2.0.9';BASE=ROOT/'.geography_0209_baseline'
Image.MAX_IMAGE_PIXELS=None
ELEV=None;CITY_POINTS=None

def atomic_png(array,path):
    import os
    path=Path(path);temporary=path.with_name(path.name+'.prepare-tmp')
    Image.fromarray(array).save(temporary,format='PNG')
    with Image.open(temporary) as im:im.verify()
    with temporary.open('rb') as f:os.fsync(f.fileno())
    temporary.replace(path)

def snapshot():
    names=['data/'+n+'.json' for n in ['world','provinces','cities','urban_population','urban_scenery','microstate_geometry','sea_regions']]
    names+=['tools/cartography/grouped_atlas_022r2.npz','tools/cartography/province_atlas_0208.npz','assets/sea_ids.png']
    if not (BASE/'data/world.json').exists():
        if read(ROOT/'data/world.json')['version']!='0.2.0.8':raise ValueError('Requires delivered 0.2.0.8 baseline')
        for n in names:
            p=BASE/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,p)
    if read(BASE/'data/world.json')['version']!='0.2.0.8':raise ValueError('Wrong cached baseline')

def partition(yy,xx,count,seed_locations=None):
    """Terrain-guided growth with physically spaced seeds, only inside a mask."""
    global ELEV,CITY_POINTS
    if count<=1:return np.ones(len(xx),np.int32)
    if ELEV is None:ELEV=np.load(SRC/'etopo_021.npz')['meters']
    y0,y1=int(yy.min()),int(yy.max())+1;x0,x1=int(xx.min()),int(xx.max())+1
    mask=np.zeros((y1-y0,x1-x0),bool);mask[yy-y0,xx-x0]=True
    u,v=focus(yy,xx);lo=u*360-180;la=90-v*180
    proj=Transformer.from_crs('EPSG:4326',f'+proj=laea +lat_0={la} +lon_0={lo} +datum=WGS84 +units=km',always_xy=True)
    px,py=proj.transform((xx+.5)/W*360-180,90-(yy+.5)/H*180);points=np.column_stack([px,py]);tree=cKDTree(points)
    seeds=[]
    if seed_locations:
        for lon,lat in seed_locations:
            j=int(tree.query(proj.transform(lon,lat))[1])
            if j not in seeds:seeds.append(j)
    elif CITY_POINTS is not None:
        for lon,lat in CITY_POINTS:
            x=int((lon+180)/360*W);y=int((90-lat)/180*H)
            if y0<=y<y1 and x0<=x<x1 and mask[y-y0,x-x0]:
                j=int(tree.query(proj.transform(lon,lat))[1])
                if all(np.linalg.norm(points[j]-points[k])>18 for k in seeds):seeds.append(j)
                # Retain most slots for spaced coverage seeds, so a dense
                # town cluster cannot leave the rural remainder as one giant.
                if len(seeds)>=max(1,count//3):break
    if not seeds:seeds=[int(tree.query(points.mean(0))[1])]
    sample=np.arange(0,len(xx),max(1,len(xx)//25000));sp=points[sample]
    dist=np.min(np.sum((sp[:,None]-points[seeds][None,:])**2,axis=2),axis=1)
    while len(seeds)<count:
        j=int(sample[np.argmax(dist)]);seeds.append(j);dist=np.minimum(dist,np.sum((sp-points[j])**2,axis=1))
    seeds=seeds[:count];markers=np.zeros(mask.shape,np.int32)
    for i,j in enumerate(seeds,1):markers[yy[j]-y0,xx[j]-x0]=i
    rows=np.clip(np.arange(y0,y1)*ELEV.shape[0]//H,0,ELEV.shape[0]-1)
    cols=np.clip(np.arange(x0,x1)*ELEV.shape[1]//W,0,ELEV.shape[1]-1)
    z=gaussian_filter(ELEV[rows[:,None],cols].astype(float),1.2)
    grad=np.hypot(*np.gradient(z)) if min(z.shape)>1 else np.zeros_like(z)
    gy,gx=np.indices(mask.shape);cost=1.2+np.clip(grad/140,0,4)+.12*np.sin(gx/19+gy/29)
    cost[~mask]=np.inf;starts=np.column_stack(np.nonzero(markers))
    distance,_=MCP_Geometric(cost,fully_connected=True).find_costs(starts)
    reached=mask&np.isfinite(distance);grown=watershed(np.where(reached,distance,0),markers,mask=reached,connectivity=2)
    result=grown[yy-y0,xx-x0];empty=result==0
    if empty.any():
        nearest=cKDTree(points[seeds]).query(points[empty])[1];result[empty]=nearest+1
    return result

def main():
    global CITY_POINTS
    snapshot();oldw=read(BASE/'data/world.json');world=copy.deepcopy(oldw)
    oldstates=np.load(BASE/'tools/cartography/grouped_atlas_022r2.npz')['regions']
    oldprov=np.load(BASE/'tools/cartography/province_atlas_0208.npz')['provinces']
    oldps=read(BASE/'data/provinces.json');records=copy.deepcopy(oldw['regions']);states=oldstates.copy()
    nextid=max(map(int,records))+1;identities={};audit=[];moved=[]
    ownerlut=np.zeros(8192,np.uint16)
    for k,s in records.items():ownerlut[int(k)]=world['countries'][s['owner']]['index']
    owners=ownerlut[oldstates]
    features=read(SRC/'geographic_subdivisions.geojson')['features'];disputes=read(SRC/'disputed_areas.geojson')['features']
    cities=read(BASE/'data/cities.json');CITY_POINTS=[(c['longitude'],c['latitude']) for c in sorted(cities,key=lambda q:-q.get('population_rank',0))]
    def find(tag,name):
        rows=[s for s in records.values() if s['owner']==tag and s['name']==name]
        if len(rows)!=1:raise ValueError(('Ambiguous state',tag,name,len(rows)))
        return rows[0]['id']
    def identity(tag,name,protected=''):
        nonlocal nextid
        key=(tag,name)
        if key not in identities:
            sid=nextid;nextid+=1;identities[key]=sid
            records[str(sid)]={'id':sid,'name':name,'owner':tag,'population':0,'buildings':{},'provinces':[],
              'cores':[tag],'claims':[],'source_states':[],'geographic_divisions':[],'geographic_codes':[],
              'map_center':[0,0],'area_km2':0,'demographic_profile':tag,'protected_territory':protected,
              'protected_territory_name':name if protected else '', 'protected_territories':[protected] if protected else [],
              'population_source':'Retained 0.2.0.8 accounting transferred by geographic overlap.'}
        return identities[key]
    def move_provinces(tag,name,indices,target_tag,target_name):
        sid=find(tag,name);target=find(target_tag,target_name)
        for i in indices:
            pp=[p for p in oldps.values() if p['region']==sid and p['local_index']==i]
            if len(pp)!=1:raise ValueError(('Ambiguous local province',name,i))
            p=pp[0];states[oldprov==p['id']]=target
            moved.append({'source':name,'old_local_index':i,'province_id':p['id'],'target':target_name,'target_state':target})
    def regroup(tag,admin,mapper,restriction=None):
        mask=owners==world['countries'][tag]['index']
        if restriction is not None:mask&=restriction
        shapes=[]
        for f in features:
            p=f['properties']
            if p.get('admin')!=admin:continue
            name=mapper(p)
            if name is None:continue
            sid=identity(tag,name);shapes.append((f['geometry'],sid))
            s=records[str(sid)];n=p.get('name_en') or p.get('name')
            if n and n not in s['geographic_divisions']:s['geographic_divisions'].append(n)
            if p.get('adm1_code') not in s['geographic_codes']:s['geographic_codes'].append(p.get('adm1_code'))
        assigned=rasterize(shapes,out_shape=(H,W),transform=from_bounds(-180,-90,180,90,W,H),dtype='uint16');assigned[~mask]=0
        missing=mask&(assigned==0)
        if restriction is not None:
            # A selective ADM1 replacement may fill coastline gaps, but must
            # not expand eighty kilometres into another native land division.
            other=[(f['geometry'],1) for f in features if f['properties'].get('admin')==admin and mapper(f['properties']) is None]
            if other:
                occupied=rasterize(other,out_shape=(H,W),transform=from_bounds(-180,-90,180,90,W,H),dtype='uint8')>0
                missing&=~occupied
        yy,xx=np.nonzero(missing);sy,sx=np.nonzero(assigned>0)
        if len(xx) and len(sx):
            step=max(1,len(sx)//250000);tree=cKDTree(xyz((sx[::step]+.5)/W*360-180,90-(sy[::step]+.5)/H*180))
            d,j=tree.query(xyz((xx+.5)/W*360-180,90-(yy+.5)/H*180));near=d*6371.0088<80
            assigned[yy[near],xx[near]]=assigned[sy[::step][j[near]],sx[::step][j[near]]]
        changed=assigned>0;states[changed]=assigned[changed]
        audit.append({'country':tag,'rule':'Explicit source administrative unions'});print('REGROUPED',tag,flush=True)
    def merge_country(tag,name):
        states[owners==world['countries'][tag]['index']]=identity(tag,name)
    # Exact user-numbered transfers are resolved BEFORE province numbering changes.
    move_provinces('CHI','Hebei',[27],'CHI','Beijing')
    move_provinces('EGY','Sinai',[19],'EGY','Red Sea Coast')
    move_provinces('SPR','Castile and León',[14],'SPR','Basque Country')
    move_provinces('SOV','Lower Amur',[14,37,3,38],'SOV','Okhotsk Krai')
    move_provinces('FIN','Åland',[2,5],'SWE','Stockholms Län')
    merge_country('PMR','Transnistria');merge_country('SOL','Solomon Islands')
    cornwall=find('ENG','Cornwall');devon=find('ENG','Devon');states[states==devon]=cornwall
    # Five coherent Austrian regions, using complete native province footprints.
    aus=mapping({'Western Austria':'Tyrol|Vorarlberg','Salzburg and Upper Austria':'Salzburg|Upper Austria',
      'Lower Austria and Vienna':'Lower Austria|Vienna','Styria and Burgenland':'Styria|Burgenland','Carinthia':'Carinthia'})
    regroup('AUS','Austria',lambda p:aus.get(p.get('name_en') or p.get('name')))
    # Genuine Croatian disputed boundaries stay separate from mainland regions.
    cro=mapping({'Adriatic Croatia':'Istria|Primorje-Gorski|Lika-Senj|Zadar|Šibenik-Knin|Split-Dalmatia|Dubrovnik-Neretva',
      'Northern Croatia':'Zagreb|Karlovac|Sisak-Moslavina|Krapina-Zagorje|Varaždin|Međimurje|Koprivnica-Križevci|Bjelovar-Bilogora',
      'Slavonia':'Virovitica-Podravina|Požega-Slavonia|Brod-Posavina|Osijek-Baranja|Vukovar-Syrmia'})
    regroup('CRO','Croatia',lambda p:cro.get(p.get('name_en') or p.get('name')))
    for sid in [248,249]:states[oldstates==sid]=sid
    urg_n={'Artigas','Salto','Paysandú','Rivera','Tacuarembó','Cerro Largo','Treinta y Tres'}
    regroup('URG','Uruguay',lambda p:'Northern Uruguay' if (p.get('name_en') or p.get('name')) in urg_n else 'Southern Uruguay')
    for sid,s in list(records.items()):
        if s['owner']=='URG' and s['name'] in ['Brazilian Island','Corner of Artigas']:states[states==int(sid)]=identity('URG','Northern Uruguay')
    west={'Zulia','Tachira','Merida','Trujillo','Falcón','Lara','Yaracuy'}
    east={'Anzoátegui','Sucre','Monagas','Delta Amacuro'}
    def venezuela(p):
        n=p.get('name_en') or p.get('name')
        if n in ['Bolívar','Amazonas']:return n
        if n in ['Nueva Esparta','Federal Dependencies'] or n is None:return 'Caribbean Islands'
        return 'Western Venezuela' if n in west else 'Eastern Venezuela' if n in east else 'Central Venezuela'
    regroup('VEN','Venezuela',venezuela)
    states[oldstates==1371]=identity('VEN','Caribbean Islands')
    westgeo={'Abkhazia','Samegrelo-Zemo Svaneti','Racha-Lechkhumi and Kvemo Svaneti','Adjara','Guria','Imereti'}
    regroup('GEO','Georgia',lambda p:'Western Georgia' if (p.get('name_en') or p.get('name')) in westgeo else 'Eastern Georgia')
    def philippines(p):
        n=p.get('name_en') or p.get('name');r=p.get('region') or ''
        if n=='Spratly Islands':return 'Spratly Islands'
        if any(x in r for x in ['Ilocos','Cordillera','Cagayan Valley']):return 'Northern Luzon'
        if any(x in r for x in ['Central Luzon','National Capital']):return 'Central Luzon'
        if any(x in r for x in ['CALABARZON','Bicol']):return 'Southern Luzon'
        if 'MIMAROPA' in r:return 'Mimaropa'
        if 'Eastern Visayas' in r:return 'Eastern Visayas'
        if 'Visayas' in r:return 'Western Visayas'
        if any(x in r for x in ['Zamboanga','Muslim Mindanao']):return 'Western Mindanao'
        if any(x in r for x in ['Northern Mindanao','XIII']):return 'Northern Mindanao'
        return 'Southern Mindanao'
    regroup('PHI','Philippines',philippines)
    for sid,s in list(records.items()):
        if s['owner']=='PHI' and ('Spratly' in s['name'] or (s['name'].startswith('Palawan') and s['area_km2']<500)):
            states[states==int(sid)]=identity('PHI','Spratly Islands',protected='B46')
    # Syria uses eight broader geographic regions plus the protected UNDOF zone.
    syr=mapping({'Northern Syria':'Aleppo|Idlib','Syrian Coast':'Latakia|Tartus',
      'Central Syria':'Hama|Homs','Damascus':'Damascus|Rif Dimashq',
      'Southern Syria':'Daraa|As-Suwayda|Quneitra|Western al-Samadania',
      'Raqqa':'Al-Raqqah','Deir ez-Zor':'Deir ez-Zor','Jazira':'Al-Hasakah'})
    regroup('SYR','Syria',lambda p:syr.get(p.get('name_en') or p.get('name')))
    for s in oldw['regions'].values():
        if s['owner']=='SYR' and s['name']=='UNDOF Zone':states[oldstates==s['id']]=s['id']
    # Selectively replace the Indonesian mega-states around the requested areas.
    kalimantan={'Central Kalimantan','East Kalimantan','West Kalimantan','South Kalimantan'}
    regroup('IND','Indonesia',lambda p:(p.get('name_en') or p.get('name')) if (p.get('name_en') or p.get('name')) in kalimantan else None,
      restriction=(oldstates==488))
    central=identity('IND','Central Kalimantan');yy,xx=np.nonzero(states==central)
    if len(xx):
        cc=partition(yy,xx,3,[(111.62,-2.69),(113.92,-2.21),(114.9,-.94)])
        for i,n in enumerate(['Western Central Kalimantan','Central Kalimantan','Eastern Central Kalimantan'],1):states[yy[cc==i],xx[cc==i]]=identity('IND',n)
    sumatra={'North Sumatra','Riau Islands'}
    regroup('IND','Indonesia',lambda p:(p.get('name_en') or p.get('name')) if (p.get('name_en') or p.get('name')) in sumatra else None,
      restriction=(oldstates==486))
    northsum=identity('IND','North Sumatra');yy,xx=np.nonzero(states==northsum)
    if len(xx):
        cc=partition(yy,xx,2,[(98.68,3.6),(99.27,1.38)])
        for i,n in enumerate(['Northern Sumatra','Toba and Southern North Sumatra'],1):states[yy[cc==i],xx[cc==i]]=identity('IND',n)
    records['486']['name']='Central Sumatra'
    # Any residual Borneo coastline joins a native Kalimantan group locally;
    # remaining Java parts of the old mega-state keep their proper Java label.
    records['488']['name']='Java Coast'
    # Kashmir: broad overlapping claim polygons must not generate separate
    # sliver states. Consolidate by actual controller and meaningful territory.
    for sid,s in list(oldw['regions'].items()):
        if s['owner']=='PAK' and ('Gilgit' in s['name'] or 'Azad Kashmir' in s['name']):
            name='Azad Kashmir' if 'Azad Kashmir' in s['name'] else 'Gilgit-Baltistan'
            states[oldstates==int(sid)]=identity('PAK',name,protected='B09' if name=='Azad Kashmir' else 'B08')
        if s['owner']=='RAJ' and ('Ladakh' in s['name'] or 'Kashmir' in s['name']):
            if 'Siachen' in s['name']:name='Siachen Glacier'
            elif 'Punjab' in s['name']:name='Punjab'
            elif 'Himachal' in s['name']:name='Himachal Pradesh'
            else:name='Ladakh' if 'Ladakh' in s['name'] or s['name'].startswith('Kashmir') else 'Jammu and Kashmir'
            target=identity('RAJ',name,protected='B45' if name=='Siachen Glacier' else 'B05')
            if name=='Punjab':target=find('RAJ','Punjab — South')
            if name=='Himachal Pradesh':target=find('RAJ','Himachal Pradesh — South')
            states[oldstates==int(sid)]=target
        if s['owner']=='CHI' and ('Aksai Chin' in s['name'] or 'Jammu and Kashmir' in s['name']):
            states[oldstates==int(sid)]=identity('CHI','Aksai Chin',protected='B07')
    # The China-owned Ladakh fragment at 77.35E/32.97N is isolated in Indian
    # Ladakh and outside the Aksai Chin/Shaksgam footprints: correct this artifact.
    states[oldstates==215]=identity('RAJ','Ladakh',protected='B05');owners[oldstates==215]=world['countries']['RAJ']['index']
    # Reconcile the regional controller mask with Natural Earth's map-unit
    # lines. The older registered MD mask puts an additional 17,000 km2 of
    # Chinese-labelled territory inside source Indian Ladakh. This affects
    # the geographic control footprint only; all claim identities are retained.
    x0,x1=int((72+180)/360*W),int((81+180)/360*W)+1
    y0,y1=int((90-37.5)/180*H),int((90-31)/180*H)+1
    transform=from_bounds(x0/W*360-180,90-y1/H*180,x1/W*360-180,90-y0/H*180,x1-x0,y1-y0)
    region_shapes=[(f['geometry'],1) for f in disputes if f['properties']['BRK_A3'] in ['B05','B06','B07','B08','B09','B45']]
    regional=rasterize(region_shapes,out_shape=(y1-y0,x1-x0),transform=transform,dtype='uint8')>0
    units=read(SRC/'natural_earth_map_units.geojson')['features'];tags={'IND':'RAJ','PAK':'PAK','CHN':'CHI'}
    src_control=rasterize([(f['geometry'],world['countries'][tags[f['properties']['ADM0_A3']]]['index']) for f in units if f['properties'].get('ADM0_A3') in tags],out_shape=regional.shape,transform=transform,dtype='uint16')
    native=rasterize([(f['geometry'],i+1) for i,f in enumerate(features) if f['properties'].get('admin') in ['India','Pakistan','China']],out_shape=regional.shape,transform=transform,dtype='uint16')
    view=states[y0:y1,x0:x1];oldown=owners[y0:y1,x0:x1]
    accepted=regional&np.isin(oldown,[world['countries'][t]['index'] for t in ['RAJ','PAK','CHI']])&(src_control>0)
    for ci,tag in [(world['countries'][t]['index'],t) for t in ['RAJ','PAK','CHI']]:
        my=accepted&(src_control==ci)
        for aid in np.unique(native[my]):
            m=my&(native==aid)
            if not m.any():continue
            pp=features[int(aid)-1]['properties'] if aid else {};n=pp.get('name_en') or pp.get('name') or ''
            if tag=='RAJ':
                if n in ['Punjab','Himachal Pradesh']:
                    sid=find('RAJ',n+' — South')
                else:sid=identity('RAJ','Jammu and Kashmir' if n=='Jammu and Kashmir' else 'Ladakh',protected='B05')
            elif tag=='PAK':sid=identity('PAK','Azad Kashmir' if n=='Azad Kashmir' else 'Gilgit-Baltistan',protected='B09' if n=='Azad Kashmir' else 'B08')
            else:sid=identity('CHI','Aksai Chin',protected='B07')
            view[m]=sid;oldown[m]=ci
    # Keep Siachen and Shaksgam independent of the broad regional claim.
    for f in disputes:
        code=f['properties']['BRK_A3']
        if code not in ['B06','B45']:continue
        q=rasterize([(f['geometry'],1)],out_shape=(H,W),transform=from_bounds(-180,-90,180,90,W,H),dtype='uint8')
        tag='CHI' if code=='B06' else 'RAJ';m=(q>0)&(owners==world['countries'][tag]['index'])
        states[m]=identity(tag,'Shaksgam Valley' if code=='B06' else 'Siachen Glacier',protected=code)
    for sid,s in oldw['regions'].items():
        if s['owner']=='CHI' and s['name']=='Shaksam Valley':states[oldstates==int(sid)]=identity('CHI','Shaksgam Valley',protected='B06')
    # Kuril membership follows island locations, not the Sakhalin ADM1 label.
    records['1086']['name']='South Kuril Islands'
    for p in oldps.values():
        if p['region']!=1037:continue
        u,v=p['map_center'];lon,lat=u*360-180,90-v*180
        if lon>145:
            sid=1086 if lat<45.7 and lon<149.5 else identity('SOV','North Kuril Islands')
            states[oldprov==p['id']]=sid
    records[str(find('SOV','Okhotsk Krai'))]['name']='Okhotsk Kraj'
    # Additional Amur subdivision gives the Stanovoy/northern portion its own
    # geography; this remains a terrain-guided gameplay division, not a treaty map.
    amur=find('SOV','Amur');yy,xx=np.nonzero(states==amur)
    cc=partition(yy,xx,2,[(124.73,55.15),(127.54,50.29)])
    states[yy[cc==1],xx[cc==1]]=identity('SOV','Stanovoy')
    # Niue was also being used as a label for the Chatham/Antipodes group.
    records['749']['name']='Chatham and Antipodes Islands'
    # Source coastline gaps must not survive as tiny old-label states after
    # their mainland/archipelago has been regrouped. Attach each remnant to
    # the nearest actual same-country regional footprint, across the sphere.
    for oldsid in [820,821,488]:
        yy,xx=np.nonzero(states==oldsid)
        if not len(xx):continue
        tag=records[str(oldsid)]['owner'];my=owners==world['countries'][tag]['index']
        sy,sx=np.nonzero(my&(states!=oldsid));step=max(1,len(sx)//500000)
        tree=cKDTree(xyz((sx[::step]+.5)/W*360-180,90-(sy[::step]+.5)/H*180))
        _,j=tree.query(xyz((xx+.5)/W*360-180,90-(yy+.5)/H*180))
        states[yy,xx]=states[sy[::step][j],sx[::step][j]]
    # Compact the record set and refresh accounts from the actual state atlas.
    active=set(map(int,np.unique(states)))-{0,8191};records={k:s for k,s in records.items() if int(k) in active}

    # Recompute all retained records and transfer actual overlapping accounts.
    old_to_new=defaultdict(Counter);overlap=defaultdict(Counter)
    for top in range(0,H,128):
        a=states[top:top+128];b=oldstates[top:top+128];m=(a>0)&(a<8191)
        keys,n=np.unique(a[m].astype(np.uint32)*8192+b[m],return_counts=True)
        for k,q in zip(keys,n):
            sid,oid=divmod(int(k),8192);old_to_new[oid][sid]+=int(q);overlap[sid][oid]+=int(q)
    boxes=find_objects(states,max_label=nextid)
    for k,s in records.items():
        sid=int(k);bb=boxes[sid-1];yy,xx=np.nonzero(states[bb]==sid);yy+=bb[0].start;xx+=bb[1].start
        s.update(population=0,buildings={},provinces=[],map_center=focus(yy,xx),area_km2=round(float(AREA[yy].sum()),2))
        oldids=list(overlap[sid]);total=sum(overlap[sid].values());rights=[i for i in oldids if overlap[sid][i]>=total*.05]
        s['source_states']=sorted({j for i in oldids for j in oldw['regions'][str(i)]['source_states']})
        s['cores']=sorted({t for i in rights for t in oldw['regions'][str(i)]['cores']}|{s['owner']})
        s['claims']=sorted({t for i in rights for t in oldw['regions'][str(i)]['claims']})
    for oid,targets in old_to_new.items():
        old=oldw['regions'][str(oid)];ids=sorted(targets);weights=[targets[i] for i in ids]
        for sid,n in zip(ids,alloc(old['population'],weights)):records[str(sid)]['population']+=int(n)
        for building,total in old['buildings'].items():
            for sid,n in zip(ids,alloc(total,weights)):
                if n:records[str(sid)]['buildings'][building]=records[str(sid)]['buildings'].get(building,0)+int(n)
    # Distinguish real repeated administrative names without arbitrary numbering.
    dup=defaultdict(list)
    for s in records.values():dup[(s['owner'],s['name'])].append(s)
    for (tag,name),items in dup.items():
        if len(items)<2:continue
        for s in items:
            if s.get('protected_territory'):suffix=s.get('protected_territory_name') or 'Protected Area'
            elif s['area_km2']<100:suffix='Coastal Islands'
            else:suffix='North' if s['map_center'][1]<np.mean([x['map_center'][1] for x in items]) else 'South'
            s['name']=name+' — '+suffix
    # Split only provinces crossed by a corrected state line. An original
    # province ID remains with its largest piece; added pieces receive new IDs.
    pieces=defaultdict(Counter)
    for top in range(0,H,128):
        a=states[top:top+128];p=oldprov[top:top+128];m=p>0
        keys,n=np.unique(p[m].astype(np.uint32)*8192+a[m],return_counts=True)
        for k,q in zip(keys,n):pid,sid=divmod(int(k),8192);pieces[pid][sid]+=int(q)
    ids={};ps={};nextpid=max(map(int,oldps))+1
    for pid,parts in sorted(pieces.items()):
        dominant=max(parts,key=parts.get)
        for sid in sorted(parts):
            q=pid if sid==dominant else nextpid
            if sid!=dominant:nextpid+=1
            ids[(pid,sid)]=q;record=copy.deepcopy(oldps[str(pid)]);record.update(id=q,region=sid,neighbors=[],cities=[],urban_group='')
            if q!=pid:record['buildings']={}
            ps[str(q)]=record
    original_province={newpid:oldpid for (oldpid,sid),newpid in ids.items()}
    # Reconstruct categorical provinces without allocating a giant dense LUT.
    province=np.zeros_like(oldprov)
    code_keys=np.array(sorted(pid*8192+sid for pid,sid in ids),np.uint32)
    code_values=np.array([ids[divmod(int(k),8192)] for k in code_keys],np.uint16)
    for top in range(0,H,128):
        a=states[top:top+128];p=oldprov[top:top+128];m=p>0;code=p[m].astype(np.uint32)*8192+a[m]
        province[top:top+128][m]=code_values[np.searchsorted(code_keys,code)]
    del oldprov,oldstates,owners
    boxes=find_objects(province,max_label=nextpid)
    for k,p in ps.items():
        bb=boxes[int(k)-1];yy,xx=np.nonzero(province[bb]==int(k));yy+=bb[0].start;xx+=bb[1].start
        p.update(map_center=focus(yy,xx),area_km2=round(float(AREA[yy].sum()),2),geometry_source='Accepted terrain-guided province, intersected with authored geographic state boundaries')
        records[str(p['region'])]['provinces'].append(int(k))
    for s in records.values():
        for j,pid in enumerate(sorted(s['provinces']),1):ps[str(pid)]['local_index']=j
    # Additional density is local to the reported oversized provinces.
    density_splits=[]
    boxes=find_objects(province,max_label=nextpid)
    for key,p in list(ps.items()):
        state=records[str(p['region'])];name=state['name'];tag=state['owner'];target=None
        if p['region']==5:target=6500
        if tag=='SYR':target=2400
        if tag=='UKR' and any(n in name for n in ['Donetsk','Luhansk']) and state['area_km2']>500:target=1300
        elif tag=='UKR' and name in ['Kharkiv','Zaporizhzhia','Dnipropetrovsk']:target=2500
        if target is None or p['area_km2']<=target*1.35:continue
        count=int(math.ceil(p['area_km2']/target));bb=boxes[int(key)-1]
        yy,xx=np.nonzero(province[bb]==int(key));yy+=bb[0].start;xx+=bb[1].start
        cc=partition(yy,xx,count);major=int(np.bincount(cc).argmax());created=[]
        for code in np.unique(cc):
            pid=int(key) if code==major else nextpid
            if code!=major:
                nextpid+=1;ps[str(pid)]=copy.deepcopy(p);ps[str(pid)].update(id=pid,neighbors=[],cities=[],buildings={})
                original_province[pid]=original_province[int(key)];records[str(p['region'])]['provinces'].append(pid)
            sel=cc==code;y,x=yy[sel],xx[sel];province[y,x]=pid
            ps[str(pid)].update(map_center=focus(y,x),area_km2=round(float(AREA[y].sum()),2));created.append(pid)
        density_splits.append({'old_province':int(key),'state':p['region'],'new_provinces':created})
    for state in records.values():
        for j,pid in enumerate(sorted(state['provinces']),1):ps[str(pid)]['local_index']=j
    # Adjacencies come from the actual final categorical atlas.
    edges=Counter()
    for top in range(0,H,128):
        for l,r in [(province[top:top+128,:-1],province[top:top+128,1:]),(province[top:min(H-1,top+128)],province[top+1:min(H,top+129)])]:
            m=(l>0)&(r>0)&(l!=r)
            codes=np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m])
            keys,counts=np.unique(codes,return_counts=True)
            edges.update({int(k):int(n) for k,n in zip(keys,counts)})
    l,r=province[:,0],province[:,-1];m=(l>0)&(r>0)&(l!=r)
    edges.update(int(min(a,b))*65536+int(max(a,b)) for a,b in zip(l[m],r[m]))
    # Intersecting two valid atlases creates tiny boundary shards. Absorb only
    # those NEW shards into an adjacent province of the same corrected state.
    # Original provinces (and the five requested Karelia IDs) stay identifiable.
    aliases={int(k):int(k) for k in ps}
    def root(pid):
        while aliases[pid]!=pid:aliases[pid]=aliases[aliases[pid]];pid=aliases[pid]
        return pid
    absorbed=[]
    density_protected={pid for q in density_splits for pid in q['new_provinces']}
    for pid in sorted((int(k) for k in ps if int(k)>max(map(int,oldps))),key=lambda i:ps[str(i)]['area_km2']):
        if pid in density_protected:continue
        p=ps[str(pid)];original=oldps[str(original_province[pid])]
        if p['area_km2']>=min(1000,max(25,original['area_km2']*.3)):continue
        candidates=Counter()
        for code,n in edges.items():
            a,b=map(root,divmod(code,65536))
            if a==b or pid not in [a,b]:continue
            other=b if a==pid else a
            if ps[str(other)]['region']==p['region']:candidates[other]+=n
        if candidates:
            target=max(candidates,key=lambda i:(candidates[i],ps[str(i)]['area_km2']))
            aliases[pid]=target;absorbed.append(pid)
    if absorbed:
        lut=np.zeros(nextpid+1,np.uint16)
        for pid in aliases:lut[pid]=root(pid)
        for top in range(0,H,128):province[top:top+128]=lut[province[top:top+128]]
        for pid in absorbed:ps.pop(str(pid))
        for s in records.values():s['provinces']=[]
        boxes=find_objects(province,max_label=nextpid)
        for k,p in ps.items():
            bb=boxes[int(k)-1];yy,xx=np.nonzero(province[bb]==int(k));yy+=bb[0].start;xx+=bb[1].start
            p.update(map_center=focus(yy,xx),area_km2=round(float(AREA[yy].sum()),2))
            records[str(p['region'])]['provinces'].append(int(k))
        for s in records.values():
            for j,pid in enumerate(sorted(s['provinces']),1):ps[str(pid)]['local_index']=j
    # A state intersection can separate two pieces of an existing province
    # on the SAME landmass. Keep genuine island groups, but reassign small
    # disconnected mainland pieces locally or give substantial pieces an ID.
    stateboxes=find_objects(states,max_label=8191);connectivity_pixels=0;connectivity_splits=0
    for key,s in records.items():
        bb=stateboxes[int(key)-1];sm=states[bb]==int(key);view=province[bb]
        land,_=label(sm,np.ones((3,3),bool))
        for pid in list(s['provinces']):
            parts,n=label(view==pid,np.ones((3,3),bool))
            if n<2:continue
            sizes=np.bincount(parts.ravel());partboxes=find_objects(parts);byland={};partland={}
            for j,pb in enumerate(partboxes,1):
                if pb is None:continue
                yy,xx=np.nonzero(parts[pb]==j);component=int(land[yy[0]+pb[0].start,xx[0]+pb[1].start]);partland[j]=component
                if component not in byland or sizes[j]>sizes[byland[component]]:byland[component]=j
            for j,component in partland.items():
                if byland[component]==j:continue
                piece=parts==j;around=binary_dilation(piece,np.ones((3,3),bool))&sm&~piece
                neighbors=view[around];neighbors=neighbors[(neighbors>0)&(neighbors!=pid)]
                if sizes[j]<=500 and len(neighbors):
                    target=int(np.bincount(neighbors).argmax());view[piece]=target;connectivity_pixels+=int(sizes[j])
                else:
                    newpid=nextpid;nextpid+=1;view[piece]=newpid
                    ps[str(newpid)]=copy.deepcopy(ps[str(pid)]);ps[str(newpid)].update(id=newpid,neighbors=[],cities=[],buildings={})
                    original_province[newpid]=original_province[pid];s['provinces'].append(newpid);connectivity_splits+=1
    used=set(map(int,np.unique(province)))-{0};ps={k:q for k,q in ps.items() if int(k) in used}
    for s in records.values():s['provinces']=[]
    boxes=find_objects(province,max_label=nextpid)
    for k,q in ps.items():
        bb=boxes[int(k)-1];yy,xx=np.nonzero(province[bb]==int(k));yy+=bb[0].start;xx+=bb[1].start
        q.update(map_center=focus(yy,xx),area_km2=round(float(AREA[yy].sum()),2),neighbors=[])
        records[str(q['region'])]['provinces'].append(int(k))
    for s in records.values():
        for j,pid in enumerate(sorted(s['provinces']),1):ps[str(pid)]['local_index']=j
    final_edges=set()
    for top in range(0,H,128):
        for l,r in [(province[top:top+128,:-1],province[top:top+128,1:]),(province[top:min(H-1,top+128)],province[top+1:min(H,top+129)])]:
            m=(l>0)&(r>0)&(l!=r);codes=np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m])
            final_edges.update(divmod(int(c),65536) for c in np.unique(codes))
    l,r=province[:,0],province[:,-1];m=(l>0)&(r>0)&(l!=r)
    final_edges.update(tuple(sorted([int(a),int(b)])) for a,b in zip(l[m],r[m]))
    for a,b in final_edges:ps[str(a)]['neighbors'].append(b);ps[str(b)]['neighbors'].append(a)
    for p in ps.values():p['neighbors'].sort()
    # Relink cities/scenery using their coordinates and controller, retaining
    # their existing urban-group identities and unchanged visual positions.
    cities=read(BASE/'data/cities.json');scene=read(BASE/'data/urban_scenery.json');oldurban=read(BASE/'data/urban_population.json')
    def locate(lon,lat,tag=None):
        x=int((lon+180)/360*W)%W;y=min(H-1,max(0,int((90-lat)/180*H)));pid=int(province[y,x])
        if pid and ({tag,records[str(ps[str(pid)]['region'])]['owner']} <= {'CHI','RAJ','PAK'} or {tag,records[str(ps[str(pid)]['region'])]['owner']}=={'FIN','SWE'}):return pid
        if pid and (not tag or records[str(ps[str(pid)]['region'])]['owner']==tag):return pid
        # Local coastal snapping cannot attach distant cities to an unrelated country.
        for radius in [12,40]:
            yy,xx=np.mgrid[max(0,y-radius):min(H,y+radius+1),max(0,x-radius):min(W,x+radius+1)]
            q=province[yy,xx];valid=q>0
            if tag:
                lut=np.zeros(nextpid+1,bool)
                for k,p in ps.items():lut[int(k)]=records[str(p['region'])]['owner']==tag
                valid&=lut[q]
            if valid.any():
                d=np.where(valid,(yy-y)**2+(xx-x)**2,np.inf);j=np.unravel_index(np.argmin(d),d.shape);return int(q[j])
        return pid
    groups={}
    for c in cities:
        pid=locate(c['longitude'],c['latitude'],c['country'])
        if not pid:raise ValueError(('Unlinked city',c['name']))
        owner=records[str(ps[str(pid)]['region'])]['owner']
        c.update(province_id=pid,country=owner);p=ps[str(pid)];p['cities'].append(c['name'])
        gid=c.get('urban_group') or 'geographic_city_%05d'%pid
        if not p['urban_group']:p['urban_group']=gid
        c['urban_group']=p['urban_group']
    for kind in ['clusters','landmarks']:
        for record in scene[kind]:
            oldp=oldps[str(record['province'])];tag=oldw['regions'][str(oldp['region'])]['owner']
            pid=locate(record['longitude'],record['latitude'],tag)
            if not pid:raise ValueError(('Unlinked scenery',record.get('name')))
            p=ps[str(pid)];record['province']=pid
            if not p['urban_group']:p['urban_group']=record.get('group') or 'geographic_city_%05d'%pid
            record['group']=p['urban_group']
            if kind=='landmarks':record['country']=records[str(p['region'])]['owner']
    for p in ps.values():
        gid=p['urban_group'];p['kind']='city' if gid else 'rural'
        if gid and gid not in groups:
            groups[gid]=copy.deepcopy(oldurban['groups'].get(gid,{'id':gid,'name':p['cities'][0] if p['cities'] else gid,'cities':[]}))
            groups[gid].update(provinces=[],population_2000=0,settlement_population_2000=0,representative_buildings=0,country_at_start=records[str(p['region'])]['owner'])
        if gid:groups[gid]['provinces'].append(p['id'])
    account={'epoch':2000,'source':{'method':'Retained state totals; existing province population shares partitioned by geographic area only where split.'},'groups':groups,'states':{},'growth_enabled':False,'country_reconciliation_factors':{},'population_scope':'Geometry bookkeeping; demographic estimates not revised.'}
    for k,s in records.items():
        pp=s['provinces'];weights=[]
        for pid in pp:
            p=ps[str(pid)]
            original=oldps.get(str(pid))
            if original is None:
                original=oldps[str(original_province[pid])]
            weights.append(original.get('population_2000',0)*p['area_km2']/max(original.get('area_km2',0),.001))
        if not sum(weights):weights=[ps[str(pid)]['area_km2'] for pid in pp]
        for pid,n in zip(pp,alloc(s['population'],weights)):ps[str(pid)]['population_2000']=int(n)
        urban=[pid for pid in pp if ps[str(pid)]['urban_group']];shared=[pid for pid in pp if pid not in urban]
        urbanpop=sum(ps[str(pid)]['population_2000'] for pid in urban)
        account['states'][k]={'state':int(k),'population_2000':s['population'],'urban_provinces':urban,'shared_provinces':shared,'urban_population_2000':urbanpop,'shared_population_2000':s['population']-urbanpop,'raw_grid_population':0,'state_reconciliation_factor':1,'fallback_area_allocation':False}
    for p in ps.values():
        if p['urban_group']:groups[p['urban_group']]['population_2000']+=p['population_2000']
    for g in groups.values():g['settlement_population_2000']=g['population_2000'];g['provinces'].sort()
    for c in cities:c['population_2000']=ps[str(c['province_id'])]['population_2000']
    for r in scene['clusters']:
        if r['group'] in groups:groups[r['group']]['representative_buildings']+=len(r['instances'])
    micro=read(BASE/'data/microstate_geometry.json')
    records[str(micro['state'])].update(name='Vatican City',map_center=micro['center_uv'],area_km2=micro['nominal_area_km2'])
    ps[str(micro['province'])].update(map_center=micro['center_uv'],area_km2=micro['nominal_area_km2'])
    world['regions']=records;world['version']=VERSION;world['scenario_id']='bunny_world_2000_0_2_0_9';scene['version']=VERSION
    for tag,c in world['countries'].items():
        ss=[int(k) for k,s in records.items() if s['owner']==tag];c['regions']=sorted(ss)
        if not ss:raise ValueError(('Country lost all states',tag))
        u,v=c['map_center'];at=int(states[min(H-1,int(v*H)),int(u*W)%W])
        if at not in ss:at=max(ss,key=lambda i:records[str(i)]['population'])
        c['capital']=at;c['map_center']=records[str(at)]['map_center']
    world['map'].update(cartography='Authored geographic state unions; mainland, overseas and protected-area allocations independent.',regional_boundary_accuracy='Natural Earth ADM1 and map-unit geography with explicit country corrections; two historical Russian cuts are gameplay approximations.',province_geometry='Existing terrain-guided provinces split only at corrected state boundaries.',urban_population='Retained population totals and province shares; split shares allocated by area; demographic refinement deferred.')
    # Vatican is unchanged; host/province IDs remain stable under this patch.
    micro['host_state']=ps[str(micro['host_province'])]['region']
    for name,obj in [('world',world),('provinces',ps),('cities',cities),('urban_population',account),('urban_scenery',scene),('microstate_geometry',micro)]:write('data/'+name+'.json',obj)
    np.savez_compressed(SRC/'grouped_atlas_022r2.npz',regions=states)
    # Write one complete atlas, then publish byte-identical versioned copies.
    # A cancelled preparation must not leave a partly written versioned ZIP.
    temporary=SRC/'province_atlas_0209.prepare-tmp.npz'
    np.savez_compressed(temporary,provinces=province)
    temporary.replace(SRC/'province_atlas_022r2.npz')
    shutil.copyfile(SRC/'province_atlas_022r2.npz',SRC/'province_atlas_0209.npz')
    index=np.zeros((65536,3),np.uint8)
    for p in ps.values():index[p['id'],:2]=[p['region']&255,p['region']>>8]
    index[65535,:2]=[255,31];atomic_png(index.reshape(256,256,3),ROOT/'assets/province_index.png')
    for i in range(4):
        y,x=i//2*4096,i%2*8192;q=province[y:y+4096,x:x+8192].copy();q[states[y:y+4096,x:x+8192]==8191]=65535
        atomic_png(np.stack([(q&255).astype(np.uint8),(q>>8).astype(np.uint8),np.zeros_like(q,np.uint8)],-1),ROOT/'assets'/f'region_ids_{i}.png')
    report={'version':VERSION,'base_version':'0.2.0.8','states':len(records),'provinces':len(ps),'split_provinces':len(ps)-len(oldps),'boundary_shards_absorbed':len(absorbed),'density_splits':density_splits,'native_connectivity_repairs':{'reassigned_pixels':connectivity_pixels,'new_provinces':connectivity_splits},'countries':audit,'requested_province_transfers':moved,
      'historical_approximations':['Karelian Isthmus uses an authored coarse pre-1940-border guide, clipped to Leningrad.','Northern Khabarovsk uses an authored Uda/Stanovoy transition guide; no archival treaty geometry is asserted.'],
      'controller_corrections':['Natural Earth Somaliland shell assigned to Somaliland rather than Puntland.','Natural Earth South Ossetia shell unified, removing Georgian-sector cartographic enclaves.'],
      'explicit_consolidation_exceptions':['Bhutan','Belize','French Guiana / Lawa Headwaters','Aruba, Curaçao and Bonaire','Comoros','Isles of Scilly into Cornwall','US Virgin Islands'],
      'state_counts':{tag:len(c['regions']) for tag,c in world['countries'].items()}}
    write('data/geography_0209_report.json',report)
    print('GEOGRAPHY_0209_COMPLETE',len(records),len(ps),'REQUESTED_MOVES',moved,flush=True)

def fix_seas():
    """Remove southern Pacific identity artifacts, preserving all land masks."""
    from shapely.geometry import Polygon,mapping as geomapping
    from shapely.affinity import translate
    rgb=np.asarray(Image.open(BASE/'assets/sea_ids.png'),np.uint16)
    sea=rgb[:,:,0]+rgb[:,:,1]*256;before=sea.copy();hh,ww=sea.shape
    lat=90-(np.arange(hh)+.5)/hh*180;lon=(np.arange(ww)+.5)/ww*360-180
    # Micronesian/Solomon identities south of their main tropical footprint
    # were detached registration artifacts in West Polynesia.
    sea[np.isin(sea,[83,97])&(lat[:,None]<-20)]=178
    # Coherent broad Tasman extension replaces the thin Far South Pacific
    # arm by the Chathams and includes Niue's water neighbourhood as requested.
    # Both halves are rasterized together across the date line.
    poly=Polygon([(165,-32),(174,-25),(184,-18),(194,-18),(194,-25),(190,-35),(190,-50),(175,-55),(165,-45),(165,-32)])
    ext=rasterize([(geomapping(poly),1),(geomapping(translate(poly,xoff=-360)),1)],out_shape=sea.shape,
      transform=from_bounds(-180,-90,180,90,ww,hh),dtype='uint8')>0
    sea[ext&(sea>0)]=86
    lo=lon%360
    sea[(sea==112)&(lo[None,:]>170)&(lo[None,:]<194)&(lat[:,None]>-55)]=86
    definitions=read(BASE/'data/sea_regions.json')
    for k,q in definitions.items():
        yy,xx=np.nonzero(sea==int(k))
        if not len(xx):raise ValueError(('Sea identity lost',k))
        step=max(1,len(xx)//100000);v=xyz(lon[xx[::step]],lat[yy[::step]]);j=int(np.argmax(v@v.mean(0)))*step
        q.update(map_center=[(float(xx[j])+.5)/ww,(float(yy[j])+.5)/hh],neighbors=[])
    edges=set()
    for l,r in [(sea[:,:-1],sea[:,1:]),(sea[:-1],sea[1:]),(sea[:,-1:],sea[:,:1])]:
        m=(l>0)&(r>0)&(l!=r)
        codes=np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m]);edges.update(map(int,np.unique(codes)))
    for code in edges:
        a,b=divmod(code,65536);definitions[str(a)]['neighbors'].append(b);definitions[str(b)]['neighbors'].append(a)
    for q in definitions.values():q['neighbors'].sort()
    atomic_png(np.stack([(sea&255).astype(np.uint8),(sea>>8).astype(np.uint8),np.zeros_like(sea,np.uint8)],-1),ROOT/'assets/sea_ids.png')
    write('data/sea_regions.json',definitions)
    report=read(ROOT/'data/geography_0209_report.json');report['sea_pixels_reassigned']=int(np.count_nonzero(sea!=before))
    report['niue_label_correction']='The old Niue state at the Chatham/Antipodes footprint is renamed Chatham and Antipodes Islands. Tasman waters are extended coherently across the date line, including Niue neighbourhood.'
    report['controller_corrections']=['Kashmir/Ladakh registration artifacts aligned with Natural Earth map-unit controller footprints.','User-requested Åland provinces 2 and 5 transferred to Stockholm, Sweden.']
    report['historical_approximations'].append('New Stanovoy/Amur division follows terrain-guided geographic grouping; not an archival Manchurian treaty border.')
    write('data/geography_0209_report.json',report)
    print('SEA_0209_COMPLETE',report['sea_pixels_reassigned'],'pixels reassigned',flush=True)

if __name__=='__main__':
    main()
    fix_seas()

