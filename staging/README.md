# KORPUS.LINGVO — Tarjima va Teng Matnlar Parallel Korpusi hamda Kollokatsiyalar Tadqiqoti Portali

Ushbu veb-sayt **"TARJIMA VA TENG MATNLAR PARALLEL KORPUSIDA OʻZARO FAOL BIRIKUVCHI (KOLLOKATSION) SOʻZLAR TADQIQI (oʻzbek va ingliz tillari misolida)"** ilmiy dissertatsiyasi rejasi va mazmuni asosida maxsus yaratilgan.

---

## 📌 Saytning Asosiy Boʻlimlari va Imkoniyatlari

### 1. Bosh Sahifa (Umumiy sharh va tezkor maʼlumotlar)
- Ilmiy ishning toʻliq nomi, mutaxassisligi va maqsadi.
- Asosiy koʻrsatkichlar: parallel jumlalar soni (12,450+), kollokatsiyalar bazasi (1,520+), jumlalarni tekislash (alignment) aniqligi (98.4%).
- Asosiy boblarga tezkor oʻtish kartalari.

### 2. Ilmiy Ish & Boblar (Dissertatsiyaning toʻliq interaktiv mundarijasi)
- **KIRISH**: Mavzuning dolzarbligi, maqsadi, vazifalari, obyekti, predmeti va ilmiy yangiligi.
- **I BOB**: Kollokatsiya tushunchasining nazariy asoslari (1.1, 1.2, 1.3-paragraflar, J.R. Firth va Sinclair qoidalari, erkin birikma va frazeologizmlar bilan qiyosiy jadval, bob xulosasi).
- **II BOB**: Tadqiqot metodologiyasi va parallel korpus yaratish jarayoni tavsifi (2.1, 2.2, 2.3-paragraflar, Gale-Church / Hunalign algoritmlari, MI va T-score formulalari).
- **III BOB**: Parallel korpus bazasi tarjima matnlarida kollokatsiyalarning qiyosiy tahlili (3.1, 3.2, 3.3-paragraflar, struktur modellar, toʻliq/qisman/konseptual ekvivalentlik, lingvomadaniy konnotatsiyalar).
- **XULOSA**: Yakuniy ilmiy xulosalar va amaliy tavsiyalar.
- **FOYDALANILGAN ADABIYOTLAR ROʻYXATI**: Xalqaro va mahalliy lingvistika manbalari.
- **ILOVALAR**: POS teglash va statistik parametrlar.
- Shrift oʻlchamini boshqarish (A- / A+) va dissertatsiya boʻlimlarini chop etish (Print) rejimi.

### 3. Parallel Korpus Qidiruv Tizimi (Bilingual Concordancer - KWIC)
- Oʻzbekcha va inglizcha matnlarni parallel qidirish.
- Badiiy, ilmiy, publitsistik va rasmiy janrlar boʻyicha saralash.
- Aligned jumlalar, kollokatsiyalar rangli ajratilishi, alignment aniqligi va MI koʻrsatkichlari.
- Jumlalarni nusxalash va ovozli oʻqib eshittirish (Web Speech API).
- Yangi parallel jumla kiritish imkoniyati.

### 4. Kollokatsiyalar Matritsasi (Collocation Explorer)
- Oʻzbekcha va inglizcha kollokatsiyalarni qidirish va filtrlash.
- Grammatik qoliplar boʻyicha saralash (Sifat+Ot, Feʼl+Ot, Ot+Feʼl, Ravish+Sifat).
- Ekvivalentlik turlari (Toʻliq, Qisman, Konseptual).
- MI Score, T-Score, Chastota boʻyicha tartiblash.
- **Kalka xatosi haqida ogohlantirish** (*strong rain, *accept a decision, *do a mistake kabi xatolarni koʻrsatish).
- Maʼlumotlarni **CSV formatida yuklab olish** (Export).

### 5. Matn Tahlili va Kollokatsiya Tekshirgich (Checker)
- Foydalanuvchi ixtiyoriy oʻzbekcha yoki inglizcha matn kiritganda, tizim avtomatik ravishda kollokatsiyalarni aniqlaydi.
- Notoʻgʻri kalka tarjimalarini qizil bilan belgilaydi va toʻgʻri muqobilini koʻrsatadi.
- Tayyor test namunalari mavjud.

### 6. Statistika va Grafiklar (Analytics)
- Chart.js dinamik diagrammalari:
  - Struktur modellar taqsimoti (Doughnut).
  - Tarjima ekvivalentligi nisbati (Bar).
  - Janrlar boʻyicha korpus hajmi (Pie).
- MI va T-score statistik xulosalari.

---

## 🚀 Saytni Ishga Tushirish

### 1-usul (Eng osoni):
Fayl menejerida `run_site.bat` faylini ikki marta bosing yoki toʻgʻridan-toʻgʻri `index.html` faylini brauzerda oching.

### 2-usul (Python mahalliy serveri orqali):
```bash
python server.py
```
Brauzer avtomatik ravishda `http://localhost:8080` manzilida ochiladi.
