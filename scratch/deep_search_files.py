import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

search_roots = [
    r'C:\Users\user\Desktop',
    r'C:\Users\user\Downloads',
    r'C:\Users\user\Documents'
]

print("=== SEARCHING FOR FILES MENTIONING KECHA / KUNDUZ / ANNOTATION / 535 ===")

interesting_files = []
for sroot in search_roots:
    for root, dirs, files in os.walk(sroot):
        # skip virtualenvs and node_modules
        if any(x in root.lower() for x in ['node_modules', '.git', 'venv', 'myenv', 'site-packages', 'appdata']):
            continue
        for f in files:
            fl = f.lower()
            if any(k in fl for k in ['kecha', 'kunduz', 'cholpon', 'annotat', 'gold', 'parallel', 'juft']):
                p = os.path.join(root, f)
                interesting_files.append((p, os.path.getsize(p)))

for p, sz in interesting_files:
    print(f"{p} ({sz:,} bytes)")

