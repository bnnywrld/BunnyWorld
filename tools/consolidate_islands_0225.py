"""Apply .25 approved State unions and restore neutral Antarctic terrain."""
from pathlib import Path
from collections import defaultdict
import copy, hashlib, json, math
import numpy as np
from PIL import Image
from rasterio.features import rasterize
from rasterio.transform import Affine

R = Path(__file__).resolve().parents[1]
Image.MAX_IMAGE_PIXELS = None
def read(name): return json.loads((R / name).read_text())
def write(name, data): (R / name).write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n')

def main():
    w, ps = read('data/world.json'), read('data/provinces.json')
    assert w['version'] == '0.2.0.24'
    before, oldps = copy.deepcopy(w), copy.deepcopy(ps)
    remap = {1732: 1735, 1601: 1603, 1606: 1602, 1600: 1602}
    for sid, target in remap.items():
        s, t = w['regions'].pop(str(sid)), w['regions'][str(target)]
        t['population'] += s['population']
        for key, value in s['buildings'].items(): t['buildings'][key] = t['buildings'].get(key, 0) + value
        for key in ['cores', 'claims', 'source_states', 'geographic_codes', 'geographic_divisions', 'protected_territories']:
            t[key] = sorted(set(t.get(key, []) + s.get(key, [])))
        for pid in s['provinces']: ps[str(pid)]['region'] = target
    members = defaultdict(list)
    for p in ps.values(): members[p['region']].append(p['id'])
    levels = {'infrastructure', 'internet_station', 'air_base', 'radar_station', 'rail_terminal', 'anti_air_building', 'stronghold_network'}
    for sid in set(remap.values()):
        s = w['regions'][str(sid)]
        s['provinces'] = sorted(members[sid])
        next_index = max(oldps[str(pid)]['local_index'] for pid in s['provinces'] if oldps[str(pid)]['region'] == sid) + 1
        for pid in s['provinces']:
            p = ps[str(pid)]
            if oldps[str(pid)]['region'] != sid:
                p['local_index'] = next_index; next_index += 1
            p['name'] = s['name'] + ' · Province ' + str(p['local_index'])
        s['area_km2'] = round(sum(ps[str(pid)]['area_km2'] for pid in s['provinces']), 3)
        for key in levels & s['buildings'].keys(): s['buildings'][key] = min(10, s['buildings'][key])
        s['building_slot_baseline'] = max(s.get('building_slot_baseline', 0), sum(v for k, v in s['buildings'].items() if k not in levels))
    for tag, c in w['countries'].items():
        c['regions'] = sorted(s['id'] for s in w['regions'].values() if s['owner'] == tag)
        c['capital'] = remap.get(c['capital'], c['capital'])
        c['population'] = sum(w['regions'][str(sid)]['population'] for sid in c['regions'])
        assert c['population'] == before['countries'][tag]['population']
    cities = read('data/cities.json')
    for c in cities:
        if c.get('state_id') in remap:
            c['state_id'] = remap[c['state_id']]
            c['state_capital'] = c.get('province_id') == w['regions'][str(c['state_id'])]['capital_province']
    scene = read('data/urban_scenery.json')
    for kind in ['clusters', 'landmarks']:
        for c in scene[kind]:
            if c.get('state') in remap: c['state'] = remap[c['state']]
    def delta(c, uv):
        return (((c['longitude'] + 180) / 360 - uv[0] + .5) % 1 - .5) ** 2 + ((90 - c['latitude']) / 180 - uv[1]) ** 2
    for sid in set(remap.values()):
        clusters = [c for c in scene['clusters'] if c['state'] == sid]
        if not clusters: continue
        capital = min(clusters, key=lambda c: delta(c, w['regions'][str(sid)]['capital_uv']))
        total = sum(max(1, len(c['instances'])) for c in clusters)
        for c in clusters:
            c['state_capital_priority'] = c is capital
            c['state_visual_weight'] = max(1, len(c['instances'])) / total
    scene['version'] = '0.2.0.25'
    urban = read('data/urban_population.json')
    urban['states'] = {k: {'population_2000': s['population']} for k, s in w['regions'].items()}
    protected = read('data/protected_territories_0210.json')
    for row in protected['territories']: row['states'] = sorted({remap.get(sid, sid) for sid in row['states']})
    protected['version'] = '0.2.0.25'
    # Antarctica is reserved land ID 65535 -> display region 8191. It is not a
    # playable/releasable country or a populated gameplay province.
    source = R / 'tools/cartography/natural_earth_map_units.geojson'
    features = json.loads(source.read_text())['features']
    antarctica = [f['geometry'] for f in features if f['properties'].get('NAME') == 'Antarctica']
    assert len(antarctica) == 1
    top = math.floor(150 / 180 * 8192)
    transform = Affine(360 / 16384, 0, -180, 0, -180 / 8192, 90 - top * 180 / 8192)
    mask = rasterize([(g, 1) for g in antarctica], out_shape=(8192 - top, 16384), transform=transform, dtype='uint8') > 0
    restored = 0
    for tile in [2, 3]:
        path = R / f'assets/region_ids_{tile}.png'
        rgb = np.array(Image.open(path).convert('RGB'))
        part = rgb[top - 4096:]
        selected = mask[:, tile % 2 * 8192:(tile % 2 + 1) * 8192]
        ids = part[:, :, 0].astype(np.uint16) + part[:, :, 1].astype(np.uint16) * 256
        assert not np.any(selected & (ids != 0) & (ids != 65535)), 'Never replace owned provinces with Antarctica'
        restored += int(np.count_nonzero(selected & (ids == 0)))
        part[selected] = [255, 255, 0]
        Image.fromarray(rgb).save(path)
    assert restored > 1_000_000
    w.update(version='0.2.0.25', scenario_id='bunny_world_2000_0_2_0_25')
    w['map']['antarctica_region_id'] = 8191
    w['map']['antarctica_province_id'] = 65535
    report = {'version': '0.2.0.25', 'state_merges': remap, 'countries': len(w['countries']), 'states': len(w['regions']), 'land_provinces': len(ps), 'population': sum(s['population'] for s in w['regions'].values()), 'antarctica': {'source': source.relative_to(R).as_posix(), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'restored_pixels': restored, 'province_sentinel': 65535, 'display_region': 8191, 'status': 'Neutral unclaimed terrain; no ordinary country created'}}
    for name, value in [('world', w), ('provinces', ps), ('cities', cities), ('urban_scenery', scene), ('urban_population', urban), ('protected_territories_0210', protected), ('geography_0225_report', report)]: write('data/' + name + '.json', value)
    path = R / 'project.godot'; path.write_text(path.read_text().replace('0.2.0.24', '0.2.0.25'))
    print('GEOGRAPHY_0225_READY', report, flush=True)

if __name__ == '__main__': main()
