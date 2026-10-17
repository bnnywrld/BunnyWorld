"""Current-country MD count and naming audit, with approved unions as constraints.
No speculative border edits: candidates are an actionable next geography pass.
"""
from pathlib import Path
from collections import Counter
import csv, hashlib, json, re, zipfile

R = Path(__file__).resolve().parents[1]
def main():
    w = json.loads((R / 'data/world.json').read_text())
    md = json.loads((R / 'data/md_geography_reference.json').read_text())
    archive = R.parent / 'project_sources/04-bunnyversion.zip'
    verified = None
    if archive.exists():
        with zipfile.ZipFile(archive) as z:
            definition = next(n for n in z.namelist() if n.endswith('map/definition.csv'))
            prefix = definition[:-len('map/definition.csv')]
            digest = hashlib.sha256()
            for n in sorted(z.namelist()):
                if n.startswith(prefix + 'history/states/') and n.endswith('.txt'): digest.update(z.read(n))
            verified = digest.hexdigest() == md['state_history_sha256'] and hashlib.sha256(z.read(definition)).hexdigest() == md['definition_sha256']
        assert verified, 'Bundled MD reference differs from supplied archive; refresh reference first'
    constraints = {
        'MIC': 'User explicitly requires ONE Micronesia state including Palau; do not split it to meet raw MD count.',
        'PAP': 'User explicitly requires FOUR states after mainland mergers: Southern Papua, Northern Papua, Bismarck Archipelago and Bougainville.',
        'USA': 'Keep Rota/Saipan/Tinian in Mariana Islands, Midway/Johnston in Hawaii, and Navassa removed. Any additional states must represent meaningful inhabited regions.',
        'NZL': 'Keep one South Island state and the approved island unions.',
        'GRN': 'Keep Hans Island integrated and earlier user-approved Greenland unions.',
        'GER': 'Keep Free Hanseatic Bremen integrated as requested.',
        'ENG': 'Keep Rockall integrated as requested.',
        'TAI': 'Keep Pratas/Spratly consolidations; add useful inhabited subdivisions instead of recreating reef states.',
        'SPR': 'Keep approved tiny enclave/island unions; consider meaningful mainland regions.',
        'WAA': 'Keep the approved Yunnan/Wa State consolidation.',
    }
    candidates = {
        'PHI': 'Prioritize Metro Manila, Cordillera, Ilocos, Cagayan, Bicol, Calabarzon, Central Visayas, Mindoro, Palawan, Caraga, Davao and Bangsamoro. Respect the approved Western/Northern Mindanao union; omit reef-only replacements. Check actual source geometry before deciding twelve additions.',
        'CHI': 'Review Pearl River Delta, Nanjing, Liaoxi, Songjiang, Hulunbuir, Shandong Peninsula, Northern Hebei and Western Sichuan as candidate population/economic regions. Preserve current country control and approved Xinjiang/Tibet unions.',
        'SYR': 'Use governorate/settlement regions around Aleppo, Idlib, Hama, Homs, Latakia, Daraa and As-Suwayda to replace broad unions; validate the footprint rather than copying MD straight boundaries.',
        'RAJ': 'Prioritize missing Awadh/Purvanchal and important urban/economic regions such as Mumbai/Vidarbha/Rayalaseema. Keep user-approved Karnataka, Chandigarh and other mergers.',
        'TAI': 'Review Taipei, Hsinchu, Taichung, Tainan, Kaohsiung and Hualien as inhabited mainland subdivisions, with Lienchiang considered from existing geography. Do not recreate Pratas or other reef-only states.',
        'PAK': 'Review Malakand, northern/central/southern Punjab and the Pashto-speaking Balochistan region. Check tribal-area overlaps to avoid duplicates.',
        'MOR': 'Review Fes-Meknes, Rabat-Sale-Kenitra, Tanger-Tetouan-Al Hoceima, Marrakesh-Safi and Draa-Tafilalet. Current slash-separated unions need geographic validation before naming or division.',
        'COL': 'Review Pacifico, Caribe, Antioquia, Santander and Amazonia against current mixed departmental unions; retain removed island states as removed.',
    }
    rows, names = [], []
    directional = re.compile(r'\b(north(?:east|west)?(?:ern)?|south(?:east|west)?(?:ern)?|east(?:ern)?|west(?:ern)?|central)\b', re.I)
    norm = lambda name: re.sub(r'[^\w]', '', name.casefold())
    for tag, c in sorted(w['countries'].items(), key=lambda t: t[1]['name']):
        states = sorted((s for s in w['regions'].values() if s['owner'] == tag), key=lambda s: s['name'])
        ref = md['countries'].get(tag)
        count = ref['states'] if ref else None
        shortfall = max(0, count - len(states)) if count is not None else None
        row = {'tag': tag, 'country': c['name'], 'current_states': len(states), 'md_states': count,
               'shortfall': shortfall, 'target_minimum': 1 if tag == 'MIC' else 4 if tag == 'PAP' else count,
               'constraint': constraints.get(tag, ''),
               'current_names': [s['name'] for s in states],
               'md_names': [md['states'][str(i)]['name'] for i in ref['state_ids']] if ref else [],
               'next_action': candidates.get(tag, 'Review missing meaningful regional divisions against MD names and geographic source; retain all explicitly approved mergers.' if shortfall else 'Review names if flagged; no count increase required.')}
        rows.append(row)
        for s in states:
            reason = []
            official = {norm(name) for name in s.get('geographic_divisions', [])} | {norm(c['name'])}
            if directional.search(s['name']) and norm(s['name']) not in official: reason.append('directional regional name; acceptable when the footprint is broad')
            if '/' in s['name']: reason.append('joined names; review for a coherent regional label')
            if s['name'].count('—') and len(set(part.strip() for part in s['name'].split('—'))) < len(s['name'].split('—')): reason.append('repeated administrative name')
            if s['name'].startswith('Near '): reason.append('descriptive placeholder; verify local toponym')
            if reason:
                names.append({'state': s['id'], 'country': c['name'], 'tag': tag, 'name': s['name'], 'population': s['population'], 'source_divisions': s.get('geographic_divisions', []), 'review_reason': '; '.join(reason), 'action': 'Validate a historical/regional name against the actual footprint; keep a directional name if it describes a broad union accurately.'})
    deficits = sorted((row for row in rows if row['shortfall']), key=lambda row: (-row['shortfall'], row['country']))
    result = {'version': w['version'], 'md_epoch': md['epoch'], 'source_archive': md['source_archive'],
              'source_state_sha256': md['state_history_sha256'], 'source_definition_sha256': md['definition_sha256'],
              'supplied_md_archive_verified': verified, 'md_total_states': md['state_count'],
              'current_total_states': len(w['regions']), 'countries_below_raw_md': len(deficits),
              'raw_country_shortfall_sum': sum(row['shortfall'] for row in deficits),
              'important_note': 'Raw country deficits are not the global net difference. MD uses different ownership and territory grouping. Explicit Micronesia/Papua reductions override a literal MD minimum; other approved unions must not be reversed to fill a numeric quota.',
              'countries': rows, 'naming_review': names}
    out = R / 'documentation/state_audit_0225'; out.mkdir(parents=True, exist_ok=True)
    (out / 'audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    with (out / 'country_counts.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['tag', 'country', 'current_states', 'md_states', 'shortfall', 'target_minimum', 'constraint', 'next_action'])
        writer.writeheader(); writer.writerows({k: row[k] for k in writer.fieldnames} for row in rows)
    lines = ['# State count and naming audit — 0.2.0.25', '',
             f"Bundled MD reference: **{md['state_count']} states** at 1 January 2000. Current BunnyWorld: **{len(w['regions'])} states**.",
             f"**{len(deficits)} countries** are below their raw MD counts, with **{sum(row['shortfall'] for row in deficits)} states** of combined country shortfalls. These are not the global net difference: other countries have more states, and ownership/territory grouping differs.", '',
             'The supplied MD archive matches the bundled state-history and province-definition checksums.' if verified else 'Counts use the checksum-recorded bundled MD reference.', '',
             'The user-approved single Micronesia state and four Papuan states remain explicit exceptions. Other requested island/state unions stay intact; useful inhabited regions should receive additional detail instead of recreating discarded islands.', '',
             '| Country | Current | MD | Shortfall |', '| --- | ---: | ---: | ---: |']
    lines += [f"| {row['country']} ({row['tag']}) | {row['current_states']} | {row['md_states']} | {row['shortfall']} |" for row in deficits]
    lines += ['', '## First geography passes', '', '1. Philippines: the largest shortfall; split meaningful inhabited regions while preserving approved Mindanao and reef unions.', '2. China and Syria: major economic/administrative regions and recognizable governorate names.', '3. Taiwan, India, Pakistan, Morocco and Colombia: prioritize inhabited regions and poorly named mixed unions.', '4. Remaining countries: review the complete country table, ownership differences and approved mergers before changing geography.', '', 'Counts are targets, not instructions to copy MD polygon geometry. Each approved split should reuse current province footprints where appropriate, preserve country totals, update capitals and references, and pass the shared map build.', '', '## Regional candidates and constraints', '']
    for row in deficits:
        lines += [f"### {row['country']}", '', row['next_action'], '', 'Current: ' + '; '.join(row['current_names']) + '.', '', 'MD reference: ' + '; '.join(row['md_names']) + '.', '']
        if row['constraint']: lines += [row['constraint'], '']
    lines += ['## Naming review', '', f'{len(names)} names are flagged for review. A directional name is not automatically wrong. These are proposals for a separate geography/name pass; no blanket automatic renaming was applied.', '', '| Country | State ID | Current name | Review reason |', '| --- | ---: | --- | --- |']
    lines += [f"| {row['country']} | {row['state']} | {row['name'].replace('|', '/')} | {row['review_reason']} |" for row in names]
    (out / 'AUDIT.md').write_text('\n'.join(lines) + '\n')
    print('STATE_AUDIT_READY', len(deficits), 'countries below raw MD;', sum(row['shortfall'] for row in deficits), 'shortfall;', len(names), 'naming flags; source verified', verified)

if __name__ == '__main__': main()
