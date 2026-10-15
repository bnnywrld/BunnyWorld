"""Aggregate GHSL's 2000 resident grid onto the accepted game provinces.

Build-time only: never ship or open the global raster in the game.
Pixel-centre assignment is approximate at coasts; state totals are reconciled
later to the supplied scenario. Every city province includes its countryside.
"""
from pathlib import Path
import argparse, hashlib, json, math
import numpy as np
import rasterio
from rasterio.windows import Window
from micro_geometry import MicroGeometry

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('raster', type=Path)
args = parser.parse_args()
atlas_path=ROOT/'tools/cartography/province_atlas_022r2.npz'
atlas = np.load(atlas_path if atlas_path.exists() else ROOT/'tools/cartography/province_atlas_021.npz')['provinces']
micro=MicroGeometry(ROOT) if (ROOT/'data/microstate_geometry.json').exists() else None
H, W = atlas.shape
N = 65536
totals = np.zeros(N)
dense = np.zeros(N)
xyz = np.zeros((N, 3))
with rasterio.open(args.raster) as src:
    step_x, step_y = src.transform.a, abs(src.transform.e)
    lon = src.transform.c + (np.arange(src.width)+.5)*step_x
    cols = np.clip(((lon+180)/360*W).astype(int),0,W-1)
    lon_r = np.deg2rad(lon)
    for top in range(0, src.height, 96):
        height = min(96,src.height-top)
        lat = src.transform.f + (np.arange(top,top+height)+.5)*src.transform.e
        rows = np.clip(((90-lat)/180*H).astype(int),0,H-1)
        ids = atlas[rows[:,None],cols[None,:]]
        if micro:
            ids[ids==micro.data['province']]=micro.data['host_province']
            left,top_uv,right,bottom=micro.bounds
            columns=np.flatnonzero(((lon+180)/360>=left)&((lon+180)/360<=right))
            for row_index in np.flatnonzero(((90-lat)/180>=top_uv)&((90-lat)/180<=bottom)):
                for col_index in columns:
                    ids[row_index,col_index]=micro.resolve(lon[col_index],lat[row_index],int(ids[row_index,col_index]))
        data = src.read(1,window=Window(0,top,src.width,height))
        data = np.maximum(0,np.nan_to_num(data,nan=0,posinf=0,neginf=0))
        valid = (ids>0)&(ids<65535)
        data *= valid
        totals += np.bincount(ids.ravel(),weights=data.ravel(),minlength=N)
        cell_area = (111.195*step_y)*(111.195*step_x)*np.cos(np.deg2rad(lat))[:,None]
        urban = np.where(data/np.maximum(cell_area,.0001)>=1000, data,0)
        dense += np.bincount(ids.ravel(),weights=urban.ravel(),minlength=N)
        coslat = np.cos(np.deg2rad(lat))[:,None]
        for axis, factor in enumerate([coslat*np.sin(lon_r)[None,:],np.broadcast_to(np.sin(np.deg2rad(lat))[:,None],data.shape),coslat*np.cos(lon_r)[None,:]]):
            xyz[:,axis] += np.bincount(ids.ravel(),weights=(urban*factor).ravel(),minlength=N)
        if top%960==0: print('POPULATION_GRID',top,src.height,flush=True)
xyz /= np.maximum(dense[:,None],1)
output=ROOT/'tools/cartography/population_022.npz'
np.savez_compressed(output,total=totals,dense=dense,xyz=xyz)
metadata={
    'epoch':2000,'source':'European Commission JRC GHS-POP R2023A, year 2000, WGS84 30 arc-seconds',
    'doi':'10.2905/2FF68A52-5B5B-4A22-8F40-C41DA8332CFE',
    'url':'https://human-settlement.emergency.copernicus.eu/ghs_pop2023.php',
    'download_url':'https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_POP_GLOBE_R2023A/GHS_POP_E2000_GLOBE_R2023A_4326_30ss/V1-0/GHS_POP_E2000_GLOBE_R2023A_4326_30ss_V1_0.zip',
    'raster_sha256':hashlib.sha256(args.raster.read_bytes()).hexdigest(),
    'prepared_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
    'dense_settlement_threshold_people_km2':1000,
    'method':'Sum resident grid cells by game province at cell centres. Scale all province shares within each state to the existing scenario total; retain the non-city shares in a single state pool.',
    'accuracy':'Modelled year-2000 estimates, not municipal census counts. Game provinces include surrounding countryside and do not reproduce census or district boundaries.'
}
(ROOT/'tools/cartography/population_022_source.json').write_text(json.dumps(metadata,indent=2))
print('POPULATION_PREPARED',output,totals[1:65535].sum(),flush=True)
