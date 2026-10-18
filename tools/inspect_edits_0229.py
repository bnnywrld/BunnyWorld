from pathlib import Path
import zipfile,json
from collections import Counter
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
R=Path(__file__).resolve().parents[1];P=R.parent
def decode(im,palette):
 rgb=np.asarray(im.convert('RGB'));a=rgb[:,:,0].astype(np.uint32)*65536+rgb[:,:,1].astype(np.uint32)*256+rgb[:,:,2]
 colors=np.array([v[0]*65536+v[1]*256+v[2]for v in palette.values()],np.uint32);ids=np.array(list(map(int,palette)),np.uint16);ix=np.argsort(colors);colors=colors[ix];ids=ids[ix];at=np.searchsorted(colors,a);assert np.all(at<len(colors))and np.array_equal(colors[at],a)
 return ids[at]
def main():
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--original',type=Path,default=P/'editing_baseline/BunnyWorld_0228_Editing_PNGs.zip');ap.add_argument('--edited',type=Path,default=P/'upload/newsts.zip');args=ap.parse_args()
 old=zipfile.ZipFile(args.original);new=zipfile.ZipFile(args.edited);D=R/'tools/cartography/edits_0229';D.mkdir(exist_ok=True)
 w=json.loads((R/'data/world.json').read_text());ps=json.loads((R/'data/provinces.json').read_text());lut=np.zeros(65536,np.uint16);lut[65535]=65535
 for k,p in ps.items():lut[int(k)]=p['region']
 pairs=Counter()
 for i in range(4):
  label=['NW','NE','SW','SE'][i];out={}
  for scope in ['states','provinces']:
   n=f'{scope}_{i}_{label}.png';im=Image.open(old.open(n));pal=json.loads(im.info['BunnyWorldEditing'])['palette'];out[scope]=decode(Image.open(new.open('sts/'+n)),pal);out['old_'+scope]=decode(im,pal)
  a,b=out['old_states'],out['states'];m=a!=b;codes=a[m].astype(np.uint32)*65536+b[m];v,c=np.unique(codes,return_counts=True);pairs.update({divmod(int(x),65536):int(y)for x,y in zip(v,c)})
  np.savez_compressed(D/f'tile_{i}.npz',**out)
  print('DECODED',i,flush=True)
 n='sea_regions.png';im=Image.open(old.open(n));pal=json.loads(im.info['BunnyWorldEditing'])['palette'];np.savez_compressed(D/'sea.npz',seas=decode(Image.open(new.open('sts/'+n)),pal),old_seas=decode(im,pal))
 for (a,b),n in pairs.items():print(a,w['regions'].get(str(a),{}).get('name','water/Antarctica'),'->',b,w['regions'].get(str(b),{}).get('name','water/Antarctica'),n)
 for i in [10465,12585]:print('REMOVED',ps[str(i)])
if __name__=='__main__':main()
