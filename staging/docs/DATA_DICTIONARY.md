# TILCOR v2.0 — Ma'lumotlar Lug‘ati (DATA DICTIONARY)

Ushbu hujjat `phd_corpus.db` relyatsion bazasidagi barcha 14 ta jadval, ularning ustunlari, turlari, cheklovlari va ma'nolari haqida to‘liq ma'lumot beradi.

---

### 1. `works` (Asarlar)
| Maydon | Turi | Cheklov | Tavsif |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Asar identifikatori (masalan, `work-cholpon-kk`) |
| `title` | TEXT | NOT NULL | Asarning asl nomi |
| `author` | TEXT | NOT NULL | Muallif F.I.Sh. |
| `original_language` | TEXT | NOT NULL | Asl tili (`uz` yoki `en`) |
| `year` | INTEGER | — | Yozilgan yoki ilk chop etilgan yili |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Yozuv yaratilgan vaqti |

---

### 2. `editions` (Nashrlar)
| Maydon | Turi | Cheklov | Tavsif |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Nashr identifikatori (masalan, `ed-cholpon-uz`) |
| `work_id` | TEXT | FK -> works(id) | Tegishli asar IDsi |
| `publisher` | TEXT | NOT NULL | Nashriyot nomi |
| `place` | TEXT | — | Nashr qilingan shahar |
| `year` | INTEGER | — | Nashr yili |
| `isbn` | TEXT | — | ISBN raqami (mavjud bo‘lsa) |
| `print_pages` | INTEGER | NOT NULL | Bosma sahifalar soni |
| `pdf_pages` | INTEGER | NOT NULL | PDF fayldagi jami sahifalar soni |
| `source_filename` | TEXT | NOT NULL | Asl PDF fayl nomi |
| `source_file_sha256` | TEXT | NOT NULL | Faylning SHA-256 xesh summasi |

---

### 3. `texts` (Matn Qatlamlari)
| Maydon | Turi | Cheklov | Tavsif |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Matn identifikatori (masalan, `txt-cholpon-uz`) |
| `work_id` | TEXT | FK -> works(id) | Tegishli asar |
| `edition_id` | TEXT | FK -> editions(id) | Tegishli nashr |
| `role` | TEXT | NOT NULL | `original` yoki `translation` |
| `language` | TEXT | NOT NULL | `uz` yoki `en` |
| `translator` | TEXT | — | Tarjimon F.I.Sh. |
| `direction` | TEXT | NOT NULL | `UZ->EN` yoki `EN->UZ` |
| `status` | TEXT | NOT NULL | `active` yoki `quarantined` |
| `licence_status` | TEXT | NOT NULL | `public_domain`, `protected`, `permission_granted` |
| `permission_note` | TEXT | — | Huquqiy asos yoki ruxsatnoma izohi |
| `permission_doc_path` | TEXT | — | Ruxsat xatining ichki fayl yo‘li |

---

### 4. `pages` (Sahifalar)
| Maydon | Turi | Cheklov | Tavsif |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Sahifa IDsi |
| `book_id` | TEXT | FK -> texts(id) | Tegishli matn |
| `page_num` | INTEGER | NOT NULL | PDF sahifa raqami (1-indexed) |
| `raw_text` | TEXT | — | Xom ajratilgan matn |
| `clean_text` | TEXT | — | Tozalangan matn |
| `status` | TEXT | NOT NULL | `OK`, `EMPTY_PAGE`, `NO_TEXT_LAYER_MISSING` |

---

### 5. `segments` (Jumla va Dialog Segmentlari)
| Maydon | Turi | Cheklov | Tavsif |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Segment IDsi |
| `book_id` | TEXT | FK -> texts(id) | Tegishli matn |
| `page_id` | TEXT | FK -> pages(id) | Tegishli sahifa |
| `pdf_page_num` | INTEGER | NOT NULL | PDF beti |
| `segment_index` | INTEGER | NOT NULL | Matn oqimidagi tartib raqami |
| `segment_type` | TEXT | NOT NULL | `body`, `dialogue`, `heading`, `footnote` |
| `raw_text` | TEXT | NOT NULL | Dastlabki matn |
| `clean_text` | TEXT | NOT NULL | Dehyphenated toza matn |
| `token_count` | INTEGER | NOT NULL | So‘zlar soni |
| `quality_flag` | TEXT | NOT NULL | Sifat bayrog‘i |

---

