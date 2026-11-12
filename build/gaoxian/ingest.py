import json,os,sys,shutil,numpy as np
from PIL import ImageOps
sys.path.insert(0,'..')
from cut import sheet
import build
from spec import S
ROOT='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244'
NAME='草-高闲'; SRC='千字文残卷'; IMG='高闲 草书千字文卷.jpg'
OUT=ROOT+'/data/masters/'+NAME; REV=ROOT+'/data/masters/_review/'+NAME
LOW={7:'梧上方混入“翠”字末笔',39:'与“耳”字界不清',40:'只切到“耳”的竖笔，字界不清',42:'与“具”连写，字界不清',43:'与“墙”连写，只切到局部',
 48:'“口”极小，与上下字连写',101:'草法简省，字界存疑',102:'墨淡，笔画残断',120:'此段“恐惶”二字只见一字形，字序存疑',121:'或为“恐”，此段“恐惶”只辨出一字',
 122:'字形不似常见“笺”草法，存疑',125:'字形存疑',146:'墨枯，蒙版残断',148:'枯笔淡墨，蒙版残断',149:'枯笔淡墨，蒙版残断',150:'枯笔淡墨，蒙版残断',151:'枯笔淡墨，蒙版残断',
 152:'枯笔淡墨，几乎未切到',153:'枯笔淡墨，几乎未切到',172:'“利俗”只辨出一字形，或为二字连写',177:'字形存疑',199:'原迹作金旁（释文作“鈈”），存疑',201:'仅存两点，字形存疑',190:'上方混入邻字笔画',
 223:'混入邻行笔画',230:'与“等”连写，字界存疑',231:'与“蒙”连写，字界存疑',232:'末行附近字序据言旁推定，存疑',233:'同上',234:'同上',235:'同上',
 236:'卷末数字字序推定',237:'卷末数字字序推定',238:'卷末数字字序推定',239:'卷末数字字序推定',240:'卷末数字字序推定',244:'混入印章残迹',245:'混入印章残迹'}
ALT={'早':'蚤','沉':'耽','桓':'垣','馂':'饫','际':'祭','钩':'钧','祐':'祜','邵':'劭','飡':'餐','翫':'玩','讌':'宴','环':'环（原迹作“鈈”）'}
for d in (OUT,REV):
    if os.path.exists(d): shutil.rmtree(d)
    os.makedirs(d)
lines=[t for t,*_ in S]
open('lines.txt','w',encoding='utf8').write('\n'.join(lines)+'\n')
items=[]
for n,it in enumerate(build.items):
    b=it[0]; im=it[1]; ink=it[2]
    box=it[3] if len(it)>3 else b[2:6]
    conf='low' if n in LOW else 'ok'
    items.append(dict(n=n,ln=b[0],ch=b[1],im=im,ink=ink,box=box,conf=conf,note=LOW.get(n)))
med=float(np.median([x['ink'] for x in items if x['conf']=='ok']))
json.dump([[x['ln'],x['ch'],IMG,*x['box'],x['conf']] for x in items],open('boxes.json','w'),ensure_ascii=False,indent=0)
chars=[]
for x in items:
    if x['im'] is None: x['conf']='low'; x['note']='切图为空'
    elif x['conf']=='ok' and x['ink']<0.35*med: x['conf']='low'; x['note']='墨量低于ok中位数35%，自动降为low'
    fn='%s_%04d.png'%(SRC,x['n'])
    base=OUT if x['conf']=='ok' else REV
    os.makedirs(base+'/'+x['ch'],exist_ok=True)
    if x['im'] is not None: ImageOps.expand(x['im'],12,fill=255).save(base+'/'+x['ch']+'/'+fn)
    rel=x['ch']+'/'+fn if x['conf']=='ok' else '../_review/'+NAME+'/'+x['ch']+'/'+fn
    c=dict(char=x['ch'],file=rel,source=SRC,line=x['ln'],seq=x['n'],box=x['box'],conf=x['conf'])
    if x['ch'] in ALT: c['standard']=ALT[x['ch']]
    if x['note']: c['note']=x['note']
    chars.append(c)
src={SRC:dict(
 title='草书千字文（残卷，存“莽抽条”至“焉哉乎也”及款“吴兴高闲书”，52行）',
 holder='上海博物馆（唐 高闲 草书千字文卷，纸本，纵30.8×横331.3 cm）。https://www.shanghaimuseum.net/mu/frontend/pg/article/id/CI00000592',
 medium='墨迹（纸本）',
 image='Wikimedia Commons「File:高闲 草书千字文卷.jpg」（6963×619 px，全卷一图），标注 {{PD-art-100}}（原作为公有领域，忠实复制件不产生新版权），图源注明上海博物馆官网。https://commons.wikimedia.org/wiki/File:%E9%AB%98%E9%97%B2_%E8%8D%89%E4%B9%A6%E5%8D%83%E5%AD%97%E6%96%87%E5%8D%B7.jpg 。分辨率低（字高约60–120 px），切字细节有限。',
 transcription='释文据 warting.com 转载释文（https://warting.com/news/201903/238118.html）并对原图逐行核对行款；按原迹写法收字（如“早”作蚤、“沉”作耽、“际”作祭、“桓”作垣、“馂”作饫、“钩”作钧、“祐”作祜、“邵”作劭），standard 字段给通行字。',
 authenticity='主流定为高闲真迹：上海博物馆以“唐 高闲 草书千字文卷”著录；流传有绪（米芾《宝章待访录》著录时尚全，元鲜于枢《困学斋杂录》著录时已残，鲜于枢补书前半；经赵明诚、鲜于枢、乔篑成、方鸣谦、卞永誉、安岐、蔡世松、景朴孙、叶恭绰递藏），一般称为高闲唯一传世墨迹（人民日报海外版/中国文明网 2011）。异说：清朱彝尊疑“世所传高闲千文及张旭书大约多出（鲜于枢）其手”（王连起《鲜于枢及其书法艺术》引）；部分图录标“传”。相关：辽宁省博物馆藏鲜于枢补书前半卷，谢稚柳一方据“箕子之裔”印不同疑辽博补卷为后人伪作（2586.wang《一份合约的夭折》）；台北故宫另藏《唐高閒書千文》全卷，与上博残卷非一物，未采用。本库结论：真迹（主流），存朱彝尊疑出鲜于枢之说。',
 lines=52, chars_written=246, note='按今本千字文，“莽…也”应为243字；本卷“恐惶”“利俗”两处各只辨出一个字形（或连写/漏书），故正文241字+款5字=246个切字。')}
idx=dict(master='高闲',sources=src,chars=chars)
json.dump(idx,open(OUT+'/index.json','w'),ensure_ascii=False,indent=1)
ok=[c for c in chars if c['conf']=='ok']
print('total',len(chars),'ok',len(ok),'distinct',len(set(c['char'] for c in chars)),'distinct_ok',len(set(c['char'] for c in ok)),'med',med)
sheet([(('' if x['conf']=='ok' else '?')+x['ch']+str(x['n']),x['im']) for x in items],ROOT+'/shufa/output/字库_高闲.jpg',cell=130,cols=20)
