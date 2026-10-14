import os
import sys
import json
import re
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def clean_reference_base():
    colloc_path = os.path.join(DATA_DIR, 'collocations_full.json')
    corpus_path = os.path.join(DATA_DIR, 'full_corpus.json')
    dict_path = os.path.join(DATA_DIR, 'dictionary.json')

    print("[*] Loading collocations, corpus, and dictionary...")
    collocs = json.load(open(colloc_path, encoding='utf-8'))
    corpus = json.load(open(corpus_path, encoding='utf-8'))
    dictionary = json.load(open(dict_path, encoding='utf-8'))

    # Dictionary lookup for LUG‘AT class
    dict_entries = {}
    for d in dictionary:
        w = d.get('word', '').lower().strip()
        if w:
            dict_entries[w] = d

    # Fast corpus index for finding book examples
    corpus_pairs = []
    for p in corpus:
        uz_txt = p.get('uz', '').strip()
        en_txt = p.get('en', '').strip()
        if uz_txt and en_txt:
            corpus_pairs.append({
                'id': p.get('id'),
                'book': p.get('book'),
                'bookTitle': p.get('bookTitle'),
                'uz': uz_txt,
                'en': en_txt,
                'uz_lower': uz_txt.lower(),
                'en_lower': en_txt.lower(),
                'uz_page': p.get('uz_page'),
                'en_page': p.get('en_page'),
                'page_source': p.get('page_source', ''),
                'page_target': p.get('page_target', '')
            })

    hidden_count = 0
    split_count = 0
    merged_count = 0
    corpus_linked_count = 0
    lugat_count = 0
    boilerplate_removed_count = 0

    cleaned_list = []
    seen_normalized = {}

    for c in collocs:
        cid = c.get('id', '')
        eng = c.get('english', '').strip()
        uzb = c.get('uzbek', '').strip()
        rej_reason = c.get('rejection_reason') or ''
        r_status = str(c.get('review_status', '')).lower()

        # 1 & 2. Rejection means hidden (public_visible = False)
        # Hide any entry with rejection_reason, rejected status, or legacy_sample
        is_rejected = bool(rej_reason) or (r_status in ('rejected', 'rad etilgan')) or (c.get('status') == 'rejected') or ('legacy_sample' in cid) or ('legacy_sample' in rej_reason)
        if is_rejected:
            c['public_visible'] = False
            hidden_count += 1
        else:
            c['public_visible'] = True

        # col-gen-1 false attribution removal
        if cid == 'col-gen-1' or 'Publitsistika va adabiyot' in str(c):
            if isinstance(c.get('example'), dict):
                c['example']['book'] = 'Namuna gap — AI tomonidan tuzilgan, tekshirilmagan'
            c['sourceBook'] = 'Akademik ma’lumotnoma'
            c['sourceMeta'] = 'Akademik ma’lumotnoma'

        # 3. Malformed entries handling
        if cid == 'colloc-6159' or eng == 'hasty conclusion hasty decision':
            # Split into hasty conclusion and hasty decision
            c['english'] = 'hasty conclusion'
            c['uzbek'] = 'shoshqaloq xulosa'
            c['example'] = {
                'uz': 'U shoshqaloq xulosa chiqarishdan o‘zini tiydi.',
                'en': 'He refrained from jumping to a hasty conclusion.',
                'book': 'Namuna gap — AI tomonidan tuzilgan, tekshirilmagan'
            }
            c_b = dict(c)
            c_b['id'] = 'colloc-6159-b'
            c_b['english'] = 'hasty decision'
            c_b['uzbek'] = 'shoshqaloq qaror'
            c_b['example'] = {
                'uz': 'Bunday jiddiy masalada shoshqaloq qaror qabul qilish yaramaydi.',
                'en': 'One should not make a hasty decision on such a serious matter.',
                'book': 'Namuna gap — AI tomonidan tuzilgan, tekshirilmagan'
            }
            cleaned_list.append(c)
            cleaned_list.append(c_b)
            split_count += 1
            continue

        if cid == 'colloc-6257' or eng == 'defend your decision arbitrary':
            c['english'] = 'defend your decision'
            c['uzbek'] = 'o‘z qarorini himoya qilmoq'
            split_count += 1

        # 4. Dictionary forms:
        # English headword singular: "snap decisions" -> "snap decision"
        if eng.endswith(' decisions') and not eng.endswith('make decisions'):
            c['english'] = eng[:-1] # drop 's'
            eng = c['english']

        # Uzbek variants: -moq form, remove personal possessives
        if uzb:
            uzb = uzb.replace('qaroringizni himoya qilmoq', 'o‘z qarorini himoya qilmoq')
            uzb = uzb.replace('qaror qabul qilish', 'qaror qabul qilmoq')
            c['uzbek'] = uzb

        if c.get('uzbek_variants'):
            for v in c['uzbek_variants']:
                vt = v.get('text', '')
                vt = vt.replace('qaroringizni himoya qilmoq', 'o‘z qarorini himoya qilmoq')
                vt = vt.replace('qaror qabul qilish', 'qaror qabul qilmoq')
                v['text'] = vt

        # 5. Duplicates: normalize by stripping leading articles ("a ", "an ", "the ")
        norm_key = re.sub(r'^(?:a|an|the)\s+', '', eng.lower().strip())
        if norm_key in seen_normalized and not is_rejected:
            # Merge with existing entry
            prev_entry = seen_normalized[norm_key]
            # merge sources
            prev_sources = prev_entry.get('all_sources') or [prev_entry.get('sourceBook') or prev_entry.get('sourceMeta')]
            curr_source = c.get('sourceBook') or c.get('sourceMeta')
            if curr_source and curr_source not in prev_sources:
                prev_sources.append(curr_source)
            prev_entry['all_sources'] = prev_sources
            merged_count += 1
            continue

        # 6. Template text: remove boilerplate in literalTrap and culturalNote
        trap = c.get('literalTrap', '')
        if trap and ('soʻzma-soʻz kalka' in trap or 'kollokatsion quvvatsiz' in trap or 'noaniq' in trap or 'uslubiy jihatdan' in trap):
            c['literalTrap'] = ''
            boilerplate_removed_count += 1

        note = c.get('culturalNote', '')
        if note and ('Milliy-madaniy xususiyatga ega birikma (3.3-bob)' in note or 'Kalka va madaniy toʻsiq (3.3-bob)' in note):
            c['culturalNote'] = ''
            boilerplate_removed_count += 1

        # 7. Link to the corpus
        # Search the English collocation in corpus
        found_pair = None
        if len(eng) >= 4:
            e_regex = re.compile(r'\b' + re.escape(eng) + r'\b', re.IGNORECASE)
            for cp in corpus_pairs:
                if e_regex.search(cp['en']):
                    found_pair = cp
                    break

        if found_pair:
            c['class'] = 'KORPUS'
            c['corpus_occurrences'] = 1
            c['example'] = {
                'source_sentence': found_pair['en'],
                'target_sentence': found_pair['uz'],
                'book': found_pair['bookTitle'],
                'page_source': found_pair['page_target'],
                'page_target': found_pair['page_source']
            }
            corpus_linked_count += 1
        else:
            c['corpus_occurrences'] = 0
            # 8. Namuna gap for entries without book example
            ex = c.get('example')
            if not ex or not ex.get('book') or 'Publitsistika' in ex.get('book', ''):
                c['example'] = {
                    'source_sentence': c.get('exampleEn') or f"He noticed that {eng} was crucial.",
                    'target_sentence': uzb if uzb else "—",
                    'book': 'Namuna gap — AI tomonidan tuzilgan, tekshirilmagan',
                    'label': 'Namuna gap — AI tomonidan tuzilgan, tekshirilmagan',
                    'uzbek_label': 'AI tarjimasi'
                }
            elif 'Namuna gap' not in ex.get('book', ''):
                ex['book'] = 'Namuna gap — AI tomonidan tuzilgan, tekshirilmagan'

        # 9. LUG‘AT class: if researcher dictionary has the Uzbek entry
        if uzb and uzb.lower() in dict_entries:
            d_hit = dict_entries[uzb.lower()]
            c['class'] = 'LUG‘AT'
            c['dictionary_source'] = d_hit.get('dictionary_source', 'O‘zbek tilining izohli lug‘ati')
            c['dictionary_page'] = d_hit.get('page', 1)
            lugat_count += 1

        if not is_rejected:
            seen_normalized[norm_key] = c

        cleaned_list.append(c)

    # Save cleaned collocations
    with open(colloc_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_list, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("PART 5 REFERENCE BASE ROUND 2 CLEANUP REPORT:")
    print("=" * 70)
    print(f"Total entries in dataset: {len(cleaned_list)}")
    print(f"Hidden entries (public_visible=False): {hidden_count}")
    print(f"Split malformed entries: {split_count}")
    print(f"Merged duplicate entries: {merged_count}")
    print(f"Boilerplate template notes removed: {boilerplate_removed_count}")
    print(f"Entries linked to book corpus with KORPUS class: {corpus_linked_count}")
    print(f"Entries assigned LUG‘AT class from dictionary: {lugat_count}")
    print(f"[+] Successfully updated {colloc_path}")

    # Re-export to SQLite
    os.system(f"python {os.path.join(BASE_DIR, 'export_to_sqlite.py')}")

if __name__ == '__main__':
    clean_reference_base()
