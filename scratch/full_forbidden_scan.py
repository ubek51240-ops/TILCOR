import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

forbidden_strings = [
    '0.95', '0.96', '2.14', 'Fair Use', 'Open Access', 'erkin ochiq', 
    'dissertationData', '5,157', '6,546', '6,533', '24,554', 'MI: 7.2', 
    'KORPUS.LINGVO', 'Cambridge / IELTS', 'plays a vital semantic role', 
    'undefined', 'Stivenson', 'Stevenson'
]

results = []
for root, dirs, files in os.walk('.'):
    if any(ig in root for ig in ['.git', 'venv', '__pycache__', 'backups', 'staging']):
        continue
    for f in files:
        if f.endswith(('.html', '.js', '.py', '.css', '.json', '.md')) and not f.startswith('find_') and f not in ['TILCOR_01.md', 'PROJECT_CONTEXT.md', 'AUDIT_REPORT.md']:
            p = os.path.join(root, f)
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                    lines = fl.readlines()
                for idx, line in enumerate(lines, 1):
                    for pat in forbidden_strings:
                        if pat.lower() in line.lower():
                            # Exception: Pearson in verified citation
                            if pat.lower() == 'pearson' and 'k. ackermann & y.-h. chen, pearson, 2013' in line.lower():
                                continue
                            results.append((p, idx, pat, line.strip()[:100]))
            except Exception:
                pass

print(f"Total forbidden occurrences found: {len(results)}")
for p, idx, pat, txt in results[:40]:
    print(f"  {p}:{idx} [{pat}] -> {txt}")
if len(results) > 40:
    print(f"  ... and {len(results)-40} more.")
