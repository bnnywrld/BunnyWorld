"""Remove projection-sampling fragments without merging across State borders.

The partition is grown on equal-area grids. This final pass enforces native
atlas connectivity on each landmass. Separate islands remain valid groups.
"""
from pathlib import Path
from collections import Counter
import json
import numpy as np
from scipy.ndimage import find_objects,label,binary_dilation,distance_transform_edt
from build_geography_0206 import ROOT,SRC,W,H,AREA,center,pairs,write
from PIL import Image

w=json.load(open(ROOT/'data/world.json'));ps=json.load(open(ROOT/'data/provinces.json'))
a=np.load(SRC/'grouped_atlas_022r2.npz')['regions'];p=np.load(SRC/'province_atlas_0206.npz')['provinces']
boxes=find_objects(a,max_label=8191);changed=0;split=0;tiny=0
for key,state in w['regions'].items():
    sid=int(key);bb=boxes[sid-1];sm=a[bb]==sid;view=p[bb];land,nland=label(sm,np.ones((3,3),bool))
    for pid in list(state['provinces']):
        mask=view==pid;parts,n=label(mask,np.ones((3,3),bool))
        if n<2:continue
        sizes=np.bincount(parts.ravel());by_land={};partboxes=find_objects(parts);part_land={}
        for k in range(1,n+1):
            pb=partboxes[k-1];yy,xx=np.nonzero(parts[pb]==k);component=int(land[yy[0]+pb[0].start,xx[0]+pb[1].start]);part_land[k]=component
            if component not in by_land or sizes[k]>sizes[by_land[component]]:by_land[component]=k
        for k in range(1,n+1):
            component=part_land[k]
            if by_land[component]==k:continue
            piece=parts==k;around=binary_dilation(piece,np.ones((3,3),bool))&sm&~piece
            neighbors=view[around];neighbors=neighbors[(neighbors>0)&(neighbors!=pid)]
            if sizes[k]<=500 and len(neighbors):
                target=int(np.bincount(neighbors).argmax());view[piece]=target;changed+=int(sizes[k])
            else:
                newpid=max(map(int,ps))+1;view[piece]=newpid
                ps[str(newpid)]={**ps[str(pid)],'id':newpid,'neighbors':[],'cities':[]};state['provinces'].append(newpid);split+=1
    # Absorb tiny slivers on the same landmass. A small island that is its own
    # landmass is not treated as a sliver.
    for pid in list(state['provinces']):
        yy,xx=np.nonzero(view==pid)
        if not len(xx):continue
        area=float(AREA[yy+bb[0].start].sum())
        if area>=180:continue
        piece=view==pid;around=binary_dilation(piece,np.ones((3,3),bool))&sm&~piece
        neighbors=view[around];neighbors=neighbors[(neighbors>0)&(neighbors!=pid)]
        if not len(neighbors):continue
        target=int(np.bincount(neighbors).argmax());view[piece]=target;tiny+=1
    state['provinces']=[pid for pid in state['provinces'] if np.any(view==pid)]
    for j,pid in enumerate(state['provinces']):
        yy,xx=np.nonzero(view==pid);yy+=bb[0].start;xx+=bb[1].start
        ps[str(pid)].update(local_index=j+1,map_center=center(yy,xx)[0],area_km2=round(float(AREA[yy].sum()),2),neighbors=[])
        ps[str(pid)]['cities']=[]
    if sid%100==0:print('FRAGMENT_QA',sid,flush=True)
used=set(int(v) for v in np.unique(p) if v)
ps={k:v for k,v in ps.items() if int(k) in used}
for (l,r),length in pairs(p).items():ps[str(l)]['neighbors'].append(r);ps[str(r)]['neighbors'].append(l)
for province in ps.values():province['neighbors'].sort()
micro=json.load(open(ROOT/'data/microstate_geometry.json'));ps[str(micro['province'])]['area_km2']=.44
# Refresh all prepared identity images after repairs.
index=np.zeros((65536,3),np.uint8)
for province in ps.values():index[province['id'],:2]=[province['region']&255,province['region']>>8]
index[65535,:2]=[255,31];Image.fromarray(index.reshape(256,256,3)).save(ROOT/'assets/province_index.png')
np.savez_compressed(SRC/'province_atlas_0206.npz',provinces=p);np.savez_compressed(SRC/'province_atlas_022r2.npz',provinces=p)
p[a==8191]=65535
for i in range(4):
    q=p[i//2*4096:(i//2+1)*4096,i%2*8192:(i%2+1)*8192]
    Image.fromarray(np.stack([(q&255).astype(np.uint8),(q>>8).astype(np.uint8),np.zeros_like(q,np.uint8)],-1)).save(ROOT/'assets'/f'region_ids_{i}.png')
if w.get('version')=='0.2.0.7':np.savez_compressed(SRC/'province_atlas_0207.npz',provinces=p*(a!=8191))
write('world',w);write('provinces',ps)
report_name='geography_0207_report' if w.get('version')=='0.2.0.7' else 'geography_0206_report'
r=json.load(open(ROOT/'data'/f'{report_name}.json'));r.update(provinces=len(ps),native_connectivity_repairs={'reassigned_pixels':changed,'split_pieces':split,'tiny_provinces_absorbed':tiny});write(report_name,r)
print('NATIVE_CONNECTIVITY_COMPLETE',r['native_connectivity_repairs'],flush=True)
