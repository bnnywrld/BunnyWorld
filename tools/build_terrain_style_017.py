"""Create a semi-realistic planet material from geographic terrain and generated
surface materials. Geometry, climate placement and relief stay geographically
anchored. Urban footprints are deliberate approximate gameplay illustrations.
Usage: python tools/build_terrain_style_017.py BASELINE_SOURCE_ZIP GENERATED_ATLAS
"""
from pathlib import Path
import json,sys,zipfile,io,hashlib,math
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parents[1];Image.MAX_IMAGE_PIXELS=None

def materials(path):
    im=Image.open(path).convert('RGB');w,h=im.size;folder=ROOT/'assets/materials';folder.mkdir(exist_ok=True)
    names=['forest','desert','grassland','urban'];result=[]
    for i,name in enumerate(names):
        q=im.crop((i%2*w//2,i//2*h//2,(i%2+1)*w//2,(i//2+1)*h//2)).resize((512,512),Image.Resampling.LANCZOS)
        # Opposing mirrored edges make derivatives used by the runtime periodic.
        if name!='urban':
            small=q.resize((256,256),Image.Resampling.LANCZOS);q=Image.new('RGB',(512,512));q.paste(small,(0,0));q.paste(small.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(256,0));q.paste(small.transpose(Image.Transpose.FLIP_TOP_BOTTOM),(0,256));q.paste(small.transpose(Image.Transpose.ROTATE_180),(256,256))
        q.save(folder/(name+'.png'));result.append(np.asarray(q,np.float32)/255)
    im.save(folder/'generated_atlas.png')
    return result

def grade(im,tx,ty,detail):
    a=np.asarray(im,np.float32)/255.;r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
    # Saturated ocean imagery does not participate in biome classification.
    ocean=np.clip((b-r)*5,0,1)*np.clip((b-g)*8,0,1)
    lum=a@np.array([.27,.55,.18],np.float32)
    low=np.asarray(im.convert('L').filter(ImageFilter.GaussianBlur(2)),np.float32)/255
    veget=np.clip((g-r*.94)/(r+g+b+.04)*9,0,1)*(1-ocean)
    dry=np.clip((r-g*.92)*5,0,1)*(1-veget)
    light=np.clip((low-.18)*1.45,0,1)
    forest=np.array([.18,.34,.16],np.float32)
    grass=np.array([.44,.51,.27],np.float32)
    plant=forest[None,None,:]*(1-light[:,:,None])+grass[None,None,:]*light[:,:,None]
    barren=np.array([.62,.49,.33],np.float32)[None,None,:]+light[:,:,None]*np.array([.16,.14,.11],np.float32)
    rock=np.array([.40,.40,.34],np.float32)[None,None,:]+light[:,:,None]*np.array([.21,.19,.18],np.float32)
    land=rock*(1-dry[:,:,None])+barren*dry[:,:,None]
    land=land*(1-veget[:,:,None])+plant*veget[:,:,None]
    ice=np.clip((np.minimum(np.minimum(r,g),b)-.53)*4,0,1)
    land=land*(1-ice[:,:,None])+np.array([.87,.91,.92],np.float32)[None,None,:]*ice[:,:,None]
    # Geographic relief remains visible, while fine photographic noise is reduced.
    shade=np.clip(.80+low*.45+(lum-low)*.7,.68,1.18)
    land*=shade[:,:,None]
    yy,xx=np.mgrid[0:1024,0:1024]
    iy=(yy+ty*1024)%512;ix=(xx+tx*1024)%512
    f,d,p=detail[:3];material=f[iy,ix]*veget[:,:,None]+d[iy,ix]*dry[:,:,None]+p[iy,ix]*np.maximum(0,1-veget-dry)[:,:,None]
    pattern=material.mean(axis=2);pattern=(pattern-.42)*.05
    land+=pattern[:,:,None]*(1-ice[:,:,None])
    land=land*.92+a*.08
    sea=np.zeros_like(a);sea[:]=[.065,.25,.37]
    out=land*(1-ocean[:,:,None])+sea*ocean[:,:,None]
    return Image.fromarray(np.clip(out*255,0,255).astype(np.uint8))

def urban_mask():
    w,h=8192,4096;mask=np.zeros((h,w),np.float32)
    cities=json.loads((ROOT/'data/cities.json').read_text());count=0
    for i,c in enumerate(cities):
        pop=float(c.get('population_rank',0))
        if pop<75000 and not c['capital']:continue
        x=(float(c['longitude'])+180)/360*w;y=(90-float(c['latitude']))/180*h
        radius=min(47,max(5,5+math.sqrt(max(pop,25000)/1000000)*7))
        rx=radius/4.89/max(.2,math.cos(math.radians(float(c['latitude']))));ry=radius/4.89
        l=int(math.floor(x-rx*1.7));r=int(math.ceil(x+rx*1.7));t=max(0,int(y-ry*1.7));bt=min(h,int(y+ry*1.7)+1)
        yy,xx=np.mgrid[t:bt,l:r+1];ang=(i*2.399963)%math.pi;dx=(xx-x)/rx;dy=(yy-y)/ry
        u=dx*math.cos(ang)+dy*math.sin(ang);v=-dx*math.sin(ang)+dy*math.cos(ang)
        rr=np.sqrt(u*u*.78+v*v*1.3);perturb=.10*np.sin(u*6+i)+.08*np.cos(v*7-i*.3)
        density=np.clip(1-(rr+perturb)/1.25,0,1)**1.25
        density*=min(.95,.58+math.log10(max(pop,75000)/75000)*.15)
        for j,col in enumerate(np.arange(l,r+1)%w):mask[t:bt,col]=np.maximum(mask[t:bt,col],density[:,j])
        count+=1
    Image.fromarray(np.clip(mask*255,0,255).astype(np.uint8)).save(ROOT/'assets/urban_density.png',optimize=True)
    return count

if __name__=='__main__':
    atlas=Path(sys.argv[2]);detail=materials(atlas);urban=urban_mask();z=zipfile.ZipFile(sys.argv[1]);prefix=next(n[:-len('data/terrain/0_0.bwt')] for n in z.namelist() if n.endswith('data/terrain/0_0.bwt'))
    base=Image.new('RGB',(8192,4096));out=ROOT/'data/terrain';out.mkdir(exist_ok=True)
    def tile(item):
        x,y=item;raw=z.read(prefix+f'data/terrain/{x}_{y}.bwt');im=Image.open(io.BytesIO(raw)).convert('RGB');styled=grade(im,x,y,detail)
        p=out/f'{x}_{y}.bwt';styled.save(p,format='JPEG',quality=86,subsampling=2);return x,y,styled.resize((128,128),Image.Resampling.LANCZOS),p.stat().st_size
    total=0
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,(x,y,thumb,size) in enumerate(pool.map(tile,[(x,y) for y in range(32) for x in range(64)]),1):
            total+=size;base.paste(thumb,(x*128,y*128))
            if i%256==0:print('Styled tiles',i,'bytes',total,flush=True)
    z.close();base.save(ROOT/'assets/earth_day.jpg',quality=94,subsampling=0)
    assert total+22370000<=200000000,total
    meta=json.loads((ROOT/'data/terrain.json').read_text());meta.update({'jpeg_quality':86,'tile_bytes':total,'total_terrain_budget_estimate':total+22370000,'source':'Geographically anchored NASA terrain with custom natural-material color treatment and generated surface details.','style':'Semi-realistic planet material; approximate city footprints and readable urban blocks.','urban_footprints':urban,'generated_atlas_sha256':hashlib.sha256(atlas.read_bytes()).hexdigest()});(ROOT/'data/terrain.json').write_text(json.dumps(meta,indent=2))
    (ROOT/'assets/materials/TERRAIN_ART.md').write_text('Terrain art: built-in Image Generation tool, 13 October 2026.\n\nThe atlas supplies woodland, desert, countryside and urban surface details. Real geographic terrain determines placement; generated materials do not determine borders, continents or city locations.\n\nPrompt: production material atlas for a modern geopolitical globe; four top-down texture squares: temperate woodland, sandy desert, grassland/countryside, readable concrete urban blocks and streets. Natural colors, mildly stylized, no labels or geographic layout.\n')
    print('TERRAIN_STYLE_017_COMPLETE',total,'tile bytes;',urban,'urban footprints',flush=True)
