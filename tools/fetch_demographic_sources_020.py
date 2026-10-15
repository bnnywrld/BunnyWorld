"""Download country-level year-2000 WDI inputs. Runtime is entirely offline."""
from pathlib import Path
import json, urllib.request, concurrent.futures, time
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'tools/sources_020'; DEST.mkdir(exist_ok=True)
codes=['SP.POP.TOTL.FE.ZS','SL.TLF.CACT.ZS','SL.UEM.TOTL.ZS','SE.PRM.CUAT.ZS','SE.SEC.CUAT.UP.ZS','SE.TER.CUAT.ST.ZS']
for age in [f'{a:02}{a+4:02}' for a in range(0,80,5)]+['80UP']:
 for sex in ['FE','MA']: codes.append(f'SP.POP.{age}.{sex}.5Y')
def fetch(code):
 path=DEST/(code+'.json')
 if path.exists(): return code, 'cached'
 date='1995:2005' if code.startswith('SE.') else '2000'
 url=f'https://api.worldbank.org/v2/country/all/indicator/{code}?date={date}&format=json&per_page=20000'
 for attempt in range(3):
  try:
   with urllib.request.urlopen(url,timeout=35) as r: data=json.load(r)
   if len(data)!=2 or not isinstance(data[1],list):raise ValueError(str(data)[:100])
   path.write_text(json.dumps({'url':url,'data':data}))
   return code,len(data[1])
  except Exception as e:
   if attempt==2:return code,str(e)
   time.sleep(1)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
 for result in pool.map(fetch,codes):print(*result,flush=True)
