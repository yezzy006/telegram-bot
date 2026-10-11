'use strict';
// ===== 3. Fizika: ho'l tosh yo'l, drift, to'qnashuvlar, politsiya ta'qibi =====
function resetPlayer() {
  Object.assign(P, { x: 0, vx: 0, speed: 0, pos: SEG * 6, steer: 0, yaw: 0, nitro: .4, boost: false, drift: 0,
    aqua: 0, stun: 0, money: 0, docs: 0, hits: 0, shake: 0, flash: 0, gap: 5200, t: 0, copX: 0, warn: 0 });
  camXs = 0; parts.length = 0; texts.length = 0; drops.length = 0;
}

// Asosiy fizika qadami (har kadrda dt soniya)
function physics(dt) {
  const c = CAR, s0 = segAt(P.pos);
  P.t += dt;

  // --- Kirish (rul silliq aylanadi)
  const sIn = (K.right ? 1 : 0) - (K.left ? 1 : 0);
  P.steer += (sIn - P.steer) * Math.min(1, dt * (sIn ? 6 : 9));
  const gas = (K.gas || touchMode) && !K.brake;
  P.boost = !!K.nitro && P.nitro > .01 && P.stun <= 0;
  if (P.boost) P.nitro = Math.max(0, P.nitro - dt * .42);

  // --- Bo'ylama harakat: gaz, tormoz, trotuar, nitro
  const top = c.max * (P.boost ? 1.3 : 1);
  if (P.stun > 0) { P.stun -= dt; P.speed = Math.max(0, P.speed - c.max * 1.5 * dt); }
  else if (gas) P.speed += c.acc * dt * (1 - .5 * clamp(P.speed / c.max, 0, 1)) * (P.boost ? 1.8 : 1);
  else P.speed -= c.max * .22 * dt;
  if (K.brake) P.speed -= c.max * 1.05 * dt;
  if (Math.abs(P.x) > 1 && P.speed > c.max * .55) { P.speed -= c.max * 1.1 * dt; P.shake = Math.max(P.shake, .12); }
  if (P.speed > top) P.speed = Math.max(top, P.speed - c.max * .8 * dt);
  P.speed = Math.max(0, P.speed);
  const pct = P.speed / c.max;

  // --- Ko'ndalang harakat: ilashish (grip) ho'l toshda past, relslarda va ko'lmakda yanada past
  let grip = c.grip * .78;
  if (Math.abs(Math.abs(P.x) - .15) < .04) grip *= .6;          // tramvay relslari
  if (P.aqua > 0) { P.aqua -= dt; grip *= .25; }                // akvaplaning
  const drifting = K.hb && pct > .3 && P.stun <= 0;
  if (drifting) { grip *= .33; P.speed -= c.max * .16 * dt; }
  const target = P.steer * c.steer * (.3 + .7 * Math.min(1, pct)) * (P.speed > 200 ? 1 : 0);
  P.vx += (target - P.vx) * Math.min(1, grip * dt);             // past grip = sirpanish
  let cf = .42 * pct * pct * s0.curve;                           // markazdan qochma kuch
  if (drifting && Math.abs(P.steer) > .3) cf *= .45;             // drift burilishni osonlashtiradi
  P.x += (P.vx - cf) * dt;
  P.yaw += ((P.steer * .16 + (drifting ? P.steer * .38 : 0) + (P.vx - target) * .12) - P.yaw) * Math.min(1, dt * 7);

  // --- Drift nitro to'playdi va pul bonusi beradi
  if (drifting && Math.abs(P.steer) > .4) { P.drift += dt; P.nitro = Math.min(1, P.nitro + dt * .2); }
  else if (P.drift > 0) {
    if (P.drift > .6) { const b = Math.round(P.drift * pct * 900 / 50) * 50; if (b > 0) { P.money += b; addText('DRIFT +$' + b, [120, 220, 255]); } }
    P.drift = 0;
  }

  // --- Devorlar (binolar)
  const lim = 1.22;
  if (Math.abs(P.x) > lim) {
    P.x = Math.sign(P.x) * lim; P.vx *= -.25;
    if (P.speed > 2500) { P.speed -= c.max * .9 * dt; sparks(.3); }
    P.shake = Math.max(P.shake, .15);
  }

  // --- Ho'l yo'ldan sachrayotgan suv
  if (P.speed > 2500 && cam !== 2) {
    const n = pct * 2.5 | 0, d = cam === 1 ? 1 : -1;
    for (const sx of [-.36, .36]) emit(n, { x: VIEW.cx + sx * VIEW.cw, y: VIEW.cy, vx: sx * u * 8, vy: d * u * (8 + pct * 14),
      rvx: u * 10, rvy: u * 6, s: u * 1.2, gs: u * 6, life: .5, col: [190, 200, 215], a: .22, k: 'mist' });
  }

  // --- Oldinga siljish va o'tilgan segmentlardagi to'qnashuvlar
  const z0 = P.pos; P.pos += P.speed * dt;
  for (let i = Math.floor(z0 / SEG); i <= Math.floor(P.pos / SEG) && i < N; i++) {
    const s = segs[i];
    if (s.pud && P.aqua <= 0 && P.speed > 3000 && Math.abs(s.pud.x - P.x) < s.pud.w / 2 + .1) {
      P.aqua = .45; P.vx += (Math.random() - .5) * 1.4;
      emit(14, { x: VIEW.cx, y: VIEW.cy, sx: VIEW.cw, vy: -u * 30, rvx: u * 40, rvy: u * 20, g: u * 90, s: u * .6, life: .6, col: [200, 215, 235], a: .7 });
      SND.noise(.25, .15, 2500);
    }
    for (const sp of s.spr) if (sp.col && !sp.dead && Math.abs(sp.x - P.x) < (sp.w + .36) / 2) hit(sp);
  }

  // --- Oqimdagi mashinalar
  for (const t of traffic) {
    t.z += t.sp * dt;
    const dz = t.z - P.pos;
    if (dz < -4000) { t.z = P.pos + 42000 + Math.random() * 30000; t.x = Math.random() < .5 ? -.4 : .4; if (t.z > FINISH - 3000) t.z = -1e9; }
    if (dz > -250 && dz < 380 && Math.abs(t.x - P.x) < .38 && P.speed > t.sp) {
      P.speed = t.sp * .8; t.z = P.pos + 1400; t.sp *= 1.15; P.vx += P.x < t.x ? -1.3 : 1.3;
      P.shake = .6; P.flash = .35; P.hits++; sparks(1); SND.crash(.8);
    }
  }

  // --- Tramvaylar: o'yinchi yaqinlashganda yo'lni kesib o'tadi
  P.warn = 0;
  for (const tr of trams) {
    const tz = tr.c * SEG;
    if (tr.st === 0 && P.pos > tz - SEG * 95) {
      tr.st = 1; const tt = Math.max(.6, (tz - P.pos) / Math.max(P.speed, 5000));
      tr.x = -tr.side * 4.6; tr.vx = tr.side * clamp(4.6 / tt * (.8 + Math.random() * .4), 1.4, 4.2);
      SND.bell();
    }
    if (tr.st === 1) {
      tr.x += tr.vx * dt;
      if (Math.abs(tr.x) > 5 && Math.sign(tr.x) === tr.side) tr.st = 2;
      if (tz - P.pos > 0 && tz - P.pos < SEG * 80) P.warn = 1;
      if (!tr.hit && P.pos > tz - 150 && P.pos < tz + 900 && Math.abs(tr.x - P.x) < 1.18) {
        tr.hit = true; P.speed *= .05; P.stun = .8; P.shake = 1; P.flash = .8; P.hits++; sparks(2); SND.crash(1.3);
        addText('TRAMVAY!', [255, 90, 80]);
      }
    }
  }

  // --- Politsiya: masofa (gap) tezliklar farqiga qarab o'zgaradi
  const prog = P.pos / FINISH;
  let ps = c.max * (.66 + .14 * prog);
  if (P.gap > 4200) ps *= 1.18;
  ps = Math.min(ps, c.acc * .75 * P.t);                       // politsiya ham joyidan qo'zg'aladi
  P.gap = Math.min(9000, P.gap + (P.speed - ps) * dt);
  P.copX += (P.x - P.copX) * Math.min(1, dt * 1.5);
  if (P.gap < 260) return finish(false);
  if (P.pos >= FINISH) return finish(true);
}

