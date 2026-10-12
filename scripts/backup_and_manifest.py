import os
import sys
import hashlib
import shutil
import datetime
import json

base_dir = r'C:\Users\user\Desktop\tarjimon'
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
backup_root = os.path.join(base_dir, 'backups')
os.makedirs(backup_root, exist_ok=True)
backup_dir = os.path.join(backup_root, f'backup_{timestamp}')
os.makedirs(backup_dir, exist_ok=True)

manifest = {
    'created_at': datetime.datetime.now().isoformat(),
    'source_directory': base_dir,
    'backup_directory': backup_dir,
    'files': []
}

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

items_to_backup = ['data', 'js', 'css', 'server.py', 'index.html']
for item in items_to_backup:
    src = os.path.join(base_dir, item)
    dst = os.path.join(backup_dir, item)
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    elif os.path.isfile(src):
        shutil.copy2(src, dst)

external_sources = [
    r'C:\Users\user\Downloads\Telegram Desktop\cholpon-kecha-va-kunduz.pdf',
    r'C:\Users\user\Downloads\Telegram Desktop\night-and-day-a-novel-9781644690482_compress-pages.pdf',
    r'C:\Users\user\Downloads\Telegram Desktop\Chol va dengiz ( Ernst).pdf',
    r'C:\Users\user\Downloads\Telegram Desktop\oldmansea.pdf',
    r'C:\Users\user\Downloads\Telegram Desktop\inglizcha-ozbekcha_lugat.pdf',
    r'C:\Users\user\Downloads\80-000-dictionary.pdf',
    r'C:\Users\user\Downloads\Collocations in Use Intermediate [www.languagecentre.ir].pdf',
    r'C:\Users\user\Downloads\1000-english-collocations-ebook.pdf',
    r'C:\Users\user\Downloads\English Collocation in Use 2nd Edition-Advanced.pdf',
    r'C:\Users\user\Downloads\IELTS-academic-collocations-list.pdf'
]

pdf_manifest = []
for p in external_sources:
    if os.path.exists(p):
        pdf_manifest.append({
            'path': p,
            'filename': os.path.basename(p),
            'size': os.path.getsize(p),
            'sha256': sha256_file(p)
        })

for root, dirs, files in os.walk(backup_dir):
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, backup_dir)
        manifest['files'].append({
            'rel_path': rel,
            'size': os.path.getsize(full),
            'sha256': sha256_file(full)
        })

manifest['source_pdfs'] = pdf_manifest

manifest_path = os.path.join(backup_dir, 'manifest.json')
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"BACKUP_SUCCESS: {backup_dir}")
print(f"TOTAL_BACKED_UP_FILES: {len(manifest['files'])}")
print(f"SOURCE_PDFS_RECORDED: {len(pdf_manifest)}")
