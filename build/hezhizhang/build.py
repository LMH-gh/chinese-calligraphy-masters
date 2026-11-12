import json,numpy as np,sys
sys.path.insert(0,'.')
from seg import dp
T='/tmp/hezhizhang/'
A=json.load(open('boxes_auto_v1.json'))
L=[l.strip() for l in open('lines.txt',encoding='utf8') if l.strip()]
M={}
def mask(pg):
    i=int(pg[2:5])
    if i not in M:
        m=np.load(T+'m%d.npy'%i).copy(); m[3030:]=0; m[:,1440:]=0; m[:,:100]=0; M[i]=m
    return M[i]
def union(ids):
    bs=[A[i] for i in ids]
    return [bs[0][2],min(b[3] for b in bs),min(b[4] for b in bs),max(b[5] for b in bs),max(b[6] for b in bs)]
def tight(pg,x1,y1,x2,y2):
    s=mask(pg)[y1:y2,x1:x2]; ys=np.nonzero(s.sum(1))[0]; xs=np.nonzero(s.sum(0))[0]
    if len(xs)==0: return [x1,y1,x2,y2]
    return [int(x1+xs.min()),int(y1+ys.min()),int(x1+xs.max()+1),int(y1+ys.max()+1)]
def gapy(pg,b,lo=0.15,hi=0.85):
    x1,y1,x2,y2=b; r=mask(pg)[y1:y2,x1:x2].sum(1).astype(float)
    r=np.convolve(r,np.ones(7)/7,'same'); n=len(r); a,c=int(n*lo),int(n*hi)
    # prefer longest zero run, else minimum
    j=a+int(np.argmin(r[a:c])); return y1+j
def regions(spec_tok):
    pass
