"""One-shot 0.2.0.23 -> .24 island edits. Run build_map.py afterwards.

Province identities survive State mergers. Only Malpelo and Navassa footprints
are removed. Their old statistical allocations stay in the same country.
"""
from pathlib import Path
from collections import defaultdict
import copy
import json
import math
import numpy as np
from PIL import Image

R = Path(__file__).resolve().parents[1]
Image.MAX_IMAGE_PIXELS = None

def read(name):
    return json.loads((R / name).read_text())

def write(name, value):
    (R / name).write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')) + '\n')

def point(uv):
    lon, lat = (uv[0] - .5) * 2 * math.pi, (.5 - uv[1]) * math.pi
    return np.array([math.cos(lat) * math.sin(lon), math.sin(lat), math.cos(lat) * math.cos(lon)])

def main():
    w, ps = read('data/world.json'), read('data/provinces.json')
    assert w['version'] == '0.2.0.21'
    assert '0.2.0.23' in (R / 'project.godot').read_text()
    before, oldps = copy.deepcopy(w), copy.deepcopy(ps)
    remap = {1733: 1735, 1734: 1735, 1737: 1707, 1740: 1707,
             674: 675, 676: 675, 677: 675, 678: 675, 679: 675, 490: 675}
    removed_states, removed_provinces = {238, 1743}, set()
    affected = set(remap.values())
    report = {'version': '0.2.0.24', 'state_merges': remap, 'removed_country': 'PAU',
              'removed_states': sorted(removed_states), 'removed_provinces': [],
              'statistical_transfers': []}
    for source, target in remap.items():
        s, t = w['regions'].pop(str(source)), w['regions'][str(target)]
        t['population'] += s['population']
        for key, value in s.get('buildings', {}).items():
            t['buildings'][key] = t['buildings'].get(key, 0) + value
        for key in ['cores', 'claims', 'source_states', 'geographic_codes', 'geographic_divisions', 'protected_territories']:
            t[key] = sorted(set(t.get(key, []) + s.get(key, [])))
        for pid in s['provinces']:
            ps[str(pid)]['region'] = target
    w['regions']['675']['name'] = 'Micronesia'
    for sid in sorted(removed_states):
        s = w['regions'].pop(str(sid))
        # Do not silently change national/world population in a geography patch.
        # Transfer statistics only; the island's actual land pixels become sea.
        candidates = [t for t in w['regions'].values() if t['owner'] == s['owner']]
        t = max(candidates, key=lambda q: float(point(q['map_center']).dot(point(s['map_center']))))
        t['population'] += s['population']
        affected.add(t['id'])
        for key, value in s.get('buildings', {}).items():
            t['buildings'][key] = t['buildings'].get(key, 0) + value
        report['statistical_transfers'].append({'from': sid, 'to': t['id'], 'to_name': t['name'], 'population': s['population']})
        for pid in s['provinces']:
            removed_provinces.add(pid)
            ps.pop(str(pid))
    report['removed_provinces'] = sorted(removed_provinces)
    report['removed_pixels'] = {}
    for tile in range(4):
        path = R / f'assets/region_ids_{tile}.png'
        rgb = np.array(Image.open(path).convert('RGB'))
        ids = rgb[:, :, 0].astype(np.uint16) + rgb[:, :, 1].astype(np.uint16) * 256
        mask = np.isin(ids, list(removed_provinces))
        if mask.any():
            for pid in removed_provinces:
                report['removed_pixels'][str(pid)] = report['removed_pixels'].get(str(pid), 0) + int((ids == pid).sum())
            rgb[mask] = 0
            Image.fromarray(rgb).save(path)
    members = defaultdict(list)
    for p in ps.values():
        members[p['region']].append(p['id'])
    levels = {'infrastructure', 'internet_station', 'air_base', 'radar_station', 'rail_terminal', 'anti_air_building', 'stronghold_network'}
    for sid, s in w['regions'].items():
        s['provinces'] = sorted(members[s['id']])
        s['neighbors'] = [n for n in s['neighbors'] if str(n) in w['regions'] and n != s['id']]
        s['cores'] = [t for t in s['cores'] if t != 'PAU']
        s['claims'] = [t for t in s['claims'] if t != 'PAU']
        if s['id'] not in affected:
            continue
        next_index = max((oldps[str(pid)]['local_index'] for pid in s['provinces'] if oldps[str(pid)]['region'] == s['id']), default=0) + 1
        for pid in s['provinces']:
            p = ps[str(pid)]
            if oldps[str(pid)]['region'] != s['id']:
                p['local_index'] = next_index
                next_index += 1
            p['name'] = s['name'] + ' · Province ' + str(p['local_index'])
        s['area_km2'] = round(sum(ps[str(pid)]['area_km2'] for pid in s['provinces']), 3)
        for key in levels & s['buildings'].keys():
            s['buildings'][key] = min(10, s['buildings'][key])
        s['building_slot_baseline'] = max(s.get('building_slot_baseline', 0), sum(v for k, v in s['buildings'].items() if k not in levels))
    for key in ['countries', 'country_registry', 'base_country_stats', 'cosmetic_colors']:
        w.get(key, {}).pop('PAU', None)
    for org in w['organizations'].values():
        org['members'] = [t for t in org.get('members', []) if t != 'PAU']
    for tag, c in w['countries'].items():
        c['regions'] = sorted(s['id'] for s in w['regions'].values() if s['owner'] == tag)
        c['population'] = sum(w['regions'][str(sid)]['population'] for sid in c['regions'])
        c['capital'] = remap.get(c['capital'], c['capital'])
        assert c['capital'] in c['regions']
    cities = read('data/cities.json')
    cities = [c for c in cities if c.get('province_id') not in removed_provinces and c.get('state_id') not in removed_states]
    for c in cities:
        pid = c.get('province_id')
        if str(pid) not in ps:
            continue
        sid = ps[str(pid)]['region']
        if c.get('state_id') in remap:
            c['state_id'] = sid
            c['state_capital'] = pid == w['regions'][str(sid)]['capital_province']
        if c.get('country') == 'PAU':
            c['country'], c['capital'] = 'MIC', False
    scene = read('data/urban_scenery.json')
    for kind in ['clusters', 'landmarks']:
        scene[kind] = [c for c in scene[kind] if c.get('province') not in removed_provinces and c.get('state') not in removed_states]
        for c in scene[kind]:
            if c.get('state') in remap:
                c['state'] = remap[c['state']]
            if c.get('country') == 'PAU':
                c['country'] = 'MIC'
    grouped = defaultdict(list)
    for c in scene['clusters']:
        grouped[c['state']].append(c)
    for sid in affected:
        clusters = grouped[sid]
        if not clusters:
            continue
        capital = min(clusters, key=lambda c: np.linalg.norm(point([(c['longitude'] + 180) / 360, (90 - c['latitude']) / 180]) - point(w['regions'][str(sid)]['capital_uv'])))
        total = sum(max(1, len(c['instances'])) for c in clusters)
        for c in clusters:
            c['state_capital_priority'] = c is capital
            c['state_visual_weight'] = max(1, len(c['instances'])) / total
    scene['version'] = '0.2.0.24'
    urban = read('data/urban_population.json')
    urban['states'] = {k: {'population_2000': s['population']} for k, s in w['regions'].items()}
    for key, g in list(urban.get('groups', {}).items()):
        g['provinces'] = [pid for pid in g.get('provinces', []) if pid not in removed_provinces]
        if not g['provinces']:
            del urban['groups'][key]
        elif g.get('country_at_start') == 'PAU':
            g['country_at_start'] = 'MIC'
    protected = read('data/protected_territories_0210.json')
    for row in protected['territories']:
        row['states'] = sorted({remap.get(sid, sid) for sid in row['states'] if sid not in removed_states})
    protected['territories'] = [row for row in protected['territories'] if row['states']]
    protected['version'] = '0.2.0.24'
    demography = read('data/demographics.json')
    demography['profiles'].pop('PAU', None)
    w.update(version='0.2.0.24', scenario_id='bunny_world_2000_0_2_0_24')
    assert sum(s['population'] for s in w['regions'].values()) == sum(s['population'] for s in before['regions'].values())
    assert w['countries']['MIC']['population'] == before['countries']['MIC']['population'] + before['countries']['PAU']['population']
    report.update(countries=len(w['countries']), states=len(w['regions']), land_provinces=len(ps), population=sum(s['population'] for s in w['regions'].values()))
    for name, value in [('world', w), ('provinces', ps), ('cities', cities), ('urban_scenery', scene), ('urban_population', urban), ('protected_territories_0210', protected), ('demographics', demography), ('geography_0224_report', report)]:
        write('data/' + name + '.json', value)
    path = R / 'project.godot'
    path.write_text(path.read_text().replace('0.2.0.23', '0.2.0.24'))
    print('ISLANDS_0224_READY', report, flush=True)

if __name__ == '__main__':
    main()
