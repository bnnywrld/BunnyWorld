"""Apply the user's 0.2.0.8 geographic corrections to the accepted 0.2.0.7 map.

Offline preparation only: explicit ADM1 unions replace nearest-name/budget
grouping. Existing province interiors are retained and split where a corrected
state border crosses them. No runtime generation or save migration is added.
"""
from pathlib import Path
from collections import Counter, defaultdict
import copy, hashlib, json, math, subprocess
import numpy as np
from PIL import Image
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from scipy.ndimage import find_objects, distance_transform_edt, label, binary_dilation
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'tools/cartography'
BASE = ROOT / '.geography_0208_baseline'
BASE_COMMIT = 'f9de969716ff5430aaad8eecadae70ba357aba77'
W, H = 16384, 8192
VERSION = '0.2.0.8'
Image.MAX_IMAGE_PIXELS = None
AREA = (6371.0088 * 2 * math.pi / W) * (6371.0088 * math.pi / H) * np.cos((np.arange(H)+.5)/H*math.pi-math.pi/2)

def read(path): return json.loads(Path(path).read_text())
def write(path, value):
    (ROOT/path).write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':'), default=lambda x: x.item()))
def alloc(total, weights):
    w = np.asarray(weights, float); exact = total*w/max(w.sum(), 1e-30)
    result = np.floor(exact).astype(np.int64)
    result[np.argsort(-(exact-result), kind='stable')[:int(total-result.sum())]] += 1
    return result
def xyz(lon, lat):
    a, b = np.deg2rad(lon), np.deg2rad(lat)
    return np.column_stack([np.cos(b)*np.sin(a), np.sin(b), np.cos(b)*np.cos(a)])
