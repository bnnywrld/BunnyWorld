"""Directional, dated starting opinion declarations only. No HOI4 script engine.
Repeated applications of the same modifier to a pair replace, not double-count.
Trade-only modifiers are stored separately and excluded from diplomatic opinion.
"""
import json,re,sys,datetime,collections
from zipfile import ZipFile
from pathlib import Path
from import_md import parse,Block,at_start,clean_name
ROOT=Path(__file__).resolve().parents[1];w=json.loads((ROOT/'data/world.json').read_text());cs=w['countries'];definitions={};loc={};pairs={};count=0
with ZipFile(sys.argv[1]) as z:
 prefix=next(n[:-len('history/countries/JAP - Japan.txt')] for n in z.namelist() if n.endswith('history/countries/JAP - Japan.txt'))
 for n in sorted(z.namelist(),key=lambda n:('/replace/' in n,n)):
  if n.startswith(prefix+'localisation/english/') and n.endswith('.yml'):
   for line in z.read(n).decode('utf-8-sig',errors='replace').splitlines():
    m=re.match(r'^\s*([\w.-]+):(?:\d+)?\s*"((?:\\.|[^"\\])*)"',line)
    if m:loc[m[1]]=m[2].replace('\\n',' ')
 for n in z.namelist():
  if n.startswith(prefix+'common/opinion_modifiers/') and n.endswith('.txt'):
   for _,_,root in parse(z.read(n).decode('utf-8-sig')).items:
    if isinstance(root,Block):
     for key,_,b in root.items:
      if not isinstance(b,Block) or not isinstance(b.get('value'),str):continue
      value=float(b.get('value'));decay=max(0,float(b.get('decay','0')));days=float(b.get('days','0'));months=int(b.get('months','0'));years=int(b.get('years','0'));expires=-1
      if days>0 or months>0 or years>0:
       m=years*12+months;end=datetime.datetime(min(2999,2000+m//12),1+m%12,1)+datetime.timedelta(days=days);expires=(end-datetime.datetime(2000,1,1)).total_seconds()/3600
      definitions[key]={'name':clean_name(loc.get(key,key.replace('_',' ')),loc),'value':value,'decay_per_month':decay,'expires_hour':expires,'trade_only':b.get('trade')=='yes'}
 for n in z.namelist():
  if not n.startswith(prefix+'history/countries/') or not n.endswith('.txt'):continue
  tag=n[len(prefix+'history/countries/'):][:3]
  if tag not in cs:continue
  h=Block(at_start(parse(z.read(n).decode('utf-8-sig'))))
  for key in ['add_opinion_modifier','reverse_add_opinion_modifier']:
   for b in h.values(key):
    if not isinstance(b,Block) or b.get('target') not in cs or b.get('modifier') not in definitions:continue
    a,t=(tag,b.get('target')) if key=='add_opinion_modifier' else (b.get('target'),tag)
    if a==t:continue
    ids=pairs.setdefault(a+'|'+t,[]);mid=b.get('modifier')
    if mid not in ids:ids.append(mid)
    count+=1
 # The supplied file has the localized name but no bare LEB key.
 cs['LEB']['name']=clean_name(loc['LEB_neutrality'],loc)
data={'definitions':definitions,'pairs':pairs,'source':'Dated starting add_opinion_modifier and reverse_add_opinion_modifier from supplied bunnyversion.zip','decay_convention':'Points per elapsed month; durations in calendar days/months/years from scenario start. No engine-generated ideological/faction/war baselines or startup scripts simulated.'}
(ROOT/'data/relations.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')));(ROOT/'data/world.json').write_text(json.dumps(w,ensure_ascii=False,separators=(',',':')))
print('RELATIONS_IMPORTED',count,'declarations',len(pairs),'directed pairs',sum(len(v) for v in pairs.values()),'unique contributions')
