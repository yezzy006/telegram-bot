"""Tungi g'aroyibotlar: musiqa + klip tovushlari + hikoyachi -> wav"""
import sys, os, subprocess, wave, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
_src = open(os.path.join(os.path.dirname(__file__), 'lift_music.py')).read()
_src = _src[:_src.index('music = np.zeros(N)')]
_ns = {}; exec(_src, _ns)
env_ad, add, reverb = _ns['env_ad'], _ns['add'], _ns['reverb']
D5, F5, A5, Gs5, E5, D6 = 587.3, 698.5, 880.0, 830.6, 659.3, 1174.7
SR_ = 44100


def bell(f, dur=2.4, amp=0.10):
    n = int(dur * SR_); tt = np.arange(n) / SR_
    y = np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 2.01 * tt) + 0.12 * np.sin(2 * np.pi * f * 3.98 * tt)
    return amp * y * np.exp(-tt * 2.6) * env_ad(n, 0.004, 0.05)
from lift import CLIPS, LINES, DUR, END0, SRC, NARR, OUT
SR = 44100; N = int(DUR * SR); t = np.arange(N) / SR


def load(p):
    return np.frombuffer(subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', p, '-ar', str(SR), '-ac', '1', '-f', 'f32le', '-'],
                                        capture_output=True).stdout, np.float32).astype(np.float64)


music = np.zeros(N); fx = np.zeros(N)
sw = 0.55 + 0.45 * np.sin(2 * np.pi * t / 14 - 1.2) ** 2
music += (0.20 * np.sin(2 * np.pi * 36.71 * t) + 0.12 * np.sin(2 * np.pi * 55 * t) + 0.08 * np.sin(2 * np.pi * 73.42 * t)) * sw * env_ad(N, 2.0, 3.0)
for c in CLIPS[1:]:
    n = int(3.0 * SR); tt = np.arange(n) / SR; e = np.sin(np.pi * tt / 3.0) ** 2
    add(music, c[1] - 1.4, 0.03 * (np.sin(2 * np.pi * 587.3 * tt) + np.sin(2 * np.pi * 622.3 * tt) + 0.6 * np.sin(2 * np.pi * 880 * tt)) * e)
motif = [(0, D6), (0.75, A5), (1.5, F5), (2.25, Gs5), (3.4, E5)]
for base in (0.3, 10.6, 22.6):
    for dt, f in motif: add(music, base + dt, bell(f))
add(music, END0 + 0.7, bell(D5, 3.5, 0.12))
# ot: teskari ko'tarilish + zarba
n = int(1.8 * SR); tt = np.arange(n) / SR
add(fx, 2.85, 0.12 * np.sin(2 * np.pi * (220 + 40 * tt) * tt) * (tt / 1.8) ** 3)
n = int(2.5 * SR); tt = np.arange(n) / SR
add(fx, 4.6, 0.75 * np.sin(2 * np.pi * np.cumsum(70 * np.exp(-tt * 3) + 28) / SR) * np.exp(-tt * 2.2))
# soat chiqillashi (8-10.5)
for k in range(5):
    n = int(0.02 * SR); tt = np.arange(n) / SR
    add(fx, 8.2 + k * 0.5, 0.10 * np.sin(2 * np.pi * 3200 * tt) * np.exp(-tt * 300))
# budka: yurak urishi (22.5-26.5)
for k in range(6):
    for off, a in ((0, 0.38), (0.22, 0.25)):
        n = int(0.25 * SR); tt = np.arange(n) / SR
        add(fx, 22.7 + k * 0.62 + off, a * np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 18))
# yakun: eshik yopilish
n = int(1.8 * SR); tt = np.arange(n) / SR
add(fx, END0 - 0.05, 0.5 * np.sin(2 * np.pi * np.cumsum(90 * np.exp(-tt * 5) + 40) / SR) * np.exp(-tt * 3))
bed = reverb(music, 0.45) + reverb(fx, 0.25)
# kliplarning tabiiy tovushi
amb = np.zeros(N)
for name, s, d, fmap, _ in CLIPS:
    a = load(os.path.join(SRC, name + '.mp4'))
    st = int(fmap(0) * SR); seg = a[st:st + int(d * SR)]
    if len(seg) == 0: continue
    k = min(len(seg), int(0.08 * SR)); e = np.ones(len(seg)); e[:k] = np.linspace(0, 1, k); e[-k:] = np.linspace(1, 0, k)
    pk = np.abs(seg).max() or 1
    add(amb, s, seg / pk * 0.18 * e)
# hikoyachi
narr = load(NARR); vo = np.zeros(N); duck = np.ones(N)
for t0, a0, b0, _ in LINES:
    v = narr[int(a0 * SR):int(b0 * SR)]; add(vo, t0, v * 1.0)
    i = int(t0 * SR); duck[max(0, i - 6000):i + len(v) + 6000] = 0.55
k = int(0.15 * SR); duck = np.convolve(duck, np.ones(k) / k, mode='same')
vo = reverb(vo, 0.12)
mix = (bed / np.abs(bed).max() * 0.5 + amb) * duck + vo / np.abs(vo).max() * 0.8
mix *= env_ad(N, 0.03, 1.5); mix = mix / np.abs(mix).max() * 0.9
raw = os.path.join(OUT, '_mix.wav')
with wave.open(raw, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
fin = os.path.join(OUT, '_mix_n.wav')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100', '-ac', '2', fin], check=True)
print(fin)
