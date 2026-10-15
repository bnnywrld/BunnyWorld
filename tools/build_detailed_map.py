"""Geographic regional rebuild: real subdivision polygons, matching MD region IDs.
Builds a 16,384 x 8,192 atlas as four 8,192 x 4,096 lossless tiles. Custom
MD regions without an equivalent geographic division use clipped local splits.
Requires NumPy, SciPy and Pillow. Inputs are bundled for offline reproduction.
"""
import ast,json,unicodedata
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import find_objects
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1];INPUT=ROOT/'tools/cartography'
W,H=16384,8192;CW,CH=4096,2048
world=json.loads((ROOT/'data/world.json').read_text());regions=world['regions'];countries=world['countries']
# Correct the imported lease/base ownership for the requested 2000 scenario.
regions['1112']['owner']='UKR'
for t,c in countries.items():
 c['regions']=[int(s) for s,r in regions.items() if r['owner']==t]
 c['population']=sum(regions[str(s)]['population'] for s in c['regions'])
world['scenario_id']='bunny_world_2000_0_1_2'
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKD',str(s or '').lower()) if c.isalnum() and not unicodedata.combining(c))
legacy=ast.parse((ROOT/'tools/build_geographic_map.py').read_text())
alias=next(ast.literal_eval(n.value) for n in legacy.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='alias' for t in n.targets))
names={norm(c['name']):t for t,c in countries.items()};names.update({norm(n):t for n,t in alias.items()})
units=json.loads((INPUT/'natural_earth_map_units.geojson').read_text())['features']
subdivisions=json.loads((INPUT/'geographic_subdivisions.geojson').read_text())['features']
def unit_tag(p):
 for key in ['GEOUNIT','NAME_EN','ADMIN','NAME','SOVEREIGNT']:
  if norm(p.get(key)) in names:return names[norm(p[key])]
 return None
iso={}
for f in units:
 t=unit_tag(f['properties'])
 if t:
  for key in ['ADM0_A3','GU_A3','ISO_A3']:iso[f['properties'][key]]=t
groups={'AFG':['TAL'],'IND':['ACE'],'BRM':['KAC','KAR','WAA','SHN'],'IRQ':['KUR','PUK','IEK'],'SRI':['TML'],'NEP':['NPM'],'SOV':['CHE'],'GEO':['ABK','SOO'],'AZE':['NKR'],'MLV':['PMR'],'SOM':['SML','PUN','SNA','JUB','AIA','SWS'],'DRC':['MLC','RCD'],'AGL':['UNI'],'SIE':['AFR'],'LIB':['LUR'],'LEB':['HEZ'],'PAL':['HAM'],'ISR':['PAL','HAM']}
region_alias={'swietokrzyskie':'kielce','malopolskie':'malopolska','wielkopolskie':'wielkopolska','mazowieckie':'mazowsze','pomorskie':'pomorze','zachodniopomorskie':'zachodniepomorze','dolnoslaskie':'dolnyslask','slaskie':'gornyslask','warminskomazurskie':'warmiaimazury','lodzkie':'lodz','lubelskie':'lubelszczyzna','podlaskie':'podlasie','lubuskie':'lubuskie','districtofcolumbia':'washingtondc','northrhinewestphalia':'nordrheinwestfalen','bavaria':'bayern','lowersaxony':'niedersachsen','thuringia':'thuringen','saxony':'sachsen','saxonyanhalt':'sachsenanhalt','sevastopol':'sevastopolbay','autonomousrepublicofcrimea':'crimea','kyivcity':'kyiv','kiev':'kyiv','dnipropetrovskoblast':'dnipropetrovsk','odessa':'odesa'}
def region_norm(s):
 n=norm(s)
 return region_alias.get(n,n)
def paint(draw,geometry,value,width,height,offset=(0,0)):
 polys=geometry['coordinates'] if geometry['type']=='MultiPolygon' else [geometry['coordinates']]
 for poly in polys:
  points=[((lon+180)/360*width-offset[0],(90-lat)/180*height-offset[1]) for lon,lat,*rest in poly[0]]
  draw.polygon(points,fill=int(value))
  for hole in poly[1:]:draw.polygon([((lon+180)/360*width-offset[0],(90-lat)/180*height-offset[1]) for lon,lat,*rest in hole],fill=0)
