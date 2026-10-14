# TILCOR v2.0 — Sinovlar Jurnali (TESTLOG.md)

Har bir bosqichda o‘tkazilgan avtomatlashtirilgan va qo‘lda bajarilgan sinovlar qaydnomasi.

## 12-Bosqich (Validatsiya, Hujjatlar va Himoyaga Tayyorgarlik) Sinovlari — 2026-10-12
- **Skript:** `scripts/test_stage12_readiness.py`
- **Natijalar (4/4 Test PASS — 100%):**
  - `TEST 1 (Hujjatlar butunligi)`: 10 ta rasmiy hujjat (`VALIDATION_REPORT`, `REPRODUCIBLE_CHAIN_EXAMPLE`, `USER_GUIDE`, `DATA_DICTIONARY`, `LIMITATIONS`, `BACKUP_RESTORE`, `ARCHITECTURE`, `DEFENCE_DEMO_SCRIPT`, `PLATFORM_FACTSHEET`, `platform_factsheet.html`) to‘liq mavjud va to‘ldirilgan (PASS).
  - `TEST 2 (Namunaviy zanjir)`: `occ-00002` kollokatsiyasi (`fished alone` ➔ `baliq ovlardi`) PDF 1-betdan boshlab eksport qatorigacha 100% takrorlanuvchan tarzda verifikatsiya qilindi (PASS).
  - `TEST 3 (Oflayn himoya to‘plami)`: Kengash a'zolari uchun mehmon hisobi (`guest` / `<parol kodda saqlanmaydi>`) va to‘liq lokal ishlash qobiliyati tasdiqlandi (PASS).
  - `TEST 4 (Baza yaxlitligi va halollik)`: 0 ta Foreign Key xatosi, Stevenson UZ 0 ta segment (karantinda), 2 ta sintetik demo birikma karantinda (PASS).

---

## 11-Bosqich (Dizayn Tizimi va Akademik Interfeys) Sinovlari — 2026-10-12
- **Skript:** `scripts/test_stage11_design.py`
- **Natijalar (4/4 Test PASS — 100%):**
  - `TEST 1 (Dizayn tokenlari)`: `#1F2A5A`, `#0F766E`, `#B45309`, status badges, `@media print` qoidalari to‘liq tekshirildi (PASS).
  - `TEST 2 (Yagona brend)`: Barcha sahifalarda yagona *"TILCOR — O‘zbek–ingliz parallel korpusi"* o‘rnatildi (PASS).
  - `TEST 3 (Tipografik test)`: `O‘zbekiston, g‘alaba, ta’lim` iborasi to‘g‘ri renderlandi (PASS).
  - `TEST 4 (Loyiha pasporti)`: Tadqiqotchi va ixtisoslik (10.02.20) ma'lumotlari to‘liq tekshirildi (PASS).

---

## 10-Bosqich (Mualliflik Huquqi, Kirish Huquqlari va Xavfsizlik) Sinovlari — 2026-10-12
- **Skript:** `scripts/test_stage10_security.py`
- **Natijalar (8/8 Test PASS — 100%):**
  - `TEST 1 (RBAC rollari)`: `admin`, `reviewer`, `guest` muvaffaqiyatli tasdiqlandi (PASS).
  - `TEST 2 (Mehmon limiti)`: Himoyalangan asarlarda mehmon uchun 50 ta natija va 1 jumla kontekst chegarasi tasdiqlandi (PASS).
  - `TEST 3 (Ommaviy eksport bloklanishi)`: Mehmon tomonidan ommaviy yuklash 100% to‘sib qo‘yildi (403 Forbidden, PASS).
  - `TEST 4 (Admin/Reviewer eksport)`: Tadqiqotchi va rahbar to‘liq eksport qila oldi (PASS).
  - `TEST 5 (Litsenziya va audit)`: Faqat admin ruxsat holatini o‘zgartira oladi, `audit_log` da to‘liq qayd etildi (PASS).
  - `TEST 6 (Xavfsizlik talablari)`: Parameterized queries, CSRF, Secure cookies, Restricted CORS, Audit logging 100% tasdiqlandi (PASS).
  - `TEST 7 (Zaxira va tiklash)`: SHA-256 bilan sinovdan o‘tgan zaxira va qayta tiklash to‘liq muvaffaqiyatli o‘tdi (PASS).
  - `TEST 8 (Baza yaxlitligi)`: 0 ta Foreign Key xatosi (PASS).

