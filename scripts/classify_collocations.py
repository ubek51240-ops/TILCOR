import json
import re
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

input_path = os.path.join('data', 'collocations_full.json')
with open(input_path, 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"Total initial collocations: {len(items)}")

turkish_chars = re.compile(r'[ğşıüöçĞŞİÜÖÇ]')

stats = {
    "already_rejected": 0,
    "legacy_rejected": 0,
    "template_or_tilde": 0,
    "non_uzbek_chars": 0,
    "repeated_tokens": 0,
    "spelling_error_engil": 0,
    "pos_mismatch": 0,
    "active_clean": 0
}

for it in items:
    cid = it.get('id', '')
    uz = it.get('uzbek', '').strip()
    en = it.get('english', '').strip()
    pattern = it.get('pattern', '').lower()
    
    # Check legacy collocations
    if any(cid.startswith(p) for p in ['col-kk-', 'col-hem-', 'col-gen-']):
        it['status'] = 'rejected'
        it['public_visible'] = False
        it['rejection_reason'] = 'legacy_sample_not_found_verbatim_in_corpus'
        it['class'] = 'AI-TAKLIF'
        stats["legacy_rejected"] += 1
        continue

    # If already rejected previously
    if it.get('status') == 'rejected' or not it.get('public_visible', True):
        stats["already_rejected"] += 1
        continue

    rejection_reason = None

    # 1. contains ~ or leftover templates
    if '~' in uz or '~' in en or '...' in uz or '{' in uz or '}' in uz or '[' in uz or ']' in uz:
        rejection_reason = 'template_fragment_or_tilde'
        stats["template_or_tilde"] += 1
    # 2. non-Uzbek words / characters (e.g. Turkish güveç)
    elif turkish_chars.search(uz):
        rejection_reason = 'non_uzbek_characters'
        stats["non_uzbek_chars"] += 1
    else:
        words = [w.lower() for w in re.findall(r'\b[\w\u02bb\u02bc\'-]+\b', uz)]
        # 3. repeated tokens
        has_repeat = False
        for i in range(len(words)-1):
            if words[i] == words[i+1] and len(words[i]) > 2:
                has_repeat = True
                break
        if has_repeat:
            rejection_reason = 'repeated_tokens'
            stats["repeated_tokens"] += 1
        # 4. spelling errors like 'engil'
        elif re.search(r'\bengil\b', uz.lower()):
            rejection_reason = 'spelling_error_engil'
            stats["spelling_error_engil"] += 1
        # 5. part of speech mismatch
        elif 'verb' in pattern and 'noun' in pattern:
            if len(words) == 1 and not uz.endswith(('moq', 'mak')):
                rejection_reason = 'pos_mismatch_single_noun_for_verb_collocation'
                stats["pos_mismatch"] += 1

    if rejection_reason:
        it['status'] = 'rejected'
        it['public_visible'] = False
        it['rejection_reason'] = rejection_reason
    else:
        it['status'] = 'active'
        it['public_visible'] = True
        it['ai_suggestion'] = True
        stats["active_clean"] += 1

print("--- CLASSIFICATION RESULTS ---")
for k, v in stats.items():
    print(f"  {k}: {v}")

with open(input_path, 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

# Also update js/collocations_list.js with active collocations only
active_collocations = [it for it in items if it.get('public_visible') and it.get('status') != 'rejected']
print(f"Total public active collocations: {len(active_collocations)}")

js_path = os.path.join('js', 'collocations_list.js')
with open(js_path, 'w', encoding='utf-8') as f:
    f.write('// TILCOR - Faol ilmiy kollokatsiyalar ma\'lumotnomasi (Tozalangan)\n')
    f.write('const collocationsDatabase = ')
    json.dump(active_collocations, f, ensure_ascii=False)
    f.write(';\n')

print(f"Updated {input_path} and {js_path}")
