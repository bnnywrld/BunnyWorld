"""Register actual MD provinces to accepted globe State geometry; offline only.
Usage: python tools/build_provinces_0202.py path/to/bunnyversion.zip
The State mask is authoritative: this never imports the mod's political setup.
"""
from pathlib import Path
import sys, zipfile, io, re, json, os
import numpy as np
from PIL import Image
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates, find_objects, distance_transform_edt
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography'
world=json.load(open(ROOT/'data/world.json'));cities=json.load(open(ROOT/'data/cities.json'))
regions=np.load(SRC/'grouped_atlas_022r2.npz')['regions'];H,W=regions.shape
z=zipfile.ZipFile(sys.argv[1]);prefix=next(n[:-len('map/provinces.bmp')] for n in z.namelist() if n.endswith('map/provinces.bmp'))
rgb=np.array(Image.open(io.BytesIO(z.read(prefix+'map/provinces.bmp'))),dtype=np.uint32)
lut=np.zeros(1<<24,np.uint16);land=[]
for line in z.read(prefix+'map/definition.csv').decode('utf-8-sig').splitlines():
    f=line.split(';')
    if len(f)>=5 and f[0].isdigit():
        p,r,g,b=map(int,f[:4]);lut[r+(g<<8)+(b<<16)]=p
        if p and f[4]=='land':land.append(p)
md=lut[rgb[:,:,0]+(rgb[:,:,1]<<8)+(rgb[:,:,2]<<16)];del rgb,lut
source_to_state={int(s):int(r['id']) for r in world['regions'].values() for s in r.get('source_states',[r['id']])}
pg=np.zeros(65536,np.uint16)
for name in z.namelist():
    if name.startswith(prefix+'history/states/') and name.endswith('.txt'):
        txt=re.sub(r'#[^\n]*','',z.read(name).decode('utf-8-sig',errors='replace'))
        sid=re.search(r'\bid\s*=\s*(\d+)',txt);body=re.search(r'\bprovinces\s*=\s*\{([^}]+)\}',txt)
        if sid and body:
            rid=source_to_state.get(int(sid[1]),0)
            for p in re.findall(r'\d+',body[1]):pg[int(p)]=rid
is_land=np.zeros(65536,bool);is_land[land]=True;pg[~is_land]=0
md_state=pg[md];md[md_state==0]=0
active=np.array(sorted(set(land)&set(np.unique(md))),dtype=int)
def centres(a,n):
    h,w=a.shape;count=np.bincount(a.ravel(),minlength=n);x=np.zeros(n);y=np.zeros(n)
    for top in range(0,h,128):
        block=a[top:top+128];x+=np.bincount(block.ravel(),weights=np.broadcast_to((np.arange(w)+.5)/w,block.shape).ravel(),minlength=n)
        y+=np.bincount(block.ravel(),weights=np.broadcast_to((np.arange(top,top+len(block))+.5)[:,None]/h,block.shape).ravel(),minlength=n)
    return np.column_stack([x/np.maximum(count,1),y/np.maximum(count,1)]),count
mc,ma=centres(md_state,8192);gc,ga=centres(regions[::4,::4],8192);pc,_=centres(md,65536)
ids=[int(r) for r in world['regions'] if ma[int(r)] and ga[int(r)]]
print("REGISTRATION_INPUTS",prefix,len(active),len(ids),len(np.unique(md_state)),flush=True)
seen=set();keep=[]
for rid in sorted(ids,key=lambda r:-ga[r]):
    key=tuple(np.round(gc[rid]*100000).astype(int))
    if key not in seen:keep.append(rid);seen.add(key)
