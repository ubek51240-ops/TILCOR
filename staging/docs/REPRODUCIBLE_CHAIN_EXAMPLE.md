# TILCOR v2.0 — Takrorlanuvchan Namunaviy Zanjir (Reproducible Chain Example)

**Dissertatsiyaning 2.3-bobi va Ilovalari uchun rasmiy namunaviy tadqiqot zanjiri.**

Ushbu hujjat bitta kollokatsiyaning asl PDF manbasidan to yakuniy dissertatsiya jadvali va eksport qatorigacha bosib o‘tgan 7 bosqichli audit yo‘lini aks ettiradi.

---

### 1-QADAM: Asl PDF Manba Sahifasi (PDF Source Page)
- **Asar:** Ernest Hemingway, *«The Old Man and the Sea»* (1952)
- **Fayl:** `oldmansea.pdf` (SHA-256: `0ad1d820761a5aca9df52c22ea1cfc4ca5dad64923f51270dbe8f106f3817eef`)
- **PDF sahifasi:** 1-bet (Bosma nashrda: 3-bet).
- **Asl matn parchasi:**
  > *"He was an old man who fished alone in a skiff in the Gulf Stream and he had gone eighty-four days now without taking a fish."*

---

### 2-QADAM: Matn Segmenti (Segment Entity)
- **Segment ID:** `seg-book-hemingway-en-p002-s001`
- **Kitob ID:** `book-hemingway-en`
- **Turi:** `body` (asosiy matn)
- **Sifat bayrog‘i (Quality flag):** `OK` (kolontitullardan tozalangan, dehyphenation qo‘llangan).

---

### 3-QADAM: Parallel Tekislangan Juftlik (Alignment Entity)
- **Alignment ID:** `aln-hem-0001`
- **Asl jumla (Source - EN):**
  > *"- 1 - By Ernest Hemingway To Charlie Shribner And To Max Perkins He was an old man who fished alone in a skiff in the Gulf Stream and he had gone eighty-four days now without taking a fish."*
- **Tarjima jumlasi (Target - UZ, Ibrohim G‘afurov):**
  > *"Ernest XEMINGUEY CHOL VA DENGIZ Qissa Ibrohim G‘OFUROV tarjimasi Toshkent «Yosh gvardiya» nashriyoti Chol qayiqda yolg‘iz o‘zi Golfstrimda baliq ovlardi. Dengizga chiqayotganiga mana sakson to‘rt kun ham to‘ldi, ammo hali bironta baliq tutganicha yo‘q."*
- **Tekislash usuli:** `anchor_window_v1`
- **Baho:** `needs_review` $\rightarrow$ Tadqiqotchi tomonidan tekshirilgan.

---

### 4-QADAM: Kollokatsiya Uchrashuvi (Occurrence Entity)
- **Occurrence ID:** `occ-00002`
- **Nomzod ID (Candidate ID):** `col-hem-1`
- **Inglizcha birikma:** `fished alone`
- **O‘zbekcha ekvivalent:** `baliq ovlardi` (yoki `yolg‘iz baliq ovlardi`)
- **PDF beti:** 1

---

### 5-QADAM: Ekspert Annotatsiyasi (Annotation Entity)
- **Annotator:** `admin` (Voxitov Ibrohim Sodiq o‘g‘li)
- **Birlik turi (`unit_type`):** `kollokatsiya`
- **Struktur qolip (`structural_pattern`):** `Fel+Ot`
- **Semantik guruh (`semantic_group`):** `tabiat_borliq`
- **Ekvivalentlik turi (`equivalence_type`):** `toliq_ekvivalent`
- **Tarjima strategiyasi (`translation_strategy`):** `bevosita_tarjima`
- **Lingvomadaniy realiya (`cultural_marker`):** `neytral`
- **Holati:** `is_confirmed = 1` (Tadqiqotchi tomonidan to‘liq tasdiqlangan).

---

### 6-QADAM: Matematik Assotsiatsiya Hisobi (Statistics Table Row)
- **Korpus hajmi ($N$):** 27,091 token
- **Birga uchrash chastotasi ($O_{11}$):** 1
- **$w_1$ ning chastotasi ($R_1$):** 2
- **$w_2$ ning chastotasi ($C_1$):** 15
- **Kutilgan chastota ($E_{11}$):** $0.0011$
- **Pointwise Mutual Information ($MI$):** $9.82$
- **Student's $t$-score:** $0.998$
- **Dunning Log-Likelihood ($G^2$):** $13.56$
- **Normallashtirilgan chastota (10k tokenga):** $0.369$

---

### 7-QADAM: Eksport Qatori (Export Row)
- **Eksport fayli:** `tilcor_parallel_corpus_stage9.xlsx` / `.csv`
- **Qator ma'lumotlari:**
  ```csv
  Record_ID: occ-00002
  Work: The Old Man and the Sea
  Edition: Charles Scribner's Sons, 1952
  Direction: EN ➔ UZ
  Source_Segment: ...fished alone in a skiff in the Gulf Stream...
  Target_Segment: ...Chol qayiqda yolg‘iz o‘zi Golfstrimda baliq ovlardi...
  Matched_Span: fished alone
  Equivalent_Span: baliq ovlardi
  PDF_Page: 1
  Structural_Pattern: Fel+Ot
  Equivalence_Type: toliq_ekvivalent
  Alignment_Status: confirmed
  Annotator: admin
  Guideline_Version: v1.0
  ```
