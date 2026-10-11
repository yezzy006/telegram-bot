'use strict';
// ===== 4. Mashinalar chizmasi (orqadan ko'rinish va yuqoridan ko'rinish) =====
const shade = (c, k) => k > 0 ? mix(c, [255, 255, 255], k) : mix(c, [0, 0, 0], -k);
function vgrad(g, y0, y1, stops) {
  const gr = g.createLinearGradient(0, y0, 0, y1);
  stops.forEach((c, i) => gr.addColorStop(i / (stops.length - 1), rgb(c)));
  return gr;
}

// O'yinchi mashinasi orqadan. (0,0) = yer, markaz. w = piksel kenglik.
function drawPlayer(g, X, Y, w, car, st = {}) {
  g.save(); g.translate(X, Y); g.rotate((st.yaw || 0) * .12);
  ell(g, 0, -w * .01, w * .58, w * .07); g.fillStyle = 'rgba(0,0,0,.5)'; g.fill();
  const B = car.body, T = car.trim, brake = !!st.brake;
  if (car.id === 'neo') neoRear(g, w, B, T, brake);
  else if (car.id === 'van') vanRear(g, w, B, T, brake);
  else phaRear(g, w, B, T, brake);
  if (st.boost) {
    for (const sx of [-.09, .09]) {
      const fl = w * (.12 + Math.random() * .1);
      glow(g, sx * w, -w * .1, fl, fl * .7, [90, 200, 255], .9);
      g.fillStyle = 'rgba(200,240,255,.9)'; ell(g, sx * w, -w * .1, w * .025, w * .02); g.fill();
    }
  }
  g.restore();
}

function tyres(g, w, wd, ht) {
  g.fillStyle = '#0a0a0c';
  rr(g, -w * .5, -ht, wd, ht, w * .03); g.fill();
  rr(g, w * .5 - wd, -ht, wd, ht, w * .03); g.fill();
}

function neoRear(g, w, B, T, brake) {
  const h = w * .46;
  tyres(g, w, w * .17, w * .2);
  // pastki korpus
  g.fillStyle = vgrad(g, -h, 0, [shade(B, .25), B, shade(B, -.45)]);
  g.beginPath(); g.moveTo(-w * .5, -w * .07); g.lineTo(-w * .5, -h * .55);
  g.quadraticCurveTo(-w * .48, -h * .92, -w * .36, -h * .95); g.lineTo(w * .36, -h * .95);
  g.quadraticCurveTo(w * .48, -h * .92, w * .5, -h * .55); g.lineTo(w * .5, -w * .07); g.closePath(); g.fill();
  // kabina va orqa oyna (dvigatel panjaralari bilan)
  g.fillStyle = rgb(shade(B, -.2));
  g.beginPath(); g.moveTo(-w * .34, -h * .95); g.lineTo(-w * .22, -h * 1.42); g.lineTo(w * .22, -h * 1.42); g.lineTo(w * .34, -h * .95); g.closePath(); g.fill();
  g.fillStyle = '#14181e';
  g.beginPath(); g.moveTo(-w * .28, -h * 1); g.lineTo(-w * .19, -h * 1.36); g.lineTo(w * .19, -h * 1.36); g.lineTo(w * .28, -h * 1); g.closePath(); g.fill();
  g.strokeStyle = 'rgba(0,0,0,.6)'; g.lineWidth = Math.max(1, w * .008);
  for (let i = 1; i < 4; i++) { const y = -h * (1 + i * .09); g.beginPath(); g.moveTo(-w * (.27 - i * .022), y); g.lineTo(w * (.27 - i * .022), y); g.stroke(); }
  // sariq chiziqlar
  g.fillStyle = rgb(T);
  g.fillRect(-w * .075, -h * 1.42, w * .035, h * 1.1); g.fillRect(w * .04, -h * 1.42, w * .035, h * 1.1);
  // LED stop-chiroq tasmasi
  const tl = brake ? [255, 70, 55] : [255, 214, 160];
  g.fillStyle = rgb(tl); g.fillRect(-w * .42, -h * .68, w * .84, h * .06);
  glow(g, 0, -h * .65, w * .6, h * .22, brake ? [255, 60, 40] : [255, 190, 110], brake ? .9 : .5);
  // diffuzor va chiqindi quvurlari
  g.fillStyle = '#0e0e10'; g.fillRect(-w * .36, -h * .32, w * .72, h * .26);
  g.strokeStyle = rgb(T); g.lineWidth = Math.max(1, w * .01);
  g.beginPath(); g.moveTo(-w * .46, -h * .1); g.lineTo(-w * .36, -h * .06); g.lineTo(w * .36, -h * .06); g.lineTo(w * .46, -h * .1); g.stroke();
  g.fillStyle = '#2a2a2e'; for (const sx of [-.09, .09]) { ell(g, sx * w, -h * .2, w * .03, w * .025); g.fill(); }
  // orqa qanot
  g.fillStyle = '#18181b';
  g.fillRect(-w * .21, -h * 1.4, w * .03, h * .46); g.fillRect(w * .18, -h * 1.4, w * .03, h * .46);
  rr(g, -w * .56, -h * 1.52, w * 1.12, h * .1, w * .02); g.fill();
  g.fillStyle = rgb(T); g.fillRect(-w * .58, -h * 1.62, w * .05, h * .26); g.fillRect(w * .53, -h * 1.62, w * .05, h * .26);
}

