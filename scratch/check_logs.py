import os
import sys, paramiko
sys.stdout.reconfigure(encoding='utf-8')
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('189.74.100.111', 22, 'root', os.environ.get("TILCOR_VPS_PASSWORD", ""))
_, o, _ = client.exec_command('tail -n 15 /var/log/nginx/access.log\necho "--- ERROR ---"\ntail -n 15 /var/log/nginx/error.log')
print(o.read().decode('utf-8'))
client.close()
