# 贺知章草书孝经 单字库 — 流程备忘（2026-11-11 续标至全文）
- 图源：Commons「File:SSID-13369520 唐賀季真草書孝經.pdf」(PD)，pdfimages -j 到 /tmp/hezhizhang/s/；正文 p-003～p-031（p-031 只取前三列，左侧建隆识语不收），p-032 起为明治校记/版权页。
- 蒙版：mkmask.py（(g−bl)>45，σ=40；清 y≥3030、x≥1440、x<100；3×3 开；去页顶/页底薄栏线），备份在 masks/m*.npz（np.load(...)['m']），用前 python3 mkmask.py 或从 npz 还原到 /tmp/hezhizhang/m*.npy。
- 1–27 行：boxes_v1_27.json（build.py 手工校定，未改）。28–140 行：seg2.py 斜切分列+连通域归列+dp2.py 动态规划切字；fix2.py 存全部手工修正（PINS 切线 / YR 纵向范围 / OVR 列界 / LOW / SKIP / NOBOX）。
- 一键重建：python3 merge.py && python3 cutlib.py && python3 mkindex.py
- 释文异文见 index.json sources.孝经.text_notes；p-032 明治校记是校对依据。
