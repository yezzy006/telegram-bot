'use strict';
// ===== 9. O'yin sikli (Game Loop), ekranlar, boshqaruv =====
function resize() {
  const cw = innerWidth, ch = innerHeight;
  DPR = Math.min(devicePixelRatio || 1, cw * ch > 1.1e6 ? 1 : 1.5);
  W = cv.width = Math.round(cw * DPR); H = cv.height = Math.round(ch * DPR);
  U = W / 2; u = Math.min(W, H) / 100; ST = ($('safe').offsetHeight || 0) * DPR;
  const portrait = H > W * 1.05;
  VIEW.hor = H * (portrait ? .47 : .42);
  const py = H * (portrait ? .84 : .88), hr = portrait ? W * .46 : Math.min(W * .3, H * .55);
  VIEW.camH = (py - VIEW.hor) * ROAD / hr;      // o'yinchi mashinasi ekranning pastida turishi uchun kamera balandligi
  VIEW.pz = DEPTH / (hr / (ROAD * U));          // kamera va mashina orasidagi masofa
  VIEW.tk = Math.min(W * .62, H * .9) / (3.4 * ROAD);
  DRAW = W * H > 1.4e6 ? 190 : 150;
  rain.length = 0;
  const nr = portrait ? 140 : 220;
  for (let i = 0; i < nr; i++) rain.push({ x: Math.random() * 1.2 - .1, y: Math.random(), v: .9 + Math.random() * .8, l: .6 + Math.random() * .8 });
  buildPost();
}

function update(dt) {
  time += dt;
  if (mode === 'play') physics(dt); else if (mode === 'garage') attract(dt);
  fx(dt);
  const t = telemetry();
  SND.update(t.rpm, (K.gas || touchMode) ? 1 : 0, mode === 'play' ? clamp(1 - P.gap / 7000, 0, 1) : 0);
}

function render() {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  const view = mode === 'garage' ? 0 : cam;
  const sx = P.shake ? (Math.random() - .5) * P.shake * u * 3 : 0, sy = P.shake ? (Math.random() - .5) * P.shake * u * 3 : 0;
  ctx.save(); ctx.translate(sx, sy);
  if (view === 1) renderTop(); else renderStreet(view === 2);
  drawRain(); drawParticles();
  ctx.restore();
  if (view === 2) drawCockpit();
  post();
  if (mode === 'play' || mode === 'pause') drawHUD();
}

let last = performance.now();
function frame(t) {
  const dt = Math.min(.05, (t - last) / 1000); last = t;
  if (mode !== 'pause') update(dt);
  render();
  requestAnimationFrame(frame);
}

// --- Ekranlar
function show(id) { for (const s of ['garage', 'pause', 'end']) $(s).hidden = s !== id; }
function setPlayUI(on) { $('chips').hidden = !on; $('touch').hidden = !(on && touchMode); document.body.classList.toggle('touch', touchMode); }

function startRun() {
  SND.init();
  buildTrack(Date.now() % 1e9); resetPlayer();
  for (const k in K) K[k] = 0;
  mode = 'play'; show(null); setPlayUI(true);
}

function toGarage() {
  mode = 'garage'; show('garage'); setPlayUI(false);
  buildTrack(1940); resetPlayer(); refreshBest();
}

let best = 0;
try { best = +localStorage.getItem('noirheist-best') || 0; } catch (e) {}
function refreshBest() { $('bestLine').innerHTML = best ? `Rekord: <b>${best.toLocaleString('en-US')}</b> ball` : ''; }

function finish(win) {
  mode = 'end'; setPlayUI(false);
  const timeBonus = win ? Math.max(0, Math.round((300 - P.t) * 120)) : 0;
  const score = Math.max(0, P.money + P.docs * 5000 + timeBonus + (win ? 10000 : 0) - P.hits * 250);
  const rec = win && score > best;
  if (rec) { best = score; try { localStorage.setItem('noirheist-best', String(best)); } catch (e) {} }
  $('endTitle').textContent = win ? 'Qochib qutuldingiz!' : "Qo'lga tushdingiz";
  $('endTitle').className = win ? 'win' : 'lose';
  $('endText').textContent = win
    ? (rec ? 'Yangi rekord. ' : '') + "Garaj eshigi yopildi. Politsiya sireni shahar tumanida so'nib boradi."
    : "Politsiya mashinasi yo'lingizni to'sdi. To'siqlarga kamroq urilib, drift bilan nitro to'plang.";
  const rows = [['Vaqt', fmtTime(P.t)], ['Pul', '$' + P.money.toLocaleString('en-US')], ['Maxfiy hujjatlar', `${P.docs} / ${DOCS}`],
    ['To\'qnashuvlar', String(P.hits)], ['Masofa', (P.pos / 470000).toFixed(2) + ' km'], ['Ball', score.toLocaleString('en-US')]];
  $('endStats').innerHTML = rows.map(r => `<dt>${r[0]}</dt><dd>${r[1]}</dd>`).join('');
  show('end'); $('again').focus();
}

function togglePause() {
  if (mode === 'play') { mode = 'pause'; show('pause'); setPlayUI(false); $('resume').focus(); }
  else if (mode === 'pause') { mode = 'play'; show(null); setPlayUI(true); last = performance.now(); }
}
const switchCam = () => { cam = (cam + 1) % 3; drops.length = 0; };

