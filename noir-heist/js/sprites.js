'use strict';
// ===== 5. Ko'cha spritelari (psevdo-3D). X,Y = yerdagi nuqta, r = shu chuqurlikdagi yo'l yarim kengligi (px), f = tuman =====
const fc = (c, f, a) => rgb(mix(c, FOG, f), a);

function drawSprite(sp, X, Y, r, f) {
  if (sp.dead || f > .97) return;
  switch (sp.t) {
    case 'lamp': return dLamp(sp, X, Y, r, f);
    case 'crate': return dCrate(X, Y, r, f);
    case 'parked': return carRear(X, Y, r * .4, sp.c, f, false);
    case 'brief': return dBrief(sp, X, Y, r, f);
    case 'doc': return dDoc(sp, X, Y, r, f);
    case 'blade': return dBlade(sp, X, Y, r, f);
    case 'marq': return dMarq(sp, X, Y, r, f);
    case 'booth': return dBooth(X, Y, r, f);
    case 'hydrant': return dHydrant(X, Y, r, f);
    case 'ped': return dPed(sp, X, Y, r, f);
    case 'safe': return dSafe(X, Y, r, f);
  }
}

function dLamp(sp, X, Y, r, f) {
  const g = ctx, pw = Math.max(1, r * .025), ph = r * 1.0, dir = -Math.sign(sp.x);
  g.fillStyle = fc([16, 16, 18], f);
  g.fillRect(X - pw / 2, Y - ph, pw, ph); g.fillRect(X - pw, Y - r * .07, pw * 2, r * .07);
  g.strokeStyle = g.fillStyle; g.lineWidth = Math.max(1, pw * .7);
  g.beginPath(); g.moveTo(X, Y - ph * .96); g.quadraticCurveTo(X + dir * r * .1, Y - ph * 1.06, X + dir * r * .16, Y - ph * .98); g.stroke();
  const lx = X + dir * r * .16, ly = Y - ph * .92;
  g.fillStyle = fc([255, 222, 160], f * .5); g.fillRect(lx - r * .025, ly - r * .04, r * .05, r * .08);
  // tumandagi hajmli yorug'lik konusi
  if (r > 6) {
    g.globalCompositeOperation = 'lighter'; g.fillStyle = rgb(LAMP, .055 * (1 - f));
    g.beginPath(); g.moveTo(lx - r * .03, ly); g.lineTo(lx - r * .3, Y); g.lineTo(lx + r * .3, Y); g.lineTo(lx + r * .03, ly); g.fill();
    g.globalCompositeOperation = 'source-over';
  }
  glow(g, lx, ly, r * .5, r * .5, LAMP, .6 * (1 - f * .7));
}

function dCrate(X, Y, r, f) {
  const g = ctx, w = r * .22, h = r * .2, t = r * .04;
  g.fillStyle = fc([0, 0, 0], f, .4); ell(g, X, Y, w * .6, w * .08); g.fill();
  g.fillStyle = fc([150, 112, 70], f);
  g.beginPath(); g.moveTo(X - w / 2, Y - h); g.lineTo(X + w / 2, Y - h); g.lineTo(X + w * .44, Y - h - t); g.lineTo(X - w * .44, Y - h - t); g.fill();
  g.fillStyle = fc([118, 84, 48], f); g.fillRect(X - w / 2, Y - h, w, h);
  g.strokeStyle = fc([62, 42, 24], f); g.lineWidth = Math.max(1, w * .05);
  g.strokeRect(X - w / 2, Y - h, w, h);
  g.beginPath(); g.moveTo(X - w / 2, Y - h); g.lineTo(X + w / 2, Y); g.moveTo(X + w / 2, Y - h); g.lineTo(X - w / 2, Y); g.stroke();
}

