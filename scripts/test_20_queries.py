import os
import sys
import json
import time

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from search_engine import execute_unified_search

def run_test_suite():
    corpus_path = os.path.join(BASE_DIR, 'data', 'full_corpus.json')
    colloc_path = os.path.join(BASE_DIR, 'data', 'collocations_full.json')
    dict_path = os.path.join(BASE_DIR, 'data', 'dictionary.json')

    print("[*] Loading datasets for 20-query test suite...")
    corpus = json.load(open(corpus_path, encoding='utf-8'))
    collocs = json.load(open(colloc_path, encoding='utf-8'))
    dictionary = json.load(open(dict_path, encoding='utf-8'))

    # The 20 exact queries from TILCOR_05 Part 3.4:
    # (yurak, yuragi, ko‘ngil written with ʻ ‘ ' `, юрак, qaror, qishloq, chol, akula, Poshshaxon, heart, decision, decide, shark, old man, sea, lions, made, take)
    test_queries = [
        "yurak",
        "yuragi",
        "ko‘ngil",
        "koʻngil",
        "ko'ngil",
        "ko`ngil",
        "юрак",
        "qaror",
        "qishloq",
        "chol",
        "akula",
        "Poshshaxon",
        "heart",
        "decision",
        "decide",
        "shark",
        "old man",
        "sea",
        "lions",
        "made",
        "take"
    ]

    results = []
    all_passed = True

    print(f"\n{'#':<3} | {'Query':<15} | {'Time (s)':<9} | {'Sentences':<10} | {'Books':<22} | {'Pagination':<10} | {'Status'}")
    print("-" * 90)

    for i, q in enumerate(test_queries, 1):
        t0 = time.time()
        try:
            res = execute_unified_search(
                query=q,
                active_corpus=corpus,
                active_collocations=collocs,
                active_dictionary=dictionary,
                limit=50,
                page=1
            )
            elapsed = time.time() - t0
            sentences_count = res['summary']['corpus_occurrences']
            page_size = len(res['corpus_sentences'])
            books_represented = set(s['book'] for s in res['corpus_sentences'])
            books_str = ", ".join(books_represented) if books_represented else "—"

            # Validations
            time_pass = elapsed < 2.0
            page_pass = page_size <= 50
            books_pass = True
            if q in ("yurak", "chol"):
                books_pass = ('hemingway' in books_represented) and ('cholpon' in books_represented)

            status = "PASS" if (time_pass and page_pass and books_pass) else "FAIL"
            if status == "FAIL":
                all_passed = False

            print(f"{i:<3} | {q:<15} | {elapsed:<9.3f} | {sentences_count:<10} | {books_str:<22} | {page_size:<10} | {status}")

            results.append({
                "query": q,
                "elapsed_seconds": round(elapsed, 4),
                "total_occurrences": sentences_count,
                "paginated_count": page_size,
                "books": list(books_represented),
                "passed": (status == "PASS")
            })
        except Exception as e:
            elapsed = time.time() - t0
            print(f"{i:<3} | {q:<15} | {elapsed:<9.3f} | ERROR: {str(e)} | FAIL")
            all_passed = False
            results.append({
                "query": q,
                "elapsed_seconds": round(elapsed, 4),
                "error": str(e),
                "passed": False
            })

    out_path = os.path.join(BASE_DIR, 'data', 'test_20_queries_report.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 90)
    print(f"Overall Result: {'100% ALL 20 TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    print(f"Report saved to {out_path}")
    print("=" * 90)

if __name__ == '__main__':
    run_test_suite()