# Coarse reference is only for matching IDs to geographic divisions, never outlines.
reference=np.asarray(Image.open(INPUT/'reference_011.png')).astype(np.uint16)
reference=reference[:,:,0]+reference[:,:,1]*256
canvas=Image.new('I',(CW,CH),0);draw=ImageDraw.Draw(canvas)
for i,f in enumerate(subdivisions,1):paint(draw,f['geometry'],i,CW,CH)
admin=np.asarray(canvas,dtype=np.uint16);del draw,canvas
boxes=find_objects(admin);assignments={};direct=[];matching=[]
for i,f in enumerate(subdivisions,1):
 p=f['properties'];tag=names.get(norm(p.get('admin'))) or iso.get(p.get('adm0_a3'))
 if p['adm1_code'] in ['RUS-283','RUS-5482']:tag='UKR'
 if not tag:continue
 tags=[tag]+groups.get(tag,[])
 candidates=[int(s) for s,r in regions.items() if r['owner'] in tags and int(s) not in [424,488,624,824,827]]
 if not candidates:continue
 pn={region_norm(p.get(k)) for k in ['name','name_en','name_alt','name_de','name_pl','name_ru','name_uk','name_fr','name_es','region'] if p.get(k)}
 for key in ['name_alt']:
  if p.get(key):pn.update(region_norm(n) for n in p[key].split('|'))
 exact=[s for s in candidates if region_norm(regions[str(s)]['name']) in pn]
 if p['adm1_code']=='RUS-283':exact=[669]
 if p['adm1_code']=='RUS-5482':exact=[1112]
 if exact:
  sid=exact[0];direct.append(i)
 else:
  box=boxes[i-1]
  values,counts=np.unique(reference[box][admin[box]==i],return_counts=True) if box else ([],[])
  overlap=[(int(count),int(value)) for value,count in zip(values,counts) if int(value) in candidates]
  if overlap:sid=max(overlap)[1]
  else:
   uv=np.array([(float(p.get('longitude') or 0)+180)/360,(90-float(p.get('latitude') or 0))/180])
   sid=min(candidates,key=lambda s:np.sum((np.array(regions[str(s)]['map_center'])-uv)**2))
  matching.append(i)
 assignments[i]=sid
print('Matched geographic subdivisions:',len(assignments),'by name:',len(direct),flush=True)
# Begin with geographic country contours; subdivision polygons refine every region.
canvas=Image.new('I',(W,H),0);draw=ImageDraw.Draw(canvas)
for f in units:
 p=f['properties'];tag=unit_tag(p)
 if p['NAME']=='Antarctica':sid=4095
 elif tag and countries[tag]['regions']:
  sid=int(countries[tag]['capital'])
  if str(sid) not in regions or regions[str(sid)]['owner']!=tag:sid=max(countries[tag]['regions'],key=lambda s:regions[str(s)]['population'])
 else:
  x=int(np.clip((p.get('LABEL_X',0)+180)/360*CW,0,CW-1));y=int(np.clip((90-p.get('LABEL_Y',0))/180*CH,0,CH-1));sid=int(reference[y,x])
  if not sid:continue
 paint(draw,f['geometry'],sid,W,H)
for i,f in enumerate(subdivisions,1):
 if i in assignments:paint(draw,f['geometry'],assignments[i],W,H)
