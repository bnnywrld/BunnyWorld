"""Independent .24 hierarchy/reference checks and exact before/after raster diff."""
from pathlib import Path
from collections import Counter
import io
import json
import struct
import subprocess
import zlib
import numpy as np
from PIL import Image

R = Path(__file__).resolve().parents[1]
Image.MAX_IMAGE_PIXELS = None
checks = []

def read(name):
    return json.loads((R / name).read_text())

def old(name):
    base = read('BUILD_INFO.json')['repository_base_commit']
    return subprocess.check_output(['git', 'show', base + ':' + name], cwd=R)

def check(value, label):
    assert value, label
    checks.append(label)

def main():
    w, ps = read('data/world.json'), read('data/provinces.json')
    before, oldps = json.loads(old('data/world.json')), json.loads(old('data/provinces.json'))
    remap = {1733: 1735, 1734: 1735, 1737: 1707, 1740: 1707, 674: 675, 676: 675, 677: 675, 678: 675, 679: 675, 490: 675}
    deleted = {3024, 13050}
    check(len(w['countries']) == 224 and len(w['regions']) == 1239 and len(ps) == 13308, 'expected country/state/province counts')
    check(w['version'] == '0.2.0.24' and w['scenario_id'].endswith('_0_2_0_24'), 'fresh scenario identity')
    check('PAU' not in w['countries'] and 'PAU' not in w['country_registry'], 'Palau removed as country and releasable registry entry')
    check(w['countries']['MIC']['regions'] == [675] and w['regions']['675']['name'] == 'Micronesia', 'single Micronesia state')
    check(sum(s['population'] for s in w['regions'].values()) == 6144737528, 'world population preserved')
    for tag, c in w['countries'].items():
        expected = before['countries'][tag]['population'] + (before['countries']['PAU']['population'] if tag == 'MIC' else 0)
        check(c['population'] == expected, 'national population ' + tag)
        check(c['regions'] == sorted(s['id'] for s in w['regions'].values() if s['owner'] == tag), 'country membership ' + tag)
        check(c['capital'] in c['regions'], 'valid national capital ' + tag)
    for pid, p in ps.items():
        check(p['region'] == remap.get(oldps[pid]['region'], oldps[pid]['region']), 'requested province membership ' + pid)
        check(all(str(n) in ps and p['id'] in ps[str(n)]['neighbors'] for n in p['neighbors']), 'symmetric province adjacency ' + pid)
    for sid, s in w['regions'].items():
        ids = s['provinces']
        check(ids and set(ids) == {p['id'] for p in ps.values() if p['region'] == s['id']}, 'complete state membership ' + sid)
        check(len({ps[str(pid)]['local_index'] for pid in ids}) == len(ids), 'unique local province numbers ' + sid)
        check(s['capital_province'] in ids, 'valid state capital ' + sid)
        check('PAU' not in s['cores'] + s['claims'], 'removed country rights ' + sid)
    seen, changed = set(), 0
    tiny_data = (R / 'assets/display/tiny_land_bits.bwd').read_bytes()
    tw, th = struct.unpack('<II', tiny_data[:8])
    tiny = np.frombuffer(zlib.decompress(tiny_data[8:]), np.uint8).reshape(th, tw)
    tiny_bits = np.unpackbits(tiny, axis=1, bitorder='little')
    for i in range(4):
        name = f'assets/region_ids_{i}.png'
        a = np.asarray(Image.open(io.BytesIO(old(name))).convert('RGB'))
        b = np.asarray(Image.open(R / name).convert('RGB'))
        ids = a[:, :, 0].astype(np.uint16) + a[:, :, 1].astype(np.uint16) * 256
        removed = np.isin(ids, list(deleted))
        expected = a.copy()
        expected[removed] = 0
        check(np.array_equal(b, expected), 'only requested island pixels removed in tile ' + str(i))
        actual = b[:, :, 0].astype(np.uint16) + b[:, :, 1].astype(np.uint16) * 256
        seen.update(np.unique(actual).tolist())
        top, left = i // 2 * 4096, i % 2 * 8192
        check(not tiny_bits[top:top + 4096, left:left + 8192][removed].any(), 'removed islands absent from physical tiny-land fallback ' + str(i))
        changed += int(removed.sum())
    check(seen - {0, 65535} == set(map(int, ps)), 'raster IDs exactly match complete province database')
    check(changed == 5, 'exactly five native land pixels removed')
    urban = read('data/urban_population.json')
    check(set(urban['states']) == set(w['regions']), 'urban population state coverage')
    for sid, s in w['regions'].items():
        check(urban['states'][sid]['population_2000'] == s['population'], 'urban population ' + sid)
    for c in read('data/cities.json'):
        pid = c.get('province_id')
        check(pid not in deleted and c.get('state_id') not in set(remap) | {238, 1743}, 'no stale island city references ' + c['name'])
        if str(pid) not in ps:
            # Existing geographic markers without a linked province remain valid.
            check(pid in [0, None] and c['country'] in w['countries'], 'unlinked geographic city ' + c['name'])
            continue
        if 'state_id' in c:
            check(c['state_id'] == ps[str(pid)]['region'], 'city state ' + c['name'])
        check(c['country'] == w['regions'][str(ps[str(pid)]['region'])]['owner'], 'city owner ' + c['name'])
    scene = read('data/urban_scenery.json')
    oldscene = json.loads(old('data/urban_scenery.json'))
    for kind in ['clusters', 'landmarks']:
        prior = {str(c.get('id')): c for c in oldscene[kind]}
        for c in scene[kind]:
            check(str(c['province']) in ps and c['state'] == ps[str(c['province'])]['region'], 'scenery references ' + str(c.get('id', c.get('name'))))
            check(c['group'] in urban['groups'] or c['group'] == prior[str(c.get('id'))]['group'], 'no new missing scenery population group ' + str(c.get('id', c.get('name'))))
    check(all('PAU' not in o['members'] for o in w['organizations'].values()), 'organization members contain no Palau')
    protected = read('data/protected_territories_0210.json')
    check(all(str(sid) in w['regions'] for row in protected['territories'] for sid in row['states']), 'protected territory references remain valid')
    target = R / 'validation_0224'
    target.mkdir(exist_ok=True)
    report = {'passed': True, 'checks': len(checks), 'countries': len(w['countries']), 'states': len(w['regions']), 'land_provinces': len(ps), 'changed_native_pixels': changed, 'global_population': 6144737528}
    (target / 'geography_results.json').write_text(json.dumps(report, indent=2) + '\n')
    print('GEOGRAPHY_0224_PASS', report)

if __name__ == '__main__':
    main()
