'use strict';
// ===== 6. Psevdo-3D ko'cha renderi (orqa kamera va salon ichidan) =====
// Segmentlar uzoqdan yaqinga qarab chiziladi (painter's algorithm): devorlar -> trotuar -> yo'l -> akslar -> spritelar.
const PX = new Float32Array(260), PY = new Float32Array(260), PR = new Float32Array(260), O1 = new Float32Array(260), O2 = new Float32Array(260);
const BK = Array.from({ length: 260 }, () => []);
let SKY = null;

function proj(z, off) {
  const d = Math.max(z - V.camZ, 60), s = DEPTH / d;
  return [W / 2 + s * (off - V.camX) * U, V.hor + s * V.camH * U, s * ROAD * U];
}
const fogF = k => Math.min(.94, Math.pow(k / DRAW, 1.1) * 1.15);

function buildSky() {
  SKY = document.createElement('canvas'); SKY.width = 1600; SKY.height = 300;
  const g = SKY.getContext('2d'), R = rng(77);
  for (const [col, hmin, hmax, lit] of [[[44, 48, 58], 120, 260, .02], [[28, 30, 36], 60, 180, .06]]) {
    let x = 0;
    while (x < 1600) {
      const w = 30 + R() * 90, h = hmin + R() * (hmax - hmin);
      g.fillStyle = rgb(col); g.fillRect(x, 300 - h, w, h);
      if (R() < .2) g.fillRect(x + w * .4, 300 - h - 40, w * .2, 40);           // minora
      if (R() < .15) { g.fillRect(x + w * .2, 300 - h - 18, 16, 18); }        // suv baki
      g.fillStyle = 'rgba(255,196,120,.8)';
      for (let yy = 300 - h + 8; yy < 290; yy += 10) for (let xx = x + 4; xx < x + w - 4; xx += 8) if (R() < lit) g.fillRect(xx, yy, 3, 4);
      x += w + R() * 6;
    }
  }
}

function drawSky() {
  const h = V.hor, fl = L.flash * (Math.random() < .7 ? 1 : .3);
  const gr = ctx.createLinearGradient(0, 0, 0, h);
  gr.addColorStop(0, rgb(mix([7, 9, 14], [120, 130, 160], fl * .5))); gr.addColorStop(1, rgb(mix(FOG, [200, 210, 230], fl * .5)));
  ctx.fillStyle = gr; ctx.fillRect(0, 0, W, h + 1);
  glow(ctx, W * .72, h * .25, u * 22, u * 22, [180, 190, 210], .25);
  // shahar ustidagi projektor nurlari
  ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 2; i++) {
    const a = -Math.PI / 2 + Math.sin(time * .25 + i * 2.1) * .5, bx = W * (.3 + i * .45), by = h;
    ctx.fillStyle = 'rgba(200,210,230,.045)'; ctx.beginPath(); ctx.moveTo(bx, by);
    ctx.lineTo(bx + Math.cos(a - .05) * H, by + Math.sin(a - .05) * H); ctx.lineTo(bx + Math.cos(a + .05) * H, by + Math.sin(a + .05) * H); ctx.fill();
  }
  ctx.globalCompositeOperation = 'source-over';
  const sh = H * .2, sw = SKY.width * sh / SKY.height;
  for (let x = -(((skyX % sw) + sw) % sw); x < W; x += sw) ctx.drawImage(SKY, x, h - sh, sw, sh);
  const fg = ctx.createLinearGradient(0, h - H * .14, 0, h + 2);
  fg.addColorStop(0, rgb(FOG, 0)); fg.addColorStop(1, rgb(FOG, .9));
  ctx.fillStyle = fg; ctx.fillRect(0, h - H * .14, W, H * .14 + 2);
}

function renderStreet(cockpit) {
  V.hor = cockpit ? H * .40 : VIEW.hor; V.camH = cockpit ? ROAD * .36 : VIEW.camH;
  V.camZ = cockpit ? P.pos - 120 : P.pos - VIEW.pz; V.camX = cockpit ? P.x * ROAD : camXs;
  drawSky();
  ctx.fillStyle = rgb(GROUND); ctx.fillRect(0, V.hor, W, H - V.hor);
  const bi = clamp(Math.floor(V.camZ / SEG), 0, N - 1), base = segs[bi], bp = (V.camZ - bi * SEG) / SEG;
  let x = 0, dx = -base.curve * bp;
  const n = Math.min(DRAW, N - bi);
  for (let k = 0; k < n; k++) {
    const s = segs[bi + k]; O1[k] = x; O2[k] = x + dx; x += dx; dx += s.curve;
    const a = proj(s.i * SEG, O1[k]); PX[k] = a[0]; PY[k] = a[1]; PR[k] = a[2]; BK[k].length = 0;
  }
  for (const t of traffic) { const k = Math.floor(t.z / SEG) - bi; if (k >= 0 && k < n) BK[k].push(t); }
  const kp = cockpit ? -1 : Math.floor(P.pos / SEG) - bi;
  for (let k = n - 1; k >= 0; k--) drawSeg(segs[bi + k], k, n, bi, k === kp);
}

