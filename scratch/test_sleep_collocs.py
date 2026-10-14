import sys, json, re
sys.path.insert(0, '.')
from word_family import get_wordnet_family, match_english_word_family, ENGLISH_IRREGULAR_PAIRS

TOKEN_EN_RE = re.compile(r"[a-zA-Z]+(?:'[a-zA-Z]+|-?[a-zA-Z]+)*")

collocs = json.load(open('data/collocations_full.json', encoding='utf-8'))
q = 'sleep'
q_low = q.lower()
q_family_tokens = {q_low} | set(get_wordnet_family(q_low))
if q_low in ENGLISH_IRREGULAR_PAIRS:
    q_family_tokens.update(ENGLISH_IRREGULAR_PAIRS[q_low])

matched = []
for it in collocs:
    en_colloc = it.get('english', '').lower()
    tokens = set(TOKEN_EN_RE.findall(en_colloc))
    if (tokens & q_family_tokens) or any(match_english_word_family(q, t) for t in tokens):
        matched.append(it.get('english'))

print(f'Matched {len(matched)} collocations for "{q}":')
for m in matched:
    print(' ', m)
