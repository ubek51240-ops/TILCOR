with open('js/app.js', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('KORPUS.LINGVO', 'TILCOR')
with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(c)

with open('js/collocations.js', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('6,533', '6,537')
with open('js/collocations.js', 'w', encoding='utf-8') as f:
    f.write(c)

with open('js/phd_hub.js', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('KORPUS.LINGVO', 'TILCOR')
c = c.replace('5,157', '3,811')
c = c.replace('6,546', '6,537')
c = c.replace('6,533', '6,537')
c = c.replace('va R.L.Stevensonning «Treasure Island» asarlari', 'asari')
c = c.replace('and Stevenson’s Treasure Island', '')
c = c.replace('va Robert Luis Stivensonning «Xazinalar oroli»', '')
c = c.replace(', Stevenson', '')
c = c.replace('(Stevenson)', '(Badiiy)')
c = c.replace(', and Stevenson’s Treasure Island', '')
with open('js/phd_hub.js', 'w', encoding='utf-8') as f:
    f.write(c)

print('Sanitized JS files successfully.')
