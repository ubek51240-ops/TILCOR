# TILCOR — 3-versiya: VPS ga joylash (yordamchi uchun)

Sana: 14.10.2026. Arxiv: `tilcor_v3_2026-10-14.zip`.
Bu arxiv 1- va 2-versiyalarni to‘liq o‘z ichiga oladi. Ular hali joylanmagan bo‘lsa, **faqat shu 3-versiyani joylang**.
Asosiy qadamlar `DEPLOY_v1_UZ.md` dagi bilan bir xil (xavfsizlik, zaxira, rsync `--delete`siz, admin paroli,
nginx sarlavhalari, qayta ishga tushirish). Quyida tartib va farqlar yozilgan.

## 0. Avval xavfsizlik (agar hali qilinmagan bo‘lsa)

`DEPLOY_v1_UZ.md`, 0-band: VPS root parolini almashtiring va Telegram bot tokenini BotFather orqali bekor qiling.
Eski kodda ikkalasi ham ochiq yozilgan edi.

## 1. Joylashdan oldin uchta tekshiruv

**a) Tadqiqotchi saytda yangi juftlik tasdiqlaganmi?** `data/full_corpus.json` arxivdagisi bilan almashtiriladi.

```bash
python3 -c "import json; d=json.load(open('/var/www/tilcor/data/full_corpus.json')); print(sum(1 for r in d if r.get('status')=='tasdiqlangan'))"
```

Natija **30 yoki undan kam** bo‘lsa — davom eting. **30 dan ko‘p** bo‘lsa — joylamang, faylni tadqiqotchiga yuboring.

**b) Xotira.** Yangi so‘z tekislash ma’lumoti birinchi qidiruvda xotiraga yuklanadi; server jami taxminan 470 MB
ishlatadi (avval taxminan 380 MB edi).

```bash
free -m      # "available" ustunida kamida 600 bo‘lishi kerak
```

Kam bo‘lsa, joylashdan oldin 1 GB swap qo‘shing (`fallocate -l 1G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile`).

**c) Python versiyasi:** `python3 --version` — 3.8 yoki undan yangi bo‘lsin. Yangi kutubxona o‘rnatish **shart emas**:
spaCy, eflomal, hunalign faqat ma’lumotni oldindan tuzish uchun ishlatilgan, tayyor natija arxivda bor.

## 2. Joylash

```bash
ts=$(date +%Y%m%d_%H%M); mkdir -p /root/tilcor_backups
tar -czf /root/tilcor_backups/tilcor_before_v3_$ts.tar.gz -C /var/www tilcor

cd /tmp && rm -rf tilcor_v3 && mkdir tilcor_v3 && cd tilcor_v3
unzip -q /path/to/tilcor_v3_2026-10-14.zip
rsync -a ./ /var/www/tilcor/          # --delete ISHLATMANG: sources/ va secrets/ saqlanib qolsin
find /var/www/tilcor -name "__pycache__" -type d -prune -exec rm -rf {} +
```

Admin paroli hali o‘rnatilmagan bo‘lsa — `DEPLOY_v1_UZ.md`, 3-band. Nginx sarlavhalari — 4-band.

```bash
systemctl restart tilcor && sleep 6 && systemctl is-active tilcor
journalctl -u tilcor -n 30 --no-pager
```

Logda `To'liq korpus yuklandi: 10096 ta jumla` qatori chiqishi kerak. VPS da hech qanday skriptni ishga tushirmang:
`scripts/build_*.py` fayllari faqat ma’lumotni qayta tuzish uchun (ular spaCy va eflomal talab qiladi).

## 3. Yangi ma’lumot fayllari (arxivda tayyor)

| Fayl | Nima |
|---|---|
| `data/word_alignment.json` | har bir juftlikda so‘z darajasidagi tekislash (tarjimadagi muqobilni topish uchun) |
| `data/lexical_table.json` | butun korpus bo‘yicha so‘z bog‘lanishlari jadvali |
| `data/collocation_index.json` | korpusdagi 2 501 ta kollokatsiya, tarjimalari va statistikasi bilan |
| `data/unpaired_sentences.json` | juft topilmagan 343 ta gap (qidiruvda izoh bilan chiqadi) |
| `css/tilcor.css` | yangi dizayn |

Bular ommaga berilmaydi (`/data/...` 404 qaytaradi), faqat server o‘qiydi.

## 4. Tekshiruv (5 daqiqa)

```bash
B=https://tilcor.uz
for u in /server.py /data/full_corpus.json /data/word_alignment.json /data/phd_corpus.db /secrets/admin.password /.git/config /DEPLOY_v3_UZ.md; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' $B$u)  $u   (404 bo‘lishi kerak)"; done
for u in / "/qidiruv?q=yurak" "/qidiruv?q=heart&lang=en" /kollokatsiyalar "/kollokatsiyalar?til=en&tartib=log_dice" \
         "/kwic?q=yurak" /korpus /statistika /metodologiya /manbalar /loyiha-haqida /yoriqnoma "/statistika?lang=ru" /kirish; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' "$B$u")  $u   (200 bo‘lishi kerak)"; done
curl -s -o /dev/null -w '%{http_code}  soxta cookie bilan admin (302 bo‘lishi kerak)\n' -H 'Cookie: tilcor_session=admin' $B/admin_collocations.html
curl -s -o /dev/null -w '%{http_code}  kirmasdan annotatsiya (401 bo‘lishi kerak)\n' -X POST -d '{}' $B/api/annotate
```

Brauzerda ko‘ring:

- `https://tilcor.uz/qidiruv?q=yurak` — «Kitobdagi tarjima muqobillari» bo‘limida birinchi muqobil **heart**; har bir gap
  juftligida qidirilgan so‘z sariq, tarjimonning so‘zi firuza rangda ajratilgan.
- `https://tilcor.uz/kollokatsiyalar` — «952 kollokatsiya» (o‘zbekcha), birinchisi *o‘rnidan turmoq* (69 marta).
- `https://tilcor.uz/statistika` — 3-bo‘lim «Kollokatsiyalarning tarjimada berilishi» va 4-bo‘lim «Assotsiatsiya o‘lchovlarini qiyoslash».
- Telefonda ochib ko‘ring: menyu «Menyu» tugmasi orqali ochiladi, sahifa yonga surilmaydi.

## 5. Muammo bo‘lsa — orqaga qaytarish

```bash
systemctl stop tilcor
rm -rf /var/www/tilcor && tar -xzf /root/tilcor_backups/tilcor_before_v3_<sana>.tar.gz -C /var/www
systemctl start tilcor
```

Xato logini (`journalctl -u tilcor -n 100 --no-pager`) tadqiqotchiga yuboring.
