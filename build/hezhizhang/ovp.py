import json,sys,subprocess
from PIL import Image
B=sys.argv[1]; ps=sys.argv[2].split(',')
ims=[]
for p in ps:
    subprocess.run(['python3','ov2.py',B,p,'0.4']); ims.append(Image.open('/tmp/hezhizhang/ov%s.jpg'%p))
S=Image.new('RGB',(sum(i.width+6 for i in ims),ims[0].height),'gray'); x=0
for i in ims: S.paste(i,(x,0)); x+=i.width+6
S.save('/tmp/hezhizhang/ovp.jpg')
