import os
import paramiko

HOST = "189.74.100.111"
USER = "root"
PASS = os.environ['TILCOR_VPS_PASSWORD']

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

sftp = client.open_sftp()
with sftp.open('/var/www/tilcor/server.py', 'r') as f:
    text = f.read().decode('utf-8')

# Replace socketserver.TCPServer with socketserver.ThreadingTCPServer
old_server_class = "class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):\n    daemon_threads = True\n    allow_reuse_address = True\n"
if "ThreadingTCPServer" not in text:
    text = text.replace(
        "socketserver.TCPServer.allow_reuse_address = True",
        "class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):\n        daemon_threads = True\n        allow_reuse_address = True"
    )
    text = text.replace(
        "with socketserver.TCPServer(('', port), AppRequestHandler) as httpd:",
        "with ThreadedTCPServer(('', port), AppRequestHandler) as httpd:"
    )
    with sftp.open('/var/www/tilcor/server.py', 'w') as f:
        f.write(text.encode('utf-8'))
    print("SUCCESS: server.py upgraded to Multi-Threaded TCP Server!")
else:
    print("ALREADY THREADED")

sftp.close()

stdin, stdout, stderr = client.exec_command('systemctl restart tilcor && sleep 1 && systemctl is-active tilcor')
print("TILCOR SERVICE ACTIVE:", stdout.read().decode('utf-8').strip())

# Test request
stdin, stdout, stderr = client.exec_command('curl -s -o /dev/null -w "%{http_code}" https://tilcor.uz')
print("TILCOR HTTPS HTTP CODE:", stdout.read().decode('utf-8').strip())

client.close()
