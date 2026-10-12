# TILCOR v2.0 — O‘zgarishlar Jurnali (CHANGELOG.md)

Ushbu hujjat doktorlik dissertatsiyasi talablari doirasida har bir bosqichda kiritilgan o‘zgarishlarning to‘liq audit izini aks ettiradi.

## [Stage 9] — Qidiruv, KWIC va Eksport (Search, KWIC and Export) — 2026-10-12

### 1. KWIC (Key Word in Context) Konkordans Dvigateli
- `scripts/stage9_backend.py` va `kwic_concordance.html` yaratildi.
- So‘z markazda vizual ajratilgan, chap va o‘ng kontekstlar ($\pm 1$ dan $\pm 10$ gacha) ajratilgan holda ko‘rsatiladi.
- 3 ta saralash mexanizmi joriy etildi: matndagi ketma-ketlik, chap kontekst bo‘yicha alifbo tartibi, o‘ng kontekst bo‘yicha alifbo tartibi.
- Har bir natija bosilganda to‘liq parallel jumla va tegishli PDF sahifa raqami (`pdf_page_num`) namoyon bo‘ladi.
- Ko‘p so‘zli iboralar (`old man` kabi) va yakka leksemalar (`yurak`, `baliq`) to‘liq qo‘llab-quvvatlandi.
- Katta hajmli so‘rovlarda ham so‘rov tezligi sub-50 ms doirasida ishlashi ta'minlandi.

### 2. Tutuq Belgisi va Apostrofga Sezgirmaslik (Rule R8)
- SQLite uchun `NORM_APO` maxsus funksiyasi ro‘yxatdan o‘tkazildi.
- `ko'ngil`, `koʻngil` (U+02BB) va `ko‘ngil` (U+2018) qidirilganda aynan bir xil 55 ta natija qaytishi sinovdan o‘tkazildi.

### 3. Parallel Matnlar Ko‘rinishi
- Asl nusxa doimo chap ustunda, Tarjima matni doimo o‘ng ustunda bo‘lishi qat'iy saqlandi.

### 4. Filtrlangan Natijalarni To‘liq Eksport Qilish
- Ko‘rinib turgan 50 ta emas, balki barcha filtrlangan satrlar eksport qilinadi.
- Excel (`.xlsx`) formati `openpyxl` orqali toza shrift va ustun kengliklari bilan yaratildi.
- CSV formati Microsoft Excel-da o‘zbekcha harflar buzilmasligi uchun UTF-8 BOM (`\xef\xbb\xbf`) bilan ta'minlandi.
- Qidiruv so‘rovi va sana-vaqt tamg‘asi fayl nomiga biriktirildi.
- Aylana sinovi (Export round-trip) 100% muvaffaqiyatli o‘tdi (472 ta qator tekshirildi, 0% axborot yo‘qotilishi).

### 5. Xavfsizlik va XSS Bartaraf Etish (Defect D12)
- `js/app.js` dagi soxta mijoz qo‘shish funksiyasi olib tashlandi.
- `toast.innerHTML` va jadval renderlashda tekshirilmagan HTML kiritish o‘rniga xavfsiz DOM `textContent` qo‘llanildi. 4 ta XSS hujum ssenariysi to‘liq zararsizlantirildi.

---

## [Stage 8] — Statistika: Haqiqiy Hisob-Kitob va III Bob Jadvallari (Transparent Statistics) — 2026-10-12

### 1. Korpus Hajmi va Leksik Boylik
- Barcha faol kitoblar bo‘yicha 303,393 ta token va 40,276 ta unikal tur (types) to‘liq hisoblab chiqildi.
- Stevenson UZ 0 ta token (karantinda) holati saqlandi.
- Har 10,000 tokenga normallashtirilgan chastota mezoni joriy qilindi.

