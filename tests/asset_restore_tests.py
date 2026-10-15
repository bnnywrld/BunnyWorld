"""Regression checks for updates from known prepared resources and mixed bundles."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,zlib
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
with tempfile.TemporaryDirectory() as folder:
 root=Path(folder);(root/'tools').mkdir();(root/'assets').mkdir();(root/'data').mkdir();(root/'repository_assets').mkdir()
 script=root/'tools/restore_repository_assets.py';script.write_bytes((ROOT/'tools/restore_repository_assets.py').read_bytes())
 old=b'old verified borders';new=b'new verified borders';part=zlib.compress(new);target=root/'assets/borders.res';target.write_bytes(old);(root/'repository_assets/part').write_bytes(part)
 manifest={'version':'test','files':[{'path':'assets/borders.res','bytes':len(new),'sha256':sha(new),'previous_sha256':[sha(old)],'parts':[{'path':'repository_assets/part','bytes':len(part),'sha256':sha(part)}]}]}
 (root/'ASSET_RESTORE.json').write_text(json.dumps(manifest))
 (root/'project.godot').write_text('config/version="test"\n')
 def run(*args):return subprocess.run([sys.executable,str(script),*args],capture_output=True,text=True)
 assert run().returncode==0 and target.read_bytes()==new
 assert run('--verify-only').returncode==0
 target.write_bytes(b'custom work');assert run().returncode!=0 and target.read_bytes()==b'custom work'
 assert run('--force').returncode==0 and target.read_bytes()==new
 (root/'data/geography_bundle.json').write_text(json.dumps({'version':'test','files':{'assets/borders.res':sha(old)}}))
 assert run().returncode!=0
 print('ASSET_RESTORE_TESTS_PASS: known-version refresh, verify-only, custom resource protection, explicit force, mixed-bundle rejection')
