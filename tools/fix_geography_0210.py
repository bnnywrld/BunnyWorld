"""Authored 0.2.0.10 corrections, from the unchanged GitHub 0.2.0.9 baseline.

Offline only: coherent state unions, terrain/river-guided province revisions,
Pacific connectivity, ownership border bands, and complete linked accounts.
"""
from pathlib import Path
from collections import Counter, defaultdict
import copy,json,shutil
import numpy as np
from PIL import Image
from scipy.ndimage import (find_objects,label,gaussian_filter,binary_dilation,
                          distance_transform_edt,maximum)
from scipy.spatial import cKDTree
from skimage.graph import MCP_Geometric
from skimage.segmentation import watershed
from skimage.measure import label as ownership_components
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from pyproj import Transformer
from fix_geography_0209 import atomic_png
from fix_geography_0208 import focus,alloc,xyz,AREA
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography'
BASE=ROOT/'.geography_0210_baseline';VERSION='0.2.0.10'
Image.MAX_IMAGE_PIXELS=None

def read(p):return json.loads(Path(p).read_text())
def write(p,obj):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')))

def snapshot():
 names=['data/'+n+'.json' for n in ['world','provinces','cities','urban_population','urban_scenery','geography_bundle','sea_regions','protected_territories_0209']]
 names+=['tools/cartography/grouped_atlas_022r2.npz','tools/cartography/province_atlas_0209.npz','assets/sea_ids.png','assets/border_fade.png']
 if (BASE/'data/world.json').exists():
  assert read(BASE/'data/world.json')['version']=='0.2.0.9';return
 assert read(ROOT/'data/world.json')['version']=='0.2.0.9','Requires 0.2.0.9'
 for n in names:
  p=BASE/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,p)