### 2. 2×2 Kontingentlik Jadvali va Assotsiatsiya Mezonlari
- $O_{11}, O_{12}, O_{21}, O_{22}, R_1, C_1, N$ barcha kirish sonlari `association_measures` jadvalida natijalar ($MI, t, G^2$) bilan birgalikda saqlandi (11,527 ta hisoblangan parametr).
- Dunning (1993) Log-Likelihood ($G^2$) mezoni kichik korpuslar uchun asosiy ko‘rsatkich sifatida hisoblandi.
- Sozlanuvchi minimal chastota chegarasi ($f \ge 2, f \ge 3, f \ge 5$) joriy etildi.

### 3. III Bob Statistik Jadvallari (Faqat Tasdiqlangan Annotatsiyalardan)
- 3.1, 3.2, 3.3, 3.4, 3.5 va 3.6-jadvallar FAQAT tadqiqotchi tomonidan tasdiqlangan annotatsiyalar (`is_confirmed = 1`) asosida generatsiya qilinadi.
- Barcha foizlar yonida maxraj ($n = \dots$) qat'iy ko‘rsatildi.

### 4. Metodologiya Sahifasi va Takrorlanuvchanlik
- `methodology_statistics.html` interaktiv sahifasi yaratildi.
- Jonli 2x2 kalkulyator va qo‘lda hisoblangan test misollari bilan ta'minlandi.
- Barcha jadvallar `settings_snapshot` (JSON va CSV) bilan to‘liq eksport qilinadi.

---

## [Stage 7] — Tarjima Mutanosibligi va Annotatsiya Ish Joyi (Translation Correspondence & Annotation Workspace) — 2026-10-12

### 1. Taksonomiya Modeli (Prompt 7 · Versiya 1.0)
- Relyatsion `taxonomies` jadvali to‘liq Prompt 7 spetsifikatsiyasi bo‘yicha 40 ta rasmiy taksonomik parametr bilan yangilandi (7 toifa: Birlik turi, Struktur qolip, Semantik guruh, Ekvivalentlik turi, Tarjima strategiyasi, Lingvomadaniy realiya, Ishonch darajasi).
- Har bir parametr ta'rif, misollar va versiya nazorati (`version = '1.0'`) bilan ta'minlandi.

### 2. Relyatsion Annotatsiyalar Jadvali (`phd_annotations`)
- Yangi `phd_annotations` jadvali yaratildi: `guideline_version`, `taxonomy_version`, `annotator_user`, `source_span`, `target_span`, `has_target_equivalent`, barcha 7 ta taksonomiya maydonlari, `is_ai_suggestion`, `is_confirmed`.
- Har bir annotator (`admin`, `reviewer`) o‘z mustaqil yozuviga ega bo‘lishi ta'minlandi.
- Barcha o‘zgarishlar `audit_log` da foydalanuvchi, harakat va JSON o‘zgarishlar bilan qayd etilmoqda.

### 3. Interaktiv Ish Joyi (`annotation_workspace.html`)
- **ORIGINAL doim chapda:** Cho‘lponda chapda o‘zbekcha asl matn, o‘ngda inglizcha tarjima; Hemingwayda chapda inglizcha asl matn, o‘ngda o‘zbekcha tarjima.
- Asl kollokatsiya jumlada sariq (`<mark>`) rang bilan yoritildi.
- Tarjima matnidan ekvivalentni sichqoncha bilan belgilash yoki `[To‘g‘ridan-to‘g‘ri ekvivalenti yo‘q]` tugmasini bosish mexanizmi.
- **Tezkor tugmalar:** `Alt+S` (Qoralama), `Alt+C` (Tasdiqlash), `Alt+N` (Keyingi), `Alt+P` (Oldingi).

### 4. Tarjima Mutanosibligi Matritsasi (Correspondence Matrix)
- 6 ta struktur qolip $\times$ 8 ta ekvivalentlik turi bo‘yicha real hisoblangan dinamik matritsa.
- Har bir katak bo‘yicha chuqur ko‘rish (Drill-down) — bosilganda barcha mos jumlalar, tarjimalar va PDF sahifalari ko‘rsatiladi.

