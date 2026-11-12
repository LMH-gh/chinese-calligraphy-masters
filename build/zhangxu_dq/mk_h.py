import numpy as np, cv2
from PIL import Image
# 第5石：哈佛美院图书馆 FHCL:886417（张旭千字文（五）），黑底白字拓本。同 mk.py 思路：局部地色+偏移。
g=cv2.imread('src/harvard_FHCL886417_qzw5.jpg',0).astype(np.float32)
sm=cv2.resize(g,None,fx=0.125,fy=0.125,interpolation=cv2.INTER_AREA).astype('uint8')
bg=cv2.medianBlur(sm,31).astype(np.float32); bg=cv2.GaussianBlur(bg,(0,0),3)
bg=cv2.resize(bg,(g.shape[1],g.shape[0]))
m=((cv2.GaussianBlur(g,(0,0),2)-bg)>70)&(g>120)
# 纸边（拓纸外白边）去掉：纸外区域在大尺度上很亮
pb=cv2.GaussianBlur(g,(0,0),40); m&=(pb<150)
m=cv2.morphologyEx(m.astype('uint8'),cv2.MORPH_OPEN,np.ones((5,5),'uint8'))
np.savez_compressed('m_h.npz',m=m)
v=Image.fromarray((255-m*255).astype('uint8')); v.thumbnail((1200,1200)); v.save('/tmp/zhangxu_dq/mask_h.png'); print(m.mean())
