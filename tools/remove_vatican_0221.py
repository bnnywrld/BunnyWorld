"""Absorb Vatican's country, State and province into Rome/Lazio, once."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];Image.MAX_IMAGE_PIXELS=None
def read(n):return json.loads((R/n).read_text())
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
def main():
 w=read('data/world.json');ps=read('data/provinces.json');assert w['version']=='0.2.0.19' and '0.2.0.20' in (R/'project.godot').read_text()
 population=sum(s['population']for s in w['regions'].values())
 source=w['regions'].pop('464');target=w['regions']['534'];p=ps.pop('4478');q=ps['4934']
 target['population']+=source['population'];target['provinces'].remove(4478)if 4478 in target['provinces']else None
 target['area_km2']=round(target['area_km2']+p['area_km2'],3);q['area_km2']=round(q['area_km2']+p['area_km2'],3)
 q['cities']=sorted(set(q.get('cities',[])+p.get('cities',[])))
 for key,value in source['buildings'].items():target['buildings'][key]=target['buildings'].get(key,0)+value
 w['countries'].pop('HLS');w['country_registry'].pop('HLS',None)
 for key in ['base_country_stats','cosmetic_colors']:
  if isinstance(w.get(key),dict):w[key].pop('HLS',None)
 for s in w['regions'].values():
  s['cores']=[t for t in s['cores']if t!='HLS'];s['claims']=[t for t in s['claims']if t!='HLS']
 for org in w['organizations'].values():org['members']=[t for t in org.get('members',[])if t!='HLS']
 w['countries']['ITA']['population']=sum(s['population']for s in w['regions'].values()if s['owner']=='ITA')
 pixels=0
 for tile in range(4):
  path=R/f'assets/region_ids_{tile}.png';rgb=np.array(Image.open(path).convert('RGB'));a=rgb[:,:,0].astype(np.uint16)+rgb[:,:,1].astype(np.uint16)*256;mask=a==4478
  if mask.any():pixels+=int(mask.sum());rgb[mask,0]=4934&255;rgb[mask,1]=4934>>8;Image.fromarray(rgb).save(path)
 cities=read('data/cities.json')
 for c in cities:
  if c.get('province_id')==4478:c['province_id']=4934
  if c.get('state_id')==464:c['state_id']=534;c['state_capital']=False
  if c.get('country')=='HLS':c['country']='ITA';c['capital']=False
 scene=read('data/urban_scenery.json')
 for kind in ['clusters','landmarks']:
  for c in scene[kind]:
   if c.get('province')==4478:c['province']=4934
   if c.get('state')==464:c['state']=534
   if c.get('country')=='HLS':c['country']='ITA'
 clusters=[c for c in scene['clusters']if c['state']==534];uv=target['capital_uv']
 if clusters:
  capital=min(clusters,key=lambda c:((c['longitude']+180)/360-uv[0])**2+((90-c['latitude'])/180-uv[1])**2);total=sum(max(1,len(c['instances']))for c in clusters)
  for c in clusters:c['state_capital_priority']=c is capital;c['state_visual_weight']=max(1,len(c['instances']))/total
 scene['version']='0.2.0.21'
 urban=read('data/urban_population.json');urban['states'].pop('464',None);urban['states']['534']['population_2000']=target['population']
 for g in urban.get('groups',{}).values():
  g['provinces']=sorted({4934 if pid==4478 else pid for pid in g.get('provinces',[])})
  if g.get('country_at_start')=='HLS':g['country_at_start']='ITA'
 protected=read('data/protected_territories_0210.json');protected['territories']=[row for row in protected['territories']if row['states']!=[464]]
 for row in protected['territories']:row['states']=sorted({534 if sid==464 else sid for sid in row['states']})
 protected['version']='0.2.0.21'
 demography=read('data/demographics.json');demography['profiles'].pop('HLS',None)
 w.update(version='0.2.0.21',scenario_id='bunny_world_2000_0_2_0_21')
 assert sum(s['population']for s in w['regions'].values())==population
 for n,d in [('world',w),('provinces',ps),('cities',cities),('urban_scenery',scene),('urban_population',urban),('protected_territories_0210',protected),('demographics',demography)]:write('data/'+n+'.json',d)
 write('data/microstate_geometry.json',{'enabled':False,'note':'Vatican country, State and province absorbed into Rome/Lazio in 0.2.0.21. No subpixel enclave override.'})
 write('data/geography_0221_report.json',{'removed_country':'HLS','removed_state':464,'removed_province':4478,'destination_state':534,'destination_province':4934,'province_pixels_reassigned':pixels,'global_population':population,'countries':len(w['countries']),'states':len(w['regions']),'provinces':len(ps)})
 path=R/'project.godot';path.write_text(path.read_text().replace('0.2.0.20','0.2.0.21'))
 print('VATICAN_ABSORBED',pixels,'pixels; population preserved',population)
if __name__=='__main__':main()
