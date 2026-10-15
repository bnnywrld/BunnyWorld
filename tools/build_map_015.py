"""0.1.5: high-detail coastlines, corrected regions and nested gameplay provinces.
Requires numpy, scipy, Pillow, pyshp, shapely. All GIS inputs are bundled.
Run on the 0.1.4 atlas (or rerun detailed-map + prepare_013 before this script).
B stores 1-based local province index; R/G continue to store the region ID.
"""
import json,io,zipfile,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import shapefile
from scipy.ndimage import distance_transform_edt,find_objects
from scipy.spatial import cKDTree
from shapely.geometry import shape,mapping,box
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography';W,H=16384,8192
world=json.loads((ROOT/'data/world.json').read_text());regions=world['regions']
result=np.zeros((H,W),np.uint16)
for i in range(4):
 rgb=np.asarray(Image.open(ROOT/f'assets/region_ids_{i}.png'),dtype=np.uint16)
 result[(i//2)*4096:(i//2+1)*4096,(i%2)*8192:(i%2+1)*8192]=rgb[:,:,0]+rgb[:,:,1]*256

def paint(draw,geo,value,width=W,height=H):
 polys=geo['coordinates'] if geo['type']=='MultiPolygon' else [geo['coordinates']]
 for poly in polys:
  pts=[((lon+180)/360*width,(90-lat)/180*height) for lon,lat,*rest in poly[0]]
  draw.polygon(pts,fill=value)
  for hole in poly[1:]:draw.polygon([((lon+180)/360*width,(90-lat)/180*height) for lon,lat,*rest in hole],fill=0)

def mask(geo):
 im=Image.new('1',(W,H),0);paint(ImageDraw.Draw(im),geo,1);return np.asarray(im).copy()

# Detailed coastlines/lakes are geographic only: never import GSHHG's political layer.
landim=Image.new('1',(W,H),0);draw=ImageDraw.Draw(landim);vertices=0
with zipfile.ZipFile(SRC/'gshhg_high.zip') as z:
 for level,value in [(1,1),(5,1),(2,0),(3,1),(4,0)]:
  stem=f'GSHHS_shp/h/GSHHS_h_L{level}'
  reader=shapefile.Reader(shp=io.BytesIO(z.read(stem+'.shp')),shx=io.BytesIO(z.read(stem+'.shx')))
  for s in reader.iterShapes():
   vertices+=len(s.points)
   starts=list(s.parts)+[len(s.points)]
   for a,b in zip(starts,starts[1:]):
    points=np.array(s.points[a:b],dtype=float)
    # GSHHG cuts dateline polygons; transform 0..360 hemispheres separately.
    if len(points)<3:continue
    for shift in [-360,0]:
     p=points.copy();p[:,0]+=shift
     if p[:,0].max() < -180 or p[:,0].min()>180:continue
     draw.polygon([((lon+180)/360*W,(90-lat)/180*H) for lon,lat in p],fill=value)
land=np.asarray(landim).copy();del landim,draw
# Preserve tiny imported bases/islets and every region's focus pixel. They are
# explicit scenario abstractions, not claimed coastline measurements.
counts=np.bincount(result.ravel(),minlength=4096)
for sid,r in regions.items():
 if counts[int(sid)] < 80:
  land[result==int(sid)]=True
# Fit the political raster to the finer geographic land. Fill added coastal
# strips from neighboring land IDs, in bounded bands to control build-time RAM.
for top in range(0,H,512):
 lo=max(0,top-256);hi=min(H,top+768);sl=result[lo:hi];missing=land[lo:hi]&(sl==0)
 if np.any(missing):
  near=distance_transform_edt(sl==0,return_distances=False,return_indices=True)
  fill=sl[near[0],near[1]];a=top-lo;b=min(H,top+512)-lo
  local=missing[a:b];dst=result[top:top+b-a];dst[local]=fill[a:b][local]
result[~land]=0
print('Detailed shoreline vertices',vertices,flush=True)
subs=json.loads((SRC/'geographic_subdivisions.geojson').read_text())['features']
# Remove incorrect old custom pieces before drawing their geographic replacements.
def remove_ids(ids,eligible):
 for sid in ids:
  ys,xs=np.nonzero(result==sid)
  if not len(ys):continue
  t,b=max(0,ys.min()-100),min(H,ys.max()+101);l,r=max(0,xs.min()-100),min(W,xs.max()+101)
  tile=result[t:b,l:r];valid=np.isin(tile,eligible)
  if not valid.any():raise ValueError(('no geographic replacement',sid))
  idx=distance_transform_edt(~valid,return_distances=False,return_indices=True);dest=tile[idx[0],idx[1]];tile[tile==sid]=dest[tile==sid]
can=[int(s) for s,r in regions.items() if r['owner']=='CAN' and int(s) not in [763,762,1159,1160]]
remove_ids([763,762,1159,1160],can)
for f in subs:
 if f['properties']['adm1_code']=='CAN-682':result[mask(f['geometry'])&land]=763
 if f['properties']['adm1_code']=='CAN-683':
  m=mask(f['geometry'])&land;ys,xs=np.nonzero(m);lat=90-(ys+.5)/H*180;lon=(xs+.5)/W*360-180
  result[ys,xs]=np.where(lat>=55,1160,np.where(lon<-73,1159,762))
remove_ids([705,706],[int(s) for s,r in regions.items() if r['owner']=='GEO'])
for f in json.loads((SRC/'disputed_areas.geojson').read_text())['features']:
 name=f['properties'].get('BRK_NAME')
 if name in ['Abkhazia','South Ossetia']:result[mask(f['geometry'])&land]=706 if name=='Abkhazia' else 705
for f in json.loads((SRC/'control_2000_overrides.geojson').read_text())['features']:
 m=mask(f['geometry'])&(result==f['properties']['within']);result[m]=f['properties']['region']
remove_ids([497,931],[int(s) for s,r in regions.items() if r['owner'] in ['BRM','SHN']])
townships=json.loads((SRC/'myanmar_townships.geojson').read_text())['features']
# Core Wa area: five townships east of the Salween. Do not include Hopang,
# which changed control much later (2024). Modern admin geometry is only a
# geographic proxy for the scenario's control perimeter, not historical survey data.
core=unary_union([shape(f['geometry']) for f in townships if f['properties']['shapeName'] in ['Mongmao','Pangwaun','Namphan','Nam Phan','Narphan','Pangsang','Matman']])
result[mask(mapping(core))&land]=497
# Southern 171 area uses an explicitly approximate control polygon, constrained
# to Myanmar land. It is not a whole Shan township or the 2008 Wa admin division.
south=shape({'type':'Polygon','coordinates':[[[98.69,20.12],[98.76,20.64],[99.02,20.90],[99.16,20.77],[99.28,20.43],[99.55,20.30],[99.78,20.12],[99.70,19.88],[99.43,19.89],[99.27,20.02],[99.10,20.01],[98.92,19.94],[98.69,20.12]]]})
myanmar=unary_union([shape(f['geometry']) for f in subs if f['properties'].get('admin') in ['Myanmar','Myanmar (Burma)']])
# NE calls the country Myanmar; retain only scenario Burmese/Shan/Wa land.
m=mask(mapping(south));m &= np.isin(result,[int(s) for s,r in regions.items() if r['owner'] in ['BRM','SHN','WAA']]);result[m]=931
# Reapply known named large lakes to prevent coastal filling/internal boundaries
# from treating water as a province.
for f in json.loads((SRC/'lakes.geojson').read_text())['features']:
 if f['properties'].get('scalerank',99)<=4:result[mask(f['geometry'])]=0
# Restore any tiny region whose shoreline placement lost it (bounded footprint).
present=set(np.unique(result))
for sid,r in regions.items():
 if int(sid) not in present:
  u,v=r['map_center'];x=int(u*W);y=int(v*H);result[max(0,y-2):y+3,max(0,x-2):x+3]=int(sid)
print('Boundary corrections complete',flush=True)
# Nested Voronoi gameplay cells with immutable original province IDs. Placement
# is deterministic and relative to actual corrected parent polygons. Two Lloyd
# passes spread cells; seeds always lie on parent pixels and remain unique.
boxes=find_objects(result,max_label=1250);blue=np.zeros((H,W),np.uint8);province_map=np.zeros((H,W),np.uint16);provinces={}
for sid,r in regions.items():
 rid=int(sid);bb=boxes[rid-1];yy,xx=np.nonzero(result[bb]==rid);yy+=bb[0].start;xx+=bb[1].start
 pids=sorted(r['provinces']);r['provinces']=pids;n=len(pids)
 assert 0<n<256 and len(xx)>=n,(sid,n,len(xx))
 scale=max(.12,math.cos(math.radians(90-yy.mean()/H*180)));coords=np.column_stack([xx*scale,yy])
 sample=coords[::max(1,len(coords)//6000)];chosen=[int(np.argmin(np.sum((sample-sample.mean(axis=0))**2,axis=1)))];d=np.sum((sample-sample[chosen[0]])**2,axis=1)
 for k in range(1,n):
  j=int(np.argmax(d));chosen.append(j);d=np.minimum(d,np.sum((sample-sample[j])**2,axis=1))
 seeds=sample[chosen].copy();tree=cKDTree(coords)
 for k in range(2):
  _,which=cKDTree(seeds).query(coords);counts=np.bincount(which,minlength=n)
  centers=np.column_stack([np.bincount(which,weights=coords[:,i],minlength=n)/np.maximum(counts,1) for i in range(2)])
  _,near=tree.query(centers);seeds=coords[near];assert len(np.unique(near))==n
 _,which=cKDTree(seeds).query(coords);blue[yy,xx]=(which+1).astype(np.uint8);province_map[yy,xx]=np.array(pids,np.uint16)[which]
 # Region focus remains a real pixel near the centroid, including dateline islands.
 mx=xx.mean();my=yy.mean()
 if xx.max()-xx.min()>W//2:
  use=xx<W//2 if np.count_nonzero(xx<W//2)>len(xx)//2 else xx>=W//2;mx=xx[use].mean();my=yy[use].mean()
 j=int(np.argmin((xx-mx)**2+(yy-my)**2));r['map_center']=[(float(xx[j])+.5)/W,(float(yy[j])+.5)/H]
 for local,pid in enumerate(pids):
  assert np.any(which==local),(sid,pid)
  provinces[str(pid)]={'id':pid,'region':rid,'local_index':local+1,'map_center':[(seeds[local,0]/scale+.5)/W,(seeds[local,1]+.5)/H],'neighbors':[],'buildings':{}}
 if rid%200==0:print('Provinces built through region',rid,flush=True)
# Only shared land edges create adjacency; no invented movement across water.
pairs=set()
for top in range(0,H,256):
 a=province_map[top:min(H,top+257)]
 for aa,bb in [(a[:,:-1],a[:,1:]),(a[:-1,:],a[1:,:])]:
  m=(aa!=bb)&(aa>0)&(bb>0);lo=np.minimum(aa[m],bb[m]).astype(np.uint32);hi=np.maximum(aa[m],bb[m]).astype(np.uint32)
  pairs.update(map(int,np.unique(lo*65536+hi)))
# Dateline is adjacent, unlike the top/bottom pole rows.
a=province_map[:,0];b=province_map[:,-1];m=(a>0)&(b>0)&(a!=b);pairs.update(map(int,np.minimum(a[m],b[m]).astype(np.uint32)*65536+np.maximum(a[m],b[m])))
for token in pairs:
 a,b=token//65536,token%65536;provinces[str(a)]['neighbors'].append(b);provinces[str(b)]['neighbors'].append(a)
for p in provinces.values():p['neighbors'].sort()
for tag,c in world['countries'].items():
 sid=str(c['capital'])
 if sid not in regions or regions[sid]['owner']!=tag:sid=str(max(c['regions'],key=lambda s:regions[str(s)]['population']))
 c['map_center']=regions[sid]['map_center']
for i in range(4):
 sl=np.s_[(i//2)*4096:(i//2+1)*4096,(i%2)*8192:(i%2+1)*8192];ids=result[sl];rgb=np.zeros((*ids.shape,3),np.uint8);rgb[:,:,0]=ids&255;rgb[:,:,1]=ids>>8;rgb[:,:,2]=blue[sl]
 Image.fromarray(rgb).save(ROOT/f'assets/region_ids_{i}.png',optimize=True)
world['scenario_id']='bunny_world_2000_0_1_5';world['map']['cartography']='GSHHG high-resolution shorelines/lakes; geographic administrative regions'
world['map']['province_encoding']='Blue channel: 1-based index into sorted region.provinces'
world['map']['regional_boundary_accuracy']='Admin-1 geography; custom Quebec splits and Wa control proxies; other mod-only subdivisions remain bounded geographic approximations.'
(ROOT/'data/world.json').write_text(json.dumps(world,ensure_ascii=False,separators=(',',':')))
(ROOT/'data/provinces.json').write_text(json.dumps(provinces,separators=(',',':')))
report={'shoreline_vertices':vertices,'resolution':[W,H],'provinces':len(provinces),'land_adjacency_edges':len(pairs),'corrected_regions':[763,762,1159,1160,705,706,497,931],'province_geometry':'Deterministic gameplay cells clipped to geographic regions, retaining original MD province IDs. No demographic data. Not administrative or historical HOI4 province boundaries.','georgia_control_limit':'Pre-2008 Georgian-controlled Upper Kodori, Akhalgori and village corridors preserved through explicit geographic proxies, not precise surveyed lines.',
'wa_boundary_limit':'Northern core township union excluding later Hopang control; southern control perimeter is an approximate geographic proxy.','terrain':'NASA Blue Marble July 2004, static daytime topography, 16384x8192; geography reference, not 2000 political control'}
(ROOT/'data/update_015_report.json').write_text(json.dumps(report,indent=2));print('MAP_015_COMPLETE',report,flush=True)
