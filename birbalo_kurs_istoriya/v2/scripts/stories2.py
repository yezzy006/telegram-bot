"""Kurs reklamasi v2 — 6 ta istoriya, After Effects uslubi. python3 scripts/stories2.py sheet|render [n..]"""
import sys, os, math, subprocess, wave, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from fx import *
import mg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICE = os.path.join(ROOT, 'voice', 'raw2.mp3')
OUT = os.path.join(ROOT, 'out2'); ASSETS = os.path.join(ROOT, 'assets')
SR = 44100; PRE = 0.35

SEG = [
    (0.00, 2.37, "Bu videoda kamera ham, aktyor ham yo'q."),
    (2.83, 4.58, "Hammasini sun'iy intellekt qildi."),
    (5.10, 6.27, "Realga yaqin videolar."),
    (6.79, 7.59, "Murakkab montaj,"),
    (7.93, 9.26, "xuddi After Effects'dagidek."),
    (9.86, 11.43, "Hammasi oddiy prompt bilan."),
    (11.95, 12.84, "SMM,"),
    (13.22, 14.66, "biznes yoki bloger."),
    (15.14, 17.62, "Bu ko'nikma bilan bizneslar sizga o'zi keladi."),
    (18.03, 19.03, "Kursda hammasi bor."),
    (19.49, 20.58, "Realga yaqin video,"),
    (20.89, 21.84, "prompt bilan montaj,"),
    (22.31, 24.56, "biznesga reklama, ovoz va personaj,"),
    (24.98, 26.06, "Instagramni o'stirish."),
    (26.57, 28.22, "Narxi 250 000 so'm."),
    (28.53, 29.89, "Joy faqat 30 kishiga."),
    (30.32, 31.81, "Va yana bitta bonus dars bor."),
    (32.19, 32.52, "U sir."),
    (33.02, 34.74, "Uni faqat kursga kirganlar ko'radi."),
    (35.23, 36.45, "Direct'ga «KURS» deb yozing."),
    (36.72, 37.85, "Joylar tugashidan oldin."),
]
STORY = {1: ([0, 1], 1.0), 2: ([2, 3, 4, 5], 1.2), 3: ([6, 7, 8], 1.2), 4: ([9, 10, 11, 12, 13, 14, 15], 1.4),
         5: ([16, 17, 18], 1.4), 6: ([19, 20], 2.6)}


def local(n):
    idx, tail = STORY[n]; g0 = SEG[idx[0]][0]
    caps = [(SEG[i][2], SEG[i][0] - g0 + PRE, SEG[i][1] - g0 + PRE) for i in idx]
    return caps, SEG[idx[-1]][1] - g0 + PRE + tail, g0


def new(): return Image.new('RGBA', (W, H), (0, 0, 0, 0))


def hitfx(t, hits, base_scale=1.0):
    dx, dy, rot = shake(t, hits)
    ca = sum(16 * amp * math.exp(-(t - at) * 8) for at, amp in hits if t >= at)
    return (base_scale, rot, dx, dy), ca


def overlay_for(n):
    caps = local(n)[0]
    def ov(c):
        mg.brand(c); subtitle(c, T[0], caps, y=1600)
    return ov


T = [0.0]


# ---------- footage (ixtiyoriy): assets/s1.mp4|png ----------
_foot = {}


def footage(name, t, z0=1.0, z1=1.12):
    if name not in _foot:
        fs = [f for f in glob.glob(os.path.join(ASSETS, name + '.*'))]
        if not fs: _foot[name] = None
        elif fs[0].endswith(('.png', '.jpg', '.jpeg')):
            im = Image.open(fs[0]).convert('RGB'); _foot[name] = ('img', im)
        else:
            raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', fs[0], '-vf',
                                  f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=30',
                                  '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
            n = len(raw) // (W * H * 3)
            _foot[name] = ('vid', [Image.frombytes('RGB', (W, H), raw[i * W * H * 3:(i + 1) * W * H * 3]) for i in range(n)])
    f = _foot[name]
    if f is None: return None
    if f[0] == 'img':
        im = f[1]; z = z0 + (z1 - z0) * clamp(t / 6)
        s = max(W / im.width, H / im.height) * z
        r = im.resize((int(im.width * s), int(im.height * s)), Image.BILINEAR)
        ox, oy = (r.width - W) // 2, (r.height - H) // 2
        return r.crop((ox, oy, ox + W, oy + H)).convert('RGBA')
    fr = f[1]; return fr[min(len(fr) - 1, int(t * 30))].convert('RGBA')


