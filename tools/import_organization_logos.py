"""Import supplied organization logos: SVG kept vector, raster kept lossless.
Usage: python tools/import_organization_logos.py FOLDER
Filenames use organization IDs such as NATO.svg, ASEAN.png or EU.webp.
"""
from pathlib import Path
import json,sys,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];source=Path(sys.argv[1]);world=json.loads((ROOT/'data/world.json').read_text());converted=[]
for oid,o in world['organizations'].items():
    found=next((source/(oid+ext) for ext in ['.svg','.png','.webp','.jpg','.jpeg'] if (source/(oid+ext)).is_file()),None)
    if found is None:continue
    folder=ROOT/'assets/organizations/supplied';folder.mkdir(exist_ok=True)
    if found.suffix=='.svg':
        dst=folder/(oid+'.svg');shutil.copyfile(found,dst)
    else:
        dst=folder/(oid+'.png');im=Image.open(found).convert('RGBA');im.save(dst,optimize=True)
    # A new supplied flag may have a different composition from the compact
    # crop prepared for the original ASEAN flag.
    o.pop('compact_icon_region',None)
    o['logo']='res://'+dst.relative_to(ROOT).as_posix();converted.append(oid)
(ROOT/'data/world.json').write_text(json.dumps(world,ensure_ascii=False,separators=(',',':')));print('Supplied logos imported:',', '.join(converted))
