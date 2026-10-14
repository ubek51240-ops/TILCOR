# TILCOR — O‘zgarishlar jurnali (CHANGELOG.md)

Ushbu hujjat doktorlik dissertatsiyasi talablari doirasida har bir bosqichda kiritilgan o‘zgarishlarning to‘liq audit izini aks ettiradi.

---

## [v3.3] — Yangi dizayn («tungi ko‘k») — 2026-10-14

- To‘q ko‘k fon (yorug‘lik dog‘lari va nuqtali to‘r), shaffof «shisha» panellar, oq sarlavhalar; kitob matni serif shriftda qoldi.
- Yuqori qator: joy, tadqiqot, asarlar; bo‘limlarga havolalar; bayroqli til almashtirgich. Uning ostida ko‘k chiziq.
- Sarlavha: TILCOR muhri (ikki sahifa: qidirilgan so‘z — oltin, muqobil — firuza), yumaloq qidiruv va menyu tugmalari.
- Butun ekranli qidiruv oynasi: qidiruv turi (so‘z va kollokatsiya, KWIC, kollokatsiyalar ro‘yxati), namuna so‘rovlar; «/» tugmasi ochadi, Esc yopadi.
- Yon menyu (barcha bo‘limlar, til), «yuqoriga» tugmasi.
- Bosh sahifa: katta sarlavha, qidiruv, ikki tugma, raqamli kartochkalar; ichki sahifalarda sarlavha bandi va bo‘lim belgisi,
  korpus va kollokatsiyalar sahifalarida raqamli kartochkalar.
- KWIC: kontekst kengligi surgich bilan (1–15 so‘z), qo‘yib yuborilganda natija yangilanadi.
- Barcha belgilar SVG da chizilgan (tashqi rasm yoki xizmat yo‘q); `assets/tilcor-emblem.svg` — sayt belgisi.

## [v3.2] — Ikkinchi o‘tish tekislash, adabiyotlar tuzatildi — 2026-10-14

- Gaplar hunalign bilan ikkinchi marta tekislandi: lug‘atga birinchi o‘tishning so‘z tekislashidan olingan 1 114 ta
  so‘z jufti qo‘shildi (`scripts/build_hunalign_lexicon.py`, `realign_hunalign.py --lexicon --base`). 10 076 juftlik;
  taxminan 1 000 juftlik o‘zgardi. Farq qilgan 30 joyning 22 tasida ikkinchi o‘tish to‘g‘riroq, 6 tasida birinchisi.
- So‘z tekislash, kollokatsiyalar (2 529 ta: o‘zbekcha 967, inglizcha 1 562) va juftsiz gaplar (321 ta) qayta tuzildi.
  Muqobil qamrovi: o‘zbekcha 30,7 %, inglizcha 41,2 %.
- Yangi tanlab tekshiruvlar (AI yordamida): `notes/tanlab_tekshiruv_2-otish_2026-10-14.md`.
- Adabiyotlar: Varga va boshq. — tekshirilgan 2007-yilgi nashr (pp. 247–258), mualliflar tartibi tuzatildi;
  Yarowsky va boshq. (2001) — ACL Anthology havolasi bilan. Saytda «[MANBANI TEKSHIRISH KERAK]» belgilari qolmadi.
  Ingliz va rus interfeysida bibliografik izohlar shu tilda.
- Kollokatsiya ro‘yxatida muqobil topilgan uchrashlar soni ko‘rsatiladi («7 ta uchrashdan 6 tasida»).

## [v3.1] — Tarjima ekvivalentlari, korpus kollokatsiyalari, yangi interfeys — 2026-10-14

**Yangi ma’lumot (oflayn tuzilgan, ishga tushirishda qo‘shimcha kutubxona kerak emas):**
- `data/word_alignment.json`, `data/lexical_table.json` — har bir juftlikda so‘z darajasidagi tekislash
  (eflomal, ikki yo‘nalish, grow-diag-final-and; `scripts/build_word_alignment.py`).
- `data/collocation_index.json` — korpusdan ajratilgan 2 501 ta kollokatsiya (f ≥ 2), har biri tarjimadagi
  ekvivalentlari, kitoblar bo‘yicha ekvivalent statistikasi va korpus ichidagi MI, t-score, logDice, G² bilan
  (`scripts/build_collocation_index.py`). Metodologiyadagi istisnolar avtomatik qo‘llanadi: juft va takroriy
  so‘zlar, ravishdosh + ko‘makchi fe’l qurilmalari, atoqli otlar.
