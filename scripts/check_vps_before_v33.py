#!/usr/bin/env python3
import sys
import paramiko

sys.stdout.reconfigure(encoding='utf-8')
HOST, USER, PASS = "189.74.100.111", "root", "AcL0hzLOh16zDoM$"

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd):
    _, o, e = c.exec_command(cmd)
    out = o.read().decode('utf-8', 'replace') + e.read().decode('utf-8', 'replace')
    return out.strip()

print("=== 1. Checking confirmed sentences on VPS ===")
cmd_1 = "python3 -c \"import json; d=json.load(open('/var/www/tilcor/data/full_corpus.json')); print('Tasdiqlangan:', sum(1 for r in d if r.get('status')=='tasdiqlangan'))\""
res_1 = run(cmd_1)
print(res_1)

c.close()
