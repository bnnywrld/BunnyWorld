"""Worldwide State audit; flags are evidence for review, not automatic edits."""
from pathlib import Path
from collections import Counter,defaultdict
import json,re,unicodedata,zlib
import numpy as np
from scipy.ndimage import find_objects,label,binary_dilation,map_coordinates
from rasterio.features import rasterize
from rasterio.transform import Affine
R=Path(__file__).resolve().parents[1];OUT=R/'validation_0215';OUT.mkdir(exist_ok=True)
def read(n):return json.loads((R/n).read_text())
def norm(s):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
w=read('data/world.json');ps=read('data/provinces.json');cities=read('data/cities.json');report=read('data/geography_0215_report.json');a=np.load(R/'tools/cartography/province_atlas_0215.npz')['provinces'];H,W=a.shape
lut=np.zeros(65536,np.uint16)
for p in ps.values():lut[p['id']]=p['region']
small=lut[a[2::4,2::4]];hh,ww=small.shape;boxes=find_objects(small,max_label=8191)
features=read('tools/cartography/geographic_subdivisions.geojson')['features'];bycode={f['properties'].get('adm1_code'):f for f in features}
index=read('assets/display/selection_distance.json');assert index['version']=='0.2.0.15';blob=(R/'assets/display/selection_distance.bwd').read_bytes()
before_index=json.loads((R.parent/'baseline_0214/assets/display/selection_distance.json').read_text());before_blob=(R.parent/'baseline_0214/assets/display/selection_distance.bwd').read_bytes()
rows=[];name_flags=[];spatial_flags=[];shape_flags=[];city_flags=[];cities_by_name=defaultdict(list)
for c in cities:
 if c.get('population_rank',0)<30000:continue
 pid=c.get('province_id',0)
 if str(pid)in ps:cities_by_name[(c['country'],norm(c['name']))].append(ps[str(pid)]['region'])
def recall(key,r,pack,yy,xx):
 d=np.frombuffer(zlib.decompress(pack[r[4]:r[4]+r[5]]),np.uint8).reshape(r[7],r[6]);v=map_coordinates(d,[(((yy+.5)/H-r[1])/r[3])*r[7]-.5,((((xx+.5)/W-r[0])%1)/r[2])*r[6]-.5],order=1,mode='constant',cval=0);return float(np.mean(v>=127.5))
for key,s in w['regions'].items():
 bb=boxes[int(key)-1]
 if bb is None:continue # Tiny islands may be below this audit sample scale.
 m=small[bb]==int(key);yy,xx=np.nonzero(m);yy=(yy+bb[0].start)*4+2;xx=(xx+bb[1].start)*4+2
 current=recall(key,index['states'][key],blob,yy,xx);previous=recall(key,before_index['states'][key],before_blob,yy,xx)if key in before_index['states']else None
 row={'id':int(key),'country':s['owner'],'name':s['name'],'provinces':len(s['provinces']),'geographic_divisions':s.get('geographic_divisions',[]),'selection_recall_before':previous,'selection_recall_after':current,'sampled_pixels':len(xx)}
 source=[bycode[c]['geometry']for c in s.get('geographic_codes',[])if c in bycode]
 if source:
  transform=Affine(360/ww,0,bb[1].start/ww*360-180,0,-180/hh,90-bb[0].start/hh*180)
  reference=rasterize([(g,1)for g in source],out_shape=m.shape,transform=transform,dtype='uint8')>0
  # Natural Earth and the accepted high-detail coastline have different
  # generalization. Permit three sample cells only around source boundaries.
  relaxed=binary_dilation(reference,iterations=3);covered=float(relaxed[m].mean());row['explained_by_source_union']=covered
  if covered<.90 and len(xx)>=100:spatial_flags.append({'id':int(key),'name':s['name'],'country':s['owner'],'explained_fraction':covered,'status':'requires geographic review; no speculative boundary change'})
 else:row['source_status']='Authored territory / microstate / no directly matching ADM1 code'
 ds=s.get('geographic_divisions',[]);n=norm(s['name'])
 if ds and not any(n in norm(d)or norm(d)in n for d in ds if norm(d))and s['name']!=w['countries'][s['owner']]['name']:
  name_flags.append({'id':int(key),'name':s['name'],'country':s['owner'],'source_divisions':ds,'status':'name heuristic only; regional names can legitimately differ from ADM1 names'})
 matches=cities_by_name.get((s['owner'],n),[])
 if matches and int(key)not in matches:city_flags.append({'id':int(key),'name':s['name'],'city_states':matches,'status':'Krasnoyarsk Krai legitimately surrounds a separately represented city State'if int(key)==1084 else'requires review'})
 components,count=label(m,np.ones((3,3),bool));sizes=np.bincount(components.ravel());significant=sorted((int(v)for v in sizes[1:]if v>=max(20,m.sum()*.03)),reverse=True)
 if len(significant)>1:shape_flags.append({'id':int(key),'name':s['name'],'country':s['owner'],'significant_components':significant,'status':'review alongside source footprint; islands, enclaves and divided territories may explain this'})
 rows.append(row)
 if len(rows)%300==0:print('AUDIT',len(rows),flush=True)
# Province density is measured and recorded, not redrawn in this patch.
density=[]
for sid in [1435,1436,424]:
 s=w['regions'][str(sid)];density.append({'id':sid,'name':s['name'],'actual_provinces':len(s['provinces']),'population':s['population'],'area_km2':s['area_km2'],'deferred_to_province_patch':True})
result={'version':'0.2.0.15','scope':'Worldwide automated State audit with focused geographic review; not a certification that all source boundaries match year 2000.','states_total':len(w['regions']),'states_sampled':len(rows),'countries':len(w['countries']),'reference':'Natural Earth ADM1 geographic_subdivisions.geojson; accepted scenario country ownership retained','source_union_flags':spatial_flags,'name_heuristic_flags':name_flags,'city_name_flags':city_flags,'component_review_flags':shape_flags,'province_density_examples':density,'corrections':report,'states':rows}
(OUT/'state_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('AUDIT_READY',len(rows),'source flags',len(spatial_flags),'city flags',len(city_flags),'components',len(shape_flags),flush=True)
print(json.dumps(spatial_flags,ensure_ascii=False),flush=True)
