import json

c = json.load(open('data/full_corpus.json', encoding='utf-8'))
targets = [
    'azayimxon', 'qozgalon', 'poshshaxon', 'qish chiqishga'
]

import sys
sys.path.insert(0, '.')
from word_family import uz_norm

for t in targets:
    t_n = uz_norm(t)
    matches = [s for s in c if t_n in uz_norm(s.get('uz', ''))]
    print(f"Target '{t}': {len(matches)} matches")
    for m in matches:
        print(f"  {m['id']}: UZ {m.get('uz_page')} <-> EN {m.get('en_page')}")
        print(f"    UZ: {m.get('uz')[:70]}")
        print(f"    EN: {m.get('en')[:70]}")
