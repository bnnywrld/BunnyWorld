"""Group geographic subdivisions around MD states; retain rights and sea zones.

Offline inputs are retained under tools/cartography. Pass the mod ZIP once to
refresh scenario rights, country names and its original naval-zone raster.
Land coastlines and year-2000 control come from the prepared 0.1.6 atlas.
"""
from pathlib import Path
import json, sys, zipfile, io, math, heapq, collections, unicodedata, re
import numpy as np
from PIL import Image
from scipy.ndimage import find_objects, distance_transform_edt, map_coordinates
from scipy.optimize import linear_sum_assignment
from scipy.interpolate import RBFInterpolator
from scipy.spatial import cKDTree
from import_md import parse, Block, at_start, load_localisation, clean_name

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'tools/cartography'
W,H=16384,8192
Image.MAX_IMAGE_PIXELS=None

class ModZip:
    def __init__(self,z):
        self.z=z
        self.prefix=next(n[:-len('map/definition.csv')] for n in z.namelist() if n.endswith('map/definition.csv'))
    def namelist(self):return [n[len(self.prefix):] for n in self.z.namelist() if n.startswith(self.prefix)]
    def read(self,n):return self.z.read(self.prefix+n)

def import_reference(archive):
    with zipfile.ZipFile(archive) as zz:
        z=ModZip(zz); loc=load_localisation(z); facts={}; referenced=set()
        for n in sorted(z.namelist()):
            if not n.startswith('history/states/') or not n.endswith('.txt'):continue
            state=parse(z.read(n).decode('utf-8-sig')).get('state')
            history=at_start(state.get('history',Block([])))
            cores=set();claims=set()
            for k,_,v in history:
                if k=='add_core_of':cores.add(v)
                elif k=='remove_core_of':cores.discard(v)
                elif k=='add_claim_by':claims.add(v)
                elif k=='remove_claim_by':claims.discard(v)
            cores=sorted(cores);claims=sorted(claims-set(cores)); referenced.update(cores+claims)
            facts[str(state.get('id'))]={'cores':cores,'claims':claims,'name':clean_name(loc.get(state.get('name'),state.get('name')),loc)}
        registry={}
        for n in z.namelist():
            if n.startswith('common/country_tags/') and n.endswith('.txt'):
                for tag,_,file in parse(z.read(n).decode('utf-8-sig')).items:
                    if tag and isinstance(file,str):
                        name=next((loc[k] for k in [tag+'_neutrality',tag+'_democratic',tag] if k in loc),tag)
                        registry[tag]={'tag':tag,'name':clean_name(name,loc),'outlook':'Unspecified','cosmetic':'','color':[115,135,145]}
        assert referenced<=set(registry),referenced-set(registry)
        (SRC/'md_state_rights.json').write_text(json.dumps(facts,ensure_ascii=False,separators=(',',':')))
        (SRC/'md_country_registry.json').write_text(json.dumps(registry,ensure_ascii=False,separators=(',',':')))
        definition=[]
        for line in z.read('map/definition.csv').decode('utf-8-sig').splitlines():
            p=line.split(';')
            if len(p)>=5:definition.append((int(p[0]),tuple(map(int,p[1:4])),p[4]))
        sea_provinces={p for p,_,kind in definition if kind=='sea'}
        pid_zone={};seas={}
        for n in sorted(z.namelist()):
            if '/strategicregions/' not in n or not n.endswith('.txt'):continue
            b=parse(z.read(n).decode('utf-8-sig')).get('strategic_region'); ps=b.get('provinces',Block([]))
            ids=[int(p) for p in ps.scalars() if int(p) in sea_provinces]
            if not ids:continue
            sid=int(b.get('id')); key=b.get('name'); name=clean_name(loc.get(key,key),loc)
            if name==key:name=Path(n).stem.split('-',1)[-1]
            if b.get('naval_terrain') is None:name+=' coastal waters'
            seas[str(sid)]={'id':sid,'name':name,'naval_terrain':b.get('naval_terrain','coastal'),'source_provinces':ids}
            for pid in ids:pid_zone[pid]=sid
        colors=np.asarray(Image.open(io.BytesIO(z.read('map/provinces.bmp'))),np.uint32)
        packed=colors[:,:,0]+colors[:,:,1]*256+colors[:,:,2]*65536
        lut=np.zeros(16777216,np.uint16)
        for pid,(r,g,b),kind in definition:
            if pid in pid_zone:lut[r+g*256+b*65536]=pid_zone[pid]
        out=lut[packed];Image.fromarray(out).save(SRC/'md_sea_zones.png')
        (SRC/'md_sea_zones.json').write_text(json.dumps(seas,ensure_ascii=False,separators=(',',':')))
        print('Imported MD rights and',len(seas),'water regions',flush=True)

