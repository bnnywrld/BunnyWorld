"""Build real Earth coastlines with approximate, calibrated MD regional boundaries.
Offline, deterministic inputs are included in tools/cartography. Requires
Python, NumPy, SciPy and Pillow. Does not claim survey-accurate region borders.
"""
import json, unicodedata
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import map_coordinates, distance_transform_edt, label
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'tools/cartography'
W,H=4096,2048
w=json.loads((ROOT/'data/world.json').read_text())
centers=json.loads((INPUT/'md_centers.json').read_text())
features=json.loads((INPUT/'natural_earth_map_units.geojson').read_text())['features']
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if c.isalnum() and not unicodedata.combining(c))
names={norm(c['name']):t for t,c in w['countries'].items()}
alias={'Czechia':'CZE','Bosnia and Herzegovina':'BOS','North Macedonia':'FYR','Macedonia':'FYR','Republic of Serbia':'SER','Democratic Republic of the Congo':'DRC','Dem. Rep. Congo':'DRC','Republic of the Congo':'CNG','Congo':'CNG','eSwatini':'SWA','Eswatini':'SWA','Swaziland':'SWA','Ivory Coast':'CDI','North Korea':'NKO','South Korea':'KOR','Taiwan':'TAI','Iran':'PER','Tanzania':'TNZ','Cape Verde':'VER','Lebanon':'LEB','United States of America':'USA','Antigua and Barb.':'ANT','Trinidad and Tobago':'TRI','N. Cyprus':'NCY','Northern Cyprus':'NCY','Palestine':'PAL','Vatican':'HLS','Sao Tome and Principe':'SAO','St. Kitts and Nevis':'STK','Saint Kitts and Nevis':'STK','St. Lucia':'STL','St. Vin. and Gren.':'STV','Saint Vincent and the Grenadines':'STV','Kyrgyz Republic':'KYR','Western Sahara':'SHA','S. Sudan':'SSU','Guinea Bissau':'GUB','Eq. Guinea':'EGU','Solomon Is.':'SOL','Falkland Islands':'ENG','East Timor':'IND','Timor-Leste':'IND'}
names.update({norm(n):t for n,t in alias.items()})
def tag_for(p):
 for key in ['GEOUNIT','NAME_EN','ADMIN','NAME','SOVEREIGNT']:
  if norm(p.get(key) or '') in names:return names[norm(p[key])]
 return None
iso={}
for f in features:
 t=tag_for(f['properties'])
 if t:
  for k in ['ADM0_A3','GU_A3','ISO_A3']:iso[f['properties'][k]]=t
# Capital-region centroids are calibration landmarks, not city coordinates.
geo=[];source=[];anchor_tags=[]
for cap in json.loads((INPUT/'capitals.json').read_text()):
 t=names.get(norm(cap['country'])) or iso.get(cap['iso'])
 if not t or t in anchor_tags:continue
 u,v=centers['countries'][t];lon,lat=cap['lon'],cap['lat']
 gu=(lon+180)/360;gv=(90-lat)/180
 if abs(gu-u)>.16:continue # overseas/alternate capital or dateline centroid
 geo.append([gu,gv]);source.append([u,v]);anchor_tags.append(t)
# Geographic poles and dateline control the global extrapolation.
for gu in [0,.25,.5,.75,1]:
 for gv,sv in [(0,-.22),(1,1.48)]:geo.append([gu,gv]);source.append([gu,sv])
for gv in [.15,.3,.5,.7,.85]:
 for gu in [0,1]:geo.append([gu,gv]);source.append([gu,gv*1.35-.18])
