"""Targeted State repair, settlement-registered provinces and sparse interiors.
No rectangular State stretching or single-pixel province restoration.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,io,os,sys,zipfile,math
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import find_objects,distance_transform_edt,label,binary_dilation
from scipy.spatial import cKDTree
from skimage.graph import route_through_array
import struct

ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography'
BASE=Path(sys.argv[1]) if len(sys.argv)>1 else SRC/'baseline_0202';Image.MAX_IMAGE_PIXELS=None
world=json.load(open(BASE/'data/world.json'));oldps=json.load(open(BASE/'data/provinces.json'));cities=json.load(open(BASE/'data/cities.json'))
regions=np.load(BASE/'tools/cartography/grouped_atlas_022r2.npz')['regions'].copy()
oldatlas=np.load(BASE/'tools/cartography/province_atlas_0202.npz')['provinces'];H,W=regions.shape
reference=np.load(SRC/'reference_registered_0203.npz');md=reference['provinces'];pg=reference['source_state']
source_to_state=np.zeros(65536,np.uint16)
for key,r in world['regions'].items():
 for source in r['source_states']:source_to_state[source]=int(key)
mapped_state=source_to_state[pg[md]]
report={'version':'0.2.0.3','state_repairs':[],'province_repairs':[],'sparse_merges':[],'fragment_repairs':0,'preserved_population':sum(r['population'] for r in world['regions'].values())}
def write(name,obj): (ROOT/'data'/f'{name}.json').write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'),default=lambda v:v.item()))
def png(a,p):
 b=io.BytesIO();Image.fromarray(a).save(b,format='PNG',compress_level=6)
 with open(str(p)+'.new','wb') as f:f.write(b.getvalue());f.flush();os.fsync(f.fileno())
 os.replace(str(p)+'.new',p)
def npz(path,**arrays):
 b=io.BytesIO();np.savez_compressed(b,**arrays)
 with open(str(path)+'.new','wb') as f:f.write(b.getvalue());f.flush();os.fsync(f.fileno())
 os.replace(str(path)+'.new',path)
def ids_for(tags):return [int(k) for k,r in world['regions'].items() if r['owner'] in tags]
def box_of(mask):
 yy,xx=np.nonzero(mask);return np.s_[yy.min():yy.max()+1,xx.min():xx.max()+1]
def group_repair(name,ids):
 mask=np.isin(regions,ids);bb=box_of(mask);mask=mask[bb];view=regions[bb];sample=mapped_state[bb]
 valid=mask&np.isin(sample,ids)
 if valid.sum()<mask.sum()*.25:raise ValueError((name,'insufficient registration coverage',valid.mean()))
 # Keep every State represented by a meaningful reference footprint.
 absent=set(ids)-set(np.unique(sample[valid]))
 if absent:
  mask &= ~np.isin(view,list(absent));valid &= mask
  print('PRESERVE_OFFSHORE_REFERENCE',name,sorted(absent),flush=True)
 near=distance_transform_edt(~valid,return_distances=False,return_indices=True)
 filled=sample[tuple(near)]
 before=view.copy();view[mask]=filled[mask]
 report['state_repairs'].append({'area':name,'states':ids,'changed_pixels':int(np.count_nonzero(before!=view)),'native_fraction':round(valid.sum()/mask.sum(),4)})
 print('STATE_REPAIR',name,report['state_repairs'][-1],flush=True)

# Whole-country interiors share one registration. Accepted external land masks
# remain authoritative; narrow scenario controllers are repaired jointly.
group_repair('Egypt',ids_for(['EGY']))
group_repair('Niger',ids_for(['NGR']))
group_repair('Saudi Arabia and Rub al Khali',ids_for(['SAU']))
group_repair('Somali controllers',ids_for(['SML','SOM','SNA','JUB','PUN','SWS','AIA']))
group_repair('Transnistria and Moldova',ids_for(['PMR','MLV']))
group_repair('South Shan and neighboring Burma',ids_for(['BRM','SHN']))
group_repair('Basque and Castilla geography',ids_for(['SPR']))
group_repair('Sichuan and Chongqing',[575,576,573])
group_repair('Heilongjiang and Hulunbuir',[546,547,545,1082])
group_repair('Xinjiang Aksai Chin Ladakh Himachal',[581,582,579,578,979,427])
group_repair('Southern Vietnam',[511,512,513,514])
group_repair('Indian State registration',ids_for(['RAJ']))
group_repair('Congo State and controller geography',ids_for(['DRC','MLC','RCD']))

# Indonesian names previously occupied the wrong islands. Reconstitute their
# footprints jointly from the reference, then use real island geography to
# bound the two Timor States (including Oecusse in the eastern group).
ind=ids_for(['IND']);group_repair('Indonesia island-chain identities',ind)
lon=(np.arange(W)+.5)/W*360-180;lat=90-(np.arange(H)+.5)/H*180
timor=(lon[None,:]>123.3)&(lon[None,:]<127.5)&(lat[:,None]>-10.6)&(lat[:,None]<-8.0)&np.isin(regions,ind)
east=timor&((lon[None,:]>125.05)|((lon[None,:]>124.0)&(lon[None,:]<124.55)&(lat[:,None]>-9.6)))
regions[timor]=1169;regions[east]=1210
assert np.any(regions==1169) and np.any(regions==1210)

# Åland: restore actual island water gaps from the retained GSHHG coastline.
# This corrects physical coverage as well as the State label.
aland=104;bb=np.s_[int((90-61.05)/180*H):int((90-59.5)/180*H),int((18.7+180)/360*W):int((21.8+180)/360*W)]
canvas=Image.new('L',(bb[1].stop-bb[1].start,bb[0].stop-bb[0].start));draw=ImageDraw.Draw(canvas)
z=zipfile.ZipFile(SRC/'gshhg_high.zip');pre='GSHHS_shp/h/GSHHS_h_L1'
raw=z.read(pre+'.shp');offset=100
while offset<len(raw):
 length=struct.unpack_from('>I',raw,offset+4)[0]*2;start=offset+8;offset=start+length
 if length<44 or struct.unpack_from('<I',raw,start)[0]!=5:continue
 left,bottom,right,top=struct.unpack_from('<4d',raw,start+4)
 if right<18.7 or left>21.8 or top<59.5 or bottom>61.05:continue
 n_parts,n_points=struct.unpack_from('<2I',raw,start+36)
 parts=list(struct.unpack_from('<'+'I'*n_parts,raw,start+44))+[n_points]
 pts=np.frombuffer(raw,dtype='<f8',count=n_points*2,offset=start+44+4*n_parts).reshape(-1,2)
 for a,b in zip(parts[:-1],parts[1:]):draw.polygon([((x+180)/360*W-bb[1].start,(90-y)/180*H-bb[0].start) for x,y in pts[a:b]],fill=1)
physical=np.array(canvas,bool);view=regions[bb];before=view.copy()
# The source archipelago has passages below the 2.4-km atlas pixel size.
# Follow a least-land sea route and retain a minimum three-pixel gap so the
# half-resolution physical mask cannot reconnect the island to Finland.
left=int((20.30+180)/360*W)-bb[1].start;right=int((21.0+180)/360*W)-bb[1].start
cost=np.where(physical[:,left:right],50.0,1.0)
route,_=route_through_array(cost,(0,cost.shape[1]//2),(cost.shape[0]-1,cost.shape[1]//2),fully_connected=True)
cut=np.zeros_like(physical)
for y,x in route:cut[y,x+left]=True
cut=binary_dilation(cut,iterations=1);physical[cut]=False
view[~physical]=0
report['aland_minimum_separation']='Least-land open-water route widened to three atlas pixels to survive physical-mask sampling; tiny channel/islet adaptation at game scale.' 
# Main Åland archipelago lies west of 20.65 E; Finnish mainland State labels
# outside it are retained. Northern and eastern offshore islets stay islands.
archipelago=physical&(lon[bb[1]][None,:]<20.65)&(lat[bb[0]][:,None]<60.75)
view[archipelago]=aland
report['aland_coast_pixels_changed']=int(np.count_nonzero(before!=view))

# Quebec is explicitly one State. Merge all State accounts and rights, not
# just its display name, while preserving the Canadian aggregate exactly.
quebec=[750,1143,1144];dest=world['regions']['750'];dest['name']='Quebec'
for key in ['population']:dest[key]=sum(world['regions'][str(i)][key] for i in quebec)
dest['buildings']=dict(sum((Counter(world['regions'][str(i)]['buildings']) for i in quebec),Counter()))
for key in ['source_states','geographic_divisions','cores','claims']:dest[key]=sorted(set(v for i in quebec for v in world['regions'][str(i)].get(key,[])))
regions[np.isin(regions,quebec)]=750
for rid in quebec[1:]:del world['regions'][str(rid)]
source_to_state[np.isin(source_to_state,quebec)]=750

# Explicit new city anchors; scenario controllers and year-2000 status stay.
for name,tag,x,y,pop in [('Hong Kong','HKG',114.17,22.30,6665000),('Macau','MAC',113.55,22.19,431000)]:
 if not any(c['name']==name for c in cities):cities.append({'name':name,'country':tag,'longitude':x,'latitude':y,'capital':True,'population_rank':pop})

repair_ids=set(i for q in report['state_repairs'] for i in q['states'])
repair_ids.update(ids_for(['KOR']))
repair_ids.update([20,308,43,954,100,438,881,449,175,585,1090])
repair_ids.update(int(k) for k,r in world['regions'].items() if r['owner']=='RAJ' and r['map_center'][1]>.39)
repair_ids.difference_update([1143,1144])
boxes=find_objects(regions,max_label=8191)
tokens=oldatlas.astype(np.uint32) # Preserves existing successful provinces.
for rid in sorted(repair_ids):
 bb=boxes[rid-1];mask=regions[bb]==rid;view=tokens[bb];sample=md[bb]
 # Refit each province to the newly shared geography, allowing clipped source
 # cells at retained State edges. Never force missing labels into one pixel.
 parent=source_to_state[pg[sample]]
 valid=mask&(sample>0)&(parent==rid)
 if valid.sum()<mask.sum()*.10:
  valid=mask&(sample>0)
 if not valid.any():
  print('PRESERVE_OFFSHORE_PROVINCES',rid,flush=True);continue
 near=distance_transform_edt(~valid,return_distances=False,return_indices=True)
 filled=sample[tuple(near)].astype(np.uint32)+65536
 view[mask]=filled[mask]
 report['province_repairs'].append({'state':rid,'name':world['regions'][str(rid)]['name'],'reference_coverage':round(valid.sum()/mask.sum(),4)})
# Correct coastline additions inherit their nearest existing local province.
missing=(regions>0)&(tokens==0)
for rid in np.unique(regions[missing]):
 bb=boxes[int(rid)-1];mask=regions[bb]==rid;view=tokens[bb];valid=mask&(view>0)
 near=distance_transform_edt(~valid,return_distances=False,return_indices=True);view[mask&~valid]=view[tuple(near[:,mask&~valid])]
tokens[regions==0]=0

# Merge adjacent, almost empty original cells into bigger irregular provinces
# in Greenland, inland Australia, Sahara/Arabian deserts and Amazon interiors.
oldraw=np.load(BASE/'tools/cartography/population_022.npz')['total']
old_density=np.zeros(65536);has_city=np.zeros(65536,bool)
for key,p in oldps.items():old_density[int(key)]=oldraw[int(key)]/max(p['area_km2'],1);has_city[int(key)]=bool(p['cities'])
ref_population=np.zeros(65536);ref_area=np.zeros(65536);ref_city=np.zeros(65536,bool)
for key,p in oldps.items():
 source=p.get('source_md_province',0);ref_population[source]+=oldraw[int(key)];ref_area[source]+=p['area_km2'];ref_city[source]|=bool(p['cities'])
ref_density=ref_population/np.maximum(ref_area,1)
old_density[0]=1e9
for key,r in world['regions'].items():
 rid=int(key);bb=boxes[rid-1];mask=regions[bb]==rid;yy,xx=np.nonzero(mask)
 la=float(90-(yy.mean()+bb[0].start+.5)/H*180);lo=float((xx.mean()+bb[1].start+.5)/W*360-180)
 area_target=350000 if -75<lo<-10 and la>58 else 65000 if 112<lo<151 and -33<la<-18 else 55000 if -18<lo<60 and 17<la<32 else 45000 if -78<lo<-47 and -15<la<5 else 0
 if not area_target:continue
 view=tokens[bb];vals=sorted(np.unique(view[mask]));areas={}
 weights=np.cos((np.arange(bb[0].start,bb[0].stop)+.5)/H*np.pi-np.pi/2)*(40075.017/W)**2
 eligible=set()
 for p in vals:
  local=mask&(view==p);areas[int(p)]=float(np.sum(np.nonzero(local)[0].astype(float)*0+weights[np.nonzero(local)[0]]))
  density=old_density[p] if p<65536 else ref_density[p-65536]
  city=has_city[p] if p<65536 else ref_city[p-65536]
  if density<1 and not city:eligible.add(int(p))
 if len(eligible)<2:continue
 edges=Counter()
 for a,b in [(view[:,:-1],view[:,1:]),(view[:-1],view[1:])]:
  m=(a!=b)&np.isin(a,list(eligible))&np.isin(b,list(eligible));pairs=np.sort(np.column_stack([a[m],b[m]]),axis=1)
  for pair,n in zip(*np.unique(pairs,axis=0,return_counts=True)):edges[tuple(map(int,pair))]+=int(n)
 parent={p:p for p in eligible};size=areas.copy()
 def root(p):
  while parent[p]!=p:parent[p]=parent[parent[p]];p=parent[p]
  return p
 merged=0
 for (a,b),n in sorted(edges.items(),key=lambda q:-q[1]):
  a,b=root(a),root(b)
  if a==b or size[a]+size[b]>area_target*1.5:continue
  if size[a]>=area_target and size[b]>=area_target*.35:continue
  parent[b]=a;size[a]+=size[b];merged+=1
 for p in eligible:
  if root(p)!=p:view[mask&(view==p)]=root(p)
 if merged:report['sparse_merges'].append({'state':rid,'name':r['name'],'merged_cells':merged,'target_area_km2':area_target})

# Split disconnected province fragments on the SAME connected land mass.
# Offshore island groups are intentionally retained as archipelago provinces.
provinces={};atlas=np.zeros_like(regions);nextid=1
area_weights=np.cos((np.arange(H)+.5)/H*np.pi-np.pi/2)*(40075.017/W)**2
for key,r in world['regions'].items():
 rid=int(key);bb=boxes[rid-1];mask=regions[bb]==rid;view=tokens[bb];out=atlas[bb];r['provinces']=[]
 land_components,_=label(mask);component_sizes=np.bincount(land_components.ravel())
 for token in sorted(np.unique(view[mask])):
  local=mask&(view==token);parts,n=label(local);sizes=np.bincount(parts.ravel());pieces=[local]
  if n>1:
   main=1+int(np.argmax(sizes[1:]));main_land=int(np.bincount(land_components[parts==main]).argmax())
   extra=[j for j in range(1,n+1) if j!=main and sizes[j]>=max(8,sizes[main]*.03) and np.any((parts==j)&(land_components==main_land))]
   if extra:pieces=[local&~np.isin(parts,extra)]+[parts==j for j in extra];report['fragment_repairs']+=len(extra)
  for piece in pieces:
   y,x=np.nonzero(piece);pid=nextid;nextid+=1;out[y,x]=pid;r['provinces'].append(pid)
   centre=np.array([y.mean(),x.mean()]);j=np.argmin((y-centre[0])**2+(x-centre[1])**2)
   source=int(token-65536) if token>=65536 else oldps[str(int(token))].get('source_md_province',0)
   provinces[str(pid)]={'id':pid,'region':rid,'local_index':len(r['provinces']),'source_md_province':source,'map_center':[(float(x[j]+bb[1].start)+.5)/W,(float(y[j]+bb[0].start)+.5)/H],'area_km2':round(float(area_weights[y+bb[0].start].sum()),2),'neighbors':[],'buildings':{},'kind':'rural','cities':[]}
 # Valid State focus point; preserve an existing one when it is still inside.
 u,v=r['map_center']
 if regions[min(H-1,int(v*H)),int(u*W)%W]!=rid:r['map_center']=provinces[str(max(r['provinces'],key=lambda p:provinces[str(p)]['area_km2']))]['map_center']
 if rid%200==0:print('REBUILD_PROVINCES',rid,len(provinces),flush=True)
assert nextid<65535
micro=json.load(open(ROOT/'data/microstate_geometry.json'));micro['province']=world['regions'][str(micro['state'])]['provinces'][0]
u,v=micro['center_uv'];cy,cx=int(v*H),int(u*W);near=atlas[cy-6:cy+7,cx-6:cx+7];allowed=[p for p in near.ravel() if p and provinces[str(p)]['region']==micro['host_state']]
micro['host_province']=int(np.bincount(allowed).argmax());provinces[str(micro['province'])].update(area_km2=.44,map_center=[u,v]);write('microstate_geometry',micro)
edges=set()
for top in range(0,H,128):
 a=atlas[top:top+128];b=np.roll(a,-1,axis=1)
 for l,r in [(a,b),(atlas[top:min(H-1,top+128)],atlas[top+1:min(H,top+129)])]:
  m=(l>0)&(r>0)&(l!=r);codes=np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m]);edges.update(map(int,np.unique(codes)))
for code in edges:
 a,b=code//65536,code%65536;provinces[str(a)]['neighbors'].append(b);provinces[str(b)]['neighbors'].append(a)
for p in provinces.values():p['neighbors'].sort()
for c in cities:
 x=int((c['longitude']+180)/360*W)%W;y=min(H-1,max(0,int((90-c['latitude'])/180*H)));pid=int(atlas[y,x])
 if not pid:
  top=max(0,y-7);left=max(0,x-7);local=atlas[top:y+8,left:x+8];yy,xx=np.nonzero(local)
  candidates=[j for j in range(len(xx)) if world['regions'][str(provinces[str(int(local[yy[j],xx[j]]))]['region'])]['owner']==c['country']]
  if candidates:j=min(candidates,key=lambda j:(xx[j]+left-x)**2+(yy[j]+top-y)**2);pid=int(local[yy[j],xx[j]])
 if pid:
  provinces[str(pid)]['cities'].append(c['name']);c['country']=world['regions'][str(provinces[str(pid)]['region'])]['owner']
for tag,c in world['countries'].items():
 c['regions']=sorted(r['id'] for r in world['regions'].values() if r['owner']==tag)
 if c['capital'] in quebec:c['capital']=750
 u,v=c['map_center'];rid=int(regions[min(H-1,int(v*H)),int(u*W)%W])
 if rid not in c['regions']:c['map_center']=world['regions'][str(c['capital'])]['map_center']
world['scenario_id']='bunny_world_2000_0_2_0_3';world['schema_version']=9
world['map']['province_geometry']='Targeted settlement-registered MD shapes; populated corridors retain detail, adjacent almost-empty interior cells consolidated; no rectangular State stretching.'
for i in range(4):
 a=atlas[i//2*(H//2):(i//2+1)*(H//2),i%2*(W//2):(i%2+1)*(W//2)];png(np.stack([(a&255).astype(np.uint8),(a>>8).astype(np.uint8),np.zeros_like(a,np.uint8)],-1),ROOT/'assets'/f'region_ids_{i}.png')
index=np.zeros((65536,3),np.uint8)
for p in provinces.values():index[p['id'],:2]=[p['region']&255,p['region']>>8]
index[65535,:2]=[255,31];png(index.reshape(256,256,3),ROOT/'assets/province_index.png')
npz(SRC/'province_atlas_0203.npz',provinces=atlas);npz(SRC/'province_atlas_022r2.npz',provinces=atlas);npz(SRC/'grouped_atlas_022r2.npz',regions=regions)
report.update(provinces=len(provinces),states=len(world['regions']),countries=len(world['countries']),quebec_merged_states=quebec,registration='1171 real settlement/reference anchors; shared smooth coordinate mapping')
for name,obj in [('world',world),('provinces',provinces),('cities',cities),('geography_0203_report',report)]:write(name,obj)
print('GEOGRAPHY_0203_COMPLETE',len(provinces),len(world['regions']),'sparse merges',sum(q['merged_cells'] for q in report['sparse_merges']),'fragment splits',report['fragment_repairs'],flush=True)
