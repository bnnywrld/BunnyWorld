"""Import a bounded 2000 scenario, not the HOI4 scripting engine.

Usage: python tools/import_md.py path/to/bunnyversion34.zip
Only declarations and supported history assignments are read. Scripts remain
reference material. Original archives are never changed.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from PIL import Image

START = (2000, 1, 1)
ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'\s+|#[^\n]*|"(?:\\.|[^"\\])*"|[{}]|[<>!]?=|[<>]|[^\s{}=<>!#]+')


@dataclass
class Block:
    items: list

    def values(self, key):
        return [v for k, op, v in self.items if k == key]

    def get(self, key, default=None):
        vals = self.values(key)
        return vals[-1] if vals else default

    def scalars(self):
        return [v for k, op, v in self.items if k is None and not isinstance(v, Block)]


def parse(text: str) -> Block:
    tokens = [m.group() for m in TOKEN.finditer(text) if not m.group().isspace() and not m.group().startswith('#')]
    index = 0

    def atom(token):
        if token.startswith('"'):
            return token[1:-1].replace('\\"', '"').replace('\\\\', '\\')
        return token

    def block(nested=False):
        nonlocal index
        items = []
        while index < len(tokens):
            if tokens[index] == '}':
                if not nested:
                    raise ValueError('Unexpected closing brace')
                index += 1
                return Block(items)
            key = atom(tokens[index])
            index += 1
            if index < len(tokens) and tokens[index] in ('=', '>', '<', '>=', '<=', '!='):
                op = tokens[index]
                index += 1
                if index >= len(tokens):
                    raise ValueError('Missing value for ' + key)
                if tokens[index] == '{':
                    index += 1
                    value = block(True)
                else:
                    value = atom(tokens[index])
                    index += 1
                items.append((key, op, value))
            else:
                items.append((None, None, key))
        if nested:
            raise ValueError('Unclosed block')
        return Block(items)

    return block()


def date_key(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}\.\d{1,2}\.\d{1,2}(?:\.\d+)?', value):
        return None
    return tuple(int(v) for v in value.split('.')[:3])


def at_start(block: Block) -> list:
    ordinary, dated = [], []
    for key, op, value in block.items:
        date = date_key(key)
        if date:
            if date <= START:
                dated.append((date, value))
        else:
            ordinary.append((key, op, value))
    for _, value in sorted(dated, key=lambda item: item[0]):
        if isinstance(value, Block):
            ordinary.extend(at_start(value))
    return ordinary


def read(z, path):
    return z.read(path).decode('utf-8-sig', errors='replace')


def load_localisation(z):
    result = {}
    # Explicit replace files take precedence over ordinary declarations.
    paths = sorted(n for n in z.namelist() if n.startswith('localisation/english/') and n.endswith('.yml'))
    paths.sort(key=lambda n: ('/replace/' in n, n))
    for n in paths:
        for line in read(z, n).splitlines():
            m = re.match(r'^\s*([\w.-]+):(?:\d+)?\s*"((?:\\.|[^"\\])*)"', line)
            if m:
                result[m[1]] = m[2].replace('\\"', '"').replace('\\n', ' ')
    return result


def clean_name(value, localisation):
    for _ in range(6):
        value = re.sub(r'\$([^$]+)\$', lambda m: localisation.get(m[1], m[1]), value)
    return re.sub(r'§.', '', value).strip()


def import_world(archive: Path):
    regions, country_history, diagnostics = {}, {}, []
    with ZipFile(archive) as z:
        loc = load_localisation(z)
        country_files = {}
        for n in sorted(z.namelist()):
            if n.startswith('common/country_tags/') and n.endswith('.txt'):
                for key, _, value in parse(read(z, n)).items:
                    if key and isinstance(value, str):
                        country_files[key] = 'common/' + value

        for n in sorted(z.namelist()):
            if n.startswith('history/countries/') and n.endswith('.txt'):
                m = re.match(r'history/countries/([A-Z0-9]{3})\b', n)
                if m:
                    country_history[m[1]] = Block(at_start(parse(read(z, n))))

        for n in sorted(z.namelist()):
            if not (n.startswith('history/states/') and n.endswith('.txt')):
                continue
            state = parse(read(z, n)).get('state')
            if not isinstance(state, Block):
                continue
            sid = int(state.get('id'))
            history = Block(at_start(state.get('history', Block([]))))
            owner = history.get('owner', '')
            province_block = state.get('provinces', Block([]))
            population = int(float(state.get('manpower', 0)))
            for change in history.values('set_manpower'):
                if not isinstance(change, Block):
                    population = int(float(change))
            # Later history blocks may override numeric population declarations.
            if history.get('manpower') is not None:
                population = int(float(history.get('manpower')))
            buildings = history.get('buildings', Block([]))
            key = state.get('name', 'STATE_' + str(sid))
            regions[str(sid)] = {
                'id': sid, 'name': clean_name(loc.get(key, key), loc), 'owner': owner,
                'population': population,
                'provinces': [int(p) for p in province_block.scalars()],
                'cores': list(dict.fromkeys(history.values('add_core_of'))),
                'buildings': {k: int(v) for k, _, v in buildings.items if k and isinstance(v, str) and v.isdigit()},
            }

        tags = sorted({r['owner'] for r in regions.values() if r['owner']})
        countries = {}
        outlooks = {'democratic': 'Western Outlook', 'communism': 'Multipolar Outlook',
                    'neutrality': 'Non-Aligned Outlook', 'fascism': 'Unspecified',
                    'nationalist': 'Nationalist Outlook'}
        for cid, tag in enumerate(tags, 1):
            history = country_history.get(tag, Block([]))
            politics = history.get('set_politics', Block([]))
            ideology = politics.get('ruling_party', '')
            name = loc.get(tag + '_' + ideology, loc.get(tag, tag))
            colour = [120, 145, 165]
            path = country_files.get(tag)
            if path and path in z.namelist():
                data = parse(read(z, path))
                cb = data.get('color')
                if isinstance(cb, Block) and len(cb.scalars()) >= 3:
                    colour = [int(float(v)) for v in cb.scalars()[:3]]
            owned = [r['id'] for r in regions.values() if r['owner'] == tag]
            ideas = []
            for ib in history.values('add_ideas'):
                ideas.extend(ib.scalars() if isinstance(ib, Block) else [ib])
            variables = {}
            for vb in history.values('set_variable'):
                if isinstance(vb, Block):
                    for k, _, v in vb.items:
                        if k and isinstance(v, str):
                            try:
                                variables[k] = float(v)
                            except ValueError:
                                pass
            countries[tag] = {
                'tag': tag, 'index': cid, 'name': clean_name(name, loc), 'color': colour,
                'outlook': outlooks.get(ideology, 'Unspecified'),
                'capital': int(history.get('capital', 0)), 'regions': owned,
                'population': sum(regions[str(r)]['population'] for r in owned),
                'organizations': [], 'starting_variables': variables,
            }
            countries[tag]['starting_ideas'] = list(dict.fromkeys(ideas))

        definitions = list(csv.reader(io.StringIO(read(z, 'map/definition.csv')), delimiter=';'))
        max_id = max(int(row[0]) for row in definitions if row and row[0].isdigit())
        province_region = np.zeros(max_id + 1, np.uint16)
        seen = set()
        for r in regions.values():
            for pid in r['provinces']:
                if pid in seen:
                    raise ValueError('Province belongs to two regions: ' + str(pid))
                seen.add(pid)
                province_region[pid] = r['id']
        # Colour lookup is independent of country colours, which may overlap.
        rgb_to_id = np.zeros(1 << 24, np.uint16)
        for row in definitions:
            if row and row[0].isdigit():
                pid, red, green, blue = map(int, row[:4])
                rgb_to_id[(red << 16) + (green << 8) + blue] = pid
        source = np.asarray(Image.open(io.BytesIO(z.read('map/provinces.bmp'))).convert('RGB'))
        encoded = (source[:, :, 0].astype(np.uint32) << 16) | (source[:, :, 1].astype(np.uint32) << 8) | source[:, :, 2]
        province_ids = rgb_to_id[encoded]
        region_ids = province_region[province_ids]
        region_rgb = np.zeros((*region_ids.shape, 3), dtype=np.uint8)
        region_rgb[:, :, 0] = region_ids & 255
        region_rgb[:, :, 1] = region_ids >> 8
        ROOT.joinpath('assets').mkdir(exist_ok=True)
        Image.fromarray(region_rgb).save(ROOT / 'assets/region_ids.png', optimize=True)

        # Stable centres: largest connected latitude/longitude distribution is
        # unnecessary for focus; a populated region avoids overseas possessions.
        h, w = region_ids.shape
        flat_regions = region_ids.ravel().astype(np.int32)
        counts = np.bincount(flat_regions, minlength=4096)
        x_sums = np.bincount(flat_regions, weights=np.tile(np.arange(w), h), minlength=4096)
        y_sums = np.bincount(flat_regions, weights=np.repeat(np.arange(h), w), minlength=4096)
        centers = {int(sid): [float(x_sums[int(sid)] / counts[int(sid)] / w),
                             float(y_sums[int(sid)] / counts[int(sid)] / h)]
                   for sid in regions if counts[int(sid)] > 0}
        for tag, country in countries.items():
            sid = country['capital']
            if str(sid) not in regions or regions[str(sid)]['owner'] != tag:
                sid = max(country['regions'], key=lambda r: regions[str(r)]['population'])
            if sid in centers:
                country['map_center'] = centers[sid]
            else:
                country['map_center'] = [0.5, 0.5]
                diagnostics.append('Region absent from map for ' + tag)
        for sid, region in regions.items():
            region['map_center'] = centers.get(int(sid), [0.5, 0.5])

        # Organizations are persistent objects; membership is many-to-many.
        # Import only membership actually declared in the dated country history.
        organizations = {}
        specs = [
            ('EU', 'European Union', 'Economic and political cooperation', 'EU_member', 'Integration'),
            ('NATO', 'NATO', 'Collective defence', 'NATO_member', 'Defensive alliance'),
            ('ASEAN', 'ASEAN', 'Regional cooperation', 'ASEAN_Member', 'Regional association'),
            ('ECOWAS', 'ECOWAS', 'West African economic cooperation', 'ecowas_member_state', 'Economic community'),
            ('WTO', 'World Trade Organization', 'International trade', 'wto_member', 'Trade organization'),
            ('G7', 'Group of Seven', 'Economic policy coordination', 'g7_member', 'Policy forum'),
        ]
        for oid, name, purpose, idea, direction in specs:
            members = sorted(tag for tag, c in countries.items() if idea in c['starting_ideas'])
            organizations[oid] = {'id': oid, 'name': name, 'purpose': purpose,
                'members': members, 'direction': direction, 'budget': 0.0,
                'projects': [], 'charter': {'voting_rule': 'Not yet simulated'}}
            for tag in members:
                countries[tag]['organizations'].append(oid)

        world = {'schema_version': 1, 'scenario_id': 'md_bunny_2000_01', 'start_date': list(START),
                 'name': 'Millennium Dawn: Bunny world, 2000',
                 'countries': countries, 'regions': regions, 'organizations': organizations,
                 'map': {'width': w, 'height': h, 'palette_width': 4096,
                         'cartography': 'MD game cartography wrapped onto a sphere'},
                 'source': {'filename': archive.name, 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest()}}
        ROOT.joinpath('data').mkdir(exist_ok=True)
        (ROOT / 'data/world.json').write_text(json.dumps(world, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        report = {'countries': len(countries), 'regions': len(regions),
                  'population': sum(r['population'] for r in regions.values()),
                  'organizations': {k: len(v['members']) for k, v in organizations.items()},
                  'diagnostics': diagnostics,
                  'limits': ['No startup scripted effects are executed.',
                            'Population is the history-state starting population.',
                            'MD map geography is not a geodetically accurate Earth projection.',
                            'Organization budgets, votes, projects and economics are foundations only.']}
        (ROOT / 'data/import_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    import_world(Path(sys.argv[1]))
