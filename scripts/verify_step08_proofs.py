import urllib.request, ssl
ctx = ssl._create_unverified_context()

def get(url):
    return urllib.request.urlopen(url, context=ctx).read().decode('utf-8', 'replace')

p1 = get('https://tilcor.uz/?lang=en').count('ni ochish')
p2 = get('https://tilcor.uz/').count('admin_collocations')
p3_text = get('https://tilcor.uz/qidiruv?q=yurak')
p3 = 'yuragi' in p3_text
p4 = get('https://tilcor.uz/kwic_concordance.html?q=yurak').count('<tr')

print(f'curl -s "https://tilcor.uz/?lang=en" | grep -c "ni ochish" -> {p1}')
print(f'curl -s "https://tilcor.uz/" | grep -c "admin_collocations" -> {p2}')
print(f'curl -s "https://tilcor.uz/qidiruv?q=yurak" contains "yuragi" -> {p3}')
print(f'curl -s "https://tilcor.uz/kwic_concordance.html?q=yurak" tr count -> {p4} (> 40 rows: {p4 > 40})')
