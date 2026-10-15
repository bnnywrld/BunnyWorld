from pathlib import Path
from collections import deque
import json,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
w=json.loads((ROOT/'data/waterways.json').read_text());s=json.loads((ROOT/'data/sea_regions.json').read_text())
a=np.load(ROOT/'tools/cartography/grouped_atlas_022r2.npz')['regions'][1::2,1::2]
rgb=np.asarray(Image.open(ROOT/'assets/sea_ids.png'),np.uint16);ids=rgb[:,:,0]+rgb[:,:,1]*256
assert not np.any((a>0)&(ids>0)),'sea IDs overlap accepted land'
for key,entry in s.items():
 for neighbor in entry['neighbors']:
  assert int(key) in s[str(neighbor)]['neighbors'],'nonreciprocal sea adjacency'
for p in w['passages']:
 left,right=p['ends'];assert right in s[str(left)]['neighbors'] and left in s[str(right)]['neighbors']
 assert p['open_at_start']
assert {(p['id'],tuple(p['ends'])) for p in w['passages']}=={('suez',(69,100)),('panama',(53,107)),('bosporus',(240,241)),('dardanelles',(241,214))}
seen={240};queue=deque([240])
while queue:
 for n in s[str(queue.popleft())]['neighbors']:
  if n not in seen:seen.add(n);queue.append(n)
assert 214 in seen and 69 in seen and 53 in seen,'Black Sea is disconnected from world ocean'
for name,lon,lat in [('Black Sea',35,43),('Marmara',28,40.6),('Caspian',51,42),('Lake Victoria',33,-1.5),('Lake Superior',-88,47.5)]:
 value=int(ids[int((90-lat)/180*ids.shape[0]),int((lon+180)/360*ids.shape[1])])
 assert value==({'Black Sea':240,'Marmara':241}.get(name,0)),(name,value)
assert 250<=len(w['rivers'])<=500
print('WATERWAYS_0201_TESTS_PASS: major rivers, reciprocal canal/strait links, Black Sea reaches world ocean, inland lakes excluded')
