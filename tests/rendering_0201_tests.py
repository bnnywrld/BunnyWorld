"""Resident assets, geography fixtures and compiled memory layout."""
from pathlib import Path
import json,struct,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'scripts/main.gd').read_text();shader=(ROOT/'scripts/planet.gdshader').read_text()
assert 'terrain_stream' not in s and 'terrain_lookup' not in shader and 'terrain_tiles' not in shader
assert not (ROOT/'data/terrain').exists()
assert 'landmark": true' not in s
assert 'biome_at' in shader and 'for(int category=0;category<8;category++)' in shader
assert shader.count('uniform sampler')<=16,'Compatibility sampler limit'
b=(ROOT/'assets/materials/terrain_materials.bwm').read_bytes();count=struct.unpack_from('<I',b)[0];assert count==8
at=4
for i in range(count):
 w,h,fmt,length=struct.unpack_from('<IIII',b,at);at+=16
 assert (w,h,fmt,length)==(2048,2048,17,2796216)
 assert len(b[at:at+length])==length;at+=length
assert at==len(b) and len(b)<24000000
mask=np.array(Image.open(ROOT/'assets/terrain_types.png'));assert mask.shape==(4096,8192,3)
assert mask[:,:,:2].max()<8
for name,lon,lat,expected in [('Sahara',10,23,3),('Amazon forest',-65,-5,1),('Greenland',-42,72,6)]:
 x=int((lon+180)/360*8192);y=int((90-lat)/180*4096)
 assert int(mask[y,x,0])==expected,(name,mask[y,x])
meta=json.loads((ROOT/'data/terrain.json').read_text());assert not meta['legacy_jpeg_tiles_used'] and meta['source'].endswith('year 2000')
scene=json.loads((ROOT/'data/urban_scenery.json').read_text());assert scene['display_size_multiplier']==3
world=json.loads((ROOT/'data/world.json').read_text());assert world['scenario_id']=='bunny_world_2000_0_2_0_2'
print('RENDERING_0201_TESTS_PASS: eight fixed compressed materials (22.4 MB), correct biome fixtures, no streamed tiles, 3x scenery and sampler budget')
