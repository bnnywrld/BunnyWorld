"""Native Natural Earth subdivisions over the explicit 0.1.5 scenario control mask.
Filtered geographic lakes; overlap allocation conserves national demographics and
buildings. Fresh geographic province IDs. Requires numpy/scipy/Pillow/pyshp.
"""
from pathlib import Path
import json,zipfile,io,math
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import distance_transform_edt,find_objects,zoom
from scipy.spatial import cKDTree
import shapefile
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography';W,H=16384,8192
world=json.loads((SRC/'world_seed_015.json').read_text());old=world['regions'];countries=world['countries'];N=8192;ANT=8191
oldmap=np.load(SRC/'control_seed_015.npz')['region_ids'].copy()

def paint(draw,geo,value):
 for poly in geo['coordinates'] if geo['type']=='MultiPolygon' else [geo['coordinates']]:
  draw.polygon([((lon+180)/360*W,(90-lat)/180*H) for lon,lat,*rest in poly[0]],fill=value)
  for hole in poly[1:]:draw.polygon([((lon+180)/360*W,(90-lat)/180*H) for lon,lat,*rest in hole],fill=0)
def shape_draw(draw,s,value):
 starts=list(s.parts)+[len(s.points)]
 for a,b in zip(starts,starts[1:]):
  pts=np.asarray(s.points[a:b],float)
  for shift in [-360,0]:
   if len(pts)<3:continue
   lon=pts[:,0]+shift
   if lon.max() < -180 or lon.min()>180:continue
   draw.polygon([((x+180)/360*W,(90-y)/180*H) for x,y in zip(lon,pts[:,1])],fill=value)
# Land without the thousands of tiny lake cut-outs.
canvas=Image.new('1',(W,H));draw=ImageDraw.Draw(canvas);kept_lakes=0
with zipfile.ZipFile(SRC/'gshhg_high.zip') as z:
 for level in [1,5]:
  stem=f'GSHHS_shp/h/GSHHS_h_L{level}';r=shapefile.Reader(shp=io.BytesIO(z.read(stem+'.shp')),shx=io.BytesIO(z.read(stem+'.shx')))
  for s in r.iterShapes():shape_draw(draw,s,1)
 stem='GSHHS_shp/h/GSHHS_h_L2';r=shapefile.Reader(shp=io.BytesIO(z.read(stem+'.shp')),dbf=io.BytesIO(z.read(stem+'.dbf')))
 for rec in r.iterShapeRecords():
  p=rec.record.as_dict()
  if float(p.get('area',p.get('area_full',0)))>=1000:shape_draw(draw,rec.shape,0);kept_lakes+=1
# Named regional exceptions and important seas/lakes use the existing NE reference.
important={'geneva','léman','balaton','garda','como','tahoe','champlain','dead sea','aral','caspian','baikal','victoria','tanganyika','malawi','titicaca','great salt'}
for f in json.loads((SRC/'lakes.geojson').read_text())['features']:
 p=f['properties'];name=str(p.get('name','')).lower()
 if any(n in name for n in important):paint(draw,f['geometry'],0)
land=np.asarray(canvas).copy();del canvas,draw
counts=np.bincount(oldmap.ravel(),minlength=4096)
for sid in old:
 if counts[int(sid)]<80:land[oldmap==int(sid)]=True
# Restored small-lake pixels inherit the nearest existing land region/control.
for top in range(0,H,512):
 lo=max(0,top-256);hi=min(H,top+768);a=top-lo;b=min(H,top+512)-lo;sl=oldmap[lo:hi];m=land[top:top+b-a]&(sl[a:b]==0)
 if m.any():
  ix=distance_transform_edt(sl==0,return_distances=False,return_indices=True);fill=sl[ix[0],ix[1]][a:b];dst=oldmap[top:top+b-a];dst[m]=fill[m]
