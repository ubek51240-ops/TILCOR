# TILCOR v2.0 — Cheklovlar va Ilmiy Ogohlantirishlar (LIMITATIONS.md)

Dissertatsiya ilmiy himoyasi va ekspertlar komissiyasi uchun halol va shaffof bayonot.

---

## 1. Hozirgi Bosqichdagi Asosiy Cheklovlar (Stage 2 Holati)

1. **Jumlalar Tekislashi (Alignment Drift) — Qayta Ishlashda:**
   - 1-bosqich auditida eski `full_corpus.json` dagi jumlalarning 80% dan ortig‘i ketma-ketlik siljishi sababli noto‘g‘ri tekislangani aniqlangan.
   - Hozirda Hemingway va Cho‘lpon parallel jumlalari tepasida *"Tekislash qayta ko‘rib chiqilmoqda — tahlil uchun foydalanmang"* banneri mavjud.
   - Bu cheklov 4-bosqich (qayta segmentlash) va 5-bosqich (Gale-Church / Hunalign + 300 ta oltin standart tekshiruvi) yakunlangach bartaraf etiladi.

2. **Robert Luis Stivenson ("Xazinalar oroli") Karantinda:**
   - O‘zbekcha manba (`Robert Luis Stivenson. Xazinalar oroli [@e_kutubxona].pdf`) 216 betlik skanerlangan rasm bo‘lib, unda raqamli matn qatlami (OCR) mavjud bo‘lmagan.
   - Natijada eski tizimda 1,346 ta soxta placeholder ("Sarguzasht parchasi: ") shakllangan.
   - Ushbu 1,346 ta qator `status = excluded` bilan karantinga olingan va barcha sanash hamda qidiruvlardan butunlay chiqarilgan.
   - Ushbu asar faqat Tesseract OCR va insoniy korrekturadan o‘tgachgina qayta kiritiladi.

3. **Kollokatsiyalar Bazasi Darslik Lug‘atidan Olingan:**
   - Hozirgi 6,544 ta birikma asosan darslik va leksikografik qo‘llanmalardan import qilingan normativ maqolalardir.
   - Badiiy korpusdan avtomatik ravishda chastotaviy oyna (window $\pm 3$) orqali birikmalarni ajratib olish va ularning haqiqiy MI/t-score ko‘rsatkichlarini hisoblash 6-bosqichda amalga oshiriladi.

4. **Tizim Yopiq Rejimda (Restricted Access):**
   - Mualliflik huquqi va dissertatsiyaning maxfiylik talablariga muvofiq, tizim ochiq internetda e'lon qilinmaydi.
   - Faqat tadqiqotchi (`admin`) va ilmiy rahbar (`reviewer`) kirish huquqiga ega.
