import rasterio, numpy as np, pandas as pd, glob, sys
from rasterio.windows import from_bounds
from pyproj import Transformer
from PIL import Image, ImageDraw, ImageFont
# usage: python3 make_maps_gagetown_2026-10-28.py <sentinel2_assets.txt> <detections.csv>
A=dict(l.split() for l in open(sys.argv[1]))
T=Transformer.from_crs(4326,32619,always_xy=True)
det=pd.read_csv(sys.argv[2])
det=det[det.source.str.startswith('VIIRS')]
F=lambda z:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',z)
cols={'13:22':(255,60,40),'14:00':(255,150,0),'14:20':(255,230,0),'15:04':(255,0,200),'15:41':(0,230,255)}
def rd(k,b):
    s=rasterio.open(A[k]); w=from_bounds(*b,s.transform); return s.read(window=w,boundless=True)
def st(a,lo=2,hi=98,g=1.0):
    a=a.astype(float); l,h=np.nanpercentile(a[a>0],(lo,hi)); return (np.clip((a-l)/(h-l),0,1)**g*255).astype(np.uint8)
def make(cE,cN,half,out,title,mode,size=1600,labels=()):
    b=(cE-half,cN-half,cE+half,cN+half)
    if mode=='tci': img=rd('visual',b).transpose(1,2,0)
    else: img=np.dstack([np.array(Image.fromarray(st(rd(k,b)[0])).resize((500,500))) for k in ('swir22','nir08','red')])
    im=Image.fromarray(img).resize((size,size),Image.LANCZOS); d=ImageDraw.Draw(im,'RGBA'); s=size/(2*half)
    P=lambda E,N:((E-b[0])*s,(b[3]-N)*s)
    for _,r in det.iterrows():
        E,N=T.transform(r.longitude,r.latitude); x,y=P(E,N); hp=max(187.5*s,3)  # ~375 m VIIRS pixel
        c=cols.get(r['local'][11:16],(255,255,255))
        d.rectangle([x-hp,y-hp,x+hp,y+hp],outline=c+(255,),width=3 if half<4000 else 2)
    for nm,la,lo in labels:
        x,y=P(*T.transform(lo,la)); d.ellipse([x-8,y-8,x+8,y+8],fill=(255,255,255),outline=(0,0,0),width=2)
        d.rectangle([x+12,y-16,x+18+d.textlength(nm,font=F(24)),y+16],fill=(0,0,0,170)); d.text((x+15,y-14),nm,font=F(24),fill=(255,255,255))
    d.rectangle([0,0,size,96],fill=(0,0,0,190)); d.text((20,10),title,font=F(30),fill=(255,255,255))
    d.text((20,54),('Sentinel-2, Oct. 27, 2026 (day BEFORE the fire), '+('true colour' if mode=='tci' else 'SWIR false colour')+'. Boxes: VIIRS detections Oct. 28 (~375 m pixels).'),font=F(19),fill=(225,225,225))
    y0=size-150; d.rectangle([0,y0,560,size],fill=(0,0,0,180))
    for i,(t,c) in enumerate(cols.items()):
        n=(det['local'].str[11:16]==t).sum(); mw=det[det['local'].str[11:16]==t].frp.max()
        d.rectangle([20,y0+12+i*26,40,y0+30+i*26],outline=c,width=3); d.text((50,y0+8+i*26),f'{t} ADT  {n} detections, peak {mw:.0f} MW',font=F(19),fill=(255,255,255))
    L=(1000 if half<4000 else 5000)*s; d.rectangle([size-40-L,size-40,size-40,size-30],fill=(255,255,255)); d.text((size-40-L,size-72),('1 km' if half<4000 else '5 km'),font=F(22),fill=(255,255,255))
    d.text((size-560,size-24),'Contains modified Copernicus Sentinel data [2026]; NASA FIRMS. Prime Rogue Inc.',font=F(14),fill=(230,230,230))
    im.convert('RGB').save(out,quality=88)
cE,cN=T.transform(-66.257,45.749)
make(cE,cN,2500,'cfb-gagetown-fire-2026-10-28-closeup-truecolour.jpg','CFB Gagetown fire, Oct. 28, 2026: satellite fire detections','tci')
make(cE,cN,2500,'cfb-gagetown-fire-2026-10-28-closeup-swir.jpg','CFB Gagetown fire, Oct. 28, 2026: satellite fire detections','swir')
oE,oN=T.transform(-66.27,45.78)
make(oE,oN,14000,'cfb-gagetown-fire-2026-10-28-locator.jpg','CFB Gagetown fire, Oct. 28, 2026: where it is','tci',labels=[('Gagetown village',45.7790,-66.1460)])
