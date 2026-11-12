import json,sys
from PIL import Image,ImageDraw,ImageFont;Image.MAX_IMAGE_PIXELS=None
from spec import COLS
F='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244/fonts/LXGWWenKai-Regular.ttf'
im=Image.open('/tmp/dumu/zh.jpg'); R=json.load(open(sys.argv[1] if len(sys.argv)>1 else 'boxes_raw.json'))
f=ImageFont.truetype(F,60)
s=0.35
for g in range(0,48,8):
    cs=COLS[g:g+8]; X1=cs[-1][1]-30; X2=cs[0][2]+30
    c=im.crop((X1,0,X2,2160)).convert('RGB'); d=ImageDraw.Draw(c)
    for r in R:
        if not (g<r[0]<=g+8): continue
        x1,y1,x2,y2=r[3:7]; col=(255,0,0) if r[7]=='ok' else (0,120,255)
        d.rectangle([x1-X1,y1,x2-X1,y2],outline=col,width=5); d.text((x2-X1-40,y1),r[1],fill=(255,255,0),font=f)
    c.resize((int(c.width*s),int(c.height*s))).save(f'/tmp/dumu/ov{g//8}.jpg')
