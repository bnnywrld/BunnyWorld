"""Consolidate small islands/enclaves while retaining real boundary unions."""
from collections import defaultdict,Counter
import json,math
import numpy as np
from build_geography_0206 import ROOT,SRC,FEATURES,KEEP_NATIVE,pairs,write,xyz

w=json.load(open(ROOT/'data/world.json'));states=w['regions'];a=np.load(SRC/'grouped_atlas_022r2.npz')['regions']
bycode={f['properties']['adm1_code']:f['properties'] for f in FEATURES}
parent={int(k):int(k) for k in states};records={int(k):dict(v) for k,v in states.items()}
def root(i):
    while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
    return i
def merge(a,b,name=None):
    a,b=root(a),root(b)
    if a==b:return a
    if records[a]['area_km2']<records[b]['area_km2']:a,b=b,a
    x,y=records[a],records[b];parent[b]=a
    x['population']+=y['population'];x['area_km2']+=y['area_km2']
    for k,v in y['buildings'].items():x['buildings'][k]=x['buildings'].get(k,0)+v
    for k in ['source_states','geographic_codes','geographic_divisions','cores','claims']:x[k]=sorted(set(x[k]+y[k]))
    if name:x['name']=name
    del records[b];return a
byowner=defaultdict(list)
for k,s in records.items():byowner[s['owner']].append(k)
edges=pairs(a)
for tag,ids in byowner.items():
    # A microcountry is one State, regardless of the number of municipalities
    # or separate islands in the source administrative file.
    area=sum(records[i]['area_km2'] for i in ids)
    if area<5000:
        dest=ids[0]
        for i in ids[1:]:dest=merge(dest,i,w['countries'][tag]['name'])
        records[root(dest)]['name']=w['countries'][tag]['name'];continue
    admin_groups=defaultdict(list);admin_area=Counter()
    for i in ids:
        admins=set(bycode[c].get('admin','') for c in records[i]['geographic_codes'] if c in bycode)
        if len(admins)==1:
            name=next(iter(admins));admin_groups[name].append(i);admin_area[name]+=records[i]['area_km2']
    primary=admin_area.most_common(1)[0][0] if admin_area else ''
    for admin,group in admin_groups.items():
        if admin!=primary and admin_area[admin]<16000:
            dest=group[0]
            for i in group[1:]:dest=merge(dest,i,admin)
    # Source coastline omissions can leave a few outlying islets in a fallback
    # record. Rejoin a fallback to the identically named geographic State.
    named=defaultdict(list)
    for i in set(root(j) for j in ids):named[records[i]['name']].append(i)
    for name,group in named.items():
        if len(group)>1 and any(all(c.startswith('scenario:') for c in records[i]['geographic_codes']) for i in group):
            dest=group[0]
            for i in group[1:]:dest=merge(dest,i,name)
    # Tiny attached fragments become part of a neighboring State. Native
    # constitutional city-states such as Bremen and DC are preserved.
    while True:
        candidates=[]
        for i in set(root(j) for j in ids):
            s=records[i]
            own_admin=set(bycode[c].get('admin','') for c in s['geographic_codes'] if c in bycode)
            foreign=bool(own_admin) and primary not in own_admin
            if s['area_km2']<850 and (tag not in KEEP_NATIVE or foreign):candidates.append(i)
        done=False
        for i in sorted(candidates,key=lambda i:records[i]['area_km2']):
            border=Counter()
            for (l,r),n in edges.items():
                l,r=root(l),root(r)
                if l==i and r!=i and records[r]['owner']==tag:border[r]+=n
                if r==i and l!=i and records[l]['owner']==tag:border[l]+=n
            if border:
                merge(i,border.most_common(1)[0][0]);done=True;break
        if not done:break
    # Small island countries receive a few coherent archipelago States.
    while area<25000 and len(set(root(j) for j in ids))>4:
        current=sorted(set(root(j) for j in ids));i=min(current,key=lambda i:records[i]['area_km2'])
        u,v=records[i]['map_center'];p=xyz(np.array([u*360-180]),np.array([90-v*180]))[0]
        j=min((j for j in current if j!=i),key=lambda j:np.linalg.norm(xyz(np.array([records[j]['map_center'][0]*360-180]),np.array([90-records[j]['map_center'][1]*180]))[0]-p))
        merge(i,j)
lut=np.zeros(8192,np.uint16);lut[8191]=8191
for i in parent:lut[i]=root(i)
a=lut[a]
for tag,c in w['countries'].items():
    c['regions']=sorted(set(root(i) for i in c['regions']));c['capital']=root(c['capital'])
    c['map_center']=records[c['capital']]['map_center']
for s in records.values():
    s['area_km2']=round(s['area_km2'],2)
    if s['owner']=='USA' and s['name']=='Washington' and s['area_km2']<1000:s['name']='District of Columbia'
    if s['owner']=='JAP' and s['name'] in ['Saga Prefecture','Nagasaki Prefecture']:
        # Handled as geographically adjoining Kyushu regions by the standard
        # boundary union in a later named-region update, rather than distortion.
        pass
w['regions']={str(k):v for k,v in sorted(records.items())}
micro=json.load(open(ROOT/'data/microstate_geometry.json'));micro['state']=root(micro['state']);micro['host_state']=root(micro['host_state']);write('microstate_geometry',micro)
np.savez_compressed(SRC/'grouped_atlas_022r2.npz',regions=a);write('world',w)
r=json.load(open(ROOT/'data/geography_0206_report.json'));r['states']=len(records);r['island_and_enclave_consolidations']=len(states)-len(records)
for row in r['country_groups']:row['states']=len(w['countries'][row['country']]['regions'])
write('geography_0206_report',r)
print('COHERENT_STATES_COMPLETE',len(records),r['island_and_enclave_consolidations'],flush=True)
