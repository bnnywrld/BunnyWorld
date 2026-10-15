"""Original vector UI symbols for the 19 organizations, using recognizable motifs.
No summit logos or tiny lettering. All text outlined; Godot imports at 256px.
Geographic motifs use Natural Earth public-domain polygons.
"""
from pathlib import Path
import math,json,argparse
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from shapely.geometry import shape
from shapely.ops import unary_union
args=argparse.ArgumentParser();args.add_argument('--font',default='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf');options=args.parse_args()
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'assets/organizations';font=TTFont(options.font);glyphs=font.getGlyphSet();cmap=font.getBestCmap();upm=font['head'].unitsPerEm
units=json.loads((ROOT/'tools/cartography/natural_earth_map_units.geojson').read_text())['features']
world=unary_union([shape(f['geometry']) for f in units if f['properties'].get('NAME')!='Antarctica']).simplify(1.5)
africa=unary_union([shape(f['geometry']) for f in units if f['properties'].get('CONTINENT')=='Africa']).simplify(.5)
def geo(g,bounds):
 l,t,r,b=bounds;x0,y0,x1,y1=g.bounds;scale=min((r-l)/(x1-x0),(b-t)/(y1-y0));paths=[]
 for p in list(g.geoms) if hasattr(g,'geoms') else [g]:
  pts=[(l+(x-x0)*scale,t+(y1-y)*scale) for x,y in p.exterior.coords];paths.append('M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in pts)+'Z')
 return ''.join(paths)
def star(x,y,size,color,n=5):
 pts=[]
 for i in range(n*2):
  a=-math.pi/2+i*math.pi/n;rr=size if i%2==0 else size*.43;pts.append(f'{x+math.cos(a)*rr:.2f},{y+math.sin(a)*rr:.2f}')
 return '<polygon points="'+' '.join(pts)+'" fill="'+color+'"/>'
def text(s,y=194,size=34,color='#eef5ff'):
 scale=size/upm;advance=sum(glyphs[cmap[ord(c)]].width for c in s)*scale;x=(256-advance)/2;parts=[]
 for c in s:
  g=glyphs[cmap[ord(c)]];pen=SVGPathPen(glyphs);g.draw(pen);parts.append(f'<path d="{pen.getCommands()}" transform="translate({x:.2f} {y}) scale({scale} {-scale})" fill="{color}"/>');x+=g.width*scale
 return ''.join(parts)
def globe(color='#73c9ee'):
 return '<circle cx="128" cy="112" r="61" fill="none" stroke="'+color+'" stroke-width="4"/><ellipse cx="128" cy="112" rx="28" ry="61" fill="none" stroke="'+color+'" stroke-width="3"/><path d="M67 112H189 M78 83Q128 64 178 83 M78 141Q128 160 178 141" fill="none" stroke="'+color+'" stroke-width="3"/>'
def laurel(color='#a2dd90'):
 return ''.join(f'<ellipse cx="{128+math.cos(a)*76:.1f}" cy="{116+math.sin(a)*76:.1f}" rx="5" ry="12" transform="rotate({math.degrees(a)+35:.1f} {128+math.cos(a)*76:.1f} {116+math.sin(a)*76:.1f})" fill="{color}"/>' for a in [math.radians(v) for v in list(range(125,236,16))+list(range(-55,56,16))])
body={}
body['EU']=''.join(star(128+58*math.sin(i*math.pi/6),111-58*math.cos(i*math.pi/6),12,'#ffdc48') for i in range(12))
body['NATO']='<circle cx="128" cy="112" r="58" fill="none" stroke="#dceeff" stroke-width="3"/><path d="M128 31L144 96L209 112L144 128L128 193L112 128L47 112L112 96Z" fill="#f1f6ff"/><path d="M128 31V112H47 M128 193V112H209" fill="none" stroke="#4485ca" stroke-width="3"/>'
body['ASEAN']='<circle cx="128" cy="111" r="67" fill="#cb2e3d" stroke="#ffffff" stroke-width="5"/>'+''.join(f'<path d="M{101+i*6} 80 Q{98+i*7} 111 128 153" fill="none" stroke="#fddd52" stroke-width="5"/><ellipse cx="{101+i*6}" cy="76" rx="3" ry="11" fill="#fddd52"/>' for i in range(10))
body['CSTO']=star(128,111,78,'#e6bd58',8)+star(128,111,54,'#498dcc',8)+'<circle cx="128" cy="111" r="26" fill="#163b72" stroke="#ffe39b" stroke-width="4"/>'
body['CIS']='<circle cx="128" cy="111" r="70" fill="none" stroke="#95cdff" stroke-width="4"/>'+''.join(f'<path d="M128 172Q{x} 155 {x} 82" fill="none" stroke="#e3f4ff" stroke-width="7" stroke-linecap="round"/>' for x in [90,109,128,147,166])+'<circle cx="128" cy="66" r="13" fill="#f5d668"/>'
body['OAU']='<path d="'+geo(africa,(87,43,173,161))+'" fill="#efd772"/>'+laurel()+text('OAU')
body['ARAB']='<circle cx="128" cy="111" r="57" fill="none" stroke="#f1db88" stroke-width="4"/>'+laurel()+text('LAS',126,34,'#f1db88')
body['GCC']='<polygon points="128,35 193,74 193,150 128,187 63,150 63,74" fill="none" stroke="#f2ce68" stroke-width="5"/>'+text('GCC',125,38,'#f2ce68')
body['APEC']='<ellipse cx="128" cy="111" rx="83" ry="57" fill="none" stroke="#71cde7" stroke-width="4"/><path d="'+geo(world,(50,74,206,152))+'" fill="#68caad"/>'+text('APEC',211,31)
body['OECD']=globe()+'<path d="M78 182L102 164L78 146 M102 182L126 164L102 146" fill="none" stroke="#a2d99a" stroke-width="7"/>'+text('OECD',218,29)
body['OPEC']=''.join(f'<circle cx="{x}" cy="{y}" r="29" fill="none" stroke="#88d4f3" stroke-width="10"/>' for x,y in [(91,75),(165,75),(91,143),(165,143)])+text('OPEC',218,30)
body['MERCOSUR']='<path d="M57 151Q127 101 200 109" fill="none" stroke="#71c88c" stroke-width="6"/>'+''.join(star(x,y,14,'#8acaff') for x,y in [(86,81),(150,53),(172,105),(124,143)])+text('MERCOSUR',211,24)
body['G7']=''.join('<circle cx="%.1f" cy="%.1f" r="13" fill="#83cdee"/>'%(128+60*math.cos(i*math.tau/7),110+60*math.sin(i*math.tau/7)) for i in range(7))+text('G7',129,48)
body['NAFTA']=''.join(f'<path d="M{x} 63L{x+54} 111L{x} 159" fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round"/>' for x,color in [(60,'#ea7081'),(101,'#eef4ff'),(142,'#71c58f')])+text('NAFTA',213,30)
body['IMF']=globe('#b2d6f6')+laurel('#8eb9e8')+text('IMF',219,31)
body['IBRD']=globe('#73cceb')+text('WORLD BANK',219,20)
body['OSCE']=''.join(f'<rect x="{35+i*48}" y="77" width="43" height="65" rx="4" fill="#427cc0"/>' for i in range(4))+text('OSCE',125,30)+text('SECURITY',203,21)
body['WTO']=''.join(f'<path d="M61 {82+i*28}Q130 {28+i*28} 195 {95+i*28}" fill="none" stroke="{color}" stroke-width="12" stroke-linecap="round"/>' for i,color in enumerate(['#e56e7f','#7ecd9f','#75bcf0']))+text('WTO',215,33)
body['ECOWAS']='<path d="'+geo(africa,(88,43,173,161))+'" fill="#a5d694"/>'+laurel('#dfcb74')+star(113,116,12,'#dfcb74')+text('ECOWAS',218,27)
for oid,contents in body.items():
 svg='<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256"><rect x="4" y="4" width="248" height="248" rx="35" fill="#102e49" stroke="#446784" stroke-width="4"/>'+contents+'</svg>'
 (out/(oid+'.svg')).write_text(svg)
for p in out.glob('*.png'):p.unlink()
for p in out.glob('*.png.import'):p.unlink()
p=ROOT/'data/world.json';w=json.loads(p.read_text())
for oid,org in w['organizations'].items():org['logo']='res://assets/organizations/'+oid+'.svg'
p.write_text(json.dumps(w,ensure_ascii=False,separators=(',',':')))
print('VECTOR_SYMBOLS_COMPLETE',len(body))