// Segment ichidagi ixtiyoriy z nuqtani proyeksiya qilish (mashinalar uchun)
function projIn(z, k, nx) {
  const fr = clamp(z / SEG - Math.floor(z / SEG), 0, 1), off = lerp(O1[k], O2[k], fr);
  const d = Math.max(z - V.camZ, 60), s = DEPTH / d;
  return [W / 2 + s * (nx * ROAD + off - V.camX) * U, V.hor + s * V.camH * U, s * ROAD * U];
}

function drawSeg(s, k, n, bi, hasPlayer) {
  const z1 = s.i * SEG;
  if (z1 + SEG - V.camZ < 60) return;
  const f = fogF(k), B = proj(z1 + SEG, O2[k]);
  const x1 = PX[k], y1 = PY[k], r1 = PR[k], x2 = B[0], y2 = B[1], r2 = B[2];
  const cross = s.cross >= 0;

  for (let sd = 0; sd < 2; sd++) {
    const d = sd ? 1 : -1, wl = s.wall[sd];
    if (wl) drawWall(s, wl, d, sd, x1, y1, r1, x2, y2, r2, f);
    else if (!cross) quad(x1 + d * 2.6 * r1, y1, x2 + d * 2.6 * r2, y2, x2 + d * 2.6 * r2, y2 - 2 * r2, x1 + d * 2.6 * r1, y1 - 2 * r1, fc([20, 20, 24], f));
  }
  if (cross) quad(x1 - 7 * r1, y1, x1 + 7 * r1, y1, x2 + 7 * r2, y2, x2 - 7 * r2, y2, rgb(mix(mix(COBBLE[s.i & 1], LAMP, s.light * .3), FOG, f)));
  else for (let sd = 0; sd < 2; sd++) {
    const d = sd ? 1 : -1;
    quad(x1 + d * r1, y1, x1 + d * 1.5 * r1, y1, x2 + d * 1.5 * r2, y2, x2 + d * r2, y2, rgb(mix(mix(SIDEWALK, LAMP, s.lt[sd] * .45), FOG, f)));
    quad(x1 + d * r1, y1, x1 + d * 1.05 * r1, y1, x2 + d * 1.05 * r2, y2, x2 + d * r2, y2, fc(CURB, f));
  }
  // nam tosh yo'l: qatorlar navbatma-navbat, fonus nuri bilan iliq
  quad(x1 - r1, y1, x1 + r1, y1, x2 + r2, y2, x2 - r2, y2, rgb(mix(mix(COBBLE[s.i & 1], LAMP, s.light * .42), FOG, f)));
  if (r1 > 40 && y1 - y2 > 1.5) {
    ctx.strokeStyle = fc([16, 16, 20], f, .6); ctx.lineWidth = Math.max(1, r1 * .006); ctx.beginPath();
    const o = (s.i & 1) ? .1 : 0;
    for (let j = 1; j < 10; j++) { const nx = -1 + j * .2 + o; ctx.moveTo(x1 + nx * r1, y1); ctx.lineTo(x2 + nx * r2, y2); }
    ctx.moveTo(x1 - r1, y1); ctx.lineTo(x1 + r1, y1); ctx.stroke();
    ctx.strokeStyle = rgb([150, 160, 180], .12); ctx.beginPath(); ctx.moveTo(x2 - r2, y2 + 1); ctx.lineTo(x2 + r2, y2 + 1); ctx.stroke();
  }
  // bo'ylama tramvay relslari
  if (r1 > 6) {
    ctx.strokeStyle = rgb(mix(mix([120, 124, 132], LAMP, s.light * .5), FOG, f)); ctx.lineWidth = Math.max(1, r1 * .012); ctx.beginPath();
    for (const nx of [-.15, .15]) { ctx.moveTo(x1 + nx * r1, y1); ctx.lineTo(x2 + nx * r2, y2); }
    ctx.stroke();
  }
  // chorraha: ko'ndalang relslar va tepadagi sim
  if (cross) {
    const c = s.cross;
    if (s.i === c + 1 || s.i === c + 3) {
      const ym = (y1 + y2) / 2, xm = (x1 + x2) / 2, rm = (r1 + r2) / 2;
      ctx.strokeStyle = fc([130, 132, 140], f); ctx.lineWidth = Math.max(1, (y1 - y2) * .15);
      ctx.beginPath(); ctx.moveTo(xm - 7 * rm, ym); ctx.lineTo(xm + 7 * rm, ym); ctx.stroke();
    }
    if (s.i === c + 2) { ctx.strokeStyle = fc([12, 12, 14], f); ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(x1 - 7 * r1, y1 - 1.12 * r1); ctx.lineTo(x1 + 7 * r1, y1 - 1.12 * r1); ctx.stroke(); }
  }
  // ko'lmak: qorong'i oyna, osmon va fonus aksi, yomg'ir halqalari
  if (s.pud && r1 > 3) {
    const p = s.pud, cx = (x1 + p.x * r1 + x2 + p.x * r2) / 2, cy = (y1 + y2) / 2, rw = p.w * (r1 + r2) / 4, rh = Math.max(1, (y1 - y2) * .9);
    ctx.fillStyle = fc([22, 26, 34], f); ell(ctx, cx, cy, rw, rh); ctx.fill();
    ctx.fillStyle = rgb(mix([96, 106, 128], FOG, f), .35); ell(ctx, cx, cy - rh * .3, rw * .7, rh * .4); ctx.fill();
    if (k < 30) { ctx.strokeStyle = 'rgba(200,210,230,.25)'; ctx.lineWidth = 1;
      for (let i = 0; i < 2; i++) { const ph = (time * 1.3 + i * .5 + s.i * .37) % 1; ell(ctx, cx + (hash(s.i, i) - .5) * rw, cy, rw * .25 * ph, rh * .25 * ph); ctx.stroke(); } }
  }
  // nam yo'ldagi vertikal akslar (yaqin 8 segmentdagi fonus va neonlardan)
  if (y1 - y2 >= .5) {
    ctx.globalCompositeOperation = 'lighter';
    for (let m = k; m < Math.min(n, k + 8); m++) for (const sp of segs[bi + m].spr) {
      if (sp.dead || !(sp.t === 'lamp' || sp.t === 'blade' || sp.t === 'marq')) continue;
      const col = sp.t === 'lamp' ? LAMP : sp.col, lx = PX[m] + sp.x * (sp.t === 'lamp' ? .84 : .8) * PR[m], ww = PR[m] * .06;
      ctx.fillStyle = rgb(col, .28 * (1 - (m - k) / 8) * (1 - f)); ctx.fillRect(lx - ww / 2, y2, ww, y1 - y2 + 1);
    }
    ctx.globalCompositeOperation = 'source-over';
  }
  // spritelar: chetdagilar avval
  const list = s.spr.length > 1 ? s.spr.slice().sort((a, b) => Math.abs(b.x) - Math.abs(a.x)) : s.spr;
  for (const sp of list) drawSprite(sp, x1 + sp.x * r1, y1, r1, f);
  for (const t of BK[k]) { const p = projIn(t.z, k, t.x); carRear(p[0], p[1], p[2] * .4, t.c, f, true); }
  if (cross && s.i === s.cross) for (const tr of trams) if (tr.c === s.i && tr.st === 1) { const p = projIn(z1 + 100, k, 0); dTram(tr, p[0], p[1], p[2], f); }
  if (hasPlayer) {
    const p = projIn(P.pos, k, P.x), w = p[2] * .4;
    VIEW.cx = p[0]; VIEW.cy = p[1]; VIEW.cw = w;
    // faralar nuri yo'lga tushadi
    const vx = lerp(p[0], W / 2, .6), vy = lerp(p[1], V.hor, .62);
    const gr = ctx.createLinearGradient(0, p[1] - w * .3, 0, vy);
    gr.addColorStop(0, 'rgba(255,236,190,.16)'); gr.addColorStop(1, 'rgba(255,236,190,0)');
    ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = gr; ctx.beginPath();
    ctx.moveTo(p[0] - w * .35, p[1] - w * .3); ctx.lineTo(vx - w * .7, vy); ctx.lineTo(vx + w * .7, vy); ctx.lineTo(p[0] + w * .35, p[1] - w * .3); ctx.fill();
    ctx.globalCompositeOperation = 'source-over';
    drawPlayer(ctx, p[0], p[1], w, CAR, { yaw: P.yaw, brake: K.brake || K.hb, boost: P.boost });
  }
}

