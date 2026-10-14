import json

c = json.load(open('data/full_corpus.json', encoding='utf-8'))
kvk = [s for s in c if s.get('book') == 'cholpon']

target_phrases = [
    'set the table', 'over tea', 'give an answer', 'with a joke',
    'heavy sleep', 'eldest wife', 'fell asleep', 'had become pale',
    'elder wife', 'deep sleep', 'heart fluttering', 'began to flutter',
    'cool wind', 'older women', 'didn’t reply', 'did not reply', 'reply to my invitation'
]

for phrase in target_phrases:
    matches = []
    for s in kvk:
        en = s.get('en', '')
        if phrase in en.lower():
            matches.append((s['id'], s.get('uz_page'), s.get('en_page'), en[:70]))
    print(f'Phrase "{phrase}": {len(matches)} matches')
    for m in matches[:2]:
        print(f'   {m[0]} (UZ p.{m[1]} <-> EN p.{m[2]}): {m[3]}...')
