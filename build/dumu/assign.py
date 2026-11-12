# 由 boxes_raw 的槽位（列宽×切点）按连通域多数归属生成每字墨迹，避免邻字笔画重复
import numpy as np, json, cv2
from spec import COLS, CUTS, MAN
M=np.load('/tmp/dumu/mask.npy')
def slots_for(ln, raw):
    """返回该列 [(token_idx, ch, rect, conf)]，rect 为槽位矩形（非 tight 框）"""
    _,x1,x2,t=COLS[ln-1]
    return [(r[8],r[1],r[9],r[7]) for r in raw if r[0]==ln]
def assign(ln, slots, P=120, minfrac=0.4):
    _,x1,x2,t=COLS[ln-1]; H,W=M.shape
    X1,X2=max(0,x1-P),min(W,x2+P)
    sub=M[:,X1:X2]; n,lab,st,_=cv2.connectedComponentsWithStats(sub,8)
    res={}
    cnt=np.zeros((n,len(slots)))
    for j,(k,ch,(a,b,c,d),conf) in enumerate(slots):
        l=lab[b:d,a-X1:c-X1]; cnt[:,j]=np.bincount(l.ravel(),minlength=n)
    area=st[:,4]
    best=cnt.argmax(1); frac=cnt.max(1)/np.maximum(area,1)
    out=[]
    for j,(k,ch,rect,conf) in enumerate(slots):
        ids=[i for i in range(1,n) if best[i]==j and frac[i]>=minfrac and area[i]>=40]
        if not ids: out.append((k,ch,None,None,conf)); continue
        m=np.isin(lab,ids)
        ys,xs=np.nonzero(m); y0,y1_,x0,x1_=ys.min(),ys.max()+1,xs.min(),xs.max()+1
        crop=m[y0:y1_,x0:x1_]
        out.append((k,ch,[int(x0+X1),int(y0),int(x1_+X1),int(y1_)],crop,conf))
    return out
