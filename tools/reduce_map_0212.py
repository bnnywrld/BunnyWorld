"""Lossless-ID 2:1 reduction with bounded small-state enlargement.

This changes display geometry, never residents, demographics or physical areas.
The accepted 0.2.1.1 source atlas and records are retained for reproducibility.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,copy,math
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt,find_objects,label
from apply_edits_0229 import repair,save_png
R=Path(__file__).resolve().parents[1];D=R/'tools/cartography/reduced_0212';W,H=8192,4096
Image.MAX_IMAGE_PIXELS=None
def read(n):return json.loads((R/n).read_text())
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n')
def main():
 w,ps=read('data/world.json'),read('data/provinces.json');assert w['version']=='0.2.1.1'
 a=np.load(D/'source_provinces.npz')['provinces'];assert a.shape==(8192,16384)
 source_centers={int(k):p['map_center']for k,p in ps.items()}
 candidates=[a[1::2,1::2],a[::2,::2],a[::2,1::2],a[1::2,::2]]
 b=candidates[0].copy();best=np.zeros(b.shape,np.uint8)
 for v in candidates:
  n=sum((v==x).astype(np.uint8)for x in candidates);m=n>best;b[m]=v[m];best[m]=n[m]
 original=b.copy();old_land=a[1::2,1::2]>0
 lut=np.zeros(65536,np.uint16);lut[65535]=65535
 for k,p in ps.items():lut[int(k)]=p['region']
 counts=np.bincount(b.ravel(),minlength=65536);statecounts=np.bincount(lut[b].ravel(),minlength=65536)
 missing=sorted(set(map(int,ps))-set(map(int,np.unique(b))));enlarged=[]
 # Pin one naturally surviving pixel per ID. Enlargement and repair may not
 # erase a neighbouring province, including another tiny enclave.
 locks=np.zeros(b.shape,np.uint16)
 boxes=find_objects(b,max_label=65535)
 for k,p in ps.items():
  pid=int(k);bb=boxes[pid-1]
  if bb is None:continue
  cx,cy=source_centers[pid];x=int(cx*W)%W;y=min(H-1,int(cy*H))
  if b[y,x]!=pid:
   yy,xx=np.nonzero(b[bb]==pid);j=np.argmin(((xx+bb[1].start-x)*math.cos((.5-cy)*math.pi))**2+(yy+bb[0].start-y)**2)
   x=int(xx[j]+bb[1].start);y=int(yy[j]+bb[0].start)
  locks[y,x]=pid
 for sid,s in w['regions'].items():
  sid=int(sid)
  if statecounts[sid]>=4:continue
  pid=int(s['capital_province']);uv=s.get('capital_uv',s['map_center']);cx,cy=int(uv[0]*W)%W,min(H-1,int(uv[1]*H))
  painted=[]
  # Prefer an existing state pixel nearest the original capital.
  yy,xx=np.nonzero(lut[b]==sid)
  if len(yy):
   j=np.argmin((xx-cx)**2+(yy-cy)**2);cy,cx=int(yy[j]),int(xx[j]);pid=int(b[cy,cx])
  # A 3×3 footprint at this resolution is deliberately exaggerated for
  # small territories, as authorised. Protected foreign anchors are skipped.
  for dy in [-1,0,1]:
   for dx in [-1,0,1]:
    y=min(H-1,max(0,cy+dy));x=(cx+dx)%W;old=int(b[y,x])
    if locks[y,x]and lut[int(locks[y,x])]!=sid:continue
    if old not in [0,65535]and old!=pid and counts[old]<=1:continue
    if old!=pid:
     counts[old]-=1;counts[pid]+=1;b[y,x]=pid;painted.append([x,y])
  locks[cy,cx]=pid
  enlarged.append({'state':sid,'name':s['name'],'before_pixels':int(statecounts[sid]),'province':pid,'painted_pixels':painted})
 # Restore any remaining province that lost the 2×2 vote. The closest free
 # cell in its own state is preferred over extending an unrelated border.
 restored=[]
 for pid in missing:
  if np.any(b==pid):continue
  sid=ps[str(pid)]['region'];uv=source_centers[pid];cx,cy=int(uv[0]*W)%W,min(H-1,int(uv[1]*H));options=[]
  for radius in [2,4,8,16]:
   for dy in range(-radius,radius+1):
    for dx in range(-radius,radius+1):
     y=min(H-1,max(0,cy+dy));x=(cx+dx)%W;other=int(b[y,x])
     if locks[y,x]or(other not in [0,65535]and counts[other]<=1):continue
     penalty=0 if lut[other]==sid else 1000
     options.append((penalty+dx*dx+dy*dy,y,x))
   if options:break
  assert options,('Cannot retain province',pid)
  _,y,x=min(options);other=int(b[y,x]);counts[other]-=1;counts[pid]+=1;b[y,x]=pid;locks[y,x]=pid
  restored.append({'province':pid,'state':sid,'pixel':[x,y],'replaced':other})
 # Retain inhabited islands and valid settlement/landmark locations even if
 # their ID also occurs on a larger island elsewhere. Do not turn older,
 # already-unmapped settlement coordinates into unrelated geography fixes.
 protected_points=[];unmapped_points=[]
 original_cities=json.loads((D/'baseline/cities.json').read_text());original_scene=json.loads((D/'baseline/urban_scenery.json').read_text())
 points=[(c,c['state_id'])for c in original_cities]
 points += [(c,c['state'])for kind in ['clusters','landmarks']for c in original_scene[kind]]
 points += [({'name':s['state_capital'],'longitude':s['capital_uv'][0]*360-180,'latitude':90-s['capital_uv'][1]*180},int(k))for k,s in w['regions'].items()if s.get('capital_uv')]
 for c,sid in points:
  hx=int((c['longitude']+180)/360*16384)%16384;hy=min(8191,max(0,int((90-c['latitude'])/180*8192)));pid=int(a[hy,hx])
  if pid in [0,65535]or lut[pid]!=sid:
   unmapped_points.append(c.get('name',''));continue
  cx,cy=hx//2,hy//2
  if lut[b[cy,cx]]==sid:continue
  options=[]
  for dy in [-1,0,1]:
   for dx in [-1,0,1]:
    y=min(H-1,max(0,cy+dy));x=(cx+dx)%W;other=int(b[y,x])
    if locks[y,x]and lut[int(locks[y,x])]!=sid:continue
    if other not in [0,65535,pid]and counts[other]<=1:continue
    options.append((dx*dx+dy*dy,y,x))
  assert options,('Protected point has no footprint',c.get('name'))
  _,y,x=min(options);other=int(b[y,x]);counts[other]-=1;counts[pid]+=1;b[y,x]=pid;locks[y,x]=pid
  protected_points.append({'name':c.get('name',''),'state':sid,'province':pid,'pixel':[x,y]})
 states=lut[b];boxes=find_objects(states,max_label=max(map(int,w['regions'])));repairs=[]
 # Preserve original islands as separate land components, but absorb accidental
 # disconnected fitting fragments on a single continuous state landmass.
 for key,s in w['regions'].items():
  sid=int(key);bb=boxes[sid-1];mask=states[bb]==sid;cell=b[bb].copy();islands,_=label(mask);bad=False
  for pid in np.unique(cell[mask]):
   components,n=label(cell==pid);seen=set()
   for j in range(1,n+1):
    members=set(map(int,np.unique(islands[components==j])))-{0}
    if seen&members:bad=True;break
    seen|=members
   if bad:break
  if bad:
   cell,changed=repair(cell,mask,locks[bb],np.ones_like(mask));b[bb][mask]=cell[mask]
   repairs.append({'state':sid,'pixels':changed})
 assert set(map(int,np.unique(b)))-{0,65535}==set(map(int,ps))
 assert np.array_equal(lut[b],states)
 # Anchors are interior cells in the exact same PNG used by GPU and picking.
 boxes=find_objects(b,max_label=65535)
 for k,p in ps.items():
  pid=int(k);bb=boxes[pid-1];mask=b[bb]==pid;dist=distance_transform_edt(mask)
  y,x=np.unravel_index(dist.argmax(),mask.shape);p['map_center']=[(x+bb[1].start+.5)/W,(y+bb[0].start+.5)/H]
  p['geometry_source']='0.2.1.1 accepted IDs reduced by 2×2 vote; protected tiny territories and province identity'
 for sid,s in w['regions'].items():
  pid=int(s['capital_province']);s['map_center']=ps[str(pid)]['map_center']
 for c in w['countries'].values():c['map_center']=w['regions'][str(c['capital'])]['map_center']
 # Keep point coordinates wherever the reduced map still contains their state;
 # otherwise relink to the nearest retained cell in that same state.
 stateboxes=find_objects(states,max_label=max(map(int,w['regions'])));moves=[]
 def point(c,sid,pidkey):
  x=int((c['longitude']+180)/360*W)%W;y=min(H-1,max(0,int((90-c['latitude'])/180*H)))
  hx=int((c['longitude']+180)/360*16384)%16384;hy=min(8191,max(0,int((90-c['latitude'])/180*8192)));source_pid=int(a[hy,hx])
  if source_pid in [0,65535]or lut[source_pid]!=sid:return
  if int(lut[b[y,x]])==sid:pid=int(b[y,x])
  else:
   bb=stateboxes[sid-1];yy,xx=np.nonzero(states[bb]==sid);yy+=bb[0].start;xx+=bb[1].start
   dx=(xx-x+W//2)%W-W//2;j=np.argmin((dx*math.cos(math.radians(c['latitude'])))**2+(yy-y)**2)
   ny,nx=int(yy[j]),int(xx[j]);pid=int(b[ny,nx])
   before=[c['longitude'],c['latitude']];c['longitude']=(nx+.5)/W*360-180;c['latitude']=90-(ny+.5)/H*180
   moves.append({'name':c.get('name',c.get('id','')),'from':before,'to':[c['longitude'],c['latitude']]})
  c[pidkey]=pid
 cities=read('data/cities.json');scene=read('data/urban_scenery.json');urban=read('data/urban_population.json')
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
 # Coast-only sea reconciliation: never fill inland lakes with ocean IDs.
 rgb=np.asarray(Image.open(D/'source_sea.png'),np.uint16);sea=rgb[:,:,0]+rgb[:,:,1]*256;oldsea=sea.copy();land=b>0
 sea[land]=0;water=~land;components,n=label(water)
 ocean=np.unique(components[sea>0]);fill=(sea==0)&water&np.isin(components,ocean)
 # Only newly exposed coast cells are candidates, not old enclosed lake zeros.
 fill &= old_land
 if fill.any():
  _,near=distance_transform_edt(sea==0,return_indices=True);sea[fill]=sea[tuple(near[:,fill])]
 assert set(map(int,np.unique(sea)))-{0}==set(map(int,read('data/sea_regions.json')))
 np.savez_compressed(D/'final_provinces.npz',provinces=b);np.savez_compressed(D/'final_states.npz',states=states)
 np.savez_compressed(D/'coast_changes.npz',added=land&~old_land,removed=~land&old_land)
 rgb=np.zeros((*b.shape,3),np.uint8);rgb[:,:,0]=b&255;rgb[:,:,1]=b>>8;save_png(R/'assets/province_ids.png',rgb)
 rgb=np.zeros((*sea.shape,3),np.uint8);rgb[:,:,0]=sea&255;rgb[:,:,1]=sea>>8;save_png(R/'assets/sea_ids.png',rgb)
 w.update(version='0.2.1.2',scenario_id='bunny_world_2000_0_2_1_2');w['map'].update(width=W,height=H,tile_width=W,tile_height=H,tiles=1,province_ids='assets/province_ids.png')
 scene['version']='0.2.1.2'
 for name,v in [('world',w),('provinces',ps),('cities',cities),('urban_scenery',scene),('urban_population',urban)]:write('data/'+name+'.json',v)
 audit={'version':'0.2.1.2','source_version':'0.2.1.1','source_size':[16384,8192],'size':[W,H],'initial_missing_provinces':missing,'restored':restored,'enlarged_states':enlarged,'protected_points':protected_points,'preexisting_unmapped_points':sorted(set(unmapped_points)),'fragment_repairs':repairs,'point_moves':moves,'pixels_different_from_majority':int((b!=original).sum()),'coast_pixels_changed':int((land!=old_land).sum()),'sea_pixels_reconciled':int((sea!=oldsea).sum()),'province_count':len(ps),'state_count':len(w['regions']),'population_unchanged':True,'physical_area_unchanged':True}
 write('data/map_reduction_audit.json',audit)
 from relink_reduced_points_0212 import main as relink_points
 relink_points()
 for name in ['project.godot','export_presets.cfg']:
  p=R/name;p.write_text(p.read_text().replace('0.2.1.1','0.2.1.2'))
 p=R/'scripts/world_state.gd';p.write_text(p.read_text().replace('const SAVE_VERSION := 19','const SAVE_VERSION := 20'))
 for i in range(4):
  for suffix in ['.png','.png.import']:(R/f'assets/region_ids_{i}{suffix}').unlink(missing_ok=True)
 print('REDUCED',json.dumps({k:v for k,v in audit.items()if k not in ['point_moves','fragment_repairs']}),flush=True)
if __name__=='__main__':main()
