"""Offline 0.1.9 country-border repair, equal-area gameplay cells and ocean-only zones.
Uses bundled geographic inputs; preserves scenario state populations/rights.
"""
from pathlib import Path
import collections,json,math,unicodedata
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import find_objects,distance_transform_edt,label
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography';W,H=16384,8192
Image.MAX_IMAGE_PIXELS=None
TARGET=10000.;KM=40075.017/W

def norm(s):return ''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if c.isalnum() and not unicodedata.combining(c))
def paint(draw,geo,value):
    for poly in geo['coordinates'] if geo['type']=='MultiPolygon' else [geo['coordinates']]:
        draw.polygon([((x+180)/360*W,(90-y)/180*H) for x,y,*_ in poly[0]],fill=value)
        # Country/subdivision holes retain the existing scenario land/control.

def repair(a,w):
    names={norm(c['name']):t for t,c in w['countries'].items()}
    aliases={'United States of America':'USA','Russia':'SOV','South Korea':'KOR','North Korea':'NKO','Taiwan':'TAI','Bosnia and Herzegovina':'BOS','Democratic Republic of the Congo':'DRC','Republic of the Congo':'CNG','Czechia':'CZE','eSwatini':'SWA','Cape Verde':'VER','East Timor':'IND','Timor-Leste':'IND','Western Sahara':'SHA','Somaliland':'SML'}
    names.update({norm(k):v for k,v in aliases.items()})
    # Infer the remaining country aliases from immutable native subdivision codes.
    seed=json.load(open(SRC/'world_seed_016.json'));votes=collections.defaultdict(collections.Counter)
    for r in seed['regions'].values():votes[r['geographic_code'].split('-')[0]][r['owner']]+=1
    guests={'TAL','ACE','KAC','KAR','WAA','SHN','KUR','PUK','IEK','TML','NPM','CHE','ABK','SOO','NKR','PMR','SML','PUN','SNA','JUB','AIA','SWS','MLC','RCD','UNI','AFR','LUR','HEZ','HAM','SSU'}
    canvas=Image.new('I',(W,H));draw=ImageDraw.Draw(canvas);features=json.load(open(SRC/'geographic_subdivisions.geojson'))['features']
    for f in features:
        p=f['properties'];tag=names.get(norm(p.get('admin','')))
        if not tag:
            candidates=votes[p['adm1_code'].split('-')[0]];tag=next((t for t,_ in candidates.most_common() if t not in guests),None)
        if tag in w['countries'] and tag not in guests:paint(draw,f['geometry'],w['countries'][tag]['index'])
    expected=np.asarray(canvas,np.uint16);del canvas,draw
    owner=np.zeros(8192,np.uint16);protected=np.zeros(8192,bool)
    for sid,r in w['regions'].items():
        owner[int(sid)]=w['countries'][r['owner']]['index']
        protected[int(sid)]=r['owner'] in guests or r['owner']=='UKR' or any(s in [424,488,624,824,827,1241,669,1112] for s in r['source_states']) or 'base' in r['name'].lower() or 'camp' in r['name'].lower()
    wrong=(a>0)&(a<8191)&(expected>0)&(owner[a]!=expected)&(~protected[a])
    corrections={}
    for tag,c in w['countries'].items():
        yy,xx=np.nonzero(wrong&(expected==c['index']))
        if not len(xx):continue
        # Nearest owned state within a bounded local window, never a foreign ID.
        t=max(0,yy.min()-256);b=min(H,yy.max()+257);l=max(0,xx.min()-256);r=min(W,xx.max()+257)
        tile=a[t:b,l:r];valid=owner[tile]==c['index']
        if not valid.any():continue
        near=distance_transform_edt(~valid,return_distances=False,return_indices=True);fill=tile[near[0],near[1]]
        a[yy,xx]=fill[yy-t,xx-l];corrections[tag]=len(xx)
    # No state may disappear; data identity and conservation remain intact.
    missing=set(map(int,w['regions']))-set(np.unique(a))
    if missing:
        original=np.load(SRC/'grouped_atlas_017.npz')['regions']
        for rid in missing:
            a[original==rid]=rid
        print('PRESERVED_SCENARIO_FOOTPRINTS',[(rid,w['regions'][str(rid)]['name']) for rid in sorted(missing)],flush=True)
        del original
    assert set(map(int,w['regions']))<=set(np.unique(a))
    del expected,wrong
    fade_owner=owner[a[::4,::4]];edge=(fade_owner!=np.roll(fade_owner,1,1))|(fade_owner!=np.roll(fade_owner,-1,1))|(fade_owner!=np.roll(fade_owner,1,0))|(fade_owner!=np.roll(fade_owner,-1,0))
    fade=np.exp(-distance_transform_edt(~edge)*9.78/220)*255;fade[fade_owner==0]=0;Image.fromarray(fade.astype(np.uint8)).save(ROOT/'assets/border_fade.png')
    print('COUNTRY_REPAIR',corrections,flush=True);return corrections

