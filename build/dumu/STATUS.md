# 杜牧《张好好诗》单字库
- 图：/tmp/dumu/zh.jpg（由 Commons「File:杜牧行书张好好诗卷.png」转存；临时目录，重建前需重新下载）。
- 重建：python3 mask.py && python3 seg.py && python3 build.py （spec.py 为分列/切点/手标；assign.py 按连通域多数归属分字）。
- 产出：data/masters/行-杜牧/、_review/行-杜牧/、shufa/output/字库_杜牧.jpg。
