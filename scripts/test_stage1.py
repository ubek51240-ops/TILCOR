"""Stage 1 check (TILCOR_08 tasks 1-3). Usage: python scripts/test_stage1.py <base_url>"""
import sys, re, ssl, urllib.request, urllib.parse

sys.stdout.reconfigure(encoding='utf-8')
BASE = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else 'https://tilcor.uz'
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

PAGES = ['/', '/qidiruv?q=yurak', '/qidiruv?q=heart', '/qidiruv?q=' + urllib.parse.quote('og‘ir uyqu'),
         '/korpus', '/kollokatsiyalar', '/lugat', '/kwic_concordance.html?q=yurak', '/methodology.html',
         '/methodology_statistics.html', '/sources_rights.html', '/kirish', '/soz/yurak', '/soz/heart',
         '/kollokatsiya/' + urllib.parse.quote('og‘ir uyqu')]
ADMIN = ['admin_collocations', 'preview_alignment_queue', 'Jonli Tarjimon', 'PhD Hub', 'sinovchisi', 'Stage', 'reviewer', 'guest']
HYB_CYR = re.compile(r'[А-Яа-яЁё]+[A-Za-z‘ʻ]+')
HYB_EN = re.compile(r'\b(Corpus|Collocations?|Dictionary|Methodology|Analysis|Translation|Statistics|Confirmed|Sources)(ni|ning|dan|ga|da|lar|dagi|si)\b')

def get(path):
    url = BASE + path
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'tilcor-test'}), context=CTX, timeout=60) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception as e:
        return 0, str(e)

def with_lang(p, l):
    return p + ('&' if '?' in p else '?') + 'lang=' + l

def nav_block(h):
    m = re.search(r'<!-- UNIFIED TOP NAVIGATION -->.*?</header>', h, re.S)
    return m.group(0) if m else ''

print(f'Base: {BASE}')
print(f'{"page":45} {"lang":4} {"http":4} {"admin":5} {"hybrid":6} {"nav":3} {"#href":5}')
total = 0
nav_links = set()
for p in PAGES:
    for l in ('uz', 'en', 'ru'):
        code, h = get(with_lang(p, l))
        adm = sum(h.count(t) for t in ADMIN)
        text = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', h, flags=re.S)
        text = re.sub(r'<[^>]*class="[^"]*corpus-text[^"]*"[^>]*>.*?</[^>]+>', ' ', text, flags=re.S)
        text = re.sub(r'<[^>]+>', ' ', text)
        hyb = (len(HYB_CYR.findall(text)) + len(HYB_EN.findall(text))) if l != 'uz' else 0
        nb = nav_block(h)
        has_nav = 1 if nb else 0
        bad_href = len(re.findall(r'href=["\'](#|)["\']', nb))
        for href in re.findall(r'href="([^"]+)"', nb):
            nav_links.add(href.split('&lang=')[0].split('?lang=')[0] or '/')
        v = (code != 200) + adm + hyb + (1 - has_nav) + bad_href
        total += v
        print(f'{urllib.parse.unquote(p)[:45]:45} {l:4} {code:4} {adm:5} {hyb:6} {has_nav:3} {bad_href:5}')

print('\nNav links check:')
for href in sorted(nav_links):
    code, _ = get(href)
    if code != 200:
        total += 1
    print(f'  {code}  {href}')

print('\nProof curls:')
_, h = get('/?lang=en'); print('  /?lang=en  "ni ochish":', h.count('ni ochish'))
_, h = get('/?lang=ru'); print('  /?lang=ru  "ni ochish":', h.count('ni ochish'))
_, h = get('/'); print('  /  "admin_collocations":', h.count('admin_collocations'))
print(f'\nTOTAL VIOLATIONS: {total}')