result=np.asarray(canvas,dtype=np.uint16);del draw,canvas
print('Geographic polygons rasterized at',W,H,flush=True)
# Missing custom regions are partitioned inside a geographic parent division.
# A split is needed where MD has more pieces than admin-1, e.g. Franken/Bayern.
present=set(np.unique(result));missing=sorted(set(map(int,regions))-present)
local_splits={};tiny=[]
raw=np.asarray(Image.open(INPUT/'md_region_ids.png')).astype(np.uint16)
source_sizes=np.bincount((raw[:,:,0]+raw[:,:,1]*256).ravel(),minlength=4096)
del raw
parent_for={child:parent for parent,children in groups.items() for child in children}
foreign={'424':(-75.15,19.9),'488':(48.1,29.3),'624':(50.61,26.22),'824':(72.42,-7.31),'827':(127.77,26.36)}
# Known small island/base coordinates fix old nearest-country relocations.
places={'19':(-5.35,36.14),'424':(-75.15,19.9),'488':(48.1,29.3),'624':(50.61,26.22),'764':(-69,45),'765':(-71.6,43.8),'767':(-71.5,42.2),'768':(-72.7,41.6),'812':(32.98,34.59),'816':(113.8,7.4),'824':(72.42,-7.31),'827':(127.77,26.36),'1084':(-71.5,41.7),'1015':(116.72,20.7),'1109':(119.95,26.16),'1117':(166.93,-.52)}
for sid in missing:
 r=regions[str(sid)];u,v=r['map_center'];x=int(u*CW);y=int(v*CH)
 nearby=[]
 for i,s in assignments.items():
  if regions[str(s)]['owner'] not in [r['owner'],parent_for.get(r['owner'])]:continue
  p=subdivisions[i-1]['properties'];pu=(float(p.get('longitude') or 0)+180)/360;pv=(90-float(p.get('latitude') or 0))/180
  nearby.append(((pu-u)**2+(pv-v)**2,i))
 # Base/island micro-regions keep an explicit small geographic footprint.
 if sid in [424,488,624,824,827] or 'base' in r['name'].lower() or source_sizes[sid] < 10 or not nearby:
  tiny.append(sid);continue
 i=min(nearby)[1];local_splits.setdefault(i,[]).append(sid)
