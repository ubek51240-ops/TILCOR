# TILCOR — MA’LUMOTLAR AUDITI HISOBOTI (AUDIT REPORT)
**Sana:** 2026-10-13  
**Holat:** 1-qadam (Step 01) doirasida yakunlangan tozalash va audit natijalari  
**Prinsip:** Soxta/to‘qima ma’lumotlar nolga keltirildi; har bir qator aniq ma’lumotlar sinfiga ajratildi.

---

## 1. Ma’lumotlar sinflari va taqsimoti

Qayta ishlangan barcha ma’lumotlar 5 ta qat’iy sinfga ajratildi:

| Sinf | Tavsif | Soni / Holati | Qilingan amallar |
| :--- | :--- | :--- | :--- |
| **KORPUS** | Ilmiy tadqiqot uchun kiritilgan badiiy parallel matn parchalari | **3 811 juftlik faol**<br>• Cho‘lpon (*Kecha va kunduz*): 2 471<br>• Hemingway (*Chol va dengiz*): 1 340<br>*(1 346 ta Stivenson arxivlandi)* | Stivenson segmentlari `removed_by_researcher` (`excluded: true`) belgisi bilan arxivlandi. Soxta o‘zgarmas moslik koeffitsiyentlari (`0.95`, `0.96`, `0.94`, `moslik`) olib tashlandi. Litsenziya matni ilmiy parcha talabiga moslashtirildi. |
| **LUG‘AT** | Chop etilgan inglizcha-o‘zbekcha lug‘atlardan olingan leksik birliklar | **23 566 ta toza**<br>*(988 ta `needs_repair`)* | 24 554 ta dastlabki OCR qatorlari saralandi. 988 ta buzilgan/qisman skanerlangan qator `needs_repair` bilan karantinlandi (`public_visible: false`). Qolgan 23 566 tasi manba bibliografiyasi bilan tasdiqlandi. |
| **MA’LUMOTNOMA** | Kollokatsiyalar bazasi (ingliz tili leksik birikmalari) | **6 537 ta faol**<br>*(9 ta brak olib tashlandi)* | Manbalar 3 ta rasmiy nashrga biriktirildi: ACL (Pearson, 2013), Cambridge Collocations in Use (McCarthy & O'Dell), 1000 English Collocations (Espresso English). 9 ta texnik brak/bo‘sh satr olib tashlandi. |
| **AI-TAKLIF** | Avtomatik tizimlar orqali generatsiya qilingan yoki tarjima qilingan birliklar | **6 537 ta tarjima**<br>• Mashina tarjimasi ogohlantirishi | Barcha 6 537 kollokatsiyaning o‘zbekcha tarjimasi `AI-taklif (tekshirilmagan)` deb belgilandi. Sinovchi va tarjimon modullardagi AI takliflariga qat’iy ogohlantirish yorliqlari qo‘yildi. |
| **TO‘QIMA** | Dastlabki prototipdan qolgan soxta namunalar, qotirilgan raqamlar va shablonlar | **To‘liq tozalandi (0 ta)** | `dissertationData` (18 ta lokal demo juftlik), `plays a vital semantic role` kabi shablon matnlar, sun’iy statistik ko‘rsatkichlar (`MI: 7.2`, `t-score: 2.14`, qotirilgan `0.95`, `0.96`, `5,157`, `6,546`) butunlay o‘chirildi. |

---

## 2. Tozalangan va o‘zgartirilgan fayllar

1. **`data/full_corpus.json` va `data/corpus.db`**:
   - Stivenson asari (1 346 juftlik) ochiq qidiruvdan chiqarildi (`excluded: true`).
   - Faol ilmiy korpus: **3 811** segment.
   - Soxta `moslik: 0.95/0.96` maydonlari o‘chirildi.

2. **`data/dictionary.json`**:
   - 24 554 ta yozuvdan 988 tasi `needs_repair` sifatida belgilandi va ommaviy ko‘rinishdan olindi.
   - 23 566 ta toza lug‘at maqolasi manba ko‘rsatilgan holda saqlandi.

3. **`data/collocations_full.json` va `js/collocations_list.js`**:
   - 9 ta yaroqsiz qator o‘chirildi (qoldi 6 537).
   - O‘zbekcha tarjimalari `ai_suggestion: true` deb belgilandi.
   - Kalibrlanmagan/soxta statistik parametrlar yashirildi.

4. **`js/data.js`**:
   - `dissertationData` massivi, sun’iy test misollari va to‘qima korpus qatorlari butunlay to‘xtatildi va tozalandi.

5. **`js/corpus.js`**:
   - API `/api/search` orqali dinamik ishlashga o‘tkazildi (limit maksimum 50).
   - Chapda original (ingliz tili), o‘ngda tarjima (o‘zbek tili) tuzilishi tiklandi.
   - Yuqori qismda ilmiy parcha va ogohlantirish bitta ixcham blokda ko‘rsatiladi.

6. **`js/dictionary.js`**:
   - Soxta kontekst gaplari olib tashlandi, real `/api/dict` qidiruvi va manbasi chiqarildi.

7. **`js/translator.js` va `js/checker.js`**:
   - Mashina tarjimasi ogohlantirishlari (`AI-taklif`) qo‘shildi.
   - Soxta `2.14` fallback va Stivenson misollari to‘liq olib tashlandi.

8. **`server.py`**:
   - Anonim foydalanuvchilar uchun cheklovlar: `/api/translate`, `/api/ai`, `/api/collocations/ai-analyze`, `/api/checker/ai-diagnose`, `/api/lab/extract` endpointlari `401 Unauthorized` qaytaradi.
   - Ochiq ilmiy qidiruv: `/api/search` limit 50 bilan cheklangan.
   - Dinamik real statistika: `/api/stats` faqat bazadagi real raqamlarni (3 811 korpus, 6 537 kollokatsiya, 23 566 lug‘at) taqdim etadi.

---

## 3. Tadqiqotchi e’tiboriga (Muhim topilma)
- *Kecha va kunduz* romanining 535 ta ekspert tekshirgan oltin standarti (gold standard) alohida fayl ko‘rinishida loyiha papkasida mavjud emasligi aniqlandi. `data/phd_corpus.db` ichidagi `gold_alignments` jadvalida 300 ta juftlik (150 ta Cho‘lpon, 150 ta Hemingway) mavjud. Ushbu 535 ta juftlik fayli tadqiqotchidan taqdim etilishi kutilmoqda.
