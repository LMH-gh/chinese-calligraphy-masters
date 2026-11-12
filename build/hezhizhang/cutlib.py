import json,os,sys,shutil,numpy as np,cv2
from PIL import Image,ImageOps
sys.path.insert(0,'..')
from cut import cut,sheet
ROOT='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244'
OUT=ROOT+'/data/masters/草-贺知章'; REV=ROOT+'/data/masters/_review/草-贺知章'
SRC='孝经'
for d in (OUT,REV):
    if os.path.exists(d): shutil.rmtree(d)
    os.makedirs(d)
B=json.load(open('boxes.json'))
M={}
def mask(pg):
    i=int(pg[2:5])
    if i not in M:
        m=np.load('/tmp/hezhizhang/m%d.npy'%i).copy(); m[3030:]=0; m[:,1440:]=0; m[:,:100]=0
        M[i]=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),'uint8'))
    return M[i]
items=[]
for n,b in enumerate(B):
    ln,ch,pg,x1,y1,x2,y2,conf=b
    if conf=='skip': continue
    if n in (47,210): conf='low'  # 对照表目检：字形/字界存疑
    im=cut(mask(pg),[x1,y1,x2,y2])
    ink=0 if im is None else int((np.asarray(im)<128).sum())
    items.append(dict(n=n,ln=ln,ch=ch,pg=pg,box=[x1,y1,x2,y2],conf=conf,im=im,ink=ink))
med=float(np.median([it['ink'] for it in items if it['conf']=='ok']))
KEEP={c['seq'] for c in json.load(open('chars_v1_27.json')) if c['conf']=='ok'}  # 1–27 行已人工校过的 ok 字不再按墨量降级
chars=[]
for it in items:
    note=None
    if it['conf']=='ok' and it['ink']<0.35*med and it['n'] not in KEEP: it['conf']='low'; note='墨量低于ok中位数35%，自动降为low'
    if it['im'] is None: it['conf']='low'; note='切图为空'
    fn='%s_%04d.png'%(SRC,it['n'])
    base=OUT if it['conf']=='ok' else REV
    os.makedirs(base+'/'+it['ch'],exist_ok=True)
    if it['im'] is not None:
        ImageOps.expand(it['im'],12,fill=255).save(base+'/'+it['ch']+'/'+fn)
    rel=it['ch']+'/'+fn if it['conf']=='ok' else '../_review/草-贺知章/'+it['ch']+'/'+fn
    c=dict(char=it['ch'],file=rel,source=SRC,line=it['ln'],seq=it['n'],image=it['pg'],box=it['box'],conf=it['conf'])
    if note: c['note']=note
    chars.append(c)
json.dump(dict(items=None),open('/dev/null','w'))
json.dump(chars,open('chars.json','w'),ensure_ascii=False)
ok=[c for c in chars if c['conf']=='ok']
print('total',len(chars),'ok',len(ok),'distinct',len(set(c['char'] for c in chars)),'distinct_ok',len(set(c['char'] for c in ok)),'med',med)
sheet([(('' if it['conf']=='ok' else '?')+it['ch']+str(it['n']),it['im']) for it in items],ROOT+'/shufa/output/字库_贺知章.jpg',cell=150,cols=20)
