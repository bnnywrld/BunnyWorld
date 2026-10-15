"""Read only country colors and CSTO declarations from the supplied mod ZIP.
Keeps the 0.1 scenario's populations/ownership; never reimports unrelated content.
"""
import hashlib,json,re,sys
from pathlib import Path
from zipfile import ZipFile
from import_md import parse, Block, at_start
root=Path(__file__).resolve().parents[1]
w=json.loads((root/'data/world.json').read_text())
with ZipFile(sys.argv[1]) as z:
 prefix=next(n[:-len('common/countries/colors.txt')] for n in z.namelist() if n.endswith('common/countries/colors.txt'))
 colors=z.read(prefix+'common/countries/colors.txt').decode('utf-8-sig')
 # Country colors use typed rgb blocks; strip the type for the bounded parser.
 changed=[]
 import colorsys
 for tag,c in w['countries'].items():
  block=re.search(r'^'+re.escape(tag)+r'\s*=\s*{(.*?)(?=^\w+\s*=|\Z)',colors,re.M|re.S)
  if not block:continue
  match=re.search(r'\bcolor\s*=\s*(rgb|hsv)?\s*{([^}]+)}',block[1])
  if not match:continue
  vals=list(map(float,match[2].split()))
  rgb=[round(v*255) for v in colorsys.hsv_to_rgb(*vals)] if match[1]=='hsv' else [int(v) for v in vals]
  if c['color']!=rgb:changed.append(tag)
  c['color']=rgb
 members=[]
 for n in z.namelist():
  if not n.startswith(prefix+'history/countries/') or not n.endswith('.txt'):continue
  tag=n[len(prefix+'history/countries/'):][:3]
  if tag not in w['countries']:continue
  hist=Block(at_start(parse(z.read(n).decode('utf-8-sig'))))
  ideas=[]
  for b in hist.values('add_ideas'):ideas.extend(b.scalars() if isinstance(b,Block) else [b])
  if 'CSTO_member' in ideas:members.append(tag)
 w['organizations']['CSTO']={'id':'CSTO','name':'Collective Security Treaty Organization','purpose':'Collective defence; the 2000 treaty framework preceding the formal organization','members':sorted(members),'direction':'Defensive alliance','budget':0.0,'projects':[],'charter':{'voting_rule':'Not yet simulated'}}
 for tag in members:
  if 'CSTO' not in w['countries'][tag]['organizations']:w['countries'][tag]['organizations'].append('CSTO')
 w['patch_source']={'filename':Path(sys.argv[1]).name,'sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'uses':['country color overrides','dated CSTO membership']}
 w['scenario_id']='bunny_world_2000_0_1_1'
 (root/'data/world.json').write_text(json.dumps(w,ensure_ascii=False,separators=(',',':')))
 report={'changed_colors':len(changed),'countries':changed,'CSTO':members,'original_population':sum(r['population'] for r in w['regions'].values())}
 (root/'data/patch_report.json').write_text(json.dumps(report,indent=2))
 print(report)
