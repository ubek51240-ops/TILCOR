import os
import sys
import json
import hashlib

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

backup_root = r'C:\Users\user\Desktop\tarjimon\backups'
backups = [os.path.join(backup_root, d) for d in os.listdir(backup_root) if os.path.isdir(os.path.join(backup_root, d))]
if not backups:
    print('ERROR: No backups found!')
    sys.exit(1)

latest_backup = sorted(backups)[-1]
manifest_file = os.path.join(latest_backup, 'manifest.json')

if not os.path.exists(manifest_file):
    print(f'ERROR: manifest.json not found in {latest_backup}')
    sys.exit(1)

with open(manifest_file, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

verified = 0
failed = 0
for f_info in manifest['files']:
    f_path = os.path.join(latest_backup, f_info['rel_path'])
    if not os.path.exists(f_path):
        print(f"MISSING: {f_info['rel_path']}")
        failed += 1
        continue
    actual_hash = sha256_file(f_path)
    if actual_hash == f_info['sha256']:
        verified += 1
    else:
        print(f"CORRUPTED: {f_info['rel_path']}")
        failed += 1

print(f"BACKUP VERIFICATION REPORT:")
print(f"Backup target: {latest_backup}")
print(f"Files verified: {verified}/{len(manifest['files'])}")
print(f"Failed files: {failed}")
if failed == 0:
    print("STATUS: 100% VERIFIED AND INTACT")
else:
    print("STATUS: VERIFICATION FAILED")
