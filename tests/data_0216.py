"""Focused regression checks for 0.2.0.16, including every Sumatra province."""
from pathlib import Path
from collections import Counter
import json,zlib,struct
import numpy as np
from scipy.ndimage import map_coordinates,distance_transform_edt
from PIL import Image
R=Path(__file__).resolve().parents[1];B=R.parent/'baseline_0215';Image.MAX_IMAGE_PIXELS=None
load=lambda p:json.loads((R/p).read_text())
w=load('data/world.json');ps=load('data/provinces.json');before=json.loads((B/'data/world.json').read_text());oldps=json.loads((B/'data/provinces.json').read_text());a=np.load(R/'tools/cartography/province_atlas_0216.npz')['provinces'];old=np.load(R/'tools/cartography/province_atlas_0215.npz')['provinces']
assert len(w['regions'])==1352 and len(ps)==13590
assert w['countries']['CYP']['regions']==[253] and w['regions']['253']['provinces']==[3096]
assert '254'not in w['regions']and'3097'not in ps and not (a==3097).any()
assert np.all(old[a!=old]==3097)and np.all(a[old==3097]==3096)
assert w['regions']['253']['state_capital']=='Nicosia'
totals=lambda x:Counter({t:sum(s['population']for s in x['regions'].values()if s['owner']==t)for t in x['countries']})
assert totals(w)==totals(before)
assert w['regions']['716']==before['regions']['716']or w['regions']['716']['neighbors']==[253,1473]
seen=[]
for s in w['regions'].values():
 seen+=s['provinces'];assert s['capital_province']in s['provinces']
 for pid in s['provinces']:assert ps[str(pid)]['region']==s['id']
assert len(seen)==len(set(seen))==len(ps)
for p in ps.values():
 assert all(str(n)in ps and p['id']in ps[str(n)]['neighbors']for n in p['neighbors'])
assert sum(s['population']for s in w['regions'].values())==6144737528
for i in range(4):
 y,x=i//2*4096,i%2*8192;rgb=np.asarray(Image.open(R/f'assets/region_ids_{i}.png'));ids=rgb[:,:,0].astype(np.uint16)+rgb[:,:,1].astype(np.uint16)*256;mask=ids!=65535;assert np.array_equal(ids[mask],a[y:y+4096,x:x+8192][mask])
index=load('assets/display/selection_distance.json');blob=(R/'assets/display/selection_distance.bwd').read_bytes();decoded=0
for scope,records in [('states',w['regions']),('provinces',ps),('seas',load('data/sea_regions.json'))]:
 assert set(index[scope])==set(records)
 for key,r in index[scope].items():assert len(zlib.decompress(blob[r[4]:r[4]+r[5]]))==r[6]*r[7];decoded+=1
mask=np.isin(a,w['regions']['1813']['provinces']);sy,sx=np.nonzero(mask);top,left=int(sy.min()),int(sx.min());depth=distance_transform_edt(mask[top:int(sy.max())+1,left:int(sx.max())+1]);r=index['states']['1813'];im=np.frombuffer(zlib.decompress(blob[r[4]:r[4]+r[5]]),np.uint8).reshape(r[7],r[6]);sumatra=[]
for pid in w['regions']['1813']['provinces']:
 yy,xx=np.nonzero(a==pid);fx=((xx+.5)/16384-r[0])/r[2]*r[6]-.5;fy=((yy+.5)/8192-r[1])/r[3]*r[7]-.5;v=map_coordinates(im.astype(float),[fy,fx],order=1,mode='constant',cval=0);recall=float(np.mean(v>127.5));interior=depth[yy-top,xx-left]>1.5;missing=int(np.sum((v<=127.5)&interior));assert missing==0,(pid,recall,missing);sumatra.append({'province':pid,'selection_coverage':recall,'pixels':len(xx),'missing_interior_pixels':missing})
# Decode the actual boundary source that was compiled, rather than trusting
# State membership alone. Every internal edge of all 17 provinces must exist.
b=(R/'tools/cartography/province_boundaries_021.bin').read_bytes();nv,ni=struct.unpack('<II',b[:8]);c=np.frombuffer(b,'<f4',count=nv*4,offset=8+nv*28).reshape(nv,4);ids=np.rint(c[::2]*255).astype(int);pairs=set(zip(ids[:,0]+ids[:,1]*256,ids[:,2]+ids[:,3]*256));expected={(p['id'],n)for p in ps.values()for n in p['neighbors']if p['id']<n and p['region']==ps[str(n)]['region']};assert expected<=pairs
sumatra_ids=set(w['regions']['1813']['provinces']);se={pair for pair in expected if pair[0]in sumatra_ids};assert se<=pairs and len(sumatra_ids)==17
result={'passed':True,'states':1352,'provinces':13590,'cyprus_one_state_one_province':True,'only_former_cyprus_buffer_pixels_changed':int((a!=old).sum()),'country_population_totals_conserved':True,'selection_fields_decoded':decoded,'sumatra_all_provinces':sumatra,'sumatra_internal_borders_verified':len(se),'all_internal_province_borders_verified':len(expected)}
(R/'validation_0216/data_results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
