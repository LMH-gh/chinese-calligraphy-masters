import json,sys,numpy as np
from PIL import Image,ImageDraw,ImageFont
F='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244/fonts/LXGWWenKai-Regular.ttf'
B=json.load(open(sys.argv[1])); pg=sys.argv[2]; sc=float(sys.argv[3]) if len(sys.argv)>3 else 0.4
f=ImageFont.truetype(F,44)
i=int(pg); m=np.load('/tmp/hezhizhang/m%d.npy'%i)
im=Image.fromarray(((1-m)*255).astype('uint8')).convert('RGB'); d=ImageDraw.Draw(im)
for n,b in enumerate(B):
    if b[2]!='p-%03d.jpg'%i: continue
    c=(0,170,0) if b[7]=='ok' else (230,120,0)
    d.rectangle(b[3:7],outline=c,width=4)
    d.text((b[3]-4,b[4]-6),b[1],fill=(220,0,0),font=f,anchor='rt')
im.resize((int(im.width*sc),int(im.height*sc))).save('/tmp/hezhizhang/ov%d.jpg'%i)
