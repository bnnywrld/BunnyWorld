"""Offline NASA July 2004 tiles. Runtime JPEG tiles keep full image quality in a
bounded texture-array cache. 65536x32768 detail (~611 m equatorial) from 500m input.
Usage: python tools/build_terrain_016.py /path/to/eight/NASA/jpegs
"""
import json,sys
from pathlib import Path
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
ROOT=Path(__file__).resolve().parents[1];src=Path(sys.argv[1]);out=ROOT/'data/terrain';out.mkdir(exist_ok=True)
quality=88
for label in ['A1','B1','C1','D1','A2','B2','C2','D2']:
 im=Image.open(src/(label+'.jpg'));im=im.resize((16384,16384),Image.Resampling.LANCZOS);col=ord(label[0])-65;row=int(label[1])-1
 for y in range(16):
  for x in range(16):im.crop((x*1024,y*1024,(x+1)*1024,(y+1)*1024)).save(out/f'{col*16+x}_{row*16+y}.bwt',quality=quality,format='JPEG')
 print('Built terrain quadrant',label,flush=True)
size=sum(p.stat().st_size for p in out.glob('*.bwt'));print('Tile bytes',size,flush=True)
# Lower quality only if the real measured disk budget requires it. Keep the
# base compressed texture + detailed source files below 200,000,000 bytes.
while size>174000000 and quality>76:
 quality-=3
 for p in out.glob('*.bwt'):
  im=Image.open(p);im.save(p,quality=quality,format='JPEG')
 size=sum(p.stat().st_size for p in out.glob('*.bwt'))
 print('Measured tile budget',quality,size,flush=True)
assert size+22370000<=200000000,(size,quality)
# Base layer uses source quadrant thumbnails, avoiding an enormous global bitmap.
base=Image.new('RGB',(8192,4096))
for label in ['A1','B1','C1','D1','A2','B2','C2','D2']:
 im=Image.open(src/(label+'.jpg'));im.thumbnail((2048,2048),Image.Resampling.LANCZOS);base.paste(im,((ord(label[0])-65)*2048,(int(label[1])-1)*2048))
base.save(ROOT/'assets/earth_day.jpg',quality=94)
meta={'columns':64,'rows':32,'tile_size':1024,'detail_resolution':[65536,32768],'equatorial_metres_per_pixel':611.5,'base_resolution':[8192,4096],'jpeg_quality':quality,'tile_bytes':size,'total_terrain_budget_estimate':size+22370000,'cache_layers':24,'source':'NASA Blue Marble Next Generation July 2004 topography, 500m source quadrants. Resampled to fit 200MB budget.','files':2048};(ROOT/'data/terrain.json').write_text(json.dumps(meta,indent=2));print('TERRAIN_016_COMPLETE',meta,flush=True)
