import os
import json
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def map_and_preserve_reviews():
    old_fc = json.load(open(os.path.join(DATA_DIR, 'full_corpus.json'), encoding='utf-8'))
    v3_fc = json.load(open(os.path.join(DATA_DIR, 'full_corpus_v3.json'), encoding='utf-8'))

    # Build index of v3 by normalized Uzbek snippet
    v3_by_uz = {}
    for p in v3_fc:
        if p.get('uz'):
            clean_snippet = re.sub(r'\s+', ' ', p['uz'].strip().lower())[:60]
            v3_by_uz[clean_snippet] = p

    mapping = {}
    carried_count = 0

    for old_p in old_fc:
        old_id = old_p['id']
        old_uz = old_p.get('uz', '').strip()
        clean_snippet = re.sub(r'\s+', ' ', old_uz.lower())[:60]
        
        target_v3 = None
        # Special explicit requirement: aln-kvk-01856 maps to the fixed azayimxon pair
        if old_id == 'aln-kvk-01856' or 'azayimxonnikiga yuborishga qaror berildi' in old_uz:
            for p in v3_fc:
                if 'azayimxonnikiga yuborishga qaror berildi' in p.get('uz', ''):
                    target_v3 = p
                    break
        elif clean_snippet in v3_by_uz:
            target_v3 = v3_by_uz[clean_snippet]

        if target_v3:
            mapping[old_id] = target_v3['id']
            # If old pair had gold_review_150 or tasdiqlangan, carry over!
            if old_p.get('gold_review_150'):
                target_v3['gold_review_150'] = True
                target_v3['status'] = old_p.get('status', 'tasdiqlangan')
                carried_count += 1
            if old_p.get('notes'):
                target_v3['notes'] = old_p.get('notes')

    # Explicitly mark anchor 12 / aln-kvk-01856 target as 'tasdiqlangan'
    for p in v3_fc:
        if 'azayimxonnikiga yuborishga qaror berildi' in p.get('uz', ''):
            p['status'] = 'tasdiqlangan'
            p['v2_id'] = 'aln-kvk-01856'
            break

    # Save mapping and updated v3
    map_path = os.path.join(DATA_DIR, 'v2_to_v3_mapping.json')
    with open(map_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    out_v3 = os.path.join(DATA_DIR, 'full_corpus_v3.json')
    with open(out_v3, 'w', encoding='utf-8') as f:
        json.dump(v3_fc, f, indent=2, ensure_ascii=False)

    print(f"[+] Total v2 to v3 mapped pairs: {len(mapping)}")
    print(f"[+] Gold review decisions carried over: {carried_count}")
    print(f"[+] Saved mapping to {map_path}")

    # Now make full_corpus_v3.json active as full_corpus.json (preserving v2 backup)
    active_path = os.path.join(DATA_DIR, 'full_corpus.json')
    with open(active_path, 'w', encoding='utf-8') as f:
        json.dump(v3_fc, f, indent=2, ensure_ascii=False)
    print(f"[+] Successfully promoted Version 3 to active {active_path}")

if __name__ == '__main__':
    map_and_preserve_reviews()
