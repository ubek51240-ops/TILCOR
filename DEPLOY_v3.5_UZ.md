# TILCOR — 3.5-versiya: VPS ga joylash (yordamchi uchun)

Sana: 14.10.2026. Arxiv: `tilcor_v3.5_2026-10-14.zip`. Saytda hozir v3.3 yoki v3.4 turibdi; bu versiya ikkalasining ustiga ham
joylanadi va ularni to‘liq o‘z ichiga oladi.

**Nima o‘zgardi (v3.5):**
- yangi **«Lug‘at»** bo‘limi (`/lugat`): o‘zbekcha–inglizcha va inglizcha–o‘zbekcha korpus lug‘ati (1 125 + 968 bosh so‘z);
  har bir tarjima — tarjimonning kitobdagi so‘zi, soni va misol gap juftligi bilan;
- yangi fayllar: `corpus_dictionary.py`, `data/corpus_dictionary.json`, `scripts/build_corpus_dictionary.py`;
- metodologiyada yangi 7-band, keyingi bandlar 8–11;
- dizayn tuzatishlari: bosh sahifadagi raqamli kartochkalar noutbuk ekranida kesilmaydi, o‘rta kenglikdagi ekranda menyu tugma orqali ochiladi.

Yangi kutubxona kerak emas. Uslublar fayli `?v=3.5` bilan ulanadi, brauzer keshi o‘zi yangilanadi.

## 0. Xavfsizlik (hali qilinmagan bo‘lsa — avval shu)

- VPS root parolini almashtiring (`passwd`). Eski parol `ubek51240-ops/tilcor` ochiq repozitoriysida yozilgan, uni har kim o‘qiy oladi.
- O‘sha repozitoriyni yoping (Settings → Danger zone → Change visibility → Private) yoki o‘chiring.
- Chatga yozilgan GitHub tokenini bekor qiling (GitHub → Settings → Developer settings → Personal access tokens → Delete).
- Telegram bot tokenini BotFather orqali bekor qiling.

## 1. Tekshiruv va zaxira

```bash
python3 -c "import json; d=json.load(open('/var/www/tilcor/data/full_corpus.json')); print(sum(1 for r in d if r.get('status')=='tasdiqlangan'))"
```

**15** chiqsa — davom eting. 15 dan ko‘p bo‘lsa — joylamang, faylni tadqiqotchiga yuboring.

```bash
ts=$(date +%Y%m%d_%H%M); mkdir -p /root/tilcor_backups
tar -czf /root/tilcor_backups/tilcor_before_v35_$ts.tar.gz -C /var/www tilcor
```

## 2. Joylash

```bash
cd /tmp && rm -rf tilcor_v35 && mkdir tilcor_v35 && cd tilcor_v35
unzip -q /path/to/tilcor_v3.5_2026-10-14.zip
rsync -a ./ /var/www/tilcor/          # --delete ISHLATMANG
find /var/www/tilcor -name "__pycache__" -type d -prune -exec rm -rf {} +
systemctl restart tilcor && sleep 6 && systemctl is-active tilcor
journalctl -u tilcor -n 30 --no-pager | grep -E "korpus yuklandi|corpus dictionary"
```

- «korpus yuklandi» qatorida «10076 ta jumla» bo‘lishi kerak.
- «corpus dictionary not loaded» degan qator chiqsa — `data/corpus_dictionary.json` ko‘chmagan: `ls -la /var/www/tilcor/data/corpus_dictionary.json`
  (taxminan 560 KB bo‘lishi kerak) va 2-qadamni qaytaring.

## 3. Tekshiruv

```bash
B=https://tilcor.uz
for u in /server.py /data/full_corpus.json /data/corpus_dictionary.json /secrets/admin.password /.git/config /notes/tanlab_tekshiruv_lugat_2026-10-14.md; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' $B$u)  $u   (404 bo‘lishi kerak)"; done
for u in "/?lang=uz" "/css/tilcor.css?v=3.5" /lugat "/lugat?q=yurak" "/lugat?q=heart" "/lugat?yo=uz&harf=Sh" "/qidiruv?q=yurak" /kollokatsiyalar /metodologiya; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' "$B$u")  $u   (200 bo‘lishi kerak)"; done
curl -s "$B/lugat?q=yurak" | grep -c "tc-sense"          # 1 yoki ko‘proq bo‘lishi kerak
curl -s "$B/" | grep -c "Tarjimon so‘zni qanday bergan"  # 1 bo‘lishi kerak (0 bo‘lsa — oraliqda kesh, v3.2 yo‘riqnomasidagi 3-qadam)
```

Brauzerda (kompyuter va telefon):
- yuqori menyuda **Lug‘at** bandi bor; `/lugat` da yo‘nalish tugmalari (bayroqlar bilan), qidiruv qatori, alifbo va
  «Ko‘p uchraydigan so‘zlar»;
- `/lugat?q=ko‘ngil` — katta «ko‘ngil» so‘zi, 1-tarjima **heart**, ostida kitobdan misol (Cho‘lpon, 169-bet ↔ Fort, 188-bet);
  o‘ngda «Kollokatsiyalari» (ona ko‘ngli …);
- qidiruv qatoriga `heart` yozilsa, inglizcha–o‘zbekcha qism o‘zi ochiladi: ko‘ngil, yurak;
- metodologiya sahifasida «7. Korpus lug‘ati» va «11. Cheklovlar».

Natijani (ekrandan rasm yoki yuqoridagi buyruqlar chiqishi) tadqiqotchiga yuboring.

## 4. Orqaga qaytarish

```bash
systemctl stop tilcor
rm -rf /var/www/tilcor && tar -xzf /root/tilcor_backups/tilcor_before_v35_<sana>.tar.gz -C /var/www
systemctl start tilcor
```
