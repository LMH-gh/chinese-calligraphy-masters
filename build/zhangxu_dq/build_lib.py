import sys,os,json,importlib,shutil,numpy as np
from PIL import Image, ImageOps
sys.path.insert(0,'..'); from cut import cut,sheet
from bx import build
ROOT='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244'
LIB=f'{ROOT}/data/masters/草-张旭'; REV=f'{ROOT}/data/masters/_review/草-张旭'
T2S=dict(zip('猶兒懷氣連規隱惻離節義葉飄獨運絳讀翫屬墻飯適腸飽飫飢厭親舊實銘時營濟傾綺漢說鉅曠遠',
             '犹儿怀气连规隐恻离节义叶飘独运绛读玩属墙饭适肠饱饫饥厌亲旧实铭时营济倾绮汉说钜旷远'))
SRC='断千字文'
import opencc; _cc=opencc.OpenCC('t2s')
def t2s(c): return T2S.get(c) or _cc.convert(c)
# 石序：Met 1977.375.29 d(犹子比儿…) c(功茂实…) a(灭虢…旷远) b(委翳…亲戚故旧) e(佳妙…永)
order=['d','c','a','b','h','e']; stone={'d':1,'c':2,'a':3,'b':4,'h':5,'e':6}  # h=第5石（哈佛 FHCL:886417）
allb=[]
for s in order:
    M=importlib.import_module(f'{s}_spec'); m=np.load(f'm_{s}.npz')['m']
    for b in build(M.S,M.IMG):
        im=cut(m,b[3:7])
        allb.append(dict(stone=s,line=b[0],char=b[1],img=b[2],box=b[3:7],conf=b[7],im=im))
ink=[ (np.asarray(x['im'])<128).sum() if x['im'] is not None else 0 for x in allb]
okink=[k for k,x in zip(ink,allb) if k>0]  # 2026-11-12：改用全部切字墨量中位数，避免 ok 集合变化牵动阈值
med=float(np.median(okink)); 
for k,x in zip(ink,allb):
    x['ink']=int(k)
    if x['conf']=='ok' and k<0.35*med: x['conf']='low'; x['note']='墨量<35%中位数，自动降级'
    if x['im'] is None: x['conf']='low'
I=json.load(open(f'{LIB}/index.json'))
# 幂等：先去掉旧的断千字文条目与文件
for c in [c for c in I['chars'] if c['source']==SRC]:
    p=f'{LIB}/{c["file"]}' if c['conf']=='ok' else f'{REV}/{c["file"]}'
    if os.path.exists(p): os.remove(p)
I['chars']=[c for c in I['chars'] if c['source']!=SRC]
items=[]
for n,x in enumerate(allb):
    ch=t2s(x['char']); fn=f'{ch}/{SRC}_{n:03d}.png'
    base=LIB if x['conf']=='ok' else REV
    os.makedirs(f'{base}/{ch}',exist_ok=True)
    out=f'{base}/{fn}'
    assert not os.path.exists(out), out
    if x['im'] is not None:
        im=ImageOps.expand(x['im'].convert('L'),12,fill=255); im.save(out)
    e={'char':ch,'file':fn,'source':SRC,'seq':n,'line':f"石{stone[x['stone']]}-{x['line']}",'image':x['img'],'box':[int(v) for v in x['box']],'conf':x['conf']}
    if x['char']!=ch: e['orig']=x['char']
    if 'note' in x: e['note']=x['note']
    I['chars'].append(e)
    items.append((f"{ch}{'' if x['conf']=='ok' else '?'}",x['im']))
I['sources'][SRC]={'holder':'西安碑林博物馆（北宋元丰三年1080吕大防摹刻，残石六块）；拓本：大都会艺术博物馆 1977.375.29a–e（20世纪拓，五纸）',
 'medium':'宋刻·拓本（第1–4、6石为20世纪拓；第5石为晚清拓）',
 'image':'Metropolitan Museum of Art Open Access (CC0)：https://www.metmuseum.org/art/collection/search/64044 ，原图 images.metmuseum.org/CRDImages/as/original/1977_375_29{a..e}_O1_sf.jpg（第1–4、6石）；第5石：Harvard Fine Arts Library, Special Collections, Chinese Rubbings Collection, Zhang Xu Qian zi wen (wu) (5)，URN-3:FHCL:886417 / HOLLIS 9736388，https://curiosity.lib.harvard.edu/chinese-rubbings-collection/catalog/6-W285975_URN-3:FHCL:886417 ，IIIF https://ids.lib.harvard.edu/ids/iiif/4260972/full/full/0/default.jpg ；哈佛图书馆对公有领域作品的数字复制品不主张版权（Policy on Access to Digital Reproductions of Works in the Public Domain）',
 'authenticity':'传张旭，宋人刻石。无款，元骆天骧《类编长安志》引《复古碑录》谓乾元二年(759)旭书，元丰三年吕大防得石苍舒藏本摹刻；历来与《肚痛帖》同被视为较可信的张旭书迹（王世贞称“出鬼入神”），但属宋人重摹之刻本，非墨迹，摹刻失真程度不明。',
 'note':'Met 五纸缺第五石（煌…矫手，19字），以哈佛藏拓补。释文据《千字文》次序与按石分段的通行释文（书法品品 shufapp.com/19851.html），分列据 9610.com 所载字帖页边释文校核（仅作对位参考，未取其图）。第三石（Met a）2026-11-12 补切全部列；狂草缠绕处与字形存疑者一律 low 存 _review。第三石“岳宗恆岱”从通行本作“恒”（shufapp 作“泰”）。'}
json.dump(I,open(f'{LIB}/index.json','w'),ensure_ascii=False,indent=1)
sheet(items,'/tmp/zhangxu_dq/final.jpg',cell=150,cols=14)
okc=[x for x in allb if x['conf']=='ok']
print('total',len(allb),'ok',len(okc),'distinct ok',len(set(t2s(x['char']) for x in okc)),'median ink',med)
print('ok chars:',''.join(t2s(x['char']) for x in okc))
