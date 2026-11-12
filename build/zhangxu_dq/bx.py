import json,sys
# spec: per piece list of columns: (line, x1,x2, [(char,y1,y2,conf),...])
def build(spec,img):
    out=[]
    for line,x1,x2,chars in spec:
        for c in chars:
            ch,y1,y2=c[:3]; conf=c[3] if len(c)>3 else 'ok'
            xx1,xx2=(c[4],c[5]) if len(c)>5 else (x1,x2)
            out.append([line,ch,img,xx1,y1,xx2,y2,conf])
    return out
