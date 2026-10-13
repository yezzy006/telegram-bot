import sys, subprocess, numpy as np
f, crop, t0, dur = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
W,H=160,90 if 'tpl' in sys.argv[5] else 160
H=90 if sys.argv[5]=='tpl' else 284
cmd=["ffmpeg","-loglevel","error","-ss",t0,"-t",dur,"-i",f,"-vf",f"{crop}scale={W}:{H},format=gray","-r","30","-f","rawvideo","-"]
raw=subprocess.run(cmd,capture_output=True).stdout
fr=np.frombuffer(raw,np.uint8).reshape(-1,H,W).astype(float)
d=np.abs(np.diff(fr,axis=0)).mean(axis=(1,2))
still=(d<1.0).mean()
# events: local peaks over threshold
thr=np.percentile(d,75); ev=[i for i in range(1,len(d)-1) if d[i]>d[i-1] and d[i]>=d[i+1] and d[i]>max(6,thr)]
# merge events closer than 4 frames
m=[]; 
for e in ev:
    if not m or e-m[-1]>4: m.append(e)
secs=len(d)/30
print(f"{sys.argv[5]}: {secs:.1f}s  mean motion {d.mean():.2f}  still frames {still*100:.0f}%  big changes {len(m)} -> every {secs/max(1,len(m)):.2f}s")