function hit(sp) {
  switch (sp.t) {
    case 'crate':
      sp.dead = 1; P.speed *= .55; P.shake = .35; P.hits++;
      emit(16, { x: VIEW.cx, y: VIEW.cy - VIEW.cw * .3, sx: VIEW.cw * .5, vy: -u * 40, rvx: u * 70, rvy: u * 30, g: u * 120, s: u * 1.1, life: .9, col: [150, 108, 62], k: 'sq' });
      SND.crash(.5); break;
    case 'brief': {
      sp.dead = 1; const v = 1500 + (Math.random() * 4 | 0) * 500; P.money += v;
      addText('+$' + v.toLocaleString('en-US'), WARM); SND.blip(880, .12); SND.blip(1320, .1, 'sine', .1, .08); break;
    }
    case 'doc':
      sp.dead = 1; P.docs++; addText(`MAXFIY HUJJAT ${P.docs}/${DOCS}`, [120, 220, 255]);
      emit(10, { x: VIEW.cx, y: VIEW.cy - VIEW.cw * .4, sx: VIEW.cw * .3, vy: -u * 30, rvx: u * 40, rvy: u * 20, g: u * 20, s: u * 1, life: 1.2, col: [226, 206, 150], k: 'sq' });
      SND.blip(660, .2); SND.blip(990, .2, 'sine', .1, .1); break;
    default:
      if (sp.hitT && time - sp.hitT < .6) return;
      sp.hitT = time; P.speed *= .35; P.vx = (P.x < sp.x ? -1 : 1) * 1.6; P.x += (P.x < sp.x ? -1 : 1) * .05;
      P.shake = .7; P.flash = .5; P.hits++; sparks(1.2); SND.crash(1);
  }
}

