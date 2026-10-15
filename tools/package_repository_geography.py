"""Package current border meshes and a versioned, checksum-verified map bundle."""
from pathlib import Path
import hashlib,json,zlib
ROOT=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 manifest=json.load(open(ROOT/'ASSET_RESTORE.json'));world=json.load(open(ROOT/'data/world.json'));version=world['version'];manifest['version']=version
 for item in manifest['files']:
  if item['path'] not in ['assets/land_boundaries.res','assets/province_boundaries.res','assets/sea_boundaries.res']:continue
  data=(ROOT/item['path']).read_bytes();digest=sha(data);previous=item['sha256'];oldparts=item['parts'];compressed=zlib.compress(data,9);parts=[]
  for n,start in enumerate(range(0,len(compressed),2*1024*1024)):
   chunk=compressed[start:start+2*1024*1024];p=Path('repository_assets')/(digest+'.zlib.part%03d'%n);(ROOT/p).write_bytes(chunk);parts.append({'path':p.as_posix(),'bytes':len(chunk),'sha256':sha(chunk)})
  history=set(item.get('previous_sha256',[]))
  if previous!=digest:history.add(previous)
  item.update(bytes=len(data),sha256=digest,parts=parts,previous_sha256=sorted(history))
  for old in oldparts:
   p=ROOT/old['path']
   if p.exists() and old['path'] not in {x['path'] for x in parts}:p.unlink()
  print('PACKAGED',item['path'],len(compressed),len(parts),flush=True)
 (ROOT/'ASSET_RESTORE.json').write_text(json.dumps(manifest,indent=2)+'\n')
 files=['data/world.json','data/provinces.json','data/cities.json','data/microstate_geometry.json','data/urban_population.json','data/urban_scenery.json','data/sea_regions.json','assets/sea_ids.png','assets/province_index.png','assets/land_boundaries.res','assets/province_boundaries.res','assets/sea_boundaries.res']+['assets/region_ids_%d.png'%i for i in range(4)]
 bundle={'version':version,'scenario':world['scenario_id'],'states':len(world['regions']),'land_provinces':len(json.load(open(ROOT/'data/provinces.json'))),'files':{p:sha((ROOT/p).read_bytes()) for p in files}}
 (ROOT/'data/geography_bundle.json').write_text(json.dumps(bundle,indent=2)+'\n')
if __name__=='__main__':main()
