import numpy as np, json, sys
sys.path.insert(0,'..')
T='/tmp/hezhizhang/'
L=[l.strip() for l in open('lines.txt',encoding='utf8')]
PAGES={3:[1,2],4:[3,4,5,6,7],5:[8,9,10,11,12],6:[13,14,15,16,17],7:[18,19,20,21,22],8:[23,24,25,26,27]}
def cols(i):
    m=np.load(T+'m%d.npy'%i); m[3030:]=0; m[:,1440:]=0; m[:,:100]=0
    if i==3: return m,[(434,640),(170,400)]
    p=np.convolve(m.sum(0),np.ones(31)/31,'same')
    mins=[x for x in range(300,1260) if p[x]==p[x-40:x+41].min() and p[x]<100]
    out=[]
    for x in mins:
        if not out or x-out[-1]>60: out.append(x)
    assert len(out)==4,(i,out)
    e=[1450]+out[::-1]+[100]
    return m,[(e[k+1],e[k]) for k in range(5)]
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
if __name__=='__main__':
    boxes=[]
    for i,ls in PAGES.items():
        m,cs=cols(i)
        for ln,(x1,x2) in zip(ls,cs):
            sub=m[:,x1:x2]; r=sub.sum(1).astype(float)
            rs=np.convolve(r,np.ones(9),"same"); yy=np.nonzero(rs>60)[0]; y0,y1=yy.min(),yy.max()
            txt=L[ln-1]; cuts=dp(r,len(txt),y0,y1)
            for k,ch in enumerate(txt):
                a,b=cuts[k],cuts[k+1]
                s=sub[a:b]; xs=np.nonzero(s.sum(0))[0]
                ys_=np.nonzero(s.sum(1))[0]
                bx=[int(x1+xs.min()) if len(xs) else x1, int(a+ys_.min()) if len(ys_) else int(a), int(x1+xs.max()+1) if len(xs) else x2, int(a+ys_.max()+1) if len(ys_) else int(b)]
                boxes.append([ln,ch,'p-%03d.jpg'%i,*bx,'ok'])
    json.dump(boxes,open('boxes_auto.json','w'),ensure_ascii=False)
    print(len(boxes))