SPEC={}
def S(line,toks): SPEC[line]=toks
# token: (char, kind, arg, conf)  kinds: 'a' ids list ; 'top'/'bot' (ids, y or None) ; 'dp' handled separately
S(1,{2:'low',3:'low'})
S(2,{16:'low',19:'low'})
S(4,[('乎','a',[37]),('曾','a',[38]),('子','a',[39]),('避','a',[40]),('席','a',[41,42]),('曰','a',[43]),('参','a',[44]),('不','a',[45]),('敏','a',[46]),('何','a',[47]),('足','top',([48],None)),('以','bot',([48],None)),('知','a',[49]),('之','a',[50]),('子','a',[51])])
S(6,[('吾','a',[67]),('语','a',[68]),('汝','a',[69]),('身','a',[70],'low'),('体','a',[71],'low'),('发','a',[72,73],'low'),('肤','a',[74],'low'),('受','a',[75],'low'),('之','a',[76],'low'),('父','a',[77]),('母','a',[78]),('不','top',([79],None),'low'),('敢','bot',([79],None))])
S(15,[(c,'a',[i]) for c,i in zip('在上不骄高而不危制',range(190,199))]+[('节','a',[199,200]),('谨','a',[201]),('度','a',[202]),('满','a',[203]),('而','top',([204],None),'low'),('不','bot',([204],None),'low')])
S(16,[(c,'a',[i]) for c,i in zip('溢高而不危',range(206,211))]+[('所','top',([211],None)),('以','bot',([211],None),'low')]+[(c,'a',[i]) for c,i in zip('长守贵也满而不溢',range(212,220))])
S(17,[('所','top',([220],None),'low'),('以','top',([220],None),'low'),('长','bot',([220],None)),('守','a',[221]),('富','a',[222],'low'),('也','a',[223],'low'),('富','a',[224,225],'low'),('贵','a',[226]),('不','a',[227]),('离','a',[228]),('其','a',[229,230],'low'),('身','a',[231],'low'),('然','a',[232]),('后','a',[233]),('能','a',[234]),('保','a',[235])])
S(19,[('也','a',[249]),('诗','a',[250]),('云','a',[251]),('战','a',[252],'low'),('々','a',[253],'skip'),('兢','a',[254]),('々','top',([255],None),'skip'),('如','bot',([255],None)),('临','a',[256]),('深','a',[257]),('渊','a',[258]),('如','a',[259]),('履','a',[260]),('薄','a',[261,262]),('冰','a',[263])])
S(20,[('卿','a',[264]),('大','a',[265],'low'),('夫','a',[266],'low'),('章','a',[267],'low'),('第','a',[268,269],'low'),('四','a',[270])]+[('DP','非先王之法服不',list(range(271,277)))])
S(22,[(c,'a',[i]) for c,i in zip('德行不敢',range(292,296))]+[('行','a',[296,297],'low'),('是','a',[298]),('故','a',[299]),('非','a',[300]),('法','a',[301]),('不','a',[302],'low'),('言','a',[303],'low'),('非','a',[304]),('道','top',([305],None)),('不','bot',([305],None))])
S(23,[(c,'a',[i]) for c,i in zip('行口无择言',range(306,311))]+[('身','a',[311],'low'),('无','a',[312]),('择','a',[313]),('行','a',[314]),('满','a',[315],'low'),('言','a',[316],'low'),('天','a',[317]),('下','top',([318,319],None)),('无','bot',([318,319],None))])
S(24,[('口','top',([320],None),'low'),('过','bot',([320],None),'low')]+[(c,'a',[i]) for c,i in zip('行满天下无怨恶',range(321,328))]+[('三','a',[328,329])]+[(c,'a',[i]) for c,i in zip('者备矣然后',range(330,335))])
S(25,[(c,'a',[i]) for c,i in zip('能守其宗',range(335,339))]+[('庙','a',[339,340])]+[(c,'a',[i]) for c,i in zip('盖卿大夫之孝也',range(341,348))]+[('诗','top',([348],None),'low'),('云','bot',([348],None),'low')])
S(26,[(c,'a',[i]) for c,i in zip('夙夜匪懈以',range(349,354))]+[('事','top',([354],None)),('一','bot',([354],None))]+[('人','a',[355]),('士','a',[356]),('章','a',[357,358]),('第','a',[359]),('五','a',[360])])
S(27,[(c,'a',[i]) for c,i in zip('资于事父以事母而爱',range(361,370))]+[('同','a',[370,371]),('资','a',[372,373]),('于','a',[374]),('事','a',[375],'low'),('父','a',[376],'low'),('以','a',[377],'low')])
out=[]
for ln in range(1,len(L)+1):
    ids=[i for i,b in enumerate(A) if b[0]==ln]
    sp=SPEC.get(ln)
    if sp is None or isinstance(sp,dict):
        sp=sp or {}
        for i in ids:
            b=A[i]; out.append([ln,b[1],b[2],*b[3:7],sp.get(i,'ok')])
        continue
    for t in sp:
        if t[0]=='DP':
            _,txt,dids=t; u=union(dids); pg=u[0]; x1,y1,x2,y2=u[1:]
            r=mask(pg)[:,x1:x2].sum(1).astype(float)
            cuts=dp(r,len(txt),y1,y2)
            for k,ch in enumerate(txt):
                out.append([ln,ch,pg,*tight(pg,x1,cuts[k],x2,cuts[k+1]),'ok'])
            continue
        ch,kind,arg=t[:3]; conf=t[3] if len(t)>3 else 'ok'
        if kind=='a':
            u=union(arg); out.append([ln,ch,u[0],*tight(u[0],*u[1:]),conf])
        else:
            ids2,y=arg; u=union(ids2); pg=u[0]; b=u[1:]
            if y is None: y=gapy(pg,b)
            bb=[b[0],b[1],b[2],y] if kind=='top' else [b[0],y,b[2],b[3]]
            out.append([ln,ch,pg,*tight(pg,*bb),conf])
# check order vs lines
txt=''.join(L); got=''.join(b[1] for b in out)
assert txt==got,(len(txt),len(got),[ (i,a,b) for i,(a,b) in enumerate(zip(txt,got)) if a!=b][:5])
json.dump(out,open('boxes.json','w'),ensure_ascii=False,indent=0)
print(len(out),sum(b[7]=='ok' for b in out))
