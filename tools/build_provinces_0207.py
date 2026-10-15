"""Use MD country land counts and smoothed MD-centre density, not MD shapes."""
from collections import Counter,defaultdict
import json
import numpy as np
from scipy.spatial import cKDTree
from build_geography_0206 import ROOT,SRC,W,H,xyz,alloc,write,build_provinces

def prepare():
 w=json.load(open(ROOT/'data/world.json'));ref=json.load(open(ROOT/'data/md_geography_reference.json'));a=np.load(SRC/'grouped_atlas_022r2.npz')['regions']
 province_country={p:s['owner'] for s in ref['states'].values() for p in s['province_ids']}
 states_by_tag={tag:[int(k) for k,s in w['regions'].items() if s['owner']==tag] for tag in w['countries']}
 trees={};ids={};points={}
 for tag,ss in states_by_tag.items():
  ids[tag]=ss;q=np.array([w['regions'][str(s)]['map_center'] for s in ss]);points[tag]=xyz(q[:,0]*360-180,90-q[:,1]*180);trees[tag]=cKDTree(points[tag])
 hints=Counter();centres=defaultdict(list)
 for pid,lon,lat in ref['density_centres']['points']:
  tag=province_country.get(pid)
  if tag not in trees:continue
  sid=int(a[min(H-1,int((90-lat)/180*H)),int((lon+180)/360*W)%W])
  if str(sid) not in w['regions'] or w['regions'][str(sid)]['owner']!=tag:
   sid=ids[tag][int(trees[tag].query(xyz(np.array([lon]),np.array([lat]))[0])[1])]
  hints[sid]+=1;centres[tag].append((lon,lat,sid))
 budgets={};rows=[]
 for tag,ss in states_by_tag.items():
  count=ref['countries'][tag]['land_provinces'];target=max(len(ss),count)
  # Sampling no longer needs to reproduce each original province location.
  # Counts by new State use MD centres with a small geographic-area prior,
  # avoiding a zero allocation where a centre moved across an ADM1 border.
  area=np.array([w['regions'][str(s)]['area_km2'] for s in ss]);prior=np.sqrt(area/area.sum())
  weights=np.array([hints[s] for s in ss],float)+prior*.25
  values=alloc(target-len(ss),weights)+1
  for sid,n in zip(ss,values):budgets[sid]=int(n)
  rows.append({'country':tag,'md_land_provinces':count,'target':target,'minimum_one_per_state':len(ss),'density_centres':len(centres[tag])})
 write('province_budget_0207',{'md_land_target':ref['counts']['land'],'planned_land_provinces':sum(budgets.values()),'method':'MD land totals by country; registered MD centre counts distributed to geographic States, with a small area prior. Settlement/terrain/river guidance places independent boundaries within each State. Sea and lake entries excluded.','countries':rows,'state_budgets':{str(k):v for k,v in budgets.items()}})
 print('PROVINCE_BUDGET',sum(budgets.values()),'MD',ref['counts']['land'],flush=True)
 return budgets

if __name__=='__main__':build_provinces(budgets=prepare())
