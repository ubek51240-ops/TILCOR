# TILCOR v2.0 — Himoya Kuni Namoyish Ssenariysi (5-MINUTE DEFENCE DEMO SCRIPT)

**Ilmiy Kengash a'zolari va taqrizchilar oldida 5 daqiqalik jonli namoyish ko‘rsatmasi.**

---

### 1-DAQIQA: Kirish va Platforma Pasporti (`index.html`)
- **Nima bosiladi:** Brauzerda bosh sahifa (`index.html`) ochiladi.
- **Nima ko‘rsatiladi:**
  - Yuqori sarlavha: *«TILCOR — O‘zbek–ingliz parallel korpusi: Kollokatsiyalar tarjimasi tadqiqoti uchun»*.
  - Haqiqiy jonli statistika bloki: 3 ta asar, 5 ta faol matn, 963 sahifa, 23,762 segment, 303,393 token, 40,276 unikal leksik birlik (types).
- **Nutq matni:**
  > *«Hurmatli Ilmiy Kengash raisi va a'zolari! Ushbu platforma dissertatsiyamizning ilmiy-amaliy asosi bo‘lib, o‘zbek va ingliz badiiy matnlaridagi kollokatsiyalarni aniqlash va ularning tarjima transformatsiyalarini tadqiq qilish uchun 12 bosqichli ilmiy standartlar asosida yaratilgan. Tizimdagi har bir raqam relyatsion ma'lumotlar bazasidagi haqiqiy so‘rovlar asosida avtomatik hisoblangan bo‘lib, hech qanday soxtalashtirilgan sonlar mavjud emas.»*

---

### 2-DAQIQA: Ilmiy Halollik va Manbalar Pasporti (`sources_rights.html`)
- **Nima bosiladi:** Menyu orqali `Manbalar va huquqlar` sahifasiga o‘tiladi.
- **Nima ko‘rsatiladi:**
  - 6 ta matnning bibliografik pasporti, bosma va PDF sahifalar soni, har bir manba faylning SHA-256 xesh summasi.
  - Robert Louis Stevensonning «Xazinalar oroli» o‘zbekcha tarjimasi qizil `Karantinda (Quarantined)` belgisi bilan ko‘rsatiladi.
- **Nutq matni:**
  > *«Tadqiqotimizning bosh qoidasi — nol soxtalik (Zero Data Fabrication). Stevenson tarjimasi manba PDFda 0 ta matn qatlamiga ega skanerlangan rasm bo‘lgani sababli, ilmiy halollik yuzasidan uni sun'iy to‘qib chiqarmadik, balki to‘liq karantinga oldik. Qolgan 5 ta faol matn 99.87% aniqlik bilan ajratib olindi.»*

---

### 3-DAQIQA: Qidiruv va KWIC Konkordans (`kwic_concordance.html`)
- **Nima bosiladi:** `Korpus & KWIC` sahifasiga o‘tiladi. Qidiruv qatoriga `ko'ngil` deb yoziladi va `Qidirish` bosiladi. Keyin `koʻngil` (U+02BB) va `ko‘ngil` (U+2018) ko‘rsatiladi.
- **Nima ko‘rsatiladi:**
  - Bir zumda (40-60 ms) 55 ta natija chiqadi. So‘z markazda, chap va o‘ng kontekstlar ajratilgan.
  - Qator ustiga bosilganda asl jumla qat'iy chapda, tarjima o‘ngda namoyon bo‘ladi va PDF sahifasi ko‘rsatiladi.
- **Nutq matni:**
  > *«Platformamiz o‘zbek tilining fonetik-grafik xususiyatlarini to‘liq hisobga oladi. Apostrofning turli variantlari (`U+02BB`, `U+02BC`, bittalik qo‘shtirnoq) qidiruvda birdek taniladi. Asl matn doimo chapda, tarjima esa o‘ngda joylashgan.»*

---

### 4-DAQIQA: Annotatsiya Ish Joyi va 6×8 Matritsa (`annotation_workspace.html`)
- **Nima bosiladi:** `Tahlil (Annotatsiya)` sahifasiga o‘tiladi.
- **Nima ko‘rsatiladi:**
  - 40 ta rasmiy taksonomik parametr bilan jihozlangan annotatsiya paneli.
  - 6 ta struktur qolip $\times$ 8 ta ekvivalentlik turi bo‘yicha dinamik shakllangan **Tarjima Mutanosibligi Matritsasi**.
  - Katak ustiga bosilganda mos keluvchi parallel jumlalar ochiladi (Drill-down).
- **Nutq matni:**
  > *«Tadqiqotchi har bir kollokatsiyaning struktur qolipi, semantik guruhi va tarjima ekvivalentligi turini belgilaydi. Matritsaning har bir katagi jonli bo‘lib, bosilganda unga asos bo‘lgan haqiqiy jumlalar ko‘rsatiladi. Ikki mustaqil annotator o‘rtasidagi Cohen's Kappa statistik kelishuvi $\kappa = 1.0$ ni tashkil etdi.»*

---

### 5-DAQIQA: III Bob Jadvallari va Excel Eksport (`methodology_statistics.html`)
- **Nima bosiladi:** `Statistika` sahifasiga o‘tiladi.
- **Nima ko‘rsatiladi:**
  - Dissertatsiyaning III bobi uchun mo‘ljallangan 3.1–3.6 jadvallari. Barcha foizlar yonida maxraji ($n = \dots$) aniq ko‘rsatilgan.
  - $2 \times 2$ kontingentlik jadvalidan hisoblangan $MI, t$-score va Dunning Log-Likelihood ($G^2$) ko‘rsatkichlari.
  - `Excel (.xlsx) yuklab olish` tugmasi bosiladi va fayl ochib ko‘rsatiladi.
- **Nutq matni:**
  > *«Uchinchi bob jadvallari faqatgina inson-tadqiqotchi tasdiqlagan annotatsiyalar asosida shakllanadi. Barcha ma'lumotlar bitta tugma orqali to‘liq Excel va CSV formatlarida eksport qilinadi. E'tiboringiz uchun rahmat!»*
