import sys
sys.path.insert(0, '.')
import re, html
import server

with open('kwic_concordance.html', 'r', encoding='utf-8') as f:
    raw_html = f.read()

kw_res = server.get_phd_kwic({'q': ['yurak']})
results = kw_res.get('results', [])
print('Results length:', len(results))

rows_html = []
for k in results:
    rows_html.append(
        f'<tr>'
        f'<td class="kwic-left" style="text-align:right;">{html.escape(k.get("left", ""))}</td>'
        f'<td class="kwic-node" style="text-align:center; font-weight:700; color:#1e40af;">{html.escape(k.get("node", ""))}</td>'
        f'<td class="kwic-right" style="text-align:left;">{html.escape(k.get("right", ""))}</td>'
        f'<td class="kwic-meta" style="text-align:center;"><div><b>{html.escape(k.get("book_title", ""))}</b></div><div>p. {html.escape(str(k.get("page", "")))}</div></td>'
        f'</tr>'
    )
table_body = ''.join(rows_html)
match1 = re.search(r'<tbody[^>]*id=["\']kwicTableBody["\'][^>]*>.*?</tbody>', raw_html, flags=re.DOTALL)
print('Match in raw_html:', bool(match1))
new_html = re.sub(r'<tbody[^>]*id=["\']kwicTableBody["\'][^>]*>.*?</tbody>', f'<tbody id="kwicTableBody">{table_body}</tbody>', raw_html, flags=re.DOTALL)
print('<tr> in new_html:', new_html.count('<tr'))
rendered = server.render_localized_html(new_html, 'uz', False, {'q': ['yurak']}, req_path='/kwic_concordance.html')
print('<tr> in rendered:', rendered.count('<tr'))
