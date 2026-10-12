"""After Effects uslubidagi effektlar: kamera, RGB ajralish, glitch, zoom-blur, 3D perspektiva, zarrachalar, nur."""
import math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from mg import (W, H, FPS, BG, NAVY, GOLD, WHITE, RED, GRAY, BLUE, TG, font, clamp, ease_out, ease_in_out, back,
                prog, text_sprite, place, ktext, pill, glass, wrap, subtitle)
import mg

MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
_mc = {}


def mono(s):
    if s not in _mc: _mc[s] = ImageFont.truetype(MONO, s)
    return _mc[s]


def expo_out(t): t = clamp(t); return 1 - 2 ** (-10 * t) if t < 1 else 1.0
def expo_in(t): t = clamp(t); return 2 ** (10 * (t - 1)) if t > 0 else 0.0


# ---------------- fon: hajmli nur + bokeh ----------------
_bg = {}


def _soft(r, col, power=2.0):
    y, x = np.mgrid[-r:r, -r:r]
    a = np.clip(1 - np.sqrt(x * x + y * y) / r, 0, 1) ** power
    arr = np.zeros((2 * r, 2 * r, 4), np.uint8); arr[..., :3] = col; arr[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')


def _init_bg():
    if _bg: return
    y = np.linspace(0, 1, H)[:, None, None]
    top = np.array([10, 12, 24]); bot = np.array([4, 5, 10])
    _bg['base'] = Image.fromarray((top * (1 - y) + bot * y).repeat(W, 1).astype(np.uint8), 'RGB')
    # diagonal nur
    beam = Image.new('L', (W * 2, H * 2), 0); d = ImageDraw.Draw(beam)
    for i, (x, w, a) in enumerate([(700, 160, 26), (1050, 90, 18), (1350, 220, 14)]):
        d.polygon([(x, 0), (x + w, 0), (x + w + 900, H * 2), (x + 900 - w, H * 2)], fill=a)
    _bg['beam'] = beam.filter(ImageFilter.GaussianBlur(60))
    rng = np.random.default_rng(3)
    _bg['bokeh'] = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(8, 40), rng.uniform(0.2, 1.0),
                     rng.choice([0, 1, 2])) for _ in range(34)]
    _bg['dots'] = {k: _soft(40, c, 1.2) for k, c in enumerate([(236, 186, 62), (90, 140, 255), (255, 255, 255)])}
    _bg['glow'] = {'gold': _soft(560, (230, 140, 30)), 'blue': _soft(620, (40, 80, 220)),
                   'red': _soft(520, (210, 40, 50)), 'violet': _soft(560, (120, 60, 220))}
    yy, xx = np.mgrid[0:H, 0:W]
    dd = np.sqrt(((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - H / 2) / (H * 0.66)) ** 2)
    _bg['vig'] = np.clip(1 - (dd - 0.5) * 1.0, 0.35, 1)[..., None].astype(np.float32)
    g = np.random.default_rng(9)
    _bg['grain'] = [g.normal(0, 8, (H // 2, W // 2, 1)).astype(np.int16).repeat(2, 0).repeat(2, 1) for _ in range(6)]


def background(t, mood=('blue', 'gold'), beams=1.0):
    _init_bg()
    c = _bg['base'].convert('RGBA')
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    g1, g2 = _bg['glow'][mood[0]], _bg['glow'][mood[1]]
    lay.alpha_composite(g1, (int(-380 + 140 * math.sin(t * 0.6)), int(-120 + 120 * math.cos(t * 0.5))))
    lay.alpha_composite(g2, (int(420 + 150 * math.cos(t * 0.55)), int(1000 + 140 * math.sin(t * 0.4))))
    lay.putalpha(lay.getchannel('A').point(lambda v: int(v * 0.6)))
    c.alpha_composite(lay)
    if beams:
        off = int((t * 40) % 400)
        bm = _bg['beam'].crop((300 + off, 200, 300 + off + W, 200 + H))
        c.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 255),) * 3 + (bm.point(lambda v: int(v * beams)),)))
    for x, y, r, z, k in _bg['bokeh']:
        yy = (y - t * 30 * z) % (H + 100) - 50; xx = x + 20 * math.sin(t * 0.7 + y)
        s = _bg['dots'][k].resize((int(r * 2), int(r * 2)))
        s.putalpha(s.getchannel('A').point(lambda v: int(v * 0.35 * z)))
        c.alpha_composite(s, (int(xx - r), int(yy - r)))
    return c