def darken(world, top=0.25, bottom=0.75):
    g = np.linspace(0, 1, H)[:, None]
    a = (np.clip((g - 0.35) / 0.65, 0, 1) * 255 * bottom + np.clip((0.3 - g) / 0.3, 0, 1) * 255 * top)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); lay.putalpha(Image.fromarray(a.repeat(W, 1).astype(np.uint8)))
    world.alpha_composite(lay)


# ================= 1. KAMERA YO'Q =================
def s1(t):
    w = new(); d = ImageDraw.Draw(w)
    hits = [(0.0, 0.6), (2.15, 1.0), (2.95, 0.9)]
    ft = footage('s1', t)
    if ft is not None: w.alpha_composite(ft); darken(w)
    A = t < 2.95
    k = expo_out((t + 0.25) / 0.45)
    col = WHITE if A else GOLD
    bx = (90, 330, 990, 1500) if A else (150 + 30 * (1 - expo_out((t - 2.95) / 0.4)), 380, 930, 1450)
    brackets(w, bx, k, col, L=90, wdt=8, alpha=230)
    f = mono(34)
    if A:
        if int(t * 2) % 2 == 0: d.ellipse((130, 372, 158, 400), fill=RED)
        d.text((172, 366), f"REC  00:00:0{int(t)}:{int(t * 30) % 30:02d}", font=f, fill=(255, 255, 255, 230))
        d.text((760, 366), "4K · 30FPS", font=f, fill=(255, 255, 255, 200))
        d.line((500, 915, 580, 915), fill=(255, 255, 255, 120), width=3); d.line((540, 875, 540, 955), fill=(255, 255, 255, 120), width=3)
        big(w, t, "KAMERA", -0.15, 540, 760, 180, end=2.95)
        mask_up(w, t, "AKTYOR", 1.3, 540, 935, 160, end=2.95)
        big(w, t, "YO'Q.", 2.15, 540, 1130, 200, fill=RED, glow=RED, end=2.95)
    else:
        lt = t - 2.95
        d.text((190, 410), "AI GENERATED", font=f, fill=GOLD + (255,))
        d.text((680, 410), "100%", font=f, fill=GOLD + (255,))
        sy = 420 + (lt * 900) % 1000
        d.line((150, sy, 930, sy), fill=GOLD + (140,), width=4)
        d.rectangle((150, sy - 40, 930, sy), fill=GOLD + (18,))
        mask_up(w, t, "SUN'IY", 3.18, 540, 760, 170)
        big(w, t, "INTELLEKT", 3.45, 540, 940, 150, fill=GOLD, glow=GOLD, sw_at=4.0)
        echo(w, t, "QILDI.", 4.1, 540, 1110, 120, col=GOLD)
        big(w, t, "QILDI.", 4.1, 540, 1110, 120, anim='pop')
        burst(w, t, 3.45, 540, 940, seed=3)
    flash(w, t, 2.95, 0.18, 0.6)
    cam, ca = hitfx(t, hits, 1.0 + 0.012 * t)
    g = 1.0 if 2.92 <= t < 3.15 else 0.0
    return dict(world=w, cam=cam, ca=ca, glitch=g, mood=('blue', 'red'), overlay=overlay_for(1))


EV1 = [(0, 'hit'), (1.3, 'swish'), (2.15, 'hit'), (2.92, 'glitch'), (3.18, 'swish'), (3.45, 'hit'), (4.1, 'pop')]


# ================= 2. REAL + MONTAJ + PROMPT =================
LAYERS = [("Kamera", BLUE), ("Matn", GOLD), ("Nur", (255, 140, 60)), ("Zarracha", (180, 120, 255)), ("Ovoz", (90, 200, 150))]


