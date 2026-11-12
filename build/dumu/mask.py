import numpy as np,cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
def make(src='/tmp/dumu/zh.jpg',x0=11800,x1=24800,th=30):
    a=np.asarray(Image.open(src).convert('RGB').crop((x0,0,x1,2160))).astype(np.float32)
    g=a.mean(2); sat=a.max(2)-a.min(2)
    bl=cv2.GaussianBlur(g,(0,0),40)
    m=(((bl-g)>th)|(g<70))&(sat<45)
    m=cv2.morphologyEx(m.astype('uint8'),cv2.MORPH_OPEN,np.ones((3,3),'uint8'))
    full=np.zeros((2160,26303),'uint8'); full[:,x0:x1]=m
    return full
if __name__=='__main__':
    m=make(); np.save('/tmp/dumu/mask.npy',m)
    Image.fromarray((1-m[:,11800:24800])*255).resize((1300,216)).save('/tmp/dumu/maskv.png')
    print(m.sum())
