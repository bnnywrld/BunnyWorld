"""Import year-2000 MD resources, rights, building workforce, elections and inactive diplomacy.
Canonical topology is retained. Named resource pools prefer their matching canonical
state; unmatched/split pools are area-apportioned once. Data Center staffing is a
BunnyWorld balance addition of 10,000 employees per level, not an MD coefficient.
"""
import argparse, hashlib, json, re, zipfile
from collections import defaultdict
from pathlib import Path
from import_md import parse, Block, at_start, clean_name
ROOT = Path(__file__).resolve().parents[1]
WORKERS = {'civ_fac':'industrial_complex','mil_fac':'arms_factory','dockyard':'dockyard','office':'offices','agriculture_district':'agriculture_district','microchip_plant':'microchip_plant','composite_plant':'composite_plant','synthetic_refinery':'synthetic_refinery','nuclear_reactor':'nuclear_reactor','fossil_powerplant':'fossil_powerplant','renewable_energy':'renewable_energy_infra','internet_station':'internet_station','rail_terminal':'rail_terminal'}
RESOURCE_NAMES = {'oil':'Fossil fuels','aluminium':'Light metals','rubber':'Rubber','tungsten':'Technology metals','steel':'Steel','chromium':'Precious metals','microchips':'Microchips','composites':'Composites'}
NATIVE = {'war':'Declare war','justify_war_goal':'Justify war goal','offer_peace':'Offer peace','improve_relations':'Improve relations','stop_improve_relations':'Stop improving relations','guarantee':'Guarantee independence','revoke_guarantee':'Revoke guarantee','non_aggression_pact':'Offer non-aggression pact','cancel_non_aggression_pact':'Cancel non-aggression pact','military_access':'Request military access','offer_military_access':'Offer military access','cancel_military_access':'Cancel military access','revoke_military_access':'Revoke military access','docking_rights':'Request docking rights','offer_docking_rights':'Offer docking rights','cancel_docking_rights':'Cancel docking rights','revoke_docking_rights':'Revoke docking rights','invite_to_faction':'Invite to alliance','join_faction':'Ask to join alliance','leave_faction':'Leave alliance','kick_from_faction':'Expel from alliance','offer_lend_lease':'Offer lend-lease','request_lend_lease':'Request lend-lease','cancel_lend_lease':'Cancel lend-lease','send_volunteers':'Send intervention forces','send_attache':'Send attaché','recall_attache':'Recall attaché','embargo':'Embargo','lift_embargo':'Lift embargo','license_production':'Request production license','cancel_license_production':'Cancel production license','expeditionary_force':'Send expeditionary force','request_expeditionary_force':'Request forces','return_expeditionary_force':'Return expeditionary force','release_subject':'Grant independence','reduce_autonomy':'Reduce autonomy','increase_autonomy':'Increase autonomy'}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('archive',type=Path);args=ap.parse_args()
 world=json.loads((ROOT/'data/world.json').read_text(encoding='utf-8'));sources={};hashes={};loc={};elections={};actions={}
 with zipfile.ZipFile(args.archive) as z:
  def read(path):
   raw=z.read(path);hashes[path]=hashlib.sha256(raw).hexdigest();return raw.decode('utf-8-sig',errors='replace')
  for path in sorted(z.namelist(),key=lambda x:('/replace/' in x,x)):
   if '/localisation/english/' in path and path.endswith('.yml'):
    for line in read(path).splitlines():
     m=re.match(r'^\s*([\w.-]+):\d*\s*"((?:\\.|[^"\\])*)"',line)
     if m:loc[m[1]]=m[2].replace('\\"','"').replace('\\n',' ')
  for path in sorted(z.namelist()):
   if '/history/states/' in path and path.endswith('.txt'):
    b=parse(read(path)).get('state');sid=str(b.get('id'));rights={'cores':set(),'claims':set()};owner=''
    for key,_,value in at_start(b.get('history',Block([]))):
     if key=='owner':owner=value
     if key in ('add_core_of','add_claim_by'):rights['cores' if key=='add_core_of' else 'claims'].add(value)
     if key in ('remove_core_of','remove_claim_by'):rights['cores' if key=='remove_core_of' else 'claims'].discard(value)
    resources={k:float(v) for k,_,v in b.get('resources',Block([])).items if k in RESOURCE_NAMES and not isinstance(v,Block)}
    source_name=loc.get(b.get('name',''),'') or re.sub(r'^\d+\s*-\s*','',Path(path).stem)
    sources[sid]={'owner':owner,'name':source_name,'resources':resources,**{k:sorted(v) for k,v in rights.items()}}
   if '/history/countries/' in path and path.endswith('.txt'):
    m=re.search(r'/([A-Z0-9]{3})\b',path)
    if not m or m[1] not in world['countries']:continue
    politics={}
    for key,_,value in at_start(parse(read(path))):
     if key=='set_politics' and isinstance(value,Block):politics.update({k:v for k,_,v in value.items})
    elections[m[1]]={'allowed':politics.get('elections_allowed')=='yes','last':politics.get('last_election',''),'frequency_months':int(politics.get('election_frequency',0))}
   if '/common/scripted_diplomatic_actions/' in path and path.endswith('.txt'):
    for key,_,value in parse(read(path)).get('scripted_diplomatic_actions',Block([])).items:
     if not isinstance(value,Block):continue
     aliases={'aisend_attache':'send_attache','airecall_attache':'recall_attache'};aid=aliases.get(key,key)
     name=loc.get(key,loc.get(key.upper()+'_TITLE',loc.get(key.upper(),'')))
     if not name or '[' in name or '$' in name:name=NATIVE.get(aid,key.replace('diplo_action_','').replace('CPD_','').replace('_',' ').capitalize())
     name=re.sub(r'§.','',clean_name(name,loc))
     actions[aid]={'name':name,'source':path,'source_id':key,'inactive':True}
  for aid,label in NATIVE.items():
   if aid not in actions:actions[aid]={'name':label,'source':'MD inherited engine diplomacy','source_id':aid,'inactive':True}
  gui_path='New folder/common/scripted_guis/01_influence_scripted_guis.txt';gui=read(gui_path)
  gui_actions={'opt_influence_action_button':('spread_influence','Spread influence'),'opt_aid_button':('economic_aid','Send economic aid'),'opt_aid_military_button':('military_aid','Send military aid'),'opt_military_supply_button':('military_supply','Send military supplies'),'opt_target_other_button':('target_foreign_influence','Target foreign influence'),'opt_manipulate_politics_button':('manipulate_politics','Manipulate politics'),'opt_coup_button':('stage_coup','Stage coup'),'opt_make_puppet_button':('make_puppet','Make puppet'),'opt_economic_exploitation_button':('economic_exploitation','Economic exploitation')}
  for button,(aid,title) in gui_actions.items():
   assert button+'_click = {' in gui
   actions[aid]={'name':title,'source':gui_path,'source_id':button,'inactive':True}
  engine_gui='New folder/interface/countrydiplomacyview.gui';engine=read(engine_gui)
  for aid,title in {'boost_party_popularity':'Boost party popularity','create_faction':'Create alliance'}.items():
   assert aid in engine
   actions[aid]={'name':title,'source':engine_gui,'source_id':aid,'inactive':True}
  money_path='New folder/common/scripted_effects/00_money_system.txt';money=read(money_path)
  workers={WORKERS[k]:int(round(float(v)*1e6)) for k,v in re.findall(r'set_temp_variable\s*=\s*\{\s*workers_per_(\w+)\s*=\s*([0-9.]+)\s*\}',money) if k in WORKERS}
  assert len(workers)==13,workers
  workers['data_center']=10000 # BunnyWorld provisional balance; not an MD coefficient.
 candidates=defaultdict(list)
 for sid,r in world['regions'].items():
  for source in r.get('source_states',[]):candidates[str(source)].append(sid)
 records={}
 states={sid:{'resources':{},'cores':[],'claims':[],'source_states':r.get('source_states',[])} for sid,r in world['regions'].items()}
 totals=defaultdict(float);mapped=defaultdict(float);unmapped=[];unknown=set();known=set(world['countries'])|set(world['country_registry'])
 for source,s in sources.items():
  destinations=candidates[source]
  if not destinations:
   if any(s['resources'].values()):unmapped.append(source)
   continue
  # Keep pools on the existing source owner's territory where possible. A split
  # source state never creates a copy of its entire resource quantity per child.
  owned=[sid for sid in destinations if world['regions'][sid]['owner']==s['owner']]
  recipients=owned or destinations
  normalize=lambda name:re.sub(r'[^a-z0-9]','',name.casefold())
  matching=[sid for sid in recipients if normalize(world['regions'][sid]['name'])==normalize(s['name'])]
  # Exact canonical names avoid leaking California's pool into neighboring states
  # merely because their province sampling also touched the source state.
  recipients=matching or recipients;weight=sum(max(.001,world['regions'][sid]['area_km2']) for sid in recipients)
  for resource,amount in s['resources'].items():
   totals[resource]+=amount;remaining=amount
   for index,sid in enumerate(recipients):
    part=remaining if index==len(recipients)-1 else round(amount*max(.001,world['regions'][sid]['area_km2'])/weight,6)
    remaining-=part;states[sid]['resources'][resource]=round(states[sid]['resources'].get(resource,0)+part,6);mapped[resource]+=part
  for sid in destinations:
   for field in ['cores','claims']:
    for tag in s[field]:
     if tag in known:states[sid][field].append(tag)
     else:
      unknown.add(tag)
      name=loc.get(tag+'_neutrality',loc.get(tag,tag))
      if name != tag:
       records[tag]={'tag':tag,'name':name,'outlook':'Unspecified','color':[113,135,147],'cosmetic':'','starting_stats':{}}
       states[sid][field].append(tag)
 for state in states.values():
  for field in ['cores','claims']:state[field]=sorted(set(state[field]))
  state['resources']={k:v for k,v in state['resources'].items() if v>0}
 for key in RESOURCE_NAMES:assert abs(totals[key]-mapped[key])<1e-5
 output={'source':{'archive':args.archive.name,'files':hashes,'policy':__doc__},'resources':RESOURCE_NAMES,'country_records':records,'workers_per_level':workers,'states':states,'elections':elections,'diplomatic_actions':actions,'report':{'unmapped_resource_sources':unmapped,'added_country_records':sorted(records),'unresolved_rights_tags':sorted(unknown-set(records)),'resource_totals':dict(totals),'mapped_totals':dict(mapped),'staffing_scope':'MD base workers per level, including dependent retail/services jobs where MD includes them. No automation, country modifiers, resource-sector/subsistence or defense manpower inferred.'}}
 (ROOT/'data/state_economy_2000.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
 print(len(states),'states;',len(workers),'staffed building types;',len(actions),'inactive actions; unmapped resources',unmapped,'added country records',sorted(records),'unresolved rights',sorted(unknown-set(records)))
if __name__=='__main__':main()