oldmap[~land]=0
owner_lut=np.zeros(4096,np.uint16);owner_lut[4095]=255
for sid,r in old.items():owner_lut[int(sid)]=countries[r['owner']]['index']
control=owner_lut[oldmap]
admin=Image.new('I',(W,H),0);draw=ImageDraw.Draw(admin);features=json.loads((SRC/'geographic_subdivisions.geojson').read_text())['features']
for i,f in enumerate(features,1):paint(draw,f['geometry'],i)
admin=np.asarray(admin,dtype=np.uint16);del draw
# Geographic slivers/coastal islands inherit an adjacent geographic division.
for top in range(0,H,512):
 lo=max(0,top-256);hi=min(H,top+768);a=top-lo;b=min(H,top+512)-lo;sl=admin[lo:hi];m=(control[top:top+b-a]>0)&(control[top:top+b-a]<255)&(sl[a:b]==0)
 if m.any():
  ix=distance_transform_edt(sl==0,return_distances=False,return_indices=True);fill=sl[ix[0],ix[1]][a:b];dst=admin[top:top+b-a];dst[m]=fill[m]
admin[(control==0)|(control==255)]=0
# Remove raster rounding slivers at ordinary national borders. Preserve scenario
# breakaways and explicit tiny/base footprints; those are actual control pieces.
pre=admin.astype(np.uint32)*256+control;values,sizes=np.unique(pre,return_counts=True)
remap=np.tile(np.arange(256,dtype=np.uint16),len(features)+1);dominant={}
for key,n in zip(values,sizes):
 aid=int(key)//256;owner=int(key)%256
 if aid and 0<owner<255 and (aid not in dominant or n>dominant[aid][0]):dominant[aid]=(int(n),owner)
guests={'TAL','ACE','KAC','KAR','WAA','SHN','KUR','PUK','IEK','TML','NPM','CHE','ABK','SOO','NKR','PMR','SML','PUN','SNA','JUB','AIA','SWS','MLC','RCD','UNI','AFR','LUR','HEZ','HAM'}
by_owner={c['index']:tag for tag,c in countries.items()};cleaned=0
for key,n in zip(values,sizes):
 aid=int(key)//256;owner=int(key)%256
 if aid in dominant and 0<owner<255 and owner!=dominant[aid][1] and n<256 and by_owner[owner] not in guests and by_owner[dominant[aid][1]] not in guests:
  remap[int(key)]=dominant[aid][1];cleaned+=1
protected_lut=np.zeros(4096,bool)
for sid,r in old.items():protected_lut[int(sid)]=counts[int(sid)]<80 or int(sid) in [424,488,624,824,827] or 'base' in r['name'].lower() or 'camp' in r['name'].lower()
fixed=remap[pre];protect=protected_lut[oldmap];control[(control>0)&(control<255)&(~protect)]=fixed[(control>0)&(control<255)&(~protect)]
del pre,fixed,protect,remap
print('Cleaned rounding fragments',cleaned,flush=True)
# A division crossing a control boundary is split, rather than stretched to fit MD.
token=admin.astype(np.uint32)*256+control;token[(control==0)|(control==255)]=0
keys=np.unique(token);keys=keys[keys>0];assert len(keys)<ANT
lookup=np.zeros((len(features)+1)*256,np.uint16);regions={};by_index={c['index']:t for t,c in countries.items()}
for rid,key in enumerate(keys,1):
 aid=int(key)//256;tag=by_index[int(key)%256];p=features[aid-1]['properties'];name=p.get('name_en') or p.get('name') or countries[tag]['name']
 lookup[int(key)]=rid;regions[str(rid)]={'id':rid,'name':name,'owner':tag,'population':0,'buildings':{},'provinces':[],'geographic_code':p['adm1_code'],'geographic_name':name,'population_source':'Conservative allocation of supplied mod figures by geographic overlap; approximate regional figures'}
result=lookup[token];result[control==255]=ANT;del token,admin,lookup
print('Native regions',len(regions),'large GSHHG lakes',kept_lakes,flush=True)
# Aggregate overlaps with latitude-area correction, then allocate integers exactly.
weights=np.zeros((1251,len(regions)+1),np.float64)
for top in range(0,H,128):
 a=oldmap[top:top+128];b=result[top:top+128];m=(a>0)&(a<=1250)&(b>0)&(b<ANT)
 dest_owner=np.zeros(N,np.uint16)
 for sid,r in regions.items():dest_owner[int(sid)]=countries[r["owner"]]["index"]
 m &= owner_lut[a]==dest_owner[b]
 yy=np.broadcast_to(np.cos(np.deg2rad(90-(np.arange(top,min(H,top+128))+.5)/H*180))[:,None],a.shape)
 pair=a[m].astype(np.int64)*(len(regions)+1)+b[m];weights+=np.bincount(pair,weights=yy[m],minlength=weights.size).reshape(weights.shape)
