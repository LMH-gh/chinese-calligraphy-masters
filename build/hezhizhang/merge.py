# 合并：1–27 行沿用 boxes_v1_27.json（build.py 手工校定），28 行起由 seg2.py(+fix2.py) 自动切分
import json,sys
sys.path.insert(0,'.')
import seg2
old=[b for b in json.load(open('boxes_v1_27.json')) if b[0]<=27]
pages=[int(x) for x in sys.argv[1].split(',')] if len(sys.argv)>1 else list(range(9,32))
new=seg2.run(pages)
L=[l.strip() for l in open('lines.txt',encoding='utf8')]
# 校验字序
for ln in sorted(set(b[0] for b in new)):
    t=L[ln-1]
    if ln in seg2.NOBOX: t=t.replace('々','')
    got=''.join(b[1] for b in new if b[0]==ln); assert got==t,(ln,got,t)
B=old+new
json.dump(B,open('boxes.json','w'),ensure_ascii=False,indent=0)
print('boxes',len(B),'lines',max(b[0] for b in B))