def editor_sprite(lt):
    k = ('ed', int(lt * 30))
    im = Image.new('RGBA', (900, 640), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 899, 639), 34, fill=(16, 20, 34, 235), outline=(255, 255, 255, 60), width=3)
    d.rounded_rectangle((0, 0, 899, 70), 34, fill=(30, 36, 56, 255)); d.rectangle((0, 40, 899, 70), fill=(30, 36, 56, 255))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]): d.ellipse((28 + i * 34, 24, 50 + i * 34, 46), fill=c)
    d.text((150, 18), "Composition · birbalo_reklama", font=mono(28), fill=(200, 205, 220))
    f = font('bold', 32)
    for r, (name, col) in enumerate(LAYERS):
        y = 110 + r * 78
        d.text((30, y + 8), name, font=f, fill=(225, 228, 238))
        x0 = 250 + (r * 37) % 90; x1 = x0 + 260 + (r * 61) % 300
        grow = clamp((lt - r * 0.18) / 0.5); x1 = x0 + (x1 - x0) * expo_out(grow)
        if x1 > x0 + 4: d.rounded_rectangle((x0, y + 6, x1, y + 50), 10, fill=col + (230,))
        for j in range(4):
            kt = r * 0.18 + 0.3 + j * 0.22
            if lt > kt:
                kx = x0 + 30 + j * 70; s = 12 * back((lt - kt) / 0.25, 2.5)
                d.polygon([(kx, y + 28 - s), (kx + s, y + 28), (kx, y + 28 + s), (kx - s, y + 28)], fill=WHITE)
    # grafik egri chiziq
    pts = []
    for i in range(60):
        u = i / 59; x = 250 + 600 * u
        y = 600 - 140 * (1 / (1 + math.exp(-12 * (u - 0.5))))
        if u <= clamp(lt / 1.6): pts.append((x, y))
    if len(pts) > 1: d.line(pts, fill=GOLD, width=6)
    ph = 250 + (lt * 260) % 620
    d.line((ph, 90, ph, 620), fill=(255, 80, 80, 230), width=4)
    return im


def s2(t):
    w = new(); d = ImageDraw.Draw(w)
    hits = [(0.0, 0.6), (2.0, 0.5), (3.18, 1.0), (6.45, 1.0)]
    zb = 0.0
    ft = footage('s2', t)
    if t < 2.0:
        if ft is not None: w.alpha_composite(ft); darken(w)
        big(w, t, "REALGA", -0.15, 540, 780, 175, zoom_out=1.8)
        big(w, t, "YAQIN", 0.5, 540, 960, 175, fill=GOLD, glow=GOLD, sw_at=0.9, zoom_out=1.85)
        pill(w, t, "AI VIDEO", 0.95, 540, 1125, 48, bg=WHITE, fg=BG, end=1.8)
        zb = 3 * clamp((t - 1.8) / 0.2)
    elif t < 5.0:
        lt = t - 2.0
        mask_up(w, t, "MURAKKAB MONTAJ", 2.04, 540, 430, 92, end=4.85)
        ed = editor_sprite(lt)
        rx = 22 * (1 - expo_out(lt / 0.8)) + 6 * math.sin(lt * 0.9); ry = -16 + 8 * math.sin(lt * 0.7)
        sp = tilt(ed, rx, ry)
        sc = 0.55 + 0.45 * expo_out(lt / 0.7)
        al = 1.0
        if t > 4.75: z = clamp((t - 4.75) / 0.25); sc *= 1 + 3 * expo_in(z); al = 1 - z
        place(w, sp, 540, 930, sc, al)
        big(w, t, "AFTER EFFECTS", 3.18, 540, 1390, 104, fill=GOLD, glow=GOLD, sw_at=3.6, end=4.8)
        mask_up(w, t, "DARAJASIDA", 3.5, 540, 1495, 60, w='xbold', fill=GRAY, end=4.8)
        zb = 2.5 * (1 - clamp((t - 2.0) / 0.25)) + 3 * clamp((t - 4.8) / 0.2)
    else:
        lt = t - 5.0
        mask_up(w, t, "ODDIY", 5.11, 540, 560, 130)
        big(w, t, "PROMPT", 5.4, 540, 720, 170, fill=GOLD, glow=GOLD, sw_at=6.5)
        y0 = 880; al = clamp(lt / 0.3); sent = t > 6.45
        glass(w, (90, y0, 990, y0 + 230), 40, al, border=(GOLD + (255,)) if sent else (255, 255, 255, 80),
              fill=(236, 186, 62, 40) if sent else (255, 255, 255, 22))
        q = "lemonad reklamasi, kinematik, oltin soat, suv tomchilari"
        n = int(clamp((t - 5.25) / 1.1) * len(q)); fz = font('semi', 42)
        lines = wrap(q[:n], fz, 800)
        for i, l in enumerate(lines[:3]): d.text((130, y0 + 30 + i * 56), l, font=fz, fill=WHITE)
        if not sent and int(t * 3) % 2 == 0 and lines:
            cx = 130 + fz.getlength(lines[-1]); cy = y0 + 30 + (len(lines) - 1) * 56
            d.rectangle((cx + 4, cy + 4, cx + 9, cy + 50), fill=GOLD)
        pill(w, t, "ENTER ↵" if False else "ENTER", 6.3, 830, y0 + 230, 40, bg=GOLD, fg=BG)
        burst(w, t, 6.45, 540, y0 + 115, n=60, seed=7, speed=1200)
        pill(w, t, "TAYYOR VIDEO", 6.6, 540, 1250, 64, bg=WHITE, fg=BG)
        zb = 2.5 * (1 - clamp((t - 5.0) / 0.25))
    flash(w, t, 6.45, 0.2, 0.45)
    cam, ca = hitfx(t, hits, 1.0 + 0.01 * (t % 3))
    return dict(world=w, cam=cam, ca=ca, zblur=zb, mood=('blue', 'gold'), overlay=overlay_for(2))