function dBrief(sp, X, Y, r, f) {
  const g = ctx, w = r * .16, h = w * .66, y = Y - r * .1 + Math.sin(time * 3 + sp.ph) * w * .12;
  glow(g, X, y - h / 2, w * 1.3, w * 1.1, [255, 200, 90], .45 * (1 - f));
  g.fillStyle = fc([0, 0, 0], f, .4); ell(g, X, Y, w * .5, w * .07); g.fill();
  g.fillStyle = fc([26, 20, 18], f); rr(g, X - w / 2, y - h, w, h, w * .08); g.fill();
  g.strokeStyle = fc([60, 46, 38], f); g.lineWidth = Math.max(1, w * .06);
  g.beginPath(); g.arc(X, y - h, w * .16, Math.PI, 0); g.stroke();
  g.fillStyle = fc([230, 180, 70], f * .5);
  g.fillRect(X - w * .34, y - h * .92, w * .1, h * .14); g.fillRect(X + w * .24, y - h * .92, w * .1, h * .14);
  g.fillStyle = 'rgba(255,255,255,.18)'; g.fillRect(X - w * .45, y - h * .95, w * .9, h * .06);
}

function dDoc(sp, X, Y, r, f) {
  const g = ctx, w = r * .15, h = w * .74, y = Y - r * .12 + Math.sin(time * 3.4 + sp.ph) * w * .12;
  glow(g, X, y - h / 2, w * 1.4, w * 1.2, [90, 200, 255], .5 * (1 - f));
  g.save(); g.translate(X, y - h / 2); g.rotate(Math.sin(time * 2 + sp.ph) * .12);
  g.fillStyle = fc([196, 168, 104], f); g.fillRect(-w / 2, -h / 2 - h * .12, w * .4, h * .14);
  g.fillStyle = fc([226, 200, 136], f); g.fillRect(-w / 2, -h / 2, w, h);
  g.fillStyle = fc([190, 30, 30], f); g.fillRect(-w / 2, -h * .1, w, h * .2);
  if (w > 36) { g.fillStyle = '#fff'; g.font = `700 ${h * .17}px "Barlow Condensed", sans-serif`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('MAXFIY', 0, 0); }
  g.restore();
}

function dBlade(sp, X, Y, r, f) {
  const g = ctx, bw = r * .13, top = Y - r * 1.9, bot = Y - r * .98, hgt = bot - top;
  const flick = hash(sp.x * 99 + sp.text.length, Math.floor(time * 9)) < .05;
  g.fillStyle = fc([22, 16, 14], f); g.fillRect(X - bw / 2, top, bw, hgt);
  if (flick) return;
  glow(g, X, top + hgt / 2, bw * 2.4, hgt * .75, sp.col, .5 * (1 - f));
  g.strokeStyle = fc(sp.col, f * .6); g.lineWidth = Math.max(1, bw * .06); g.strokeRect(X - bw * .42, top + bw * .1, bw * .84, hgt - bw * .2);
  const txt = sp.text.replace(/ /g, ''), n = txt.length, fs = Math.min(bw * .62, hgt / n * .86);
  if (fs >= 4) {
    g.fillStyle = fc(mix(sp.col, [255, 255, 255], .45), f * .6);
    g.font = `${fs}px Limelight, Georgia, serif`; g.textAlign = 'center'; g.textBaseline = 'middle';
    for (let i = 0; i < n; i++) g.fillText(txt[i], X, top + (i + .5) * hgt / n);
  }
}