def read_atlas():
    ids=np.zeros((H,W),np.uint16);pids=np.zeros((H,W),np.uint16)
    w=json.loads((ROOT/'data/world.json').read_text())
    # Kept immutable so repeated builds do not group an already grouped atlas.
    seed=SRC/'region_seed_016.npz'
    if seed.exists():
        a=np.load(seed);return a['regions'],a['provinces'],json.loads((SRC/'world_seed_016.json').read_text()),json.loads((SRC/'province_seed_016.json').read_text())
    ps=json.loads((ROOT/'data/provinces.json').read_text()); lut=np.zeros(8192*256,np.uint16)
    for r in w['regions'].values():
        for i,pid in enumerate(r['provinces'],1):lut[r['id']*256+i]=pid
    for i in range(4):
        a=np.asarray(Image.open(ROOT/f'assets/region_ids_{i}.png'),np.uint32);rr=a[:,:,0]+a[:,:,1]*256
        sl=np.s_[i//2*4096:(i//2+1)*4096,i%2*8192:(i%2+1)*8192];ids[sl]=rr;pids[sl]=lut[rr*256+a[:,:,2]]
    np.savez_compressed(seed,regions=ids,provinces=pids)
    (SRC/'world_seed_016.json').write_text(json.dumps(w,ensure_ascii=False,separators=(',',':')))
    (SRC/'province_seed_016.json').write_text(json.dumps(ps,separators=(',',':')))
    return ids,pids,w,ps

def dxy(a,b):
    dx=abs(a[0]-b[0]);dx=min(dx,1-dx)
    return math.hypot(dx*max(.15,math.cos((a[1]+b[1])*.5*math.pi-math.pi*.5)),a[1]-b[1])

def build_land():
    current,pmap,world,oldps=read_atlas();old=json.loads((SRC/'world_seed_015.json').read_text())
    # A single modern Shan subdivision contains the two distant Wa control
    # areas. They are separate MD regions, not neighboring units to merge.
    wa_native=[int(s) for s,r in world['regions'].items() if r['owner']=='WAA']
    for native in wa_native:
        southern=(current==native)&(np.arange(H)[:,None]>(90-21.0)/180*H)
        northern=(current==native)&(~southern)
        if southern.any() and northern.any():
            extra=max(map(int,world['regions']))+1
            record=dict(world['regions'][str(native)]);record['id']=extra;record['geographic_name']='Southern Wa area'
            world['regions'][str(extra)]=record;current[southern]=extra
    # MD groups Yukon with the Northwest Territories and PEI with Nova Scotia,
    # but divides Quebec into three larger geographic areas. Keep the real
    # provincial perimeter, then make those bounded internal subdivisions.
    def geographic_key(value):
        value=unicodedata.normalize('NFKD',value.lower())
        return ''.join(c for c in value if c.isalnum() and not unicodedata.combining(c))
    quebec=[int(s) for s,r in world['regions'].items() if r['owner']=='CAN' and geographic_key(r['geographic_name'])=='quebec']
    lat=90-(np.arange(H)+.5)/H*180;lon=(np.arange(W)+.5)/W*360-180
    for native in quebec:
        mask=current==native;record=world['regions'][str(native)];record['geographic_name']='Eastern Quebec'
        for name,area in [('Ungava',lat[:,None]>=55),('Western Quebec',(lat[:,None]<55)&(lon[None,:]<-73))]:
            piece=mask&area
            if not piece.any():continue
            extra=max(map(int,world['regions']))+1;copy=dict(record);copy['id']=extra;copy['geographic_name']=name;world['regions'][str(extra)]=copy;current[piece]=extra
    md=np.load(SRC/'control_seed_015.npz')['region_ids'];rights=json.loads((SRC/'md_state_rights.json').read_text())
    owners=np.zeros(8192,np.uint16);mdowners=np.zeros(4096,np.uint16)
    for rid,r in world['regions'].items():owners[int(rid)]=world['countries'][r['owner']]['index']
    for rid,r in old['regions'].items():mdowners[int(rid)]=world['countries'][r['owner']]['index']
    profile_index={};profiles=[None];mp=np.zeros(4096,np.uint16)
    for sid,r in old['regions'].items():
        q=rights[sid];key=(r['owner'],tuple(q['cores']),tuple(q['claims']))
        if key not in profile_index:profile_index[key]=len(profiles);profiles.append(key)
        mp[int(sid)]=profile_index[key]
    # Split only where a meaningful source rights profile differs. This prevents
    # unioning a local foreign claim into every part of a larger merged region.
    weights=np.zeros((len(world['regions'])+1,1251),np.float64)
    for y in range(0,H,128):
        a=current[y:y+128];b=md[y:y+128];m=(a>0)&(a<8191)&(b>0)&(b<=1250)&(owners[a]==mdowners[b])
        yy=np.broadcast_to(np.cos((np.arange(y,y+len(a))+.5)/H*math.pi-math.pi*.5)[:,None],a.shape)
        weights+=np.bincount((a[m].astype(np.int64)*1251+b[m]),weights=yy[m],minlength=weights.size).reshape(weights.shape)
    dominant=np.argmax(weights,axis=1);default=np.zeros(8192,np.uint16);default[:len(dominant)]=mp[dominant]
    for rid,r in world['regions'].items():
        if default[int(rid)]==0:
            s=next(s for s,q in old['regions'].items() if q['owner']==r['owner']);default[int(rid)]=mp[int(s)]
    canadian_states={'northwestterritories':753,'yukon':753,'britishcolumbia':754,'alberta':755,'saskatchewan':756,'manitoba':757,'nunavut':758,'newfoundlandandlabrador':759,'novascotia':760,'princeedwardisland':760,'newbrunswick':761,'easternquebec':762,'ontario':763,'westernquebec':1159,'ungava':1160}
    canadian_profile=np.zeros(8192,np.uint16)
    for rid,r in world['regions'].items():
        if r['owner']=='CAN':
            state=canadian_states.get(geographic_key(r['geographic_name']))
            if state:canadian_profile[int(rid)]=mp[state]
    token=np.zeros((H,W),np.uint32)
    for y in range(0,H,256):
        a=current[y:y+256];b=md[y:y+256];valid=(a>0)&(a<8191)
        pp=default[a].copy();same=(b>0)&(b<=1250)&(owners[a]==mdowners[b]);pp[same]=mp[b[same]]
        canada=canadian_profile[a]>0;pp[canada]=canadian_profile[a][canada]
        token[y:y+256]=np.where(valid,a.astype(np.uint32)*2048+pp,0)
    keys,counts=np.unique(token,return_counts=True);keys=keys[keys>0]
    lut=np.zeros(int(keys.max())+1,np.uint16);lut[keys]=np.arange(1,len(keys)+1);units=lut[token];del token,lut,weights
    print('Geographic units after rights protection',len(keys),flush=True)
    unit_meta={i+1:(int(k)//2048,int(k)%2048) for i,k in enumerate(keys)}
    overlaps=np.zeros((len(keys)+1,1251),np.float64);sx=np.zeros(len(keys)+1);sy=sx.copy();nn=sx.copy()
    for y in range(0,H,128):
        a=units[y:y+128];b=md[y:y+128];yy=np.broadcast_to(np.arange(y,y+len(a))[:,None]+.5,a.shape);xx=np.broadcast_to(np.arange(W)[None,:]+.5,a.shape)
        nn+=np.bincount(a.ravel(),minlength=len(nn));sx+=np.bincount(a.ravel(),weights=xx.ravel(),minlength=len(nn));sy+=np.bincount(a.ravel(),weights=yy.ravel(),minlength=len(nn))
        m=(a>0)&(b>0)&(b<=1250);area=np.cos(yy/H*math.pi-math.pi*.5)
        overlaps+=np.bincount(a[m].astype(np.int64)*1251+b[m],weights=area[m],minlength=overlaps.size).reshape(overlaps.shape)
    centers=np.column_stack([sx/np.maximum(nn,1)/W,sy/np.maximum(nn,1)/H]);del sx,sy
    pairs=set()
    for y in range(0,H,256):
        a=units[y:min(H,y+257)]
        for l,r in [(a[:,:-1],a[:,1:]),(a[:-1],a[1:])]:
            m=(l>0)&(r>0)&(l!=r);pairs.update(map(int,np.unique(np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m]))))
    a,b=units[:,0],units[:,-1];m=(a>0)&(b>0)&(a!=b);pairs.update(map(int,np.minimum(a[m],b[m]).astype(np.uint32)*65536+np.maximum(a[m],b[m])))
    graph=collections.defaultdict(list)
    for pair in pairs:
        a,b=pair//65536,pair%65536
        if unit_meta[a][1]==unit_meta[b][1]:graph[a].append(b);graph[b].append(a)
    unit_target={};target_sources={};target_profile={}
    def norm(value):
        value=unicodedata.normalize('NFKD',value.lower())
        return ''.join(c for c in value if c.isalnum() and not unicodedata.combining(c))
    capitals={int(c['capital']):c['map_center'] for c in old['countries'].values()}
    geographic_names={u:norm(world['regions'][str(native)]['geographic_name']) for u,(native,p) in unit_meta.items()}
    for profile in range(1,len(profiles)):
        us=[u for u,(_,p) in unit_meta.items() if p==profile];ss=[int(s) for s in old['regions'] if mp[int(s)]==profile]
        if not us:raise ValueError(('rights profile missing',profile,profiles[profile]))
        score=overlaps[np.ix_(us,ss)]
        # Represent the largest source states if NE has fewer units than MD.
        name_matches=np.array([[geographic_names[u] in {norm(rights[str(s)]['name']),norm(old['regions'][str(s)]['name'])} for s in ss] for u in us],bool)
        if len(ss)>len(us):
            priority=score.sum(axis=0)+name_matches.any(axis=0)*1e10+np.array([s in capitals for s in ss])*1e12
            keep=np.argsort(-priority,kind='stable')[:len(us)];ss=[ss[i] for i in keep];score=score[:,keep];name_matches=name_matches[:,keep]
        normalized=score/np.maximum(score.sum(axis=0,keepdims=True),1)
        normalized+=name_matches*25.0
        # Pin each capital to the actual geographic capital pixel whenever its
        # territorial-rights profile agrees. Area-only ranking can drop cities.
        for j,s in enumerate(ss):
            if s not in capitals:continue
            u,v=world['countries'][old['regions'][str(s)]['owner']]['map_center']
            unit=int(units[min(H-1,int(v*H)),int(u*W)%W])
            if unit in us:normalized[us.index(unit),j]+=1000.0
        rows,cols=linear_sum_assignment(-normalized)
        seeds={us[i]:ss[j] for i,j in zip(rows,cols)};dist={};queue=[];fixed=set(seeds)
        for u,s in seeds.items():dist[u]=0.;unit_target[u]=s;heapq.heappush(queue,(0.,u,s));target_profile[s]=profile
        ss_index={s:i for i,s in enumerate(ss)};us_index={u:i for i,u in enumerate(us)}
        while queue:
            cost,u,s=heapq.heappop(queue)
            if cost!=dist[u] or unit_target[u]!=s:continue
            for v in graph[u]:
                if v in fixed:continue
                compat=score[us_index[v],ss_index[s]]/max(1.,overlaps[v].sum())
                step=max(.00002,dxy(centers[u],centers[v]))*(1.0+2.5*(1-compat));new=cost+step
                if new<dist.get(v,float('inf')):dist[v]=new;unit_target[v]=s;heapq.heappush(queue,(new,v,s))
        for u in us:
            if u not in unit_target:
                row=score[us_index[u]]
                unit_target[u]=ss[int(np.argmax(row))] if row.max()>0 else min(ss,key=lambda s:dxy(centers[u],old['regions'][str(s)]['map_center']))
        for s in [int(s) for s in old['regions'] if mp[int(s)]==profile]:
            dest=s if s in ss else min(ss,key=lambda d:dxy(old['regions'][str(s)]['map_center'],old['regions'][str(d)]['map_center']))
            target_sources.setdefault(dest,[]).append(s)
    targets=sorted(set(unit_target.values()));target_id={s:i+1 for i,s in enumerate(targets)};remap=np.zeros(len(keys)+1,np.uint16)
    for u,s in unit_target.items():remap[u]=target_id[s]
    result=remap[units];result[current==8191]=8191
    regions={};members=collections.defaultdict(set)
    for u,s in unit_target.items():members[s].add(unit_meta[u][0])
    for target in targets:
        rid=target_id[target];src=old['regions'][str(target)];q=rights[str(target)];seeds=target_sources[target]
        buildings=collections.Counter()
        for s in seeds:buildings.update(old['regions'][str(s)].get('buildings',{}))
        name='Northern Wa' if src['owner']=='WAA' and target==497 else q['name']
        regions[str(rid)]={'id':rid,'name':name,'owner':src['owner'],'population':sum(old['regions'][str(s)]['population'] for s in seeds),'buildings':dict(buildings),'provinces':[],'cores':q['cores'],'claims':q['claims'],'source_states':seeds,'geographic_divisions':[world['regions'][str(a)]['geographic_name'] for a in sorted(members[target])],'population_source':'Supplied MD state totals, combined where geographic subdivisions have been grouped.'}
    del overlaps,md,current,units
    # Reparent prepared gameplay cells. Split only cells crossing a protected
    # rights boundary; every resulting province has one geographic parent.
    token=result.astype(np.uint32)*65536+pmap;token[(result==0)|(result==8191)]=0
    keys=np.unique(token);keys=keys[keys>0];newps={};province_lut={};nextpid=max(map(int,oldps))+1;used=set()
    for key in keys:
        rid,oldpid=int(key)//65536,int(key)%65536
        pid=oldpid if oldpid not in used else nextpid
        if pid==nextpid:nextpid+=1
        used.add(pid);regions[str(rid)]['provinces'].append(pid);province_lut[int(key)]=pid
        newps[str(pid)]={'id':pid,'region':rid,'local_index':0,'neighbors':[],'buildings':{}}
    assert nextpid<65536
    for r in regions.values():
        r['provinces'].sort();assert 0<len(r['provinces'])<256,(r['name'],len(r['provinces']))
        for i,p in enumerate(r['provinces'],1):newps[str(p)]['local_index']=i
    pk=np.array(sorted(province_lut),np.uint32);pv=np.array([province_lut[int(k)] for k in pk],np.uint16)
    newmap=np.zeros((H,W),np.uint16)
    for y in range(0,H,256):
        a=token[y:y+256];m=a>0;out=newmap[y:y+256];out[m]=pv[np.searchsorted(pk,a[m])]
    del pmap,token
    bb=find_objects(newmap,max_label=nextpid-1)
    for pid,p in newps.items():
        box=bb[int(pid)-1];yy,xx=np.nonzero(newmap[box]==int(pid));yy+=box[0].start;xx+=box[1].start
        # Use an owned pixel nearest the local centroid, including dateline cells.
        if xx.max()-xx.min()>W//2:
            keep=xx<W//2 if np.count_nonzero(xx<W//2)>len(xx)/2 else xx>=W//2;xx=xx[keep];yy=yy[keep]
        i=int(np.argmin((xx-xx.mean())**2+(yy-yy.mean())**2));p['map_center']=[(float(xx[i])+.5)/W,(float(yy[i])+.5)/H]
    pairs=set()
    for y in range(0,H,256):
        a=newmap[y:min(H,y+257)]
        for l,r in [(a[:,:-1],a[:,1:]),(a[:-1],a[1:])]:
            m=(l>0)&(r>0)&(l!=r);pairs.update(map(int,np.unique(np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m]))))
    a,b=newmap[:,0],newmap[:,-1];m=(a>0)&(b>0)&(a!=b);pairs.update(map(int,np.minimum(a[m],b[m]).astype(np.uint32)*65536+np.maximum(a[m],b[m])))
    for pair in pairs:
        a,b=pair//65536,pair%65536;newps[str(a)]['neighbors'].append(b);newps[str(b)]['neighbors'].append(a)
    for p in newps.values():p['neighbors'].sort()
    for r in regions.values():
        largest=max(r['provinces'],key=lambda p:(bb[p-1][0].stop-bb[p-1][0].start)*(bb[p-1][1].stop-bb[p-1][1].start));r['map_center']=newps[str(largest)]['map_center']
    local=np.zeros(65536,np.uint8)
    for p in newps.values():local[p['id']]=p['local_index']
    for i in range(4):
        sl=np.s_[i//2*4096:(i//2+1)*4096,i%2*8192:(i%2+1)*8192];a=result[sl]
        rgb=np.stack([(a&255).astype(np.uint8),(a>>8).astype(np.uint8),local[newmap[sl]]],axis=-1);Image.fromarray(rgb).save(ROOT/f'assets/region_ids_{i}.png',optimize=True)
    for tag,c in world['countries'].items():
        ids=[r['id'] for r in regions.values() if r['owner']==tag];c['regions']=ids
        u,v=c['map_center'];rid=int(result[min(H-1,int(v*H)),int(u*W)%W]);rid=rid if rid in ids else max(ids,key=lambda s:regions[str(s)]['population']);c['capital']=rid
        if int(result[min(H-1,int(v*H)),int(u*W)%W]) not in ids:c['map_center']=regions[str(rid)]['map_center']
        assert sum(regions[str(s)]['population'] for s in ids)==c['population'],tag
    registry=json.loads((SRC/'md_country_registry.json').read_text());registry.update({t:{k:c[k] for k in ['tag','name','outlook','color','cosmetic'] if k in c} for t,c in world['countries'].items()})
    world['country_registry']=registry;world['regions']=regions;world['scenario_id']='bunny_world_2000_0_1_7';world['schema_version']=7
    world['map']['cartography']='Natural Earth subdivisions grouped around MD state areas, with protected scenario control and core/claim profiles.'
    world['map']['regional_boundary_accuracy']='Approximate MD state coverage using adjacent geographic subdivisions. Sources with fewer subdivisions are combined only within identical territorial-rights profiles.'
    (ROOT/'data/world.json').write_text(json.dumps(world,ensure_ascii=False,separators=(',',':')));(ROOT/'data/provinces.json').write_text(json.dumps(newps,separators=(',',':')))
    np.savez_compressed(SRC/'grouped_atlas_017.npz',regions=result)
    report={'regions':len(regions),'mod_states':1250,'provinces':len(newps),'land_adjacency_edges':len(pairs),'population':sum(r['population'] for r in regions.values()),'rights_profiles':len(profiles)-1,'countries_with_claims':sorted({t for r in regions.values() for t in r['claims']}),'per_country':{t:{'mod':sum(r['owner']==t for r in old['regions'].values()),'geographic':len(c['regions'])} for t,c in world['countries'].items()}}
    (ROOT/'data/update_017_geography_report.json').write_text(json.dumps(report,indent=2));print('LAND_017_COMPLETE',len(regions),'regions',len(newps),'provinces',flush=True)
    return result,world

def build_seas(result,world):
    centers=json.loads((SRC/'md_centers.json').read_text());geo=[];source=[];seen=set()
    # Retain the source game's nonlinear cartography fit; oceans need the same
    # calibration as its land, with pole/dateline constraints and shoreline clip.
    for cap in json.loads((SRC/'capitals.json').read_text()):
        tag=next((t for t,c in world['countries'].items() if c['name']==cap['country']),None)
        if not tag or tag in seen or tag not in centers['countries']:continue
        u,v=centers['countries'][tag];gu=(cap['lon']+180)/360;gv=(90-cap['lat'])/180
        if abs(gu-u)>.16:continue
        geo.append([gu,gv]);source.append([u,v]);seen.add(tag)
    for gu in [0,.25,.5,.75,1]:
        for gv,sv in [(0,-.22),(1,1.48)]:geo.append([gu,gv]);source.append([gu,sv])
    for gv in [.15,.3,.5,.7,.85]:
        for gu in [0,1]:geo.append([gu,gv]);source.append([gu,gv*1.35-.18])
    geo=np.asarray(geo);source=np.asarray(source);transform=RBFInterpolator(geo,source,kernel='thin_plate_spline',smoothing=.00002)
    raw=np.asarray(Image.open(SRC/'md_sea_zones.png'),np.uint16);ww,hh=8192,4096
    gy,gx=np.mgrid[0:1:129j,0:1:257j];grid=transform(np.column_stack([gx.ravel(),gy.ravel()])).reshape(129,257,2)
    sea=np.zeros((hh,ww),np.uint16)
    for y in range(0,hh,128):
        yy,xx=np.mgrid[y:min(hh,y+128),0:ww];sx=map_coordinates(grid[:,:,0],[(yy+.5)/hh*128,(xx+.5)/ww*256],order=1);sy=map_coordinates(grid[:,:,1],[(yy+.5)/hh*128,(xx+.5)/ww*256],order=1)
        sea[y:y+len(yy)]=map_coordinates(raw,[sy*(raw.shape[0]-1),sx*(raw.shape[1]-1)],order=0,mode='constant',cval=0)
    # Fill only missing ocean samples, not existing named areas. The game clips
    # this separate water layer against the accurate land atlas when rendering.
    for y in range(0,hh,256):
        lo=max(0,y-512);hi=min(hh,y+768);a=sea[lo:hi];near=distance_transform_edt(a==0,return_distances=False,return_indices=True);fill=a[near[0],near[1]];out=sea[y:y+256];m=out==0;out[m]=fill[y-lo:y-lo+len(out)][m]
    if np.any(sea==0):
        iy,ix=np.nonzero(sea);tree=cKDTree(np.column_stack([iy,ix]));yy,xx=np.nonzero(sea==0);_,ind=tree.query(np.column_stack([yy,xx]));sea[yy,xx]=sea[iy[ind],ix[ind]]
    definitions=json.loads((SRC/'md_sea_zones.json').read_text());water=result[1::2,1::2]==0
    for sid,s in definitions.items():
        yy,xx=np.nonzero((sea==int(sid))&water)
        if not len(xx):continue
        if xx.max()-xx.min()>ww//2:
            use=xx<ww//2 if np.count_nonzero(xx<ww//2)>len(xx)/2 else xx>=ww//2;xx=xx[use];yy=yy[use]
        j=int(np.argmin((xx-xx.mean())**2+(yy-yy.mean())**2));s['map_center']=[(float(xx[j])+.75)/ww,(float(yy[j])+.75)/hh]
    definitions={s:q for s,q in definitions.items() if 'map_center' in q}
    # Source zones lost to geographic coast correction map to the nearest
    # surviving source zone. No owner or demographic fields belong to water.
    missing=~np.isin(sea,list(map(int,definitions)))
    if missing.any():
        near=distance_transform_edt(missing,return_distances=False,return_indices=True);sea[missing]=sea[near[0],near[1]][missing]
    edges=set()
    for a,b in [(sea[:,:-1],sea[:,1:]),(sea[:-1],sea[1:])]:
        m=a!=b;edges.update(map(int,np.unique(np.minimum(a[m],b[m]).astype(np.uint32)*256+np.maximum(a[m],b[m]))))
    for s in definitions.values():s['neighbors']=[]
    for e in edges:
        a,b=e//256,e%256
        if str(a) in definitions and str(b) in definitions:definitions[str(a)]['neighbors'].append(b);definitions[str(b)]['neighbors'].append(a)
    for s in definitions.values():s['neighbors']=sorted(set(s['neighbors']))
    rgb=np.stack([(sea&255).astype(np.uint8),(sea>>8).astype(np.uint8),np.zeros_like(sea,np.uint8)],axis=-1);Image.fromarray(rgb).save(ROOT/'assets/sea_ids.png',optimize=True)
    (ROOT/'data/sea_regions.json').write_text(json.dumps(definitions,ensure_ascii=False,separators=(',',':')))
    print('SEA_017_COMPLETE',len(definitions),'sea zones',flush=True)

if __name__=='__main__':
    if len(sys.argv)>1:import_reference(Path(sys.argv[1]))
    result,world=build_land();build_seas(result,world)
