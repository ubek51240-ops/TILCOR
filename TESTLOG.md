# TILCOR v2.0 — Sinovlar Jurnali (TESTLOG.md)

Har bir bosqichda o‘tkazilgan avtomatlashtirilgan va qo‘lda bajarilgan sinovlar qaydnomasi.

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