split_records=[]
for i,extra in local_splits.items():
 box=boxes[i-1]
 if not box:
  tiny.extend(extra);continue
 top,bottom=box[0].start*4,min(H,box[0].stop*4);left,right=box[1].start*4,min(W,box[1].stop*4)
 local_canvas=Image.new('1',(right-left,bottom-top),0)
 paint(ImageDraw.Draw(local_canvas),subdivisions[i-1]['geometry'],1,W,H,(left,top));inside=np.asarray(local_canvas)
 yy,xx=np.nonzero(inside);yy=yy+top;xx=xx+left
 if len(yy)<len(extra)*4:tiny.extend(extra);continue
 existing=assignments[i];ids=[existing]+extra
 seeds=[]
 for sid in ids:
  u,v=regions[str(sid)]['map_center'];px=u*W;py=v*H
  j=int(np.argmin((xx-px)**2+(yy-py)**2));seeds.append([float(xx[j]),float(yy[j])])
 # Separate coincident seeds inside the polygon to keep each region meaningful.
 for k in range(1,len(seeds)):
  if any(np.linalg.norm(np.array(seeds[k])-p)<2 for p in seeds[:k]):
   j=min(len(xx)-1,k*len(xx)//len(seeds));seeds[k]=[float(xx[j]),float(yy[j])]
 coords=np.column_stack([xx,yy]);scale=np.array([max(.2,np.cos(np.deg2rad(float(subdivisions[i-1]['properties'].get('latitude') or 0)))),1])
 _,which=cKDTree(np.array(seeds)*scale).query(coords*scale)
 result[yy,xx]=np.array(ids,np.uint16)[which]
 split_records.append({'division':subdivisions[i-1]['properties']['name'],'region_ids':ids})
# Restore the small footprints at actual geographic locations, only a few pixels.
counts=np.bincount(result.ravel(),minlength=4096)
for sid in tiny:
 r=regions[str(sid)];u,v=r['map_center']
 if str(sid) in places:
  lon,lat=places[str(sid)];u,v=(lon+180)/360,(90-lat)/180
 x=int(np.clip(u*W,3,W-4));y=int(np.clip(v*H,3,H-4))
 # Use a small inland footprint where possible; overseas bases deliberately retain
 # their scenario owner within the host territory, never spread over the province.
 patch=result[y-2:y+3,x-2:x+3]
 if any(counts[z]<=np.count_nonzero(patch==z) for z in np.unique(patch) if z not in [0,4095]):
  x=min(W-4,x+8);patch=result[y-2:y+3,x-2:x+3]
 patch[:]=sid
# Rare custom pieces can lose an overlap during a split: give them a local patch.
missing_final=sorted(set(map(int,regions))-set(np.unique(result)))
for sid in missing_final:
 u,v=regions[str(sid)]['map_center'];x=int(np.clip(u*W,3,W-4));y=int(np.clip(v*H,3,H-4));result[y-1:y+2,x-1:x+2]=sid
assert set(map(int,regions))<=set(np.unique(result))
# Update focus points from actual region pixels using bounded-label boxes.
focus_boxes=find_objects(result,max_label=1250)
for sid,r in regions.items():
 box=focus_boxes[int(sid)-1];yy,xx=np.nonzero(result[box]==int(sid));yy+=box[0].start;xx+=box[1].start
 # Large overseas pieces: choose the largest connected component's approximate
 # centroid using the densest longitude cluster, avoiding dateline/ocean centroids.
 if xx.max()-xx.min()>W//2:
  use=xx<W//2 if np.count_nonzero(xx<W//2)>len(xx)//2 else xx>=W//2;yy=yy[use];xx=xx[use]
 j=int(np.argmin((yy-yy.mean())**2+(xx-xx.mean())**2));r['map_center']=[(float(xx[j])+.5)/W,(float(yy[j])+.5)/H]
for t,c in countries.items():
 sid=str(c['capital'])
 if sid not in regions or regions[sid]['owner']!=t:sid=str(max(c['regions'],key=lambda s:regions[str(s)]['population']))
 c['map_center']=regions[sid]['map_center']
for ty in range(2):
 for tx in range(2):
  ids=result[ty*H//2:(ty+1)*H//2,tx*W//2:(tx+1)*W//2];rgb=np.zeros((*ids.shape,3),np.uint8);rgb[:,:,0]=ids&255;rgb[:,:,1]=ids>>8
  Image.fromarray(rgb).save(ROOT/f'assets/region_ids_{ty*2+tx}.png',optimize=True)
# Keep a compact matching reference for future rebuilds, not used by the renderer.
world['map']={'width':W,'height':H,'tile_width':W//2,'tile_height':H//2,'tiles':4,'palette_width':4096,'antarctica_region_id':4095,'cartography':'Geographic subdivision polygons fitted to real Earth coastlines','regional_boundary_accuracy':'Natural Earth admin-1 divisions merged to MD region IDs; custom regions use local clipped splits and tiny bases/islands use small footprints'}
(ROOT/'data/world.json').write_text(json.dumps(world,ensure_ascii=False,separators=(',',':')))
report={'resolution':[W,H],'geographic_divisions':len(assignments),'name_matches':len(direct),'custom_local_splits':split_records,'tiny_footprints':tiny,'additional_footprints':missing_final,'Crimea_region':669,'Sevastopol_region':1112,'Crimea_owner':'UKR','population':sum(r['population'] for r in regions.values()),'limits':world['map']['regional_boundary_accuracy']}
(ROOT/'data/cartography_report.json').write_text(json.dumps(report,indent=2))
# Internal visual overview with regional boundaries.
preview=result[::4,::4];palette=np.zeros((4096,3),np.uint8);palette[0]=[22,57,77];palette[4095]=[213,229,235]
for sid,r in regions.items():palette[int(sid)]=countries.get(r['owner'],{}).get('color',[120,145,165])
rgb=palette[preview];edges=(preview!=np.roll(preview,1,axis=0))|(preview!=np.roll(preview,1,axis=1));rgb[edges]=(rgb[edges]*.45).astype(np.uint8)
Image.fromarray(rgb).save('/tmp/bunny_regions_012.png')
print('MAP_BUILD_COMPLETE',W,H,'custom splits',len(split_records),'tiny footprints',len(tiny),flush=True)
