"""Build data/collocation_alternatives.json from the reviewed pairs in data/phd_corpus.db.

Only candidates listed in REVIEWED are exported. Every value is checked against the database:
if a stored span, occurrence or annotation does not match, the script stops without writing.
Nothing is inferred: the alternative is exactly the span the researcher/annotator recorded.

Run:  python -X utf8 scripts/build_collocation_alternatives.py
"""
import json
import os
import sqlite3
import sys
import unicodedata

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, 'data', 'phd_corpus.db')
OUT = os.path.join(BASE, 'data', 'collocation_alternatives.json')

# candidate id -> (query language, query span, alternative language, expected alternative, book pair)
REVIEWED = [
    ('col-hem-1', 'en', 'fished alone', 'uz', 'baliq ovlardi', 'pair-hemingway-old-man-sea'),
    ('col-hem-3', 'en', 'deep wrinkles', 'uz', 'chuqur ajinlar', 'pair-hemingway-old-man-sea'),
    ('col-kk-1', 'uz', 'koʻngli tusamoq', 'en', 'hearts wished for', 'pair-cholpon-night-and-day'),
]


def norm(s):
    s = unicodedata.normalize('NFC', s).lower()
    for ch in ('‘', '’', 'ʼ', 'ʻ', '`', "'"):
        s = s.replace(ch, "'")
    return ' '.join(s.split())


def main():
    con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    books = {r['id']: r['title'] for r in con.execute('select id, title from books')}
    entries, errors = [], []
    for n, (cand, q_lang, q_span, a_lang, a_span, pair) in enumerate(REVIEWED, 1):
        occs = con.execute(
            'select * from collocation_occurrences where candidate_id = ? and is_verified = 1 order by id', (cand,)).fetchall()
        if not occs:
            errors.append(f'{cand}: verified occurrence yo\'q')
            continue
        q_field = 'matched_span_en' if q_lang == 'en' else 'matched_span_uz'
        a_field = 'matched_span_uz' if a_lang == 'uz' else 'matched_span_en'
        good = []
        for o in occs:
            # the Uzbek side is sometimes only stored on the confirmed annotation (source_span)
            q_vals = {norm(o[q_field])}
            q_vals |= {norm(r['source_span']) for r in con.execute(
                'select source_span from phd_annotations where occurrence_id = ? and is_confirmed = 1', (o['id'],))}
            if norm(q_span) in q_vals and norm(o[a_field]) == norm(a_span):
                good.append(o)
        if not good:
            errors.append(f'{cand}: DB da {q_span!r} -> {a_span!r} juftligi topilmadi')
            continue
        ann = con.execute(
            f"select annotator_user from phd_annotations where occurrence_id in ({','.join('?' * len(good))}) "
            "and is_confirmed = 1", [o['id'] for o in good]).fetchall()
        entries.append({
            'id': f'alt-{n:03d}',
            'query_lang': q_lang,
            'query': q_span,
            'alternative_lang': a_lang,
            'alternative': a_span,
            'candidate_id': cand,
            'pair_id': pair,
            'book': books.get(good[0]['book_id'], ''),
            'occurrence_ids': [o['id'] for o in good],
            'verified_by': sorted({r['annotator_user'] for r in ann}),
            'status': 'tasdiqlangan',
            'source': 'data/phd_corpus.db',
        })
    if errors:
        print('XATO, fayl yozilmadi:')
        for e in errors:
            print(' -', e)
        sys.exit(1)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f'{len(entries)} ta juftlik yozildi: {OUT}')


if __name__ == '__main__':
    main()
