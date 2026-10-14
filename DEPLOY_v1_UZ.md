# TILCOR — 1-versiya: VPS ga joylash yo‘riqnomasi (yordamchi uchun)

Sana: 14.10.2026. Arxiv: `tilcor_v1_2026-10-14.zip`.
Bu arxiv tadqiqotchi yuborgan `tarjimon_1.rar` (Antigravity ishlagan lokal nusxa) asosida tuzatilgan to‘liq sayt kodidir.
VPS dagi hozirgi kod bundan eski. Shu sababli faqat ayrim fayllarni emas, butun papkani yangilash kerak.

## 0. Muhim: avval xavfsizlik

Eski kodda quyidagilar ochiq turgan edi. Ular endi koddan olib tashlangan, lekin **eski qiymatlar allaqachon oshkor bo‘lgan**:

1. **VPS ning root paroli** bir nechta skript ichida ochiq yozilgan edi. **Parolni darhol almashtiring** (`passwd`). Iloji bo‘lsa, parol bilan kirishni o‘chirib, SSH kalitga o‘ting.
2. **Telegram bot tokeni** skriptlarda ochiq edi. BotFather orqali **tokenni bekor qilib, yangisini oling** (`/revoke`). Yangi tokenni kodga yozmang: faqat `TILCOR_BOT_TOKEN` muhit o‘zgaruvchisi orqali bering.
3. Saytdagi standart parollar (admin, reviewer, guest) va «orqa eshik» kirishlar (`tilcor_session=admin` cookie, `admin_token_2026`) olib tashlandi. Parollar endi kodda saqlanmaydi.
4. Eski sayt `server.py`, `data/*.json`, `data/phd_corpus.db`, `PROJECT_CONTEXT.md` kabi fayllarni hammaga ochiq berib turgan edi. Endi faqat ommaviy sahifalar va `css/ js/ assets/ locales/` beriladi, qolgan hamma narsa 404 qaytaradi.

## 1. Zaxira nusxa

```bash
ts=$(date +%Y%m%d_%H%M)
mkdir -p /root/tilcor_backups
tar -czf /root/tilcor_backups/tilcor_before_v1_$ts.tar.gz -C /var/www tilcor
```

## 2. Yangi kodni joylash

`sources/` papkasidagi kitob PDF lari arxivga **kiritilmagan** (mualliflik huquqi; ular VPS da allaqachon bor). Shuning uchun papkani o‘chirmang, ustidan yozing:

```bash
cd /tmp && rm -rf tilcor_v1 && mkdir tilcor_v1 && cd tilcor_v1
unzip -q /path/to/tilcor_v1_2026-10-14.zip
rsync -a ./ /var/www/tilcor/          # --delete ISHLATMANG: sources/ va secrets/ saqlanib qolsin
find /var/www/tilcor -name "__pycache__" -type d -prune -exec rm -rf {} +
```

## 3. Admin parolini o‘rnatish (bitta usulni tanlang)

**A usul — fayl orqali (tavsiya etiladi):**

```bash
mkdir -p /var/www/tilcor/secrets
python3 -c "import secrets; print(secrets.token_urlsafe(18))" > /var/www/tilcor/secrets/admin.password
chmod 700 /var/www/tilcor/secrets && chmod 600 /var/www/tilcor/secrets/admin.password
cat /var/www/tilcor/secrets/admin.password      # parolni tadqiqotchiga xavfsiz yo‘l bilan bering
```

Tekshiruvchi (reviewer) kerak bo‘lsa, xuddi shunday `secrets/reviewer.password` yarating. Fayl bo‘lmasa, bu rol umuman yoqilmaydi.

**B usul — systemd orqali:** `systemctl edit tilcor` buyrug‘i bilan quyidagini qo‘shing:

```
[Service]
Environment=TILCOR_ADMIN_PASSWORD=<yangi-kuchli-parol>
```

Agar ikkala usul ham qo‘llanmasa, server birinchi ishga tushganda admin parolini o‘zi yaratib, `secrets/admin.password` ga yozadi (mode 600). Parol logga chiqmaydi.

## 4. Nginx: haqiqiy IP va https belgisi

Login urinishlari chegarasi to‘g‘ri ishlashi va cookie `Secure` bo‘lishi uchun `location /` blokida bular bo‘lsin:

```nginx
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

So‘ng: `nginx -t && systemctl reload nginx`.

## 5. Xizmatni qayta ishga tushirish

```bash
systemctl cat tilcor          # port va ishga tushirish buyrug‘ini tekshiring (masalan: python3 server.py --port 5050)
systemctl restart tilcor
sleep 5 && systemctl is-active tilcor
journalctl -u tilcor -n 30 --no-pager
```

Logda `To'liq korpus yuklandi: 8355 ta jumla` va `NLTK WordNet ... oldindan yuklandi` qatorlari chiqishi kerak.
WordNet xatosi chiqsa: `python3 -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"`.

## 6. Ma’lumotlar haqida

Arxivdagi `data/full_corpus.json` va `data/collocations_full.json` allaqachon tozalangan. Skriptlarni VPS da qayta ishga tushirish **shart emas**. Agar VPS dagi ma’lumot fayllari alohida yangilansa, quyidagi tartibda bir marta ishga tushiring (har biri o‘zi zaxira oladi):

```bash
cd /var/www/tilcor
python3 scripts/clean_reference_base_v3.py   # ma’lumotnoma bazasidagi o‘ylab topilgan MI/t-score/chastota qiymatlarini o‘chiradi
python3 scripts/clean_reference_base_v4.py   # buzuq yozuvlarni yashiradi ("play play soccer", "~", «Xazinalar oroli»)
python3 scripts/fix_corpus_metadata.py       # nashr ma’lumotlarini to‘g‘rilaydi (Sharq 2000; Yosh gvardiya 1986; 2019)
```

## 7. Tekshiruv (5 daqiqa)

```bash
B=https://tilcor.uz
for u in /server.py /data/full_corpus.json /data/phd_corpus.db /PROJECT_CONTEXT.md /secrets/admin.password /.git/config; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' $B$u)  $u   (404 bo‘lishi kerak)"; done
for u in / /korpus /kollokatsiyalar /lugat "/qidiruv?q=yurak" "/qidiruv?q=heart&lang=en" "/kwic?q=yurak" /methodology.html; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' "$B$u")  $u   (200 bo‘lishi kerak)"; done
curl -s -o /dev/null -w '%{http_code}  cookie orqali admin (302 bo‘lishi kerak)\n' -H 'Cookie: tilcor_session=admin' $B/admin_collocations.html
```

Brauzerda: `https://tilcor.uz/qidiruv?q=og‘ir uyqu` — uchta tasdiqlangan ekvivalent chiqishi kerak: *a heavy sleep* (36→74), *fell asleep* (65→98), *a deep sleep* (93→123).

## 8. Muammo bo‘lsa — orqaga qaytarish

```bash
systemctl stop tilcor
rm -rf /var/www/tilcor && tar -xzf /root/tilcor_backups/tilcor_before_v1_<sana>.tar.gz -C /var/www
systemctl start tilcor
```
