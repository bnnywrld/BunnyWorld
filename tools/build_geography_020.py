"""Common-area provinces with city annotations; geographic Chishima/Sakhalin repair.
Prepared 0.1.9 atlas is immutable input. Province IDs use the existing RG atlas,
with a tiny province-to-state lookup, removing the 255-cell per-state limit.
"""
from pathlib import Path
import json,collections,math
import numpy as np
from PIL import Image
from scipy.ndimage import find_objects
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography';W,H=16384,8192;KM=40075.017/W;TARGET=3000.
Image.MAX_IMAGE_PIXELS=None

def split_islands(a,w):
    old=json.load(open(SRC/'world_seed_015.json'));rs=w['regions'];south=next(r for r in rs.values() if 690 in r['source_states'] and 1168 in r['source_states']);sak=next(r for r in rs.values() if r['source_states']==[691])
    sid=south['id'];kid=sak['id'];nid=max(map(int,rs))+1
    yy,xx=np.nonzero((a==sid)|(a==kid));lon=(xx+.5)/W*360-180;lat=90-(yy+.5)/H*180
    # Sakhalin's island is west of the Kuril arc. The northern/southern arc
    # boundary is the open-water gap between Iturup and Urup, near 45.5 N.
    karafuto=(lon<145.0)&(lat>45.5);north=(~karafuto)&(lat>=45.5);southmask=(~karafuto)&(lat<45.5)
    before=a[yy,xx].copy();a[yy,xx]=np.where(karafuto,kid,np.where(north,nid,sid))
    # Reconstitute each of the three source state totals and territorial rights.
    rights=json.load(open(SRC/'md_state_rights.json'))
    for rid,source,name in [(kid,691,'Karafuto'),(sid,1168,'South Chishima Islands'),(nid,690,'North Chishima Islands')]:
        base=old['regions'][str(source)];q=rights[str(source)]
        rs[str(rid)]={'id':rid,'name':name,'owner':base['owner'],'population':base['population'],'buildings':base['buildings'].copy(),'provinces':[],'cores':q['cores'],'claims':q['claims'],'source_states':[source],'geographic_divisions':['Sakhalin' if source==691 else name],'population_source':'Supplied MD starting state total; geographic Sakhalin/Kuril island split.'}
    for c in w['countries'].values():c['regions']=sorted(r['id'] for r in rs.values() if r['owner']==c['tag'])
    return {'karafuto_state':kid,'south_chishima_state':sid,'north_chishima_state':nid,'returned_to_karafuto_pixels':int(np.count_nonzero(karafuto&(before==sid))),'removed_from_karafuto_pixels':int(np.count_nonzero((~karafuto)&(before==kid))),'north_south_gap_latitude':45.5}

