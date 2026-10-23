"""Import names and research graph from the supplied MD archive, never effects.

Uses the modern NSB/BBA/Gotterdammerung branches. Supported country-history
conditions are DLC, country tag, date and boolean combinations; unknown script
conditions are skipped and counted, rather than executed or guessed.
"""
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from import_md import Block, parse, at_start, clean_name

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = {'civilian_folder': 'Industry', 'electronics_folder': 'Electronics',
           'infantry_folder': 'Infantry', 'nsb_armour_folder': 'Armor',
           'artillery_folder': 'Artillery', 'bba_aircraft_folder': 'Aircraft',
           'air_techs_folder': 'Helicopters', 'naval_folder': 'Naval',
           'naval_module_folder': 'Naval systems', 'cruise_missiles_folder': 'Missiles',
           'space_folder': 'Space'}
LEGACY = {'armor.txt', 'anti_air.txt', 'artillery.txt', 'fixed_wing.txt',
          'bombers.txt', 'non_got_missiles.txt'}


def condition(b, tag=''):
    results = []
    for key, op, value in b.items:
        if key in ('AND', 'ROOT', 'limit') and isinstance(value, Block):
            result = condition(value, tag)
        elif key in ('NOT', 'OR') and isinstance(value, Block):
            parts = [condition(Block([item]), tag) for item in value.items]
            if key == 'NOT':
                result = None if None in parts else not all(parts)
            else:
                result = True if True in parts else (None if None in parts else False)
        elif key == 'has_dlc': result = True
        elif key == 'always': result = value == 'yes'
        elif key in ('tag', 'original_tag'): result = value == tag if tag else None
        elif key == 'date':
            date = tuple(int(v) for v in value.split('.')[:3])
            result = {'<': (2000, 1, 1) < date, '>': (2000, 1, 1) > date,
                      '=': (2000, 1, 1) == date, '>=': (2000, 1, 1) >= date,
                      '<=': (2000, 1, 1) <= date}[op]
        else: result = None
        results.append(result)
    return False if False in results else (None if None in results else True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('archive', type=Path)
    args = ap.parse_args()
    techs, raw_defs, loc, hashes = {}, {}, {}, {}
    skipped_conditions = 0
    with zipfile.ZipFile(args.archive) as z:
        names = z.namelist()
        for path in sorted(names, key=lambda n: ('/replace/' in n, n)):
            if '/localisation/english/' in path and path.endswith('.yml'):
                for line in z.read(path).decode('utf-8-sig').splitlines():
                    m = re.match(r'^\s*([\w.-]+):\d*\s*"((?:\\.|[^"\\])*)"', line)
                    if m: loc[m[1]] = m[2].replace('\\"', '"').replace('\\n', ' ')
        for path in sorted(names):
            if '/common/technologies/' not in path or not path.endswith('.txt'): continue
            if Path(path).name in LEGACY: continue
            raw = z.read(path)
            hashes[path] = hashlib.sha256(raw).hexdigest()
            container = parse(raw.decode('utf-8-sig')).get('technologies')
            variables = {k: v for k, _, v in container.items if k and k.startswith('@')}
            for key, _, b in container.items:
                if not isinstance(b, Block): continue
                raw_defs[key] = b
                folders = [f for f in b.values('folder') if f.get('name') in FOLDERS]
                if not folders: continue
                branch = b.get('allow_branch')
                if isinstance(branch, Block) and condition(branch) is False: continue
                folder = folders[0]
                pos = folder.get('position', Block([]))
                def number(value): return float(variables.get(value, value))
                year = int(b.get('start_year', 2000))
                # Special-project placeholders use years 0/1/2; keep them beside
                # their prerequisites rather than presenting them as ancient tech.
                techs[key] = {'name': clean_name(loc.get(key, key.replace('_', ' ').title()), loc),
                              'category': FOLDERS[folder.get('name')],
                              'year': year if year > 1900 else 2000,
                              'days': float(b.get('research_cost', 1)) * 250,
                              'x': number(pos.get('x', 0)), 'y': number(pos.get('y', 0)),
                              'parents': [], 'dependencies': [], 'exclusive': []}
        for key, t in techs.items():
            b = raw_defs[key]
            for p in b.values('path'):
                target = p.get('leads_to_tech')
                # This archive's nsb_drone_artillery_ammo_3 points to itself.
                # A self arrow is not a prerequisite and cannot be researched.
                if target in techs and target != key: techs[target]['parents'].append(key)
            deps = b.get('dependencies', Block([]))
            t['dependencies'] = [k for k, _, v in deps.items if k in techs]
            exclusive = b.get('mutually_exclusive', Block([]))
            t['exclusive'] = [v for v in exclusive.scalars() if v in techs]
        starts = {}
        world = json.loads((ROOT / 'data/world.json').read_text(encoding='utf-8'))
        for path in sorted(names):
            m = re.search(r'/history/countries/([A-Z0-9]{3})\b', path)
            if not m or not path.endswith('.txt'): continue
            tag = m[1]
            if tag not in world['countries']: continue
            hashes[path] = hashlib.sha256(z.read(path)).hexdigest()
            known = {}
            def history(b):
                nonlocal skipped_conditions
                previous = False
                for key, _, v in at_start(b):
                    if key == 'set_technology' and isinstance(v, Block):
                        for tech, _, level in v.items:
                            if tech in techs: known[tech] = float(level) > 0
                    elif key in ('if', 'else_if', 'else') and isinstance(v, Block):
                        if key == 'if': previous = False
                        if previous is True or previous is None: continue
                        result = condition(v.get('limit', Block([])), tag)
                        if result is None:
                            skipped_conditions += 1
                            previous = None
                        elif result:
                            history(v)
                            previous = True
            history(parse(z.read(path).decode('utf-8-sig')))
            starts[tag] = sorted(k for k, yes in known.items() if yes)
        defines = next(n for n in names if n.endswith('/common/defines/MD_defines.lua'))
        text = z.read(defines).decode('utf-8-sig')
        base = float(re.search(r'NTechnology.BASE_TECH_COST\s*=\s*([\d.]+)', text)[1])
        ahead = float(re.search(r'NTechnology.BASE_YEAR_AHEAD_PENALTY_FACTOR\s*=\s*([\d.]+)', text)[1])
        assert base == 250
        hashes[defines] = hashlib.sha256(z.read(defines)).hexdigest()
    # Enforce dependency and chronological order, including same-year branches.
    visiting, done = set(), set()
    def depth(key):
        if key in done: return techs[key]['row']
        if key in visiting: raise ValueError('Cyclic technology graph: ' + key)
        visiting.add(key)
        t = techs[key]
        parents = t['parents'] + t['dependencies']
        t['row'] = max([t['year']] + [depth(p) + 1 for p in parents])
        visiting.remove(key); done.add(key)
        return t['row']
    for key in techs: depth(key)
    data = {'source': {'archive': args.archive.name, 'files': hashes,
                       'policy': 'Modern DLC branches; visible technologies only. No effects, focus, special-project or doctrine gates. Country history through 2000-01-01; supported boolean/DLC/tag/date conditions only.',
                       'skipped_history_conditions': skipped_conditions},
            'base_days': base, 'ahead_factor': ahead,
            'categories': [v for v in FOLDERS.values() if any(t['category'] == v for t in techs.values())],
            'technologies': techs, 'countries': {tag: starts.get(tag, []) for tag in world['countries']}}
    (ROOT / 'data/research.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(len(techs), 'technologies;', len(data['categories']), 'categories;', len(data['countries']), 'countries;', skipped_conditions, 'unsupported history conditions skipped')


if __name__ == '__main__': main()