EV2 = [(0, 'hit'), (0.5, 'swish'), (1.8, 'whoosh'), (2.04, 'swish'), (3.18, 'hit'), (4.75, 'whoosh'), (5.11, 'swish'),
       (5.4, 'hit')] + [(5.25 + i * 0.09, 'tick') for i in range(12)] + [(6.45, 'hit'), (6.6, 'pop')]


# ================= 3. KIMGA + BIZNESLAR KELADI =================
NOTIF = [("Kafe egasi", "Reklama video kerak. Narxi qancha?", GOLD, 4.3),
         ("Kiyim do'koni", "Yangi kolleksiyaga video qilasizmi?", BLUE, 4.85),
         ("Stomatologiya", "Hamkorlik qilamizmi?", (90, 200, 150), 5.35)]


def notif(w, t, name, msg, col, st, y):
    lt = t - st
    if lt < 0: return
    k = expo_out(lt / 0.45); yy = y - 260 * (1 - k); al = clamp(lt / 0.2)
    glass(w, (80, yy, 1000, yy + 160), 36, al, border=(255, 255, 255, 70), fill=(255, 255, 255, 30))
    d = ImageDraw.Draw(w)
    d.rounded_rectangle((110, yy + 32, 206, yy + 128), 24, fill=col + (int(255 * al),))
    d.text((140, yy + 44), name[0], font=font('black', 60), fill=BG)
    d.text((232, yy + 30), name, font=font('xbold', 40), fill=(255, 255, 255, int(255 * al)))
    d.text((232, yy + 86), msg, font=font('semi', 34), fill=(210, 214, 225, int(255 * al)))
    d.text((880, yy + 34), "hozir", font=font('semi', 28), fill=(160, 166, 180, int(255 * al)))


def s3(t):
    w = new()
    hits = [(0.0, 0.8), (1.62, 0.8), (2.5, 0.8), (5.7, 0.9)]
    zb = 0.0
    if t < 3.5:
        for txt, st, zo, col, glow in [("SMM", -0.15, 1.45, GOLD, GOLD), ("BIZNES", 1.62, 2.35, WHITE, None),
                                       ("BLOGER", 2.5, 3.35, (120, 165, 255), BLUE)]:
            if st <= t < zo + 0.3:
                echo(w, t, txt, st, 540, 900, 250 if len(txt) > 3 else 330, col=col, end=zo)
                big(w, t, txt, st, 540, 900, 250 if len(txt) > 3 else 330, fill=col, glow=glow, zoom_out=zo)
                zb = max(zb, 3 * clamp((t - zo) / 0.25) if t > zo else 0)
        ktext(w, t, "SIZ KIMSIZ?", -0.3, 540, 560, 56, w='xbold', fill=GRAY, end=3.3)
    else:
        mask_up(w, t, "BU KO'NIKMA BILAN", 3.54, 540, 420, 64, w='xbold', fill=GRAY)
        for i, (nm, msg, col, st) in enumerate(NOTIF): notif(w, t, nm, msg, col, st, 540 + i * 190)
        big(w, t, "O'ZI KELADI", 5.7, 540, 1280, 140, fill=GOLD, glow=GOLD, sw_at=6.1)
        burst(w, t, 5.7, 540, 1280, n=50, seed=11)
    cam, ca = hitfx(t, hits, 1.0 + 0.015 * math.sin(t))
    return dict(world=w, cam=cam, ca=ca, zblur=zb, mood=('gold', 'violet'), overlay=overlay_for(3))


