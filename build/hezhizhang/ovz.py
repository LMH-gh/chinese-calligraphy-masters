# 放大看某页某几列：python3 ovz.py boxes.json page x1 x2 [y1 y2] [scale]
import json,sys,numpy as np
from PIL import Image,ImageDraw,ImageFont
F='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244/fonts/LXGWWenKai-Regular.ttf'
B=json.load(open(sys.argv[1])); i=int(sys.argv[2]); x1,x2=int(sys.argv[3]),int(sys.argv[4])
y1,y2=(int(sys.argv[5]),int(sys.argv[6])) if len(sys.argv)>6 else (0,3056)
sc=float(sys.argv[7]) if len(sys.argv)>7 else 0.5
f=ImageFont.truetype(F,40); g=Image.open('/tmp/hezhizhang/s/p-%03d.jpg'%i).convert('L')
m=np.load('/tmp/hezhizhang/m%d.npy'%i)
im=Image.fromarray(((1-m)*255).astype('uint8')).convert('RGB'); d=ImageDraw.Draw(im)
for n,b in enumerate(B):
    if b[2]!='p-%03d.jpg'%i: continue
    c=(0,170,0) if b[7]=='ok' else (230,120,0)
    d.rectangle(b[3:7],outline=c,width=3)
    d.text((b[3]-3,b[4]),b[1]+str(n),fill=(220,0,0),font=f,anchor='rt')
for y in range(0,3056,100): d.line([(x1,y),(x1+25 if y%500 else x1+60,y)],fill=(0,0,255),width=3)
im=im.crop((x1-120,y1,x2,y2)); im.resize((int(im.width*sc),int(im.height*sc))).save('/tmp/hezhizhang/z.jpg')
