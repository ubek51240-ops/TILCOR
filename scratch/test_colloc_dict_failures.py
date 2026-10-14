import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
from search_engine import execute_unified_search
import server

active_col = server.get_active_collocations()
active_d = server.get_active_dictionary()

test_queries = [
    # o' variants
    ("o'z", "o‘z", "oʻz", "o’z", "o`z"),
    ("ko'z", "ko‘z", "koʻz", "ko’z", "ko`z"),
    # g' variants
    ("g'olib", "g‘olib", "gʻolib", "g’olib", "g`olib"),
    # tutuq variants
    ("ma'no", "ma‘no", "maʻno", "ma’no", "ma`no"),
    ("san'at", "san‘at", "sanʻat", "san’at", "san`at"),
]

print("=== TESTING COLLOCATIONS SEARCH ===")
for group in test_queries:
    print(f"\nGroup: {group[0]}")
    for q in group:
        res = server.search_collocations(query=q)
        print(f"  Query '{q}' -> {res.get('totalFound', 0)} collocations")

print("\n=== TESTING DICTIONARY SEARCH ===")
for group in test_queries:
    print(f"\nGroup: {group[0]}")
    for q in group:
        res = server.search_dictionary(query=q)
        print(f"  Query '{q}' -> {len(res)} dictionary entries")
