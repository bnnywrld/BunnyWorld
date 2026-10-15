"""Extract factual January-2000 state and LAND-province budgets from an MD archive."""
from pathlib import Path
from collections import Counter
import argparse,csv,hashlib,io,json,re,zipfile
from import_md import parse,Block,at_start,clean_name
ROOT=Path(__file__).resolve().parents[1]

def extract(path):
 with zipfile.ZipFile(path) as z:
  definition=next(n for n in z.namelist() if n.endswith('/map/definition.csv') or n=='map/definition.csv')
  prefix=definition[:-len('map/definition.csv')]
  rows=list(csv.reader(io.StringIO(z.read(definition).decode('utf-8-sig')),delimiter=';'))
  kinds={int(r[0]):r[4] for r in rows if len(r)>4 and r[0].isdigit() and int(r[0])>0}
  loc={}
  for n in sorted(z.namelist(),key=lambda n:('/replace/' in n,n)):
   if not n.startswith(prefix+'localisation/english/') or not n.endswith('.yml'):continue
   for line in z.read(n).decode('utf-8-sig',errors='replace').splitlines():
    m=re.match(r'^\s*([\w.-]+):(?:\d+)?\s*"((?:\\.|[^"\\])*)"',line)
    if m:loc[m[1]]=m[2].replace('\\"','"').replace('\\n',' ')
  states={};countries={};assigned=set()
  sourcehash=hashlib.sha256()
  for n in sorted(z.namelist()):
   if not n.startswith(prefix+'history/states/') or not n.endswith('.txt'):continue
   data=z.read(n);sourcehash.update(data)
   s=parse(data.decode('utf-8-sig')).get('state');h=Block(at_start(s.get('history',Block([]))))
   sid=int(s.get('id'));tag=h.get('owner','');pids=list(map(int,s.get('provinces',Block([])).scalars()))
   land=[i for i in pids if kinds.get(i)=='land'];assigned.update(land)
   name=clean_name(loc.get(s.get('name'),Path(n).stem.split('-',1)[-1]),loc)
   states[str(sid)]={'id':sid,'name':name,'owner':tag,'controller':h.get('controller',tag),'land_provinces':len(land),'province_ids':land,'file_sha256':hashlib.sha256(data).hexdigest()}
   c=countries.setdefault(tag,{'states':0,'land_provinces':0,'state_ids':[]});c['states']+=1;c['land_provinces']+=len(land);c['state_ids'].append(sid)
  report={'source_archive':Path(path).name,'state_history_sha256':sourcehash.hexdigest(),'definition_sha256':hashlib.sha256(z.read(definition)).hexdigest(),'epoch':[2000,1,1],
   'counts':dict(Counter(kinds.values())),'dummy_id_excluded':True,'state_count':len(states),'assigned_land_provinces':len(assigned),
   'unassigned_land_provinces':sorted(i for i,k in kinds.items() if k=='land' and i not in assigned),'countries':countries,'states':states}
 # Geographic centres are used only as smooth density hints. No source province
 # or state outline is copied into the new geometry.
 old=json.load(open(ROOT/'tools/cartography/baseline_0205/provinces.json'));seen=set();points=[]
 for p in old.values():
  mid=p.get('source_md_province')
  if not mid or mid in seen:continue
  seen.add(mid);u,v=p['map_center'];points.append([mid,round(u*360-180,5),round(90-v*180,5)])
 report['density_centres']={'method':'Geographically registered baseline centres; smoothed hints only. Per-country totals come from the original MD definitions. No MD boundaries reused.','points':points}
 return report

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('archive');a=p.parse_args();r=extract(a.archive)
 (ROOT/'data/md_geography_reference.json').write_text(json.dumps(r,ensure_ascii=False,separators=(',',':')))
 print('MD_REFERENCE',r['state_count'],r['counts'],'assigned',r['assigned_land_provinces'])
