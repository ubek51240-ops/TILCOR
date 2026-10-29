# TILCOR — 3.9-versiya: VPS ga joylash (yordamchi uchun)

Sana: 29.10.2026. v3.9 — morfologik va semantik teglash moduli (`tagging.py`, 16.10.2026 da VPS ga yuklangan, lekin
saytga ulanmagan edi) endi qidiruv, kollokatsiya va ro‘yxat sahifalariga hamda `/api/tags` ga ulandi.
Joylash tartibi DEPLOY_v3.7_UZ.md dagi bilan BIR XIL (zaxira → yuklash → rsync `--delete`siz → kompilyatsiya →
restart → tekshiruv). Hammasi bitta skriptda:

```powershell
$env:TILCOR_VPS_PASSWORD = "<parol>"
python scripts\deploy_v39_to_vps.py
```

**Nima o‘zgardi (v3.9):**
- `ui_components.py`: «So‘z shakllari» jadvalida «Morfologiya» ustuni; «Teglar (avtomatik)» bo‘limi qidiruv, `/soz/` va
  `/kollokatsiya/` sahifalarida; `/kollokatsiyalar` da semantik guruh filtri (`?guruh=…`);
- `server.py`: `/api/tags?q=<so‘z>&til=uz|en` (tezlik chekovi 120/daqiqa), `guruh` parametri;
- `citation_pages.py`: teglar bo‘limi, iqtibosda versiya 3.9;
- `locales/uz|en|ru.json`: 40 ta yangi kalit (`tags_*`, `sem_*`, `pos_*`), ruscha so‘z turkumlari to‘liq so‘z bilan;
- `scripts/verify_v39_pages.py`: 21 ta tekshiruv (deploy skripti oxirida avtomatik ishlaydi).

## Qo‘shimcha tekshiruvlar (v3.7 tekshiruvlaridan keyin)

```bash
B=https://tilcor.uz
for u in /tagging.py /data/tags_index.json /scripts/build_tags_index.py; do echo "$u (404 kerak): $(curl -s -o /dev/null -w '%{http_code}' $B$u)"; done
curl -s "$B/api/tags?q=yuraklarida&til=uz" | head -c 300; echo      # lemma yurak, -lar -i -da, Case=Loc
curl -s "$B/qidiruv?q=yurak" | grep -c "Teglar (avtomatik)"           # 1 yoki ko‘proq
curl -s "$B/kollokatsiya/en-92df8fc4e3" | grep -c "Ijtimoiy-madaniy"  # 1 yoki ko‘proq
curl -s "$B/kollokatsiyalar?guruh=inson_ruhiyati" | grep -c 'aria-current="true">Inson'   # 1
```

Brauzerda: `yurak` qidirilganda «So‘z shakllari» jadvalida «Morfologiya» ustuni (yurak + -i, egalik, III shaxs) va
«Teglar (avtomatik)» bo‘limi; `/kollokatsiyalar` da «Semantik guruh (3.1)» chiplari; har bir teg yonida oltin
«Avtomatik teg — tadqiqotchi tasdig‘i kutilmoqda» belgisi.

## Orqaga qaytarish

```bash
ls -t /root/tilcor_backups/tilcor_before_v39_*.tar.gz | head -1
tar -xzf /root/tilcor_backups/tilcor_before_v39_<sana>.tar.gz -C /var/www && systemctl restart tilcor
```
