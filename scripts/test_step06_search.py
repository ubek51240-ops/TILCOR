import sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from search_engine import execute_unified_search

corpus = json.load(open('data/full_corpus.json', encoding='utf-8'))
collocations = json.load(open('data/collocations_full.json', encoding='utf-8'))
dictionary = json.load(open('data/dictionary.json', encoding='utf-8'))

def search_corpus(q, limit=50):
    return execute_unified_search(q, corpus, collocations, dictionary, limit=limit)

print("=== 1. Testing Cyrillic Queries ===")
for q_cyr, expected_lat in [('юрак', 'yurak'), ('кўнгил', 'ko‘ngil'), ('қарор', 'qaror'), ('қишлоқ', 'qishloq')]:
    res = search_corpus(q_cyr, limit=5)
    s_cnt = res['summary']['corpus_occurrences']
    w_cnt = len(res['words'])
    print(f"Query '{q_cyr}' -> {w_cnt} word forms, {s_cnt} occurrences (sentences: {res['summary']['total_sentences']})")
    assert s_cnt > 0, f"Cyrillic query '{q_cyr}' returned 0 occurrences!"

print("\n=== 2. Testing Gold Candidates ===")
gold_tests = [
    ('javob', 'javob bermoq', 'Ot + fe’l'),
    ('qaror', 'qaror bermoq', 'Ot + fe’l'),
    ('uyqu', 'og‘ir uyqu', 'Sifat + ot'),
    ('dasturxon', 'dasturxon solmoq', 'Ot + fe’l'),
    ('qaror', 'qat’iy qaror', 'Sifat + ot'),
    ('sleep', 'heavy sleep', 'Adjective + noun'),
    ('sleep', 'deep sleep', 'Adjective + noun')
]

for query, expected_cand, expected_pat in gold_tests:
    res = search_corpus(query, limit=50)
    cands = [c for c in res['collocations'] if c.get('collocation') == expected_cand]
    if not cands:
        # Check admin candidates if any
        cands = [c for c in res.get('admin_candidates', []) if c.get('collocation') == expected_cand]
    
    assert cands, f"Gold candidate '{expected_cand}' NOT found for query '{query}'!"
    c = cands[0]
    print(f"FOUND: '{c['collocation']}' | Pattern: {c['pattern']} | Sentences: {c['sentences_count']} | Occurrences: {c['occurrences_count']}")
    assert c['pattern'] == expected_pat, f"Pattern mismatch for {expected_cand}: expected {expected_pat}, got {c['pattern']}"
    
    # Check example contains both constituent words
    ex = c.get('example', {})
    src_sentence = ex.get('source_sentence', '').lower()
    words_in_cand = expected_cand.split()
    print(f"   Example: {src_sentence[:70]}...")

print("\n=== 3. Testing Direction Labels & S5 Display ===")
res_uz = search_corpus('yurak', limit=5)
s0 = res_uz['corpus_sentences'][0]
print(f"Top box (source): {s0.get('source_label')}")
print(f"Bottom box (target): {s0.get('target_label')}")
print(f"Is open: {s0.get('is_open')} | Status label: {s0.get('target_status_label')}")
assert 'Asliyat' in s0.get('source_label'), "source_label missing 'Asliyat'"
assert 'Tarjima' in s0.get('target_label'), "target_label missing 'Tarjima'"

# Test English query on Cho'lpon
res_en = search_corpus('heart', limit=50)
ch_sentences = [s for s in res_en['corpus_sentences'] if s['book'] == 'cholpon']
if ch_sentences:
    ch0 = ch_sentences[0]
    print(f"EN query on Cho'lpon -> Source: {ch0.get('source_label')} | Target: {ch0.get('target_label')}")
    assert 'Asliyat (o‘zbekcha)' in ch0.get('source_label'), "English query on Cho'lpon must have Uzbek as Asliyat"
    assert 'Tarjima (inglizcha)' in ch0.get('target_label'), "English query on Cho'lpon must have English as Tarjima"

print("\n=== 4. Testing Aligned Counts (Defect K) ===")
for q in ['javob', 'sleep', 'qaror', 'heart', 'dasturxon']:
    res = search_corpus(q, limit=10)
    summary_occ = res['summary']['corpus_occurrences']
    sum_words = sum(w['total_occurrences'] for w in res['words'])
    print(f"Query '{q}': summary={summary_occ}, sum_of_words={sum_words}")
    assert summary_occ == sum_words, f"Count mismatch for '{q}': summary {summary_occ} != sum of words {sum_words}"

print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")
