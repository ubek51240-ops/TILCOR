with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
start = text.find('id="view-collocations"')
end = text.find('id="view-checker"')
print(f"view-collocations block: characters {start} to {end}")
sub = text[start:end]
for line in sub.splitlines():
    l_strip = line.strip()
    if 'id=' in l_strip or '<h' in l_strip or '<button' in l_strip:
        print(' ', l_strip[:100])
