import sys, os, subprocess, pathlib
from playwright.sync_api import sync_playwright
d = pathlib.Path(sys.argv[1]).resolve(); mode = sys.argv[2]; import os; HTML=os.environ.get("HTML","index.html")
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get("CHROME") or None)
    pg = b.new_page(viewport={"width":1080,"height":1920})
    pg.goto((d/HTML).as_uri()); pg.wait_for_function("window.READY===true"); pg.wait_for_timeout(300)
    errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
    if mode == "sheet":
        for t in [float(x) for x in sys.argv[3].split(",")]:
            pg.evaluate(f"render({t})"); pg.screenshot(path=str(d/f"sheet_{t:05.2f}.png"))
    else:
        end = pg.evaluate("END"); n = int(end*30)
        ff = subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","image2pipe","-framerate","30","-i","-",
            "-i",str(d/os.environ.get("AUDIO","audio.wav")),"-c:v","libx264","-pix_fmt","yuv420p","-crf","18","-preset","medium",
            "-c:a","aac","-b:a","192k","-af","apad","-t",str(end),"-movflags","+faststart",str(d/"out.mp4")], stdin=subprocess.PIPE)
        for i in range(n):
            pg.evaluate(f"render({i/30})"); ff.stdin.write(pg.screenshot(type="jpeg", quality=95))
        ff.stdin.close(); ff.wait()
    print("errors:", errs); b.close()