function drawWall(s, wl, d, sd, x1, y1, r1, x2, y2, r2, f) {
  const h = wl.h, ax = x1 + d * 1.5 * r1, bx = x2 + d * 1.5 * r2;
  quad(ax, y1, bx, y2, bx, y2 - h * r2, ax, y1 - h * r1, rgb(mix(mix(wl.col, LAMP, s.lt[sd] * .22), FOG, f)));
  if (Math.abs(ax - bx) < 2 || h * r1 < 14 || f > .85) return;
  const WP = (t, hy) => [lerp(ax, bx, t), lerp(y1, y2, t) - lerp(r1, r2, t) * hy];
  const wq = (t0, t1, h0, h1, c) => { const a = WP(t0, h0), b = WP(t1, h0), c2 = WP(t1, h1), e = WP(t0, h1); quad(a[0], a[1], b[0], b[1], c2[0], c2[1], e[0], e[1], c); };
  wq(0, 1, h - .1, h, rgb(mix(shade(wl.col, -.45), FOG, f)));
  let fl = 0;
  for (let hy = .95; hy + .5 < h - .1; hy += .62, fl++) {
    const r = hash(s.i * 3 + fl, wl.seed + d);
    wq(.28, .72, hy + .12, hy + .44, rgb(r < .28 ? mix(WARM, FOG, f * .7) : r < .36 ? mix([150, 100, 60], FOG, f) : mix([18, 20, 26], FOG, f)));
  }
  if (s.shop[sd]) {
    wq(.06, .94, .1, .62, rgb(mix([255, 214, 150], FOG, f * .6)));
    wq(0, 1, .64, .8, rgb(mix(s.i & 1 ? wl.awn : [214, 204, 180], FOG, f)));
  } else {
    const r = hash(s.i, wl.seed);
    wq(.3, .7, .1, r < .15 ? .6 : .5, rgb(mix(r < .15 ? [120, 84, 50] : [16, 18, 22], FOG, f)));
  }
}

