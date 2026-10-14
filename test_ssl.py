import os
import paramiko

HOST = "189.74.100.111"
USER = "root"
PASS = os.environ['TILCOR_VPS_PASSWORD']

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

stdin, stdout, stderr = client.exec_command("curl -k -s -o /dev/null -w '%{http_code}' https://127.0.0.1 -H 'Host: tilora.uz'")
code = stdout.read().decode('utf-8').strip()
print("TILORA LOCAL HTTPS STATUS CODE:", code)

client.close()
