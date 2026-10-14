import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/dictionary.json', 'r', encoding='utf-8') as f:
    dict_entries = json.load(f)

print(f"Total dictionary entries: {len(dict_entries)}")

# Common English words that might leak into Uzbek translation
english_stopwords = {
    'the', 'and', 'with', 'for', 'about', 'from', 'that', 'this', 'have', 'sweet',
    'take', 'give', 'make', 'which', 'their', 'there', 'what', 'when', 'where', 'who'
}

failed = []
reasons = {}

for e in dict_entries:
    w = e.get('word', '').strip()
    tr = e.get('translation', '').strip()
    pos = e.get('pos', '').strip()
    
    reason = None
    
    # 1. Ends with '-' or ','
    if tr.endswith('-') or tr.endswith(','):
        reason = 'ends_with_hyphen_or_comma'
    # 2. Capital letter inside a word (e.g. sevimlL)
    elif re.search(r'[a-z\u02bb\u02bc][A-Z]', tr):
        reason = 'capital_letter_inside_word'
    # 3. Soft hyphens or stray symbols such as '{', '[', '~'
    elif any(sym in tr for sym in ['{', '}', '[', ']', '~', '\u00ad']):
        reason = 'stray_symbols_or_brackets'
    # 4. English words inside Uzbek translation (e.g. 'sweet' in 'sevikli, sevimlL sweet')
    elif any(re.search(rf'\b{re.escape(ew)}\b', tr.lower()) for ew in english_stopwords):
        reason = 'english_words_in_uzbek_translation'
    # 5. Looks truncated (e.g. ends abruptly with single letter or incomplete word without punctuation)
    elif re.search(r'\s[a-z]$', tr.lower()) or len(tr) <= 2:
        reason = 'truncated_translation'
    # 6. Headword looks like a split error (e.g. headword has stray hyphen, comma, or strange chars)
    elif w.startswith('-') or w.endswith('-') or ',' in w or len(w) <= 1:
        reason = 'headword_split_error'
        
    if reason:
        failed.append((w, tr, reason))
        reasons[reason] = reasons.get(reason, 0) + 1

print(f"Total entries inspected: {len(dict_entries)}")
print(f"Total flagged needs_repair: {len(failed)}")
for r, c in reasons.items():
    print(f"  {r}: {c}")

print("\nSample 15 flagged entries:")
for item in failed[:15]:
    print(f"  [{item[2]}] {item[0]} -> {item[1]}")
