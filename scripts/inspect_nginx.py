import os
import paramiko

HOST = "189.74.100.111"
USER = "root"
PASS = os.environ['TILCOR_VPS_PASSWORD']

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

cmds = [
    "ls -la /etc/nginx/sites-enabled",
    "cat /etc/nginx/sites-available/tilcor",
    "nginx -T",
    "find /var/cache/nginx -type f"
]

for cmd in cmds:
    print(f"\n=== CMD: {cmd} ===")
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out:
        print(out)
    if err:
        print("[STDERR]", err)

client.close()
