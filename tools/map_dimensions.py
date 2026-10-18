"""Current authoritative ID-map layout, shared by active build tools."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
CONFIG=json.loads((ROOT/'data/world.json').read_text())['map']
W,H=int(CONFIG['width']),int(CONFIG['height'])
SCALE=W/16384.0
PATHS=[CONFIG.get('province_ids','assets/province_ids.png')]if int(CONFIG['tiles'])==1 else [f'assets/region_ids_{i}.png'for i in range(4)]
