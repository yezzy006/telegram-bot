"""Birbalo motion grafika dvigateli: kinetik yozuv, shisha kartochka, glow, grain -> 1080x1920 istoriya."""
import math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
BG = (7, 9, 15); NAVY = (19, 35, 75); GOLD = (236, 186, 62); WHITE = (255, 255, 255)
RED = (226, 58, 58); GRAY = (165, 174, 192); BLUE = (64, 120, 255); TG = (42, 171, 238)
FD = '/usr/share/fonts/opentype/inter/'
FONTS = {'black': FD + 'InterDisplay-Black.otf', 'xbold': FD + 'InterDisplay-ExtraBold.otf',
         'bold': FD + 'InterDisplay-Bold.otf', 'semi': FD + 'InterDisplay-SemiBold.otf'}
_fc, _sc = {}, {}


def font(w, s):
    k = (w, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(FONTS[w], s)
    return _fc[k]


def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(t): return 1 - (1 - clamp(t)) ** 3
def ease_in_out(t): t = clamp(t); return 3 * t * t - 2 * t * t * t
def back(t, s=1.8):
    t = clamp(t) - 1; return t * t * ((s + 1) * t + s) + 1
def prog(t, start, dur): return clamp((t - start) / dur)


# ---------- fon ----------
def _blob(r, col):
    y, x = np.mgrid[-r:r, -r:r]
    d = np.sqrt(x * x + y * y) / r
    a = np.clip(1 - d, 0, 1) ** 2.2
    arr = np.zeros((2 * r, 2 * r, 4), np.uint8)
    arr[..., :3] = col; arr[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')

_BASE = None; _GRAIN = None; _BLOBS = None; _VIG = None

def _init():
    global _BASE, _GRAIN, _BLOBS, _VIG
    if _BASE is not None: return
    y = np.linspace(0, 1, H)[:, None, None]
    top = np.array([12, 16, 30]); bot = np.array(BG)
    _BASE = (top * (1 - y) + bot * y).repeat(W, 1).astype(np.uint8)
    rng = np.random.default_rng(7)
    _GRAIN = [rng.normal(0, 7, (H // 2, W // 2, 1)).astype(np.int16) for _ in range(6)]
    _BLOBS = {'gold': _blob(520, (226, 140, 40)), 'blue': _blob(600, (40, 80, 210)),
              'red': _blob(480, (200, 40, 50))}
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2)
    _VIG = np.clip(1 - (d - 0.55) * 0.9, 0.45, 1)[..., None].astype(np.float32)


def background(t, mood=('blue', 'gold'), strength=0.55):
    _init()
    c = Image.fromarray(_BASE, 'RGB').convert('RGBA')
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    b1 = _BLOBS[mood[0]]; b2 = _BLOBS[mood[1]]
    lay.alpha_composite(b1, (int(-250 + 120 * math.sin(t * 0.5)), int(150 + 90 * math.cos(t * 0.4))))
    lay.alpha_composite(b2, (int(500 + 110 * math.cos(t * 0.45)), int(1050 + 120 * math.sin(t * 0.35))))
    a = lay.getchannel('A').point(lambda v: int(v * strength)); lay.putalpha(a)
    c.alpha_composite(lay)
    # nozik to'r
    d = ImageDraw.Draw(c)
    off = int(t * 12) % 90
    for x in range(-90 + off, W, 90): d.line((x, 0, x, H), fill=(255, 255, 255, 9))
    for y in range(-90 + off, H, 90): d.line((0, y, W, y), fill=(255, 255, 255, 9))
    return c


def finish(c, t):
    """grain + vinyetka -> RGB bytes"""
    arr = np.asarray(c.convert('RGB')).astype(np.float32) * _VIG
    g = _GRAIN[int(t * FPS) % len(_GRAIN)]
    g = g.repeat(2, 0).repeat(2, 1)
    arr = np.clip(arr + g, 0, 255).astype(np.uint8)
    return arr.tobytes()


# ---------- yozuv ----------
def text_sprite(text, w, size, fill=WHITE, glow=None, track=0, stroke=0, stroke_fill=(0, 0, 0)):
    k = ('t', text, w, size, fill, glow, track, stroke)
    if k in _sc: return _sc[k]
    f = font(w, size)
    if track:
        tw = sum(f.getlength(ch) + track for ch in text) - track
    else:
        tw = f.getlength(text)
    asc, desc = f.getmetrics()
    pad = 60 if glow else 10 + stroke
    im = Image.new('RGBA', (int(tw) + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if track:
        x = pad
        for ch in text:
            d.text((x, pad), ch, font=f, fill=fill + (255,)); x += f.getlength(ch) + track
    else:
        d.text((pad, pad), text, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=stroke_fill)
    if glow:
        gl = Image.new('RGBA', im.size, (210, 120, 20, 0))
        gl.putalpha(im.getchannel('A').filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * 0.75)))
        base = Image.new('RGBA', im.size, (0, 0, 0, 0)); base.alpha_composite(gl); base.alpha_composite(im); im = base
    _sc[k] = im
    return im


def place(c, spr, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if alpha <= 0.01 or scale <= 0.02: return
    s = spr
    if rot: s = s.rotate(rot, resample=Image.BICUBIC, expand=True)
    if abs(scale - 1) > 0.005:
        s = s.resize((max(1, int(s.width * scale)), max(1, int(s.height * scale))), Image.BILINEAR)
    if alpha < 0.999:
        s = s.copy(); s.putalpha(s.getchannel('A').point(lambda v: int(v * alpha)))
    c.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))


def ktext(c, t, text, start, cx, cy, size=120, w='black', fill=WHITE, glow=None, anim='pop',
          end=None, track=0, rot=0.0, stroke=0):
    """kinetik yozuv. anim: pop / rise / slam / none"""
    lt = t - start
    if lt < 0: return
    spr = text_sprite(text, w, size, fill, glow, track, stroke)
    sc, al, dy = 1.0, 1.0, 0
    if anim == 'pop': sc = back(lt / 0.32, 2.2); al = clamp(lt / 0.12)
    elif anim == 'rise': dy = 70 * (1 - ease_out(lt / 0.4)); al = clamp(lt / 0.25)
    elif anim == 'slam': sc = 1 + 1.4 * (1 - ease_out(lt / 0.22)); al = clamp(lt / 0.1)
    if end is not None and t > end:
        e = clamp((t - end) / 0.25); al *= 1 - e; sc *= 1 - 0.2 * e
    place(c, spr, cx, cy + dy, sc, al, rot)


def pill(c, t, text, start, cx, cy, size=56, bg=GOLD, fg=BG, w='black', rot=0.0, end=None, padx=38, pady=20,
         outline=None):
    lt = t - start
    if lt < 0: return
    k = ('p', text, size, bg, fg, w, padx, pady, outline)
    if k not in _sc:
        f = font(w, size); tw = f.getlength(text); asc, desc = f.getmetrics()
        bw, bh = int(tw + padx * 2), int(asc + desc + pady * 2 - size * 0.18)
        im = Image.new('RGBA', (bw + 20, bh + 26), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((10, 18, bw + 10, bh + 18), bh // 2, fill=(0, 0, 0, 120))
        d.rounded_rectangle((10, 8, bw + 10, bh + 8), bh // 2, fill=bg + (255,) if len(bg) == 3 else bg,
                            outline=outline, width=4 if outline else 0)
        d.text((10 + padx, 8 + pady - size * 0.12), text, font=f, fill=fg)
        _sc[k] = im
    sc = back(lt / 0.32, 2.4); al = clamp(lt / 0.1)
    if end is not None and t > end:
        e = clamp((t - end) / 0.25); al *= 1 - e
    place(c, _sc[k], cx, cy, sc, al, rot)


def glass(c, box, radius=36, alpha=1.0, border=(255, 255, 255, 40), fill=(255, 255, 255, 16), blur_bg=True):
    x0, y0, x1, y1 = [int(v) for v in box]
    if alpha <= 0.01: return
    if blur_bg:
        reg = c.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(18))
        m = Image.new('L', reg.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, reg.width - 1, reg.height - 1), radius, fill=int(255 * alpha))
        c.paste(reg, (x0, y0), m)
    lay = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = fill[:3] + (int(fill[3] * alpha),); b = border[:3] + (int(border[3] * alpha),)
    d.rounded_rectangle((0, 0, lay.width - 1, lay.height - 1), radius, fill=f, outline=b, width=3)
    c.alpha_composite(lay, (x0, y0))


def flash(c, t, at, dur=0.25, strength=0.35, col=WHITE):
    lt = t - at
    if 0 <= lt < dur:
        a = int(255 * strength * (1 - lt / dur))
        c.alpha_composite(Image.new('RGBA', (W, H), col + (a,)))


def brand(c):
    pill_static = ('brand',)
    if pill_static not in _sc:
        f = font('xbold', 30); a, b = '@birbalo_ai', '  ·  AI STUDIYA'
        w = int(f.getlength(a + b) + 48)
        im = Image.new('RGBA', (w, 58), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, 57), 29, fill=(255, 255, 255, 22), outline=(255, 255, 255, 50), width=2)
        d.text((24, 11), a, font=f, fill=GOLD); d.text((24 + f.getlength(a), 11), b, font=f, fill=(225, 228, 235))
        _sc[pill_static] = im
    s = _sc[pill_static]; c.alpha_composite(s, ((W - s.width) // 2, 236))


def wrap(text, f, maxw):
    lines, cur = [], ''
    for wd in text.split():
        tst = (cur + ' ' + wd).strip()
        if f.getlength(tst) <= maxw or not cur: cur = tst
        else: lines.append(cur); cur = wd
    if cur: lines.append(cur)
    return lines


def subtitle(c, t, caps, y=1585, size=46):
    for txt, s, e in caps:
        if s <= t < e + 0.15:
            f = font('bold', size)
            words = txt.split(); n = len(words)
            k = clamp((t - s) / max(0.2, (e - s) * 0.92))
            shown = n if t >= e else max(1, int(k * n) + 1)
            lines = wrap(txt, f, 900)
            d = ImageDraw.Draw(c); idx = 0
            for i, l in enumerate(lines):
                x = (W - f.getlength(l)) / 2
                for wd in l.split():
                    col = GOLD if idx == shown - 1 and t < e else (WHITE if idx < shown else (150, 155, 165))
                    d.text((x, y + i * int(size * 1.3)), wd, font=f, fill=col, stroke_width=6, stroke_fill=(0, 0, 0))
                    x += f.getlength(wd + ' '); idx += 1
            return


def render(draw, dur, out, audio, mood=('blue', 'gold')):
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
           '-r', str(FPS), '-i', '-', '-i', audio, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264',
           '-preset', 'medium', '-b:v', '5000k', '-maxrate', '6500k', '-bufsize', '9000k', '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(int(round(dur * FPS))):
        t = fi / FPS
        c = background(t, mood)
        draw(c, t)
        brand(c)
        p.stdin.write(finish(c, t))
    p.stdin.close(); p.wait()


def frame(draw, t, mood=('blue', 'gold')):
    c = background(t, mood); draw(c, t); brand(c)
    return Image.frombytes('RGB', (W, H), finish(c, t))
