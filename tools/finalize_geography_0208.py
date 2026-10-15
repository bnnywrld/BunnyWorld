"""Refresh territory references and version metadata after the authored patch."""
from pathlib import Path
from collections import Counter
import json
import numpy as np
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from shapely.geometry import shape
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography'
w=json.load(open(ROOT/'data/world.json'));a=np.load(SRC/'grouped_atlas_022r2.npz')['regions'];H,W=a.shape
labels={}
for s in w['regions'].values():labels.setdefault((s['owner'],s['name']),[]).append(s)
for (tag,name),items in labels.items():
 if len(items)<2:continue
 # Some pre-existing three-way duplicates survive the first North/South or
 # Coastal Islands qualifier. Resolve the remaining pair by actual position.
 xs=[s['map_center'][0] for s in items];ys=[s['map_center'][1] for s in items]
 axis=0 if max(xs)-min(xs)>max(ys)-min(ys) else 1
 ordered=sorted(items,key=lambda s:s['map_center'][axis]);base=name.split(' — ')[0]
 for i,s in enumerate(ordered):
  if len(items)==2:direction=('Western' if i==0 else 'Eastern') if axis==0 else ('Northern' if i==0 else 'Southern')
  else:direction=('Western' if axis==0 else 'Northern') if i==0 else ('Eastern' if axis==0 else 'Southern') if i==len(items)-1 else 'Central'
  s['name']=base+' — '+direction+(' Islands' if 'Island' in name else ' Coast')
features=json.load(open(SRC/'disputed_areas.geojson'))['features'];catalog=[]
for f in json.load(open(SRC/'natural_earth_map_units.geojson'))['features']:
 if f['properties'].get('ADM0_A3')=='TLS':features.append({'geometry':f['geometry'],'properties':{'BRK_A3':'TLS','BRK_NAME':'Timor-Leste'}})
for f in json.load(open(SRC/'bosnia_entities_0208.geojson'))['features']:
 n=f['properties']['shapeName']
 if n in ['Republika Srpska','Brčko District']:features.append({'geometry':f['geometry'],'properties':{'BRK_A3':'BIH-SRP' if n=='Republika Srpska' else 'BIH-BRC','BRK_NAME':n}})
exceptions={'B75','B76','B51','B80','B14','B22','B59','B71','B24','B25','B26','B27','B23'}
for f in features:
 p=f['properties'];code=p['BRK_A3'];l,b,r,t=shape(f['geometry']).bounds
 x0=max(0,int((l+180)/360*W)-2);x1=min(W,int((r+180)/360*W)+3)
 y0=max(0,int((90-t)/180*H)-2);y1=min(H,int((90-b)/180*H)+3)
 mask=rasterize([(f['geometry'],1)],out_shape=(y1-y0,x1-x0),transform=from_bounds(x0/W*360-180,90-y1/H*180,x1/W*360-180,90-y0/H*180,x1-x0,y1-y0),dtype='uint8').astype(bool)
 ids,nn=np.unique(a[y0:y1,x0:x1][mask],return_counts=True)
 states=[int(i) for i,n in zip(ids,nn) if 0<i<8191 and n>=max(1,nn[(ids>0)&(ids<8191)].sum()*.005)]
 for sid in states:
  s=w['regions'][str(sid)];s.setdefault('protected_territories',[])
  if code not in s['protected_territories']:s['protected_territories'].append(code)
 catalog.append({'code':code,'name':p['BRK_NAME'],'states':states,'boundary_reserved':bool(states),
   'policy':'User-authorized territorial consolidation' if code in exceptions else 'Authored geographic subdivision / preserved territory footprint',
   'start_status':'2000 scenario control retained except documented Somaliland/South Ossetia shell corrections.'})
(ROOT/'data/world.json').write_text(json.dumps(w,ensure_ascii=False,separators=(',',':')))
(ROOT/'data/protected_territories_0208.json').write_text(json.dumps({'version':'0.2.0.8','territories':catalog},ensure_ascii=False,separators=(',',':')))
info={'version':'0.2.0.8','scenario_id':w['scenario_id'],'engine':'Godot 4.5.1 stable official','baseline_commit':'f9de969716ff5430aaad8eecadae70ba357aba77','source_update':True,'windows_executable_exported':False,'native_windows_tested':False,'fresh_campaign_required':True,'countries':len(w['countries']),'states':len(w['regions']),'land_provinces':len(json.load(open(ROOT/'data/provinces.json'))),'md_land_provinces':13221,'population':sum(s['population'] for s in w['regions'].values()),'local_demographic_refinement':'deferred','limits':json.load(open(ROOT/'data/geography_0208_report.json'))['historical_approximations']}
(ROOT/'BUILD_INFO.json').write_text(json.dumps(info,indent=2)+'\n')
print('FINALIZED_0208',len(catalog),'territory references',flush=True)
