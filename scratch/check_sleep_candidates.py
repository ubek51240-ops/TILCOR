import sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, '.')
from search_engine import execute_unified_search

corpus = json.load(open('data/full_corpus.json', encoding='utf-8'))
collocations = json.load(open('data/collocations_full.json', encoding='utf-8'))
dictionary = json.load(open('data/dictionary.json', encoding='utf-8'))

res = execute_unified_search('sleep', corpus, collocations, dictionary, limit=50)
print('Collocations extracted for sleep:')
for c in res['corpus_candidates']:
    print(' ', c['collocation'], ':', c['pattern'], f"({c['occurrences_count']} occurrences)")

print('Admin candidates for sleep:')
for c in res.get('admin_candidates', []):
    print(' ', c['collocation'], ':', c['pattern'], f"({c['occurrences_count']} occurrences)")
