"""Geographic States and terrain-aware provinces, independent of MD cartography.

Offline only. Natural Earth administrative polygons supply boundaries; the
accepted scenario supplies country control. Each province is grown on a local
Lambert equal-area metric grid, with settlements, real administrative edges,
relief and rivers guiding the partition. No latitude/longitude Voronoi cells.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse, copy, json, math
import numpy as np
from PIL import Image
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from scipy.ndimage import (find_objects, distance_transform_edt, binary_dilation,
                           gaussian_filter, label)
from scipy.spatial import cKDTree
from pyproj import Transformer
from skimage.graph import MCP_Geometric
from skimage.segmentation import watershed

ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/'tools/cartography'
BASE=SRC/'baseline_0205'; W,H=16384,8192; R=6371.0088
Image.MAX_IMAGE_PIXELS=None
FEATURES=json.load(open(SRC/'geographic_subdivisions.geojson'))['features']
TRANSFORM=from_bounds(-180,-90,180,90,W,H)
# Genuine upper-level divisions in these countries already have a useful scale.
KEEP_NATIVE={'USA','CAN','AST','BRA','ARG','MEX','GER','POL','SOV','CHI','RAJ',
             'PAK','IRN','SAU','SAF','UKR','ROM','NGR','EGY','FIN','SWE'}
NAMED_GROUP={'United Kingdom','France','Italy','Spain','Japan','Slovenia','Latvia',
             'Philippines','Uganda','Azerbaijan','Thailand','Vietnam','Burkina Faso',
             'Hungary','Ireland','Guinea','Belgium'}
AREA=(R*2*math.pi/W)*(R*math.pi/H)*np.cos((np.arange(H)+.5)/H*math.pi-math.pi/2)

def write(name,data):
    (ROOT/'data'/f'{name}.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'),default=lambda x:x.item()))
def xyz(lon,lat):
    a,b=np.deg2rad(lon),np.deg2rad(lat)
    return np.column_stack([np.cos(b)*np.sin(a),np.sin(b),np.cos(b)*np.cos(a)])
def center(yy,xx):
    q=xyz((xx+.5)/W*360-180,90-(yy+.5)/H*180).mean(0)
    lon=math.degrees(math.atan2(q[0],q[2]));lat=math.degrees(math.atan2(q[1],math.hypot(q[0],q[2])))
    v=xyz((xx+.5)/W*360-180,90-(yy+.5)/H*180)
    k=np.argmax(v@q)
    return [(float(xx[k])+.5)/W,(float(yy[k])+.5)/H],lon,lat
def pairs(a):
    out=Counter()
    for top in range(0,len(a),256):
        for l,r in [(a[top:top+256,:-1],a[top:top+256,1:]),(a[top:min(H-1,top+256)],a[top+1:min(H,top+257)])]:
            m=(l>0)&(r>0)&(l!=r)
            if m.any():
                codes=np.minimum(l[m],r[m]).astype(np.uint64)*65536+np.maximum(l[m],r[m])
                keys,counts=np.unique(codes,return_counts=True)
                out.update({(int(k//65536),int(k%65536)):int(n) for k,n in zip(keys,counts)})
    l,r=a[:,0],a[:,-1];m=(l>0)&(r>0)&(l!=r)
    for l,r in zip(l[m],r[m]):out[tuple(sorted([int(l),int(r)]))]+=1
    return out
def alloc(total,weights):
    w=np.asarray(weights,float);x=total*w/max(w.sum(),1e-30);n=np.floor(x).astype(np.int64)
    n[np.argsort(-(x-n),kind='stable')[:int(total-n.sum())]]+=1
    return n

def build_states():
    world=json.load(open(BASE/'world.json'));old=np.load(BASE/'states.npz')['regions']
    owners=np.zeros(8192,np.uint16)
    for k,r in world['regions'].items():owners[int(k)]=world['countries'][r['owner']]['index']
    country=owners[old];del owners
    admin=rasterize([(f['geometry'],i+1) for i,f in enumerate(FEATURES)],out_shape=(H,W),transform=TRANSFORM,dtype='uint16')
    print('ADMIN_POLYGONS_RASTERIZED',len(FEATURES),flush=True)
    # Retain an intersection only if it is a meaningful part of that country.
    # Small coastline/generalisation differences must not create foreign slivers.
    counts=Counter()
    for top in range(0,H,128):
        c=country[top:top+128];a=admin[top:top+128];m=(c>0)&(a>0)
        v,n=np.unique(c[m].astype(np.uint32)*8192+a[m],return_counts=True)
        counts.update({int(k):int(q) for k,q in zip(v,n)})
    unit_counts=Counter();country_counts=Counter()
    for code,n in counts.items():unit_counts[code%8192]+=n;country_counts[code//8192]+=n
    guests={'TAL','ACE','KAC','KAR','WAA','SHN','KUR','PUK','IEK','TML','NPM','CHE','ABK','SOO','NKR','PMR','SML','PUN','SNA','JUB','AIA','SWS','MLC','RCD','UNI','AFR','LUR','HEZ','HAM','SSU'}
    tag_by_index={c['index']:tag for tag,c in world['countries'].items()}
    dominant={}
    for code,n in counts.items():
        aid=code%8192
        if aid not in dominant or n>counts[dominant[aid]]:dominant[aid]=code
    bad=set(code for code,n in counts.items() if
            code!=dominant[code%8192]
            and tag_by_index[code//8192] not in guests
            and tag_by_index[dominant[code%8192]//8192] not in guests
            and n<country_counts[code//8192]*.10)
    for top in range(0,H,128):
        c=country[top:top+128];a=admin[top:top+128];codes=c.astype(np.uint32)*8192+a
        a[(c==0)|np.isin(codes,list(bad))]=0
    missing=(country>0)&(admin==0)
    # Spherical nearest neighbours fill only source-data coastline gaps, within
    # each country's accepted outline. They do not stretch State interiors.
    for tag,c in world['countries'].items():
        index=c['index'];my=(country==index);yy,xx=np.nonzero(missing&my)
        if not len(xx):continue
        sy,sx=np.nonzero(my&(admin>0));step=max(1,len(sx)//300000)
        if len(sx):
            tree=cKDTree(xyz((sx[::step]+.5)/W*360-180,90-(sy[::step]+.5)/H*180))
            distance,j=tree.query(xyz((xx+.5)/W*360-180,90-(yy+.5)/H*180))
            admin[yy,xx]=admin[sy[::step][j],sx[::step][j]]
            far=distance*R>100
            admin[yy[far],xx[far]]=len(FEATURES)+old[yy[far],xx[far]]
        else:
            # Microcountries and scenario controllers with no NE ADM1 footprint.
            admin[yy,xx]=len(FEATURES)+old[yy,xx]
        print('COUNTRY_ADMIN_COVERAGE',tag,len(xx),flush=True)
    del missing
    # Each country receives its own administrative pieces; no State has two owners.
    units={}; token_to_unit={}; nextid=1; tokens=np.zeros((H,W),np.uint16)
    lookup=np.zeros((max(c['index'] for c in world['countries'].values())+1,8192),np.uint16)
    by_index={c['index']:tag for tag,c in world['countries'].items()}
    existing_codes=set()
    for top in range(0,H,128):
        c=country[top:top+128];a=admin[top:top+128];m=c>0
        existing_codes.update(map(int,np.unique(c[m].astype(np.uint32)*8192+a[m])))
    for code in sorted(existing_codes):
        ci,aid=divmod(code,8192);tag=by_index[ci]
        p=FEATURES[aid-1]['properties'] if aid<=len(FEATURES) else {'name':world['regions'][str(aid-len(FEATURES))]['name']}
        name=p.get('name_en') or p.get('name') or world['countries'][tag]['name']
        group=p.get('region') if p.get('admin') in NAMED_GROUP else None
        if group in ['None','',None]:group=p.get('adm1_code',name)
        # Keep Île-de-France etc as recognizable geographic regions; grouping
        # does not assert those administrative institutions existed in 2000.
        units[nextid]={'owner':tag,'admin_id':aid,'name':name,'group':str(group),'named_group':bool(p.get('region')),'admin':p.get('admin',''),'code':p.get('adm1_code','scenario:'+str(aid))}
        lookup[ci,aid]=nextid;nextid+=1
    for top in range(0,H,128):tokens[top:top+128]=lookup[country[top:top+128],admin[top:top+128]]
    n=nextid;areas=np.bincount(tokens.ravel(),weights=np.repeat(AREA,W),minlength=n)
    # Metadata groups unite real adjacent subdivisions before any size merging.
    parent=list(range(n));members={i:[i] for i in units};size={i:float(areas[i]) for i in units}
    def root(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    def merge(a,b):
        a,b=root(a),root(b)
        if a==b:return a
        if size[a]<size[b]:a,b=b,a
        parent[b]=a;size[a]+=size[b];members[a]+=members.pop(b);size.pop(b);return a
    groups={}
    for i,u in units.items():
        key=(u['owner'],u['admin'],u['group'])
        if key in groups:merge(groups[key],i)
        else:groups[key]=i
    edges=pairs(tokens);by_country=defaultdict(list)
    for i,u in units.items():by_country[u['owner']].append(i)
    merge_report=[]
    for tag,ids in by_country.items():
        total=sum(areas[i] for i in ids);native=tag in KEEP_NATIVE
        # Budget each land-connected component separately. Offshore territories
        # must not consume all of a country's mainland State allowance.
        initial_roots=set(root(i) for i in ids);adj={i:set() for i in initial_roots}
        for a,b in edges:
            if units[a]['owner']==tag and units[b]['owner']==tag:
                a,b=root(a),root(b)
                if a!=b:adj[a].add(b);adj[b].add(a)
        components=[];remaining=set(initial_roots)
        while remaining:
            stack=[remaining.pop()];component=set(stack)
            while stack:
                for neighbor in adj[stack.pop()]&remaining:
                    remaining.remove(neighbor);component.add(neighbor);stack.append(neighbor)
            components.append(component)
        target=0
        for component in components:
            component_area=sum(size[i] for i in component)
            budget=1 if component_area<2500 else max(2,int(math.ceil((component_area/10000)**.78)))
            named_area=sum(size[i] for i in component if units[i]['named_group'] and units[i]['admin'] in NAMED_GROUP)
            if named_area>component_area*.5 and total>100000:budget=max(budget,len(component))
            target+=min(len(component),budget)
        target=min(len(initial_roots),target)
        # Preserve upper-level native divisions; only merge their very small
        # attached city enclaves, unless explicitly protected by KEEP_NATIVE.
        while not native and len(set(root(i) for i in ids))>target:
            candidates=Counter()
            for (a,b),length in edges.items():
                if units[a]['owner']!=tag or units[b]['owner']!=tag:continue
                a,b=root(a),root(b)
                if a!=b:candidates[tuple(sorted([a,b]))]+=length
            if not candidates:break
            # Prefer removing the smallest fragments along a substantial common
            # border. This retains actual boundaries instead of drawing cut lines.
            a,b=min(candidates,key=lambda ab:(min(size[ab[0]],size[ab[1]])/(candidates[ab]**.55),size[ab[0]]+size[ab[1]]))
            merge(a,b)
        merge_report.append({'country':tag,'source_divisions':len(ids),'states':len(set(root(i) for i in ids)),'target':target,'native_preserved':native})
    roots=sorted(set(root(i) for i in units),key=lambda i:(units[i]['owner'],i))
    rootid={r:j+1 for j,r in enumerate(roots)};lut=np.zeros(n,np.uint16)
    for i in units:lut[i]=rootid[root(i)]
    states=lut[tokens];states[old==8191]=8191
    np.savez_compressed(SRC/'admin_atlas_0206.npz',admin=tokens)
    records={};boxes=find_objects(states,max_label=8191)
    overlap=defaultdict(Counter)
    for top in range(0,H,128):
        s=states[top:top+128];o=old[top:top+128];m=(s>0)&(s<8191)
        code=s[m].astype(np.uint32)*8192+o[m];v,nn=np.unique(code,return_counts=True)
        for q,k in zip(v,nn):overlap[int(q//8192)][int(q%8192)]+=int(k)
    for r in roots:
        sid=rootid[r];ids=members[r];tag=units[r]['owner'];bb=boxes[sid-1]
        yy,xx=np.nonzero(states[bb]==sid);yy+=bb[0].start;xx+=bb[1].start
        focus,_,_=center(yy,xx)
        meaningful=[i for i in ids if areas[i]>=max(100,size[r]*.005)] or [max(ids,key=lambda i:areas[i])]
        groupset=set(units[i]['group'] for i in meaningful)
        if len(groupset)==1 and units[r]['admin'] in NAMED_GROUP and units[r]['named_group']:name=next(iter(groupset))
        elif len(meaningful)==1:name=units[meaningful[0]]['name']
        else:
            ordered=sorted(meaningful,key=lambda i:-areas[i]);name=' / '.join(units[i]['name'] for i in ordered[:2])
        if size[r]<2500 and len(by_country[tag])>1 and len(world['countries'][tag]['regions'])==1:name=world['countries'][tag]['name']
        oldids=sorted(overlap[sid]);dominant=max(oldids,key=overlap[sid].get);prev=world['regions'][str(dominant)]
        rights=[i for i in oldids if overlap[sid][i]>=sum(overlap[sid].values())*.1]
        records[str(sid)]={'id':sid,'name':name,'owner':tag,'population':0,'buildings':{},'provinces':[],
            'cores':sorted(set(v for i in rights for v in world['regions'][str(i)]['cores'])),
            'claims':sorted(set(v for i in rights for v in world['regions'][str(i)]['claims'])),
            'source_states':sorted(set(v for i in oldids for v in world['regions'][str(i)]['source_states'])),
            'geographic_divisions':[units[i]['name'] for i in ids],'geographic_codes':[units[i]['code'] for i in ids],
            'map_center':focus,'demographic_profile':prev.get('demographic_profile',tag),'area_km2':round(size[r],2),
            'population_source':'Temporary area-overlap transfer from the accepted baseline; demographic refinement deferred.'}
    # Transfer only the required existing bookkeeping; no demographic rebuild.
    old_to_new=defaultdict(list)
    for sid,counts in overlap.items():
        for oid,count in counts.items():old_to_new[oid].append((sid,count))
    for oid,targets in old_to_new.items():
        prev=world['regions'][str(oid)];weights=[n for s,n in targets]
        for (sid,_),pop in zip(targets,alloc(prev['population'],weights)):records[str(sid)]['population']+=int(pop)
        for building,value in prev['buildings'].items():
            for (sid,_),amount in zip(targets,alloc(int(value),weights)):
                if amount:records[str(sid)]['buildings'][building]=records[str(sid)]['buildings'].get(building,0)+int(amount)
    for tag,c in world['countries'].items():
        ids=[int(k) for k,r in records.items() if r['owner']==tag]
        u,v=c['map_center'];at=int(states[min(H-1,int(v*H)),int(u*W)%W])
        if at not in ids:
            prev=world['regions'][str(c['capital'])];u,v=prev['map_center'];at=int(states[min(H-1,int(v*H)),int(u*W)%W])
        if at not in ids:at=max(ids,key=lambda k:records[str(k)]['population'])
        c['regions']=sorted(ids);c['capital']=at;c['map_center']=records[str(at)]['map_center']
    world['regions']=records;world['scenario_id']='bunny_world_2000_0_2_0_6';world['version']='0.2.0.6'
    world['map'].update(cartography='Real geographic administrative boundaries with adjacent gameplay grouping; accepted year-2000 country controllers.',regional_boundary_accuracy='Natural Earth geographic ADM1 boundaries; larger named regions and adjacent small-unit merges. No MD bitmap registration.',province_geometry='Locally equal-area terrain/settlement-guided partitions; independent of Millennium Dawn province geometry.',urban_population='Temporary transferred baseline bookkeeping; new demographic distribution is deferred.')
    micro=json.load(open(BASE/'microstate_geometry.json'));micro['state']=next(int(k) for k,r in records.items() if r['owner']==micro['country'])
    u,v=micro['center_uv'];cx,cy=int(u*W),int(v*H)
    host=states[cy-5:cy+6,cx-5:cx+6];host=host[(host>0)&(host!=micro['state'])]
    micro['host_state']=int(np.bincount(host).argmax());write('microstate_geometry',micro)
    write('world',world);np.savez_compressed(SRC/'grouped_atlas_022r2.npz',regions=states)
    report={'version':'0.2.0.6','states':len(records),'countries':len(world['countries']),'country_groups':merge_report,'source':'Natural Earth geographic subdivisions; accepted scenario country mask','demographics':'Deferred; existing totals transferred for runtime bookkeeping.'}
    write('geography_0206_report',report)
    print('STATES_COMPLETE',len(records),flush=True)

def build_provinces(limit=None, budgets=None):
    world=json.load(open(ROOT/'data/world.json'));a=np.load(SRC/'grouped_atlas_022r2.npz')['regions']
    admin=np.load(SRC/'admin_atlas_0206.npz')['admin'];boxes=find_objects(a,max_label=8191)
    elev=np.load(SRC/'etopo_021.npz')['meters'];types=np.asarray(Image.open(ROOT/'assets/terrain_types.png'))[:,:,0]
    # Real rivers and administrative edges resist crossings during region growth.
    riverpath=SRC/'rivers_0206.npy'
    if not riverpath.exists():
        features=json.load(open(SRC/'rivers_0201.geojson'))['features']
        rivers=rasterize([(f['geometry'],1) for f in features if f['properties'].get('featurecla')=='River'],out_shape=elev.shape,transform=from_bounds(-180,-90,180,90,elev.shape[1],elev.shape[0]),dtype='uint8')
        np.save(riverpath,rivers)
    rivers=np.load(riverpath)
    cities=json.load(open(BASE/'cities.json'));city_by_state=defaultdict(list)
    for c in cities:
        x=int((c['longitude']+180)/360*W)%W;y=min(H-1,max(0,int((90-c['latitude'])/180*H)));sid=int(a[y,x])
        if not 0<sid<8191 or world['regions'][str(sid)]['owner']!=c['country']:
            yy,xx=np.mgrid[max(0,y-7):min(H,y+8),max(0,x-7):min(W,x+8)];s=a[yy,xx]
            valid=np.array([world['regions'].get(str(i),{}).get('owner')==c['country'] for i in s.ravel()]).reshape(s.shape)
            if valid.any():
                d=np.where(valid,(yy-y)**2+(xx-x)**2,np.inf);j=np.unravel_index(np.argmin(d),d.shape);y,x=int(yy[j]),int(xx[j]);sid=int(a[y,x])
            elif 0<sid<8191:c['country']=world['regions'][str(sid)]['owner']
            else:continue
        c['map_pixel']=[x,y];city_by_state[sid].append(c)
    city_points=np.array([[c['longitude'],c['latitude']] for c in cities if c.get('population_rank',0)>=50000])
    citytree=cKDTree(xyz(city_points[:,0],city_points[:,1]));atlas=np.zeros_like(a);ps={};report=[]
    sample_states=set(limit or [])
    for key,state in world['regions'].items():
        sid=int(key)
        if limit and state['owner'] not in sample_states:continue
        bb=boxes[sid-1];yy,xx=np.nonzero(a[bb]==sid);yy+=bb[0].start;xx+=bb[1].start
        focus,lon0,lat0=center(yy,xx);area=float(AREA[yy].sum())
        if (area<1200 or len(xx)<50) and (budgets is None or budgets[sid]<=1):
            codes=np.ones(len(xx),np.int32);count=1;gridstep=0
        else:
            # Work in kilometres on a local equal-area projection. Native
            # geographic raster pixels are only a final storage format.
            proj=Transformer.from_crs('EPSG:4326',f'+proj=laea +lat_0={lat0:.8f} +lon_0={lon0:.8f} +datum=WGS84 +units=km',always_xy=True)
            inverse=Transformer.from_crs(proj.target_crs,'EPSG:4326',always_xy=True)
            lon=(xx+.5)/W*360-180;lat=90-(yy+.5)/H*180;px,py=proj.transform(lon,lat)
            gridstep=3.5;left=px.min()-gridstep*2;bottom=py.min()-gridstep*2
            ix=np.floor((px-left)/gridstep).astype(int);iy=np.floor((py-bottom)/gridstep).astype(int)
            shape=(iy.max()+3,ix.max()+3);mask=np.zeros(shape,bool);mask[iy,ix]=True
            mask=binary_dilation(mask,iterations=1)
            gy,gx=np.indices(shape);glon,glat=inverse.transform(left+(gx+.5)*gridstep,bottom+(gy+.5)*gridstep)
            cols=np.clip(((glon+180)/360*elev.shape[1]).astype(int),0,elev.shape[1]-1);rows=np.clip(((90-glat)/180*elev.shape[0]).astype(int),0,elev.shape[0]-1)
            z=gaussian_filter(np.maximum(elev[rows,cols],0).astype(float),1.1)
            dz=np.hypot(*np.gradient(z))/gridstep
            native_cols=np.clip(((glon+180)/360*W).astype(int),0,W-1);native_rows=np.clip(((90-glat)/180*H).astype(int),0,H-1)
            ad=admin[native_rows,native_cols];edge=np.zeros(shape,bool)
            edge[:,1:]|=(ad[:,1:]!=ad[:,:-1]);edge[1:]|=(ad[1:]!=ad[:-1])
            noise=(np.sin((left+gx*gridstep)/37+np.cos((bottom+gy*gridstep)/91))+np.sin((bottom+gy*gridstep)/49+np.sin((left+gx*gridstep)/77)))*.35
            cost=1.2+noise+np.clip(dz/70,0,2.5)+edge*3.5+rivers[rows,cols]*5
            cost[~mask]=np.inf
            # Settlement proximity and arid/ice land cover determine resolution;
            # this does not calculate or replace any demographic accounts.
            dcity=citytree.query(xyz(lon,lat))[0]*R
            lc=types[yy//2,xx//2]
            target=np.full(len(xx),16000.,float)
            target[dcity<100]=7000;target[dcity<35]=2500
            barren=(lc==3)|(lc==6)
            target[barren&(dcity>120)]=100000
            target[(abs(lat)>62)&(dcity>180)]=150000
            target[(state['owner']=='GRN')&(dcity>120)]=350000
            target[(dcity>300)&(~barren)&(abs(lat)<62)]=50000
            count=max(1,min(220,int(round(np.sum(AREA[yy]/target)))))
            if budgets is not None:count=budgets[sid]
            points=np.column_stack([px,py]);samples=np.arange(0,len(xx),max(1,len(xx)//18000));sp=points[samples]
            importance=np.sqrt(16000/target[samples]);seeds=[]
            # Settlement seeds are separated by at least ~30 km. Closely packed
            # cities share a playable province instead of generating pinpricks.
            localtree=cKDTree(points)
            for c in sorted(city_by_state[sid],key=lambda c:-c.get('population_rank',0)):
                cx,cy=c['map_pixel'];qlon=(cx+.5)/W*360-180;qlat=90-(cy+.5)/H*180;q=np.array(proj.transform(qlon,qlat))
                if all(np.linalg.norm(q-points[j])>=30 for j in seeds):seeds.append(int(localtree.query(q)[1]))
            count=max(count,len(seeds)) if budgets is None else budgets[sid]
            if budgets is None:count=min(count,240)
            seeds=seeds[:count]
            if not seeds:seeds=[int(localtree.query(points.mean(0))[1])]
            dist=np.min(np.sum((sp[:,None,:]-points[seeds][None,:,:])**2,axis=2),axis=1)
            while len(seeds)<count:
                j=int(samples[np.argmax(dist*importance**2)]);seeds.append(j);dist=np.minimum(dist,np.sum((sp-points[j])**2,axis=1))
            markers=np.zeros(shape,np.int32)
            for i,j in enumerate(seeds):markers[iy[j],ix[j]]=i+1
            # Each substantial disconnected island receives a seed. Tiny
            # islands can belong to a nearby archipelago province.
            components,n=label(mask);sizes=np.bincount(components.ravel());seeded=set(components[markers>0])
            for component in range(1,n+1):
                if component in seeded:continue
                if sizes[component]*gridstep**2<1200:continue
                sy,sx=np.nonzero(components==component);j=len(sy)//2;markers[sy[j],sx[j]]=int(markers.max())+1
            starts=np.column_stack(np.nonzero(markers))
            distance,_=MCP_Geometric(cost,fully_connected=True).find_costs(starts)
            reached=mask&np.isfinite(distance)
            grown=watershed(np.where(reached,distance,0),markers=markers,mask=reached,connectivity=2)
            empty=mask&(grown==0)
            if empty.any():
                near=distance_transform_edt(grown==0,return_distances=False,return_indices=True);grown[empty]=grown[tuple(near[:,empty])]
            codes=grown[iy,ix];count=int(codes.max())
        state['provinces']=[]
        for code in sorted(np.unique(codes)):
            sel=codes==code;y,x=yy[sel],xx[sel];pid=len(ps)+1;atlas[y,x]=pid
            point,_,_=center(y,x);names=[c['name'] for c in city_by_state[sid] if atlas[c['map_pixel'][1],c['map_pixel'][0]]==pid]
            ps[str(pid)]={'id':pid,'region':sid,'local_index':len(state['provinces'])+1,'map_center':point,'area_km2':round(float(AREA[y].sum()),2),'neighbors':[],'buildings':{},'kind':'city' if names else 'rural','cities':names,'geometry_source':'Geographic administrative boundaries and locally equal-area terrain-guided growth'}
            state['provinces'].append(pid)
        report.append({'state':sid,'name':state['name'],'area_km2':round(area),'provinces':len(state['provinces']),'projection':'Lambert azimuthal equal-area','grid_km':gridstep})
        if sid%25==0:print('PROVINCES',sid,state['name'],len(ps),flush=True)
    if limit:
        np.savez_compressed(SRC/'prototype_0206.npz',provinces=atlas)
        write('prototype_0206_provinces',ps);return
    # Native-grid connectivity is checked separately after generation. Store
    # only the graph from the actual final atlas, including the dateline.
    for (l,r),length in pairs(atlas).items():ps[str(l)]['neighbors'].append(r);ps[str(r)]['neighbors'].append(l)
    for p in ps.values():p['neighbors'].sort()
    for c in cities:
        if 'map_pixel' not in c:continue
        x,y=c.pop('map_pixel');c['province_id']=int(atlas[y,x]);c['urban_group']='';c['population_2000']=None
    micro=json.load(open(ROOT/'data/microstate_geometry.json'));micro['province']=world['regions'][str(micro['state'])]['provinces'][0]
    u,v=micro['center_uv'];cx,cy=int(u*W),int(v*H);near=atlas[cy-5:cy+6,cx-5:cx+6]
    host=[int(i) for i in near.ravel() if i and ps[str(int(i))]['region']==micro['host_state']]
    micro['host_province']=int(np.bincount(host).argmax());ps[str(micro['province'])]['area_km2']=.44
    write('microstate_geometry',micro);write('cities',cities);write('world',world);write('provinces',ps)
    np.savez_compressed(SRC/'province_atlas_022r2.npz',provinces=atlas)
    np.savez_compressed(SRC/'province_atlas_0206.npz',provinces=atlas)
    if budgets is not None:np.savez_compressed(SRC/'province_atlas_0207.npz',provinces=atlas)
    index=np.zeros((65536,3),np.uint8)
    for p in ps.values():index[p['id'],:2]=[p['region']&255,p['region']>>8]
    index[65535,:2]=[255,31];Image.fromarray(index.reshape(256,256,3)).save(ROOT/'assets/province_index.png')
    atlas[a==8191]=65535
    for i in range(4):
        q=atlas[i//2*4096:(i//2+1)*4096,i%2*8192:(i%2+1)*8192]
        Image.fromarray(np.stack([(q&255).astype(np.uint8),(q>>8).astype(np.uint8),np.zeros_like(q,np.uint8)],-1)).save(ROOT/'assets'/f'region_ids_{i}.png')
    report_name='geography_0207_report' if budgets is not None else 'geography_0206_report'
    r=json.load(open(ROOT/'data'/f'{report_name}.json'));r.update(provinces=len(ps),province_generation=report);write(report_name,r)
    print('PROVINCES_COMPLETE',len(ps),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['states','provinces']);p.add_argument('--sample',nargs='+');args=p.parse_args()
    if args.phase=='states':build_states()
    else:build_provinces(args.sample)