EV3 = [(0, 'hit'), (1.45, 'whoosh'), (1.62, 'hit'), (2.35, 'whoosh'), (2.5, 'hit'), (3.54, 'swish'), (4.3, 'notif'),
       (4.85, 'notif'), (5.35, 'notif'), (5.7, 'hit')]


# ================= 4. KURS KARTOCHKASI =================
ITEMS = [("Realga yaqin AI video", 1.81), ("Prompt bilan montaj", 3.21), ("Biznesga reklama", 4.63),
         ("Ovoz va personaj", 5.9), ("Instagram o'stirish", 7.30)]


def card_sprite(t):
    im = Image.new('RGBA', (880, 1000), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 879, 999), 48, fill=(18, 22, 38, 240), outline=GOLD + (200,), width=4)
    d.rounded_rectangle((250, 50, 630, 110), 30, fill=TG)
    ft = font('black', 32); s = "YOPIQ TELEGRAM KANAL"; d.text((440 - ft.getlength(s) / 2, 62), s, font=ft, fill=WHITE)
    for txt, y, sz, col in [("BIRBALO AI", 150, 104, GOLD), ("AKADEMIYA", 270, 96, WHITE)]:
        f = font('black', sz); d.text((440 - f.getlength(txt) / 2, y), txt, font=f, fill=col)
    d.line((80, 410, 800, 410), fill=(255, 255, 255, 50), width=3)
    fi = font('xbold', 50)
    for i, (txt, st) in enumerate(ITEMS):
        y = 460 + i * 100; lt = t - st
        on = lt >= 0
        r = 28 * (back(lt / 0.3, 2.5) if on else 1)
        d.ellipse((100 - r, y + 32 - r, 100 + r, y + 32 + r), fill=GOLD if on else (255, 255, 255, 30))
        if on and lt > 0.1: d.line((86, y + 33, 97, y + 44, 116, y + 20), fill=BG, width=7)
        d.text((150, y + 2), txt, font=fi, fill=WHITE if on else (110, 116, 132))
    return im


def s4(t):
    w = new(); d = ImageDraw.Draw(w)
    hits = [(0.0, 0.5), (9.05, 1.0), (10.85, 0.6)]
    cs = card_sprite(t)
    sw_p = ((t - 0.6) % 3.2) / 0.9
    cs = sweep(cs, sw_p, 220, 110)
    rx = 6 * math.sin(t * 0.7); ry = -10 + 9 * math.sin(t * 0.45)
    if t < 8.7:
        sc = 0.62 + 0.38 * expo_out((t + 0.3) / 0.6); cy = 900
    else:
        k = expo_out((t - 8.7) / 0.6); sc = 1.0 - 0.5 * k; cy = 900 - 380 * k; rx += 18 * k
    place(w, tilt(cs, rx, ry), 540, cy, sc)
    big(w, t, "250 000", 9.05, 540, 1060, 210, fill=GOLD, glow=GOLD, sw_at=9.6)
    mask_up(w, t, "SO'M", 9.3, 540, 1215, 90)
    burst(w, t, 9.05, 540, 1060, n=60, seed=5, speed=1300)
    pill(w, t, "FAQAT 30 KISHI", 10.85, 540, 1345, 50, bg=RED, fg=WHITE)
    if t > 11.1:
        n = int(clamp((t - 11.1) / 1.0) * 30)
        for i in range(30):
            x = 177 + (i % 15) * 52; y = 1440 + (i // 15) * 40
            d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=(GOLD + (255,)) if i < n else (255, 255, 255, 45))
    flash(w, t, 9.05, 0.2, 0.4)
    cam, ca = hitfx(t, hits)
    return dict(world=w, cam=cam, ca=ca, zblur=2.5 * clamp(1 - abs(t - 8.85) / 0.2), mood=('blue', 'gold'),
                overlay=overlay_for(4))


