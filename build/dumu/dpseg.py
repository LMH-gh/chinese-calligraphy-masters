import numpy as np
def dp(r,N,y0,y1,step=4):
    ink=r>2
    ys=list(range(y0,y1+2,step)); K=len(ys)
    nxt=np.full(len(r)+2,10**9); prv=np.full(len(r)+2,-1)
    last=10**9
    for y in range(len(r)-1,-1,-1):
        if ink[y]: last=y
        nxt[y]=last
    last=-1
    for y in range(len(r)):
        if ink[y]: last=y
        prv[y]=last
    # expected height: total ink extent minus gaps >40px
    gaps=0;run=0
    for y in range(y0,y1):
        if not ink[y]: run+=1
        else:
            if run>40: gaps+=run
            run=0
    H=(y1-y0-gaps)/N
    c=np.array([r[max(0,y-3):y+4].sum() for y in ys])
    INF=1e18; f=np.full((N+1,K),INF); bk=np.zeros((N+1,K),int); f[0][0]=0
    rm=r.mean()
    for k in range(1,N+1):
        for j in range(1,K):
            best=INF;bj=-1
            for jj in range(j):
                if f[k-1][jj]>=INF: continue
                a,b=ys[jj],ys[j]
                t=nxt[a]; u=prv[min(b,len(r)-1)]
                h=u-t if (t<b and u>=a) else 0
                if h<0.25*H or h>2.0*H: continue
                v=f[k-1][jj]+(c[j] if k<N else 0)+30*rm*((h-H)/H)**2
                if v<best: best=v;bj=jj
            f[k][j]=best;bk[k][j]=bj
    j=K-1; cuts=[ys[j]]
    for k in range(N,0,-1):
        j=bk[k][j]; cuts.append(ys[j])
    return cuts[::-1]
