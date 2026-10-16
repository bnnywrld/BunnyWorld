"""Apply approved small-State corrections over 0.2.0.16. No density redesign."""
from pathlib import Path
from collections import defaultdict,Counter
import copy,json,io,math,re,hashlib
import numpy as np
from scipy.ndimage import find_objects,binary_dilation
from PIL import Image
R=Path(__file__).resolve().parents[1];W,H=16384,8192;Image.MAX_IMAGE_PIXELS=None
read=lambda n:json.loads((R/n).read_text())
def write(n,d):(R/n).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
w=read('data/world.json');ps=read('data/provinces.json');assert w['version']=='0.2.0.16','Apply to a clean 0.2.0.16 baseline'
oldw=copy.deepcopy(w);oldps=copy.deepcopy(ps);a=np.load(R/'tools/cartography/province_atlas_0216.npz')['provinces'];old=a.copy();report={'version':'0.2.0.17','merges':[],'ownership':[],'province_merges':[],'audit':[],'general_province_redesign':False};state_remap={};province_remap={}
audit_ids=[int(l.split('|')[1])for l in (R/'documentation/small_states_audit_source.md').read_text().splitlines()if re.match(r'\| \d+ \|',l)]
keep={1415,1411,1419,1418,237,1762,1489,1490,1500,1525,1524,1529,1520,464,497,1761,1760,1763,633,1599,818,914,1615,1614,1737,1725,33,224,223,238,242,241,248,359,1530,448,1758,547,1567,581,1576,705,703,702,704,925,972,1743,1740,673,490}
def own(sid,tag,reason):
 s=w['regions'][str(sid)]
 if s['owner']!=tag:report['ownership'].append({'state':sid,'name':s['name'],'from':s['owner'],'to':tag,'reason':reason});s['owner']=tag;s['demographic_profile']=tag

def add_country(tag,parent,capital,name=None,administration=None):
 if tag in w['countries']:return
 c=copy.deepcopy(w['countries'][parent]);c.update(w['country_registry'][tag]);c.update(tag=tag,index=max(c['index']for c in w['countries'].values())+1,capital=capital,regions=[],population=0,organizations=[],cosmetic='',color_override=[],government={'party':'','outlook':'Western Outlook'},outlook='Western Outlook');c['name']=name or c['name'];c['starting_stats']=copy.deepcopy(w['countries'][parent]['starting_stats']);c['starting_data_note']='Existing scenario values inherited pending demographic/economic refinement.'
 if administration:c['administration_2000']=administration
 w['countries'][tag]=c
add_country('MNC','FRA',1500);add_country('NAU','MIC',673);add_country('PAU','MIC',490);add_country('TIM','IND',1749,'Timor-Leste','UNTAET')
for sid,tag,reason in [(1500,'MNC','Monaco is an independent State, not French territory.'),(673,'NAU','The footprint is Nauru, not the Marshall Islands.'),(490,'PAU','Main Palau footprint; independence in 1994.'),(1749,'TIM','UNTAET administration from October 1999, not Indonesian control.'),(33,'BRA','Brazilian Island administered by Brazil in 2000.'),(224,'PHI','Scarborough under Philippine de facto control before the 2012 standoff.'),(211,'TAI','Actual footprint is Pratas, controlled by Taiwan.'),(359,'FRA','Matthew and Hunter administered with New Caledonia.'),(547,'COL','Footprint is Bajo Nuevo; Colombian administration, not Jamaican sovereignty.'),(703,'SPR','Spanish-administered Peñón de Alhucemas.'),(702,'SPR','Spanish-administered Peñón de Vélez de la Gomera.'),(704,'SPR','Spanish-administered Chafarinas Islands.')]:own(sid,tag,reason)
renames={33:'Brazilian Island',211:'Pratas Islands',223:'Paracel Islands',238:'Malpelo Island',241:'Serrana Bank',242:'Serranilla Bank',547:'Bajo Nuevo Bank',673:'Nauru',490:'Palau',678:'Woleai Atoll',1113:'Eastern Equatoria',1749:'Timor-Leste'}
for sid,name in renames.items():w['regions'][str(sid)]['name']=name
merges={8:275,57:788,58:740,127:114,128:120,160:155,185:567,210:223,230:228,273:1115,495:485,491:490,492:490,493:490,496:490,637:973,669:663,672:663,799:1187,899:742,885:742,900:742,1002:1785,1085:1765,1047:1039,209:223,212:223,220:223,221:223,222:223,249:972,1755:1432,462:1758,582:581,1119:581,700:1614,701:694,743:925,867:865,1757:1489,1265:1278,1275:1261,1256:687,1742:1738,498:482,680:677,1741:1566}
reasons={57:'Reference point is in Iran/Ardabil, not an Azerbaijani island.',58:'Reference point is in Fuzuli, controlled by NKR in 2000.',185:'Reference point is in Kachin, not China.',273:'Reference point is in Central Equatoria, not DRC.',637:'Farquhar island footprint belongs to Seychelles.',799:'Reference point is in Farah, Afghanistan; Taliban-controlled scenario region.',1002:'Upper Kodori was Georgian-controlled in 2000.',1256:'Reference points lie in Moldova; label Luhansk is geographically unrelated.',701:'Moroccan mainland immediately outside Melilla; merge into Oriental, not Spain.',498:'Footprint is Gunungapi Wetar in the Banda Sea, not mainland Timor-Leste.',1741:'US military presence on Okinawa is not sovereign US territory after 1972.'}
def merge(source,target):
 s=w['regions'].pop(str(source));t=w['regions'][str(target)];state_remap[source]=target;t['population']+=s['population']
 for k,v in s.get('buildings',{}).items():t['buildings'][k]=t['buildings'].get(k,0)+v
 for key in ['cores','claims','geographic_divisions','geographic_codes']:t[key]=sorted(set(t.get(key,[])+s.get(key,[])))
 for pid in s['provinces']:ps[str(pid)]['region']=target;t['provinces'].append(pid)
 for c in w['countries'].values():
  if c['capital']==source:c['capital']=target
 report['merges'].append({'removed':source,'into':target,'name':s['name'],'owner':t['owner'],'reason':reasons.get(source,'Consolidate the listed fragment or duplicate dispute sector into its geographic parent.')})