def build(a,w):
    boxes=find_objects(a,max_label=8191);pmap=np.zeros_like(a);ps={};weights_y=np.cos((np.arange(H)+.5)/H*math.pi-math.pi/2)*KM*KM
    for sid,r in w['regions'].items():
        rid=int(sid);bb=boxes[rid-1];yy,xx=np.nonzero(a[bb]==rid);yy+=bb[0].start;xx+=bb[1].start
        x=xx.astype(float);cross=x.max()-x.min()>W//2
        if cross:x[x<W//2]+=W
        scale=max(.015,math.cos((yy.mean()+.5)/H*math.pi-math.pi/2));points=np.column_stack([x*scale,yy]);weights=weights_y[yy];area=weights.sum();n=min(len(xx),max(1,round(area/TARGET)))
        sample=points[::max(1,len(points)//16000)];chosen=[sample[np.argmin(np.sum((sample-sample.mean(0))**2,axis=1))]];d=np.sum((sample-chosen[0])**2,axis=1)
        for _ in range(1,n):
            j=np.argmax(d);chosen.append(sample[j]);d=np.minimum(d,np.sum((sample-sample[j])**2,axis=1))
        seeds=np.array(chosen);tree=cKDTree(points)
        for _ in range(5):
            _,cell=cKDTree(seeds).query(points);counts=np.bincount(cell,weights=weights,minlength=n)
            centers=np.column_stack([np.bincount(cell,weights=points[:,i]*weights,minlength=n)/np.maximum(counts,1e-12) for i in range(2)])
            _,near=tree.query(centers);seeds=points[near]
        _,cell=cKDTree(seeds).query(points);r['provinces']=[]
        for i in range(n):
            indexes=np.flatnonzero(cell==i)
            if not len(indexes):continue
            pid=len(ps)+1;assert pid<65535,'Province encoding exhausted';local=len(r['provinces'])+1;r['provinces'].append(pid);pmap[yy[indexes],xx[indexes]]=pid
            j=indexes[np.argmin(np.sum((points[indexes]-seeds[i])**2,axis=1))]
            ps[str(pid)]={'id':pid,'region':rid,'local_index':local,'map_center':[(float(xx[j])+.5)/W,(float(yy[j])+.5)/H],'area_km2':round(float(weights[indexes].sum()),2),'neighbors':[],'buildings':{},'kind':'rural','cities':[]}
        p=max(r['provinces'],key=lambda p:ps[str(p)]['area_km2']);r['map_center']=ps[str(p)]['map_center']
        if rid%100==0:print('COMMON_AREA_PROVINCES',rid,len(ps),flush=True)
    # City markers annotate their actual containing province. No extra seeds,
    # radius carving or smaller city quota. Several cities can share one cell.
    placed=0;skipped=[]
    for city in json.load(open(ROOT/'data/cities.json')):
        x=int((city['longitude']+180)/360*W)%W;y=min(H-1,int((90-city['latitude'])/180*H));pid=int(pmap[y,x])
        if not pid or w['regions'][str(ps[str(pid)]['region'])]['owner']!=city.get('country'):
            t=max(0,y-4);b=min(H,y+5);cols=np.arange(x-4,x+5)%W;tile=pmap[t:b][:,cols];yy,xx=np.nonzero(tile)
            candidates=[i for i in range(len(xx)) if w['regions'][str(ps[str(int(tile[yy[i],xx[i]]))]['region'])]['owner']==city.get('country')]
            if not candidates:skipped.append(city['name']);continue
            i=min(candidates,key=lambda i:(yy[i]+t-y)**2+(int(cols[xx[i]])-x)**2);pid=int(tile[yy[i],xx[i]])
        p=ps[str(pid)];p['kind']='city';p['cities'].append(city['name']);placed+=1
        if float(city.get('population_rank',0))>=float(p.get('city_population_rank',-1)):p['name']=city['name'];p['city_population_rank']=city.get('population_rank',0)
    edges=set()
    for y in range(0,H,256):
        tile=pmap[y:min(H,y+257)]
        for l,r in [(tile[:,:-1],tile[:,1:]),(tile[:-1],tile[1:])]:
            m=(l>0)&(r>0)&(l!=r);edges.update(map(int,np.unique(np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m]))))
    l,r=pmap[:,0],pmap[:,-1];m=(l>0)&(r>0)&(l!=r);edges.update(map(int,np.unique(np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m]))))
    for e in edges:
        l,r=e//65536,e%65536;ps[str(l)]['neighbors'].append(r);ps[str(r)]['neighbors'].append(l)
    index=np.zeros((256,256,3),np.uint8);index[255,255]=[255,31,0]
    for p in ps.values():
        p['neighbors'].sort();index[p['id']//256,p['id']%256]=[p['region']&255,p['region']>>8,0]
    Image.fromarray(index).save(ROOT/'assets/province_index.png')
    for i in range(4):
        sl=np.s_[i//2*4096:(i//2+1)*4096,i%2*8192:(i%2+1)*8192];ids=pmap[sl].copy();ids[a[sl]==8191]=65535
        Image.fromarray(np.stack([(ids&255).astype(np.uint8),(ids>>8).astype(np.uint8),np.zeros_like(ids,np.uint8)],-1)).save(ROOT/f'assets/region_ids_{i}.png',optimize=True)
    np.savez_compressed(SRC/'province_atlas_020.npz',provinces=pmap)
    (ROOT/'data/provinces.json').write_text(json.dumps(ps,ensure_ascii=False,separators=(',',':')))
    stats={}
    for tag,c in w['countries'].items():
        ids=[p for p in ps.values() if w['regions'][str(p['region'])]['owner']==tag]
        stats[tag]={'count':len(ids),'median_area_km2':round(float(np.median([p['area_km2'] for p in ids])),2)}
        u,v=c['map_center'];rid=int(a[min(H-1,int(v*H)),int(u*W)%W])
        if rid not in c['regions']:c['map_center']=w['regions'][str(c['capital'])]['map_center']
    return {'count':len(ps),'target_area_km2':TARGET,'city_containing_provinces':sum(p['kind']=='city' for p in ps.values()),'cities_placed':placed,'skipped_city_markers':skipped,'per_country':stats,'millennium_dawn_land_provinces':13222,'previous_land_provinces':15350,'largest_state_province_count':max(len(r['provinces']) for r in w['regions'].values())}

if __name__=='__main__':
    w=json.load(open(SRC/'world_seed_019.json'));a=np.load(SRC/'grouped_atlas_019.npz')['regions'].copy()
    report={'version':'0.1.10','islands':split_islands(a,w)};report['provinces']=build(a,w)
    w['scenario_id']='bunny_world_2000_0_1_10';w['map']['province_encoding']='RG global 16-bit province ID; 0 water; 65535 Antarctica. Province index RG stores parent state.';w['map']['province_geometry']='Shared 3000 km2 target for all land cells; cities annotate containing cells without changing their size.'
    (ROOT/'data/world.json').write_text(json.dumps(w,ensure_ascii=False,separators=(',',':')));np.savez_compressed(SRC/'grouped_atlas_020.npz',regions=a)
    (ROOT/'data/update_020_report.json').write_text(json.dumps(report,indent=2));print('GEOGRAPHY_020_COMPLETE',len(w['regions']),report['provinces']['count'],report['islands'],flush=True)
