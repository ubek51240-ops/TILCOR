import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
from test_uz_norm import uz_norm

with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
    corpus = json.load(f)

# Collect all tokens containing ko...ng in Cholpon
matched_sentences = []
word_forms = set()

for c in corpus:
    if c.get('book') != 'stevenson':
        uz_raw = c.get('uz', '')
        uz_n, offsets = uz_norm(uz_raw, return_offsets=True)
        # Match tokens starting with koʻngil or koʻngl
        tokens = re.finditer(r'\b(ko\u02bbngil[a-z\u02bb\u02bc]*|ko\u02bbngl[a-z\u02bb\u02bc]*)\b', uz_n)
        has_match = False
        for m in tokens:
            has_match = True
            norm_word = m.group(0)
            orig_span = (offsets[m.start()], offsets[m.end() - 1] + 1)
            orig_word = uz_raw[orig_span[0]:orig_span[1]]
            word_forms.add((norm_word, orig_word))
        if has_match:
            matched_sentences.append(c['id'])

print(f"Total sentences matching koʻngil / koʻngl: {len(matched_sentences)}")
print(f"Unique forms found ({len(word_forms)}):")
for n_w, o_w in sorted(word_forms)[:25]:
    print(f"  Norm: {n_w:<15} | Orig in text: {o_w}")
