'use strict';
// ===== 7. Yuqoridan (izometrikka yaqin) ko'rinish: binolar balandligi qiya siljish bilan beriladi =====
function renderTop() {
  const k = VIEW.tk, PYs = H * .68, g = ctx;
  g.fillStyle = rgb([14, 15, 19]); g.fillRect(0, 0, W, H);
  const i0 = Math.max(0, Math.floor((P.pos - (H - PYs) / k) / SEG) - 2);
  const i1 = Math.min(N - 1, Math.floor((P.pos + PYs / k) / SEG) + 18);
  const pi = clamp(Math.floor(P.pos / SEG), i0, i1);
  // burilish siljishlari: o'yinchi segmentida 0
  const off = new Float32Array(i1 - i0 + 2);
  let d = 0;
  for (let i = pi; i <= i1; i++) { off[i - i0 + 1] = off[i - i0] + d; d += segs[i].curve; }
  d = 0;
  for (let i = pi - 1; i >= i0; i--) { d -= segs[i].curve; off[i - i0] = off[i - i0 + 1] - d; }
  const offAt = z => { const i = clamp(Math.floor(z / SEG), i0, i1), fr = clamp(z / SEG - i, 0, 1); return lerp(off[i - i0], off[i - i0 + 1], fr); };
  const TX = P.x * ROAD * .5 + offAt(P.pos);
  const SX = (nx, o) => W / 2 + (nx * ROAD + o - TX) * k, SY = z => PYs - (z - P.pos) * k;

  for (let i = i1; i >= i0; i--) {
    const s = segs[i], oa = off[i - i0], ob = off[i - i0 + 1], ya = SY(i * SEG), yb = SY((i + 1) * SEG);
    if (yb > H + 40 || ya < -H * .6) continue;
    const q = (n1, n2, col) => quad(SX(n1, oa), ya, SX(n2, oa), ya, SX(n2, ob), yb, SX(n1, ob), yb, col);
    if (s.cross >= 0) q(-7, 7, rgb(mix(COBBLE[i & 1], LAMP, s.light * .3)));
    else for (const sd of [-1, 1]) { q(sd, sd * 1.5, rgb(mix(SIDEWALK, LAMP, s.lt[sd > 0 ? 1 : 0] * .45))); q(sd, sd * 1.05, rgb(CURB)); }
    q(-1, 1, rgb(mix(COBBLE[i & 1], LAMP, s.light * .42)));
    if (k * SEG > 5) {
      g.strokeStyle = 'rgba(14,14,18,.55)'; g.lineWidth = 1; g.beginPath();
      const o = (i & 1) ? .1 : 0;
      for (let j = 1; j < 10; j++) { const nx = -1 + j * .2 + o; g.moveTo(SX(nx, oa), ya); g.lineTo(SX(nx, ob), yb); }
      g.moveTo(SX(-1, oa), ya); g.lineTo(SX(1, oa), ya); g.stroke();
    }
    g.strokeStyle = rgb(mix([120, 124, 132], LAMP, s.light * .5)); g.lineWidth = Math.max(1, ROAD * k * .02); g.beginPath();
    for (const nx of [-.15, .15]) { g.moveTo(SX(nx, oa), ya); g.lineTo(SX(nx, ob), yb); }
    g.stroke();
    if (s.cross >= 0 && (i === s.cross + 1 || i === s.cross + 3)) {
      g.strokeStyle = 'rgb(130,132,140)'; g.beginPath(); const ym = (ya + yb) / 2, om = (oa + ob) / 2; g.moveTo(SX(-7, om), ym); g.lineTo(SX(7, om), ym); g.stroke();
    }
    if (s.pud) { g.fillStyle = 'rgba(22,26,34,.9)'; ell(g, SX(s.pud.x, (oa + ob) / 2), (ya + yb) / 2, s.pud.w * ROAD * k / 2, SEG * k * .9); g.fill(); }
    for (const sp of s.spr) if (!sp.dead) topSprite(sp, SX(sp.x, oa), ya, k);
    // binolar: ichki devor va tom (tashqariga og'ish)
    for (let sd = 0; sd < 2; sd++) {
      const wl = s.wall[sd]; if (!wl) continue;
      const dd = sd ? 1 : -1, hh = wl.h * ROAD * k * .3, lean = wl.h * .07;
      const R = (x, y) => [x + (x - W / 2) * lean, y - hh];
      const ia = [SX(dd * 1.5, oa), ya], ib = [SX(dd * 1.5, ob), yb], oa2 = [SX(dd * 4.5, oa), ya], ob2 = [SX(dd * 4.5, ob), yb];
      const ra = R(...ia), rb = R(...ib), roa = R(...oa2), rob = R(...ob2);
      quad(ia[0], ia[1], ib[0], ib[1], rb[0], rb[1], ra[0], ra[1], rgb(shade(wl.col, -.1)));
      if (s.shop[sd]) { g.fillStyle = rgb([255, 206, 140], .8); const m = [(ia[0] + ib[0]) / 2, (ia[1] + ib[1]) / 2]; g.fillRect(m[0] - u * .4, m[1] - hh * .12, u * .8, hh * .1); }
      else if (hash(i, wl.seed) < .3) { g.fillStyle = rgb(WARM, .7); const m = [lerp(ia[0], ra[0], .5), lerp(ia[1], ra[1], .5)]; g.fillRect(m[0] - u * .3, m[1], u * .6, u * .5); }
      const prev = segs[i - 1];
      if (!prev || prev.wall[sd] !== wl) quad(ia[0], ia[1], oa2[0], oa2[1], roa[0], roa[1], ra[0], ra[1], rgb(shade(wl.col, -.35)));
      quad(ra[0], ra[1], roa[0], roa[1], rob[0], rob[1], rb[0], rb[1], rgb(mix([36, 38, 44], wl.col, .15)));
      if (hash(i, wl.seed + 3) < .12) { g.fillStyle = '#1c1d22'; const c = [lerp(ra[0], roa[0], .6), lerp(ra[1], rb[1], .5)]; g.fillRect(c[0], c[1] - u, u * 1.4, u * 1.6); }
    }
    for (const tr of trams) if (tr.c === i && tr.st === 1) {
      const z0 = i * SEG + 100, z1 = z0 + 800, o = (oa + ob) / 2;
      g.fillStyle = 'rgba(0,0,0,.4)'; g.fillRect(SX(tr.x - 1, o) + u, SY(z1) + u, (2 * ROAD) * k, 800 * k);
      g.fillStyle = 'rgb(44,74,60)'; g.fillRect(SX(tr.x - 1, o), SY(z1), 2 * ROAD * k, 800 * k);
      g.fillStyle = 'rgb(206,192,148)'; g.fillRect(SX(tr.x - 1, o) + u * .5, SY(z1) + u * .5, 2 * ROAD * k - u, 800 * k - u);
      glow(g, SX(tr.x + Math.sign(tr.vx), o), SY(z0 + 400), u * 6, u * 4, [255, 240, 200], .8);
    }
  }
  // mashinalar
  const cl = .96 * ROAD * k, cw = .38 * ROAD * k;
  for (const t of traffic) { const y = SY(t.z); if (y > -cl && y < H + cl) drawTopCar(SX(t.x, offAt(t.z)), y, cl, cw, t.c, 'old', 0, true); }
  const px = SX(P.x, offAt(P.pos));
  VIEW.cx = px; VIEW.cy = PYs + cl * .5; VIEW.cw = cw * 2;
  drawTopCar(px, PYs, cl, cw, CAR.body, CAR.id, P.yaw * .8, true);
  if (mode === 'play') {
    const cz = P.pos - P.gap, cy = SY(cz);
    if (cy < H + cl) drawTopCar(SX(P.copX, offAt(Math.max(cz, i0 * SEG))), cy, cl, cw, [16, 16, 18], 'police', 0, true);
    else { const on = Math.floor(time * 7) % 2; glow(g, px, H - u * 2, u * 14, u * 6, on ? [255, 50, 60] : [70, 140, 255], .8); }
  }
}

