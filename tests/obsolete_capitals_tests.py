"""Capital-decoration cleanup must preserve real cities and simulation data."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from clean_obsolete_capitals import clean


class CapitalCleanupTests(unittest.TestCase):
    def test_cleanup_and_repeat(self):
        world = {'regions': {'1': {'state_capital': 'Current', 'capital_province': 1,
                                  'capital_uv': [.5, .5], 'population': 12345}}}
        def city(name, rank, **extra):
            return dict(name=name, province_id=1, population_rank=rank, capital=False,
                        source='GeoNames cities500', **extra)
        cities = [city('Former', 200, state_capital=True, state_id=1),
                  city('Current', 10), city('National', 20), city('Large', 20000),
                  city('Original', 1)]
        cities[2]['capital'] = True
        cities[-1].pop('source')
        def cluster(identity, name, category):
            return dict(id=identity, name=name, province=1, state=1, longitude=0,
                        latitude=0, category=category, instances=[[0, 0, 20, 24, 0, 0]])
        scenery = {'clusters': [cluster(1, 'Former', 'State capital'),
                                cluster(2, 'Current', 'State capital'),
                                cluster(3, 'Former', 'Town')], 'landmarks': [{'id': 'keep'}]}
        original_world = copy.deepcopy(world)
        report = clean(cities, scenery, world)
        self.assertEqual(report['removed_markers'], 1)
        self.assertEqual(report['removed_clusters'], 1)
        self.assertEqual({c['name'] for c in cities}, {'Current', 'National', 'Large', 'Original'})
        self.assertEqual([c['id'] for c in scenery['clusters']], [2, 3])
        self.assertEqual(scenery['landmarks'], [{'id': 'keep'}])
        self.assertEqual(world, original_world)
        snapshot = copy.deepcopy((cities, scenery))
        self.assertEqual(clean(cities, scenery, world)['removed_markers'], 0)
        self.assertEqual((cities, scenery), snapshot)

    def test_current_data_links(self):
        read = lambda name: json.loads((ROOT / 'data' / (name + '.json')).read_text())
        cities, scenery, world, provinces = map(read, ['cities', 'urban_scenery', 'world', 'provinces'])
        capitals = {(s.get('state_capital'), s.get('capital_province')) for s in world['regions'].values()}
        for c in cities:
            self.assertIn(str(c['province_id']), provinces)
            if c.get('state_capital'):
                self.assertIn((c['name'], c['province_id']), capitals)
        for c in scenery['clusters']:
            self.assertIn(str(c['province']), provinces)
            self.assertEqual(c['state'], provinces[str(c['province'])]['region'])
        before = copy.deepcopy((cities, scenery, world))
        self.assertEqual(clean(cities, scenery, world)['removed_markers'], 0)
        self.assertEqual((cities, scenery, world), before)


if __name__ == '__main__':
    unittest.main()