// --- Garaj: mashina kartochkalari
function buildCards() {
  const box = $('cars'); box.innerHTML = '';
  CARS.forEach((c, i) => {
    const b = document.createElement('button'); b.className = 'card'; b.type = 'button'; b.dataset.i = i;
    b.setAttribute('aria-pressed', i === carIdx ? 'true' : 'false');
    const stat = (l, v) => `<span>${l}</span><span class="bar"><i style="width:${v}%"></i></span><b>${v}</b>`;
    b.innerHTML = `<canvas></canvas><h3>${c.name}<span class="yr">${c.year}</span></h3><p>${c.desc}</p>
      <div class="stats">${stat('Tezlik', c.speed)}${stat('Tezlanish', c.accel)}${stat('Boshqaruv', c.handling)}</div>`;
    b.addEventListener('click', () => selectCar(i));
    box.appendChild(b);
  });
  drawPreviews();
}
function selectCar(i) {
  carIdx = (i + CARS.length) % CARS.length; CAR = CARS[carIdx];
  document.querySelectorAll('.card').forEach((b, j) => b.setAttribute('aria-pressed', j === carIdx ? 'true' : 'false'));
}
function drawPreviews() {
  document.querySelectorAll('.card canvas').forEach((c, i) => {
    const r = c.getBoundingClientRect(), d = Math.min(devicePixelRatio || 1, 2);
    c.width = Math.max(1, r.width * d); c.height = Math.max(1, r.height * d);
    const g = c.getContext('2d'), w = Math.min(c.width * .44, c.height * .8), by = c.height * .88;
    const bg = g.createRadialGradient(c.width / 2, by, 0, c.width / 2, by, c.width * .6);
    bg.addColorStop(0, '#3a3328'); bg.addColorStop(1, '#101216'); g.fillStyle = bg; g.fillRect(0, 0, c.width, c.height);
    const sp = g.createLinearGradient(0, 0, 0, by); sp.addColorStop(0, 'rgba(255,214,150,0)'); sp.addColorStop(1, 'rgba(255,214,150,.12)');
    g.fillStyle = sp; g.beginPath(); g.moveTo(c.width * .45, 0); g.lineTo(c.width * .55, 0); g.lineTo(c.width * .85, by); g.lineTo(c.width * .15, by); g.fill();
    g.save(); g.translate(0, by * 2); g.scale(1, -1); g.globalAlpha = .18; drawPlayer(g, c.width / 2, by, w, CARS[i], {}); g.restore();
    drawPlayer(g, c.width / 2, by, w, CARS[i], {});
  });
}

// --- Klaviatura
const KEYMAP = { ArrowLeft: 'left', KeyA: 'left', ArrowRight: 'right', KeyD: 'right', ArrowUp: 'gas', KeyW: 'gas',
  ArrowDown: 'brake', KeyS: 'brake', Space: 'hb', ShiftLeft: 'nitro', ShiftRight: 'nitro', KeyN: 'nitro' };
addEventListener('keydown', e => {
  if (mode === 'garage') {
    if (e.code === 'ArrowLeft' || e.code === 'KeyA') { selectCar(carIdx - 1); e.preventDefault(); }
    if (e.code === 'ArrowRight' || e.code === 'KeyD') { selectCar(carIdx + 1); e.preventDefault(); }
    if (/^Digit[1-3]$/.test(e.code)) selectCar(+e.code.slice(5) - 1);
    if (e.code === 'Enter' && document.activeElement?.tagName !== 'BUTTON') startRun();
    return;
  }
  if (KEYMAP[e.code]) { K[KEYMAP[e.code]] = 1; touchMode = false; e.preventDefault(); }
  if (e.code === 'KeyC' && mode === 'play') switchCam();
  if (e.code === 'KeyP' || e.code === 'Escape') togglePause();
  if (e.code === 'KeyM') SND.toggle();
});
addEventListener('keyup', e => { if (KEYMAP[e.code]) K[KEYMAP[e.code]] = 0; });
addEventListener('blur', () => { for (const k in K) K[k] = 0; if (mode === 'play') togglePause(); });
document.addEventListener('visibilitychange', () => { if (document.hidden && mode === 'play') togglePause(); });

// --- Sensorli tugmalar (bir vaqtda bir nechta barmoq)
addEventListener('touchstart', () => { if (!touchMode) { touchMode = true; if (mode === 'play') setPlayUI(true); } }, { passive: true });
document.querySelectorAll('#touch button').forEach(b => {
  const k = b.dataset.k;
  const on = e => { e.preventDefault(); K[k] = 1; b.classList.add('on'); try { b.setPointerCapture(e.pointerId); } catch (_) {} };
  const off = () => { K[k] = 0; b.classList.remove('on'); };
  b.addEventListener('pointerdown', on);
  for (const ev of ['pointerup', 'pointercancel', 'lostpointercapture']) b.addEventListener(ev, off);
});
$('bCam').addEventListener('click', switchCam);
$('bPause').addEventListener('click', togglePause);
$('bMute').addEventListener('click', () => SND.toggle());
$('go').addEventListener('click', startRun);
$('again').addEventListener('click', startRun);
$('resume').addEventListener('click', togglePause);
$('toGarage1').addEventListener('click', toGarage);
$('toGarage2').addEventListener('click', toGarage);
addEventListener('resize', () => { resize(); if (mode === 'garage') drawPreviews(); });

// --- Ishga tushirish
buildSky(); resize(); buildCards(); toGarage();
document.fonts?.ready.then(drawPreviews);
requestAnimationFrame(frame);
