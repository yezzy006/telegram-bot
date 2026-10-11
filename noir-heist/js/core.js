'use strict';
// ===== 1. Asosiy yordamchilar, konstantalar va umumiy holat =====
const $ = id => document.getElementById(id);
const cv = $('game'), ctx = cv.getContext('2d');
const clamp = (v, a, b) => v < a ? a : v > b ? b : v;
const lerp = (a, b, t) => a + (b - a) * t;
const hash = (a, b) => { const s = Math.sin(a * 127.1 + b * 311.7) * 43758.5453; return s - Math.floor(s); };
function rng(seed) {
  let a = seed >>> 0;
  return () => { a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
}
const mix = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
const rgb = (c, al) => al == null ? `rgb(${c[0] | 0},${c[1] | 0},${c[2] | 0})` : `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${al})`;
const easeIn = t => t * t, easeInOut = t => -Math.cos(Math.PI * t) / 2 + .5;

// Dunyo o'lchamlari: ROAD = yo'lning yarim kengligi. x koordinatalari shu birlikda (-1..1 = yo'l).
const ROAD = 2000, SEG = 200, DEPTH = 1 / Math.tan(50 * Math.PI / 180);

// Rang palitrasi (retro-noir)
const FOG = [48, 52, 62], GROUND = [20, 22, 27], LAMP = [255, 184, 96], WARM = [255, 204, 128];
const COBBLE = [[52, 52, 58], [44, 44, 50]], SIDEWALK = [66, 64, 66], CURB = [100, 98, 95];
const BRICKS = [[92, 40, 34], [74, 36, 32], [64, 58, 58], [86, 62, 46], [54, 46, 48], [98, 52, 38]];
const AWN = [[150, 40, 40], [40, 90, 70], [40, 60, 110], [140, 110, 40]];
const NEON = [[255, 176, 64], [255, 84, 72], [96, 212, 255], [255, 112, 184], [130, 255, 160]];
const SHOPS = ['TAILOR', 'BARBER', 'GRAND CINEMA', 'HOTEL', 'JAZZ CLUB', 'DINER', 'PAWN', 'DRUGS', 'BAR', 'RADIO', 'MEBEL', 'BAKERY', 'TICKETS', 'SHOES', 'CAFE'];
const MARQUEE = new Set(['GRAND CINEMA', 'HOTEL', 'JAZZ CLUB', 'TICKETS']);
const TRAFFIC_COL = [[24, 24, 28], [38, 52, 44], [86, 30, 34], [196, 186, 160], [34, 40, 62], [70, 64, 58]];

// Mashinalar: xarakteristikalar fizikaga aylantiriladi (tune)
const CARS = [
  { id: 'neo', name: 'Neo-9', year: 'Retro-mod', desc: "Zamonaviy aerodinamik siluet, 40-yillar sarg'ish optikasi. Eng chaqqon.", speed: 95, accel: 88, handling: 92, body: [58, 60, 66], trim: [242, 182, 44] },
  { id: 'van', name: 'Vanguard V-8', year: '1942', desc: "Ulkan xrom panjarali to'q qizil hot-rod. To'g'ri yo'lda eng kuchli.", speed: 89, accel: 91, handling: 82, body: [112, 26, 36], trim: [214, 214, 206] },
  { id: 'pha', name: 'Phantom Roadster', year: '1948', desc: "Simli disklar, ochiq salon, yengil korpus. Burilishlar ustasi.", speed: 93, accel: 85, handling: 95, body: [26, 74, 50], trim: [226, 220, 200] },
];
for (const c of CARS) {
  c.max = 6000 + c.speed * 80;              // maksimal tezlik (birlik/s)
  c.acc = c.max / (9 - c.accel * 0.06);     // tezlanish
  c.steer = 1.5 + c.handling * 0.012;       // rul kuchi (yo'l kengligi/s)
  c.grip = 2.2 + (c.handling - 80) * 0.22;  // shinalar ilashishi
}

// O'yin holati
let segs = [], N = 0, FINISH = 0, trams = [], traffic = [], DOCS = 0, route = [], routeBox = null;
const P = {};
let CAR = CARS[0], carIdx = 0, mode = 'garage', cam = 0, camXs = 0, skyX = 0, time = 0;
const K = { left: 0, right: 0, gas: 0, brake: 0, hb: 0, nitro: 0 };
let touchMode = matchMedia('(pointer: coarse)').matches;
const parts = [], texts = [], rain = [], drops = [];
const L = { t: 9, flash: 0, thunder: 0 };
const WIPER = { a: -Math.PI, prev: -Math.PI };
const V = { hor: 0, camH: 0, camZ: 0, camX: 0 };       // joriy kamera
const VIEW = { cx: 0, cy: 0, cw: 0 };                  // o'yinchi mashinasining ekrandagi joyi
let W = 0, H = 0, U = 0, u = 0, DPR = 1, DRAW = 160, ST = 0;

const segAt = z => segs[clamp(Math.floor(z / SEG), 0, N - 1)];

function quad(x1, y1, x2, y2, x3, y3, x4, y4, col) {
  ctx.fillStyle = col; ctx.beginPath();
  ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.lineTo(x3, y3); ctx.lineTo(x4, y4); ctx.closePath(); ctx.fill();
}
function rr(g, x, y, w, h, r) {
  r = Math.min(r, w / 2, h / 2); g.beginPath();
  g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath();
}
function ell(g, x, y, rx, ry) { g.beginPath(); g.ellipse(x, y, Math.max(.1, rx), Math.max(.1, ry), 0, 0, Math.PI * 2); }

// Oldindan chizilgan yorug'lik "glow" teksturalari (har rang uchun bitta)
const GLOWS = new Map();
function glowTex(col) {
  const key = col.join(',');
  let c = GLOWS.get(key);
  if (!c) {
    c = document.createElement('canvas'); c.width = c.height = 64;
    const g = c.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    gr.addColorStop(0, rgb(col, 1)); gr.addColorStop(.25, rgb(col, .45)); gr.addColorStop(1, rgb(col, 0));
    g.fillStyle = gr; g.fillRect(0, 0, 64, 64); GLOWS.set(key, c);
  }
  return c;
}
function glow(g, x, y, rx, ry, col, a) {
  if (a <= 0.01 || rx < 1) return;
  g.globalCompositeOperation = 'lighter'; g.globalAlpha = Math.min(1, a);
  g.drawImage(glowTex(col), x - rx, y - ry, rx * 2, ry * 2);
  g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
}

// Zarrachalar va suzuvchi yozuvlar
function emit(n, o) {
  for (let i = 0; i < n && parts.length < 420; i++) parts.push({
    x: o.x + (Math.random() - .5) * (o.sx || 0), y: o.y + (Math.random() - .5) * (o.sy || 0),
    vx: (o.vx || 0) + (Math.random() - .5) * (o.rvx || 0), vy: (o.vy || 0) + (Math.random() - .5) * (o.rvy || 0),
    g: o.g || 0, s: o.s || u * .4, gs: o.gs || 0, life: o.life * (.6 + Math.random() * .6), max: o.life,
    col: o.col, a: o.a == null ? 1 : o.a, k: o.k || 'dot', rot: Math.random() * 6, vr: (Math.random() - .5) * 10,
  });
}
function addText(s, col) { texts.push({ s, col: col || WARM, x: W / 2, y: H * .36, life: 1.6 }); }
