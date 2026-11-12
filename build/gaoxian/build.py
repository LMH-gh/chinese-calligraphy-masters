import json,os,sys,shutil,numpy as np,cv2
from PIL import Image,ImageOps
sys.path.insert(0,'..')
from cut import sheet
from seg import boxes, assign, M
ROOT='/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244'
m=np.load(M); m[600:]=0
bx=boxes()
LOW=json.load(open('low.json')) if os.path.exists('low.json') else {}
xs,ys,best,bd,pl,st=assign(m,bx)
items=[]
for i,b in enumerate(bx):
    sel=(best==i)&(bd<10*25)   # drop pixels farther than 25px outside the box
    # drop tiny fragments: components with <40 px in this char
    X,Y,P=xs[sel],ys[sel],pl[sel]
    if len(X):
        cnt=np.bincount(P); keep=cnt[P]>=40
        X,Y=X[keep],Y[keep]
    if len(X)==0: items.append((b,None,0)); continue
    x0,y0=X.min(),Y.min(); w,h=X.max()-x0+1,Y.max()-y0+1
    a=np.full((h,w),255,'uint8'); a[Y-y0,X-x0]=0
    items.append((b,Image.fromarray(a),len(X),[int(x0),int(y0),int(x0+w),int(y0+h)]))
json.dump([[*b[:2],*it[3]] if len(it)>3 else b for b,it in zip(bx,items)],open('boxes_tight.json','w'),ensure_ascii=False)
if __name__=='__main__':
    sheet([(f"{k}{it[0][1]}",it[1]) for k,it in enumerate(items)],'/tmp/gaoxian/sheet.jpg',cell=120,cols=20)
    json.dump(bx,open('boxes_raw.json','w'),ensure_ascii=False)