def focus(yy, xx):
    # Sample only to select a focus; all pixels still contribute to area.
    step = max(1, len(xx)//100000)
    points = xyz((xx[::step]+.5)/W*360-180, 90-(yy[::step]+.5)/H*180)
    j = int(np.argmax(points @ points.mean(0))) * step
    return [(float(xx[j])+.5)/W, (float(yy[j])+.5)/H]
def snapshot():
    for name in ['world','provinces','cities','urban_population','urban_scenery','microstate_geometry']:
        path = 'data/'+name+'.json'; target = BASE/path
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(subprocess.check_output(['git','show',BASE_COMMIT+':'+path], cwd=ROOT))
    for name in ['grouped_atlas_022r2.npz','province_atlas_0207.npz']:
        path = 'tools/cartography/'+name; target = BASE/path
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(subprocess.check_output(['git','show',BASE_COMMIT+':'+path], cwd=ROOT))

def mapping(groups):
    return {member: group for group, members in groups.items() for member in members.split('|')}

FRANCE = mapping({
 'Hauts-de-France':'Nord|Pas-de-Calais|Somme|Aisne|Oise',
 'Normandie':'Manche|Calvados|Orne|Eure|Seine-Maritime',
 'Île-de-France':"Paris|Hauts-de-Seine|Seine-Saint-Denis|Val-de-Marne|Val-d'Oise|Yvelines|Essonne|Seine-et-Marne",
 'Champagne-Ardenne':'Ardennes|Marne|Aube|Haute-Marne',
 'Alsace-Lorraine':'Meuse|Meurthe-et-Moselle|Moselle|Vosges|Bas-Rhin|Haut-Rhin',
 'Bourgogne':'Yonne|Nièvre|Côte-d’Or|Saône-et-Loire',
 'Franche-Comté':'Doubs|Jura|Haute-Saône|Territoire de Belfort',
 'Loire':'Cher|Eure-et-Loir|Indre|Indre-et-Loire|Loir-et-Cher|Loiret',
 'Pays de la Loire':'Loire-Atlantique|Maine-et-Loire|Mayenne|Sarthe|Vendée',
 'Bretagne':"Finistère|Côtes-d'Armor|Ille-et-Vilaine|Morbihan",
 'Aquitaine':'Gironde|Landes|Lot-et-Garonne|Dordogne|Pyrenees-Atlantics',
 'Poitou-Limousin':'Charente|Charente-Maritime|Deux-Sèvres|Vienne|Haute-Vienne|Creuse|Corrèze',
 'Occitanie':'Gers|Haute-Garonne|Hautes-Pyrénées|Ariège|Aveyron|Lot|Tarn|Tarn-et-Garonne',
 'Languedoc-Roussillon':'Gard|Hérault|Aude|Lozère|Pyrénées-Orientales',
 'Auvergne':'Allier|Cantal|Haute-Loire|Puy-de-Dôme',
 'Rhône-Alpes':'Ain|Ardèche|Drôme|Isère|Loire|Rhône',
 'Savoy':'Savoie|Haute-Savoie', 'Nice':'Alpes-Maritimes',
 'Provence':'Alpes-de-Haute-Provence|Hautes-Alpes|Bouches-du-Rhône|Var|Vaucluse',
 'Corsica':'Haute-Corse|Corse-du-Sud'})
JAPAN = mapping({
 'Northern Kyushu':'Fukuoka Prefecture|Saga Prefecture|Nagasaki Prefecture|Ōita Prefecture',
 'Southern Kyushu':'Kumamoto Prefecture|Miyazaki Prefecture|Kagoshima Prefecture',
 'Shikoku':'Ehime Prefecture|Kagawa Prefecture|Kōchi Prefecture|Tokushima Prefecture',
 'Kansai':'Hyōgo Prefecture|Kyōto Prefecture|Mie Prefecture|Nara Prefecture|Shiga Prefecture|Wakayama Prefecture|Ōsaka Prefecture',
 'Chugoku':'Hiroshima Prefecture|Yamaguchi Prefecture|Okayama Prefecture|Shimane Prefecture|Tottori Prefecture',
 'Kanto':'Tokyo|Kanagawa Prefecture|Gunma Prefecture|Saitama Prefecture|Chiba Prefecture|Ibaraki Prefecture|Tochigi Prefecture',
 'Hokuriku':'Fukui Prefecture|Ishikawa Prefecture|Toyama Prefecture',
 'Koshinetsu':'Niigata Prefecture|Nagano Prefecture|Yamanashi Prefecture',
 'Tokai':'Aichi Prefecture|Gifu Prefecture|Shizuoka Prefecture',
 'Northern Tohoku':'Aomori Prefecture|Akita Prefecture|Iwate Prefecture',
 'Southern Tohoku':'Fukushima Prefecture|Miyagi Prefecture|Yamagata Prefecture',
 'Hokkaido':'Hokkaidō', 'Okinawa':'Okinawa Prefecture'})
ROMANIA = mapping({
 'Banat-Crișana':'Arad|Timiș|Caraș-Severin|Bihor',
 'Northern Transylvania':'Cluj|Sălaj|Satu Mare|Maramureș|Bistrița-Năsăud|Mureș|Harghita|Covasna',
 'Southern Transylvania':'Alba|Hunedoara|Sibiu|Brașov',
 'Moldavia':'Suceava|Botoșani|Neamț|Iași|Vaslui|Bacău|Vrancea|Galați',
 'Oltenia':'Mehedinți|Dolj|Gorj|Olt|Vâlcea',
 'Wallachia':'Argeș|Bucharest|Dâmbovița|Giurgiu|Ilfov|Prahova|Teleorman|Buzău|Brăila|Călărași|Ialomița',
 'Dobruja':'Constanța|Tulcea'})
TURKEY = mapping({
 'Thrace':'Edirne|Kırklareli|Tekirdağ', 'Istanbul':'Istanbul',
 'Izmir':'İzmir|Manisa|Uşak', 'South Aegean':'Aydın|Denizli|Muğla',
 'Balikesir':'Balıkesir|Çanakkale', 'Bursa':'Bursa|Bilecik|Yalova',
 'Kocaeli':'Bolu|Düzce|Kocaeli|Sakarya', 'Eskisehir':'Afyonkarahisar|Eskişehir|Kütahya',
 'Antalya':'Antalya|Burdur|Isparta',
 'Ankara':'Ankara|Bartın|Karabük|Kırıkkale|Kırşehir|Zonguldak|Çankırı',
 'Samsun':'Amasya|Kastamonu|Samsun|Sinop|Tokat|Yozgat|Çorum',
 'Konya':'Aksaray|Karaman|Konya|Mersin', 'Adana':'Adana|Kayseri|Nevşehir|Niğde',
 'Sivas':'Sivas|Malatya', 'Trabzon':'Artvin|Bayburt|Erzincan|Giresun|Gümüşhane|Ordu|Rize|Trabzon',
 'Erzurum':'Ardahan|Ağrı|Erzurum|Iğdır|Kars', 'Van':'Bitlis|Hakkâri|Muş|Siirt|Van|Şırnak',
 'Diyarbakir':'Batman|Bingöl|Diyarbakır|Elazığ|Mardin|Tunceli',
 'Gaziantep':'Gaziantep|Kahramanmaraş|Kilis|Osmaniye',
 'Middle Euphrates':'Adıyaman|Şanlıurfa', 'Hatay':'Hatay'})
KOREA = mapping({'Gyeonggi':'Gyeonggi|Seoul|Incheon','Gangwon':'Gangwon',
 'Chungcheong':'North Chungcheong|South Chungcheong|Daejeon|Sejong',
 'North Jeolla':'North Jeolla','South Jeolla':'South Jeolla|Gwangju',
 'North Gyeongsang':'North Gyeongsang|Daegu','South Gyeongsang':'South Gyeongsang|Busan|Ulsan','Jeju':'Jeju'})
TAIWAN = mapping({'Northern Taiwan':'Taipei|New Taipei|Keelung|Taoyuan|Hsinchu|Miaoli',
 'Central Taiwan':'Taichung City|Changhua|Nantou|Yunlin',
 'Southern Taiwan':'Chiayi|Tainan|Kaohsiung|Pingtung',
 'Eastern Taiwan':'Yilan|Hualien|Taitung','Kinmen':'Kinmen','Penghu':'Penghu'})
EGYPT = mapping({'Sinai':'North Sinai|South Sinai', 'Aswan':'Aswan',
 'Upper Egypt':'Luxor|Qena|Sohag|Asyut', 'Middle Egypt':'Beni Suef|Faiyum|Minya',
 'Red Sea Coast':'Red Sea','Matrouh':'Matrouh','New Valley':'New Valley',
 'Suez Canal':'Suez|Ismailia|Port Said','Eastern Delta':'Al Sharqia|Dakahlia|Damietta',
 'Western Delta':'Beheira|Gharbia|Kafr el-Sheikh|Monufia|Qalyubia',
 'Alexandria':'Alexandria','Cairo':'Cairo','Giza':'Giza'})
PAPUA = mapping({'Sepik':'Sandaun|East Sepik', 'Western Papua':'Western|Gulf',
 'Papuan Highlands':'Chimbu|Enga|Western Highlands|Southern Highlands|Eastern Highlands',
 'Northern Papua':'Madang|Morobe','Southern Papua':'Central|Port Moresby|Oro|Milne Bay',
 'Bismarck Archipelago':'West New Britain|East New Britain|New Ireland|Manus',
 'Bougainville':'of Bougainville'})

# Existing scenario controllers are used, including overseas dependencies.
ADM_COUNTRY = {'France':'FRA','Netherlands':'HOL','Japan':'JAP','Denmark':'DEN',
 'United States of America':'USA','Australia':'AST','Turkey':'TUR','Norway':'NRY',
 'United Kingdom':'ENG','Romania':'ROM','Bulgaria':'BUL','Israel':'ISR','Egypt':'EGY',
 'Eritrea':'ERI','Gabon':'GAB','Syria':'SYR','South Korea':'KOR','Taiwan':'TAI',
 'Papua New Guinea':'PAP','Bosnia and Herzegovina':'BOS','Libya':'LBA',
 'Spain':'SPR','Cuba':'CUB','Guatemala':'GUA','Honduras':'HON','Costa Rica':'COS'}

def native_group(tag, p):
    n = p.get('name_en') or p.get('name') or 'Unnamed'; code=p.get('adm1_code','')
    if tag=='FRA': return FRANCE.get(n, n)
    if tag=='HOL':
        return mapping({'Northern Netherlands':'Groningen|Friesland|Drenthe',
          'Eastern Netherlands':'Overijssel|Gelderland|Flevoland',
          'Western Netherlands':'North Holland|South Holland|Utrecht|Zeeland',
          'Southern Netherlands':'North Brabant|Limburg',
          'Caribbean Netherlands':'Saba|Sint Eustatius'}) .get(n,n)
    if tag=='JAP': return JAPAN.get(n,n)
    if tag=='DEN': return 'Capital Region' if code=='DNK-3419' else n
    if tag=='USA': return 'Washington, D.C.' if code=='USA-3556' else n
    if tag=='TUR': return TURKEY.get(n,n)
    if tag=='ROM': return ROMANIA.get(n,n)
    if tag=='KOR': return KOREA.get(n,n)
    if tag=='TAI': return TAIWAN.get(n,n)
    if tag=='EGY': return EGYPT.get(n,n)
    if tag=='PAP': return PAPUA.get(n,n)
    if tag=='NRY':
        return mapping({'Northern Norway':'Finnmark|Troms','Nordland':'Nordland',
          'Trøndelag':'Nord-Trøndelag|Sør-Trøndelag',
          'Western Norway':'Møre og Romsdal|Sogn og Fjordane|Hordaland|Rogaland',
          'Southern Norway':'Aust-Agder|Vest-Agder|Telemark|Vestfold',
          'Eastern Norway':'Oslo|Akershus|Østfold|Buskerud|Hedmark|Oppland'}).get(n,n)
    if tag=='BUL':
        if n in ['Dobrich','Silistra']: return 'South Dobruja'
        return mapping({'Western Bulgaria':'Blagoevgrad|Kyustendil|Montana|Pazardzhik|Pernik|Smolyan|Sofia|Vidin|Vratsa',
          'Northern Bulgaria':'Gabrovo|Lovech|Pleven|Ruse|Veliko Tarnovo|Razgrad|Shumen|Targovishte',
          'Southern Bulgaria':'Burgas|Sliven|Yambol|Stara Zagora|Haskovo|Kardzhali|Plovdiv',
          'Varna':'Varna'}).get(n,n)
    if tag=='ERI': return 'Western Eritrea' if n in ['Gash-Barka','Anseba'] else 'Eastern Eritrea'
    if tag=='GAB': return 'Western Gabon' if n in ['Estuaire','Ogooué-Maritime','Moyen-Ogooué','Ngounié','Nyanga'] else 'Eastern Gabon'
    if tag=='SYR': return 'Quneitra' if n=='Western al-Samadania' else n
    if tag=='BOS':
        if n=='Brčko': return 'Brčko District'
        if n=='Posavina Canton': return 'Federation — Posavina'
        if 'Srpska' in (p.get('region') or ''): return 'Republika Srpska'
        return 'Federation — Herzegovina' if n in ['Herzegovina-Neretva Canton','West Herzegovina Canton','Livno'] else 'Federation — Bosnia'
    if tag=='LBA':
        return mapping({'Tripoli':'Tripoli District|Jafara|Zawiya|Nuqat al Khams','Misrata':'Misrata|Murqub',
          'Derna':'Al Qubbah|Jabal al Akhdar','Sabha':'Sabha|Wadi al Hayaa|Ash Shati'}).get(n,n)
    if tag=='SPR':
        # Correct all community boundaries, retaining Ceuta/Melilla/Olivenza separately below.
        return mapping({'Basque Country':'Araba / Álava|Biscay|Gipuzkoa','La Rioja':'La Rioja',
          'Castile and León':'Ávila|Burgos|León|Palencia|Salamanca|Segovia|Soria|Valladolid|Zamora',
          'Castilla-La Mancha':'Albacete|Ciudad Real|Cuenca|Guadalajara|Toledo',
          'Madrid':'Community of Madrid','Andalusia':'Almería|Cádiz|Córdoba|Granada|Huelva|Jaén|Málaga|Seville',
          'Catalonia':'Barcelona|Girona|Lleida|Tarragona','Valencia':'Alicante|Castellón|Valencia',
          'Galicia':'A Coruña|Lugo|Ourense|Pontevedra','Aragon':'Huesca|Teruel|Zaragoza',
          'Extremadura':'Badajoz|Cáceres','Canary Islands':'Las Palmas|Santa Cruz de Tenerife'}).get(n,n)
    if tag=='CUB':
        return mapping({'Western Cuba':'Pinar del Río|Artemisa|Havana|Mayabeque|Matanzas|Isla de la Juventud',
          'Central Cuba':'Camagüey|Ciego de Ávila|Cienfuegos|Sancti Spíritus|Villa Clara',
          'Eastern Cuba':'Granma|Guantánamo|Holguín|Las Tunas|Santiago de Cuba'}).get(n,n)
    if tag=='GUA': return 'Petén' if n=='Petén' else 'Southern Guatemala'
    if tag=='HON': return 'Eastern Honduras' if n in ['Olancho','Gracias a Dios','Colón'] else 'Western Honduras'
    if tag=='COS': return 'Costa Rica'
    if tag=='ENG':
        r=p.get('region') or ''
        if r in ['East Wales','West Wales and the Valleys']: return 'Wales'
        if r=='Northern Ireland': return 'Northern Ireland'
        if r=='Greater London': return 'Greater London'
        if n in ['Cornwall','Isles of Scilly']: return 'Cornwall'
        if n in ['Devon','Plymouth','Torbay']: return 'Devon'
        if r=='Highlands and Islands': return n if n in ['Outer Hebrides','Orkney Islands','Shetland Islands'] else 'Scottish Highlands'
        if r=='North Eastern': return 'Northeast Scotland'
        if r=='Eastern': return 'Eastern Scotland'
        if r=='South Western': return 'Southwest Scotland'
        return {'East':'East Anglia','South East':'Southeast England','South West':'Southwest England',
          'North East':'Northeast England','North West':'Northwest England','East Midlands':'East Midlands',
          'West Midlands':'West Midlands','Yorkshire and the Humber':'Yorkshire'}.get(r,n)
    return n

def main():
    snapshot()
    oldw=read(BASE/'data/world.json'); world=copy.deepcopy(oldw)
    oldstates=np.load(BASE/'tools/cartography/grouped_atlas_022r2.npz')['regions']
    oldps=read(BASE/'data/provinces.json')
    oldprov=np.load(BASE/'tools/cartography/province_atlas_0207.npz')['provinces']
    features=read(SRC/'geographic_subdivisions.geojson')['features']
    disputes=read(SRC/'disputed_areas.geojson')['features']
    ownerlut=np.zeros(8192,np.uint16)
    for k,s in oldw['regions'].items(): ownerlut[int(k)]=oldw['countries'][s['owner']]['index']
    owners=ownerlut[oldstates]
    states=oldstates.copy(); records=copy.deepcopy(oldw['regions']); nextid=max(map(int,records))+1
    oldboxes=find_objects(oldstates,max_label=8191)
    identities={}; audit=[]
    def identity(tag,name,code='',protected=''):
        nonlocal nextid
        key=(tag,name)
        if key not in identities:
            sid=nextid; nextid+=1; identities[key]=sid
            records[str(sid)]={'id':sid,'name':name,'owner':tag,'population':0,'buildings':{},'provinces':[],
              'cores':[tag],'claims':[],'source_states':[],'geographic_divisions':[], 'geographic_codes':[],
              'map_center':[0,0],'area_km2':0,'demographic_profile':tag,'protected_territory':'',
              'protected_territory_name':'','protected_territories':[],
              'population_source':'Retained 0.2.0.7 population, transferred by area overlap.'}
        sid=identities[key];s=records[str(sid)]
        if code and code not in s['geographic_codes']:s['geographic_codes'].append(code)
        if protected and protected not in s['protected_territories']:
            s['protected_territories'].append(protected);s['protected_territory']=protected;s['protected_territory_name']=name
        return sid
    # The native atlas is rasterized once. Geometry is always selected by ADM1
    # identity, never a nearby MD label or its share of a country-wide budget.
    admin=rasterize([(f['geometry'],i+1) for i,f in enumerate(features)],out_shape=(H,W),
      transform=from_bounds(-180,-90,180,90,W,H),dtype='uint16')
    print('ADM1_READY',len(features),flush=True)
    for tag in sorted(set(ADM_COUNTRY.values())):
        index=world['countries'][tag]['index']; mask=owners==index
        lut=np.zeros(len(features)+1,np.uint16)
        for i,f in enumerate(features,1):
            p=f['properties']
            if ADM_COUNTRY.get(p.get('admin'))!=tag and not (tag=='FRA' and p.get('admin') in ['Andorra','Monaco']):continue
            name=p['admin'] if tag=='FRA' and p.get('admin') in ['Andorra','Monaco'] else native_group(tag,p)
            sid=identity(tag,name,p.get('adm1_code',''))
            lut[i]=sid
            n=p.get('name_en') or p.get('name')
            if n and n not in records[str(sid)]['geographic_divisions']:records[str(sid)]['geographic_divisions'].append(n)
        assigned=lut[admin];assigned[~mask]=0
        # Fill generalized coastline gaps locally, before consulting old
        # labels. Otherwise an old merged mainland label can survive as a
        # thin extra state (notably the Dutch coast).
        yy,xx=np.nonzero(mask&(assigned==0))
        if len(xx):
            sy,sx=np.nonzero(assigned>0);step=max(1,len(sx)//300000)
            tree=cKDTree(xyz((sx[::step]+.5)/W*360-180,90-(sy[::step]+.5)/H*180))
            d,j=tree.query(xyz((xx+.5)/W*360-180,90-(yy+.5)/H*180))
            near=d*6371.0088<75
            assigned[yy[near],xx[near]]=assigned[sy[::step][j[near]],sx[::step][j[near]]]
            del tree,sy,sx,yy,xx,d,j
        # Overseas records have different Natural Earth admin owners. Group
        # only within the existing territory; never snap an overseas island
        # across an ocean to a mainland administrative polygon.
        for k,s in oldw['regions'].items():
            if s['owner']!=tag:continue
            bb=oldboxes[int(k)-1];local=assigned[bb];oldlocal=oldstates[bb]
            m=(oldlocal==int(k))&mask[bb]&(local==0)
            if not m.any():continue
            oldnames=s.get('geographic_divisions',[]) or [s['name']]
            name=s['name']
            if tag=='FRA':
                if any('Guiana' in x for x in oldnames):name='French Guiana'
                elif any(x in ['North','South','Loyalty Islands','New Caledonia'] for x in oldnames):name='New Caledonia'
                elif any(x in ['Alo','Sigave','Uvea','Wallis and Futuna'] for x in oldnames):name='Wallis and Futuna'
                elif any(x in ['Tuamotu Archipelago','Windward Islands','Leeward Islands','Austral Islands','Marquesas Islands','French Polynesia'] for x in oldnames):name='French Polynesia'
                elif any(x in ['Miquelon-Langlade','St Pierre and Miquelon'] for x in oldnames):name='Saint Pierre and Miquelon'
                elif 'Mayotte' in oldnames and s.get('protected_territory') not in ['B24','B25','B27']:name='Mayotte'
            if tag=='HOL':
                name='Aruba, Curaçao and Bonaire' if any(x in ['Aruba','Curaçao','Bonaire'] for x in oldnames) else 'Caribbean Netherlands' if any(x in ['Saba','Sint Eustatius'] for x in oldnames) else name
            if tag=='USA':
                if any(x in ['Saint Croix','Saint John','Saint Thomas','United States Virgin Islands'] for x in oldnames):name='United States Virgin Islands'
                elif name in ['Guantanamo Bay USNB','USNB, Guantanamo Bay']:name='Guantanamo Bay'
                elif name in ['Diego Garcia NSF','Diego Garcia']:name='Diego Garcia'
                elif name in ['Wake Island','Wake Atoll']:name='Wake Island'
                elif any(x in ['Eastern District','Western District',"Manu'a Islands",'American Samoa'] for x in oldnames):name='American Samoa'
            if tag=='ENG' and name=='Isles of Scilly':name='Cornwall'
            if tag=='ENG':
                if name in ['Falkland Islands','Falkland Is.']:name='Falkland Islands'
                if name in ['South Georgia and the South Sandwich Islands','S. Georgia','S. Sandwich Is.']:name='South Georgia and the South Sandwich Islands'
                if name in ['Southern England','Diego Garcia NSF','Br. Indian Ocean Ter.']:name='British Indian Ocean Territory'
            # Coastline fringes near mainland ADM1 should join that same local
            # source unit. Distant islands retain their named identity.
            covered=local[oldlocal==int(k)]
            covered=covered[covered>0]
            if len(covered) and tag not in ['HOL']:
                sid=int(np.bincount(covered).argmax());local[m]=sid
            else: local[m]=identity(tag,name)
        # Remove cartographic duplicate island labels where the user requested
        # territory-wide unions, including covered pieces assigned above.
        if tag=='FRA':
            for names,group in [(['North','South','Loyalty Islands'],'New Caledonia'),
              (['Tuamotu Archipelago','Windward Islands','Leeward Islands','Austral Islands','Marquesas Islands'],'French Polynesia'),
              (['Alo','Sigave','Uvea'],'Wallis and Futuna'),(['Miquelon-Langlade','St Pierre and Miquelon'],'Saint Pierre and Miquelon')]:
                for sid,s in list(records.items()):
                    if s['owner']==tag and s['name'] in names:assigned[assigned==int(sid)]=identity(tag,group)
            for sid,s in list(records.items()):
                if s['owner']==tag and s['name'] in ['Scattered Islands in the Indian Ocean','Juan De Nova I.','Europa Island','Bassas da India','Tromelin I.','Glorioso Is.']:
                    assigned[assigned==int(sid)]=identity(tag,'Scattered Islands in the Indian Ocean')
        states[mask]=assigned[mask]
        audit.append({'country':tag,'rule':'Explicit Natural Earth administrative unions; overseas allocation independent.'})
        print('AUTHORED_COUNTRY',tag,len(np.unique(states[mask])),flush=True)
    del admin,assigned
    def polygon(geometry, tag, name, protected='', controllers=None, change_owner=False):
        from shapely.geometry import shape
        bounds=shape(geometry).bounds
        x0=max(0,int((bounds[0]+180)/360*W)-2);x1=min(W,int((bounds[2]+180)/360*W)+3)
        y0=max(0,int((90-bounds[3])/180*H)-2);y1=min(H,int((90-bounds[1])/180*H)+3)
        if x1<=x0 or y1<=y0:return
        m=rasterize([(geometry,1)],out_shape=(y1-y0,x1-x0),transform=from_bounds(x0/W*360-180,90-y1/H*180,x1/W*360-180,90-y0/H*180,x1-x0,y1-y0),dtype='uint8').astype(bool)
        land=owners[y0:y1,x0:x1]>0;m&=land
        accepted=controllers or [tag]
        m&=np.isin(owners[y0:y1,x0:x1],[world['countries'][t]['index'] for t in accepted])
        if m.any():
            sid=identity(tag,name,protected=protected);states[y0:y1,x0:x1][m]=sid
            if change_owner:owners[y0:y1,x0:x1][m]=world['countries'][tag]['index']
            return sid
    # Explicit whole-country consolidations override the old generic claim cap.
    for tag,name in [('BHU','Bhutan'),('BLZ','Belize'),('ELS','El Salvador'),('COM','Comoros')]:
        states[owners==world['countries'][tag]['index']]=identity(tag,name)
    # Native Denmark's capital polygon also contains Bornholm, which must not
    # be used as the name for two mainland regions.
    from shapely.geometry import box, mapping as geometry_mapping
    # Use the ADM1 entity source for Bosnia: the finer Natural Earth canton
    # layer has overlapping Brcko/Bijeljina geometry and a mislabeled entity.
    bosnia=read(SRC/'bosnia_entities_0208.geojson')['features']
    for f in bosnia:
        if f['properties']['shapeName']=='Republika Srpska':polygon(f['geometry'],'BOS','Republika Srpska',protected='BIH-SRP')
    for f in bosnia:
        if f['properties']['shapeName']=='Brčko District':polygon(f['geometry'],'BOS','Brčko District',protected='BIH-BRC')
    polygon(geometry_mapping(box(14.5,54.9,15.4,55.5)),'DEN','Bornholm')
    # European Canakkale is Gallipoli; the Asian part stays in Balikesir.
    # Restrict that mask to the actual European coastline, not all of the box.
    # A polyline along the Dardanelles separates Gallipoli from Asian Turkey.
    thrace={'type':'Polygon','coordinates':[[[25.5,40.0],[26.15,40.03],[26.25,40.15],[26.39,40.21],[26.58,40.37],[26.7,40.5],[27.0,40.7],[28.0,40.95],[28.0,42.2],[25.5,42.2],[25.5,40.0]]]}
    # Reassign the box from native Canakkale/Istanbul classification before
    # applying only the authored European Thrace polygon below.
    # (Native Thrace provinces remain included in their entirety.)
    for i,f in enumerate(features):
        p=f['properties'];n=p.get('name_en') or p.get('name')
        if p.get('admin')=='Turkey' and n=='Çanakkale':polygon(f['geometry'],'TUR','Balikesir')
    polygon(thrace,'TUR','Thrace')
    # Sinai is one peninsula. Governorates crossing the canal are clipped at
    # an authored canal line, preserving their west-bank mainland portions.
    sinai={'type':'Polygon','coordinates':[[[32.31,31.35],[32.34,30.9],[32.3,30.6],[32.5,30.35],[32.57,30.0],[32.56,29.85],[33.1,27.3],[35.1,27.3],[35.1,31.4],[32.31,31.35]]]}
    polygon(sinai,'EGY','Sinai')
    # Natural Earth map units include whole breakaway territories that are
    # absent from its separate disputed-area file (notably Timor-Leste).
    for f in read(SRC/'natural_earth_map_units.geojson')['features']:
        if f['properties'].get('ADM0_A3')=='TLS':polygon(f['geometry'],'IND','Timor-Leste',protected='TLS')
    # Keep meaningful territorial boundaries even when above normal budgets.
    protected_names={'B18':('JAP','Senkaku'),'B10':('KOR','Southern DMZ'),
      'B84':('KOR','Baengnyeong Islands'),'B39':('KOR','Dokdo'),
      'B16':('ISR','Golan Heights'),'B58':('ISR','Shebaa Farms'),
      'B98':('ISR','East Jerusalem'),'B78':('ISR','Latrun'),
      'B93':('EGY','Halayib Triangle'),'B68':('EGY','Tiran and Sanafir'),
      'B49':('SYR','UNDOF Zone'),'B60':('SPR','Ceuta'),'B61':('SPR','Melilla'),
      'B67':('SPR','Olivenza'),'B55':('SPR','Gibraltar — Spanish sector'),
      'B50':('CUB','Guantanamo Bay — Cuban sector')}
    for f in disputes:
        code=f['properties']['BRK_A3']
        if code in protected_names:polygon(f['geometry'],*protected_names[code],protected=code)
        if code=='B30':polygon(f['geometry'],'SML','Somaliland',protected=code,controllers=['SML','PUN'],change_owner=True)
        if code=='B37':polygon(f['geometry'],'SOO','South Ossetia',protected=code,controllers=['SOO','GEO'],change_owner=True)
    # Remaining tiny Somali boundary fringes are integrated into the nearest
    # substantial same-controller state, rather than becoming extra states.
    for tag,name in [('SML','Somaliland'),('SOO','South Ossetia')]:
        states[owners==world['countries'][tag]['index']]=identity(tag,name,protected='B30' if tag=='SML' else 'B37')
    # Retain Puntland outside the Somaliland footprint with geographic labels.
    for sid,s in list(records.items()):
        if s['owner']=='PUN' and s['name']=='Somaliland':
            states[states==int(sid)]=identity('PUN','Nugal')
    # Remove the Georgian protected-polygon slivers after the explicit shell fix.
    for sid in ['415','416','417']:
        m=(states==int(sid))&(owners==world['countries']['GEO']['index'])
        if m.any():states[m]=414
    # Correct the accidental mainland name inherited from Natural Earth.
    records['1031']['name']='Altai Krai';records['1074']['name']='Moscow Oblast';records['1075']['name']='Moscow City'
    # Northern Khabarovsk extends far beyond Outer Manchuria. Keep the native
    # Amur/Jewish/Primorye divisions; separate the Okhotsk-facing northern area.
    # This gameplay cut approximates the Uda/Stanovoy transition at province
    # scale; it is explicitly not an archival treaty-boundary reconstruction.
    kcut={'type':'Polygon','coordinates':[[[130.0,54.0],[134.0,54.7],[137.0,54.9],[140.0,54.7],[142.0,54.2],[143.0,54.2],[143.0,64],[130.0,64],[130.0,54.0]]]}
    khab=next(int(k) for k,s in oldw['regions'].items() if s['owner']=='SOV' and s['name']=='Khabarovsk Krai')
    saved=states.copy();newid=polygon(kcut,'SOV','Okhotsk Krai')
    states[(saved!=khab)&(states==newid)]=saved[(saved!=khab)&(states==newid)]
    records[str(khab)]['name']='Lower Amur';del saved
    # Karelian Isthmus: authored coarse historical line, clipped to Leningrad.
    # Ceded Karelia's other parts lie in the existing Karelia state already.
    isthmus={'type':'Polygon','coordinates':[[[27.0,62.0],[32.0,62.0],[32.0,60.82],[31.5,60.72],[31.15,60.60],[30.8,60.53],[30.55,60.35],[30.45,60.2],[29.8,60.1],[27.0,60.1],[27.0,62.0]]]}
    saved=states.copy();newid=polygon(isthmus,'SOV','Karelian Isthmus')
    states[(saved!=1011)&(states==newid)]=saved[(saved!=1011)&(states==newid)]
    del saved
    moved=[]
    for p in oldps.values():
        if p['region']==1010 and p['local_index'] in [14,8,24,13,3]:
            states[oldprov==p['id']]=1043;moved.append({'province_id':p['id'],'old_local_index':p['local_index']})
    # Neutral names preserve separately reserved later-conflict geometry.
    for sid,name in [('1256','Luhansk — Southern Fringe'),('1260','Northern Luhansk'),('1274','Southern Luhansk'),
      ('1261','Northern Donetsk'),('1275','Donetsk — Western Fringe'),('1276','Southern Donetsk'),
      ('1250','Kyiv Oblast'),('1273','Kyiv City'),('1262','Crimean Border Strip'),('1265','Sevastopol Border Strip')]:records[sid]['name']=name
    # Find remaining duplicated names, retaining geographic and city identities.
    active=set(map(int,np.unique(states)))-{0,8191};records={k:s for k,s in records.items() if int(k) in active}
    # Recompute all retained records and transfer actual overlapping accounts.
    old_to_new=defaultdict(Counter);overlap=defaultdict(Counter)
    for top in range(0,H,128):
        a=states[top:top+128];b=oldstates[top:top+128];m=(a>0)&(a<8191)
        keys,n=np.unique(a[m].astype(np.uint32)*8192+b[m],return_counts=True)
        for k,q in zip(keys,n):
            sid,oid=divmod(int(k),8192);old_to_new[oid][sid]+=int(q);overlap[sid][oid]+=int(q)
    boxes=find_objects(states,max_label=nextid)
    for k,s in records.items():
        sid=int(k);bb=boxes[sid-1];yy,xx=np.nonzero(states[bb]==sid);yy+=bb[0].start;xx+=bb[1].start
        s.update(population=0,buildings={},provinces=[],map_center=focus(yy,xx),area_km2=round(float(AREA[yy].sum()),2))
        oldids=list(overlap[sid]);total=sum(overlap[sid].values());rights=[i for i in oldids if overlap[sid][i]>=total*.05]
        s['source_states']=sorted({j for i in oldids for j in oldw['regions'][str(i)]['source_states']})
        s['cores']=sorted({t for i in rights for t in oldw['regions'][str(i)]['cores']}|{s['owner']})
        s['claims']=sorted({t for i in rights for t in oldw['regions'][str(i)]['claims']})
    for oid,targets in old_to_new.items():
        old=oldw['regions'][str(oid)];ids=sorted(targets);weights=[targets[i] for i in ids]
        for sid,n in zip(ids,alloc(old['population'],weights)):records[str(sid)]['population']+=int(n)
        for building,total in old['buildings'].items():
            for sid,n in zip(ids,alloc(total,weights)):
                if n:records[str(sid)]['buildings'][building]=records[str(sid)]['buildings'].get(building,0)+int(n)
    # Distinguish real repeated administrative names without arbitrary numbering.
    dup=defaultdict(list)
    for s in records.values():dup[(s['owner'],s['name'])].append(s)
    for (tag,name),items in dup.items():
        if len(items)<2:continue
        for s in items:
            if s.get('protected_territory'):suffix=s.get('protected_territory_name') or 'Protected Area'
            elif s['area_km2']<100:suffix='Coastal Islands'
            else:suffix='North' if s['map_center'][1]<np.mean([x['map_center'][1] for x in items]) else 'South'
            s['name']=name+' — '+suffix
    # Split only provinces crossed by a corrected state line. An original
    # province ID remains with its largest piece; added pieces receive new IDs.
    pieces=defaultdict(Counter)
    for top in range(0,H,128):
        a=states[top:top+128];p=oldprov[top:top+128];m=p>0
        keys,n=np.unique(p[m].astype(np.uint32)*8192+a[m],return_counts=True)
        for k,q in zip(keys,n):pid,sid=divmod(int(k),8192);pieces[pid][sid]+=int(q)
    ids={};ps={};nextpid=max(map(int,oldps))+1
    for pid,parts in sorted(pieces.items()):
        dominant=max(parts,key=parts.get)
        for sid in sorted(parts):
            q=pid if sid==dominant else nextpid
            if sid!=dominant:nextpid+=1
            ids[(pid,sid)]=q;record=copy.deepcopy(oldps[str(pid)]);record.update(id=q,region=sid,neighbors=[],cities=[],urban_group='')
            if q!=pid:record['buildings']={}
            ps[str(q)]=record
    original_province={newpid:oldpid for (oldpid,sid),newpid in ids.items()}
    # Reconstruct categorical provinces without allocating a giant dense LUT.
    province=np.zeros_like(oldprov)
    code_keys=np.array(sorted(pid*8192+sid for pid,sid in ids),np.uint32)
    code_values=np.array([ids[divmod(int(k),8192)] for k in code_keys],np.uint16)
    for top in range(0,H,128):
        a=states[top:top+128];p=oldprov[top:top+128];m=p>0;code=p[m].astype(np.uint32)*8192+a[m]
        province[top:top+128][m]=code_values[np.searchsorted(code_keys,code)]
    del oldprov,oldstates,owners
    boxes=find_objects(province,max_label=nextpid)
    for k,p in ps.items():
        bb=boxes[int(k)-1];yy,xx=np.nonzero(province[bb]==int(k));yy+=bb[0].start;xx+=bb[1].start
        p.update(map_center=focus(yy,xx),area_km2=round(float(AREA[yy].sum()),2),geometry_source='Accepted terrain-guided province, intersected with authored geographic state boundaries')
        records[str(p['region'])]['provinces'].append(int(k))
    for s in records.values():
        for j,pid in enumerate(sorted(s['provinces']),1):ps[str(pid)]['local_index']=j
    # Adjacencies come from the actual final categorical atlas.
    edges=Counter()
    for top in range(0,H,128):
        for l,r in [(province[top:top+128,:-1],province[top:top+128,1:]),(province[top:min(H-1,top+128)],province[top+1:min(H,top+129)])]:
            m=(l>0)&(r>0)&(l!=r)
            codes=np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m])
            keys,counts=np.unique(codes,return_counts=True)
            edges.update({int(k):int(n) for k,n in zip(keys,counts)})
    l,r=province[:,0],province[:,-1];m=(l>0)&(r>0)&(l!=r)
    edges.update(int(min(a,b))*65536+int(max(a,b)) for a,b in zip(l[m],r[m]))
    # Intersecting two valid atlases creates tiny boundary shards. Absorb only
    # those NEW shards into an adjacent province of the same corrected state.
    # Original provinces (and the five requested Karelia IDs) stay identifiable.
    aliases={int(k):int(k) for k in ps}
    def root(pid):
        while aliases[pid]!=pid:aliases[pid]=aliases[aliases[pid]];pid=aliases[pid]
        return pid
    absorbed=[]
    for pid in sorted((int(k) for k in ps if int(k)>max(map(int,oldps))),key=lambda i:ps[str(i)]['area_km2']):
        p=ps[str(pid)];original=oldps[str(original_province[pid])]
        if p['area_km2']>=min(1000,max(25,original['area_km2']*.3)):continue
        candidates=Counter()
        for code,n in edges.items():
            a,b=map(root,divmod(code,65536))
            if a==b or pid not in [a,b]:continue
            other=b if a==pid else a
            if ps[str(other)]['region']==p['region']:candidates[other]+=n
        if candidates:
            target=max(candidates,key=lambda i:(candidates[i],ps[str(i)]['area_km2']))
            aliases[pid]=target;absorbed.append(pid)
    if absorbed:
        lut=np.zeros(nextpid+1,np.uint16)
        for pid in aliases:lut[pid]=root(pid)
        for top in range(0,H,128):province[top:top+128]=lut[province[top:top+128]]
        for pid in absorbed:ps.pop(str(pid))
        for s in records.values():s['provinces']=[]
        boxes=find_objects(province,max_label=nextpid)
        for k,p in ps.items():
            bb=boxes[int(k)-1];yy,xx=np.nonzero(province[bb]==int(k));yy+=bb[0].start;xx+=bb[1].start
            p.update(map_center=focus(yy,xx),area_km2=round(float(AREA[yy].sum()),2))
            records[str(p['region'])]['provinces'].append(int(k))
        for s in records.values():
            for j,pid in enumerate(sorted(s['provinces']),1):ps[str(pid)]['local_index']=j
    # A state intersection can separate two pieces of an existing province
    # on the SAME landmass. Keep genuine island groups, but reassign small
    # disconnected mainland pieces locally or give substantial pieces an ID.
    stateboxes=find_objects(states,max_label=8191);connectivity_pixels=0;connectivity_splits=0
    for key,s in records.items():
        bb=stateboxes[int(key)-1];sm=states[bb]==int(key);view=province[bb]
        land,_=label(sm,np.ones((3,3),bool))
        for pid in list(s['provinces']):
            parts,n=label(view==pid,np.ones((3,3),bool))
            if n<2:continue
            sizes=np.bincount(parts.ravel());partboxes=find_objects(parts);byland={};partland={}
            for j,pb in enumerate(partboxes,1):
                if pb is None:continue
                yy,xx=np.nonzero(parts[pb]==j);component=int(land[yy[0]+pb[0].start,xx[0]+pb[1].start]);partland[j]=component
                if component not in byland or sizes[j]>sizes[byland[component]]:byland[component]=j
            for j,component in partland.items():
                if byland[component]==j:continue
                piece=parts==j;around=binary_dilation(piece,np.ones((3,3),bool))&sm&~piece
                neighbors=view[around];neighbors=neighbors[(neighbors>0)&(neighbors!=pid)]
                if sizes[j]<=500 and len(neighbors):
                    target=int(np.bincount(neighbors).argmax());view[piece]=target;connectivity_pixels+=int(sizes[j])
                else:
                    newpid=nextpid;nextpid+=1;view[piece]=newpid
                    ps[str(newpid)]=copy.deepcopy(ps[str(pid)]);ps[str(newpid)].update(id=newpid,neighbors=[],cities=[],buildings={})
                    original_province[newpid]=original_province[pid];s['provinces'].append(newpid);connectivity_splits+=1
    used=set(map(int,np.unique(province)))-{0};ps={k:q for k,q in ps.items() if int(k) in used}
    for s in records.values():s['provinces']=[]
    boxes=find_objects(province,max_label=nextpid)
    for k,q in ps.items():
        bb=boxes[int(k)-1];yy,xx=np.nonzero(province[bb]==int(k));yy+=bb[0].start;xx+=bb[1].start
        q.update(map_center=focus(yy,xx),area_km2=round(float(AREA[yy].sum()),2),neighbors=[])
        records[str(q['region'])]['provinces'].append(int(k))
    for s in records.values():
        for j,pid in enumerate(sorted(s['provinces']),1):ps[str(pid)]['local_index']=j
    final_edges=set()
    for top in range(0,H,128):
        for l,r in [(province[top:top+128,:-1],province[top:top+128,1:]),(province[top:min(H-1,top+128)],province[top+1:min(H,top+129)])]:
            m=(l>0)&(r>0)&(l!=r);codes=np.minimum(l[m],r[m]).astype(np.uint32)*65536+np.maximum(l[m],r[m])
            final_edges.update(divmod(int(c),65536) for c in np.unique(codes))
    l,r=province[:,0],province[:,-1];m=(l>0)&(r>0)&(l!=r)
    final_edges.update(tuple(sorted([int(a),int(b)])) for a,b in zip(l[m],r[m]))
    for a,b in final_edges:ps[str(a)]['neighbors'].append(b);ps[str(b)]['neighbors'].append(a)
    for p in ps.values():p['neighbors'].sort()
    # Relink cities/scenery using their coordinates and controller, retaining
    # their existing urban-group identities and unchanged visual positions.
    cities=read(BASE/'data/cities.json');scene=read(BASE/'data/urban_scenery.json');oldurban=read(BASE/'data/urban_population.json')
    def locate(lon,lat,tag=None):
        x=int((lon+180)/360*W)%W;y=min(H-1,max(0,int((90-lat)/180*H)));pid=int(province[y,x])
        if pid and {tag,records[str(ps[str(pid)]['region'])]['owner']} in [{'PUN','SML'},{'GEO','SOO'}]:return pid
        if pid and (not tag or records[str(ps[str(pid)]['region'])]['owner']==tag):return pid
        # Local coastal snapping cannot attach distant cities to an unrelated country.
        for radius in [12,40]:
            yy,xx=np.mgrid[max(0,y-radius):min(H,y+radius+1),max(0,x-radius):min(W,x+radius+1)]
            q=province[yy,xx];valid=q>0
            if tag:
                lut=np.zeros(nextpid+1,bool)
                for k,p in ps.items():lut[int(k)]=records[str(p['region'])]['owner']==tag
                valid&=lut[q]
            if valid.any():
                d=np.where(valid,(yy-y)**2+(xx-x)**2,np.inf);j=np.unravel_index(np.argmin(d),d.shape);return int(q[j])
        return pid
    groups={}
    for c in cities:
        pid=locate(c['longitude'],c['latitude'],c['country'])
        if not pid:raise ValueError(('Unlinked city',c['name']))
        owner=records[str(ps[str(pid)]['region'])]['owner']
        c.update(province_id=pid,country=owner);p=ps[str(pid)];p['cities'].append(c['name'])
        gid=c.get('urban_group') or 'geographic_city_%05d'%pid
        if not p['urban_group']:p['urban_group']=gid
        c['urban_group']=p['urban_group']
    for kind in ['clusters','landmarks']:
        for record in scene[kind]:
            oldp=oldps[str(record['province'])];tag=oldw['regions'][str(oldp['region'])]['owner']
            pid=locate(record['longitude'],record['latitude'],tag)
            if not pid:raise ValueError(('Unlinked scenery',record.get('name')))
            p=ps[str(pid)];record['province']=pid
            if not p['urban_group']:p['urban_group']=record.get('group') or 'geographic_city_%05d'%pid
            record['group']=p['urban_group']
            if kind=='landmarks':record['country']=records[str(p['region'])]['owner']
    for p in ps.values():
        gid=p['urban_group'];p['kind']='city' if gid else 'rural'
        if gid and gid not in groups:
            groups[gid]=copy.deepcopy(oldurban['groups'].get(gid,{'id':gid,'name':p['cities'][0] if p['cities'] else gid,'cities':[]}))
            groups[gid].update(provinces=[],population_2000=0,settlement_population_2000=0,representative_buildings=0,country_at_start=records[str(p['region'])]['owner'])
        if gid:groups[gid]['provinces'].append(p['id'])
    account={'epoch':2000,'source':{'method':'Retained state totals; existing province population shares partitioned by geographic area only where split.'},'groups':groups,'states':{},'growth_enabled':False,'country_reconciliation_factors':{},'population_scope':'Geometry bookkeeping; demographic estimates not revised.'}
    for k,s in records.items():
        pp=s['provinces'];weights=[]
        for pid in pp:
            p=ps[str(pid)]
            original=oldps.get(str(pid))
            if original is None:
                original=oldps[str(original_province[pid])]
            weights.append(original.get('population_2000',0)*p['area_km2']/max(original.get('area_km2',0),.001))
        if not sum(weights):weights=[ps[str(pid)]['area_km2'] for pid in pp]
        for pid,n in zip(pp,alloc(s['population'],weights)):ps[str(pid)]['population_2000']=int(n)
        urban=[pid for pid in pp if ps[str(pid)]['urban_group']];shared=[pid for pid in pp if pid not in urban]
        urbanpop=sum(ps[str(pid)]['population_2000'] for pid in urban)
        account['states'][k]={'state':int(k),'population_2000':s['population'],'urban_provinces':urban,'shared_provinces':shared,'urban_population_2000':urbanpop,'shared_population_2000':s['population']-urbanpop,'raw_grid_population':0,'state_reconciliation_factor':1,'fallback_area_allocation':False}
    for p in ps.values():
        if p['urban_group']:groups[p['urban_group']]['population_2000']+=p['population_2000']
    for g in groups.values():g['settlement_population_2000']=g['population_2000'];g['provinces'].sort()
    for c in cities:c['population_2000']=ps[str(c['province_id'])]['population_2000']
    for r in scene['clusters']:
        if r['group'] in groups:groups[r['group']]['representative_buildings']+=len(r['instances'])
    micro=read(BASE/'data/microstate_geometry.json')
    records[str(micro['state'])].update(name='Vatican City',map_center=micro['center_uv'],area_km2=micro['nominal_area_km2'])
    ps[str(micro['province'])].update(map_center=micro['center_uv'],area_km2=micro['nominal_area_km2'])
    world['regions']=records;world['version']=VERSION;world['scenario_id']='bunny_world_2000_0_2_0_8';scene['version']=VERSION
    for tag,c in world['countries'].items():
        ss=[int(k) for k,s in records.items() if s['owner']==tag];c['regions']=sorted(ss)
        if not ss:raise ValueError(('Country lost all states',tag))
        u,v=c['map_center'];at=int(states[min(H-1,int(v*H)),int(u*W)%W])
        if at not in ss:at=max(ss,key=lambda i:records[str(i)]['population'])
        c['capital']=at;c['map_center']=records[str(at)]['map_center']
    world['map'].update(cartography='Authored geographic state unions; mainland, overseas and protected-area allocations independent.',regional_boundary_accuracy='Natural Earth ADM1 and map-unit geography with explicit country corrections; two historical Russian cuts are gameplay approximations.',province_geometry='Existing terrain-guided provinces split only at corrected state boundaries.',urban_population='Retained population totals and province shares; split shares allocated by area; demographic refinement deferred.')
    # Vatican is unchanged; host/province IDs remain stable under this patch.
    micro['host_state']=ps[str(micro['host_province'])]['region']
    for name,obj in [('world',world),('provinces',ps),('cities',cities),('urban_population',account),('urban_scenery',scene),('microstate_geometry',micro)]:write('data/'+name+'.json',obj)
    np.savez_compressed(SRC/'grouped_atlas_022r2.npz',regions=states)
    for name in ['province_atlas_022r2.npz','province_atlas_0208.npz']:np.savez_compressed(SRC/name,provinces=province)
    index=np.zeros((65536,3),np.uint8)
    for p in ps.values():index[p['id'],:2]=[p['region']&255,p['region']>>8]
    index[65535,:2]=[255,31];Image.fromarray(index.reshape(256,256,3)).save(ROOT/'assets/province_index.png')
    for i in range(4):
        y,x=i//2*4096,i%2*8192;q=province[y:y+4096,x:x+8192].copy();q[states[y:y+4096,x:x+8192]==8191]=65535
        Image.fromarray(np.stack([(q&255).astype(np.uint8),(q>>8).astype(np.uint8),np.zeros_like(q,np.uint8)],-1)).save(ROOT/'assets'/f'region_ids_{i}.png')
    report={'version':VERSION,'base_commit':BASE_COMMIT,'states':len(records),'provinces':len(ps),'split_provinces':len(ps)-len(oldps),'boundary_shards_absorbed':len(absorbed),'native_connectivity_repairs':{'reassigned_pixels':connectivity_pixels,'new_provinces':connectivity_splits},'countries':audit,'karelia_transfers':moved,
      'historical_approximations':['Karelian Isthmus uses an authored coarse pre-1940-border guide, clipped to Leningrad.','Northern Khabarovsk uses an authored Uda/Stanovoy transition guide; no archival treaty geometry is asserted.'],
      'controller_corrections':['Natural Earth Somaliland shell assigned to Somaliland rather than Puntland.','Natural Earth South Ossetia shell unified, removing Georgian-sector cartographic enclaves.'],
      'explicit_consolidation_exceptions':['Bhutan','Belize','French Guiana / Lawa Headwaters','Aruba, Curaçao and Bonaire','Comoros','Isles of Scilly into Cornwall','US Virgin Islands'],
      'state_counts':{tag:len(c['regions']) for tag,c in world['countries'].items()}}
    write('data/geography_0208_report.json',report)
    print('GEOGRAPHY_0208_COMPLETE',len(records),len(ps),'KARELIA',moved,flush=True)

if __name__=='__main__':main()
