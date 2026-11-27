# Qamchiqqa Qochish

Brauzerda ishlaydigan 3D o'yin: haqiqiy A373 yo'li bo'ylab Andijondan Qamchiq dovonigacha YHXB quvayotgan holda yetib borish.

**Ishga tushirish:** o'yin `route.json` faylini yuklaydi, shuning uchun uni oddiy fayl sifatida emas, kichik server orqali oching:

```
cd qamchiq && python3 -m http.server 8000
# keyin brauzerda: http://localhost:8000
```

**Boshqaruv:** ← → / A D — rul (birinchi versiyadagidek tez), ↑ / W — gaz, ↓ / S — tormoz, Probel — qo'l tormozi (drift), C — kamera (salon, orqadan, kapot). Telefonda ekrandagi tugmalar; salon ko'rinishida yon va orqa ko'zgular ekranda chiqadi. Telefonni yotqizib o'ynash qulayroq.

**Qoidalar**
- GAI urmaydi: to'liq tezlikda undan uzoqlasha olasan. To'xtab qolsang (avariya, tirbandlik, post) va GAI yaqin bo'lsa, inspektor mashinadan tushib, yugurib kelib ushlaydi.
- Menyuda mashinangni tanlaysan: Cobalt, Gentra yoki Nexia 3 va rangi.
- Mashinalarga urilish shikast beradi; 100% bo'lsa mashina ishdan chiqadi.
- Radar oldidan 100 km/h dan tez o'tsang, qidiruv darajasi oshadi.
- Yo'l o'rtasida beton to'siq bor (OSM bo'yicha ajratilgan yo'lda); burilish joylarida va YHXB postlari oldida u bo'lmaydi.

**Haqiqiy yo'l (`route.json`)**
- Yo'l chizig'i: OpenStreetMap (A373, © OpenStreetMap hissadorlari, ODbL). Relyef: NASA SRTM 1″.
- Ikki qism, 1:1 o'lchamda: Andijondan chiqish (5 km) va Qamchiq dovoniga ko'tarilish (14 km, 1588 → 2187 m, 416 m lik Qamchiq tunneli bilan). Oradagi ~180 km (Shahrixon, Bo'ston, Yozyovon) o'tish ekrani bilan qisqartirilgan.
- Qayta yaratish: `python3 tools/build_route.py --osm a373.json --dem SRTM_PAPKA --places places.json --out route.json` (so'rovlar skript ichida yozilgan).

**Bosqichlar**
1. ✅ Salon ko'rinishi (rul, spidometr, taxometr, ko'zgular), GAI quvish rejimi.
2. ✅ Mashinalar: Cobalt, Nexia, Spark, Damas, Malibu, fura; fizika: shina sirpanishi, og'irlik ko'chishi, 6 bosqichli avtomat uzatma, qo'l tormozi, tutun.
3. ✅ Haqiqiy yo'l, relyef, tunnel, beton to'siq, yo'l bo'yidagi shahar nomlari.
