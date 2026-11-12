#!/usr/bin/env python3
"""名家书法学习馆 · 本地生成器（仅供个人学习研究，不得商用）

数据来源
  真迹单字：zhuojg/chinese-calligraphy-dataset（Apache-2.0），19 家碑帖真迹切字，约 11.5 万字 → data/masters/
  名家字体：方正/汉仪名家书法字库（来自 209-Tongji/Fonts，仅限个人学习研究）→ fonts/

用法
  python3 masters.py list                                   # 列出全部名家/碑帖
  python3 masters.py char 永 [--only 楷|行|草|隶|篆|名家名]   # 单字名家对照表
  python3 masters.py jizi "文本" --master 颜真卿 [--title 题 --author 作者 --seal 印文 --grid --trad]
                                                            # 集字成篇（竖排册页）
  python3 masters.py practice "字" --master 欧阳询           # 米字格临摹字帖（范字 + 描红）
  python3 masters.py compare "文本" --masters 颜真卿,柳公权,欧阳询  # 同一句多家对照
"""
import os, sys, re, glob, random, argparse, json, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageOps
from fontTools.ttLib import TTFont
import opencc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "masters")
FONTS = os.path.join(ROOT, "fonts")
OUT = os.path.join(ROOT, "shufa", "output")
LABEL_FONT = os.path.join(FONTS, "LXGWWenKai-Regular.ttf")
S2T, T2S = opencc.OpenCC("s2t"), opencc.OpenCC("t2s")

