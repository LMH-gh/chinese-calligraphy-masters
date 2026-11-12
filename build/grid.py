import sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS=None
F='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244/fonts/LXGWWenKai-Regular.ttf'
def grid(src,x1,y1,x2,y2,out,scale=0.5,step=100):
    im=Image.open(src).convert('RGB'); c=im.crop((x1,y1,x2,y2)); d=ImageDraw.Draw(c)
    f=ImageFont.truetype(F,int(36/scale*0.5))
    for x in range((x1//step+1)*step,x2,step):
        big=x%(step*5)==0
        d.line([(x-x1,0),(x-x1,c.height)],fill=(255,0,0) if big else (255,150,150),width=3 if big else 1)
        if big: d.text((x-x1+4,4),str(x),fill=(255,0,0),font=f)
    for y in range((y1//step+1)*step,y2,step):
        big=y%(step*5)==0
        d.line([(0,y-y1),(c.width,y-y1)],fill=(0,0,255) if big else (150,150,255),width=3 if big else 1)
        if big: d.text((4,y-y1+4),str(y),fill=(0,0,255),font=f)
    c.resize((int(c.width*scale),int(c.height*scale))).save(out)
if __name__=='__main__':
    a=sys.argv; grid(a[1],*map(int,a[2:6]),a[6],float(a[7]) if len(a)>7 else 0.5)
