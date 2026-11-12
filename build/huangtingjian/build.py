import json,os,shutil,sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
sys.path.insert(0,'..')
from cut import cut
from hl import mask, F
ROOT='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244'
W='廉颇蔺相如传'
LIB=f'{ROOT}/data/masters/草-黄庭坚'; REV=f'{ROOT}/data/masters/_review/草-黄庭坚'
exec(open('spec.py').read())
open('lines.txt','w').write('\n'.join(f'{r[0]}\t{r[4]}' for r in S)+'\n')
B=json.load(open('boxes.json'))
for d in (LIB,REV):
    if os.path.exists(d): shutil.rmtree(d)
    os.makedirs(d)
items=[]
for k,(ln,ch,img,x1,y1,x2,y2,conf) in enumerate(B):
    x1,y1=max(0,x1),max(0,y1); x2,y2=min(4000,x2),min(3000,y2)
    im=cut(mask(int(img[1:4])),[x1,y1,x2,y2])
    ink=0 if im is None else int((np.asarray(im)<128).sum())
    items.append(dict(seq=k,char=ch,line=ln,image=img,box=[x1,y1,x2,y2],conf=conf,ink=ink,im=im))
med=float(np.median([t['ink'] for t in items if t['conf']=='ok']))
chars=[]
for t in items:
    if t['im'] is None: t['conf']='low'; continue
    if t['ink']<0.35*med and t['conf']=='ok': t['conf']='low'; t['auto']='low_ink'
    im=ImageOps.expand(t['im'],12,fill=255)
    base=LIB if t['conf']=='ok' else REV
    os.makedirs(f"{base}/{t['char']}",exist_ok=True)
    fn=f"{t['char']}/{W}_{t['seq']:04d}.png"
    im.save(f'{base}/{fn}')
    e=dict(char=t['char'],file=fn if t['conf']=='ok' else '../_review/草-黄庭坚/'+fn,source=W,line=t['line'],seq=t['seq'],image=t['image'],box=t['box'],conf=t['conf'])
    if 'auto' in t: e['note']='墨量低于ok中位数35%，自动降为low'
    chars.append(e)
idx={"master":"黄庭坚","sources":{W:{
 "holder":"大都会艺术博物馆（The Metropolitan Museum of Art）1989.363.4，顾洛阜（John M. Crawford Jr.）旧藏",
 "date":"约1095年（北宋）","medium":"纸本墨迹，手卷，33.7×1840.2 cm",
 "image":"Met Open Access 高清图 DP-18548-002～033（images.metmuseum.org/CRDImages/as/original/），CC0 公有领域",
 "authenticity":"大都会艺术博物馆定为黄庭坚真迹（约1095年）。2013年《东方早报·艺术评论》刊《黄庭坚草书〈廉颇蔺相如传〉质疑》，认为系伪作，理由包括错字与败笔、卷中接缝、用笔不类、印鉴可疑。列为「馆藏定真·有异说」。"}},
 "chars":chars}
json.dump(idx,open(f'{LIB}/index.json','w'),ensure_ascii=False,indent=1)
ok=[c for c in chars if c['conf']=='ok']
print('lines',len(S),'boxes',len(B),'saved',len(chars),'ok',len(ok),'low',len(chars)-len(ok),'distinct_ok',len({c['char'] for c in ok}),'distinct_all',len({c['char'] for c in chars}),'median_ink',med,'autolow',sum('note' in c for c in chars))
# sheet
cell,cols=150,24; f=ImageFont.truetype(F,24)
rows=(len(items)+cols-1)//cols
Sh=Image.new('RGB',(cols*cell,rows*(cell+30)+60),'white'); d=ImageDraw.Draw(Sh)
d.text((10,10),f'黄庭坚 草书《廉颇蔺相如传》单字库 第1–{S[-1][0]}行  共{len(items)}字 ok {len(ok)}  （紫色=low/待审）',fill=(0,0,0),font=ImageFont.truetype(F,34))
for i,t in enumerate(items):
    x,y=(i%cols)*cell,(i//cols)*(cell+30)+60
    lowc=t['conf']!='ok'
    if t['im'] is not None:
        a=t['im'].copy(); a.thumbnail((cell-10,cell-10)); Sh.paste(a,(x+5,y+28))
    if lowc: d.rectangle([x+1,y+1,x+cell-2,y+cell+28],outline=(200,0,200),width=3)
    d.text((x+5,y+2),f"{t['line']}{t['char']}",fill=(200,0,200) if lowc else (200,0,0),font=f)
out=f'{ROOT}/shufa/output/字库_黄庭坚.jpg'; Sh.save(out,quality=70); print(out,Sh.size)
