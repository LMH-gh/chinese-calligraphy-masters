import numpy as np, json, sys, cv2
from dp2 import dp2
from spec import WOVER, CUTS, MAN
from spec import COLS, LOW
M=np.load('/tmp/dumu/mask.npy')
def tight(b,P=80):
    x1,y1,x2,y2=b; H,W=M.shape
    X1,Y1,X2,Y2=max(0,x1-P),max(0,y1-P),min(W,x2+P),min(H,y2+P)
    big=M[Y1:Y2,X1:X2]; n,lab,st,_=cv2.connectedComponentsWithStats(big,8)
    inner=np.zeros(big.shape,bool); inner[y1-Y1:y2-Y1,x1-X1:x2-X1]=True
    xs=[];ys=[]
    for i in range(1,n):
        a=st[i][4]
        if a<40: continue
        ins=((lab==i)&inner).sum()
        if ins<40 or ins/a<0.5: continue
        l,t,w,h=st[i][:4]; xs+= [l,l+w]; ys+=[t,t+h]
    if not xs: return b
    return [int(min(xs)+X1-3),int(min(ys)+Y1-3),int(max(xs)+X1+3),int(max(ys)+Y1+3)]
MANUAL=json.load(open('manual.json')) if __import__('os').path.exists('manual.json') else {}
out=[]
for ln,x1,x2,t in COLS:
    if str(ln) in MANUAL:
        for k,(ch,b,conf) in enumerate(MANUAL[str(ln)]):
            out.append([ln,ch,'zh.jpg',*b,conf,k]); 
        continue
    if ln in MAN:
        for k,(ch,(xr,ya,yb)) in enumerate(zip(t,MAN[ln])):
            xa,xb=xr if xr else (x1,x2)
            out.append([ln,ch,'zh.jpg',*tight([xa,ya,xb,yb]),'low' if (ln,k) in LOW else 'ok',k,[xa,ya,xb,yb]])
        continue
    sub=M[:,x1:x2]; r=sub.sum(1).astype(float)
    rs=np.convolve(r,np.ones(9),'same'); yy=np.nonzero(rs>40)[0]; y0,y1=int(yy.min()),int(yy.max())
    cuts=CUTS[ln] if ln in CUTS else dp2(r,t,y0,y1,wover=WOVER.get(ln))
    for k,ch in enumerate(t):
        b=tight([x1,cuts[k],x2,cuts[k+1]])
        out.append([ln,ch,'zh.jpg',*b,'low' if (ln,k) in LOW else 'ok',k,[x1,cuts[k],x2,cuts[k+1]]])
json.dump(out,open('boxes_raw.json','w'),ensure_ascii=False)
print(len(out))