geo=np.array(geo);source=np.array(source)
transform=RBFInterpolator(geo,source,kernel='thin_plate_spline',smoothing=.00002)
inverse=RBFInterpolator(source,geo,kernel='thin_plate_spline',smoothing=.00002)
# Compute the nonlinear warp on a coarse grid, then smoothly sample it.
gy,gx=np.mgrid[0:1:257j,0:1:513j]
grid=transform(np.column_stack([gx.ravel(),gy.ravel()])).reshape(257,513,2)
raw=np.asarray(Image.open(INPUT/'md_region_ids.png')).astype(np.uint16)
raw_ids=raw[:,:,0]+raw[:,:,1]*256
result=np.zeros((H,W),np.uint16)
for start in range(0,H,128):
 end=min(H,start+128);yy,xx=np.mgrid[start:end,0:W]
 sy=map_coordinates(grid[:,:,1],[(yy+.5)/H*256,(xx+.5)/W*512],order=1)
 sx=map_coordinates(grid[:,:,0],[(yy+.5)/H*256,(xx+.5)/W*512],order=1)
 result[start:end]=map_coordinates(raw_ids,[sy*raw_ids.shape[0],sx*raw_ids.shape[1]],order=0,mode='constant',cval=0)
print('Warp calibrated with',len(anchor_tags),'capital regions',flush=True)
# Geographic coastlines and international border masks, retaining scenario factions.
canvas=Image.new('I',(W,H),0);draw=ImageDraw.Draw(canvas)
mask_tags={};unmapped=[]
for i,f in enumerate(features,1):
 p=f['properties'];t=tag_for(p);mask_tags[i]=t
 if not t and p['NAME']!='Antarctica':unmapped.append(p['NAME'])
 polys=f['geometry']['coordinates'] if f['geometry']['type']=='MultiPolygon' else [f['geometry']['coordinates']]
 for poly in polys:
  points=[((lon+180)/360*W,(90-lat)/180*H) for lon,lat,*rest in poly[0]]
  draw.polygon(points,fill=i)
  for hole in poly[1:]:draw.polygon([((lon+180)/360*W,(90-lat)/180*H) for lon,lat,*rest in hole],fill=0)
mask=np.array(canvas)
# Source rebels and breakaway administrations remain eligible inside parent borders.
groups={'AFG':['TAL'],'IND':['ACE'],'BRM':['KAC','KAR','WAA','SHN'],'IRQ':['KUR','PUK','IEK'],'SRI':['TML'],'NEP':['NPM'],'SOV':['CHE'],'GEO':['ABK','SOO'],'AZE':['NKR'],'MLV':['PMR'],'SOM':['SML','PUN','SNA','JUB','AIA','SWS'],'DRC':['MLC','RCD'],'AGL':['UNI'],'SIE':['AFR'],'LIB':['LUR'],'LEB':['HEZ'],'PAL':['HAM'],'ISR':['PAL','HAM']}
owner=np.zeros(4096,np.uint16)
for sid,r in w['regions'].items():owner[int(sid)]=w['countries'].get(r['owner'],{}).get('index',0)
all_y,all_x=np.nonzero(result)
all_tree=cKDTree(np.column_stack([all_y,all_x]))
for i,f in enumerate(features,1):
 yy,xx=np.nonzero(mask==i)
 if not len(yy):continue
 if f['properties']['NAME']=='Antarctica':result[yy,xx]=4095;continue
 t=mask_tags[i]
 if not t:
  missing=result[yy,xx]==0
  if missing.any():
   _,ix=all_tree.query(np.column_stack([yy[missing],xx[missing]]))
   result[yy[missing],xx[missing]]=result[all_y[ix],all_x[ix]]
  continue
 allowed_tags=[t]+groups.get(t,[])
 allowed=[w['countries'][tag]['index'] for tag in allowed_tags if tag in w['countries']]
 valid=np.isin(owner[result],allowed)
 bad=~valid[yy,xx]
 if bad.any():
  sy,sx=np.nonzero(valid)
  if len(sy):
   tree=cKDTree(np.column_stack([sy,sx]));_,ix=tree.query(np.column_stack([yy[bad],xx[bad]]))
   result[yy[bad],xx[bad]]=result[sy[ix],sx[ix]]
  else:result[yy[bad],xx[bad]]=w['countries'][t]['capital']
