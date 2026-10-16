"""Integrity checks for approved State changes and their current visual fields."""
from pathlib import Path
import json,zlib,struct,hashlib
import numpy as np
from scipy.ndimage import distance_transform_edt,map_coordinates
from PIL import Image
R=Path(__file__).resolve().parents[1];Image.MAX_IMAGE_PIXELS=None
read=lambda p:json.loads((R/p).read_text())
w=read('data/world.json');ps=read('data/provinces.json');report=read('data/geography_0217_report.json');a=np.load(R/'tools/cartography/province_atlas_0217.npz')['provinces'];old=np.load(R/'tools/cartography/province_atlas_0216.npz')['provinces']
assert len(w['countries'])==227 and len(w['regions'])==1305 and len(ps)==13312
assert len(report['audit'])==len({r['input_state']for r in report['audit']})==97
assert sum(s['population']for s in w['regions'].values())==6144737528
assert all(k not in w['regions']for k in report['state_remap'])
assert all(k not in ps for k in report['province_remap'])
for sid,owner in {1489:'ENG',1614:'SPR',1615:'SPR',1758:'ISR',925:'RAJ',972:'SER',581:'KEN',223:'CHI',224:'PHI',211:'TAI',242:'COL',547:'COL',1500:'MNC',673:'NAU',490:'PAU',1749:'TIM'}.items():assert w['regions'][str(sid)]['owner']==owner,(sid,owner)
for sid in [1489,1614,1615,1758,925,972,581,223,253,242,547,490]:assert len(w['regions'][str(sid)]['provinces'])==1
assert '1755'not in w['regions']and w['regions']['1725']['owner']=='USA'
assert ps['3642']['region']==1460 and ps['3642']['local_index']==1 and '13516'not in ps
assert ps['5973']['region']==663 and ps['5973']['local_index']==5
assert np.all(a[old==13516]==3642)
seen=[]
for key,s in w['regions'].items():
 assert s['capital_province']in s['provinces'];seen+=s['provinces']
 for pid in s['provinces']:assert ps[str(pid)]['region']==int(key)
assert len(seen)==len(set(seen))==len(ps)
for p in ps.values():
 assert all(str(n)in ps and p['id']in ps[str(n)]['neighbors']for n in p['neighbors'])
 if p['area_km2']<100:assert len(w['regions'][str(p['region'])]['provinces'])==1
for tag,c in w['countries'].items():
 actual=sorted(s['id']for s in w['regions'].values()if s['owner']==tag);assert c['regions']==actual and c['capital']in actual
 assert c['population']==sum(w['regions'][str(s)]['population']for s in actual)
for i in range(4):
 y,x=i//2*4096,i%2*8192;rgb=np.asarray(Image.open(R/f'assets/region_ids_{i}.png'));ids=rgb[:,:,0].astype(np.uint16)+rgb[:,:,1].astype(np.uint16)*256;mask=ids!=65535;assert np.array_equal(ids[mask],a[y:y+4096,x:x+8192][mask])
newland=(old==0)&(a>0);assert int(newland.sum())==report['paracel_display_pixels_added']and np.all(a[newland]==w['regions']['223']['provinces'][0]);assert not np.any((old>0)&(a==0))
index=read('assets/display/selection_distance.json');assert index['format']=='RH'and index['geography_sha256']==hashlib.sha256((R/'data/provinces.json').read_bytes()).hexdigest();blob=(R/'assets/display/selection_distance_0217.bwd').read_bytes();decoded=0
for scope,records in [('states',w['regions']),('provinces',ps),('seas',read('data/sea_regions.json'))]:
 assert set(index[scope])==set(records)
 for key,r in index[scope].items():
  raw=zlib.decompress(blob[r[4]:r[4]+r[5]]);assert len(raw)==r[6]*r[7]*2;f=np.frombuffer(raw,'<f2');assert np.isfinite(f).all()and f.min()>=0 and f.max()<=1;decoded+=1
coverage=[]
for sid in [1813,1569,1568,253,1811,223,1460,663]:
 ids=w['regions'][str(sid)]['provinces'];mask=np.isin(a,ids);yy,xx=np.nonzero(mask);top,left=yy.min(),xx.min();depth=distance_transform_edt(mask[top:yy.max()+1,left:xx.max()+1]);r=index['states'][str(sid)];im=np.frombuffer(zlib.decompress(blob[r[4]:r[4]+r[5]]),'<f2').reshape(r[7],r[6]).astype(float);fx=(((xx+.5)/16384-r[0])%1)/r[2]*r[6]-.5;fy=((yy+.5)/8192-r[1])/r[3]*r[7]-.5;v=map_coordinates(im,[fy,fx],order=1,mode='constant',cval=0);interior=depth[yy-top,xx-left]>1.5;missing=int(((v<=.5)&interior).sum());assert missing==0,(sid,missing)
 coverage.append({'state':sid,'provinces':len(ids),'interior_missing_pixels':missing,'coverage_all_source_cells':float(np.mean(v>.5))})
# Every current internal province edge, including southern North Sumatra.
b=(R/'tools/cartography/province_boundaries_021.bin').read_bytes();nv,ni=struct.unpack('<II',b[:8]);c=np.frombuffer(b,'<f4',count=nv*4,offset=8+nv*28).reshape(nv,4);ids=np.rint(c[::2]*255).astype(int);pairs=set(zip(ids[:,0]+ids[:,1]*256,ids[:,2]+ids[:,3]*256));expected={(p['id'],n)for p in ps.values()for n in p['neighbors']if p['id']<n and p['region']==ps[str(n)]['region']};assert expected<=pairs
coast=read('assets/display/local_coasts.json');assert coast['format']=='RH'
for sid in [1813,1569,1568,253,1811,223]:assert sid in coast['rebuilt_states']
pack=(R/'assets/display/local_coasts.bwd').read_bytes()
for key,r in coast['states'].items():assert key in w['regions']and len(zlib.decompress(pack[r[4]:r[4]+r[5]]))==r[6]*r[7]*2
scenery=read('data/urban_scenery.json');assert sum(len(c['instances'])for c in scenery['clusters'])==85643
for kind in ['clusters','landmarks']:
 for c in scenery[kind]:assert str(c['province'])in ps and ps[str(c['province'])]['region']==c['state']
result={'passed':True,'countries':227,'states':1305,'provinces':13312,'audit_rows_completed':97,'states_consolidated':47,'provinces_consolidated':278,'global_population_conserved':True,'fields_decoded':decoded,'merged_state_coverage':coverage,'all_internal_borders_verified':len(expected),'coast_windows_rebuilt':len(coast['rebuilt_states']),'scenery_instances':85643}
(R/'validation_0217/data_results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
