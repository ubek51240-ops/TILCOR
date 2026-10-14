import json
import re

with open('data/collocations_full.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

failed = []
reasons = {}

# Non-Uzbek characters (Turkish / Cyrillic in Latin text / unusual Unicode)
turkish_chars = re.compile(r'[ğşıüöçĞŞİÜÖÇ]')

for it in items:
    if it.get('status') == 'rejected' or not it.get('public_visible', True):
        continue
    uz = it.get('uzbek', '').strip()
    en = it.get('english', '').strip()
    pattern = it.get('pattern', '').lower()
    reason = None
    
    # 1. contains ~ or leftover templates
    if '~' in uz or '~' in en or '...' in uz or '{' in uz or '}' in uz or '[' in uz or ']' in uz:
        reason = 'template_fragment_or_tilde'
    # 2. non-Uzbek words / characters (e.g. Turkish güveç)
    elif turkish_chars.search(uz):
        reason = 'non_uzbek_characters'
    # 3. repeated tokens (consecutive duplicate words)
    else:
        words = [w.lower() for w in re.findall(r'\b[\w\u02bb\u02bc\'-]+\b', uz)]
        has_repeat = False
        for i in range(len(words)-1):
            if words[i] == words[i+1] and len(words[i]) > 2:
                has_repeat = True
                break
        if has_repeat:
            reason = 'repeated_tokens'
        # 4. spelling errors like 'engil' instead of 'yengil'
        elif re.search(r'\bengil\b', uz.lower()):
            reason = 'spelling_error_engil'
        # 5. part of speech mismatch:
        # e.g., English has verb+noun, but uzbek is just a raw noun or has nonsensical ending like '~' or 'bor' as noun
        elif 'verb' in pattern and 'noun' in pattern:
            # Verb + Noun in English usually translates to a verb phrase ending in moq, qildi, bo'ldi, etdi, qol, etc.
            # but if uzbek translation is just a single noun or adjective
            if len(words) == 1 and not uz.endswith(('moq', 'mak')):
                reason = 'pos_mismatch_single_noun_for_verb_collocation'

    if reason:
        failed.append((it['id'], en, uz, reason))
        reasons[reason] = reasons.get(reason, 0) + 1

active_count = len([i for i in items if i.get('status') != 'rejected' and i.get('public_visible', True)])
print(f'Total active items checked: {active_count}')
print(f'Failed items: {len(failed)}')
for r, c in reasons.items():
    print(f'  {r}: {c}')
print('Sample 10 failed:')
for it in failed[:10]:
    print(' ', it)
