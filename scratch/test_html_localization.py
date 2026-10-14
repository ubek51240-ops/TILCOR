import sys
sys.path.insert(0, '.')
from server import render_localized_html

raw = open('index.html', encoding='utf-8').read()
en_html = render_localized_html(raw, lang='en', is_admin=False)
ru_html = render_localized_html(raw, lang='ru', is_admin=False)
print('EN html length:', len(en_html))
print('RU html length:', len(ru_html))
assert 'lang="en"' in en_html, 'lang="en" missing'
assert 'lang="ru"' in ru_html, 'lang="ru" missing'
assert 'hreflang="en"' in en_html, 'hreflang="en" missing'
assert 'nav-laboratoriya' not in en_html, 'Admin menu must be omitted for logged-out visitors!'
assert 'nav-laboratoriya-mobile' not in en_html, 'Admin mobile menu must be omitted!'
assert 'Ibrohim G‘afurov' not in en_html, 'G‘afurov must be replaced with G‘ofurov!'
print('HTML Localization rendering tests PASSED!')
