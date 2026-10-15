#!/usr/bin/env python3
"""
scripts/deploy_v3_to_vps.py - Full deployment of TILCOR v3 to VPS per DEPLOY_v3_UZ.md
"""
import os
import sys
import time
import paramiko

sys.stdout.reconfigure(encoding='utf-8')
HOST, USER, PASS = "189.74.100.111", "root", os.environ.get("TILCOR_VPS_PASSWORD", "")
LOCAL_ZIP = r"C:\Users\user\Downloads\Telegram Desktop\tilcor_v3_2026-10-14.zip"
REMOTE_ZIP = "/tmp/tilcor_v3_2026-10-14.zip"

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
print("\n[*] 1. Uploading zip file to VPS /tmp...")
sftp = c.open_sftp()
sftp.put(LOCAL_ZIP, REMOTE_ZIP)
sftp.close()
print("[+] Zip uploaded successfully!")

# 2. Backup on VPS
print("\n[*] 2. Creating full backup of /var/www/tilcor...")
run("ts=$(date +%Y%m%d_%H%M%S); mkdir -p /root/tilcor_backups && tar -czf /root/tilcor_backups/tilcor_before_v3_$ts.tar.gz -C /var/www tilcor && ls -lh /root/tilcor_backups/tilcor_before_v3_$ts.tar.gz")

# 3. Unzip and sync
print("\n[*] 3. Extracting and syncing v3 files to /var/www/tilcor...")
cmd_extract = """
rm -rf /tmp/tilcor_v3 && mkdir -p /tmp/tilcor_v3
python3 -c "import zipfile; zipfile.ZipFile('/tmp/tilcor_v3_2026-10-14.zip').extractall('/tmp/tilcor_v3')"
rsync -a /tmp/tilcor_v3/ /var/www/tilcor/
find /var/www/tilcor -name "__pycache__" -type d -prune -exec rm -rf {} +
"""
run(cmd_extract)

# 4. Check admin password in secrets
print("\n[*] 4. Checking / creating secrets/admin.password...")
cmd_secrets = """
mkdir -p /var/www/tilcor/secrets
if [ ! -f /var/www/tilcor/secrets/admin.password ]; then
    python3 -c "import secrets; print(secrets.token_urlsafe(18))" > /var/www/tilcor/secrets/admin.password
    chmod 700 /var/www/tilcor/secrets
    chmod 600 /var/www/tilcor/secrets/admin.password
    echo "Created new admin.password"
else
    echo "admin.password already exists"
fi
"""
run(cmd_secrets)

# 5. Compile check
print("\n[*] 5. Verifying Python compilation...")
run("cd /var/www/tilcor && python3 -m py_compile server.py ui_components.py content_pages.py equivalents.py search_plus.py search_engine.py && echo 'COMPILE OK'")

# 6. Restart tilcor
print("\n[*] 6. Restarting tilcor.service...")
run("systemctl restart tilcor && sleep 6 && systemctl is-active tilcor")

# 7. Check status and log
print("\n[*] 7. Checking systemd logs...")
run("journalctl -u tilcor -n 35 --no-pager")

c.close()
print("\n[*] Deployment script completed!")
