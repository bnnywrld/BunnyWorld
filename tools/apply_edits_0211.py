"""Apply approved 0.2.1 colour-map edits: sea silhouette > states > provinces.

Decoded inputs and the pre-edit runtime capture are retained in edits_0211.
Run only against the recorded 0.2.1 / .29 geography baseline, then build_map.py.
"""
from pathlib import Path
from collections import Counter, defaultdict
import copy,json,sys,shutil,math
import numpy as np
from PIL import Image
from scipy.ndimage import find_objects,distance_transform_edt,binary_dilation
from scipy.spatial import cKDTree
from apply_edits_0229 import repair,transport,allocate,save_png

R=Path(__file__).resolve().parents[1]; D=R/'tools/cartography/edits_0211'
W,H=16384,8192; VERSION='0.2.1.1'
AREA=(6371.0088*2*np.pi/W)*(6371.0088*np.pi/H)*np.cos((np.arange(H)+.5)/H*np.pi-np.pi/2)
Image.MAX_IMAGE_PIXELS=None
def read(n):return json.loads((R/n).read_text())
def write(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def fill_near(arr,missing):
    # Missing coast pixels are sparse. Bounded periodic windows avoid a full
    # 134-million-cell nearest-neighbour allocation and preserve the date line.
    yy,xx=np.nonzero(missing)
    for by,bx in sorted(set(zip(yy//128,xx//128))):
        top,bottom=max(0,int(by)*128-128),min(H,int(by)*128+256)
        left=int(bx)*128-128;cols=np.arange(left,left+384)%W
        cell=arr[top:bottom,cols].copy();need=missing[top:bottom,cols]
        valid=(cell>0)&(cell!=65535)
        assert valid.any(),('No land neighbour',by,bx)
        _,near=distance_transform_edt(~valid,return_indices=True)
        cell[need]=cell[tuple(near[:,need])];arr[np.arange(top,bottom)[:,None],cols]=cell
        missing[np.arange(top,bottom)[:,None],cols]=False

def population(w,sd,oldw,olds,states,removed):
    rt=json.loads((D/'runtime_before.json').read_text())
    overlaps=Counter();totals=np.zeros(65536)
    for top in range(0,H,128):
        a,b=olds[top:top+128],states[top:top+128]
        totals+=np.bincount(a.ravel(),weights=np.broadcast_to(AREA[top:top+128,None],a.shape).ravel(),minlength=65536)
        m=(a>0)&(a!=65535)&(b>0)&(b!=65535)&(a!=b)
        yy,xx=np.nonzero(m);code=a[m].astype(np.uint32)*65536+b[m]
        vals,inv=np.unique(code,return_inverse=True)
        counts=np.bincount(inv,weights=AREA[top+yy])
        for code,area in zip(vals,counts):overlaps[divmod(int(code),65536)]+=float(area)
    recipients={}
    for sid in removed:
        dests=[(area,b) for (a,b),area in overlaps.items() if a==sid]
        assert dests,('Removed state without recipient',sid)
        recipients[sid]=max(dests)[1]
    flows={}
    for sid in map(int,oldw['regions']):
        total=oldw['regions'][str(sid)]['population']
        if sid in recipients:flows[sid]={recipients[sid]:total};continue
        weights={b:area for(a,b),area in overlaps.items()if a==sid}
        weights[sid]=max(0,totals[sid]-sum(weights.values()))
        ids=sorted(weights);nums=allocate(total,[weights[i]for i in ids])
        flows[sid]={i:int(n) for i,n in zip(ids,nums)}
    affected=set(removed)
    for sid,f in flows.items():
        if f!={sid:oldw['regions'][str(sid)]['population']}:affected.add(sid);affected.update(f)
    sums={sid:{'pop':0,'bands':np.zeros(4,np.int64),'single':np.zeros(101),'religion':Counter(),'education':Counter(),'work':np.zeros(3,np.int64)}for sid in affected if sid not in removed}
    for sid in sorted(affected):
        p=sd['states'][str(sid)];m=rt['states'][str(sid)];total=oldw['regions'][str(sid)]['population']
        ids=sorted(flows[sid]);cols=[flows[sid][i]for i in ids]
        ac=m['metrics']['age']['counts'];adult=int(m['metrics']['education']['denominator'])
        bands=[int(ac['Underage']),total-int(ac['Underage'])-adult,adult-int(ac['Retired']),int(ac['Retired'])]
        bt=transport(bands,cols)
        rc=m['metrics']['religion']['counts'];rk=sorted(rc);relig=transport([int(rc[k])for k in rk],cols)
        ec=m['metrics']['education']['counts'];ek=sorted(ec);edu=transport([int(ec[k])for k in ek],bt[2]+bt[3])
        wc=m['workforce'];work=transport([int(wc[k])for k in ['employed','unemployed','outside_labour_force']],bt[1]+bt[2])
        for j,dest in enumerate(ids):
            t=sums[dest];t['pop']+=cols[j];t['bands']+=bt[:,j];t['work']+=work[:,j]
            t['religion'].update({k:int(relig[i,j])for i,k in enumerate(rk)})
            t['education'].update({k:int(edu[i,j])for i,k in enumerate(ek)})
            singles=np.array(p['age_single_year'],float)
            for i,(lo,hi)in enumerate([(0,18),(18,25),(25,65),(65,101)]):
                sub=singles[lo:hi];t['single'][lo:hi]+=sub/max(sub.sum(),1e-30)*bt[i,j]
    expected={}
    for sid,t in sums.items():
        total=t['pop'];p=sd['states'][str(sid)];s=w['regions'][str(sid)];bands=t['bands']
        adult=int(bands[2]+bands[3]);working=int(bands[1]+bands[2]);employed,unemployed,inactive=map(int,t['work']);labour=employed+unemployed
        if total:p['age_single_year']=(t['single']/total).tolist()
        p['adult25_share']=adult/max(total,1);p['population_2000']=total
        p['population_source']='Conserved .29 residents; removed states transferred whole, other boundary transfers estimated by source land area'
        for kind,counts,denom in [('religion',t['religion'],total),('education',t['education'],adult)]:
            p['metrics'][kind]['shares']={k:v/max(denom,1)for k,v in counts.items()}
            p['metrics'][kind].update(source=p['population_source'],status='Year-2000 modeled transfer',reference='data/map_edit_audit_0211.json')
        p['metrics']['age']['shares']={'Underage':int(bands[0])/max(total,1),'Working age':working/max(total,1),'Retired':int(bands[3])/max(total,1)}
        p['workforce'].update(participation_rate=labour/max(working,1),unemployment_rate=unemployed/max(labour,1),source=p['population_source'])
        p.pop('merge_audit',None);s.update(population=total,population_source=p['population_source'],workforce=copy.deepcopy(p['workforce']))
        expected[str(sid)]={'population':total,'age':{'Underage':int(bands[0]),'Working age':working,'Retired':int(bands[3])},'religion':dict(t['religion']),'education':dict(t['education']),'adult25':adult,'workforce':{'working_age':working,'labour_force':labour,'employed':employed,'unemployed':unemployed,'outside_labour_force':inactive}}
    for sid,dest in recipients.items():
        # Keep existing state infrastructure when merging its full population.
        s=w['regions'][str(sid)];target=w['regions'][str(dest)]
        for k,v in s.get('buildings',{}).items():
            if isinstance(v,(float,int)):target['buildings'][k]=target['buildings'].get(k,0)+v
        for k in ['building_slot_baseline']:
            if isinstance(s.get(k),(int,float)):target[k]=target.get(k,0)+s[k]
        del w['regions'][str(sid)];del sd['states'][str(sid)]
    return {'expected_demographics':expected,'removed_states':[{'id':sid,'name':oldw['regions'][str(sid)]['name'],'recipient':dest,'population':oldw['regions'][str(sid)]['population']}for sid,dest in recipients.items()],
            'transfers':[{'from':sid,'to':dest,'residents':n}for sid,f in flows.items()for dest,n in f.items()if sid!=dest]},recipients

def main():
    w,ps,sd=map(read,['data/world.json','data/provinces.json','data/state_demographics.json'])
    assert w['version']=='0.2.0.29';oldw=copy.deepcopy(w);oldps=copy.deepcopy(ps)
    B=D/'baseline';B.mkdir(exist_ok=True)
    for n in ['world','provinces','state_demographics','cities','urban_scenery','urban_population','sea_regions']:
        shutil.copy2(R/f'data/{n}.json',B/f'{n}.json')
    a=np.zeros((H,W),np.uint16);states=a.copy();olda=a.copy();olds=a.copy()
    for i,label in enumerate(['NW','NE','SW','SE']):
        t,l=i//2*4096,i%2*8192;bb=np.s_[t:t+4096,l:l+8192]
        for scope,arr,orig in [('provinces',a,olda),('states',states,olds)]:
            d=np.load(D/f'{scope}_{i}_{label}.npz');arr[bb]=d['edited'];orig[bb]=d['old']
        rgb=np.asarray(Image.open(R/f'assets/region_ids_{i}.png'),np.uint16)
        assert np.array_equal(olda[bb],rgb[:,:,0]+rgb[:,:,1]*256),'Editing base differs from current game'
    sea_data=np.load(D/'sea_regions.npz');sea,oldsea=sea_data['edited'],sea_data['old']
    target_land=olda>0;newland=(oldsea>0)&(sea==0);newwater=(oldsea==0)&(sea>0)
    for dy in [0,1]:
        for dx in [0,1]:target_land[dy::2,dx::2][newland]=True;target_land[dy::2,dx::2][newwater]=False
    coast_changed=target_land!=(olda>0)
    states[~target_land]=0;states[(olda==65535)&target_land]=65535
    fill_near(states,target_land&(states==0))
    a[~target_land]=0;a[states==65535]=65535
    removed_states=set(map(int,w['regions']))-(set(map(int,np.unique(states)))-{0,65535})
    audit,recipients=population(w,sd,oldw,olds,states,removed_states)
    # State priority also preserves a surviving state's province membership.
    # Painting its colour across another state cannot steal that state's sole
    # province. Only a removed-state merger transfers the child province IDs.
    lut=np.zeros(65536,np.uint16);lut[65535]=65535;membership=[]
    for k,p in ps.items():
        pid=int(k);sid=recipients.get(p['region'],p['region'])
        lut[pid]=sid
        if sid!=p['region']:membership.append({'province':pid,'from':p['region'],'to':sid});p['region']=sid
    # A province whose majority state changes can leave an unchanged residual
    # in another state. Include those residuals in fitting, not just paint.
    edited=(a!=olda)|(states!=olds)|coast_changed|(lut[a]!=states)
    touched=(set(map(int,np.unique(states[edited])))|set(map(int,np.unique(olds[edited]))))-{0,65535}-removed_states
    a[(lut[a]!=states)&(states!=65535)]=0
    boxes=find_objects(states,max_label=max(map(int,w['regions'])));repairs=[]
    for sid in sorted(touched):
        bb=boxes[sid-1];mask=states[bb]==sid;cell=a[bb].copy();valid=mask&(cell>0)
        if not valid.any():
            eligible=[p['id']for p in ps.values()if p['region']==sid]
            assert eligible,('State without original province',sid)
            original=olda[bb][mask];v,n=np.unique(original[np.isin(original,eligible)],return_counts=True)
            pid=int(v[np.argmax(n)])if len(v)else min(eligible)
            cell[mask]=pid;valid=mask.copy()
        _,near=distance_transform_edt(~valid,return_indices=True);missing=mask&~valid
        cell[missing]=cell[tuple(near[:,missing])];lock=np.zeros_like(cell)
        for pid in np.unique(cell[mask]):
            dist=distance_transform_edt(cell==pid);pos=np.unravel_index(dist.argmax(),dist.shape);lock[pos]=pid
        cell,absorbed=repair(cell,mask,lock,edited[bb]);a[bb][mask]=cell[mask]
        repairs.append({'state':sid,'filled_pixels':int(missing.sum()),'fragment_sliver_pixels':absorbed})
        print('FIT',sid,int(missing.sum()),absorbed,flush=True)
    removed_provinces=set(map(int,ps))-(set(map(int,np.unique(a)))-{0,65535})
    for pid in removed_provinces:del ps[str(pid)]
    if not np.array_equal(lut[a],states):
        bad=lut[a]!=states
        np.savez_compressed(D/'fitting_diagnostic.npz',provinces=a,states=states)
        print('UNFITTED',[(int(s),int((bad&(states==s)).sum()))for s in np.unique(states[bad])],flush=True)
    assert np.array_equal(lut[a],states);assert np.array_equal(a>0,target_land)
    boxesp=find_objects(a,max_label=65535)
    changed_ids=(set(map(int,np.unique(a[edited])))|set(map(int,np.unique(olda[edited]))))-{0,65535}-removed_provinces
    for k,p in ps.items():
        pid=int(k);sid=p['region'];bb=boxesp[pid-1]
        if pid in changed_ids or sid in touched:
            mask=a[bb]==pid;yy,xx=np.nonzero(mask);p['area_km2']=round(float(AREA[yy+bb[0].start].sum()),3)
            dist=distance_transform_edt(mask);y,x=np.unravel_index(dist.argmax(),mask.shape)
            p['map_center']=[(x+bb[1].start+.5)/W,(y+bb[0].start+.5)/H]
            p['geometry_source']='Approved .2.1 map edits, sea > state > province; neighbouring province fitting'
        if oldps[k]['region']!=sid and ' · Province 'in p['name']:p['name']=w['regions'][str(sid)]['name']+' · Province '+str(p['local_index'])
    for sid,s in w['regions'].items():
        s['provinces']=sorted(p['id']for p in ps.values()if p['region']==int(sid));assert s['provinces']
        s['area_km2']=round(sum(ps[str(i)]['area_km2']for i in s['provinces']),3)
        for j,pid in enumerate(s['provinces'],1):ps[str(pid)]['local_index']=j
    trees={};coords={}
    def nearest(lon,lat,sid=None):
        x=int((lon+180)/360*W)%W;y=min(H-1,max(0,int((90-lat)/180*H)));pid=int(a[y,x])
        if pid not in [0,65535]and(sid is None or ps[str(pid)]['region']==sid):return pid
        assert sid is not None
        sid=recipients.get(sid,sid)
        if sid not in trees:
            bb=boxes[sid-1];yy,xx=np.nonzero(states[bb]==sid);yy+=bb[0].start;xx+=bb[1].start
            step=max(1,len(yy)//250000);yy=yy[::step];xx=xx[::step];lo=(xx+.5)/W*2*np.pi-np.pi;la=np.pi/2-(yy+.5)/H*np.pi
            coords[sid]=(yy,xx);trees[sid]=cKDTree(np.column_stack([np.cos(la)*np.sin(lo),np.sin(la),np.cos(la)*np.cos(lo)]))
        lo,la=math.radians(lon),math.radians(lat);j=trees[sid].query([math.cos(la)*math.sin(lo),math.sin(la),math.cos(la)*math.cos(lo)])[1];yy,xx=coords[sid];return int(a[yy[j],xx[j]])
    cities=read('data/cities.json');scene=read('data/urban_scenery.json');urban=read('data/urban_population.json');citychanges=[]
    for p in ps.values():p['cities']=[]
    def point_id(lon,lat,sid):
        x=int((lon+180)/360*W)%W;y=min(H-1,max(0,int((90-lat)/180*H)))
        return nearest(lon,lat,None if int(a[y,x])not in [0,65535]else recipients.get(sid,sid))
    for c in cities:
        oldpid,oldsid=c['province_id'],c['state_id'];pid=point_id(c['longitude'],c['latitude'],oldsid);sid=ps[str(pid)]['region']
        if(pid,sid)!=(oldpid,oldsid):citychanges.append({'city':c['name'],'from_province':oldpid,'to_province':pid,'from_state':oldsid,'to_state':sid})
        c.update(province_id=pid,state_id=sid,country=w['regions'][str(sid)]['owner']);ps[str(pid)]['cities'].append(c['name'])
        if c.get('urban_group'):ps[str(pid)]['urban_group']=c['urban_group']
    for group in urban['groups'].values():group['provinces']=[]
    for c in cities:
        if c.get('urban_group')in urban['groups']:urban['groups'][c['urban_group']]['provinces'].append(c['province_id'])
    weights=Counter()
    for kind in ['clusters','landmarks']:
        for c in scene[kind]:
            pid=point_id(c['longitude'],c['latitude'],c['state']);sid=ps[str(pid)]['region'];c.update(province=pid,state=sid)
            if kind=='clusters':weights[sid]+=len(c['instances'])
            else:c['country']=w['regions'][str(sid)]['owner']
            if c.get('group')in urban['groups']:urban['groups'][c['group']]['provinces'].append(pid)
    for c in scene['clusters']:c['state_visual_weight']=len(c['instances'])/max(1,weights[c['state']])
    for g in urban['groups'].values():g['provinces']=sorted(set(g['provinces']))
    for p in ps.values():p['cities']=sorted(set(p['cities']))
    for sid,s in w['regions'].items():
        uv=s.get('capital_uv',s['map_center']);pid=nearest(uv[0]*360-180,90-uv[1]*180,int(sid));s['capital_province']=pid
        if pid!=oldw['regions'][sid]['capital_province']or int(sid)in touched:s['map_center']=ps[str(pid)]['map_center']
    for tag,c in w['countries'].items():
        c['regions']=sorted(s['id']for s in w['regions'].values()if s['owner']==tag);assert c['regions'],('Country lost all territory',tag)
        c['population']=sum(w['regions'][str(i)]['population']for i in c['regions'])
        if c['capital']not in c['regions']:c['capital']=recipients.get(c['capital'],c['regions'][0])
        c['map_center']=w['regions'][str(c['capital'])]['map_center']
    assert sum(s['population']for s in w['regions'].values())==sum(s['population']for s in oldw['regions'].values())
    w.update(version=VERSION,scenario_id='bunny_world_2000_0_2_1_1');scene['version']=VERSION
    urban['states']={sid:{'population_2000':s['population']}for sid,s in w['regions'].items()}
    for i in range(4):
        t,l=i//2*4096,i%2*8192;part=a[t:t+4096,l:l+8192];rgb=np.zeros((*part.shape,3),np.uint8);rgb[:,:,0]=part&255;rgb[:,:,1]=part>>8;save_png(R/f'assets/region_ids_{i}.png',rgb)
    rgb=np.zeros((*sea.shape,3),np.uint8);rgb[:,:,0]=sea&255;rgb[:,:,1]=sea>>8;save_png(R/'assets/sea_ids.png',rgb)
    np.savez_compressed(D/'final_provinces.npz',provinces=a);np.savez_compressed(D/'final_states.npz',states=states)
    np.savez_compressed(D/'coast_changes.npz',added=newland,removed=newwater)
    audit.update(version=VERSION,base_version='0.2.1',geography_base='0.2.0.29',priority=['sea','state','province'],sea_land_pixels_added=int(newland.sum()),sea_water_pixels_added=int(newwater.sum()),native_land_pixels_changed=int(coast_changed.sum()),membership_changes=membership,repairs=repairs,removed_provinces=[{'id':pid,'name':oldps[str(pid)]['name']}for pid in sorted(removed_provinces)],city_reference_changes=citychanges,country_population_changes={tag:{'before':oldw['countries'][tag]['population'],'after':c['population']}for tag,c in w['countries'].items()if c['population']!=oldw['countries'][tag]['population']})
    for n,data in [('world',w),('provinces',ps),('state_demographics',sd),('cities',cities),('urban_scenery',scene),('urban_population',urban),('map_edit_audit_0211',audit)]:write('data/'+n+'.json',data)
    for n in ['project.godot','export_presets.cfg']:
        p=R/n;p.write_text(p.read_text().replace('0.2.1','0.2.1.1'))
    p=R/'scripts/world_state.gd';p.write_text(p.read_text().replace('const SAVE_VERSION := 18','const SAVE_VERSION := 19'))
    print('APPLIED',len(ps),'provinces',len(w['regions']),'states',len(citychanges),'city relinks',flush=True)

if __name__=='__main__':main()