function sparks(k) {
  emit(10 * k | 0, { x: VIEW.cx, y: VIEW.cy - VIEW.cw * .15, sx: VIEW.cw * .8, vy: -u * 20, rvx: u * 90, rvy: u * 50,
    g: u * 100, s: u * .5, life: .45, col: [255, 196, 110], k: 'spark' });
}

// Garaj ekranida fonda avtomatik harakat
function attract(dt) {
  P.speed = 5200; P.pos += P.speed * dt;
  P.x += (-segAt(P.pos).curve * .12 - P.x) * Math.min(1, dt * 2); P.steer = 0; P.yaw *= .9;
  if (P.pos > FINISH - 4000) P.pos = SEG * 6;
  for (const t of traffic) { t.z += t.sp * dt; if (t.z - P.pos < -4000) t.z = P.pos + 40000 + Math.random() * 20000; }
}

// Vizual effektlar holati: zarrachalar, yomg'ir, oynadagi tomchilar, chaqmoq
function fx(dt) {
  for (let i = parts.length - 1; i >= 0; i--) {
    const p = parts[i]; p.life -= dt;
    if (p.life <= 0) { parts.splice(i, 1); continue; }
    p.x += p.vx * dt; p.y += p.vy * dt; p.vy += p.g * dt; p.s += p.gs * dt; p.rot += p.vr * dt;
  }
  for (let i = texts.length - 1; i >= 0; i--) { const t = texts[i]; t.life -= dt; t.y -= u * 4 * dt; if (t.life <= 0) texts.splice(i, 1); }
  const pct = P.speed / CAR.max;
  for (const d of rain) {
    d.y += d.v * dt * (1 + pct * .5); d.x += (-.06 - P.steer * pct * .25) * dt;
    if (d.y > 1.05) { d.y = -.05 - Math.random() * .1; d.x = Math.random() * 1.2 - .1; }
    if (d.x < -.1) d.x += 1.2; if (d.x > 1.1) d.x -= 1.2;
  }
  if (cam === 2) {
    // Old oynadagi tomchilar va "dvornik"
    if (drops.length < 140 && Math.random() < dt * 30 * (1 + pct)) drops.push({ x: W * (.08 + Math.random() * .84), y: H * (.05 + Math.random() * .66), r: u * (.35 + Math.random() * .9), life: 3 + Math.random() * 3 });
    const ph = (time % 1.8) / 1.8; WIPER.prev = WIPER.a; WIPER.a = -Math.PI + Math.PI * .85 * Math.sin(ph * Math.PI);
    const px = W * .36, py = H * .76, len = Math.min(H * .66, W * .5);
    const a0 = Math.min(WIPER.prev, WIPER.a) - .03, a1 = Math.max(WIPER.prev, WIPER.a) + .03;
    for (let i = drops.length - 1; i >= 0; i--) {
      const d = drops[i]; d.life -= dt;
      d.y += (u * 5 - pct * u * 22) * dt * (d.r / u); d.x += (d.x - W / 2) / W * pct * u * 30 * dt;
      const ang = Math.atan2(d.y - py, d.x - px), dist = Math.hypot(d.x - px, d.y - py);
      if (d.life <= 0 || d.y < 0 || d.y > H * .74 || (ang > a0 && ang < a1 && dist < len)) drops.splice(i, 1);
    }
  }
  L.t -= dt;
  if (L.t <= 0) { L.flash = 1; L.t = 14 + Math.random() * 22; L.thunder = .7 + Math.random(); }
  if (L.thunder > 0) { L.thunder -= dt; if (L.thunder <= 0) SND.noise(1.8, .35, 160); }
  L.flash = Math.max(0, L.flash - dt * 2.2);
  P.shake = Math.max(0, P.shake - dt * 1.6); P.flash = Math.max(0, P.flash - dt * 2);
  skyX += segAt(P.pos).curve * pct * dt * u * 6;
  camXs += (P.x * ROAD - camXs) * Math.min(1, dt * 5);
}

