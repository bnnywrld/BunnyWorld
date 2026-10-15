"""Major river ribbons and explicit canal/strait adjacency without widening land masks."""
from pathlib import Path
import json,struct,math
import numpy as np
from PIL import Image
from scipy.ndimage import label
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography'
world=json.loads((ROOT/'data/world.json').read_text());seas=json.loads((ROOT/'data/sea_regions.json').read_text())
a=np.load(SRC/'grouped_atlas_022r2.npz')['regions'][1::2,1::2];H,W=a.shape
rgb=np.asarray(Image.open(ROOT/'assets/sea_ids.png'),np.uint16);sea=rgb[:,:,0]+rgb[:,:,1]*256

def xy(lon,lat):return min(W-1,max(0,int((lon+180)/360*W))),min(H-1,max(0,int((90-lat)/180*H)))
def add_component(sid,name,bounds,seeds):
    left,top=xy(bounds[0],bounds[3]);right,bottom=xy(bounds[2],bounds[1]);right+=1;bottom+=1
    water=a[top:bottom,left:right]==0
    components,_=label(water,np.ones((3,3),np.uint8));ids=set()
    for lon,lat in seeds:
        x,y=xy(lon,lat);v=int(components[y-top,x-left]);assert v>0,(name,'water seed covered by land');ids.add(v)
    mask=np.isin(components,list(ids));target=sea[top:bottom,left:right];target[mask]=sid
    yy,xx=np.nonzero(mask);j=len(xx)//2
    seas[str(sid)]={'id':sid,'name':name,'naval_terrain':'water_littoral','source_provinces':[], 'map_center':[(float(xx[j]+left)+.5)/W,(float(yy[j]+top)+.5)/H],'neighbors':[]}
    return int(mask.sum())
black=add_component(240,'Black Sea',(27,39.8,43.5,47.9),[(35,43),(37.5,46)])
marmara=add_component(241,'Sea of Marmara',(26.4,39.6,30.4,41.3),[(28,40.6)])
# Derive natural sea adjacency from the actual sea atlas.
for v in seas.values():v['neighbors']=[]
edges=set()
for p,q in [(sea[:,:-1],sea[:,1:]),(sea[:-1],sea[1:])]:
    m=(p>0)&(q>0)&(p!=q)
    edges.update(map(int,np.unique(np.minimum(p[m],q[m]).astype(np.uint32)*65536+np.maximum(p[m],q[m]))))
for e in edges:
    p,q=e//65536,e%65536
    if str(p) in seas and str(q) in seas:seas[str(p)]['neighbors'].append(q);seas[str(q)]['neighbors'].append(p)

def nearby(lon,lat):
    x,y=xy(lon,lat)
    for radius in [0,2,4,8,16,32]:
        local=sea[max(0,y-radius):y+radius+1,max(0,x-radius):x+radius+1]
        yy,xx=np.nonzero(local)
        if len(xx):
            j=np.argmin((xx-radius)**2+(yy-radius)**2);return int(local[yy[j],xx[j]])
    raise RuntimeError(('No endpoint sea',lon,lat))
passages=[
 {'id':'suez','name':'Suez Canal','kind':'canal','country':'EGY','coordinates':[[32.30,31.28],[32.32,31.05],[32.34,30.82],[32.30,30.60],[32.49,30.35],[32.55,30.10],[32.58,29.95]],'ends':[nearby(32.35,31.5),nearby(32.65,29.7)]},
 {'id':'panama','name':'Panama Canal','kind':'canal','country':'PAN','coordinates':[[-79.91,9.36],[-79.93,9.27],[-79.86,9.18],[-79.73,9.12],[-79.66,9.08],[-79.61,9.03],[-79.57,8.95]],'ends':[nearby(-79.98,9.5),nearby(-79.55,8.75)]},
 {'id':'bosporus','name':'Bosporus','kind':'strait','country':'TUR','coordinates':[[29.08,41.24],[29.08,41.19],[29.06,41.15],[29.05,41.12],[29.06,41.09],[29.04,41.06],[29.01,41.03],[29.01,40.98]],'ends':[240,241]},
 {'id':'dardanelles','name':'Dardanelles','kind':'strait','country':'TUR','coordinates':[[26.72,40.39],[26.58,40.29],[26.47,40.19],[26.40,40.15],[26.35,40.08],[26.23,40.03],[26.14,40.01]],'ends':[241,214]}
]
for p in passages:
    p['display_width_km']={'suez':.22,'panama':.20,'bosporus':.85,'dardanelles':1.6}[p['id']]
    p['coordinate_accuracy']='Approximate gameplay centreline; narrow waterway drawn as a subpixel ribbon'
    p['open_at_start']=True
    x,y=p['ends'];assert x!=y,(p['name'],x,y)
    for first,second in [(x,y),(y,x)]:
        if second not in seas[str(first)]['neighbors']:seas[str(first)]['neighbors'].append(second)
        seas[str(first)].setdefault('passages',[]).append({'id':p['id'],'name':p['name'],'neighbor':second})
