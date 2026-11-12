import numpy as np
WD={'々':.3,'一':.3,'二':.5,'三':.55,'×':.4,'十':.8,'之':.75,'小':.6}
def dp2(r,toks,y0,y1,step=4,wover=None,A=1.0,Bc=3.0):
    N=len(toks); w=np.array([ (wover or {}).get(k, WD.get(t,1.0)) for k,t in enumerate(toks)])
    ink=r>2
    ys=np.arange(y0,y1+step,step); K=len(ys)
    n=len(r)
    nxt=np.full(n+1,10**9); prv=np.full(n+1,-1); last=10**9
    for y in range(n-1,-1,-1):
        if ink[y]: last=y
        nxt[y]=last
    last=-1
    for y in range(n):
        if ink[y]: last=y
        prv[y]=last
    tot=ink[y0:y1].sum()  # inked rows
    H=tot/ w.sum()
    rm=max(r[y0:y1].mean(),1)
    c=np.array([r[max(0,y-3):y+4].sum()/7/rm for y in ys])
    T=nxt[np.minimum(ys,n-1)]
    # ink rows between ys[a],ys[b]
    cs=np.concatenate([[0],np.cumsum(ink)])
    INF=1e18; f=np.full((N+1,K),INF); bk=np.zeros((N+1,K),int); f[0][0]=0
    yi=np.minimum(ys,n)
    for k in range(1,N+1):
        Hk=H*w[k-1]
        for j in range(1,K):
            prevf=f[k-1][:j]
            h=(cs[yi[j]]-cs[yi[:j]]).astype(float)
            pen=A*((h-Hk)/H)**2*4
            v=prevf+pen+(Bc*c[j] if k<N else 0)
            jj=int(np.argmin(v)); f[k][j]=v[jj]; bk[k][j]=jj
    j=K-1; cuts=[int(ys[j])]
    for k in range(N,0,-1):
        j=bk[k][j]; cuts.append(int(ys[j]))
    return cuts[::-1]
