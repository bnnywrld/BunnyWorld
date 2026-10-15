"""Offline physical coverage, relief, regional albedo and detailed materials.
Usage: python tools/build_surface_0202.py downloaded_material_directory
Raw sources are CC0 Poly Haven textures. Unique canopy master is included.
"""
from pathlib import Path
import sys,json,io,os,hashlib
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt,gaussian_filter
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography';AS=ROOT/'assets';MAT=AS/'materials'
def png(a,p):
    b=io.BytesIO();Image.fromarray(a).save(b,format='PNG',compress_level=6);tmp=p.with_suffix('.png.new')
    with tmp.open('wb') as f:f.write(b.getvalue());f.flush();os.fsync(f.fileno())
    os.replace(tmp,p)
state=np.load(SRC/'grouped_atlas_022r2.npz')['regions'][1::2,1::2]
antarctica=np.load(SRC/'grouped_atlas_020.npz')['regions'][1::2,1::2]==8191
land=(state>0)|antarctica;inside=distance_transform_edt(land);outside=distance_transform_edt(~land)
shore=np.clip(.5+(inside-outside)/24,0,1)
t=np.clip((inside-.5)/4,0,1);feather=t*t*(3-2*t)
alt=np.maximum(np.load(SRC/'etopo_021.npz')['meters'].astype(np.float32),0)
height=(.0000125+np.minimum(alt,9000)*8/6371000)*feather; height[~land]=0
value=np.clip(np.round(height/.016*65535),0,65535).astype('<u2')
with (AS/'relief_data.bin').open('wb') as f:f.write(value.tobytes());f.flush();os.fsync(f.fileno())
rgba=np.stack([value&255,value>>8,np.clip(alt/9000*255,0,255),np.round(shore*255)],axis=-1).astype(np.uint8)
png(rgba,AS/'relief_data.png');np.savez_compressed(SRC/'physical_land_0202.npz',land=land)
meta=json.load(open(ROOT/'data/relief.json'));meta.update(revision='0.2.0.2',radial_displacement_scale=.016,height_exaggeration=8.0,land_lift=.0000125,land_lift_meters=79.6375,maximum_displacement=float(height.max()),antarctica_pixels=int(antarctica.sum()),land_geometry='Independent physical mask, signed-distance shore coverage, unassigned Antarctic terrain restored')
(ROOT/'data/relief.json').write_text(json.dumps(meta,indent=2));print('RELIEF_PREPARED',height.max(),int(antarctica.sum()),flush=True)
if '--relief-only' in sys.argv:sys.exit(0)
seed=AS/'terrain_color_seed_0202.png'
if not seed.exists():seed.write_bytes((AS/'terrain_color.png').read_bytes())
colour=np.array(Image.open(seed)).astype(np.float32);types=np.array(Image.open(AS/'terrain_types.png'))
h,w=land.shape;arid=np.zeros((h,w),np.float32)
for left,right,bottom,top in [(-125,-98,20,43),(110,145,-35,-18),(35,80,15,45)]:
    arid[int((90-top)/180*h):int((90-bottom)/180*h),int((left+180)/360*w):int((right+180)/360*w)]=1
arid=gaussian_filter(arid,12);grass=((types[:,:,0]==4)|(types[:,:,1]==4)).astype(np.float32)
amount=(arid*grass*.64)[:,:,None];colour=colour*(1-amount)+np.array([175,147,102])*amount
colour[antarctica]=[224,232,235];types[antarctica]=[6,0,0]
png(np.clip(colour,0,255).astype(np.uint8),AS/'terrain_color.png');png(types,AS/'terrain_types.png')
RAW=ROOT/'tools/art_0202';RAW.mkdir(exist_ok=True);(RAW/'.gdignore').touch()
inputs=Path(sys.argv[1]);names=['aerial_sand','aerial_grass_rock','rocky_terrain','snow_field_aerial','sparse_grass','brown_mud_dry'];sources={}
for name in names:
    p=inputs/(name+'_4k.jpg');a=np.array(Image.open(p).convert('RGB'));assert a.shape==(4096,4096,3)
    sources[name]={'width':4096,'height':4096,'md5':hashlib.md5(p.read_bytes()).hexdigest(),'metadata_url':'https://api.polyhaven.com/files/'+name,'license':'CC0 1.0','native_photo':True}
def read(name):return np.array(Image.open(inputs/(name+'_4k.jpg')).convert('RGB'),dtype=np.float32)
forest=Image.open(MAT/'forest_master_0202.png').convert('RGB');original=forest.size;forest=np.array(forest.resize((4096,4096),Image.Resampling.LANCZOS),dtype=np.float32)
# Blend only opposite edge strips offline to suppress a visible tile seam.
for axis in [0,1]:
    f=np.moveaxis(forest,axis,0)
    for i in range(64):
        a=(64-i)/128;left=f[i].copy();right=f[-1-i].copy();f[i]=left*(1-a)+right*a;f[-1-i]=right*(1-a)+left*a
crop=read('aerial_grass_rock');yy,xx=np.mgrid[:4096,:4096];fields=(xx//384+yy//512*3)%7;crop*= (.78+fields*.035)[:,:,None];crop[(xx%384<8)|(yy%512<8)]=[106,93,65]
layers=[forest,forest*np.array([.74,1.02,.78]),crop,read('aerial_sand'),read('sparse_grass'),read('rocky_terrain'),read('snow_field_aerial'),read('brown_mud_dry')*np.array([.73,.92,.75])]
for i,a in enumerate(layers):png(np.clip(a,0,255).astype(np.uint8),RAW/f'quality_0202_{i}.png');print('MATERIAL_SOURCE',i,flush=True)
sources['forest_master']={'native_size':original,'prepared_size':[4096,4096],'native_photo':False,'source':'Built-in image generation, full-frame woodland canopy; resized offline'}
(ROOT/'data/material_sources_0202.json').write_text(json.dumps(sources,indent=2))
meta=json.load(open(ROOT/'data/terrain.json'));meta.update(version='0.2.0.2',material_size=4096,light_material_size=2048,art_source='Native 4K CC0 Poly Haven surface photos, new full-frame canopy master and offline crop pattern',antarctica_physical_coverage=True,regional_dryness='Biome-limited regional arid albedo adjustment; preserves forest classes',legacy_jpeg_tiles_used=False)
(ROOT/'data/terrain.json').write_text(json.dumps(meta,indent=2))