// Yomg'ir chiziqlari va yo'ldagi sachrashlar
function drawRain() {
  const pct = P.speed / CAR.max;
  if (cam === 1) {
    ctx.strokeStyle = 'rgba(190,200,220,.3)'; ctx.lineWidth = Math.max(1, u * .1); ctx.beginPath();
    for (let i = 0; i < 70; i++) { const ph = (time * 1.6 + hash(i, 1)) % 1, x = hash(i, 2 + Math.floor(time * 1.6 + hash(i, 1))) * W, y = hash(i, 3 + Math.floor(time * 1.6 + hash(i, 1))) * H;
      ctx.moveTo(x + u * 1.6 * ph, y); ctx.ellipse(x, y, Math.max(0, u * 1.6 * ph), Math.max(0, u * .8 * ph), 0, 0, Math.PI * 2); }
    ctx.stroke(); return;
  }
  ctx.strokeStyle = 'rgba(175,188,210,.3)'; ctx.lineWidth = Math.max(1, u * .12); ctx.beginPath();
  const sl = .12 - P.steer * .3 * pct, ln = u * (1.6 + pct * 2.2);
  for (const d of rain) { const x = d.x * W, y = d.y * H; ctx.moveTo(x, y); ctx.lineTo(x + sl * d.l * ln, y + d.l * ln); }
  ctx.stroke();
  if (cam === 0) {
    ctx.strokeStyle = 'rgba(200,210,230,.22)'; ctx.beginPath();
    for (let i = 0; i < 26; i++) { const ph = (time * 2.2 + hash(i, 5)) % 1, cyc = Math.floor(time * 2.2 + hash(i, 5));
      const y = lerp(V.hor, H, .25 + hash(i, cyc) * .75), x = hash(cyc, i) * W, s = (y - V.hor) / (H - V.hor) * u * 1.4 * ph;
      ctx.moveTo(x + s, y); ctx.ellipse(x, y, Math.max(0, s), Math.max(0, s * .3), 0, 0, Math.PI * 2); }
    ctx.stroke();
  }
}

