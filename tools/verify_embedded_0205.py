"""Verify every embedded digest and raw runtime file against this source."""
from pathlib import Path
import hashlib,json,struct,sys
from build_windows import validate_embedded_launcher
ROOT=Path(__file__).resolve().parents[1];exe=Path(sys.argv[1]);result=validate_embedded_launcher(exe)
start=result['pack_offset'];matched=[];entries=[]
with exe.open('rb') as f:
 f.seek(start);header=f.read(40);base,directory=struct.unpack_from('<QQ',header,24)
 f.seek(start+directory);count=struct.unpack('<I',f.read(4))[0]
 for _ in range(count):
  n=struct.unpack('<I',f.read(4))[0];name=f.read(n).rstrip(b'\0').decode('utf-8');offset,length=struct.unpack('<QQ',f.read(16));digest=f.read(16);flags=struct.unpack('<I',f.read(4))[0]
  assert flags==0,('Unexpected packed file flags',name,flags)
  entries.append((name,start+base+offset,length,digest))
 for name,offset,length,digest in entries:
  f.seek(offset);h=hashlib.md5();left=length
  while left:
   chunk=f.read(min(left,4*1024*1024));assert chunk,('Truncated embedded file',name);h.update(chunk);left-=len(chunk)
  assert h.digest()==digest,('Embedded digest mismatch',name)
  local=ROOT/name
  if local.is_file() and (name.startswith('data/') or name.endswith(('.bwm','.bin','.gdshader','.gdshaderinc','.res'))):
   local_md5=hashlib.md5(local.read_bytes()).digest();assert local_md5==digest,('Source differs from executable',name);matched.append(name)
 for required in ['data/world.json','data/provinces.json','data/cities.json','data/urban_population.json','data/flags.json','assets/relief_data.bin','assets/materials/terrain_materials_high.bwm','scripts/planet.gdshader','scripts/waterways.gdshader']:
  assert required in matched,('Required source byte match missing',required)
h=hashlib.sha256()
with exe.open('rb') as f:
 for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
result.update(version='0.2.0.5',executable=exe.name,bytes=exe.stat().st_size,sha256=h.hexdigest(),all_embedded_file_md5_verified=len(entries),source_data_byte_matches=len(matched),source_data_matched_files=matched,native_windows_execution_tested=False)
destination=Path(sys.argv[2]);destination.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
