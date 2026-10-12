"""Coca-Cola × Samarqand — hazil versiyasi (gaplar bilan). python3 scripts/cola.py sheet|render"""
import sys, os, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from fx import *
import mg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'cola', 'src'); OUT = os.path.join(ROOT, 'cola')
SR = 44100
RED_C = (230, 30, 40)

# (fayl, chiqish boshlanishi, chiqish davomiyligi, src_vaqt(u) funksiyasi, audio gain dB)
CLIPS = [
    ('Young_woman_running_and_shouting', 0.0, 4.0, lambda u: u, -99),
    ('Drone_approaching_giant_bottle', 4.0, 3.4, lambda u: u, 6),
    ('Condensation_droplets_on_bottle', 7.4, 1.4, lambda u: u, 4),
    ('Vendor_lifting_glass_bottle', 8.8, 4.0, lambda u: u * 0.98, -99),
    ('Bottle_cap_twists_and_hisses', 12.8, 1.6, lambda u: u, 2),
    ('Cola_spray_erupts_upward', 14.4, 3.0, lambda u: 3.6 * (u / 3.0) ** 0.75, 0),
    ('Woman_reacts_to_foam_quilt', 17.4, 2.5, lambda u: 1.4 + u, -99),
    ('Bubbles_falling_over_people_square', 19.9, 1.6, lambda u: 0.3 + u, 2),
    ('Vendor_hands_man_Coca-Cola_bottle', 21.5, 4.4, lambda u: u * 0.9, -99),
    ('Illuminated_Registan_Square_with_', 25.9, 2.7, lambda u: u * 1.1, 2),
]
END0 = 28.6; DUR = 32.0
CUTS = [c[1] for c in CLIPS[1:]] + [END0]
HITS = [(0.0, 0.5), (12.92, 1.0), (14.4, 1.2), (28.75, 0.7), (29.15, 0.7), (29.55, 0.9)]
VO = 'cola/voice/'
# (vaqt, fayl, bosh, oxir, subtitr)
LINES = [
    (0.1, 'yigit.mp3', 0.0, 2.32, "Tez yuringlar! Registonda nimadir bo'lyapti!"),
    (2.3, 'qiz_v4b.mp3', 0.0, 1.74, "MrBeast yana kelganmish!"),
    (4.9, 'yigit_v4.mp3', 2.08, 4.48, "Yo'q. Bu undan ham kattaroq."),
    (8.95, 'sotuvchi.mp3', 0.0, 3.75, "Ukam, menda kichkinasi ham bor. Sovuq. Arzon."),
    (14.6, 'yigit.mp3', 9.15, 9.95, "Voooy!"),
    (14.75, 'qiz.mp3', 1.75, 2.69, None),
    (17.5, 'opa.mp3', 0.0, 2.18, "Endi yuvgan ko'rpachalarim-a!"),
    (21.7, 'yigit_v4.mp3', 0.0, 1.72, "Aka, kattasini kim ochdi?"),
    (23.6, 'sotuvchi.mp3', 4.34, 6.53, "Men emas. O'zi chidolmadi."),
]
CAPS = [(txt, t, t + (b - a)) for t, f, a, b, txt in LINES if txt]

_cur = {'name': None, 'frames': None}


def clip_frames(name):
    if _cur['name'] != name:
        raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', os.path.join(SRC, name + '.mp4'), '-f', 'rawvideo',
                              '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
        n = len(raw) // (720 * 1280 * 3)
        _cur['name'] = name
        _cur['frames'] = [np.frombuffer(raw[i * 2764800:(i + 1) * 2764800], np.uint8).reshape(1280, 720, 3) for i in range(n)]
    return _cur['frames']