// Salon ichidan ko'rinish: oynadagi tomchilar, dvornik, ustunlar, oyna, yog'och panel, rul va spidometrlar
function drawCockpit() {
  const g = ctx, pct = P.speed / CAR.max;
  for (const d of drops) {
    g.fillStyle = 'rgba(190,205,230,.16)'; ell(g, d.x, d.y, d.r, d.r * 1.1); g.fill();
    g.fillStyle = 'rgba(255,255,255,.4)'; ell(g, d.x - d.r * .3, d.y - d.r * .35, d.r * .25, d.r * .22); g.fill();
  }
  const px = W * .36, py = H * .76, len = Math.min(H * .66, W * .5);
  g.strokeStyle = '#0b0b0d'; g.lineWidth = Math.max(2, u * .8); g.lineCap = 'round';
  g.beginPath(); g.moveTo(px, py); g.lineTo(px + Math.cos(WIPER.a) * len, py + Math.sin(WIPER.a) * len); g.stroke(); g.lineCap = 'butt';
  g.fillStyle = '#0d0d10';
  g.beginPath(); g.moveTo(0, 0); g.lineTo(W * .09, 0); g.lineTo(W * .015, H * .78); g.lineTo(0, H * .78); g.fill();
  g.beginPath(); g.moveTo(W, 0); g.lineTo(W * .91, 0); g.lineTo(W * .985, H * .78); g.lineTo(W, H * .78); g.fill();
  g.fillRect(0, 0, W, H * .035);
  // orqani ko'rish oynasi: politsiya chiroqlari
  const mw = Math.min(W * .24, u * 40), mh = mw * .28, mx = W / 2 - mw / 2, my = H * .045;
  g.fillStyle = '#1a1c22'; rr(g, mx - u * .4, my - u * .4, mw + u * .8, mh + u * .8, u); g.fill();
  g.fillStyle = vgrad(g, my, my + mh, [[30, 34, 42], [14, 15, 19]]); rr(g, mx, my, mw, mh, u * .8); g.fill();
  const heat = clamp(1 - P.gap / 6000, 0, 1);
  if (heat > 0 && mode === 'play') {
    g.save(); rr(g, mx, my, mw, mh, u * .8); g.clip();
    const on = Math.floor(time * 7) % 2, cs = mw * (.05 + heat * .12);
    glow(g, W / 2 - cs, my + mh * .55, cs * 2.2, cs * 1.4, on ? [255, 50, 60] : [70, 140, 255], .9 * heat);
    glow(g, W / 2 + cs, my + mh * .55, cs * 2.2, cs * 1.4, on ? [70, 140, 255] : [255, 50, 60], .9 * heat);
    g.fillStyle = 'rgba(255,245,220,.9)'; ell(g, W / 2 - cs * .7, my + mh * .7, cs * .2, cs * .15); g.fill(); ell(g, W / 2 + cs * .7, my + mh * .7, cs * .2, cs * .15); g.fill();
    g.restore();
  }
  // yog'och panel
  const dy = H * .76;
  g.fillStyle = vgrad(g, dy - H * .04, H, [[92, 54, 30], [58, 32, 18], [26, 14, 8]]);
  g.beginPath(); g.moveTo(0, dy + H * .03); g.quadraticCurveTo(W / 2, dy - H * .06, W, dy + H * .03); g.lineTo(W, H); g.lineTo(0, H); g.fill();
  g.strokeStyle = 'rgba(0,0,0,.18)'; g.lineWidth = 1;
  for (let i = 1; i < 6; i++) { g.beginPath(); g.moveTo(0, dy + H * .03 + i * H * .04); g.quadraticCurveTo(W / 2, dy - H * .04 + i * H * .045, W, dy + H * .03 + i * H * .04); g.stroke(); }
  g.strokeStyle = '#c9c4b4'; g.lineWidth = Math.max(1, u * .3);
  g.beginPath(); g.moveTo(0, dy + H * .03); g.quadraticCurveTo(W / 2, dy - H * .06, W, dy + H * .03); g.stroke();
  const gr = Math.min(H * .085, W * .075);
  drawGauges(W * .58, dy + gr * 1.25, gr, true);
  // rul
  const wx = W * .34, wy = H * 1.02, R = Math.min(W * .24, H * .3), rot = P.steer * 1.2 + P.yaw * .8;
  g.save(); g.translate(wx, wy); g.rotate(rot);
  g.strokeStyle = '#c8c2b0'; g.lineWidth = R * .05;
  for (const a of [0, Math.PI, Math.PI / 2]) { g.beginPath(); g.moveTo(0, 0); g.lineTo(Math.cos(a) * R, Math.sin(a) * R); g.stroke(); }
  g.strokeStyle = '#5a3018'; g.lineWidth = R * .13; g.beginPath(); g.arc(0, 0, R, 0, Math.PI * 2); g.stroke();
  g.strokeStyle = 'rgba(255,200,140,.25)'; g.lineWidth = R * .03; g.beginPath(); g.arc(0, 0, R * 1.02, Math.PI * 1.1, Math.PI * 1.6); g.stroke();
  g.fillStyle = '#1a1410'; ell(g, 0, 0, R * .18, R * .18); g.fill();
  g.fillStyle = '#c9a24a'; ell(g, 0, 0, R * .07, R * .07); g.fill();
  g.restore();
}
