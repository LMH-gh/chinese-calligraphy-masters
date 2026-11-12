import json,sys
from hl import *
exec(open('spec.py').read())   # S: list of [line,img,x1,x2,text,cuts(optional list of y pairs or None),lowset(optional str of indices)]
R=[]
for row in S:
    ln,i,x1,x2,t=row[:5]; cuts=row[5] if len(row)>5 else None; low=row[6] if len(row)>6 else ''
    n=len(t)
    if cuts is None: cuts=split(i,x1,x2,n)
    assert len(cuts)==n,(ln,n,len(cuts))
    for k,(ch,c) in enumerate(zip(t,cuts)):
        a,b=(c if len(c)==2 else (None,c))
        bx=tight(i,[x1,a,x2,b]) if not isinstance(b,(list,tuple)) else tight(i,list(b))
        R.append([ln,ch,f'm{i:03d}.jpg']+[int(v) for v in bx]+['low' if str(k) in low.split(',') else 'ok'])
json.dump(R,open('boxes.json','w'),ensure_ascii=False)
if len(sys.argv)>1:
    for i in map(int,sys.argv[1:]):
        bs=[r[3:7]+[r[1],r[7]] for r in R if r[2]==f'm{i:03d}.jpg']
        view(i,f'/tmp/huangtingjian/o{i}a.jpg',2000,4000,0.45,bs)
        view(i,f'/tmp/huangtingjian/o{i}b.jpg',0,2100,0.45,bs)
print(len(R))
