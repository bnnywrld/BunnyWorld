"""Aggregate original GHSL 2000 raster against current canonical province IDs.
Never reuses historical province-number caches. Small shoreline mismatches snap
within 8 km to existing coastal land; no map geometry changes.
"""
from pathlib import Path
import hashlib,json,math
import numpy as np,rasterio
from rasterio.windows import Window
from scipy.spatial import cKDTree
R=Path(__file__).resolve().parents[1];D=R/'tools/sources_0227'
def unit(lon,lat):
 a,b=np.deg2rad(lon),np.deg2rad(lat);return np.column_stack([np.cos(b)*np.sin(a),np.sin(b),np.cos(b)*np.cos(a)])
def main():
 meta=json.loads((D/'grid_source.json').read_text());a=np.load(R/'tools/cartography/map_provinces.npz')['provinces'];H,W=a.shape
 land=(a>0)&(a<65535);edge=land&(~np.roll(land,1,0)|~np.roll(land,-1,0)|~np.roll(land,1,1)|~np.roll(land,-1,1));cy,cx=np.nonzero(edge);tree=cKDTree(unit((cx+.5)/W*360-180,90-(cy+.5)/H*180));del edge,land
 total=np.zeros(65536);dense=np.zeros(65536);snapped=np.zeros(65536);lost=0.
 with rasterio.open(R/meta['raster'])as src:
  lon=src.transform.c+(np.arange(src.width)+.5)*src.transform.a;cols=np.clip(((lon+180)/360*W).astype(int),0,W-1)
  for top in range(0,src.height,96):
   hh=min(96,src.height-top);lat=src.transform.f+(np.arange(top,top+hh)+.5)*src.transform.e;rows=np.clip(((90-lat)/180*H).astype(int),0,H-1)
   b=np.maximum(0,np.nan_to_num(src.read(1,window=Window(0,top,src.width,hh)),nan=0,posinf=0,neginf=0));iy,ix=np.nonzero(b>0)
   if not len(ix):continue
   value=b[iy,ix];pid=a[rows[iy],cols[ix]].copy();missing=(pid==0)|(pid==65535)
   if missing.any():
    dist,j=tree.query(unit(lon[ix[missing]],lat[iy[missing]]),workers=2);good=dist*6371.0088<=8.;at=np.flatnonzero(missing);ids=a[cy[j[good]],cx[j[good]]];pid[at[good]]=ids
    snapped+=np.bincount(ids,weights=value[at[good]],minlength=65536);lost+=float(value[at[~good]].sum())
   valid=(pid>0)&(pid<65535);pid=pid[valid];value=value[valid];yy=iy[valid]
   area=(111.195*abs(src.transform.e))*(111.195*src.transform.a)*np.cos(np.deg2rad(lat[yy]));total+=np.bincount(pid,weights=value,minlength=65536);dense+=np.bincount(pid,weights=np.where(value/np.maximum(area,.0001)>=1000,value,0),minlength=65536)
   if top%1920==0:print('POPULATION_AGGREGATE',top,src.height,float(total.sum()),flush=True)
 ps=json.loads((R/'data/provinces.json').read_text());out={'epoch':2000,'source':meta,'registration':{'atlas_sha256':hashlib.sha256((R/'tools/cartography/map_provinces.npz').read_bytes()).hexdigest(),'province_tiles_sha256':{f'assets/region_ids_{i}.png':hashlib.sha256((R/f'assets/region_ids_{i}.png').read_bytes()).hexdigest()for i in range(4)},'rule':'Original source raster cell centres into current canonical province IDs; coastal source pixels within 8km snapped to nearest existing coastal land.'},'unmapped_source_population':lost,'mapped_population':float(total.sum()),'shoreline_snapped_population':float(snapped.sum()),'provinces':{k:{'population':round(float(total[int(k)]),6),'dense_population':round(float(dense[int(k)]),6),'shoreline_snapped':round(float(snapped[int(k)]),6)}for k in ps}}
 (R/'data/population_grid_0227.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print('CURRENT_GRID_READY',out['mapped_population'],'lost',lost,'snapped',out['shoreline_snapped_population'],flush=True)
if __name__=='__main__':main()
