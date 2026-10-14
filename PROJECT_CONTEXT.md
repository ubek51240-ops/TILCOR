# TILCOR — PROJECT CONTEXT (Sections A–G)

## A. Project and goal
**TILCOR (tilcor.uz)** is a public Uzbek–English platform for words and collocations, built on a literary parallel corpus. It supports the PhD dissertation:
TARJIMA VA TENG MATNLAR PARALLEL KORPUSIDA O‘ZARO FAOL BIRIKUVCHI (KOLLOKATSION) SO‘ZLAR TADQIQI (o‘zbek va ingliz tillari misolida).

Chapters:
- I — theory: 1.1 collocation vs free combination and phraseological unit; 1.2 translation of collocations; 1.3 parallel corpora.
- II — methodology: 2.1 corpus building; 2.2 linguistic and software support; 2.3 corpus design and features.
- III — analysis: 3.1 semantic-structural classification; 3.2 translation equivalence; 3.3 linguocultural features.

Never rename or rewrite this outline.

Institution: Buxoro davlat universiteti (BuxDU). Specialty code: 10.00.06. Researcher: Voxitov Ibrohim Sodiq o‘g‘li.

**Comparison principle:** every analysis compares ONE work with its own translation, sentence by sentence (original ↔ translation). Different works are never compared with each other. Results may later be summarised by translation direction (UZ → EN vs EN → UZ).

**The dissertation's working definition (chapter 1.1) is binding for the platform:**
- The linguistic criteria decide the CATEGORY of a unit. Statistical evidence from reference corpora decides its STATUS.
- Status values:
  - tasdiqlangan kollokatsiya;
  - kollokatsiya nomzodi;
  - barqaror erkin birikma;
  - frazeologik birlik;
  - chegaraviy.
- Base (asos) and collocate (kollokat) rules for Uzbek:
  - Ot + fe’l → base = noun;
  - Ega + kesim → base = noun;
  - Sifat + ot → base = noun;
  - Ravish + fe’l → base = verb;
  - Ot + ot → tagged separately as a lexicalised name.
- Excluded from analysis: proverbs and sayings, full sentences, similes, speech formulas, proper names and nicknames, paired and reduplicated words, auxiliary-verb constructions (chiqib ketmoq, olib kelmoq).
- Unit of analysis = a collocation OCCURRENCE together with its contextual meaning. Homonymous combinations get a meaning label per occurrence.
- Translation equivalent form: kollokatsiya / bitta so‘z / tasviriy ifoda / tushirib qoldirish. The equivalence degree is a separate field, defined by the researcher.
- Page numbering:
  - original = the page number printed in the ziyouz.com copy;
  - translation = the page number of the printed book.

**EQUIVALENT PRINCIPLE — the most important rule of the platform:**
1. A translation equivalent is ALWAYS the translator's own words, taken verbatim from the aligned translation sentence of the uploaded book, with its page number.
2. You must NEVER translate a collocation yourself, and never take an equivalent from machine translation, an AI model or the dictionary. The question is not "how should this be translated?" but "how did THIS translator translate it in THIS book?"
3. The translator may have translated differently from the dictionary: a different image, a paraphrase, one word, or omission. That is exactly what the dissertation studies. Record it as it is:
   - equivalent form = kollokatsiya / bitta so‘z / tasviriy ifoda / tushirib qoldirish;
   - never "correct" the translator;
   - never replace the translator's choice with a dictionary or AI translation.
4. The dictionary or an AI may only HELP locate the matching words inside the aligned translation sentence. The stored equivalent must still be an exact substring of that sentence.
5. Automatic check: before saving any equivalent, verify that its text occurs exactly in the aligned target segment(s). If it does not, reject it.
6. If no matching words can be found, store "tarjimada topilmadi — ko‘rib chiqish kerak". Never fill the gap.
7. An AI may propose which span is the equivalent ("AI-taklif"); only the researcher confirms it.

The platform is part of the dissertation's scientific novelty: a bidirectional Uzbek–English collocation resource where every word, collocation, equivalent and example is traceable to its source. It must be professional, compact, easy to read and correct.

## B. Target functionality (for all steps — do NOT build it all now)

