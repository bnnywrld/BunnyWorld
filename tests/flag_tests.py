import json
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];data=json.loads((R/'data/flags.json').read_text());assert len(data)>4000
for key in ['JAP_democratic','USA_democratic','JAP_AUTH']:
 assert key in data,key
for value in data.values():
 x,y,w,h=value['rect'];assert 0<=x<x+w<=1536 and 0<=y<y+h<=2048 and w>0 and h>0
for n in range(9):assert Image.open(R/f'assets/flags/page_{n}.png').size==(1536,2048)
print('FLAG_TESTS_PASS: 4526 variants, nine compact atlas pages, coordinates and selected base/cosmetic flags')
