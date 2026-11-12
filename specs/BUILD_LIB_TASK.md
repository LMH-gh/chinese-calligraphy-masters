# 自建名家单字库：通用流程

项目根：/workspace/projects/159f54f7-2b3c-49d2-bc06-091192a2e244 （下称 ROOT）。工作目录 ROOT/work/kc，为你的书家另建子目录 ROOT/work/kc/<书家拼音>/，临时图放 /tmp/<书家拼音>/（别用 /tmp/a.jpg 这类公共名，会和别的任务互相覆盖）。
需要 python 包：numpy opencv-python-headless pillow（缺就 pip install -q）。

## 1. 取图（只用公有领域或开放授权的高清图）
- 用 Wikimedia Commons API 查文件和原图 URL：
  curl -s -G "https://commons.wikimedia.org/w/api.php" -A "HarkBot/1.0 (jing19870623@gmail.com)" --data-urlencode action=query --data-urlencode list=search --data-urlencode srnamespace=6 --data-urlencode format=json --data-urlencode "srsearch=关键词"
  再用 prop=imageinfo&iiprop=url|size 拿原图 URL，curl -L 下载（带同样的 -A）。PDF 用 pdfimages -j 抽图。
- 记下来源、馆藏、授权。

## 2. 释文与行款
- 网上找可靠释文（博物馆官网、书法网站），整理成按原卷行款、每行一行的简体文本，存 <书家>/lines.txt。注意异体、衍字、涂改字（涂掉的字不收）。

## 3. 标框
- 预览带坐标网格：cd ROOT/work/kc && python3 -c "from grid import grid; grid('图路径',x1,y1,x2,y2,'/tmp/<拼音>/x.jpg',0.5,step=50)"，read_file 看图。红竖线=x，蓝横线=y，原图坐标=起点+视图像素/缩放。
- 每字一个框，写到 <书家>/boxes.json：[[行号,"字",图片文件名,x1,y1,x2,y2,"ok"|"low"], ...]
- 字数顺序必须和 lines.txt 一致。拿不准字界或字形的标 low——错标比漏标糟糕得多。

## 4. 蒙版与切字（墨迹黑字、白底输出）
from cut import cut, sheet   # cut(mask, [x1,y1,x2,y2]) -> PIL 白底黑字；sheet(items,out,cell,cols) 出对照表
蒙版自己按图做：墨迹本用自适应阈值，例如
  g=灰度; bl=cv2.GaussianBlur(g,(0,0),40); m=(((bl-g)>30)|(g<100))&(饱和度<65)  再 MORPH_OPEN 3x3（去朱印）
拓本（黑底白字）用 (g-bl)>45 取白字。每做完一批出对照表 read_file 检查。

## 5. 入库
- 输出：ROOT/data/masters/<书体>-<书家>/<简体字>/<作品名>_<序号>.png（白底黑字，四周留 12px 白边）。low 的放 ROOT/data/masters/_review/<书体>-<书家>/<字>/。
- 墨量（黑像素数）低于全部 ok 字中位数 35% 的，自动降为 low（多半是只切到残笔）。
- 写 ROOT/data/masters/<书体>-<书家>/index.json：{"master":书家, "sources":{作品名:{"holder":馆藏,"medium":墨迹/拓本,"image":图源+授权,"authenticity":真伪定论与主要争议（写清谁持何说）}}, "chars":[{"char","file","source","line","box","conf"}]}
- 不要改 masters.py，主代理会注册。

## 6. 回报
书家、作品、真伪结论（一两句，含主要异说）、图源与授权、总切字数、ok 数、不同字数、库目录路径。卡住两次以上的地方标 low 继续，不要停。