### B1. One search box, two directions
The user types one Uzbek or English word (UZ → EN or EN → UZ).
- Automatic language detection with a manual UZ / EN switch.
- Uzbek Latin and Cyrillic are both accepted. Every apostrophe variant (ʻ ‘ ' ` ’) counts as the same letter.
- Uzbek root matching handles agglutination and stem changes:
  - consonant alternation: yurak → yuragi, qishloq → qishlog‘i;
  - vowel drop: burun → burni, o‘g‘il → o‘g‘li;
  - suffix chains.
- English lemma and derivation matching: heart, hearts, hearty, heartless, heartbeat, wholehearted.

### B2. Results — two separate sections

**"So‘zlar" — all words with the same root, grouped as:**
1. inflected forms (yuragi, yurakda …);
2. derived words (yurakli, yuraksiz …);
3. compounds and paired words (yurak-bag‘ir …).

Header: number of distinct words and total corpus occurrences.
For each word show, side by side and clearly separated:
- **"Lug‘atdagi tarjima"** — from the researcher's dictionaries, with the dictionary named;
- **"Kitobdagi tarjima"** — how the translator actually rendered this word in each book: verbatim spans from the aligned sentences, with book, page and number of occurrences.

The contrast between the dictionary and the translator's real choices is scientifically valuable (chapter 3.2). Never merge the two.

Also show for each word: part of speech, occurrences per book, and a link to its corpus sentences.

**"Kollokatsiyalar" — collocations of that word in the same language.** Each card shows:
- the base form, with the searched word highlighted;
- structure: pattern such as Fe’l + Ot / Verb + Noun, with node and collocate marked;
- one source badge (see section D);
- one example sentence, always labelled with its origin, chosen in this order:
  1. corpus sentence + book + page + aligned translation, with the equivalent highlighted;
  2. a named, citable reference source;
  3. "Namuna gap (AI tuzgan, korpusdan emas)".
  An AI sentence is never shown as coming from a book.
- the equivalent in the other language, with:
  - equivalent form (kollokatsiya / bitta so‘z / tasviriy ifoda / tushirib qoldirish);
  - equivalence degree (researcher-defined);
  - review status (AI-taklif / tasdiqlangan);
- a "Barcha misollar" link to a KWIC list with book, page and translation.

Filters: language, source type, pattern, book, translation direction, status.

### B3. Rules for results
- **Statistical status (chapter 1.1):**
  - Reference corpora: BNC for English; the Uzbek National Corpus or uzWaC for Uzbek.
  - Main measure: logDice. MI is shown only together with a frequency filter. t-score is a reliability indicator only.
  - Minimum frequency in the reference corpus: 5 (initial value). Frequencies are normalised per million.
  - Values are imported with the reference corpus name, version and access date. Thresholds are calibrated later on an annotated sample.
  - Raw statistics from the small literary corpus never decide a status. Every displayed value shows its n.
- Collocation cards show the status value from section A, the base and collocate, and the equivalent form.
- Every AI result is "AI-taklif" until the researcher confirms it in the admin review screen ("tasdiqlangan").
- Dissertation tables use confirmed data only.

### B4. Planned steps (never start one yourself)
01 audit, cleanup, compact navigation → 02 data model, HTTPS, dictionary re-parsing → 03 text extraction from PDFs → 04 alignment → 05 morphology and word families → 06 collocation detection → 07 translation equivalents and classification → 08 search results page → 09 admin review screen → 10 statistics → 11 KWIC and export → 12 design polish → 13 security, validation, defence kit.

## C. Information architecture and design (apply from step 01; polish later)

### C1. Navigation
One compact top bar:
- Desktop: dropdown sub-menus open on mouse hover and on keyboard focus.
- Mobile: hamburger menu with accordion sub-menus.

Menu:
- **Bosh sahifa** (with the main search box)
- **Korpus ▾** — Parallel matnlar · Konkordans (KWIC) · Manbalar
- **Kollokatsiyalar ▾** — Kollokatsiya qidiruvi · Tuzilish (qolip) bo‘yicha · Tarjima ekvivalentlari
- **Lug‘at**
- **Tahlil ▾** — Statistika · Metodologiya · Eksport
- **Admin** (visible only after login) — Ko‘rib chiqish · Research Lab · AI vositalari · Import

Research Lab, Tarjimon and AI Assistent are removed from the public menu.

### C2. Home page (compact)
1. Hero: name, one-sentence description, large search box with UZ / EN switch, example chips (yurak, heart, qaror, decision).
2. One strip of 3–4 live figures from the database.
3. Three short cards: Korpus · Kollokatsiyalar · Lug‘at.
4. A two-line "Loyiha haqida" with a link to Metodologiya.

Move the module–chapter table and the methodological warning to the Metodologiya page. Delete the old roadmap and the sample "make a decision" card.

### C3. Visual style
Calm, scholarly, modern — like a university digital library.
- **Theme:** light by default, dark switch. Colour tokens in one file. WCAG AA contrast.
- **Typography:**
  - fonts with full support for o‘ g‘ ’ (Inter or Noto Sans for the interface; Noto Serif for corpus text);
  - body 16 px, corpus text 17 px, line-height 1.6, maximum content width about 1200 px;
  - test rendering of "O‘zbekiston, g‘alaba, ta’lim".
- **Badges:** consistent colours for source types (korpus / lug‘at / ma’lumotnoma / internet / AI-taklif) and statuses.
- **Parallel pair card:** the ORIGINAL first (left on desktop, top on mobile), translation second. Book, page, segment ID and status sit in one small meta line. Warnings are shown once at the top of a page, never repeated inside every card.
- **Mobile header:** short logo "TILCOR" only, no overflow, nothing overlapping.

## D. Data provenance policy (applies to every record, every step)
Every data item belongs to exactly one class:

| Class | What | Action |
|---|---|---|
| KORPUS | text from the uploaded books | keep, with book + page |
| LUG‘AT | entries from the researcher's printed dictionaries (an 80,000-word dictionary, 881 pp.; a second dictionary, 816 pp.) | keep; record full bibliographic data (ask the researcher if unknown); repair OCR errors |
| MA’LUMOTNOMA | entries from named reference works supplied by the researcher | keep with the exact per-entry source; hide from public until traced |
| INTERNET | data from a reputable, citable online source | keep only with URL + access date |
| AI-TAKLIF | anything generated by AI or machine translation | keep only labelled "AI-taklif (tekshirilmagan)"; never counted in statistics; never shown as sourced. AI or machine translations are NEVER valid as translation equivalents. |
| TO‘QIMA | invented data with no source | delete from all public places; archive in the database with the reason |

Details:
- **MA’LUMOTNOMA sources** are, for example:
  - *English Collocations in Use* (Intermediate / Advanced; M. McCarthy & F. O’Dell, Cambridge University Press);
  - the *Academic Collocation List* (K. Ackermann & Y.-H. Chen, Pearson, 2013);
  - a "1000 English Collocations" e-book.
  Every entry gets its exact source, verified against the researcher's original file. If an entry cannot be traced → "manba aniqlanmagan".
- **Machine-translation garbage** is TO‘QIMA: non-Uzbek words (e.g., "güveç") or nonsense (e.g., "ostiga keling yurak bor", "oling yaxshi go‘zal go‘zal"). Set status = rejected and hide it.
- **The dictionary** is a real source with OCR damage. Keep the entries, but flag broken ones as "needs_repair" and hide them until step 02 re-parses the dictionary.

## E. Corpus (researcher's decision, 13.10.2026)
The corpus contains exactly TWO pairs. No other works for now.

| Pair | Direction | Files | Verified facts |
|---|---|---|---|
| Cho‘lpon, *Kecha va kunduz* ↔ *Night and Day* (tr. Christopher Fort, Academic Studies Press, 2019) | UZ → EN | KVK-UZ, KVK-EN | UZ: Toshkent, «Sharq» NMK, 2000; ziyouz.com copy; footer "www.ziyouz.com kutubxonasi N" on every page. EN: Academic Studies Press, 2019, ISBN 9781644690482, DOI 10.1515/9781644690482; numbered footnotes; glossary. |
| Hemingway, *The Old Man and the Sea* ↔ *Chol va dengiz* (tr. Ibrohim G‘ofurov, «Yosh gvardiya», 1986) | EN → UZ | OMS-EN, OMS-UZ | EN: web copy with inline page markers like "[9]"; first edition Charles Scribner's Sons, 1952. UZ: Toshkent, «Yosh gvardiya», 1986. |

**Removed by the researcher:**
- Stevenson, *Treasure Island* / *Xazinalar oroli* — both languages, completely removed.
- Orwell, *Animal Farm* / *Molxona* (tr. Karim Bahriyev) — removed from public corpus and archived. No other works for now. Future works may be added later on researcher instruction only.

## F. Access and rights
**The site is public**, with no login for visitors. Hemingway's original and the translations by Fort, G‘ofurov and Bahriyev are under copyright, so:
- visitors see sentence-level excerpts only (one sentence + its aligned translation);
- no continuous reading, no full-text download, no bulk export for visitors;
- at most 50 corpus sentences per query, with rate limiting;
- example sentences from reference books are never shown publicly.

Admin features require the researcher's login.

## G. Rules for every step
1. Never invent anything. Unknown → "—". Never translate book text yourself: every equivalent and every "Kitobdagi tarjima" comes verbatim from the uploaded books (see the EQUIVALENT PRINCIPLE in section A).
2. No number typed into HTML/JS/templates; every number is computed live from the database.
3. Full backup before every change; source files and original data stay read-only.
4. Never claim something works until tested. Mark items ISHLAYDI / QISMAN / REJADA.
5. Do only the current step. Then STOP, report in Uzbek, wait.
6. No paid services, no new external AI APIs, no uploading book texts to third parties.
7. Keep CHANGELOG.md, TESTLOG.md and AUDIT_REPORT.md updated.
8. A step is complete only when it is live on tilcor.uz. Always state: lokal / staging / tilcor.uz.
9. If the data API fails, show a clear error message. Never fall back to local sample data.

**Report format (Uzbek):** 1) Nima o‘zgardi 2) O‘zgargan fayllar 3) Testlar va natijasi 4) Qolgan muammolar 5) Qaror talab qilinadigan joylar 6) Qayerda: lokal / staging / tilcor.uz.

