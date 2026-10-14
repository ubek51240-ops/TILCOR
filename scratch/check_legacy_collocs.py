import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/collocations_full.json', 'r', encoding='utf-8') as f:
    collocs = json.load(f)

with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
    corpus = json.load(f)

active_corpus = [s for s in corpus if not s.get('excluded')]

legacy = [it for it in collocs if any(it.get('id', '').startswith(p) for p in ['col-kk-', 'col-hem-', 'col-gen-'])]
print(f"Total legacy collocations found: {len(legacy)}")

results = []
for it in legacy:
    cid = it.get('id')
    en = it.get('english', '')
    uz = it.get('uzbek', '')
    example_en = it.get('exampleEn', '') or it.get('contextEn', '') or ''
    example_uz = it.get('exampleUz', '') or it.get('contextUz', '') or ''
    
    # Check if example sentences or collocation occur verbatim in active corpus
    found_in_books = False
    book_info = None
    for seg in active_corpus:
        s_uz = seg.get('uz', '').lower()
        s_en = seg.get('en', '').lower()
        if (example_uz and example_uz.lower() in s_uz) or (example_en and example_en.lower() in s_en):
            found_in_books = True
            book_info = f"{seg.get('book')} (segment {seg.get('id')})"
            break
            
    results.append({
        "id": cid,
        "en": en,
        "uz": uz,
        "exampleEn": example_en,
        "exampleUz": example_uz,
        "found_in_books": found_in_books,
        "book_info": book_info
    })

print(json.dumps(results, indent=2, ensure_ascii=False))
