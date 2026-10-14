import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
from search_engine import execute_unified_search
import server

# Sample 500 corpus sentences
active_c = server.get_active_corpus()[:500]
active_col = server.get_active_collocations()[:500]
active_d = server.get_active_dictionary()[:500]

test_queries = [
    ("o'z", "o‘z", "oʻz", "o’z", "o`z"),
    ("ko'z", "ko‘z", "koʻz", "ko’z", "ko`z"),
    ("chol", "sea"),
    ("ma'lum", "ma‘lum", "maʻlum", "ma’lum", "ma`lum")
]

print("=== TESTING UNIFIED SEARCH ON 500 CORPUS SENTENCES ===")
for group in test_queries:
    print(f"\nGroup: {group[0]}")
    for q in group:
        res = execute_unified_search(q, active_c, active_col, active_d, forced_lang=None)
        sent_count = res.get('summary', {}).get('corpus_occurrences', 0)
        word_count = res.get('summary', {}).get('total_word_forms', 0)
        colloc_count = res.get('summary', {}).get('collocations_count', 0)
        print(f"  Query '{q}' -> {sent_count} sentences, {word_count} words, {colloc_count} collocations")
