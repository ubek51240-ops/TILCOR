-- =====================================================================
-- PhD RESEARCH PARALLEL CORPUS SCHEMA (Bilingual Uzbek-English)
-- Research Title: TARJIMA VA TENG MATNLAR PARALLEL KORPUSIDA
--                 O'ZARO FAOL BIRIKUVCHI (KOLLOKATSION) SO'ZLAR TADQIQI
-- Chapters Supported:
--   II Bob: Metodologiya, dasturiy ta'minot va korpus dizayni (2.1 - 2.3)
--   III Bob: Semantik-struktur, ekvivalentlik va lingvomadaniy tasnif (3.1 - 3.3)
-- Unicode: UTF-8 strict (o', g', tutuq belgisi, kirill/lotin)
-- Provenance: Har bir segment va kollokatsiya manba kitob va sahifaga bog'langan
-- =====================================================================

PRAGMA foreign_keys = ON;
PRAGMA encoding = 'UTF-8';

-- 1. Kitoblar va meta-ma'lumotlar jadvali
CREATE TABLE IF NOT EXISTS books (
    id TEXT PRIMARY KEY,                       -- e.g. 'book-cholpon-uz', 'book-cholpon-en'
    pair_id TEXT NOT NULL,                     -- e.g. 'pair-night-and-day', 'pair-old-man-sea'
    role TEXT NOT NULL,                        -- 'source' (original) yoki 'target' (translation)
    language TEXT NOT NULL,                    -- 'uz' yoki 'en'
    title TEXT NOT NULL,                       -- Asar nomi
    author TEXT NOT NULL,                      -- Muallif
    translator TEXT,                           -- Tarjimon (agar tarjima bo'lsa)
    pub_year TEXT,                             -- Nashr yili
    publisher TEXT,                            -- Nashriyot
    isbn TEXT,                                 -- ISBN kodi
    license TEXT NOT NULL,                     -- Litsenziya / Fair Use izohi
    source_pdf_filename TEXT NOT NULL,         -- Asl PDF fayl nomi
    source_pdf_sha256 TEXT NOT NULL,           -- PDF SHA256 nazorat yig'indisi
    total_pages INTEGER NOT NULL,              -- Sahifalar soni
    is_active INTEGER DEFAULT 1,               -- 1 = faol korpus qismi
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Sahifalar jadvali (Page-level extraction va visual traceability)
CREATE TABLE IF NOT EXISTS pages (
    id TEXT PRIMARY KEY,                       -- e.g. 'page-cholpon-uz-004'
    book_id TEXT NOT NULL,
    pdf_page_num INTEGER NOT NULL,             -- PDF dagi haqiqiy bet raqami (1-based)
    printed_page_num INTEGER,                  -- Kitob betiga bosilgan raqam (agar mavjud bo'lsa)
    raw_text TEXT NOT NULL,                    -- O'zgartirilmagan xom matn
    clean_text TEXT NOT NULL,                  -- Normalizatsiya qilingan matn
    char_count INTEGER NOT NULL,               -- Belgilar soni
    token_count INTEGER NOT NULL,              -- So'zlar soni
    has_text_layer INTEGER NOT NULL,           -- 1 = raqamli matn qatlami, 0 = skan
    extraction_method TEXT NOT NULL,           -- 'pymupdf_v1.24', 'ocr_tesseract', h.k.
    quality_flag TEXT DEFAULT 'OK',            -- 'OK', 'SUSPICIOUS_HYPHEN', 'EMPTY', 'HEADER_NOISE'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE RESTRICT
);

-- 3. Matn segmentlari / jumlalar jadvali
CREATE TABLE IF NOT EXISTS segments (
    id TEXT PRIMARY KEY,                       -- e.g. 'seg-cholpon-uz-p004-s001'
    book_id TEXT NOT NULL,
    page_id TEXT NOT NULL,
    pdf_page_num INTEGER NOT NULL,
    segment_order INTEGER NOT NULL,            -- Sahifa ichidagi tartib raqami
    raw_text TEXT NOT NULL,                    -- Asl jumla matni
    clean_text TEXT NOT NULL,                  -- Qidiruv uchun tozalangan jumla
    token_count INTEGER NOT NULL,
    char_start INTEGER,                        -- Sahifa matnidagi boshlanish indeksi
    char_end INTEGER,                          -- Sahifa matnidagi tugash indeksi
    is_heading INTEGER DEFAULT 0,              -- 1 = sarlavha, 0 = oddiy matn
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE RESTRICT,
    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE RESTRICT
);

-- 4. Inglizcha va o'zbekcha jumlalar tekislanishi (Alignments)
CREATE TABLE IF NOT EXISTS alignments (
    id TEXT PRIMARY KEY,                       -- e.g. 'aln-cholpon-0001'
    pair_id TEXT NOT NULL,                     -- Juftlik identifikatori
    source_book_id TEXT NOT NULL,              -- Manba kitob ID
    target_book_id TEXT NOT NULL,              -- Tarjima kitob ID
    source_segment_ids TEXT NOT NULL,          -- JSON massiv: ['seg-cholpon-uz-p004-s001']
    target_segment_ids TEXT NOT NULL,          -- JSON massiv: ['seg-cholpon-en-p004-s001']
    source_text TEXT NOT NULL,                 -- Birlashtirilgan manba matni
    target_text TEXT NOT NULL,                 -- Birlashtirilgan tarjima matni
    alignment_type TEXT NOT NULL,              -- '1:1', '1:many', 'many:1', 'unmatched'
    alignment_method TEXT NOT NULL,            -- 'gale_church', 'hunalign', 'manual_verified'
    confidence_score REAL DEFAULT 1.0,         -- Moslik ishonch darajasi (0.0 - 1.0)
    reviewer_status TEXT DEFAULT 'draft',      -- 'draft', 'in_review', 'verified', 'flagged'
    reviewer_notes TEXT,                       -- Tadqiqotchi izohi
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_book_id) REFERENCES books(id),
    FOREIGN KEY (target_book_id) REFERENCES books(id)
);

-- 5. Kollokatsiya nomzodlari va lug'aviy yozuvlar
CREATE TABLE IF NOT EXISTS collocation_candidates (
    id TEXT PRIMARY KEY,                       -- e.g. 'cand-kk-001'
    lemma_en TEXT NOT NULL,                    -- Inglizcha lemma / bosh so'z
    lemma_uz TEXT NOT NULL,                    -- O'zbekcha lemma / bosh so'z
    surface_form_en TEXT NOT NULL,             -- Inglizcha shakl
    surface_form_uz TEXT NOT NULL,             -- O'zbekcha shakl
    grammatical_pattern TEXT NOT NULL,         -- Masalan: 'Noun + Verb', 'Adj + Noun' (3.1-bob)
    semantic_group TEXT NOT NULL,              -- Masalan: 'Ruhiy holat', 'Harakat' (3.1-bob)
    equivalence_type TEXT NOT NULL,            -- 'To'liq ekvivalent', 'Qisman', 'Muqobil' (3.2-bob)
    is_lingvocultural INTEGER DEFAULT 0,       -- 1 = lingvomadaniy konnotatsiyaga ega (3.3-bob)
    cultural_note TEXT,                        -- Lingvomadaniy izoh
    mi_score REAL,                             -- Mutual Information (MI)
    t_score REAL,                              -- t-score
    log_dice REAL,                             -- Sketch Engine logDice
    log_likelihood REAL,                       -- Log-Likelihood G^2
    corpus_frequency INTEGER DEFAULT 1,        -- Umumiy uchrashlar soni
    literal_trap TEXT,                         -- Kalka xatosi tuzog'i (masalan: *cold look)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Kollokatsiyaning korpusdagi real qo'llanishi (Occurrences in Context)
CREATE TABLE IF NOT EXISTS collocation_occurrences (
    id TEXT PRIMARY KEY,                       -- e.g. 'occ-kk-001-01'
    candidate_id TEXT NOT NULL,
    alignment_id TEXT NOT NULL,                -- Qaysi parallel jumlada uchragani
    book_id TEXT NOT NULL,
    pdf_page_num INTEGER NOT NULL,
    matched_span_en TEXT NOT NULL,             -- Inglizcha matndagi aniq qismi
    matched_span_uz TEXT NOT NULL,             -- O'zbekcha matndagi aniq qismi
    translation_strategy TEXT,                 -- Masalan: 'so'zma-so'z', 'funksional o'xshash', 'tasviriy'
    is_verified INTEGER DEFAULT 0,             -- 1 = tadqiqotchi tomonidan tasdiqlangan
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES collocation_candidates(id),
    FOREIGN KEY (alignment_id) REFERENCES alignments(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);

-- 7. Tadqiqotchi ilmiy annotatsiyalari jadvali (Researcher Annotations)
CREATE TABLE IF NOT EXISTS annotations (
    id TEXT PRIMARY KEY,
    occurrence_id TEXT NOT NULL,
    chapter_code TEXT NOT NULL,                -- '3.1_structure', '3.2_equivalence', '3.3_culture'
    taxonomy_label TEXT NOT NULL,              -- Klassifikator yorlig'i
    scientific_note TEXT NOT NULL,             -- Dissertatsiya uchun tahliliy izoh
    annotator_name TEXT DEFAULT 'Researcher',
    is_final INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (occurrence_id) REFERENCES collocation_occurrences(id)
);

-- 8. O'zgarishlar tarixi (Audit & Provenance Trail)
CREATE TABLE IF NOT EXISTS provenance_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,                 -- 'EXTRACT', 'ALIGN', 'ANNOTATE', 'BACKUP'
    entity_name TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    details TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indekslar (Qidiruv tezligini oshirish uchun)
CREATE INDEX IF NOT EXISTS idx_segments_page ON segments(page_id);
CREATE INDEX IF NOT EXISTS idx_alignments_pair ON alignments(pair_id);
CREATE INDEX IF NOT EXISTS idx_alignments_status ON alignments(reviewer_status);
CREATE INDEX IF NOT EXISTS idx_occurrences_candidate ON collocation_occurrences(candidate_id);
CREATE INDEX IF NOT EXISTS idx_occurrences_alignment ON collocation_occurrences(alignment_id);
