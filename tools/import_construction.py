"""Extract MD construction values and derive coastal states without changing geography."""
import argparse, hashlib, json, re, zipfile
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
NAMES={'industrial_complex':'Civilian Industry','arms_factory':'Military Industry','dockyard':'Naval Dockyard','offices':'Offices','agriculture_district':'Agriculture District','microchip_plant':'Microchip Plant','composite_plant':'Composite Plant','synthetic_refinery':'Synthetic Refinery','fossil_powerplant':'Fossil Fuel Power Plant','nuclear_reactor':'Nuclear Power Plant','renewable_energy_infra':'Renewable Energy','infrastructure':'Infrastructure','internet_station':'Internet Infrastructure','rail_terminal':'Railroads','air_base':'Air Base','anti_air_building':'SAM Site','radar_station':'Radar Station','fuel_silo':'Strategic Resource Reserve','rocket_site':'Missile Launch Site','energy_infrastructure':'Reinforced Electrical Grid','industrial_infrastructure':'High Capacity Electrical Grid','enrichment_facility':'Enrichment Facility'}
PRICE_KEYS={'industrial_complex':'Civilian Industry','arms_factory':'Military Industry','dockyard':'Dockyard','offices':'Offices','agriculture_district':'Agriculture District','microchip_plant':'Microchip Plant','composite_plant':'Composite Plant','synthetic_refinery':'Synthetic Refinery','fossil_powerplant':'Fossil Fuel Powerplant','nuclear_reactor':'Nuclear Reactor','renewable_energy_infra':'Renewable Energy Infrastructure','infrastructure':'Infrastructure','internet_station':'Network Infrastructure','rail_terminal':'Rail Terminal','air_base':'Air Base','anti_air_building':'Sam Site','radar_station':'Radar Station','fuel_silo':'Fuel Silo','rocket_site':'Missile Launch Site','energy_infrastructure':'Reinforced Electrical Grid','industrial_infrastructure':'High Capacity Electrical Grid','enrichment_facility':'Enrichment Facility'}
GDP={'industrial_complex':17.5,'arms_factory':1.5,'dockyard':1.5,'offices':50,'agriculture_district':25,'microchip_plant':32,'composite_plant':28,'synthetic_refinery':10,'nuclear_reactor':4,'fossil_powerplant':1.7,'renewable_energy_infra':2,'internet_station':3.5,'rail_terminal':2.5}
def block(text,key):
 start=re.search(r'^\s*'+re.escape(key)+r'\s*=\s*\{',text,re.M).end();depth=1;i=start
 while depth:
  depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[start:i-1]
def number(text,key,default=0):
 m=re.search(r'^\s*'+key+r'\s*=\s*([\d.]+)',text,re.M)
 return float(m[1]) if m else default

def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);a=ap.parse_args()
 with zipfile.ZipFile(a.archive) as z:
  path=next(n for n in z.namelist() if n.endswith('/common/buildings/00_buildings.txt'))
  raw=z.read(path);text=raw.decode('utf-8-sig');clean=re.sub(r'#.*','',text)
  money_path=next(n for n in z.namelist() if n.endswith('/common/scripted_effects/00_money_system.txt'))
  money_raw=z.read(money_path);money_text=money_raw.decode('utf-8-sig')
 data={}
 gdp_vars={'industrial_complex':'civ','arms_factory':'mil','dockyard':'dockyard','offices':'office','agriculture_district':'agriculture_district','microchip_plant':'microchip','composite_plant':'composite','synthetic_refinery':'synthetic'}
 for key,name in NAMES.items():
  b=block(clean,key); price=re.search(r'^# '+re.escape(PRICE_KEYS[key])+r' \([^)]*\) - \$([\d.]+)',text,re.M)
  if not price: raise ValueError(key)
  network=key in ['infrastructure','internet_station','rail_terminal']
  data[key]={'name':name,'points':number(b,'base_cost'),'extra_points':number(b,'per_level_extra_cost'),'money_usd':float(price[1])*1e9,'max_level':10 if network else int(number(b,'state_max',1)),'shared':bool(re.search(r'shares_slots\s*=\s*yes',b)) and not network,'coastal':bool(re.search(r'only_costal\s*=\s*yes',b)),'gdp_base_billion':number(money_text,'@gdp_'+gdp_vars[key]+'_base_factor') if key in gdp_vars else GDP.get(key,0),'category':'Networks' if network else ('Economy' if key in GDP else 'State facilities')}
 # Only proper sea areas count: exclude lakes/reservoirs and source-ID water holes.
 p=np.asarray(Image.open(ROOT/'assets/province_ids.png').convert('RGB'),dtype=np.uint32);pid=p[:,:,0]+256*p[:,:,1]
 s=np.asarray(Image.open(ROOT/'assets/sea_ids.png').convert('RGB'),dtype=np.uint32);sid=s[:,:,0]+256*s[:,:,1]
 seas=json.loads((ROOT/'data/sea_regions.json').read_text());valid=[int(k) for k,v in seas.items() if not v.get('is_inland_water',False) and not v['name'].startswith('Inland Water')]
 water=np.isin(sid,valid)&(pid==0)
 near=np.roll(water,1,1)|np.roll(water,-1,1)
 near[1:]|=water[:-1];near[:-1]|=water[1:]
 coastal_pids=np.unique(pid[near&(pid>0)&(pid<65535)])
 provinces=json.loads((ROOT/'data/provinces.json').read_text())
 coast=sorted({int(provinces[str(int(p))]['region']) for p in coastal_pids if str(int(p)) in provinces})
 out={'source':{'file':path,'sha256':hashlib.sha256(raw).hexdigest(),'money_unit':'MD billion USD; pricing-model header','money_system_sha256':hashlib.sha256(money_raw).hexdigest(),'gdp':'00_money_system.txt base coefficients; neutral sector modifiers, full staffing; overall_productivity / 1000','railroads':'State-level rail network uses MD rail_terminal cost/output. Province routes deferred.'},'buildings':data,'coastal_states':coast,'factory_points_per_day':4.0}
 (ROOT/'data/construction.json').write_text(json.dumps(out,indent=2)+'\n')
 print(len(data),'building types;',len(coast),'coastal states')
if __name__=='__main__':main()
