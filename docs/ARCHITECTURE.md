# TILCOR v2.0 — Tizim Arxitekturasi va Bosqichlar Zanjiri (ARCHITECTURE)

Ushbu hujjat platformaning 12 bosqichli ilmiy qayta tiklash konveyeri va uning qat'iy ajratilgan qatlamlarini tavsiflaydi.

```mermaid
flowchart TD
    subgraph S1_S4 ["1-QATLAM: Xom Manbalar va Ekstraksiya (Raw Layer)"]
        PDF["Asl PDF Manbalar (SHA-256 Nazoratida)"] --> Extractor["extract_all_texts.py (PyMuPDF)"]
        Extractor --> Pages["pages (963 bet)"]
        Extractor --> Segments["segments (23,762 segment)"]
        Extractor -.-> Quarantined["Stevenson UZ (0 matn / Karantin)"]
    end

    subgraph S5_S6 ["2-QATLAM: Tekislash va Kollokatsiyalar (Alignment & Candidates)"]
        Segments --> Aligner["run_full_alignment.py (Anchor Window)"]
        Aligner --> Alignments["alignments (7,391 juftlik)"]
        Aligner --> RevQueue["Review Queue (6,193 needs_review)"]
        Segments --> Morfo["uzbek_morphology.py & regex_en"]
        Morfo --> Occurrences["collocation_occurrences (469 uchrashuv)"]
        LexiconSupplied["collocations_full.json"] --> Lexicon["lexicon_entries (6,546 ta halol manba)"]
    end

    subgraph S7_S8 ["3-QATLAM: Annotatsiya va Statistika (Human-Confirmed Layer)"]
        Occurrences --> Workspace["annotation_workspace.html (Alt+C, Alt+S)"]
        Workspace --> Annotations["phd_annotations (40 ta taksonomik parametr)"]
        Annotations --> Matrix["6x8 Tarjima Mutanosibligi Matritsasi"]
        Occurrences --> StatEngine["compute_corpus_statistics.py"]
        StatEngine --> Contingency["2x2 Kontingentlik Jadvali (O11, R1, C1, N)"]
        Contingency --> Measures["association_measures (11,527 ta MI, t, G2, NormFreq)"]
        Annotations --> Chap3["III Bob Jadvallari (3.1 - 3.6, faqat is_confirmed=1)"]
    end

    subgraph S9_S12 ["4-QATLAM: Xizmatlar, Xavfsizlik va Himoya (Interface & Security)"]
        Segments --> KWIC["stage9_backend.py (KWIC Konkordans)"]
        Occurrences --> Exporter["Export Engine (.xlsx & UTF-8 BOM CSV)"]
        RBAC["Stage 10 RBAC (admin / reviewer / guest)"] --> KWIC
        RBAC --> Exporter
        Design["Stage 11 Dizayn Tizimi (Inter, Noto, #1F2A5A, #0F766E, #B45309)"] --> UI["Foydalanuvchi Interfeysi"]
        Backup["scripts/backup_corpus.py (SHA-256 + Restore Test)"] --> Storage["Zaxira Ombori"]
    end
```

---

## Asosiy Qoidalar (Architectural Invariants)
1. **Rule R1 (Zero Data Fabrication):** Hech bir raqam yoki matn qatlami taxmin qilib qo‘shilmaydi.
2. **Rule R3 (Three Strictly Separated Layers):**
   - *Raw Data:* Faqat manbadan olingan xom jumlalar va tokenlar.
   - *Draft / AI Suggestions:* Tavsiya holatidagi qoralamalar, statistikaga ta'sir qilmaydi.
   - *Confirmed Research Data:* Faqat inson-tadqiqotchi tomonidan tasdiqlangan annotatsiyalar.
3. **Rule R8 (Canonical Unicode):** O‘zbekcha `U+02BB` va `U+02BC` belgilari standartlashtirilgan.
4. **Direction Invariant:** Original doimo chapda, Tarjima doimo o‘ngda.