def provinces(a,w):
    cities=json.load(open(ROOT/'data/cities.json'));by_state=collections.defaultdict(list)
    for city in cities:
        x=int((city['longitude']+180)/360*W)%W;y=min(H-1,int((90-city['latitude'])/180*H));rid=int(a[y,x])
        # Coastal city coordinates may be just off the high-detail shoreline.
        if not 0<rid<8191:
            t=max(0,y-4);b=min(H,y+5);cols=np.arange(x-4,x+5)%W;tile=a[t:b][:,cols];valid=(tile>0)&(tile<8191)
            yy,xx=np.nonzero(valid)
            if not len(xx):continue
            j=np.argmin((yy+t-y)**2+(cols[xx]-x)**2);y=int(yy[j]+t);x=int(cols[xx[j]]);rid=int(a[y,x])
        if w['regions'][str(rid)]['owner']!=city.get('country'):continue
        by_state[rid].append((city,x,y))
    boxes=find_objects(a,max_label=8191);pmap=np.zeros_like(a);ps={};urban=0;merged=[];caps=[];areaweights=np.cos((np.arange(H)+.5)/H*math.pi-math.pi/2)*KM*KM
    for sid,r in w['regions'].items():
        rid=int(sid);bb=boxes[rid-1];yy,xx=np.nonzero(a[bb]==rid);yy+=bb[0].start;xx+=bb[1].start
        unwrap=xx.astype(float);cross=xx.max()-xx.min()>W//2
        if cross:unwrap[unwrap<W//2]+=W
        scale=max(.015,math.cos((yy.mean()+.5)/H*math.pi-math.pi/2));coords=np.column_stack([unwrap*scale,yy]);tree=cKDTree(coords)
        which=np.full(len(xx),-1,np.int32);records=[];city_centers=[];city_coords=[]
        for city,x,y in by_state[rid]:
            if cross and x<W//2:x+=W
            _,idx=tree.query([x*scale,y]);point=coords[idx]
            if any(np.linalg.norm(point-q)<1.5 for q in city_coords):merged.append(city['name']);continue
            city_coords.append(point);city_centers.append(int(idx));records.append({'kind':'city','name':city['name'],'cities':[city['name']],'population_rank':city.get('population_rank',0)})
        if city_coords:
            city_coords=np.array(city_coords);dist,ci=cKDTree(city_coords).query(coords)
            radii=np.array([max(8.,min(24.,8.+math.sqrt(max(0,float(rec['population_rank'])))/600.)) for rec in records])/KM
            mask=dist<=radii[ci];which[mask]=ci[mask]
            for i,idx in enumerate(city_centers):which[idx]=i
        rural=np.flatnonzero(which<0);city_count=len(records)
        if len(rural):
            area=float(areaweights[yy[rural]].sum());n=max(1,int(round(area/TARGET)));n=min(n,len(rural),255-city_count)
            if city_count+n>=255:caps.append(r['name'])
            points=coords[rural];sample=points[::max(1,len(points)//12000)]
            first=np.argmin(np.sum((sample-sample.mean(0))**2,axis=1));seeds=[sample[first]];d=np.sum((sample-seeds[0])**2,axis=1)
            for _ in range(1,n):
                j=np.argmax(d);seeds.append(sample[j]);d=np.minimum(d,np.sum((sample-sample[j])**2,axis=1))
            seeds=np.array(seeds);localtree=cKDTree(points)
            # Weighted Lloyd relaxation: the same geographic-area density worldwide.
            weights=areaweights[yy[rural]]
            for _ in range(4):
                _,cell=cKDTree(seeds).query(points);counts=np.bincount(cell,weights=weights,minlength=n)
                center=np.column_stack([np.bincount(cell,weights=points[:,j]*weights,minlength=n)/np.maximum(counts,1e-12) for j in range(2)])
                _,near=localtree.query(center);seeds=points[near]
            _,cell=cKDTree(seeds).query(points);which[rural]=cell+city_count
            records.extend({'kind':'rural'} for _ in range(n))
        assert len(records)<=255
        r['provinces']=[]
        for i,rec in enumerate(records):
            indexes=np.flatnonzero(which==i)
            if not len(indexes):continue
            pid=len(ps)+1;local=len(r['provinces'])+1;r['provinces'].append(pid);pmap[yy[indexes],xx[indexes]]=pid
            mean=coords[indexes].mean(0);j=indexes[np.argmin(np.sum((coords[indexes]-mean)**2,axis=1))]
            ps[str(pid)]={'id':pid,'region':rid,'local_index':local,'map_center':[(float(xx[j])+.5)/W,(float(yy[j])+.5)/H],'area_km2':round(float(areaweights[yy[indexes]].sum()),2),'neighbors':[],'buildings':{},**rec};urban+=rec['kind']=='city'
        # Repaired camera targets always land on their state.
        u,v=r['map_center']
        if int(a[min(H-1,int(v*H)),int(u*W)%W])!=rid:r['map_center']=ps[str(r['provinces'][0])]['map_center']
        if rid%100==0:print('PROVINCES',rid,'total',len(ps),flush=True)
    assert len(ps)<65536
    edges=set()
    for y in range(0,H,256):
        tile=pmap[y:min(H,y+257)]
        for l,r in [(tile[:,:-1],tile[:,1:]),(tile[:-1],tile[1:])]:
            m=(l>0)&(r>0)&(l!=r);edges.update(map(int,np.unique(np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m]))))
    l,r=pmap[:,0],pmap[:,-1];m=(l>0)&(r>0)&(l!=r);edges.update(map(int,np.unique(np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m]))))
    for e in edges:
        l,r=e//65536,e%65536;ps[str(l)]['neighbors'].append(r);ps[str(r)]['neighbors'].append(l)
    local=np.zeros(65536,np.uint8);index=np.zeros((256,256,3),np.uint8)
    for p in ps.values():
        p['neighbors'].sort();local[p['id']]=p['local_index'];index[p['id']//256,p['id']%256]=[p['region']&255,p['region']>>8,p['local_index']]
    Image.fromarray(index).save(ROOT/'assets/province_index.png')
    for i in range(4):
        sl=np.s_[i//2*4096:(i//2+1)*4096,i%2*8192:(i%2+1)*8192];r=a[sl];rgb=np.stack([(r&255).astype(np.uint8),(r>>8).astype(np.uint8),local[pmap[sl]]],-1);Image.fromarray(rgb).save(ROOT/f'assets/region_ids_{i}.png',optimize=True)
    np.savez_compressed(SRC/'province_atlas_019.npz',provinces=pmap)
    (ROOT/'data/provinces.json').write_text(json.dumps(ps,separators=(',',':')))
    return {'count':len(ps),'city_provinces':urban,'target_rural_area_km2':TARGET,'encoding_limited_states':caps,'coincident_city_centers':merged}

def oceans(a):
    rgb=np.asarray(Image.open(ROOT/'assets/sea_ids.png'),np.uint16);sea=rgb[:,:,0]+rgb[:,:,1]*256
    water=a[1::2,1::2]==0;components,n=label(water,np.ones((3,3),np.uint8));sizes=np.bincount(components.ravel());sizes[0]=0;ocean=components==np.argmax(sizes)
    # Only the connected world ocean is selectable. All enclosed inland water is 0.
    definitions={k:v for k,v in json.load(open(ROOT/'data/sea_regions.json')).items() if int(k)<1000 and v['name']!='Caspian Sea'}
    sea[~ocean]=0
    lon=(np.arange(8192)+.5)/8192*360-180;lat=90-(np.arange(4096)+.5)/4096*180
    sectors=[(230,'Beaufort Sea',-155,-100),(231,'Canadian Arctic Waters',-100,-45),(232,'Greenland Sea',-45,10),(46,'Barents Sea',10,55),(233,'Kara Sea',55,100),(234,'Laptev Sea',100,145),(235,'East Siberian Sea',145,180),(236,'Chukchi Sea',-180,-155)]
    for sid,name,lo,hi in sectors:
        mask=ocean&(lat[:,None]>=70)&(lat[:,None]<82)&(lon[None,:]>=lo)&(lon[None,:]<hi);sea[mask]=sid
        if str(sid) not in definitions:definitions[str(sid)]={'id':sid,'name':name,'naval_terrain':'arctic','source_provinces':[]}
    sea[ocean&(lat[:,None]>=82)]=237;definitions['237']={'id':237,'name':'Central Arctic Ocean','naval_terrain':'arctic','source_provinces':[]}
    # Replace old lake IDs that sat in connected coastal water with nearest ocean IDs.
    bad=ocean&(~np.isin(sea,list(map(int,definitions))))
    if bad.any():
        valid=ocean&np.isin(sea,list(map(int,definitions)))
        near=distance_transform_edt(~valid,return_distances=False,return_indices=True);sea[bad]=sea[near[0],near[1]][bad]
    definitions={k:v for k,v in definitions.items() if np.any(sea==int(k))}
    for k,s in definitions.items():
        yy,xx=np.nonzero(sea==int(k));x=xx.astype(float)
        if x.max()-x.min()>4096:x[x<4096]+=8192
        j=np.argmin((x-x.mean())**2+(yy-yy.mean())**2);s['map_center']=[(float(xx[j])+.5)/8192,(float(yy[j])+.5)/4096];s['neighbors']=[]
    edges=set()
    for l,r in [(sea[:,:-1],sea[:,1:]),(sea[:-1],sea[1:]),(sea[:,-1:],sea[:,:1])]:
        m=(l>0)&(r>0)&(l!=r);edges.update(map(int,np.unique(np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m]))))
    for e in edges:
        l,r=e//65536,e%65536;definitions[str(l)]['neighbors'].append(r);definitions[str(r)]['neighbors'].append(l)
    for s in definitions.values():s['neighbors'].sort()
    Image.fromarray(np.stack([(sea&255).astype(np.uint8),(sea>>8).astype(np.uint8),np.zeros_like(sea,np.uint8)],-1)).save(ROOT/'assets/sea_ids.png',optimize=True)
    (ROOT/'data/sea_regions.json').write_text(json.dumps(definitions,separators=(',',':')))
    return {'zones':len(definitions),'excluded_inland_water_pixels':int(np.count_nonzero(water&~ocean)),'central_arctic_min_latitude':82,'coastal_arctic_min_latitude':70}

