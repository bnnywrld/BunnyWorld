"""Apply the user's 55-item consolidation list to the 0.2.0.18 main baseline.
Run once, then tools/build_map.py. Keep province geometry except the explicitly
requested Tiran/Sanafir union with Sinai Province 14.
"""
from pathlib import Path
from collections import defaultdict
import copy, json
import numpy as np
from PIL import Image

R = Path(__file__).resolve().parents[1]
Image.MAX_IMAGE_PIXELS = None
def read(name): return json.loads((R/name).read_text())
def write(name, value): (R/name).write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':'))+'\n')

def main():
    w = read('data/world.json'); ps = read('data/provinces.json')
    assert w['version'] == '0.2.0.17' and '0.2.0.18' in (R/'project.godot').read_text()
    before = copy.deepcopy(w); oldps = copy.deepcopy(ps)
    # (request number, source, destination). Small islands stay on the map;
    # their separate State records are dissolved into these parent States.
    operations = [
        (1,448,447),(2,85,84),(3,1262,1277),(4,972,971),(5,248,1776),
        (7,704,1615),(8,1756,1620),(9,703,1615),(10,702,1615),(11,705,695),
        (12,1762,1440),(13,1760,1552),(13,1761,1552),(14,1551,1553),
        (15,1204,1203),(16,502,591),(17,515,516),(18,506,874),(19,818,801),
        (20,4,1187),(21,1490,1469),(22,914,891),(23,910,906),(24,903,893),
        (25,1382,1383),(26,494,483),(28,497,1811),(29,224,1792),
        (30,1796,1789),(31,211,1649),(32,1576,1574),(33,1567,1566),
        (34,1411,1410),(35,1415,1410),(36,748,752),(37,749,753),
        (38,34,29),(38,231,229),(39,547,236),(40,237,236),(41,241,236),
        (42,242,236),(43,33,100),(44,129,100),(45,1787,1790),
        (47,1007,176),(49,1481,1482),(50,1529,1526),(51,1530,1523),
        (52,359,1521),(53,1525,1520),(54,428,423),(55,1500,1497),
    ]
    renames = {
        2:(84,'Minsk'),6:(1148,'Zürich–Eastern Switzerland'),
        27:(480,'West Papua'),36:(752,'South Island'),
        46:(177,'Xinjiang'),48:(1023,'Jewish Autonomous Oblast'),
        53:(1520,'Saint Martin and Saint Barthélemy'),
    }
    report = {'version':'0.2.0.19','base_commit':'0ec7ff2c16170256b5b029584f03c297652c35ef',
              'merges':[], 'renames':[], 'province_merges':[], 'country_population_changes':{}}
    remap = {s:t for _,s,t in operations}
    for item, source, target in operations:
        s = w['regions'].pop(str(source)); t = w['regions'][str(target)]
        report['merges'].append({'request':item,'source':source,'name':s['name'],
            'destination':target,'destination_name':t['name'],'from_owner':s['owner'],'to_owner':t['owner']})
        t['population'] += s['population']
        for k,v in s.get('buildings',{}).items(): t['buildings'][k] = t['buildings'].get(k,0)+v
        for k in ['cores','claims','source_states','geographic_codes','geographic_divisions','protected_territories']:
            t[k] = sorted(set(t.get(k,[])+s.get(k,[])))
        for pid in s['provinces']: ps[str(pid)]['region'] = target
        for c in w['countries'].values():
            if c['capital'] == source: c['capital'] = target
    for item,(sid,name) in renames.items():
        report['renames'].append({'request':item,'state':sid,'old':w['regions'][str(sid)]['name'],'name':name})
        w['regions'][str(sid)]['name'] = name
    w['regions']['178']['name'] = 'Tibet'
    report['renames'].append({'request':46,'state':178,'old':before['regions']['178']['name'],'name':'Tibet'})
    # Explicit footprint union, retaining the original Sinai Province 14 ID.
    target = next(p['id'] for p in oldps.values() if p['region']==1440 and p['local_index']==14)
    province_remap = {}
    for source in before['regions']['1762']['provinces']:
        p = ps.pop(str(source)); ps[str(target)]['area_km2'] += p['area_km2']; province_remap[source] = target
        report['province_merges'].append({'source':source,'destination':target,'request':12})
    for tile in range(4):
        path = R/f'assets/region_ids_{tile}.png'
        rgb = np.array(Image.open(path).convert('RGB')); ids = rgb[:,:,0].astype(np.uint16)+rgb[:,:,1].astype(np.uint16)*256
        changed = False
        for source,target in province_remap.items():
            mask = ids==source
            if mask.any(): rgb[mask,0] = target&255; rgb[mask,1] = target>>8; changed = True
        if changed: Image.fromarray(rgb).save(path)
    # Preserve existing local indices; append moved provinces after them.
    members = defaultdict(list)
    for p in ps.values(): members[p['region']].append(p['id'])
    levels = {'infrastructure','internet_station','air_base','radar_station','rail_terminal','anti_air_building','stronghold_network'}
    for key,s in w['regions'].items():
        ids = sorted(members[s['id']]); s['provinces'] = ids; s['neighbors'] = []
        assert ids
        old_indices = {pid:oldps[str(pid)]['local_index'] for pid in ids if oldps[str(pid)]['region']==s['id']}
        next_index = max(old_indices.values(), default=0)+1
        for pid in ids:
            p = ps[str(pid)]
            if pid not in old_indices: p['local_index'] = next_index; next_index += 1
            p['name'] = s['name']+' · Province '+str(p['local_index'])
            p['neighbors'] = []
        s['area_km2'] = round(sum(ps[str(pid)]['area_km2'] for pid in ids),3)
        for k in levels & s['buildings'].keys(): s['buildings'][k] = min(10,s['buildings'][k])
        s['building_slot_baseline'] = max(s.get('building_slot_baseline',0),sum(v for k,v in s['buildings'].items() if k not in levels))
        if s.get('capital_province') not in ids:
            s['capital_province'] = max(ids,key=lambda pid:ps[str(pid)]['area_km2'])
            s['capital_uv'] = ps[str(s['capital_province'])]['map_center']
        if s['id'] in remap.values():
            s['map_center'] = s['capital_uv']
    for tag,c in list(w['countries'].items()):
        c['regions'] = sorted(s['id'] for s in w['regions'].values() if s['owner']==tag)
        if not c['regions']:
            assert tag == 'MNC'
            del w['countries'][tag]; continue
        c['population'] = sum(w['regions'][str(s)]['population'] for s in c['regions'])
        if c['capital'] not in c['regions']: c['capital'] = max(c['regions'],key=lambda sid:w['regions'][str(sid)]['population'])
        c['map_center'] = w['regions'][str(c['capital'])]['capital_uv']
        if c['population'] != before['countries'][tag]['population']:
            report['country_population_changes'][tag] = c['population']-before['countries'][tag]['population']
    cities = read('data/cities.json')
    for c in cities:
        pid = province_remap.get(c.get('province_id'),c.get('province_id'))
        if pid is not None: c['province_id'] = pid
        if str(pid) in ps: c['country'] = w['regions'][str(ps[str(pid)]['region'])]['owner']
        if 'state_id' in c: c['state_id'] = remap.get(c['state_id'],c['state_id'])
        if c.get('state_capital') and str(pid) in ps:
            c['state_capital'] = pid == w['regions'][str(ps[str(pid)]['region'])].get('capital_province')
    scene = read('data/urban_scenery.json')
    for kind in ['clusters','landmarks']:
        for c in scene[kind]:
            pid = province_remap.get(c.get('province'),c.get('province'))
            if str(pid) in ps:
                c['province'] = pid; c['state'] = ps[str(pid)]['region']
                if 'country' in c: c['country'] = w['regions'][str(c['state'])]['owner']
    scene['version'] = '0.2.0.19'
    grouped = defaultdict(list)
    for c in scene['clusters']: grouped[c['state']].append(c)
    for sid,clusters in grouped.items():
        uv = w['regions'][str(sid)]['capital_uv']
        capital = min(clusters,key=lambda c:(((c['longitude']+180)/360-uv[0]+.5)%1-.5)**2+((90-c['latitude'])/180-uv[1])**2)
        total = sum(max(1,len(c['instances'])) for c in clusters)
        for c in clusters: c['state_capital_priority'] = c is capital; c['state_visual_weight'] = max(1,len(c['instances']))/total
    urban = read('data/urban_population.json'); urban['states'] = {k:{'population_2000':s['population']} for k,s in w['regions'].items()}
    for g in urban.get('groups',{}).values():
        g['provinces'] = sorted({province_remap.get(pid,pid) for pid in g.get('provinces',[])})
        owners = {w['regions'][str(ps[str(pid)]['region'])]['owner'] for pid in g['provinces'] if str(pid) in ps}
        if len(owners)==1: g['country_at_start'] = owners.pop()
    protected = read('data/protected_territories_0210.json'); protected['version'] = '0.2.0.19'
    for row in protected['territories']: row['states'] = sorted({remap.get(s,s) for s in row['states']})
    w.update(version='0.2.0.19',scenario_id='bunny_world_2000_0_2_0_19')
    assert sum(s['population'] for s in w['regions'].values()) == sum(s['population'] for s in before['regions'].values())
    report.update(states=len(w['regions']),provinces=len(ps),countries=len(w['countries']),state_remap=remap,province_remap=province_remap)
    assert set(range(1,56)) == {x[0] for x in operations}|set(renames)
    for name,value in [('world',w),('provinces',ps),('cities',cities),('urban_scenery',scene),('urban_population',urban),('protected_territories_0210',protected),('geography_0219_report',report)]: write('data/'+name+'.json',value)
    path = R/'project.godot'; path.write_text(path.read_text().replace('0.2.0.18','0.2.0.19'))
    print('STATES_0219_READY',report['states'],report['provinces'],report['countries'],'all 55 requests covered')

if __name__ == '__main__': main()
