"""Prepare NOAA ETOPO elevation, coastal feathering and refined detail materials.
Input: ERDDAP ETOPO 2022 surface, 60s grid sampled every third cell (3 arc-min).
Prepared relief meters/displacement are bundled for offline rebuilding/export.
"""
from pathlib import Path
import json,sys,hashlib
import numpy as np
from PIL import Image,ImageFilter,ImageEnhance
from scipy.io import netcdf_file
from scipy.ndimage import map_coordinates,distance_transform_edt,gaussian_filter
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography';W,H=8192,4096
MAX_DISPLACEMENT=.008;LAND_LIFT=.00035;EXAGGERATION=4.;RADIUS_METERS=6371000.
Image.MAX_IMAGE_PIXELS=None

def main():
    prepared=SRC/'etopo_021.npz'
    if len(sys.argv)>1:
        with netcdf_file(sys.argv[1],mmap=False) as f:
            raw=f.variables['z'].data.copy().astype(np.float32);lat=f.variables['latitude'].data.copy();lon=f.variables['longitude'].data.copy()
        meters=np.empty((H,W),np.float32)
        longitude=((np.arange(W)+.5)/W*360-180)%360
        x=(longitude-lon[0])/(lon[1]-lon[0])
        for top in range(0,H,128):
            yy=np.arange(top,min(H,top+128));latitude=90-(yy+.5)/H*180
            y=(latitude-lat[0])/(lat[1]-lat[0])
            yy,xx=np.meshgrid(np.clip(y,0,len(lat)-1),x,indexing='ij')
            meters[top:top+len(y)]=map_coordinates(raw,[yy,xx],order=1,mode='grid-wrap').astype(np.float32)
        del raw,yy,xx,y,x
        meters=np.rint(meters).astype(np.int16)
        np.savez_compressed(prepared,meters=meters)
    else:meters=np.load(prepared)['meters']
    meters=meters.astype(np.float32)
    atlas=np.load(SRC/'grouped_atlas_020.npz')['regions'];land=atlas[1::2,1::2]>0
    inland=distance_transform_edt(land).astype(np.float32);feather=np.clip(inland/2.5,0,1)
    altitude=np.maximum(0,meters);height=(LAND_LIFT+np.minimum(9000,altitude)*EXAGGERATION/RADIUS_METERS)*feather
    height[~land]=0;packed=np.rint(height/MAX_DISPLACEMENT*65535).astype(np.uint16)
    # R/G hold linear 16-bit radial displacement; B true altitude; A land feather.
    rgb=np.stack([(packed&255).astype(np.uint8),(packed>>8).astype(np.uint8),np.clip(altitude/9000*255,0,255).astype(np.uint8),np.rint(feather*255).astype(np.uint8)],-1)
    Image.fromarray(rgb).save(ROOT/'assets/relief_data.png',optimize=True)
    (ROOT/'assets/relief_data.bin').write_bytes(packed.astype('<u2').tobytes())
    # Refine existing authored material masters, no replacement geographic atlas.
    out=Image.new('RGB',(1024,1024));names=['forest','desert','grassland','rock']
    for i,name in enumerate(names):
        if name=='rock':
            source=Image.open(ROOT/'assets/materials/grassland.png').convert('L');source=ImageEnhance.Contrast(source).enhance(1.35);gray=np.asarray(source,np.float32)/255
            color=np.stack([gray*.40+.22,gray*.38+.22,gray*.34+.21],-1);im=Image.fromarray(np.clip(color*255,0,255).astype(np.uint8))
        else:
            im=Image.open(ROOT/f'assets/materials/{name}.png').convert('RGB');im=ImageEnhance.Color(im).enhance(.85);im=ImageEnhance.Contrast(im).enhance(1.08);im=im.filter(ImageFilter.UnsharpMask(2,110,2))
        out.paste(im.resize((512,512),Image.Resampling.LANCZOS),(i%2*512,i//2*512))
    master=ROOT/'assets/materials/detail_master_021.png'
    if master.exists():out=Image.open(master).convert('RGB')
    out.save(ROOT/'assets/materials/surface_detail.png',optimize=True)
    # Improve street/block microcontrast within the existing city material.
    urban=Image.open(ROOT/'assets/materials/urban.png').convert('RGB');urban=ImageEnhance.Contrast(urban).enhance(1.16);urban=urban.filter(ImageFilter.UnsharpMask(1.2,130,2));urban.save(ROOT/'assets/materials/urban_detail.png',optimize=True)
    report={'source':'NOAA NCEI ETOPO 2022 ice-surface elevation; 60 arc-second source sampled every third cell through NOAA ERDDAP.', 'doi':'10.25921/fd45-gt74','source_url':'https://oceanwatch.pifsc.noaa.gov/erddap/griddap/ETOPO_2022_v1_60s.nc?z[0:3:10799][0:3:21599]', 'prepared_resolution':[W,H],'source_sample_arc_minutes':3,'radial_displacement_scale':MAX_DISPLACEMENT,'land_lift':LAND_LIFT,'height_exaggeration':EXAGGERATION,'maximum_displacement':float(height.max()),'maximum_source_meters':float(meters.max()),'cpu_binary_bytes':packed.nbytes,'land_geometry':'Ocean/lake mask remains the accepted gameplay mask; coast elevation is feathered over 2.5 prepared pixels.', 'prepared_source_sha256':hashlib.sha256(prepared.read_bytes()).hexdigest()}
    (ROOT/'data/relief.json').write_text(json.dumps(report,indent=2));print('RELIEF_021_PASS',report,flush=True)

if __name__=='__main__':main()
