import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

views = re.findall(r'id=["\'](view-[^"\']+)["\']', text)
navs = re.findall(r'data-view=["\']([^"\']+)["\']', text)
print('Views found in index.html:', views)
print('Navigation targets in index.html:', sorted(list(set(navs))))
