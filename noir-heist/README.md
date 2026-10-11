# CYBER-SPRINT: NOIR HEIST 1940

1940-yillar retro-noir uslubidagi arkada poyga o'yini. HTML5 Canvas 2D'da yozilgan psevdo-3D dvigatelda ishlaydi. Kutubxona, server yoki API kerak emas.

**Ishga tushirish:** `noir-heist/index.html` faylini brauzerda oching.

## Boshqaruv

| Amal | Klaviatura | Telefon |
|---|---|---|
| Rul | ← → yoki A / D | ◀ ▶ |
| Gaz | ↑ yoki W | avtomatik |
| Tormoz | ↓ yoki S | TORMOZ |
| Qo'l tormozi (drift) | SPACE | DRIFT |
| Nitro | SHIFT yoki N | NITRO |
| Kamera / pauza / ovoz | C / P / M | yuqoridagi tugmalar |

## O'yin

- **Maqsad:** politsiya sizga yetib olishidan oldin yo'l oxiridagi SAFEHOUSE garajiga yetib borish.
- **Ta'qib masofasi:** har bir to'qnashuv tezlikni pasaytiradi. Shunda politsiya yaqinlashadi va masofa 10 m dan kam bo'lsa, qo'lga tushasiz.
- **Yig'iladigan narsalar:** pul solingan diplomatlar ($1 500 – $3 000) va 12 ta maxfiy hujjat (har biri 5 000 ball).
- **To'siqlar:** yog'och qutilar, to'xtab turgan mashinalar, fonus ustunlari, telefon budkalari, oqimdagi 1940-yillar mashinalari va chorrahada yo'lni kesib o'tadigan tramvaylar.
- **Mashinalar:** Neo-9 (tezlik 95, boshqaruv 92), Vanguard V-8 1942 (tezlanish 91), Phantom Roadster 1948 (boshqaruv 95). Xarakteristikalar to'g'ridan-to'g'ri fizikaga ulangan.
- **Kameralar:** orqadan kuzatish, yuqoridan ko'rinish va salon ichidan ko'rinish (yog'och rul, dvornik, oynadagi tomchilar, orqani ko'rish oynasidagi sirena).

## Kod tuzilishi

| Fayl | Vazifasi |
|---|---|
| `js/core.js` | Yordamchi funksiyalar, palitra, mashina xarakteristikalari, umumiy holat |
| `js/track.js` | Ko'cha generatori: burilishlar, binolar bloklari, do'kon neonlari, fonuslar, to'siqlar, tramvay chorrahalari |
| `js/physics.js` | Fizika, to'qnashuvlar, politsiya, effektlar va ovoz (Web Audio) |
| `js/cars.js` | Mashinalarni orqadan va yuqoridan chizish |
| `js/sprites.js` | Ko'cha obyektlari: fonus, quti, diplomat, hujjat, neon yozuvlar, tramvay, safehouse |
| `js/street.js` | Psevdo-3D render, osmon va shahar silueti, yomg'ir, salon ichidan ko'rinish |
| `js/topdown.js` | Yuqoridan ko'rinish (binolar balandligi qiya siljish bilan beriladi) |
| `js/hud.js` | Ta'qib paneli, mini-xarita, mexanik spidometrlar, kino effektlari |
| `js/main.js` | O'yin sikli, ekranlar, klaviatura va sensorli boshqaruv |

### O'yin sikli

`requestAnimationFrame` → `update(dt)` → `render()`. Bitta kadr uchun `dt` 50 ms bilan cheklangan, shuning uchun sekin qurilmada ham fizika "sakramaydi".

### Ho'l tosh yo'l fizikasi (drift)

Mashinaning ko'ndalang tezligi `vx` rul ko'rsatgan nishonga darhol emas, **grip** tezligida yaqinlashadi:

```
vx += (target - vx) * grip * dt
x  += (vx - markazdan_qochma) * dt
```

- Ho'l tosh yo'lda grip 0.78 ga ko'paytiriladi, tramvay relslarida yana ×0.6, ko'lmakda (akvaplaning) ×0.25.
- Qo'l tormozi gripni ×0.33 gacha tushiradi. Mashina sirpanadi, burilishdagi markazdan qochma kuch esa 55% ga kamayadi. Bu drift.
- Drift nitro to'playdi, uzoq drift esa pul bonusi beradi.

### To'qnashuvlar

Har kadrda mashina o'tib ketgan **barcha** segmentlar tekshiriladi. Shuning uchun yuqori tezlikda ham obyekt "sakrab o'tilmaydi". Ko'ndalang kesishish: `|x1 - x2| < (w1 + w2) / 2`. Tramvay o'yinchi yaqinlashganda ishga tushadi. Uning tezligi o'yinchi chorrahaga yetib keladigan paytga moslab hisoblanadi.

### Render

Klassik psevdo-3D: har bir segment `scale = DEPTH / z` bilan ekranga proyeksiya qilinadi, burilishlar esa yig'iladigan `x` siljishi bilan beriladi. Segmentlar uzoqdan yaqinga qarab chiziladi: devorlar va derazalar, trotuar, toshlar, akslar, keyin spritelar. Fonus va neonlarning nam yo'ldagi vertikal akslari keyingi 8 segmentga bo'lib chiziladi, shuning uchun yaqindagi segmentlar ularni yopib qo'ymaydi.
