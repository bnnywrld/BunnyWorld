"""Prepare view-independent tangent normals and snow for distant terrain.

Camera lighting remains dynamic; ownership is never an input. No GPU color
compression is used for these data channels. Near terrain/picking are unchanged.
"""
from pathlib import Path
import hashlib
import json
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'assets/relief_data.png'
OUTPUT = 'assets/display/terrain_cache.bwd'
META = 'assets/display/terrain_cache.json'
ALGORITHM = 3


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check():
    info = json.loads((ROOT/META).read_text())
    assert info['algorithm'] == ALGORITHM, 'Distant terrain preparation version changed.'
    assert info['source_sha256'] == sha(ROOT/SOURCE), 'Relief changed: rebuild distant terrain shading.'
    assert info['sha256'] == sha(ROOT/OUTPUT), 'Distant terrain cache differs from its contract.'


def build():
    if (ROOT/META).exists() and (ROOT/OUTPUT).exists():
        try:
            check()
            return json.loads((ROOT/META).read_text())
        except AssertionError:
            pass
    import numpy as np
    from PIL import Image
    rgba = np.asarray(Image.open(ROOT/SOURCE).convert('RGBA'))
    h, w = rgba.shape[:2]
    assert (w, h) == (8192, 4096)
    heights = (rgba[:, :, 0].astype(np.float32) + rgba[:, :, 1].astype(np.float32)*256.0) * (.016/65535.0)
    def half(a):
        return (a[0::2,0::2]+a[0::2,1::2]+a[1::2,0::2]+a[1::2,1::2])*.25
    # Evaluate normals/snow at native relief resolution before filtering.
    # Averaging heights first would flatten steep cliffs and add excess snow.
    east = np.roll(heights,-1,axis=1)-np.roll(heights,1,axis=1)
    north = np.roll(heights,-1,axis=0)-np.roll(heights,1,axis=0)
    del heights
    latitude = ((np.arange(h,dtype=np.float32)+.5)/h)[:,None]
    east /= (2.0/w*2.0*np.pi*np.maximum(.08,np.sin(latitude*np.pi)))
    north /= (2.0/h*np.pi)
    steep = np.sqrt(east*east+north*north)
    inv = 1.0/np.sqrt(1.0+steep*steep)
    nx, ny, nz = half(-east*inv), half(north*inv), half(inv)
    length = np.sqrt(nx*nx+ny*ny+nz*nz)
    nx /= length; ny /= length
    del east,north,inv,nz,length
    meters = rgba[:,:,2].astype(np.float32)*(9000.0/255.0)
    def smooth(a,b,x):
        t=np.clip((x-a)/(b-a),0,1)
        return t*t*(3.0-2.0*t)
    snowline = 4700.0+(1700.0-4700.0)*smooth(.25,.85,np.abs(latitude-.5)*2.0)
    snow = half(smooth(snowline,snowline+1000.0,meters)*(1.0-smooth(.65,1.25,steep)))
    rock = half(np.maximum(smooth(.25,.95,steep), smooth(2900.0,5400.0,meters)))
    # 128 represents exact zero; 127 steps cover either sign. Flat oceans
    # therefore retain exactly radial normals, including through the mips.
    packed = np.stack([
        np.rint(np.clip(nx,-1,1)*127.0+128.0),
        np.rint(np.clip(ny,-1,1)*127.0+128.0),
        np.rint(snow*255.0),
        np.rint(rock*255.0),
    ],axis=-1).astype(np.uint8)
    data=struct.pack('<II',w//2,h//2)+zlib.compress(packed.tobytes(),9)
    target=ROOT/OUTPUT
    temporary=target.with_suffix('.bwd.prepare-tmp');temporary.write_bytes(data);temporary.replace(target)
    info={'schema':1,'algorithm':ALGORITHM,'format':'RGBA8','channels':'RG tangent normal XY; B snow weight; A rock exposure','width':w//2,'height':h//2,'mipmaps':True,'source':SOURCE,'source_sha256':sha(ROOT/SOURCE),'sha256':sha(target),'base_decoded_bytes':packed.nbytes,'ownership_baked':False,'near_terrain_unchanged':False,'lighting':'World-space sun applied at runtime to the cached tangent normal'}
    (ROOT/META).write_text(json.dumps(info,indent=2)+'\n')
    return info


if __name__ == '__main__':
    print(json.dumps(build(),indent=2))
