import os
import paramiko

HOST = "189.74.100.111"
USER = "root"
PASS = os.environ['TILCOR_VPS_PASSWORD']

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

cmds = [
    "ls -la /var/www",
    "grep -rn 'ayvon' /var/www/",
    "grep -rn '2 471' /var/www/",
    "find /etc/nginx -type f -exec grep -H 'tilcor' {} +",
    "find /etc/nginx -type f -exec grep -H 'proxy_pass' {} +",
    "history | tail -n 50"
]

for cmd in cmds:
    print(f"\n==================== CMD: {cmd} ====================")
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out:
        print(out[:2000])
    if err:
        print("[STDERR]", err[:1000])

client.close()
