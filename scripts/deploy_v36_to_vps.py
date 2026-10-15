#!/usr/bin/env python3
"""
scripts/deploy_v36_to_vps.py - Full deployment of TILCOR v3.6 to VPS per DEPLOY_v3.6_UZ.md
"""
import os
import sys
import time
import paramiko

sys.stdout.reconfigure(encoding='utf-8')
HOST, USER, PASS = "189.74.100.111", "root", os.environ.get("TILCOR_VPS_PASSWORD", "")
LOCAL_ZIP = r"C:\Users\user\Downloads\Telegram Desktop\tilcor_v3.6_2026-10-14-1.zip"
REMOTE_ZIP = "/tmp/tilcor_v3.6_2026-10-14.zip"

print(f"[*] Connecting to {HOST} via SSH...")
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=30)

def run(cmd, timeout=180):
    print(f"\n[RUN] {cmd}")
    _, o, e = c.exec_command(cmd, timeout=timeout)
    out = o.read().decode('utf-8', 'replace') + e.read().decode('utf-8', 'replace')
    res = out.strip()
    if res:
        print(res)
    return res

# 1. Upload zip to /tmp
print("\n[*] 1. Uploading v3.6 zip to VPS /tmp...")
sftp = c.open_sftp()
sftp.put(LOCAL_ZIP, REMOTE_ZIP)
sftp.close()
print("[+] v3.6 zip uploaded successfully!")

# 2. Backup on VPS
print("\n[*] 2. Creating full backup of /var/www/tilcor...")
run("ts=$(date +%Y%m%d_%H%M%S); mkdir -p /root/tilcor_backups && tar -czf /root/tilcor_backups/tilcor_before_v36_$ts.tar.gz -C /var/www tilcor && ls -lh /root/tilcor_backups/tilcor_before_v36_$ts.tar.gz")

# 3. Unzip and sync
print("\n[*] 3. Extracting and syncing v3.6 files to /var/www/tilcor...")
cmd_extract = """
rm -rf /tmp/tilcor_v36 && mkdir -p /tmp/tilcor_v36
python3 -c "import zipfile; zipfile.ZipFile('/tmp/tilcor_v3.6_2026-10-14.zip').extractall('/tmp/tilcor_v36')"
rsync -a /tmp/tilcor_v36/ /var/www/tilcor/
find /var/www/tilcor -name "__pycache__" -type d -prune -exec rm -rf {} +
"""
run(cmd_extract)

# 4. Compile check
print("\n[*] 4. Verifying Python compilation...")
run("cd /var/www/tilcor && python3 -m py_compile server.py ui_components.py content_pages.py equivalents.py search_plus.py search_engine.py analysis.py validation.py validation_pages.py corpus_dictionary.py suggest.py && echo 'COMPILE OK'")

# 5. Restart tilcor
print("\n[*] 5. Restarting tilcor.service...")
run("systemctl restart tilcor && sleep 6 && systemctl is-active tilcor")

# 6. Check logs
print("\n[*] 6. Checking systemd logs...")
run("journalctl -u tilcor -n 40 --no-pager")

c.close()
print("\n[*] Deployment script for v3.6 completed!")
