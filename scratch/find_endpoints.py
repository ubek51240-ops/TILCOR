import re

with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

endpoints = set()
for line in text.splitlines():
    m = re.search(r'path(?:\.startswith|\s*==)\s*\(?[\'"](/api[^\'"]*)[\'"]', line)
    if m:
        endpoints.add(m.group(1))

print('Server API endpoints:')
for ep in sorted(endpoints):
    print(' ', ep)
