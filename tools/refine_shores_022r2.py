"""Keep broad ETOPO relief while eliminating the artificial coastal plateau."""
from pathlib import Path
import json,hashlib
import numpy as np
from scipy.ndimage import distance_transform_edt
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography'
Image.MAX_IMAGE_PIXELS=None
SCALE=.008;LIFT=.0000125;EXAGGERATION=4.;RADIUS=6371000.
meters=np.load(SRC/'etopo_021.npz')['meters'].astype(np.float32)
atlas=np.load(SRC/'grouped_atlas_022r2.npz')['regions']
land=atlas[1::2,1::2]>0
distance=distance_transform_edt(land).astype(np.float32)
amount=np.clip((distance-.5)/4.0,0,1)
feather=amount*amount*(3-2*amount)
altitude=np.maximum(meters,0)
height=(LIFT+np.minimum(altitude,9000)*EXAGGERATION/RADIUS)*feather
height[~land]=0
packed=np.rint(height/SCALE*65535).astype('<u2')
rgb=np.stack([(packed&255).astype(np.uint8),(packed>>8).astype(np.uint8),np.clip(altitude/9000*255,0,255).astype(np.uint8),np.rint(feather*255).astype(np.uint8)],-1)
Image.fromarray(rgb).save(ROOT/'assets/relief_data.png',optimize=True)
(ROOT/'assets/relief_data.bin').write_bytes(packed.tobytes())
report=json.load(open(ROOT/'data/relief.json'))
report.update({'land_lift':LIFT,'land_lift_meters':LIFT*RADIUS,'coastal_feather':'Smoothstep from half a prepared pixel to 4.5 pixels inland; water retains zero displacement.','maximum_displacement':float(height.max()),'land_geometry':'Lower gentle land lift and smooth shoreline taper; accepted geographic land/lake mask retained.','revision':'0.1.12-r2'})
(ROOT/'data/relief.json').write_text(json.dumps(report,indent=2))
edge=(distance>=1)&(distance<1.1)&land
assert height[~land].max(initial=0)==0
assert float(height[edge].max())<.0005
assert LIFT*RADIUS<100
print('SHORES_022R2_PASS',{'lift_meters':LIFT*RADIUS,'shore_maximum_displacement':float(height[edge].max()),'maximum_displacement':float(height.max())},flush=True)
