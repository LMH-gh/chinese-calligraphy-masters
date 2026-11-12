import numpy as np, cv2, functools, sys
from PIL import Image, ImageDraw, ImageFont
Image.MAX_IMAGE_PIXELS=None
T='/tmp/huangtingjian'
F='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244/fonts/LXGWWenKai-Regular.ttf'
def path(i): return f'{T}/m{i:03d}.jpg'
TH={10:20}
@functools.lru_cache(None)
def mask(i):
    a=np.asarray(Image.open(path(i)).convert('RGB')).astype(np.float32)
    g=a.mean(2); sat=a.max(2)-a.min(2)
    bl=cv2.GaussianBlur(g,(0,0),40)
    th=TH.get(i,30)
    m=(((bl-g)>th)|(g<90))&(sat<60)
    # restrict to paper band
    col=g[:,1000:3000].mean(1); ys=np.where(col>120)[0]
    m[:ys.min()+15]=0; m[ys.max()-15:]=0
    m=m.astype('uint8')
    return cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),'uint8'))
def cols(i,minw=40,th=3):
    m=mask(i); p=m.sum(0)
    on=p>th; out=[];s=None
    for x,v in enumerate(on):
        if v and s is None: s=x
        if not v and s is not None:
            if x-s>=minw: out.append((s,x))
            s=None
    return out
def view(i,out,x1=0,x2=4000,scale=0.4,boxes=None,marks=None):
    im=Image.open(path(i)).convert('RGB').crop((x1,700,x2,2240))
    d=ImageDraw.Draw(im); f=ImageFont.truetype(F,40)
    for x in range((x1//100+1)*100,x2,100):
        big=x%500==0
        d.line([(x-x1,0),(x-x1,40 if not big else 80)],fill=(255,0,0),width=3)
        if big: d.text((x-x1+4,40),str(x),fill=(255,0,0),font=f)
    for y in range(800,2240,100):
        d.line([(0,y-700),(30,y-700)],fill=(0,0,255),width=3)
        if y%500==0: d.text((32,y-720),str(y),fill=(0,0,255),font=f)
    if boxes:
        for k,b in enumerate(boxes):
            c=(0,160,0) if (len(b)<6 or b[5]=='ok') else (255,0,255)
            d.rectangle([b[0]-x1,b[1]-700,b[2]-x1,b[3]-700],outline=c,width=4)
            if len(b)>4: d.text((b[2]-x1+3,b[1]-700),str(b[4]),fill=(0,0,200),font=f)
    im.resize((int(im.width*scale),int(im.height*scale))).save(out)

def split(i,x1,x2,n,y1=None,y2=None):
    m=mask(i)[:,x1:x2]
    r=m.sum(1).astype(float)
    ys=np.nonzero(r>2)[0]
    Y1=y1 if y1 else int(ys.min()); Y2=y2 if y2 else int(ys.max())+1
    if n==1: return [(Y1,Y2)]
    s=5; prof=r[Y1:Y2]; L=len(prof)//s
    cost=np.array([prof[k*s:(k+1)*s].sum() for k in range(L)])
    cost=np.convolve(cost,np.ones(3)/3,'same')
    mean=L/n; lam=cost.max()/ (mean*mean) *0.6 if cost.max()>0 else 1
    INF=1e18
    D=np.full((n+1,L+1),INF); P=np.zeros((n+1,L+1),int); D[0][0]=0
    for k in range(1,n+1):
        for e in range(1,L+1):
            best=INF;bp=0
            for b in range(max(0,e-int(mean*2.2)),e-max(1,int(mean*0.3))+1):
                if D[k-1][b]>=INF: continue
                c=D[k-1][b]+lam*(e-b-mean)**2+(cost[e-1] if k<n else 0)
                if c<best: best=c;bp=b
            D[k][e]=best;P[k][e]=bp
    cuts=[];e=L
    for k in range(n,0,-1):
        b=P[k][e]; cuts.append((Y1+b*s,Y1+e*s)); e=b
    cuts=cuts[::-1]; cuts[-1]=(cuts[-1][0],Y2)
    return cuts
def tight(i,b,P=60):
    m=mask(i); H,W=m.shape; x1,y1,x2,y2=b
    X1,Y1,X2,Y2=max(0,x1-P),max(0,y1-P),min(W,x2+P),min(H,y2+P)
    big=m[Y1:Y2,X1:X2]; n,lab,st,_=cv2.connectedComponentsWithStats(big,8)
    inner=np.zeros_like(lab); inner[y1-Y1:y2-Y1,x1-X1:x2-X1]=1
    keep=np.zeros_like(big)
    for k in range(1,n):
        a=st[k][4]; ins=((lab==k)&(inner==1)).sum()
        if ins<60 or ins/a<0.3: continue
        keep[(lab==k)&(inner==1)]=1
    ys,xs=np.nonzero(keep)
    if len(xs)==0: return list(b)
    return [int(xs.min()+X1-4),int(ys.min()+Y1-4),int(xs.max()+X1+4),int(ys.max()+Y1+4)]
