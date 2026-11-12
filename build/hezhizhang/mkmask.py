import cv2,numpy as np,os
T='/tmp/hezhizhang/'; D=os.path.dirname(os.path.abspath(__file__))+'/masks/'
for i in range(3,35):
    g=cv2.imread(T+'s/p-%03d.jpg'%i,0).astype(np.float32)
    bl=cv2.GaussianBlur(g,(0,0),40)
    m=((g-bl)>45).astype(np.uint8); m[3030:]=0; m[:,1440:]=0; m[:,:100]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    # 去乌丝栏上下横线（只在页顶 y<330 / 页底 y>2850 带内）：一段≤25px 厚、横跨过半宽度、上下 10~30px 都空的行带才视为栏线
    cov=m[:,100:1420].reshape(m.shape[0],33,40).max(2).mean(1)
    rows=np.nonzero(cov>0.5)[0]; rows=rows[(rows<330)|(rows>2850)]
    groups=[]
    for y in rows:
        if groups and y-groups[-1][1]<=3: groups[-1][1]=y
        else: groups.append([y,y])
    for a_,b_ in groups:
        if b_-a_>25: continue
        up=cov[max(0,a_-30):max(1,a_-10)].mean(); dn=cov[b_+10:b_+30].mean() if b_+30<len(cov) else 0
        if up<0.25 and dn<0.25: m[max(0,a_-6):b_+7]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    np.save(T+'m%d.npy'%i,m); np.savez_compressed(D+'m%d.npz'%i,m=m)
