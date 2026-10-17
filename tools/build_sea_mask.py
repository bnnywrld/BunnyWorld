"""Prepare an exact GPU ocean mask; CPU selection retains full sea IDs."""
from pathlib import Path
import hashlib
import json
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]


def build():
    import numpy as np
    from PIL import Image
    source = ROOT / 'assets/sea_ids.png'
    output = ROOT / 'assets/display/sea_mask.bwd'
    metadata = output.with_suffix('.json')
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    if output.exists() and metadata.exists():
        old = json.loads(metadata.read_text())
        if old.get('source_sha256') == source_hash and old.get('sha256') == hashlib.sha256(output.read_bytes()).hexdigest():
            return old
    rgb = np.asarray(Image.open(source).convert('RGB'))
    # Match ocean_sample's exact predicate: either ID byte is nonzero.
    mask = ((rgb[:, :, 0] != 0) | (rgb[:, :, 1] != 0)).astype(np.uint8) * 255
    height, width = mask.shape
    data = struct.pack('<II', width, height) + zlib.compress(mask.tobytes(), 9)
    temporary = output.with_suffix('.bwd.prepare-tmp')
    temporary.write_bytes(data)
    temporary.replace(output)
    info = {'schema':1, 'format':'R8', 'width':width, 'height':height, 'source':'assets/sea_ids.png', 'source_sha256':source_hash, 'sha256':hashlib.sha256(data).hexdigest(), 'decoded_bytes':mask.nbytes, 'predicate':'R != 0 or G != 0; nearest sampling at original resolution'}
    metadata.write_text(json.dumps(info, indent=2)+'\n')
    return info


def check():
    output = ROOT / 'assets/display/sea_mask.bwd'
    info = json.loads(output.with_suffix('.json').read_text())
    assert hashlib.sha256((ROOT/info['source']).read_bytes()).hexdigest() == info['source_sha256'], 'Sea IDs changed; rebuild the GPU sea mask.'
    assert hashlib.sha256(output.read_bytes()).hexdigest() == info['sha256'], 'GPU sea mask differs from its contract.'


if __name__ == '__main__':
    print(json.dumps(build(), indent=2))
