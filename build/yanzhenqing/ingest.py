import json,sys,os,shutil
sys.path.insert(0,'..')
import numpy as np
from PIL import Image, ImageOps
from cut import cut,sheet
from seg import M
ROOT='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244'
LIB=f'{ROOT}/data/masters/行-颜真卿祭侄'; REV=f'{ROOT}/data/masters/_review/行-颜真卿祭侄'
for d in (LIB,REV):
    if os.path.isdir(d): shutil.rmtree(d)
    os.makedirs(d)
B=json.load(open('boxes.json'))
lines=[l.strip() for l in open('lines.txt') if l.strip()]
exp=[(i+1,c) for i,l in enumerate(lines) for c in l]
assert [(b[0],b[1]) for b in B]==exp, 'order mismatch'
recs=[]
for seq,b in enumerate(B):
    im=cut(M,b[3:7])
    ink=0 if im is None else int((np.asarray(im)<128).sum())
    recs.append(dict(char=b[1],line=b[0],seq=seq,box=b[3:7],conf=b[7],ink=ink,im=im))
med=float(np.median([r['ink'] for r in recs if r['conf']=='ok']))
for r in recs:
    if r['conf']=='ok' and r['ink']<0.35*med: r['conf']='low'; r['note']='墨量低于ok中位数35%，自动降为low'
chars=[]
for r in recs:
    name=f"祭侄文稿_{r['seq']:04d}.png"
    base=LIB if r['conf']=='ok' else REV
    os.makedirs(f"{base}/{r['char']}",exist_ok=True)
    if r['im'] is not None:
        ImageOps.expand(r['im'].convert('L'),12,255).save(f"{base}/{r['char']}/{name}")
    rel=f"{r['char']}/{name}" if r['conf']=='ok' else f"../_review/行-颜真卿祭侄/{r['char']}/{name}"
    e=dict(char=r['char'],file=rel,source='祭侄文稿',line=r['line'],seq=r['seq'],image='祭侄文稿卷.唐.顏真卿.纸本行书.台北故宫博物院藏 (cropped).tif',box=r['box'],conf=r['conf'],ink=r['ink'])
    if 'note' in r: e['note']=r['note']
    chars.append(e)
idx={'master':'颜真卿','sources':{'祭侄文稿':{
 'holder':'台北故宫博物院 故书000060',
 'date':'唐乾元元年（758年）',
 'medium':'麻纸墨迹，手卷（行书草稿）',
 'image':'Wikimedia Commons「File:祭侄文稿卷.唐.顏真卿.纸本行书.台北故宫博物院藏 (cropped).tif」15610×5784，源自台北故宫开放图档（Open Data），公有领域 PD',
 'authenticity':'公认颜真卿真迹（唐代原稿墨迹，历代著录、元鲜于枢等题跋），学界无实质异议。释文小争议：第6行末字，多数释「曰」，亦有释「今」者；本库按「曰」收并标 low。涂改圈去之字不收。'}},
 'chars':chars}
json.dump(idx,open(f'{LIB}/index.json','w'),ensure_ascii=False,indent=1)
ok=[r for r in recs if r['conf']=='ok']
print('total',len(recs),'ok',len(ok),'low',len(recs)-len(ok),'distinct_all',len({r['char'] for r in recs}),'distinct_ok',len({r['char'] for r in ok}),'median',med)
print('demoted',[ (r['seq'],r['char']) for r in recs if 'note' in r])
items=[(f"{r['char']}{r['seq']}",r['im']) for r in ok]
os.makedirs(f'{ROOT}/shufa/output',exist_ok=True)
sheet(items,'/tmp/yanzhenqing/okall.png',150,18)
Image.open('/tmp/yanzhenqing/okall.png').convert('RGB').save(f'{ROOT}/shufa/output/字库_颜真卿祭侄.jpg',quality=88)
