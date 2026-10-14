import re

t = open('index.html', encoding='utf-8').read()

cards = [
    ('corpus', 'Korpusni ochish', '/korpus', 'btn_open_corpus', 'indigo'),
    ('collocations', 'Kollokatsiyalarni ko‘rish', '/kollokatsiyalar', 'btn_view_collocations', 'emerald'),
    ('dictionary', 'Lug‘atni ochish', '/lugat', 'btn_open_dictionary', 'amber'),
]
for tab, label, href, key, c in cards:
    pat = r"""<button onclick="app\.switchTab\('""" + tab + r"""'\)"[^>]*>\s*""" + re.escape(label) + r'.*?</button>'
    new = (f'<a href="{href}" class="w-full py-2 rounded-xl bg-{c}-50 dark:bg-{c}-950 text-{c}-700 dark:text-{c}-300 '
           f'font-bold text-xs hover:bg-{c}-600 hover:text-white transition flex items-center justify-center gap-1.5" '
           f'data-i18n="{key}">{label} <i data-lucide="arrow-right" class="w-3 h-3"></i></a>')
    t, n = re.subn(pat, lambda m: new, t, flags=re.S)
    print(tab, n)

books = [
    ('cholpon', 'Ushbu romandan qidirish →', 'btn_search_novel', '/qidiruv?kitob=kvk'),
    ('hemingway', 'Ushbu qissadan qidirish →', 'btn_search_novella', '/qidiruv?kitob=oms'),
]
for book, label, key, href in books:
    pat = r"""<button onclick="app\.switchTab\('corpus'\); corpusManager\.filterByBook\('""" + book + r"""'\);"[^>]*>\s*""" + re.escape(label) + r'\s*</button>'
    new = f'<a href="{href}" class="mt-3 text-xs text-indigo-600 font-semibold hover:underline flex items-center gap-1" data-i18n="{key}">{label}</a>'
    t, n = re.subn(pat, lambda m: new, t, flags=re.S)
    print(book, n)

pat = r'<a href="methodology\.html"[^>]*>\s*<span>Metodologiya sahifasiga o‘tish</span>.*?</a>'
new = ('<a href="/methodology.html" class="inline-flex items-center gap-1.5 font-bold text-indigo-600 dark:text-indigo-400 '
       'hover:underline shrink-0" data-i18n="btn_go_methodology">Metodologiya sahifasiga o‘tish '
       '<i data-lucide="arrow-right" class="w-3.5 h-3.5"></i></a>')
t, n = re.subn(pat, lambda m: new, t, flags=re.S)
print('methodology', n)

open('index.html', 'w', encoding='utf-8').write(t)
