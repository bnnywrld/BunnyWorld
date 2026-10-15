"""Conservative adjacent remote-cell merges using state density/city/coast buffers.
No detailed population grid is available; all classification is an explicit proxy.
"""
from pathlib import Path
import json,math,collections
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography';W,H=16384,8192
Image.MAX_IMAGE_PIXELS=None

def sphere(u,v):
    lon=(u-.5)*2*math.pi;lat=(.5-v)*math.pi
    return np.array([math.cos(lat)*math.sin(lon),math.sin(lat),math.cos(lat)*math.cos(lon)])

def main():
    world=json.load(open(SRC/'world_seed_020.json'));ps=json.load(open(SRC/'province_seed_020.json'));a=np.load(SRC/'grouped_atlas_020.npz')['regions'];pmap=np.load(SRC/'province_atlas_020.npz')['provinces']
    land=a[1::4,1::4]>0;near=distance_transform_edt(land,return_distances=False,return_indices=True);yy,xx=np.indices(land.shape);scale=np.cos((yy+.5)/land.shape[0]*math.pi-math.pi/2)
    coast=np.hypot((xx-near[1])*scale,yy-near[0])*40075.017/land.shape[1];del near,yy,xx,scale,land
    cities=json.load(open(ROOT/'data/cities.json'));tree=cKDTree(np.array([sphere((c['longitude']+180)/360,(90-c['latitude'])/180) for c in cities]));positions={int(k):sphere(*p['map_center']) for k,p in ps.items()}
    eligible={};before={t:sum(world['regions'][str(p['region'])]['owner']==t for p in ps.values()) for t in world['countries']}
    for region in world['regions'].values():
        tag=region['owner'];area=sum(ps[str(pid)]['area_km2'] for pid in region['provinces']);density=region['population']/max(1,area)
        for pid in region['provinces']:
            p=ps[str(pid)];u,v=p['map_center'];lat=90-v*180;lon=u*360-180
            if p['cities'] or p['buildings']:continue
            distance=tree.query(positions[pid])[0]*6371.0;shore=coast[min(2047,int(v*2048)),int(u*4096)%4096]
            target=0
            if tag=='GRN' and distance>90 and shore>30:target=25000
            sahara=tag in ['ALG','LBA','MAU','MAL','NGR','CHA','SUD','EGY'] and 18<lat<31 and -18<lon<35
            nile=tag in ['EGY','SUD'] and 29.5<lon<35
            if sahara and not nile and density<12 and distance>110 and shore>35:target=15000
            other=(tag in ['CAN','SOV'] and lat>55) or (tag=='AST' and -34<lat<-18 and 120<lon<142) or tag=='MON'
            if other and density<1.5 and distance>150 and shore>45:target=18000
            if target:eligible[pid]=target
    remap=np.arange(65536,dtype=np.uint16);remaining=set(eligible);merged=0;clusters=0
    while remaining:
        seed=min(remaining);remaining.remove(seed);group=[seed];area=ps[str(seed)]['area_km2'];target=eligible[seed];parent=ps[str(seed)]['region'];frontier=set(ps[str(seed)]['neighbors'])&remaining
        while frontier and area<target:
            options=[p for p in frontier if ps[str(p)]['region']==parent]
            if not options:break
            p=min(options,key=lambda p:float(np.sum((positions[p]-positions[seed])**2)))
            frontier.remove(p);remaining.remove(p);group.append(p);area+=ps[str(p)]['area_km2'];frontier|=set(ps[str(p)]['neighbors'])&remaining
        if len(group)>1:
            clusters+=1;merged+=len(group)-1
            for p in group[1:]:remap[p]=seed;del ps[str(p)]
            ps[str(seed)]['area_km2']=round(area,2);ps[str(seed)]['remote_merge_count']=len(group);ps[str(seed)]['size_class']='remote';ps[str(seed)]['remote_target_km2']=target
    pmap=remap[pmap];edges=set()
    for y in range(0,H,256):
        tile=pmap[y:min(H,y+257)]
        for l,r in [(tile[:,:-1],tile[:,1:]),(tile[:-1],tile[1:])]:
            m=(l>0)&(r>0)&(l!=r);edges.update(map(int,np.unique(np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m]))))
    l,r=pmap[:,0],pmap[:,-1];m=(l>0)&(r>0)&(l!=r);edges.update(map(int,np.unique(np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m]))))
    for p in ps.values():p['neighbors']=[]
    for e in edges:
        l,r=e//65536,e%65536;ps[str(l)]['neighbors'].append(r);ps[str(r)]['neighbors'].append(l)
    index=np.zeros((256,256,3),np.uint8);index[255,255]=[255,31,0]
    for region in world['regions'].values():
        region['provinces']=sorted(set(int(remap[p]) for p in region['provinces']))
        for i,pid in enumerate(region['provinces'],1):ps[str(pid)]['local_index']=i
    for p in ps.values():
        p['neighbors'].sort();index[p['id']//256,p['id']%256]=[p['region']&255,p['region']>>8,0]
    Image.fromarray(index).save(ROOT/'assets/province_index.png')
    for i in range(4):
        sl=np.s_[i//2*4096:(i//2+1)*4096,i%2*8192:(i%2+1)*8192];ids=pmap[sl].copy();ids[a[sl]==8191]=65535;Image.fromarray(np.stack([(ids&255).astype(np.uint8),(ids>>8).astype(np.uint8),np.zeros_like(ids,np.uint8)],-1)).save(ROOT/f'assets/region_ids_{i}.png',optimize=True)
    world['scenario_id']='bunny_world_2000_0_1_11';world['map']['province_geometry']='3000 km2 standard cells; conservative adjacent remote merges with protected city/coastal buffers; density is a state-level proxy.'
    (ROOT/'data/world.json').write_text(json.dumps(world,ensure_ascii=False,separators=(',',':')));(ROOT/'data/provinces.json').write_text(json.dumps(ps,ensure_ascii=False,separators=(',',':')));np.savez_compressed(SRC/'province_atlas_021.npz',provinces=pmap)
    report={'before':sum(before.values()),'after':len(ps),'removed_cells':merged,'remote_clusters':clusters,'eligible_remote_cells':len(eligible),'protected_city_provinces':sum(bool(p['cities']) for p in ps.values()),'per_country':{t:{'before':before[t],'after':sum(world['regions'][str(p['region'])]['owner']==t for p in ps.values())} for t in before},'limits':'State-level population density and bundled city/coastal buffers are conservative proxies, not a detailed population-density grid.'}
    (ROOT/'data/remote_provinces_021_report.json').write_text(json.dumps(report,indent=2));print('REMOTE_021_PASS',len(ps),merged,{t:report['per_country'][t] for t in ['GRN','ALG','KOR','LUX','CAN','SOV','AST']},flush=True)

if __name__=='__main__':main()
