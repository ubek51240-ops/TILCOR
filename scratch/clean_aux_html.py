with open('kwic_concordance.html', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('<option value="book-stevenson-en">Stevenson: «Treasure Island» (EN)</option>', '')
with open('kwic_concordance.html', 'w', encoding='utf-8') as f:
    f.write(c)

with open('preview_alignment_queue.html', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('<option value="pair-stevenson-treasure-island" disabled>Stevenson: «Treasure Island» (EN ➔ UZ, Karantinda)</option>', '')
with open('preview_alignment_queue.html', 'w', encoding='utf-8') as f:
    f.write(c)

with open('sources_rights.html', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('Fair Use & Ilmiy Maqsadlar', 'Qonuniy Asos & Cheklangan Ilmiy Maqsadlar')
c = c.replace('(Fair Use & Ilmiy Maqsadlar)', '(Ilmiy tadqiqot uchun cheklangan parcha)')
c = c.replace('Fair Use / Ilmiy Tadqiqot', 'Cheklangan Ilmiy Parsha')
c = c.replace('t.licence_status || "Fair Use"', 't.licence_status || "Cheklangan ilmiy parcha"')
with open('sources_rights.html', 'w', encoding='utf-8') as f:
    f.write(c)

with open('platform_factsheet.html', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('3 ta</td><td>Cho‘lpon, Hemingway, Stevenson', '2 ta</td><td>Cho‘lpon, Hemingway')
c = c.replace('5 ta faol, 1 ta karantinda (Stevenson)', '4 ta faol ilmiy qatlam')
c = c.replace('6,546 ta', '6,537 ta')
c = c.replace('Fair Use (Ilmiy tadqiqot)', 'Cheklangan ilmiy parcha')
c = c.replace('<tr><td>Stevenson: «Treasure Island»</td><td>Original (en)</td><td class="num">142</td><td>43,770</td><td>Publikatsiyada (Public Domain)</td></tr>', '')
c = c.replace('<tr><td>Stevenson: «Xazinalar oroli» (Sharif Rizo)</td><td>Tarjima (uz)</td><td class="num">0*</td><td>—</td><td class="karantin">KARANTIN (faqat skaner rasm)</td></tr>', '')
with open('platform_factsheet.html', 'w', encoding='utf-8') as f:
    f.write(c)

with open('methodology.html', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('asarlar (Stivenson)', 'matnlar')
with open('methodology.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Cleaned auxiliary HTML files successfully.')
