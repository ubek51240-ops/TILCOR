"""Lokal zaxira: loyiha papkasini (backups/, scratch/, staging/, sources/, .git, secrets/ dan tashqari) zip qiladi."""
import os, sys, zipfile, datetime
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tag = sys.argv[1] if len(sys.argv) > 1 else 'v39'
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
out = os.path.join(root, 'backups', f'local_pre_{tag}_{ts}.zip')
EXCLUDE_DIRS = {'backups', 'scratch', 'staging', 'sources', '.git', '__pycache__', 'secrets', '.system_generated', '.claude'}
EXCLUDE_EXT = {'.pyc', '.zip', '.log'}
n = 0
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if os.path.splitext(f)[1].lower() in EXCLUDE_EXT:
                continue
            p = os.path.join(r, f)
            z.write(p, os.path.relpath(p, root).replace('\\', '/'))
            n += 1
print(out, n, 'files', round(os.path.getsize(out) / 1e6, 1), 'MB')