---

## S. New permanent rule — Search language rule (Added in Step 02)
- A query in one language returns words, collocations and examples in that language only, with translations in the other language shown beside them.
- Uzbek results never come from AI translations of English reference entries.
- Every example highlights the whole word family of the query.
- A translation sentence is presented as a correct translation only when its alignment status is "confirmed".
- An equivalent is highlighted only when its span is confirmed (EQUIVALENT PRINCIPLE).

---

## S2. New permanent rules (Added in Step 03)

**Corpus:**
- Exactly two pairs: *Kecha va kunduz* ↔ *Night and Day* (UZ → EN) and *The Old Man and the Sea* ↔ *Chol va dengiz* (EN → UZ).
- New works are added only on the researcher's instruction.

**Uzbek text normalization:**
- All Uzbek searching, matching, counting and highlighting use `uz_norm()`.
- Stored text is never changed. English text never passes through `uz_norm()`.

**Reference base equivalents:**
- Every Uzbek variant carries exactly one source class: KORPUS / LUG‘AT / AI-taklif / tasdiqlangan.
- AI variants are never presented as corpus or dictionary data and never enter Chapter III statistics.

**Interface languages:**
- uz (default), en and ru, with the binding glossary.
- Corpus content, equivalents and bibliographic data are never translated.
- The interface language switch and the search language switch are independent.