result[mask==0]=0
# Preserve islands too small for rasterization and every imported region.
# Missing tiny regions receive a small footprint near their calibrated location;
# regional boundaries remain an approximation, never fabricated new populations.
missing=sorted(set(map(int,w['regions']))-set(np.unique(result)))
restored=[]
for sid in missing:
 r=w['regions'][str(sid)];uv=inverse(np.array([centers['regions'][str(sid)]]))[0]
 x=int(np.clip(uv[0]*W,0,W-1));y=int(np.clip(uv[1]*H,0,H-1))
 cid=w['countries'].get(r['owner'],{}).get('index',0)
 yy,xx=np.nonzero(owner[result]==cid) if cid else (np.array([]),np.array([]))
 if len(yy):
  j=np.argmin((yy-y)**2+(xx-x)**2);x,y=int(xx[j]),int(yy[j])
 # Choose only pixels of a region with enough area left; no cascade losses.
 y0,y1=max(0,y-2),min(H,y+3);x0,x1=max(0,x-2),min(W,x+3)
 patch=result[y0:y1,x0:x1]
 for other in np.unique(patch):
  if other in [0,4095]:continue
  if np.count_nonzero(result==other)<=np.count_nonzero(patch==other):
   patch=patch.copy();patch[patch==other]=sid # already tiny: skip overwriting all
   # Fall back to nearby ocean for the small-island footprint.
   y0,y1=max(0,y-5),max(0,y-5)+2;x0,x1=max(0,x-5),max(0,x-5)+2
   break
 result[y0:y1,x0:x1]=sid;restored.append(sid)
assert set(map(int,w['regions'])) <= set(np.unique(result)), 'Region lost in coast correction'
# Pick actual in-region pixels for camera focus, so sea centroids cannot break picking.
for sid,r in w['regions'].items():
 yy,xx=np.nonzero(result==int(sid))
 j=np.argmin((yy-yy.mean())**2+(xx-xx.mean())**2)
 r['map_center']=[(float(xx[j])+.5)/W,(float(yy[j])+.5)/H]
for tag,c in w['countries'].items():
 sid=str(c['capital'])
 if sid not in w['regions'] or w['regions'][sid]['owner']!=tag:sid=str(max(c['regions'],key=lambda sid:w['regions'][str(sid)]['population']))
 c['map_center']=w['regions'][sid]['map_center']
rgb=np.zeros((H,W,3),np.uint8);rgb[:,:,0]=result&255;rgb[:,:,1]=result>>8
Image.fromarray(rgb).save(ROOT/'assets/region_ids.png',optimize=True)
w['map']={'width':W,'height':H,'palette_width':4096,'cartography':'Geographic equirectangular Earth coastlines, including Antarctica; calibrated approximate MD regional boundaries','antarctica_region_id':4095,'geographic_source':'Natural Earth 1:10m admin-0 map units (public domain)','regional_boundary_accuracy':'Approximate: capital-calibrated MD warp with geographic country masks; tiny regions restored as small footprints'}
(ROOT/'data/world.json').write_text(json.dumps(w,ensure_ascii=False,separators=(',',':')))
report={'projection':'equirectangular (longitude/latitude)','resolution':[W,H],'anchors':len(anchor_tags),'preserved_regions':len(w['regions']),'restored_small_regions':restored,'geographic_units_without_direct_tag':unmapped,'antarctica_pixels':int(np.count_nonzero(result==4095)),'limits':w['map']['regional_boundary_accuracy']}
(ROOT/'data/cartography_report.json').write_text(json.dumps(report,indent=2))
# Internal review image, not part of the game.
palette=np.zeros((4096,3),np.uint8);palette[0]=[22,57,77];palette[4095]=[213,229,235]
for sid,r in w['regions'].items():palette[int(sid)]=w['countries'].get(r['owner'],{}).get('color',[120,145,165])
Image.fromarray(palette[result]).resize((2048,1024)).save('/tmp/bunny_geography.png')
print(json.dumps(report,indent=2),flush=True)
