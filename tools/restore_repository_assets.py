"""Restore byte-identical prepared assets stored compressed for GitHub's upload API."""
import argparse
import hashlib
import json
from pathlib import Path
import zlib


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--force', action='store_true', help='Replace a modified generated asset')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'ASSET_RESTORE.json').read_text())
    for item in manifest['files']:
        target = root / item['path']
        archives = item['parts']
        if target.is_file():
            if digest(target.read_bytes()) == item['sha256']:
                print('Verified:', item['path'])
                continue
            if not args.force:
                raise SystemExit('Existing asset differs: ' + item['path'] + '. Preserve changes before using --force.')
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
    print('Prepared repository assets are ready. Open project.godot with Godot 4.5.1 stable.')


if __name__ == '__main__':
    main()
