"""Offline QA: six globe views plus regional inspections of the final exact atlas."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image
from pyproj import Transformer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography';OUT=ROOT/'validation_0210';OUT.mkdir(exist_ok=True)
Image.MAX_IMAGE_PIXELS=None
w=json.load(open(ROOT/'data/world.json'));a=np.load(SRC/'grouped_atlas_022r2.npz')['regions'];p=np.load(SRC/'province_atlas_0210.npz')['provinces'];H,W=a.shape
colors=np.zeros((8192,3));colors[0]=[.04,.09,.14];colors[8191]=[.76,.82,.85]
for k,s in w['regions'].items():colors[int(k)]=np.clip(np.array(w['countries'][s['owner']]['color'])/255*.65+.18+np.random.default_rng(int(k)).uniform(-.07,.07,3),.06,.93)
def render(lon,lat):
 valid=np.isfinite(lon)&np.isfinite(lat);xx=np.clip(((np.where(valid,lon,0)+180)/360*W).astype(int),0,W-1);yy=np.clip(((90-np.where(valid,lat,0))/180*H).astype(int),0,H-1);s=a[yy,xx];q=p[yy,xx];im=colors[s].copy()
 def edge(v):
  e=np.zeros(v.shape,bool);e[1:]|=v[1:]!=v[:-1];e[:,1:]|=v[:,1:]!=v[:,:-1];return e
 im[edge(q)&(q>0)]*=.35;im[edge(s)]=[.96,.97,.94];im[~valid]=[.025,.04,.06];return im
fig,axs=plt.subplots(2,3,figsize=(18,12),facecolor='#101d2b')
for ax,(name,lo,la) in zip(axs.flat,[('Americas',-90,20),('Europe / Africa',15,25),('Asia',100,25),('Pacific',170,-20),('Northern hemisphere',30,80),('South Atlantic / Antarctica',-20,-65)]):
 inv=Transformer.from_crs(f'+proj=ortho +lat_0={la} +lon_0={lo} +R=6371008.8','EPSG:4326',always_xy=True);xy=np.linspace(-6371008.8,6371008.8,1400);x,y=np.meshgrid(xy,xy[::-1]);lon,lat=inv.transform(x,y);ax.imshow(render(lon,lat));ax.set_title(name,color='white');ax.axis('off')
fig.tight_layout();fig.savefig(OUT/'global_review.png',dpi=115,facecolor=fig.get_facecolor());plt.close(fig)
areas=[('North America',-130,20,-60,55),('South America',-82,-56,-34,13),('Europe',-13,35,35,62),('Africa',-18,-35,52,37),('Middle East',32,12,64,42),('Central Asia',45,30,90,57),('South Asia',65,5,95,37),('East Asia',100,18,145,53),('Southeast Asia',90,-12,141,26),('Australasia',110,-48,180,0),('Russia west',28,45,95,76),('Russia east',90,43,178,76),('Kalimantan',108,-5,120,7),('Ghazni',66,31,70,34.5),('Syria',35,32,43,38),('Eastern Ukraine',32,45,41,51),('Sweden and Aland',16,58.5,23,61.5),('Guyana',-62,1,-56,9)]
for page in range(3):
 fig,axs=plt.subplots(2,3,figsize=(18,12),facecolor='#101d2b')
 for ax,(name,l,b,r,t) in zip(axs.flat,areas[page*6:page*6+6]):
  width=1100;height=max(600,min(1600,int(width*(t-b)/(r-l)/max(.2,math.cos(math.radians((b+t)/2))))));lon,lat=np.meshgrid(np.linspace(l,r,width),np.linspace(t,b,height));ax.imshow(render(lon,lat),extent=[l,r,b,t]);ax.set_aspect(1/max(.2,math.cos(math.radians((b+t)/2))));ax.set_title(name,color='white');ax.tick_params(colors='#aabaca',labelsize=7)
 fig.tight_layout();fig.savefig(OUT/f'regional_review_{page+1}.png',dpi=115,facecolor=fig.get_facecolor());plt.close(fig)
# A continuous Pacific view crosses the date line without introducing a seam.
rgb=np.array(Image.open(ROOT/'assets/sea_ids.png'),np.uint16);sea=rgb[:,:,0]+rgb[:,:,1]*256;hh,ww=sea.shape
lon,lat=np.meshgrid(np.linspace(145,210,1400),np.linspace(0,-65,1400));s=sea[np.clip(((90-lat)/180*hh).astype(int),0,hh-1),((lon+180)/360*ww).astype(int)%ww];pal=np.random.default_rng(99).uniform(.2,.8,(256,3));pal[0]=.07;im=pal[s];e=np.zeros(s.shape,bool);e[1:]|=s[1:]!=s[:-1];e[:,1:]|=s[:,1:]!=s[:,:-1];im[e]=1
fig,ax=plt.subplots(figsize=(10,10));ax.imshow(im,extent=[145,210,-65,0]);ax.set_title('0.2.0.10 Pacific water identities');seas=json.load(open(ROOT/'data/sea_regions.json'))
for sid in np.unique(s):
 if not sid:continue
 yy,xx=np.nonzero(s==sid);j=len(xx)//2;ax.text(145+xx[j]/1400*65,-yy[j]/1400*65,seas[str(sid)]['name'],fontsize=7)
fig.tight_layout();fig.savefig(OUT/'pacific_review.png',dpi=120);plt.close(fig)
print('GEOGRAPHY_0210_PREVIEWS_COMPLETE')
