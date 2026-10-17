"""Review whole-province State assignments against geographic administrative data.
GADM archives are local analysis inputs only, not redistributed. No MD geometry.
Run with --references /path/containing/CHN_2.zip, IND_2.zip, PAK_2.zip, SYR_2.zip.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse, hashlib, json, math, zipfile
import numpy as np
from scipy.ndimage import find_objects
from rasterio.features import rasterize
from rasterio.transform import Affine
from shapely.geometry import shape, Point
from shapely.ops import unary_union

R = Path(__file__).resolve().parents[1]
def read(n): return json.loads((R/n).read_text())
def source(name, keep, specials, province=None):
    return {'source':name,'keep':keep,'specials':specials,'province_filter':province}
def group(name, ids=None, members=None):
    return {'name':name,'id':ids,'members':members or []}

def definitions():
    plans=[]
    def split(tag,sid,province,name,newname,names):
        plans.append({'key':f'{tag}_{sid}','country':tag,'parents':[sid],
          'groups':[group(name,sid),group(newname,members=names)],
          'ref':source(tag,0,{n:1 for n in names},province)})
    split('CHI',179,'NeiMongol','Inner Mongolia','Hulunbuir',['Hulunbuir'])
    split('CHI',182,'Heilongjiang','Heilongjiang','Songjiang',['Harbin','Mudanjiang','Jixi','Qitaihe','Shuangyashan','Jiamusi'])
    split('CHI',184,'Liaoning','Liaoning','Liaoxi',['Chaoyang','Fuxin','Huludao','Jinzhou','Panjin'])
    split('CHI',187,'Guangdong','Guangdong','Pearl River Delta',['Guangzhou','Foshan','Shenzhen','Dongguan','Zhongshan','Zhuhai','Jiangmen','Huizhou','Zhaoqing'])
    plans[-1]['groups'].append(group('Western Guangdong',members=['Maoming','Zhanjiang','Yangjiang','Yunfu']))
    plans[-1]['ref']['specials'].update({'Maoming':2,'Zhanjiang':2,'Yangjiang':2,'Yunfu':2})
    split('CHI',192,'Jiangsu','Jiangsu','Nanjing',['Nanjing'])
    split('CHI',193,'Shandong','Shandong','Jiaodong',['Qingdao','Yantai','Weihai'])
    split('CHI',194,'Hebei','Hebei','Northern Hebei',['Chengde','Zhangjiakou','Tangshan','Qinhuangdao'])
    split('CHI',197,'Sichuan','Sichuan','Western Sichuan',['GarzêTibetan','NgawaTibetanandQiang','LiangshanYi','Panzhihua'])
    # Whole governorates; the smaller Quneitra/UNDOF footprint stays with Daraa.
    for sid,names,keep in [(1797,['Daraa–Quneitra','As-Suwayda'],{'Daraa':0,'Quneitra':0,'Western al-Samadania':0,'As-Suwayda':1}),
                           (1798,['Homs','Hama'],{'Homs':0,'Hama':1}),
                           (1799,['Latakia','Tartus'],{'Latakia':0,'Tartus':1}),
                           
                           (1803,['Aleppo','Idlib'],{'Aleppo':0,'Idlib':1})]:
        plans.append({'key':f'SYR_{sid}','country':'SYR','parents':[sid],
          'groups':[group(n,sid if i==0 else None)for i,n in enumerate(names)],
          'ref':source('NE',0,keep,'Syria')})
    split('SYR',1800,'RifDimashq','Damascus and Rif Dimashq','Qalamoun',['Al-Qutayfah','An-Nabk','Yabrud'])
    plans.append({'key':'SYR_1804','country':'SYR','parents':[1804],
      'groups':[group('Northern Deir ez-Zor',1804),group('Southern Deir ez-Zor')],
      'ref':source('SYR',0,{},None)}) # district names are resolved explicitly after input inspection
    plans[-1]['ref']['specials']={'AlMayadin':1,'AbuKamal':1,'Al-Mayadin':1,'AbuKamalDistrict':1,'AlBuKamal':1}
    split('RAJ',904,'Maharashtra','Maharashtra','Vidarbha',['Akola','Amravati','Bhandara','Buldana','Chandrapur','Garhchiroli','Gondiya','Nagpur','Wardha','Washim','Yavatmal'])
    # Add Mumbai as a third group, only if an existing province actually fits.
    plans[-1]['groups'].append(group('Mumbai',members=['MumbaiCity','MumbaiSuburban']))
    plans[-1]['ref']['specials'].update({'MumbaiCity':2,'MumbaiSuburban':2})
    split('RAJ',915,'MadhyaPradesh','Madhya Pradesh','Malwa–Nimar',['AgarMalwa','Alirajpur','Barwani','Burhanpur','Dewas','Dhar','EastNimar','Indore','Jhabua','Mandsaur','Neemuch','Ratlam','Shajapur','Ujjain','WestNimar'])
    split('RAJ',892,'Rajasthan','Rajasthan','Marwar',['Barmer','Jaisalmer','Jalor','Jodhpur','Nagaur','Pali','Sirohi'])
    split('RAJ',893,'Gujarat','Gujarat','Saurashtra–Kutch',['Amreli','Bhavnagar','Botad','DevbhumiDwarka','GirSomnath','Jamnagar','Junagadh','Kachchh','Morbi','Porbandar','Rajkot','Surendranagar'])
    # GADM ISO uses IND/PAK; country tags in BunnyWorld remain RAJ/PAK.
    for p in plans:
        if p['country']=='RAJ':p['ref']['source']='IND'
    plans.append({'key':'PAK_764','country':'PAK','parents':[764],
      'groups':[group('Central Punjab',764),group('Northern Punjab',members=['Rawalpindi','Sargodha']),group('Southern Punjab',members=['Bahawalpur','DeraGhaziKhan','Multan'])],
      'ref':source('PAK',0,{'Rawalpindi':1,'Sargodha':1,'Bahawalpur':2,'DeraGhaziKhan':2,'Multan':2},'Punjab')})
    split('PAK',761,'Khyber-Pakhtunkhwa','Khyber Pakhtunkhwa','Malakand',['Malakand'])
    mor=[('Oriental',694,['Oriental']),('Tanger–Tetouan',None,['Tangier-Tetouan']),
         ('Fès–Taza',None,['Fès-méknas-boulmane','Taza-Al Hoceïma-Taounate']),
         ('Rabat–Salé–Gharb',None,['Rabat-Salé-Zemmour-Zaër','Gharb-Chrarda-Béni Hssen']),
         ('Meknès–Tafilalet',695,['Meknès-Tafilalet']),
         ('Casablanca–Chaouia–Doukkala',None,['Grand Casablanca','Chaouia-Ouardigha','Doukkala Abda']),
         ('Marrakech–Tadla',697,['Marrakesh-Tensift-El Haouz','Tadla-Azilal']),
         ('Souss–Massa–Draa',696,['Suss-Massa-Draa'])]
    plans.append({'key':'MOR_mainland','country':'MOR','parents':[694,695,696,697],
      'groups':[group(n,i,m)for n,i,m in mor],
      'ref':source('NE',0,{n:i for i,(_,_,members) in enumerate(mor)for n in members},'Morocco')})
    col=[('Amazonia',234,['Amazonas','Caquetá','Guaviare','Putumayo','Vaupés']),
         ('Orinoquía',235,['Arauca','Casanare','Guainía','Vichada','Meta']),
         ('Caribe',236,['Atlántico','Bolívar','Cesar','La Guajira','Magdalena','Sucre','Córdoba','Archipelago of Saint Andréws']),
         ('Cundinamarca–Boyacá',239,['Bogotá','Cundinamarca','Boyacá']),
         ('Antioquia',240,['Antioquia']),
         ('Santander',None,['Santander','Norte de Santander']),
         ('Central Andes',None,['Caldas','Quindío','Risaralda','Tolima','Huila']),
         ('Pacífico',None,['Chocó','Valle del Cauca','Cauca','Nariño'])]
    plans.append({'key':'COL_regions','country':'COL','parents':[234,235,236,239,240],
      'groups':[group(n,i,m)for n,i,m in col],
      'ref':source('NE',2,{n:i for i,(_,_,members) in enumerate(col)for n in members},'Colombia')})
    return plans

def components(ids,ps):
    remain=set(ids);out=[]
    while remain:
        todo=[remain.pop()];found=[]
        while todo:
            pid=todo.pop();found.append(pid)
            for n in ps[str(pid)]['neighbors']:
                if n in remain:remain.remove(n);todo.append(n)
        out.append(sorted(found))
    return sorted(out,key=lambda c:-sum(ps[str(pid)]['area_km2']for pid in c))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--references',type=Path,required=True);args=ap.parse_args()
    w,ps=read('data/world.json'),read('data/provinces.json')
    assert w['version']=='0.2.0.25'
    data={};sources={}
    for tag in ['CHN','IND','PAK','SYR']:
        path=args.references/f'{tag}_2.zip'
        with zipfile.ZipFile(path)as z:data[tag]=json.loads(z.read(z.namelist()[0]))['features']
        sources[tag]={'url':f'https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{tag}_2.json.zip','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'license':'https://gadm.org/license.html','note':'Local analysis input; GADM source/derived polygon geometry is not included in this patch. Reference is modern; game divisions are geographic approximations for 2000.'}
    data['CHI']=data['CHN'];data['NE']=read('tools/cartography/geographic_subdivisions.geojson')['features']
    sources['NE']={'path':'tools/cartography/geographic_subdivisions.geojson','sha256':hashlib.sha256((R/'tools/cartography/geographic_subdivisions.geojson').read_bytes()).hexdigest(),'license':'Natural Earth public domain'}
    atlas=np.load(R/'tools/cartography/map_provinces.npz')['provinces']
    boxes=find_objects(atlas,max_label=65535)
    # The historical GHSL cache is not registered to the current layout.
    # Use disclosed settlement ranks + a rural area floor, within each old state.
    cities=read('data/cities.json');ranks=defaultdict(float)
    for c in cities:
        if str(c.get('province_id')) in ps:ranks[c['province_id']]+=max(0,c.get('population_rank',0))
    pop=np.zeros(65536)
    for state in w['regions'].values():
        ids=state['provinces'];area=sum(ps[str(i)]['area_km2']for i in ids);urban=sum(ranks[i]for i in ids)
        for i in ids:
            share=ps[str(i)]['area_km2']/area
            if urban:share=.4*share+.6*ranks[i]/urban
            pop[i]=state['population']*share
    (R/'data/population_weights_0226.json').write_text(json.dumps({'method':'Modeled subdivision shares: 40% of each old state total by province land area and 60% by existing mapped settlement population ranks; 100% area if no ranked settlements. Retains a rural floor and reconciles each old state independently. Not local census counts. Historical GHSL cache rejected because its registration is not reliable for current geography. Demographic refinement remains a separate task.','weights':{str(k):round(float(pop[k]),6)for k in map(int,ps)}},separators=(',',':'))+'\n')
    results=[];nextid=max(map(int,w['regions']))+1
    for plan in definitions():
        tag=plan['country'];ref=plan['ref'];features=[];members=defaultdict(list)
        for f in data[ref['source']]:
            p=f['properties']
            if ref['source']=='NE':
                if p.get('admin')!=ref['province_filter']:continue
                name=p.get('name_en')or p.get('name')
                if name not in ref['specials']:continue
                index=ref['specials'][name]
            else:
                if ref['province_filter']and p['NAME_1']!=ref['province_filter']:continue
                name=p['NAME_2'];index=ref['specials'].get(name,ref['keep'])
                if plan['key']=='SYR_1804':
                    if 'Dayr' not in p['NAME_1']and 'Deir' not in p['NAME_1']:continue
                    index=1 if ('Mayad' in name or 'Kamal' in name or 'Būkam' in name)else 0
            features.append((f['geometry'],index+1));members[index].append(name)
        assert features,plan['key']
        pids=[p['id']for p in ps.values()if p['region']in plan['parents']]
        bb=[boxes[pid-1]for pid in pids];top=min(b[0].start for b in bb);bottom=max(b[0].stop for b in bb);left=min(b[1].start for b in bb);right=max(b[1].stop for b in bb)
        geo=rasterize(features,out_shape=(bottom-top,right-left),transform=Affine(360/16384,0,left*360/16384-180,0,-180/8192,90-top*180/8192),dtype='uint8')
        arr=atlas[top:bottom,left:right];mask=np.isin(arr,pids)
        codes=arr[mask].astype(np.uint32)*32+geo[mask]
        vals,counts=np.unique(codes,return_counts=True);votes=defaultdict(Counter)
        for v,count in zip(vals,counts):votes[int(v)//32][int(v)%32-1]+=int(count)
        unions={i:unary_union([shape(g)for g,k in features if k==i+1])for i in range(len(plan['groups']))if any(k==i+1 for _,k in features)}
        assigned=defaultdict(list);details=[]
        for pid in pids:
            total=sum(votes[pid].values());valid={i:n for i,n in votes[pid].items()if i>=0}
            if valid:index=max(valid,key=valid.get);fit=valid[index]/sum(valid.values());coverage=sum(valid.values())/total;method='native land-pixel majority overlap'
            else:
                u,v=ps[str(pid)]['map_center'];point=Point(u*360-180,90-v*180)
                index=min(unions,key=lambda i:unions[i].distance(point));fit=0.;coverage=0.;method='nearest administrative footprint for source coastline/remote-island mismatch'
            assigned[index].append(pid)
            details.append({'province':pid,'old_state':ps[str(pid)]['region'],'group':index,'fit':round(fit,4),'source_coverage':round(coverage,4),'votes':dict(votes[pid]),'method':method})
        for i,g in enumerate(plan['groups']):
            if g['id']is None:g['id']=nextid;nextid+=1
            ids=sorted(assigned[i]);g.update(provinces=ids,reference_members=members[i],area_km2=round(sum(ps[str(pid)]['area_km2']for pid in ids),3),population_weight=round(sum(float(pop[pid])for pid in ids),3),components=components(ids,ps))
        plan.update(groups=plan['groups'],assignments=details)
        results.append(plan)
        print(plan['key'],[(g['name'],len(g['provinces']),len(g['components']),g['area_km2'],g['population_weight'])for g in plan['groups']],flush=True)
    target=R/'data/state_plan_0226.json'
    target.write_text(json.dumps({'base_version':'0.2.0.25','sources':sources,'population_source':read('data/population_weights_0226.json')['method'],'plans':results},ensure_ascii=False,indent=2)+'\n')
    print('STATE_PLAN_READY',nextid-max(map(int,w['regions']))-1,'proposed additions',flush=True)

if __name__=='__main__':main()
