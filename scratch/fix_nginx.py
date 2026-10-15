import os
import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("189.74.100.111", 22, "root", os.environ.get("TILCOR_VPS_PASSWORD", ""))

nginx_content = """server {
    listen 80;
    server_name _;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:5050;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""

sftp = client.open_sftp()
with sftp.open("/etc/nginx/sites-available/tilcor", "w") as f:
    f.write(nginx_content)
sftp.close()

stdin, stdout, stderr = client.exec_command("""
nginx -t && systemctl restart nginx && systemctl status nginx --no-pager && systemctl status tilcor --no-pager
""")
print("OUT:\n", stdout.read().decode("utf-8", errors="replace"))
print("ERR:\n", stderr.read().decode("utf-8", errors="replace"))
client.close()
