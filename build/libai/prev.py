import sys,json
from fix import *
B=json.load(open('boxes.json'))
Ts=[float(t) for t in sys.argv[2].split(',')]
names=sys.argv[1].split(',')
cell=300;f=ImageFont.truetype(F,26)
rows=[b for b in B if b[0] in names]
S=Image.new('RGB',((len(Ts)+1)*cell,len(rows)*(cell+30)),'white');d=ImageDraw.Draw(S)
ms={T:mask(T) for T in Ts}
for r,b in enumerate(rows):
    box=b[1:5]; fr=b[6] if len(b)>6 else 0.5
    ims=[orig(box)]+[cut(ms[T],box,fr) for T in Ts]
    for c,t in enumerate(ims):
        if t is None: continue
        t=t.copy();t.thumbnail((cell-10,cell-10));S.paste(t,(c*cell+5,r*(cell+30)+30))
        d.text((c*cell+5,r*(cell+30)),f"{b[0]} {'orig' if c==0 else 'T=%g'%Ts[c-1]}",fill=(200,0,0),font=f)
S.save(sys.argv[3]);print(sys.argv[3])