function vanRear(g, w, B, T, brake) {
  const h = w * .62;
  tyres(g, w, w * .15, w * .19);
  g.fillStyle = vgrad(g, -h, 0, [shade(B, .2), B, shade(B, -.5)]);
  for (const sx of [-1, 1]) { ell(g, sx * w * .36, -w * .2, w * .15, w * .17); g.fill(); }  // qanotlar
  rr(g, -w * .44, -h * .66, w * .88, h * .54, w * .12); g.fill();
  ell(g, 0, -h * .64, w * .36, h * .2); g.fill();
  // gumbaz kabina
  g.fillStyle = rgb(shade(B, -.15));
  g.beginPath(); g.moveTo(-w * .3, -h * .66); g.bezierCurveTo(-w * .3, -h * 1.22, w * .3, -h * 1.22, w * .3, -h * .66); g.closePath(); g.fill();
  g.fillStyle = '#161a20'; ell(g, 0, -h * .86, w * .16, h * .09); g.fill();
  g.strokeStyle = 'rgba(255,220,170,.25)'; g.lineWidth = Math.max(1, w * .008); g.beginPath(); g.moveTo(-w * .1, -h * .9); g.lineTo(w * .04, -h * .82); g.stroke();
  // kichik spoiler
  g.fillStyle = rgb(shade(B, -.35)); g.fillRect(-w * .3, -h * .82, w * .6, h * .04);
  // dumaloq stop-chiroqlar
  for (const sx of [-1, 1]) {
    g.fillStyle = brake ? '#ff4a3a' : '#c42a22'; ell(g, sx * w * .36, -h * .44, w * .04, w * .04); g.fill();
    glow(g, sx * w * .36, -h * .44, w * (brake ? .16 : .1), w * (brake ? .16 : .1), [255, 50, 30], .8);
  }
  g.fillStyle = 'rgba(255,255,255,.85)'; g.font = `700 ${w * .1}px "Barlow Condensed", sans-serif`; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText('88', 0, -h * .5);
  // xrom bamper
  g.fillStyle = vgrad(g, -h * .2, -h * .12, [[236, 236, 230], [150, 150, 146]]); rr(g, -w * .48, -h * .2, w * .96, h * .08, w * .03); g.fill();
  g.fillStyle = '#e8e2c8'; g.fillRect(-w * .07, -h * .32, w * .14, h * .08);
}