EV4 = [(0, 'hit')] + [(st, 'pop') for _, st in ITEMS] + [(8.7, 'whoosh'), (9.05, 'hit'), (10.85, 'pop')] + \
      [(11.1 + i * 0.066, 'tick') for i in range(0, 30, 2)]


# ================= 5. SIR BONUS =================
def secret_card():
    k = ('secret',)
    if k in mg._sc: return mg._sc[k]
    im = Image.new('RGBA', (860, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 859, 519), 40, fill=(26, 22, 44, 245))
    d.rounded_rectangle((40, 40, 330, 480), 26, fill=(200, 120, 40))
    d.ellipse((110, 140, 260, 290), fill=(250, 200, 120)); d.rounded_rectangle((90, 300, 280, 470), 50, fill=(120, 60, 200))
    for i in range(6):
        d.rounded_rectangle((370, 60 + i * 70, 370 + [420, 380, 300, 410, 260, 340][i], 96 + i * 70), 16,
                            fill=(255, 255, 255, 150 if i == 0 else 90))
    im = im.filter(ImageFilter.GaussianBlur(16))
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).rounded_rectangle((0, 0, 859, 519), 40,
        fill=(255, 255, 255, 18), outline=(255, 255, 255, 70), width=3)
    im.alpha_composite(lay); mg._sc[k] = im
    return im


def stamp(text, size=200, col=RED):
    k = ('stamp', text, size)
    if k in mg._sc: return mg._sc[k]
    f = font('black', size); tw = f.getlength(text); asc, desc = f.getmetrics()
    im = Image.new('RGBA', (int(tw + 120), int(asc + desc + 80)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, im.width - 8, im.height - 8), 30, outline=col, width=16)
    d.text((60, 30), text, font=f, fill=col)
    mg._sc[k] = im
    return im


def s5(t):
    w = new()
    hits = [(0.0, 0.5), (2.22, 1.2)]
    big(w, t, "+1 BONUS DARS", -0.15, 540, 470, 110, fill=WHITE, anim='pop')
    lt = t + 0.3
    sc = 0.7 + 0.3 * expo_out(lt / 0.6)
    place(w, tilt(secret_card(), 10 * math.sin(t * 0.8), -8 * math.cos(t * 0.6)), 540, 880, sc, clamp(lt / 0.3))
    sh = 0
    if 2.22 <= t < 2.8: sh = 14 * math.sin((t - 2.22) * 60) * math.exp(-(t - 2.22) * 6)
    pul = 1 + 0.04 * math.sin(t * 5)
    place(w, lock_icon(200), 540 + sh, 870, pul, 1.0 if t < 2.22 else max(0.18, 1 - (t - 2.22) / 0.2))
    lt2 = t - 2.22
    if lt2 >= 0:
        sp = stamp("SIR", 230); s = 1 + 1.2 * (1 - expo_out(lt2 / 0.25))
        place(w, sp, 540, 900, s, clamp(lt2 / 0.06), rot=-9)
    mask_up(w, t, "FAQAT KURSGA", 3.05, 540, 1310, 80)
    mask_up(w, t, "KIRGANLAR KO'RADI", 3.3, 540, 1410, 80, fill=GOLD, glow=GOLD)
    flash(w, t, 2.22, 0.15, 0.5, col=RED)
    cam, ca = hitfx(t, hits, 1.0 + 0.01 * t)
    g = 0.9 if 2.18 <= t < 2.36 else 0.0
    return dict(world=w, cam=cam, ca=ca, glitch=g, mood=('violet', 'red'), overlay=overlay_for(5))


EV5 = [(0, 'hit'), (2.18, 'glitch'), (2.22, 'hit'), (3.05, 'swish'), (3.3, 'swish')]


