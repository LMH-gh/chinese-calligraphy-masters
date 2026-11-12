import numpy as np, cv2, json, sys
from spec import S
M='/tmp/gaoxian/m.npy'
B=[218, 407, 556, 718, 850, 998, 1138, 1251, 1367, 1485, 1593, 1707, 1825, 1957, 2103, 2230, 2359, 2473, 2617, 2728, 2843, 2962, 3073, 3180, 3301, 3407, 3523, 3640, 3767, 3857, 3985, 4112, 4238, 4341, 4464, 4574, 4691, 4811, 4940, 5089, 5217, 5338, 5465, 5587, 5703, 5841, 5979, 6119, 6244, 6377, 6501, 6725]
EDGES=[0]+B   # 53 edges -> 52 bands, left to right
BANDS=[(EDGES[i],EDGES[i+1]) for i in range(52)][::-1]  # right-to-left = line order
SNAP={(48,2):300,(48,3):430,(46,4):505}
XO={}    # (line,k) -> (x1,x2) override
def boxes():
    m=np.load(M)
    out=[]
    for li,(t,_,_,ys) in enumerate(S):
        x1,x2=BANDS[li]
        r=m[:,x1:x2].sum(1).astype(float)
        r=np.convolve(r,np.ones(5)/5,'same')
        ys=list(ys)
        for k in range(1,len(ys)-1):
            if (li+1,k) in SNAP: ys[k]=SNAP[(li+1,k)]; continue
            a,b=ys[k]-15,ys[k]+16
            ys[k]=a+int(np.argmin(r[a:b]))
        for k,ch in enumerate(t):
            bx=XO.get((li+1,k),(x1,x2))
            out.append([li+1,ch,bx[0],ys[k],bx[1],ys[k+1]])
    return out
def assign(m,bxs):
    """component-based assignment; returns list of masks (full-size crops) per box"""
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    H,W=m.shape
    owner=np.full((H,W),-1,int)
    # pixel-level: box containing pixel; nearest center otherwise
    cx=np.array([(b[2]+b[4])/2 for b in bxs]); cy=np.array([(b[3]+b[5])/2 for b in bxs])
    res=[np.zeros((H,W),'uint8') for _ in bxs] if False else None
    ys,xs=np.nonzero(m)
    # inside test per box
    best=np.full(len(xs),-1); bd=np.full(len(xs),1e9)
    for i,b in enumerate(bxs):
        _,_,x1,y1,x2,y2=b
        # distance to box (0 inside) + small center term for tie-break
        dx=np.maximum(np.maximum(x1-xs,xs-x2),0); dy=np.maximum(np.maximum(y1-ys,ys-y2),0)
        d=np.hypot(dx,dy)*10+np.hypot(xs-cx[i],ys-cy[i])*0.01
        sel=d<bd; bd[sel]=d[sel]; best[sel]=i
    pl=lab[ys,xs]
    # whole-component assignment when >=65% pixels agree
    comp_owner={}
    for c in range(1,n):
        idx=np.nonzero(pl==c)[0]
        if len(idx)==0: continue
        v=np.bincount(best[idx],minlength=len(bxs)); j=int(v.argmax())
        if v[j]>=0.8*len(idx): best[idx]=j
    return xs,ys,best,bd,pl,st