# key: (显示名, 书体, 朝代, 类型, 来源, 说明)
REAL = {
    "集字圣教序": ("王羲之", "行", "东晋", "行-集字圣教序", "《集王圣教序》"),
    "智永": ("智永", "楷", "隋", "楷-智永", "《真草千字文》楷书"),
    "虞世南": ("虞世南", "楷", "唐", "楷-虞世南", "《孔子庙堂碑》"),
    "多宝塔": ("颜真卿", "楷", "唐", "楷-多宝塔", "《多宝塔碑》"),
    "柳公权": ("柳公权", "楷", "唐", "楷-柳公权", "《玄秘塔碑》等"),
    "魏碑": ("魏碑", "楷", "北魏", "楷-魏碑", "北魏碑刻集字"),
    "米芾": ("米芾", "行", "北宋", "行-米芾", "米芾行书集字"),
    "张即之": ("张即之", "楷", "南宋", "楷-张即之", "张即之楷书"),
    "赵孟頫": ("赵孟頫", "楷", "元", "楷-赵孟俯三门记", "《玄妙观重修三门记》"),
    "王铎": ("王铎", "行", "明", "行-王铎", "王铎行书集字"),
    "傅山": ("傅山", "行", "明末清初", "行-傅山", "傅山行书集字"),
    "郑板桥": ("郑板桥", "行", "清", "行-郑板桥", "郑板桥六分半书"),
    "金农": ("金农", "隶", "清", "隶-金农", "金农漆书"),
    "邓石如": ("邓石如", "隶", "清", "隶-邓石如", "邓石如隶书"),
    "伊秉绶": ("伊秉绶", "隶", "清", "隶-伊秉绶", "伊秉绶隶书"),
    "何绍基": ("何绍基", "隶", "清", "隶-何绍基", "何绍基隶书"),
    "赵之谦": ("赵之谦", "楷", "清", "楷-赵之谦", "赵之谦魏楷"),
    "沈尹默": ("沈尹默", "楷", "近现代", "楷-沈尹默", "沈尹默楷书"),
    "王壮为": ("王壮为", "行", "近现代", "行-王壮为", "王壮为行书"),
    "张旭": ("张旭", "草", "唐", "草-张旭", "《古诗四帖》（传，有争议）《肚痛帖》《断千字文》（宋刻）自建集字"),
    "李白": ("李白", "草", "唐", "草-李白", "《上阳台帖》墨迹自建集字（仅9字）"),
    "怀素": ("怀素", "草", "唐", "草-怀素", "《自叙帖》（传本，剔除苏舜钦补书）自建集字"),
    "黄庭坚草书": ("黄庭坚草书", "草", "宋", "草-黄庭坚", "《廉颇蔺相如传》墨迹（Met藏，全卷正文）自建集字"),
    "颜真卿祭侄": ("颜真卿祭侄", "行", "唐", "行-颜真卿祭侄", "《祭侄文稿》墨迹（台北故宫）自建集字，涂改字不收"),
    "贺知章": ("贺知章", "草", "唐", "草-贺知章", "传贺知章《孝经》全文（明治十七年钩摹刻本）自建集字"),
    "杜牧": ("杜牧", "行", "唐", "行-杜牧", "《张好好诗》墨迹（北京故宫）自建集字"),
    "高闲": ("高闲", "草", "唐", "草-高闲", "《草书千字文》残卷墨迹（上博）自建集字"),
}
FONT = {
    "王羲之行书": ("王羲之", "行", "东晋", "FZWangXZXSJF.TTF"),
    "王献之小楷": ("王献之", "楷", "东晋", "FZWangXZXKJW.TTF"),
    "索靖章草": ("索靖", "草", "西晋", "FZSuoJZCFU.TTF"),
    "智永楷书": ("智永", "楷", "隋", "FZZhiYKSJW.TTF"),
    "欧阳询楷书": ("欧阳询", "楷", "唐", "FZOuYXKSJF.TTF"),
    "褚遂良楷书": ("褚遂良", "楷", "唐", "FZChuSLKSJW.TTF"),
    "颜真卿楷书": ("颜真卿", "楷", "唐", "FZYanZQKSJF.TTF"),
    "柳公权楷书": ("柳公权", "楷", "唐", "FZLiuGQKSJF.TTF"),
    "李邕行书": ("李邕", "行", "唐", "FZLiYXSJW.TTF"),
    "孙过庭草书": ("孙过庭", "草", "唐", "FZSunGTCSFU.TTF"),
    "李阳冰篆书": ("李阳冰", "篆", "唐", "FZLiYBZSFU.TTF"),
    "灵飞经小楷": ("钟绍京", "楷", "唐", "FZLingFJXKJW.TTF"),
    "杨凝式行书": ("杨凝式", "行", "五代", "FZYangNSXSJW.TTF"),
    "苏轼行书": ("苏轼", "行", "北宋", "FZSuSXSJF.TTF"),
    "黄庭坚行书": ("黄庭坚", "行", "北宋", "FZHuangTJXSJF.TTF"),
    "米芾行书": ("米芾", "行", "北宋", "FZMiFXSJW.TTF"),
    "瘦金体": ("赵佶", "楷", "北宋", "FZZhaoJSJSJF.TTF"),
    "赵孟頫楷书": ("赵孟頫", "楷", "元", "FZZhaoMFKSJF.TTF"),
    "赵孟頫行书": ("赵孟頫", "行", "元", "FZZhaoMFXSJF.TTF"),
    "文徵明小楷": ("文徵明", "楷", "明", "FZWenZMXKJW.TTF"),
    "文徵明行草": ("文徵明", "草", "明", "FZWenZMXCJF.TTF"),
    "董其昌行书": ("董其昌", "行", "明", "FZDongQCXSJW.TTF"),
    "王铎行草": ("王铎", "草", "明", "FZWangDXCJF.TTF"),
    "八大山人行楷": ("八大山人", "行", "清", "FZBaDSRXKJW.TTF"),
    "伊秉绶隶书": ("伊秉绶", "隶", "清", "FZYiBSLSJW.TTF"),
    "曹全碑": ("曹全碑", "隶", "东汉", "FZCaoQBLSJW.TTF"),
    "张迁碑": ("张迁碑", "隶", "东汉", "FZZhangQBLSJW.TTF"),
    "乙瑛碑": ("乙瑛碑", "隶", "东汉", "FZYiYBLSJW.TTF"),
    "石门颂": ("石门颂", "隶", "东汉", "FZShiMSLSJW.TTF"),
    "西狭颂": ("西狭颂", "隶", "东汉", "FZXiXSLSJW.TTF"),
    "马王堆帛书": ("马王堆帛书", "隶", "西汉", "FZMaWDBSJF.TTF"),
    "张猛龙碑": ("张猛龙碑", "楷", "北魏", "FZZhangMLBKSJW.TTF"),
    "郑文公碑": ("郑文公碑", "楷", "北魏", "FZZHengWGBKSJW.TTF"),
    "沈尹默行书": ("沈尹默", "行", "近现代", "FZShenYMXSJF.TTF"),
    "启功行楷": ("启功", "行", "近现代", "FZQiGXKJF.TTF"),
    "舒同行书": ("舒同", "行", "近现代", "FZShuTXSJF.TTF"),
    "鲁迅行书": ("鲁迅", "行", "近现代", "FZLuXXSJF.TTF"),
}
ALIAS = {"张好好诗": ["杜牧"], "祭侄文稿": ["颜真卿祭侄"], "廉颇蔺相如传": ["黄庭坚草书"], "孝经": ["贺知章"], "颠张醉素": ["张旭", "怀素"], "张旭怀素": ["张旭", "怀素"], "王羲之": ["集字圣教序", "王羲之行书"], "颜真卿": ["多宝塔", "颜真卿楷书"], "颜体": ["多宝塔", "颜真卿楷书"],
         "柳体": ["柳公权", "柳公权楷书"], "欧体": ["欧阳询楷书"], "欧阳询": ["欧阳询楷书"], "赵体": ["赵孟頫", "赵孟頫楷书"],
         "宋徽宗": ["瘦金体"], "赵佶": ["瘦金体"], "瘦金书": ["瘦金体"], "钟绍京": ["灵飞经小楷"],
         "苏东坡": ["苏轼行书"], "苏轼": ["苏轼行书"], "黄庭坚": ["黄庭坚行书"], "文征明": ["文徵明小楷"], "文徵明": ["文徵明小楷"],
         "褚遂良": ["褚遂良楷书"], "董其昌": ["董其昌行书"], "启功": ["启功行楷"], "八大山人": ["八大山人行楷"]}
