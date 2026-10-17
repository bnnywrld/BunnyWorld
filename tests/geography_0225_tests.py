"""Verify .25 unions, unchanged owned land, and restored Antarctic coverage."""
from pathlib import Path
import hashlib, io, json, struct, subprocess, zlib
import numpy as np
from PIL import Image

R = Path(__file__).resolve().parents[1]
Image.MAX_IMAGE_PIXELS = None
checks = 0
def read(name): return json.loads((R / name).read_text())
def old(name): return subprocess.check_output(['git', 'show', read('BUILD_INFO.json')['repository_base_commit'] + ':' + name], cwd=R)
def check(value, label):
    global checks
    checks += 1
    assert value, label
def main():
    w, ps = read('data/world.json'), read('data/provinces.json')
    before, oldps = json.loads(old('data/world.json')), json.loads(old('data/provinces.json'))
    remap = {1732: 1735, 1601: 1603, 1606: 1602, 1600: 1602}
    check(len(w['countries']) == 224 and len(w['regions']) == 1235 and len(ps) == 13308, 'expected counts')
    check(set(ps) == set(oldps), 'all gameplay province identities preserved')
    check(set(w['countries']) == set(before['countries']), 'no country added or removed')
    check(w['version'] == '0.2.0.25' and w['scenario_id'].endswith('_0_2_0_25'), 'fresh scenario identity')
    for tag, c in w['countries'].items():
        check(c['population'] == before['countries'][tag]['population'], 'country population ' + tag)
        check(c['regions'] == sorted(s['id'] for s in w['regions'].values() if s['owner'] == tag), 'country state list ' + tag)
        check(c['capital'] in c['regions'], 'country capital ' + tag)
    check(sum(s['population'] for s in w['regions'].values()) == 6144737528, 'global population preserved')
    for pid, p in ps.items():
        check(p['region'] == remap.get(oldps[pid]['region'], oldps[pid]['region']), 'province membership ' + pid)
        check(all(str(n) in ps and p['id'] in ps[str(n)]['neighbors'] for n in p['neighbors']), 'province adjacency ' + pid)
    for sid, s in w['regions'].items():
        check(set(s['provinces']) == {p['id'] for p in ps.values() if p['region'] == s['id']}, 'complete state membership ' + sid)
        check(len({ps[str(pid)]['local_index'] for pid in s['provinces']}) == len(s['provinces']), 'unique local numbers ' + sid)
        check(s['capital_province'] in s['provinces'], 'state capital ' + sid)
    check(set(w['countries']['PAP']['regions']) == {1602,1603,1604,1605}, 'four Papuan states')
    check(w['regions']['1602']['name'] == 'Northern Papua' and w['regions']['1603']['name'] == 'Southern Papua', 'Papuan names')
    check(ps['12397']['region'] == 1735, 'Rota belongs to Mariana Islands')
    seen, added = set(), 0
    for i in range(4):
        name = f'assets/region_ids_{i}.png'
        a = np.asarray(Image.open(io.BytesIO(old(name))).convert('RGB'))
        b = np.asarray(Image.open(R / name).convert('RGB'))
        oldids = a[:,:,0].astype(np.uint16) + a[:,:,1].astype(np.uint16) * 256
        ids = b[:,:,0].astype(np.uint16) + b[:,:,1].astype(np.uint16) * 256
        changed = np.any(a != b, axis=2)
        check(not changed.any() if i < 2 else np.all(oldids[changed] == 0) and np.all(ids[changed] == 65535), 'only Antarctic ocean-to-land additions in tile ' + str(i))
        check(np.array_equal(a[(oldids > 0) & (oldids != 65535)], b[(oldids > 0) & (oldids != 65535)]), 'all owned province pixels unchanged in tile ' + str(i))
        seen.update(np.unique(ids).tolist())
        added += int(changed.sum())
    check(seen - {0,65535} == set(map(int,ps)), 'complete province raster ID set')
    check(added == 12530235, 'exact Antarctic restoration delta')
    blob = (R / 'assets/display/coast_distance_0217.bwd').read_bytes()
    ww, hh = struct.unpack('<II',blob[:8]);coast=np.frombuffer(zlib.decompress(blob[8:]),'<f2').reshape(hh,ww)
    for lon,lat in [(0,-85),(90,-80),(-90,-80),(140,-80)]:
        check(float(coast[int((90-lat)/180*hh),int((lon+180)/360*ww)]) > .99, 'Antarctic interior coast coverage ' + str(lon))
    for lon,lat in [(0,-55),(90,-55),(-90,-55)]:
        check(float(coast[int((90-lat)/180*hh),int((lon+180)/360*ww)]) < .01, 'Southern Ocean remains water ' + str(lon))
    for c in read('data/cities.json'):
        check(c.get('state_id') not in remap, 'city has no removed state ' + c['name'])
        if str(c.get('province_id')) in ps and 'state_id' in c:
            check(c['state_id'] == ps[str(c['province_id'])]['region'], 'city state/province consistency ' + c['name'])
    for kind in ['clusters','landmarks']:
        for c in read('data/urban_scenery.json')[kind]:
            check(c['state'] == ps[str(c['province'])]['region'], 'scenery state/province consistency ' + str(c.get('id')))
    urban = read('data/urban_population.json')
    check(set(urban['states']) == set(w['regions']), 'urban state coverage')
    for sid,s in w['regions'].items(): check(urban['states'][sid]['population_2000'] == s['population'], 'urban population ' + sid)
    audit = read('documentation/state_audit_0225/audit.json')
    check(audit['supplied_md_archive_verified'] is True, 'MD reference verified against supplied archive')
    check(len(audit['countries']) == len(w['countries']) and audit['countries_below_raw_md'] == 34 and audit['raw_country_shortfall_sum'] == 82, 'complete accurate country audit')
    for row in audit['countries']: check(row['current_states'] == len(w['countries'][row['tag']]['regions']), 'current audit count ' + row['tag'])
    out = R / 'validation_0225';out.mkdir(exist_ok=True)
    result = {'passed':True,'checks':checks,'countries':224,'states':1235,'land_provinces':13308,'global_population':6144737528,'restored_antarctic_pixels':added,'owned_province_pixels_changed':0,'audit_countries_below_raw_md':34,'raw_md_shortfall_sum':82}
    (out/'geography_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print('GEOGRAPHY_0225_PASS',result)
if __name__ == '__main__': main()
