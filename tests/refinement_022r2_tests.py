from pathlib import Path
import json,sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from micro_geometry import MicroGeometry
def read(name):return json.load(open(ROOT/'data'/f'{name}.json'))
w,p,m=read('world'),read('provinces'),MicroGeometry(ROOT)
a=np.load(ROOT/'tools/cartography/province_atlas_022r2.npz')['provinces'];H,W=a.shape
assert np.count_nonzero(a==m.data['province'])==1
assert p[str(m.data['province'])]['area_km2']==.44
assert .3<m.data['reference_polygon_area_km2']<.8
def point(lon,lat):
    coarse=int(a[int((90-lat)/180*H),int((lon+180)/360*W)])
    return m.resolve(lon,lat,coarse)
assert point(12.4922,41.8902)!=m.data['province'],'Colosseum incorrectly inside Vatican'
assert w['regions'][str(p[str(point(12.4922,41.8902))]['region'])]['owner']=='ITA'
u,v=m.data['center_uv'];assert point(u*360-180,90-v*180)==m.data['province']
for identity in [m.data['province'],m.data['host_province'],821,826]:
    pp=p[str(identity)]
    assert identity not in pp['neighbors']
    for other in pp['neighbors']: assert identity in p[str(other)]['neighbors']
for identity in [821,826]:
    yy,xx=np.nonzero(a==identity);neighbors=set()
    for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:
        ys=np.clip(yy+dy,0,H-1);xs=(xx+dx)%W
        neighbors.update(map(int,np.unique(a[ys,xs])))
    neighbors-={0,65535,identity}
    assert neighbors==set(p[str(identity)]['neighbors']),(identity,neighbors.symmetric_difference(p[str(identity)]['neighbors']))
height=np.fromfile(ROOT/'assets/relief_data.bin',dtype='<u2').reshape(4096,8192)
image=np.asarray(Image.open(ROOT/'assets/relief_data.png'))
assert np.array_equal(height,image[:,:,0].astype(np.uint16)+image[:,:,1].astype(np.uint16)*256),'CPU/GPU prepared channels'
relief=read('relief');assert relief['land_lift_meters']<100 and relief['height_exaggeration']==4
assert relief['maximum_displacement']>.004,'mountain relief retained'
assert len(p)==40031 and len(w['countries'])==223 and len(w['regions'])==1235
print('REFINEMENT_022R2_TESTS_PASS: subpixel Vatican/Italian Colosseum, exact local graph adjacency, retained IDs, shared CPU/GPU relief, gentle shores and preserved mountains')