def natural_partition(sm,old,ids,sid,top,left,elev,rivers,cities):
 """Retain province IDs and seed distribution on an isotropic local km grid.

Strong, smooth terrain costs and mapped rivers replace the near-uniform
8-direction growth that produced straight equal-distance cells in 0.2.0.9.
Small deterministic broad-scale variation resolves flat terrain; no boundary
jitter is applied to the final atlas. State and country masks stay fixed.
 """
 H,W=8192,16384
 yy,xx=np.nonzero(sm);gy=yy+top;gx=xx+left;u,v=focus(gy,gx);lon0=u*360-180;lat0=90-v*180
 proj=Transformer.from_crs('EPSG:4326',f'+proj=laea +lat_0={lat0} +lon_0={lon0} +datum=WGS84 +units=km',always_xy=True)
 inv=Transformer.from_crs(proj.target_crs,'EPSG:4326',always_xy=True)
 px,py=proj.transform((gx+.5)/W*360-180,90-(gy+.5)/H*180);points=np.column_stack([px,py]);tree=cKDTree(points)
 step=1.5;west=px.min()-step*2;south=py.min()-step*2
 ix=np.floor((px-west)/step).astype(int);iy=np.floor((py-south)/step).astype(int)
 shape=(int(iy.max())+3,int(ix.max())+3);mask=np.zeros(shape,bool);mask[iy,ix]=True;mask=binary_dilation(mask,iterations=1)
 y,x=np.indices(shape);lo,la=inv.transform(west+(x+.5)*step,south+(y+.5)*step)
 rows=np.clip(((90-la)/180*elev.shape[0]).astype(int),0,elev.shape[0]-1);cols=((lo+180)/360*elev.shape[1]).astype(int)%elev.shape[1]
 z=gaussian_filter(np.maximum(0,elev[rows,cols]).astype(float),1.2);slope=np.hypot(*np.gradient(z))/step
 # Spatial variation has scales in kilometres, independent of native latitude.
 rng=np.random.default_rng(sid+21000)
 def field(km):
  q=gaussian_filter(rng.standard_normal(shape),km/step);return q/max(float(q[mask].std()),1e-6)
 broad=field(22);fine=field(7)
 cost=np.exp(np.clip(.65*broad+.22*fine,-1.4,1.4))+.75+np.clip(slope/35,0,5)+gaussian_filter(rivers[rows,cols].astype(float),.65)*8
 cost[~mask]=np.inf;markers=np.zeros(shape,np.int32)
 # One retained anchor per province; use an existing city in its footprint
 # where possible so a city does not drift to a neighbouring province.
 seed_positions={}
 for i,pid in enumerate(ids,1):
  py0,px0=np.nonzero(old==pid)
  candidates=[c for c in cities if c['province_id']==pid]
  if candidates:
   c=max(candidates,key=lambda q:q.get('population_rank',0));q=proj.transform(c['longitude'],c['latitude']);j=int(tree.query(q)[1])
   if old[yy[j],xx[j]]!=pid:candidates=[]
  if not candidates:
   dist=distance_transform_edt(old==pid,sampling=(1,max(.2,np.cos(np.deg2rad(lat0)))))
   cy,cx=np.unravel_index(np.argmax(dist),dist.shape);q=proj.transform((cx+left+.5)/W*360-180,90-(cy+top+.5)/H*180);j=int(tree.query(q)[1])
  sy,sx=iy[j],ix[j]
  if markers[sy,sx]:
   available=(old[yy,xx]==pid)&(markers[iy,ix]==0);jj=np.flatnonzero(available);assert len(jj);j=int(jj[0]);sy,sx=iy[j],ix[j]
  markers[sy,sx]=i;seed_positions[pid]=[int(gy[j]),int(gx[j])]
 distance,_=MCP_Geometric(cost,fully_connected=True).find_costs(np.column_stack(np.nonzero(markers)))
 reached=mask&np.isfinite(distance);grown=watershed(np.where(reached,distance,0),markers,mask=reached,connectivity=2)
 result=np.array(ids,np.uint16)[np.maximum(grown[iy,ix]-1,0)]
 # Preserve disconnected genuine islands if projection sampling did not reach
 # them. Only mainland portions are redrawn, never unseeded island identities.
 empty=grown[iy,ix]==0;result[empty]=old[yy[empty],xx[empty]]
 native=old.copy();native[sm]=result
 # Rasterization can separate a few corner pixels. Keep each province
 # connected on each state landmass, moving only the detached remnant.
 land,_=label(sm,np.ones((3,3),bool));repaired=0
 for _ in range(3):
  edits=0
  for pid in ids:
   parts,n=label(native==pid,np.ones((3,3),bool))
   if n<2:continue
   sizes=np.bincount(parts.ravel());best={};which={}
   for j in range(1,n+1):
    y1,x1=np.nonzero(parts==j);lid=int(land[y1[0],x1[0]]);which[j]=lid
    if lid not in best or sizes[j]>sizes[best[lid]]:best[lid]=j
   for j,lid in which.items():
    if j==best[lid]:continue
    m=parts==j;ring=binary_dilation(m,np.ones((3,3),bool))&sm&~m;ns=native[ring];ns=ns[(ns!=pid)&np.isin(ns,ids)]
    if len(ns):native[m]=int(np.bincount(ns).argmax());edits+=int(sizes[j])
  repaired+=edits
  if not edits:break
 assert set(map(int,np.unique(native[sm])))==set(ids),(sid,'Province identity lost')
 return native,{'state':sid,'provinces':len(ids),'changed_pixels':int(np.count_nonzero(sm&(native!=old))),'connectivity_pixels':repaired,'anchors':seed_positions}

