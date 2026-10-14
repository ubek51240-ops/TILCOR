import json

c = json.load(open('data/full_corpus.json', encoding='utf-8'))
anchors_def = [
    ('aln-kvk-00067', 'set the table', 'dasturxon solmoq'),
    ('aln-kvk-00069', 'over tea', 'choy ustida'),
    ('aln-kvk-00287', 'give an answer', 'javob bermoq'),
    ('aln-kvk-00473', 'with a joke', 'hazillashib'),
    ('aln-kvk-00775', 'heavy sleep', 'og‘ir uyqu'),
    ('aln-kvk-01188', 'eldest wife', 'katta xotin'),
    ('aln-kvk-01449', 'fell asleep', 'uyquga ketmoq'),
    ('aln-kvk-01472', 'had become pale', 'oqarib ketmoq'),
    ('aln-kvk-01407', 'elder wife', 'katta xotin'),
    ('aln-kvk-02079', 'deep sleep', 'og‘ir uyqu'),
    ('aln-kvk-02342', 'heart fluttering', 'yurak duk-duk'),
    ('aln-kvk-02936', 'began to flutter', 'ura boshladi'),
    ('aln-kvk-00011', 'cool wind', 'salqin shamol'),
    ('aln-kvk-00022', 'older women', 'katta xotinlar'),
    ('aln-kvk-00043', 'reply to my invitation', 'taklifimga javob')
]

for sid, en_phrase, uz_phrase in anchors_def:
    s = next((x for x in c if x['id'] == sid), None)
    if not s:
        print(f'MISSING: {sid}')
        continue
    en = s.get('en', '')
    idx = en.lower().find(en_phrase.lower())
    if idx >= 0:
        span = [idx, idx + len(en_phrase)]
        print(f'FOUND {sid}: "{en[span[0]:span[1]]}" at {span}')
    else:
        print(f'PHRASE NOT FOUND IN {sid}: {en_phrase}')