print("KEEP",len(keep),gc[ids[:10]],flush=True)
fit=RBFInterpolator(gc[keep],mc[keep],neighbors=40,kernel='thin_plate_spline',smoothing=.000002)
inverse=RBFInterpolator(mc[keep],gc[keep],neighbors=40,kernel='thin_plate_spline',smoothing=.000002)
yy,xx=np.mgrid[0:1:257j,0:1:513j];coarse=fit(np.column_stack([xx.ravel(),yy.ravel()])).reshape(257,513,2)
mapped=np.zeros((H,W),np.uint16)
for top in range(0,H,64):
    height=min(64,H-top);gy,gx=np.broadcast_arrays((np.arange(top,top+height)+.5)[:,None]/H*256,(np.arange(W)+.5)[None,:]/W*512)
    uv=np.array([map_coordinates(coarse[:,:,i],[gy,gx],order=1,mode='nearest') for i in [1,0]])
    sample=map_coordinates(md,[uv[0]*md.shape[0]-.5,uv[1]*md.shape[1]-.5],order=0,mode='constant',cval=0)
    rr=regions[top:top+height];mapped[top:top+height]=np.where((rr>0)&(rr==pg[sample]),sample,0)
    if top%1024==0:print('REGISTER',top,H,flush=True)
boxes=find_objects(regions,max_label=8191);source_boxes=find_objects(md_state,max_label=8191)
report={'source_land_definitions':len(active),'state_local_fits':[],'restored_small_labels':0,'states':[]}
for key,r in world['regions'].items():
    rid=int(key);bb=boxes[rid-1]
    if bb is None:raise ValueError('Missing accepted State '+key)
    mask=regions[bb]==rid;view=mapped[bb];valid=mask&(view>0)
    sb=source_boxes[rid-1]
    if valid.sum()<mask.sum()*.65 and sb:
        hh,ww=mask.shape
        sy=(np.arange(hh)+.5)/hh*(sb[0].stop-sb[0].start)+sb[0].start-.5
        sx=(np.arange(ww)+.5)/ww*(sb[1].stop-sb[1].start)+sb[1].start-.5
        sy,sx=np.broadcast_arrays(sy[:,None],sx[None,:]);sample=map_coordinates(md,[sy,sx],order=0,mode='nearest')
        good=mask&(pg[sample]==rid)
        if good.sum()>valid.sum():view[mask]=np.where(good,sample,0)[mask];valid=good;report['state_local_fits'].append(rid)
    candidates=active[pg[active]==rid];missing=[int(p) for p in candidates if p not in np.unique(view[mask])]
    y,x=np.nonzero(mask);tree=None;used=set()
    if missing:
        tree=cKDTree(np.column_stack([(x+bb[1].start+.5)/W,(y+bb[0].start+.5)/H]))
        guesses=inverse(pc[missing])
        for p,point in zip(missing,guesses):
            _,near=tree.query(point,k=min(40,len(y)))
            for j in np.atleast_1d(near):
                pos=(int(y[j]),int(x[j]))
                if pos not in used:view[pos]=p;used.add(pos);report['restored_small_labels']+=1;break
    valid=mask&(view>0)
    if not valid.any():raise ValueError('No reference provinces for State '+key)
    native=int(valid.sum());nearest=distance_transform_edt(~valid,return_distances=False,return_indices=True)
    fill=mask&~valid;view[fill]=view[tuple(nearest[:,fill])]
    report['states'].append({'state':rid,'native_fraction':native/int(mask.sum())})
    print('STATE',rid,'native',round(native/int(mask.sum()),3),flush=True) if rid%100==0 else None
provinces={};atlas=np.zeros_like(mapped);next_id=1
weights=np.cos(np.deg2rad(90-(np.arange(H)+.5)/H*180))*(40075.017/W)**2
for key,r in world['regions'].items():
    rid=int(key);bb=boxes[rid-1];mask=regions[bb]==rid;view=mapped[bb];out=atlas[bb];r['provinces']=[]
    assert np.all(view[mask]>0), ('unfilled State',rid)
    for local,p in enumerate(sorted(np.unique(view[mask])),1):
        y,x=np.nonzero(mask&(view==p));pid=next_id;next_id+=1;out[y,x]=pid;r['provinces'].append(pid)
        provinces[str(pid)]={'id':pid,'region':rid,'local_index':local,'source_md_province':int(p),'map_center':[float((x.mean()+bb[1].start+.5)/W),float((y.mean()+bb[0].start+.5)/H)],'area_km2':round(float(weights[y+bb[0].start].sum()),2),'neighbors':[],'buildings':{},'kind':'rural','cities':[]}