# ================= 6. CTA =================
def s6(t):
    w = new(); d = ImageDraw.Draw(w)
    hits = [(0.0, 0.6), (1.2, 0.8)]
    big(w, t, "DIRECT'GA", -0.15, 540, 450, 160)
    mask_up(w, t, "«KURS» DEB YOZING", 0.4, 540, 580, 74, fill=GOLD, glow=GOLD)
    y0 = 1100; al = clamp((t + 0.3) / 0.3)
    glass(w, (80, y0, 1000, y0 + 130), 65, al, border=(255, 255, 255, 90), fill=(255, 255, 255, 26))
    q = "KURS"; n = int(clamp((t - 0.6) / 0.45) * 4) if t < 1.2 else 0
    fz = font('black', 58)
    if n == 0: d.text((130, y0 + 34), "Xabar yozing...", font=font('semi', 50), fill=(150, 156, 170))
    else: d.text((130, y0 + 30), q[:n], font=fz, fill=WHITE)
    pr = 1 + (0.15 * math.sin((t - 1.2) * 12) * math.exp(-(t - 1.2) * 3) if t > 1.2 else 0)
    r = 46 * pr; d.ellipse((920 - r, y0 + 65 - r, 920 + r, y0 + 65 + r), fill=GOLD)
    d.polygon([(900, y0 + 45), (948, y0 + 65), (900, y0 + 85), (908, y0 + 65)], fill=BG)
    # yuborilgan xabar
    lt = t - 1.2
    if lt >= 0:
        k = expo_out(lt / 0.5); by = y0 - 60 - 320 * k
        s = back(lt / 0.35, 2.0)
        bub = Image.new('RGBA', (300, 120), (0, 0, 0, 0)); bd = ImageDraw.Draw(bub)
        bd.rounded_rectangle((0, 0, 299, 119), 50, fill=GOLD); bd.text((70, 22), "KURS", font=fz, fill=BG)
        place(w, bub, 820 - 30 * (1 - k), by, s)
        burst(w, t, 1.2, 900, y0 + 65, n=40, seed=13, speed=900)
    lt = t - 1.8
    if lt >= 0:
        s = back(lt / 0.35, 2.0)
        bub = Image.new('RGBA', (560, 120), (0, 0, 0, 0)); bd = ImageDraw.Draw(bub)
        bd.rounded_rectangle((0, 0, 559, 119), 50, fill=(255, 255, 255, 40), outline=(255, 255, 255, 80), width=3)
        txt = "· · ·" if lt < 0.6 else "Salom! Ma'lumot yuboraman"
        fb = font('xbold', 38); bd.text((280 - fb.getlength(txt) / 2, 36), txt, font=fb, fill=WHITE)
        place(w, bub, 340, 900, s)
    if t > 1.84:
        pul = 1 + 0.05 * math.sin((t - 1.84) * 7)
        pill(w, t, "JOYLAR TUGASHIDAN OLDIN", 1.84, 540, 1330, 52, bg=RED, fg=WHITE)
    if t > 2.3:
        b = 18 * math.sin((t - 2.3) * 5); a = clamp((t - 2.3) / 0.3)
        for k2 in range(2):
            y = 1440 + b + k2 * 36
            d.line((480, y, 540, y + 40, 600, y), fill=GOLD + (int(255 * a * (1 - 0.4 * k2)),), width=13, joint='curve')
    flash(w, t, 1.2, 0.15, 0.35, col=GOLD)
    cam, ca = hitfx(t, hits)
    return dict(world=w, cam=cam, ca=ca, mood=('red', 'gold'), overlay=overlay_for(6))


EV6 = [(0, 'hit'), (0.4, 'swish')] + [(0.6 + i * 0.11, 'tick') for i in range(4)] + [(1.2, 'send'), (1.8, 'pop'),
                                                                                    (2.4, 'notif'), (1.84, 'pop')]

STORIES = {1: (s1, EV1), 2: (s2, EV2), 3: (s3, EV3), 4: (s4, EV4), 5: (s5, EV5), 6: (s6, EV6)}

# ---------- audio ----------
_raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', VOICE, '-ar', str(SR), '-ac', '1', '-f', 'f32le', '-'],
                      capture_output=True).stdout
VOX = np.frombuffer(_raw, np.float32)


