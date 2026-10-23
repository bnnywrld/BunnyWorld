"""Build one global religion mapping/palette without altering source shares."""
import colorsys
import json
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ALIASES = {'Nonreligious':'Atheist','Other / not stated':'Other / unspecified','Tibetan Buddhist':'Buddhist','Maronite':'Catholic','Greek Catholic':'Catholic','Shia (Zaydi)':'Shia','Ismaili':'Shia'}
COLORS = {'Catholic':'4f88d0','Protestant':'83b9e6','Orthodox':'8b78ca','Sunni':'4fac78','Shia':'227357','Hindu':'ee9645','Buddhist':'e0c55a','Jewish':'6dcbd5','Sikh':'dfad70','Traditional / folk':'a77a53','Other religions':'c67caf','Atheist':'a6aab4','Other / unspecified':'647681','Unknown':'43505e','Christian (unspecified)':'6b91af','Muslim (unspecified)':'7b9a82'}

def main():
    counts = {}
    for file,container in [('demographics.json','profiles'),('state_demographics.json','states')]:
        data = json.loads((ROOT/'data'/file).read_text(encoding='utf-8'))
        counter = Counter()
        for profile in data[container].values(): counter.update(profile.get('metrics',{}).get('religion',{}).get('shares',{}))
        counts[container] = counter
    labels = sorted(set(counts['profiles'])|set(counts['states'])|{'Unknown'})
    mapping = {label:ALIASES.get(label,label) for label in labels}
    names = sorted(set(mapping.values()))
    catalog = {}
    for i,name in enumerate(names):
        color = COLORS.get(name)
        if not color:
            color = ''.join(f'{round(v*255):02x}' for v in colorsys.hsv_to_rgb((i*.61803398875)%1,.42,.77))
        catalog[name] = {'name':name,'color':color,'selectable':name not in ['Other religions','Other / unspecified','Unknown','Christian (unspecified)','Muslim (unspecified)','Christian (other)','Shinto / Buddhist']}
    unresolved = [{'label':label,'reason':'Broad/combined/unspecified source category retained; no branch split or atheist reassignment.','profiles':sum(label in p.get('metrics',{}).get('religion',{}).get('shares',{}) for p in json.loads((ROOT/'data/demographics.json').read_text(encoding='utf-8'))['profiles'].values()),'state_labels_present':label in counts['states']} for label in labels if any(t in label.lower() for t in ['unspecified','not stated',' / ','other','unknown'])]
    data = {'aliases':mapping,'catalog':catalog,'unresolved':unresolved,'policy':'Nonreligious means Atheist for gameplay. Missing/unspecified values stay separate. Clear branch aliases merge by addition; all other distinct and syncretic categories are retained. Source profiles are unchanged.'}
    (ROOT/'data/religion_catalog.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(len(labels),'source labels;',len(catalog),'canonical categories;',len(unresolved),'flagged source categories')
if __name__ == '__main__': main()
