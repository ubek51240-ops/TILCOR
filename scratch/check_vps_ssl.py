import paramiko

HOST = "189.74.100.111"
USER = "root"
PASS = "AcL0hzLOh16zDoM$"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

cmds = [
    "cat /etc/nginx/sites-available/tilora_and_tilcor",
    "ls -la /etc/nginx/sites-enabled",
    "ls -la /etc/letsencrypt/live || true",
    "curl -I http://tilcor.uz || true",
    "curl -I -k https://tilcor.uz || true"
]

for cmd in cmds:
    print(f"\n--- {cmd} ---")
    stdin, stdout, stderr = client.exec_command(cmd)
    print(stdout.read().decode('utf-8', errors='replace'))
    err = stderr.read().decode('utf-8', errors='replace')
    if err:
        print("[ERR]", err)

client.close()
