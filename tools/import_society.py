"""Import MD party names/support and available logo references; never run scripts.

Country history is bounded to 2000-01-01. Explicit per-outlook support rescales
the declared party array within that outlook, as MD's startup calculation does.
Missing groups are left unrepresented rather than using MD's random fill-in.
"""
import argparse
import colorsys
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from PIL import Image
from import_md import Block, parse, at_start, clean_name

ROOT = Path(__file__).resolve().parents[1]
IDEAS = ['Western_Autocracy','conservatism','liberalism','socialism','communist_state','anarchist_communism','Conservative','Autocracy','Mod_Vilayat_e_Faqih','Vilayat_e_Faqih','Kingdom','Caliphate','Neutral_Muslim_Brotherhood','Neutral_Autocracy','Neutral_conservatism','oligarchism','Neutral_Libertarian','Neutral_green','neutral_Social','Neutral_Communism','Nat_Populism','Nat_Fascism','Nat_Autocracy','Monarchist']
OUTLOOKS = {'democratic':'Western Outlook','communism':'Multipolar Outlook','neutrality':'Non-Aligned Outlook','nationalist':'Nationalist Outlook'}
COLORS = {'Western Outlook':'498fe0','Multipolar Outlook':'d75650','Non-Aligned Outlook':'d7b553','Nationalist Outlook':'aa77cc'}

def family(index):
    return 'democratic' if index < 4 else ('communism' if index < 10 else ('fascism' if index < 12 else ('neutrality' if index < 20 else 'nationalist')))

def condition(block, tag, flags, focuses, cosmetic):
    result = []
    for key, op, value in block.items:
        if key in ('AND','ROOT'): v = condition(value,tag,flags,focuses,cosmetic)
        elif key == 'NOT':
            x = condition(value,tag,flags,focuses,cosmetic); v = None if x is None else not x
        elif key == 'OR':
            xs = [condition(Block([item]),tag,flags,focuses,cosmetic) for item in value.items]
            v = True if True in xs else (None if None in xs else False)
        elif key in ('original_tag','tag','TAG'): v = value == tag
        elif key == 'always': v = value == 'yes'
        elif key == 'has_dlc': v = True
        elif key == 'has_country_flag': v = value in flags
        elif key == 'has_completed_focus': v = value in focuses
        elif key == 'has_cosmetic_tag': v = value == cosmetic
        elif key == 'date':
            date = tuple(map(int,value.split('.')[:3])); start = (2000,1,1)
            v = {'<':start<date,'>':start>date,'=':start==date,'<=':start<=date,'>=':start>=date}[op]
        else: v = None
        result.append(v)
    return False if False in result else (None if None in result else True)

