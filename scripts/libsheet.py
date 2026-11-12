#!/usr/bin/env python3
"""自建名家库字表：python3 libsheet.py 草-张旭 [标题]"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, "fonts", "LXGWWenKai-Regular.ttf")
d = sys.argv[1]; lib = os.path.join(ROOT, "data", "masters", d)
I = json.load(open(os.path.join(lib, "index.json")))
items = [x for x in I["chars"] if x["conf"] == "ok"]
cols, cell, lab = 14, 210, 44
rows = (len(items) + cols - 1) // cols
W, H = cols * cell + 120, rows * (cell + lab) + 260
img = Image.new("RGB", (W, H), (242, 234, 214)); dr = ImageDraw.Draw(img)
ft = ImageFont.truetype(F, 64); fs = ImageFont.truetype(F, 30); fl = ImageFont.truetype(F, 26)
title = sys.argv[2] if len(sys.argv) > 2 else f"{I['master']} 自建字库"
dr.text((60, 50), title, font=ft, fill=(40, 30, 25))
srcs = "；".join(f"{k}：{v['authenticity']}" for k, v in I["sources"].items())
dr.text((60, 140), f"{len(items)} 字（{len(set(x['char'] for x in items))} 个不同字） · 仅收可靠切字，存疑字另存待复核", font=fs, fill=(110, 80, 60))
for i, x in enumerate(items):
    cx, cy = 60 + (i % cols) * cell, 230 + (i // cols) * (cell + lab)
    g = Image.open(os.path.join(lib, x["file"])).convert("L")
    g.thumbnail((cell - 30, cell - 30))
    m = ImageOps.invert(g)
    img.paste((24, 20, 18), (cx + (cell - g.width) // 2, cy + (cell - g.height) // 2), m)
    dr.text((cx + 8, cy + cell - 4), f"{x['char']} · {x['source']}", font=fl, fill=(160, 40, 30))
out = os.path.join(ROOT, "shufa", "output", f"字库_{I['master']}.jpg")
img.save(out, quality=90); print(out)
