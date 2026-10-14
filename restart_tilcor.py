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

# Ensure socketserver.TCPServer.allow_reuse_address is TRUE at top and in class
fix_code = """
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

"""
if "class ThreadedTCPServer" not in text:
    text = text.replace("import socketserver", "import socketserver" + fix_code)

# Replace TCPServer usage
text = text.replace("socketserver.TCPServer.allow_reuse_address = True", "")
text = text.replace("with socketserver.TCPServer((\"\", port), AppRequestHandler) as httpd:", "httpd = ThreadedTCPServer((\"\", port), AppRequestHandler)\n    with httpd:")
text = text.replace("with socketserver.TCPServer(('', port), AppRequestHandler) as httpd:", "httpd = ThreadedTCPServer((\"\", port), AppRequestHandler)\n    with httpd:")

with sftp.open('/var/www/tilcor/server.py', 'w') as f:
    f.write(text.encode('utf-8'))

sftp.close()

# Stop, kill port, restart
cmds = [
    "systemctl stop tilcor",
    "fuser -k 5050/tcp 2>/dev/null || true",
    "sleep 1",
    "systemctl start tilcor",
    "sleep 3",
    "systemctl is-active tilcor",
    "curl -I http://127.0.0.1:5050"
]

for cmd in cmds:
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    print(f"[{cmd}] -> {out}")

client.close()
