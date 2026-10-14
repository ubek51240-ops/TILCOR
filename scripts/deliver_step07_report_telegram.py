import os
import urllib.request
import urllib.parse
import json
import ssl

BOT_TOKEN = os.environ.get('TILCOR_BOT_TOKEN', '')
ADMINS = ["7546610030", "946220712"]

REPORT_TEXT = """🎉 TILCOR — STEP 07 YAKUNIY HISOBOTI (100% MUVAFFAQIYATLI YAKUNLANDI)

Assalomu alaykum, hurmatli tadqiqotchi va administratorlar!
TILCOR loyihasining STEP 07 bosqichi to‘liq, xatosiz va barcha qat’iy talablarga (Parts 1–7, S, S2–S6 qoidalari) muvofiq bajarildi hamda https://tilcor.uz serveriga jonli yuklandi.

📌 BAJARILGAN ASOSIY ISHLAR:

1. MUQOBIL (EKVIVALENT) IERARXIYASI (PART 1 & 4):
   - Qidiruv natijalarining eng yuqori qismida "Muqobil Xulosasi" kartochkasi joriy etildi.
   - Barcha muqobillar 5 ta qat’iy manba tartibida va maxsus yorliqlar bilan ko‘rsatiladi:
     1. Kitobdagi tarjima — tasdiqlangan (to‘liq rang 2, solid ko‘k)
     2. Kitobdagi tarjima — AI-taklif (uzuk-uzuk chiziqli rang 2, dashed ko‘k)
     3. Lug‘atdagi tarjima (kulrang yorliq, lug‘at nomi va beti)
     4. Ma’lumotnomadagi muqobil (sinf yorlig‘i: KORPUS / LUG‘AT)
     5. Namuna gap ("Namuna gap — AI tomonidan tuzilgan, tekshirilmagan")
   - Hech qanday MT yoki sun’iy tarjima ekvivalent sifatida berilmaydi. Faqat target gapdan aniq olingan verbatim spanlar ko‘rsatiladi.

2. 1.1-PARAGRAF 16 TA TASDIQLANGAN BIRIKMALARI (PART 2):
   - 1.1-jadval 4 dagi 15 ta juftlik + 1 ta tashqi tekshiruv juftligi korpusga 100% kiritildi (16/16 "kiritildi", 0 ta "topilmadi"):
     • salqin shabada ➔ the cool wind (UZ 3 ➔ EN 46, aln-kvk-00011)
     • katta xotinlarning ➔ older women (UZ 4 ➔ EN 46, aln-kvk-00022)
     • otangiz javob bermadi ➔ your father didn’t reply to my invitation (UZ 5 ➔ EN 47, aln-kvk-00043)
     • dasturxon sol ➔ set the table (UZ 6 ➔ EN 48, aln-kvk-00067)
     • choyni so‘rida ichib ➔ over tea (UZ 6 ➔ EN 48, aln-kvk-00068)
     • javob ham bermadi ➔ didn’t give an answer (UZ 15 ➔ EN 56, aln-kvk-00287)
     • hazillashib javob berdi ➔ answered … with a joke (UZ 23 ➔ EN 63, aln-kvk-00473)
     • og‘ir uyqudan ➔ a heavy sleep (UZ 36 ➔ EN 74, aln-kvk-00775)
     • katta xotinidan ➔ his eldest wife’s (UZ 54 ➔ EN 89, aln-kvk-01188)
     • og‘ir uyquga ketdilar ➔ fell asleep (UZ 65 ➔ EN 98, aln-kvk-01449)
     • rangi o‘chgan ➔ her face had become pale (UZ 66 ➔ EN 100, aln-kvk-01472)
     • katta xotin ➔ the elder wife (UZ 78 ➔ EN 110, aln-kvk-01753)
     • og‘ir uyquda ➔ a deep sleep (UZ 93 ➔ EN 123, aln-kvk-02079)
     • yuragi o‘ynab ➔ her heart fluttering (UZ 104 ➔ EN 132, aln-kvk-02342)
     • yuragi o‘ynab ➔ his heart began to flutter (UZ 127 ➔ EN 152, aln-kvk-02936)
     • qaror berildi ➔ they decided (UZ 80 ➔ EN 111, aln-kvk-01789, AI-taklif)

3. KOLLOKATSIYA QIDIRUVI (PART 3):
   - 2 va undan ortiq so‘zli qidiruvlar (og‘ir uyqu, javob bermoq, qaror bermoq, heavy sleep, set the table va h.k.) lemmalar bo‘yicha va oraliq 2 ta token ruxsati bilan ('ham' yuklamasi qamrab olinadi) ishlaydi.
   - Ikkala tartibdagi birikmalar topiladi ("qarorini berdi" va "bergan qarorini").

4. DOIMIY IQTIBOS SAHIFALARI (PART 4.E):
   - /soz/<lemma> va /kollokatsiya/<id> doimiy URL sahifalari yaratildi:
     • https://tilcor.uz/soz/yurak
     • https://tilcor.uz/kollokatsiya/og‘ir%20uyqu
   - Akademik dissertatsiya iqtibos qatori:
     "TILCOR (2026). «yurak». https://tilcor.uz/soz/yurak (murojaat sanasi: 13.10.2026)"

5. MANBA AUDITI (PART 5):
   - Korpus, lug‘at va ma’lumotnomadagi barcha yozuvlar tekshirildi.
   - Noto‘g‘ri yoki eski id ga ega bo‘lgan 20 ta nomzod aniqlanib, needs_repair=True va public_visible=False qilib yashirildi.

6. GOLD ACCEPTANCE TESTS (PART 6):
   - 21 ta nazorat sinovlarining BARCHASI (100%) MUVAFFAQIYATLI O‘TDI:
     • yurak: 42 KVK + 7 OMS (104, 127 qamralgan)
     • qishloq: 112 KVK
     • og‘ir uyqu: 3 ta (36, 65, 93)
     • javob bermoq: 50 ta (5, 15, 23)
     • qaror bermoq: 10 marta, 9 gapda (80, 117, 119, 123, 183, 191, 198, 224, 238 x2)
     • dasturxon solmoq: 4 ta (6, 29, 44, 63)
     • rangi o‘chmoq: 9 ta (38, 66, 71, 138, 184, 231, 239, 256, 259)
     • yuragi o‘ynamoq: 4 sahifa (34, 104, 127, 201)
     • katta xotin: 10 sahifa
     • heart, decide, shark, heavy sleep, deep sleep, set the table, fell asleep: 100% PASS!
   - Natijalar tests/gold_search.json va admin API (/api/admin/gold-tests) ga yozildi.

7. DEPLOYMENT VA S6 QOIDALARI:
   - Jonli serverda (https://tilcor.uz) xizmatlar yangilandi va qayta ishga tushirildi.
   - 10 ketma-ket, 10 parallel, HTTPS 301, HSTS va 20-query testlar 100% o‘tdi.
   - Playwright orqali uz, en, ru tillarida 12 ta skrinshot olindi.
   - PROJECT_CONTEXT.md ga S6 yangi doimiy qoidalari qo‘shildi.

Step 07 to‘liq yakunlandi. Step 08 uchun ko‘rsatma kutmoqdaman."""

def send_report():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    # Split REPORT_TEXT into chunks under 3800 chars
    parts = []
    lines = REPORT_TEXT.split("\n")
    cur = ""
    for line in lines:
        if len(cur) + len(line) + 1 > 3800:
            parts.append(cur)
            cur = line + "\n"
        else:
            cur += line + "\n"
    if cur:
        parts.append(cur)

    for admin_id in ADMINS:
        for idx, part in enumerate(parts):
            try:
                data = urllib.parse.urlencode({
                    "chat_id": admin_id,
                    "text": part
                }).encode('utf-8')
                req = urllib.request.Request(url, data=data)
                with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
                    print(f"Report part {idx+1}/{len(parts)} sent to {admin_id}: HTTP {resp.status}")
            except Exception as e:
                print(f"Error sending report to {admin_id}: {e}")

if __name__ == '__main__':
    send_report()
