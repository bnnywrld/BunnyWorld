"""Relink all live geography references without allocating province population."""
from pathlib import Path
from collections import defaultdict,Counter
import copy,json,math
import numpy as np
from scipy.ndimage import find_objects
from scipy.spatial import cKDTree
R=Path(__file__).resolve().parents[1];B=R/'tools/cartography/baseline_0227';W,H=16384,8192
read=lambda p:json.loads((R/p).read_text())
def write(p,d): (R/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n')
def main():
    w,ps=map(read,['data/world.json','data/provinces.json'])
    assert w['version']=='0.2.0.28','Only link the prepared .28 scenario'
    urban=json.loads((B/'urban_population.json').read_text());scene=json.loads((B/'urban_scenery.json').read_text())
    a=np.load(R/'tools/cartography/province_atlas_0228.npz')['provinces'];oldps=json.loads((B/'provinces.json').read_text());plan=read('data/province_plan_0228.json');merges={int(k):v for k,v in plan['merges'].items()}
    lut=np.zeros(65536,np.uint16)
    for p in ps.values():lut[p['id']]=p['region']
    states=lut[a];boxes=find_objects(states,max_label=max(s['id']for s in w['regions'].values()));trees={};pixelrows={}
    def nearest(lon,lat,sid):
        x=int((lon+180)/360*W)%W;y=min(H-1,max(0,int((90-lat)/180*H)));pid=int(a[y,x])
        if pid and pid!=65535 and ps[str(pid)]['region']==sid:return pid
        # Offshore/generalized city coordinates keep their accepted state.
        yy,xx=np.mgrid[max(0,y-18):min(H,y+19),max(0,x-18):min(W,x+19)];ids=a[yy,xx];valid=lut[ids]==sid
        if valid.any():
            d=np.where(valid,(yy-y)**2+((xx-x)*math.cos(math.radians(lat)))**2,np.inf);i=np.unravel_index(np.argmin(d),d.shape);return int(ids[i])
        if sid not in trees:
            bb=boxes[sid-1];py,px=np.nonzero(states[bb]==sid);py+=bb[0].start;px+=bb[1].start
            # Exact native pixels for a fallback used only on sparse references.
            lonr=(px+.5)/W*2*np.pi-np.pi;latr=np.pi/2-(py+.5)/H*np.pi
            points=np.column_stack([np.cos(latr)*np.sin(lonr),np.sin(latr),np.cos(latr)*np.cos(lonr)])
            step=max(1,len(points)//200000);trees[sid]=cKDTree(points[::step]);pixelrows[sid]=(py[::step],px[::step])
        lo,la=math.radians(lon),math.radians(lat);q=[math.cos(la)*math.sin(lo),math.sin(la),math.cos(la)*math.cos(lo)]
        j=int(trees[sid].query(q)[1]);py,px=pixelrows[sid];return int(a[py[j],px[j]])
    cities=json.loads((B/'cities.json').read_text())
    for p in ps.values():p['cities']=[];p['urban_group']=''
    for c in cities:
        old=oldps.get(str(c.get('province_id')))
        if old:sid=merges.get(old['region'],old['region'])
        else:
            # An inherited city may be in a lake/coastal source pixel (e.g.
            # Managua). Repair the reference inside its accepted controller.
            candidates=[s for s in w['regions'].values()if s['owner']==c['country']]
            u,v=(c['longitude']+180)/360,(90-c['latitude'])/180
            sid=min(candidates,key=lambda s:((s['map_center'][0]-u+.5)%1-.5)**2*math.cos(math.radians(c['latitude']))**2+(s['map_center'][1]-v)**2)['id']
            c['reference_repair_0228']='Previously unlinked source coordinate; nearest state of accepted controller'
        pid=nearest(c['longitude'],c['latitude'],sid)
        c.update(province_id=pid,state_id=sid,country=w['regions'][str(sid)]['owner']);ps[str(pid)]['cities'].append(c['name'])
        if c.get('urban_group'):ps[str(pid)]['urban_group']=c['urban_group']
        if c.get('population_rank',0)>=1000000:ps[str(pid)]['kind']='city'
        c.pop('population_2000',None)
    groups=copy.deepcopy(urban['groups'])
    for g in groups.values():
        g['provinces']=[]
        for k in ['population_2000','settlement_population_2000']:g.pop(k,None)
    for c in cities:
        gid=c.get('urban_group')
        if gid in groups:groups[gid]['provinces'].append(c['province_id'])
    scenery_weights=Counter()
    for kind in ['clusters','landmarks']:
        for c in scene[kind]:
            sid=merges.get(oldps[str(c['province'])]['region'],oldps[str(c['province'])]['region']);pid=nearest(c['longitude'],c['latitude'],sid)
            c.update(province=pid,state=sid)
            if kind=='landmarks':c['country']=w['regions'][str(sid)]['owner']
            else:scenery_weights[sid]+=len(c['instances'])
            gid=c.get('group','')
            if gid in groups:groups[gid]['provinces'].append(pid)
    for c in scene['clusters']:c['state_visual_weight']=len(c['instances'])/max(1,scenery_weights[c['state']])
    for gid,g in groups.items():g['provinces']=sorted(set(g['provinces']))
    urban.update(groups=groups,states={k:{'population_2000':s['population']}for k,s in w['regions'].items()},source={'method':'State-only .27 populations, with approved count-preserving state unions. City groups are visual/site references; provinces have no population.'},population_scope='State residents only. Movement tiles and visual city groups do not create or divide population.')
    scene['version']='0.2.0.28'
    for sid,s in w['regions'].items():
        uv=s.get('capital_uv',s['map_center']);pid=nearest(uv[0]*360-180,90-uv[1]*180,int(sid));s['capital_province']=pid;s['map_center']=ps[str(pid)]['map_center']
    for tag,c in w['countries'].items():
        cap=w['regions'][str(c['capital'])];c['map_center']=cap['map_center'];c['regions']=sorted(s['id']for s in w['regions'].values()if s['owner']==tag)
        assert c['population']==sum(w['regions'][str(i)]['population']for i in c['regions'])
    for p in ps.values():
        p['cities']=sorted(set(p['cities']))
        assert 'population'not in p and 'population_2000'not in p
    write('data/world.json',w);write('data/provinces.json',ps);write('data/cities.json',cities);write('data/urban_population.json',urban);write('data/urban_scenery.json',scene)
    print('PROVINCES_0228_LINKED',len(cities),'cities',len(scene['clusters']),'clusters',len(scene['landmarks']),'landmarks; state-only population',flush=True)
if __name__=='__main__':main()
