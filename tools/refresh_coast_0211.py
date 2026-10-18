"""Update CPU/GPU terrain only around approved coastline edits."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects,distance_transform_edt,binary_dilation
R=Path(__file__).resolve().parents[1];D=R/'tools/cartography/edits_0211'
Image.MAX_IMAGE_PIXELS=None
def main():
    d=np.load(D/'sea_regions.npz');oldsea,sea=d['old'],d['edited']
    added=(oldsea>0)&(sea==0);removed=(oldsea==0)&(sea>0);changed=added|removed
    rgba=np.array(Image.open(R/'assets/relief_data.png'));original=rgba.copy()
    packed=rgba[:,:,0].astype(np.uint16)+rgba[:,:,1].astype(np.uint16)*256
    # Region samples and relief have the same 2:1 relationship.
    a=np.load(D/'final_provinces.npz')['provinces'];land=a[1::2,1::2]>0
    meters=np.load(R/'tools/cartography/etopo_021.npz')['meters']
    meta=json.loads((R/'data/relief.json').read_text())
    patches=0
    near=binary_dilation(changed,iterations=7)
    labs,n=label(near)
    for i,bb in enumerate(find_objects(labs),1):
        top=max(0,bb[0].start-8);bottom=min(4096,bb[0].stop+8)
        left=max(0,bb[1].start-8);right=min(8192,bb[1].stop+8);bb=np.s_[top:bottom,left:right]
        mask=land[bb];dist=distance_transform_edt(mask).astype(np.float32)
        t=np.clip((dist-.5)/4.,0,1);feather=t*t*(3-2*t)
        height=(meta['land_lift']+np.clip(meters[bb],0,9000)*meta['height_exaggeration']/6371000.)*feather
        values=np.rint(height/.016*65535).astype(np.uint16);values[~mask]=0
        active=near[bb];view=packed[bb];view[active]=values[active]
        alpha=rgba[bb][:,:,3];alpha[active]=np.rint(feather[active]*255).astype(np.uint8)
        patches+=1
    rgba[:,:,0]=packed&255;rgba[:,:,1]=packed>>8
    Image.fromarray(rgba).save(R/'assets/relief_data.png')
    (R/'assets/relief_data.bin').write_bytes(packed.astype('<u2').tobytes())
    # Newly exposed land inherits the closest accepted land surface. Existing
    # terrain/material pixels stay unchanged; water is clipped by coast data.
    for name in ['terrain_color','terrain_types']:
        p=R/f'assets/{name}.png';rgb=np.array(Image.open(p));seeds=added.copy()
        yy,xx=np.nonzero(added)
        for y,x in zip(yy,xx):
            t,b=max(0,y-16),min(4096,y+17);l,r=max(0,x-16),min(8192,x+17)
            valid=land[t:b,l:r]&~added[t:b,l:r]
            assert valid.any(),('New island surface has no neighbour',x,y)
            ys,xs=np.nonzero(valid);j=np.argmin((ys+t-y)**2+(xs+l-x)**2)
            rgb[y,x]=rgb[ys[j]+t,xs[j]+l]
        Image.fromarray(rgb).save(p)
    meta.update(coast_revision='0.2.1.1',coast_pixels_changed=int(changed.sum()),coast_land_added=int(added.sum()),coast_water_added=int(removed.sum()))
    (R/'data/relief.json').write_text(json.dumps(meta,indent=2)+'\n')
    # Keep point features on surviving land when the sea edit removes their
    # previous pixel. Move only newly submerged anchors, within the province
    # already selected by the state-priority fitting step.
    boxes=find_objects(a,max_label=65535);moves=[]
    for filename,kinds in [('cities.json',[None]),('urban_scenery.json',['clusters','landmarks'])]:
        path=R/'data'/filename;data=json.loads(path.read_text())
        for kind in kinds:
            for c in data if kind is None else data[kind]:
                x=int((c['longitude']+180)/360*16384)%16384;y=min(8191,int((90-c['latitude'])/180*8192))
                if not removed[y//2,x//2]or a[y,x]>0:continue
                pid=c['province_id']if kind is None else c['province'];bb=boxes[pid-1]
                yy,xx=np.nonzero(a[bb]==pid);yy+=bb[0].start;xx+=bb[1].start
                dx=(xx-x+8192)%16384-8192
                j=np.argmin((dx*np.cos(np.deg2rad(c['latitude'])))**2+(yy-y)**2)
                old=[c['longitude'],c['latitude']]
                c['longitude']=(int(xx[j])+.5)/16384*360-180;c['latitude']=90-(int(yy[j])+.5)/8192*180
                moves.append({'file':filename,'kind':kind,'name':c.get('name',c.get('city','cluster')),'from':old,'to':[c['longitude'],c['latitude']]})
        path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
    audit_path=R/'data/map_edit_audit_0211.json';audit=json.loads(audit_path.read_text())
    previous=audit.get('coastal_anchor_moves',[])
    audit['coastal_anchor_moves']=previous+moves;audit_path.write_text(json.dumps(audit,ensure_ascii=False,separators=(',',':'))+'\n')
    assert np.array_equal(rgba[~near],original[~near]);assert np.all(packed[removed]==0)
    print('COAST_TERRAIN_REFRESHED',patches,'windows',int(changed.sum()),'sea-grid changes',flush=True)
if __name__=='__main__':main()