### 6. `alignments` (Parallel Jumlalar Bog‘lanishi)
| Maydon | Turi | Cheklov | Tavsif |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Tekislash juftligi IDsi |
| `source_book_id` | TEXT | NOT NULL | Asl matn kitob IDsi |
| `target_book_id` | TEXT | NOT NULL | Tarjima kitob IDsi |
| `source_text` | TEXT | NOT NULL | Asl jumla(lar) |
| `target_text` | TEXT | NOT NULL | Tarjima jumla(lar) |
| `alignment_type` | TEXT | NOT NULL | `1:1`, `1:2`, `2:1`, `n:m` |
| `alignment_method` | TEXT | NOT NULL | Algoritm nomi |
| `confidence_score` | REAL | — | Algoritm xarajat bali (xom ball) |
| `status` | TEXT | NOT NULL | `needs_review`, `draft`, `confirmed` |

---

### 7. `collocation_occurrences` (Kollokatsiya Uchrashuvlari)
| Maydon | Turi | Cheklov | Tavsif |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Uchrashuv IDsi (masalan, `occ-00002`) |
| `candidate_id` | TEXT | FK -> collocation_candidates(id) | Nomzod IDsi |
| `alignment_id` | TEXT | FK -> alignments(id) | Parallel jumla IDsi |
| `book_id` | TEXT | NOT NULL | Kitob IDsi |
| `pdf_page_num` | INTEGER | NOT NULL | PDF sahifasi |
| `matched_span_uz` | TEXT | — | O‘zbekcha birikma matni |
| `matched_span_en` | TEXT | — | Inglizcha birikma matni |

---

### 8. `phd_annotations` (Ekspert Annotatsiyalari)
| Maydon | Turi | Cheklov | Tavsif |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Annotatsiya IDsi |
| `occurrence_id` | TEXT | FK -> collocation_occurrences(id) | Tegishli uchrashuv |
| `annotator_user` | TEXT | NOT NULL | Annotator (`admin`, `reviewer`) |
| `unit_type` | TEXT | NOT NULL | Taksonomiya: Birlik turi |
| `structural_pattern` | TEXT | NOT NULL | Taksonomiya: Struktur qolip |
| `semantic_group` | TEXT | NOT NULL | Taksonomiya: Semantik guruh |
| `equivalence_type` | TEXT | NOT NULL | Taksonomiya: Ekvivalentlik turi |
| `translation_strategy`| TEXT | NOT NULL | Taksonomiya: Tarjima strategiyasi |
| `cultural_category` | TEXT | NOT NULL | Taksonomiya: Lingvomadaniy realiya |
| `source_span` | TEXT | — | Asl birikma chegarasi |
| `target_span` | TEXT | — | Tarjima ekvivalenti chegarasi |
| `is_confirmed` | INTEGER | DEFAULT 0 | 1 = Tasdiqlangan, 0 = Qoralama |

---

### 9. `association_measures` (2×2 Kontingentlik va Statistik Mezonlar)
| Maydon | Turi | Cheklov | Tavsif |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Assotsiatsiya yozuv identifikatori |
| `candidate_id` | TEXT | FK -> collocation_candidates(id) | Nomzod IDsi |
| `language` | TEXT | NOT NULL | Til (`uz` yoki `en`) |
| `node_token` | TEXT | NOT NULL | Tugun so‘z ($w_1$) |
| `collocate_token` | TEXT | NOT NULL | Birikuvchi so‘z ($w_2$) |
| `window_type` | TEXT | NOT NULL | Kontekst turi (`adjacent`, `window_5`) |
| `min_threshold` | INTEGER | NOT NULL | Minimal chastota chegarasi |
| `o11` | REAL | NOT NULL | Birga uchrashish chastotasi ($O_{11}$) |
| `o12` | REAL | NOT NULL | $w_1 \wedge \neg w_2$ ($O_{12}$) |
| `o21` | REAL | NOT NULL | $\neg w_1 \wedge w_2$ ($O_{21}$) |
| `o22` | REAL | NOT NULL | $\neg w_1 \wedge \neg w_2$ ($O_{22}$) |
| `r1` | REAL | NOT NULL | $w_1$ ning jami chastotasi ($R_1$) |
| `c1` | REAL | NOT NULL | $w_2$ ning jami chastotasi ($C_1$) |
| `corpus_size_n` | INTEGER | NOT NULL | Jami tokenlar soni ($N$) |
| `expected_e11` | REAL | NOT NULL | Kutilgan chastota ($E_{11}$) |
| `mi_score` | REAL | NOT NULL | Pointwise Mutual Information ($MI$) |
| `t_score` | REAL | NOT NULL | Student's $t$-score |
| `log_likelihood_g2` | REAL | NOT NULL | Dunning Log-Likelihood ($G^2$) |
| `normalized_freq_per_10k` | REAL | NOT NULL | 10k tokenga normallashtirilgan chastota |
| `calculated_at` | DATETIME | NOT NULL | Hisoblash vaqti |

