import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
corpus = json.load(open('data/full_corpus.json', encoding='utf-8'))

EQUIV_TARGETS_UZ = {
    'ko‘ngil': ['heart', 'soul', 'mind', 'spirit', 'desire', 'wish', 'feeling', 'mood', 'affection'],
    'yurak': ['heart', 'breast', 'courage', 'chest', 'bosom'],
    'qaror': ['decision', 'determination', 'resolution', 'decree', 'decide', 'decided', 'resolve']
}

EQUIV_TARGETS_EN = {
    'heart': ['yurak', 'yuragi', 'yurakdan', 'ko‘ngil', 'ko‘ngli', 'qalb', 'dil', 'bag‘ir'],
    'decision': ['qaror', 'qarori', 'hukm', 'to‘xtam', 'xulosa']
}

def propose_target_spans(src_text, tgt_text, q, lang='uz'):
    targets = EQUIV_TARGETS_UZ.get(q, []) if lang == 'uz' else EQUIV_TARGETS_EN.get(q, [])
    found = []
    for t in targets:
        for m in re.finditer(r'\b' + re.escape(t) + r'[a-z\u02bb\u02bc]*\b', tgt_text, re.I):
            found.append({
                'span': m.span(),
                'text': tgt_text[m.start():m.end()]
            })
    return found

print("=== 10 TEST SENTENCE PAIRS FOR 'ko‘ngil' WITH PROPOSED TARGET EQUIVALENTS ===")
cnt = 0
for s in corpus:
    uz = s.get('uz', '')
    en = s.get('en', '')
    if any(k in uz.lower() for k in ['ko‘ngil', 'ko‘ngl', 'koʻngil', 'koʻngl']):
        spans = propose_target_spans(uz, en, 'ko‘ngil', 'uz')
        eq_text = [x['text'] for x in spans] if spans else ["tushirib qoldirilgan"]
        print(f"[{cnt+1}] Status: {s.get('status')} | Equiv: {eq_text}")
        print(f"    Asliyat ({s.get('page_source')}): {uz}")
        print(f"    Tarjima ({s.get('page_target')}): {en}")
        cnt += 1
        if cnt >= 10:
            break

print("\n=== 10 TEST SENTENCE PAIRS FOR 'heart' WITH PROPOSED TARGET EQUIVALENTS ===")
cnt = 0
for s in corpus:
    uz = s.get('uz', '')
    en = s.get('en', '')
    if re.search(r'\bheart[a-z]*\b', en, re.I):
        spans = propose_target_spans(en, uz, 'heart', 'en')
        eq_text = [x['text'] for x in spans] if spans else ["tushirib qoldirilgan"]
        print(f"[{cnt+1}] Status: {s.get('status')} | Equiv: {eq_text}")
        print(f"    Asliyat ({s.get('page_source')}): {en}")
        print(f"    Tarjima ({s.get('page_target')}): {uz}")
        cnt += 1
        if cnt >= 10:
            break
