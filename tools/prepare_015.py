"""Bounded starting cosmetics and major 2000 organization membership import."""
import json,sys,re,colorsys
from pathlib import Path
from zipfile import ZipFile
from import_md import Block,parse,at_start
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'data/world.json';w=json.loads(p.read_text());cs=w['countries'];orgs=w['organizations']
with ZipFile(sys.argv[1]) as z:
 prefix=next(n[:-len('common/countries/cosmetic.txt')] for n in z.namelist() if n.endswith('common/countries/cosmetic.txt'))
 changes={}
 for n in z.namelist():
  if not n.startswith(prefix+'history/countries/') or not n.endswith('.txt'):continue
  tag=n[len(prefix+'history/countries/'):][:3]
  if tag not in cs:continue
  hist=Block(at_start(parse(z.read(n).decode('utf-8-sig'))));cos=hist.get('set_cosmetic_tag','')
  if isinstance(cos,str):cs[tag]['cosmetic']=cos;changes[tag]=cos
 colors={}
 s=z.read(prefix+'common/countries/cosmetic.txt').decode('utf-8-sig')
 for m in re.finditer(r'^([\w]+)\s*=\s*{\s*color\s*=\s*(rgb|hsv)?\s*{([^}]+)}',s,re.M):
  try:
   vals=list(map(float,m[3].split()));rgb=[round(v*255) for v in colorsys.hsv_to_rgb(*vals)] if m[2]=='hsv' else [int(v) for v in vals]
   if len(rgb)==3 and all(0<=v<=255 for v in rgb):colors[m[1]]=rgb
  except ValueError:pass
 w['cosmetic_colors']=colors
for c in cs.values():c['color_override']=[]
def add(oid,name,purpose,direction,members,source):
 assert all(t in cs for t in members),(oid,[t for t in members if t not in cs])
 orgs[oid]={'id':oid,'name':name,'purpose':purpose,'direction':direction,'members':sorted(set(members)),'budget':0.0,'projects':[],'charter':{'voting_rule':'Not yet simulated'},'membership_source':source}
def idea(key):return [t for t,c in cs.items() if key in c.get('starting_ideas',[])]
add('OAU','Organization of African Unity','Continental cooperation before the African Union','Continental organization',idea('OAU_member'),'Dated mod histories; African Union member accession records (amo.au.int/en/member-states). Morocco absent in 2000.')
add('ARAB','League of Arab States','Cooperation among Arab states','Regional organization',idea('LoAS_member'),'Dated mod histories: LoAS_member, 22 starting states')
add('GCC','Gulf Cooperation Council','Political and economic cooperation in the Gulf','Regional council',idea('idea_gcc_member_state'),'Dated mod histories; six founding members')
# Georgia was a CIS member in 2000 (withdrew 2009); Ukraine participated as a
# founding state without ratifying the charter; Turkmenistan was full then.
add('CIS','Commonwealth of Independent States','Cooperation among former Soviet republics','Intergovernmental association',idea('CIS_member_state_idea')+['GEO','UKR','TRK'],'2000 participating states; UKR included as founding participant, not charter ratifier; TRK before 2005 associate status')
add('APEC','Asia-Pacific Economic Cooperation','Trade and economic cooperation across the Pacific','Economic forum','AST BRU CAN CHI CHL HKG IND JAP KOR MAY MEX NZL PAP PHI PRU SIA SIN SOV TAI USA VIE'.split(),'https://www.apec.org/who-we-are/our-members (all 21 joined by November 1998)')
add('OECD','Organisation for Economic Co-operation and Development','Economic policy and development cooperation','Policy organization','AST AUS BEL CAN CZE DEN ENG FIN FRA GER GRE HOL HUN ICE IRE ITA JAP KOR LUX MEX NRY NZL POL POR SPR SWE SWI TUR USA'.split(),'https://www.oecd.org/en/about/legal.html (29 members on 1 January; Slovakia joined 14 December 2000)')
add('OPEC','Organization of the Petroleum Exporting Countries','Coordination of petroleum policies','Producer organization','ALG IND IRQ PER KUW LBA NIG QAT SAU UAE VEN'.split(),'https://www.opec.org/member-countries.html (Indonesia and Qatar present; Ecuador and Gabon absent in 2000)')
add('MERCOSUR','Southern Common Market','Regional trade and economic integration','Customs union','ARG BRA PAR URG'.split(),'https://www.mercosur.int/en/documents/founding-texts (four founding states; later accessions excluded)')
add('NAFTA','North American Free Trade Agreement','North American trade cooperation','Free trade agreement','CAN MEX USA'.split(),'https://ustr.gov/about-us/policy-offices/press-office/ustr-archives/north-american-free-trade-agreement-nafta')
# 54 active participating states in January, before FR Yugoslavia returned in
# November 2000. Monaco, Vatican etc absent from this territorial game roster.
osce='ALB ARM AUS AZE BEL BLR BOS BUL CAN CRO CYP CZE DEN ENG EST FIN FRA GEO GER GRE HOL HUN ICE IRE ITA KAZ KYR LAT LIT LUX FYR MLT MLV NRY POL POR ROM SLO SLV SPR SOV SWE SWI TAJ TUR UKR USA UZB TRK HLS'.split()
add('OSCE','Organization for Security and Co-operation in Europe','Security, conflict prevention and cooperation','Security organization',osce,'https://www.osce.org/cio/53099 (2000 participants; only territorial countries represented in this game, microstates omitted; FRY inactive until November)')
financial=json.loads((ROOT/'tools/cartography/financial_memberships.json').read_text())
for oid,name,purpose in [('IMF','International Monetary Fund','Monetary cooperation and financial stability'),('IBRD','World Bank (IBRD)','Development finance and reconstruction')]:
 add(oid,name,purpose,'International financial institution',financial['represented_2000'],'Bundled financial_memberships.json: World Bank membership dates; IMF membership history, January 2000 cutoff')
 orgs[oid]['membership_note']='Only members represented in the game are listed. January 2000 memberships precede the return of FR Yugoslavia.'
orgs['OSCE']['membership_note']='Only participating states represented in the game are listed. FR Yugoslavia is excluded until its November 2000 return.'
for oid,o in orgs.items():o['logo']='res://assets/organizations/'+oid+'.png'
for t,c in cs.items():c['organizations']=[oid for oid,o in orgs.items() if t in o['members']]
w['scenario_id']='bunny_world_2000_0_1_5';p.write_text(json.dumps(w,ensure_ascii=False,separators=(',',':')))
(ROOT/'data/cosmetics_import.json').write_text(json.dumps({'starting_cosmetics':{t:v for t,v in changes.items() if v},'cosmetic_colors':len(colors)},indent=2));print('PREPARE_015',len(orgs),'organizations',sum(bool(v) for v in changes.values()),'starting cosmetics')
