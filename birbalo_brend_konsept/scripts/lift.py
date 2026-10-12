"""Tungi g'aroyibotlar — surreal tungi sahnalar, eski plyonka uslubi. python3 scripts/lift.py sheet|render"""
import sys, os, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from fx import shake, camera, zoom_blur, expo_out, expo_in
from mg import W, H, FPS, clamp, place
import mg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'lift', 'src'); OUT = os.path.join(ROOT, 'lift')
SR = 44100
SERIF_I = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'
SERIF_B = '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'
_f = {}


def sfont(p, s):
    if (p, s) not in _f: _f[(p, s)] = ImageFont.truetype(p, s)
    return _f[(p, s)]


# (fayl, boshlanish, davomiylik, src(u), o'tish turi kirishda)
CLIPS = [
    ('Old_man_standing_in_fog', 0.0, 2.5, lambda u: 0.3 + u * 1.2, None),
    ('Finger_presses_illuminated_button', 2.5, 2.0, lambda u: 0.6 + u * 1.3, 'zoom'),
    ('Horse_bursts_from_elevator', 4.5, 3.5, lambda u: u * 1.1, 'burn'),
    ('Man_checking_pocket_watch', 8.0, 2.5, lambda u: 0.5 + u * 1.2, 'flicker'),
    ('Full_moon_rises_from_tandoor', 10.5, 4.0, lambda u: u * 2.0, 'iris'),
    ('Woman_lifts_fog_into_bag', 14.5, 4.0, lambda u: u * 2.0, 'fog'),
    ('Water_pouring_from_television', 18.5, 4.0, lambda u: 2.0 + u, 'whip'),
    ('Young_man_turning_head', 22.5, 4.0, lambda u: u * 1.5, 'flicker'),
    ('Books_and_lamp_moving', 26.5, 4.0, lambda u: u * 1.5, 'zoom'),
    ('Camera_pushes_toward_mirror', 30.5, 4.0, lambda u: u * 2.0, 'burn'),
]
END0 = 34.5; DUR = 38.5
LINES = [  # (global vaqt, narr boshi, narr oxiri, subtitr)
    (0.2, 0.0, 2.16, "Bu shaharda tunlar boshqacha."),
    (2.6, 2.79, 4.69, "Bir qavatli uyda lift bor."),
    (5.3, 5.22, 6.75, "Bugun undan ot chiqdi."),
    (8.3, 7.32, 8.46, "Chol ajablanmadi."),
    (10.9, 9.01, 10.42, "Nonvoy tandir yoqdi."),
    (12.6, 10.89, 12.51, "Bugun undan oy chiqdi."),
    (15.0, 13.21, 15.75, "Tunda bozorda tuman kilolab sotiladi."),
    (18.8, 16.37, 18.03, "Buvi televizor ko'radi."),
    (20.7, 18.52, 20.0, "Bugun dengiz haqida."),
    (22.8, 20.59, 21.67, "Telefon jiringladi."),
    (24.1, 22.17, 24.18, "Qo'ng'iroq qilgan odam, o'zi edi."),
    (27.2, 24.75, 26.83, "Kitoblar tunda uyiga qaytadi."),
    (31.0, 27.46, 30.16, "Bu to'yxonada to'y hech qachon tugamagan."),
    (35.6, 30.78, 32.8, "Yaxshisi, bugun uxlamang."),
]
NARR = os.path.join(OUT, 'voice', 'narr.mp3')

_cur = {'name': None}


def frames(name):
    if _cur['name'] != name:
        raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', os.path.join(SRC, name + '.mp4'), '-f', 'rawvideo',
                              '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
        n = len(raw) // 2764800
        _cur['name'] = name
        _cur['fr'] = [np.frombuffer(raw[i * 2764800:(i + 1) * 2764800], np.uint8).reshape(1280, 720, 3) for i in range(n)]
    return _cur['fr']


def clip_index(t):
    for i, c in enumerate(CLIPS):
        if c[1] <= t < c[1] + c[2]: return i
    return None


BOOTH = 'Young_man_turning_head'


