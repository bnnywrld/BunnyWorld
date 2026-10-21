"""Remove tiny decorative settlements introduced solely for former capitals.

Run on current data; repeat runs are safe. Original settlements, national and
current state capitals, and added cities ranked at least 10,000 are retained.
Population ranks select decoration only; resident population is never edited.
"""
from collections import defaultdict
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def clean(cities, scenery, world):
    capitals = {(s.get('state_capital'), s.get('capital_province'))
                for s in world['regions'].values()}
    removed = [c for c in cities if 'GeoNames cities500' in c.get('source', '')
               and not c.get('capital')
               and (c['name'], c.get('province_id')) not in capitals
               and c.get('population_rank', 0) < 10000]
    removed_keys = {(c['name'], c['province_id']) for c in removed}
    cities[:] = [c for c in cities if (c['name'], c.get('province_id')) not in removed_keys]
    # A former capital remains a real city, but must lose its administrative icon.
    for city in cities:
        current = (city['name'], city.get('province_id')) in capitals
        if city.get('state_capital') and not current:
            city['state_capital'] = False
            city.pop('state_id', None)
    old_clusters = scenery['clusters']
    discarded = [c for c in old_clusters if c.get('category') == 'State capital'
                 and (c['name'], c['province']) in removed_keys]
    ids = {c['id'] for c in discarded}
    scenery['clusters'] = [c for c in old_clusters if c['id'] not in ids]
    by_state = defaultdict(list)
    for cluster in scenery['clusters']:
        by_state[cluster['state']].append(cluster)
    # Renormalize decoration weights without reallocating a single resident or lot.
    for sid, clusters in by_state.items():
        state = world['regions'][str(sid)]
        lon, lat = state['capital_uv'][0] * 360 - 180, 90 - state['capital_uv'][1] * 180
        nearest = min(clusters, key=lambda c: (((c['longitude'] - lon + 180) % 360 - 180) ** 2
                                             + (c['latitude'] - lat) ** 2))
        weights = [max(1, len(c['instances'])) * (1.2 if c is nearest else 1) for c in clusters]
        for cluster, weight in zip(clusters, weights):
            cluster['state_capital_priority'] = cluster is nearest
            cluster['state_visual_weight'] = weight / sum(weights)
    return {'removed_markers': len(removed), 'removed_clusters': len(discarded),
            'removed_buildings': sum(len(c['instances']) for c in discarded),
            'removed_names': [c['name'] for c in removed]}


def main():
    read = lambda name: json.loads((ROOT / 'data' / name).read_text())
    cities, scenery, world = map(read, ['cities.json', 'urban_scenery.json', 'world.json'])
    report = clean(cities, scenery, world)
    if report['removed_markers']:
        for name, data in [('cities.json', cities), ('urban_scenery.json', scenery)]:
            (ROOT / 'data' / name).write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
        # These are ordinary JSON files, not packed resources or map topology.
        path = ROOT / 'data/geography_bundle.json'
        bundle = json.loads(path.read_text())
        for name in ['data/cities.json', 'data/urban_scenery.json']:
            bundle['files'][name] = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        path.write_text(json.dumps(bundle, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
