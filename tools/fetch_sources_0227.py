"""Fetch primary year-2000 inputs once; retain provenance/checksums."""
from pathlib import Path
import concurrent.futures,urllib.request,json,time,hashlib,zipfile
R=Path(__file__).resolve().parents[1];D=R/'tools/sources_0227';D.mkdir(exist_ok=True)
GRID='https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_POP_GLOBE_R2023A/GHS_POP_E2000_GLOBE_R2023A_4326_30ss/V1-0/GHS_POP_E2000_GLOBE_R2023A_4326_30ss_V1_0.zip'
def fetch(url,path):
 if path.exists():return path
 for attempt in range(3):
  try:
   temp=path.with_suffix(path.suffix+'.partial');total=0
   with urllib.request.urlopen(url,timeout=90)as f,open(temp,'wb')as out:
    while True:
     b=f.read(4*1024*1024)
     if not b:break
     out.write(b);total+=len(b)
     if total%(64*1024*1024)==0:print('FETCH_PROGRESS',path.name,total,flush=True)
   temp.replace(path);return path
  except Exception as e:
   print('FETCH_RETRY',path.name,str(e),flush=True)
   if attempt==2:raise
 return path

def grid():
 p=fetch(GRID,D/'ghsl_population_2000.zip')
 with zipfile.ZipFile(p)as z:
  name=next(n for n in z.namelist()if n.endswith('.tif'));target=D/Path(name).name
  if not target.exists():
   with z.open(name)as f,open(target,'wb')as out:
    import shutil;shutil.copyfileobj(f,out)
 meta={'url':GRID,'dataset':'EC JRC GHS-POP R2023A, year 2000, WGS84 30 arc-seconds','doi':'10.2905/2FF68A52-5B5B-4A22-8F40-C41DA8332CFE','archive_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'raster':str(target.relative_to(R))}
 (D/'grid_source.json').write_text(json.dumps(meta,indent=2)+'\n');print('GRID_READY',target,flush=True)
def wdi(code):
 url=f'https://api.worldbank.org/v2/country/all/indicator/{code}?date=2000&format=json&per_page=20000';p=fetch(url,D/(code+'.json'));d=json.loads(p.read_text());assert len(d)==2 and isinstance(d[1],list)
 print('WDI_READY',code,len(d[1]),flush=True)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
  tasks=[pool.submit(grid)]+[pool.submit(wdi,c)for c in ['SP.POP.TOTL']]
  for f in concurrent.futures.as_completed(tasks):f.result()