def booth_cam(lt):
    """budka sahnasi: chap odam -> uzluksiz panorama -> o'ng odam. (cx, cy, zoom) manba (720x1280) koordinatida"""
    L, R = (150.0, 640.0), (600.0, 630.0)
    if lt < 1.5:
        k = lt / 1.5; return L[0], L[1], 2.1 + 0.35 * k
    if lt < 2.7:
        k = (lt - 1.5) / 1.2; e = k * k * (3 - 2 * k)
        return L[0] + (R[0] - L[0]) * e, L[1] + (R[1] - L[1]) * e, 2.45 - 0.25 * math.sin(math.pi * k)
    k = (lt - 2.7) / 1.3; return R[0], R[1], 2.45 + 0.5 * expo_out(k)


def video(t):
    i = clip_index(t)
    name, s, d, fmap, _ = CLIPS[i]
    fr = frames(name); st = fmap(t - s)
    if name == BOOTH:
        cx, cy, z = booth_cam(t - s)
        cw, ch = 720 / z, 1280 / z
        x0 = min(max(cx - cw / 2, 0), 720 - cw); y0 = min(max(cy - ch / 2, 0), 1280 - ch)
        src = Image.fromarray(fr[min(len(fr) - 1, int(st * 24))])
        im = src.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BICUBIC)
        lt = t - s
        if 1.5 < lt < 2.7:
            sp = math.sin(math.pi * (lt - 1.5) / 1.2)
            im = im.filter(ImageFilter.BoxBlur(int(10 * sp))) if sp > 0.15 else im
        if lt > 3.0:
            a = 0.35 * math.exp(-(lt - 3.0) * 4) + (0.12 if int(lt * 12) % 3 == 0 else 0) * (lt < 3.6)
            im = Image.blend(im, Image.new('RGB', (W, H), (150, 10, 10)), min(0.5, a))
        return im, i, lt, d
    im = Image.fromarray(fr[min(len(fr) - 1, int(st * 24))]).resize((W, H), Image.LANCZOS)
    z = 1.0 + 0.04 * (t - s) / d
    im = im.resize((int(W * z), int(H * z)), Image.BILINEAR)
    ox, oy = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((ox, oy, ox + W, oy + H)), i, t - s, d