# ---------------- kamera va post-effektlar ----------------
def shake(t, hits):
    dx = dy = rot = 0.0
    for at, amp in hits:
        lt = t - at
        if 0 <= lt < 0.6:
            e = math.exp(-lt * 9) * amp
            dx += e * 22 * math.sin(lt * 71 + at); dy += e * 22 * math.cos(lt * 53 + at * 2); rot += e * 1.2 * math.sin(lt * 40)
    return dx, dy, rot


def camera(img, scale=1.0, rot=0.0, dx=0.0, dy=0.0):
    if abs(scale - 1) < 1e-3 and abs(rot) < 1e-3 and abs(dx) < 0.5 and abs(dy) < 0.5: return img
    a = math.radians(rot); ca, sa = math.cos(a) / scale, math.sin(a) / scale
    cx, cy = W / 2, H / 2
    # chiqish (x,y) -> kirish
    m = (ca, sa, cx - ca * (cx + dx) - sa * (cy + dy), -sa, ca, cy + sa * (cx + dx) - ca * (cy + dy))
    return img.transform((W, H), Image.AFFINE, m, resample=Image.BILINEAR)


def zoom_blur(img, amt):
    if amt < 0.02: return img
    acc = np.asarray(img, np.float32); n = 1
    for k in (1, 2, 3, 4):
        s = 1 + amt * 0.06 * k
        z = img.resize((int(W * s), int(H * s)), Image.BILINEAR)
        ox, oy = (z.width - W) // 2, (z.height - H) // 2
        acc = acc + np.asarray(z.crop((ox, oy, ox + W, oy + H)), np.float32); n += 1
    return Image.fromarray((acc / n).astype(np.uint8), img.mode)


def post(img, t, ca=0.0, glitch=0.0, seed=0):
    arr = np.asarray(img.convert('RGB')).copy()
    if ca > 0.3:
        k = int(ca)
        arr[..., 0] = np.roll(arr[..., 0], k, axis=1); arr[..., 2] = np.roll(arr[..., 2], -k, axis=1)
    if glitch > 0.05:
        rng = np.random.default_rng(int(t * FPS) + seed)
        for _ in range(int(6 + 14 * glitch)):
            y = rng.integers(0, H - 80); h = int(rng.integers(8, 70)); sh = int(rng.integers(-120, 120) * glitch)
            arr[y:y + h] = np.roll(arr[y:y + h], sh, axis=1)
            if rng.random() < 0.4: arr[y:y + h, :, rng.integers(0, 3)] = 255
    a = arr.astype(np.float32) * _bg['vig'] + _bg['grain'][int(t * FPS) % 6]
    return np.clip(a, 0, 255).astype(np.uint8)


# ---------------- 3D perspektiva ----------------
def _coeffs(src, dst):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def tilt(spr, rx=0.0, ry=0.0, f=1800.0):
    """spr ni 3D da aylantiradi (gradus). Natija: yangi sprite (markazi saqlanadi)."""
    w, h = spr.size; cx, cy = w / 2, h / 2
    ax, ay = math.radians(rx), math.radians(ry)
    pts = []
    for x, y in [(0, 0), (w, 0), (w, h), (0, h)]:
        X, Y, Z = x - cx, y - cy, 0.0
        X, Z = X * math.cos(ay) + Z * math.sin(ay), -X * math.sin(ay) + Z * math.cos(ay)
        Y, Z = Y * math.cos(ax) - Z * math.sin(ax), Y * math.sin(ax) + Z * math.cos(ax)
        s = f / (f + Z); pts.append((X * s, Y * s))
    mx = min(p[0] for p in pts); my = min(p[1] for p in pts)
    dst = [(p[0] - mx, p[1] - my) for p in pts]
    ow = int(max(p[0] for p in dst)) + 1; oh = int(max(p[1] for p in dst)) + 1
    co = _coeffs([(0, 0), (w, 0), (w, h), (0, h)], dst)
    return spr.transform((ow, oh), Image.PERSPECTIVE, co, resample=Image.BICUBIC)


