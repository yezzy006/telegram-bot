"""Tungi g'aroyibotlar I. Lift — qo'rqinchli fon musiqasi (31 s). python3 scripts/lift_music.py out.wav"""
import sys, wave, numpy as np
from scipy.signal import lfilter
SR = 44100; DUR = 31.0; N = int(DUR * SR); t = np.arange(N) / SR


def env_ad(n, a, d):
    e = np.ones(n); ka = int(a * SR); kd = int(d * SR)
    if ka: e[:ka] = np.linspace(0, 1, ka)
    if kd: e[-kd:] *= np.linspace(1, 0, kd)
    return e


def add(buf, at, s):
    i = int(at * SR); m = min(len(s), len(buf) - i)
    if m > 0: buf[i:i + m] += s[:m]


def reverb(x, mix=0.35):
    out = np.zeros_like(x)
    for dl, g in [(1557, 0.84), (1617, 0.83), (1491, 0.85), (1422, 0.86), (1277, 0.87), (1356, 0.85)]:
        a = np.zeros(dl + 1); a[0] = 1; a[dl] = -g
        out += lfilter([1], a, x)
    out /= 6
    for dl, g in [(225, 0.5), (556, 0.5)]:
        b = np.zeros(dl + 1); b[0] = -g; b[dl] = 1
        a = np.zeros(dl + 1); a[0] = 1; a[dl] = -g
        out = lfilter(b, a, out)
    return x * (1 - mix) + out * mix


music = np.zeros(N); fx = np.zeros(N)
# 1) chuqur guvillash: D1 + A1 + D2, sekin ko'tarilib-tushadi
sw = 0.55 + 0.45 * np.sin(2 * np.pi * t / 14 - 1.2) ** 2
drone = (0.20 * np.sin(2 * np.pi * 36.71 * t) + 0.12 * np.sin(2 * np.pi * 55.0 * t) + 0.08 * np.sin(2 * np.pi * 73.42 * t))
music += drone * sw * env_ad(N, 3.0, 4.0)
# 2) kichik sekunda klasterlari (sahna almashganda)
for at in (4, 8, 12, 16, 20, 24):
    n = int(3.5 * SR); tt = np.arange(n) / SR
    e = np.sin(np.pi * np.clip(tt / 3.5, 0, 1)) ** 2
    s = 0.035 * (np.sin(2 * np.pi * 587.3 * tt) + np.sin(2 * np.pi * 622.3 * tt) + 0.6 * np.sin(2 * np.pi * 880 * tt)) * e
    add(music, at - 1.6, s)


# 3) musiqa qutisi (D minor, tritonli motiv)
def bell(f, dur=2.4, amp=0.10):
    n = int(dur * SR); tt = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * f * 2.01 * tt) + 0.12 * np.sin(2 * np.pi * f * 3.98 * tt)
    return amp * y * np.exp(-tt * 2.6) * env_ad(n, 0.004, 0.05)


D5, F5, A5, Gs5, E5, C6, D6 = 587.3, 698.5, 880.0, 830.6, 659.3, 1046.5, 1174.7
motif = [(0, D6), (0.75, A5), (1.5, F5), (2.25, Gs5), (3.4, E5)]
for base in (1.0, 9.0, 20.5):
    for dt, f in motif: add(music, base + dt, bell(f))
add(music, 29.0, bell(D5, 3.5, 0.12))
# 4) ot chiqishidan oldin teskari ko'tarilish + zarba (4-sahna, ~12.6 s)
n = int(2.2 * SR); tt = np.arange(n) / SR
rev = 0.12 * np.sin(2 * np.pi * (220 + 40 * tt) * tt) * (tt / 2.2) ** 3
add(fx, 10.45, rev)
n = int(2.5 * SR); tt = np.arange(n) / SR
boom = 0.75 * np.sin(2 * np.pi * np.cumsum(70 * np.exp(-tt * 3) + 28) / SR) * np.exp(-tt * 2.2)
add(fx, 12.65, boom)
# 5) yurak urishi 5-sahnada
for k in range(6):
    for off, a in ((0, 0.38), (0.22, 0.25)):
        n = int(0.25 * SR); tt = np.arange(n) / SR
        add(fx, 16.3 + k * 0.62 + off, a * np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 18))
# 6) soat chiqillashi 6-sahnada
for k in range(8):
    n = int(0.02 * SR); tt = np.arange(n) / SR
    add(fx, 20.2 + k * 0.5, (0.10 if k % 2 == 0 else 0.07) * np.sin(2 * np.pi * 3200 * tt) * np.exp(-tt * 300))
# 7) yakun: eshik yopilish zarbasi
n = int(1.8 * SR); tt = np.arange(n) / SR
add(fx, 27.9, 0.5 * np.sin(2 * np.pi * np.cumsum(90 * np.exp(-tt * 5) + 40) / SR) * np.exp(-tt * 3))

mix = reverb(music, 0.45) + reverb(fx, 0.25)
mix *= env_ad(N, 0.05, 1.5)
mix = mix / np.abs(mix).max() * 0.85
out = sys.argv[1] if len(sys.argv) > 1 else 'lift_music.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok', out)