function dMarq(sp, X, Y, r, f) {
  const g = ctx, mw = r * .42, mh = r * .27, top = Y - r * 1.24;
  g.strokeStyle = fc([30, 30, 32], f); g.lineWidth = Math.max(1, r * .006);
  g.beginPath(); g.moveTo(X - mw * .4, top); g.lineTo(X - mw * .3, top - r * .3); g.moveTo(X + mw * .4, top); g.lineTo(X + mw * .3, top - r * .3); g.stroke();
  g.fillStyle = fc([34, 22, 16], f); g.fillRect(X - mw / 2, top, mw, mh);
  glow(g, X, top + mh / 2, mw * .95, mh * 1.4, sp.col, .45 * (1 - f));
  const bs = r * .012;
  if (bs > .8) {
    const n = Math.floor(mw / (r * .04)), on = Math.floor(time * 4) % 2;
    g.fillStyle = fc([255, 226, 160], f * .5);
    for (let i = 0; i < n; i++) if ((i + on) % 2) {
      const x = X - mw / 2 + (i + .5) * mw / n;
      g.fillRect(x - bs, top + bs, bs * 2, bs * 2); g.fillRect(x - bs, top + mh - bs * 3, bs * 2, bs * 2);
    }
  }
  const words = sp.text.split(' '), main = words[words.length - 1];
  const fs = Math.min(mh * .42, mw / main.length * 1.5);
  if (fs >= 4) {
    g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillStyle = fc(mix(sp.col, [255, 255, 255], .4), f * .6);
    if (words.length > 1) { g.font = `${fs * .55}px Limelight, Georgia, serif`; g.fillText(words[0], X, top + mh * .3); g.font = `${fs}px Limelight, Georgia, serif`; g.fillText(main, X, top + mh * .64); }
    else { g.font = `${fs}px Limelight, Georgia, serif`; g.fillText(main, X, top + mh * .52); }
  }
}

function dBooth(X, Y, r, f) {
  const g = ctx, w = r * .16, h = r * .52;
  g.fillStyle = fc([110, 28, 26], f); g.fillRect(X - w / 2, Y - h, w, h);
  g.fillStyle = fc([236, 214, 150], f * .7);
  for (let i = 0; i < 3; i++) g.fillRect(X - w * .36, Y - h * (.82 - i * .22), w * .72, h * .17);
  g.fillStyle = fc([30, 20, 18], f); g.fillRect(X - w * .55, Y - h * 1.06, w * 1.1, h * .1);
  glow(g, X, Y - h * .55, w * 1.2, h * .7, [255, 210, 140], .25 * (1 - f));
}

function dHydrant(X, Y, r, f) {
  const g = ctx, w = r * .05, h = r * .1;
  g.fillStyle = fc([150, 34, 26], f); g.fillRect(X - w / 2, Y - h, w, h); ell(g, X, Y - h, w * .55, w * .4); g.fill();
}

function dPed(sp, X, Y, r, f) {
  const g = ctx, ph = r * .38, pw = ph * .32, sw = Math.sin(time * 3 + sp.ph) * pw * .08;
  if (ph < 3) return;
  const c = fc([20, 20, 24], f * .8);
  g.fillStyle = c;
  g.fillRect(X - pw * .2 + sw, Y - ph * .2, pw * .14, ph * .2); g.fillRect(X + pw * .06 - sw, Y - ph * .2, pw * .14, ph * .2);
  g.beginPath(); g.moveTo(X - pw * .34, Y - ph * .8); g.lineTo(X + pw * .34, Y - ph * .8); g.lineTo(X + pw * .48, Y - ph * .18); g.lineTo(X - pw * .48, Y - ph * .18); g.fill();
  g.fillStyle = fc([40, 32, 28], f * .8); ell(g, X, Y - ph * .87, pw * .16, pw * .18); g.fill();
  g.fillStyle = c; ell(g, X, Y - ph * .95, pw * .32, pw * .06); g.fill(); g.fillRect(X - pw * .17, Y - ph * 1.05, pw * .34, ph * .1);
  if (sp.umb) {
    g.fillStyle = fc([14, 14, 18], f * .8); g.beginPath(); g.arc(X, Y - ph * 1.08, pw * .9, Math.PI, 0); g.fill();
    g.strokeStyle = c; g.lineWidth = Math.max(1, pw * .05); g.beginPath(); g.moveTo(X, Y - ph * 1.08); g.lineTo(X, Y - ph * .7); g.stroke();
  }
  g.strokeStyle = rgb(LAMP, .25 * (1 - f)); g.lineWidth = Math.max(1, pw * .05);
  g.beginPath(); g.moveTo(X + pw * .34, Y - ph * .8); g.lineTo(X + pw * .48, Y - ph * .18); g.stroke();
}

