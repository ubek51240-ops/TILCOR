# TILCOR — 3.7-versiya: VPS ga joylash (yordamchi uchun)

Sana: 15.10.2026. v3.7 — v3.6 ustiga kichik qo‘shimcha: qidiruv takliflari va xavfsizlik kuchaytirishlari.
Joylash tartibi DEPLOY_v3.6_UZ.md dagi bilan BIR XIL (zaxira → rsync → restart → tekshiruv); faqat quyidagi
qo‘shimcha fayllar va tekshiruvlar bor.

**Nima o‘zgardi (v3.7):**
- `suggest.py` (YANGI): qidiruv qatorida avtomatik takliflar va «Buni nazarda tutdingizmi?» —
  faqat korpusda real uchragan so‘z shakllaridan;
- `/api/suggest` endpointi; ommaviy qidiruvga IP bo‘yicha tezlik chekovi (30/daqiqa, takliflarga 120/daqiqa);
- `.html` berishda yo‘l normallashtirish; ruxsatnoma xati yuklashiga 15 MB chegara;
- `locales/uz|en|ru.json` ga `did_you_mean`, `rate_limited` kalitlari; `css/tilcor.css` ga `.tc-ac` uslublari;
  uslublar endi `?v=3.7` bilan ulanadi.

## Qo‘shimcha tekshiruvlar (v3.6 tekshiruvlaridan keyin)

```bash
B=https://tilcor.uz
echo "$(curl -s -o /dev/null -w '%{http_code}' $B/suggest.py)  /suggest.py   (404 bo‘lishi kerak)"
curl -s "$B/api/suggest?q=yura" | head -c 200; echo       # yuragi, yura, yuradi ... chiqishi kerak
curl -s "$B/qidiruv?q=yurok" | grep -c "nazarda tutdingizmi"   # 1 bo‘lishi kerak
curl -s "$B/" | grep -c "tc-ac"                                # 1 yoki ko‘proq
# Tezlik chekovi (35 ta so‘rovdan oxirgilari 429 bo‘lishi kerak):
for i in $(seq 1 35); do curl -s -o /dev/null -w '%{http_code} ' "$B/qidiruv?q=heart"; done; echo
```

Brauzerda: qidiruv qatoriga `yura` yozilganda ostida takliflar ro‘yxati (so‘z + uchrashlar soni) chiqadi,
↑/↓/Enter bilan tanlanadi; `yurok` deb qidirilganda «Buni nazarda tutdingizmi: yurak …» chiplari ko‘rinadi.

## Orqaga qaytarish

v3.6 yo‘riqnomasidagi bilan bir xil (zaxiradan tiklash).
