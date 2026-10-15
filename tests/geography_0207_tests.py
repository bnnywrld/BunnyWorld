"""Whole-world output checks and independent geographic reference probes."""
from pathlib import Path
from collections import Counter,defaultdict
import sys,json,math
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects

ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography';BASE=SRC/'baseline_0205'
Image.MAX_IMAGE_PIXELS=None
w=json.load(open(ROOT/'data/world.json'));oldw=json.load(open(BASE/'world.json'))
ps=json.load(open(ROOT/'data/provinces.json'));cities=json.load(open(ROOT/'data/cities.json'))
a=np.load(SRC/'grouped_atlas_022r2.npz')['regions'];p=np.load(SRC/'province_atlas_0207.npz')['provinces'];H,W=a.shape
checks=[];failures=[]
def check(value,text):
    checks.append(text)
    if not value:failures.append(text);print('FAIL',text,flush=True)
def at(lon,lat):return int(a[min(H-1,int((90-lat)/180*H)),int((lon+180)/360*W)%W])
check(len(w['countries'])==223 and set(w['countries'])==set(oldw['countries']),'all 223 scenario countries retained')
check(w['scenario_id']=='bunny_world_2000_0_2_0_7','new scenario identity')
oldpop=Counter();newpop=Counter();oldbuild=defaultdict(Counter);newbuild=defaultdict(Counter)
for s in oldw['regions'].values():oldpop[s['owner']]+=s['population'];oldbuild[s['owner']].update(s['buildings'])
for s in w['regions'].values():newpop[s['owner']]+=s['population'];newbuild[s['owner']].update(s['buildings'])
check(oldpop==newpop and sum(newpop.values())==6144737528,'existing country population totals retained without demographic refinement')
check(all(oldbuild[t]==newbuild[t] for t in oldbuild),'country building totals retained')
owner=np.zeros(8192,np.uint16);oldowner=np.zeros_like(owner);parent=np.zeros(65536,np.uint16)
for k,s in w['regions'].items():owner[int(k)]=w['countries'][s['owner']]['index']
for k,s in oldw['regions'].items():oldowner[int(k)]=oldw['countries'][s['owner']]['index']
for k,province in ps.items():parent[int(k)]=province['region']
old=np.load(BASE/'states.npz')['regions'];mismatched=0;uncovered=0
for top in range(0,H,128):
    q=a[top:top+128];pp=p[top:top+128]
    mismatched+=int(np.count_nonzero(owner[q]!=oldowner[old[top:top+128]]))
    uncovered+=int(np.count_nonzero((q>0)&(q<8191)&((pp==0)|(parent[pp]!=q))))
check(mismatched==0,'country control and coast coverage agree with accepted scenario everywhere')
check(uncovered==0,'every land pixel has a province in its State')
check(set(map(int,ps))==set(map(int,np.unique(p)))-{0},'all province IDs have data and footprints')
check(all(s['name'].strip() and s['provinces'] for s in w['regions'].values()),'all States have names and provinces')
check(max(map(int,w['regions']))<8191 and max(map(int,ps))<65535,'IDs fit renderer palette and categorical texture encoding')
for k,s in w['regions'].items():
    u,v=s['map_center'];check(at(u*360-180,90-v*180)==int(k),'State focus lies within '+s['name'])
    check(all(ps[str(i)]['region']==int(k) for i in s['provinces']),'province lists belong to State '+k)
for tag,c in w['countries'].items():
    check(w['regions'][str(c['capital'])]['owner']==tag,'capital belongs to '+tag)
    check(set(c['regions'])=={int(k) for k,s in w['regions'].items() if s['owner']==tag},'country State list agrees '+tag)
for k,province in ps.items():
    u,v=province['map_center'];pid=int(p[min(H-1,int(v*H)),int(u*W)%W])
    check(pid==int(k),'province focus lies within '+k)
    check(all(int(k) in ps[str(i)]['neighbors'] for i in province['neighbors']),'province neighbor graph symmetric '+k)
    check('source_md_province' not in province,'province independent of MD geometry '+k)