def distribute(total,ids,w):
 values=np.array(w,float);values=values/values.sum()*total;v=np.floor(values).astype(np.int64);order=np.argsort(-(values-v),kind='stable');v[order[:int(total-v.sum())]]+=1
 return zip(ids,map(int,v))
quotas=np.zeros(len(regions)+1,float)
for sid,r in old.items():
 row=weights[int(sid)];ids=np.flatnonzero(row)
 if not len(ids):ids=np.array([int(s) for s,x in regions.items() if x['owner']==r['owner']]);ww=np.ones(len(ids))
 else:ww=row[ids]
 for rid,value in distribute(r['population'],ids,ww):regions[str(rid)]['population']+=value
 for k,value in r.get('buildings',{}).items():
  for rid,v in distribute(value,ids,ww):regions[str(rid)]['buildings'][k]=regions[str(rid)]['buildings'].get(k,0)+v
 quotas[ids]+=len(r['provinces'])*ww/ww.sum()
del weights,oldmap,land
# Geographic province cells, deterministic fresh IDs and land adjacency.
blue=np.zeros((H,W),np.uint8);province_map=np.zeros((H,W),np.uint16);provinces={};boxes=find_objects(result,max_label=len(regions));next_pid=1
for sid,r in regions.items():
 rid=int(sid);bb=boxes[rid-1];yy,xx=np.nonzero(result[bb]==rid);yy+=bb[0].start;xx+=bb[1].start;n=min(len(xx),200,max(1,round(quotas[rid])))
 scale=max(.12,math.cos(math.radians(90-yy.mean()/H*180)));coords=np.column_stack([xx*scale,yy]);sample=coords[::max(1,len(coords)//6000)]
 chosen=[int(np.argmin(np.sum((sample-sample.mean(axis=0))**2,axis=1)))];d=np.sum((sample-sample[chosen[0]])**2,axis=1)
 for k in range(1,n):
  j=int(np.argmax(d));chosen.append(j);d=np.minimum(d,np.sum((sample-sample[j])**2,axis=1))
 seeds=sample[chosen].copy();tree=cKDTree(coords)
 for k in range(2):
  _,which=cKDTree(seeds).query(coords);cnt=np.bincount(which,minlength=n);cent=np.column_stack([np.bincount(which,weights=coords[:,i],minlength=n)/np.maximum(cnt,1) for i in range(2)]);_,near=tree.query(cent);seeds=coords[near]
  assert len(np.unique(near))==n,(sid,n)
 _,which=cKDTree(seeds).query(coords);pids=list(range(next_pid,next_pid+n));next_pid+=n;r['provinces']=pids;blue[yy,xx]=(which+1).astype(np.uint8);province_map[yy,xx]=np.array(pids,np.uint16)[which]
 mx,my=xx.mean(),yy.mean()
 if xx.max()-xx.min()>W//2:
  use=xx<W//2 if np.count_nonzero(xx<W//2)>len(xx)//2 else xx>=W//2;mx,my=xx[use].mean(),yy[use].mean()
 j=int(np.argmin((xx-mx)**2+(yy-my)**2));r['map_center']=[(float(xx[j])+.5)/W,(float(yy[j])+.5)/H]
 for i,pid in enumerate(pids):
  assert np.any(which==i)
  provinces[str(pid)]={'id':pid,'region':rid,'local_index':i+1,'map_center':[(seeds[i,0]/scale+.5)/W,(seeds[i,1]+.5)/H],'neighbors':[],'buildings':{}}
 if rid%1000==0:print('Province cells',rid,flush=True)
assert next_pid<65536
pairs=set()
for top in range(0,H,256):
 a=province_map[top:min(H,top+257)]
 for aa,bb in [(a[:,:-1],a[:,1:]),(a[:-1,:],a[1:,:])]:
  m=(aa!=bb)&(aa>0)&(bb>0);lo=np.minimum(aa[m],bb[m]).astype(np.uint32);hi=np.maximum(aa[m],bb[m]).astype(np.uint32);pairs.update(map(int,np.unique(lo*65536+hi)))
a=province_map[:,0];b=province_map[:,-1];m=(a>0)&(b>0)&(a!=b);pairs.update(map(int,np.minimum(a[m],b[m]).astype(np.uint32)*65536+np.maximum(a[m],b[m])))
for key in pairs:
 a,b=key//65536,key%65536;provinces[str(a)]['neighbors'].append(b);provinces[str(b)]['neighbors'].append(a)
for p in provinces.values():p['neighbors'].sort()
for tag,c in countries.items():
 ids=[int(s) for s,r in regions.items() if r['owner']==tag];assert ids,tag
 assert sum(regions[str(s)]['population'] for s in ids)==c['population'],tag
 old_uv=c['map_center'];x=int(old_uv[0]*W);y=int(old_uv[1]*H);rid=int(result[y,x]);rid=rid if rid in ids else max(ids,key=lambda i:regions[str(i)]['population']);c['regions']=ids;c['capital']=rid;c['map_center']=regions[str(rid)]['map_center']
 # Prefer an actual capital's geographic point when it lies on owned terrain.
 for city in json.loads((ROOT/'data/cities.json').read_text()):
  if city['capital'] and city.get('country')==tag:
   u=(city['longitude']+180)/360;v=(90-city['latitude'])/180;rr=int(result[min(H-1,int(v*H)),int(u*W)%W])
   if rr in ids:c['capital']=rr;c['map_center']=[u,v];break
for i in range(4):
 sl=np.s_[(i//2)*4096:(i//2+1)*4096,(i%2)*8192:(i%2+1)*8192];a=result[sl];rgb=np.zeros((*a.shape,3),np.uint8);rgb[:,:,0]=a&255;rgb[:,:,1]=a>>8;rgb[:,:,2]=blue[sl];Image.fromarray(rgb).save(ROOT/f'assets/region_ids_{i}.png',optimize=True)
# Broad inward distance gradient. Small lookup, not a per-frame expensive transform.
coarse=control[::4,::4];border=(coarse!=np.roll(coarse,1,axis=1))|(coarse!=np.roll(coarse,-1,axis=1))|(coarse!=np.roll(coarse,1,axis=0))|(coarse!=np.roll(coarse,-1,axis=0));distance=distance_transform_edt(~border)
fade=np.exp(-distance*9.78/220)*255;fade[(coarse==0)|(coarse==255)]=0;Image.fromarray(fade.astype(np.uint8)).save(ROOT/'assets/border_fade.png')
world['regions']=regions;world['scenario_id']='bunny_world_2000_0_1_6';world['map'].update({'palette_width':N,'antarctica_region_id':ANT,'cartography':'Native Natural Earth admin-1 shapes, split at the explicit 2000 control layer, fitted to detailed coastline','regional_boundary_accuracy':'Geographic subdivisions are not forced into MD regions. Disputed control proxies inherited from documented 2000 overrides.','lakes':'GSHHG lakes >=1000 square km plus named important exceptions; small lakes removed from gameplay masks'})
(ROOT/'data/world.json').write_text(json.dumps(world,ensure_ascii=False,separators=(',',':')));(ROOT/'data/provinces.json').write_text(json.dumps(provinces,separators=(',',':')))
report={'version':'0.1.6','regions':len(regions),'native_divisions':len(features),'provinces':len(provinces),'adjacency_edges':len(pairs),'large_lakes':kept_lakes,'population':sum(r['population'] for r in regions.values()),'source_country_control':'0.1.5 geographic 2000 control, including Crimea and explicit Georgian/Wa proxies','allocation':'Country totals conserved; regional numbers allocated by latitude-weighted source-region overlap, approximate'};(ROOT/'data/update_016_report.json').write_text(json.dumps(report,indent=2));print('MAP_016_COMPLETE',report,flush=True)
