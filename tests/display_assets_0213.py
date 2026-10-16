"""Regression checks for label coverage, colour seams and immutable geography."""
from pathlib import Path
import hashlib,json,struct,zlib,subprocess
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/display'

def unpack(name,channels):
    raw=(OUT/name).read_bytes();w,h=struct.unpack('<II',raw[:8]);data=zlib.decompress(raw[8:])
    assert len(data)==w*h*channels
    return np.frombuffer(data,np.uint8).reshape((h,w,channels) if channels>1 else (h,w))

def main():
    mask=unpack('country_glyph_mask.bwd',3)
    original=np.asarray(Image.open(OUT/'country_glyphs.png').convert('RGBA'))
    assert np.array_equal(mask[:,:,0],original[:,:,3]),'exact glyph coverage retained'
    assert np.array_equal(mask[:,:,1],original[:,:,0]),'exact outline/ink retained'
    atlas=json.loads((OUT/'country_glyphs.json').read_text())
    for letter,entry in atlas['glyphs'].items():
        if letter==' ':continue
        u,v,w,h=entry['uv'];hh,ww=mask.shape[:2]
        area=mask[round(v*hh):round((v+h)*hh),round(u*ww):round((u+w)*ww),0]
        assert area.max()>200 and (area==0).any(),letter+' has strokes and clear background'
    shade=unpack('country_border_shade.bwd',1)
    # Tokai: old shade had a hard zero water mask. Prepared shading must extend
    # continuously across it, with final visibility controlled by the coast SDF.
    old=np.asarray(Image.open(ROOT/'assets/border_fade.png').convert('L'))
    y0,y1,x0,x1=1240,1340,7200,7350
    a=old[y0:y1,x0:x1];b=shade[y0:y1,x0:x1]
    assert np.count_nonzero((a==0)&(b>25))>20,'coastal shading extends through categorical seam'
    assert b.max()>100 and b.min()<10,'country edge shading retained'
    manifest=json.loads((OUT/'BUNDLE.json').read_text())
    assert manifest['version']=='0.2.0.13'
    for name,expected in manifest['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
    # The patch is display/UI only: compare every tracked authoritative map and
    # prepared asset input against the working 0.2.0.12 Git baseline.
    names=subprocess.check_output(['git','ls-files','data','tools/cartography','repository_assets'],cwd=ROOT,text=True).splitlines()
    for name in names:
        baseline=subprocess.check_output(['git','show','HEAD:'+name],cwd=ROOT)
        assert (ROOT/name).read_bytes()==baseline,name+' changed'
    print(json.dumps({'glyphs':len(atlas['glyphs'])-1,'bundle_files':len(manifest['files']),'unchanged_map_files':len(names),'coastal_seam_samples':int(np.count_nonzero((a==0)&(b>25))),'failures':0}))

if __name__=='__main__':main()
