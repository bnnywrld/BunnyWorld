"""Extract subpixel geographic border paths into screen-width GPU ribbons.
The ID atlas remains lossless and discrete for simulation/picking. Polylines
are simplified by at most 0.65 source pixels (~1.6km at the equator), then
drawn with smooth coverage independent of map texel size and camera zoom.
"""
from pathlib import Path
import json,struct
from functools import lru_cache
import numpy as np
from PIL import Image
from scipy.ndimage import find_objects
from skimage.measure import find_contours
from shapely.geometry import LineString
ROOT=Path(__file__).resolve().parents[1];W,H=16384,8192
Image.MAX_IMAGE_PIXELS=None

@lru_cache(maxsize=1)
def province_membership():
 return {int(k):p['region']for k,p in json.loads((ROOT/'data/provinces.json').read_text()).items()}

def contours(atlas,ids,scale,water=False,province=False):
    hh,ww=atlas.shape;boxes=find_objects(atlas,max_label=max(ids));paths=[]
    for sid in ids:
        bb=boxes[sid-1]
        if bb is None:continue
        t=max(0,bb[0].start-1);b=min(hh,bb[0].stop+1);l=max(0,bb[1].start-1);r=min(ww,bb[1].stop+1)
        mask=np.pad(atlas[t:b,l:r]==sid,1)
        for contour in find_contours(mask,.5,fully_connected='high'):
            yy=contour[:,0]+t-1;xx=contour[:,1]+l-1
            # Classify each segment using samples across its normal. Sampling
            # diagonal vertex corners creates overlapping spurs on stairs.
            dx=np.diff(xx);dy=np.diff(yy);length=np.maximum(np.hypot(dx,dy),1e-12)
            mx=(xx[:-1]+xx[1:])*.5;my=(yy[:-1]+yy[1:])*.5
            nx=-dy/length*.65;ny=dx/length*.65
            def sample(x,y):
                return atlas[np.clip(np.floor(y+.5).astype(int),0,hh-1),np.floor(x+.5).astype(int)%ww]
            side0=sample(mx+nx,my+ny);side1=sample(mx-nx,my-ny)
            other=np.where(side0==sid,side1,side0)
            start=0
            for end in range(1,len(other)+1):
                if end<len(other) and other[end]==other[start]:continue
                neighbor=int(other[start])
                if neighbor!=sid and (neighbor==0 or sid<neighbor):
                    pts=np.column_stack([xx[start:end+1],yy[start:end+1]])
                    from display_shape_0215 import smooth,smooth_internal
                    member=province_membership()
                    internal=(province and neighbor>0 and member.get(sid)==member.get(neighbor))
                    simple=smooth_internal(pts)if internal else smooth(np.asarray(LineString(pts).simplify(.8,preserve_topology=False).coords))
                    if len(simple)>1:paths.append((simple[:,0]/ww,simple[:,1]/hh,sid,neighbor,1 if water else 0))
                start=end
        if sid%250==0:print('Boundary contours',sid,'paths',len(paths),flush=True)
    return paths

def mesh(paths,name):
    vs=[];ts=[];cs=[];uvs=[];indices=[];base=0
    for x,y,a,b,kind in paths:
        # Simplification is planar. Long latitude/longitude runs need extra
        # vertices before spherical projection; otherwise a ribbon becomes a
        # chord through the planet and no longer follows the categorical atlas.
        points=np.column_stack([x,y])+np.array([.5/W,.5/H])*(2 if kind==1 else 1);step=np.max(np.abs(np.diff(points,axis=0))*np.array([2048,1024]),axis=1)
        pieces=[]
        for j,n in enumerate(np.maximum(1,np.ceil(step).astype(int))):
            t=np.arange(n,dtype=float)/n
            pieces.append(points[j]+(points[j+1]-points[j])*t[:,None])
        dense=np.vstack([*pieces,points[-1:]]);x,y=dense[:,0],dense[:,1]
        lon=(x-.5)*np.pi*2;lat=(.5-y)*np.pi
        p=np.column_stack([np.cos(lat)*np.sin(lon),np.sin(lat),np.cos(lat)*np.cos(lon)])*1.000075
        direction=np.empty_like(p);direction[1:-1]=p[2:]-p[:-2];direction[0]=p[1]-p[0];direction[-1]=p[-1]-p[-2];direction/=np.maximum(1e-12,np.linalg.norm(direction,axis=1))[:,None]
        v=np.repeat(p,2,axis=0);tan=np.repeat(direction,2,axis=0);tan=np.column_stack([tan,np.ones(len(tan))]);colors=np.tile(np.array([a&255,a>>8,b&255,b>>8])/255,(len(v),1));uv=np.column_stack([np.tile([-1.,1.],len(p)),np.full(len(v),kind)])
        j=base+np.arange(len(p)-1)*2;idx=np.column_stack([j,j+1,j+2,j+1,j+3,j+2]).ravel();vs.append(v);ts.append(tan);cs.append(colors);uvs.append(uv);indices.append(idx);base+=len(v)
    arrays=[np.concatenate(vs).astype('<f4'),np.concatenate(ts).astype('<f4'),np.concatenate(cs).astype('<f4'),np.concatenate(uvs).astype('<f4'),np.concatenate(indices).astype('<i4')]
    path=ROOT/'tools/cartography'/f'{name}.bin'
    with path.open('wb') as f:
        f.write(struct.pack('<II',len(arrays[0]),len(arrays[-1])))
        for a in arrays:f.write(a.tobytes())
    return {'paths':len(paths),'vertices':len(arrays[0]),'triangles':len(arrays[-1])//3}

if __name__=='__main__':
    world=json.loads((ROOT/'data/world.json').read_text());a=np.load(ROOT/'tools/cartography/grouped_atlas_022r2.npz' if (ROOT/'tools/cartography/grouped_atlas_022r2.npz').exists() else ROOT/'tools/cartography/grouped_atlas_020.npz')['regions']
    land=contours(a,sorted(map(int,world['regions'])),1)+contours(a,[8191],1)
    micro_path=ROOT/'data/microstate_geometry.json'
    if micro_path.exists():
        micro=json.load(open(micro_path));sid=micro['state']
        land=[p for p in land if p[2]!=sid and p[3]!=sid]
        points=np.array(micro['polygon_uv']+[micro['polygon_uv'][0]])
        land.append((points[:,0],points[:,1],sid,micro['host_state'],0))
    report={'land':mesh(land,'land_boundaries_021')};del a,land
    rgb=np.asarray(Image.open(ROOT/'assets/sea_ids.png'),np.uint16);sea=rgb[:,:,0]+rgb[:,:,1]*256
    report['sea']=mesh(contours(sea,sorted(map(int,json.loads((ROOT/'data/sea_regions.json').read_text()))),2,True),'sea_boundaries_021');del sea,rgb
    atlas=np.load(ROOT/'tools/cartography/province_atlas_022r2.npz' if (ROOT/'tools/cartography/province_atlas_022r2.npz').exists() else ROOT/'tools/cartography/province_atlas_021.npz')['provinces'];ps=json.loads((ROOT/'data/provinces.json').read_text())
    paths=contours(atlas,sorted(map(int,ps)),1,province=True)
    # State and national edges are already drawn by the land layer.
    paths=[(x,y,a,b,2) for x,y,a,b,_ in paths if b>0 and ps[str(a)]['region']==ps[str(b)]['region']]
    report['province']=mesh(paths,'province_boundaries_021')
    (ROOT/'data/boundaries_021_report.json').write_text(json.dumps(report,indent=2));print('BOUNDARIES_021_COMPLETE',report,flush=True)
