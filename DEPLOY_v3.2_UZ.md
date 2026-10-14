# TILCOR — 3.2-versiya: VPS ga joylash (yordamchi uchun)

Sana: 14.10.2026. Arxiv: `tilcor_v3.2_2026-10-14.zip`. Bu yangilanish v3 ustiga joylanadi, v3 ni to‘liq o‘z ichiga oladi.

**Nima o‘zgardi:** gaplar lug‘at bilan ikkinchi marta tekislandi (taxminan 1 000 juftlik tuzatildi), shunga ko‘ra
so‘z tekislash, kollokatsiyalar va juftsiz gaplar qayta tuzildi. Adabiyotlar ro‘yxati tuzatildi. Yangi kutubxona kerak emas.

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
tar -czf /root/tilcor_backups/tilcor_before_v32_$ts.tar.gz -C /var/www tilcor
```

## 2. Joylash

```bash
cd /tmp && rm -rf tilcor_v32 && mkdir tilcor_v32 && cd tilcor_v32
unzip -q /path/to/tilcor_v3.2_2026-10-14.zip
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
for u in "/?lang=uz" "/qidiruv?q=yurak" /kollokatsiyalar /statistika /metodologiya "/kwic?q=yurak"; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' "$B$u")  $u   (200 bo‘lishi kerak)"; done
```

Brauzerda: `/kollokatsiyalar` — «967 kollokatsiya»; `/qidiruv?q=yurak` — birinchi muqobil **heart**, «28 gapda».

## 5. Orqaga qaytarish

```bash
systemctl stop tilcor
rm -rf /var/www/tilcor && tar -xzf /root/tilcor_backups/tilcor_before_v32_<sana>.tar.gz -C /var/www
systemctl start tilcor
```
