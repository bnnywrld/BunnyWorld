"""Build tunable BunnyWorld economy rules around current MD-derived building metadata.
Prices and flow coefficients are gameplay calibration, not physical commodity statistics.
"""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def main():
    buildings=json.loads((ROOT/'data/construction.json').read_text(encoding='utf8'))['buildings']
    staffing=json.loads((ROOT/'data/state_economy_2000.json').read_text(encoding='utf8'))['workers_per_level']
    names={'oil':'Fossil Fuels','steel':'Steel','aluminium':'Light Metals','chromium':'Precious Metals','tungsten':'Technology Metals','rubber':'Rubber','microchips':'Microchips','composites':'Advanced Composites','food':'Food','manufactured_goods':'Manufactured Goods'}
    prices={'oil':1000,'steel':600,'aluminium':1500,'chromium':50000,'tungsten':20000,'rubber':2000,'microchips':10000,'composites':8000,'food':12,'manufactured_goods':10000}
    shares={'oil':.045,'steel':.025,'aluminium':.012,'chromium':.003,'tungsten':.006,'rubber':.004,'microchips':.012,'composites':.006,'food':0,'manufactured_goods':.14}
    outputs={'industrial_complex':'manufactured_goods','agriculture_district':'food','microchip_plant':'microchips','composite_plant':'composites','synthetic_refinery':'oil'}
    # Use the accepted ESA-2000 cropland family, never total desert/ice area.
    # This reads immutable render inputs and writes no geographic asset.
    world=json.loads((ROOT/'data/world.json').read_text(encoding='utf8'))
    provinces=json.loads((ROOT/'data/provinces.json').read_text(encoding='utf8'))
    ids=np.asarray(Image.open(ROOT/'assets/province_ids.png').convert('RGB'),dtype=np.uint16)
    province_ids=ids[:,:,0]+ids[:,:,1]*256
    lookup=np.zeros(65536,dtype=np.uint16)
    for pid,p in provinces.items():lookup[int(pid)]=int(p['region'])
    states=lookup[province_ids]
    terrain=np.asarray(Image.open(ROOT/'assets/terrain_types.png').convert('RGB').resize((ids.shape[1],ids.shape[0]),Image.Resampling.NEAREST))
    mixture=terrain[:,:,2].astype(np.float32)/255
    cropland=(terrain[:,:,0]==2)*(1-mixture)+(terrain[:,:,1]==2)*mixture
    latitude=np.cos(np.linspace(np.pi/2,-np.pi/2,ids.shape[0],dtype=np.float32))[:,None]
    total=np.bincount(states.ravel(),weights=np.broadcast_to(latitude,states.shape).ravel(),minlength=8192)
    crops=np.bincount(states.ravel(),weights=(cropland*latitude).ravel(),minlength=8192)
    potential={sid:{'cropland_share':round(float(crops[int(sid)]/total[int(sid)]),6) if total[int(sid)]>0 else 0.,'cropland_km2':round(float(r['area_km2'])*float(crops[int(sid)]/total[int(sid)]),3) if total[int(sid)]>0 else 0.} for sid,r in world['regions'].items()}
    recipes={}
    for key,b in buildings.items():
        recipes[key]={'workers':staffing.get(key,0),'output':outputs.get(key,''),'output_capacity':(.1 if key=='synthetic_refinery' else 1) if key in outputs else 0,'inputs':{},'electricity_mw':None,'technology_modifiers':{},'operating_expense_share':.02}
    recipes['industrial_complex']['inputs']={'steel':.08,'aluminium':.03,'rubber':.02,'microchips':.02}
    recipes['microchip_plant']['inputs']={'tungsten':.06,'chromium':.02}
    recipes['composite_plant']['inputs']={'oil':.06,'aluminium':.03}
    recipes['agriculture_district']['inputs']={'oil':.03}
    recipes['data_center']['inputs']={'microchips':.015}
    out={'version':1,'source':{'policy':__doc__,'construction_sha256':hashlib.sha256((ROOT/'data/construction.json').read_bytes()).hexdigest(),'cropland':'Area-weighted cropland-family coverage from existing ESA CCI 2000 prepared terrain types; approximate potential, not historical food output.','terrain_sha256':hashlib.sha256((ROOT/'assets/terrain_types.png').read_bytes()).hexdigest(),'province_ids_sha256':hashlib.sha256((ROOT/'assets/province_ids.png').read_bytes()).hexdigest()},'agricultural_potential':potential,
         'goods':{k:{'name':v,'base_price_usd':prices[k],'gdp_demand_share':shares[k],'unit':'person-month food basket' if k=='food' else 'standardized market bundle','capacity_unit':'RU; MD source capacity points' if k in ['oil','steel','aluminium','chromium','tungsten','rubber'] else 'building production capacity'} for k,v in names.items()},
         'buildings':recipes,'price_monthly_limit':.025,'price_response':.12,'price_minimum_factor':.35,'price_maximum_factor':4.,'initial_supply_margin':1.08,'private_import_budget_gdp_share':.55,
         'base_productivity_growth':.012,'education_productivity_growth':.008,'quality_adjustment':.02,'quality_monthly_limit':.6,'education_maintenance':[1.,5.],'healthcare_maintenance':[1.,7.],
         'health_growth_per_quality_point':.0001,'food_stress_adjustment':.15,'food_growth_penalty':.06,'employment_adjustment':.12,'frictional_unemployment':.02,
         'budget':{'population_tax':22.,'corporate_tax':22.,'military':2.,'administration':1.5,'security':1.,'education':4.,'healthcare':5.,'welfare':3.5,'research':1.},
         'budget_limits':{'population_tax':60.,'corporate_tax':60.,'military':15.,'administration':8.,'security':8.,'education':10.,'healthcare':15.,'welfare':20.,'research':5.},
         'electricity':{'active':False,'generation':None,'consumption':None,'storage':None,'connections':[]},'computing':{'active':False,'capacity':None,'allocations':{},'technology_unlocks':[]}}
    (ROOT/'data/economy_rules.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8',newline='\n')
    print('Economy rules:',len(names),'goods,',len(recipes),'building definitions')
if __name__=='__main__':main()
