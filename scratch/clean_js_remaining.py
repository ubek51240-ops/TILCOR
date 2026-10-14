with open('js/collocations_list.js', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('"Open Access (Ilmiy tadqiqot)"', '"Faqat ilmiy tadqiqot uchun cheklangan parcha"')
c = c.replace('Open Access', 'Faqat ilmiy tadqiqot uchun cheklangan parcha')
with open('js/collocations_list.js', 'w', encoding='utf-8') as f:
    f.write(c)

with open('js/corpus.js', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace("To'qima mahalliy namunalar va Stivenson butunlay olib tashlangan.", "To'qima namunalar butunlay olib tashlangan.")
with open('js/corpus.js', 'w', encoding='utf-8') as f:
    f.write(c)

with open('js/translator.js', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('KORPUS.LINGVO', 'TILCOR')
with open('js/translator.js', 'w', encoding='utf-8') as f:
    f.write(c)

with open('js/phd_hub.js', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('from Hemingway and Stevenson', 'from Hemingway')
c = c.replace('va Robert Luis Stivenson', '')
c = c.replace('va Stevenson', '')
c = c.replace('and Stevenson', '')
with open('js/phd_hub.js', 'w', encoding='utf-8') as f:
    f.write(c)

print('Cleaned JS files successfully.')
