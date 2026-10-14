with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace("<!-- Badiiy Korpus Pasporti (Faqat Cho'lpon va Hemingway, Stevenson yo'q!) -->", 
              "<!-- Badiiy Korpus Pasporti (Faqat Cho'lpon va Hemingway) -->")
c = c.replace("<!-- VIEW 3: PARALLEL CORPUS (5,157 JUMLALIK CONCORDANCE) -->", 
              "<!-- VIEW 3: PARALLEL CORPUS -->")
c = c.replace("Choʻlpon, Xeminguey va Stivenson asarlari korpusi asosida diagrammalar", 
              "Choʻlpon va Hemingway asarlari korpusi asosida diagrammalar")
c = c.replace("Choʻlpon, Stivenson va Xeminguey ulushi", "Asarlar ulushi")
c = c.replace('data-i18n-uz="5,157 parallel jumla va 6,533 ta ilmiy birikma tahlil qilinib, MI Score ≥ 3.0 va T-Score ≥ 2.0 filtrlash algoritmi yordamida oʻzaro faol birikuvchilik darajasi hisoblab chiqildi."',
              'data-i18n-uz="Parallel jumlalar va ilmiy birikmalar tahlil qilinib, oʻzaro birikuvchilik darajasi va tarjima ekvivalentligi hisoblab chiqildi."')
c = c.replace('5,157 parallel jumla va 6,533 ta ilmiy birikma tahlil qilinib, MI Score ≥ 3.0 va T-Score ≥ 2.0 filtrlash algoritmi yordamida oʻzaro faol birikuvchilik darajasi hisoblab chiqildi.',
              'Parallel jumlalar va ilmiy birikmalar tahlil qilinib, oʻzaro birikuvchilik darajasi va tarjima ekvivalentligi hisoblab chiqildi.')
c = c.replace('data-i18n-en="Analyzed 5,157 parallel sentences and 6,533 academic collocations, calculating association strength using MI Score ≥ 3.0 and T-Score ≥ 2.0 filtering algorithms."',
              'data-i18n-en="Analyzed parallel sentences and academic collocations, calculating association strength and translation equivalence."')
c = c.replace('(Choʻlpon, Hemingway, Stevenson)', '(Choʻlpon, Hemingway)')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Cleaned index.html completely.')
