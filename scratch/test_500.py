import json
import sys
import os
import traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.stdout.reconfigure(encoding='utf-8')
from search_engine import execute_unified_search

corpus = json.load(open('data/full_corpus.json', encoding='utf-8'))
collocs = json.load(open('data/collocations_full.json', encoding='utf-8'))
dict_data = json.load(open('data/dictionary.json', encoding='utf-8'))

for q in ['heart', 'shark', 'decision', 'chol']:
    try:
        res = execute_unified_search(q, corpus, collocs, dict_data)
        print(f"{q}: SUCCESS (sentences: {len(res['corpus_sentences'])}, candidates: {len(res['corpus_candidates'])})")
    except Exception as e:
        print(f"{q}: ERROR: {e}")
        traceback.print_exc()
