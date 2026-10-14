with open('platform_factsheet.html', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('<tr><td>Matn Qatlamlari</td><td class="num">6 ta</td><td>5 ta faol, 1 ta karantinda (Stevenson)</td></tr>',
              '<tr><td>Matn Qatlamlari</td><td class="num">4 ta</td><td>4 ta faol ilmiy qatlam</td></tr>')
c = c.replace('Protected (Fair Use)', 'Cheklangan ilmiy parcha')
c = c.replace('<tr><td>Stevenson: «Treasure Island»</td><td>Original (en)</td><td class="num">142</td><td class="num">3,160</td><td class="num">69,676</td><td>Public Domain</td></tr>\n', '')
c = c.replace('<tr><td>Stevenson: «Xazinalar oroli» (Sharif Rizo)</td><td>Tarjima (uz)</td><td class="num">216</td><td class="num">0</td><td class="num">0</td><td class="badge-q">Karantinda (0 matn)</td></tr>\n', '')
with open('platform_factsheet.html', 'w', encoding='utf-8') as f:
    f.write(c)

with open('preview_alignment_queue.html', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('<option value="pair-stevenson-treasure-island" disabled>Stevenson: «Treasure Island» (EN ➔ UZ [Karantinda])</option>\n', '')
with open('preview_alignment_queue.html', 'w', encoding='utf-8') as f:
    f.write(c)

with open('sources_rights.html', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace("hamda xalqaro <em>Fair Use</em> me'yorlariga muvofiq,", "talablariga muvofiq,")
c = c.replace("'Fair Use (Ilmiy tadqiqot maqsadida)'", "'Mualliflik huquqi egalariga tegishli. Faqat ilmiy tadqiqot uchun cheklangan parcha.'")
with open('sources_rights.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Updated files successfully.')
