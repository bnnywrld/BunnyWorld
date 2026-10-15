"""Prepare immutable geography masks and aerial material masters for resident rendering.
Official ESA CCI 2000 viewer WMS is spatially sampled; legend colours recover
LCCS families. NOAA relief and accepted gameplay water remain independent.
"""
from pathlib import Path
import json,re,hashlib,shutil
import numpy as np
from PIL import Image,ImageFilter
from scipy.ndimage import gaussian_filter,distance_transform_edt
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography';OUT=ROOT/'assets';W,H=8192,4096
Image.MAX_IMAGE_PIXELS=None
legend=(SRC/'landcover_0201_legend.js').read_text()
entries=[]
for line in legend.splitlines():
    if line.strip().startswith('//'):continue
    m=re.match(r"\s*\['(\d+)',.*?'([0-9A-F]{6})', '([0-9A-F]{6})', '([0-9A-F]{6})'",line)
    if m:
        value=int(m[1])
        for col in m.groups()[1:]:entries.append((tuple(bytes.fromhex(col)),value))
raw=np.asarray(Image.open(SRC/'landcover_2000_0201.png').convert('RGB'))
unique,inv=np.unique(raw.reshape(-1,3),axis=0,return_inverse=True)
# Server emits exact categorical palette colours; match its current legend.
colors=np.array([e[0] for e in entries],float);values=np.array([e[1] for e in entries])
_,ix=cKDTree(colors).query(unique.astype(float));codes=values[ix][inv].reshape(H,W).astype(np.uint8)
# Match current v2 palette first: the third colour in each legend row.
for line in legend.splitlines():
    if line.strip().startswith('//'):continue
    m=re.match(r"\s*\['(\d+)',.*?'([0-9A-F]{6})', '([0-9A-F]{6})', '([0-9A-F]{6})'",line)
    if m:
        color=np.frombuffer(bytes.fromhex(m[4]),np.uint8)
        hit=np.all(unique==color,axis=1)
        if hit.any():codes.ravel()[np.isin(inv,np.flatnonzero(hit))]=int(m[1])
groups=np.full(256,4,np.uint8)
groups[[10,11,12,20,30,40]]=2
groups[[50,160,170]]=1
groups[[60,61,62,70,71,72,80,81,82,90,100]]=0
groups[[200,202,150,151,152,153]]=3
groups[201]=5;groups[220]=6;groups[180]=7
# White is snow/ice; no-data shares that colour and is ocean in this product.
groups[0]=6
a=groups[codes];del raw,inv,codes
p1=np.zeros((H,W),np.uint8);p2=p1.copy();v1=np.zeros((H,W),np.float32);v2=v1.copy()
for kind in range(8):
    weight=gaussian_filter((a==kind).astype(np.float32),.85,mode=('nearest','wrap'))
    best=weight>v1
    p2[best]=p1[best];v2[best]=v1[best];p1[best]=kind;v1[best]=weight[best]
    second=(~best)&(weight>v2);p2[second]=kind;v2[second]=weight[second]
    print('Biome family',kind,'prepared',flush=True)
fraction=v2/np.maximum(v1+v2,1e-6)
types=np.stack([p1,p2,np.rint(fraction*255).astype(np.uint8)],-1)
Image.fromarray(types).save(OUT/'terrain_types.png',optimize=True)
palette=np.array([[70,99,51],[40,81,42],[113,125,72],[192,157,100],[130,133,80],[126,119,98],[219,225,221],[58,94,66]],np.float32)
old=np.asarray(Image.open(OUT/'earth_day.jpg').convert('RGB').filter(ImageFilter.GaussianBlur(5)),np.float32)
color=palette[p1]*(1-fraction[:,:,None])+palette[p2]*fraction[:,:,None]
# Existing broad geographic tone contributes only low-frequency regional variation.
luminance=old.mean(-1);tone=np.clip(luminance/np.maximum(gaussian_filter(luminance,18),1),.90,1.10)
color*=tone[:,:,None]
Image.fromarray(np.clip(color,0,255).astype(np.uint8)).save(OUT/'terrain_color.png',optimize=True)
art=Image.open(OUT/'materials/resident_master_0201.png').convert('RGB');aw,ah=art.size
patches=[art.crop((0,0,aw//2,ah//2)),art.crop((0,0,aw//2,ah//2)),art.crop((0,ah//2,aw//2,ah)),art.crop((aw//2,0,aw,ah//2)),Image.open(OUT/'materials/grassland.png').convert('RGB'),art.crop((aw//2,ah//2,aw,ah)),art.crop((aw//2,ah//2,aw,ah)),art.crop((0,0,aw//2,ah//2))]
for i,im in enumerate(patches):
    data=np.asarray(im.resize((2048,2048),Image.Resampling.LANCZOS),np.float32)/255
    if i==1:data*=np.array([.78,1.03,.80])
    if i==6:data=data*.12+np.array([.81,.85,.84])
    if i==7:data*=np.array([.82,.92,.92])
    # Build a periodic material from an aerial patch using a narrow edge blend.
    band=64
    for axis in [0,1]:
        left=np.take(data,np.arange(band),axis=axis).copy();right=np.take(data,np.arange(2048-band,2048),axis=axis).copy()
        t=(np.arange(band)+.5)/band;t=t[:,None,None] if axis==0 else t[None,:,None]
        edge=(left+right)*.5
        low=edge*(1-t)+left*t;high=right*(1-t)+edge*t
        if axis==0:data[:band]=low;data[-band:]=high
        else:data[:,:band]=low;data[:,-band:]=high
    im=Image.fromarray(np.clip(data*255,0,255).astype(np.uint8));im.save(OUT/f'materials/resident_{i}.png',optimize=True)
    (OUT/f'materials/resident_{i}.png.import').write_text('''[remap]
importer="texture"
type="CompressedTexture2D"

[deps]
source_file="res://assets/materials/resident_%d.png"

[params]
compress/mode=2
compress/high_quality=false
mipmaps/generate=true
'''%i)
# Exact classification IDs use lossless import; colour can use GPU compression.
for name,mode,mips in [('terrain_types',0,'false'),('terrain_color',2,'true')]:
    (OUT/f'{name}.png.import').write_text(f'''[remap]
importer="texture"
type="CompressedTexture2D"

[deps]
source_file="res://assets/{name}.png"

[params]
compress/mode={mode}
mipmaps/generate={mips}
''')
report=json.loads((SRC/'landcover_0201_source.json').read_text())
report.update(version='0.2.0.1',rendering='Resident geographical layers and eight fixed compressed material layers; no geographic image-tile streaming',materials=['Temperate forest','Evergreen / tropical forest','Cropland','Sand / sparse dry ground','Grass / shrubland','Rock','Snow / ice','Wetland'],material_size=[2048,2048],art_source='Built-in image generation, 14 October 2026; original master retained',geographic_mask_sha256=hashlib.sha256((OUT/'terrain_types.png').read_bytes()).hexdigest(),legacy_jpeg_tiles_used=False)
(ROOT/'data/terrain.json').write_text(json.dumps(report,indent=2));print('RESIDENT_TERRAIN_PREPARED',flush=True)
