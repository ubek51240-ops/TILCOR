# TILCOR v2.0 — O‘zgarishlar Jurnali (CHANGELOG.md)

Ushbu hujjat doktorlik dissertatsiyasi talablari doirasida har bir bosqichda kiritilgan o‘zgarishlarning to‘liq audit izini aks ettiradi.

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