---

## 9-Bosqich (Qidiruv, KWIC va Eksport) Sinovlari — 2026-10-12

### 1. Avtomatlashtirilgan KWIC va Eksport Sinov To‘plami
- **Skript:** `scripts/test_stage9_kwic_export.py`
- **Natijalar (7/7 Test PASS — 100%):**
  - `TEST 1 (KWIC 3 ta so‘rov bo‘yicha tekshiruv)`:
    - `'yurak'`: 9 ta uchrashuv (42.58 ms) | Namuna: `...Qish ichi [yuraklaring] g‘ash...` (PDF 5-bet).
    - `'old man'`: 245 ta uchrashuv (62.92 ms) | Namuna: `...neath her eyelids saw the [old man] as cold as snow....` (PDF 6-bet).
    - `'baliq'`: 409 ta uchrashuv (45.14 ms) | Namuna: `... yolg‘iz o‘zi Golfstrimda [baliq] ovlardi....` (PDF 1-bet).
    - So‘z markazda vizual ajratilgan, kontekst chegaralari to‘g‘ri, PDF sahifalari ulangan.
  - `TEST 2 (KWIC Kontekst Saralash)`: Chap kontekstdagi birinchi so‘z va o‘ng kontekstdagi birinchi so‘z bo‘yicha alifbo tartibida saralash to‘liq tekshirildi (PASS).
  - `TEST 3 (Apostrof va Tutuq Belgisiga Sezgirmaslik)`:
    - `'ko'ngil'`: 55 ta natija
    - `'koʻngil'` (U+02BB): 55 ta natija
    - `'ko‘ngil'` (U+2018): 55 ta natija
    - Barcha apostrof variantlari aynan bir xil natija berdi (PASS).
  - `TEST 4 (Parallel Ko‘rinish Yo‘nalishi)`: Original doimo chapda, tarjima doimo o‘ngda qat'iy saqlandi (PASS).
  - `TEST 5 (Eksport Aylana Sinovi - Round-Trip)`:
    - Excel (`.xlsx`): 472 ta qator (Sarlavha + Ma'lumotlar) to‘liq o‘qildi va tekshirildi.
    - CSV (`UTF-8 BOM`): 472 ta qator to‘liq o‘qildi.
    - 0 ta buzilgan yoki yo‘qolgan belgi (PASS).
  - `TEST 6 (XSS Xavfsizligi Sinovi - Defect D12)`: 4 ta zararli script va img payloadlari kiritildi va ularning zararsizlantirilganligi DOM `textContent` orqali tekshirildi (PASS).
  - `TEST 7 (Baza Yaxlitligi)`: 0 ta Foreign Key xatosi (PASS).

---

## 8-Bosqich (Statistika: Haqiqiy Hisob-Kitob) Sinovlari — 2026-10-12

### 1. Avtomatlashtirilgan Statistika Test To‘plami
- **Skript:** `scripts/test_stage8_statistics.py`
- **Natijalar (7/7 Test PASS — 100%):**
  - `TEST 1 (Hand-computable validation)`: $N=100000, O_{11}=10, R_1=50, C_1=100$ parametrlarida qo‘lda hisoblangan natijalar ($E_{11}=0.05, MI=7.6439, t=3.1465, G^2=89.2209, \text{NormFreq}=1.0$) dastur natijasi bilan 100% aniqlikda mos keldi.
  - `TEST 2 (Corpus sizes)`: Jami faol tokenlar soni: 303,393 ta, types: 40,276 ta. Stevenson UZ matni 0 ta token (karantin) holatida saqlandi.
  - `TEST 3 (Contingency balance)`: Barcha $2 \times 2$ kontingentlik jadvallarida qatorlar va ustunlar muvozanati ($O_{11}+O_{12}=R_1$, $O_{21}+O_{22}=N-R_1$, $O_{11}+O_{21}=C_1$, $O_{12}+O_{22}=N-C_1$) to‘liq saqlangan.
  - `TEST 4 (Configurable threshold)`: Minimal chastota filtrlari ($f \ge 2: 913, f \ge 3: 715, f \ge 5: 548$) dinamik va to‘g‘ri ishladi.
  - `TEST 5 (Chapter III Denominators)`: Barcha statistik ko‘rsatkichlar FAQAT tasdiqlangan annotatsiyalar asosida hisoblandi va har bir foiz yonida maxraj ($n = \dots$) ko‘rsatildi.
  - `TEST 6 (Export & Snapshot)`: JSON va CSV formatdagi eksportlar `settings_snapshot` bilan birga to‘liq hosil bo‘ldi.
  - `TEST 7 (Database Integrity)`: 0 ta Foreign Key xatosi.

### 2. Korpus Statistikalarini Hisoblash Skripti
- **Skript:** `scripts/compute_corpus_statistics.py`
- **Natija:** 11,527 ta assotsiatsiya mezonlari hisoblanib, `association_measures` va `corpus_statistics_snapshot` jadvallariga saqlandi.

---

## 7-Bosqich (Tarjima Mutanosibligi va Annotatsiya Ish Joyi) Sinovlari — 2026-10-12

### 1. Avtomatlashtirilgan Ish Joyi Test To‘plami
- **Skript:** `scripts/test_stage7_workspace.py`
- **Natijalar (8/8 Test PASS — 100%):**
  - `TEST 1 (Taxonomies)`: 7 ta toifaning barchasi (40 ta parametr) muvaffaqiyatli yuklandi (`unit_type`, `structural_pattern`, `semantic_group`, `equivalence_type`, `translation_strategy`, `cultural_marker`, `confidence_level`).
  - `TEST 2 (Occurrences & Direction)`: 469 ta uchrashuv tekshirildi. Cho‘lponda asl nusxa qat'iy chapda (UZ), tarjima o‘ngda (EN); Hemingwayda asl nusxa qat'iy chapda (EN), tarjima o‘ngda (UZ).
  - `TEST 3 (Context & Single Occurrence)`: $\pm 2$ ta qo‘shni parallel jumla konteksti bilan to‘liq yuklandi.
  - `TEST 4 (Save & Confirm)`: Qoralama (`is_confirmed = 0`) va tasdiqlangan (`is_confirmed = 1`) yozuvlar `phd_annotations` va `audit_log` ga to‘liq yozildi.
  - `TEST 5 (Matrix & Drill-down)`: 6x8 tarjima mutanosibligi matritsasi hisoblandi va katak bo‘yicha aniq parallel jumlalar va PDF sahifalari drill-down orqali ko‘rsatildi.
  - `TEST 6 (Cohen's Kappa)`: Ikki annotator (`admin` va `reviewer`) kelishuvi matematik jihatdan to‘g‘ri hisoblandi ($\kappa = 1.0$ deyarli to‘liq moslik).
  - `TEST 7 (AI Suggestion)`: AI taklifi faqat bitta jumla uchun va 'Loyiha' sifatida shakllantirildi, statistikaga ta'sir qilmadi.
  - `TEST 8 (Database Foreign Keys)`: 0 ta Foreign Key xatosi.

### 2. Yaxlitlik va Qayta Tiklash Sinovi (Reconciliation)
- **Skript:** `scripts/validate_integrity.py`
- **Natija:** Barcha 10 ta asosiy relyatsion jadvallar bo‘yicha 0 ta FK xatosi, 40 ta taksonomik parametr va 469 ta uchrashuv to‘liq muvofiqlashtirildi (PASSED).

---

## 6-Bosqich (Collocations: Reference List vs Occurrences) Sinovlari — 2026-10-12

### 1. Tozalash Navbati (`Clean-up Queue`) Sinovi
- **Skript:** `scripts/build_cleanup_queue.py`
- **Natijalar:**
  - `lexicon_entries` jami: 6,546 ta.
  - Faol ilmiy ma'lumotnoma: 6,440 ta.
  - Tozalash navbatiga ajratilgan (`needs_cleanup`): 104 ta (o‘chirilmagan, tadqiqotchi qaroriga qoldirilgan).
  - Karantindagi sintetik demo birikmalar (`excluded`): 2 ta (*nice nice nice*, *good good good*).

### 2. O‘zbek Tili Morfologik Analizatori Sinovi (200-Token Benchmark)
- **Skript:** `scripts/uzbek_morphology.py`
- **Oltin namuna:** Cho‘lpon va Hemingway asarlaridan 213 ta tokendan iborat morfologik oltin namuna.
- **Natijalar:**
  - Negiz (Stem) aniqligi: **83.57%** (178/213).
  - So‘z turkumi (POS) aniqligi: **75.59%** (161/213).
  - Morfologik xatolik darajasi: **24.41%**.
  - Cheklovlar hujjati: [`docs/LIMITATIONS.md`](file:///C:/Users/user/Desktop/tarjimon/docs/LIMITATIONS.md) yaratildi.

### 3. Tasdiqlangan Segmentlardan Nomzodlar Qazib Olish (50-Sample Evaluation)
- **Skript:** `scripts/extract_collocation_candidates.py`
- **Ingliz tili (NLTK POS Tagging):**
  - Qoliplar: `Adj+Noun`, `Verb+Noun`, `Adv+Verb`, `Noun+of+Noun`.
  - 50 ta nomzoddan to‘g‘ri kollokatsiya birikmalari: **50 ta (100.00% Precision)**.
- **O‘zbek tili (Morfologik Analizator):**
  - Qoliplar: `Sifat+Ot`, `Ot+Fe’l`, `Ravish+Fe’l`, `Ot+Ot`.
  - 50 ta nomzoddan to‘g‘ri kollokatsiya birikmalari: **48 ta (96.00% Precision)**.
  - Xatolik: 2 ta yordamchi/funksional birlik (*shu uchun*, *ham olmoq*).

### 4. Lemmaga va Tutuq Belgisiga Sezgir Qidiruv Sinovi
- **So‘rov:** `yurak urmoq`
- **Natija:** Korpusdan 5 ta real kontekstual uchrashuv topildi:
  - *«Yurakdan urgan ekan-a!»* (32-bet)
  - *«Yuragi urgan holda...»* (34-bet)
  - *«...yuragi bir zarb bilan uribdi!»* (45-bet)
  - *«...yuragi... juda sust urmoqda...»* (70-bet)
  - *«...yuragi yorilib o‘ladi!»* (110-bet)

---

## 5-Bosqich (Rebuild Sentence Alignment) Sinovlari — 2026-10-12

### 1. Mahalliy Algoritmlarning `gold_v1` da Baholanishi
- **Skript:** `scripts/compare_alignment_methods.py`
- **Oltin namuna:** 300 ta tasdiqlangan guruh (150 ta Cho‘lpon, 150 ta Hemingway; 50 tadan Bosh, O‘rta, Oxir).

| Asar va Juftlik | Baholangan Algoritm | Precision (Aniqlik) | Recall (To‘liqlik) | F1-Score | To‘g‘ri Mosliklar |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Cho‘lpon: «Kecha va kunduz»** | **Method A (Gale-Church + 24k Dict Seed)** | **54.19%** | **56.00%** | **0.5508** | **84 / 150** |
| (UZ ➔ EN) | Method B (Lexical-Anchor DP / Jaccard+Char) | 33.58% | 30.67% | 0.3206 | 46 / 150 |
| **Hemingway: «Chol va dengiz»** | **Method A (Gale-Church + 24k Dict Seed)** | **48.03%** | **48.67%** | **0.4834** | **73 / 150** |
| (EN ➔ UZ) | Method B (Lexical-Anchor DP / Jaccard+Char) | 46.81% | 44.00% | 0.4536 | 66 / 150 |

### 2. Relyatsion Yaxlitlik va Traceability Sinovi
- **Skript:** `scripts/verify_alignment_stats.py` va `scripts/validate_integrity.py`
- **Natijalar:**
  - `PRAGMA foreign_key_check`: 0 ta xatolik (`PASSED`).
  - Jami faol tekislangan juftliklar: 6,617 ta (Cho‘lpon: 5,428 ta, Hemingway: 1,189 ta, Stivenson: 0 ta).
  - Baza jami yozuvlari: 7,391 ta (Legacy uchrashuvlar FK yaxlitligi 100% ta’minlandi).
  - PDF sahifa bog‘lanishi: Har bir juftlik manba va tarjima PDF sahifalariga (`pdf_page_num`) 100% bog‘langan (`PASSED`).
  - Avtomatik tasdiqlangan: 0 ta (`Nothing auto-confirmed` talabi 100% bajarildi).
  - Ko‘rib chiqish navbatiga o‘tkazilgan: 6,193 ta (`needs_review`), Dastlabki taklif: 424 ta (`draft`).

### 3. Review Queue Interfeysi Sinovi
- **Fayl:** `preview_alignment_queue.html` va `staging/preview_alignment_queue.html`
- **Natijalar:**
  - ORIGINAL har doim chapda (Cho‘lpon: UZ chapda; Hemingway: EN chapda).
  - $\pm 2$ qo‘shni segment konteksti to‘liq ishlamoqda.
  - Xom xarajat balli (masalan, `11.20`, `15.11`) to‘g‘ri aks etmoqda, hech qanday foiz yozuvi yo‘q.
  - Klaviatura buyruqlari (`C`, `S`, `M`, `U`, `J`, `K`) to‘liq ishlamoqda (`PASSED`).

---

## 4-Bosqich (Text Extraction & Quality Control) Sinovlari — 2026-10-12

### 1. Quvur Idempotentligi Sinovi (Idempotency Test)
- **Skript:** `scripts/extract_all_texts.py`
- **Sinov usuli:** Ekstraksiya quvuri ketma-ket 2 marta qayta ishga tushirildi.
- **Natija:** Har ikki safar ham aniq bir xil natijalar olindi: 963 sahifa, 23,762 segment, 301,512 token. Hech qanday ma'lumot dublikati yoki siljish sodir bo‘lmadi (`PASSED`).

### 2. Relyatsion Yaxlitlik va Traceability Sinovi
- **Skript:** `scripts/verify_stage4_results.py` va `scripts/validate_integrity.py`
- **Natijalar:**
  - `PRAGMA foreign_key_check`: 0 ta xatolik (`PASSED`).
  - Sahifaga bog‘lanmagan yetim segmentlar (`orphaned segments`): 0 ta (`PASSED`).
  - Belgilar ofseti (`char_start`, `char_end`) bo‘lmagan segmentlar: 0 ta (`PASSED`).
  - Barcha 23,762 ta segment o‘zining `book_id`, `pdf_page_num`, `page_id` siga to‘liq va uzluksiz bog‘langan (`PASSED`).

### 3. Stratifikatsiyalangan Qo‘lda Sifat Nazorati (Stratified 10-Page Audit)
- **Skript:** `scripts/stratified_manual_check.py`
- **Tanlanma:** Har bir matndan 10 tadan sahifa (Boshidan 3 ta, O‘rtasidan 4 ta, Oxiridan 3 ta).

| № | Matn Nomi | Til | Tanlangan Sahifalar | Tekshirilgan Segmentlar | Kolontitul Sizishi | Footer Sizishi | Noto‘g‘ri Bo‘linish (Hyphen) | Xato Jumla Ajralishi | Xatolik Foizi |
|---|-----------|-----|---------------------|-------------------------|--------------------|----------------|------------------------------|----------------------|---------------|
| 1 | Cho‘lpon: «Kecha va kunduz» | UZ | 3, 10, 25, 80, 120, 160, 200, 240, 255, 264 | 319 | 0 | 0 | 0 | 0 | **0.00%** |
| 2 | Hemingway: «Chol va dengiz» | UZ | 1, 5, 10, 15, 22, 28, 35, 40, 44, 46 | 376 | 0 | 0 | 0 | 0 | **0.00%** |
| 3 | Hemingway: «The Old Man and the Sea» | EN | 2, 5, 10, 18, 25, 32, 38, 44, 48, 50 | 314 | 0 | 0 | 0 | 0 | **0.00%** |
| 4 | Stevenson: «Treasure Island» | EN | 3, 10, 20, 45, 70, 95, 115, 130, 138, 142 | 232 | 0 | 0 | 0 | 0 | **0.00%** |
| 5 | Stevenson: «Xazinalar oroli» | UZ | 1, 20, 50, 80, 108, 140, 170, 190, 210, 216 | 0 | 0 | 0 | 0 | 0 | **0.00% (Karantin)** |
| 6 | Cho‘lpon: «Night and Day» | EN | 3, 10, 25, 75, 110, 145, 180, 215, 225, 229 | 301 | 0 | 0 | 0 | 2* | **0.66%** |
| **JAMI** | **6 ta kitob** | **UZ/EN** | **60 ta sahifa** | **1,542 segment** | **0** | **0** | **0** | **2** | **0.13% (99.87% Aniq)** |

*\*Izoh:* Cho‘lpon EN 145-betdagi 2 ta ogohlantirish (`jakob.45`, `maryam.`) matndagi xatolar emas, balki tarjimon Christopher Fort tomonidan personaj maktubidagi asl kichik harflarning o‘zgarishsiz berilishidir.

---

## 3-Bosqich (Data Foundation) Sinovlari — 2026-10-12

### 1. Migratsiya va Orqaga Qaytarish (Rollback) Sinovi
- **Skript:** `scripts/migrate_to_phd_v2.py` va `scripts/rollback_phd_v2.py`
- **Sinov usuli:** Sandbox va test nusxalarida ma'lumotlar bazasi to‘liq migratsiya qilindi, so‘ngra `phd_corpus.db.pre_stage3.bak` dan orqaga qaytarildi.
- **Natija:** Barcha 12 ta yangi jadval to‘liq barpo bo‘ldi va rollback paytida bazaning asl holati 100% tiklandi (`PASSED`).

### 2. Relyatsion Yaxlitlik Sinovi (Referential Integrity Check)
- **Skript:** `scripts/validate_integrity.py`
- **Buyruq:** `PRAGMA foreign_key_check`
- **Natija:** 0 ta xatolik. Barcha FK bog‘lanishlar (works $\rightarrow$ editions $\rightarrow$ texts $\rightarrow$ pages $\rightarrow$ segments $\rightarrow$ alignments $\rightarrow$ occurrences) mukammal ishlamoqda (`PASSED`).

### 3. Sanoqlarni 1-Bosqich Auditi Bilan Solishtirish (Reconciliation Check)
| № | Entiti / Jadval | Kutilgan (Stage 1 Audit) | Haqiqiy (Migratsiyadan so‘ng) | Moslik |
|---|-----------------|--------------------------|------------------------------|--------|
| 1 | `works` | 3 ta asar | 3 ta asar | **100% MOS** |
| 2 | `editions` | 6 ta nashr | 6 ta nashr | **100% MOS** |
| 3 | `texts` | 6 ta matn | 6 ta matn (5 ta active, 1 ta quarantined) | **100% MOS** |
| 4 | `pages` | 606 ta sahifa | 606 ta sahifa | **100% MOS** |
| 5 | `segments` | 19,507 ta jumla | 19,507 ta jumla | **100% MOS** |
| 6 | `alignments` | 1,963 ta juftlik | 1,963 ta juftlik (status: draft) | **100% MOS** |
| 7 | `lexicon_entries` | 6,546 ta birikma | 6,546 ta birikma (6,544 faol, 2 karantinda) | **100% MOS** |
| 8 | `collocation_occurrences` | 469 ta uchrash | 469 ta uchrash | **100% MOS** |
| 9 | `taxonomies` | 8 ta standart tasnif | 8 ta standart tasnif | **100% MOS** |
| 10 | `audit_log` | $\ge 1$ ta yozuv | 1 ta yozuv (MIGRATE v2.0_stage3) | **100% MOS** |

### 4. Unicode Normalizatsiya Sinovi
- **Skript:** `scratch/test_normalizer.py`
- **Sinov namunalari:** `o'tmoq`, `g'olib`, `O‘zbekiston`, `Gʻalaba`, `ma'no`, `san'at`, `ta'lim`, `o\`g\`il`, `ҳаёт`.
- **Natija:**
  - o‘/g‘ variantlari $\rightarrow$ `U+02BB` (`ʻ`) ga 100% aniqlikda xaritalandi.
  - Tutuq belgilari $\rightarrow$ `U+02BC` (`ʼ`) ga 100% aniqlikda xaritalandi.
  - Kirill yozuvi (*ҳаёт*) buzilmasdan saqlandi (`PASSED`).

---

## 2-Bosqich (Emergency Containment) Sinovlari — 2026-10-12

### 1. Zaxira va Tiklash Sinovi (Restore Verification Test)
- **Skript:** `scratch/test_restore_sandbox`
- **Sinov usuli:** `backups/backup_stage2_20261012_1423/checksums.sha256` dagi barcha 35 ta fayl qumloq katalogiga tiklandi va har bir faylning SHA256 nazorati qayta hisoblandi.
- **Natija:** Barcha 35 ta fayl checksumlari 100% mos keldi (`PASSED`).

### 2. Autentifikatsiya va Xavfsizlik Sinovlari (Automated Suite: `scratch/test_stage2_containment.py`)
| № | Test Nomi | So‘rov turi | Kutilgan Natija | Haqiqiy Natija | Holat |
|---|-----------|-------------|-----------------|----------------|-------|
| 1 | Anonim HTML so‘rovi | `GET /` | HTTP 401 Unauthorized + `noindex` | 401 + `X-Robots-Tag: noindex, nofollow` | **PASSED** |
| 2 | Anonim Korpus Qidiruvi | `GET /api/search?q=dengiz` | HTTP 401 Unauthorized | 401 Unauthorized (korpus o‘qib bo‘lmaydi) | **PASSED** |
| 3 | Anonim AI So‘rovi | `POST /api/ai` | HTTP 401 Unauthorized | 401 Unauthorized | **PASSED** |
| 4 | Ilmiy rahbar ruxsati | `GET /api/search?q=dengiz` (`reviewer`) | HTTP 200 OK, active=3,811 | 200 OK, totalCorpus=3,811, topildi=99 | **PASSED** |
| 5 | Ilmiy rahbar AI kirishi | `POST /api/ai` (`reviewer`) | HTTP 403 Forbidden | 403 Forbidden (faqat admin mumkin) | **PASSED** |
| 6 | Jonli Statistika API | `GET /api/stats` (`admin`) | HTTP 200 OK | 200 OK: seg=3811, col=6544, dict=24554, qar_seg=1346, qar_col=2 | **PASSED** |
| 7 | Stivenson karantini | `GET /api/search?q=Sarguzasht+parchasi` | topilgan=0 ta | topilgan=0 ta (1346 ta placeholder chiqarilgan) | **PASSED** |
| 8 | Sintetik demo karantini | `GET /api/collocations?q=nice+nice+nice` | `colloc-6411` mavjud emas | `colloc-6411` va `colloc-6412` natijadan chiqarilgan | **PASSED** |

### 3. Kod va Shablonlarda Qalbaki Ma'lumotlarni Qidirish Sinovi
- **Skript:** `re.finditer` skaneri (`index.html`, `js/*.js`, `server.py`).
- **Natijalar:**
  - `dissertationData`: 0 faol nusxa (faqat izoh).
  - `researchStats`: 0 faol nusxa (faqat izoh).
  - `Fair Use` / `Open Access`: 0 faol nusxa (faqat neytral ilmiy bildirishnoma).
  - `98.4%`: 0 faol nusxa (haqiqiy empirik statusga almashtirildi).
  - `12,450`, `169,500`, `1,520+`: 0 faol nusxa.
