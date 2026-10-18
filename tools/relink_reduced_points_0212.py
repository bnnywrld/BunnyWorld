"""Relink from immutable accepted point records; never compound prior moves."""
from pathlib import Path
import json,math
import numpy as np
from scipy.ndimage import find_objects
R=Path(__file__).resolve().parents[1];D=R/'tools/cartography/reduced_0212'
def read(p):return json.loads(p.read_text())
def main():
 ps=read(R/'data/provinces.json');a=np.load(D/'final_provinces.npz')['provinces'];source=np.load(D/'source_provinces.npz')['provinces'];lut=np.zeros(65536,np.uint16);lut[65535]=65535
 for k,p in ps.items():lut[int(k)]=p['region']
 states=lut[a];boxes=find_objects(states,max_label=int(states[states!=65535].max()));moves=[]
 def point(c,sid,key):
  hx=int((c['longitude']+180)/360*16384)%16384;hy=min(8191,max(0,int((90-c['latitude'])/180*8192)));old=int(source[hy,hx])
  if old in [0,65535]or lut[old]!=sid:return
  x,y=hx//2,hy//2;pid=int(a[y,x])
  if lut[pid]!=sid:
   bb=boxes[sid-1];yy,xx=np.nonzero(states[bb]==sid);yy+=bb[0].start;xx+=bb[1].start
   dx=(xx-x+4096)%8192-4096;j=np.argmin((dx*math.cos(math.radians(c['latitude'])))**2+(yy-y)**2)
   ny,nx=int(yy[j]),int(xx[j]);pid=int(a[ny,nx]);before=[c['longitude'],c['latitude']]
   c['longitude']=(nx+.5)/8192*360-180;c['latitude']=90-(ny+.5)/4096*180
   moves.append({'name':c.get('name',c.get('id','')),'from':before,'to':[c['longitude'],c['latitude']]})
  c[key]=pid
 cities=read(D/'baseline/cities.json');scene=read(D/'baseline/urban_scenery.json');urban=read(R/'data/urban_population.json')
 for p in ps.values():p['cities']=[]
 for c in cities:point(c,c['state_id'],'province_id');ps[str(c['province_id'])]['cities'].append(c['name'])
 for kind in ['clusters','landmarks']:
  for c in scene[kind]:point(c,c['state'],'province')
 for g in urban['groups'].values():g['provinces']=[]
 for c in cities:
  if c.get('urban_group')in urban['groups']:urban['groups'][c['urban_group']]['provinces'].append(c['province_id'])
 for kind in ['clusters','landmarks']:
  for c in scene[kind]:
   if c.get('group')in urban['groups']:urban['groups'][c['group']]['provinces'].append(c['province'])
 for g in urban['groups'].values():g['provinces']=sorted(set(g['provinces']))
 for p in ps.values():p['cities']=sorted(set(p['cities']))
 scene['version']='0.2.1.2';audit=read(R/'data/map_reduction_audit.json');audit['point_moves']=moves
 for name,value in [('cities',cities),('provinces',ps),('urban_scenery',scene),('urban_population',urban),('map_reduction_audit',audit)]:
  (R/f'data/{name}.json').write_text(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n')
 print('CANONICAL_POINT_RELINK',len(moves),'small moves',flush=True)
if __name__=='__main__':main()
