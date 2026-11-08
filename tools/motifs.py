"""Procedural background art for Mühürlü Tarih videos. Each motif returns an RGB PIL image of size (w, h).
Palette: dark ground, aged gold, wax-seal red, cream. All art is generated; no external images."""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GROUND = (20, 17, 15)
GOLD = (201, 165, 92)
SEAL = (122, 28, 28)
CREAM = (233, 225, 210)


def font(name, size, weight=600):
    f = ImageFont.truetype(os.path.join(HERE, 'fonts', name), size)
    try:
        axes = f.get_variation_axes()
        vals = []
        for a in axes:
            vals.append(weight if a['name'] == b'Weight' else a['default'])
        f.set_variation_by_axes(vals)
    except Exception:
        pass
    return f


def mix(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def base(w, h, top=(28, 23, 20), bottom=GROUND):
    img = Image.new('RGB', (w, h), bottom)
    d = ImageDraw.Draw(img)
    for y in range(0, h, 4):
        d.rectangle([0, y, w, y + 4], fill=mix(top, bottom, y / h))
    return img


def finish(img, rnd):
    w, h = img.size
    # vignette
    v = Image.new('L', (w, h), 0)
    dv = ImageDraw.Draw(v)
    for i in range(40):
        t = i / 40
        dv.ellipse([-w * 0.25 + t * w * 0.3, -h * 0.25 + t * h * 0.3, w * 1.25 - t * w * 0.3, h * 1.25 - t * h * 0.3], fill=int(255 * t))
    v = v.filter(ImageFilter.GaussianBlur(min(w, h) // 12))
    dark = Image.new('RGB', (w, h), (6, 5, 4))
    img = Image.composite(img, dark, v)
    # grain
    noise = Image.effect_noise((w // 2, h // 2), 18).resize((w, h)).convert('RGB')
    img = Image.blend(img, noise, 0.04)
    return img


def dust(d, w, h, rnd, n=220, color=GOLD):
    for _ in range(n):
        x, y = rnd.random() * w, rnd.random() * h
        r = rnd.random() * 2.2 + 0.4
        d.ellipse([x - r, y - r, x + r, y + r], fill=mix(GROUND, color, rnd.random() * 0.5 + 0.2))


def stars(d, w, h, rnd, n=300, ymax=1.0):
    for _ in range(n):
        x, y = rnd.random() * w, rnd.random() * h * ymax
        r = rnd.random() * 1.8 + 0.3
        d.ellipse([x - r, y - r, x + r, y + r], fill=mix(GROUND, CREAM, rnd.random() * 0.7 + 0.2))


def ridge(w, base_y, amp, rnd, step=8, rough=0.5):
    pts = []
    y = base_y
    phase = [rnd.random() * 10 for _ in range(4)]
    for x in range(0, w + step, step):
        y = base_y - amp * (0.55 * math.sin(x / w * 3.1 + phase[0]) + 0.3 * math.sin(x / w * 7.3 + phase[1])
                            + 0.15 * math.sin(x / w * 17 + phase[2]) * rough + 0.08 * math.sin(x / w * 41 + phase[3]) * rough)
        pts.append((x, y))
    return pts


def big_text(img, text, frac=0.22, color=GOLD, y=0.5, alpha=0.18):
    w, h = img.size
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    size = int(min(w, h) * frac)
    f = font('Cormorant.ttf', size, 700)
    while d.textlength(text, font=f) > w * 0.9 and size > 20:
        size = int(size * 0.9)
        f = font('Cormorant.ttf', size, 700)
    d.text((w / 2, h * y), text, font=f, fill=color + (int(255 * alpha),), anchor='mm')
    img.paste(layer, (0, 0), layer)


# ---------------- motifs ----------------

def m_mountains(w, h, rnd, p):
    img = base(w, h, (24, 26, 34), (12, 12, 16))
    d = ImageDraw.Draw(img)
    stars(d, w, h, rnd, 260, 0.55)
    mx, my, mr = w * 0.74, h * 0.34, min(w, h) * 0.06
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=mix(CREAM, GOLD, 0.2))
    for i, (by, amp, col) in enumerate([(0.62, 0.2, (40, 42, 52)), (0.72, 0.16, (30, 31, 40)), (0.84, 0.12, (20, 20, 26))]):
        pts = ridge(w, h * by, h * amp, rnd)
        d.polygon(pts + [(w, h), (0, h)], fill=col)
        # snow caps
        for x, y in pts[::3]:
            if y < h * by - h * amp * 0.5:
                d.line([(x - 6, y + 6), (x, y), (x + 6, y + 6)], fill=mix(col, CREAM, 0.5), width=2)
    if p.get('tent'):
        tx, ty = w * 0.4, h * 0.8
        s = min(w, h) * 0.07
        d.polygon([(tx - s, ty), (tx, ty - s * 0.8), (tx + s, ty)], fill=mix(GROUND, GOLD, 0.35))
        d.line([(tx + s * 0.2, ty - s * 0.6), (tx + s * 0.35, ty - s * 0.1)], fill=GROUND, width=4)
    for _ in range(500):
        x, y = rnd.random() * w, rnd.random() * h
        r = rnd.random() * 2 + 0.5
        d.ellipse([x - r, y - r, x + r, y + r], fill=mix(GROUND, CREAM, 0.6))
    return img


def m_parchment(w, h, rnd, p):
    img = base(w, h, (74, 58, 38), (48, 36, 24))
    d = ImageDraw.Draw(img)
    # stains
    for _ in range(30):
        x, y, r = rnd.random() * w, rnd.random() * h, rnd.random() * min(w, h) * 0.2
        d.ellipse([x - r, y - r, x + r, y + r], fill=mix((60, 46, 30), (90, 72, 48), rnd.random()))
    img = img.filter(ImageFilter.GaussianBlur(min(w, h) // 30))
    d = ImageDraw.Draw(img)
    ink = (38, 26, 18)
    # invented script lines
    lh = min(w, h) * 0.045
    y = h * 0.1
    while y < h * 0.9:
        x = w * 0.08
        while x < w * 0.9:
            gw = lh * (0.5 + rnd.random() * 0.6)
            pts = [(x + gw * i / 5, y + math.sin(i * 1.7 + rnd.random() * 3) * lh * 0.25 + rnd.random() * lh * 0.15) for i in range(6)]
            d.line(pts, fill=ink, width=max(2, int(lh * 0.08)))
            if rnd.random() < 0.35:
                d.arc([x, y - lh * 0.4, x + gw * 0.5, y + lh * 0.1], 180, 360, fill=ink, width=max(2, int(lh * 0.07)))
            x += gw + lh * 0.25 * (2 if rnd.random() < 0.2 else 1)
        y += lh * 1.6
    if p.get('plant', True):
        cx, cy = w * 0.5, h * 0.55
        s = min(w, h) * 0.3
        green = (70, 84, 50)
        d.line([(cx, cy + s), (cx, cy - s * 0.4)], fill=green, width=6)
        for i in range(7):
            a = -math.pi / 2 + (i - 3) * 0.45
            ex, ey = cx + math.cos(a) * s * 0.7, cy - s * 0.2 + math.sin(a) * s * 0.5
            d.ellipse([ex - s * 0.12, ey - s * 0.06, ex + s * 0.12, ey + s * 0.06], fill=green)
        d.ellipse([cx - s * 0.12, cy - s * 0.6, cx + s * 0.12, cy - s * 0.36], fill=(120, 50, 40))
        for i in range(5):
            d.line([(cx, cy + s), (cx + (i - 2) * s * 0.15, cy + s * 1.15)], fill=green, width=3)
    return img


def m_map(w, h, rnd, p):
    img = base(w, h, (34, 30, 24), (22, 19, 16))
    d = ImageDraw.Draw(img)
    # grid
    for x in range(0, w, int(min(w, h) / 8)):
        d.line([(x, 0), (x, h)], fill=(40, 35, 28), width=1)
    for y in range(0, h, int(min(w, h) / 8)):
        d.line([(0, y), (w, y)], fill=(40, 35, 28), width=1)
    # coastline
    cx = w * (0.45 + rnd.random() * 0.1)
    pts = []
    for y in range(-20, h + 40, 12):
        cx += (rnd.random() - 0.5) * 40
        pts.append((cx + 80 * math.sin(y / 130), y))
    d.polygon(pts + [(w + 10, h + 40), (w + 10, -20)], fill=(30, 36, 40))
    for k in range(1, 5):
        d.line([(x + k * 18, y) for x, y in pts], fill=mix((30, 36, 40), GOLD, 0.25 / k), width=2)
    d.line(pts, fill=GOLD, width=3)
    # islands
    for _ in range(4):
        ix, iy = cx + w * 0.1 + rnd.random() * w * 0.25, rnd.random() * h
        r = rnd.random() * 25 + 10
        d.ellipse([ix - r * 1.6, iy - r, ix + r * 1.6, iy + r], outline=GOLD, width=2, fill=(34, 30, 24))
    # dotted route
    x0, y0 = w * 0.15, h * 0.8
    x1, y1 = w * 0.8, h * 0.25
    for i in range(40):
        t = i / 40
        x = x0 + (x1 - x0) * t + math.sin(t * 6) * 60
        y = y0 + (y1 - y0) * t
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=SEAL)
    # compass
    cxp, cyp, r = w * 0.18, h * 0.2, min(w, h) * 0.09
    d.ellipse([cxp - r, cyp - r, cxp + r, cyp + r], outline=GOLD, width=3)
    for a in range(0, 360, 90):
        ra = math.radians(a)
        d.polygon([(cxp + math.cos(ra) * r * 1.2, cyp + math.sin(ra) * r * 1.2),
                   (cxp + math.cos(ra + 1.4) * r * 0.2, cyp + math.sin(ra + 1.4) * r * 0.2),
                   (cxp + math.cos(ra - 1.4) * r * 0.2, cyp + math.sin(ra - 1.4) * r * 0.2)], fill=GOLD)
    if p.get('x'):
        d.line([(x1 - 25, y1 - 25), (x1 + 25, y1 + 25)], fill=SEAL, width=10)
        d.line([(x1 - 25, y1 + 25), (x1 + 25, y1 - 25)], fill=SEAL, width=10)
    return img


def m_forest(w, h, rnd, p):
    img = base(w, h, (26, 30, 26), (12, 14, 12))
    d = ImageDraw.Draw(img)
    stars(d, w, h, rnd, 120, 0.4)
    for layer, col in enumerate([(30, 36, 30), (22, 26, 22), (14, 16, 14)]):
        for _ in range(26 + layer * 6):
            x = rnd.random() * w
            th = h * (0.35 + rnd.random() * 0.3) * (1 + layer * 0.2)
            bw = th * 0.25
            by = h * (0.8 + layer * 0.08)
            d.polygon([(x, by - th), (x - bw, by), (x + bw, by)], fill=col)
    if p.get('carve'):
        txt = p['carve']
        pw, ph = min(w, h) * 0.16, h * 0.55
        px, py = w * 0.5 - pw / 2, h * 0.38
        for k in range(-3, 4):  # palisade wall of posts
            qx = px + k * pw * 0.62
            qy = py + abs(k) * ph * 0.03 + rnd.random() * ph * 0.04
            col = mix((70, 52, 34), (40, 30, 20), abs(k) / 4)
            d.polygon([(qx, qy + pw * 0.2), (qx + pw * 0.3, qy), (qx + pw * 0.6, qy + pw * 0.2), (qx + pw * 0.6, py + ph), (qx, py + ph)], fill=col)
            d.line([(qx + pw * 0.6, qy + pw * 0.2), (qx + pw * 0.6, py + ph)], fill=(20, 14, 10), width=3)
        # horizontal carved board on the post
        bw_, bh_ = min(w, h) * 0.62, min(w, h) * 0.13
        bx, by_ = w * 0.5 - bw_ / 2, py + ph * 0.18
        d.rectangle([bx + 8, by_ + 8, bx + bw_ + 8, by_ + bh_ + 8], fill=(8, 6, 4))
        d.rectangle([bx, by_, bx + bw_, by_ + bh_], fill=(92, 68, 44))
        for i in range(5):
            yy = by_ + bh_ * (i + 0.5) / 5
            d.line([(bx, yy), (bx + bw_, yy + rnd.random() * 4)], fill=(80, 58, 38), width=2)
        size = int(bh_ * 0.7)
        f = font('Cormorant.ttf', size, 700)
        while d.textlength(txt, font=f) > bw_ * 0.9:
            size -= 2; f = font('Cormorant.ttf', size, 700)
        d.text((w * 0.5 + 2, by_ + bh_ / 2 + 2), txt, font=f, fill=(150, 120, 80), anchor='mm')
        d.text((w * 0.5, by_ + bh_ / 2), txt, font=f, fill=(28, 18, 10), anchor='mm')
    d.rectangle([0, h * 0.92, w, h], fill=(10, 11, 10))
    return img


def m_pillars(w, h, rnd, p):
    img = base(w, h, (52, 36, 26), (18, 14, 12))
    d = ImageDraw.Draw(img)
    # sunrise glow
    sx, sy = w * 0.5, h * 0.72
    for i in range(30, 0, -1):
        r = min(w, h) * 0.02 * i
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=mix((18, 14, 12), (150, 90, 50), (30 - i) / 45))
    d.rectangle([0, h * 0.72, w, h], fill=(26, 20, 16))
    # enclosure ring
    d.ellipse([w * 0.08, h * 0.66, w * 0.92, h * 0.92], outline=(60, 46, 34), width=8)
    n = p.get('count', 7)
    for i in range(n):
        a = math.pi * (i + 0.5) / n
        x = w * 0.5 - math.cos(a) * w * 0.4
        y = h * 0.79 + math.sin(a) * h * 0.1
        s = min(w, h) * (0.18 + 0.06 * math.sin(a))
        col = mix((70, 56, 42), (120, 96, 70), math.sin(a))
        d.rectangle([x - s * 0.12, y - s * 1.6, x + s * 0.12, y], fill=col)
        d.rectangle([x - s * 0.38, y - s * 1.9, x + s * 0.38, y - s * 1.55], fill=col)
        if rnd.random() < 0.6:
            d.arc([x - s * 0.08, y - s * 1.2, x + s * 0.08, y - s * 0.9], 0, 300, fill=mix(col, GROUND, 0.5), width=3)
    # central pair
    for dx in (-1, 1):
        x, y = w * 0.5 + dx * w * 0.07, h * 0.84
        s = min(w, h) * 0.32
        col = (150, 122, 88)
        d.rectangle([x - s * 0.1, y - s * 1.5, x + s * 0.1, y], fill=col)
        d.rectangle([x - s * 0.32, y - s * 1.75, x + s * 0.32, y - s * 1.45], fill=col)
        d.line([(x - s * 0.08, y - s * 0.5), (x + s * 0.08, y - s * 0.5)], fill=(110, 86, 60), width=6)
    return img


def m_stars(w, h, rnd, p):
    img = base(w, h, (16, 18, 30), (8, 8, 14))
    d = ImageDraw.Draw(img)
    stars(d, w, h, rnd, 700)
    pts = [(rnd.random() * w, rnd.random() * h * 0.7) for _ in range(7)]
    d.line(pts, fill=mix(GROUND, GOLD, 0.6), width=2)
    for x, y in pts:
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=GOLD)
    pts = ridge(w, h * 0.9, h * 0.06, rnd)
    d.polygon(pts + [(w, h), (0, h)], fill=(10, 10, 12))
    return img


def m_sea(w, h, rnd, p):
    img = base(w, h, (24, 30, 38), (10, 14, 20))
    d = ImageDraw.Draw(img)
    stars(d, w, h, rnd, 150, 0.4)
    hy = h * 0.55
    d.rectangle([0, hy, w, h], fill=(14, 20, 28))
    for i in range(40):
        y = hy + (h - hy) * (i / 40) ** 1.5
        amp = 3 + i * 0.6
        pts = [(x, y + math.sin(x / (40 + i * 3) + i) * amp) for x in range(0, w + 10, 10)]
        d.line(pts, fill=mix((14, 20, 28), GOLD, 0.08 + 0.004 * i), width=2)
    if p.get('ship', True):
        sx, sy, s = w * 0.55, hy + 10, min(w, h) * 0.2
        d.polygon([(sx - s, sy - s * 0.1), (sx + s, sy - s * 0.1), (sx + s * 0.7, sy + s * 0.12), (sx - s * 0.75, sy + s * 0.12)], fill=(8, 8, 10))
        for mxx, mh in [(-0.4, 1.0), (0.1, 1.2), (0.55, 0.8)]:
            x = sx + mxx * s
            d.line([(x, sy - s * 0.1), (x, sy - s * mh)], fill=(8, 8, 10), width=5)
            d.polygon([(x + 3, sy - s * mh * 0.95), (x + s * 0.3, sy - s * mh * 0.5), (x + 3, sy - s * 0.2)], fill=(30, 30, 32))
    return img


def m_ruins(w, h, rnd, p):
    img = base(w, h, (46, 38, 30), (16, 13, 11))
    d = ImageDraw.Draw(img)
    d.rectangle([0, h * 0.78, w, h], fill=(28, 22, 18))
    n = 6
    for i in range(n):
        x = w * (0.1 + 0.8 * i / (n - 1))
        cw = min(w, h) * 0.07
        ch = h * (0.25 + rnd.random() * 0.35)
        col = mix((90, 76, 60), (130, 110, 86), rnd.random())
        top = h * 0.78 - ch
        d.rectangle([x - cw / 2, top, x + cw / 2, h * 0.78], fill=col)
        for k in range(4):
            xx = x - cw / 2 + cw * (k + 0.5) / 4
            d.line([(xx, top), (xx, h * 0.78)], fill=mix(col, GROUND, 0.3), width=3)
        d.polygon([(x - cw / 2, top), (x + cw / 2, top), (x + cw * 0.2, top - cw * 0.5 * rnd.random())], fill=col)
    for _ in range(14):
        x, y = rnd.random() * w, h * 0.8 + rnd.random() * h * 0.15
        s = rnd.random() * 40 + 15
        d.rectangle([x, y, x + s * 1.5, y + s * 0.6], fill=(80, 68, 54))
    return img


def m_document(w, h, rnd, p):
    img = base(w, h, (30, 27, 24), (14, 12, 11))
    d = ImageDraw.Draw(img)
    pw, ph = min(w * 0.7, h * 0.55), min(w * 0.7, h * 0.55) * 1.35
    px, py = (w - pw) / 2, (h - ph) / 2
    d.rectangle([px + 14, py + 14, px + pw + 14, py + ph + 14], fill=(6, 5, 4))
    d.rectangle([px, py, px + pw, py + ph], fill=(206, 194, 168))
    y = py + ph * 0.12
    while y < py + ph * 0.88:
        x = px + pw * 0.08
        while x < px + pw * 0.88:
            lw = pw * (0.05 + rnd.random() * 0.14)
            col = (20, 18, 16) if rnd.random() < 0.18 else (110, 100, 86)
            hh = ph * 0.025 if col[0] == 20 else ph * 0.008
            d.rectangle([x, y, min(x + lw, px + pw * 0.92), y + hh], fill=col)
            x += lw + pw * 0.02
        y += ph * 0.045
    # stamp
    sx, sy, r = px + pw * 0.75, py + ph * 0.18, pw * 0.12
    d.ellipse([sx - r, sy - r, sx + r, sy + r], outline=SEAL, width=6)
    if p.get('stamp'):
        f = font('Cormorant.ttf', int(r * 0.45), 700)
        d.text((sx, sy), p['stamp'], font=f, fill=SEAL, anchor='mm')
    return img


def m_seal(w, h, rnd, p):
    img = base(w, h)
    d = ImageDraw.Draw(img)
    dust(d, w, h, rnd, 160)
    cx, cy, r = w / 2, h / 2, min(w, h) * 0.22
    pts = []
    for i in range(361):
        a = math.radians(i)
        rr = r + r * 0.09 * (0.5 + 0.5 * math.cos(18 * a)) ** 0.6
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=SEAL)
    d.ellipse([cx - r * 0.8, cy - r * 0.8, cx + r * 0.8, cy + r * 0.8], outline=GOLD, width=max(3, int(r * 0.02)))
    f = font('Cormorant.ttf', int(r * 0.85), 700)
    d.text((cx, cy), 'MT', font=f, fill=GOLD, anchor='mm')
    for k in range(1, 4):
        rr = r * (1.3 + 0.35 * k)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=mix(GROUND, GOLD, 0.15), width=2)
    return img


def m_question(w, h, rnd, p):
    img = base(w, h)
    d = ImageDraw.Draw(img)
    dust(d, w, h, rnd, 260)
    cx, cy, r = w / 2, h / 2, min(w, h) * 0.3
    for k in range(3):
        rr = r * (1 + 0.18 * k)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=mix(GROUND, GOLD, 0.5 - 0.15 * k), width=3)
    f = font('Cormorant.ttf', int(r * 1.4), 700)
    d.text((cx, cy + r * 0.05), p.get('glyph', '?'), font=f, fill=GOLD, anchor='mm')
    return img


