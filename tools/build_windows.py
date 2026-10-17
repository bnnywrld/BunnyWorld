"""Export the source project with an installed Godot 4.5.1 editor."""
import argparse
import json
from pathlib import Path
import struct
import subprocess

def validate_external_launcher(path):
    """An external-pack launcher must not contain an older embedded game."""
    path = Path(path)
    with path.open('rb') as f:
        f.seek(0, 2)
        size = f.tell()
        if size < 64:
            raise ValueError(f'Invalid Windows executable: {path}')
        f.seek(size - 12)
        if f.read(12)[-4:] == b'GDPC':
            raise ValueError(f'Embedded game pack in {path}; use a clean official Godot export template.')
        f.seek(0)
        header = f.read(64)
        if header[:2] != b'MZ':
            raise ValueError(f'Invalid Windows executable: {path}')
        pe_offset = struct.unpack_from('<I', header, 60)[0]
        f.seek(pe_offset)
        pe = f.read(24)
        if len(pe) != 24 or pe[:4] != b'PE\0\0':
            raise ValueError(f'Invalid PE header: {path}')
        section_count = struct.unpack_from('<H', pe, 6)[0]
        optional_size = struct.unpack_from('<H', pe, 20)[0]
        f.seek(pe_offset + 24 + optional_size)
        sections = f.read(40 * section_count)
        if len(sections) != 40 * section_count:
            raise ValueError(f'Truncated PE section table: {path}')
        for offset in range(0, len(sections), 40):
            name = sections[offset:offset + 8].rstrip(b'\0')
            raw_size, raw_offset = struct.unpack_from('<II', sections, offset + 16)
            if raw_offset + raw_size > size:
                raise ValueError(f'Truncated PE section {name!r}: {path}')
            if name in (b'pck', b'.pck') and raw_size:
                f.seek(raw_offset)
                # The official template reserves a zero-filled section. An
                # exported game changes that section to the embedded PCK.
                data = f.read(raw_size)
                if data.strip(b'\0'):
                    raise ValueError(f'Embedded game in PE pack section: {path}')


def validate_embedded_launcher(path):
    """Check the actual executable's embedded pack, including its PE location."""
    path = Path(path)
    with path.open('rb') as f:
        f.seek(0, 2)
        size = f.tell()
        if size < 64:
            raise ValueError(f'Invalid executable: {path}')
        f.seek(size - 12)
        footer = f.read(12)
        if footer[-4:] != b'GDPC':
            raise ValueError(f'Missing embedded game footer: {path}')
        pack_size = struct.unpack_from('<Q', footer)[0]
        pack_start = size - 12 - pack_size
        if pack_start < 64:
            raise ValueError(f'Invalid embedded game offset: {path}')
        f.seek(pack_start)
        pack_header = f.read(40)
        if pack_header[:4] != b'GDPC' or struct.unpack_from('<I', pack_header, 4)[0] != 3:
            raise ValueError(f'Invalid embedded pack header: {path}')
        directory = pack_start + struct.unpack_from('<Q', pack_header, 32)[0]
        if directory < pack_start + 112 or directory >= size - 12:
            raise ValueError(f'Invalid embedded pack directory: {path}')
        f.seek(directory)
        count = struct.unpack('<I', f.read(4))[0]
        if count < 100:
            raise ValueError(f'Embedded pack has unexpectedly few resources: {path}')
        f.seek(0)
        dos = f.read(64)
        if dos[:2] != b'MZ':
            raise ValueError(f'Invalid Windows executable: {path}')
        pe_offset = struct.unpack_from('<I', dos, 60)[0]
        f.seek(pe_offset)
        pe = f.read(24)
        if pe[:4] != b'PE\0\0':
            raise ValueError(f'Invalid Windows PE header: {path}')
        section_count = struct.unpack_from('<H', pe, 6)[0]
        optional_size = struct.unpack_from('<H', pe, 20)[0]
        f.seek(pe_offset + 24 + optional_size)
        sections = f.read(40 * section_count)
        pack_section = False
        for offset in range(0, len(sections), 40):
            name = sections[offset:offset + 8].rstrip(b'\0')
            if name in (b'pck', b'.pck'):
                raw_size, raw_offset = struct.unpack_from('<II', sections, offset + 16)
                if raw_offset == pack_start and raw_size == pack_size + 12:
                    pack_section = True
        if not pack_section:
            raise ValueError(f'Windows PE pack section disagrees with embedded game: {path}')
    return {'pack_offset': pack_start, 'pack_bytes': pack_size, 'pack_entries': count}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--godot', required=True, help='Path to the Godot editor executable')
    p.add_argument('--template', help='Optional clean official Windows x64 release template')
    p.add_argument('--output', required=True, help='Destination executable')
    p.add_argument('--embed-pck', action='store_true', help='Embed this export in the executable instead of using an external pack')
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    preset = root / 'export_presets.cfg'
    original = preset.read_text()
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if args.template:
        validate_external_launcher(args.template)
    try:
        configured = original
        if args.template:
            template = Path(args.template).resolve().as_posix()
            configured = configured.replace('custom_template/release=""', 'custom_template/release=' + json.dumps(template))
        if args.embed_pck:
            configured = configured.replace('binary_format/embed_pck=false', 'binary_format/embed_pck=true')
        embedded = 'binary_format/embed_pck=true' in configured
        preset.write_text(configured)
        subprocess.run([args.godot, '--headless', '--path', str(root), '--editor', '--import'], check=True)
        subprocess.run([args.godot, '--headless', '--path', str(root), '--export-release', 'Windows Desktop', str(output)], check=True)
        if embedded:
            print(validate_embedded_launcher(output))
            info = json.loads((root / 'BUILD_INFO.json').read_text())
            world = json.loads((root / 'data/world.json').read_text())
            subprocess.run([args.godot, '--headless', '--main-pack', str(output), '--script', str(root / 'tests/export_pack_version_tests.gd'), '--', '--expected-version=' + info['version'], '--expected-scenario=' + world['scenario_id']], check=True)
        else:
            validate_external_launcher(output)
            pack = output.with_suffix('.pck')
            with pack.open('rb') as f:
                if f.read(4) != b'GDPC':
                    raise ValueError(f'Invalid external game pack: {pack}')
    finally:
        preset.write_text(original)
    print(output)


if __name__ == '__main__':
    main()
