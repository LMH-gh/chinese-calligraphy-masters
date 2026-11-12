import sys
from PIL import Image, ImageDraw, ImageFont
from spec import S
F='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244/fonts/LXGWWenKai-Regular.ttf'
im=Image.open('/tmp/gaoxian/sh.jpg').convert('RGB'); d=ImageDraw.Draw(im); f=ImageFont.truetype(F,16)
for li,(t,x1,x2,ys) in enumerate(S):
    for k,ch in enumerate(t):
        c=[(255,0,0),(0,90,255),(0,170,0)][k%3]
        d.rectangle([x1,ys[k],x2,ys[k+1]],outline=c,width=2)
        d.text((x1+2,ys[k]+1),ch,fill=c,font=f)
    d.text((x1+2,600),str(li+1),fill=(255,0,255),font=f)
im.save('/tmp/gaoxian/ov.jpg')
for i,x in enumerate(range(6700,0,-900)):
    im.crop((max(0,x-950),0,x,619)).save('/tmp/gaoxian/ov%d.jpg'%i)
