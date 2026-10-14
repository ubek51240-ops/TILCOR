import json

corpus = json.load(open('data/full_corpus.json', encoding='utf-8'))

anchors = [
    ('salqin shabada', 'cool wind', 3, 46),
    ('katta xotinlarning', 'older women', 4, 46),
    ('otangiz javob bermadi', 'reply', 5, 47),
    ('dasturxon sol', 'set the table', 6, 48),
    ('javob ham bermadi', 'give an answer', 15, 56),
    ('hazillashib javob berdi', 'joke', 23, 63),
    ('og‘ir uyqudan', 'heavy sleep', 36, 74),
    ('katta xotinidan', 'eldest wife', 54, 89),
    ('og‘ir uyquga ketdilar', 'fell asleep', 65, 98),
    ('rangi o‘chgan', 'pale', 66, 100),
    ('katta xotin', 'elder wife', 78, 110),
    ('og‘ir uyquda', 'deep sleep', 93, 123),
    ('yuragi o‘ynab', 'fluttering', 104, 132),
    ('yuragi o‘ynab', 'flutter', 127, 152),
    ('azayimxon', 'healer', 80, 111),
    ('olomon qo‘zg‘alon', 'rebellion', 134, 159),
    ('Poshshaxon ham boridi', 'arrow had missed', 245, 252),
    ('qarindoshlari kelib', 'relatives came', 265, 271)
]

for uz_phrase, en_phrase, exp_uz_p, exp_en_p in anchors:
    # search in corpus
    norm_u = uz_phrase.replace('‘', "'").replace('’', "'")
    matches = [p for p in corpus if p.get('uz') and norm_u in p['uz'].replace('‘', "'").replace('’', "'")]
    if not matches:
        print(f"MISSING UZ: {uz_phrase}")
    else:
        # find the one on exp_uz_p if multiple
        target_m = None
        for m in matches:
            if m.get('uz_page') == exp_uz_p:
                target_m = m
                break
        if not target_m:
            target_m = matches[0]
        
        uz_p = target_m.get('uz_page')
        en_p = target_m.get('en_page')
        en_text = target_m.get('en', '')
        has_en = any(w.lower() in en_text.lower() for w in en_phrase.split())
        passed = (uz_p == exp_uz_p and en_p == exp_en_p)
        status = "o‘tdi" if passed else "o‘tmadi"
        print(f"{uz_phrase:<25} | ID: {target_m['id']} | UZ p.{uz_p} (exp {exp_uz_p}) | EN p.{en_p} (exp {exp_en_p}) | {status} | EN: {en_text[:50]}")
