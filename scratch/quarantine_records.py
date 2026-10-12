import json

# 1. Update full_corpus.json
with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
    corpus = json.load(f)

excluded_stevenson = 0
for item in corpus:
    uz_text = item.get('uz', '')
    book = item.get('book', '')
    if 'Sarguzasht parchasi:' in uz_text or book == 'stevenson':
        item['status'] = 'excluded'
        item['exclusion_reason'] = "D2: Xazinalar oroli o'zbekcha tarjimasi skanerlangan rasm (matn qatlami yo'q), vaqtinchalik sarguzasht parchasi to'ldiruvchisi"
        excluded_stevenson += 1
    else:
        item['status'] = 'active'

with open('data/full_corpus.json', 'w', encoding='utf-8') as f:
    json.dump(corpus, f, ensure_ascii=False, indent=2)

print(f"full_corpus.json: {len(corpus)} total items. {excluded_stevenson} quarantined (Stevenson placeholders). {len(corpus) - excluded_stevenson} active.")

# 2. Update collocations_full.json
with open('data/collocations_full.json', 'r', encoding='utf-8') as f:
    collocs = json.load(f)

excluded_collocs = 0
for c in collocs:
    en_words = c.get('english', '').strip().split()
    uz_words = c.get('uzbek', '').strip().split()
    is_repeated = (len(en_words) >= 3 and len(set(en_words)) == 1) or (len(uz_words) >= 3 and len(set(uz_words)) == 1)
    if is_repeated or c.get('id') in ['colloc-6411', 'colloc-6412']:
        c['status'] = 'excluded'
        c['exclusion_reason'] = "D6: Sintetik yoki takroriy demo yozuv"
        excluded_collocs += 1
    else:
        c['status'] = 'active'

with open('data/collocations_full.json', 'w', encoding='utf-8') as f:
    json.dump(collocs, f, ensure_ascii=False, indent=2)

print(f"collocations_full.json: {len(collocs)} total items. {excluded_collocs} quarantined (D6 synthetic records). {len(collocs) - excluded_collocs} active.")
