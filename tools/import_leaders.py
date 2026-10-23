"""Import starting MD leaders and explicit ruling/coalition party IDs at 2000-01-01.
Unknown conditional branches and future leaders are never guessed. Cabinet mechanics
remain inactive. Portrait references are retained even when the archive lacks images.
"""
import argparse, hashlib, json, re, zipfile
from pathlib import Path
from import_md import parse, Block, at_start, clean_name
from import_society import condition, IDEAS, family
ROOT = Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('archive',type=Path); args=ap.parse_args()
    world=json.loads((ROOT/'data/world.json').read_text(encoding='utf8'))
    laws=json.loads((ROOT/'data/government_laws_2000.json').read_text(encoding='utf8'))['countries']
    countries={}; hashes={}; loc={}; sprites={}; ideas={}; characters={}; report={'missing_leaders':[], 'missing_portraits':0,'unresolved_conditions':0,'excluded_ruling_parties':[]}
    portrait_manifest=ROOT/'data/leader_portraits.json'
    portraits=json.loads(portrait_manifest.read_text(encoding='utf8'))['entries'] if portrait_manifest.exists() else {}
    with zipfile.ZipFile(args.archive) as z:
        def read(p):
            raw=z.read(p); hashes[p]=hashlib.sha256(raw).hexdigest()
            try: return raw.decode('utf-8-sig')
            except UnicodeDecodeError: return raw.decode('cp1252')
        for p in sorted(z.namelist(),key=lambda p:('/replace/' in p,p)):
            if '/localisation/english/' in p and p.endswith('.yml'):
                for line in read(p).splitlines():
                    m=re.match(r'^\s*([\w.-]+):\d*\s*"((?:\\.|[^"\\])*)"',line)
                    if m: loc[m[1]]=m[2].replace('\\"','"').replace('\\n',' ')
            if '/interface/' in p and p.endswith('.gfx'):
                for b in parse(read(p)).get('spriteTypes',Block([])).values('spriteType'):
                    if isinstance(b,Block): sprites[str(b.get('name','')).lower()]=b.get('texturefile','')
            if '/common/ideas/' in p and p.endswith('.txt'):
                for _,_,group in parse(read(p)).get('ideas',Block([])).items:
                    if isinstance(group,Block):
                        for key,_,b in group.items:
                            if isinstance(b,Block): ideas[key]=(b,p)
            if '/common/characters/' in p and p.endswith('.txt'):
                for key,_,b in parse(read(p)).get('characters',Block([])).items:
                    if isinstance(b,Block): characters[key]=b
        paths={}
        for p in z.namelist():
            m=re.search(r'/history/countries/([A-Z0-9]{3})\b',p)
            if m and p.endswith('.txt'): paths[m[1]]=p
        for tag,c in world['countries'].items():
            leaders=[]; flags=set(); focuses=set(); coalition=[]; ruling=None; outlook=''; active_ideas=[]; cosmetic=c.get('cosmetic','')
            def history(b):
                nonlocal ruling,outlook,cosmetic
                previous=False
                for k,_,v in at_start(b):
                    if k=='create_country_leader' and isinstance(v,Block): leaders.append(v)
                    elif k=='recruit_character' and v in characters:
                        character=characters[v]
                        for leader in character.values('country_leader'):
                            if not isinstance(leader,Block): continue
                            portraits=character.get('portraits',Block([])).get('civilian',Block([]))
                            leaders.append(Block([('name','=',character.get('name',v)),('picture','=',portraits.get('large','')),('ideology','=',leader.get('ideology',''))]))
                    elif k=='set_politics' and isinstance(v,Block): outlook=v.get('ruling_party',outlook)
                    elif k=='set_variable' and isinstance(v,Block) and v.get('ruling_party') is not None: ruling=int(float(v.get('ruling_party')))
                    elif k=='add_to_array' and isinstance(v,Block) and v.get('gov_coalition_array') is not None: coalition.append(int(float(v.get('gov_coalition_array'))))
                    elif k=='clear_array' and v=='gov_coalition_array': coalition.clear()
                    elif k=='add_ideas': active_ideas.extend([x for _,_,x in v.items] if isinstance(v,Block) else [v])
                    elif k=='remove_ideas':
                        for x in ([x for _,_,x in v.items] if isinstance(v,Block) else [v]):
                            if x in active_ideas: active_ideas.remove(x)
                    elif k=='set_country_flag': flags.add(v.get('flag','') if isinstance(v,Block) else v)
                    elif k=='clr_country_flag': flags.discard(v.get('flag','') if isinstance(v,Block) else v)
                    elif k=='complete_national_focus': focuses.add(v)
                    elif k=='set_cosmetic_tag': cosmetic=v
                    elif k in ('if','else_if','else') and isinstance(v,Block):
                        if k=='if': previous=False
                        if previous is True or previous is None: continue
                        match=condition(v.get('limit',Block([])),tag,flags,focuses,cosmetic)
                        if match is None: report['unresolved_conditions']+=1; previous=None
                        elif match: history(v); previous=True
            if tag in paths: history(parse(read(paths[tag])))
            # Only the explicitly declared ruling ideology/outlook selects a leader.
            candidates=[b for b in leaders if ruling is not None and 0<=ruling<len(IDEAS) and b.get('ideology')==IDEAS[ruling]]
            if not candidates: candidates=[b for b in leaders if b.get('ideology') in IDEAS and family(IDEAS.index(b.get('ideology')))==outlook]
            selected=candidates[-1] if candidates else (leaders[0] if len(leaders)==1 else None)
            roles={'head_of_state':None,'head_of_government':None}
            if selected:
                government=laws[tag]
                form=government.get('form_of_government','')
                role='head_of_government' if ('Monarchy' in form and form!='Absolute Monarchy') or government.get('executive')=='Parliamentary' else 'head_of_state'
                reference=selected.get('picture','')
                roles[role]={'name':clean_name(selected.get('name',''),loc),'portrait_reference':reference,'portrait':'','source':paths[tag],'role_basis':'Starting constitution/executive and MD ruling leader'}
                if ruling is None and selected.get('ideology') in IDEAS: ruling=IDEAS.index(selected.get('ideology'))
            else: report['missing_leaders'].append(tag)
            # Explicit monarch ideas are a second named office, not a duplicate leader.
            for key in active_ideas:
                if key not in ideas or not re.search(r'(emperor|king_|queen_|monarch)',key,re.I): continue
                b,p=ideas[key]; name=clean_name(loc.get(key,''),loc)
                if not name or name in ('King','Queen','Emperor','Monarch') or any(x in name.lower() for x in ['monarchy','monarchism','monarchist','monarchists','movement','support','legacy']): continue
                if roles['head_of_state'] is None:
                    roles['head_of_state']={'name':re.sub(r'§.','',name),'portrait_reference':sprites.get(('GFX_idea_'+b.get('picture','')).lower(),b.get('picture','')),'portrait':'','source':p,'role_basis':'Explicit starting monarch idea'}
            # England supplies its monarch as a country flag rather than a second leader.
            if tag=='ENG' and 'ENG_elizabeth_ruling_monarch' in flags and roles['head_of_state'] is None:
                name=loc.get('ENG_elizabeth_queen','')
                if name: roles['head_of_state']={'name':clean_name(name,loc),'portrait_reference':'','portrait':'','source':paths[tag],'role_basis':'Explicit starting monarch flag and localization'}
            supported=lambda i: i is not None and 0<=i<24 and i not in (10,11)
            if ruling in (10,11): report['excluded_ruling_parties'].append(tag)
            countries[tag]={**roles,'ruling_party':str(ruling) if supported(ruling) else '', 'coalition':sorted({str(i) for i in coalition if supported(i) and i!=ruling},key=int)}
            for role,person in roles.items():
                asset=portraits.get(tag+':'+role,{})
                if person and asset.get('name')==person['name'] and asset.get('reference')==person['portrait_reference']:
                    person['portrait']=asset['asset']
            report['missing_portraits']+=sum(1 for x in roles.values() if x and not x['portrait'])
    out={'source':{'archive':args.archive.name,'files':hashes,'policy':__doc__},'countries':countries,'report':report}
    (ROOT/'data/leaders_2000.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print(len(countries),'countries;',report)
if __name__=='__main__': main()
