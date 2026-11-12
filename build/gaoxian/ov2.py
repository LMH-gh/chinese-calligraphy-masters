import sys,json
from PIL import Image, ImageDraw, ImageFont
F='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244/fonts/LXGWWenKai-Regular.ttf'
bx=json.load(open('boxes_raw.json'))
x1,x2,sc,out=int(sys.argv[1]),int(sys.argv[2]),float(sys.argv[3]),sys.argv[4]
im=Image.open('/tmp/gaoxian/sh.jpg').convert('RGB').crop((x1,0,x2,619))
im=im.resize((int(im.width*sc),int(im.height*sc))); d=ImageDraw.Draw(im); f=ImageFont.truetype(F,18)
for i,b in enumerate(bx):
    l,ch,a,y,c,z=b
    if c<x1 or a>x2: continue
    col=[(255,0,0),(0,90,255),(0,170,0)][i%3]
    d.rectangle([(a-x1)*sc,y*sc,(c-x1)*sc,z*sc],outline=col,width=2)
    d.text(((a-x1)*sc+3,y*sc+2),f'{i}{ch}',fill=col,font=f)
im.save(out)