# ---------------- yozuv effektlari ----------------
def sweep(spr, p, width=140, strength=200):
    """yozuv ustidan diagonal nur o'tadi. p: 0..1"""
    if p <= 0 or p >= 1: return spr
    w, h = spr.size
    band = Image.new('L', (w, h), 0); d = ImageDraw.Draw(band)
    x = -width - h + (w + 2 * width + h) * p
    d.polygon([(x, h), (x + width, h), (x + width + h * 0.6, 0), (x + h * 0.6, 0)], fill=strength)
    band = band.filter(ImageFilter.GaussianBlur(12))
    m = Image.fromarray(np.minimum(np.asarray(band), np.asarray(spr.getchannel('A'))))
    out = spr.copy(); out.alpha_composite(Image.merge('RGBA', (Image.new('L', (w, h), 255),) * 3 + (m,)))
    return out


def outline_sprite(text, w, size, col=WHITE, sw=3):
    k = ('ol', text, w, size, col, sw)
    if k in mg._sc: return mg._sc[k]
    f = font(w, size); tw = int(f.getlength(text)); asc, desc = f.getmetrics()
    im = Image.new('RGBA', (tw + 20, asc + desc + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), text, font=f, fill=(0, 0, 0, 0), stroke_width=sw, stroke_fill=col + (255,))
    mg._sc[k] = im
    return im


def echo(c, t, text, start, cx, cy, size, col=GOLD, w='black', n=3, end=None):
    """kinetik aks-sado: orqasida kontur nusxalar kengayadi"""
    lt = t - start
    if lt < 0: return
    al_end = 1.0
    if end is not None and t > end: al_end = 1 - clamp((t - end) / 0.2)
    o = outline_sprite(text, w, size, col)
    for i in range(n, 0, -1):
        k = expo_out(lt / 0.6)
        place(c, o, cx, cy + i * 0, 1 + 0.09 * i * k, (0.55 - 0.15 * i) * al_end * clamp(lt / 0.2))


def mask_up(c, t, text, start, cx, cy, size, w='black', fill=WHITE, glow=None, end=None):
    """yozuv chiziq ortidan ko'tariladi (niqob)"""
    lt = t - start
    if lt < 0: return
    spr = text_sprite(text, w, size, fill, glow)
    k = expo_out(lt / 0.55)
    oy = int(spr.height * (1 - k))
    al = 1.0 if end is None or t < end else 1 - clamp((t - end) / 0.25)
    if al <= 0: return
    vis = spr.crop((0, 0, spr.width, spr.height - oy)) if oy > 0 else spr
    if vis.height < 2: return
    if al < 1: vis = vis.copy(); vis.putalpha(vis.getchannel('A').point(lambda v: int(v * al)))
    c.alpha_composite(vis, (int(cx - spr.width / 2), int(cy - spr.height / 2 + oy)))


def big(c, t, text, start, cx, cy, size, fill=WHITE, glow=None, w='black', anim='slam', end=None, sw_at=None,
        zoom_out=None):
    """slam + nur o'tishi + yakunda kameraga uchib ketish (zoom_out=vaqt)"""
    lt = t - start
    if lt < 0: return
    spr = text_sprite(text, w, size, fill, glow)
    if sw_at is not None: spr = sweep(spr, (t - sw_at) / 0.7)
    sc, al = 1.0, 1.0
    if anim == 'slam': sc = 1 + 1.6 * (1 - expo_out(lt / 0.3)); al = clamp(lt / 0.08)
    elif anim == 'pop': sc = back(lt / 0.35, 2.0); al = clamp(lt / 0.1)
    elif anim == 'grow': sc = 0.6 + 0.4 * expo_out(lt / 0.5); al = clamp(lt / 0.2)
    if zoom_out is not None and t > zoom_out:
        z = clamp((t - zoom_out) / 0.28); sc *= 1 + 5 * expo_in(z); al *= 1 - z
    if end is not None and t > end: al *= 1 - clamp((t - end) / 0.2)
    sc *= 1 + 0.015 * math.sin(lt * 2.0)
    place(c, spr, cx, cy, sc, al)


