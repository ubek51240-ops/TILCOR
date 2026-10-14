import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

for fname in ['js/collocations.js', 'js/dictionary.js', 'js/app.js', 'index.html']:
    with open(fname, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for idx, l in enumerate(lines, 1):
        for pattern in ['6,546', '6,533', '5,157', '24,554', 'MI: 7.2', '2.14', '0.95', '0.96', 'Stevenson', 'Stivenson', 'KORPUS.LINGVO', 'Cambridge / IELTS', 'plays a vital semantic role', 'dissertationData']:
            if pattern.lower() in l.lower():
                print(f"{fname}:{idx}: [{pattern}] -> {l.strip()[:120]}")
