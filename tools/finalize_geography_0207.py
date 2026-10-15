"""Write all runtime ID textures atomically from the final repaired atlas."""
from pathlib import Path
import json,os
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography'
Image.MAX_IMAGE_PIXELS=None

def atomic_png(array,path):
 temporary=path.with_name(path.name+'.prepare-tmp')
 Image.fromarray(array).save(temporary,format="PNG")
 with Image.open(temporary) as image:image.load()
 os.replace(temporary,path)

def main():
 states=np.load(SRC/'grouped_atlas_022r2.npz')['regions'];p=np.load(SRC/'province_atlas_0207.npz')['provinces'];ps=json.load(open(ROOT/'data/provinces.json'))
 index=np.zeros((65536,3),np.uint8)
 for province in ps.values():index[province['id'],:2]=[province['region']&255,province['region']>>8]
 index[65535,:2]=[255,31];atomic_png(index.reshape(256,256,3),ROOT/'assets/province_index.png')
 for i in range(4):
  y,x=i//2*4096,i%2*8192;q=p[y:y+4096,x:x+8192].copy();q[states[y:y+4096,x:x+8192]==8191]=65535
  atomic_png(np.stack([(q&255).astype(np.uint8),(q>>8).astype(np.uint8),np.zeros_like(q,np.uint8)],-1),ROOT/'assets'/f'region_ids_{i}.png')
  print('ATOMIC_ID_TILE',i,flush=True)
if __name__=='__main__':main()
