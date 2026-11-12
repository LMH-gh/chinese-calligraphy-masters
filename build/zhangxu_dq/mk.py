import numpy as np, cv2, sys
from PIL import Image
# 拓本（黑底白字）：主判据 (g-bl)>45，bl=σ40 高斯；粗笔画内部会被 bl 抬高而漏掉，
# 另以"局部地色"(4x 缩小后 1/8 缩小 41px 中值≈330px 再模糊) 加偏移 D 补粗笔画。
D=int(sys.argv[1]) if len(sys.argv)>1 else 95
for s in 'abcde':
    g=cv2.imread(f'src/1977_375_29{s}_O1_sf.jpg',0).astype(np.float32)
    bl=cv2.GaussianBlur(g,(0,0),40)
    m1=(g-bl)>45
    sm=cv2.resize(g,None,fx=0.125,fy=0.125,interpolation=cv2.INTER_AREA).astype('uint8')
    bg=cv2.medianBlur(sm,41).astype(np.float32)   # ≈330px 中值=局部地色
    bg=cv2.GaussianBlur(bg,(0,0),4)
    bg=cv2.resize(bg,(g.shape[1],g.shape[0]))
    m2=(cv2.GaussianBlur(g,(0,0),2)-bg)>D
    m=(m1&m2|m2).astype('uint8') if False else ((m1&((g-bg)>D-35))|m2).astype('uint8')
    pb=cv2.GaussianBlur(g,(0,0),25)
    paper=(pb<150).astype('uint8')
    n,lab,st,_=cv2.connectedComponentsWithStats(paper,8)
    k=1+np.argmax(st[1:,4]); paper=(lab==k).astype('uint8')
    paper=cv2.morphologyEx(paper,cv2.MORPH_CLOSE,np.ones((151,151),'uint8'))
    # 填洞：大块白笔画会被误判为纸外
    ff=paper.copy(); h,w=ff.shape; msk=np.zeros((h+2,w+2),'uint8'); cv2.floodFill(ff,msk,(0,0),1)
    paper=paper|(1-ff)
    paper=cv2.erode(paper,np.ones((25,25),'uint8'))
    m&=paper
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),'uint8'))
    np.savez_compressed(f'm_{s}.npz',m=m)
    Image.fromarray((255-m*255).astype('uint8')).save(f'/tmp/zhangxu_dq/M_{s}.png')
    v=Image.fromarray((255-m*255).astype('uint8')); v.thumbnail((1400,1400)); v.save(f'/tmp/zhangxu_dq/mask_{s}.png')
    print(s,m.mean())
