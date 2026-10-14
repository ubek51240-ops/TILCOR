import json
import re

def run_provenance_audit():
    print("Starting Provenance Audit...")
    
    with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
        corpus = json.load(f)
    with open('data/collocations_full.json', 'r', encoding='utf-8') as f:
        collocations = json.load(f)
    with open('data/dictionary.json', 'r', encoding='utf-8') as f:
        dictionary = json.load(f)

    # Index corpus sentences by ID
    corpus_by_id = {s.get('id'): s for s in corpus if s.get('id')}
    
    # Track audit results
    counts_by_class = {
        "KORPUS": 0,
        "LUG‘AT": 0,
        "AI-taklif": 0,
        "TASDIQLANGAN": 0
    }
    failure_reasons = {}
    failure_examples = []
    
    # 1. Audit Dictionary
    for d in dictionary:
        cls = "LUG‘AT"
        counts_by_class[cls] += 1
        
        # Check source and page
        d_src = str(d.get('dictionary_source') or '') + ' ' + str(d.get('source') or '')
        if not any(k in d_src for k in ['Nazarov', '816', 'BuxDU', 'Katta Lug']):
            d['needs_repair'] = True
            d['public_visible'] = False
            reason = "Lug'at manbasi to'liq ko'rsatilmagan"
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
            if len(failure_examples) < 20:
                failure_examples.append(f"Dictionary '{d.get('word')}': {reason}")
                
        # Check if translation is empty or OCR corrupt
        tr = d.get('translation', '')
        if not tr or d.get('needs_repair'):
            d['public_visible'] = False

    # 2. Audit Collocations
    for c in collocations:
        c_class = c.get('class', 'AI-taklif')
        if 'KORPUS' in str(c_class).upper():
            counts_by_class["KORPUS"] += 1
        elif 'LUG' in str(c_class).upper():
            counts_by_class["LUG‘AT"] += 1
        elif 'TASDIQ' in str(c.get('status', '')).upper():
            counts_by_class["TASDIQLANGAN"] += 1
        else:
            counts_by_class["AI-taklif"] += 1

        # Check example attribution
        ex = c.get('example', {})
        if isinstance(ex, dict):
            ex_book = ex.get('book', '')
            # If attributed to a book, must be in corpus
            if ex_book and ex_book not in [
                "Abdulhamid Cho‘lpon: «Kecha va kunduz»",
                "Ernest Hemingway: «The Old Man and the Sea»",
                "Namuna gap — AI tomonidan tuzilgan, tekshirilmagan"
            ]:
                if "Cho‘lpon" not in ex_book and "Hemingway" not in ex_book and "Namuna gap" not in ex_book:
                    c['needs_repair'] = True
                    c['public_visible'] = False
                    reason = f"Kitob nomi korpusga mos kelmaydi: {ex_book[:30]}"
                    failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
                    if len(failure_examples) < 20:
                        failure_examples.append(f"Collocation '{c.get('id')}': {reason}")

        # Check AI-taklif label
        if c.get('class') == 'AI-taklif':
            rev_st = c.get('review_status') or ''
            if not rev_st or 'AI-taklif' not in rev_st:
                c['review_status'] = "AI-taklif (tekshirilmagan)"

        # Check KORPUS exact substring
        if c.get('corpus_segments'):
            for sid in c.get('corpus_segments'):
                seg = corpus_by_id.get(sid)
                if not seg:
                    c['needs_repair'] = True
                    c['public_visible'] = False
                    reason = f"Ko'rsatilgan segment ({sid}) korpusda mavjud emas"
                    failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
                    if len(failure_examples) < 20:
                        failure_examples.append(f"Collocation '{c.get('id')}': {reason}")
                else:
                    uz_col = c.get('uzbek', '')
                    if uz_col and uz_col.lower() not in seg.get('uz', '').lower():
                        c['needs_repair'] = True
                        c['public_visible'] = False
                        reason = f"Kollokatsiya matni ko'rsatilgan gapda exact substring emas"
                        failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
                        if len(failure_examples) < 20:
                            failure_examples.append(f"Collocation '{c.get('id')}': {reason} (seg {sid})")

    # 3. Audit Corpus confirmed equivalents
    for s in corpus:
        if s.get('status') == 'tasdiqlangan':
            counts_by_class["TASDIQLANGAN"] += 1
            conf_eq = s.get('confirmed_equivalent')
            if conf_eq:
                # Target exact substring
                en_span = conf_eq.get('en_span')
                en_text = s.get('en', '')
                if isinstance(en_span, list):
                    for part in en_span:
                        if part.lower() not in en_text.lower():
                            s['needs_repair'] = True
                            reason = f"Ekvivalent qismi target matnda topilmadi: '{part}'"
                            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
                            if len(failure_examples) < 20:
                                failure_examples.append(f"Segment '{s.get('id')}': {reason}")
                elif en_span:
                    if en_span.lower() not in en_text.lower():
                        s['needs_repair'] = True
                        reason = f"Ekvivalent target matnda topilmadi: '{en_span}'"
                        failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
                        if len(failure_examples) < 20:
                            failure_examples.append(f"Segment '{s.get('id')}': {reason}")

    # Save audited datasets
    with open('data/collocations_full.json', 'w', encoding='utf-8') as f:
        json.dump(collocations, f, ensure_ascii=False, indent=2)
    with open('data/dictionary.json', 'w', encoding='utf-8') as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=2)
    with open('data/full_corpus.json', 'w', encoding='utf-8') as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    audit_summary = {
        "counts_by_class": counts_by_class,
        "failure_reasons": failure_reasons,
        "failure_examples_count": len(failure_examples),
        "failure_examples": failure_examples
    }
    with open('data/provenance_audit_results.json', 'w', encoding='utf-8') as f:
        json.dump(audit_summary, f, ensure_ascii=False, indent=2)

    print("Audit finished successfully.")
    print("Counts by class:", counts_by_class)
    print("Failure reasons:", failure_reasons)
    print(f"Sample 20 failure examples ({len(failure_examples)}):")
    for ex in failure_examples[:20]:
        print(" -", ex)

if __name__ == '__main__':
    run_provenance_audit()
