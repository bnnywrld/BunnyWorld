"""Fetch matching MD portraits at a pinned revision and losslessly encode decoded pixels as PNG.
The committed manifest is the reproducible input on subsequent runs. --tree accepts
an external GitHub tree snapshot for the initial match, never a copied asset tree.
"""
import argparse, concurrent.futures, hashlib, io, json, os, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
REPO='MillenniumDawn/Millennium-Dawn'
COMMIT='e231ce3935a558f1d7baaa3c9bf15ef888cd3f04'

def fetch(path):
    url=f'https://raw.githubusercontent.com/{REPO}/{COMMIT}/'+urllib.parse.quote(path)
    for attempt in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'BunnyWorld portrait importer'}),timeout=45).read()
        except OSError:
            if attempt==2: raise
            time.sleep(1)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--tree',type=Path);args=ap.parse_args()
    target=ROOT/'data/leader_portraits.json'
    if args.tree:
        tree=json.loads(args.tree.read_text(encoding='utf8'));assert tree['sha']==COMMIT
        blobs={x['path'].lower():x for x in tree['tree'] if x['type']=='blob'}
        leaders=json.loads((ROOT/'data/leaders_2000.json').read_text(encoding='utf8'))['countries']
        entries={}
        for tag,country in leaders.items():
            for role in ['head_of_state','head_of_government']:
                person=country[role]
                if not person:continue
                reference=person['portrait_reference']
                candidates=[reference, 'gfx/leaders/'+tag+'/'+reference] if reference else ['gfx/leaders/'+tag+'/'+person['name'].replace(' ','_')+'.dds']
                match=next((blobs[p.lower()] for p in candidates if p.lower() in blobs),None)
                if match:
                    entries[tag+':'+role]={'name':person['name'],'reference':reference,'upstream_path':match['path'],'git_blob':match['sha'],'asset':'res://assets/ui/leaders/'+match['sha']+'.png'}
        manifest={'repository':'https://github.com/'+REPO,'commit':COMMIT,'license':'CC-BY-SA-4.0; see licenses/Millennium_Dawn_LICENSE.txt','entries':entries}
    else:
        manifest=json.loads(target.read_text(encoding='utf8'));assert manifest['commit']==COMMIT
    (ROOT/'assets/ui/leaders').mkdir(parents=True,exist_ok=True)
    cache=Path(os.environ.get('TEMP','/tmp'))/'bunnyworld-md-portrait-sources'
    cache.mkdir(parents=True,exist_ok=True)
    def install(pair):
        key,entry=pair
        entry['asset']='res://assets/ui/leaders/'+entry['git_blob']+'.png'
        path=ROOT/entry['asset'].removeprefix('res://')
        original=cache/(entry['git_blob']+'.dds')
        legacy=path.with_suffix('.dds')
        raw=original.read_bytes() if original.exists() else (legacy.read_bytes() if legacy.exists() else fetch(entry['upstream_path']))
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==entry['git_blob'],key
        assert raw.startswith(b'DDS '),key
        if not original.exists():original.write_bytes(raw)
        image=Image.open(io.BytesIO(raw)).convert('RGBA')
        image.save(path,format='PNG')
        # Preserve source bytes externally, keeping only the runtime format in Git.
        if legacy.exists():
            assert legacy.resolve().is_relative_to((ROOT/'assets/ui/leaders').resolve())
            legacy.unlink()
        entry['source_sha256']=hashlib.sha256(raw).hexdigest()
        entry['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        return key,entry
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        done=dict(pool.map(install,manifest['entries'].items()))
    manifest['entries']=done
    license_path=ROOT/'licenses/Millennium_Dawn_LICENSE.txt'
    if not license_path.exists():license_path.write_bytes(fetch('LICENSE'))
    target.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    print(len(done),'lossless PNG portraits installed from',COMMIT,flush=True)
if __name__=='__main__':main()
