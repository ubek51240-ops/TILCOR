# TILCOR v2.0 — Zaxira Nusxalash va Qayta Tiklash Yo‘riqnomasi (BACKUP & RESTORE)

Platforma ma'lumotlar bazasining doimiy yaxlitligi va falokatdan keyin qayta tiklanishini ta'minlovchi qo‘llanma.

---

## 1. Zaxira Nusxasi Qanday Yaratiladi? (Backup Procedure)
Zaxira nusxasi atomar darajada SQLite `backup` APIsi orqali yaratiladi, bu esa baza faol ishlab turgan vaqtda ham ma'lumotlar buzilmasligini kafolatlaydi.

### Qo‘lda buyruq orqali zaxiralash:
```powershell
python scripts/backup_corpus.py
```

### Amal mexanizmi:
1. `data/phd_corpus.db` o‘qiladi.
2. `backups/phd_corpus_backup_YYYYMMDD_HHMMSS.db` fayli shakllanadi.
3. Faylning SHA-256 xesh summasi hisoblanadi va `.sha256` fayliga yoziladi.
4. Terminalda `[BACKUP SUCCESS]` xabari va xesh qiymati ko‘rsatiladi.

---

## 2. Qayta Tiklash Qanday Amalga Oshiriladi? (Restore Procedure)
Qayta tiklash jarayoni 3 bosqichli xavfsizlik tekshiruvidan so‘ng atomar fayl almashtirish (`os.replace`) orqali bajariladi:

### Buyruq orqali tiklash:
```powershell
python scripts/restore_corpus.py
```

### Tekshiruv bosqichlari:
1. **SHA-256 tekshiruvi:** Zaxira faylining joriy xeshi dastlabki yaratilgan xesh bilan baytma-bayt solishtiriladi. Agar mos kelmasa, tiklash to‘xtatiladi.
2. **SQLite Quick Check:** `PRAGMA quick_check` buyrug‘i orqali B-Tree tuzilishi tekshiriladi.
3. **Foreign Key Integrity:** `PRAGMA foreign_key_check` buyrug‘i orqali barcha relyatsion bog‘liqliklar 0 ta xatoga ega ekanligi tasdiqlanadi.
4. **Atomar almashtirish:** Baza to‘liq tekshirilgandan so‘nggina `data/phd_corpus.db` o‘rniga joylanadi.
