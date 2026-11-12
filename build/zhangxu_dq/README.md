断千字文 切字工作目录。图：src/（Met CC0，1977.375.29a–e）。
mk.py 生成蒙版 m_*.npz（(g-bl)>45 白字 + 局部中值地色补粗笔）；*_spec.py 为各纸列/字框；
prev.py <a-e> 出预览；build_lib.py 幂等入库到 data/masters/草-张旭（ok）与 _review/草-张旭（low），并更新 index.json。
2026-11-12：a_spec 补切第3石全部列（共64字）；b/c_spec 修框并回收 ok；新增第5石 h（哈佛 FHCL:886417 晚清拓；哈佛图书馆对公有领域作品复制品不主张版权），
mk_h.py 生成 m_h.npz；build_lib 顺序 d c a b h e，繁简转换回落 opencc，墨量阈值改用全部切字中位数。grid.py <a-e> x1 x2 y1 y2 scale out 出带坐标的原图局部。
