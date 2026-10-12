import paramiko

HOST = "189.74.100.111"
USER = "root"
PASS = "AcL0hzLOh16zDoM$"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

nginx_conf = """# ==========================================
# 1. TILORA (tilora.uz & www.tilora.uz) -> Port 8010
# ==========================================
server {
    listen 80;
    listen [::]:80;
    listen 8080;
    server_name tilora.uz www.tilora.uz;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8010;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# ==========================================
# 2. TILCOR (tilcor.uz & Default IP) -> Port 5050
# ==========================================
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name tilcor.uz www.tilcor.uz _;

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
with sftp.open('/etc/nginx/sites-available/tilora_and_tilcor', 'w') as f:
    f.write(nginx_conf.encode('utf-8'))
sftp.close()

stdin, stdout, stderr = client.exec_command('nginx -t && systemctl restart nginx')
print("NGINX TEST & RESTART:")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

client.close()
