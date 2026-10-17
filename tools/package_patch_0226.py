"""Build the reviewed .26 overlay from tracked changes and an explicit file list."""
from pathlib import Path
import hashlib,json,subprocess,zipfile,zlib
R=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=R).decode()
def main():
 assert json.loads((R/'validation_0226/runtime_results.json').read_text())['passed']
 assert json.loads((R/'validation_0226/geography_results.json').read_text())['passed']
 files=set(filter(None,git('diff','--name-only','--diff-filter=ACMRTUXB','-z','aeacb59').split('\0')))
 baseline=set(git('ls-tree','-r','--name-only','aeacb59').splitlines())
 manifest=json.loads((R/'ASSET_RESTORE.json').read_text());compressed_checks=0
 for item in manifest['files']:
  if all(p['path']in baseline for p in item['parts']):continue
  data=[]
  for part in item['parts']:
   path=R/part['path'];b=path.read_bytes();assert hashlib.sha256(b).hexdigest()==part['sha256'] and len(b)==part['bytes'];data.append(b)
   if part['path']not in baseline:files.add(part['path'])
  raw=zlib.decompress(b''.join(data));assert hashlib.sha256(raw).hexdigest()==item['sha256'] and len(raw)==item['bytes'];compressed_checks+=1
 extras=['data/state_plan_0226.json','data/population_weights_0226.json','data/geography_0226_report.json','documentation/state_audit_0226/STATE_CHANGES.md','documentation/state_audit_0226/COUNTRY_COUNTS.md','documentation/versions/README_main_0225.md','tests/geography_0226_tests.py','tests/states_0226_tests.gd','tools/review_states_0226.py','tools/apply_states_0226.py','tools/report_states_0226.py','tools/package_patch_0226.py','validation_0226/geography_results.json','validation_0226/runtime_results.json']
 files.update(extras)
 uid=R/'tests/states_0226_tests.gd.uid'
 if uid.exists():files.add(uid.relative_to(R).as_posix())
 removed=git('diff','--name-only','--diff-filter=D','aeacb59').splitlines()
 (R/'PATCH_REMOVED_FILES_0226.txt').write_text('# Obsolete generated parts only. Optional cleanup after applying .26.\n'+'\n'.join(removed)+'\n');files.add('PATCH_REMOVED_FILES_0226.txt')
 (R/'APPLY_0_2_0_26.txt').write_text('Bunny World 0.2.0.26 changed-files patch\nBase: working 0.2.0.25 / GitHub main aeacb59\n\n1. Close Godot and the game; keep a copy of .25.\n2. Extract all files into the project root beside project.godot and replace included files.\n3. Run Prepare_BunnyWorld.bat and wait for success (app/geography/display .26).\n4. Open in Godot 4.5.1 Standard and start a FRESH campaign, or export a new release EXE.\n\nRead documentation/state_audit_0226/STATE_CHANGES.md for full inventory, modeled population allocation and your short test.\nNo Windows executable included. Taiwan, Afghanistan and all exclusions remain unchanged.\n');files.add('APPLY_0_2_0_26.txt')
 entries=[{'path':n,'bytes':(R/n).stat().st_size,'sha256':hashlib.sha256((R/n).read_bytes()).hexdigest()}for n in sorted(files)]
 (R/'PATCH_MANIFEST_0226.json').write_text(json.dumps({'version':'0.2.0.26','baseline':'0.2.0.25','base_commit':'aeacb59','files':entries,'obsolete_parts':removed,'compressed_resource_roundtrips':compressed_checks},indent=2)+'\n');files.add('PATCH_MANIFEST_0226.json')
 target=R.parent/'BunnyWorld_0_2_0_26_patch.zip'
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for n in sorted(files):z.write(R/n,n)
 with zipfile.ZipFile(target)as z:assert z.testzip()is None
 print('PATCH_READY',str(target),target.stat().st_size,'bytes',len(files),'files',compressed_checks,'changed compressed resources roundtrip verified')
if __name__=='__main__':main()