for s,t in merges.items():merge(s,t)
# Explicit requested province destinations are captured before any renumbering.
def local(sid,n):return next(pid for pid in oldw['regions'][str(sid)]['provinces']if oldps[str(pid)]['local_index']==n)
def dissolve(source,target,reason):
 if source==target or str(source)not in ps:return
 p=ps.pop(str(source));q=ps[str(target)];q['area_km2']=round(q['area_km2']+p['area_km2'],3);province_remap[source]=target
 report['province_merges'].append({'removed':source,'into':target,'reason':reason})
dissolve(local(1453,6),local(1460,1),'Requested Isle of Man union with Southwest Scotland Province 1')
# Move Isle of Man State membership too; merge leaves no orphaned source record.
ps[str(local(1460,1))]['region']=1460
for sid in [669,672]:
 for pid in oldw['regions'][str(sid)]['provinces']:dissolve(pid,local(663,5),'Requested Yucatan Province 5 island union')
# Collapse duplicated disputed islands, and all small kept territories, to one
# province. Never merge an independent country into another country.
for sid in keep|{253}:
 if str(sid)not in w['regions']:continue
 ids=[p['id']for p in ps.values()if p['region']==sid]
 if len(ids)>1:
  target=max(ids,key=lambda pid:ps[str(pid)]['area_km2'])
  for pid in ids:dissolve(pid,target,'One province for this kept small territory / dispute')
# Remove remaining sub-100 km² provinces through a same-State union. Tiny
# single-province strategic States and independent countries are exceptions.
def metric(p,q):
 u,v=p['map_center'];x,y=q['map_center'];dx=((u-x+.5)%1-.5)*math.cos((.5-v)*math.pi);return dx*dx+(v-y)**2
by=defaultdict(set)
for p in ps.values():by[p['region']].add(p['id'])
for pid in sorted(list(map(int,ps)),key=lambda k:ps[str(k)]['area_km2']):
 if str(pid)not in ps:continue
 p=ps[str(pid)];sid=p['region']
 if p['area_km2']>=100 or len(by[sid])<=1:continue
 candidates=[n for n in p['neighbors']if n in by[sid]and n!=pid and str(n)in ps]
 if not candidates:candidates=list(by[sid]-{pid})
 target=min(candidates,key=lambda n:metric(p,ps[str(n)]));dissolve(pid,target,'Same-State province smaller than 100 km²');by[sid].remove(pid)
# Resolve chains before changing IDs, retaining original land coverage.
lookup=np.arange(65536,dtype=np.uint16)
for source in province_remap:
 target=province_remap[source]
 while target in province_remap:target=province_remap[target]
 province_remap[source]=target;lookup[source]=target
