"""Offline miniature flag atlas: all variants, no full-page hover uploads."""
from pathlib import Path
import io,json,math,os
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
catalog=json.load(open(ROOT/'data/flags.json'));columns=64;cell_w,cell_h=36,24
atlas=Image.new('RGBA',(columns*cell_w,math.ceil(len(catalog)/columns)*cell_h));pages={}
for i,(key,item) in enumerate(sorted(catalog.items())):
 page=item['page']
 if page not in pages:pages[page]=Image.open(ROOT/'assets/flags'/f'page_{page}.png').convert('RGBA')
 x,y,w,h=item['rect'];flag=pages[page].crop((x,y,x+w,y+h)).resize((32,20),Image.Resampling.LANCZOS)
 left=(i%columns)*cell_w+2;top=(i//columns)*cell_h+2;atlas.paste(flag,(left,top));item['hover_rect']=[left,top,32,20]
b=io.BytesIO();atlas.save(b,format='PNG')
with (ROOT/'assets/flags/hover.png').open('wb') as f:f.write(b.getvalue());f.flush();os.fsync(f.fileno())
(ROOT/'data/flags.json').write_text(json.dumps(catalog,separators=(',',':')))
print('HOVER_FLAGS_PREPARED',len(catalog),atlas.size,len(b.getvalue()),flush=True)
