import json
ROOT='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244'
idx=json.load(open('index_v1_27.json'))
C=json.load(open('chars.json'))
L=[l.strip() for l in open('lines.txt',encoding='utf8')]
lines=max(c['line'] for c in C); pages=sorted(set(c['image'] for c in C))
s=idx['sources']['孝经']
last=L[lines-1]
s['title']='草书孝经（开宗明义章至丧亲章全文，含卷末“孝经一卷”，共%d行；第1–%d行已切字）'%(len(L),lines)
s['image']='Wikimedia Commons「File:SSID-13369520 唐賀季真草書孝經.pdf」，公有领域（PD）。用其第3–%d幅图（pdfimages 编号 %s～%s）；卷末建隆二年识语、明治校记、版权页不收。https://commons.wikimedia.org/wiki/File:SSID-13369520_唐賀季真草書孝經.pdf'%(int(pages[-1][2:5]),pages[0][:5],pages[-1][:5])
s['text_notes']=('释文按原卷行款（lines.txt，每行一列）。与开元石台本异文据卷后明治校记（p-032）并逐列目验：士章 28–30 行蠹蚀阙“而”“君取”“则”“忠”；三才章 38 行首衍“地之义也”、脱“则天之明因地之利”、42 行蠹蚀阙“不”；'
 '孝治章脱“故得万国之欢心以事其先王”、“百姓”作“万国”、50 行“以事”下无“其”；圣治章“夫圣”下脱“人”、“日严”下脱“圣人因严…不严而治”廿六字（作“日严其所因者本也”）、“德教而”下衍“能”；'
 '广要道章“教民”下衍“礼”；广至德章“教以孝”下衍“者”、“日见之”下有“也”；广扬名章“家理”下脱“故”；谏争章“乎”作“矣”、“是何言欤”重文以点号、“不失”下脱“其”、阙“友”；丧亲章“伤生”下衍“也”、“簠”“簋”间衍“而”；“悌”多作“弟”。'
 '重文号（々）不入库。参考了大鹏书法字典草稿分列释文（https://zidian.dapengshufa.com/work/87384c0e-4369-5c20-90e1-0c29660f215e/1），但其多处行界与异文经目验更正。')
out=dict(idx); out['sources']={'孝经':s}
out['chars']=[{k:c[k] for k in ('char','file','source','line','box','conf')} | ({'note':c['note']} if 'note' in c else {}) | {'image':c['image'],'seq':c['seq']} for c in C]
json.dump(out,open(ROOT+'/data/masters/草-贺知章/index.json','w'),ensure_ascii=False,indent=1)
print('index chars',len(out['chars']))
