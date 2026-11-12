import sys,numpy as np
from PIL import Image,ImageDraw,ImageFont
Image.MAX_IMAGE_PIXELS=None
F='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244/fonts/LXGWWenKai-Regular.ttf'
s,x1,x2,y1,y2,sc=sys.argv[1],*map(int,sys.argv[2:6]),float(sys.argv[6])
im=Image.open(f'src/1977_375_29{s}_O1_sf.jpg').convert('RGB').crop((x1,y1,x2,y2))
im=im.resize((int(im.width*sc),int(im.height*sc)))
d=ImageDraw.Draw(im); f=ImageFont.truetype(F,int(22))
for x in range((x1//100+1)*100,x2,100):
    X=(x-x1)*sc; d.line([(X,0),(X,12 if x%500 else 30)],fill=(255,0,0),width=2)
    if x%500==0: d.text((X+2,30),str(x),fill=(255,0,0),font=f)
for y in range((y1//100+1)*100,y2,100):
    Y=(y-y1)*sc; d.line([(0,Y),(12 if y%500 else 30,Y)],fill=(0,160,255),width=2)
    if y%500==0: d.text((32,Y),str(y),fill=(0,160,255),font=f)
im.save(sys.argv[7] if len(sys.argv)>7 else '/tmp/zhangxu_dq/g.jpg',quality=85)
