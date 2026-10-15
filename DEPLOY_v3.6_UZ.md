# TILCOR — 3.6-versiya: VPS ga joylash (yordamchi uchun)

Sana: 14.10.2026. Arxiv: `tilcor_v3.6_2026-10-14.zip`.

**Hozirgi holat.** 14.10.2026 soat 22:50 da tilcor.uz da v3.4 turgani tekshirildi: menyuda «Lug‘at» yo‘q, `/lugat` da eski
«Lug‘at bo‘limi hozircha yopiq» yozuvi chiqadi. v3.5 ni joylash shart emas: v3.6 uni to‘liq o‘z ichiga oladi va v3.4 ustiga ham,
v3.5 ustiga ham shu tartibda joylanadi. Arxiv v3.4 nusxasiga joylab sinaldi (Python 3.12): barcha sahifalar ochildi, himoyalangan
fayllar 404 qaytardi.

**Nima o‘zgardi (qisqacha):**
- bosh sahifa yangi ko‘rinishda («So‘zlar kontekstda.»), **Lug‘at** bo‘limi ochildi;
- tadqiqotchi kabinetida **Inson tekshiruvi** (`/baholash`): tadqiqotchi va ikkinchi annotator platforma natijalarini baholaydi;
- statistika sahifasida tayanch korpus, teng (qiyosiy) matnlar, yo‘nalishlar orasidagi statistik testlar va inson tekshiruvi
  natijalari bo‘limlari;
- statistikadagi token sanog‘i tuzatildi (endi 214 244);
- yangi fayllar: `analysis.py`, `validation.py`, `validation_pages.py`, `corpus_dictionary.py`, `data/corpus_dictionary.json`,
  `data/reference_en.json`, `data/comparable_stats.json`, `data/validation/samples.json` va `scripts/` dagi skriptlar.

Yangi kutubxona kerak emas. Python 3.8 yoki yangisi bo‘lishi kerak (`python3 --version`).

**Kalit haqida.** Asl koddan qolgan AI xizmati kaliti oldingi versiyalarda `server.py` ichida yozilgan edi; v3.6 da u olib
tashlandi. O‘sha kalitni xizmat egasining kabinetida bekor qiling (tadqiqotchi yoki kalit egasi).

## 1. Tekshiruv va zaxira

```bash
python3 --version
python3 -c "import json; d=json.load(open('/var/www/tilcor/data/full_corpus.json')); print(sum(1 for r in d if r.get('status')=='tasdiqlangan'))"
```

**15** chiqsa — davom eting. 15 dan ko‘p bo‘lsa — joylamang, faylni tadqiqotchiga yuboring.

```bash
ts=$(date +%Y%m%d_%H%M); mkdir -p /root/tilcor_backups
tar -czf /root/tilcor_backups/tilcor_before_v36_$ts.tar.gz -C /var/www tilcor
ls -la /root/tilcor_backups/
```

## 2. Joylash

```bash
cd /tmp && rm -rf tilcor_v36 && mkdir tilcor_v36 && cd tilcor_v36
unzip -q /path/to/tilcor_v3.6_2026-10-14.zip
rsync -a ./ /var/www/tilcor/          # --delete ISHLATMANG: secrets/, sources/ va baholar fayli saqlanib qolsin
find /var/www/tilcor -name "__pycache__" -type d -prune -exec rm -rf {} +
systemctl restart tilcor && sleep 6 && systemctl is-active tilcor
journalctl -u tilcor -n 40 --no-pager | grep -E "korpus yuklandi|not loaded|Error|Traceback"
```

- «korpus yuklandi» qatorida «10076 ta jumla» bo‘lishi kerak.
- `not loaded`, `Error` yoki `Traceback` chiqsa — to‘xtang, shu chiqishni tadqiqotchiga yuboring va 5-qadam bilan qaytaring.

## 3. Tekshiruv

