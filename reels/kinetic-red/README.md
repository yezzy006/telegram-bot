# Kinetic Red — birbalo_ai reel shabloni

Kod bilan yig‘iladigan vertikal (1080×1920) kinetik-tipografiya reel. Birinchi marta
"Claude'ga 3 ta yangi skill" videosi uchun qilingan (13.10.2026, 6-versiya Odiljonga yoqdi).
Seedance/Higgsfield krediti ketmaydi — faqat ElevenLabs ovozi.

## Uslub
- To‘liq ekran 9:16, noutbuk/xona YO‘Q (reference video shunchaki ekrandan suratga olingan edi).
- Ranglar: qora + qizil `#ff2e2a` + oq. Fonlar navbatma-navbat: `k` qora-qizil nur, `w` oq, `r` qizil, `g` qora to‘r.
- Shrift: Archivo 900, kenglik 125% (`fonts/`), hammasi KATTA harf.
- Bitta jumla = bitta sahna; so‘zlar ovozga mos o‘z joyiga qo‘shiladi.
- Harflar alohida kiradi: `pop` (blur+kattalashib), `rise` (pastdan aylanib), `type` (qizil blok bilan),
  so‘z bo‘yicha: `slam`, `glitch`, `fill` (kontur → to‘la).
- Har sahnada chizma: oyna (`WIN`), kartalar, qizil tugun, SVG chiziqlar, 3D kub, X, muhr (`stamp`), fayl ikonkalari.
- Sahnalar orasida whip (blur + surilish + aylanish).
- **Temp (eng muhimi):** har bir yangi so‘z/element kelganda butun kadr zarba oladi (zoom + silkinish),
  kamera doim suriladi/aylanadi, elementlar suzib turadi. Maqsad: o‘zgarish har ~0.6 s, qotgan kadr <20%.
  Tekshirish: `python3 motion.py out.mp4 "" 0 36 mine` (reference: har 0.64 s, qotgan 4%).
- Effekt ovozi faqat kerakli joyda: sahna almashganda whoosh, asosiy so‘zlarda zarba, glitch’da chiqillash. Musiqa yo‘q
  (Odiljon Instagram’da o‘zi qo‘shadi).
- `@birbalo_ai × @andijon.kuryer` tegi pastda (y≈1505), matn 250 px yuqori / 350 px pastki zonadan tashqarida.

## Ish tartibi
1. Ssenariy (o‘zbekcha, ~35–40 s) → Odiljonga ko‘rsat.
2. Ovoz: ElevenLabs, ovoz **"Odiljon - birbalo.ai"** (`uYEt3VyWxTQSZ0l7Edrl`), model **`eleven_v4`**
   (v3 uning ovoziga o‘xshamaydi!), `generations_count=1`, avval `estimate_only`.
   Ovoz matnida "Claude" → "Klod", "skill" → "skil", "ChatPlace" → "Chatpleys", "Flow" → "Flou".
3. So‘z vaqtlari: ElevenLabs `creative_transcribe_audio` (scribe, 0 kredit). (Bulutda faster-whisper modeli HF proksida bloklangan.)
4. Ovozni tezlashtirish: `ffmpeg -i voice.mp3 -af atempo=1.12 voice_fast.wav`.
   `index.html` dagi barcha vaqtlar **asl ovoz** sekundida yoziladi; `RATE=1.12` o‘zi hisoblaydi.
5. `index.html` → `SC` massivini yangi ssenariy bo‘yicha yoz: `[boshlanish, fon, [L(y, W(...)), I(x,y,at,anim,html), ...]]`.
   `W(matn, vaqt, o‘lcham, klass, rejim)`, `L(y, ...so‘zlar)` (avtomatik 900 px ga sig‘diriladi), `I(x,y,vaqt,"pop|up|stamp",html)`.
6. Kontakt varaq: `HTML=index.html python3 render.py . sheet 1,5,9,...` → `sheet_*.png` ni ko‘rib chiq.
7. SFX: `sfx.py` dagi `SCENES` va zarba vaqtlarini yangila → `python3 sfx.py` → `sfx.wav`.
8. Miks: `ffmpeg -i voice_fast.wav -i sfx.wav -filter_complex "[1:a]volume=0.5[s];[0:a][s]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5" audio.wav`
9. Render (~9 daqiqa, fonda ishga tushir, `timeout` qo‘yma): `AUDIO=audio.wav CHROME=/opt/pw-browsers/chromium-1194/chrome-linux/chrome python3 render.py . full`
   → `out.mp4`; yuborish uchun siq: `ffmpeg -i out.mp4 -c:v libx264 -crf 23 -preset slow -maxrate 7M -bufsize 14M -c:a copy final.mp4` (30 MB dan kichik).

Kerakli paketlar: `pip install playwright scipy numpy`, ffmpeg.
