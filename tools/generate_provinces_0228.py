"""Independent terrain-guided movement tiles inside immutable .28 states.

No population is stored on provinces. Output IDs are new scenario identities.
Local Lambert equal-area growth, settlement seeds, continuous geographic costs,
multi-label curvature smoothing and native-grid connectivity reconciliation.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,json,math,time
import numpy as np
from PIL import Image
from scipy.ndimage import find_objects,gaussian_filter,label,distance_transform_edt,binary_dilation
from scipy.spatial import cKDTree
from pyproj import Transformer
from skimage.graph import MCP_Geometric
from skimage.segmentation import watershed
R=Path(__file__).resolve().parents[1];C=R/'tools/cartography';W,H=16384,8192;EARTH=6371.0088
AREA=(EARTH*2*np.pi/W)*(EARTH*np.pi/H)*np.cos((np.arange(H)+.5)/H*np.pi-np.pi/2)
Image.MAX_IMAGE_PIXELS=None
read=lambda p:json.loads((R/p).read_text())
def write(p,d): (R/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
def state_crop(a,bb,sid):
    top,left=bb[0].start,bb[1].start;part=a[bb]==sid
    if part.shape[1]>W*.55:
        cols=np.flatnonzero(part.any(0))+left;gaps=np.diff(np.r_[cols,cols[0]+W]);gap=int(gaps.argmax());left=int(cols[(gap+1)%len(cols)]);part=a[bb[0],(np.arange(W-int(gaps[gap])+1)+left)%W]==sid
    return top,left,part
def rounded_partition(codes,mask,anchors,sigma=1.1):
    """Diffuse competing region indicators, preserving seed anchors/count."""
    best=np.full(codes.shape,-1.,np.float32);out=np.zeros_like(codes)
    for code in np.unique(codes[mask]):
        if not code:continue
        score=gaussian_filter((codes==code).astype(np.float32),sigma,mode='nearest')
        win=mask&(score>best);out[win]=code;best[win]=score[win]
    for y,x,code in anchors:out[y,x]=code
    return out
def _native_repair_once(codes,mask,city_codes):
    """No isolated inland scraps; disconnected original islands may share IDs."""
    islands,_=label(mask,np.ones((3,3),np.uint8));repairs=0
    boxes=find_objects(codes,max_label=int(codes.max()))
    for code,bb in enumerate(boxes,1):
        if bb is None:continue
        bb=tuple(slice(max(0,b.start-1),min(codes.shape[j],b.stop+1))for j,b in enumerate(bb));cell=codes[bb];pieces,n=label(cell==code,np.ones((3,3),np.uint8))
        if n<=1:continue
        sizes=np.bincount(pieces.ravel());keep=int(np.argmax(sizes[1:])+1)
        # Keep one component on every original island occupied by this ID.
        by_island={}
        for j in range(1,n+1):
            yy,xx=np.nonzero(pieces==j);island=int(islands[bb][yy[0],xx[0]])
            if island not in by_island or sizes[j]>sizes[by_island[island]]:by_island[island]=j
        for j in range(1,n+1):
            if j in by_island.values():continue
            part=pieces==j;ring=binary_dilation(part,structure=np.ones((3,3),bool))&~part;neighbors=cell[ring];neighbors=neighbors[(neighbors>0)&(neighbors!=code)]
            if not len(neighbors):continue
            dest=int(np.bincount(neighbors).argmax());cell[part]=dest;repairs+=int(part.sum())
    return codes,repairs
def native_repair(codes,mask,city_codes):
    total=0
    # Recompute bounding boxes after absorption: a neighboring province can
    # acquire pixels outside the bounding box it had at the start of a pass.
    for _ in range(5):
        codes,changed=_native_repair_once(codes,mask,city_codes);total+=changed
        if not changed:break
    return codes,total
def create_state(sid,state,a,bb,count,elev,rivers,lc,cities):
    top,left,mask_native=state_crop(a,bb,sid);ly,lx=np.nonzero(mask_native);yy=ly+top;xx=(lx+left)%W
    lon=(xx+.5)/W*360-180;lat=90-(yy+.5)/H*180;area=float(AREA[yy].sum())
    if count==1:
        return top,left,mask_native,np.where(mask_native,1,0).astype(np.int32),{'grid_km':0,'city_codes':{},'repairs':0,'width_exceptions':[]}
    zlon=np.deg2rad(lon);lon0=float(np.rad2deg(np.arctan2(np.sin(zlon).mean(),np.cos(zlon).mean())));lat0=float(np.mean(lat))
    proj=Transformer.from_crs('EPSG:4326',f'+proj=laea +lat_0={lat0:.8f} +lon_0={lon0:.8f} +datum=WGS84 +units=km',always_xy=True)
    inv=Transformer.from_crs(proj.target_crs,'EPSG:4326',always_xy=True);px,py=proj.transform(lon,lat);points=np.column_stack([px,py])
    step=max(.75,min(3.5,math.sqrt(area/count)/18));x0,y0=px.min()-step*3,py.min()-step*3
    ix=np.floor((px-x0)/step).astype(int);iy=np.floor((py-y0)/step).astype(int);shape=(int(iy.max()+4),int(ix.max()+4))
    gy,gx=np.indices(shape);glon,glat=inv.transform(x0+(gx+.5)*step,y0+(gy+.5)*step)
    nx=(np.floor((glon+180)/360*W).astype(int))%W;ny=np.clip(np.floor((90-glat)/180*H).astype(int),0,H-1)
    mask=a[ny,nx]==sid
    # Include every native footprint sample, including narrow natural coast.
    mask[iy,ix]=True
    er=np.clip((ny*elev.shape[0]//H),0,elev.shape[0]-1);ec=np.clip((nx*elev.shape[1]//W),0,elev.shape[1]-1)
    height=gaussian_filter(np.maximum(elev[er,ec],0).astype(np.float32),max(.8,5/step))
    slope=np.hypot(*np.gradient(height))/step
    river=gaussian_filter(rivers[er,ec].astype(np.float32),max(.65,3/step));relief=np.clip(slope/90,0,1.8)
    # Broad, continuous variations avoid rectilinear watershed/cost cells.
    wave=.055*(np.sin((x0+gx*step)/73+np.cos((y0+gy*step)/151))+np.sin((y0+gy*step)/97+np.sin((x0+gx*step)/113)))
    cost=1.1+relief*.45+river*2.8+wave;cost[~mask]=np.inf
    components,ncomp=label(mask,np.ones((3,3),np.uint8))
    # Tiny disconnected source pieces share a province; they must never win
    # a farthest-point seed just because they are distant from the mainland.
    native_components=components[iy,ix];component_area=np.bincount(native_components,weights=AREA[yy])
    threshold=max(400.,min(2000.,area/count*.35));eligible_components=set(np.flatnonzero(component_area>=threshold))-{0}
    eligible_components.add(int(np.argmax(component_area[1:])+1))
    eligible=np.flatnonzero(np.isin(native_components,list(eligible_components)))
    tree=cKDTree(points[eligible]);samples=eligible[::max(1,len(eligible)//25000)];sp=points[samples]
    def nearest_point(q):return int(eligible[int(tree.query(q)[1])])
    # Settlement seeds improve location. Density influences distribution only;
    # these are geometric hints, never resident accounts on movement tiles.
    local_cities=[];groups=set();seeds=[];city_seed={};spacing=max(8.,math.sqrt(area/count)*.4)
    for city in sorted(cities,key=lambda c:-c.get('population_rank',0)):
        group=city.get('urban_group')or city['name']
        if group in groups:continue
        groups.add(group);q=np.array(proj.transform(city['longitude'],city['latitude']));j=nearest_point(q)
        if np.linalg.norm(points[j]-q)>80:continue
        if seeds and min(np.linalg.norm(points[j]-points[k])for k in seeds)<spacing:continue
        local_cities.append((j,city));seeds.append(j)
        if city.get('population_rank',0)>=1000000:city_seed[len(seeds)]=city
        if len(seeds)>=max(1,min(count//2,16)):break
    if not seeds:
        center=points[eligible].mean(0);seeds=[nearest_point(center)]
    distance=np.min(np.sum((sp[:,None,:]-points[seeds][None,:,:])**2,axis=2),axis=1)
    while len(seeds)<count:
        j=int(samples[np.argmax(distance)]);seeds.append(j);distance=np.minimum(distance,np.sum((sp-points[j])**2,axis=1))
    # Three constrained centroid relaxation passes give compact interiors.
    fixed=len(local_cities)
    for _ in range(3):
        near=cKDTree(points[seeds]).query(sp)[1]
        for k in range(fixed,len(seeds)):
            cell=sp[near==k]
            if len(cell):seeds[k]=nearest_point(cell.mean(0))
    # Give large original islands a seed by moving an unneeded seed, never by
    # exceeding the reviewed state/country/global allocation.
    components,ncomp=label(mask,np.ones((3,3),np.uint8));sizes=np.bincount(components.ravel());seeded=Counter(int(components[iy[j],ix[j]])for j in seeds)
    for comp in sorted(range(1,ncomp+1),key=lambda c:-sizes[c]):
        if sizes[comp]*step**2<max(400,area/count*.35)or seeded[comp]:continue
        movable=[k for k in range(fixed,len(seeds))if seeded[int(components[iy[seeds[k]],ix[seeds[k]]])]>1]
        if not movable:break
        candidates=np.flatnonzero(components[iy,ix]==comp)
        if not len(candidates):continue
        k=movable[-1];seeded[int(components[iy[seeds[k]],ix[seeds[k]]])]-=1;seeds[k]=int(candidates[len(candidates)//2]);seeded[comp]+=1
    # Distinct native seeds can alias one local grid cell; choose another cell.
    markers=np.zeros(shape,np.int32);anchor=[]
    for k,j in enumerate(seeds,1):
        y,x=iy[j],ix[j]
        if markers[y,x]:
            good=np.flatnonzero((markers[iy,ix]==0));j=int(good[np.argmin(np.sum((points[good]-points[j])**2,axis=1))]);y,x=iy[j],ix[j]
        markers[y,x]=k;anchor.append((int(y),int(x),k))
    dist,_=MCP_Geometric(cost,fully_connected=True).find_costs(np.array([(y,x)for y,x,_ in anchor]))
    reached=mask&np.isfinite(dist);grown=watershed(np.where(reached,dist,0),markers,mask=reached,connectivity=2)
    missing=mask&(grown==0)
    if missing.any():
        near=distance_transform_edt(grown==0,return_distances=False,return_indices=True);grown[missing]=grown[tuple(near[:,missing])]
    for _ in range(2):grown=rounded_partition(grown,mask,anchor,max(.9,4/step))
    # Explicit city tile: connected sampled ESA urban footprint near the seed,
    # grown modestly for source resolution, not a huge radial hinterland tile.
    city_codes={}
    urban=(lc[ny//2,nx//2,0]==195)&(lc[ny//2,nx//2,1]==20)
    for code,city in city_seed.items():
        sy,sx=anchor[code-1][:2];urban_near=urban&mask&(((gx-sx)*step)**2+((gy-sy)*step)**2<=80**2)
        urban_near=binary_dilation(urban_near,iterations=1)&mask
        comps,n=label(urban_near,np.ones((3,3),np.uint8))
        if not n:continue
        uy,ux=np.nonzero(urban_near);k=int(np.argmin((uy-sy)**2+(ux-sx)**2));component=comps[uy[k],ux[k]]
        footprint=comps==component
        if footprint.sum()*step**2<25 or footprint.sum()>mask.sum()*.65:continue
        # Do not consume another seed or cut across a distinct state's border.
        for ay,ax,other in anchor:
            if other!=code:footprint[ay,ax]=False
        replacement=grown==code;grown[replacement]=0;remaining=(grown>0)
        if remaining.any():
            near=distance_transform_edt(~remaining,return_distances=False,return_indices=True);grown[replacement]=grown[tuple(near[:,replacement])]
        grown[footprint]=code;grown[sy,sx]=code;city_codes[code]=city['name']
    out=np.zeros(mask_native.shape,np.int32);out[ly,lx]=grown[iy,ix]
    out,repairs=native_repair(out,mask_native,city_codes)
    # Smoothing can eliminate a label only on very narrow inherited land.
    present=set(np.unique(out))-{0}
    if len(present)!=count:
        # Restore missing seeds with a small compact disk on their original
        # footprint; this cannot create territory outside the fixed state.
        for code in set(range(1,count+1))-present:
            j=seeds[code-1];d2=(px-px[j])**2+(py-py[j])**2;chosen=np.argsort(d2)[:max(1,min(12,len(px)//count//3))];out[ly[chosen],lx[chosen]]=code
        out,more=native_repair(out,mask_native,city_codes);repairs+=more
    assert len(set(np.unique(out))-{0})==count,(sid,count,len(set(np.unique(out))-{0}))
    return top,left,mask_native,out,{'grid_km':step,'city_codes':city_codes,'repairs':repairs,'width_exceptions':[]}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sample',nargs='*');args=ap.parse_args()
    w=read('data/world.json');assert w['version']=='0.2.0.28','Prepare the .28 state unions first';plan=read('data/province_plan_0228.json');a=np.load(C/'states_0228.npz')['regions'];boxes=find_objects(a,max_label=8191)
    elev=np.load(C/'etopo_021.npz')['meters'];lc=np.asarray(Image.open(C/'landcover_2000_0201.png'));rivers_path=C/'rivers_0228.npy'
    if not rivers_path.exists():
        from rasterio.features import rasterize
        from rasterio.transform import from_bounds
        features=json.loads((C/'rivers_0201.geojson').read_text())['features'];river=rasterize([(f['geometry'],1)for f in features if f['properties'].get('featurecla')=='River'],out_shape=elev.shape,transform=from_bounds(-180,-90,180,90,elev.shape[1],elev.shape[0]),dtype='uint8');np.save(rivers_path,river)
    rivers=np.load(rivers_path);cities=json.loads((C/'baseline_0227/cities.json').read_text());oldps=json.loads((C/'baseline_0227/provinces.json').read_text());by=defaultdict(list);merges={int(k):v for k,v in plan['merges'].items()}
    for c in cities:
        sid=oldps.get(str(c.get('province_id')),{}).get('region')
        if sid:by[merges.get(sid,sid)].append(c)
    atlas=np.zeros((H,W),np.uint16);atlas[a==8191]=65535;ps={};rows=[];start=time.time()
    for sid,s in sorted(w['regions'].items(),key=lambda x:int(x[0])):
        if args.sample and s['owner']not in args.sample:continue
        count=plan['budgets'][sid];top,left,mask,out,meta=create_state(int(sid),s,a,boxes[int(sid)-1],count,elev,rivers,lc,by[int(sid)])
        s['provinces']=[];cols=(np.arange(out.shape[1])+left)%W
        for code in sorted(set(np.unique(out))-{0}):
            ly,lx=np.nonzero(out==code);yy=ly+top;xx=cols[lx];pid=len(ps)+1;atlas[yy,xx]=pid
            # Focus on a resident identity pixel with a large interior radius.
            local=out==code;dist=distance_transform_edt(np.pad(local,1))[1:-1,1:-1];cy,cx=np.unravel_index(np.argmax(dist),dist.shape);focus=[(int(cols[cx])+.5)/W,(cy+top+.5)/H]
            city=meta['city_codes'].get(int(code));name=city if city else s['name']+' · Province '+str(len(s['provinces'])+1)
            ps[str(pid)]={'id':pid,'region':int(sid),'local_index':len(s['provinces'])+1,'name':name,'map_center':focus,'area_km2':round(float(AREA[yy].sum()),3),'neighbors':[],'buildings':{},'kind':'city'if city else'rural','cities':[],'urban_group':'','geometry_source':'Independent local equal-area terrain/river partition, curvature-smoothed within immutable state footprint'}
            s['provinces'].append(pid)
        rows.append({'state':int(sid),'name':s['name'],'country':s['owner'],'planned':count,'actual':len(s['provinces']),'grid_km':round(meta['grid_km'],3),'native_connectivity_pixels_reassigned':meta['repairs'],'city_tiles':list(meta['city_codes'].values())})
        if len(rows)%20==0:print('PROVINCES_0228',len(rows),'states',len(ps),'provinces',round(time.time()-start),'seconds',flush=True)
    if args.sample:
        np.savez_compressed(C/'sample_0228.npz',provinces=atlas);write('data/sample_provinces_0228.json',ps);return
    assert len(ps)==plan['global_planned']
    write('data/world.json',w);write('data/provinces.json',ps);write('data/province_generation_0228.json',{'version':'0.2.0.28','land_provinces':len(ps),'states':rows,'elapsed_seconds':round(time.time()-start),'population_on_provinces':False})
    np.savez_compressed(C/'province_atlas_0228.npz',provinces=atlas)
    for i in range(4):
        q=atlas[i//2*4096:(i//2+1)*4096,i%2*8192:(i%2+1)*8192]
        path=R/'assets'/f'region_ids_{i}.png';temp=path.with_suffix('.prepare-tmp')
        Image.fromarray(np.stack([(q&255).astype(np.uint8),(q>>8).astype(np.uint8),np.zeros_like(q,np.uint8)],-1)).save(temp,format='PNG')
        Image.open(temp).verify();temp.replace(path)
    print('PROVINCES_0228_COMPLETE',len(ps),'seconds',round(time.time()-start),flush=True)
if __name__=='__main__':main()