---

## S3. New permanent rules (Added in Step 04)

**Alignment display:**
- A translation sentence is shown open only when its pair is "avtomatik — ikki usul mos" (labelled "Avtomatik tekislangan — tekshirilmagan") or "tasdiqlangan".
- Low-confidence pairs are collapsed and labelled.

**Equivalent display:**
- A proposed equivalent span is shown dashed and labelled "AI-taklif".
- Only a researcher-confirmed span is shown solid.
- Only confirmed spans enter Chapter III statistics.

**Full forms:**
- Results never show truncated stems or abbreviations. Lemmas appear in dictionary form; parts of speech appear as full words.

**Terminology:** "Avtomatik nomzod" (machine-extracted) is never called "kollokatsiya nomzodi"; that term is reserved for the 1.1.4 status.

**Examples:** a book example always carries book and page on both sides and its parallel translation sentence. A non-book example is always labelled "Namuna gap (kitobdan emas)".

**Page numbers:**
- *Kecha va kunduz*: the page of the ziyouz.com copy (footer number).
- *Night and Day* and *The Old Man and the Sea*: the printed page.
- *Chol va dengiz*: the page of the kutubxonachi.uz electronic copy, always labelled "elektron nusxa", until the researcher supplies the printed 1986 edition.
- A page number is never estimated or invented.

