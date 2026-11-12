import json,os,shutil
from fix import *
R='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244'
LIB=R+'/data/masters/草-李白'; REV=R+'/data/masters/_review/草-李白'
old=json.load(open(LIB+'/index.json'))
oldbox={c['char']:c for c in old['chars']}
B={b[0]:b[1:5] for b in json.load(open('boxes.json'))}
text="山高水长物象千万非有老笔清壮可穷十八日上阳台书太白"
lines=["山高水长物象","千万非有老","笔清壮可穷","十八日上阳台书","太白"]
lineof={};i=0
for li,l in enumerate(lines,1):
    for c in l: lineof[i]=li;i+=1
keep_old={'千','万','非','有','上','阳','太','白'}   # untouched ok cuts
faint={'笔','清','壮','可','穷','台','书','水','长','物','象'}
review={'水':'水渍剥蚀严重，仅存左竖钩与右侧残点，字形不可辨（学界亦称第一行水长物象基本不可辨析）',
 '长':'大面积水渍洇损，仅剩零散墨点，无法还原笔画',
 '物':'仅存一团洇墨，牛旁与勿部笔画均已模糊，形不可认',
 '象':'只余三处断续残笔，上下部件均缺，残损过重',
 '壮':'丬旁仅存一竖残痕，士部可见但右上剥落，学界称“壮”已基本不可辨析，依行款位置定释，形不可靠'}
notes={'清':'左侧氵旁淡化（水渍），右侧青部完整',
 '可':'或释“何”（亻旁剥蚀），按通行释文作“可”；此为可/句形本体',
 '穷':'复核修正切框：原框混入上字“可”的圈环、截掉下部；现框为穴头+下部，下部笔画淡，略有断续',
 '十':'复核修正切框：原框混入下方“八”字两笔',
 '八':'新增：原库漏切（原框并入“十”）',
 '台':'新增：原库把此字误标为“书”，实为“臺”（存简体台）',
 '书':'复核修正：原“书”框实为“臺”，真“书”是其下小字',
 '山':'复核修正：右侧原被截，底部Z形连笔归下字“高”',
 '高':'复核修正：补入上方连笔点、右缘',
 '笔':'复核修正切框：⺮头+聿部完整；左下淡圈环过淡未取',
 '日':'复核：原框混入“八”残笔，已收紧'}
masks={}
def M(T):
    if T not in masks: masks[T]=mask(T)
    return masks[T]
# clear old files
for d in os.listdir(REV): shutil.rmtree(os.path.join(REV,d))
chars=[];tmpold={}
for c in keep_old:
    f=os.path.join(LIB,oldbox[c]['file']); tmpold[c]=Image.open(f).copy()
for d in os.listdir(LIB):
    p=os.path.join(LIB,d)
    if os.path.isdir(p): shutil.rmtree(p)
for seq,c in enumerate(text):
    fn=f"上阳台帖_{seq:03d}.png"
    if c in keep_old:
        img=tmpold[c]; box=oldbox[c]['box']
    else:
        box=B[c]; T=22 if c in faint else 28
        img=cut(M(T),box,0.5,120 if c in faint else 80)
    conf='low' if c in review else 'ok'
    base=REV if conf=='low' else LIB
    os.makedirs(os.path.join(base,c),exist_ok=True)
    img.save(os.path.join(base,c,fn))
    e={"char":c,"file":(f"{c}/{fn}" if conf=='ok' else f"../_review/草-李白/{c}/{fn}"),"source":"上阳台帖","line":lineof[seq],"seq":seq,"box":list(map(int,box)),"conf":conf}
    if c in ('台','书'): e['orig']={'台':'臺','书':'書'}[c]
    if c in review: e['note']=review[c]
    elif c in notes: e['note']=notes[c]
    chars.append(e)
old['chars']=chars
json.dump(old,open(LIB+'/index.json','w'),ensure_ascii=False,indent=1)
print(sum(e['conf']=='ok' for e in chars),'ok',sum(e['conf']=='low' for e in chars),'low')
