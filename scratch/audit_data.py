import json
import re
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("--- AUDITING FULL_CORPUS.JSON ---")
with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
    corpus = json.load(f)

books = {}
scores = set()
licenses = set()
for item in corpus:
    b = item.get('book', 'unknown')
    books[b] = books.get(b, 0) + 1
    scores.add(item.get('score'))
    licenses.add(item.get('license'))

print("Total corpus items:", len(corpus))
print("Books breakdown:", books)
print("Unique scores:", scores)
print("Unique licenses:", licenses)

print("\n--- AUDITING COLLOCATIONS_FULL.JSON ---")
with open('data/collocations_full.json', 'r', encoding='utf-8') as f:
    collocs = json.load(f)

print("Total collocations:", len(collocs))
src_counts = {}
repeated_tokens = 0
garbage_uz = 0
for c in collocs:
    srcs = tuple(c.get('sources', []))
    src_counts[srcs] = src_counts.get(srcs, 0) + 1
    en = c.get('english', '').lower()
    uz = c.get('uzbek', '').lower()
    words = en.split()
    if len(words) >= 2 and len(set(words)) == 1:
        repeated_tokens += 1
    if any(g in uz for g in ['güveç', 'ostiga keling', 'yaxshi go‘zal go‘zal']):
        garbage_uz += 1

print("Sources breakdown:")
for k, v in sorted(src_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {k}: {v}")
print(f"Repeated tokens: {repeated_tokens}, Garbage Uzbek: {garbage_uz}")

print("\n--- AUDITING DICTIONARY.JSON ---")
with open('data/dictionary.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("Total dictionary items:", len(d))
damaged = 0
for item in d:
    w = item.get('word', '')
    tr = item.get('translation', '')
    if w in ['rim', 'tomir', 'va yuzdan yurakka'] or tr.startswith('gan-') or 'qo‘rqoq, yurak-' in tr:
        damaged += 1
    elif re.search(r'\b(adj\.|n\.|v\.|adv\.)', w) or len(w) <= 1 or tr.endswith('-') or len(tr) <= 1:
        damaged += 1

print(f"Identified OCR-damaged dictionary entries: {damaged}")
