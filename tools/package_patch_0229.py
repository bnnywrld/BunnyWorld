"""Changed-files ZIP, with complete prepared resources and checksum checks."""
from pathlib import Path
import subprocess,json,hashlib,zipfile,io,zlib,shutil
R=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 info=json.loads((R/'BUILD_INFO.json').read_text());assert info['version']=='0.2.0.29'and info['validation']['runtime']['passed']
 names=set(subprocess.check_output(['git','diff','--name-only','--diff-filter=ACMRT','HEAD'],cwd=R,text=True).splitlines())
 names.update(['tools/apply_edits_0229.py','tools/build_sea_coverage.py','tools/capture_baseline_0229.gd','tools/inspect_edits_0229.py','tools/finalize_map_edits_0229.py','tools/package_patch_0229.py','tests/map_edits_0229_tests.py','tests/map_edits_0229_runtime.gd','documentation/MAP_EDITS_0229.md','data/map_edit_audit_0229.json','tools/cartography/province_boundaries_021.bin'])
 for dirname in ['tools/cartography/edits_0229','validation_0229']:
  names.update(p.relative_to(R).as_posix()for p in (R/dirname).rglob('*')if p.is_file()and p.name!='zip_results.json')
 # Omitted binary resources are restored from checked, versioned parts. They
 # must be fully reproducible before a patch can be delivered.
 restore=json.loads((R/'ASSET_RESTORE.json').read_text())
 tracked=set(subprocess.check_output(['git','ls-files'],cwd=R,text=True).splitlines())
 for item in restore['files']:
  stream=b''.join((R/p['path']).read_bytes()for p in item['parts']);raw=zlib.decompress(stream)
  assert len(raw)==item['bytes']and sha(raw)==item['sha256'],item['path']
  for part in item['parts']:
   rawpart=(R/part['path']).read_bytes();assert sha(rawpart)==part['sha256']and len(rawpart)==part['bytes']
   if part['path']not in tracked:names.add(part['path'])
 removed=subprocess.check_output(['git','diff','--name-only','--diff-filter=D','HEAD'],cwd=R,text=True).splitlines();(R/'PATCH_REMOVED_FILES_0229.txt').write_text('\n'.join(removed)+'\n');names.add('PATCH_REMOVED_FILES_0229.txt')
 manifest={'version':'0.2.0.29','base_version':'0.2.0.28','base_commit':info['repository_base_commit'],'files':[{'path':n,'bytes':(R/n).stat().st_size,'sha256':sha((R/n).read_bytes())}for n in sorted(names)],'removed_files':removed}
 (R/'PATCH_MANIFEST_0229.json').write_text(json.dumps(manifest,indent=2)+'\n');names.add('PATCH_MANIFEST_0229.json')
 target=R.parent/'BunnyWorld_0_2_0_29_patch.zip'
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,6)as z:
  for n in sorted(names):z.write(R/n,n)
 with zipfile.ZipFile(target)as z:
  assert z.testzip()is None
  for row in manifest['files']:assert sha(z.read(row['path']))==row['sha256']
 report={'passed':True,'files':len(names),'bytes':target.stat().st_size,'sha256':sha(target.read_bytes()),'base_version':'0.2.0.28','prepared_resources_verified':len(restore['files'])}
 (R/'validation_0229/zip_results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
