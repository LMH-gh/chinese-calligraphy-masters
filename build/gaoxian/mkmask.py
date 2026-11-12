# 重建蒙版：python3 mkmask.py  -> /tmp/gaoxian/m.npy, sh.jpg（build.py/ingest.py 依赖）
import numpy as np,cv2,os,shutil
from PIL import Image
os.makedirs('/tmp/gaoxian',exist_ok=True)
shutil.copy('src/高闲 草书千字文卷.jpg','/tmp/gaoxian/sh.jpg')
a=np.asarray(Image.open('/tmp/gaoxian/sh.jpg').convert('RGB')).astype(int)
g=a.mean(2); sat=a.max(2)-a.min(2)
gb=cv2.GaussianBlur(g.astype('float32'),(0,0),25)
m=(((gb-g)>35)|(g<90))&(sat<45)
m=cv2.morphologyEx(m.astype('uint8'),cv2.MORPH_OPEN,np.ones((2,2),'uint8'))
np.save('/tmp/gaoxian/m.npy',m)
