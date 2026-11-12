import json, os, shutil, sys, numpy as np
from PIL import Image
sys.path.insert(0,'..')
from cut import sheet
from spec import COLS
from assign import assign
ROOT='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244'
LIB=ROOT+'/data/masters/行-杜牧'; REV=ROOT+'/data/masters/_review/行-杜牧'
W='张好好诗'
raw=json.load(open('boxes_raw.json'))
recs=[]
for ln,x1,x2,t in COLS:
    slots=[(r[8],r[1],r[9],r[7]) for r in raw if r[0]==ln]
    assert len(slots)==len(t),(ln,len(slots),len(t))
    for k,ch,box,crop,conf in assign(ln,slots):
        if ch in '々×': continue
        recs.append(dict(line=ln,ch=ch,box=box,crop=crop,conf=conf if box else 'low'))
# lines.txt (cut chars only, in order)
lines={}
for r in recs: lines.setdefault(r['line'],'');lines[r['line']]+=r['ch']
open('lines.txt','w').write('\n'.join(lines[i] for i in sorted(lines))+'\n')
ink=[int(r['crop'].sum()) if r['crop'] is not None else 0 for r in recs]
med=np.median([i for i,r in zip(ink,recs) if r['conf']=='ok'])
for i,r in zip(ink,recs):
    r['ink']=i
    if i<0.35*med and r['conf']=='ok': r['conf']='low'; r['why']='ink<35%median'
for d in (LIB,REV):
    if os.path.exists(d): shutil.rmtree(d)
os.makedirs(LIB); os.makedirs(REV)
items=[]; chars=[]; boxes=[]
for s,r in enumerate(recs):
    ch=r['ch']; fn=f'{W}_{s:04d}.png'
    if r['crop'] is None: img=None
    else:
        c=r['crop']; img=Image.new('L',(c.shape[1]+24,c.shape[0]+24),255)
        img.paste(Image.fromarray(((1-c)*255).astype('uint8')),(12,12))
    base=LIB if r['conf']=='ok' else REV
    if img is not None:
        os.makedirs(f'{base}/{ch}',exist_ok=True); img.save(f'{base}/{ch}/{fn}')
        rel=f'{ch}/{fn}' if r['conf']=='ok' else f'../_review/行-杜牧/{ch}/{fn}'
        chars.append(dict(char=ch,file=rel,source=W,line=r['line'],seq=s,image='zh.jpg',box=r['box'],conf=r['conf']))
    boxes.append([r['line'],ch,'zh.jpg',*(r['box'] or [0,0,0,0]),r['conf']])
    items.append((f"{r['line']}{ch}{'?' if r['conf']!='ok' else ''}",img))
json.dump(boxes,open('boxes.json','w'),ensure_ascii=False)
SRC=json.load(open('source.json'))
json.dump({'master':'杜牧','sources':{W:SRC},'chars':chars},open(LIB+'/index.json','w'),ensure_ascii=False,indent=1)
os.makedirs(ROOT+'/shufa/output',exist_ok=True)
sheet(items,ROOT+'/shufa/output/字库_杜牧.jpg',cell=150,cols=20)
ok=[c for c in chars if c['conf']=='ok']
print('total',len(recs),'ok',len(ok),'low',len(recs)-len(ok),'distinct',len({c['char'] for c in chars}),'distinct_ok',len({c['char'] for c in ok}))