ERA = ["西汉", "东汉", "西晋", "东晋", "北魏", "隋", "唐", "五代", "北宋", "南宋", "元", "明", "明末清初", "清", "近现代"]

_cmaps, _fonts = {}, {}
MARK_FB = False
PREF = ["孙过庭草书", "王铎行草", "文徵明行草", "索靖章草"]


def cmap(fn):
    if fn not in _cmaps:
        _cmaps[fn] = TTFont(os.path.join(FONTS, fn), lazy=True).getBestCmap()
    return _cmaps[fn]


def pfont(fn, size):
    k = (fn, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(os.path.join(FONTS, fn) if not os.path.isabs(fn) else fn, size)
    return _fonts[k]


def resolve(name):
    """名字 → [(kind,key)]，kind=real|font"""
    if name in REAL:
        return [("real", name)]
    if name in FONT:
        return [("font", name)]
    if name in ALIAS:
        return [("real" if k in REAL else "font", k) for k in ALIAS[name]]
    out = [("real", k) for k, v in REAL.items() if name in (v[0], k)]
    out += [("font", k) for k, v in FONT.items() if name in (v[0], k) or name in k]
    if not out:
        sys.exit(f"UNKNOWN_MASTER: {name}（运行 list 查看）")
    return out


# ---------- 取字 ----------
def real_glyph(key, ch, pick=0):
    d = os.path.join(DATA, REAL[key][3])
    for c in (ch, T2S.convert(ch)):
        fs = sorted(glob.glob(os.path.join(d, c, "*")))
        if fs:
            f = fs[pick % len(fs)] if pick >= 0 else random.choice(fs)
            im = Image.open(f).convert("L")
            return ImageOps.invert(im), len(fs)  # 白=墨
    return None, 0


def font_glyph(key, ch, size=400):
    fn = FONT[key][3]
    cm = cmap(fn)
    for c in (ch, S2T.convert(ch), T2S.convert(ch)):
        if ord(c) in cm:
            f = pfont(fn, size)
            im = Image.new("L", (int(size * 1.4), int(size * 1.4)), 0)
            ImageDraw.Draw(im).text((size * 0.2, size * 0.2), c, font=f, fill=255)
            bb = im.getbbox()
            return (im.crop(bb) if bb else None), 1
    return None, 0


def glyph(src, ch, pick=0):
    kind, key = src
    return real_glyph(key, ch, pick) if kind == "real" else font_glyph(key, ch)


def get_char(srcs, ch, pick=0):
    for s in srcs:
        g, n = glyph(s, ch, pick)
        if g is not None:
            return g, s
    return None, None


# ---------- 纸张与印章 ----------
def paper(w, h, tone=(240, 230, 208), seed=7):
    random.seed(seed)
    base = Image.new("RGB", (w, h), tone)
    noise = Image.effect_noise((w // 4, h // 4), 18).resize((w, h)).filter(ImageFilter.GaussianBlur(2))
    fib = Image.effect_noise((w // 2, h // 2), 30).resize((w, h)).filter(ImageFilter.GaussianBlur(0.8))
    n = ImageChops.blend(noise, fib, 0.4).point(lambda v: 128 + (v - 128) // 4)
    return ImageChops.multiply(base, Image.merge("RGB", [n.point(lambda v: min(255, v + 127))] * 3))


def ink(canvas, mask, box, color=(24, 20, 18), scale=0.86):
    """把墨迹 mask 缩放进 box=(x,y,w,h)"""
    x, y, w, h = box
    mw, mh = mask.size
    r = min(w * scale / mw, h * scale / mh)
    m = mask.resize((max(1, int(mw * r)), max(1, int(mh * r))), Image.LANCZOS)
    px, py = x + (w - m.width) // 2, y + (h - m.height) // 2
    layer = Image.new("RGB", m.size, color)
    canvas.paste(layer, (px, py), m)


def seal(text, size=120):
    text = text[:4]
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    red = (178, 34, 34, 235)
    d.rounded_rectangle([2, 2, size - 3, size - 3], radius=size // 14, fill=red)
    cells = [(1, 0), (1, 1), (0, 0), (0, 1)] if len(text) == 4 else None
    zfont = "FZLiYBZSFU.TTF"
    tt = S2T.convert(text)
    if len(text) == 4:
        cs = size // 2 - 8
        for i, c in enumerate(tt):
            cx, cy = cells[i]
            m, _ = font_glyph("李阳冰篆书", c, 200)
            if m is None:
                m, _ = (lambda f: (f, 1))(_label_glyph(c))
            m = m.resize((cs - 6, cs - 6))
            im.paste((255, 245, 235, 255), (8 + cx * cs + 3, 8 + cy * cs + 3), m)
    else:
        n = len(tt)
        cs = (size - 16) // max(n, 1)
        for i, c in enumerate(tt):
            m, _ = font_glyph("李阳冰篆书", c, 200)
            if m is None:
                m = _label_glyph(c)
            m = m.resize((size - 30, cs - 4))
            im.paste((255, 245, 235, 255), (15, 8 + i * cs + 2), m)
    # 斑驳
    rough = Image.effect_noise((size, size), 60).point(lambda v: 0 if v > 228 else 255)
    a = ImageChops.multiply(im.getchannel("A"), rough)
    im.putalpha(a)
    return im


def _label_glyph(c, size=200):
    f = pfont(LABEL_FONT, size)
    im = Image.new("L", (int(size * 1.3),) * 2, 0)
    ImageDraw.Draw(im).text((size * 0.15, size * 0.1), c, font=f, fill=255)
    return im.crop(im.getbbox() or (0, 0, 1, 1))


def label(d, xy, text, size=26, fill=(60, 50, 40), anchor="la"):
    d.text(xy, text, font=pfont(LABEL_FONT, size), fill=fill, anchor=anchor)


def clean(text):
    return [c for c in text if '\u3400' <= c <= '\u9fff' or '\U00020000' <= c <= '\U0002ffff']


def save(img, name):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, re.sub(r'[\\/:*?"<>| ]', "_", name))
    img.save(p, quality=92)
    return p


# ---------- 命令 ----------
def cmd_list():
    rows = []
    for k, v in REAL.items():
        rows.append((ERA.index(v[2]), v[0], v[1], "真迹", k, v[4]))
    for k, v in FONT.items():
        rows.append((ERA.index(v[2]), v[0], v[1], "字库", k, ""))
    for r in sorted(rows):
        print(f"{ERA[r[0]]}\t{r[1]}\t{r[2]}\t{r[3]}\t{r[4]}\t{r[5]}")
    print(f"TOTAL real={len(REAL)} font={len(FONT)}")


def cmd_char(ch, only=None, per_real=2):
    ch = clean(ch)[0]
    items = []
    srcs = [("real", k) for k in REAL] + [("font", k) for k in FONT]
    for kind, key in srcs:
        meta = REAL[key] if kind == "real" else FONT[key]
        if only and only not in (meta[1], meta[0], key):
            continue
        reps = per_real if kind == "real" else 1
        for i in range(reps):
            g, n = glyph((kind, key), ch, i)
            if g is None or (kind == "real" and i >= n):
                break
            tag = (meta[4] if kind == "real" else key)
            items.append((ERA.index(meta[2]), meta[1], meta[0], tag, kind, g))
    if not items:
        sys.exit(f"NO_GLYPH: {ch}")
    order = {"篆": 0, "隶": 1, "楷": 2, "行": 3, "草": 4}
    items.sort(key=lambda t: (order[t[1]], t[0]))
    cols, cw, chh = 6, 230, 300
    rows = math.ceil(len(items) / cols)
    W, H = cols * cw + 80, rows * chh + 190
    img = paper(W, H)
    d = ImageDraw.Draw(img)
    label(d, (W // 2, 50), f"「{ch}」名家写法对照", 48, (40, 30, 25), "ma")
    label(d, (W // 2, 112), f"共 {len(items)} 种 · 按书体（篆隶楷行草）与年代排列 · 朱框为碑帖真迹，墨框为名家字库", 22, (120, 90, 70), "ma")
    for i, (era, sty, who, tag, kind, g) in enumerate(items):
        x, y = 40 + (i % cols) * cw, 160 + (i // cols) * chh
        box = (x + 15, y + 5, cw - 30, cw - 30)
        frame = (170, 50, 40) if kind == "real" else (90, 80, 70)
        d.rectangle([box[0], box[1], box[0] + box[2], box[1] + box[3]], outline=frame, width=2)
        mx, my = box[0] + box[2] // 2, box[1] + box[3] // 2
        for a, b in [((box[0], my), (box[0] + box[2], my)), ((mx, box[1]), (mx, box[1] + box[3])),
                     ((box[0], box[1]), (box[0] + box[2], box[1] + box[3])), ((box[0] + box[2], box[1]), (box[0], box[1] + box[3]))]:
            d.line([a, b], fill=(225, 180, 165), width=1)
        ink(img, g, box, scale=0.84)
        label(d, (x + cw // 2, y + cw - 18), f"{ERA[era]}·{who}（{sty}）", 21, (50, 40, 35), "ma")
        label(d, (x + cw // 2, y + cw + 8), tag[:12], 17, (130, 100, 80), "ma")
    label(d, (W // 2, H - 30), "名家书法学习馆 · 仅供个人学习临摹", 18, (150, 120, 100), "ma")
    return save(img, f"对照_{ch}{'_' + only if only else ''}.jpg")


def layout_rows(text, n):
    parts = [p for p in re.split(r"[，。！？；、,.!?;：:\s]+", text) if p]
    lens = {len(clean(p)) for p in parts}
    if len(lens) == 1 and list(lens)[0] in (4, 5, 7):
        L = list(lens)[0]
        return L * 2 if n > L * 4 else L * 2 if L != 7 else 14
    return max(6, min(16, math.ceil(math.sqrt(n * 1.6))))


PLAIN = False


def cmd_jizi(text, master, title="", author="", seal_text="", grid=False, trad=False, rows=None, cell=150):
    srcs = resolve(master)
    if trad:
        text, title, author = S2T.convert(text), S2T.convert(title), S2T.convert(author)
    chars = clean(text)
    if not chars:
        sys.exit("EMPTY_TEXT")
    R = rows or layout_rows(text, len(chars))
    body_cols = math.ceil(len(chars) / R)
    extra_r = 1 if title else 0
    extra_l = 1
    C = body_cols + extra_r + extra_l
    mx, my = 110, 120
    W, H = C * cell + mx * 2, R * cell + my * 2 + 40
    img = paper(W, H)
    d = ImageDraw.Draw(img)
    if grid:
        d.rectangle([mx - 14, my - 14, W - mx + 14, my + R * cell + 14], outline=(150, 60, 50), width=3)
        for c in range(1, C):
            x = W - mx - c * cell
            d.line([(x, my - 14), (x, my + R * cell + 14)], fill=(170, 80, 65), width=1)
    missing, used, fallback = [], {}, []
    pick_ctr = {}

    def put(ch, col, row, scale=0.88, size=cell):
        pick_ctr[ch] = pick_ctr.get(ch, -1) + 1  # 同字异形轮换
        g, s = get_char(srcs, ch, pick_ctr[ch])
        if g is None:
            for alt in sorted([("font", k) for k in FONT if FONT[k][1] == (REAL.get(srcs[0][1]) or FONT.get(srcs[0][1]))[1]], key=lambda a: PREF.index(a[1]) if a[1] in PREF else 99):
                g, _ = glyph(alt, ch)
                if g is not None:
                    s = alt
                    break
        if g is None:
            order = {"草": 0, "行": 1, "楷": 2}
            for k in sorted(FONT, key=lambda k: order.get(FONT[k][1], 9)):
                g, _ = glyph(("font", k), ch)
                if g is not None:
                    s = ("font", k)
                    break
        if g is None:
            missing.append(ch)
            return
        used[s[1]] = used.get(s[1], 0) + 1
        x = W - mx - (col + 1) * cell
        y = my + row * cell
        fb = s not in srcs
        if fb:
            fallback.append(ch)
        ink(img, g, (x, y, cell, size), color=(120, 100, 85) if (fb and MARK_FB) else (24, 20, 18), scale=scale)

    col = 0
    if title:
        tc = clean(title)
        for i, ch in enumerate(tc[:R - 1]):
            put(ch, 0, i + 1, 0.8)
        col = 1
    for i, ch in enumerate(chars):
        put(ch, col + i // R, i % R)
    # 落款
    lc = col + body_cols
    sign = clean(author or "")
    sig = sign + (["书"] if author else [])
    start = max(0, R - len(sig) - 2) if sig else 0
    for i, ch in enumerate(sig):
        put(ch, lc, start + i, 0.72)
    st = seal_text or "临池"
    if PLAIN:
        sp = None
    else:
      sp = seal(st, int(cell * 0.75))
    if sp is not None:
        sx = W - mx - (lc + 1) * cell + (cell - sp.width) // 2
        sy = my + (start + len(sig)) * cell + 10 if sig else my + (R - 2) * cell
        img.paste(sp, (sx, min(sy, H - my - sp.height)), sp)
    meta = REAL.get(srcs[0][1]) or FONT.get(srcs[0][1])
    src_txt = "、".join(f"{k}{'(真迹)' if k in REAL else '(字库)'}×{v}" for k, v in used.items())
    if not PLAIN: label(d, (W // 2, H - 52), f"{meta[0]}集字 · {src_txt}", 20, (130, 100, 80), "ma")
    name = f"集字_{meta[0]}_{(clean(title) or chars)[:8] and ''.join((clean(title) or chars)[:8])}.jpg"
    p = save(img, name)
    print(json.dumps({"path": p, "missing": "".join(missing), "fallback": "".join(fallback), "sources": used, "rows": R, "cols": C}, ensure_ascii=False))
    return p


def cmd_practice(text, master, reps=4, cell=260):
    srcs = resolve(master)
    chars = clean(text)[:8]
    W = 70 * 2 + cell * (reps + 1)
    H = 200 + len(chars) * (cell + 40)
    img = paper(W, H, (248, 244, 234))
    d = ImageDraw.Draw(img)
    meta = REAL.get(srcs[0][1]) or FONT.get(srcs[0][1])
    label(d, (W // 2, 50), f"{meta[0]}{meta[1]}书 · 米字格临摹字帖", 44, (40, 30, 25), "ma")
    label(d, (W // 2, 112), "第一格为范字，后面为描红格，由深到浅", 22, (130, 100, 80), "ma")
    miss = []
    for r, ch in enumerate(chars):
        g, s = get_char(srcs, ch)
        y = 170 + r * (cell + 40)
        for k in range(reps + 1):
            x = 70 + k * cell
            d.rectangle([x, y, x + cell, y + cell], outline=(190, 40, 40), width=3)
            for a, b in [((x, y + cell / 2), (x + cell, y + cell / 2)), ((x + cell / 2, y), (x + cell / 2, y + cell)),
                         ((x, y), (x + cell, y + cell)), ((x + cell, y), (x, y + cell))]:
                for t in range(0, cell, 14):  # 虚线
                    p1 = (a[0] + (b[0] - a[0]) * t / cell, a[1] + (b[1] - a[1]) * t / cell)
                    p2 = (a[0] + (b[0] - a[0]) * min(t + 7, cell) / cell, a[1] + (b[1] - a[1]) * min(t + 7, cell) / cell)
                    d.line([p1, p2], fill=(230, 160, 150), width=1)
            if g is None:
                continue
            if k == 0:
                ink(img, g, (x, y, cell, cell), scale=0.86)
            elif k <= 2:
                c = 200 + k * 10 if False else (int(205 + 15 * (k - 1)), int(120 + 40 * (k - 1)), int(110 + 40 * (k - 1)))
                ink(img, g, (x, y, cell, cell), color=c, scale=0.86)
        if g is None:
            miss.append(ch)
    p = save(img, f"字帖_{meta[0]}_{''.join(chars)}.jpg")
    print(json.dumps({"path": p, "missing": "".join(miss)}, ensure_ascii=False))
    return p


def cmd_compare(text, masters, cell=120):
    chars = clean(text)[:14]
    ms = [m.strip() for m in masters.split(",") if m.strip()]
    rows = [(m, resolve(m)) for m in ms]
    head = 200
    W = head + 60 + len(chars) * cell
    H = 130 + len(rows) * (cell + 20) + 40
    img = paper(W, H)
    d = ImageDraw.Draw(img)
    label(d, (W // 2, 36), f"「{''.join(chars)}」名家对照", 40, (40, 30, 25), "ma")
    for r, (m, srcs) in enumerate(rows):
        y = 110 + r * (cell + 20)
        meta = REAL.get(srcs[0][1]) or FONT.get(srcs[0][1])
        label(d, (30, y + cell // 2 - 26), meta[0], 30, (40, 30, 25))
        label(d, (30, y + cell // 2 + 10), f"{meta[2]}·{meta[1]}书", 20, (130, 100, 80))
        d.line([(30, y + cell + 10), (W - 30, y + cell + 10)], fill=(210, 190, 170), width=1)
        for i, ch in enumerate(chars):
            g, s = get_char(srcs, ch)
            if g is not None:
                ink(img, g, (head + i * cell, y, cell, cell), scale=0.84)
            else:
                label(d, (head + i * cell + cell // 2, y + cell // 2), "缺", 22, (190, 160, 140), "mm")
    p = save(img, f"对照_{''.join(chars)[:8]}_{len(rows)}家.jpg")
    print(json.dumps({"path": p}, ensure_ascii=False))
    return p


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "char", "jizi", "practice", "compare"])
    ap.add_argument("text", nargs="?", default="")
    ap.add_argument("--master", default="颜真卿")
    ap.add_argument("--masters", default="王羲之,颜真卿,柳公权,欧阳询,赵孟頫,苏轼,米芾,瘦金体")
    ap.add_argument("--only")
    ap.add_argument("--title", default="")
    ap.add_argument("--author", default="")
    ap.add_argument("--seal", default="")
    ap.add_argument("--grid", action="store_true")
    ap.add_argument("--trad", action="store_true")
    ap.add_argument("--rows", type=int)
    ap.add_argument("--mark", action="store_true", help="补字用浅墨标出")
    ap.add_argument("--plain", action="store_true", help="无印章、无底部注释")
    a = ap.parse_args()
    PLAIN = a.plain
    MARK_FB = a.mark
    if a.cmd == "list":
        cmd_list()
    elif a.cmd == "char":
        print(json.dumps({"path": cmd_char(a.text, a.only)}, ensure_ascii=False))
    elif a.cmd == "jizi":
        cmd_jizi(a.text, a.master, a.title, a.author, a.seal, a.grid, a.trad, a.rows)
    elif a.cmd == "practice":
        cmd_practice(a.text, a.master)
    else:
        cmd_compare(a.text, a.masters)