def sweep_tone(f0, f1, dur, amp, decay):
    n = int(dur * SR); tt = np.arange(n) / SR; f = f0 + (f1 - f0) * tt / dur
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * decay)


def sfx(kind):
    if kind == 'pop': return sweep_tone(950, 500, 0.09, 0.22, 45)
    if kind == 'tick': return sweep_tone(2300, 2100, 0.025, 0.09, 250)
    if kind == 'hit':
        a = sweep_tone(120, 42, 0.7, 0.5, 6); b = sweep_tone(1800, 300, 0.05, 0.12, 80)
        a[:len(b)] += b; return a
    if kind in ('swish', 'whoosh'):
        dur = 0.3 if kind == 'swish' else 0.45; n = int(dur * SR); tt = np.arange(n) / SR
        env = np.sin(np.pi * tt / dur) ** 2
        f = 250 + 2200 * (tt / dur) ** 2 if kind == 'whoosh' else 400 + 1500 * tt / dur
        return (0.06 if kind == 'swish' else 0.09) * env * np.sin(2 * np.pi * np.cumsum(f) / SR)
    if kind == 'glitch':
        n = int(0.2 * SR); tt = np.arange(n) / SR
        sq = np.sign(np.sin(2 * np.pi * 95 * tt)) * (np.sin(2 * np.pi * 23 * tt) > 0)
        return 0.08 * sq * np.exp(-tt * 6)
    if kind == 'notif':
        a = sweep_tone(1320, 1320, 0.12, 0.12, 20); b = sweep_tone(1760, 1760, 0.16, 0.12, 18)
        o = np.zeros(len(a) + len(b) - 2000); o[:len(a)] += a; o[len(a) - 2000:] += b; return o
    if kind == 'send': return sweep_tone(500, 1400, 0.15, 0.18, 12)
    return np.zeros(1)


def audio(n):
    caps, dur, g0 = local(n); idx, _ = STORY[n]
    N = int(dur * SR); mix = np.zeros(N, np.float32)
    a = int(max(0, g0 - 0.05) * SR); b = int((SEG[idx[-1]][1] + 0.12) * SR)
    v = VOX[a:b]; st = int((PRE - 0.05) * SR); m = min(len(v), N - st); mix[st:st + m] += v[:m]
    tt = np.arange(N) / SR; env = np.clip(tt / 0.8, 0, 1) * np.clip((dur - tt) / 0.8, 0, 1)
    for fq in (55.0, 110.0, 164.81, 220.0):
        mix += 0.007 * np.sin(2 * np.pi * fq * tt) * env
    for at, kind in STORIES[n][1]:
        s = sfx(kind); i = int(max(0, at) * SR); m = min(len(s), N - i)
        if m > 0: mix[i:i + m] += s[:m]
    raw = os.path.join(OUT, f'_a{n}.wav')
    with wave.open(raw, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
    fin = os.path.join(OUT, f'_a{n}_n.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af',
                    'loudnorm=I=-12.5:TP=-1.5:LRA=11,aresample=44100', '-ac', '2', fin], check=True)
    return fin


class Clock:
    def __init__(self, fn): self.fn = fn
    def __call__(self, t): T[0] = t; return self.fn(t)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    mode = sys.argv[1]; ns = [int(x) for x in sys.argv[2:]] or list(STORIES)
    for n in ns:
        fn = Clock(STORIES[n][0]); caps, dur, _ = local(n)
        if mode == 'sheet':
            ts = [0.0] + [dur * k / 6 for k in range(1, 6)] + [dur - 0.1]
            if len(sys.argv) > 2 and os.environ.get('TS'): ts = [float(x) for x in os.environ['TS'].split(',')]
            ims = [Image.fromarray(compose(fn, t)).resize((270, 480)) for t in ts]
            sh = Image.new('RGB', (270 * len(ims), 480))
            for i, im in enumerate(ims): sh.paste(im, (i * 270, 0))
            sh.save(os.path.join(OUT, f'sheet{n}.jpg'), quality=85); print(n, f'{dur:.2f}', [round(x, 1) for x in ts])
        else:
            render(fn, dur, os.path.join(OUT, f'v2_istoriya_{n}.mp4'), audio(n)); print('done', n, f'{dur:.2f}')
