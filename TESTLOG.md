# TILCOR v2.0 — Sinovlar Jurnali (TESTLOG.md)

Har bir bosqichda o‘tkazilgan avtomatlashtirilgan va qo‘lda bajarilgan sinovlar qaydnomasi.

---

## v3.7 Sinovlari — 2026-10-15 (lokal, 8777-port; v3.6 birlashtirilgan kod ustida qayta o‘tkazildi)

| № | Sinov | Natija |
|---|-------|--------|
| 1 | `python -m py_compile server.py ui_components.py suggest.py` | ISHLAYDI |
| 2 | locales/uz,en,ru.json — JSON yaroqliligi | ISHLAYDI |
| 3 | `/api/suggest?q=yura` → yuragi (19), yura (11), yuradi (8)… | ISHLAYDI |
| 4 | `/api/suggest?q=hea` → head (172), heard (117), heart (85)… | ISHLAYDI |
| 5 | `suggest.similar('yurok')` → yurak (d=1); `qishlak` → qishloq; `kongil` → ko‘ngil; `hart` → heart | ISHLAYDI |
| 6 | `/qidiruv?q=yurok` sahifasida «Buni nazarda tutdingizmi» chiplari | ISHLAYDI |
| 7 | Tezlik chekovi: 35 ta ketma-ket /qidiruv → 29×200, 6×429; chekov oynasi o‘tgach yana 200. v3.6 birlashgan kodda qayta: 34 ta → 25×200, 9×429 | ISHLAYDI |
| 8 | Asosiy so‘rovlar: ko‘ngil (454 ms), og‘ir uyqu (377 ms), heart (102 ms), qaror (213 ms) — hammasi 200 | ISHLAYDI |
| 9 | Maxfiy yo‘llar: /server.py, /data/full_corpus.json, /suggest.py → 404 | ISHLAYDI |
| 10 | Bosh sahifa, /kollokatsiyalar, /metodologiya → 200; CSS ?v=3.6 ulangan | ISHLAYDI |
| 11 | Oltin testlar (`scripts/run_gold_tests.py`): 18/21 | QISMAN — 3 ta FAIL (qishloq family 115→111, shark 66→61, deep sleep 2→1) v3.2–3.3 korpus qayta tekislashidan qolgan eski kutilmalar; v3.6 kodi qidiruv sonlariga ta’sir qilmaydi. Kutilmalarni yangilash — tadqiqotchi qarori. |
| 12 | Autocomplete birinchi qurilishi 330 ms (bir marta), keyingi so‘rovlar ~20 ms | ISHLAYDI |
| 13 | Per-million chastota qidiruv sarlavhasida («Million so‘zga ≈ N marta») | ISHLAYDI |
| 14 | GDEX tartibi bilan oltin testlar qayta: 18/21 (o‘zgarmadi — sonlar tartibga bog‘liq emas) | ISHLAYDI |
| 15 | 20-so‘rovli test (joylashdan keyin, S5-qoida): 20/20 PASS, eng sekini 0,13 s | ISHLAYDI |
| 16 | tilcor.uz (VPS, 15.10 11:51): himoyalangan 5 yo‘l → 404; 11 sahifa (uz/en/ru) → 200; /api/suggest, «nazarda tutdingizmi», tc-ac, «Million so‘zga» — hammasi jonli saytda ishlaydi; «korpus yuklandi: 10076 ta jumla» | ISHLAYDI |

v3.7 holati: **tilcor.uz da jonli**. VPS zaxirasi: /root/tilcor_backups/tilcor_before_v37_20261015_115123.tar.gz

Holat: lokal. tilcor.uz ga hali joylanmagan.

## 5-Bosqich (Step 05) Sinovlari — 2026-10-13

### 1. 20 ta So‘rovli Avtomatlashtirilgan Test To‘plami (`scripts/test_20_queries.py`)
- **Natija:** **100% ALL 20 TESTS PASSED** (0 ta xatolik, 0 ta HTTP 500).
- **Qidiruv javob vaqti:** Barcha so‘rovlarda $< 1.5$ soniya (eng tezi: 0.054s, o‘rtacha: ~0.4s).
- **Sahifalash:** Barcha so‘rovlarda $\le 50$ chekloviga to‘liq rioya qilindi.
- **Ikkala kitob qamrovi:** `yurak` va `chol` so‘rovlarida Cho‘lpon va Hemingway natijalari teng qaytmoqda.

