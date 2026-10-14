import re

with open('server.py', encoding='utf-8') as f:
    text = f.read()

routes = sorted(set(re.findall(r"parsed\.path\s*==\s*['\"](/api[^'\"]+)['\"]", text)))
for r in routes:
    print(r)
