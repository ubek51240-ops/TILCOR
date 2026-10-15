import os
#!/usr/bin/env python3
"""
scripts/check_vps_before_v3.py - Runs pre-deployment checks on VPS per DEPLOY_v3_UZ.md
"""
import sys
import paramiko

sys.stdout.reconfigure(encoding='utf-8')
HOST, USER, PASS = "189.74.100.111", "root", os.environ.get("TILCOR_VPS_PASSWORD", "")

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd):
    _, o, e = c.exec_command(cmd)
    out = o.read().decode('utf-8', 'replace') + e.read().decode('utf-8', 'replace')
    return out.strip()

print("=== 1a. Confirmed count in full_corpus.json ===")
cmd_1a = "python3 -c \"import json; d=json.load(open('/var/www/tilcor/data/full_corpus.json')); print(sum(1 for r in d if r.get('status')=='tasdiqlangan'))\""
res_1a = run(cmd_1a)
print("Confirmed count:", res_1a)

print("\n=== 1b. Memory / Swap ===")
print(run("free -m"))

print("\n=== 1c. Python version ===")
print(run("python3 --version"))

print("\n=== Secrets check ===")
print(run("ls -la /var/www/tilcor/secrets/ 2>/dev/null || echo NO_SECRETS_DIR"))

print("\n=== Nginx headers check ===")
print(run("cat /etc/nginx/sites-enabled/* | grep -E 'proxy_set_header'"))

c.close()
