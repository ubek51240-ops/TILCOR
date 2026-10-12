# TILCOR v2.0 — Platforma Faktlar Varaqasi (PLATFORM FACTSHEET)

**«TARJIMA VA TENG MATNLAR PARALLEL KORPUSIDA O‘ZARO FAOL BIRIKUVCHI (KOLLOKATSION) SO‘ZLAR TADQIQI»**  
*PhD himoyasi uchun rasmiy bir sahifalik ma'lumotnoma (Baza holati: 2026-10-12).*

---

### 📊 Asosiy Korpus Ko‘rsatkichlari (Live Database Counts)

| Ko‘rsatkich | Son Qiymati | Izoh / Ilmiy Asosi |
| :--- | :---: | :--- |
| **Badiiy Asarlar soni** | **3** | Cho‘lpon, Hemingway, Stevenson |
| **Nashrlar soni (Editions)** | **6** | Bosma va elektron akademik nashrlar |
| **Matn Qatlamlari (Texts)** | **6** | 5 ta faol matn, 1 ta karantinda (Stevenson UZ: 0 matn qatlami) |
| **PDF Sahifalari soni** | **963** | PyMuPDF orqali ekstraksiya qilingan betlar |
| **Jumla va Dialog Segmentlari** | **23,762** | Jumla va dialog chegaralari to‘liq ajratilgan |
| **Jami So‘z Qamrovi (Tokens)** | **303,393** | `\b[\w\u02bb\u02bc'-]+\b` qolipi asosida |
| **Unikal Leksik Shakllar (Types)**| **40,276** | So‘z shakllari lug‘ati |
| **Parallel Juftliklar (Alignments)**| **7,391** | Anchor-window usulida tekislangan parallel jumlalar |
| **Oltin Standart Juftliklari (`gold_v1`)**| **300** | Ekspert tomonidan 100% qo‘lda tekshirilgan oltin namuna |
| **Leksik Ma'lumotnoma (Lexicon)** | **6,546** | Foydalanuvchi taqdim etgan leksikografik ma'lumotlar |
| **Kollokatsiya Uchrashuvlari** | **469** | Matnlarda bevosita tasdiqlangan birikmalar |
| **Taksonomik Parametrlar** | **40** | Prompt 7 taksonomiyasi (7 ta asosiy toifa, v1.0) |
| **2×2 Assotsiatsiya Hisoblari** | **11,527** | $O_{11}, R_1, C_1, N$ asosidagi $MI, t$-score, $G^2$, NormFreq |
| **Baza Yaxlitligi (Foreign Keys)**| **0 xato** | SQLite ACID relyatsion modeli |

---

### 🔬 Asarlar Bo‘yicha Taqsimot

| Asar | Muallif / Tarjimon | Yo‘nalish | Sahifa | Segment | Token | Litsenziya |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **«Kecha va kunduz»** | A. Cho‘lpon (Asl nusxa) | UZ ➔ EN | 272 | 9,363 | 80,594 | Public Domain |
| **«Night and Day»** | Ch. Fort (Tarjima, 2020) | UZ ➔ EN | 235 | 7,695 | 99,721 | Protected (Fair Use) |
| **«The Old Man and the Sea»**| E. Hemingway (Asl nusxa, 1952)| EN ➔ UZ | 52 | 1,699 | 27,091 | Protected (Fair Use) |
| **«Chol va dengiz»** | I. G‘afurov (Tarjima, 1986) | EN ➔ UZ | 46 | 1,845 | 26,311 | Protected (Fair Use) |
| **«Treasure Island»** | R. L. Stevenson (Asl, 1883) | EN ➔ UZ | 142 | 3,160 | 69,676 | Public Domain |
| **«Xazinalar oroli»** | Sharif Rizo (Tarjima, 1974) | EN ➔ UZ | 216 | 0 | 0 | **Karantinda (0 matn)** |

---

### 🛡️ Tizim Xavfsizligi va Huquqiy Maqom
- **Qonuniy Asos:** O‘zbekiston Respublikasi «Mualliflik huquqi va turdosh huquqlar to‘g‘risida»gi Qonunining 19-moddasi (Ilmiy maqsadda erkin foydalanish).
- **Kirish Huquqi (RBAC):** Admin (Tadqiqotchi), Reviewer (Ilmiy rahbar), Guest (Kengash a'zolari).
- **Zaxiralash:** SHA-256 xesh nazorati bilan atomar kunlik nusxa olish va sinovdan o‘tgan qayta tiklash tizimi.
