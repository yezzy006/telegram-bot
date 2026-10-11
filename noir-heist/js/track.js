'use strict';
// ===== 2. Shahar ko'chasini yaratish: segmentlar, binolar, chiroqlar, to'siqlar =====
// Yo'l SEG uzunlikdagi segmentlardan iborat. Har segmentda: burilish (curve), yon binolar,
// yoritilganlik, ko'lmak va spritelar (chiroq, quti, diplomat ...).
function buildTrack(seed) {
  const R = rng(seed);
  segs = []; trams = []; traffic = [];
  const add = c => segs.push({ i: segs.length, curve: c, spr: [], light: 0, lt: [0, 0], pud: null, cross: -1, near: 0, wall: [null, null], shop: [0, 0] });
  const road = (e, h, l, c) => {
    for (let i = 0; i < e; i++) add(c * easeIn(i / e));
    for (let i = 0; i < h; i++) add(c);
    for (let i = 0; i < l; i++) add(c * (1 - easeInOut(i / l)));
  };
  road(0, 90, 0, 0);
  while (segs.length < 5200) {
    if (R() < .38) road(0, 50 + R() * 90 | 0, 0, 0);
    else { const c = (R() < .5 ? -1 : 1) * (1.6 + R() * 3.4); road(25 + R() * 30 | 0, 20 + R() * 60 | 0, 25 + R() * 30 | 0, c); }
  }
  road(0, 280, 0, 0);
  N = segs.length; FINISH = (N - 62) * SEG;

  // Tramvay chorrahalari faqat to'g'ri qismlarda
  for (let i = 420; i < N - 420;) {
    let ok = true;
    for (let j = i - 8; j <= i + 10; j++) if (segs[j].curve !== 0) { ok = false; break; }
    if (ok) {
      for (let j = i - 3; j <= i + 6; j++) segs[j].cross = i;
      for (let j = i - 14; j <= i + 16; j++) segs[j].near = 1;
      trams.push({ c: i, x: 0, vx: 0, st: 0, side: R() < .5 ? -1 : 1, hit: false });
      i += 520 + R() * 260 | 0;
    } else i += 7;
  }

  // Binolar bloklari (har ikki tomonda)
  for (let sd = 0; sd < 2; sd++) {
    let i = 0;
    while (i < N) {
      const len = 9 + R() * 15 | 0, sh = R() < .6 ? SHOPS[R() * SHOPS.length | 0] : null;
      const blk = { h: 2.1 + R() * 1.7, col: BRICKS[R() * BRICKS.length | 0], shop: sh, start: i, len,
                    awn: AWN[R() * AWN.length | 0], neon: NEON[R() * NEON.length | 0], seed: R() * 1000 };
      for (let j = i; j < i + len && j < N; j++) if (segs[j].cross < 0) segs[j].wall[sd] = blk;
      if (sh) {
        const j = i + 2, x = sd ? 1 : -1;
        if (j < N - 70 && segs[j].cross < 0)
          segs[j].spr.push(MARQUEE.has(sh) ? { t: 'marq', x: x * 1.25, w: .42, text: sh, col: blk.neon }
                                           : { t: 'blade', x: x * 1.43, w: .13, text: sh, col: blk.neon });
        for (let j2 = i + 1; j2 < i + len - 1 && j2 < N; j2++) if (segs[j2].cross < 0) segs[j2].shop[sd] = 1;
      }
      i += len + (R() < .3 ? 1 + (R() * 2 | 0) : 0);
    }
  }

  // Ko'cha fonuslari va ularning yorug'lik dog'lari
  for (let i = 8; i < N - 62; i += 13) for (let sd = 0; sd < 2; sd++) {
    const j = i + sd * 6;
    if (j >= N || segs[j].cross >= 0) continue;
    segs[j].spr.push({ t: 'lamp', x: (sd ? 1 : -1) * 1.13, w: .07, col: 1 });
    for (let d = -7; d <= 7; d++) {
      const s = segs[j + d]; if (!s) continue;
      s.lt[sd] = Math.max(s.lt[sd], (1 - Math.abs(d) / 7) ** 2);
    }
  }
  for (const s of segs) {
    for (let sd = 0; sd < 2; sd++) if (s.shop[sd]) s.lt[sd] = Math.max(s.lt[sd], .5);
    s.light = Math.max(s.lt[0], s.lt[1]) * .75;
  }

  // Trotuar bezaklari: piyodalar, telefon budkalari, gidrantlar
  for (let i = 20; i < N - 70; i++) {
    const s = segs[i]; if (s.cross >= 0) continue;
    for (let sd = 0; sd < 2; sd++) {
      const x = sd ? 1 : -1, r = R();
      if (r < .035) s.spr.push({ t: 'ped', x: x * (1.43 + R() * .04), w: .12, umb: R() < .45, ph: R() * 6 });
      else if (r < .041) s.spr.push({ t: 'booth', x: x * 1.33, w: .17, col: 1 });
      else if (r < .05) s.spr.push({ t: 'hydrant', x: x * 1.07, w: .06, col: 1 });
    }
  }

  // O'yin obyektlari: qutilar, to'xtab turgan mashinalar, diplomatlar, ko'lmaklar
  for (let i = 110; i < N - 300; i++) {
    const s = segs[i]; if (s.near) continue;
    const t = i / N, r = R();
    if (R() < .045) s.pud = { x: -.8 + R() * 1.6, w: .28 + R() * .4 };
    if (r < .016 + .022 * t) {
      const x = -.72 + R() * 1.44;
      s.spr.push({ t: 'crate', x, w: .22, col: 1 });
      if (R() < .45) s.spr.push({ t: 'crate', x: x + (x > 0 ? -.24 : .24), w: .22, col: 1 });
      i += 4; continue;
    }
    if (r < .03 + .03 * t) { s.spr.push({ t: 'parked', x: (R() < .5 ? -1 : 1) * .8, w: .4, col: 1, c: TRAFFIC_COL[R() * 6 | 0] }); i += 6; continue; }
    if (r < .06 + .03 * t) s.spr.push({ t: 'brief', x: -.82 + R() * 1.64, w: .16, col: 1, ph: R() * 6 });
  }
  // Maxfiy hujjatlar: 12 dona, teng taqsimlangan
  DOCS = 0;
  const step = Math.floor((N - 600) / 12);
  for (let d = 0; d < 12; d++) {
    let i = 300 + d * step; while (segs[i].near) i++;
    segs[i].spr.push({ t: 'doc', x: -.7 + R() * 1.4, w: .15, col: 1, ph: R() * 6 }); DOCS++;
  }
  segs[N - 62].spr.push({ t: 'safe', x: 0, w: 3.2 });

  // Oqimdagi 1940-yillar mashinalari
  for (let k = 0; k < 14; k++)
    traffic.push({ z: 9000 + k * (FINISH / 14) + R() * 3000, x: R() < .5 ? -.4 : .4, sp: 3800 + R() * 2600, c: TRAFFIC_COL[R() * 6 | 0] });

  // Mini-xarita uchun marshrut chizig'i
  route = []; let hd = 0, px = 0, py = 0, x0 = 0, x1 = 0, y0 = 0, y1 = 0;
  for (let i = 0; i < N; i++) {
    hd += segs[i].curve * .0022; px += Math.sin(hd); py += Math.cos(hd);
    if (i % 8 === 0) { route.push([px, py]); x0 = Math.min(x0, px); x1 = Math.max(x1, px); y0 = Math.min(y0, py); y1 = Math.max(y1, py); }
  }
  routeBox = { x0, x1, y0, y1 };
}
