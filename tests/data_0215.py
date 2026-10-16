from pathlib import Path
from collections import Counter,defaultdict
import json,zlib,struct
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];B=R.parent/'baseline_0214';Image.MAX_IMAGE_PIXELS=None
read=lambda p:json.loads((R/p).read_text())
w=read('data/world.json');ps=read('data/provinces.json');old=json.loads((B/'data/world.json').read_text());oldps=json.loads((B/'data/provinces.json').read_text());a=np.load(R/'tools/cartography/province_atlas_0215.npz')['provinces'];before=np.load(R/'tools/cartography/province_atlas_0210.npz')['provinces'];report=read('data/geography_0215_report.json')
assert len(w['regions'])==1353 and len(ps)==13591
assert not {'1485','1751','738','1753','1084'}.intersection(w['regions'])
removed={r['removed']for r in report['province_dissolutions']};assert removed=={6633,5500,10335}
assert np.all(np.isin(before[a!=before],list(removed))), 'Only strip geometry may change'
assert not any(str(i)in ps for i in removed) and not np.isin(a,list(removed)).any()
assert w['regions']['1484']['name']=='Channel Islands' and len(w['regions']['1484']['provinces'])==3
assert w['regions']['363']['provinces']==[3865]and ps['3865']['local_index']==6
assert 'Bohemia'in w['regions'][str(ps['3118']['region'])]['name']
assert 'Moravia'in w['regions'][str(ps['3112']['region'])]['name']
assert 'Akmola'in w['regions'][str(ps['5261']['region'])]['name']
assert w['countries']['IND']['capital']==1827
assert w['regions']['1827']['geographic_divisions']==['Banten','Jakarta','West Java']
for lon,lat,sid in [(106.827492,-6.172472,1827),(107.606,-6.918,1827),(104.746,-2.99,487),(105.266,-5.429,487)]:
 pid=int(a[int((90-lat)/180*8192),int((lon+180)/360*16384)]);assert ps[str(pid)]['region']==sid,(lon,lat,pid)
assert w['countries']['JAP']['capital']==1563 and w['countries']['USA']['capital']==1699 and w['countries']['AST']['capital']==1416
totals=lambda x:Counter({t:sum(s['population']for s in x['regions'].values()if s['owner']==t)for t in x['countries']})
assert totals(w)==totals(old)
own=np.zeros(65536,np.uint16);oldown=np.zeros(65536,np.uint16)
for p in ps.values():own[p['id']]=w['countries'][w['regions'][str(p['region'])]['owner']]['index']
for p in oldps.values():oldown[p['id']]=old['countries'][old['regions'][str(p['region'])]['owner']]['index']
assert np.array_equal(own[a],oldown[before]),'No country ownership changes allowed'
for i in range(4):
 y,x=i//2*4096,i%2*8192;rgb=np.asarray(Image.open(R/f'assets/region_ids_{i}.png'));p=rgb[:,:,0].astype(np.uint16)+rgb[:,:,1].astype(np.uint16)*256;mask=p!=65535;assert np.array_equal(p[mask],a[y:y+4096,x:x+8192][mask])
seen=[]
for key,s in w['regions'].items():
 assert s['capital_province']in s['provinces'];seen+=s['provinces']
 for pid in s['provinces']:assert ps[str(pid)]['region']==int(key)
assert len(seen)==len(set(seen))==len(ps)
index=read('assets/display/selection_distance.json');blob=(R/'assets/display/selection_distance.bwd').read_bytes();count=0
for scope,records in [('states',w['regions']),('provinces',ps),('seas',read('data/sea_regions.json'))]:
 assert set(index[scope])==set(records)
 for k,r in index[scope].items():assert len(zlib.decompress(blob[r[4]:r[4]+r[5]]))==r[6]*r[7];count+=1
# Verify all encoded border IDs and adjacency against the current State map.
for kind in ['land','province']:
 b=(R/f'tools/cartography/{kind}_boundaries_021.bin').read_bytes();nv,ni=struct.unpack('<II',b[:8]);c=np.frombuffer(b,np.dtype('<f4'),count=nv*4,offset=8+nv*28).reshape(nv,4);ids=np.rint(c*255).astype(int);left=ids[:,0]+ids[:,1]*256;right=ids[:,2]+ids[:,3]*256
 valid=set(map(int,w['regions']))|{0,8191}if kind=='land'else set(map(int,ps))|{0}
 assert set(left)|set(right)<=valid
 if kind=='province':
  pairs=set(zip(left[::2],right[::2]));expected={(p['id'],n)for p in ps.values()for n in p['neighbors']if p['id']<n and p['region']==ps[str(n)]['region']}
  assert expected<=pairs,('Missing internal province borders',len(expected-pairs))
  assert all(ps[str(l)]['region']==ps[str(r)]['region']for l,r in pairs)
audit=read('validation_0215/state_audit.json');nd=next(r for r in audit['states']if r['id']==1677)
for sid in [487,1827]:assert next(r for r in audit['states']if r['id']==sid)['selection_recall_after']>.98
assert nd['selection_recall_after']>.995 and nd['selection_recall_after']>nd['selection_recall_before']+.04
scene=read('data/urban_scenery.json');assert sum(len(c['instances'])for c in scene['clusters'])==85643
weights=defaultdict(float)
for c in scene['clusters']:weights[c['state']]+=c['state_visual_weight'];assert str(c['province'])in ps
assert all(abs(v-1)<1e-6 for v in weights.values())
result={'passed':True,'countries':len(w['countries']),'states':1353,'provinces':13591,'distance_fields_validated':count,'strip_provinces_removed':sorted(removed),'country_ownership_unchanged':True,'country_population_totals_unchanged':True,'all_internal_province_edges_present':True,'north_dakota_coverage_before':nd['selection_recall_before'],'north_dakota_coverage_after':nd['selection_recall_after'],'scenery_instances_unchanged':85643}
(R/'validation_0215/data_results.json').write_text(json.dumps(result,indent=2));print(result)
