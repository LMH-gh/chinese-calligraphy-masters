import json,sys,os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS=None
F='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244/fonts/LXGWWenKai-Regular.ttf'
def load_mask(img,th=85,ymax=None):
    a=np.asarray(Image.open(img).convert('RGB')).astype(int)
    g=a.mean(2); sat=a.max(2)-a.min(2)
    m=((g<th)&(sat<70)).astype('uint8')
    if ymax: m[ymax:]=0
    return cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),'uint8'))
def cut(mask,box,pad=0):
    x1,y1,x2,y2=box; H,W=mask.shape
    sub=mask[y1:y2,x1:x2].copy()
    # remove components touching edge that are mostly outside: check in padded region
    P=60; X1,Y1,X2,Y2=max(0,x1-P),max(0,y1-P),min(W,x2+P),min(H,y2+P)
    big=mask[Y1:Y2,X1:X2]
    n,lab,st,_=cv2.connectedComponentsWithStats(big,8)
    inner=lab[y1-Y1:y2-Y1,x1-X1:x2-X1]
    for i in range(1,n):
        area=st[i][4]; ins=(inner==i).sum()
        if ins==0: continue
        if ins<80 or ins/area<0.25: sub[inner==i]=0
    n2,lab2,st2,_=cv2.connectedComponentsWithStats(sub,8)
    for i in range(1,n2):
        if st2[i][4]<50: sub[lab2==i]=0
    ys,xs=np.nonzero(sub)
    if len(xs)==0: return None
    sub=sub[ys.min():ys.max()+1, xs.min():xs.max()+1]
    return Image.fromarray(((1-sub)*255).astype('uint8'))
def sheet(items,out,cell=180,cols=12):
    f=ImageFont.truetype(F,28)
    rows=(len(items)+cols-1)//cols
    S=Image.new('RGB',(cols*cell,rows*(cell+36)),'white'); d=ImageDraw.Draw(S)
    for i,(lab,im) in enumerate(items):
        x,y=(i%cols)*cell,(i//cols)*(cell+36)
        if im is not None:
            t=im.copy(); t.thumbnail((cell-10,cell-10)); S.paste(t,(x+5,y+36))
        d.text((x+5,y+2),lab,fill=(200,0,0),font=f)
    S.save(out)
if __name__=='__main__':
    img,boxes,out=sys.argv[1:4]
    m=load_mask(img); B=json.load(open(boxes))
    items=[(f"{i}{b[0]}",cut(m,b[1:])) for i,b in enumerate(B)]
    sheet(items,out)
