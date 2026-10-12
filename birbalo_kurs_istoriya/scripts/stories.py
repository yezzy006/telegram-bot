"""Kurs reklamasi: 5 ta istoriya (motion grafika). python3 scripts/stories.py sheet|render [n]"""
import sys, os, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from mg import *
import mg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICE = os.path.join(ROOT, 'voice', 'raw.mp3')
OUT = os.path.join(ROOT, 'out')
SR = 44100
PRE = 0.35

# (global start, end, subtitr) — silencedetect bo'yicha
SEG = [
    (0.00, 2.80, "Bu videolarni men kamerasiz, aktyorsiz qildim."),
    (3.18, 4.86, "Hammasini sun'iy intellekt bilan."),
    (5.40, 6.81, "Avval kadrlarni yarataman."),
    (7.17, 9.82, "Keyin sun'iy intellekt mening ovozim bilan gapiradi."),
    (10.24, 11.11, "Oxirida montaj."),
    (11.73, 13.43, "Telefon va bir necha soat yetadi."),
    (13.94, 18.30, "SMM qilsangiz, biznesingiz bo'lsa yoki bloger bo'lmoqchi bo'lsangiz,"),
    (18.70, 20.93, "bu ko'nikma sizga pul topishga yordam beradi."),
    (21.54, 24.20, "Bizneslar hozir aynan shunday reklamani qidiryapti."),
    (24.73, 26.89, "Hammasini yopiq Telegram kanalda o'rgataman."),
    (27.37, 31.64, "Reels video, biznesga reklama, o'z ovozingiz va personajingiz,"),
    (32.11, 33.15, "Instagramni o'stirish."),
    (33.72, 35.31, "Narxi 250 000 so'm."),
    (35.73, 37.23, "Joy faqat 30 kishiga."),
    (37.70, 40.81, "Qatnashmoqchi bo'lsangiz, hoziroq Direct'ga «KURS» deb yozing."),
    (41.21, 42.64, "Joylar tugashidan oldin."),
]
STORY = {1: ([0, 1], 1.0), 2: ([2, 3, 4, 5], 1.2), 3: ([6, 7, 8], 1.2), 4: ([9, 10, 11, 12, 13], 1.6),
         5: ([14, 15], 2.6)}


def local(n):
    idx, tail = STORY[n]
    g0 = SEG[idx[0]][0]
    caps = [(SEG[i][2], SEG[i][0] - g0 + PRE, SEG[i][1] - g0 + PRE) for i in idx]
    dur = SEG[idx[-1]][1] - g0 + PRE + tail
    return caps, dur, g0


# ---------- ovoz konverti (to'lqin uchun) ----------
_raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', VOICE, '-ar', str(SR), '-ac', '1', '-f', 'f32le', '-'],
                      capture_output=True).stdout
VOX = np.frombuffer(_raw, np.float32)


def rms_at(gt, win=0.05):
    i = int(gt * SR); w = int(win * SR)
    seg = VOX[max(0, i - w):i + w]
    return float(np.sqrt((seg ** 2).mean())) if len(seg) else 0.0


def ltext(c, spr, x, cy, alpha=1.0):
    place(c, spr, x + spr.width / 2, cy, 1.0, alpha)