function phaRear(g, w, B, T, brake) {
  const h = w * .42;
  tyres(g, w, w * .14, w * .2);
  g.fillStyle = vgrad(g, -h, 0, [shade(B, .25), B, shade(B, -.5)]);
  for (const sx of [-1, 1]) { ell(g, sx * w * .34, -h * .55, w * .16, h * .5); g.fill(); }
  rr(g, -w * .42, -h * .8, w * .84, h * .64, w * .1); g.fill();
  // ochiq salon: haydovchi boshi va bosh tayanchi
  g.fillStyle = rgb(shade(B, -.2)); ell(g, -w * .14, -h * .86, w * .1, h * .22); g.fill();
  g.fillStyle = '#2a201a'; ell(g, -w * .14, -h * 1.2, w * .07, w * .075); g.fill();
  g.fillStyle = '#3b2c22'; ell(g, -w * .14, -h * 1.27, w * .07, w * .04); g.fill();
  g.strokeStyle = 'rgba(220,220,210,.6)'; g.lineWidth = Math.max(1, w * .01);
  g.beginPath(); g.moveTo(-w * .32, -h * .98); g.lineTo(w * .32, -h * .98); g.stroke();
  // raqamli doira
  g.fillStyle = rgb(T); ell(g, w * .16, -h * .5, w * .07, w * .07); g.fill();
  g.fillStyle = '#111'; g.font = `700 ${w * .08}px "Barlow Condensed", sans-serif`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('07', w * .16, -h * .49);
  for (const sx of [-1, 1]) {
    g.fillStyle = brake ? '#ff4a3a' : '#b82820'; ell(g, sx * w * .34, -h * .62, w * .028, w * .028); g.fill();
    glow(g, sx * w * .34, -h * .62, w * (brake ? .14 : .08), w * (brake ? .14 : .08), [255, 50, 30], .8);
  }
  g.fillStyle = vgrad(g, -h * .24, -h * .14, [[236, 236, 230], [150, 150, 146]]); rr(g, -w * .44, -h * .24, w * .88, h * .09, w * .03); g.fill();
}

// 1940-yillar sedani orqadan (oqim va to'xtab turgan mashinalar)
function carRear(X, Y, w, col, f, lights) {
  const g = ctx, c = mix(col, FOG, f), h = w * .78;
  ell(g, X, Y, w * .55, w * .06); g.fillStyle = rgb([0, 0, 0], .45 * (1 - f)); g.fill();
  g.fillStyle = rgb(mix([10, 10, 12], FOG, f));
  g.fillRect(X - w * .46, Y - w * .18, w * .16, w * .18); g.fillRect(X + w * .3, Y - w * .18, w * .16, w * .18);
  g.fillStyle = rgb(shade(c, -.2));
  for (const sx of [-1, 1]) { ell(g, X + sx * w * .36, Y - w * .22, w * .15, w * .16); g.fill(); }
  g.fillStyle = rgb(c); rr(g, X - w * .42, Y - h * .64, w * .84, h * .52, w * .1); g.fill();
  ell(g, X, Y - h * .62, w * .36, h * .18); g.fill();
  g.fillStyle = rgb(shade(c, -.12));
  g.beginPath(); g.moveTo(X - w * .3, Y - h * .64); g.bezierCurveTo(X - w * .3, Y - h * 1.15, X + w * .3, Y - h * 1.15, X + w * .3, Y - h * .64); g.closePath(); g.fill();
  g.fillStyle = rgb(mix([28, 34, 42], FOG, f)); ell(g, X, Y - h * .84, w * .15, h * .08); g.fill();
  for (const sx of [-1, 1]) {
    g.fillStyle = lights ? rgb(mix([255, 60, 50], FOG, f * .6)) : rgb(mix([80, 20, 20], FOG, f));
    ell(g, X + sx * w * .35, Y - h * .42, w * .035, w * .035); g.fill();
    if (lights) glow(g, X + sx * w * .35, Y - h * .42, w * .14, w * .14, [255, 50, 30], .7 * (1 - f));
  }
  g.fillStyle = rgb(mix([170, 170, 165], FOG, f)); g.fillRect(X - w * .46, Y - h * .2, w * .92, h * .07);
  g.fillStyle = rgb(mix([220, 212, 180], FOG, f)); g.fillRect(X - w * .07, Y - h * .33, w * .14, h * .07);
}