// ===== Ovoz: dvigatel, yomg'ir, sirena (Web Audio, faqat tugma bosilgandan keyin) =====
const SND = {
  ac: null, master: null, on: true,
  init() {
    if (this.ac) { if (this.ac.state === 'suspended') this.ac.resume(); return; }
    try {
      const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return;
      const ac = this.ac = new AC(), m = this.master = ac.createGain();
      m.gain.value = this.on ? .55 : 0; m.connect(ac.destination);
      const f = this.ef = ac.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = 700;
      const eg = this.eg = ac.createGain(); eg.gain.value = 0; f.connect(eg); eg.connect(m);
      const o1 = this.o1 = ac.createOscillator(); o1.type = 'sawtooth';
      const o2 = this.o2 = ac.createOscillator(); o2.type = 'square';
      const g2 = ac.createGain(); g2.gain.value = .4; o1.connect(f); o2.connect(g2); g2.connect(f); o1.start(); o2.start();
      const nb = this.nb = ac.createBuffer(1, ac.sampleRate * 2, ac.sampleRate), d = nb.getChannelData(0);
      for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
      const rn = ac.createBufferSource(); rn.buffer = nb; rn.loop = true;
      const bf = ac.createBiquadFilter(); bf.type = 'bandpass'; bf.frequency.value = 2200; bf.Q.value = .5;
      const rg = ac.createGain(); rg.gain.value = .07; rn.connect(bf); bf.connect(rg); rg.connect(m); rn.start();
      const so = this.so = ac.createOscillator(); so.type = 'triangle';
      const sg = this.sg = ac.createGain(); sg.gain.value = 0; so.connect(sg); sg.connect(m); so.start();
    } catch (e) { this.ac = null; }
  },
  update(rpm, load, siren) {
    if (!this.ac) return;
    const t = this.ac.currentTime, play = mode === 'play';
    this.o1.frequency.setTargetAtTime(32 + rpm * 14, t, .05);
    this.o2.frequency.setTargetAtTime(16 + rpm * 7, t, .05);
    this.ef.frequency.setTargetAtTime(400 + rpm * 120 + load * 600, t, .08);
    this.eg.gain.setTargetAtTime(play ? .05 + load * .05 : 0, t, .1);
    this.sg.gain.setTargetAtTime(play ? siren * .045 : 0, t, .1);
    this.so.frequency.setTargetAtTime(Math.floor(t * 2.4) % 2 ? 640 : 860, t, .03);
  },
  blip(f, d, type = 'sine', v = .15, delay = 0) {
    if (!this.ac) return;
    const t = this.ac.currentTime + delay, o = this.ac.createOscillator(), g = this.ac.createGain();
    o.type = type; o.frequency.value = f; g.gain.setValueAtTime(v, t); g.gain.exponentialRampToValueAtTime(.001, t + d);
    o.connect(g); g.connect(this.master); o.start(t); o.stop(t + d + .02);
  },
  noise(d, v, freq) {
    if (!this.ac) return;
    const t = this.ac.currentTime, s = this.ac.createBufferSource(), f = this.ac.createBiquadFilter(), g = this.ac.createGain();
    s.buffer = this.nb; f.type = 'lowpass'; f.frequency.value = freq;
    g.gain.setValueAtTime(v, t); g.gain.exponentialRampToValueAtTime(.001, t + d);
    s.connect(f); f.connect(g); g.connect(this.master); s.start(t, Math.random()); s.stop(t + d + .05);
  },
  crash(v) { this.noise(.35, .5 * v, 900); this.blip(70, .25, 'square', .2 * v); },
  bell() { this.blip(1180, .5, 'sine', .12); this.blip(1180, .5, 'sine', .12, .28); },
  toggle() { this.on = !this.on; if (this.master) this.master.gain.value = this.on ? .55 : 0; },
};