function topSprite(sp, X, Y, k) {
  const g = ctx, s = ROAD * k;
  switch (sp.t) {
    case 'lamp': g.fillStyle = '#121214'; ell(g, X, Y, s * .04, s * .04); g.fill(); glow(g, X - Math.sign(sp.x) * s * .16, Y, s * .6, s * .6, LAMP, .55); break;
    case 'crate': g.fillStyle = 'rgb(128,90,52)'; g.fillRect(X - s * .11, Y - s * .11, s * .22, s * .22); g.strokeStyle = 'rgb(70,48,28)'; g.lineWidth = Math.max(1, s * .02);
      g.beginPath(); g.moveTo(X - s * .11, Y - s * .11); g.lineTo(X + s * .11, Y + s * .11); g.moveTo(X + s * .11, Y - s * .11); g.lineTo(X - s * .11, Y + s * .11); g.stroke(); break;
    case 'parked': drawTopCar(X, Y, s * .96, s * .38, sp.c, 'old', 0, false); break;
    case 'brief': glow(g, X, Y, s * .3, s * .3, [255, 200, 90], .5); g.fillStyle = '#1a1412'; g.fillRect(X - s * .08, Y - s * .05, s * .16, s * .1); g.fillStyle = '#d8a848'; g.fillRect(X - s * .03, Y - s * .07, s * .06, s * .02); break;
    case 'doc': glow(g, X, Y, s * .3, s * .3, [90, 200, 255], .6); g.fillStyle = 'rgb(226,200,136)'; g.fillRect(X - s * .07, Y - s * .055, s * .14, s * .11); g.fillStyle = 'rgb(190,30,30)'; g.fillRect(X - s * .07, Y - s * .01, s * .14, s * .02); break;
    case 'blade': case 'marq': glow(g, X, Y, s * .35, s * .2, sp.col, .7); g.fillStyle = rgb(sp.col); g.fillRect(X - s * .06, Y - s * .015, s * .12, s * .03); break;
    case 'booth': g.fillStyle = 'rgb(110,28,26)'; g.fillRect(X - s * .08, Y - s * .08, s * .16, s * .16); break;
    case 'hydrant': g.fillStyle = 'rgb(150,34,26)'; ell(g, X, Y, s * .03, s * .03); g.fill(); break;
    case 'ped': g.fillStyle = '#16161a'; ell(g, X, Y, s * (sp.umb ? .12 : .05), s * (sp.umb ? .12 : .05)); g.fill(); break;
    case 'safe': g.fillStyle = 'rgb(58,36,32)'; g.fillRect(X - s * 1.6, Y - s * 1.2, s * 3.2, s * 1.2); glow(g, X, Y, s * .9, s * .5, [255, 190, 110], .7);
      g.fillStyle = 'rgb(190,255,200)'; g.font = `${s * .22}px Limelight, Georgia, serif`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('SAFEHOUSE', X, Y - s * .6); break;
  }
}