def grade(im):
    a = np.asarray(im).astype(np.float32)
    a = (a - 128) * 1.06 + 128
    a[..., 0] *= 1.03; a[..., 2] *= 0.96
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def video_at(t):
    for name, s, d, fmap, _ in CLIPS:
        if s <= t < s + d:
            fr = clip_frames(name); st = fmap(t - s)
            i = min(len(fr) - 1, int(st * 24))
            im = Image.fromarray(fr[i]).resize((W, H), Image.LANCZOS)
            im = grade(im).filter(ImageFilter.UnsharpMask(2, 60, 2))
            z = 1.0 + 0.05 * (t - s) / d
            if z > 1.001:
                im = im.resize((int(W * z), int(H * z)), Image.BILINEAR)
                ox, oy = (im.width - W) // 2, (im.height - H) // 2; im = im.crop((ox, oy, ox + W, oy + H))
            return im.convert('RGBA')
    return None


_last = {}


def endcard_bg():
    if 'bg' not in _last:
        name, s, d, fmap, _ = CLIPS[-1]
        fr = clip_frames(name)[-1]
        im = Image.fromarray(fr).resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(26))
        im = Image.blend(im, Image.new('RGB', (W, H), (6, 6, 10)), 0.55)
        _last['bg'] = im.convert('RGBA')
    return _last['bg'].copy()


def disclaimer(c):
    f = font('semi', 26); s = "Norasmiy AI konsept · Coca-Cola bilan bog'liq emas"
    w = f.getlength(s) + 36; x = (W - w) / 2; d = ImageDraw.Draw(c)
    d.rounded_rectangle((x, 1500, x + w, 1544), 22, fill=(0, 0, 0, 120))
    d.text((x + 18, 1507), s, font=f, fill=(235, 235, 235, 220))


def story(t):
    if t < END0:
        w = video_at(t)
        # pastki/yuqori qorong'ilik (yozuv o'qilishi uchun)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for i in range(0, 520, 8): d.rectangle((0, i, W, i + 8), fill=(0, 0, 0, int(120 * (1 - i / 520))))
        w.alpha_composite(lay)
        big(w, t, "KIM KELDI?!", -0.1, 540, 360, 130, fill=WHITE, glow=RED_C, end=3.85)
        big(w, t, "COCA-COLA", 26.1, 540, 380, 120, fill=WHITE, glow=RED_C, sw_at=26.7, anim='grow')
        mask_up(w, t, "×  SAMARQAND", 26.45, 540, 500, 70, w='xbold', fill=(255, 215, 150))
        flash(w, t, 12.92, 0.18, 0.55); flash(w, t, 14.4, 0.22, 0.7)
        burst(w, t, 14.45, 540, 760, n=50, col=(255, 240, 220), speed=1400, seed=21)
    else:
        w = endcard_bg()
        lt = t - END0
        k = expo_out(lt / 0.4)
        big(w, t, "1 PROMPT", 28.75, 540, 640, 150, fill=GOLD, glow=GOLD)
        big(w, t, "0 SO'M", 29.15, 540, 800, 150)
        big(w, t, "1 KUN", 29.55, 540, 960, 150, fill=GOLD, glow=GOLD, sw_at=30.1)
        pill(w, t, "@birbalo_ai", 30.1, 540, 1150, 58, bg=WHITE, fg=BG)
        mask_up(w, t, "Brendingiz uchun ham qilamiz", 30.4, 540, 1270, 50, w='xbold', fill=(225, 228, 238))
        mask_up(w, t, "Direct'ga yozing", 30.65, 540, 1345, 50, w='xbold', fill=GOLD)
        flash(w, t, END0, 0.2, 0.5)
    # kesishlarda zoom blur
    zb = 0.0
    for ct in CUTS:
        if abs(t - ct) < 0.12: zb = max(zb, 3.2 * (1 - abs(t - ct) / 0.12))
    dx, dy, rot = shake(t, HITS)
    ca = sum(14 * amp * math.exp(-(t - at) * 8) for at, amp in HITS if t >= at)

    def ov(c):
        disclaimer(c)
        if t < END0: subtitle(c, t, CAPS, y=1360, size=50)
    return dict(world=w, cam=(1.0 + (0.03 if t < END0 else 0), rot, dx, dy), ca=ca, zblur=zb, beams=0, overlay=ov)


