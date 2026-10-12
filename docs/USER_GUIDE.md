# TILCOR v2.0 — Foydalanuvchi Qo‘llanmasi (USER GUIDE)

**Doktorlik dissertatsiyasi tadqiqotchilari, ilmiy rahbarlar va kengash a'zolari uchun amaliy qo‘llanma.**

---

## 1. Tizimga Kirish va Rollar (Authentication & RBAC)
TILCOR platformasi uch xil kirish darajasiga ega:
1. **Tadqiqotchi (`admin`):** To‘liq boshqaruv, annotatsiya kiritish, litsenziya holatini yangilash, barcha ma'lumotlarni eksport qilish.
   - Parol: `tilcor_phd_admin_2026` (yoki `TILCOR_ADMIN_PASSWORD` muhit o‘zgaruvchisi).
2. **Ilmiy rahbar (`reviewer`):** Annotatsiyalarni tekshirish, tasdiqlash, III bob statistik jadvallarini ko‘rish va to‘liq eksport qilish.
   - Parol: `tilcor_supervisor_2026`.
3. **Mehmon / Kengash a'zosi (`guest`):** Qidiruv, KWIC konkordans va metodologiyani ko‘rish. Himoyalangan matnlarda natijalar 50 tagacha cheklangan, ommaviy yuklab olish bloklangan.
   - Parol: `tilcor_guest_2026`.

---

## 2. Qidiruv va KWIC Konkordans (`kwic_concordance.html`)
- **Qidiruv:** Istalgan so‘z yoki ko‘p so‘zli iborani kiriting (masalan, `yurak`, `old man`, `baliq`).
- **Apostrofga sezgirmaslik:** `ko'ngil`, `koʻngil` va `ko‘ngil` so‘rovlari bir xil to‘liq natija beradi.
- **Kontekst darchasi:** $\pm 2$ dan $\pm 10$ gacha so‘z kontekstini sozlash mumkin.
- **Saralash:**
  - *Matndagi tartib:* Asardagi ketma-ketlik bo‘yicha.
  - *Chap kontekst:* Chapdagi birinchi so‘z alifbosi bo‘yicha.
  - *O‘ng kontekst:* O‘ngdagi birinchi so‘z alifbosi bo‘yicha.
- **Tafsilotlar:** Har bir qator ustiga bosilganda asl jumla, uning tarjimasi va PDF beti ochiladi.

---

## 3. Annotatsiya Ish Joyi (`annotation_workspace.html`)
- **Yo‘nalish qoidasi:** Asl matn doimo chapda, Tarjima matni doimo o‘ngda.
- **Belgilash:** Tarjima matnidagi ekvivalent so‘z sichqoncha bilan belgilanadi yoki `[To‘g‘ridan-to‘g‘ri ekvivalenti yo‘q]` tugmasi bosiladi.
- **Tezkor tugmalar (Hotkeys):**
  - `Alt + S`: Qoralama sifatida saqlash (`is_confirmed = 0`).
  - `Alt + C`: Tasdiqlash (`is_confirmed = 1`).
  - `Alt + N`: Keyingi uchrashuvga o‘tish.
  - `Alt + P`: Oldingi uchrashuvga qaytish.

---

## 4. Tarjima Mutanosibligi Matritsasi va III Bob Jadvallari
- **Matritsa:** 6 ta struktur qolip va 8 ta ekvivalentlik turi kesishuvidagi sonlar dinamik hisoblanadi.
- **Drill-down:** Har qanday katak ustiga bosilganda o‘sha katakka tegishli barcha parallel jumlalar ro‘yxati chiqadi.
- **III Bob jadvallari:** Faqat tasdiqlangan annotatsiyalar asosida hisoblanadi va barcha foizlar yonida maxraj ($n = \dots$) ko‘rsatiladi.

---

## 5. Eksport Qilish
- **Formatlar:** Microsoft Excel (`.xlsx`) va CSV (UTF-8 BOM bilan).
- **Qamrov:** Faqat ko‘rinib turgan 50 ta emas, balki filtrlangan barcha satrlar eksport qilinadi.