def m_hourglass(w, h, rnd, p):
    img = base(w, h)
    d = ImageDraw.Draw(img)
    dust(d, w, h, rnd, 200)
    cx, cy, s = w / 2, h / 2, min(w, h) * 0.3
    d.rectangle([cx - s * 0.7, cy - s * 1.2, cx + s * 0.7, cy - s * 1.1], fill=GOLD)
    d.rectangle([cx - s * 0.7, cy + s * 1.1, cx + s * 0.7, cy + s * 1.2], fill=GOLD)
    d.polygon([(cx - s * 0.55, cy - s * 1.1), (cx + s * 0.55, cy - s * 1.1), (cx + s * 0.06, cy), (cx - s * 0.06, cy)], outline=CREAM, width=4)
    d.polygon([(cx - s * 0.55, cy + s * 1.1), (cx + s * 0.55, cy + s * 1.1), (cx + s * 0.06, cy), (cx - s * 0.06, cy)], outline=CREAM, width=4)
    d.polygon([(cx - s * 0.3, cy - s * 0.55), (cx + s * 0.3, cy - s * 0.55), (cx, cy - s * 0.02)], fill=GOLD)
    d.polygon([(cx - s * 0.5, cy + s * 1.08), (cx + s * 0.5, cy + s * 1.08), (cx, cy + s * 0.55)], fill=GOLD)
    d.line([(cx, cy), (cx, cy + s * 0.6)], fill=GOLD, width=3)
    return img


def m_year(w, h, rnd, p):
    img = m_seal(w, h, rnd, p) if p.get('on') == 'seal' else base(w, h)
    d = ImageDraw.Draw(img)
    dust(d, w, h, rnd, 200)
    big_text(img, p.get('year', '?'), 0.3, GOLD, 0.5, 0.85)
    d.line([(w * 0.2, h * 0.68), (w * 0.8, h * 0.68)], fill=mix(GROUND, GOLD, 0.5), width=3)
    return img


MOTIFS = {k[2:]: v for k, v in globals().items() if k.startswith('m_')}


def make(motif, w, h, seed=0, **p):
    rnd = random.Random(seed)
    img = MOTIFS[motif](w, h, rnd, p)
    if p.get('watermark'):
        big_text(img, p['watermark'], 0.16, GOLD, 0.5, 0.12)
    return finish(img, rnd)


if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/motifs'
    os.makedirs(out, exist_ok=True)
    for name in MOTIFS:
        make(name, 1080, 1920, 1, carve='CROATOAN', tent=True, year='1959').save(f'{out}/{name}.jpg', quality=85)
    print(sorted(MOTIFS))
