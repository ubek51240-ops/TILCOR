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
   - Abdulhamid Cho‘lpon: «Kecha va kunduz» (Toshkent, «Sharq» NMK, 2000, 272 bet) ➔ Christopher Fort: «Night and Day» (Academic Studies Press, 2019, ISBN 9781644690482, DOI 10.1515/9781644690482, 235 bet).
   - O‘zbek milliy koloritidagi kollokatsiyalarning ingliz tiliga funksional-adekvat tarjima qilinishi tadqiq etiladi.
2. **Inglizcha Asl Nusxa ➔ O‘zbekcha Tarjima (EN ➔ UZ):**
   - Ernest Hemingway: «The Old Man and the Sea» (Charles Scribner's Sons, 1952, 52 bet) ➔ Ibrohim G‘OFUROV: «Chol va dengiz» (Toshkent, «Yosh gvardiya», 1986; manbalarda: G‘afurov, 46 bet).
   - Lakonik inglizcha kollokatsiyalarning o‘zbek tilidagi ekvivalentligi o‘rganiladi.
   - *Eslatma:* R. L. Stevenson («Xazinalar oroli») tadqiqotchi qarori bilan korpusdan butunlay chiqarilgan.

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

### 4.5. Sifat Nazorati Bayroqlari (Quality Flags)
- `OK` — Sahifa to‘liq matn qatlamiga ega, xatolik aniqlanmadi.
- `FOOTNOTE_DETECTED` — Sahifa pastida izoh/snoska ajratib olindi.
- `LOW_TEXT_VOLUME` — Sahifadagi belgilar soni 100 tadan kam (sarlavha yoki bob boshi).
- `EMPTY_PAGE` — Bo‘sh sahifa.
- `NO_TEXT_LAYER` — Raqamli matn qatlami yo‘q (skanerlangan rasm, OCR talab etiladi).

---

## 5. Morfologik So‘z Oilasini Qiyoslash Moduli (Word Family Matching Module - 2-qadam)

2-bosqich talablariga binoan, qidiruv tizimida so‘zning faqat yalang‘och shakli emas, butun leksik-morfologik oilasi (`word family`) aniqlanadi va parallel gaplar hamda kollokatsiyalarda bir vaqtning o‘zida qiyoslanadi.

### 5.1. O‘zbek Tili Morfologik Qoidalari (`word_family.py`)
1. **Apostrof va Grafema Standartlashtirish:**
   - Qidiruv parametrlarida barcha apostrof variantlari (`ʻ`, `‘`, `'`, `` ` ``, `’`) yagona xalqaro standartga normallashtiriladi:
     - `o‘` va `g‘` harflari uchun: `‘` (`\u02bb` / `\u2018`);
     - Tutuq belgisi (bo‘g‘in ajratish) uchun: `ʼ` (`\u02bc` / `\u2019`).
   - *Qoida:* Asl matnlar bazada o‘zgartirilmaydi; normallashtirish faqat qidiruv xeshlarida qo‘llaniladi.
2. **Fonetik O‘zgarishlar va Singarmonizm:**
   - **Jaranglashish (undosh almashinuvi):** `k` $\rightarrow$ `g` (*yurak* $\rightarrow$ *yuragi*, *tilak* $\rightarrow$ *tilagim*); `q` $\rightarrow$ `g‘` (*qishloq* $\rightarrow$ *qishlog‘i*, *buloq* $\rightarrow$ *bulog‘i*).
   - **Toriq unli tushishi (vowel drop):** Egalik qo‘shimchasi oldidan ikkinchi bo‘g‘indagi tor unli tushishi (*burun* $\rightarrow$ *burni*, *o‘g‘il* $\rightarrow$ *o‘g‘li*, *ko‘ngil* $\rightarrow$ *ko‘ngli*, *bag‘ir* $\rightarrow$ *bag‘ri*).
3. **Qo‘shimchalar Zanjiri (Suffix Chaining):**
   - Ko‘plik (`-lar`), egalik (`-im`, `-ing`, `-i`, `-imiz`, `-ingiz`), kelishik (`-ning`, `-ni`, `-ga`, `-ka`, `-qa`, `-da`, `-dan`), yasovchi (`-li`, `-siz`, `-lik`, `-chi`, `-dor`, `-kor`) qo‘shimchalar qat'iy ketma-ketlik bo‘yicha tekshiriladi.
   - Soxta mosliklardan himoya (False Match Guard): So‘z o‘zagi kamida 3 harfdan iborat bo‘lishi va qolgan qism to‘liq ruxsat etilgan grammatik zanjirga mos kelishi shart. Masalan, *yurak* so‘zi *yurakat* bilan moslashtirilmaydi.
4. **Guruhlash Tipologiyasi:**
   - `inflected` — Turlangan shakllar (*yuragi*, *yurakka*, *yuraklari*);
   - `derived` — Yasalgan so‘zlar (*yurakli*, *yuraksiz*, *yurakchan*);
   - `compound` — Qo‘shma va juft so‘zlar (*yurak-bag‘ir*, *ochiq-yurak*).

### 5.2. Ingliz Tili Morfologik Qoidalari (NLTK 3.10.3)
1. **Lematizatsiya:** NLTK `WordNetLemmatizer` orqali fe'l, ot, sifat shakllari asliga keltiriladi (*heart* $\leftrightarrow$ *hearts*; *decide* $\leftrightarrow$ *decided* $\leftrightarrow$ *deciding*).
2. **O‘zak va Derivatsiya:** `PorterStemmer` hamda WordNet `derivationally_related_forms()` leksik grafi orqali etimologik qardosh yasalishlar (*hearty*, *heartless*, *decision*, *decisive*) ajratiladi. Sinset sinonimlari (leksik adashishlar) qat'iy cheklangan.

### 5.3. Modullarning Xatolik Darajasi (Unit Test Natijalari)
- **O‘zbek tili testi (`scripts/test_word_family.py`):** 51 ta turlicha murakkab shakl (almashinuv, unli tushishi, zanjirlar, soxta nomzodlar) ustida o‘tkazildi:
  - Natija: **51 / 51 to‘g‘ri** $\rightarrow$ **0.00% xatolik darajasi**.
- **Ingliz tili testi (`scripts/test_word_family.py`):** 49 ta shakl ustida o‘tkazildi:
  - Natija: **49 / 49 to‘g‘ri** $\rightarrow$ **0.00% xatolik darajasi**.