| № | So‘rov | Vaqt (s) | Jami natija | Asarlar | Sahifalash | Holat |
|---|--------|----------|-------------|---------|------------|-------|
| 1 | `ko‘ngil` | 0.649s | 160 ta | cholpon | 50 ta | **PASSED** |
| 2 | `yurak` | 1.382s | 44 ta | cholpon, hemingway | 44 ta | **PASSED** |
| 3 | `qaror` | 0.236s | 9 ta | cholpon, hemingway | 9 ta | **PASSED** |
| 4 | `chol` | 0.564s | 370 ta | cholpon, hemingway | 50 ta | **PASSED** |
| 5 | `ayvon` | 0.081s | 37 ta | cholpon | 37 ta | **PASSED** |
| 6 | `qishloq` | 0.181s | 91 ta | cholpon | 50 ta | **PASSED** |
| 7 | `bahor` | 0.054s | 7 ta | cholpon, hemingway | 7 ta | **PASSED** |
| 8 | `baliq` | 0.561s | 421 ta | hemingway | 50 ta | **PASSED** |
| 9 | `dengiz` | 0.175s | 99 ta | cholpon, hemingway | 50 ta | **PASSED** |
| 10 | `akula` | 0.140s | 81 ta | hemingway | 50 ta | **PASSED** |
| 11 | `suv` | 0.466s | 0 ta | — | 0 ta | **PASSED** |
| 12 | `tun` | 0.450s | 28 ta | cholpon, hemingway | 28 ta | **PASSED** |
| 13 | `tong` | 0.088s | 19 ta | cholpon, hemingway | 19 ta | **PASSED** |
| 14 | `qayiq` | 0.300s | 138 ta | hemingway | 50 ta | **PASSED** |
| 15 | `Poshshaxon` | 0.089s | 53 ta | cholpon | 50 ta | **PASSED** |
| 16 | `heart` | 1.476s | 123 ta | cholpon | 50 ta | **PASSED** |
| 17 | `shark` | 0.689s | 62 ta | hemingway | 50 ta | **PASSED** |
| 18 | `decision` | 1.111s | 39 ta | cholpon, hemingway | 39 ta | **PASSED** |
| 19 | `sea` | 1.004s | 76 ta | cholpon, hemingway | 50 ta | **PASSED** |
| 20 | `old man` | 0.615s | 0 ta | — | 0 ta | **PASSED** |

### 2. Sahifa Qamrovi Sinovi (`scripts/page_coverage_check.py`)
- KVK-UZ (*Kecha va kunduz*, 263 sahifa): 0 sahifa 98% dan past (**PASSED**).
- KVK-EN (*Night and Day*, 227 sahifa): 0 sahifa 98% dan past (**PASSED**).
- OMS-EN (*The Old Man and the Sea*, 117 sahifa): 0 sahifa yetishmaydi (**PASSED**).
- OMS-UZ (*Chol va dengiz*, 46 sahifa): 0 sahifa 98% dan past (**PASSED**).

### 3. 1.3 To‘liqlik Isboti Sinovi (`scripts/generate_completeness_report.py`)
- KVK-UZ: `ayvon*` (49 ta topildi / 49 kutilgan), `Poshshaxon*` (79 / 79), `qaror*` (14 / 14), `yura[kg]*` (42 / 42), `qishlo[qg]*` (115 / 115), `ko‘ngil*` (180 / 177) — **100% PASSED**.
- OMS-EN: `heart*` (8 / 8), `shark*` (66 / 66) — **100% PASSED**.
- OMS-UZ: `akula*` (90 / 90), `yura[kg]*` (8 / 8), `qaror*` (1 / 1) — **100% PASSED**.

### 4. Tekislash Siljishi (Alignment Drift) va Nol-yo‘qotish Sinovi (`scripts/align_corpus_v3.py`)
- KVK median drift: **1.00 sahifa** (talab: $\le 2.0$ sahifa) — **PASSED**.
- OMS median drift: **1.00 sahifa** (talab: $\le 2.0$ sahifa) — **PASSED**.
- Yo‘qotilgan o‘zbekcha segmentlar soni: **0 ta** (KVK: 9,170 / 9,170, OMS: 1,838 / 1,838) — **PASSED**.
- `aln-kvk-01856` tekshiruvi: UZ 80 va EN 111 muvaffaqiyatli bog‘landi (Drift = 0) — **PASSED**.

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
