"""Apply reviewed whole-province geography. Input .25; refuses repeated mutation.
Review with review_states_0226.py first. Never changes canonical province pixels.
"""
from pathlib import Path
from collections import defaultdict, Counter
import copy, hashlib, json, math
import numpy as np
R=Path(__file__).resolve().parents[1]
def read(n):return json.loads((R/n).read_text())
def write(n,x): (R/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def alloc(total,weights):
    a=np.array(weights,float);a=a/a.sum()*total;out=np.floor(a).astype(np.int64)
    out[np.argsort(-(a-out),kind='stable')[:int(total-out.sum())]]+=1
    return list(map(int,out))
def totals(w,tag):
    ss=[s for s in w['regions'].values()if s['owner']==tag];b=Counter()
    for s in ss:b.update(s['buildings'])
    return sum(s['population']for s in ss),dict(b),sum(s['building_slot_baseline']for s in ss)
def main():
    w,ps=read('data/world.json'),read('data/provinces.json');assert w['version']=='0.2.0.25'
    old=copy.deepcopy(w);oldps=copy.deepcopy(ps);plan=read('data/state_plan_0226.json')
    weights={int(k):v for k,v in read('data/population_weights_0226.json')['weights'].items()}
    cities=read('data/cities.json');changed=set();parent_children={};allocations=[];skipped=[]
    for pl in plan['plans']:
        groups=[g for g in pl['groups']if g['provinces']]
        for g in pl['groups']:
            if not g['provinces']:skipped.append({'name':g['name'],'reason':'No whole province fits the municipal footprint; retained in Maharashtra. Options: retain combined state, or revisit after a future province subdivision.'})
        assert set(i for g in groups for i in g['provinces'])==set(i for sid in pl['parents']for i in old['regions'][str(sid)]['provinces'])
        for sid in pl['parents']:
            parent_children[sid]=[g['id']for g in groups if set(g['provinces'])&set(old['regions'][str(sid)]['provinces'])]
        for g in groups:
            ids=g['provinces'];parents=sorted({oldps[str(i)]['region']for i in ids});template=max(parents,key=lambda s:sum(ps[str(i)]['area_km2']for i in ids if oldps[str(i)]['region']==s))
            s=copy.deepcopy(old['regions'][str(template)])
            s.update(id=g['id'],name=g['name'],provinces=ids,area_km2=g['area_km2'],population=0,buildings={},building_slot_baseline=0,neighbors=[])
            for field in ['cores','claims','source_states','geographic_codes','geographic_divisions','protected_territories']:
                s[field]=sorted({v for sid in parents for v in old['regions'][str(sid)].get(field,[])})
            s['population_source']='Modeled settlement-rank and rural-area shares; each 0.2.0.25 parent total retained exactly. See data/population_weights_0226.json.'
            s['geography_0226']={'parents':parents,'reference_members':g['reference_members'],'method':'Whole current provinces assigned by maximum administrative land-pixel overlap; source mismatch islands use nearest regional footprint.'}
            for j,pid in enumerate(ids,1):
                p=ps[str(pid)];p.update(region=s['id'],local_index=j)
                # Preserve distinct city/district labels; regenerate only generic state labels.
                if ' · Province ' in p.get('name',''):p['name']=s['name']+' · Province '+str(j)
            # Keep an existing capital when it lies in this child; otherwise use a mapped settlement.
            retained=[old['regions'][str(sid)]for sid in parents if old['regions'][str(sid)]['capital_province']in ids]
            national=old['countries'][pl['country']]['capital']
            retained.sort(key=lambda t:(t['id']!=national,t['id']!=g['id']))
            if retained:
                t=retained[0]
                for key in ['state_capital','capital_province','capital_uv','capital_source','capital_is_settlement']:s[key]=copy.deepcopy(t[key])
            else:
                settlements=[c for c in cities if c.get('province_id')in ids and c['country']==s['owner']]
                if settlements:
                    c=max(settlements,key=lambda c:c.get('population_rank',0));s.update(state_capital=c['name'],capital_province=c['province_id'],capital_uv=[(c['longitude']+180)/360,(90-c['latitude'])/180],capital_source='Existing mapped settlement',capital_is_settlement=True)
                else:
                    pid=max(ids,key=lambda i:(weights[i],ps[str(i)]['area_km2']))
                    s.update(state_capital=s['name']+' administrative centre',capital_province=pid,capital_uv=ps[str(pid)]['map_center'],capital_source='Province anchor; no mapped settlement available',capital_is_settlement=False)
            # Province anchor lies on owned land even when a city point sits offshore.
            s['map_center']=ps[str(s['capital_province'])]['map_center']
            w['regions'][str(s['id'])]=s;changed.add(s['id'])
        for sid in pl['parents']:
            parent=old['regions'][str(sid)];child_ids=parent_children[sid]
            child_weights=[sum(weights[i]for i in g['provinces']if oldps[str(i)]['region']==sid)for g in groups if g['id']in child_ids]
            # group and child order are deliberately identical.
            assert child_ids==[g['id']for g in groups if g['id']in child_ids]
            row={'parent':sid,'children':child_ids,'population':alloc(parent['population'],child_weights),'buildings':{}}
            for child,value in zip(child_ids,row['population']):w['regions'][str(child)]['population']+=value
            for key,total in parent['buildings'].items():
                parts=alloc(total,child_weights);row['buildings'][key]=parts
                for child,value in zip(child_ids,parts):
                    if value:w['regions'][str(child)]['buildings'][key]=w['regions'][str(child)]['buildings'].get(key,0)+value
            for child,value in zip(child_ids,alloc(parent['building_slot_baseline'],child_weights)):w['regions'][str(child)]['building_slot_baseline']+=value
            allocations.append(row)
            if sid not in [g['id']for g in groups]:del w['regions'][str(sid)]
    # A clear governorate name replaces an older geographic label.
    renames=[]
    s=w['regions']['1801'];renames.append({'id':1801,'before':s['name'],'after':'Al-Hasakah'});s['name']='Al-Hasakah'
    for pid in s['provinces']:
        if ' · Province ' in ps[str(pid)].get('name',''):ps[str(pid)]['name']=s['name']+' · Province '+str(ps[str(pid)]['local_index'])
    for sid in changed:
        s=w['regions'][str(sid)]
        if str(sid)in old['regions']and s['name']!=old['regions'][str(sid)]['name']:renames.append({'id':sid,'before':old['regions'][str(sid)]['name'],'after':s['name']})
    for tag,c in w['countries'].items():
        c['regions']=sorted(s['id']for s in w['regions'].values()if s['owner']==tag)
        cp=old['regions'][str(c['capital'])]['capital_province'];c['capital']=ps[str(cp)]['region']
        assert totals(w,tag)==totals(old,tag),('Country totals changed',tag,totals(w,tag),totals(old,tag))
    # Recompute references only where membership changed; unaffected country records remain exact.
    for c in cities:
        pid=c.get('province_id');sid=ps.get(str(pid),{}).get('region')
        if sid in changed:
            c['state_id']=sid;c['state_capital']=pid==w['regions'][str(sid)]['capital_province'] and c['name']==w['regions'][str(sid)]['state_capital']
    scene=read('data/urban_scenery.json')
    for kind in ['clusters','landmarks']:
        for c in scene[kind]:
            sid=ps[str(c['province'])]['region']
            if sid in changed:c['state']=sid
    for sid in changed:
        clusters=[c for c in scene['clusters']if c['state']==sid]
        if not clusters:continue
        uv=w['regions'][str(sid)]['capital_uv']
        cap=min(clusters,key=lambda c:((c['longitude']+180)/360-uv[0])**2+((90-c['latitude'])/180-uv[1])**2)
        total=sum(max(1,len(c['instances']))for c in clusters)
        for c in clusters:c['state_capital_priority']=c is cap;c['state_visual_weight']=max(1,len(c['instances']))/total
    scene['version']='0.2.0.26'
    urban=read('data/urban_population.json');urban['states']={k:{'population_2000':s['population']}for k,s in w['regions'].items()}
    protected=read('data/protected_territories_0210.json')
    for row in protected['territories']:
        row['states']=sorted({v for sid in row['states']for v in parent_children.get(sid,[sid])})
    protected['version']='0.2.0.26'
    w.update(version='0.2.0.26',scenario_id='bunny_world_2000_0_2_0_26')
    counts=[{'tag':t,'country':w['countries'][t]['name'],'before':len(old['countries'][t]['regions']),'after':len(w['countries'][t]['regions']),'md':read('data/md_geography_reference.json')['countries'][t]['states']}for t in ['CHI','SYR','RAJ','MOR','PAK','COL']]
    skipped.extend([
      {'name':'Damascus municipal state','reason':'The city has no separate whole-province footprint. Kept with Rif Dimashq; Qalamoun uses northern administrative districts instead. Options: retain the combined state or subdivide provinces in a later patch.'},
      {'name':'Uttar Pradesh / Braj','reason':'Braj, Awadh and Purvanchal lack a single agreed administrative division at this scale. Options: official district groups, or real administrative divisions grouped into larger states. Existing state and name retained pending that decision.'},
      {'name':'Balochistan ethnic split','reason':'Pashtun/Baloch boundaries and an appropriate year-2000 grouping need more evidence. Options: official divisions or a documented cultural grouping. Kept intact; Pakistan is already within one of MD.'},
      {'name':'Optional countries','reason':'Germany, Spain, United Kingdom, Indonesia, Argentina, Chile, Madagascar and Angola unchanged. No optional split selected in this pass; these need a separate review of missing populous regions rather than count-driven additions.'},
      {'name':'Taiwan, Afghanistan and all explicit exclusions','reason':'Unchanged as requested, including Philippines and all previously approved territory merges.'}])
    report={'version':'0.2.0.26','base_commit':'aeacb59','counts':counts,'new_states':[{'id':g['id'],'name':g['name'],'country':pl['country'],'provinces':g['provinces'],'reference_members':g['reference_members']}for pl in plan['plans']for g in pl['groups']if g['provinces']and str(g['id'])not in old['regions']], 'renames':sorted(renames,key=lambda x:x['id']),'allocations':allocations,'skipped':skipped,'population_method':plan['population_source'],'province_pixels_changed':0,'countries':len(w['countries']),'states':len(w['regions']),'land_provinces':len(ps),'population':sum(s['population']for s in w['regions'].values()),'changed_states':sorted(changed),'source_note':'MD count/name guide only. Native whole provinces grouped against Natural Earth ADM1 and GADM ADM2 references; no MD geometry, no GADM polygons shipped. Modern reference groupings are gameplay approximations, not exact 2000 administrative boundaries.'}
    for name,value in [('world',w),('provinces',ps),('cities',cities),('urban_scenery',scene),('urban_population',urban),('protected_territories_0210',protected),('geography_0226_report',report)]:write('data/'+name+'.json',value)
    for fn in ['project.godot','export_presets.cfg']:
        path=R/fn;path.write_text(path.read_text().replace('0.2.0.25','0.2.0.26').replace('Interface and Islands','State Detail'))
    info=read('BUILD_INFO.json');info.update(version='0.2.0.26',baseline_version='0.2.0.25',repository_base_commit='aeacb59',states=len(w['regions']),geography_version='0.2.0.26',display_version='0.2.0.26',scenario_id=w['scenario_id'],changes=['Whole-province regional detail for China, Syria, India, Morocco, Pakistan and Colombia','Preserve approved merges, explicit exclusions, all country population and building totals','Regenerate shared state borders, membership lookups and map bundle'],validation={'pending':True});write('BUILD_INFO.json',info)
    print('STATES_0226_APPLIED',counts,len(report['new_states']),'new states',flush=True)
if __name__=='__main__':main()
