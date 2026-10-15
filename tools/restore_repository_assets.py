"""Restore byte-identical prepared assets stored compressed for GitHub's upload API."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import zlib


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--force', action='store_true', help='Replace a modified generated asset')
    parser.add_argument('--verify-only', action='store_true', help='Check prepared files without changing them')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'ASSET_RESTORE.json').read_text())
    for item in manifest['files']:
        target = root / item['path']
        archives = item['parts']
        if target.is_file():
            existing_hash = digest(target.read_bytes())
            if existing_hash == item['sha256']:
                print('Verified:', item['path'])
                continue
            if args.verify_only:
                raise SystemExit('Outdated prepared asset: ' + item['path'])
            if not args.force and existing_hash not in item.get('previous_sha256', []):
                raise SystemExit('Existing asset differs: ' + item['path'] + '. Preserve changes before using --force.')
        if args.verify_only:
            raise SystemExit('Missing prepared asset: ' + item['path'])
        buffers = []
        for part in archives:
            data = (root / part['path']).read_bytes()
            if len(data) != part['bytes'] or digest(data) != part['sha256']:
                raise SystemExit('Asset part checksum mismatch: ' + part['path'])
            buffers.append(data)
        compressed = b''.join(buffers)
        data = zlib.decompress(compressed)
        if len(data) != item['bytes'] or digest(data) != item['sha256']:
            raise SystemExit('Restored asset checksum mismatch: ' + item['path'])
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + '.restore-tmp')
        temporary.write_bytes(data)
        temporary.replace(target)
        print('Restored:', item['path'])
    bundle_path = root / 'data/geography_bundle.json'
    if bundle_path.is_file():
        bundle = json.loads(bundle_path.read_text())
        project_version = re.search(r'^\s*config/version\s*=\s*"([^"]+)"', (root / 'project.godot').read_text(), re.M)
        if not project_version or project_version.group(1) != bundle['version']:
            raise SystemExit('Project version differs from the geography bundle. Finish pulling the update before opening Godot.')
        for name, expected in bundle['files'].items():
            path = root / name
            if not path.is_file() or digest(path.read_bytes()) != expected:
                raise SystemExit('Geography bundle mismatch: ' + name + '. Finish pulling the update, close Godot, then run preparation again.')
        print('Geography bundle verified:', bundle['version'])
    print('Prepared repository assets are ready for ' + manifest['version'] + '. Open project.godot with Godot 4.5.1 stable.')


if __name__ == '__main__':
    main()