for i in range(4):
    rgb=np.asarray(Image.open(ROOT/'assets'/f'region_ids_{i}.png'),np.uint16);encoded=rgb[:,:,0]+rgb[:,:,1]*256
    q=p[i//2*4096:(i//2+1)*4096,i%2*8192:(i%2+1)*8192].copy()
    q[a[i//2*4096:(i//2+1)*4096,i%2*8192:(i%2+1)*8192]==8191]=65535
    check(np.array_equal(encoded,q),'runtime identity texture matches final atlas tile '+str(i))
check(len(w['countries']['POL']['regions'])==15,'Poland respects strict 13-to-15 State budget')
check(len(w['countries']['GER']['regions'])==17,'Germany meets MD minimum with geographic Bavaria/Franken split')
for lon,lat,tag,name in [(-119,36,'USA','California'),(-105,39,'USA','Colorado'),(-74,43,'USA','New York'),(19,52,'POL',''),(11.5,48.2,'GER',''),(31.2,30,'EGY',''),(139.7,35.7,'JAP',''),(151,-33,'AST','New South Wales')]:
    s=w['regions'][str(at(lon,lat))];check(s['owner']==tag and (not name or name in s['name']),'geographic reference '+tag+' '+name)
for tag in ['ALB','BEL','EST','LAT','LIT','SLV','SWI']:
    check(len(w['countries'][tag]['regions'])<=8,'small-country State count bounded '+tag)
for c in cities:
    pid=c.get('province_id',0)
    check(not pid or (str(pid) in ps and w['regions'][str(ps[str(pid)]['region'])]['owner']==c['country']),'city reference valid '+c['name'])
# Detect disconnected pieces on the SAME landmass, rather than flagging every
# legitimate island group as malformed.
boxes=find_objects(a,max_label=8191);badpieces=[]
for key,s in w['regions'].items():
    bb=boxes[int(key)-1];land,_=label(a[bb]==int(key),np.ones((3,3),bool));view=p[bb]
    for pid in s['provinces']:
        pieces,n=label(view==pid,np.ones((3,3),bool))
        if n<2:continue
        sizes=np.bincount(pieces.ravel());pb=find_objects(pieces);seen=set()
        for i in range(1,n+1):
            if sizes[i]<8:continue
            yy,xx=np.nonzero(pieces[pb[i-1]]==i);component=int(land[yy[0]+pb[i-1][0].start,xx[0]+pb[i-1][1].start])
            if component in seen:badpieces.append(pid)
            seen.add(component)
check(not badpieces,'no substantial disconnected province pieces on the same landmass')
# Agreed budgets are constraints, including explicit +1 small-country cases.
ref=json.load(open(ROOT/'data/md_geography_reference.json'))
budget=json.load(open(ROOT/'data/geography_0207_report.json'))
check(ref['counts']['land']==13221 and ref['state_count']==1250,'original MD counts exclude dummy/sea/lake entries')
check(abs(len(ps)-ref['counts']['land'])/ref['counts']['land']<.03,'land province total within 3 percent of original MD')
for row in budget['country_budgets']:
 tag=row['country'];n=len(w['countries'][tag]['regions']);normal=row['md_states']*120//100
 check(row['minimum']<=n<=row['allowed_maximum'],'strict MD State bounds '+tag)
 check(row['allowed_maximum']<=normal+1 and (row['allowed_maximum']==normal or row['exception_reason']),'at most one justified extra State '+tag)
for tag in ['ALG','KOR','USA','CHI','RAJ','JAP']:
 n=sum(len(s['provinces']) for s in w['regions'].values() if s['owner']==tag);target=ref['countries'][tag]['land_provinces']
 check(abs(n-target)<=max(4,target*.06),'MD land density budget retained '+tag)
territories=json.load(open(ROOT/'data/protected_territories_0207.json'))['territories']
check(len(territories)==99 and all(t['states'] for t in territories),'all 99 Natural Earth territory identities have reserved State coverage')
for t in territories:
 check(all(t['code'] in w['regions'][str(s)]['protected_territories'] for s in t['states']),'protected territory mapping '+t['code'])
for name,tag in [('Crimea','UKR'),("Donetsk People's Republic",'UKR'),("Luhansk People's Republic",'UKR')]:
 matches=[t for t in territories if t['name']==name]
 check(matches and all(w['regions'][str(s)]['owner']==tag for t in matches for s in t['states']),'future dispute boundary retains 2000 owner '+name)
report={'checks':len(checks),'failures':failures,'countries':len(w['countries']),'states':len(w['regions']),'provinces':len(ps),'disconnected_provinces':sorted(set(badpieces))}
(ROOT/'validation_0207').mkdir(exist_ok=True);(ROOT/'validation_0207/geography_results.json').write_text(json.dumps(report,indent=2))
print('GEOGRAPHY_0207',json.dumps(report),flush=True)
sys.exit(bool(failures))
