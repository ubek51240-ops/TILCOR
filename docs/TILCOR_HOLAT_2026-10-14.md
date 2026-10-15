> **Tarixiy hujjat (v2 holati).** Joriy holat: `README.md` va `CHANGELOG.md` (v3.5).

# TILCOR platformasi: joriy holat

*14.10.2026. Konsepsiya: claude/tilcor-platforma-konsepsiyasi.md. Kod: tilcor_v2_2026-10-14.zip (VPS ga joylash yordamchi orqali).*

- **Tasdiqlangan juftliklar:** faqat 1.1-paragrafda tadqiqotchi keltirgan 15 juftlik (hammasi Cho'lpon juftligidan). Oldingi dastur o'zi qo'ygan 15 ta "tasdiqlangan" juftlik "avtomatik — tayanch nuqta" deb qayta belgilandi. Hemingway juftligida tasdiqlangan juftlik yo'q.
- **Tekislash:** gaplar hunalign (Varga va boshq., 2007; Gale–Church uzunlik modeli + leksik dalil) bilan qayta tekislandi, tasdiqlangan juftliklar va tayanch nuqtalar qo'zg'almas. Jami 10 096 juftlik (8 368 + 1 728). Maqomlar: "avtomatik — ikki usul mos", "avtomatik — faqat hunalign", "avtomatik — tayanch nuqta", "tasdiqlangan". AI yordamida tanlab tekshiruv: oldingi usul 15 tadan 7 to'liq + 1 qisman; yangi usul 38 tadan 31 to'liq + 5 qisman, 2 noto'g'ri (tadqiqotchi tekshiruvi emas).
- **Ma'lumotnoma bazasi** (5 306 ko'rinadigan yozuv) inglizcha o'quv to'plamlaridan, o'zbekchasi AI taklifi; MI/t-score/chastota qiymatlari o'ylab topilgani uchun o'chirildi. III bob statistikasiga kirmaydi.
- **III bob jadvallari:** oldingi kodda tasdiqlangan annotatsiya 50 tadan kam bo'lsa jadval to'qima raqamlar (n = 469, kitoblarga 60/40 bo'lingan) bilan to'ldirilardi. Bu olib tashlandi; hozir 5 ta tasdiqlangan annotatsiya bor, foizlar ko'rsatilmaydi. Kappa 50 umumiy birlikdan kam bo'lsa ishonchsiz deb belgilanadi.
- **Lug'at** (bosma lug'atlar, OCR) ommaga yopiq.
- **Nomzodlar:** ommaga faqat korpusda kamida 2 marta uchragan avtomatik nomzod ko'rsatiladi; ±4 so'z oynasi, so'z turkumi qoliplari.
- **Interfeys:** barcha ommaviy sahifalar server tomonida, uch tilda; qisqartmasiz; raqamlar jonli hisoblanadi.
- **Tuzatilgan faktlar:** ixtisoslik 10.00.06 (saytda 10.02.20 edi); Kecha va kunduz — Sharq, 2000 (saytda 1995); Night and Day — 2019; Hemingway korpus nusxasi — Asiaing.com, bosma nashri aniqlanmagan.

## Tadqiqotchi uchun ochiq vazifalar

- VPS root parolini almashtirish va Telegram bot tokenini bekor qilish (eski kodda ochiq yozilgan edi).
- Tayanch nuqta juftliklarini ko'rib chiqish: matn bo'yicha to'g'ri ko'ringanlari (aln-kvk-00069, 01407, 01789, 03162, 04394, 06198, 06357, 06817, 06823; Hemingway 4 tasi) admin panelda tasdiqlanishi mumkin; aln-kvk-02071 noto'g'ri edi.
- Juftliklarni tasdiqlash: ekvivalentlar faqat tasdiqlangan juftlikdan olinadi.
- Ixtisoslik nomini OAK ro'yxati bilan solishtirish.
- Ikkinchi annotatorni tanlash; tayanch korpus (milliy korpus yoki uzWaC).
