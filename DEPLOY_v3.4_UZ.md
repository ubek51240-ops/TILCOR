# TILCOR — 3.4-versiya: VPS ga joylash (yordamchi uchun)

Sana: 14.10.2026. Arxiv: `tilcor_v3.4_2026-10-14.zip`. Saytda hozir v3.3 turibdi; bu kichik tuzatish uning ustiga joylanadi.

**Nima o‘zgardi (v3.4):** sarlavha va yorliqlarda so‘zlar orasidagi bo‘shliqlar (ekran o‘quvchi dasturlar va qidiruv tizimlari uchun),
belgili tugmalar uchun yashirin matn, «hamma gaplarda topildi» holati uchun to‘g‘ri jumla; 1.1-paragrafdagi juftliklarda kollokatsiya
muqobili tadqiqotchi belgilagan so‘zdan olinadi (qidiruv sahifasi bilan bir xil). Quyida v3.3 dagi o‘zgarishlar ham saqlangan:
- yangi dizayn: to‘q ko‘k fon, yuqori qator va bayroqlar, yumaloq qidiruv va menyu tugmalari, butun ekranli qidiruv oynasi,
  bo‘limlar menyusi, sahifa sarlavhasi bandi, statistika kartochkalari, KWIC da kontekst kengligi uchun surgich;
- (v3.2 dan) gaplar lug‘at bilan ikkinchi marta tekislandi, so‘z tekislash va kollokatsiyalar qayta tuzildi, adabiyotlar tuzatildi.
Yangi kutubxona kerak emas. Uslublar fayli `?v=3.3` bilan ulanadi, brauzer keshi o‘zi yangilanadi.

## 0. Xavfsizlik (hali qilinmagan bo‘lsa — avval shu)

- VPS root parolini almashtiring (`passwd`). Eski parol `ubek51240-ops/tilcor` ochiq repozitoriysida yozilgan, uni har kim o‘qiy oladi.
- O‘sha repozitoriyni yoping (Settings → Danger zone → Change visibility → Private) yoki o‘chiring.
- Telegram bot tokenini BotFather orqali bekor qiling.

## 1. Tekshiruv va zaxira

```bash
python3 -c "import json; d=json.load(open('/var/www/tilcor/data/full_corpus.json')); print(sum(1 for r in d if r.get('status')=='tasdiqlangan'))"
```

**15** chiqsa — davom eting. 15 dan ko‘p bo‘lsa — joylamang, faylni tadqiqotchiga yuboring.

```bash
ts=$(date +%Y%m%d_%H%M); mkdir -p /root/tilcor_backups
tar -czf /root/tilcor_backups/tilcor_before_v34_$ts.tar.gz -C /var/www tilcor
```

## 2. Joylash

```bash
cd /tmp && rm -rf tilcor_v34 && mkdir tilcor_v34 && cd tilcor_v34
unzip -q /path/to/tilcor_v3.4_2026-10-14.zip
rsync -a ./ /var/www/tilcor/          # --delete ISHLATMANG
find /var/www/tilcor -name "__pycache__" -type d -prune -exec rm -rf {} +
systemctl restart tilcor && sleep 6 && systemctl is-active tilcor
journalctl -u tilcor -n 20 --no-pager | grep "korpus yuklandi"    # "10076 ta jumla" bo‘lishi kerak
```

## 3. Bosh sahifa keshini tekshirish

Tashqaridan `https://tilcor.uz/` manzilida hali eski sahifa ko‘rindi, `https://tilcor.uz/?lang=uz` esa yangisini ko‘rsatdi.
Shuni tekshiring:

```bash
curl -s http://127.0.0.1:5050/ | grep -c "Tarjimon so‘zni qanday bergan"     # 1 bo‘lishi kerak
curl -s https://tilcor.uz/ | grep -c "Tarjimon so‘zni qanday bergan"         # 1 bo‘lishi kerak
curl -sI https://tilcor.uz/ | grep -iE "cache|cf-|age:|server"
grep -rnE "proxy_cache|location = /|expires" /etc/nginx/ 2>/dev/null
```

- Ikkalasi ham 1 bo‘lsa — hammasi joyida, eski sahifa faqat tashqi vositaning keshida qolgan.
- Birinchisi 1, ikkinchisi 0 bo‘lsa — oraliqda kesh bor:
  - sarlavhalarda `cf-cache-status` bo‘lsa, Cloudflare panelida Caching → Purge Everything qiling;
  - nginx da `proxy_cache` yoki `location = /` bo‘lsa, shu qatorlarni olib tashlab, `nginx -t && systemctl reload nginx`.
- Natijalarni tadqiqotchiga yuboring.

## 4. Tekshiruv

```bash
B=https://tilcor.uz
for u in /server.py /data/full_corpus.json /data/word_alignment.json /secrets/admin.password /.git/config; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' $B$u)  $u   (404 bo‘lishi kerak)"; done
for u in "/?lang=uz" /assets/tilcor-emblem.svg "/css/tilcor.css?v=3.3" "/qidiruv?q=yurak" /kollokatsiyalar /statistika /metodologiya "/kwic?q=yurak"; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' "$B$u")  $u   (200 bo‘lishi kerak)"; done
```

Brauzerda (kompyuter va telefon):
- bosh sahifa to‘q ko‘k, sarlavha «Tarjimon so‘zni qanday bergan», o‘ngda raqamli kartochkalar (10 076 juftlik);
- o‘ng yuqoridagi lupa tugmasi butun ekranli qidiruv oynasini ochadi, Esc yopadi; uch chiziqli tugma bo‘limlar menyusini ochadi;
- `/kollokatsiyalar` — «967 kollokatsiya»; `/qidiruv?q=yurak` — birinchi muqobil **heart**, «28 gapda»;
- `/kwic?q=yurak` — «Kontekst kengligi» surgichini sichqoncha bilan sursangiz, natija yangilanadi.

## 5. Orqaga qaytarish

```bash
systemctl stop tilcor
rm -rf /var/www/tilcor && tar -xzf /root/tilcor_backups/tilcor_before_v34_<sana>.tar.gz -C /var/www
systemctl start tilcor
```