a=lookup[a]
# Modest enlargement of isolated Paracel components, explicitly display scale.
paracel=next(p['id']for p in ps.values()if p['region']==223);yy,xx=np.nonzero(a==paracel);top,left=yy.min()-3,xx.min()-3;bottom,right=yy.max()+4,xx.max()+4;view=a[top:bottom,left:right];mask=view==paracel;enlarged=binary_dilation(mask,iterations=1)&(view==0);view[enlarged]=paracel;w['regions']['223']['display_exaggeration']='One native map cell around original island footprints; recorded area remains geographic scenario area.';report['paracel_display_pixels_added']=int(enlarged.sum())
for s in w['regions'].values():s['provinces']=[];s['neighbors']=[]
for p in ps.values():w['regions'][str(p['region'])]['provinces'].append(p['id']);p['neighbors']=[]
# Rebuild exact adjacency from the final province-ID atlas, not stale metadata.
edges=set()
for t in range(0,H,128):
 for l,r in [(a[t:t+128,:-1],a[t:t+128,1:]),(a[t:min(H-1,t+128)],a[t+1:min(H,t+129)])]:
  mask=(l>0)&(r>0)&(l!=r);codes=np.minimum(l[mask],r[mask]).astype(np.uint32)*65536+np.maximum(l[mask],r[mask]);edges.update(divmod(int(c),65536)for c in np.unique(codes))
for l,r in edges:
 if str(l)not in ps or str(r)not in ps:continue
 ps[str(l)]['neighbors'].append(r);ps[str(r)]['neighbors'].append(l);sl,sr=ps[str(l)]['region'],ps[str(r)]['region']
 if sl!=sr:w['regions'][str(sl)]['neighbors'].append(sr);w['regions'][str(sr)]['neighbors'].append(sl)
levels={'infrastructure','internet_station','air_base','radar_station','rail_terminal','anti_air_building','stronghold_network'}
for key,s in w['regions'].items():
 s['provinces'].sort();s['neighbors']=sorted(set(s['neighbors']));assert s['provinces'],key;s['area_km2']=round(sum(ps[str(pid)]['area_km2']for pid in s['provinces']),3)
 original={pid:oldps[str(pid)]['local_index']for pid in oldw['regions'].get(key,{}).get('provinces',[])if str(pid)in ps and ps[str(pid)]['region']==s['id']};used=set(original.values());next_index=max(used or {0})+1
 for pid in s['provinces']:
  p=ps[str(pid)]
  if pid in original:p['local_index']=original[pid]
  else:p['local_index']=next_index;next_index+=1
  if len(s['provinces'])==1 and s['id']in keep:p['local_index']=1
  p['name']=s['name']+' · Province '+str(p['local_index']);p['neighbors'].sort()
 for k in s['buildings']:
  if k in levels:s['buildings'][k]=min(10,s['buildings'][k])
 s['building_slot_baseline']=max(sum(n for k,n in s['buildings'].items()if k not in levels),4+int(4*math.sqrt(s['population']/100000)))
 s['protected_territories']=[v for v in s.get('protected_territories',[])if not any(v==x for x in ['B43'])]
# Re-associate all marker, capital, and decorative scenery references.
def at(lon,lat):return int(a[min(H-1,max(0,int((90-lat)/180*H))),int((lon+180)/360*W)%W])
cities=read('data/cities.json');choices=defaultdict(list)
for c in cities:
 pid=at(c['longitude'],c['latitude']);c['province_id']=pid;c.pop('state_id',None);c.pop('state_capital',None)
 if str(pid)in ps:c['country']=w['regions'][str(ps[str(pid)]['region'])]['owner'];choices[ps[str(pid)]['region']].append(c)
for key,s in w['regions'].items():
 cs=choices[s['id']]
 if cs:
  c=max(cs,key=lambda c:(bool(c.get('capital')),c.get('population_rank',0)));c.update(state_capital=True,state_id=s['id']);s.update(state_capital=c['name'],capital_province=c['province_id'],capital_uv=[(c['longitude']+180)/360,(90-c['latitude'])/180],capital_source='Existing mapped settlement',capital_is_settlement=True)
 else:
  pid=max(s['provinces'],key=lambda i:ps[str(i)]['area_km2']);s.update(state_capital=s['name']+' Centre',capital_province=pid,capital_uv=ps[str(pid)]['map_center'],capital_source='Administrative anchor; no mapped settlement',capital_is_settlement=False)
 if int(s.get('capital_province',0))not in s['provinces']:s['capital_province']=s['provinces'][0]
 if s['id']in state_remap.values()or s['id']in keep:s['map_center']=ps[str(s['capital_province'])]['map_center']
for tag,c in w['countries'].items():
 c['regions']=sorted(s['id']for s in w['regions'].values()if s['owner']==tag);c['population']=sum(w['regions'][str(s)]['population']for s in c['regions'])
 if c['capital']not in c['regions']:c['capital']=max(c['regions'],key=lambda i:w['regions'][str(i)]['population'])
 c['map_center']=w['regions'][str(c['capital'])]['capital_uv']
