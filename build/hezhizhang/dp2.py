import numpy as np
def dp2(r,N,y0,y1,step=4,wcut=3.0,whgt=30.0,pins=None):
    """r: 行墨量; 把 [y0,y1] 切成 N 段。pins: {k: y} 强制第 k 条切线(1..N-1)落在 y 附近(±12)。"""
    ink=r>2; n=len(r)
    ys=np.arange(y0,y1+2,step); K=len(ys)
    nxt=np.full(n+1,10**9); prv=np.full(n+1,-1); last=10**9
    for y in range(n-1,-1,-1):
        if ink[y]: last=y
        nxt[y]=last
    last=-1
    for y in range(n):
        if ink[y]: last=y
        prv[y]=last
    gaps=0;run=0
    for y in range(y0,y1):
        if not ink[y]: run+=1
        else:
            if run>40: gaps+=run
            run=0
    H=(y1-y0-gaps)/N; rm=r[y0:y1].mean()
    c=np.array([r[max(0,y-3):y+4].sum() for y in ys])*wcut
    t=nxt[np.minimum(ys,n)]; u=prv[np.minimum(ys,n-1)]
    A=t[:,None]; Bu=u[None,:]
    h=np.where((A<ys[None,:])&(Bu>=ys[:,None]),Bu-A,0).astype(float)
    pen=whgt*rm*((h-H)/H)**2
    lo_,hi_=(0.08,3.5) if pins else (0.25,2.2)
    valid=(h>=lo_*H)&(h<=hi_*H)&(ys[None,:]>ys[:,None])
    pen=np.where(valid,pen,np.inf)
    f=np.full(K,np.inf); f[0]=0; bks=[]
    for k in range(1,N+1):
        tot=f[:,None]+pen
        bj=np.argmin(tot,0); g=tot[bj,np.arange(K)]
        if k<N:
            g=g+c
            if pins and k in pins:
                g=np.where(np.abs(ys-pins[k])<=12,g,np.inf)
        f=g; bks.append(bj)
    j=K-1; cuts=[int(ys[j])]
    for k in range(N,0,-1):
        j=bks[k-1][j]; cuts.append(int(ys[j]))
    return cuts[::-1]
