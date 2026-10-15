"""Give retained named inland lakes their own water-region identifiers.
This prevents a lake hover from inheriting the nearest warped ocean-zone name.
Run after build_geography_017.py and before build_boundaries_017.py.
"""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import binary_dilation
ROOT=Path(__file__).resolve().parents[1];W,H=8192,4096;Image.MAX_IMAGE_PIXELS=None
rgb=np.asarray(Image.open(ROOT/'assets/sea_ids.png'),np.uint16);ids=rgb[:,:,0]+rgb[:,:,1]*256
water=np.load(ROOT/'tools/cartography/grouped_atlas_017.npz')['regions'][1::2,1::2]==0
regions=json.loads((ROOT/'data/sea_regions.json').read_text());regions={k:v for k,v in regions.items() if int(k)<1000}
features=json.loads((ROOT/'tools/cartography/lakes.geojson').read_text())['features'];next_id=1000
for feature in sorted(features,key=lambda f:f['properties'].get('name','')):
    name=feature['properties'].get('name','').strip()
    if not name:continue
    polygons=feature['geometry']['coordinates'] if feature['geometry']['type']=='MultiPolygon' else [feature['geometry']['coordinates']]
    xs=[(p[0]+180)/360*W for poly in polygons for p in poly[0]];ys=[(90-p[1])/180*H for poly in polygons for p in poly[0]]
    l=max(0,int(min(xs))-3);r=min(W,int(max(xs))+4);t=max(0,int(min(ys))-3);b=min(H,int(max(ys))+4)
    canvas=Image.new('1',(r-l,b-t),0);draw=ImageDraw.Draw(canvas)
    for poly in polygons:
        draw.polygon([((lon+180)/360*W-l,(90-lat)/180*H-t) for lon,lat,*rest in poly[0]],fill=1)
        for hole in poly[1:]:draw.polygon([((lon+180)/360*W-l,(90-lat)/180*H-t) for lon,lat,*rest in hole],fill=0)
    mask=np.asarray(canvas).copy();mask=binary_dilation(mask,iterations=2)&water[t:b,l:r]
    yy,xx=np.nonzero(mask)
    if len(xx)<4:continue
    existing=next((int(k) for k,v in regions.items() if v['name']==name and v.get('naval_terrain')=='lake'),None)
    sid=existing or next_id
    if not existing:next_id+=1
    ids[t:b,l:r][mask]=sid
    j=int(np.argmin((xx-xx.mean())**2+(yy-yy.mean())**2))
    regions[str(sid)]={'id':sid,'name':name,'naval_terrain':'lake','source_provinces':[],'map_center':[(float(xx[j]+l)+.75)/W,(float(yy[j]+t)+.75)/H],'neighbors':[]}
for s in regions.values():s['neighbors']=[]
edges=set()
for a,b in [(ids[:,:-1],ids[:,1:]),(ids[:-1],ids[1:])]:
    m=a!=b;edges.update(map(int,np.unique(np.minimum(a[m],b[m]).astype(np.uint32)*65536+np.maximum(a[m],b[m]))))
for e in edges:
    a,b=e//65536,e%65536
    if str(a) in regions and str(b) in regions and (a<1000 and b<1000):regions[str(a)]['neighbors'].append(b);regions[str(b)]['neighbors'].append(a)
for s in regions.values():s['neighbors']=sorted(set(s['neighbors']))
rgb=np.stack([(ids&255).astype(np.uint8),(ids>>8).astype(np.uint8),np.zeros_like(ids,np.uint8)],axis=-1);Image.fromarray(rgb).save(ROOT/'assets/sea_ids.png',optimize=True)
(ROOT/'data/sea_regions.json').write_text(json.dumps(regions,ensure_ascii=False,separators=(',',':')))
print('INLAND_WATER_017_COMPLETE',sum(int(k)>=1000 for k in regions),'named lakes;',len(regions),'water regions total')