```bash
B=https://tilcor.uz
for u in /server.py /data/full_corpus.json /data/corpus_dictionary.json /data/reference_en.json /data/validation/samples.json \
         /data/validation/annotations.json /secrets/admin.password /secrets/annotator.password /.git/config /notes/tanlab_tekshiruv_lugat_2026-10-14.md; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' $B$u)  $u   (404 bo‘lishi kerak)"; done
for u in "/?lang=uz" "/?lang=en" "/?lang=ru" "/css/tilcor.css?v=3.6" /lugat "/lugat?q=yurak" "/lugat?q=heart" "/qidiruv?q=yurak" "/kwic?q=yurak" \
         /kollokatsiyalar /korpus /metodologiya /statistika; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' "$B$u")  $u   (200 bo‘lishi kerak)"; done
echo "$(curl -s -o /dev/null -w '%{http_code}' $B/baholash)  /baholash   (302 bo‘lishi kerak: kirish sahifasiga yo‘naltiradi)"
curl -s "$B/" | grep -c "kontekstda"          # 1 bo‘lishi kerak
curl -s "$B/" | grep -cE "214.{1,2}244"       # 1 yoki ko‘proq (sonlar orasida bo‘linmaydigan bo‘shliq)
curl -s "$B/statistika" | grep -c "Tayanch korpus"   # 1 yoki ko‘proq
```

`grep -c` 0 chiqsa, oraliq kesh eski sahifani bermoqda: v3.2 yo‘riqnomasidagi 3-qadamni bajaring.

Brauzerda (kompyuter va telefon):
- bosh sahifada katta «So‘zlar kontekstda.» sarlavhasi, oq yumaloq qidiruv qatori va ostida namuna so‘rovlar;
- menyuda **Lug‘at**; `/lugat?q=ko‘ngil` — 1-tarjima **heart**, ostida kitobdan misol;
- statistika sahifasida 5-bo‘lim «Tayanch korpus», 6-bo‘lim «Teng (qiyosiy) matnlar», 7-bo‘lim «Inson tekshiruvi natijalari»;
- tadqiqotchi sifatida kirilganda yuqori menyudagi «Laboratoriya» ichida **Inson tekshiruvi**.

Natijani (ekrandan rasm yoki yuqoridagi buyruqlar chiqishi) tadqiqotchiga yuboring.

## 4. Ikkinchi annotator uchun parol (tadqiqotchi so‘raganda)

Ikkinchi annotator «annotator» nomi bilan kiradi. Parol fayli bo‘lmasa, bu foydalanuvchi umuman yoqilmaydi.

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(14))" > /var/www/tilcor/secrets/annotator.password
chmod 600 /var/www/tilcor/secrets/annotator.password
systemctl restart tilcor
cat /var/www/tilcor/secrets/annotator.password     # parolni tadqiqotchiga xavfsiz yo‘l bilan bering, chatga yozmang
```

## 5. Baholar fayli

Baholar `/var/www/tilcor/data/validation/annotations.json` ga yoziladi. Bu fayl hech qaysi yangilash arxivida yo‘q, shuning uchun
yangilash uni o‘chirmaydi. Baholash boshlangach, uni haftada bir marta alohida saqlang:

```bash
mkdir -p /root/tilcor_backups/annotations
cp /var/www/tilcor/data/validation/annotations.json /root/tilcor_backups/annotations/annotations_$(date +%Y%m%d).json
```

`scripts/build_validation_samples.py` ni serverda ishga tushirmang: tanlanma o‘zgarsa, eski baholar yangi birliklarga mos kelmaydi.

## 6. Orqaga qaytarish

Avval baholar faylini saqlang (bo‘lsa), keyin joriy papkani chetga oling va zaxirani oching:

```bash
cp /var/www/tilcor/data/validation/annotations.json /root/ 2>/dev/null
systemctl stop tilcor
mv /var/www/tilcor /root/tilcor_v36_olib_tashlangan_$(date +%Y%m%d_%H%M)
tar -xzf /root/tilcor_backups/tilcor_before_v36_SANA.tar.gz -C /var/www     # SANA — 1-qadamdagi fayl nomidan
systemctl start tilcor && sleep 6 && systemctl is-active tilcor
```
