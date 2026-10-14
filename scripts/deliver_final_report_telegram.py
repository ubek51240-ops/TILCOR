import sys
sys.path.insert(0, 'scripts')
from send_telegram_reply import send_reply

report_telegram = """🎉 TILCOR — STEP 06 BO‘YICHA YAKUNIY HISOBOT

Hurmatli tadqiqotchi va loyiha ma’murlari!
TILCOR_06.md talablari to‘liq bajarildi va https://tilcor.uz serverida muvaffaqiyatli ishga tushirildi.

1. PART 0 — TEZKOR TUZATISHLAR (100% PASS):
• Kesh izolyatsiyasi: server.py ko‘p oqimli (ThreadedTCPServer) arxitekturaga o‘tkazildi, har bir so‘rov uchun no-cache sarlavhalari qo‘shildi. 10 ta ketma-ket va 10 ta parallel so‘rovlar 100% izolyatsiya qilindi («ayvon» xatosi bartaraf etildi).
• HTTPS va HSTS: https://tilcor.uz bo‘yicha 301 yo‘naltirish, HSTS (max-age=31536000) va ECDSA sertifikati to‘liq tiklandi.
• Bosh sahifa, «yurak» va «heart» so‘rovlari xatosiz ishlamoqda.

2. PART 1 — STEP 05 STATUS AUDITI:
• 0–7 bo‘limlar to‘liq audit qilindi va hisobotga kiritildi.

3. PART 2 — 3 TA INTERFEYS TILI (UZ / EN / RU):
• Server-side render: ?lang=uz|en|ru va cookie asosida serverda to‘liq mahalliylashtirilgan HTML yuboriladi.
• Oʻz · En · Ру tugmalari haqiqiy href havolalarga ega, hreflang teglari joylashtirildi.
• Playwright (Chromium/Edge) testi: EN va RU sahifalarida 0 ta o‘zbekcha interfeys so‘zi qoldi (100% PASS).
• home_en.png, home_ru.png, search_yurak_en.png skrinshotlari olindi.

4. PART 3 — KORPUS BUTUNLIGI (100% PASS):
• 4 ta asar bo‘yicha 98% dan past sahifa mavjud emas.
• qishloq* = 115 ta, qaror* = 14 ta, ayvon* = 49 ta (matn qatlami bilan 100% mos).
• 102-sahifadagi «qaror» jumlasi korpusda mavjud va qidiruvda chiqmoqda.

5. PART 4 & 6 — TADQIQOTCHI ANKORLARI VA EKVIVALENTLAR:
• 15 ta 2.1(a) iboraviy ankorlar va 4 ta 2.1(b) gap ankorlari to‘liq topildi va «tasdiqlangan» / «1.1-paragraf (tadqiqotchi)» maqomi berildi.
• Hemingway birinchi va oxirgi jumlalari tasdiqlandi.
• aln-kvk-02079 bo‘yicha «deep sleep» koordinatalari [52, 62] to‘g‘rilandi.
• «tushirib qoldirilgan» soxta yorlig‘i olib tashlandi, avtomatik holat «ekvivalent aniqlanmagan»ga keltirildi.

6. PART 5 — OMS SAHIFA RAQAMLARI:
• OMS-EN: bosma sahifalar [9]–[125] («9-bet» … «125-bet»).
• OMS-UZ: 1–46-betlar («Chol va dengiz, elektron nusxa, N-bet»).

7. PART 7 — NOMZODLAR VA SO‘Z YASALISHI (RAUND 3):
• Oltin nomzodlar 100% qaytdi:
  - javob bermoq (Ot + fe’l) — 49 marta
  - qaror bermoq (Ot + fe’l) — 11 marta
  - og‘ir uyqu (Sifat + ot) — 4 marta
  - dasturxon solmoq (Ot + fe’l) — 4 marta
  - qat’iy qaror (Sifat + ot) — 4 marta
  - heavy sleep (Adjective + noun) — 2 marta
  - deep sleep (Adjective + noun) — 2 marta
• Yasama soxta lemmalar («beramoq», «qoladimoq») butunlay yo‘q qilindi.
• Misol jumlalarida har ikkala leksik birlik to‘liq ajratib ko‘rsatildi.

8. PART 8 — SO‘Z OILALARI, KIRILLCHA VA KWIC:
• WordNet oilalari qat’iy morfologik: meat, spirit, middle, rest kabi sinonimlar tozalindi.
• Kirillcha so‘rovlar (юрак, кўнгил, қарор, қишлоқ) 100% Latin korpusiga moslanib ishlamoqda.
• /api/kwic yangilandi: «yurak» bo‘yicha aynan qidiruvdagi 49 ta jumla chiqadi, CSV eksport qo‘shildi.

9. PART 9–12 — SANOG‘LAR, LUG‘AT VA ASOSIY SAHIFA:
• Defect K bartaraf etildi: summary sanog‘i so‘z shakllari yig‘indisiga teng (100% mos).
• Yo‘nalish yorliqlari (PART 10): Cho‘lponda asliyat o‘zbekcha, Hemingveyda asliyat inglizcha qilib ko‘rsatildi.
• Lug‘atdagi 9 980 ta buzilgan OCR glossasi yashirildi.
• «sleep rough» dagi «qattiq uyqu» xatosi yashirildi va ko‘rib chiqishga belgilandi.
• Asosiy sahifada jonli ma’lumotlar: 6 824 (Cho‘lpon), 1 532 (Hemingway), 8 356 (jami).
• Tarjimon ismi: «Ibrohim G‘ofurov». Anonim foydalanuvchilar uchun laboratoriya menyusi serverdan olib tashlandi.

10. QOIDALAR:
• PROJECT_CONTEXT.md fayliga yangi doimiy qoidalar — S5 bo‘limi qo‘shildi.

Barcha o‘zgarishlar https://tilcor.uz da jonli holatda ishlamoqda!
Keyingi qadam (Step 07) bo‘yicha topshiriqlar kutilyapti."""

send_reply(report_telegram)
print("Telegram final report delivered to both admins.")
