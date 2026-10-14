import json
import re
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

dict_path = os.path.join('data', 'dictionary.json')
with open(dict_path, 'r', encoding='utf-8') as f:
    entries = json.load(f)

print(f"Total initial dictionary entries: {len(entries)}")

english_stopwords = {
    'the', 'and', 'with', 'for', 'about', 'from', 'that', 'this', 'have', 'sweet',
    'take', 'give', 'make', 'which', 'their', 'there', 'what', 'when', 'where', 'who'
}

stats = {
    "ends_with_hyphen_or_comma": 0,
    "capital_letter_inside_word": 0,
    "stray_symbols_or_brackets": 0,
    "english_words_in_uzbek": 0,
    "truncated_translation": 0,
    "headword_split_error": 0,
    "active_clean": 0
}

source_str = "Inglizcha-o‘zbekcha lug‘at (Nazarov S. va boshq., «Niso Poligraf», 2013, 816 b.)"

for e in entries:
    w = e.get('word', '').strip()
    tr = e.get('translation', '').strip()
    
    e['dictionary_source'] = source_str
    
    reason = None
    
    # 1. Ends with '-' or ','
    if tr.endswith('-') or tr.endswith(','):
        reason = 'ends_with_hyphen_or_comma'
        stats["ends_with_hyphen_or_comma"] += 1
    # 2. Capital letter inside a word (e.g. sevimlL)
    elif re.search(r'[a-z\u02bb\u02bc][A-Z]', tr):
        reason = 'capital_letter_inside_word'
        stats["capital_letter_inside_word"] += 1
    # 3. Soft hyphens or stray symbols such as '{', '[', '~'
    elif any(sym in tr for sym in ['{', '}', '[', ']', '~', '\u00ad']):
        reason = 'stray_symbols_or_brackets'
        stats["stray_symbols_or_brackets"] += 1
    # 4. English words inside Uzbek translation
    elif any(re.search(rf'\b{re.escape(ew)}\b', tr.lower()) for ew in english_stopwords):
        reason = 'english_words_in_uzbek_translation'
        stats["english_words_in_uzbek"] += 1
    # 5. Looks truncated
    elif re.search(r'\s[a-z]$', tr.lower()) or len(tr) <= 2:
        reason = 'truncated_translation'
        stats["truncated_translation"] += 1
    # 6. Headword split error
    elif w.startswith('-') or w.endswith('-') or ',' in w or len(w) <= 1:
        reason = 'headword_split_error'
        stats["headword_split_error"] += 1

    if reason:
        e['needs_repair'] = True
        e['public_visible'] = False
        e['repair_reason'] = reason
    else:
        e['needs_repair'] = False
        e['public_visible'] = True
        stats["active_clean"] += 1

print("--- DICTIONARY AUDIT RESULTS ---")
for k, v in stats.items():
    print(f"  {k}: {v}")

with open(dict_path, 'w', encoding='utf-8') as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print(f"Updated {dict_path}. Clean active entries: {stats['active_clean']}")
