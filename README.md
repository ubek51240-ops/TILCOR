# TILCOR — o‘zbekcha–inglizcha badiiy tarjima parallel korpusi

Dissertatsiya: «Tarjima va teng matnlar parallel korpusida o‘zaro faol birikuvchi (kollokatsion) so‘zlar tadqiqi
(o‘zbek va ingliz tillari misolida)», Buxoro davlat universiteti, ixtisoslik 10.00.06. Sayt: https://tilcor.uz

Bu fayl joriy holatni (v3.6, 14.10.2026) qisqa beradi. Raqamlar ma’lumot fayllaridan olingan; saytdagi raqamlar so‘rov paytida
shu fayllardan hisoblanadi. O‘zgarishlar tarixi — `CHANGELOG.md`, joylash — `DEPLOY_v3.6_UZ.md`.

## Korpus

| | Asliyat | Tarjima | Gap juftliklari |
|---|---|---|---|
| 1 | Abdulhamid Cho‘lpon, «Kecha va kunduz» (Sharq, 2000) | Christopher Fort, «Night and Day» (Academic Studies Press, 2019) | 8 358 |
| 2 | Ernest Hemingway, «The Old Man and the Sea» (1952) | Ibrohim G‘ofurov, «Chol va dengiz» (Yosh gvardiya, 1986) | 1 718 |

- Jami 10 076 gap juftligi, 214 244 token (butun segmentlangan matn; so‘z ichidagi tutuq belgisi va chiziqcha so‘zni bo‘lmaydi);
  juft topilmagan 321 gap qidiruvda izoh bilan ko‘rsatiladi.
- Gaplar hunalign bilan ikki o‘tishda tekislangan (ikkinchi o‘tishda so‘z tekislashidan olingan lug‘at bilan).
  1.1-paragrafda tadqiqotchi tahlil qilgan 15 juftlik «tasdiqlangan» maqomida, qolganlari avtomatik.
- So‘z darajasidagi tekislash: eflomal, grow-diag-final-and. Muqobil faqat juftlik korpusda kamida 3 marta bog‘langan va
  so‘z bog‘lanishlarining kamida 3 foizi bo‘lsa ko‘rsatiladi (qamrov: o‘zbekcha mustaqil so‘zlarning 30,7 %, inglizchaning 41,2 %).
- Kollokatsiya nomzodlari: 2 536 ta (o‘zbekcha 974, inglizcha 1 562), har biri logDice, MI, t-score, G² va tarjimadagi muqobili bilan.
  Nomzodning maqomi 1.1.4-banddagi qaror tartibi bilan belgilanadi: lingvistik baho (inson tekshiruvi) va tayanch korpus.
- Inglizcha tayanch korpus (BNC ulanguncha): Brown, MASC va Gutenberg badiiy nasri, jami 2 598 511 token (`data/reference_en.json`).
- Teng (qiyosiy) matnlar: har bir tilda asliyat va tarjima tili solishtiriladi (`data/comparable_stats.json`, Bernardini, 2007).
- Inson tekshiruvi: besh vazifa, har birida 50 birlik o‘quv va 200 birlik asosiy tanlanma (`data/validation/samples.json`);
  baholar `data/validation/annotations.json` ga yoziladi va yangilash arxivida bo‘lmaydi.
- Korpus lug‘ati: 1 117 o‘zbekcha va 966 inglizcha bosh so‘z, 3 168 tarjima.

Kitob matnlari mualliflik huquqi egalariga tegishli; saytda faqat qidiruvga mos parchalar ko‘rsatiladi, to‘liq matn va
ma’lumot fayllari (`data/`) tashqariga berilmaydi.

## Halollik qoidalari

- Muqobil va lug‘atdagi tarjima — har doim tarjimonning kitobdagi so‘zi. Sun’iy intellekt yoki mashina tarjimasi muqobil sifatida berilmaydi.
- Ma’lumot o‘ylab topilmaydi: biror ko‘rsatkich hisoblanmagan bo‘lsa, saytda u yo‘q.
- Sun’iy intellekt yordamida qilingan tanlab tekshiruvlar `notes/` papkasida, shu izoh bilan. Ular tadqiqotchining o‘z tekshiruvi
  va ikkinchi annotator o‘rnini bosmaydi.
- Bosma lug‘atlardan olingan `data/dictionary.json` (OCR xatolari ko‘p) ommaga ko‘rsatilmaydi.

## Sahifalar

`/` bosh sahifa · `/qidiruv` so‘z va kollokatsiya qidiruvi · `/kwic` konkordans · `/kollokatsiyalar` va `/kollokatsiya/<id>` ·
`/lugat` korpus lug‘ati · `/korpus` · `/metodologiya` · `/statistika` · `/yoriqnoma` · `/manbalar` · `/loyiha-haqida` ·
`/kirish` (tadqiqotchi kabineti) · `/baholash` (inson tekshiruvi, faqat kirgan baholovchilar uchun). Interfeys o‘zbek (asosiy),
ingliz va rus tillarida.

## Ishga tushirish

```bash
python3 server.py --port 5050 --env local      # Python 3.8+ (3.12 da sinalgan), nltk kerak
```

VPS da: systemd xizmati `tilcor`, nginx → 5050-port, papka `/var/www/tilcor`. Maxfiy fayllar `secrets/` da, ular arxivga kirmaydi.
Ikkinchi baholovchi uchun `secrets/annotator.password` fayli yaratiladi; fayl bo‘lmasa, bu foydalanuvchi yoqilmaydi.

## Ma’lumotlarni qayta qurish (tartib muhim)

1. `scripts/build_hunalign_lexicon.py`, `scripts/realign_hunalign.py --lexicon data/hunalign_lexicon.json --base …` — gap tekislash;
2. `scripts/build_word_alignment.py` → `data/word_alignment.json`, `data/lexical_table.json`;
3. `scripts/build_collocation_index.py` → `data/collocation_index.json`;
4. `scripts/build_unpaired.py` → `data/unpaired_sentences.json`;
5. `scripts/build_corpus_dictionary.py` → `data/corpus_dictionary.json`;
6. `scripts/build_reference_en.py --nltk-dir <papka>` → `data/reference_en.json` (spaCy en_core_web_sm va NLTK korpuslari kerak;
   BNC bo‘lsa `--bnc <papka>`), so‘ng 3-qadam qayta (indeksga tayanch korpus ko‘rsatkichlari yoziladi);
7. `scripts/build_comparable_stats.py` → `data/comparable_stats.json`;
8. `scripts/build_validation_samples.py` → `data/validation/samples.json` — faqat manba ma’lumoti qayta qurilganda va
   baholash boshlanmasdan oldin (tanlanma o‘zgarsa, eski baholar yangi birliklarga mos kelmaydi);
9. `scripts/sample_dictionary_check.py` — lug‘atning tanlab tekshiruvi uchun 50 ta tasodifiy tarjima.

Har bir qadamdan keyin server qayta ishga tushiriladi.
