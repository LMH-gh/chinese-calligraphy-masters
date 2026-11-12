# 续标 p-009 起：按页分列 + 每列 DP 切字，输出 boxes_auto2.json
import numpy as np, json, sys
sys.path.insert(0,'.')
from dp2 import dp2 as dp
T='/tmp/hezhizhang/'
L=[l.strip() for l in open('lines.txt',encoding='utf8')]
def page_lines(p):
    if p==31: return [138,139,140]
    s=28+5*(p-9); return list(range(s,s+5))
def mask(i):
    m=np.load(T+'m%d.npy'%i).copy(); m[3030:]=0; m[:,1440:]=0; m[:,:100]=0; return m
import cv2
def cols(i,n):
    """斜切分列：搜索剪切角 s 使列间空白最深；按连通域质心归列。返回 (m, [(colmask,x1,x2),...]) 右→左"""
    m=mask(i); H,W=m.shape
    ys,xs=np.nonzero(m)
    best=None
    for s in np.linspace(-0.08,0.08,41):
        xp=xs-s*(ys-1500)
        p=np.bincount(np.clip(xp,0,W-1).astype(int),minlength=W).astype(float)
        p=np.convolve(p,np.ones(31)/31,'same')
        lo,hi=int(np.percentile(xp,1))+80,int(np.percentile(xp,99))-80
        cand=[x for x in range(lo,hi) if p[x]==p[max(0,x-40):x+41].min()]
        cand=sorted(cand,key=lambda x:p[x]); g=[]
        for x in cand:
            if all(abs(x-y)>150 for y in g): g.append(x)
            if len(g)==n-1: break
        if len(g)<n-1: continue
        sc=sum(p[x] for x in g)
        if best is None or sc<best[0]: best=(sc,s,sorted(g))
    _,s,g=best
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    cx=cen[:,0]-s*(cen[:,1]-1500)
    e=[10**9]+g[::-1]+[-10**9]
    out=[]
    for k in range(n):
        ids=np.nonzero((cx<e[k])&(cx>=e[k+1]))[0]; ids=ids[ids>0]
        cm=np.isin(lab,ids).astype(np.uint8)
        xx=np.nonzero(cm.sum(0))[0]
        out.append((cm,int(xx.min()) if len(xx) else 0,int(xx.max())+1 if len(xx) else 1))
    return m,out
OVR={}  # (page,line)->(x1,x2) 手工列界
YR={}   # line->(y0,y1) 手工纵向范围
PINS={}  # line->{k:y}
LOW={}  # line->[0-based idx] 标 low
SKIP={}
NOBOX=set()  # 这些行的 々 是附在字旁的小点，不单独出框
exec(open('fix2.py',encoding='utf8').read()) if __import__('os').path.exists('fix2.py') else None
def toprule(m):
    """页顶乌丝栏残线：y 60~330 内第一段 cov>0.35 的薄行带（厚≤25，其下 10 行几乎无墨），返回其下沿+10；否则 120"""
    cov=m[:,100:1420].reshape(m.shape[0],33,40).max(2).mean(1)
    r=[y for y in np.nonzero(cov[:330]>0.3)[0] if y>=60]
    if not r: return 120
    e=r[0]
    for y in r[1:]:
        if y-e<=4: e=y
        else: break
    if e-r[0]<=25 and cov[e+6:e+16].max()<0.2: return int(e)+14
    return 120
def run(pages):
    boxes=[]
    for i in pages:
        ls=page_lines(i); m,cs=cols(i,len(ls)); TOP=toprule(m)
        for ln,(cm,x1,x2) in zip(ls,cs):
            if ln in OVR: x1,x2=OVR[ln]; cm=m.copy(); cm[:,:x1]=0; cm[:,x2:]=0
            sub=cm[:,x1:x2]; r=sub.sum(1).astype(float)
            rs=np.convolve(r,np.ones(9),"same"); rs[:TOP]=0; yy=np.nonzero(rs>60)[0]; y0,y1=yy.min(),yy.max()
            a,b=YR.get(ln,(None,None)); y0=a or y0; y1=b or y1
            txt=L[ln-1]
            if ln in NOBOX: txt=txt.replace('々','')
            cuts=dp(r,len(txt),y0,y1,pins=PINS.get(ln))
            for k,ch in enumerate(txt):
                a,b=cuts[k],cuts[k+1]
                s=sub[a:b]; xs=np.nonzero(s.sum(0))[0]; ys_=np.nonzero(s.sum(1))[0]
                bx=[int(x1+xs.min()) if len(xs) else x1, int(a+ys_.min()) if len(ys_) else int(a), int(x1+xs.max()+1) if len(xs) else x2, int(a+ys_.max()+1) if len(ys_) else int(b)]
                boxes.append([ln,ch,'p-%03d.jpg'%i,*bx,'skip' if k in SKIP.get(ln,[]) else ('low' if k in LOW.get(ln,[]) else 'ok')])
    return boxes
if __name__=='__main__':
    pages=[int(x) for x in sys.argv[1].split(',')]
    b=run(pages); json.dump(b,open(sys.argv[2],'w'),ensure_ascii=False); print(len(b))
