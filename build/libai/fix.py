import json,sys,os,numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
K='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244/work/kc'
F='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244/fonts/LXGWWenKai-Regular.ttf'
im=cv2.imread(K+'/lb.jpg').astype(np.float32)
g=im.mean(2); sat=im.max(2)-im.min(2)
X0,X1=12300,15000
gs=g[:,X0:X1]; bl=cv2.GaussianBlur(gs,(0,0),40)
def mask(T,minarea=60):
    m=(((bl-gs)>T)|(gs<85))&(sat[:,X0:X1]<60)
    m=m.astype('uint8')
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),'uint8'))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((3,3),'uint8'))
    return m
def cut(m,box,frac=0.5,minc=60):
    x1,y1,x2,y2=box; x1-=X0;x2-=X0
    H,W=m.shape;P=150
    X1_,Y1_,X2_,Y2_=max(0,x1-P),max(0,y1-P),min(W,x2+P),min(H,y2+P)
    big=m[Y1_:Y2_,X1_:X2_]
    n,lab,st,_=cv2.connectedComponentsWithStats(big,8)
    inner=lab[y1-Y1_:y2-Y1_,x1-X1_:x2-X1_]
    sub=np.zeros_like(inner,dtype='uint8')
    for i in range(1,n):
        ins=(inner==i).sum()
        if ins<minc: continue
        if ins/st[i][4]>=frac: sub[inner==i]=1
    ys,xs=np.nonzero(sub)
    if len(xs)==0: return None
    sub=sub[ys.min():ys.max()+1,xs.min():xs.max()+1]
    sub=np.pad(sub,12)
    return Image.fromarray(((1-sub)*255).astype('uint8'))
def orig(box):
    x1,y1,x2,y2=box
    return Image.fromarray(cv2.cvtColor(im[y1:y2,x1:x2].astype('uint8'),cv2.COLOR_BGR2RGB))
