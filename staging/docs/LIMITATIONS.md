# TILCOR v2.0 — Tadqiqot Cheklovlari (LIMITATIONS)

**Doktorlik dissertatsiyasi ilmiy xolisligi va shaffofligini ta'minlovchi rasmiy cheklovlar bayonnomasi.**

Ushbu hujjatda parallel korpusni yaratish, avtomatlashtirilgan tahlil va statistik hisob-kitoblar jarayonidagi barcha mavjud cheklovlar ochiq va ilmiy halollik bilan qayd etilgan.

---

### 1. Manbalar va Matn Qatlami Cheklovlari (Stevenson Karantini)
- Robert Louis Stevensonning «Xazinalar oroli» asarining o‘zbekcha tarjimasi (Sharif Rizo tarjimasi, G‘afur G‘ulom nashriyoti, 1974) manba PDF faylida **0 ta matn qatlamiga ega skanerlangan rasm** holatida mavjud bo‘lgan.
- Ilmiy soxtalashtirish (data fabrication) qat'iy taqiqlanganligi (Rule R1) sababli, ushbu tarjima korpusga sun'iy tarzda qo‘shilmadi, balki to‘liq `quarantined` holatida saqlandi. Korpus jami hisob-kitoblarida ushbu matn 0 segment va 0 token sifatida aks ettirilgan.

---

### 2. O‘zbek Tili Morfologik Analizatori Cheklovlari
- O‘zbek tili uchun yaratilgan yengil affiksli morfologik analizator (`scripts/uzbek_morphology.py`) qoidaga asoslangan (rule-based) model hisoblanadi.
- 213 ta tokendan iborat oltin benchmark sinovida quyidagi aniqlik ko‘rsatkichlari qayd etildi:
  - **Negiz (Stem) aniqligi:** **83.57%**
  - **So‘z turkumi (POS) aniqligi:** **75.59%**
  - **Xatolik darajasi:** **24.41%**
- Ayniqsa ko‘p ma'noli affikslar (`-lik`, `-siz`, `-dosh`) va qisqartmalar tahlilida noaniqliklar mavjud. Tadqiqotchi bu cheklovni bilgan holda, yakuniy ilmiy xulosalarni avtomatik tahlilga emas, balki ekspert annotatsiyasiga tayangan holda chiqargan.

---

### 3. Jumlalarni Avtomatik Tekislash (Alignment) Cheklovlari
- Gale-Church (1993) uzunlikka asoslangan algoritmi o‘zbek va ingliz tillarining tipologik farqlari (agglyutinativ vs flektiv/analitik) tufayli barcha hollarda to‘liq 1:1 aniqlik bermaydi.
- Oltin standart (`gold_v1`, 300 juftlik) bo‘yicha o‘lchangan F1 ko‘rsatkichi:
  - Cho‘lpon (UZ ➔ EN): **F1 = 0.51** (Precision: 0.55, Recall: 0.48)
  - Hemingway (EN ➔ UZ): **F1 = 0.41** (Precision: 0.44, Recall: 0.38)
- Shu sababli, 6,193 ta juftlik hech qachon avtomatik tarzda «tasdiqlangan» deb e'lon qilinmadi, balki tadqiqotchi ko‘rib chiqishi uchun `needs_review` navbatiga ajratildi.

---

### 4. Mualliflik Huquqi va Kirish Huquqlari Cheklovlari (Fair Use)
- Ernest Hemingwayning «The Old Man and the Sea» asari va Ibrohim G‘afurov hamda Christopher Fort tarjimalari mualliflik huquqi bilan himoyalangan (`protected`).
- O‘zbekiston Respublikasi «Mualliflik huquqi va turdosh huquqlar to‘g‘risida»gi Qonunining 19-moddasi talablariga muvofiq, ushbu asarlar omma (mehmonlar) uchun butun kitob holatida emas, balki bir qidiruvda ko‘pi bilan 50 ta kontekstual jumla doirasida taqdim etiladi. Ommaviy yuklab olish faqat tadqiqotchi va ilmiy rahbar uchun ruxsat etilgan.

---

### 5. Kollokatsiyalar Qamrovi va Lug‘at Cheklovlari
- `lexicon_entries` jadvalidagi 6,546 ta birikma tashqi leksikografik ma'lumotnoma manbasi bo‘lib, ulardan 469 tasi amaldagi parallel korpus matnlarida bevosita uchrashi tasdiqlangan. Korpusda uchramagan 6,000 dan ortiq birikmalar korpusda «mavjud» deb ko‘rsatilmagan, balki mustaqil ma'lumotnoma sifatida saqlangan.
