import json,zipfile,sys,hashlib,ast,unicodedata
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from import_md import parse,Block,at_start,load_localisation,clean_name
R=Path(__file__).resolve().parents[1];w=json.load(open(R/'data/world.json'))
with zipfile.ZipFile(sys.argv[1]) as z:
 loc={}
 import re
 for filename in z.namelist():
  if '/localisation/english/' not in filename or not filename.endswith('.yml'):continue
  for line in z.read(filename).decode('utf-8-sig',errors='replace').splitlines():
   match=re.match(r'^\s*([\w.-]+):(?:\d+)?\s*"((?:\\.|[^"\\])*)"',line)
   if match:loc[match[1]]=match[2]
 coverage={}
 for n in z.namelist():
  if '/history/countries/' not in n or not n.endswith('.txt'):continue
  tag=n.split('/history/countries/')[1][:3]
  if tag not in w['countries']:continue
  b=Block(at_start(parse(z.read(n).decode('utf-8-sig'))));stats={}
  for key,target in [('set_stability','stability'),('set_war_support','war_support'),('set_political_power','political_power')]:
   value=b.get(key)
   try:
    if value is not None:stats[target]=float(value)
   except (TypeError,ValueError):pass
  variables=w['countries'][tag]['starting_variables']
  if variables.get('gdp_per_capita',0)>0:stats['gdp_per_capita_usd']=variables['gdp_per_capita']*1000
  politics=b.get('set_politics',Block([]));outlook=politics.get('ruling_party','')
  party=loc.get(tag+'_'+outlook+'_party',loc.get(tag+'_'+outlook+'_party_long',''))
  party_id=int(w['countries'][tag]['starting_variables'].get('ruling_party',0))
  party_types={1:'social_conservative',2:'social_liberal',3:'social_democrat'}
  party=loc.get(tag+'_ruling_party_'+party_types.get(party_id,''),party)
  kind={1:'conservatism',2:'liberalism',3:'socialism'}.get(party_id)
  if w['countries'][tag]['outlook']=='Western Outlook' and kind and tag+'.'+kind in loc:
   party=re.sub(r'£\w+\s*','',re.sub(r'§.','',loc[tag+'.'+kind])).strip()
  w['countries'][tag]['government']={'outlook':w['countries'][tag]['outlook'],'party':clean_name(party,loc) if party else ''}
  w['countries'][tag]['starting_stats']=stats;coverage[tag]=list(stats)
 w['stats_source']={'sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'gdp_unit_evidence':'!_energy_effects.txt identifies a gdp_per_capita value of 40 as 40k; converted to USD by multiplying by 1000.','limit':'Explicit dated history declarations only; no startup script execution or invented defaults.'}
# City positions are geographic; retain capitals and prominent cities.
def norm(v):return ''.join(c for c in unicodedata.normalize('NFKD',v.lower()) if c.isalnum() and not unicodedata.combining(c))
alias=next(ast.literal_eval(n.value) for n in ast.parse((R/'tools/build_geographic_map.py').read_text()).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='alias' for t in n.targets))
names={norm(c['name']):t for t,c in w['countries'].items()};names.update({norm(n):t for n,t in alias.items()})
cities=[]
for f in json.load(open(R/'tools/cartography/city_reference.geojson'))['features']:
 p=f['properties'];capital=bool(p['adm0cap']);tag=names.get(norm(p['adm0name']))
 if not capital and p['pop_max']<250000:continue
 if not tag:continue
 cities.append({'name':p['name'],'longitude':p['longitude'],'latitude':p['latitude'],'capital':capital,'country':tag,'population_rank':p['pop_max']})
cities.sort(key=lambda c:(not c['capital'],-c['population_rank']))
(R/'data/cities.json').write_text(json.dumps(cities,ensure_ascii=False,separators=(',',':')))
# Geographic lakes cut holes in the actual ID textures and in picking data.
lakes=json.load(open(R/'tools/cartography/lakes.geojson'));compact={'type':'FeatureCollection','features':[]};lake_names=[]
for f in lakes['features']:
 p=f['properties'];name=p.get('name') or p.get('name_en') or ''
 compact['features'].append({'type':'Feature','properties':{'name':name},'geometry':f['geometry']});lake_names.append(name)
(R/'tools/cartography/lakes.geojson').write_text(json.dumps(compact,separators=(',',':')))
for tile in range(4):
 path=R/f'assets/region_ids_{tile}.png';im=Image.open(path).convert('RGB');draw=ImageDraw.Draw(im);ox=(tile%2)*8192;oy=(tile//2)*4096
 for f in compact['features']:
  polygons=f['geometry']['coordinates'] if f['geometry']['type']=='MultiPolygon' else [f['geometry']['coordinates']]
  for poly in polygons:
   pts=[((lon+180)/360*16384-ox,(90-lat)/180*8192-oy) for lon,lat,*rest in poly[0]]
   if max(p[0] for p in pts)<0 or min(p[0] for p in pts)>=8192 or max(p[1] for p in pts)<0 or min(p[1] for p in pts)>=4096:continue
   # Preserve lake islands by excluding inner rings from the cut mask.
   mask=Image.new('1',im.size,0);md=ImageDraw.Draw(mask);md.polygon(pts,fill=1)
   for hole in poly[1:]:md.polygon([((lon+180)/360*16384-ox,(90-lat)/180*8192-oy) for lon,lat,*rest in hole],fill=0)
   im.paste((0,0,0),(0,0),mask)
 im.save(path,optimize=True)
# Update camera centers if they were submerged; preserve all map IDs.
images=[];present=set()
for i in range(4):
 rgb=np.asarray(Image.open(R/f'assets/region_ids_{i}.png'),dtype=np.uint16);ids=rgb[:,:,0]+rgb[:,:,1]*256;images.append(ids);present.update(np.unique(ids))
assert set(map(int,w['regions']))<=present,'A lake submerged a whole game region'
for sid,r in w['regions'].items():
 u,v=r['map_center'];x=int(u*16384);y=int(v*8192)
 if images[(y//4096)*2+x//8192][y%4096,x%8192]==int(sid):continue
 for i,ids in enumerate(images):
  yy,xx=np.nonzero(ids==int(sid))
  if len(xx):
   j=len(xx)//2;r['map_center']=[(float(xx[j])+i%2*8192+.5)/16384,(float(yy[j])+i//2*4096+.5)/8192];break
for c in w['countries'].values():
 sid=str(c['capital'])
 if sid in w['regions'] and w['regions'][sid]['owner']==c['tag']:c['map_center']=w['regions'][sid]['map_center']
w['map']['lakes']='Natural Earth 1:10m geographic lakes, rendered and picked as water'
(R/'data/world.json').write_text(json.dumps(w,ensure_ascii=False,separators=(',',':')))
(R/'data/update_013_report.json').write_text(json.dumps({'cities':len(cities),'lake_features':len(compact['features']),'statistics_coverage':coverage},indent=2))
print('PREPARED',len(cities),'cities',len(compact['features']),'lakes')
