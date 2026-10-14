import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Import our prototype uz_norm
from test_uz_norm import uz_norm

with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
    corpus = json.load(f)

# Pre-normalize Uzbek sentences in the corpus and keep offsets
normalized_corpus = []
for c in corpus:
    if c.get('book') != 'stevenson':
        uz_raw = c.get('uz', '')
        uz_n, offsets = uz_norm(uz_raw, return_offsets=True)
        normalized_corpus.append({
            'id': c.get('id'),
            'book': c.get('book'),
            'uz_raw': uz_raw,
            'uz_norm': uz_n,
            'offsets': offsets
        })

print(f"Total active normalized corpus sentences: {len(normalized_corpus)}")

# Test the 8 words
test_words = [
    ("o‘zbek", ["o‘zbek", "o'zbek", "oʻzbek", "o`zbek", "o’zbek", "ўзбек"]),
    ("bog‘", ["bog‘", "bog'", "bogʻ", "bog`", "bog’", "боғ"]),
    ("o‘g‘il", ["o‘g‘il", "o'g'il", "oʻgʻil", "o`g`il", "o’g’il", "ўғил"]),
    ("to‘g‘ri", ["to‘g‘ri", "to'g'ri", "toʻgʻri", "to`g`ri", "to’g’ri", "тўғри"]),
    ("ko‘ngil", ["ko‘ngil", "ko'ngil", "koʻngil", "ko`ngil", "ko’ngil", "кўнгил"]),
    ("qishlog‘i", ["qishlog‘i", "qishlog'i", "qishlogʻi", "qishlog`i", "qishlog’i", "қишлоғи"]),
    ("ta’lim", ["ta’lim", "ta'lim", "taʻlim", "ta`lim", "ta’lim", "таълим"]),
    ("ma’no", ["ma’no", "ma'no", "maʻno", "ma`no", "ma’no", "маъно"]),
]

for base, variants in test_words:
    print(f"\n--- Testing word: {base} ---")
    counts = {}
    for var in variants:
        v_norm = uz_norm(var)
        # Count sentences containing v_norm as a word or stem prefix
        token_pat = re.compile(r'\b' + re.escape(v_norm) + r'[a-z\u02bb\u02bc]*\b', re.UNICODE)
        matches = [c for c in normalized_corpus if token_pat.search(c['uz_norm'])]
        counts[var] = len(matches)
        
    print(f"Results for '{base}': {counts}")
    unique_counts = set(counts.values())
    if len(unique_counts) == 1:
        print(f"PASS: All {len(variants)} spellings have identical count: {list(unique_counts)[0]}")
    else:
        print(f"FAIL: Inconsistent counts: {counts}")
