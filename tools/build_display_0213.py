"""Prepare display-only label coverage and continuous country border shading.
Does not alter IDs, geography, picking, simulation data or source textures.
"""
from pathlib import Path
import hashlib,json,struct,zlib
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/display'

def pack(name,array):
    h,w=array.shape[:2]
    (OUT/name).write_bytes(struct.pack('<II',w,h)+zlib.compress(array.tobytes(),9))

def main():
    glyph=np.array(Image.open(OUT/'country_glyphs.png').convert('RGBA'))
    # RGB data texture: coverage in R/B, ink luminance in G; no importer alpha.
    mask=np.stack([glyph[:,:,3],glyph[:,:,0],glyph[:,:,3]],axis=-1)
    pack('country_glyph_mask.bwd',mask)
    fade=np.asarray(Image.open(ROOT/'assets/border_fade.png').convert('L'),dtype=np.float32)/255
    # The old shade is zero on water, leaving a categorical stair at the coast.
    # Extend its weighted valid shade across that seam, then gently reconstruct
    # the continuous band. Final visibility uses the existing smooth coast SDF.
    land=np.zeros(fade.shape,bool)
    for tile in range(4):
        image=np.asarray(Image.open(ROOT/f'assets/region_ids_{tile}.png'))
        block=(image[1::2,1::2,0]>0)|(image[1::2,1::2,1]>0)
        h,w=block.shape;land[(tile//2)*h:(tile//2+1)*h,(tile%2)*w:(tile%2+1)*w]=block
    # Only a narrow coast apron is needed; avoid storing a global nearest-ID map.
    weight=gaussian_filter(land.astype(np.float32),.9,mode=('nearest','wrap'))
    smooth=gaussian_filter(fade,.9,mode=('nearest','wrap'))
    smooth=np.divide(smooth,weight,out=np.zeros_like(smooth),where=weight>.0001)
    pack('country_border_shade.bwd',np.clip(np.rint(smooth*255),0,255).astype(np.uint8))
    manifest=json.loads((OUT/'BUNDLE.json').read_text())
    manifest['version']='0.2.0.13'
    for name in ['country_glyph_mask.bwd','country_border_shade.bwd']:
        manifest['files']['assets/display/'+name]=hashlib.sha256((OUT/name).read_bytes()).hexdigest()
    (OUT/'BUNDLE.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Prepared label mask and smooth country shading')

if __name__=='__main__':main()
