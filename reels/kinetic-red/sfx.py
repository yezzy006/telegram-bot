import numpy as np, wave
from scipy.signal import butter, sosfilt
RATE=1.12; SR=48000; END=41.1/RATE; N=int((END+1)*SR); out=np.zeros(N); rng=np.random.default_rng(5)
SCENES=[0,2.48,4.36,9.12,10.2,17.28,18.4,20.44,24.12,26.12,27.2,30.24,33.81,34.64,36.16,36.88]
def f(x,k,c): return sosfilt(butter(4,c,k,fs=SR,output='sos'),x)
def add(s,at,g):
    i=max(0,int(at*SR)); n=min(len(s),N-i); out[i:i+n]+=s[:n]*g
def whoosh(d=.3):
    n=int(d*SR); t=np.linspace(0,1,n); env=np.sin(np.pi*t**.6)**2
    x=f(rng.standard_normal(n),'bandpass',[400,4500]); return x*env/np.abs(x).max()
def hit():
    n=int(.5*SR); t=np.arange(n)/SR
    b=np.sin(2*np.pi*np.cumsum(48+90*np.exp(-t*28))/SR)*np.exp(-t*6)
    c=f(rng.standard_normal(n),'lowpass',3000)*np.exp(-t*50)*.5
    return np.tanh(1.5*(b+c))
def tick():
    n=int(.05*SR); t=np.arange(n)/SR; return f(rng.standard_normal(n),'highpass',3000)*np.exp(-t*80)
for s in SCENES[1:]: add(whoosh(),s/RATE-.17,.55)
for h in [1.52,9.12,17.28,26.12,19.45,25.09,36.16]: add(hit(),h/RATE,.9)
add(hit(),13.8/RATE,.5)
for k in range(7): add(tick(),35.4/RATE+k*.05,.35)
out=out/np.abs(out).max()*.9
with wave.open("sfx.wav","wb") as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((out*32767).astype(np.int16).tobytes())
