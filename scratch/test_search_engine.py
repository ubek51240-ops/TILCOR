import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
sys.path.insert(0, os.path.abspath('.'))

from search_engine import execute_unified_search

with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
    corpus = [c for c in json.load(f) if not c.get('excluded')]

with open('data/collocations_full.json', 'r', encoding='utf-8') as f:
    collocs = [c for c in json.load(f) if c.get('public_visible') and c.get('status') != 'rejected']

with open('data/dictionary.json', 'r', encoding='utf-8') as f:
    dictionary = [d for d in json.load(f) if d.get('public_visible') and not d.get('needs_repair')]

test_queries = ['yurak', 'yuragi', 'heart', 'qaror', 'bor']

for q in test_queries:
    print('='*70)
    print(f"QUERY: '{q}'")
    res = execute_unified_search(q, corpus, collocs, dictionary)
    print(f"  Detected Lang: {res['detected_lang']} | Selected: {res['selected_lang']} | Ambiguous: {res['is_ambiguous']}")
    print(f"  Summary: {res['summary']}")
    print(f"  Words found ({len(res['words'])}): {[w['word'] + ' (' + w['group'] + ')' for w in res['words'][:6]]}")
    print(f"  Collocations found ({len(res['collocations'])}): {[c['collocation'] for c in res['collocations'][:5]]}")
    print(f"  Corpus sentences ({res['pagination']['total_sentences']}):")
    for s in res['corpus_sentences'][:2]:
        print(f"    - [{s['id']}] {s['source_raw'][:70]}...")