- `data/unpaired_sentences.json` — tekislashda juft topilmagan 343 ta gap; qidiruvga izoh bilan kiradi,
  juftliklar soniga kirmaydi (`scripts/build_unpaired.py`).

**Platforma:**
- Har bir gap juftligida tarjimonning so‘zi ajratib ko‘rsatiladi; ekvivalentlar ulushi va kitobdan misoli bilan.
- So‘z yoki kollokatsiya qidirilganda: shu so‘z bilan tuzilgan barcha korpus kollokatsiyalari, so‘z shakllari va
  yasama so‘zlar, har biri misol bilan.
- «Kollokatsiyalar» sahifasi: qolip bo‘yicha va uchrash soni, logDice, MI, t-score, G² bo‘yicha tartiblash;
  har bir kollokatsiya sahifasida assotsiatsiya ko‘rsatkichlari va barcha misollar.
- «Statistika»: kollokatsiyalarning tarjimada berilishi (to‘rt yo‘nalish, qoliplar bo‘yicha), eng ko‘p
  uchragan kollokatsiyalar va ekvivalentlari, assotsiatsiya o‘lchovlarini qiyoslash (Spirmen ρ, birinchi 50 talik).
- Metodologiya: so‘z darajasidagi tekislash bandi, tanlab tekshiruv natijalari (AI yordamida; 50 tadan 45 to‘g‘ri),
  ekvivalent qamrovi (o‘zbekcha 29,7 %, inglizcha 39,8 % mustaqil so‘zlar).
- Yangi dizayn (`css/tilcor.css`), uch tilli interfeys; saytda «tasdiqlanmagan», «tekshirilmagan» kabi yozuvlar yo‘q.
- Ko‘rinishdagi tozalash: elektron nusxalardagi sahifa belgilari («- 31 -») va izoh raqamlari («Hast1») matnda
  saqlanadi, lekin ko‘rsatilmaydi.
- `/kirish.html` yangi kirish sahifasiga yo‘naltiriladi; admin sahifalarida yagona menyu uslubi.

**Ishchi hujjat:** `notes/tanlab_tekshiruv_muqobillar_2026-10-14.md` — 50 ta ekvivalentning tanlab tekshiruvi.

---

## [Step 05] — Korpus v3, Tayanch Nuqtali Tekislash va Qidiruv Barqarorligi — 2026-10-13

### Part 0 & 1: Korpus 3-Versiyasi va Sahifa Qamrovi (Page Coverage)
- **Defect 1 sababi aniqlandi va tuzatildi:** Oldingi `align_corpus_v2.py` da inglizcha jumlalar kamligi tufayli while loop erta to‘xtab, 3,643 ta o‘zbekcha jumlani tashlab ketgan edi. Yangi qoidalar bo‘yicha har bir o‘zbekcha jumla 100% to‘liq saqlandi.
- **Sahifa qamrovi 100% verifikatsiya qilindi (`data/page_coverage_v3.json`):**
  - KVK-UZ (*Kecha va kunduz*, 3–265-betlar): 263 sahifadan 0 tasi 98% dan past! (100% to‘liq qamrov).
  - KVK-EN (*Night and Day*, 45–271-betlar): 227 sahifadan 0 tasi 98% dan past!
  - OMS-EN (*The Old Man and the Sea*, [9]–[125]): 117 sahifadan 0 tasi yetishmaydi.
  - OMS-UZ (*Chol va dengiz*, 1–46-betlar): 46 sahifadan 0 tasi 98% dan past!
- **1.3 To‘liqlik Isboti (Completeness Proof - `data/completeness_proof_v3.json`):**
  - KVK-UZ: `ayvon*` (49 ta), `Poshshaxon*` (79 ta), `qaror*` (14 ta), `yura[kg]*` (42 ta), `qishlo[qg]*` (115 ta), `ko‘ngil*` (180 ta) — 100% PASS!
  - OMS-EN: `heart*` (8 ta), `shark*` (66 ta) — 100% PASS!
  - OMS-UZ: `akula*` (90 ta), `yura[kg]*` (8 ta), `qaror*` (1 ta) — 100% PASS!
- **Chol va dengiz OCR xatolari reestri (`data/ocr_errors_oms.json`):**
  - 26 ta xato turi (`chnqishim` ➔ `chiqishim`, `uchui` ➔ `uchun`, `unnng` ➔ `uning`) aniqlandi va tuzatildi. Ismlar lug‘atiga `santyago` qo‘shildi.

