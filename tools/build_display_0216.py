"""Replace only affected selection fields; preserve all other prepared tiles."""
from pathlib import Path
import json,io,zlib
import numpy as np
from build_display_0215 import field
R=Path(__file__).resolve().parents[1];B=R.parent/'baseline_0215/assets/display'
index=json.loads((B/'selection_distance.json').read_text());old=(B/'selection_distance.bwd').read_bytes();a=np.load(R/'tools/cartography/province_atlas_0216.npz')['provinces'];w=json.loads((R/'data/world.json').read_text());ps=json.loads((R/'data/provinces.json').read_text());pack=io.BytesIO()
index['states'].pop('254');index['provinces'].pop('3097');index['version']='0.2.0.16'
for scope in ['states','provinces','seas']:
 for key,r in index[scope].items():
  if (scope=='states'and key in ['253','1813'])or(scope=='provinces'and key=='3096'):
   ids=w['regions'][key]['provinces']if scope=='states'else[int(key)];mask=np.isin(a,ids);yy,xx=np.nonzero(mask);t,l=int(yy.min()),int(xx.min());part=mask[t:int(yy.max())+1,l:int(xx.max())+1];rect,data=field(part,t+.5,l+.5,1536 if scope=='states' else 1024);blob=zlib.compress(data.tobytes(),6);record=rect+[pack.tell(),len(blob),data.shape[1],data.shape[0]]
  else:blob=old[r[4]:r[4]+r[5]];record=[(r[0]+.5/16384)%1,r[1]+.5/8192,r[2],r[3],pack.tell(),len(blob),r[6],r[7]]
  index[scope][key]=record;pack.write(blob)
b=pack.getvalue();(R/'assets/display/selection_distance.bwd').write_bytes(b);(R/'assets/display/selection_distance.json').write_text(json.dumps(index,separators=(',',':')))
# Retire local coast windows tied to the old buffer-zone shape. The combined
# State uses the global smooth coast until a matching local window is prepared.
local=json.loads((R/'assets/display/local_coasts.json').read_text())
for scope,key in [('states','254'),('provinces','3097'),('states','253'),('provinces','3096')]:local[scope].pop(key,None)
(R/'assets/display/local_coasts.json').write_text(json.dumps(local,separators=(',',':')))
print('FOCUSED_FIELDS_READY',len(b))
