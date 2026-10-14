import json
import re

with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
    corpus = json.load(f)

print('Total segments in full_corpus:', len(corpus))
chars = set()
sample_matches = []

for c in corpus:
    uz = c.get('uz', '')
    if c.get('book') == 'cholpon':
        for ch in uz:
            if ch in "'‘’`´ʻʼ":
                chars.add(ch)
        # Search for words with ko...ngil or ko...ngli
        m = re.findall(r'\b[kK][o\u02bb\u2018\'`\u2019\u00b4\u02bc]+ng[^\s.,!?";:—«»]*', uz)
        if m:
            sample_matches.extend(m)

print('Apostrophe characters in Cholpon:', [f"{c} (U+{ord(c):04X})" for c in chars])
print('Total matches for ko...ng* in Cholpon:', len(sample_matches))
print('Sample matching forms:', list(set(sample_matches))[:20])
