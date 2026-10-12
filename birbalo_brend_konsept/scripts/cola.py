"""Coca-Cola × Samarqand — norasmiy FOOH konsept. python3 scripts/cola.py sheet|render"""
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
    ('Drone_approaching_giant_bottle', 0.0, 2.6, lambda u: u * 1.15, 8),
    ('Condensation_droplets_on_bottle', 2.6, 1.6, lambda u: u, 6),
    ('Bottle_cap_twists_and_hisses', 4.2, 1.6, lambda u: u, 3),
    ('Cola_spray_erupts_upward', 5.8, 3.0, lambda u: 3.6 * (u / 3.0) ** 0.75, 0),
    ('Bubbles_falling_over_people_square', 8.8, 2.0, lambda u: 0.3 + u, 4),
    ('Carbonation_bubbles_rise_in_cola', 10.8, 2.0, lambda u: u * 0.9, 7),
    ('Vendor_hands_man_Coca-Cola_bottle', 12.8, 2.2, lambda u: 0.5 + u * 1.2, -60),
    ('Illuminated_Registan_Square_with_', 15.0, 3.0, lambda u: u * 1.1, 3),
]
END0 = 18.0; DUR = 21.6
CUTS = [c[1] for c in CLIPS[1:]] + [END0]
HITS = [(0.0, 0.5), (4.32, 1.0), (5.8, 1.2), (18.15, 0.7), (18.55, 0.7), (18.95, 0.9)]

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
        mask_up(w, t, "AGAR COCA-COLA", -0.1, 540, 360, 92, end=2.45)
        mask_up(w, t, "SAMARQANDGA KELSA...", 0.35, 540, 465, 74, w='xbold', fill=(255, 220, 200), end=2.45)
        mask_up(w, t, "HAR BIR PUFAKCHADA", 10.9, 540, 820, 70, w='xbold', end=12.65)
        big(w, t, "SAMARQAND", 11.3, 540, 940, 140, fill=WHITE, glow=(255, 170, 60), sw_at=11.8, end=12.65)
        big(w, t, "COCA-COLA", 15.35, 540, 380, 120, fill=WHITE, glow=RED_C, sw_at=16.0, anim='grow')
        mask_up(w, t, "×  SAMARQAND", 15.7, 540, 500, 70, w='xbold', fill=(255, 215, 150))
        flash(w, t, 4.32, 0.18, 0.55); flash(w, t, 5.8, 0.22, 0.7)
        burst(w, t, 5.85, 540, 760, n=50, col=(255, 240, 220), speed=1400, seed=21)
    else:
        w = endcard_bg()
        lt = t - END0
        k = expo_out(lt / 0.4)
        big(w, t, "1 PROMPT", 18.15, 540, 640, 150, fill=GOLD, glow=GOLD)
        big(w, t, "0 SO'M", 18.55, 540, 800, 150)
        big(w, t, "1 KUN", 18.95, 540, 960, 150, fill=GOLD, glow=GOLD, sw_at=19.5)
        pill(w, t, "@birbalo_ai", 19.5, 540, 1150, 58, bg=WHITE, fg=BG)
        mask_up(w, t, "Brendingiz uchun ham qilamiz", 19.8, 540, 1270, 50, w='xbold', fill=(225, 228, 238))
        mask_up(w, t, "Direct'ga yozing", 20.05, 540, 1345, 50, w='xbold', fill=GOLD)
        flash(w, t, END0, 0.2, 0.5)
    # kesishlarda zoom blur
    zb = 0.0
    for ct in CUTS:
        if abs(t - ct) < 0.12: zb = max(zb, 3.2 * (1 - abs(t - ct) / 0.12))
    dx, dy, rot = shake(t, HITS)
    ca = sum(14 * amp * math.exp(-(t - at) * 8) for at, amp in HITS if t >= at)

    def ov(c):
        disclaimer(c)
    return dict(world=w, cam=(1.0 + (0.03 if t < END0 else 0), rot, dx, dy), ca=ca, zblur=zb, beams=0, overlay=ov)


# ---------- audio ----------
def load_audio(name):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', os.path.join(SRC, name + '.mp4'), '-ar', str(SR), '-ac', '1',
                          '-f', 'f32le', '-'], capture_output=True).stdout
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
        a = load_audio(name); st = int(s * SR); n = int(d * SR)
        seg = a[:n] * (10 ** (gdb / 20))
        fade = np.ones(len(seg)); k = min(len(seg), int(0.03 * SR)); fade[:k] = np.linspace(0, 1, k); fade[-k:] = np.linspace(1, 0, k)
        mix[st:st + len(seg)] += seg * fade
    ev = [(4.32, tone(140, 45, 0.6, 0.5, 6)), (5.8, tone(110, 38, 0.9, 0.6, 4)), (4.5, tone(200, 900, 1.3, 0.06, 0, 'swell'))]
    for ct in CUTS: ev.append((ct - 0.18, tone(300, 2400, 0.35, 0.07, 0, 'bell')))
    for at in (18.15, 18.55, 18.95): ev.append((at, tone(120, 45, 0.6, 0.45, 7)))
    ev += [(19.5, tone(950, 500, 0.09, 0.2, 45)), (19.8, tone(950, 500, 0.09, 0.15, 45))]
    for at, s in ev:
        i = int(at * SR); m = min(len(s), N - i); mix[i:i + m] += s[:m]
    tt = np.arange(N) / SR; env = np.clip((tt - END0) / 0.4, 0, 1) * np.clip((DUR - tt) / 0.8, 0, 1)
    for fq in (55.0, 110.0, 164.81, 220.0): mix += 0.008 * np.sin(2 * np.pi * fq * tt) * env
    raw = os.path.join(OUT, '_a.wav')
    with wave.open(raw, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
    fin = os.path.join(OUT, '_a_n.wav')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', 'loudnorm=I=-13:TP=-1.5:LRA=11,aresample=44100',
                    '-ac', '2', fin], check=True)
    return fin


if __name__ == '__main__':
    if sys.argv[1] == 'sheet':
        ts = [float(x) for x in (sys.argv[2].split(',') if len(sys.argv) > 2 else
                                 '0.05,1.3,3.2,4.4,6.5,9.5,11.8,13.8,16.2,18.4,19.2,21.4'.split(','))]
        ims = [Image.fromarray(compose(story, t)).resize((216, 384)) for t in ts]
        sh = Image.new('RGB', (216 * len(ims), 384))
        for i, im in enumerate(ims): sh.paste(im, (i * 216, 0))
        sh.save(os.path.join(OUT, 'sheet.jpg'), quality=85)
    else:
        render(story, DUR, os.path.join(OUT, 'cola_samarqand_raw.mp4'), audio()); print('done')
