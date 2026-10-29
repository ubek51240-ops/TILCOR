#!/usr/bin/env python3
"""scripts/verify_v39_pages.py — v3.9 (teglash) sahifalari va API ning tekshiruvi.

Foydalanish: python scripts/verify_v39_pages.py http://127.0.0.1:8791   (lokal)
             python scripts/verify_v39_pages.py https://tilcor.uz       (jonli sayt)
Har bir yo‘l uchun HTTP kodi va kutilgan matn parchalari tekshiriladi; maxfiy yo‘llar 404 bo‘lishi shart.
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
B = (sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8791').rstrip('/')


def get(path):
    t = time.time()
    try:
        r = urllib.request.urlopen(B + path, timeout=60)
        return r.status, r.read().decode('utf-8', 'replace'), time.time() - t
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace'), time.time() - t


CHECKS = [
    ('/qidiruv?q=yurak', ['Teglar (avtomatik)', 'tc-badge--amber', 'yurak</span> + -i', 'egalik, III shaxs', 'Morfologiya']),
    ('/qidiruv?q=yurak&lang=en', ['Tags (automatic)', 'Automatic tag', 'Morphology', 'Person[psor]=3']),
    ('/qidiruv?q=yurak&lang=ru', ['Теги (автоматические)', 'Морфология', 'существительное']),
    ('/qidiruv?q=heart', ['Teglar (avtomatik)', 'noun.cognition', 'Nutqiy va aqliy faoliyat']),
    ('/qidiruv?q=' + urllib.parse.quote('javob bermoq'), ['Teglar (avtomatik)', 'bermoq</span></td>']),
    ('/qidiruv?q=' + urllib.parse.quote('og‘ir uyqu'), ['Teglar (avtomatik)']),
    ('/kollokatsiya/uz-2d594a3d8a', ['Teglar (avtomatik)', 'javob', 'bermoq</span></td>', 'berdi = bermoq + -di']),
    ('/kollokatsiya/en-92df8fc4e3', ['Teglar (avtomatik)', 'asos', 'kollokat', 'Ijtimoiy-madaniy munosabatlar', 'noun.person']),
    ('/kollokatsiya/en-92df8fc4e3?lang=en', ['Tags (automatic)', 'base', 'collocate', 'Social and cultural relations']),
    ('/kollokatsiyalar', ['guruhlar', 'Barcha semantik guruhlar', 'Semantik guruh (3.1)']),
    ('/kollokatsiyalar?til=uz&guruh=inson_ruhiyati', ['aria-current="true">Inson his-tuyg']),
    ('/kollokatsiyalar?til=en&guruh=tabiat_borliq&qolip=adjective+%2B+noun', ['Tabiat va atrof-muhit']),
    ('/kollokatsiyalar?guruh=xxx', ['Barcha semantik guruhlar']),
    ('/soz/yurak', ['Teglar (avtomatik)', 'TILCOR, versiya 3.9']),
    ('/api/tags?q=qishlog%E2%80%98idan', ['"lemma": "qishloq"', 'chiqish kelishigi']),
    ('/api/tags?q=hearts', ['"lemma": "heart"', 'Number=Plur']),
    ('/api/tags?q=yuraklarida&til=uz', ['Case=Loc']),
    ('/?lang=uz', ['TILCOR']),
    ('/tagging.py', None), ('/data/tags_index.json', None), ('/server.py', None), ('/scripts/build_tags_index.py', None),
]


def main():
    bad = 0
    for path, needles in CHECKS:
        st, body, dt = get(path)
        if needles is None:
            ok = st == 404
            print('%s %-70s %d (%.2fs) 404 kerak' % ('OK  ' if ok else 'XATO', path, st, dt))
        else:
            missing = [n for n in needles if n not in body]
            ok = st == 200 and not missing
            print('%s %-70s %d (%.2fs)%s' % ('OK  ' if ok else 'XATO', path, st, dt, (' yo‘q: ' + repr(missing)) if missing else ''))
        bad += not ok
    st, body, _ = get('/api/tags?q=yuraklarida&til=uz')
    try:
        w = json.loads(body)['words'][0]
        print('api/tags yuraklarida ->', w['lemma'], w['pos'], [m['affix'] for m in w['morphs']], w['ud'], (w.get('sem') or {}).get('group'))
    except Exception as e:
        print('api/tags JSON xatosi:', e)
        bad += 1
    print('\nJAMI:', 'HAMMASI OK' if not bad else '%d ta XATO' % bad)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
