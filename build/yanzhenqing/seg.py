import numpy as np,cv2,json,sys
from PIL import Image,ImageDraw,ImageFont
Image.MAX_IMAGE_PIXELS=None
F='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244/fonts/LXGWWenKai-Regular.ttf'
M=np.load('/tmp/yanzhenqing/mask.npy')
def prof(x1,x2,y1,y2,step=20):
    r=M[y1:y2,x1:x2].sum(1)
    return ' '.join(f"{y1+y}:{r[y:y+step].sum()//step}" for y in range(0,len(r),step))
def tight(b,P=60):
    x1,y1,x2,y2=b; H,W=M.shape
    X1,Y1,X2,Y2=max(0,x1-P),max(0,y1-P),min(W,x2+P),min(H,y2+P)
    big=M[Y1:Y2,X1:X2]; n,lab,st,_=cv2.connectedComponentsWithStats(big,8)
    inner=lab[y1-Y1:y2-Y1,x1-X1:x2-X1]
    keep=np.zeros_like(inner,dtype=bool)
    for i in range(1,n):
        a=st[i][4]; ins=(inner==i).sum()
        if ins<80 or ins/a<0.25: continue
        keep|=(inner==i)
    ys,xs=np.nonzero(keep)
    if len(xs)==0: return list(b)
    return [int(x1+xs.min()-4),int(y1+ys.min()-4),int(x1+xs.max()+4),int(y1+ys.max()+4)]
def overlay(boxes,x1,y1,x2,y2,out,scale=0.2):
    im=Image.open('/tmp/yanzhenqing/yzq.png').convert('RGB').crop((x1,y1,x2,y2))
    d=ImageDraw.Draw(im); f=ImageFont.truetype(F,int(60))
    for k,b in enumerate(boxes):
        ln,ch=b[0],b[1]; bx=b[3:7]
        col=(255,0,0) if b[7]=='ok' else (0,0,255)
        d.rectangle([bx[0]-x1,bx[1]-y1,bx[2]-x1,bx[3]-y1],outline=col,width=8)
        d.text((bx[0]-x1-70,bx[1]-y1),ch,fill=(0,140,0),font=f)
    im.resize((int(im.width*scale),int(im.height*scale))).save(out)

def band_prof(xa,xb,hw,y1,y2):
    p=np.zeros(y2-y1)
    for y in range(y1,y2):
        xc=int(xa+(xb-xa)*(y-y1)/max(1,y2-y1))
        p[y-y1]=M[y,xc-hw:xc+hw].sum()
    k=np.ones(15)/15
    return np.convolve(p,k,'same')
def dp_cuts(p,n,alpha=3.0,step=5,w=None):
    # choose n-1 cuts; segment cost = alpha*mean_ink*((len-L)/L)^2 ; cut cost = p[c]
    N=len(p); L=N/n; idx=list(range(0,N,step))+[N]
    mi=p.mean()+1e-6
    INF=1e18
    # dp over positions in idx
    P=len(idx); best=[[INF]*P for _ in range(n+1)]; arg=[[-1]*P for _ in range(n+1)]
    best[0][0]=0
    wl=w or [1]*n
    for k in range(1,n+1):
        Lk=L*wl[k-1]*n/sum(wl)
        for j in range(1,P):
            cc=0 if j==P-1 else p[idx[j]]
            for i in range(max(0,j-int(3*Lk/step)),j):
                if best[k-1][i]>=INF: continue
                ln=idx[j]-idx[i]
                c=best[k-1][i]+cc+alpha*mi*((ln-Lk)/Lk)**2
                if c<best[k][j]: best[k][j]=c; arg[k][j]=i
    cuts=[]; j=P-1
    for k in range(n,0,-1):
        i=arg[k][j]; cuts.append(idx[i]); j=i
    return sorted(cuts)[1:]
def auto(ln,ch,xa,xb,hw,y1,y2,alpha=3.0,w=None,src='yzq'):
    p=band_prof(xa,xb,hw,y1,y2)
    cuts=[0]+dp_cuts(p,len(ch),alpha,w=w)+[y2-y1]
    out=[]
    for k,c in enumerate(ch):
        ya,yb=y1+cuts[k],y1+cuts[k+1]
        xm=int(xa+(xb-xa)*((ya+yb)/2-y1)/(y2-y1))
        out.append([ln,c,src]+tight([xm-hw,ya,xm+hw,yb])+['ok'])
    return out