# ---------- audio ----------
def load_audio(name):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', os.path.join(SRC, name + '.mp4'), '-ar', str(SR), '-ac', '1',
                          '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def load_audio_f(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ar', str(SR), '-ac', '1', '-f', 'f32le', '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def tone(f0, f1, dur, amp, decay=0.0, env=None):
    n = int(dur * SR); tt = np.arange(n) / SR; f = f0 + (f1 - f0) * tt / dur
    y = amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * decay)
    if env == 'swell': y *= (tt / dur) ** 2
    if env == 'bell': y *= np.sin(np.pi * tt / dur) ** 2
    return y


def audio():
    N = int(DUR * SR); mix = np.zeros(N, np.float32)
    for name, s, d, fmap, gdb in CLIPS:
        if gdb < -90: continue
        a = load_audio(name); st = int(s * SR); n = int(d * SR)
        seg = a[:n] * (10 ** (gdb / 20))
        fade = np.ones(len(seg)); k = min(len(seg), int(0.03 * SR)); fade[:k] = np.linspace(0, 1, k); fade[-k:] = np.linspace(1, 0, k)
        mix[st:st + len(seg)] += seg * fade
    crowd = load_audio('Bubbles_falling_over_people_square')[:int(4.0 * SR)] * 0.5
    mix[:len(crowd)] += crowd
    amb = np.ones(N, np.float32)
    vo = np.zeros(N, np.float32)
    for t0, f, a0, b0, _ in LINES:
        v = load_audio_f(os.path.join(ROOT, VO + f))[int(a0 * SR):int(b0 * SR)]
        i = int(t0 * SR); m = min(len(v), N - i); vo[i:i + m] += v[:m] * 1.4
        amb[max(0, i - 4000):i + m + 4000] = 0.45
    k = int(0.08 * SR); amb = np.convolve(amb, np.ones(k) / k, mode='same').astype(np.float32)
    mix = mix * amb + vo
    ev = [(12.92, tone(140, 45, 0.6, 0.5, 6)), (14.4, tone(110, 38, 0.9, 0.6, 4)), (13.1, tone(200, 900, 1.3, 0.06, 0, 'swell'))]
    for ct in CUTS: ev.append((ct - 0.18, tone(300, 2400, 0.35, 0.07, 0, 'bell')))
    for at in (28.75, 29.15, 29.55): ev.append((at, tone(120, 45, 0.6, 0.45, 7)))
    ev += [(30.1, tone(950, 500, 0.09, 0.2, 45)), (30.4, tone(950, 500, 0.09, 0.15, 45))]
    for at, s in ev:
        i = int(at * SR); m = min(len(s), N - i); mix[i:i + m] += s[:m]
    tt = np.arange(N) / SR; env = np.clip((tt - END0) / 0.4, 0, 1) * np.clip((DUR - tt) / 0.8, 0, 1)
    for fq in (55.0, 110.0, 164.81, 220.0): mix += 0.008 * np.sin(2 * np.pi * fq * tt) * env
    raw = os.path.join(OUT, '_ah.wav')
    with wave.open(raw, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
    fin = os.path.join(OUT, '_ah_n.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', 'loudnorm=I=-13:TP=-1.5:LRA=11,aresample=44100',
                    '-ac', '2', fin], check=True)
    return fin


if __name__ == '__main__':
    if sys.argv[1] == 'sheet':
        ts = [float(x) for x in (sys.argv[2].split(',') if len(sys.argv) > 2 else
                                 '0.05,3.0,6.0,10.0,13.0,15.5,18.5,22.5,24.5,27.0,30.0,31.8'.split(','))]
        ims = [Image.fromarray(compose(story, t)).resize((216, 384)) for t in ts]
        sh = Image.new('RGB', (216 * len(ims), 384))
        for i, im in enumerate(ims): sh.paste(im, (i * 216, 0))
        sh.save(os.path.join(OUT, 'sheet.jpg'), quality=85)
    else:
        render(story, DUR, os.path.join(OUT, 'cola_hazil_raw.mp4'), audio()); print('done')
