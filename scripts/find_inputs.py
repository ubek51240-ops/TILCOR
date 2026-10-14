import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

ids = re.findall(r'id=["\']([^"\']+)["\']', text)
search_ids = [i for i in ids if 'search' in i.lower()]
print('Search IDs in index.html:', search_ids)

# Check buttons or tabs
tab_ids = [i for i in ids if 'tab' in i.lower() or 'nav' in i.lower() or 'corpus' in i.lower()]
print('Tab/Corpus IDs in index.html:', tab_ids)
