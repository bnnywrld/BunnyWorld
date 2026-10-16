"""Focused 0.2.0.16 Cyprus merge; retain every other province footprint."""
from pathlib import Path
import json,io,math
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];B=R.parent/'baseline_0215';Image.MAX_IMAGE_PIXELS=None
read=lambda n:json.loads((B/n).read_text())
write=lambda n,d:(R/n).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
w=read('data/world.json');ps=read('data/provinces.json');source=w['regions'].pop('254');target=w['regions']['253'];old=ps.pop('3097');p=ps['3096']
assert source['owner']==target['owner']=='CYP'
target['population']+=source['population'];target['area_km2']=round(target['area_km2']+source['area_km2'],3);p['area_km2']=target['area_km2']
for key in ['cores','claims','geographic_divisions','geographic_codes']:target[key]=sorted(set(target.get(key,[])+source.get(key,[])))
for k,v in source['buildings'].items():target['buildings'][k]=target['buildings'].get(k,0)+v
target['provinces']=[3096];target['protected_territories']=[];target['building_slot_baseline']=4+int(4*math.sqrt(target['population']/100000))
for s in w['regions'].values():s['neighbors']=sorted(set(253 if n==254 else n for n in s['neighbors'])-{s['id']})
p['neighbors']=sorted(set(p['neighbors']+old['neighbors'])-{3096,3097});p['local_index']=1;p['name']='Cyprus · Province 1'
for q in ps.values():q['neighbors']=sorted(set(3096 if n==3097 else n for n in q['neighbors'])-{q['id']})
for c in w['countries'].values():
 c['regions']=sorted(set(253 if sid==254 else sid for sid in c['regions']))
 if c['capital']==254:c['capital']=253
cities=read('data/cities.json')
for c in cities:
 if c.get('province_id')==3097:c['province_id']=3096
 if c.get('state_id') in [253,254]:c.pop('state_id',None);c.pop('state_capital',None)
choices=[c for c in cities if c.get('province_id')==3096];capital=next((c for c in choices if c['name']=='Nicosia'),max(choices,key=lambda c:c.get('population_rank',0)));capital.update(state_capital=True,state_id=253)
target.update(state_capital=capital['name'],capital_province=3096,capital_uv=[(capital['longitude']+180)/360,(90-capital['latitude'])/180],capital_source='Existing mapped settlement; national capital',map_center=p['map_center'])
urban=read('data/urban_population.json');urban['states'].pop('254',None);urban['states']['253']={'population_2000':target['population']}
for g in urban.get('groups',{}).values():g['provinces']=sorted(set(3096 if pid==3097 else pid for pid in g.get('provinces',[])))
scene=read('data/urban_scenery.json');groups=[]
for kind in ['clusters','landmarks']:
 for c in scene[kind]:
  if c.get('province')==3097:c['province']=3096
  if c.get('state')==254:c['state']=253
  if kind=='clusters'and c.get('state')==253:groups.append(c)
if groups:
 closest=min(groups,key=lambda c:(c['longitude']-capital['longitude'])**2+(c['latitude']-capital['latitude'])**2);weights=[max(1,len(c['instances']))*(1.2 if c is closest else 1)for c in groups]
 for c,v in zip(groups,weights):c['state_capital_priority']=c is closest;c['state_visual_weight']=v/sum(weights)
protected=read('data/protected_territories_0210.json');protected['version']='0.2.0.16'
for r in protected['territories']:
 if r['code']=='B20':r['states']=[716]
 if r['code']=='B43':r['states']=[253];r['boundary_reserved']=False;r['policy']='User-authorized Cyprus buffer-zone dissolution in 0.2.0.16'
w.update(version='0.2.0.16',scenario_id='bunny_world_2000_0_2_0_16');scene['version']='0.2.0.16'
for n,d in [('world',w),('provinces',ps),('cities',cities),('urban_population',urban),('urban_scenery',scene),('protected_territories_0210',protected)]:write('data/'+n+'.json',d)
a=np.load(R/'tools/cartography/province_atlas_0215.npz')['provinces'];changed=int((a==3097).sum());a[a==3097]=3096
b=io.BytesIO();np.savez_compressed(b,provinces=a);(R/'tools/cartography/province_atlas_0216.npz').write_bytes(b.getvalue())
s=np.load(R/'tools/cartography/grouped_atlas_022r2.npz')['regions'];s[s==254]=253;b=io.BytesIO();np.savez_compressed(b,regions=s);(R/'tools/cartography/grouped_atlas_022r2.npz').write_bytes(b.getvalue())
for i in [1]:
 path=R/f'assets/region_ids_{i}.png';rgb=np.asarray(Image.open(path)).copy();mask=rgb[:,:,0].astype(np.uint16)+rgb[:,:,1].astype(np.uint16)*256==3097;rgb[mask,0]=3096&255;rgb[mask,1]=3096>>8;b=io.BytesIO();Image.fromarray(rgb).save(b,format='PNG');path.write_bytes(b.getvalue())
rgb=np.asarray(Image.open(R/'assets/province_index.png')).copy();rgb[3097//256,3097%256]=0;rgb[3096//256,3096%256]=[253,0,1];Image.fromarray(rgb).save(R/'assets/province_index.png')
print('CYPRUS_MERGED',changed,'pixels; states',len(w['regions']),'provinces',len(ps),'capital',target['state_capital'])
