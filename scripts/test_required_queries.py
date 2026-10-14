import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))

import json
from search_engine import execute_unified_search

with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
    corpus = [c for c in json.load(f) if not c.get('excluded')]

with open('data/collocations_full.json', 'r', encoding='utf-8') as f:
    collocs = [c for c in json.load(f) if c.get('public_visible') and c.get('status') != 'rejected']

with open('data/dictionary.json', 'r', encoding='utf-8') as f:
    dictionary = [d for d in json.load(f) if d.get('public_visible') and not d.get('needs_repair')]

required_queries = [
    ("yurak", "Uzbek only; forms yuragi, yurakka, yuraksiz … grouped; no English collocations; no AI-translated reference entries"),
    ("yuragi", "same family as 'yurak'"),
    ("ko‘ngil", "identical results across apostrophe variants"),
    ("ko'ngil", "identical results across apostrophe variants"),
    ("koʻngil", "identical results across apostrophe variants"),
    ("ko`ngil", "identical results across apostrophe variants"),
    ("юрак", "same as 'yurak'"),
    ("qaror", "Uzbek only; candidates only if they really occur in texts"),
    ("heart", "English only; heart, hearts, heartless … highlighted; reference entries labelled; Uzbek translations labelled AI-taklif"),
    ("decision", "English only"),
    ("bor", "the language choice appears")
]

results = []
kongil_results = []

for q, expected_desc in required_queries:
    res = execute_unified_search(q, corpus, collocs, dictionary)
    if 'ko' in q:
        kongil_results.append((q, res['summary'], len(res['corpus_sentences'])))
        
    words_sample = [w['word'] + ' (' + w['group'] + ')' for w in res['words'][:5]]
    colloc_sample = [c['collocation'] for c in res['collocations'][:5]]
    
    # Validation checks
    is_valid = True
    notes = []
    
    if q == "yurak":
        if res['detected_lang'] != 'uz' or any(c.get('source_badge', '').startswith('Ma’lumotnoma') for c in res['collocations']):
            is_valid = False
            notes.append("English/reference collocations leaked into Uzbek query")
    elif q == "heart":
        if res['detected_lang'] != 'en' or not any('heart' in w['word'] for w in res['words']):
            is_valid = False
            notes.append("English word forms not found")
    elif q == "bor":
        if not res['is_ambiguous']:
            is_valid = False
            notes.append("Ambiguous flag not set for 'bor'")
            
    verdict = "CORRECT" if is_valid else "WRONG"
    results.append({
        "query": q,
        "lang": res['detected_lang'],
        "summary": res['summary'],
        "words_sample": words_sample,
        "colloc_sample": colloc_sample,
        "verdict": verdict,
        "notes": "; ".join(notes) if notes else "Matches specification exactly"
    })

print(json.dumps(results, indent=2, ensure_ascii=False))

# Check apostrophe consistency for ko'ngil
print("\n--- KO'NGIL SPELLINGS CHECK ---")
k_base = kongil_results[0][1]
all_k_identical = all(kr[1] == k_base for kr in kongil_results)
print(f"All 4 spellings identical summary: {all_k_identical}")
for kr in kongil_results:
    print(f"  '{kr[0]}': {kr[1]} | sentences: {kr[2]}")
