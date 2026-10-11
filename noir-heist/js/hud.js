'use strict';
// ===== 8. HUD: ta'qib paneli, mini-xarita, mexanik spidometrlar, ogohlantirishlar va kino effektlari =====
let VIG = null, GRAIN = null;
function buildPost() {
  VIG = document.createElement('canvas'); VIG.width = 256; VIG.height = 256;
  const g = VIG.getContext('2d'), gr = g.createRadialGradient(128, 128, 60, 128, 128, 182);
  gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(1, 'rgba(0,0,0,.72)'); g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
  const nc = document.createElement('canvas'); nc.width = nc.height = 128;
  const ng = nc.getContext('2d'), id = ng.createImageData(128, 128);
  for (let i = 0; i < id.data.length; i += 4) { const v = Math.random() * 255; id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
  ng.putImageData(id, 0, 0); GRAIN = ctx.createPattern(nc, 'repeat');
}

function hudFont(sz, w = 800) { return `${w} ${sz}px Orbitron, "Arial Black", sans-serif`; }

function panel(x, y, w, h) {
  const c = u * 1.2, g = ctx;
  g.beginPath(); g.moveTo(x, y); g.lineTo(x + w - c, y); g.lineTo(x + w, y + c); g.lineTo(x + w, y + h); g.lineTo(x + c, y + h); g.lineTo(x, y + h - c); g.closePath();
  g.fillStyle = 'rgba(8,12,18,.74)'; g.fill(); g.strokeStyle = 'rgba(69,200,240,.55)'; g.lineWidth = Math.max(1, u * .15); g.stroke();
}

// Mexanik spidometr va taxometr (1940-yillar uslubida)
function gauge(cx, cy, R, val, max, step, label, red, odo) {
  const g = ctx, a0 = Math.PI * .75, a1 = Math.PI * 2.25;
  g.fillStyle = vgrad(g, cy - R * 1.1, cy + R * 1.1, [[214, 180, 110], [110, 84, 40], [60, 44, 20]]); ell(g, cx, cy, R * 1.1, R * 1.1); g.fill();
  const face = g.createRadialGradient(cx, cy - R * .3, R * .1, cx, cy, R);
  face.addColorStop(0, '#ece3c8'); face.addColorStop(1, '#bfb08a'); g.fillStyle = face; ell(g, cx, cy, R, R); g.fill();
  if (red != null) { g.strokeStyle = '#b42a1e'; g.lineWidth = R * .08; g.beginPath(); g.arc(cx, cy, R * .82, a0 + (red / max) * (a1 - a0), a1); g.stroke(); }
  g.strokeStyle = '#1a1612'; g.fillStyle = '#1a1612'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.font = `700 ${R * .2}px "Barlow Condensed", sans-serif`;
  for (let v = 0; v <= max + .001; v += step / 2) {
    const a = a0 + v / max * (a1 - a0), major = Math.abs(v / step - Math.round(v / step)) < .01;
    g.lineWidth = major ? R * .035 : R * .018;
    g.beginPath(); g.moveTo(cx + Math.cos(a) * R * (major ? .74 : .8), cy + Math.sin(a) * R * (major ? .74 : .8)); g.lineTo(cx + Math.cos(a) * R * .9, cy + Math.sin(a) * R * .9); g.stroke();
    if (major) g.fillText(String(Math.round(v)), cx + Math.cos(a) * R * .58, cy + Math.sin(a) * R * .58);
  }
  g.font = `600 ${R * .12}px "Barlow Condensed", sans-serif`; g.fillText(label, cx, cy - R * .28);
  if (odo) { g.fillStyle = '#16120e'; g.fillRect(cx - R * .34, cy + R * .4, R * .68, R * .2); g.fillStyle = '#ece3c8'; g.font = `700 ${R * .15}px "Barlow Condensed", sans-serif`; g.fillText(odo, cx, cy + R * .505); }
  const a = a0 + clamp(val / max, 0, 1.04) * (a1 - a0);
  g.strokeStyle = '#a8231a'; g.lineWidth = R * .045; g.lineCap = 'round';
  g.beginPath(); g.moveTo(cx - Math.cos(a) * R * .15, cy - Math.sin(a) * R * .15); g.lineTo(cx + Math.cos(a) * R * .8, cy + Math.sin(a) * R * .8); g.stroke(); g.lineCap = 'butt';
  g.fillStyle = '#16120e'; ell(g, cx, cy, R * .09, R * .09); g.fill();
  g.strokeStyle = 'rgba(255,255,255,.18)'; g.lineWidth = R * .05; g.beginPath(); g.arc(cx, cy, R * .92, Math.PI * 1.1, Math.PI * 1.45); g.stroke();
}

function telemetry() {
  const pct = clamp(P.speed / CAR.max, 0, 1.3), gear = mode === 'play' ? 1 + Math.min(4, Math.floor(Math.min(pct, .999) * 5)) : 2;
  const rpm = P.speed < 100 ? .9 : 1.2 + ((pct * 5) % 1 + (pct >= 1 ? 1 : 0)) * 5.8 + (P.boost ? .6 : 0);
  return { kmh: P.speed * .0165, gear, rpm: Math.min(8.4, rpm) };
}

function drawGauges(cx, cy, R, cockpit) {
  const t = telemetry();
  gauge(cx, cy, R, t.kmh, 240, 40, 'KM/SOAT', null, String(Math.floor(P.pos / 470)).padStart(5, '0'));
  gauge(cx + R * 2.35, cy, R * (cockpit ? 1 : .82), t.rpm, 8, 1, 'TAXOMETR', 6.5, '1940');
  ctx.fillStyle = cockpit ? '#ece3c8' : '#ece4cf'; ctx.font = hudFont(R * .26); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText('UZATMA ' + t.gear, cx + R * 1.18, cy - R * 1.32);
}

function fmtTime(t) { const m = Math.floor(t / 60), s = t % 60; return `${String(m).padStart(2, '0')}:${s.toFixed(1).padStart(4, '0')}`; }

function drawHUD() {
  const g = ctx, pad = u * 2.2, top = ST + pad;
  g.textBaseline = 'middle';
  // Chap tepa: ta'qib holati, pul, hujjatlar
  const pw = u * 34, ph = u * 17;
  panel(pad, top, pw, ph);
  const heat = clamp(1 - P.gap / 9000, 0, 1);
  g.fillStyle = '#939cab'; g.font = hudFont(u * 1.5, 600); g.textAlign = 'left'; g.fillText("TA'QIB", pad + u * 1.6, top + u * 2.4);
  g.textAlign = 'right'; g.fillStyle = heat > .7 ? '#ff3b4e' : '#ece4cf'; g.fillText(Math.round(P.gap / 25) + ' m', pad + pw - u * 1.6, top + u * 2.4);
  g.fillStyle = '#1d232d'; g.fillRect(pad + u * 1.6, top + u * 4.2, pw - u * 3.2, u * 1.3);
  g.fillStyle = heat > .7 ? (Math.floor(time * 6) % 2 ? '#ff3b4e' : '#9a1e2a') : heat > .45 ? '#f2b33d' : '#45c8f0';
  g.fillRect(pad + u * 1.6, top + u * 4.2, (pw - u * 3.2) * heat, u * 1.3);
  g.textAlign = 'left'; g.fillStyle = '#f2b33d'; g.font = hudFont(u * 3);
  g.fillText('$' + P.money.toLocaleString('en-US'), pad + u * 1.6, top + u * 9);
  g.fillStyle = '#45c8f0'; g.font = hudFont(u * 1.7, 600); g.fillText(`HUJJATLAR ${P.docs}/${DOCS}`, pad + u * 1.6, top + u * 13.6);

  // O'ng tepa: mini-xarita va vaqt
  const ms = u * 22, mx = W - pad - ms;
  panel(mx, top, ms, ms + u * 7);
  if (routeBox) {
    const bw = routeBox.x1 - routeBox.x0 || 1, bh = routeBox.y1 - routeBox.y0 || 1, sc = Math.min((ms - u * 4) / bw, (ms - u * 4) / bh);
    const MX = x => mx + ms / 2 + (x - (routeBox.x0 + routeBox.x1) / 2) * sc, MY = y => top + ms / 2 - (y - (routeBox.y0 + routeBox.y1) / 2) * sc;
    g.strokeStyle = 'rgba(236,228,207,.35)'; g.lineWidth = Math.max(1, u * .3); g.beginPath();
    route.forEach((p, i) => i ? g.lineTo(MX(p[0]), MY(p[1])) : g.moveTo(MX(p[0]), MY(p[1]))); g.stroke();
    const at = z => route[clamp(Math.floor(z / SEG / 8), 0, route.length - 1)];
    const e = route[route.length - 1]; g.fillStyle = '#8ff0a8'; g.fillRect(MX(e[0]) - u * .7, MY(e[1]) - u * .7, u * 1.4, u * 1.4);
    const c = at(Math.max(0, P.pos - P.gap)); g.fillStyle = Math.floor(time * 6) % 2 ? '#ff3b4e' : '#4aa8ff'; ell(g, MX(c[0]), MY(c[1]), u * .7, u * .7); g.fill();
    const p = at(P.pos); g.fillStyle = '#f2b33d'; ell(g, MX(p[0]), MY(p[1]), u * .9, u * .9); g.fill();
  }
  g.textAlign = 'center'; g.fillStyle = '#ece4cf'; g.font = hudFont(u * 1.9, 600); g.fillText(fmtTime(P.t), mx + ms / 2, top + ms + u * 1.8);
  g.fillStyle = '#8ff0a8'; g.font = hudFont(u * 1.3, 600); g.fillText('SAFEHOUSE ' + (Math.max(0, FINISH - P.pos) / 470000 * 1).toFixed(2) + ' km', mx + ms / 2, top + ms + u * 4.6);

  // Markaz tepa: logotip (keng ekranda)
  if (W / u > 150) {
    g.font = `italic ${hudFont(u * 2.6)}`; g.textAlign = 'right'; g.fillStyle = '#45c8f0'; g.fillText('CYBER-', W / 2 + u * .5, top + u * 2);
    g.textAlign = 'left'; g.fillStyle = '#f2b33d'; g.fillText('SPRINT', W / 2 + u * .5, top + u * 2);
    g.textAlign = 'center'; g.fillStyle = '#ece4cf'; g.font = `${u * 1.5}px Limelight, Georgia, serif`; g.fillText('NOIR HEIST 1940', W / 2, top + u * 4.6);
  }

  // Pastki: spidometrlar va nitro
  if (cam !== 2) {
    const R = u * 7.5;
    drawGauges(W - pad - R * 3.3, H - pad - R * 1.15 - (touchMode ? u * 22 : 0), R, false);
  }
  const nx = pad, ny = H - pad - u * 4 - (touchMode ? u * 24 : 0) - (cam === 2 ? H * .2 : 0);
  g.textAlign = 'left'; g.fillStyle = '#45c8f0'; g.font = hudFont(u * 1.4, 600); g.fillText('NITRO', nx, ny - u * 1.6);
  g.fillStyle = '#1d232d'; g.fillRect(nx, ny, u * 22, u * 1.2);
  g.fillStyle = P.boost ? '#ffffff' : '#45c8f0'; g.fillRect(nx, ny, u * 22 * P.nitro, u * 1.2);
  if (P.drift > .3) { g.fillStyle = '#f2b33d'; g.font = hudFont(u * 2.2); g.fillText('DRIFT ' + P.drift.toFixed(1) + 's', nx, ny - u * 4.4); }

  // Ogohlantirishlar
  g.textAlign = 'center';
  if (P.warn && Math.floor(time * 5) % 2) { g.fillStyle = '#f2b33d'; g.font = hudFont(u * 3.4); g.fillText('⚠ TRAMVAY!', W / 2, H * .28); }
  else if (heat > .72 && Math.floor(time * 4) % 2) { g.fillStyle = '#ff3b4e'; g.font = hudFont(u * 3); g.fillText('POLITSIYA YAQIN!', W / 2, H * .28); }
  for (const t of texts) { g.globalAlpha = clamp(t.life, 0, 1); g.fillStyle = rgb(t.col); g.font = hudFont(u * 3.2); g.fillText(t.s, t.x, t.y); }
  g.globalAlpha = 1;
}

function drawParticles() {
  const g = ctx;
  for (const p of parts) {
    const a = p.a * clamp(p.life / p.max, 0, 1);
    if (p.k === 'mist') { glow(g, p.x, p.y, p.s, p.s * .7, p.col, a); continue; }
    if (p.k === 'spark') { g.globalCompositeOperation = 'lighter'; g.strokeStyle = rgb(p.col, a); g.lineWidth = Math.max(1, p.s * .6);
      g.beginPath(); g.moveTo(p.x, p.y); g.lineTo(p.x - p.vx * .03, p.y - p.vy * .03); g.stroke(); g.globalCompositeOperation = 'source-over'; continue; }
    g.fillStyle = rgb(p.col, a);
    if (p.k === 'sq') { g.save(); g.translate(p.x, p.y); g.rotate(p.rot); g.fillRect(-p.s, -p.s * .6, p.s * 2, p.s * 1.2); g.restore(); }
    else { ell(g, p.x, p.y, p.s, p.s); g.fill(); }
  }
}

// Kino effektlari: vinyetka, plyonka donadorligi, chaqmoq, zarba, sirena chaqnashi, nitro chiziqlari
function post() {
  const g = ctx;
  if (P.boost && mode === 'play') {
    g.globalCompositeOperation = 'lighter'; g.strokeStyle = 'rgba(180,230,255,.18)'; g.lineWidth = Math.max(1, u * .2); g.beginPath();
    for (let i = 0; i < 24; i++) { const a = hash(i, Math.floor(time * 20)) * Math.PI * 2, r0 = Math.max(W, H) * (.3 + hash(i, 9) * .2);
      g.moveTo(W / 2 + Math.cos(a) * r0, H * .45 + Math.sin(a) * r0); g.lineTo(W / 2 + Math.cos(a) * r0 * 1.6, H * .45 + Math.sin(a) * r0 * 1.6); }
    g.stroke(); g.globalCompositeOperation = 'source-over';
  }
  g.drawImage(VIG, 0, 0, W, H);
  if (GRAIN) { g.save(); g.globalAlpha = .06; g.translate(Math.random() * 128, Math.random() * 128); g.fillStyle = GRAIN; g.fillRect(-128, -128, W + 256, H + 256); g.restore(); }
  if (L.flash > 0) { g.fillStyle = `rgba(220,230,255,${L.flash * .22})`; g.fillRect(0, 0, W, H); }
  if (P.flash > 0) { g.fillStyle = `rgba(255,120,90,${P.flash * .28})`; g.fillRect(0, 0, W, H); }
  const heat = mode === 'play' ? clamp(1 - P.gap / 6000, 0, 1) : 0;
  if (heat > 0) {
    const on = Math.floor(time * 7) % 2;
    for (const [x, col] of [[0, on ? [255, 40, 60] : [60, 120, 255]], [W, on ? [60, 120, 255] : [255, 40, 60]]]) glow(g, x, H * .75, W * .3, H * .5, col, heat * .55);
  }
}
