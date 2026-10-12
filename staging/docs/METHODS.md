# TILCOR v2.0 — Ilmiy Metodologiya (METHODS.md)

Dissertatsiya mavzusi: *"TARJIMA VA TENG MATNLAR PARALLEL KORPUSIDA O‘ZARO FAOL BIRIKUVCHI (KOLLOKATSION) SO‘ZLAR TADQIQI (o‘zbek va ingliz tillari misolida)"*

---

## 1. Uch Qatlamli Ma'lumotlar Arxitekturasi (Three-Layer Model)
Tadqiqotning ilmiy ishonchliligi quyidagi qat'iy ajratilgan uch qatlam orqali kafolatlanadi:
1. **1-Qatlam: Xom Ma'lumotlar (Raw Layer):**
   - PDF fayllardan olingan harflar, jumlalar, tinish belgilari o‘zgarmagan holda saqlanadi (`raw_text`).
   - Hech qanday normallashtirish asl matn ustida bajarilmaydi; normallashtirish faqat qidiruv maydonida (`clean_text`) yuritiladi.
2. **2-Qatlam: Avtomatik Takliflar (Automatic Suggestions Layer):**
   - Gale-Church / Hunalign algoritmlari, spaCy / NLTK POS-tagging, leksikografik qidiruv vositalari.
   - Bu qatlamdagi barcha ma'lumotlar `draft` maqomiga ega bo‘lib, ilmiy statistikaga qo‘shilmaydi.
3. **3-Qatlam: Inson Tasdiqlagan Annotatsiyalar (Human-Confirmed Layer):**
   - Tadqiqotchi (`admin`) va ilmiy rahbar (`reviewer`) tomonidan bevosita tekshirilib tasdiqlangan annotatsiyalar (`is_verified = 1`, `is_final = 1`).
   - Faqat ushbu qatlam dissertatsiya avtoreferati, bobi va taqdimotidagi jadvallarga asos bo‘ladi.

---

## 2. Ikki Tomonlama Badiiy Manbalar (Bidirectional Corpus Design)
Dissertatsiya talabiga ko‘ra korpus ikki yo‘nalishli empirik bazaga ega:
1. **O‘zbekcha Asl Nusxa ➔ Inglizcha Tarjima (UZ ➔ EN):**
   - Abdulhamid Cho‘lpon: «Kecha va kunduz» (272 bet) ➔ Christopher Fort: «Night and Day» (235 bet).
   - O‘zbek milliy koloritidagi kollokatsiyalarning ingliz tiliga funksional-adekvat tarjima qilinishi tadqiq etiladi.
2. **Inglizcha Asl Nusxa ➔ O‘zbekcha Tarjima (EN ➔ UZ):**
   - Ernest Hemingway: «The Old Man and the Sea» (52 bet) ➔ Ibrohim G‘afurov: «Chol va dengiz» (46 bet).
   - Lakonik inglizcha kollokatsiyalarning o‘zbek tilidagi ekvivalentligi o‘rganiladi.
   - Robert Louis Stevenson: «Treasure Island» (142 bet) ➔ Sharif Rizo: «Xazinalar oroli» (216 bet — skanerlangan rasm, OCR holati tekshirilmoqda).

---

## 3. Matematik-Statistik Hisoblash Standartlari
Barcha kollokatsion metrikalar sun'iy intellekt xomxayoli bilan emas, quyidagi standart formulalar asosida hisoblanadi:

1. **Mutual Information (MI-Score):**
   $$MI(w_1, w_2) = \log_2 \frac{f(w_1, w_2) \cdot N}{f(w_1) \cdot f(w_2)}$$
   - $f(w_1, w_2)$ — kollokatsiyaning korpusdagi birgalikdagi chastotasi.
   - $f(w_1), f(w_2)$ — komponentlarning alohida chastotasi.
   - $N$ — korpusdagi umumiy tokenlar soni.

