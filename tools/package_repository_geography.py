"""Package current border meshes and a versioned, checksum-verified map bundle."""
from pathlib import Path
import hashlib,json,zlib
ROOT=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 manifest=json.load(open(ROOT/'ASSET_RESTORE.json'));world=json.load(open(ROOT/'data/world.json'));version=world['version'];manifest['version']=version
 existing={item['path']for item in manifest['files']}
 for path in sorted((ROOT/'assets/rendering').glob('*_chunks.res')):
  name=path.relative_to(ROOT).as_posix()
  if name not in existing:manifest['files'].append({'path':name,'sha256':'','bytes':0,'parts':[]})
 for item in manifest['files']:
  if item['path'] not in ['assets/land_boundaries.res','assets/province_boundaries.res','assets/sea_boundaries.res','assets/display/selection_distance_0217.bwd'] and not item['path'].startswith('assets/rendering/'):continue
  data=(ROOT/item['path']).read_bytes();digest=sha(data);previous=item['sha256'];oldparts=item['parts'];compressed=zlib.compress(data,9);parts=[]
  chunk_size=8*1024*1024 if item['path'].endswith('.bwd')else 2*1024*1024
  for n,start in enumerate(range(0,len(compressed),chunk_size)):
   chunk=compressed[start:start+chunk_size];p=Path('repository_assets')/(digest+'.zlib.part%03d'%n);(ROOT/p).write_bytes(chunk);parts.append({'path':p.as_posix(),'bytes':len(chunk),'sha256':sha(chunk)})
  history=set(item.get('previous_sha256',[]))
  if previous and previous!=digest:history.add(previous)
  item.update(bytes=len(data),sha256=digest,parts=parts,previous_sha256=sorted(history))
  for old in oldparts:
   p=ROOT/old['path']
   if p.exists() and old['path'] not in {x['path'] for x in parts}:p.unlink()
  print('PACKAGED',item['path'],len(compressed),len(parts),flush=True)
 (ROOT/'ASSET_RESTORE.json').write_text(json.dumps(manifest,indent=2)+'\n')
 from repository_hygiene import check as check_repository
 check_repository(prune=True)
 files=['data/world.json','data/provinces.json','data/cities.json','data/microstate_geometry.json','data/urban_population.json','data/urban_scenery.json','data/sea_regions.json','assets/sea_ids.png','assets/province_index.png','assets/land_boundaries.res','assets/province_boundaries.res','assets/sea_boundaries.res']+['assets/region_ids_%d.png'%i for i in range(4)]
 files += [p for p in ['data/demographics.json','data/state_demographics.json']if (ROOT/p).is_file()]
 bundle={'version':version,'scenario':world['scenario_id'],'states':len(world['regions']),'land_provinces':len(json.load(open(ROOT/'data/provinces.json'))),'files':{p:sha((ROOT/p).read_bytes()) for p in files}}
 (ROOT/'data/geography_bundle.json').write_text(json.dumps(bundle,indent=2)+'\n')
if __name__=='__main__':main()
