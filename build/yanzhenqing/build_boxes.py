import json
from seg import tight
C=json.load(open('coarse.json')); out=[]
for ln in sorted(C,key=int):
    for it in C[ln]:
        out.append([int(ln),it[0],'yzq']+tight(it[1])+[it[2] if len(it)>2 else 'ok'])
json.dump(out,open('boxes.json','w'),ensure_ascii=False)
import sys; sys.path.insert(0,'..')
from cut import cut,sheet
from seg import M
items=[(f'{i}{b[1]}'+('*' if b[7]=='low' else ''),cut(M,b[3:7])) for i,b in enumerate(out)]
for k in range(0,len(items),80): sheet(items[k:k+80],f'/tmp/yanzhenqing/sh{k//80}.png',150,16)
print(len(out))