// Yuqoridan ko'rinish. old tomoni = ekranda yuqoriga.
function drawTopCar(X, Y, len, wid, body, kind, yaw, lights) {
  const g = ctx;
  g.save(); g.translate(X, Y); g.rotate(yaw || 0);
  if (lights) {
    g.globalCompositeOperation = 'lighter';
    const gr = g.createLinearGradient(0, -len * .5, 0, -len * 2.6);
    gr.addColorStop(0, 'rgba(255,236,190,.32)'); gr.addColorStop(1, 'rgba(255,236,190,0)');
    g.fillStyle = gr; g.beginPath(); g.moveTo(-wid * .4, -len * .5); g.lineTo(-wid * 1.3, -len * 2.6); g.lineTo(wid * 1.3, -len * 2.6); g.lineTo(wid * .4, -len * .5); g.fill();
    g.globalCompositeOperation = 'source-over';
  }
  g.fillStyle = 'rgba(0,0,0,.45)'; rr(g, -wid * .5 + wid * .12, -len * .5 + wid * .15, wid, len, wid * .3); g.fill();
  g.fillStyle = rgb(body); rr(g, -wid * .5, -len * .5, wid, len, wid * .32); g.fill();
  if (kind === 'police') { g.fillStyle = '#e8e4da'; g.fillRect(-wid * .5, -len * .12, wid, len * .26); }
  if (kind === 'pha') {
    g.fillStyle = '#1a1410'; rr(g, -wid * .32, -len * .05, wid * .64, len * .3, wid * .12); g.fill();
    g.fillStyle = '#3b2c22'; ell(g, -wid * .14, len * .08, wid * .12, wid * .12); g.fill();
  } else {
    g.fillStyle = rgb(shade(body, kind === 'police' ? .3 : -.25)); rr(g, -wid * .38, -len * .14, wid * .76, len * .42, wid * .2); g.fill();
    g.fillStyle = '#1b222b'; rr(g, -wid * .34, -len * .16, wid * .68, len * .1, wid * .08); g.fill();
    rr(g, -wid * .32, len * .2, wid * .64, len * .07, wid * .06); g.fill();
  }
  if (kind === 'neo') { g.fillStyle = 'rgb(242,182,44)'; g.fillRect(-wid * .12, -len * .5, wid * .07, len); g.fillRect(wid * .05, -len * .5, wid * .07, len);
    g.fillStyle = '#18181b'; g.fillRect(-wid * .55, len * .36, wid * 1.1, len * .07); }
  if (kind === 'police') {
    const on = Math.floor(time * 8) % 2;
    g.fillStyle = on ? '#ff3b4e' : '#5a1a20'; g.fillRect(-wid * .32, -len * .02, wid * .3, len * .06);
    g.fillStyle = on ? '#2a3a7a' : '#4aa8ff'; g.fillRect(wid * .02, -len * .02, wid * .3, len * .06);
    glow(g, on ? -wid * .2 : wid * .2, 0, wid * 1.6, wid * 1.6, on ? [255, 50, 60] : [70, 150, 255], .7);
  }
  g.fillStyle = '#ff4a3a'; g.fillRect(-wid * .4, len * .46, wid * .16, len * .04); g.fillRect(wid * .24, len * .46, wid * .16, len * .04);
  g.fillStyle = '#fff4d0'; g.fillRect(-wid * .4, -len * .5, wid * .14, len * .03); g.fillRect(wid * .26, -len * .5, wid * .14, len * .03);
  g.restore();
}