# ---------- eski plyonka ----------
_rng = np.random.default_rng(5)
YY, XX = np.mgrid[0:H, 0:W]
VIG = np.clip(1 - (np.sqrt(((XX - W / 2) / (W * 0.62)) ** 2 + ((YY - H / 2) / (H * 0.62)) ** 2) - 0.45) * 1.25, 0.18, 1)[..., None].astype(np.float32)
GRAIN = [np.random.default_rng(k).normal(0, 13, (H // 3, W // 3, 1)).astype(np.int16).repeat(3, 0).repeat(3, 1) for k in range(8)]


def old_film(im, t):
    fi = int(t * FPS)
    r = np.random.default_rng(fi)
    # kadr titrashi
    dx, dy = int(r.normal(0, 1.6)), int(r.normal(0, 2.2))
    im = im.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.BILINEAR)
    d = ImageDraw.Draw(im)
    # tirnalishlar
    for _ in range(r.integers(0, 3)):
        x = r.integers(40, W - 40); c = int(r.integers(150, 230))
        d.line((x, 0, x + r.integers(-6, 6), H), fill=(c, c, c), width=1)
    # chang
    for _ in range(r.integers(2, 9)):
        x, y = r.integers(0, W), r.integers(0, H); s = r.integers(1, 5)
        c = int(r.choice([20, 230]))
        d.ellipse((x, y, x + s, y + r.integers(1, 4)), fill=(c, c, c))
    a = np.asarray(im).astype(np.float32)
    # rang: ko'kimtir soya, qahrabo yorug'
    lum = a.mean(-1, keepdims=True) / 255
    a = a * (0.92 + 0.0) + (np.array([18, -4, -14]) * lum + np.array([-6, 4, 10]) * (1 - lum))
    flick = 1 + 0.05 * math.sin(t * 23) * math.sin(t * 7.3) + r.normal(0, 0.015)
    a = a * flick * VIG + GRAIN[fi % 8]
    return np.clip(a, 0, 255).astype(np.uint8)


# ---------- o'tishlar ----------
def transition(im, kind, lt, prev_kind_out=None):
    """lt = yangi klip boshlanganidan beri vaqt (kirish). Kirish effekti 0.35 s."""
    T = 0.35
    if kind is None or lt > T: return im
    k = lt / T
    if kind == 'zoom':
        s = 1.6 - 0.6 * expo_out(k)
        z = im.resize((int(W * s), int(H * s)), Image.BILINEAR); ox, oy = (z.width - W) // 2, (z.height - H) // 2
        im = zoom_blur(z.crop((ox, oy, ox + W, oy + H)), 3 * (1 - k))
    elif kind == 'burn':
        a = (1 - k) ** 1.5
        lay = Image.new('RGB', (W, H), (255, 170, 60))
        im = Image.blend(im, lay, 0.85 * a)
    elif kind == 'flicker':
        if int(lt * FPS) % 3 != 2 and lt < 0.25: im = Image.eval(im, lambda v: v // 8)
    elif kind == 'iris':
        r = int(80 + 1200 * expo_out(k))
        m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), fill=255)
        im = Image.composite(im, Image.new('RGB', (W, H), (0, 0, 0)), m)
    elif kind == 'fog':
        im = Image.blend(im, Image.new('RGB', (W, H), (200, 210, 212)), 0.9 * (1 - k) ** 1.2)
    elif kind == 'whip':
        off = int(W * 0.6 * (1 - expo_out(k)))
        im = im.transform((W, H), Image.AFFINE, (1, 0, off, 0, 1, 0), resample=Image.BILINEAR)
        im = im.filter(ImageFilter.BoxBlur(int(30 * (1 - k)) + 0)) if k < 1 else im
    return im


def exit_fx(im, i, lt, d):
    """chiqish effekti: keyingi klip turi bo'yicha oxirgi 0.3 s"""
    if i + 1 >= len(CLIPS): return im
    nxt = CLIPS[i + 1][4]; rem = d - lt
    if rem > 0.3: return im
    k = 1 - rem / 0.3
    if nxt == 'zoom':
        s = 1 + 0.5 * expo_in(k)
        z = im.resize((int(W * s), int(H * s)), Image.BILINEAR); ox, oy = (z.width - W) // 2, (z.height - H) // 2
        im = zoom_blur(z.crop((ox, oy, ox + W, oy + H)), 3 * k)
    elif nxt == 'burn':
        im = Image.blend(im, Image.new('RGB', (W, H), (255, 170, 60)), 0.85 * k ** 1.5)
    elif nxt == 'iris':
        r = int(1300 - 1250 * expo_in(k))
        m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), fill=255)
        im = Image.composite(im, Image.new('RGB', (W, H), (0, 0, 0)), m)
    elif nxt == 'fog':
        im = Image.blend(im, Image.new('RGB', (W, H), (200, 210, 212)), 0.9 * k)
    elif nxt == 'whip':
        off = int(-W * 0.6 * expo_in(k))
        im = im.transform((W, H), Image.AFFINE, (1, 0, off, 0, 1, 0), resample=Image.BILINEAR).filter(ImageFilter.BoxBlur(int(30 * k)))
    elif nxt == 'flicker':
        if int(rem * FPS) % 2 == 0: im = Image.eval(im, lambda v: v // 6)
    return im


def doors_close(im, lt):
    """yakun: ikki qora panel o'rtaga yopiladi"""
    k = expo_out(clamp(lt / 0.6))
    d = ImageDraw.Draw(im); w = int(W / 2 * k)
    d.rectangle((0, 0, w, H), fill=(6, 5, 4)); d.rectangle((W - w, 0, W, H), fill=(6, 5, 4))
    if 0 < k < 1:
        d.line((w, 0, w, H), fill=(120, 90, 50), width=3); d.line((W - w, 0, W - w, H), fill=(120, 90, 50), width=3)
    return im


# ---------- yozuvlar ----------
WM_POS = [(800, 300), (260, 1150), (820, 320), (250, 300), (810, 1180), (250, 330), (820, 300), (540, 330), (820, 320),
          (250, 300)]


def watermark(im, t):
    i = clip_index(t)
    if i is None: return
    lt = t - CLIPS[i][1]; d = CLIPS[i][2]
    x, y = WM_POS[i]; x += 10 * math.sin(lt * 1.2 + i); y += 8 * math.cos(lt + i)
    al = clamp(lt / 0.3) * (1 - clamp((lt - d + 0.15) / 0.15))
    f = sfont(SERIF_I, 34); txt = '@birbalo_ai'
    lay = Image.new('RGBA', (300, 60), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
    dd.text((150 - f.getlength(txt) / 2, 10), txt, font=f, fill=(235, 225, 205, int(170 * al)))
    im.paste(lay, (int(x - 150), int(y - 30)), lay)


def narr_caption(im, t):
    for tt, a, b, txt in LINES:
        if tt <= t < tt + (b - a) + 0.25:
            lt = t - tt; al = clamp(lt / 0.25) * (1 - clamp((lt - (b - a)) / 0.25))
            f = sfont(SERIF_I, 54)
            lines = mg.wrap(txt, f, 900)
            lay = Image.new('RGBA', (W, 200), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
            for j, l in enumerate(lines):
                x = (W - f.getlength(l)) / 2
                dd.text((x, 20 + j * 66), l, font=f, fill=(240, 232, 215, int(255 * al)), stroke_width=4,
                        stroke_fill=(0, 0, 0, int(200 * al)))
            im.paste(lay, (0, 1330), lay)
            return


def endcard(lt):
    im = Image.new('RGB', (W, H), (6, 5, 4)); d = ImageDraw.Draw(im)
    a = clamp((lt - 0.6) / 0.8)
    f1 = sfont(SERIF_B, 92); f2 = sfont(SERIF_I, 46); f3 = sfont(SERIF_I, 38)
    c = lambda v: tuple(int(x * a) for x in v)
    for txt, f, y, col in [("Tungi", f1, 760, (232, 220, 196)), ("g'aroyibotlar", f1, 870, (232, 220, 196)),
                           ("I qism", f2, 1010, (190, 160, 110)), ("@birbalo_ai", f3, 1180, (200, 190, 170))]:
        d.text(((W - f.getlength(txt)) / 2, y), txt, font=f, fill=c(col))
    return im


def frame(t):
    if t < END0:
        im, i, lt, d = video(t)
        im = transition(im, CLIPS[i][4], lt)
        im = exit_fx(im, i, lt, d)
        if t > END0 - 0.6: im = doors_close(im, t - (END0 - 0.6))
        dx, dy, rot = shake(t, [(4.6, 0.9), (25.5, 1.1)])
        im = camera(im.convert('RGBA'), 1.0 + (0.02 if abs(dx) > 0.5 else 0), rot, dx, dy).convert('RGB')
        watermark(im, t); narr_caption(im, t)
    else:
        im = endcard(t - END0); narr_caption(im, t)
    return old_film(im, t)


def render(out, audio):
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', '-i', audio, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-b:v', '7000k',
           '-maxrate', '9000k', '-bufsize', '14000k', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest',
           '-movflags', '+faststart', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(int(round(DUR * FPS))): p.stdin.write(frame(fi / FPS).tobytes())
    p.stdin.close(); p.wait()


if __name__ == '__main__':
    if sys.argv[1] == 'sheet':
        ts = [float(x) for x in (sys.argv[2] if len(sys.argv) > 2 else '0.1,2.6,5.0,8.2,12,16,20,24,28,32,34.3,37').split(',')]
        ims = [Image.fromarray(frame(t)).resize((180, 320)) for t in ts]
        sh = Image.new('RGB', (180 * len(ims), 320))
        for i, im in enumerate(ims): sh.paste(im, (i * 180, 0))
        sh.save(os.path.join(OUT, 'sheet.jpg'), quality=85)
    else:
        render(os.path.join(OUT, 'tungi_raw.mp4'), sys.argv[2]); print('done')