# ---------------- zarrachalar ----------------
def burst(c, t, at, x, y, n=46, col=GOLD, speed=900, seed=1):
    lt = t - at
    if lt < 0 or lt > 1.2: return
    rng = np.random.default_rng(seed)
    d = ImageDraw.Draw(c)
    for i in range(n):
        ang = rng.uniform(0, 2 * math.pi); v = rng.uniform(0.3, 1.0) * speed
        k = (1 - math.exp(-lt * 4)) / 4
        px = x + math.cos(ang) * v * k; py = y + math.sin(ang) * v * k + 260 * lt * lt
        r = max(0.5, rng.uniform(3, 9) * (1 - lt / 1.2))
        a = int(255 * (1 - lt / 1.2))
        d.ellipse((px - r * 2.2, py - r * 2.2, px + r * 2.2, py + r * 2.2), fill=col + (a // 5,))
        d.ellipse((px - r, py - r, px + r, py + r), fill=(255, 245, 220, a))


def flare(c, t, at, x, y, dur=0.7, col=(255, 200, 120)):
    lt = t - at
    if lt < 0 or lt > dur: return
    a = math.sin(math.pi * lt / dur)
    k = ('flare', col)
    if k not in mg._sc:
        im = Image.new('RGBA', (1400, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.ellipse((0, 140, 1400, 160), fill=col + (160,))
        im = im.filter(ImageFilter.GaussianBlur(10))
        core = _soft(140, col, 1.6); im.alpha_composite(core, (560, 10))
        mg._sc[k] = im
    s = mg._sc[k].copy(); s.putalpha(s.getchannel('A').point(lambda v: int(v * a)))
    c.alpha_composite(s, (int(x - 700), int(y - 150)))


def flash(c, t, at, dur=0.22, strength=0.5, col=WHITE):
    lt = t - at
    if 0 <= lt < dur:
        c.alpha_composite(Image.new('RGBA', (W, H), col + (int(255 * strength * (1 - lt / dur)),)))


def brackets(c, box, k, col=WHITE, L=70, wdt=7, alpha=255):
    x0, y0, x1, y1 = box; d = ImageDraw.Draw(c); l = L * k; cc = col + (alpha,)
    for (x, y, sx, sy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x1, y1, -1, -1), (x0, y1, 1, -1)]:
        d.line((x, y, x + sx * l, y), fill=cc, width=wdt); d.line((x, y, x, y + sy * l), fill=cc, width=wdt)


def lock_icon(size=220, col=WHITE):
    k = ('lock', size, col)
    if k in mg._sc: return mg._sc[k]
    im = Image.new('RGBA', (size, int(size * 1.25)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    s = size
    d.arc((s * 0.22, s * 0.02, s * 0.78, s * 0.62), 180, 360, fill=col, width=int(s * 0.1))
    d.line((s * 0.22 + s * 0.05, s * 0.32, s * 0.22 + s * 0.05, s * 0.52), fill=col, width=int(s * 0.1))
    d.line((s * 0.78 - s * 0.05, s * 0.32, s * 0.78 - s * 0.05, s * 0.52), fill=col, width=int(s * 0.1))
    d.rounded_rectangle((s * 0.08, s * 0.5, s * 0.92, s * 1.2), int(s * 0.12), fill=col)
    d.ellipse((s * 0.43, s * 0.7, s * 0.57, s * 0.84), fill=BG); d.rectangle((s * 0.475, s * 0.8, s * 0.525, s * 1.0), fill=BG)
    mg._sc[k] = im
    return im


# ---------------- render ----------------
def compose(story, t):
    """story(t) -> dict(world=RGBA, cam=(s,rot,dx,dy), ca, glitch, zblur, mood, overlay=fn(c))"""
    r = story(t)
    c = background(t, r.get('mood', ('blue', 'gold')), r.get('beams', 1.0))
    c.alpha_composite(r['world'])
    s, rot, dx, dy = r.get('cam', (1, 0, 0, 0))
    c = camera(c, s, rot, dx, dy)
    c = zoom_blur(c, r.get('zblur', 0))
    if r.get('overlay'): r['overlay'](c)
    return post(c, t, r.get('ca', 0), r.get('glitch', 0))


def render(story, dur, out, audio):
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
           '-r', str(FPS), '-i', '-', '-i', audio, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264',
           '-preset', 'medium', '-b:v', '6000k', '-maxrate', '8000k', '-bufsize', '12000k', '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(int(round(dur * FPS))):
        p.stdin.write(compose(story, fi / FPS).tobytes())
    p.stdin.close(); p.wait()