for v in seas.values():
    v['neighbors']=sorted(set(v['neighbors']))
    if 'passages' in v:v['passages']=list({(p['id'],p['neighbor']):p for p in v['passages']}.values())
Image.fromarray(np.stack([(sea&255).astype(np.uint8),(sea>>8).astype(np.uint8),np.zeros_like(sea,np.uint8)],-1)).save(ROOT/'assets/sea_ids.png',optimize=True)
(ROOT/'data/sea_regions.json').write_text(json.dumps(seas,separators=(',',':')))
paths=[];river_names=set();segments=0
rivers=json.loads((SRC/'rivers_0201.geojson').read_text())['features']
for f in rivers:
    p=f['properties'];rank=float(p.get('scalerank',10) or 0);name=p.get('name_en') or p.get('name') or ''
    if rank>6 or p.get('featurecla')!='River':continue
    geometry=f['geometry'];lines=geometry['coordinates'] if geometry['type']=='MultiLineString' else [geometry['coordinates']]
    for line in lines:
        if len(line)<2:continue
        paths.append((line,rank,0));segments+=len(line)-1
    if name:river_names.add(name)
for p in passages:paths.append((p['coordinates'],0,1))
positions=[];tangents=[];uvs=[];types=[];indices=[];base=0
for line,rank,passage in paths:
    line=np.array(line,dtype=float)[:,:2];dense=[]
    for left,right in zip(line[:-1],line[1:]):
        if abs(right[0]-left[0])>180:continue
        n=max(1,int(np.ceil(np.max(np.abs(right-left))/.08)))
        dense.extend(left+(right-left)*t/n for t in range(n))
    dense.append(line[-1]);line=np.array(dense)
    if len(line)<2:continue
    lon=np.deg2rad(line[:,0]);lat=np.deg2rad(line[:,1]);pts=np.column_stack([np.cos(lat)*np.sin(lon),np.sin(lat),np.cos(lat)*np.cos(lon)])
    tangent=np.empty_like(pts);tangent[0]=pts[1]-pts[0];tangent[-1]=pts[-1]-pts[-2];tangent[1:-1]=pts[2:]-pts[:-2];tangent/=np.maximum(np.linalg.norm(tangent,axis=1)[:,None],1e-9)
    positions.append(np.repeat(pts,2,axis=0));tangents.append(np.column_stack([np.repeat(tangent,2,axis=0),np.ones(len(pts)*2)]));uvs.append(np.column_stack([np.tile([-1,1],len(pts)),np.zeros(len(pts)*2)]));types.append(np.tile([rank,passage],(len(pts)*2,1)))
    j=base+np.arange(len(pts)-1)*2;indices.append(np.column_stack([j,j+1,j+2,j+1,j+3,j+2]).ravel());base+=len(pts)*2
arrays=[np.concatenate(positions).astype('<f4'),np.concatenate(tangents).astype('<f4'),np.concatenate(uvs).astype('<f4'),np.concatenate(types).astype('<f4'),np.concatenate(indices).astype('<i4')]
with (SRC/'waterways_0201.bin').open('wb') as f:
    f.write(struct.pack('<II',len(arrays[0]),len(arrays[-1])))
    for a in arrays:f.write(a.tobytes())
report={'version':'0.2.0.3','rivers':sorted(river_names),'river_features':len(paths)-4,'passages':passages,'restored_black_sea_pixels':black,'restored_marmara_pixels':marmara,'river_source':'Natural Earth 1:10m rivers, public domain; ranks 0–6, named rivers plus eight connecting unnamed features, excludes lake centre lines','vertices':base,'province_geometry_preserved':True,'inland_lakes_remain_excluded':True}
(ROOT/'data/waterways.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('WATERWAYS_PREPARED',len(river_names),'named river entries;',[(p['name'],p['ends']) for p in passages],flush=True)
