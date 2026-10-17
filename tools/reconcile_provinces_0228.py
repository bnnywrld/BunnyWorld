"""Native-grid component reconciliation; no per-area masks or ownership edits.

Optional/idempotent after generation. Uses the same repair as the generator.
Always run the shared map build after changing any canonical identity pixels.
"""
import json
import numpy as np
from PIL import Image
from scipy.ndimage import find_objects
from generate_provinces_0228 import R,C,W,H,AREA,state_crop,native_repair
def main():
    w=json.loads((R/'data/world.json').read_text());ps=json.loads((R/'data/provinces.json').read_text());s=np.load(C/'states_0228.npz')['regions'];a=np.load(C/'province_atlas_0228.npz')['provinces'];boxes=find_objects(s,max_label=8191);changed=0
    for sid,state in w['regions'].items():
        t,l,mask=state_crop(s,boxes[int(sid)-1],int(sid));cols=(np.arange(mask.shape[1])+l)%W
        view=a[t:t+mask.shape[0],cols];codes=np.where(mask,view,0).astype(np.int32)
        fixed,n=native_repair(codes,mask,{});changed+=n
        if n:
            yy,xx=np.nonzero(mask);a[yy+t,cols[xx]]=fixed[yy,xx]
            for pid in state['provinces']:
                py,px=np.nonzero(fixed==pid);assert len(px),('Province removed',pid);ps[str(pid)]['area_km2']=round(float(AREA[py+t].sum()),3)
                # Keep an existing interior focus if its identity is stable.
                u,v=ps[str(pid)]['map_center']
                if int(a[min(H-1,int(v*H)),int(u*W)%W])!=pid:
                    j=len(px)//2;ps[str(pid)]['map_center']=[(int(cols[px[j]])+.5)/W,(int(py[j])+t+.5)/H]
    if changed:
        np.savez_compressed(C/'province_atlas_0228.npz',provinces=a)
        for i in range(4):
            q=a[i//2*4096:(i//2+1)*4096,i%2*8192:(i%2+1)*8192];path=R/'assets'/f'region_ids_{i}.png';temp=path.with_suffix('.prepare-tmp')
            Image.fromarray(np.stack([(q&255).astype(np.uint8),(q>>8).astype(np.uint8),np.zeros_like(q,np.uint8)],-1)).save(temp,format='PNG');Image.open(temp).verify();temp.replace(path)
        (R/'data/provinces.json').write_text(json.dumps(ps,ensure_ascii=False,separators=(',',':'))+'\n')
    (R/'data/province_reconciliation_0228.json').write_text(json.dumps({'reassigned_pixels':changed,'ownership_or_state_pixels_changed':0,'province_ids_removed':0},indent=2)+'\n')
    print('NATIVE_PROVINCE_RECONCILIATION',changed,'pixels; state footprints and province counts preserved',flush=True)
if __name__=='__main__':main()
