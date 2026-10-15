"""Offline visual QA of the exact categorical map, in geographic/orthographic views."""
from pathlib import Path
import argparse,json,math
import numpy as np
from PIL import Image
from scipy.ndimage import maximum_filter
from pyproj import Transformer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'tools/cartography';W,H=16384,8192
world=json.load(open(ROOT/'data/world.json'));states=np.load(SRC/'grouped_atlas_022r2.npz')['regions']
parser=argparse.ArgumentParser();parser.add_argument('--prototype',action='store_true');args=parser.parse_args()
file=SRC/('prototype_0206.npz' if args.prototype else 'province_atlas_0206.npz')
provinces=np.load(file)['provinces'] if file.exists() else np.zeros_like(states)
colors=np.zeros((8192,3));colors[0]=[.055,.10,.15];colors[8191]=[.65,.72,.76]
for key,s in world['regions'].items():
    seed=np.random.default_rng(int(key)*73)
    base=np.array(world['countries'][s['owner']]['color'])/255
    colors[int(key)]=np.clip(base*.55+.25+seed.uniform(-.13,.13,3),.12,.9)
out=ROOT/'validation_0206';out.mkdir(exist_ok=True)

def render(lon,lat):
    valid=np.isfinite(lon)&np.isfinite(lat)
    xx=np.clip(((np.where(valid,lon,0)+180)/360*W).astype(int),0,W-1)
    yy=np.clip(((90-np.where(valid,lat,0))/180*H).astype(int),0,H-1)
    s=states[yy,xx];p=provinces[yy,xx]
    image=colors[s].copy()
    def edges(q):
        e=np.zeros(q.shape,bool);e[1:]|=q[1:]!=q[:-1];e[:,1:]|=q[:,1:]!=q[:,:-1];return e
    pe=edges(p)&(s>0)&(p>0);se=edges(s)
    image[pe]*=.46;image[se]=[.94,.95,.92];image[~valid]=[.025,.04,.065]
    return image

areas=[('Continental USA',-126,25,-66,50),('Europe',-12,35,32,60),('Egypt and Sahara',-18,12,39,34),('Japan',127,29,147,46),('Greenland',-74,58,-10,84),('Southeast Asia',92,-12,143,26)]
fig,axes=plt.subplots(2,3,figsize=(21,13),facecolor='#101d2b')
for ax,(title,l,b,r,t) in zip(axes.ravel(),areas):
    width=1150;height=max(400,int(width*(t-b)/(r-l)/max(.2,math.cos(math.radians((b+t)/2)))))
    lon,lat=np.meshgrid(np.linspace(l,r,width),np.linspace(t,b,height))
    ax.imshow(render(lon,lat),extent=[l,r,b,t]);ax.set_aspect(1/math.cos(math.radians((b+t)/2)))
    ax.set_title(title,color='white',fontsize=15);ax.tick_params(colors='#aabaca',labelsize=8)
    for state in world['regions'].values():
        u,v=state['map_center'];x=u*360-180;y=90-v*180
        if l<x<r and b<y<t and state['area_km2']>(r-l)*(t-b)*22:
            name=state['name'];ax.text(x,y,name[:26],fontsize=5.7,color='white',ha='center',va='center',bbox=dict(facecolor='#101d2b',alpha=.5,edgecolor='none',pad=.7))
fig.suptitle('BunnyWorld 0.2.0.6 · Geographic States and Provinces',color='white',fontsize=23,y=.99)
fig.tight_layout(rect=[0,0,1,.97]);fig.savefig(out/'regional_review.png',dpi=120,facecolor=fig.get_facecolor());plt.close(fig)
fig,axes=plt.subplots(1,3,figsize=(20,7),facecolor='#101d2b')
for ax,(title,lo,la) in zip(axes,[('Americas',-95,30),('Europe and Africa',15,30),('Asia',100,25)]):
    inverse=Transformer.from_crs(f'+proj=ortho +lat_0={la} +lon_0={lo} +R=6371008.8','EPSG:4326',always_xy=True)
    xy=np.linspace(-6371008.8,6371008.8,1500);x,y=np.meshgrid(xy,xy[::-1]);lon,lat=inverse.transform(x,y)
    ax.imshow(render(lon,lat));ax.set_title(title,color='white',fontsize=16);ax.axis('off')
fig.tight_layout();fig.savefig(out/'globe_review.png',dpi=110,facecolor=fig.get_facecolor());plt.close(fig)
print('GEOGRAPHY_PREVIEWS',out,flush=True)
