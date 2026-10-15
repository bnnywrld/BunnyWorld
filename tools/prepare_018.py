"""Apply the bounded 0.1.8 UI assets and uniform base country statistics.

Usage: python tools/prepare_018.py MOD_ZIP ORGANIZATIONS_ZIP
Prepared assets are bundled; normal game export does not require these archives.
"""
from pathlib import Path
from zipfile import ZipFile
import argparse, collections, hashlib, io, json, re, xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'EU': 'Flag_of_Europe.svg.png', 'NATO': 'Flag_of_NATO.svg.png',
    'ASEAN': 'ASEAN_Flag.svg.png', 'ECOWAS': 'ECOWAS_logo.svg',
    'WTO': 'WTO_Logo.svg.png', 'CSTO': 'Emblem_of_the_Collective_Security_Treaty_Organization.svg',
    'OAU': 'Emblem_of_the_African_Union.svg', 'ARAB': 'Emblem_of_the_Arab_League.svg',
    'GCC': 'Emblem_GCC.svg', 'CIS': 'Emblem_of_CIS.svg', 'APEC': 'APEC_logo_vertical.svg',
    'OECD': 'OECD_logo_new.svg', 'OPEC': 'Organization_of_the_Petroleum_Exporting_Countries_Logo.svg',
    'MERCOSUR': 'Flag_of_Mercosur_Mercosul.svg', 'NAFTA': 'NAFTA_logo.svg',
    'OSCE': 'OSCE_logo.svg', 'IMF': 'IMF-Seal_ENG_RGB.svg',
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mod_zip', type=Path)
    parser.add_argument('organizations_zip', type=Path)
    args = parser.parse_args()
    world = json.loads((ROOT / 'data/world.json').read_text())
    with ZipFile(args.mod_zip) as archive:
        text = '\n'.join(archive.read(n).decode('utf-8-sig') for n in archive.namelist()
                         if '/common/defines/' in n and n.endswith('.lua'))
    defaults = {}
    for key, target in [('DEFAULT_STABILITY', 'stability'), ('DEFAULT_WAR_SUPPORT', 'war_support')]:
        matches = re.findall(r'^\s*NDefines\.NCountry\.' + key + r'\s*=\s*([\d.]+)', text, re.M)
        if len(matches) != 1:
            raise ValueError('Ambiguous mod default: ' + key)
        defaults[target] = float(matches[0])
    assert defaults == {'stability': .65, 'war_support': .5}
    # The user requested the same base values for every starting country.
    for collection in ['countries', 'country_registry']:
        for country in world[collection].values():
            country.setdefault('starting_stats', {}).update(defaults)
    world['base_country_stats'] = defaults
    restored = []
    with ZipFile(args.organizations_zip) as archive:
        for oid, filename in FILES.items():
            entries = [n for n in archive.namelist() if Path(n).name == filename]
            if len(entries) != 1:
                raise ValueError('Missing or ambiguous supplied logo: ' + filename)
            data = archive.read(entries[0])
            extension = '.svg' if filename.endswith('.svg') else '.png'
            path = ROOT / ('assets/organizations/supplied/' + oid + extension)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)  # Keep the supplied master bytes unchanged.
            world['organizations'][oid]['logo'] = 'res://' + path.relative_to(ROOT).as_posix()
            restored.append(oid)
    # The compact ASEAN badge views the supplied emblem at its original pixels;
    # the organization heading continues to show the complete supplied flag.
    asean = Image.open(ROOT / 'assets/organizations/supplied/ASEAN.png').convert('RGBA')
    pixels = np.asarray(asean)
    background = np.array(collections.Counter(map(tuple, pixels.reshape(-1, 4))).most_common(1)[0][0])
    foreground = np.any(np.abs(pixels[:, :, :3].astype(int) - background[:3]) > 5, axis=2)
    yy, xx = np.nonzero(foreground)
    side = int(np.ceil(max(xx.max() - xx.min() + 1, yy.max() - yy.min() + 1) * 1.12))
    x = int(round((xx.min() + xx.max() + 1 - side) / 2))
    y = int(round((yy.min() + yy.max() + 1 - side) / 2))
    assert x >= 0 and y >= 0 and x + side <= asean.width and y + side <= asean.height
    world['organizations']['ASEAN']['compact_icon_region'] = [x, y, side, side]
    report = {'version': '0.1.8', 'uniform_base_stats': defaults,
              'active_countries': len(world['countries']), 'country_registry': len(world['country_registry']),
              'restored_original_logos': restored, 'asean_original_size': list(asean.size),
              'asean_compact_region': [x, y, side, side],
              'mod_sha256': hashlib.sha256(args.mod_zip.read_bytes()).hexdigest()}
    for oid, organization in world['organizations'].items():
        asset = ROOT / organization['logo'][6:]
        preset = asset.with_name(asset.name + '.import')
        content = preset.read_text()
        content = content.replace('mipmaps/generate=false', 'mipmaps/generate=true')
        content = re.sub(r'detect_3d/compress_to=\d+', 'detect_3d/compress_to=0', content)
        if asset.suffix == '.svg':
            svg = ET.fromstring(asset.read_bytes())
            box = list(map(float, re.split(r'[ ,]+', svg.get('viewBox', '').strip()))) if svg.get('viewBox') else []
            width = float(re.match(r'[\d.]+', svg.get('width', str(box[2] if box else 256)))[0])
            height = float(re.match(r'[\d.]+', svg.get('height', str(box[3] if box else 256)))[0])
            scale = 768.0 / max(width, height)
            content = re.sub(r'svg/scale=[\d.]+', 'svg/scale=' + str(scale), content)
        preset.write_text(content)
    (ROOT / 'data/world.json').write_text(json.dumps(world, ensure_ascii=False, separators=(',', ':')))
    (ROOT / 'data/update_018_report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PREPARE_018_PASS', report)

if __name__ == '__main__':
    main()
