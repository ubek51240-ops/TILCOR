import re

with open('index.html', 'r', encoding='utf-8') as f:
    s = f.read()

m = re.search(r'<div[^>]*id=["\']nav-laboratoriya["\'][^>]*>.*?</div>\s*</div>', s, flags=re.DOTALL)
print('Matched:', bool(m))
if m:
    print('Match len:', len(m.group(0)))
    print('End snippet:', repr(m.group(0)[-100:]))
else:
    print('NOT MATCHED!')
