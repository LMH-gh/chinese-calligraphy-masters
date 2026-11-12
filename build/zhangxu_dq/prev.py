import sys,importlib,numpy as np
sys.path.insert(0,'..'); from cut import cut,sheet
from bx import build
s=sys.argv[1]; M=importlib.import_module(f'{s}_spec')
m=np.load(f'm_{s}.npz')['m']
B=build(M.S,M.IMG)
items=[(f"{b[0]}{b[1]}{'?' if b[7]=='low' else ''}",cut(m,b[3:7])) for b in B]
sheet(items,f'/tmp/zhangxu_dq/sh_{s}.jpg',cell=170,cols=10); print(len(B))
