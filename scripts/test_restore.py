import os
import sys
import shutil
import tempfile
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
latest_backup = sorted([os.path.join(backup_root, d) for d in os.listdir(backup_root) if os.path.isdir(os.path.join(backup_root, d))])[-1]

with tempfile.TemporaryDirectory() as temp_dir:
    # Simulate restore
    print(f"Testing restore into sandbox: {temp_dir}")
    manifest_path = os.path.join(latest_backup, 'manifest.json')
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    # Copy files
    for item in os.listdir(latest_backup):
        if item == 'manifest.json':
            continue
        s = os.path.join(latest_backup, item)
        d = os.path.join(temp_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

    # Verify checksums in restored sandbox
    restored_ok = 0
    for f_info in manifest['files']:
        restored_file = os.path.join(temp_dir, f_info['rel_path'])
        assert os.path.exists(restored_file), f"File {f_info['rel_path']} missing in restore!"
        assert sha256_file(restored_file) == f_info['sha256'], f"Checksum mismatch in {f_info['rel_path']}!"
        restored_ok += 1

    print(f"RESTORE_TEST_SUCCESS: All {restored_ok} files restored and verified with zero discrepancy.")