### 5. Mustaqil Annotatsiya Yo‘riqnomasi va Cohen's Kappa
- `annotation_guidelines.html` mustaqil sahifasi yaratildi.
- Ikki annotator (`admin` va `reviewer`) o‘rtasida **Cohen's Kappa ($\kappa$)** statistik kelishuvi hisob-kitobi joriy etildi.
- AI tavsiyalari qat'iy ravishda faqat bitta jumla uchun loyiha sifatida cheklandi va standart holatda o‘chirib qo‘yildi (Rule R3).

---

## [Stage 6] — Kollokatsiyalar: Ma'lumotnoma Ro‘yxati va Korpus Uchrashlari (Collocations: Reference List vs Occurrences) — 2026-10-12

### 1. `lexicon_entries` va `collocation_occurrences` To‘liq Ajratildi
- `lexicon_entries` jadvali halol bibliografik manba (`provenance = "user-supplied reference list: collocations_full.json"`) sifatida mustahkamlandi (6,546 ta yozuv).
- Kitobda topilmagan lug‘at yozuvlari hech qachon korpusda mavjuddek ko‘rsatilmaydi ($0..n$ bog‘lanish).
- Korpus uchrashlari faqat tasdiqlangan parallel segmentlar va PDF sahifalariga tayangan holda saqlanadi.

### 2. Tozalash Navbati (`Clean-up Queue`) O‘rnatildi
- Birorta ham ma'lumot o‘chirilmasdan, 104 ta shubhali birlik `status = 'needs_cleanup'` holatiga o‘tkazildi:
  - 104 ta tarjimasiz nusxa ko‘chirilgan kalka (*human behaviour*, *human interaction*).
  - 2 ta sintetik demo birikma (*nice nice nice*, *good good good*) `status = 'excluded'` karantinida saqlandi.
  - 6,440 ta faol ilmiy ma'lumotnoma yozuvi tasdiqlandi.

### 3. Tasdiqlangan Segmentlardan Nomzodlar Qazib Olish
- **Ingliz tili (NLTK POS Tagging):**
  - Qoliplar: `Adj+Noun`, `Verb+Noun`, `Adv+Verb`, `Noun+of+Noun`.
  - 50 ta nomzodlik tekshiruvda **100.00% aniqlik** qayd etildi (`young girls`, `other hand`, `old man`, `parcel of land`).
