# TILCOR — 2-versiya: VPS ga joylash (yordamchi uchun)

Sana: 14.10.2026. Arxiv: `tilcor_v2_2026-10-14.zip`. Bu arxiv 1-versiyani to‘liq o‘z ichiga oladi.
1-versiya hali joylanmagan bo‘lsa, faqat shu 2-versiyani joylang. Qadamlar `DEPLOY_v1_UZ.md` bilan bir xil
(zaxira, rsync `--delete`siz, admin paroli, nginx sarlavhalari, qayta ishga tushirish). Quyida faqat farqlar yozilgan.

## 1. Joylashdan oldin: tadqiqotchi saytda juftlik tasdiqlaganmi?

2-versiyada `data/full_corpus.json` butunlay yangilangan (gaplar qayta tekislangan). Agar tadqiqotchi
1-versiyadan keyin admin panelda yangi juftliklarni tasdiqlagan bo‘lsa, ular ustidan yozilib ketmasligi kerak.
VPS da tekshiring:

```bash
python3 -c "import json; d=json.load(open('/var/www/tilcor/data/full_corpus.json')); print(sum(1 for r in d if r.get('status')=='tasdiqlangan'))"
```

- Natija **30 yoki undan kam** bo‘lsa — davom eting.
- Natija **30 dan ko‘p** bo‘lsa — joylamang. `/var/www/tilcor/data/full_corpus.json` faylini tadqiqotchiga yuboring:
  yangi tasdiqlarni yangi korpusga ko‘chirish kerak.

## 2. Joylash

`DEPLOY_v1_UZ.md` dagi 1–5-qadamlar. Arxivda ma’lumotlar tayyor. VPS da hech qanday skriptni ishga tushirish shart emas.

## 3. Tekshiruv

`DEPLOY_v1_UZ.md` dagi 7-qadamdagi buyruqlar, qo‘shimcha ravishda:

```bash
B=https://tilcor.uz
for u in /methodology.html /sources_rights.html /methodology_statistics.html /annotation_guidelines.html /about_project.html \
         "/methodology.html?lang=en" "/methodology.html?lang=ru" "/kwic?q=heart&lang=en"; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' "$B$u")  $u   (200 bo‘lishi kerak)"; done
```

Statistika sahifasida «Kecha va kunduz» uchun 80 594 token, juftliklar jadvalida jami 8 368 va 1 728 juftlik,
tasdiqlangani 15 va 0 ko‘rinishi kerak.

## 4. Orqaga qaytarish

`DEPLOY_v1_UZ.md`, 8-qadam.
