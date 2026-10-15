#!/usr/bin/env python3
"""
scripts/merge_v36_local.py - Merges v3.6 into local codebase C:\\Users\\user\\Desktop\\tarjimon
"""
import os
import sys
import zipfile
import shutil
import time

sys.stdout.reconfigure(encoding='utf-8')

LOCAL_DIR = r"C:\Users\user\Desktop\tarjimon"
ZIP_V36 = r"C:\Users\user\Downloads\Telegram Desktop\tilcor_v3.6_2026-10-14-1.zip"

# 1. Local backup
ts = time.strftime('%Y%m%d_%H%M%S')
backup_zip = os.path.join(LOCAL_DIR, "backups", f"local_pre_v36_{ts}.zip")
os.makedirs(os.path.join(LOCAL_DIR, "backups"), exist_ok=True)
print(f"[*] 1. Creating local backup: {backup_zip} ...")

ignore = {'.git', 'backups', '__pycache__', 'venv', '.idea', '.vscode', '.system_generated'}
with zipfile.ZipFile(backup_zip, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(LOCAL_DIR):
        dirs[:] = [d for d in dirs if d not in ignore]
        for f in files:
            if f.endswith(('.pyc', '.zip', '.tar.gz')):
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, LOCAL_DIR)
            z.write(full_path, rel_path)

print(f"[+] Backup created: {os.path.getsize(backup_zip)} bytes")

# 2. Extract v3.6
print(f"\n[*] 2. Merging v3.6 into {LOCAL_DIR} ...")
with zipfile.ZipFile(ZIP_V36, 'r') as z:
    z.extractall(LOCAL_DIR)
print("[+] v3.6 merged successfully!")

# 3. Remove any __pycache__
for root, dirs, files in os.walk(LOCAL_DIR):
    if '__pycache__' in dirs:
        shutil.rmtree(os.path.join(root, '__pycache__'))

print("\n[*] All local files updated to v3.6!")