### Part 2: Tayanch Nuqtalarga Asoslangan Tekislash (Anchored Alignment v3)
- **18 ta tayanch nuqta (Fixed anchors) bo‘yicha bo‘laklab tekislash amalga oshirildi:**
  - KVK 18 ta tayanch nuqtasi (UZ 3 ↔ EN 46 dan UZ 265 ↔ EN 271 gacha) va OMS 2 ta tayanch nuqtasi qat'iy bog'landi (100% o‘tdi).
  - Kutilgan sahifadan median mutlaq siljish (drift): **KVK: 0.54 sahifa**, **OMS: 1.03 sahifa** (talab: $\le 2.0$ sahifa — to‘liq bajarildi).
  - Bitta ham o‘zbekcha segment tashlab ketilmadi (Zero-loss qoidasi): tarjimasi topilmagan segmentlar 1:0 qilib saqlandi.
  - **Defect 2 tuzatildi (`aln-kvk-01789`):** UZ 80 *Ancha nari-beri gaplardan keyin ertaga erta bilan Xadichaxonni cho‘loq azayimxonnikiga yuborishga qaror berildi...* to‘g‘ri bog‘landi: EN 111 *After several impractical suggestions, they decided that Xadichaxon would go to the healer tomorrow morning.* (Drift: 0 sahifa).
  - V2 ➔ V3 ID xaritasi (`data/v2_to_v3_mapping.json`) tuzildi, oldingi tekshiruv belgilari saqlandi.
  - Jami toza va tekislangan korpus hajmi: **8,355 ta parallel juftlik** (KVK: 6,823 ta, OMS: 1,532 ta).

### Part 3 & 4: Qidiruv Barqarorligi va Nomzodlar 2-Raundi
- **20 ta so‘rovli test to‘plami (`scripts/test_20_queries.py`): 100% PASS.**
  - 0 ta HTTP 500 xatosi; qidiruv javob vaqti barcha so‘rovlarda < 1.5 soniya (o‘rtacha 0.4s).
  - Ikkala kitob qidiruvda teng ishtirok etmoqda (`yurak` va `chol` so‘rovlarida Cho‘lpon va Hemingway natijalari mavjud).
  - Sahifalash $\le 50$ chekloviga to‘liq mos.
- **Nomzodlar filtri va qoliplar yangilandi:**
  - Yopiq so‘z turkumlari (olmoshlar, ko‘makchilar, bog‘lovchilar, yuklamalar, modal so‘zlar, sonlar) nomzodlardan chetlatildi.
  - So‘z turkumi noma’lum so‘zlar "so‘z turkumi aniqlanmagan" deb belgilandi (hech qachon "ot" deb xato standartlashtirilmaydi).
  - Ega + kesim: 3-shaxs egalik shaklida lemmalashtirildi (`ko‘ngli tushmoq`, `yuragi urmoq`).
  - Yordamchi fe’llar (`-a/-y boshlamoq`, `-ib qo‘ymoq`, `-ib ketmoq`) bosh leksik fe’lga qaytarildi.
  - `Ot + ot` qoliplari ommaviy ko‘rinishdan ajratilib, faqat admin ko‘rinishiga o‘tkazildi.
  - Shovqin birliklar (`ko‘ngil uni`, `ikkala ko‘ngil`, `nomer qaror`, `chol yurak`, `ko‘ngil boshlamoq`) bartaraf etildi.

### Part 5, 6, 7 & S4: Ma'lumotnoma Bazasi, Interfeys, Ish Maydoni va Qoidalar
- **Ma'lumotnoma bazasi:** Rad etilgan yozuvlar yashirildi (`public_visible: false`), `col-gen-1` soxta manbadan tozalandi va haqiqiy korpus misoli ulandi, `colloc-6159` va `colloc-6257` tuzatildi.
- **Interfeys:** Barcha `javascript:void(0)` dead-end havolalari olib tashlandi, URL `?lang=uz|en|ru` orqali to‘liq boshqariladi, "Manbalar va huquqlar" sahifasida aniq 4 ta asar pasporti qoldirildi, Statistika sahifasida 3.1, 3.2, 3.3 jadvallari live hisoblangan empirik sonlar bilan to‘ldirildi.
- **Annotatsiya ish maydoni:** 1.1.4 4 qadamli qaror protsedurasi joriy etildi, `annotator2` roli va Cohen's Kappa hisoblash integratsiya qilindi, CSV va XLSX formatlarida eksport tugmalari qo‘shildi.
- **Doimiy qoidalar (Section S4):** `PROJECT_CONTEXT.md` ga 7 ta doimiy qoida kiritildi.

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
