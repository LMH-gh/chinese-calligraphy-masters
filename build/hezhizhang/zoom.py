import json,sys,numpy as np
from PIL import Image,ImageDraw,ImageFont
F='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244/fonts/LXGWWenKai-Regular.ttf'
f=ImageFont.truetype(F,22)
def strip(i,x1,y1,x2,y2,step=20,scale=0.55):
    m=np.load('/tmp/hezhizhang/m%d.npy'%i)
    im=Image.fromarray(((1-m[y1:y2,x1:x2])*255).astype('uint8')).convert('RGB'); d=ImageDraw.Draw(im)
    for y in range((y1//step+1)*step,y2,step):
        big=y%100==0
        d.line([(0,y-y1),(12 if not big else 40,y-y1)],fill=(0,0,255),width=2)
        if big: d.text((42,y-y1-12),str(y),fill=(0,0,255),font=f)
    return im.resize((int(im.width*scale),int(im.height*scale)))
specs=json.loads(sys.argv[1]); out=sys.argv[2]
ims=[strip(*s) for s in specs]
W=sum(i.width for i in ims)+10*len(ims); H=max(i.height for i in ims)
S=Image.new('RGB',(W,H),'white'); x=0
for i in ims: S.paste(i,(x,0)); x+=i.width+10
S.save(out)
