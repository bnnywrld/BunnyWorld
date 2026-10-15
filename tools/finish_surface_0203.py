"""Prepared border-distance bands, enlarged-scale city ground and river trials."""
from pathlib import Path
import json,io,os,math,sys
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,gaussian_filter,label,maximum
from skimage.measure import label as ownership_components
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography';AS=ROOT/'assets'
def png(a,p):
 b=io.BytesIO();Image.fromarray(a).save(b,format='PNG',compress_level=6)
 with open(str(p)+'.new','wb') as f:f.write(b.getvalue());f.flush();os.fsync(f.fileno())
 os.replace(str(p)+'.new',p)
world=json.load(open(ROOT/'data/world.json'));regions=np.load(SRC/'grouped_atlas_022r2.npz')['regions'][1::2,1::2];H,W=regions.shape
owner=np.zeros(8192,np.uint16)
for sid,r in world['regions'].items():owner[int(sid)]=world['countries'][r['owner']]['index']
owners=owner[regions]
def border_band(sea):
 edge=np.zeros_like(owners,bool)
 for axis,shift in [(0,1),(0,-1),(1,1),(1,-1)]:
  other=np.roll(owners,shift,axis);other_sea=np.roll(sea,shift,axis)
  national=(owners>0)&(other>0)&(owners!=other)
  coast=(owners>0)&(other==0)&(other_sea>0)
  edge|=national|coast
 distance=distance_transform_edt(~edge)
 # Thin countries and small islands retain a natural-colour interior instead
 # of being filled by two opposing coastal bands. Offline work only.
 components=ownership_components(owners,connectivity=1)
 maxima=maximum(distance,components,index=np.arange(int(components.max())+1))
 widths=np.clip(maxima*.30,1.0,5.0)
 t=np.clip(1-distance/widths[components],0,1)
 band=t*t*(3-2*t);band[owners==0]=0
 png(np.round(band*255).astype(np.uint8),AS/'border_fade.png')

if '--border-only' in sys.argv:
 raw=np.array(Image.open(AS/'sea_ids.png'));sea=raw[:,:,0].astype(np.uint16)+raw[:,:,1].astype(np.uint16)*256
 border_band(sea)
 report=json.load(open(ROOT/'data/surface_0203_report.json'))
 report['border_band']='Finite inward bands at international borders and ocean coasts, narrowed on small country/island components; no interior wash or lake bands'
 (ROOT/'data/surface_0203_report.json').write_text(json.dumps(report,indent=2))
 print('BORDER_BANDS_0203_COMPLETE',flush=True);sys.exit(0)

# Ground surfaces are broad streets/yards/parks, not a second undersized city
# photograph. Four blocks per ~15-km material tile match representative models.
N=1024;yy,xx=np.mgrid[:N,:N];rng=np.random.default_rng(2003)
noise=gaussian_filter(rng.normal(0,1,(N,N)),1)*9
city=np.zeros((N,N,3),np.float32);city[:]=[96,101,94];city+=noise[:,:,None]
for y in range(4):
 for x in range(4):
  a,b=x*256,y*256;colour=np.array([100,105,96])+rng.integers(-10,11,3)
  city[b+20:b+237,a+20:a+237]=colour+noise[b+20:b+237,a+20:a+237,None]
  if (x+y*3)%7==0:city[b+50:b+220,a+50:a+220]=np.array([79,100,70])+noise[b+50:b+220,a+50:a+220,None]
roads=(xx%256<17)|(xx%256>239)|(yy%256<17)|(yy%256>239)
city[roads]=np.array([58,64,65])+noise[roads,None]*.4
png(np.clip(city,0,255).astype(np.uint8),AS/'materials/urban_detail.png')

# Trial shallow broad channels on two lowland reaches. Their width is limited
# by the prepared relief grid; this is not a claim of surveyed river bathymetry.
# The SAME packed field supplies GPU displacement, CPU picking and anchors.
rgba=np.array(Image.open(AS/'relief_data.png'));packed=rgba[:,:,0].astype(np.uint16)+rgba[:,:,1].astype(np.uint16)*256
land=np.load(SRC/'physical_land_0202.npz')['land'];seeds=np.zeros((H,W),bool);names=set()
for f in json.load(open(SRC/'rivers_0201.geojson'))['features']:
 p=f['properties'];name=p.get('name_en') or p.get('name') or ''
 if not any(n in name.lower() for n in ['nile','amazon']):continue
 g=f['geometry'];lines=g['coordinates'] if g['type']=='MultiLineString' else [g['coordinates']]
 for line in lines:
  for a,b in zip(line[:-1],line[1:]):
   if abs(a[0]-b[0])>180:continue
   n=max(1,int(np.ceil(np.linalg.norm(np.array(b[:2])-a[:2])/.015)))
   for t in np.arange(n)/n:
    lon,lat=np.array(a[:2])+(np.array(b[:2])-a[:2])*t
    trial=('nile' in name.lower() and 28<lat<31.3) or ('amazon' in name.lower() and -60<lon<-50 and -4<lat<1)
    if trial:seeds[min(H-1,int((90-lat)/180*H)),int((lon+180)/360*W)%W]=True;names.add(name)
trial_distance=distance_transform_edt(~seeds);channel=np.exp(-(trial_distance/.85)**2)*land
height=packed.astype(float)/65535*.016
depression=np.minimum(channel*48/6371000,height*.20)
height-=depression;packed=np.rint(height/.016*65535).astype('<u2')
rgba[:,:,0]=packed&255;rgba[:,:,1]=packed>>8
png(rgba,AS/'relief_data.png')
with (AS/'relief_data.bin').open('wb') as f:f.write(packed.tobytes());f.flush();os.fsync(f.fileno())
meta=json.load(open(ROOT/'data/relief.json'));meta.update(revision='0.2.0.3',trial_riverbeds={'rivers':sorted(names),'maximum_display_depression_m':48,'width':'Smooth broad profile, limited by 8192×4096 prepared elevation; lowland reaches only','runtime_work':'None: baked into shared CPU/GPU relief'})
(ROOT/'data/relief.json').write_text(json.dumps(meta,indent=2))

# Newly opened Åland water joins only connected coastal components. Retain
# zero IDs for enclosed inland lakes and clear IDs under restored islands.
raw=np.array(Image.open(AS/'sea_ids.png'));sea=raw[:,:,0].astype(np.uint16)+raw[:,:,1].astype(np.uint16)*256
bb=np.s_[int((90-61.1)/180*H):int((90-59.4)/180*H),int((18.6+180)/360*W):int((21.9+180)/360*W)]
water=regions[bb]==0;view=sea[bb];view[~water]=0
components,_=label(water);linked=np.unique(components[water&(view>0)]);fill=water&np.isin(components,linked)&(view==0)
near=distance_transform_edt(~(view>0),return_distances=False,return_indices=True);view[fill]=view[tuple(near[:,fill])]
png(np.stack([(sea&255).astype(np.uint8),(sea>>8).astype(np.uint8),np.zeros_like(sea,np.uint8)],-1),AS/'sea_ids.png')
border_band(sea)
(ROOT/'data/surface_0203_report.json').write_text(json.dumps({'border_band':'Finite inward bands at international borders and ocean coasts, narrowed on small country/island components; no interior wash or lake bands','urban_ground':'Four broad blocks in ~15 km world-projected tile; width calibrated to displayed models','trial_channels':sorted(names),'riverbed_pixels':int((depression>1e-8).sum()),'aland_new_coastal_water_pixels':int(fill.sum())},indent=2))
print('SURFACE_0203_COMPLETE',sorted(names),int((depression>1e-8).sum()),flush=True)