def main():
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('archive',type=Path); args = ap.parse_args()
    world = json.loads((ROOT/'data/world.json').read_text(encoding='utf-8'))
    countries, loc, hashes, selectors, sprites = {}, {}, {}, {}, {}
    report = {'excluded_indices':[10,11], 'missing_history':[], 'missing_country_names':[], 'missing_logos':[], 'unsupported_history_conditions':0}
    with zipfile.ZipFile(args.archive) as z:
        paths = {p.lower():p for p in z.namelist()}
        def read(path):
            raw = z.read(path); hashes[path] = hashlib.sha256(raw).hexdigest(); return raw.decode('utf-8-sig',errors='replace')
        for path in sorted(z.namelist(),key=lambda p:('/replace/' in p,p)):
            if '/localisation/english/' in path and path.endswith('.yml'):
                for line in read(path).splitlines():
                    m = re.match(r'^\s*([\w.-]+):\d*\s*"((?:\\.|[^"\\])*)"',line)
                    if m: loc[m[1]] = m[2].replace('\\"','"').replace('\\n',' ')
        for path in sorted(z.namelist()):
            if '/common/scripted_localisation/' in path and path.endswith('.txt') and ('politics' in path):
                for b in parse(read(path)).values('defined_text'):
                    if b.get('name') in [key+'_L' for key in IDEAS]: selectors[b.get('name')] = b.values('text')
            if '/interface/' in path and 'parties_icons' in path and path.endswith('.gfx'):
                container = parse(read(path)).get('spriteTypes',Block([]))
                for b in container.values('spriteType'): sprites[str(b.get('name')).lower()] = b.get('texturefile','')
        history_paths = {}
        for path in z.namelist():
            m = re.search(r'/history/countries/([A-Z0-9]{3})\b',path)
            if m and path.endswith('.txt'): history_paths[m[1]] = path
        for tag, country in world['countries'].items():
            values, popularities, flags, focuses = {}, {}, set(), set()
            cosmetic = country.get('cosmetic','')
            def history(b):
                nonlocal cosmetic
                previous = False
                for key, _, value in at_start(b):
                    if key == 'set_variable' and isinstance(value,Block):
                        for k,_,v in value.items:
                            if k and k.startswith('party_pop_array^') and re.fullmatch(r'party_pop_array\^\d+',k): values[int(k.split('^')[1])] = float(v)
                    elif key == 'set_popularities':
                        for k,_,v in value.items: popularities[k] = float(v)
                    elif key == 'set_country_flag': flags.add(value.get('flag','') if isinstance(value,Block) else value)
                    elif key == 'clr_country_flag': flags.discard(value.get('flag','') if isinstance(value,Block) else value)
                    elif key == 'complete_national_focus': focuses.add(value)
                    elif key == 'set_cosmetic_tag': cosmetic = value
                    elif key in ('if','else_if','else') and isinstance(value,Block):
                        if key == 'if': previous = False
                        if previous is True or previous is None: continue
                        matched = condition(value.get('limit',Block([])),tag,flags,focuses,cosmetic)
                        if matched is None: report['unsupported_history_conditions'] += 1; previous = None
                        elif matched: history(value); previous = True
            if tag in history_paths: history(parse(read(history_paths[tag])))
            else: report['missing_history'].append(tag)
            totals = {key:sum(v for i,v in values.items() if family(i)==key) for key in OUTLOOKS}
            parties = []
            for index, ideology in enumerate(IDEAS):
                group = family(index)
                if group not in OUTLOOKS: continue
                key = ''
                for choice in selectors.get(ideology+'_L',[]):
                    if condition(choice.get('trigger',Block([])),tag,flags,focuses,cosmetic) is True:
                        candidate = choice.get('localization_key','')
                        if candidate in loc: key = candidate; break
                if not key: key = tag+'.'+ideology if tag+'.'+ideology in loc else ideology
                raw = clean_name(loc.get(key,ideology.replace('_',' ')),loc)
                logo_ref = (re.findall(r'£([\w.-]+)',raw) or re.findall(r'£([\w.-]+)',loc.get(key+'_icon','')) or [''])[0]
                name = re.sub(r'£[\w.-]+','',raw).strip()
                if '[' in name or '$' in name: name = clean_name(loc.get(ideology,ideology.replace('_',' ')),loc)
                generic = not key.startswith(tag+'.') and not re.match(r'^[A-Z0-9]{3}\.',key)
                if generic: report['missing_country_names'].append(tag+':'+str(index))
                value = max(0,values.get(index,0))
                support = value/totals[group]*popularities[group] if totals[group]>0 and group in popularities else value*100
                base = COLORS[OUTLOOKS[group]]
                rgb = tuple(int(base[i:i+2],16)/255 for i in (0,2,4)); h,s,v = colorsys.rgb_to_hsv(*rgb)
                shade = colorsys.hsv_to_rgb(h,max(.35,s-(index%4)*.09),max(.4,v-(index%3)*.12))
                color = ''.join(f'{round(c*255):02x}' for c in shade)
                logo_path = sprites.get(('GFX_'+logo_ref).lower(),'')
                asset = ''
                actual = paths.get(('New folder/'+logo_path).lower())
                if actual:
                    raw_image = z.read(actual); digest = hashlib.sha256(raw_image).hexdigest()
                    hashes[actual] = digest
                    target = ROOT/'assets/ui/parties'/f'{digest[:20]}.png'; target.parent.mkdir(parents=True,exist_ok=True)
                    try:
                        image = Image.open(io.BytesIO(raw_image)).convert('RGBA'); image.thumbnail((96,96)); image.save(target)
                        asset = 'res://'+target.relative_to(ROOT).as_posix()
                    except (OSError,ValueError): pass
                if logo_ref and not asset: report['missing_logos'].append({'party':tag+':'+str(index),'sprite':logo_ref,'path':logo_path})
                parties.append({'id':str(index),'name':name,'outlook':OUTLOOKS[group],'support':round(support,8),'color':color,'logo':asset,'logo_reference':logo_ref,'source_key':key,'generic':generic})
            represented = sum(p['support'] for p in parties)
            # Do not invent votes if the source declarations are incomplete.
            if represented > 100.00001: raise ValueError('Party support exceeds 100: '+tag)
            countries[tag] = {'parties':parties,'unrepresented':round(max(0,100-represented),8)}
    output = {'source':{'archive':args.archive.name,'files':hashes,'policy':__doc__},'outlooks':OUTLOOKS,'colors':COLORS,'countries':countries,'report':report}
    (ROOT/'data/parties_2000.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(len(countries),'countries;',sum(len(c['parties']) for c in countries.values()),'party slots;',len(report['missing_logos']),'missing logo references')

if __name__ == '__main__': main()