**Candidate extraction:** window of 4 words left and right, filtered by the 1.1 part-of-speech patterns. Proper names, same-lemma pairs, function words and the 1.1 exclusion categories never become public candidates.

---

## S4. New permanent rules (Added in Step 05)

1. **Corpus switch gate:** a corpus version goes live only when every novel or narrative page has at least 98% token coverage and the completeness table passes. Never switch first and check later.
2. **Anchors:** the anchor set (2.1) is permanent. Every re-alignment must reproduce it and report the drift.
3. **Zero-loss alignment:** no Uzbek sentence segment may ever be dropped (loops must never exit prematurely; unmatched segments stored as 1:0).
4. **Rejected means hidden:** a record with a rejection reason is never public. No example is ever attributed to a book that is not in the corpus.
5. **Closed classes:** pronouns, numerals, postpositions, conjunctions, particles and modal words never form candidates. Unknown parts of speech never default to "ot" (always tagged "so‘z turkumi aniqlanmagan").
6. **Ot + ot:** never public before the researcher confirms it. Ega + kesim patterns preserve the 3rd person possessive affix on lemmas (`ko‘ngli tushmoq`, `yuragi urmoq`).
7. **Namuna gap:** always labelled as AI-composed or as coming from a named reference source, and never counted in corpus statistics.
8. **Annotation:** only on confirmed pairs. Chapter III fields are never pre-filled.
9. **Language:** the interface language is part of the URL (?lang=uz|en|ru).
10. **Testing:** the 20-query test runs after every deployment, and its result is part of every report.

---

## S5. New permanent rules (Added in Step 06)

1. **Deployment gate:** after every deployment run the 20-query test, the parallel-query test, the HTTPS check and the home and search checks. Any failure means an immediate rollback.
2. **Caching:** a cache key always includes the full normalised query and the corpus version.
3. **Alignment display (replaces S3):** only "tasdiqlangan" pairs show the translation sentence open. Automatic pairs are collapsed and labelled "Tarjima gapi hali tadqiqotchi tomonidan tasdiqlanmagan".
4. **Omission:** "tushirib qoldirilgan" is set only by the researcher. The automatic state is "ekvivalent aniqlanmagan".
5. **Word families:** morphological only. Synonyms and translations are never part of a family.
6. **Lemmas:** a lemma must exist as a headword or in a verb list; otherwise the surface form is shown.
7. **Examples:** the example of a candidate always contains that candidate.
8. **Interface languages:** every page in uz, en and ru, server-rendered, tested in a browser.
9. **Direction labels:** "Asliyat" and "Tarjima" by book, never by query language.
10. **Method honesty:** a label that claims a method (for example "ikki usul mos") is shown only if that method really ran, and its version is recorded.---

## S6. New permanent rules (Added in Step 07)

**Equivalent hierarchy:** muqobils are shown only from the five labelled sources of PART 1, in that order. Nothing unlabelled, nothing machine-translated.

**Seed data:** chapter 1.1 pairs are confirmed researcher data. The pair from the external check stays an AI-taklif equivalent until the researcher confirms it.

**Collocation queries:** queries of two or more words are lemma-based and allow up to 2 intervening tokens.

**Provenance audit:** it runs after every import. Failing records are hidden.

**Gold tests:** tests/gold_search.json runs after every deployment, and its result is part of every report. A failed gold test blocks the deployment.

**Citation pages:** /soz/ and /kollokatsiya/ pages are permanent URLs. Their content changes are versioned with dates.

---

## S7. New permanent rules (Added in Step 08)

**Translation:** interface translation is key-based only. No word substitution inside strings. Every key exists in uz, en and ru.

**Corpus content:** corpus content (sentences, titles, examples, bibliography) is wrapped in `.corpus-text` and is never translated.

**Public HTML:** it never contains admin items, internal labels ("Stage …") or role identifiers.

**Navigation:** one component on every page. No "#" links.

**Results:** every search result has its own server-rendered URL.

**Testing:** the interface test (task 13) runs after every deployment and its table is part of every report.
