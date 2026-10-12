import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

dict_path = 'data/dictionary.json'
with open(dict_path, 'r', encoding='utf-8') as f:
    raw_dict = json.load(f)

print(f"Loaded {len(raw_dict):,} entries from {dict_path}")

en2uz = {}
uz2en = {}

clean_word_pattern = re.compile(r"[\w\u02bb\u02bc']+", re.UNICODE)

for entry in raw_dict:
    en_word = entry.get('word', '').strip().lower()
    trans = entry.get('translation', '').strip().lower()
    if not en_word or not trans:
        continue
    
    # Strip phonetic transcriptions like ['fju:^a(r)l
    trans_clean = re.sub(r'\[.*?\]', ' ', trans)
    # Extract uzbek words
    uz_words = clean_word_pattern.findall(trans_clean)
    uz_clean_words = [w for w in uz_words if len(w) > 2 and w not in ['masalan', 'bilan', 'yoki', 'deb']]
    
    if uz_clean_words:
        if en_word not in en2uz:
            en2uz[en_word] = set()
        en2uz[en_word].update(uz_clean_words)
        
        for uz_w in uz_clean_words:
            if uz_w not in uz2en:
                uz2en[uz_w] = set()
            uz2en[uz_w].add(en_word)

print(f"Constructed bilingual index: {len(en2uz):,} English lemmas -> {len(uz2en):,} Uzbek words")

# Test lookup on sample sentence pair from Hemingway
en_sample = "He was an old man who fished alone in a skiff in the Gulf Stream and he had gone eighty-four days now without taking a fish."
uz_sample = "Chol Golfstrimda kema minib yolg'iz o'zi baliq ovlardi, mana, saksonto'rt kundan beri birorta ham baliq tutolmagandi."

en_tokens = clean_word_pattern.findall(en_sample.lower())
uz_tokens = set(clean_word_pattern.findall(uz_sample.lower()))

matches = []
for tok in en_tokens:
    if tok in en2uz:
        overlap = en2uz[tok].intersection(uz_tokens)
        if overlap:
            matches.append((tok, list(overlap)))

print(f"\nTest alignment overlap between Hemingway EN & UZ opening sentences:")
print(f"Matched lexical anchors: {matches}")
