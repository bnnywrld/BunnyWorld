import io,json,sys,zipfile,hashlib
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1];out=R/'assets/flags';out.mkdir(exist_ok=True);catalog={};page=None;index=0
with zipfile.ZipFile(sys.argv[1]) as z:
 files=sorted(n for n in z.namelist() if n.count('/')==1 and n.lower().endswith(('.tga','.dds')))
 for n in files:
  try:im=Image.open(io.BytesIO(z.read(n))).convert('RGBA')
  except Exception:continue
  cell=index%512
  if cell==0:page=Image.new('RGBA',(1536,2048),(0,0,0,0))
  im.thumbnail((92,60),Image.Resampling.LANCZOS);x=(cell%16)*96+2;y=(cell//16)*64+2
  page.paste(im,(x,y));catalog[Path(n).stem]={'page':index//512,'rect':[x,y,im.width,im.height]}
  index+=1
  if cell==511:page.save(out/f'page_{index//512-1}.png',optimize=True)
 if index%512:page.save(out/f'page_{index//512}.png',optimize=True)
(R/'data/flags.json').write_text(json.dumps(catalog,separators=(',',':')))
(R/'data/flags_import.json').write_text(json.dumps({'flags':index,'atlas_pages':(index+511)//512,'source_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()},indent=2))
print('FLAGS_IMPORTED',index)