scene=read('data/urban_scenery.json');grouped=defaultdict(list)
for kind in ['clusters','landmarks']:
 for c in scene[kind]:
  pid=at(c['longitude'],c['latitude'])
  if str(pid)not in ps:pid=province_remap.get(int(c.get('province',0)),int(c.get('province',0)))
  if str(pid)in ps:c['province']=pid;c['state']=ps[str(pid)]['region']
  if kind=='clusters':grouped[c['state']].append(c)
for sid,clusters in grouped.items():
 s=w['regions'][str(sid)];uv=s['capital_uv'];capital=min(clusters,key=lambda c:((c['longitude']+180)/360-uv[0])**2+((90-c['latitude'])/180-uv[1])**2);weights=[max(1,len(c['instances']))*(1.2 if c is capital else 1)for c in clusters]
 for c,v in zip(clusters,weights):c['state_capital_priority']=c is capital;c['state_visual_weight']=v/sum(weights)
urban=read('data/urban_population.json');urban['states']={k:{'population_2000':s['population']}for k,s in w['regions'].items()}
for g in urban.get('groups',{}).values():g['provinces']=sorted(set(province_remap.get(pid,pid)for pid in g.get('provinces',[])if str(province_remap.get(pid,pid))in ps))
protected=read('data/protected_territories_0210.json');protected['version']='0.2.0.17'
for row in protected['territories']:
 row['states']=sorted(set(state_remap.get(s,s)for s in row['states']if str(state_remap.get(s,s))in w['regions']))
 row['policy']='Single footprint; de facto control at 2000 start; claims remain metadata.'
for sid,note in [(448,'Uninhabited and contested in 2000; no exclusive de facto controller. Existing Greenland assignment is a scenario convention, not a finding of sovereignty.'),(705,'Unoccupied status quo in 2000; existing Moroccan assignment is a scenario convention, not an exclusive-control claim.')]:w['regions'][str(sid)]['control_2000_note']=note
# Complete disposition of every input row, including retained strategic areas.
for sid in audit_ids:
 target=state_remap.get(sid,sid);s=w['regions'][str(target)];report['audit'].append({'input_state':sid,'input_name':oldw['regions'][str(sid)]['name'],'result_state':target,'result_name':s['name'],'owner_2000':s['owner'],'action':'merged'if target!=sid else 'corrected'if oldw['regions'][str(sid)]['owner']!=s['owner']or oldw['regions'][str(sid)]['name']!=s['name']else 'retained','note':s.get('control_2000_note',reasons.get(sid,'Retained real/strategic territory, with a single province and a larger selection marker where small.'))})
w.update(version='0.2.0.17',scenario_id='bunny_world_2000_0_2_0_17');scene['version']='0.2.0.17'
for n,d in [('world',w),('provinces',ps),('cities',cities),('urban_scenery',scene),('urban_population',urban),('protected_territories_0210',protected)]:write('data/'+n+'.json',d)
for n,values in [('province_atlas_0217.npz',{'provinces':a})]:
 b=io.BytesIO();np.savez_compressed(b,**values);(R/'tools/cartography'/n).write_bytes(b.getvalue())
slut=np.zeros(65536,np.uint16)
for p in ps.values():slut[p['id']]=p['region']
states=slut[a]
for i in range(4):
 t,l=i//2*4096,i%2*8192;v=a[t:t+4096,l:l+8192].copy();path=R/f'assets/region_ids_{i}.png';before=np.asarray(Image.open(path));antarctica=(before[:,:,0]==255)&(before[:,:,1]==255);v[antarctica]=65535;states[t:t+4096,l:l+8192][antarctica]=8191
 rgb=np.stack([(v&255).astype(np.uint8),(v>>8).astype(np.uint8),np.zeros_like(v,np.uint8)],-1);b=io.BytesIO();Image.fromarray(rgb).save(b,format='PNG');path.write_bytes(b.getvalue())
b=io.BytesIO();np.savez_compressed(b,regions=states);(R/'tools/cartography/grouped_atlas_022r2.npz').write_bytes(b.getvalue())
idx=np.zeros((256,256,3),np.uint8)
for p in ps.values():idx[p['id']//256,p['id']%256]=[p['region']&255,p['region']>>8,p['local_index']]
idx[255,255]=[255,31,0];Image.fromarray(idx).save(R/'assets/province_index.png')
report.update(countries=len(w['countries']),states=len(w['regions']),provinces=len(ps),global_population=sum(s['population']for s in w['regions'].values()),state_remap=state_remap,province_remap=province_remap,small_province_exceptions=[p['id']for p in ps.values()if p['area_km2']<100],changed_atlas_pixels=int((old!=a).sum()))
assert report['global_population']==sum(s['population']for s in oldw['regions'].values());write('data/geography_0217_report.json',report);print('STATES_0217_READY',report['countries'],report['states'],report['provinces'],'merges',len(merges),'province merges',len(province_remap),'audit',len(report['audit']))
