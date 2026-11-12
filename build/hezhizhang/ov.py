import json,sys,numpy as np
from PIL import Image,ImageDraw,ImageFont
F='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244/fonts/LXGWWenKai-Regular.ttf'
B=json.load(open(sys.argv[1])); f=ImageFont.truetype(F,40)
for pg in sorted(set(b[2] for b in B)):
    i=int(pg[2:5]); m=np.load('/tmp/hezhizhang/m%d.npy'%i)
    im=Image.fromarray(((1-m)*255).astype('uint8')).convert('RGB'); d=ImageDraw.Draw(im)
    for n,b in enumerate(B):
        if b[2]!=pg: continue
        c=(0,160,0) if b[7]=='ok' else (230,120,0)
        d.rectangle(b[3:7],outline=c,width=3)
        d.text((b[5]+4,b[4]),b[1]+str(n),fill=(220,0,0),font=f)
    im.resize((im.width//2,im.height//2)).save('/tmp/hezhizhang/ov%d.jpg'%i)