if __name__=='__main__':
    w=json.load(open(ROOT/'data/world.json'));a=np.load(SRC/'grouped_atlas_017.npz')['regions'].copy()
    report={'version':'0.1.9','country_repaired_pixels':repair(a,w)};report['provinces']=provinces(a,w);report['oceans']=oceans(a)
    for collection in ['countries','country_registry']:
        for c in w[collection].values():c.setdefault('starting_stats',{})['political_power']=100
    w.setdefault('base_country_stats',{})['political_power']=100
    w['scenario_id']='bunny_world_2000_0_1_9';w['map']['province_geometry']='Latitude-weighted 10000 km2 rural target plus clipped city footprints; gameplay approximations.'
    for tag,c in w['countries'].items():
        u,v=c['map_center'];rid=int(a[min(H-1,int(v*H)),int(u*W)%W])
        if rid not in c['regions']:c['map_center']=w['regions'][str(c['capital'])]['map_center']
    (ROOT/'data/world.json').write_text(json.dumps(w,ensure_ascii=False,separators=(',',':')))
    np.savez_compressed(SRC/'grouped_atlas_019.npz',regions=a)
    (ROOT/'data/update_019_report.json').write_text(json.dumps(report,indent=2));print('GEOGRAPHY_019_COMPLETE',report,flush=True)