# ================= 1: KAMERA YO'Q =================
def camera_icon():
    if ('cam',) in mg._sc: return mg._sc[('cam',)]
    im = Image.new('RGBA', (520, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((60, 110, 460, 380), 44, outline=WHITE, width=18)
    d.rounded_rectangle((170, 60, 300, 120), 18, fill=WHITE)
    d.ellipse((180, 160, 340, 320), outline=WHITE, width=18)
    d.ellipse((380, 145, 410, 175), fill=GOLD)
    mg._sc[('cam',)] = im
    return im


def s1(c, t):
    caps, dur, g0 = local(1)
    p2 = 3.45
    if t < p2 + 0.3:
        e = clamp((t - p2) / 0.3); al = 1 - e
        place(c, camera_icon(), 540, 690, back((t + 0.3) / 0.32) * (1 - 0.3 * e), al)
        k = ease_out(prog(t, 0.35, 0.4))
        if k > 0 and al > 0:
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            x0, y0, x1, y1 = 330, 500, 750, 880
            d.line((x0, y0, x0 + (x1 - x0) * k, y0 + (y1 - y0) * k), fill=RED + (int(255 * al),), width=26)
            g = lay.filter(ImageFilter.GaussianBlur(14)); c.alpha_composite(g); c.alpha_composite(lay)
        ktext(c, t, "KAMERA YO'Q.", -0.3, 540, 1010, 128, end=p2)
        pill(c, t, "AKTYOR HAM.", 1.85, 540, 1170, 100, bg=RED, fg=WHITE, rot=-3, end=p2)
    flash(c, t, 3.5, 0.3, 0.4)
    ktext(c, t, "100%", 3.53, 540, 820, 330, fill=GOLD, glow=GOLD, anim='slam')
    ktext(c, t, "SUN'IY INTELLEKT", 3.95, 540, 1060, 86, track=4, anim='rise')
    ktext(c, t, "BILAN", 4.25, 540, 1170, 60, w='bold', fill=GRAY, anim='rise')
    subtitle(c, t, caps)


EV1 = [(0.0, 'hit'), (0.4, 'swish'), (1.85, 'pop'), (3.53, 'hit'), (3.95, 'pop')]


# ================= 2: 3 QADAM =================
CARD_Y = [470, 735, 1000]; CARD_H = 230
STEP_T = [-0.25, 2.11, 5.18]
LABELS = ['KADR', 'OVOZ', 'MONTAJ']
SUBL = ['rasm va sahnalar', 'mening AI ovozim', 'tayyor video']


def mini_kadr(c, t, x, y, active):
    cols = [(236, 186, 62), (64, 120, 255), (226, 58, 58), (120, 200, 160), (236, 186, 62), (180, 120, 255)]
    n = int(max(0, t + 0.5) / 0.18) % 9 if active else 6
    d = ImageDraw.Draw(c)
    for i in range(6):
        cx = x + (i % 3) * 92; cy = y + (i // 3) * 104
        on = i < n
        fill = cols[i] + (230 if on else 40,)
        d.rounded_rectangle((cx, cy, cx + 76, cy + 92), 12, fill=fill, outline=(255, 255, 255, 60), width=2)


def mini_wave(c, t, x, y, active, g0):
    d = ImageDraw.Draw(c)
    for i in range(14):
        if active:
            a = rms_at(g0 + t - PRE + (i - 7) * 0.035)
            h = 16 + min(170, a * 1400)
        else:
            h = 16 + 30 * abs(math.sin(i * 1.3))
        cx = x + i * 20
        d.rounded_rectangle((cx, y + 100 - h / 2, cx + 11, y + 100 + h / 2), 5,
                            fill=(GOLD if active else (120, 128, 145)) + (255,))


def mini_timeline(c, t, x, y, active):
    d = ImageDraw.Draw(c)
    tracks = [[(0, 90, BLUE), (96, 180, GOLD)], [(20, 150, RED), (160, 270, BLUE)], [(0, 270, (120, 200, 160))]]
    for r, tr in enumerate(tracks):
        for a, b, col in tr:
            d.rounded_rectangle((x + a, y + 30 + r * 52, x + b, y + 66 + r * 52), 8, fill=col + (220 if active else 70,))
    if active:
        ph = x + (t * 90) % 280
        d.line((ph, y + 16, ph, y + 190), fill=WHITE, width=5)


def s2(c, t):
    caps, dur, g0 = local(2)
    pill(c, t, "3 QADAM", -0.3, 540, 380, 50, bg=(255, 255, 255), fg=BG)
    act = 0 if t < STEP_T[1] else (1 if t < STEP_T[2] else 2)
    for i in range(3):
        lt = t - STEP_T[i]
        if lt < 0: continue
        dx = 700 * (1 - ease_out(lt / 0.45)); al = clamp(lt / 0.25)
        y = CARD_Y[i]; on = (i == act) and t < 6.6
        glass(c, (90 + dx, y, 990 + dx, y + CARD_H), 40, al,
              border=(GOLD + (230,)) if on else (255, 255, 255, 45),
              fill=(236, 186, 62, 26) if on else (255, 255, 255, 12))
        dim = 1.0 if on or t >= 6.6 else 0.55
        ltext(c, text_sprite(f"0{i + 1}", 'black', 92, GOLD), 120 + dx, y + 115, al * dim)
        ltext(c, text_sprite(LABELS[i], 'black', 74, WHITE), 255 + dx, y + 92, al * dim)
        ltext(c, text_sprite(SUBL[i], 'semi', 36, GRAY), 262 + dx, y + 160, al * dim)
        mx, my = 690 + dx, y + 18
        if al > 0.5:
            if i == 0: mini_kadr(c, lt, mx - 30, my, on)
            elif i == 1: mini_wave(c, t, mx - 20, my, on, g0)
            else: mini_timeline(c, lt, mx - 30, my, on)
    flash(c, t, 6.6, 0.25, 0.25)
    ktext(c, t, "TELEFON +", 6.67, 540, 1330, 100, anim='slam')
    ktext(c, t, "BIR NECHA SOAT", 7.25, 540, 1445, 92, fill=GOLD, glow=GOLD, anim='pop')
    subtitle(c, t, caps, y=1590)


EV2 = [(0.0, 'hit'), (2.11, 'swish'), (5.18, 'swish'), (6.67, 'hit'), (7.25, 'pop')]


# ================= 3: KIMGA =================
def s3(c, t):
    caps, dur, g0 = local(3)
    A, B = 4.9, 7.8
    ktext(c, t, "BU SIZMI?", -0.3, 540, 430, 64, w='xbold', fill=GRAY, end=A)
    pill(c, t, "SMM?", -0.3, 360, 640, 104, bg=GOLD, fg=BG, rot=5, end=A)
    pill(c, t, "BIZNES EGASI?", 1.3, 560, 860, 96, bg=WHITE, fg=BG, rot=-4, end=A)
    pill(c, t, "BLOGER?", 2.85, 700, 1080, 104, bg=BLUE, fg=WHITE, rot=4, end=A)
    flash(c, t, 5.0, 0.25, 0.3)
    ktext(c, t, "BU KO'NIKMA", 5.11, 540, 680, 96, anim='rise', end=B)
    ktext(c, t, "PUL", 6.0, 540, 900, 320, fill=GOLD, glow=GOLD, anim='slam', end=B)
    ktext(c, t, "TOPISHGA YORDAM BERADI", 6.45, 540, 1120, 62, w='xbold', anim='rise', end=B)
    flash(c, t, 7.9, 0.25, 0.3)
    ktext(c, t, "BIZNESLAR", 7.95, 540, 610, 132, anim='pop')
    lt = t - 8.3
    if lt >= 0:
        al = clamp(lt / 0.25); y0 = 760 + 40 * (1 - ease_out(lt / 0.4))
        glass(c, (110, y0, 970, y0 + 130), 65, al, border=(255, 255, 255, 90), fill=(255, 255, 255, 30))
        d = ImageDraw.Draw(c)
        d.ellipse((160, y0 + 38, 206, y0 + 84), outline=(255, 255, 255, int(220 * al)), width=7)
        d.line((198, y0 + 78, 222, y0 + 102), fill=(255, 255, 255, int(220 * al)), width=8)
        q = "AI video reklama"; n = int(clamp((t - 8.55) / 0.07 / len(q)) * len(q))
        f = font('bold', 52); d.text((255, y0 + 32), q[:n], font=f, fill=WHITE)
        if int(t * 2.5) % 2 == 0:
            cx = 255 + f.getlength(q[:n]) + 6; d.rectangle((cx, y0 + 36, cx + 5, y0 + 96), fill=GOLD)
    ktext(c, t, "QIDIRYAPTI", 9.75, 540, 1080, 124, fill=GOLD, glow=GOLD, anim='slam')
    subtitle(c, t, caps)


EV3 = [(0.0, 'hit'), (1.3, 'pop'), (2.85, 'pop'), (5.11, 'swish'), (6.0, 'hit'), (7.95, 'pop'),
       ] + [(8.55 + i * 0.07, 'tick') for i in range(16)] + [(9.75, 'hit')]


# ================= 4: TAKLIF =================
ITEMS = [("Reels video", 2.99), ("Biznesga reklama", 3.85), ("Ovoz va personaj", 5.1), ("Instagram o'stirish", 7.73)]


def s4(c, t):
    caps, dur, g0 = local(4)
    glass(c, (70, 330, 1010, 1505), 48, 1.0, border=(255, 255, 255, 55), fill=(255, 255, 255, 14))
    pill(c, t, "YOPIQ TELEGRAM KANAL", 1.2, 540, 420, 40, bg=TG, fg=WHITE)
    ktext(c, t, "BIRBALO AI", -0.3, 540, 545, 112, fill=GOLD, glow=GOLD)
    ktext(c, t, "AKADEMIYA", -0.2, 540, 660, 104)
    d = ImageDraw.Draw(c)
    for i, (txt, st) in enumerate(ITEMS):
        lt = t - st
        if lt < 0: continue
        y = 790 + i * 88; al = clamp(lt / 0.2); dx = 60 * (1 - ease_out(lt / 0.35))
        r = 26 * back(lt / 0.3, 2.5)
        d.ellipse((170 + dx - r, y - r, 170 + dx + r, y + r), fill=GOLD + (int(255 * al),))
        if lt > 0.12:
            d.line((157 + dx, y + 1, 167 + dx, y + 11, 184 + dx, y - 10), fill=BG + (255,), width=6)
        ltext(c, text_sprite(txt, 'xbold', 54, WHITE), 205 + dx, y, al)
    if t > 9.2:
        k = ease_out(prog(t, 9.2, 0.4)); d.line((540 - 400 * k, 1150, 540 + 400 * k, 1150), fill=(255, 255, 255, 60), width=3)
    ktext(c, t, "250 000 SO'M", 9.6, 540, 1245, 118, fill=GOLD, glow=GOLD, anim='slam')
    pill(c, t, "FAQAT 30 KISHI", 11.35, 540, 1365, 46, bg=RED, fg=WHITE)
    if t > 11.7:
        n = int(clamp((t - 11.7) / 1.1) * 30)
        for i in range(30):
            x = 180 + (i % 15) * 51; y = 1438 + (i // 15) * 34
            d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=(GOLD + (255,)) if i < n else (255, 255, 255, 50))
    subtitle(c, t, caps, y=1600)


EV4 = [(0.0, 'hit'), (1.2, 'pop')] + [(st, 'pop') for _, st in ITEMS] + [(9.6, 'hit'), (11.35, 'pop')] + \
      [(11.7 + i * 0.037, 'tick') for i in range(0, 30, 2)]


# ================= 5: CTA =================
def s5(c, t):
    caps, dur, g0 = local(5)
    ktext(c, t, "DIRECT'GA", -0.3, 540, 540, 150)
    lt = t + 0.3
    y0 = 700
    glass(c, (100, y0, 980, y0 + 130), 65, clamp(lt / 0.3), border=(255, 255, 255, 90), fill=(255, 255, 255, 26))
    d = ImageDraw.Draw(c); f = font('bold', 54)
    q = "KURS"; n = int(clamp((t - 2.1) / 0.5) * 4)
    if n == 0:
        d.text((150, y0 + 32), "Xabar yozing...", font=f, fill=(150, 156, 170))
    else:
        d.text((150, y0 + 32), q[:n], font=font('black', 60), fill=WHITE)
    if int(t * 2.5) % 2 == 0 and n < 4:
        cx = 150 + (font('black', 60).getlength(q[:n]) if n else 0); d.rectangle((cx, y0 + 34, cx + 5, y0 + 96), fill=GOLD)
    pr = 1 + (0.12 * math.sin((t - 2.6) * 9) * math.exp(-(t - 2.6) * 1.5) if t > 2.6 else 0)
    r = 46 * pr
    d.ellipse((900 - r, y0 + 65 - r, 900 + r, y0 + 65 + r), fill=GOLD)
    d.polygon([(880, y0 + 45), (928, y0 + 65), (880, y0 + 85), (888, y0 + 65)], fill=BG)
    ktext(c, t, "«KURS»", 2.6, 540, 1000, 180, fill=GOLD, glow=GOLD, anim='slam')
    ktext(c, t, "DEB YOZING", 3.0, 540, 1170, 100, anim='rise')
    if t > 3.86:
        pul = 1 + 0.04 * math.sin((t - 3.86) * 6)
        pill(c, t, "JOYLAR TUGASHIDAN OLDIN", 3.86, 540, 1320, 50, bg=RED, fg=WHITE)
    if t > 4.3:
        b = 18 * math.sin((t - 4.3) * 5); al = clamp((t - 4.3) / 0.3)
        for k in range(2):
            y = 1430 + b + k * 34
            d.line((490, y, 540, y + 36, 590, y), fill=GOLD + (int(255 * al * (1 - 0.4 * k)),), width=12, joint='curve')
    subtitle(c, t, caps)


EV5 = [(0.0, 'hit'), (2.1, 'tick'), (2.22, 'tick'), (2.35, 'tick'), (2.47, 'tick'), (2.6, 'hit'), (3.0, 'swish'),
       (3.86, 'pop')]

DRAW = {1: (s1, EV1, ('blue', 'red')), 2: (s2, EV2, ('blue', 'gold')), 3: (s3, EV3, ('gold', 'blue')),
        4: (s4, EV4, ('blue', 'gold')), 5: (s5, EV5, ('red', 'gold'))}


# ---------- audio ----------
def sfx(kind):
    if kind == 'pop':
        n = int(0.09 * SR); tt = np.arange(n) / SR
        f = 900 - 4000 * tt; return 0.22 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 45)
    if kind == 'tick':
        n = int(0.025 * SR); tt = np.arange(n) / SR; return 0.09 * np.sin(2 * np.pi * 2200 * tt) * np.exp(-tt * 260)
    if kind == 'hit':
        n = int(0.6 * SR); tt = np.arange(n) / SR
        f = 90 * np.exp(-tt * 6) + 45; return 0.42 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7)
    if kind == 'swish':
        n = int(0.25 * SR); tt = np.arange(n) / SR
        f = 300 + 1600 * tt / 0.25; env = np.sin(np.pi * tt / 0.25) ** 2
        return 0.07 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env
    return np.zeros(1)


def audio(n):
    caps, dur, g0 = local(n)
    idx, _ = STORY[n]
    N = int(dur * SR); mix = np.zeros(N, np.float32)
    a = int(max(0, g0 - 0.05) * SR); b = int((SEG[idx[-1]][1] + 0.12) * SR)
    v = VOX[a:b].copy(); st = int((PRE - 0.05) * SR)
    mix[st:st + len(v)] += v[:N - st]
    tt = np.arange(N) / SR
    env = np.clip(tt / 1.0, 0, 1) * np.clip((dur - tt) / 0.8, 0, 1)
    for fq in (110.0, 164.81, 220.0, 261.63):
        mix += 0.007 * np.sin(2 * np.pi * fq * tt) * env
    for at, kind in DRAW[n][1]:
        s = sfx(kind); i = int(max(0, at) * SR); m = min(len(s), N - i)
        if m > 0: mix[i:i + m] += s[:m]
    raw = os.path.join(OUT, f'_a{n}.wav')
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(raw, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())
    fin = os.path.join(OUT, f'_a{n}_n.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af',
                    'loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100', '-ac', '2', fin], check=True)
    return fin


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    mode = sys.argv[1]
    ns = [int(x) for x in sys.argv[2:]] or [1, 2, 3, 4, 5]
    for n in ns:
        fn, ev, mood = DRAW[n]; caps, dur, _ = local(n)
        if mode == 'sheet':
            ts = [0.0] + [dur * k / 5 for k in range(1, 5)] + [dur - 0.1]
            ims = [frame(fn, t, mood).resize((270, 480)) for t in ts]
            sh = Image.new('RGB', (270 * len(ims), 480))
            for i, im in enumerate(ims): sh.paste(im, (i * 270, 0))
            sh.save(os.path.join(OUT, f'sheet{n}.jpg'), quality=85)
            print(n, f'{dur:.2f}s', ' '.join(f'{t:.1f}' for t in ts))
        else:
            a = audio(n)
            render(fn, dur, os.path.join(OUT, f'istoriya_{n}.mp4'), a, mood)
            print('done', n, f'{dur:.2f}s')
