import sys
sys.path.insert(0, 'scripts')
from send_telegram_reply import send_reply

msg = """✅ TILCOR — STAGE 1 DEPLOYMENT VA TEST NATIJALARI (https://tilcor.uz)

Hurmatli Ibrohim Vakhidov va administratorlar!
Topshiriq to‘liq bajarildi va https://tilcor.uz serveriga muvaffaqiyatli deploy qilindi.

1. Bajarilgan ishlar:
• "Corpusni ochish", "Collocationsni ko‘rish" kabi duragay (gibrid) tarjimalar to‘liq yo‘qotildi, barcha matnlar uz.json, en.json, ru.json asosida kalitli (key-based) toza tarjimaga o‘tkazildi.
• Public HTML dan barcha admin elementlar (admin_collocations, sinovchisi, Jonli Tarjimon, PhD Hub, preview_alignment_queue) butunlay olib tashlandi.
• Barcha sahifalar uchun yagona navigatsiya o‘rnatildi, '#' bo‘sh havolalar bartaraf etildi.
• /korpus, /kollokatsiyalar, /lugat, /kirish sahifalari to‘liq ochilmoqda (HTTP 200).

2. Task 13 bo‘yicha Public Curl va Test natijalari:
• curl https://tilcor.uz/?lang=en | grep 'ni ochish' -> 0
• curl https://tilcor.uz/?lang=ru | grep 'ni ochish' -> 0
• curl https://tilcor.uz/ | grep 'admin_collocations' -> 0
• 15 ta sahifa x 3 ta tilda (45 ta URL): barchasi HTTP 200
• Navigatsiya havolalari: barchasi HTTP 200, '#' havolalar soni: 0

JAMI XATOLIKLAR (TOTAL VIOLATIONS): 0 (100% PASS)

Sayt jonli ishlamoqda va barcha talablarga to‘liq javob beradi!"""

send_reply(msg)
print("[*] Telegram hisoboti muvaffaqiyatli yuborildi.")
