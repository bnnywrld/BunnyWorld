"""Validate current asset packs; --prune removes only unreferenced pack files."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[1]


def check(root=ROOT, prune=False):
    manifest = json.loads((root / 'ASSET_RESTORE.json').read_text())
    expected = set()
    # Validate every active pack and decoded asset before permitting deletion.
    for item in manifest['files']:
        decoder = zlib.decompressobj()
        digest = hashlib.sha256()
        size = 0
        for part in item['parts']:
            name = part['path']
            path = Path(name)
            if path.parent.as_posix() != 'repository_assets' or not re.fullmatch(r'[0-9a-f]{64}\.zlib\.part[0-9]{3}', path.name):
                raise ValueError('Invalid pack path: ' + name)
            data = (root / path).read_bytes()
            if len(data) != part['bytes'] or hashlib.sha256(data).hexdigest() != part['sha256']:
                raise ValueError('Damaged active pack: ' + name)
            expected.add(name)
            raw = decoder.decompress(data)
            digest.update(raw)
            size += len(raw)
        raw = decoder.flush()
        digest.update(raw)
        size += len(raw)
        if not decoder.eof or decoder.unused_data or size != item['bytes'] or digest.hexdigest() != item['sha256']:
            raise ValueError('Damaged restored asset: ' + item['path'])
    extras = sorted(p for p in (root / 'repository_assets').glob('*.zlib.part*')
                    if re.fullmatch(r'[0-9a-f]{64}\.zlib\.part[0-9]{3}', p.name) and p.relative_to(root).as_posix() not in expected)
    wasted = sum(p.stat().st_size for p in extras)
    if prune:
        for path in extras:
            path.unlink()
    print(f'{len(expected)} active parts verified; {len(extras)} unused parts; {wasted:,} bytes ' + ('removed' if prune else 'unused'))
    if extras and not prune:
        raise ValueError('Run python tools/repository_hygiene.py --prune before committing.')
    return len(extras), wasted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prune', action='store_true')
    args = parser.parse_args()
    check(prune=args.prune)
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    forbidden = [p for p in tracked if p and (
        '.godot' in Path(p).parts or '__pycache__' in Path(p).parts
        or p.endswith(('.exe', '.pck', '.pyc', '.translation'))
        or (p.endswith('.zip') and not p.startswith('tools/cartography/'))
        or Path(p).name.startswith(('PATCH_MANIFEST', 'PATCH_REMOVED_FILES', 'APPLY_')))]
    if forbidden:
        raise SystemExit('Unnecessary tracked outputs:\n' + '\n'.join(forbidden))
    print('REPOSITORY_HYGIENE_PASS')


if __name__ == '__main__':
    main()
