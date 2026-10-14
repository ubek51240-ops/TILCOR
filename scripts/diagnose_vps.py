import os
import paramiko

HOST = "189.74.100.111"
USER = "root"
PASS = os.environ['TILCOR_VPS_PASSWORD']

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

cmds = [
    "ss -tlnp",
    "ps aux | grep -E 'python|nginx|gunicorn|uvicorn|tilcor'",
    "cat /etc/systemd/system/tilcor.service",
    "cat /etc/systemd/system/tilora.service",
    "cat /etc/nginx/sites-enabled/*",
    "curl -sI http://127.0.0.1:5050",
    "curl -sI http://127.0.0.1:8010",
    "curl -s 'http://127.0.0.1:5050/api/search?q=yurak' | head -c 200",
    "curl -s 'http://127.0.0.1:8010/api/search?q=yurak' | head -c 200"
]

for cmd in cmds:
    print(f"\n==================== CMD: {cmd} ====================")
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out:
        print(out)
    if err:
        print("[STDERR]", err)

client.close()