function dSafe(X, Y, r, f) {
  const g = ctx, w = r * 3.2, h = r * 2.7;
  g.fillStyle = fc([58, 36, 32], f); g.fillRect(X - w / 2, Y - h, w, h);
  g.fillStyle = fc([255, 200, 120], f * .6);
  for (let i = 0; i < 8; i++) for (let j = 0; j < 3; j++) if (hash(i, j) < .35) g.fillRect(X - w * .45 + i * w * .118, Y - h * (.9 - j * .17), w * .05, h * .08);
  const dw = r * 1.5, dh = r * .85;
  const gr = g.createLinearGradient(0, Y - dh, 0, Y);
  gr.addColorStop(0, rgb(mix([255, 196, 120], FOG, f * .5))); gr.addColorStop(1, rgb(mix([130, 74, 30], FOG, f * .5)));
  g.fillStyle = gr; g.fillRect(X - dw / 2, Y - dh, dw, dh);
  g.fillStyle = fc([84, 84, 88], f); g.fillRect(X - dw / 2, Y - dh, dw, dh * .32);
  g.strokeStyle = fc([50, 50, 54], f); g.lineWidth = Math.max(1, r * .006);
  for (let i = 1; i < 5; i++) { g.beginPath(); g.moveTo(X - dw / 2, Y - dh + i * dh * .064); g.lineTo(X + dw / 2, Y - dh + i * dh * .064); g.stroke(); }
  glow(g, X, Y - dh * .4, dw, dh, [255, 190, 110], .5 * (1 - f));
  const fs = r * .22;
  glow(g, X, Y - dh - r * .25, r * 1.4, r * .35, [120, 255, 150], .7 * (1 - f));
  if (fs > 4) { g.fillStyle = fc([190, 255, 200], f * .5); g.font = `${fs}px Limelight, Georgia, serif`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('SAFEHOUSE', X, Y - dh - r * .25); }
}

// Tramvay: yon tomoni kameraga qaragan, yo'lni ko'ndalang kesib o'tadi
function dTram(tr, X0, Y, r, f) {
  const g = ctx, xa = X0 + (tr.x - 1) * r, xb = X0 + (tr.x + 1) * r, w = xb - xa;
  g.fillStyle = fc([0, 0, 0], f, .5); g.fillRect(xa + r * .03, Y - r * .05, w, r * .06);
  g.fillStyle = fc([20, 20, 22], f); g.fillRect(xa + r * .1, Y - r * .1, w - r * .2, r * .1);
  g.fillStyle = fc([44, 74, 60], f); g.fillRect(xa, Y - r * .4, w, r * .32);
  g.fillStyle = fc([206, 192, 148], f); g.fillRect(xa, Y - r * .72, w, r * .33);
  g.fillStyle = fc([60, 60, 64], f); g.fillRect(xa + r * .05, Y - r * .78, w - r * .1, r * .07);
  g.fillStyle = fc([255, 206, 130], f * .6);
  for (let i = 0; i < 9; i++) g.fillRect(xa + r * .1 + i * (w - r * .2) / 9, Y - r * .66, (w - r * .2) / 9 * .7, r * .18);
  const cx = (xa + xb) / 2, dir = Math.sign(tr.vx) || 1;
  g.strokeStyle = fc([30, 30, 32], f); g.lineWidth = Math.max(1, r * .012);
  g.beginPath(); g.moveTo(cx, Y - r * .78); g.lineTo(cx - dir * r * .35, Y - r * 1.12); g.stroke();
  if (r > 20) { g.fillStyle = fc([255, 230, 170], f * .5); g.font = `${r * .07}px Limelight, Georgia, serif`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('7 · MARKAZ', cx, Y - r * .27); }
  glow(g, dir > 0 ? xb : xa, Y - r * .3, r * .5, r * .3, [255, 240, 200], .8 * (1 - f));
}
