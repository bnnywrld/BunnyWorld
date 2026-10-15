"""Generate GPU water fill from the same centre lines/widths as CPU picking."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
passages=json.loads((ROOT/'data/waterways.json').read_text())['passages']
code=['// Authored narrow waterways: source of truth is data/waterways.json.','float water_passage(vec2 uv){',' vec2 p=vec2(uv.x*360.0-180.0,90.0-uv.y*180.0);']
for passage in passages:
 pts=passage['coordinates'];xs=[p[0] for p in pts];ys=[p[1] for p in pts];w=passage['display_width_km'];sid=passage['ends'][0]
 code.append(f' if(p.x>{min(xs)-.05:.6f}&&p.x<{max(xs)+.05:.6f}&&p.y>{min(ys)-.05:.6f}&&p.y<{max(ys)+.05:.6f})'+'{')
 code.append('  vec2 metric=vec2(cos(p.y*.01745329252)*111.195,111.195);')
 for a,b in zip(pts[:-1],pts[1:]):
  code.append(f'  {{vec2 a=vec2({a[0]:.6f},{a[1]:.6f});vec2 v=(vec2({b[0]:.6f},{b[1]:.6f})-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<{w/2:.6f})return {sid:.1f};}}')
 code.append(' }')
code+=[' return 0.0;','}']
(ROOT/'scripts/water_passages.gdshaderinc').write_text('\n'.join(code)+'\n')
print('WATER_PASSAGE_INCLUDE_PREPARED',len(passages))