- **O‘zbek tili (Ierarxik Morfologik Analizator):**
  - 200-tokenlik oltin namunada sinovdan o‘tdi (negiz aniqligi 83.57%, POS aniqligi 75.59%, xatolik 24.41%).
  - Tizim cheklovlari [`docs/LIMITATIONS.md`](file:///C:/Users/user/Desktop/tarjimon/docs/LIMITATIONS.md) faylida rasmiylashtirildi.
  - 50 ta nomzodlik tekshiruvda **96.00% aniqlik** qayd etildi (`yuz kulmoq`, `kirib kelmoq`, `javob bermoq`).
  - Barcha nomzodlar inson tasdiqlaguniga qadar qat'iy **"SUGGESTION"** maqomida belgilandi va statistikaga kiritilmadi.

### 4. Lemmaga va Tutuq Belgisiga Sezgir Qidiruv (Lemma-Aware Search)
- Fonologik o‘zgaruvchanlik (`k` $\leftrightarrow$ `g`, `q` $\leftrightarrow$ `g‘`) va o‘zbekcha egalik/kelishik qo‘shimchalarini qamrab oluvchi qidiruv tizimi yaratildi.
- Misol: `yurak urmoq` so‘rovi korpusdagi *yurakdan urgan*, *yuragi urgan*, *yuragi sust urmoqda* kontekstlarini to‘liq topdi.

---

## [Stage 5] — Jumlalarni Qayta Qurish (Rebuild Sentence Alignment) — 2026-10-12

### 1. Oltin Namuna (`gold_v1`) Yaratildi va Muzlatildi
- Har bir kitobdan boshidan (50 juftlik), o‘rtasidan (50 juftlik) va oxiridan (50 juftlik) jami 150 tadan, umumiy **300 ta to‘liq tekshirilgan oltin parallel juftlik** `gold_alignments` jadvali va `data/gold_v1.json` faylida muzlatildi.

### 2. Mahalliy Tekislash Usullari Qiyosiy Baholandi
- **Method A (Length-based Gale-Church + 24k Lug‘at Ankori):**
  - Cho‘lpon UZ $\leftrightarrow$ EN: Precision = 54.19%, Recall = 56.00%, **F1 = 0.5508**
  - Hemingway EN $\leftrightarrow$ UZ: Precision = 48.03%, Recall = 48.67%, **F1 = 0.4834**
- **Method B (Lexical-Anchor DP / Jaccard + Char 3-gram):**
  - Cho‘lpon UZ $\leftrightarrow$ EN: Precision = 33.58%, Recall = 30.67%, F1 = 0.3206
  - Hemingway EN $\leftrightarrow$ UZ: Precision = 46.81%, Recall = 44.00%, F1 = 0.4536
- Method A ikkala asar bo‘yicha sezilarli ustunlik ko‘rsatgani sababli asosiy tekislash dvijogi sifatida tanlandi.

### 3. To‘liq Korpus Bo‘yicha Jumlalarni Tekislash
- Yangi ajratilgan segmentlar asosida Cho‘lpon va Hemingway asarlari ankorli darcha usulida tekislandi (`scripts/run_full_alignment.py`):
  - **Cho‘lpon (UZ ➔ EN):** 5,428 ta juftlik (1:1 = 1,796, 1:2 = 2,150, 2:1 = 1,482).
  - **Hemingway (EN ➔ UZ):** 1,189 ta juftlik (1:1 = 364, 1:2 = 648, 2:1 = 177).
  - **Stevenson («Treasure Island»):** 0 ta juftlik (o‘zbekcha matn qatlami bo‘lmagani sababli to‘liq karantinda).
  - **Jami faol tekislangan juftliklar:** **6,617 ta juftlik**.
  - **Legacy mosliklar saqlandi:** `collocation_occurrences` dagi 469 ta uchrashuvning Foreign Key uzluksizligi to‘liq ta’minlandi (baza jami juftliklari: 7,391 ta, FK xatolari: 0).

### 4. Sifat Nazorati va Ko‘rib Chiqish Navbati (Review Queue)
- Interaktiv ikki ustunli ko‘rib chiqish ekrani yaratildi ([`preview_alignment_queue.html`](file:///C:/Users/user/Desktop/tarjimon/preview_alignment_queue.html)).
- **ORIGINAL doim chapda:** Cho‘lponda chapda o‘zbekcha; Hemingwayda chapda inglizcha.
- **Kontekst:** Faol juftlik atrofida $\pm 2$ ta qo‘shni segment ko‘rsatiladi.
- **Hech narsa avtomatik tasdiqlanmadi:** Yuqori xarajatli yoki n:m juftliklar (6,193 ta) `needs_review`, past xarajatli 1:1 juftliklar (424 ta) `draft` holatida.
- **Xom ball (Raw score):** Algoritm nomi va xarajat soni ko‘rsatiladi (masalan, `gale_church_dict_v1: 15.11`), hech qanday soxta foiz ko‘rsatilmaydi.
- Tezkor tugmalar joriy etildi: `C` (Tasdiqlash), `S` (Ajratish), `M` (Birlashtirish), `U` (1:0), `A` (0:1), `Z` (Bekor qilish).

---

## [Stage 4] — Matnni PDFdan Ajratish va Sifat Nazorati (Text Extraction & Quality Control) — 2026-10-12

### 1. 20 Betlik Prototip Sinovi (Hemingway: 3–22-betlar)
- Hemingway «Chol va dengiz» (UZ) va «The Old Man and the Sea» (EN) asarlarining ketma-ket 20 beti (3–22-betlar) ajratib olindi.
- 40 ta yuqori sifatli (150 DPI) PDF sahifa rasmi yaratildi (`static/previews/` va `staging/static/previews/`).
- Interaktiv ikki ustunli solishtiruvchi vizual interfeys (`preview_prototype.html`) yaratildi va foydalanuvchi tomonidan tasdiqlandi.

### 2. Barcha 6 ta Matn Bo‘yicha To‘liq Qayta Ajratish (Full Pipeline)
- Eski segmentlar haqiqat manbasi sifatida ishlatilmadi; barcha 6 ta kitob asl PDF manbalaridan noldan qayta ajratildi (`scripts/extract_all_texts.py`).
- **Sahifalar soni:** Jami 963 bet (`pages` jadvalida).
  - Cho‘lpon UZ: 272 bet
  - Cho‘lpon EN: 235 bet
  - Hemingway EN: 52 bet
  - Hemingway UZ: 46 bet
  - Stevenson EN: 142 bet
  - Stevenson UZ: 216 bet (skanerlangan rasm, 0 matn qatlami — Prompt 4 qoidasi bo‘yicha `NO_TEXT_LAYER_MISSING` sifatida karantinda, 0 segment).
- **Segmentlar soni:** Jami 23,762 ta jumla va dialog segmenti (`segments` jadvalida).
  - Cho‘lpon UZ: 9,363 segment (Tana: 6,338, Dialog: 2,600, Sarlavha: 407, Snoska: 18)
  - Cho‘lpon EN: 7,695 segment (Tana: 6,458, Dialog: 1,053, Sarlavha: 67, Snoska: 117)
  - Stevenson EN: 3,160 segment (Tana: 2,476, Dialog: 650, Sarlavha: 34, Snoska: 0)
  - Hemingway UZ: 1,845 segment (Tana: 1,393, Dialog: 431, Sarlavha: 13, Snoska: 8)
  - Hemingway EN: 1,699 segment (Tana: 1,364, Dialog: 320, Sarlavha: 15, Snoska: 0)
  - Stevenson UZ: 0 segment (soxtalashtirish taqiqlangan).
- **Leksemalar (Tokenlar) soni:** Jami 301,512 ta so‘z (`\b[\w\u02bb\u02bc'-]+\b` qolipi asosida).

### 3. Sifat Nazorati va Mexanizmlar
- **Kolontitul va Sahifa Raqamlari:** `header_text`, `footer_text`, `printed_page_num` maydonlariga to‘liq ajratildi. Matn tanasiga kolontitul sizishi 0% ga tushirildi.
- **Snoskalar (Footnotes):** Sahifa pastidagi izohlar asosiy matndan ajratilib, `segment_type = 'footnote'` sifatida alohida segmentlandi (Cho‘lpon EN da 117 ta, Cho‘lpon UZ da 18 ta, Hemingway UZ da 8 ta).
- **Dehyphenation (Satr oxiri chiziqchalarini birlashtirish):** Bo‘lingan so‘zlar kontekstda birlashtirildi, `penny-pieces`, `tree-tops` kabi qo‘shma so‘zlar to‘g‘ri tiklandi.
- **Jumla Chegaralari:** O‘zbekcha va inglizcha qisqartmalar, initsiallar (`E. Hemingway`, `A. Cho‘lpon`) va dialog tirelari (`—`) to‘liq saqlandi.
- **Sifat Bayroqlari:** `OK`, `FOOTNOTE_DETECTED`, `HYPHEN_JOINED`, `FRONT_MATTER`, `AFTERWORD`, `GLOSSARY`, `BIBLIOGRAPHY`, `EMPTY_PAGE`, `NO_TEXT_LAYER_MISSING`.

### 4. Stratifikatsiyalangan Qo‘lda Tekshiruv (Stratified Manual Audit)
- Har bir matndan boshidan, o‘rtasidan va oxiridan 10 tadan sahifa (jami 60 ta sahifa, 1,542 ta segment, 21,883 ta so‘z) tekshirildi:
  - Cho‘lpon UZ: 0 xato / 319 segment (0.00%)
  - Hemingway UZ: 0 xato / 376 segment (0.00%)
  - Hemingway EN: 0 xato / 314 segment (0.00%)
  - Stevenson EN: 0 xato / 232 segment (0.00%)
  - Stevenson UZ: 0 xato / 0 segment (0.00%, karantin)
  - Cho‘lpon EN: 2 ta ogohlantirish / 301 segment (0.66% — manba matndagi haqiqiy `jakob.45` va `maryam.` kichik harf qaydlari).
  - Jami aniqlik darajasi: **99.87%** (xatolik darajasi: 0.13%).

---

## [Stage 3] — Ma'lumotlar Poydevori (Data Foundation) — 2026-10-12

### Arxitektura va Relyatsion Ma'lumotlar Modeli (12 ta Entiti)
- **12 ta toza ob'ekt joriy etildi:** `works`, `editions`, `texts`, `pages`, `segments`, `alignments`, `lexicon_entries`, `collocation_occurrences`, `equivalents`, `annotations`, `taxonomies`, `audit_log`.
- **Eski jadvallar yaxlitligi saqlandi:** Eski jadvallar o‘chirilmasdan qiyosiy taqqoslash uchun read-only holatda qoldirildi.
- **Qaytariluvchi migratsiya va rollback:**
  - [`scripts/migrate_to_phd_v2.py`](file:///C:/Users/user/Desktop/tarjimon/scripts/migrate_to_phd_v2.py) — migratsiya skripti.
  - [`scripts/rollback_phd_v2.py`](file:///C:/Users/user/Desktop/tarjimon/scripts/rollback_phd_v2.py) — xavfsiz avtomatik snapshot orqali orqaga qaytarish skripti.
  - [`scripts/validate_integrity.py`](file:///C:/Users/user/Desktop/tarjimon/scripts/validate_integrity.py) — Foreign Key yaxlitligi va 1-bosqich audit hisoblari bilan 100% moslik tekshiruvi.
- **Bibliografik pasport va SHA256 nazorati:**
  - 3 ta asar (`works`): Cho‘lpon, Hemingway, Stevenson.
  - 6 ta nashr (`editions`): Barcha 6 ta PDF faylning SHA256 nazorat summasi, nashriyoti, shahri, yili, betlari bog‘landi.
  - 6 ta matn (`texts`): Yo‘nalishlar (`UZ->EN`, `EN->UZ`), roli (`original`, `translation`), tarjimonlar va statuslari kiritildi.
- **Kollokatsiyalar lug‘ati halol manbasi:** `lexicon_entries` jadvaliga 6,546 ta birikma to‘liq o‘tkazildi. `provenance = "user-supplied reference list: collocations_full.json"` halol qayd etildi. 2 ta sintetik demo birikma `status = 'excluded'` holatida belgilandi.
- **Unicode Normalizatsiya:**
  - Asl matnlar `raw_text` maydonida 100% tegilmasdan saqlandi.
  - Qidiruv maydonida (`normalized_text`) barcha o‘/g‘ variantlari kanonik `U+02BB` (`ʻ`) ga, tutuq belgisi esa `U+02BC` (`ʼ`) ga keltirildi; kirill matni asliga sodiq saqlandi.

---

## [Stage 2] — Favqulodda Bartaraf Etish (Emergency Containment) — 2026-10-12

### Xavfsizlik va Autentifikatsiya (D8, D9)
- **Tizim yopiq rejimga o‘tkazildi:** HTTP Basic Auth va token orqali himoyalandi. Anonymous foydalanuvchilar korpus matnlari va API lardan foydalana olmaydi (401 Unauthorized).
- **Rollar joriy etildi:**
  - `admin` (Tadqiqotchi) — to‘liq boshqaruv, lab, annotatsiya, cheklangan AI tahlil.
  - `reviewer` (Ilmiy rahbar) — korpus, konkordans va eksport ko‘rish huquqi.
- **Qidiruv robotlari bloklandi:** `<meta name="robots" content="noindex, nofollow">` va HTTP `X-Robots-Tag: noindex, nofollow` sarlavhalari kiritildi.
- **AI himoyasi va so‘rovlar cheklovi:** `/api/ai`, `/api/collocations/ai-analyze`, `/api/checker/ai-diagnose` faqat `admin` uchun cheklandi va daqiqasiga 10 ta so‘rovlik Rate Limiting bilan himoyalandi. AI dan statistik sonlar (MI, t-score) so‘rash so‘rovlari butunlay olib tashlandi.

### Soxta va Asossiz Ma'lumotlarni Tozalash (D3, D4, D7)
- **"PhD Boblar" dissertatsiya matni olib tashlandi:** `index.html` dan `view-chapters` va `js/data.js` dan `dissertationData` ob'ekti to‘liq chiqarildi.
- **Qalbaki statistika o‘chirildi:** `researchStats` (46/38/16%, 38/31/18/13%) va `literaryCorporaMeta` dagi hisoblanmagan raqamlar olib tashlandi.
- **Grafiklar to‘xtatildi:** `js/charts.js` dagi qalbaki diagrammalar o‘rniga inson tomonidan tasdiqlangan empirik ma'lumotlar hisoblanishini ko‘rsatuvchi rasmiy ogohlantirish o‘rnatildi.
- **Statistik sonlar nol holatiga keltirildi:** Bosh sahifadagi stat ko‘rsatkichlar live `/api/stats` endpointi orqali real bazadan olinadigan qilindi (baza ko‘rsatkichlari: 3,811 faol jumlalar, 6,544 faol kollokatsiyalar).

### Karantin (Quarantine) choralari (D2, D6)
- **Stivenson ("Xazinalar oroli") placeholderlari (1,346 ta jumla):** O‘zbekcha tarjima skanerlangan rasm (0 matn qatlami) bo‘lgani sababli, barcha `"Sarguzasht parchasi: "` yozuvlari `status = excluded` va `exclusion_reason` bilan karantinga olindi. O‘chirilmagan, lekin barcha qidiruv va sanashlardan chiqarildi.
- **Sintetik takroriy demo birikmalar (D6):** `colloc-6411` ("nice nice nice") va `colloc-6412` ("good good good") `status = excluded` bilan karantinga olindi.
- **Ogohlantirish banneri (Stage 2–4):** Hemingway va Cho‘lpon parallel jumlalari tepasiga *"Tekislash qayta ko‘rib chiqilmoqda — tahlil uchun foydalanmang"* banneri qo‘shildi.

### Mualliflik Huquqi Bildirishnomasi (D8)
- "Fair Use", "Open Access" va "erkin ochiq korpus" yorliqlari olib tashlandi.
- Rasmiy neytral bildirishnoma kiritildi:
  > *"Korpusdagi matnlar mualliflik huquqi egalariga tegishli. Ular faqat ilmiy tadqiqot maqsadida, cheklangan parchalar ko‘rinishida ko‘rsatiladi. Nusxa ko‘chirish va tarqatish taqiqlanadi."*

### Arxitektura va Muhit
- **Zaxira nusxa:** `backups/backup_stage2_20261012_1423` yaratildi, SHA256 nazorat summalari tekshirildi, qumloqda (sandbox) tiklash sinovdan o‘tdi.
- **Staging muhiti:** `staging/` katalogida to‘liq klon yaratildi (Port 5055). Ishga tushirish uchun `run_staging.bat` tayyorlandi.

---

## [Stage 1] — Boshlang‘ich Tizimli Audit — 2026-10-12
- 14 ta nuqson (D1–D14) aniqlandi va empirik testlar bilan isbotlandi.
- Hemingway va Cho‘lpon bo‘yicha 30 ta namuna orqali tekislash siljishi (>80%) tasdiqlandi.
- Stivenson o‘zbekcha manbasi skanerlangan rasm ekanligi aniqlandi.
- 6,546 ta kollokatsiya tahlil qilindi: darslik lug‘ati va takroriy tokenlar borligi qayd etildi.
