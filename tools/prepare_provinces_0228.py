"""Merge approved states and allocate population-aware province budgets.

Input is .27. This phase never redraws a coast or transfers ownership.
The report is written before province generation. No camera click-size rule.
"""
from pathlib import Path
from collections import Counter, defaultdict
import copy, hashlib, json, math
import numpy as np
R=Path(__file__).resolve().parents[1]
B=R/'tools/cartography/baseline_0227'
read=lambda p:json.loads((R/p).read_text())
def write(p,d): (R/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
def merged_profile(ids,target,w,sd,rt):
    total=sum(w['regions'][str(i)]['population'] for i in ids)
    p=copy.deepcopy(sd['states'][str(target)])
    weights=np.array([w['regions'][str(i)]['population'] for i in ids],float)
    if weights.sum()==0:weights[:]=1
    singles=np.average([sd['states'][str(i)]['age_single_year'] for i in ids],axis=0,weights=weights)
    age=Counter();religion=Counter();education=Counter();work=Counter();adults=0
    for i in ids:
        e=rt['states'][str(i)]
        for key,dest in [('age',age),('religion',religion),('education',education)]:dest.update(e['metrics'][key]['counts'])
        adults+=e['metrics']['education']['denominator']
        for k in ['working_age','labour_force','employed','unemployed','outside_labour_force']:work[k]+=e['workforce'][k]
    # Preserve rounded .27 group totals exactly at the baseline retirement age.
    age['Adult working']=adults-age['Retired'];age['Young working']=age['Working age']-age['Adult working']
    for lo,hi,name in [(0,18,'Underage'),(18,25,'Young working'),(25,65,'Adult working'),(65,101,'Retired')]:
        if singles[lo:hi].sum()>0:singles[lo:hi]*=(age[name]/max(total,1))/singles[lo:hi].sum()
    if total==0:singles/=singles.sum()
    p.update(state=target,population_2000=total,age_single_year=singles.tolist(),adult25_share=adults/max(total,1),population_source='Sum of approved .27 state populations; no population reassignment',merged_from=ids)
    age.pop('Adult working',None);age.pop('Young working',None)
    for key,counts,denom in [('age',age,total),('religion',religion,total),('education',education,adults)]:
        m=p['metrics'][key]
        if denom:m['shares']={k:v/denom for k,v in counts.items()}
        m.update(source='Population/adult-weighted union of .27 state profiles '+str(ids),status='Preserved historical estimates; merged counts, not averaged percentages',reference='tools/cartography/baseline_0227/runtime_demographics.json; documentation/PROVINCES_0228.md',year=2000)
    p['workforce'].update(participation_rate=work['labour_force']/max(work['working_age'],1),unemployment_rate=work['unemployed']/max(work['labour_force'],1),source='Sum of .27 workforce counts across approved state union',status='Preserved modeled workforce; independent rates recalculated')
    p['merge_audit']={'metrics':{'age':dict(age),'religion':dict(religion),'education':dict(education)},'adult25':adults,'workforce':dict(work)}
    p['context']={'merged_from':ids,'national_capital':any(sd['states'][str(i)].get('context',{}).get('national_capital',False)for i in ids)}
    return p
def capped_alloc(total,weights,caps):
    n=np.ones(len(caps),dtype=int);caps=np.array(caps,int);weights=np.array(weights,float)
    left=min(total,int(caps.sum()))-len(n)
    while left>0:
        room=caps-n;eligible=room>0
        ww=np.where(eligible,weights,0.)
        if ww.sum()==0:ww=eligible.astype(float)
        exact=left*ww/ww.sum();add=np.minimum(room,np.floor(exact).astype(int));n+=add;left-=int(add.sum())
        if not left:break
        order=np.argsort(-(exact-np.floor(exact)),kind='stable')
        made=0
        for j in order:
            if n[j]<caps[j]:n[j]+=1;left-=1;made+=1
            if not left:break
        if not made:break
    return n
def main():
    w,ps,sd=read('data/world.json'),read('data/provinces.json'),read('data/state_demographics.json')
    assert w['version']=='0.2.0.27','Start from .27; do not merge twice'
    rt=json.loads((B/'runtime_demographics.json').read_text());before=copy.deepcopy(w);merges={622:624,623:624,1758:1750}
    unions=[([622,623,624],624,'Lebanon'),([1750,1758],1750,'Golan Heights')]
    for ids,target,name in unions:
        assert len({w['regions'][str(i)]['owner']for i in ids})==1
        p=merged_profile(ids,target,before,sd,rt);s=copy.deepcopy(w['regions'][str(target)])
        s.update(name=name,population=p['population_2000'],area_km2=sum(w['regions'][str(i)]['area_km2']for i in ids),provinces=sorted(v for i in ids for v in w['regions'][str(i)]['provinces']),building_slot_baseline=sum(w['regions'][str(i)]['building_slot_baseline']for i in ids),workforce=p['workforce'],population_source=p['population_source'])
        bc=Counter()
        for i in ids:bc.update(w['regions'][str(i)]['buildings'])
        s['buildings']=dict(bc)
        for field in ['cores','claims','source_states','geographic_divisions','geographic_codes','protected_territories']:s[field]=sorted({v for i in ids for v in w['regions'][str(i)].get(field,[])})
        s['geography_0228']={'merged_from':ids,'method':'Union of accepted state footprints; starting ownership retained'}
        for i in ids:
            if i!=target:del w['regions'][str(i)];del sd['states'][str(i)]
        w['regions'][str(target)]=s;sd['states'][str(target)]=p
    for p in ps.values():p['region']=merges.get(p['region'],p['region'])
    for c in w['countries'].values():
        c['regions']=sorted(s['id']for s in w['regions'].values()if s['owner']==c['tag']) if 'tag'in c else c['regions']
        c['capital']=merges.get(c['capital'],c['capital'])
    for tag,c in w['countries'].items():c['regions']=sorted(s['id']for s in w['regions'].values()if s['owner']==tag)
    for s in w['regions'].values():s['neighbors']=sorted({merges.get(i,i)for i in s['neighbors']}-{s['id']})
    protected=read('data/protected_territories_0210.json')
    for p in protected['territories']:
        p['states']=sorted({merges.get(i,i)for i in p['states']})
        if p.get('code')=='B58':p.update(boundary_reserved=False,policy='Shebaa Farms absorbed into Golan Heights by approved .28 merge; no separate state boundary.')
    protected['version']='0.2.0.28';write('data/protected_territories_0210.json',protected)
    # Resolve current accepted state geometry from canonical province IDs.
    from build_boundary_hint import atlas
    olda=atlas();lut=np.zeros(65536,np.uint16);lut[65535]=8191
    for p in ps.values():lut[p['id']]=p['region']
    a=lut[olda]
    np.savez_compressed(R/'tools/cartography/states_0228.npz',regions=a)
    ref=read('data/md_geography_reference.json');country_rows=[];state_rows=[];budgets={}
    min_area=400.;scale=1.0
    for tag,c in sorted(w['countries'].items()):
        ss=sorted([s for s in w['regions'].values()if s['owner']==tag],key=lambda s:s['id'])
        md=ref['countries'].get(tag,{}).get('land_provinces');oldcount=sum(len(s['provinces'])for s in ss)
        target=max(len(ss),round(md*scale))if md is not None else max(len(ss),oldcount)
        caps=[max(1,min(3,math.floor(s['area_km2']/min_area)))if s['area_km2']<2500 else max(1,math.floor(s['area_km2']/min_area))for s in ss]
        weights=[math.sqrt(max(s['area_km2'],0)*max(s['population'],0))for s in ss]
        ns=capped_alloc(target,weights,caps)
        for s,cap,n in zip(ss,caps,ns):
            budgets[str(s['id'])]=int(n)
            state_rows.append({'state':s['id'],'country':tag,'name':s['name'],'area_km2':s['area_km2'],'population':s['population'],'before':len(s['provinces']),'planned':int(n),'cap':cap,'hit_cap':bool(n==cap),'weight':math.sqrt(s['area_km2']*s['population'])})
        country_rows.append({'country':tag,'name':c['name'],'md':md,'before':oldcount,'target':target,'planned':int(ns.sum()),'shortfall':target-int(ns.sum()),'note':'No camera click cap. Tiny-state/area cap limits retained archipelagos.'if ns.sum()<target else ('No matching MD country; retain existing budget'if md is None else '')})
    report={'version':'0.2.0.28','scale':scale,'md_global_land':ref['counts']['land'],'global_before':len(ps),'global_planned':sum(budgets.values()),'global_limit':math.floor(ref['counts']['land']*1.15),'min_province_area_km2':min_area,'minimum_width_target_km':8,'click_rule':False,'cap_policy':'One minimum; floor(area/400), max 3 below 2500 km2. A source-scale city footprint may be smaller; no new province is added outside its state budget. Narrow natural land and tiny-state exceptions reported.','weights':'sqrt(state area km2 * state population); capped iterative redistribution within each country','merges':{str(k):v for k,v in merges.items()},'hezbollah_controller_preserved':True,'countries':country_rows,'states':state_rows,'budgets':budgets,'population_preserved':sum(s['population']for s in w['regions'].values())}
    assert report['global_planned']<=report['global_limit']
    w.update(version='0.2.0.28',scenario_id='bunny_world_2000_0_2_0_28')
    w['map'].update(province_geometry='Population/area-budgeted independent local equal-area terrain and river partitions; whole accepted state footprints retained.',microstate_geometry='No enclave override; previously approved territory unions retained.')
    write('data/world.json',w);write('data/provinces.json',ps);write('data/state_demographics.json',sd);write('data/province_plan_0228.json',report)
    d=R/'documentation/provinces_0228';d.mkdir(exist_ok=True)
    lines=['# Province allocation before generation','','No pixel clickability rule. Minimum area target: 400 km²; minimum width target: 8 km. Natural narrow land/tiny states are exceptions. City footprints may be smaller within the same budget.','','| Country | MD | Before | Planned | Cap shortfall |','|---|---:|---:|---:|---:|']
    lines += [f"| {x['country']} — {x['name']} | {x['md'] if x['md'] is not None else '—'} | {x['before']} | {x['planned']} | {x['shortfall']} |"for x in country_rows]
    lines += ['',f"Global planned: **{report['global_planned']:,}**, MD land: **{report['md_global_land']:,}**, 1.15× ceiling: **{report['global_limit']:,}**.",'','| ID | Country | State | Area km² | Population | Before | Planned | Cap | At cap |','|---:|---|---|---:|---:|---:|---:|---:|---|']
    lines += [f"| {x['state']} | {x['country']} | {x['name'].replace('|','/')} | {x['area_km2']:,.1f} | {x['population']:,} | {x['before']} | {x['planned']} | {x['cap']} | {'yes'if x['hit_cap']else ''} |"for x in state_rows]
    (d/'ALLOCATION.md').write_text('\n'.join(lines)+'\n')
    print('PROVINCE_PLAN_0228',report['global_planned'],'MD',report['md_global_land'],'states',len(w['regions']),'cap_shortfall',sum(c['shortfall']for c in country_rows),flush=True)
if __name__=='__main__':main()
