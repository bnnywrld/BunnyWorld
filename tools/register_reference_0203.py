"""Register the mod bitmap with actual settlement anchors, never State boxes.
Prepared conversion input only; no runtime dependency on SciPy or the mod.
"""
from pathlib import Path
import io,json,re,sys,zipfile,unicodedata
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.interpolate import RBFInterpolator
from scipy.spatial import cKDTree

ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography'
z=zipfile.ZipFile(sys.argv[1]);prefix=next(n[:-len('map/provinces.bmp')] for n in z.namelist() if n.endswith('map/provinces.bmp'))
rgb=np.array(Image.open(io.BytesIO(z.read(prefix+'map/provinces.bmp'))),dtype=np.uint32)
lut=np.zeros(1<<24,np.uint16);land=[]
for line in z.read(prefix+'map/definition.csv').decode('utf-8-sig').splitlines():
 f=line.split(';')
 if len(f)>=5 and f[0].isdigit():
  p,r,g,b=map(int,f[:4]);lut[r+(g<<8)+(b<<16)]=p
  if p and f[4]=='land':land.append(p)
md=lut[rgb[:,:,0]+(rgb[:,:,1]<<8)+(rgb[:,:,2]<<16)];del lut,rgb
pg=np.zeros(65536,np.uint16)
for name in z.namelist():
 if name.startswith(prefix+'history/states/') and name.endswith('.txt'):
  txt=re.sub(r'#[^\n]*','',z.read(name).decode('utf-8-sig',errors='replace'))
  sid=re.search(r'\bid\s*=\s*(\d+)',txt);body=re.search(r'\bprovinces\s*=\s*\{([^}]+)\}',txt)
  if sid and body:
   for p in re.findall(r'\d+',body[1]):pg[int(p)]=int(sid[1])
is_land=np.zeros(65536,bool);is_land[land]=True;md[~is_land[md]]=0
h,w=md.shape;count=np.bincount(md.ravel(),minlength=65536)
pc=np.zeros((65536,2))
for top in range(0,h,128):
 a=md[top:top+128]
 pc[:,0]+=np.bincount(a.ravel(),weights=np.broadcast_to((np.arange(w)+.5)/w,a.shape).ravel(),minlength=65536)
 pc[:,1]+=np.bincount(a.ravel(),weights=np.broadcast_to((np.arange(top,top+len(a))+.5)[:,None]/h,a.shape).ravel(),minlength=65536)
pc/=np.maximum(count[:,None],1)
norm=lambda s:''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if c.isalnum() and not unicodedata.combining(c))
vps={norm(n):int(p) for p,n in re.findall(r'^\s*VICTORY_POINTS_(\d+):\d*\s*"([^"]+)"',z.read(prefix+'localisation/english/victory_points_l_english.yml').decode('utf-8-sig'),re.M)}
anchors=[];used=set()
for c in json.load(open(SRC/'baseline_0202/data/cities.json')):
 p=vps.get(norm(c['name']))
 if p and count[p] and p not in used:
  anchors.append({'name':c['name'],'province':p,'source':pc[p].tolist(),'target':[(c['longitude']+180)/360,(90-c['latitude'])/180]});used.add(p)
# Reject ambiguous duplicate place names using neighboring matched settlements.
a=np.array([q['source'] for q in anchors]);b=np.array([q['target'] for q in anchors]);tree=cKDTree(a)
good=[];rejected=[]
for i,q in enumerate(anchors):
 _,j=tree.query(a[i],k=13);j=j[1:]
 delta=a[j]-a[i];matrix=np.column_stack([delta,np.ones(len(j))]);weight=1/np.maximum(np.linalg.norm(delta,axis=1),.003)
 pred=np.linalg.lstsq(matrix*weight[:,None],b[j]*weight[:,None],rcond=None)[0][-1]
 if np.linalg.norm(pred-b[i])<.024:good.append(q)
 else:rejected.append(q['name'])
# Exact-scale enclaves and narrow disputed regions need explicit geographic
# anchors. These points calibrate registration; they do not paint land.
world=json.load(open(SRC/'baseline_0202/data/world.json'));source_state=pg[md]
for tag,lon,lat in [('PMR',29.15,47.20),('SHN',98.40,20.90),('HKG',114.17,22.30),('MAC',113.55,22.19)]:
 ids=[s for r in world['regions'].values() if r['owner']==tag for s in r['source_states']]
 yy,xx=np.nonzero(np.isin(source_state,ids))
 good.append({'name':tag+' reference footprint','source':[(xx.mean()+.5)/w,(yy.mean()+.5)/h],'target':[(lon+180)/360,(90-lat)/180]})
a=np.array([q['source'] for q in good]);b=np.array([q['target'] for q in good])
fit=RBFInterpolator(b,a,neighbors=24,kernel='thin_plate_spline',smoothing=2e-7)
G=1024;yy,xx=np.mgrid[0:1:513j,0:1:1025j]
grid=fit(np.column_stack([xx.ravel(),yy.ravel()])).reshape(513,1025,2).astype(np.float32)
regions=np.load(SRC/'grouped_atlas_022r2.npz')['regions'];H,W=regions.shape
mapped=np.zeros((H,W),np.uint16)
for top in range(0,H,64):
 gy,gx=np.broadcast_arrays((np.arange(top,min(H,top+64))+.5)[:,None]/H*512,(np.arange(W)+.5)[None,:]/W*1024)
 uv=[map_coordinates(grid[:,:,i],[gy,gx],order=1,mode='nearest') for i in [1,0]]
 mapped[top:top+64]=map_coordinates(md,[uv[0]*h-.5,uv[1]*w-.5],order=0,mode='constant',cval=0)
 if top%2048==0:print('REFERENCE_REGISTRATION',top,H,flush=True)
np.savez_compressed(SRC/'reference_registered_0203.npz',provinces=mapped,source_state=pg,source_centres=pc,grid=grid,source_bitmap=md)
(SRC/'registration_0203.json').write_text(json.dumps({'method':'Settlement-anchored local thin-plate geographic registration; no per-State rectangular scaling','anchors':good,'rejected_ambiguous_names':rejected},indent=2))
print('REFERENCE_REGISTERED',len(good),'anchors',len(rejected),'rejected',flush=True)
