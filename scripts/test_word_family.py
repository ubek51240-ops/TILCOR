import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from word_family import match_uzbek_word_family, match_english_word_family, detect_query_language

# =============================================================================
# 1. UZBEK TEST LIST (50+ items)
# =============================================================================
# (query, candidate, expected_match, expected_group)
uzbek_test_cases = [
    # yurak family
    ("yurak", "yurak", True, "exact"),
    ("yurak", "yuragi", True, "inflected"),
    ("yurak", "yurakka", True, "inflected"),
    ("yurak", "yuraklari", True, "inflected"),
    ("yurak", "yurakdan", True, "inflected"),
    ("yurak", "yuragim", True, "inflected"),
    ("yurak", "yuragimiz", True, "inflected"),
    ("yurak", "yuragida", True, "inflected"),
    ("yurak", "yurakli", True, "derived"),
    ("yurak", "yuraksiz", True, "derived"),
    ("yurak", "yuraklik", True, "derived"),
    ("yurak", "yurakcha", True, "derived"),
    ("yurak", "yurak-bag‘ir", True, "compound"),
    ("yurak", "ochiq-yurak", True, "compound"),
    ("yurak", "yurakat", False, None),       # false candidate: invalid suffix
    ("yurak", "yurakchaq", False, None),     # false candidate
    ("yurak", "yurakiston", False, None),    # false candidate
    ("yurak", "boshqa", False, None),        # non-match
    
    # burun (vowel drop)
    ("burun", "burun", True, "exact"),
    ("burun", "burni", True, "inflected"),
    ("burun", "burnim", True, "inflected"),
    ("burun", "burunlar", True, "inflected"),
    ("burun", "burniga", True, "inflected"),
    ("burun", "burunli", True, "derived"),
    ("burun", "burnsiz", True, "derived"),
    ("burun", "burunat", False, None),
    
    # ko'ngil (vowel drop & apostrophe)
    ("ko‘ngil", "ko‘ngil", True, "exact"),
    ("ko'ngil", "ko‘ngli", True, "inflected"),
    ("koʻngil", "ko‘nglim", True, "inflected"),
    ("ko`ngil", "ko‘ngliga", True, "inflected"),
    ("ko‘ngil", "ko‘ngilsiz", True, "derived"),
    ("ko‘ngil", "ko‘ngilli", True, "derived"),
    
    # qishloq (consonant alternation q -> g')
    ("qishloq", "qishloq", True, "exact"),
    ("qishloq", "qishlog‘i", True, "inflected"),
    ("qishloq", "qishloqqa", True, "inflected"),
    ("qishloq", "qishloqlar", True, "inflected"),
    ("qishloq", "qishloqchi", True, "derived"),
    ("qishloq", "qishloqcha", True, "derived"),
    
    # qaror
    ("qaror", "qaror", True, "exact"),
    ("qaror", "qarori", True, "inflected"),
    ("qarorlar", "qaror", True, "inflected"),
    ("qaror", "qarorimiz", True, "inflected"),
    ("qaror", "qarordan", True, "inflected"),
    ("qaror", "qarorli", True, "derived"),
    ("qaror", "qarorsiz", True, "derived"),
    ("qaror", "qarorat", False, None),
    
    # cyrillic inputs
    ("юрак", "yurak", True, "exact"),
    ("юрак", "yuragi", True, "inflected"),
    ("юрак", "yuraksiz", True, "derived"),
    ("қарор", "qarori", True, "inflected"),
    ("кўнгил", "ko‘ngli", True, "inflected")
]

# =============================================================================
# 2. ENGLISH TEST LIST (50+ items)
# =============================================================================
english_test_cases = [
    # heart family
    ("heart", "heart", True, "exact"),
    ("heart", "hearts", True, "inflected"),
    ("heart", "heartless", True, "derived"),
    ("heart", "hearty", True, "derived"),
    ("heart", "heartily", True, "derived"),
    ("heart", "heartbeat", True, "compound"),
    ("heart", "heartbreak", True, "compound"),
    ("heart", "heartfelt", True, "compound"),
    ("heart", "wholehearted", True, "compound"),
    ("heart", "soft-hearted", True, "compound"),
    ("heart", "fainthearted", True, "compound"),
    ("heart", "cold-hearted", True, "compound"),
    ("heart", "hearth", False, None),          # false candidate (fireplace)
    ("heart", "heartyest", False, None),
    ("heart", "something", False, None),
    
    # decide family
    ("decide", "decide", True, "exact"),
    ("decide", "decides", True, "inflected"),
    ("decide", "decided", True, "inflected"),
    ("decide", "deciding", True, "inflected"),
    ("decide", "decision", True, "inflected"),
    ("decide", "decisions", True, "inflected"),
    ("decide", "decisive", True, "derived"),
    ("decide", "indecisive", True, "compound"),
    ("decide", "apple", False, None),
    
    # see family
    ("see", "see", True, "exact"),
    ("see", "sees", True, "inflected"),
    ("see", "seeing", True, "inflected"),
    ("see", "saw", True, "inflected"),
    ("see", "seen", True, "inflected"),
    ("see", "sight", True, "derived"),
    ("see", "unseen", True, "compound"),
    ("see", "foresee", True, "compound"),
    ("see", "seed", False, None),
    
    # dark family
    ("dark", "dark", True, "exact"),
    ("dark", "darker", True, "derived"),
    ("dark", "darkest", True, "derived"),
    ("dark", "darkness", True, "derived"),
    ("dark", "darkly", True, "derived"),
    ("dark", "dark-haired", True, "compound"),
    ("dark", "after-dark", True, "compound"),
    ("dark", "dart", False, None),
    
    # life family
    ("life", "life", True, "exact"),
    ("life", "lives", True, "inflected"),
    ("life", "lifeless", True, "derived"),
    ("life", "lifelike", True, "derived"),
    ("life", "lifestyle", True, "compound"),
    ("life", "lifespan", True, "compound"),
    ("life", "real-life", True, "compound"),
    ("life", "line", False, None)
]

print("=== RUNNING UZBEK WORD FAMILY UNIT TESTS ===")
uz_passed = 0
uz_errors = 0
for q, cand, exp_match, exp_grp in uzbek_test_cases:
    res = match_uzbek_word_family(q, cand)
    matched = res is not None
    if matched == exp_match and (not exp_match or res[0] == exp_grp or exp_grp is None):
        uz_passed += 1
    else:
        uz_errors += 1
        print(f"  [FAIL] Uzbek '{q}' vs '{cand}': got {res}, expected match={exp_match}, group={exp_grp}")

uz_err_rate = (uz_errors / len(uzbek_test_cases)) * 100
print(f"Uzbek Tests: {len(uzbek_test_cases)} cases | Passed: {uz_passed} | Errors: {uz_errors} | Error Rate: {uz_err_rate:.2f}%")

print("\n=== RUNNING ENGLISH WORD FAMILY UNIT TESTS ===")
en_passed = 0
en_errors = 0
for q, cand, exp_match, exp_grp in english_test_cases:
    res = match_english_word_family(q, cand)
    matched = res is not None
    if matched == exp_match:
        en_passed += 1
    else:
        en_errors += 1
        print(f"  [FAIL] English '{q}' vs '{cand}': got {res}, expected match={exp_match}")

en_err_rate = (en_errors / len(english_test_cases)) * 100
print(f"English Tests: {len(english_test_cases)} cases | Passed: {en_passed} | Errors: {en_errors} | Error Rate: {en_err_rate:.2f}%")
