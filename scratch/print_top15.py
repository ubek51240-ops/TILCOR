import sys
sys.path.insert(0, '.')
import json
from search_engine import execute_unified_search

corpus = json.load(open('data/full_corpus.json', encoding='utf-8'))
collocs = json.load(open('data/collocations_full.json', encoding='utf-8'))
dictionary = json.load(open('data/dictionary.json', encoding='utf-8'))

words = ["yurak", "ko‘ngil", "qaror", "heart", "decision"]

forbidden = ["ko‘ngil uni", "ikkala ko‘ngil", "gap ko‘ngil", "nomer qaror", "uyi qaror", "chol yurak", "bosh yurak", "ko‘ngil boshlamoq"]

for w in words:
    res = execute_unified_search(w, corpus, collocs, dictionary)
    cands = res.get('corpus_candidates', [])
    print(f"\n================ TOP 15 PUBLIC CANDIDATES FOR '{w}' ({len(cands)} total) ================")
    for i, c in enumerate(cands[:15], 1):
        col = c.get('collocation', '')
        pat = c.get('pattern', '')
        occ = c.get('occurrences_count', 0)
        scnt = c.get('sentences_count', 0)
        is_bad = any(f in col.lower() for f in forbidden)
        flag = " [FORBIDDEN!]" if is_bad else ""
        print(f"{i:2d}. {col:<30} | {pat:<15} | Occ: {occ} | Sent: {scnt}{flag}")