micro=json.load(open(ROOT/'data/microstate_geometry.json'));micro['province']=world['regions'][str(micro['state'])]['provinces'][0]
u,v=micro['center_uv'];cy,cx=int(v*H),int(u*W);near=atlas[max(0,cy-6):cy+7,max(0,cx-6):cx+7];allowed=[p for p in near.ravel() if p and provinces[str(p)]['region']==micro['host_state']]
micro['host_province']=int(np.bincount(allowed).argmax());p=provinces[str(micro['province'])];p['area_km2']=.44;p['map_center']=[u,v]
(ROOT/'data/microstate_geometry.json').write_text(json.dumps(micro,indent=2))
for c in cities:
    y=int((90-c['latitude'])/180*H);x=int((c['longitude']+180)/360*W)%W;pid=int(atlas[min(H-1,max(0,y)),x])
    if not pid:
        small=atlas[max(0,y-6):min(H,y+7),max(0,x-6):min(W,x+7)];ys,xs=np.nonzero(small)
        if len(ys):j=np.argmin((ys+max(0,y-6)-y)**2+(xs+max(0,x-6)-x)**2);pid=int(small[ys[j],xs[j]])
    if pid:provinces[str(pid)]['cities'].append(c['name']);c['country']=world['regions'][str(provinces[str(pid)]['region'])]['owner']
edges=set()
for top in range(0,H,128):
    a=atlas[top:top+128];b=np.roll(a,-1,axis=1);pair=np.column_stack([a.ravel(),b.ravel()]);pair=pair[(pair[:,0]>0)&(pair[:,1]>0)&(pair[:,0]!=pair[:,1])];edges.update(map(tuple,np.unique(np.sort(pair,axis=1),axis=0)))
    a=atlas[top:min(H-1,top+128)];b=atlas[top+1:min(H,top+129)];pair=np.column_stack([a.ravel(),b.ravel()]);pair=pair[(pair[:,0]>0)&(pair[:,1]>0)&(pair[:,0]!=pair[:,1])];edges.update(map(tuple,np.unique(np.sort(pair,axis=1),axis=0)))
for a,b in edges:provinces[str(a)]['neighbors'].append(int(b));provinces[str(b)]['neighbors'].append(int(a))
for p in provinces.values():p['neighbors'].sort()
def png_atomic(image,path):
    buf=io.BytesIO();image.save(buf,format='PNG',compress_level=6);temp=path.with_suffix('.png.new')
    with temp.open('wb') as f:f.write(buf.getvalue());f.flush();os.fsync(f.fileno())
    os.replace(temp,path)
for i in range(4):
    a=atlas[(i//2)*(H//2):(i//2+1)*(H//2),(i%2)*(W//2):(i%2+1)*(W//2)];rgb=np.zeros((*a.shape,3),np.uint8);rgb[:,:,0]=a&255;rgb[:,:,1]=a>>8
    png_atomic(Image.fromarray(rgb),ROOT/'assets'/f'region_ids_{i}.png')
index=np.zeros((65536,3),np.uint8)
for p in provinces.values():index[p['id'],:2]=[p['region']&255,p['region']>>8]
index[65535,:2]=[255,31];png_atomic(Image.fromarray(index.reshape(256,256,3)),ROOT/'assets/province_index.png')
for name in ['province_atlas_0202','province_atlas_022r2']:np.savez_compressed(SRC/(name+'.npz'),provinces=atlas)
world['scenario_id']='bunny_world_2000_0_2_0_2';world['map']['province_geometry']='Actual Millennium Dawn provinces registered to accepted year-2000 State geometry; polar/local coastline adaptations.'
report['final_provinces']=len(provinces);report['absent_source_labels']=sorted(set(active)-set(p['source_md_province'] for p in provinces.values()))
for name,data in [('world',world),('provinces',provinces),('cities',cities),('province_conversion_0202',report)]:
    (ROOT/'data'/f'{name}.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'),default=lambda v:v.item()))
print('PROVINCES_0202_COMPLETE',len(provinces),'missing',len(report['absent_source_labels']),flush=True)
