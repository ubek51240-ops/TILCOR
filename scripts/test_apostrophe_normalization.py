import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')

import re
from word_family import (
    normalize_apostrophes,
    clean_word,
    match_uzbek_word_family,
    detect_query_language,
    APOSTROPHE_CHARS
)
from search_engine import execute_unified_search, TOKEN_PATTERN
import server

def test_normalization():
    print("--- 1. Testing normalize_apostrophes ---")
    variants = ["'", "’", "‘", "`", "ʻ", "ʼ", "´", "ʹ", "՚", "′", "‵", "ˈ"]
    for v in variants:
        word = f"o{v}z"
        norm = normalize_apostrophes(word)
        assert norm == "o'z", f"Failed for {word}: got {norm}"
    print("✓ All 12 Unicode apostrophe variants normalized to standard ASCII '")

def test_clean_word_and_cyrillic():
    print("\n--- 2. Testing clean_word & Cyrillic ---")
    oz_variants = ["o'z", "o‘z", "oʻz", "o’z", "o`z", "ўз"]
    for v in oz_variants:
        cw = clean_word(v)
        assert cw == "o'z", f"clean_word({v}) expected o'z, got {cw}"
    print("✓ All o'z variants (phone, keyboard, book, Cyrillic) map to 'o'z'")

    g_variants = ["g'olib", "g‘olib", "gʻolib", "g’olib", "g`olib", "ғолиб"]
    for v in g_variants:
        cw = clean_word(v)
        assert cw == "g'olib", f"clean_word({v}) expected g'olib, got {cw}"
    print("✓ All g'olib variants map to 'g'olib'")

    mano_variants = ["ma'no", "ma‘no", "maʻno", "ma’no", "maʼno", "ma`no", "маъно"]
    for v in mano_variants:
        cw = clean_word(v)
        assert cw == "ma'no", f"clean_word({v}) expected ma'no, got {cw}"
    print("✓ All ma'no tutuq belgisi variants map to 'ma'no'")

def test_morphological_matching():
    print("\n--- 3. Testing match_uzbek_word_family across apostrophes ---")
    # Phone query matching book candidate
    res1 = match_uzbek_word_family("o’z", "o‘zini")
    assert res1 is not None and res1[0] == 'inflected', f"Failed phone->book: {res1}"
    
    # Keyboard backtick query matching standard candidate
    res2 = match_uzbek_word_family("ko`z", "koʻzlar")
    assert res2 is not None and res2[0] == 'inflected', f"Failed keyboard->standard: {res2}"
    
    # Exact matching with different apostrophes
    res3 = match_uzbek_word_family("ma’no", "maʻno")
    assert res3 is not None and res3[0] == 'exact', f"Failed exact match: {res3}"
    print("✓ Morphological cross-apostrophe matching verified")

def test_token_pattern():
    print("\n--- 4. Testing TOKEN_PATTERN extraction ---")
    sample_sentence = "Chol dengizda o‘z qayig‘ida suzib yurardi. Bu ma’lum va mashhur san’at edi. Don’t worry, o`g`il!"
    tokens = TOKEN_PATTERN.findall(sample_sentence)
    expected_words = ["o‘z", "qayig‘ida", "ma’lum", "san’at", "Don’t", "o`g`il"]
    for ew in expected_words:
        assert ew in tokens, f"TOKEN_PATTERN missed '{ew}' in extracted: {tokens}"
    print("✓ TOKEN_PATTERN correctly preserves tokens without splitting at curly/phone apostrophes")

def test_collocations_equivalence():
    print("\n--- 5. Testing server.search_collocations consistency ---")
    results = {}
    for q in ["o'z", "o‘z", "oʻz", "o’z", "o`z"]:
        res = server.search_collocations(query=q)
        results[q] = res.get('totalFound', 0)
    print(f"Collocations 'o'z' results: {results}")
    counts = list(results.values())
    assert all(c == counts[0] for c in counts), f"Inconsistent collocation counts: {results}"
    assert counts[0] > 0, "No collocations found for o'z!"

    dict_results = {}
    for q in ["ko'z", "ko‘z", "koʻz", "ko’z", "ko`z"]:
        res = server.search_dictionary(query=q)
        dict_results[q] = len(res)
    print(f"Dictionary 'ko'z' results: {dict_results}")
    d_counts = list(dict_results.values())
    assert all(c == d_counts[0] for c in d_counts), f"Inconsistent dictionary counts: {dict_results}"
    assert d_counts[0] > 0, "No dictionary entries found for ko'z!"
    print("✓ 100% identical results across all phone, keyboard, book queries in collocations & dictionary")

def test_unified_search_consistency():
    print("\n--- 6. Testing execute_unified_search consistency ---")
    active_c = server.get_active_corpus()[:300]
    active_col = server.get_active_collocations()[:300]
    active_d = server.get_active_dictionary()[:300]
    
    q_variants = ["ko'z", "ko‘z", "koʻz", "ko’z", "ko`z"]
    counts = []
    for q in q_variants:
        res = execute_unified_search(q, active_c, active_col, active_d)
        sc = res.get('summary', {}).get('corpus_occurrences', 0)
        wc = res.get('summary', {}).get('total_word_forms', 0)
        counts.append((sc, wc))
    print(f"Unified search 'ko'z' occurrences & word forms: {dict(zip(q_variants, counts))}")
    assert all(c == counts[0] for c in counts), f"Unified search inconsistent: {counts}"
    assert counts[0][0] > 0, "No sentences found for ko'z!"
    print("✓ Unified search returns perfectly identical results across all apostrophe inputs")

if __name__ == '__main__':
    test_normalization()
    test_clean_word_and_cyrillic()
    test_morphological_matching()
    test_token_pattern()
    test_collocations_equivalence()
    test_unified_search_consistency()
    print("\n==========================================")
    print("🎉 ALL APOSTROPHE TESTS PASSED SUCCESSFULLY!")
    print("==========================================")