def main():
 snapshot();w=read(BASE/'data/world.json');ps=read(BASE/'data/provinces.json');oldps=copy.deepcopy(ps)
 oldw=copy.deepcopy(w);states=np.load(BASE/'tools/cartography/grouped_atlas_022r2.npz')['regions'];province=np.load(BASE/'tools/cartography/province_atlas_0209.npz')['provinces'];H,W=states.shape
 report={'version':VERSION,'baseline_commit':'cb61e7c3db749ca079ee1aa077395143af215bdb','baseline_version':'0.2.0.9','state_merges':[],'province_redraws':[]}
 def find(tag,name):return next(int(k) for k,s in w['regions'].items() if s['owner']==tag and s['name']==name)
 def merge(target,others,name):
  s=w['regions'][str(target)];before=s['name'];sources=[target]+others
  for sid in others:
   q=w['regions'].pop(str(sid));states[states==sid]=target
   s['population']+=q['population']
   for b,n in q['buildings'].items():s['buildings'][b]=s['buildings'].get(b,0)+n
   for key in ['cores','claims','source_states','geographic_divisions','geographic_codes','protected_territories']:
    s[key]=sorted(set(s.get(key,[]))|set(q.get(key,[])))
  for p in ps.values():
   if p['region'] in others:p['region']=target
  s['name']=name;report['state_merges'].append({'target':target,'sources':sources,'name':name,'previous_name':before})
 merge(find('IND','Central Kalimantan'),[find('IND',n) for n in ['South Kalimantan','Western Central Kalimantan','Eastern Central Kalimantan']],'Central–South Kalimantan')
 merge(455,[456],'Mahaica-Berbice')
 cities=read(BASE/'data/cities.json');elev=np.load(SRC/'etopo_021.npz')['meters']
 rivers=rasterize([(f['geometry'],1) for f in read(SRC/'rivers_0201.geojson')['features'] if f['properties'].get('featurecla')=='River' and f['geometry'].get('coordinates')],out_shape=elev.shape,transform=from_bounds(-180,-90,180,90,elev.shape[1],elev.shape[0]),dtype='uint8')
 boxes=find_objects(states,max_label=8191)
 for sid in sorted({q['state'] for q in read(ROOT/'data/geography_0209_report.json')['density_splits']}):
  bb=boxes[sid-1];sm=states[bb]==sid;ids=sorted(p['id'] for p in ps.values() if p['region']==sid)
  out,row=natural_partition(sm,province[bb],ids,sid,bb[0].start,bb[1].start,elev,rivers,cities)
  province[bb][sm]=out[sm];report['province_redraws'].append(row)
  for pid in ids:ps[str(pid)]['geometry_source']='0.2.0.10 equal-area terrain/river-guided growth with retained province identity and settlement anchors'
  print('REDRAW',sid,w['regions'][str(sid)]['name'],len(ids),row['changed_pixels'],flush=True)
 del elev,rivers
 # Refresh areas, actual focus points and complete symmetric adjacency.
 boxes=find_objects(states,max_label=8191)
 for k,s in w['regions'].items():
  bb=boxes[int(k)-1];yy,xx=np.nonzero(states[bb]==int(k));yy+=bb[0].start;xx+=bb[1].start
  s.update(provinces=[],map_center=focus(yy,xx),area_km2=round(float(AREA[yy].sum()),2))
 boxes=find_objects(province,max_label=max(map(int,ps)))
 for k,p in ps.items():
  bb=boxes[int(k)-1];yy,xx=np.nonzero(province[bb]==int(k));yy+=bb[0].start;xx+=bb[1].start
  p.update(map_center=focus(yy,xx),area_km2=round(float(AREA[yy].sum()),2),neighbors=[],cities=[],urban_group='')
  w['regions'][str(p['region'])]['provinces'].append(int(k))
 for s in w['regions'].values():
  s['provinces'].sort()
  for j,pid in enumerate(s['provinces'],1):ps[str(pid)]['local_index']=j
 edges=set()
 for top in range(0,H,128):
  for l,r in [(province[top:top+128,:-1],province[top:top+128,1:]),(province[top:min(H-1,top+128)],province[top+1:min(H,top+129)])]:
   m=(l>0)&(r>0)&(l!=r);codes=np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m]);edges.update(divmod(int(c),65536) for c in np.unique(codes))
 for l,r in zip(province[:,0],province[:,-1]):
  if l and r and l!=r:edges.add(tuple(sorted((int(l),int(r)))))
 for l,r in edges:ps[str(l)]['neighbors'].append(r);ps[str(r)]['neighbors'].append(l)
 for p in ps.values():p['neighbors'].sort()
 # Coordinate relinking retains buildings and every state population total.
 oldurban=read(BASE/'data/urban_population.json');scene=read(BASE/'data/urban_scenery.json');groups={}
 def locate(lon,lat,tag):
  x=int((lon+180)/360*W)%W;y=min(H-1,max(0,int((90-lat)/180*H)));pid=int(province[y,x])
  if pid and w['regions'][str(ps[str(pid)]['region'])]['owner']==tag:return pid
  for radius in [12,40]:
   yy,xx=np.mgrid[max(0,y-radius):min(H,y+radius+1),max(0,x-radius):min(W,x+radius+1)];q=province[yy,xx]
   valid=np.isin(q,[p['id'] for p in ps.values() if w['regions'][str(p['region'])]['owner']==tag])
   if valid.any():
    j=np.unravel_index(np.argmin(np.where(valid,(yy-y)**2+(xx-x)**2,np.inf)),valid.shape);return int(q[j])
  raise ValueError(('City cannot be linked',lon,lat,tag))
 for c in cities:
  pid=locate(c['longitude'],c['latitude'],c['country']);c['province_id']=pid;p=ps[str(pid)];p['cities'].append(c['name'])
  if not p['urban_group']:p['urban_group']=c.get('urban_group') or 'geographic_city_%05d'%pid
  c['urban_group']=p['urban_group']
 for kind in ['clusters','landmarks']:
  for record in scene[kind]:
   tag=oldw['regions'][str(oldps[str(record['province'])]['region'])]['owner']
   pid=locate(record['longitude'],record['latitude'],tag);p=ps[str(pid)];record['province']=pid
   if not p['urban_group']:p['urban_group']=record.get('group') or 'geographic_city_%05d'%pid
   record['group']=p['urban_group']
   if kind=='landmarks':record['country']=tag
 for p in ps.values():
  gid=p['urban_group'];p['kind']='city' if gid else 'rural'
  if gid not in groups and gid:
   groups[gid]=copy.deepcopy(oldurban['groups'].get(gid,{'id':gid,'name':p['cities'][0] if p['cities'] else gid,'cities':[]}))
   groups[gid].update(provinces=[],population_2000=0,settlement_population_2000=0,representative_buildings=0,country_at_start=w['regions'][str(p['region'])]['owner'])
  if gid:groups[gid]['provinces'].append(p['id'])
 for cluster in scene['clusters']:groups[cluster['group']]['representative_buildings']+=len(cluster['instances'])
 account=copy.deepcopy(oldurban);account.update(groups=groups,states={})
 for k,s in w['regions'].items():
  pp=s['provinces'];weights=[oldps[str(pid)]['population_2000'] for pid in pp]
  for pid,n in zip(pp,alloc(s['population'],weights)):ps[str(pid)]['population_2000']=int(n)
  urban=[pid for pid in pp if ps[str(pid)]['urban_group']];shared=[pid for pid in pp if pid not in urban];up=sum(ps[str(pid)]['population_2000'] for pid in urban)
  q=copy.deepcopy(oldurban['states'].get(k,{}));q.update(state=int(k),population_2000=s['population'],urban_provinces=urban,shared_provinces=shared,urban_population_2000=up,shared_population_2000=s['population']-up);account['states'][k]=q
 for p in ps.values():
  if p['urban_group']:groups[p['urban_group']]['population_2000']+=p['population_2000']
 for g in groups.values():g['settlement_population_2000']=g['population_2000'];g['provinces'].sort()
 for c in cities:c['population_2000']=ps[str(c['province_id'])]['population_2000']
 # Vatican's subpixel overlay is authoritative, as in the accepted baseline.
 micro=read(ROOT/'data/microstate_geometry.json');w['regions'][str(micro['state'])].update(map_center=micro['center_uv'],area_km2=micro['nominal_area_km2']);ps[str(micro['province'])].update(map_center=micro['center_uv'],area_km2=micro['nominal_area_km2'])
 for tag,c in w['countries'].items():
  c['regions']=sorted(int(k) for k,s in w['regions'].items() if s['owner']==tag);c['population']=sum(w['regions'][str(s)]['population'] for s in c['regions'])
  if c['capital'] not in c['regions']:
   c['capital']=next((m['target'] for m in report['state_merges'] if c['capital'] in m['sources']),c['regions'][0])
  c['map_center']=w['regions'][str(c['capital'])]['map_center']
 w.update(version=VERSION,scenario_id='bunny_world_2000_0_2_0_10');scene['version']=VERSION
 w['map']['province_geometry']='Retained global atlas; affected 0.2.0.9 density states redrawn with local equal-area terrain/river guidance and stable province identities.'
 for name,obj in [('world',w),('provinces',ps),('cities',cities),('urban_population',account),('urban_scenery',scene)]:write('data/'+name+'.json',obj)
 protected=read(BASE/'data/protected_territories_0209.json');protected['version']=VERSION
 aliases={sid:m['target'] for m in report['state_merges'] for sid in m['sources']}
 for item in protected['territories']:item['states']=sorted({aliases.get(s,s) for s in item['states']})
 write('data/protected_territories_0210.json',protected)
 np.savez_compressed(SRC/'grouped_atlas_022r2.npz',regions=states)
 np.savez_compressed(SRC/'province_atlas_022r2.npz',provinces=province);shutil.copyfile(SRC/'province_atlas_022r2.npz',SRC/'province_atlas_0210.npz')
 index=np.zeros((65536,3),np.uint8)
 for p in ps.values():index[p['id'],:2]=[p['region']&255,p['region']>>8]
 index[65535,:2]=[255,31];atomic_png(index.reshape(256,256,3),ROOT/'assets/province_index.png')
 for i in range(4):
  y,x=i//2*4096,i%2*8192;q=province[y:y+4096,x:x+8192].copy();q[states[y:y+4096,x:x+8192]==8191]=65535
  atomic_png(np.stack([(q&255).astype(np.uint8),(q>>8).astype(np.uint8),np.zeros_like(q,np.uint8)],-1),ROOT/'assets'/f'region_ids_{i}.png')
 # All of the southern West Polynesia arm joins Tasman, including the corridor
 # separating its southeastern enclave. Only water identities change.
 rgb=np.asarray(Image.open(BASE/'assets/sea_ids.png'),np.uint16);sea=rgb[:,:,0]+rgb[:,:,1]*256;hh,ww=sea.shape;before=sea.copy()
 lat=90-(np.arange(hh)+.5)/hh*180;lon=(np.arange(ww)+.5)/ww*360-180
 # Follow a broad northern edge from New Caledonia toward the existing
 # Niue/Tasman extension; remove the narrow eastern stub as well as the arm.
 sea[(sea==178)&((lat[:,None]<-25)|((lon[None,:]%360>190)&(lat[:,None]<-18)))]=86
 # A four-pixel source-registration shard west of Tasmania belongs to the
 # adjacent Southern Indian Ocean, not a detached Tasman identity.
 parts,n=label(sea==86,np.ones((3,3),bool));sizes=np.bincount(parts.ravel())
 for j in range(1,n+1):
  if sizes[j]>=32:continue
  m=parts==j;ring=binary_dilation(m,np.ones((3,3),bool));ns=sea[ring];ns=ns[(ns>0)&(ns!=86)]
  if len(ns):sea[m]=int(np.bincount(ns).argmax())
 definitions=read(BASE/'data/sea_regions.json');edges=set()
 for k,q in definitions.items():
  yy,xx=np.nonzero(sea==int(k));assert len(xx);v=xyz(lon[xx[::max(1,len(xx)//100000)]],lat[yy[::max(1,len(xx)//100000)]]);j=int(np.argmax(v@v.mean(0)))*max(1,len(xx)//100000)
  q.update(map_center=[(float(xx[j])+.5)/ww,(float(yy[j])+.5)/hh],neighbors=[])
 for l,r in [(sea[:,:-1],sea[:,1:]),(sea[:-1],sea[1:]),(sea[:,-1:],sea[:,:1])]:
  m=(l>0)&(r>0)&(l!=r);codes=np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m]);edges.update(map(int,np.unique(codes)))
 for code in edges:
  l,r=divmod(code,65536);definitions[str(l)]['neighbors'].append(r);definitions[str(r)]['neighbors'].append(l)
 for q in definitions.values():q['neighbors'].sort()
 write('data/sea_regions.json',definitions);atomic_png(np.stack([(sea&255).astype(np.uint8),(sea>>8).astype(np.uint8),np.zeros_like(sea,np.uint8)],-1),ROOT/'assets/sea_ids.png')
 report['sea_pixels_reassigned']=int(np.count_nonzero(sea!=before))
 # Ownership bands are regenerated from CURRENT states, not the 0.2.0.3 mask.
 owner=np.zeros(8192,np.uint16)
 for k,s in w['regions'].items():owner[int(k)]=w['countries'][s['owner']]['index']
 owners=owner[states[1::2,1::2]];edge=np.zeros_like(owners,bool)
 for axis,shift in [(0,1),(0,-1),(1,1),(1,-1)]:
  other=np.roll(owners,shift,axis);other_sea=np.roll(sea,shift,axis)
  edge|=((owners>0)&(other>0)&(owners!=other))|((owners>0)&(other==0)&(other_sea>0))
 distance=distance_transform_edt(~edge);components=ownership_components(owners,connectivity=1)
 maxima=maximum(distance,components,index=np.arange(int(components.max())+1));widths=np.clip(maxima*.30,1.,5.);t=np.clip(1-distance/widths[components],0,1);band=t*t*(3-2*t);band[owners==0]=0
 atomic_png(np.round(band*255).astype(np.uint8),ROOT/'assets/border_fade.png');report['border_band']='Rebuilt globally from 0.2.0.10 ownership, including Sweden/Åland transfers.'
 report.update(states=len(w['regions']),land_provinces=len(ps),countries=len(w['countries']),population=sum(s['population'] for s in w['regions'].values()))
 write('data/geography_0210_report.json',report)
 print('GEOGRAPHY_0210_COMPLETE',report['states'],len(ps),'sea pixels',report['sea_pixels_reassigned'],flush=True)
if __name__=='__main__':main()