2. **T-Score (Student's t-test):**
   $$t = \frac{f(w_1, w_2) - \frac{f(w_1) \cdot f(w_2)}{N}}{\sqrt{f(w_1, w_2)}}$$
   - Barqaror bog‘lanishning statistik ishonchlilik darajasi ($t \ge 2.0$ — statistik ahamiyatli).

3. **logDice:**
   $$\text{logDice} = 14 + \log_2 \frac{2 \cdot f(w_1, w_2)}{f(w_1) + f(w_2)}$$
   - Chastota o‘zgarishiga chidamli, korpus hajmiga bog‘liq bo‘lmagan assotsiativ o‘lchov.

---

## 4. Matn Ajratish, Segmentlash va Sifat Nazorati Standartlari (4-Bosqich)

### 4.1. Kolontitul va Sahifa Raqamlarini Ajratish
- Sahifa tepasidagi asar nomi, muallif, veb-manzil reklama satrlari (`kutubxonachi.uz`, `Asiaing.com`) va raqamlar matn tanasidan ajratilib, `header_lines` va `printed_page_num` maydonlariga o‘tkaziladi.
- Sahifa pastidagi snoskalar (masalan, `1 Qo‘ysang-chi!`) tanadan ajratilib, `footer_lines` va alohida izoh segmentiga kiritiladi.

### 4.2. Satr Oxiridagi So‘z Bo‘linishlarini Birlashtirish (Dehyphenation)
- Satr oxirida tire (`-`) bilan tugab, keyingi satrda davom etgan so‘zlar qoidaga muvofiq birlashtiriladi (masalan, `hay-` + `batli` $\rightarrow$ `haybatli`).
- Agar so‘z qo‘shma so‘z bo‘lsa (masalan, `to‘r-po‘r`, `duk-duk`), tire saqlanadi.

### 4.3. Dialog va Iqtibos Belgilarini Asl Nusxada Saqlash
- O‘zbekcha dialog tirelari (`—`, `–`, `-`), tirnoqlar (`«`, `»`, `“`, `”`) va ko‘p nuqtalar (`…`) aynan asl nusxadagi holatida saqlanadi.

### 4.4. Tillarga Mos Jumla Chegaralarini Belgilash (Sentence Boundary Disambiguation)
Nuqta har doim ham jumla tugaganini bildirmaydi:
1. **O‘zbekcha qisqartmalar:** `h.k.`, `sh.k.`, `q.`, `b.`, `prof.`, `dots.`, `akadem.`, `filol.`, `fan.` kabi qisqartmalardan so‘ng jumla bo‘linmaydi.
2. **Inglizcha qisqartmalar:** `Mr.`, `Mrs.`, `Ms.`, `Dr.`, `Prof.`, `St.`, `vs.`, `etc.`, `i.e.`, `e.g.`, `no.`, `vol.` dan keyin jumla bo‘linmaydi.
3. **Initsial va Murakkab Ismlar:** `Di Madjio`, `E. Hemingway`, `A. Cho‘lpon` kabi ism initsiallari matn yaxlitligi sifatida saqlanadi.

### 4.5. Tokenizatsiya Qoidasi (Token Count Standard)
Korpusdagi har bir sahifa va jumla uchun so‘zlar soni quyidagi standart leksema qolipi bo‘yicha hisoblanadi:
- Formula / Pattern: `\b[\w\u02bb\u02bc'-]+\b`
- Ushbu qolip barcha alfanumerik so‘zlarni, o‘zbekcha `ʻ` (U+02BB) va `ʼ` (U+02BC) harf hamda tutuq belgilarini, inglizcha qisqartma apostroflarini (`don't`, `man's`) va qo‘shma so‘zlarni (`sea-cook`, `old-man`) yaxlit token sifatida hisoblaydi.

### 4.6. Sifat Nazorati Bayroqlari (Quality Flags)
- `OK` — Sahifa to‘liq raqamli matn qatlamiga ega, xatolik aniqlanmadi.
- `FOOTNOTE_DETECTED` — Sahifa pastida izoh/snoska aniqlanib, tanadan ajratildi va alohida izoh segmentiga o‘tkazildi.
- `HYPHEN_JOINED` — Satr oxirida bo‘lingan so‘z muvaffaqiyatli birlashtirildi.
- `FRONT_MATTER` — Muqova, titul varag‘i, mundarija, nashriyot ma'lumotlari.
- `AFTERWORD` — Asar oxiridagi ilmiy maqola / so‘ngso‘z (Cho‘lpon «Kecha va kunduz», 266–272-betlar).
- `GLOSSARY` — Asar oxiridagi leksik glossariy (Fort «Night and Day», 230–235-betlar).
- `BIBLIOGRAPHY` — Asar oxiridagi bibliografiya (Hemingway «The Old Man and the Sea», 51–52-betlar).
- `EMPTY_PAGE` — Matn qatlami bo‘lmagan yoki bo‘sh sahifa.
- `NO_TEXT_LAYER_MISSING` — Skanerlangan grafik rasm, matn qatlami mavjud emas (Stivenson «Xazinalar oroli», 216 bet — 0 generatsiya qoidasi asosida karantinda).

### 4.7. Stratifikatsiyalangan Qo‘lda Tekshiruv Metodologiyasi (Stratified Quality Audit)
Har bir matndan 10 ta sahifa (Boshidan 3 ta, O‘rtasidan 4 ta, Oxiridan 3 ta) tanlab olinib, 4 ta xatolik mezoni bo‘yicha tekshirildi:
1. Kolontitul sarlavhalarining matnga sizishi (Header leakage)
2. Sahifa raqamlari yoki footerning matnga sizishi (Footer leakage)
3. Noto‘g‘ri yoki qolib ketgan chiziqchalar (Bad / unjoined hyphens)
4. Noto‘g‘ri bo‘lingan jumlalar (False sentence splits)

---

## 5. Parallel Jumlalarni Tekislash Metodologiyasi (5-Bosqich)

### 5.1. Oltin Namuna (Gold Standard: `gold_v1`) Dizayni
- Algoritmlarni baholash uchun har bir kitobdan boshidan (50 juftlik), o‘rtasidan (50 juftlik) va oxiridan (50 juftlik) jami 150 tadan, umumiy **300 ta inson tomonidan tekshirilgan oltin parallel juftlik** muzlatildi (`data/gold_v1.json` va `gold_alignments` jadvali).
- 1:1, 1:2, 2:1 kabi barcha transformatsion munosabatlar inobatga olindi.

### 5.2. Mahalliy Algoritmlar Taqqoslanishi
1. **Method A (Length-based Gale-Church + 24k Lug‘at Ankori):**
   - Belgi uzunliklari nisbatiga asoslangan Geyl-Chyorch xarajati:
     $$\delta = \frac{len(target) - len(source) \cdot c}{\sqrt{len(source) \cdot s^2 + 0.1}}$$
     $$\text{cost}_{GC} = -100 \log \left( 2 \cdot (1 - \Phi(|\delta|)) \right)$$
   - `data/dictionary.json` dagi 24,554 ta o‘zbekcha-inglizcha so‘z juftliklaridan leksik ankor chegirmasi: har bir tasdiqlangan lug‘at mosligi uchun $-30.0$ ball xarajat kamaytiriladi.
2. **Method B (Lexical-Anchor DP / Jaccard + Simvol 3-gram):**
   - Lug‘at kengaytmasi asosidagi Jaccard o‘xshashligi va 3-gram simvol o‘xshashligi kombinatsiyasi.

### 5.3. Aniq Hisoblash Qoidalari (Precision, Recall, F1)
- **Precision (Aniqlik):** $\frac{\text{To‘g‘ri bashorat qilingan juftliklar}}{\text{Jami bashorat qilingan juftliklar}}$
- **Recall (To‘liqlik):** $\frac{\text{To‘g‘ri bashorat qilingan juftliklar}}{\text{Jami oltin juftliklar (Gold)}}$
- **F1-Score:** $\frac{2 \cdot P \cdot R}{P + R}$
- *Natija:* Method A ikkala asar bo‘yicha ham ustunlik qildi (Cho‘lpon: F1 = 0.5508 vs 0.3206; Hemingway: F1 = 0.4834 vs 0.4536).

### 5.4. Ko‘rib Chiqish Navbati (Review Queue) Qoidalari
- **ORIGINAL doim chapda:** Cho‘lponda chapda o‘zbekcha asl nusxa; Hemingway va Stevensonda chapda inglizcha asl nusxa.
- **Kontekst:** Faol juftlik atrofida $\pm 2$ ta qo‘shni segment ko‘rsatiladi.
- **Xom ball (Raw score):** Algoritm nomi va xarajat soni ko‘rsatiladi (masalan, `gale_church_dict_v1: 15.11`), hech qachon `% moslik` tarzida ko‘rsatilmaydi.
- **Hech narsa avtomatik tasdiqlanmaydi:** Yuqori xarajatli yoki n:m juftliklar `needs_review`, qolganlari `draft` maqomida saqlanadi. Faqat tadqiqotchi harakatidan so‘ng `confirmed` bo‘ladi.

---

## 6. Kollokatsiyalar: Ma'lumotnoma Ro‘yxati va Korpus Uchrashlari (6-Bosqich)

### 6.1. Ikki Alohida Ob'ekt: `lexicon_entries` vs `collocation_occurrences`
- **`lexicon_entries` (Lug‘aviy ma'lumotnoma):** 6,546 ta birikmadan iborat ilmiy manba ro‘yxati (`provenance = "user-supplied reference list: collocations_full.json"`). Kitobda topilmagan yozuvlar hech qachon korpusda topilgandek ko‘rsatilmaydi ($0..n$ ta uchrashuv).
- **`collocation_occurrences` (Haqiqiy matn uchrashlari):** Faqat tasdiqlangan parallel jumlalar va aniq PDF betlariga bog‘langan real kontekstual uchrashlar.

### 6.2. Tozalash Navbati (Clean-up Queue)
- Birorta ham yozuv o‘chirilmaydi. Xatoli/shubhali yozuvlar `status = 'needs_cleanup'` holatiga o‘tkaziladi:
  - `REPEATED_TOKENS`: takrorlangan so‘zlar (*nice nice nice*).
  - `PATTERN_MISMATCH_SINGLE_WORD`: qo‘shma qolipda bitta so‘z kelishi.
  - `UNTRANSLATED_CALQUE_COPY`: tarjima qilinmasdan inglizcha so‘z aynan nusxalangan holatlar.
  - `TEMPLATE_PLACEHOLDER`: shablon matnlar (*Kontekstdan tasdiqlanmoqda*).

### 6.3. Nomzodlarni Qazib Olish (Candidate Extraction)
1. **Ingliz tili (NLTK POS + Lemmatizer):**
   - Qoliplar: `Adj+Noun`, `Verb+Noun`, `Adv+Verb`, `Noun+of+Noun`.
   - 50 ta nomzodlik tekshiruvda **100.00% aniqlik (Precision)** qayd etildi.
2. **O‘zbek tili (Ierarxik Morfologik Analizator):**
   - Qoliplar: `Sifat+Ot`, `Ot+Fe’l`, `Ravish+Fe’l`, `Ot+Ot`, `Fe’l+Fe’l`.
   - 200-tokenlik oltin namunada negiz aniqligi 83.57%, POS aniqligi 75.59%, morfologik xatolik 24.41% ni tashkil etdi (cheklovlar `LIMITATIONS.md` da hujjatlashtirildi).
   - 50 ta nomzodlik tekshiruvda **96.00% aniqlik (Precision)** qayd etildi.
   - Barcha yangi nomzodlar qat'iy ravishda inson tasdiqlaguniga qadar **"SUGGESTION"** maqomida qoladi va statistikaga qo‘shilmaydi.

### 6.4. Lemmaga va Tutuq Belgisiga Sezgir Qidiruv (Lemma-Aware Search)
- So‘rov (masalan, *yurak urmoq*) o‘zbekcha affiks stripping va fonologik variantlar (*yurag-i*, *yurak-dan*, *ur-di*, *ur-moqda*) orqali kengaytiriladi.
- Ushbu qidiruv korpusdagi *yurakdan urgan ekan*, *yuragi urgan holda*, *yuragi sust urmoqda* kabi barcha grammatik tuslanishlarni topish imkonini beradi.

---

## 7. Tarjima Mutanosibligi va Annotatsiya Ish Joyi (Stage 7)

### 7.1. Taksonomiya Tuzilishi (Versiya 1.0)
Dissertatsiyaning 1.2, 3.1, 3.2 va 3.3-fasllari talablari asosida relyatsion `taxonomies` jadvaliga 40 ta rasmiy parametr kiritildi:
1. **Birlik turi (1.1-fasl):** `kollokatsiya` (barqaror birikma), `erkin_birikma`, `frazeologik_birlik` (idiom), `noaniq`.
2. **Struktur qolip (3.1-fasl):** `Fe’l+Ot`, `Sifat+Ot`, `Ot+Fe’l`, `Ravish+Fe’l`, `Ot+Ot`, `boshqa`.
3. **Semantik guruh (3.1-fasl):** `inson_ruhiyati`, `tabiat_borliq`, `harakat_holat`, `ijtimoiy_munosabat`, `nutq_tafakkur`, `moddiy_borliq`, `boshqa`.
4. **Ekvivalentlik turi (3.2-fasl):** `toliq_ekvivalent`, `qisman_ekvivalent`, `strukturaviy_transformatsiya`, `obraz_almashtirish`, `tasviriy_tarjima`, `bir_sozga_siqilgan`, `tushirib_qoldirilgan`, `tarjimada_qoshilgan`.
5. **Tarjima strategiyasi (1.2, 3.2):** `kalka`, `modulyatsiya`, `generalizatsiya`, `konkretizatsiya`, `kompensatsiya`, `izoh`, `boshqa`.
6. **Lingvomadaniy realiya (3.3-fasl):** `yoq`, `etnografik`, `geografik`, `ijtimoiy_siyosiy`, `diniy_mafkuraviy` + ilmiy dalil izohi.
7. **Ishonch darajasi:** `yuqori`, `orta`, `past` + dalil izohi.

### 7.2. Annotatsiya Ish Oqimi (Workflow)
- **ORIGINAL doim chapda:** Cho‘lponda chap ustunda o‘zbekcha asl matn (`book-cholpon-uz`), o‘ngda inglizcha tarjima; Hemingwayda chap ustunda inglizcha asl matn (`book-hemingway-en`), o‘ngda o‘zbekcha tarjima.
- **Ekvivalent tanlash:** Tadqiqotchi o‘ng ustundagi tarjima matnidan mos parchani sichqoncha bilan belgilaydi yoki `[To‘g‘ridan-to‘g‘ri ekvivalenti yo‘q]` tugmasini bosadi.
- **Statuslar:** `draft` (qoralama) va `confirmed` (tasdiqlangan). Faqat tasdiqlangan annotatsiyalar III bob statistik jadvallariga o‘tadi.

### 7.3. Tarjima Mutanosibligi Matritsasi (Correspondence Matrix)
- 6 ta struktur qolip $\times$ 8 ta ekvivalentlik turi kesimidagi chastotalar matritsasi.
- Har bir katakka bosganda (Drill-down) tegishli aniq parallel jumlalar va ularning asl PDF sahifa raqamlari ochiladi.

### 7.4. Ekspertlar Kelishuvi (Cohen's Kappa)
- Ikki annotator (`admin` va `reviewer`) mustaqil belgilagan yozuvlar bo‘yicha $\kappa$ koeffitsiyenti:
$$\kappa = \frac{P_o - P_e}{1 - P_e}$$
- Qat'iy ilmiy standart: $\kappa \ge 0.61$ (Substantial / Almost Perfect) bo‘lgandagina annotatsiyalar himoya uchun qabul qilinadi.

### 7.5. AI Taklifi Cheklovi (Rule R3)
- AI taklifi faqat bitta jumla uchun qoralama sifatida taklif beradi, standart holatda o‘chirilgan bo‘ladi, kitobning to‘liq matnini olmaydi va hech qachon avtomatik tarzda bazaga yozilmaydi.

---

## 8. Statistika: Haqiqiy Hisob-Kitob va Formulalar (Stage 8)

### 8.1. Korpus Hajmi va Leksik Boylik
- **Tokenizer qoidasi:** `\b[\w\u02bb\u02bc'-]+\b` (kichik harflarga keltirilgan, tutuq belgilari va chiziqchalar saqlangan).
- **Normallashtirilgan chastota:** 10,000 tokenga normallashtirish:
$$\text{NormFreq} = \frac{\text{RawFreq}}{N} \times 10{,}000$$
(Doim maxraj $N$ ko‘rsatiladi).

### 8.2. 2×2 Kontingentlik Jadvali va Assotsiatsiya Mezonlari
Har bir $(w_1, w_2)$ birikmasi uchun:
- $O_{11}$ — birga uchrash chastotasi;
- $R_1 = O_{11} + O_{12}$ — $w_1$ ning umumiy korpus chastotasi;
- $C_1 = O_{11} + O_{21}$ — $w_2$ ning umumiy korpus chastotasi;
- $N$ — til yoki asar bo‘yicha jami tokenlar soni.

1. **Kutilgan chastota (Expected Frequency):**
$$E_{11} = \frac{R_1 \cdot C_1}{N}$$

2. **Pointwise Mutual Information (MI):**
$$MI = \log_2 \left( \frac{O_{11} \cdot N}{R_1 \cdot C_1} \right)$$
*(Izoh: MI noyob va kam uchraydigan juftliklarga yuqori ball berishga moyil).*

3. **Student's t-score:**
$$t = \frac{O_{11} - E_{11}}{\sqrt{O_{11}}}$$
*(Izoh: t-score grammatik va yuqori chastotali birikmalarni afzal ko‘radi).*

4. **Dunning Log-Likelihood ($G^2$, 1993):**
$$G^2 = 2 \sum_{i \in \{1,2\}} \sum_{j \in \{1,2\}} O_{ij} \ln \left( \frac{O_{ij}}{E_{ij}} \right)$$
*(Izoh: Kichik va o‘rta hajmli korpuslar uchun eng mustahkam ko‘rsatkich).*

### 8.3. Kirish va Chiqish Sonlarini Birgalikda Saqlash
Har bir yozuv bazadagi `association_measures` jadvalida barcha $O_{11}, O_{12}, O_{21}, O_{22}, R_1, C_1, N$ sonlari bilan birga saqlanadi. Kirish soni mavjud bo‘lmaganda ball hisoblanmaydi.

### 8.4. III Bob Jadvallari va Takrorlanuvchanlik
- Jadvallar (3.1, 3.2, 3.3, 3.4, 3.5, 3.6) **FAQAT tasdiqlangan annotatsiyalar** (`is_confirmed = 1`) asosida generatsiya qilinadi.
- Har bir foiz yonida uning maxraji ($n = \dots$) qat'iy ko‘rsatiladi.
- Barcha jadvallar va filtrlash parametrlari JSON/CSV holatida `settings_snapshot` bilan to‘liq eksport qilinadi.

---

## 9. Qidiruv, KWIC va Eksport Standartlari (Stage 9)

### 9.1. KWIC (Key Word in Context) Konkordans Mexanizmi
- **Kontekst oynasi:** $\pm 1$ dan $\pm 10$ gacha so‘z (standart: $\pm 6$ so‘z).
- **Format:** Chap kontekst (Right-aligned), Tugun so‘z (Markazda, ajratilgan), O‘ng kontekst (Left-aligned).
- **Saralash imkoniyatlari:**
  1. Matndagi tartib (Position in text stream)
  2. Chap kontekst bo‘yicha alifbo tartibida (First word to the left)
  3. O‘ng kontekst bo‘yicha alifbo tartibida (First word to the right)
- **Bog‘lanish:** Har bir KWIC satri segment ID va tegishli PDF sahifa raqami (`pdf_page_num`) bilan uzluksiz bog‘langan.
- **Tezlik:** Katta hajmli matnlarda sub-50 ms tezlikni kafolatlash uchun tekislash (alignment lookup) paginatsiya qilingan sahifa (50 qator) doirasida bajariladi.

### 9.2. Apostrof va Tutuq Belgilariga Sezgirmaslik (Rule R8)
- O‘zbek tilidagi barcha tutuq belgilari (`ʻ`, `ʼ`, `'`, `‘`, `’`) qidiruvda bir xil normal shaklga keltiriladi (`NORM_APO`).
- `ko'ngil`, `koʻngil` (U+02BB) va `ko‘ngil` (U+2018) qidirilganda aynan bir xil to‘liq natijalar to‘plami qaytadi.

### 9.3. Parallel Matnlar Ko‘rinishi (Parallel Alignment View)
- Doimiy qat'iy qoida: Asl nusxa (Original / Source) doimo chap ustunda, Tarjima (Target) doimo o‘ng ustunda ko‘rsatiladi.

### 9.4. Eksport Standartlari va Aylana Sinovi (Export Round-Trip)
- **Faqat ko‘rinadigan 50 ta emas, balki filtrlangan BARCHA natijalar** eksport qilinadi.
- **Formatlar:**
  - Excel (`.xlsx` - `openpyxl` yordamida toza uslublar bilan).
  - CSV (Microsoft Excel-da o‘zbekcha harflar buzilmasligi uchun UTF-8 BOM `\xef\xbb\xbf` bilan).
- **Metadata:** Fayl nomi generatsiyasi qidiruv so‘rovi va sana-vaqt tamg‘asini o‘z ichiga oladi: `tilcor_kwic_{query}_{timestamp}.xlsx`.
- **Aylana sinovi (Round-trip test):** Eksport qilingan fayllar qayta o‘qilganda ma'lumotlar yo‘qolishi va buzilishi 0% ni tashkil etadi.

### 9.5. XSS va Xavfsizlik (Defect D12 Tuzatish)
- Brauzerda xom HTML kiritish (`toast.innerHTML`, `table.innerHTML` tekshirilmagan holda) butunlay xavfsiz DOM usullari (`textContent`) bilan almashtirildi. Barcha qidiruv parametrlari SQL parametrli so‘rovlari orqali himoyalangan.




