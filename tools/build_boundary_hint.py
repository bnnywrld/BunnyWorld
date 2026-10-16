"""Ownership-independent acceleration only: no State/country IDs or shapes.
Every visible fill and line resolves the same categorical province map in shader.
"""
from pathlib import Path
import json,zlib,struct,hashlib
import numpy as np
from PIL import Image
from scipy.ndimage import maximum_filter
R=Path(__file__).resolve().parents[1];W,H=16384,8192
Image.MAX_IMAGE_PIXELS=None

def atlas():
 a=np.zeros((H,W),np.uint16)
 for i in range(4):
  rgb=np.asarray(Image.open(R/f'assets/region_ids_{i}.png'));t,l=i//2*4096,i%2*8192
  a[t:t+4096,l:l+8192]=rgb[:,:,0].astype(np.uint16)+rgb[:,:,1].astype(np.uint16)*256
 return a

def build():
 a=atlas();edge=np.zeros(a.shape,np.uint8)
 e=a!=np.roll(a,1,axis=1);edge[e]=255;edge[np.roll(e,-1,axis=1)]=255
 e=a[1:]!=a[:-1];edge[1:][e]=255;edge[:-1][e]=255
 # Two native texels per hint texel; cover full 4x4 cubic footprint and
 # linear hint filtering. Conservative overdraw cannot alter geography.
 hint=np.maximum.reduce([edge[::2,::2],edge[1::2,::2],edge[::2,1::2],edge[1::2,1::2]])
 hint=maximum_filter(hint,size=5,mode=('nearest','wrap'))
 p=R/'assets/display/boundary_hint.bwd';p.write_bytes(struct.pack('<II',W//2,H//2)+zlib.compress(hint.tobytes(),8))
 return p
if __name__=='__main__':
 p=build();print('BOUNDARY_HINT_READY',p.stat().st_size,flush=True)
