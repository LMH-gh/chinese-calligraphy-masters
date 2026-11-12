import json,sys
from PIL import Image,ImageDraw,ImageFont;Image.MAX_IMAGE_PIXELS=None
from spec import COLS
F='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244/fonts/LXGWWenKai-Regular.ttf'
im=Image.open('/tmp/dumu/zh.jpg'); R=json.load(open('boxes_raw.json')); f=ImageFont.truetype(F,50)
L=[int(x) for x in sys.argv[2].split(',')]; s=0.35; ims=[]
for ln in L:
    _,a,b,t=COLS[ln-1]; X1=a-60; c=im.crop((X1,0,b+60,2160)).convert('RGB'); d=ImageDraw.Draw(c)
    for r in R:
        if r[0]!=ln: continue
        x1,y1,x2,y2=r[3:7]; col=(255,0,0) if r[7]=='ok' else (0,120,255)
        d.rectangle([x1-X1,y1,x2-X1,y2],outline=col,width=5); d.text((x2-X1-30,y1),r[1],fill=(255,255,0),font=f)
    d.text((5,5),str(ln),fill=(255,0,255),font=f)
    ims.append(c.resize((int(c.width*s),int(c.height*s))))
W=sum(i.width+8 for i in ims); S=Image.new('RGB',(W,ims[0].height),'white'); x=W
for i in ims: x-=i.width+8; S.paste(i,(x,0))
S.save(sys.argv[1])
