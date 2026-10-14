import os
import paramiko

HOST = "189.74.100.111"
USER = "root"
PASS = os.environ['TILCOR_VPS_PASSWORD']

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
    return 301 https://tilora.uz$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name tilora.uz www.tilora.uz;

    ssl_certificate /etc/letsencrypt/live/tilora.uz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tilora.uz/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8010;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect http:// https://;
    }
}

# ==========================================
# 2. TILCOR (tilcor.uz & Default IP) -> Port 5050
# ==========================================
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name tilcor.uz www.tilcor.uz _;
    return 301 https://tilcor.uz$request_uri;
}

server {
    listen 443 ssl default_server;
    listen [::]:443 ssl default_server;
    server_name tilcor.uz www.tilcor.uz _;

    ssl_certificate /etc/letsencrypt/live/tilcor.uz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tilcor.uz/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:5050;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect http:// https://;
    }
}
"""

sftp = client.open_sftp()
with sftp.open('/etc/nginx/sites-available/tilora_and_tilcor', 'w') as f:
    f.write(nginx_conf.encode('utf-8'))
sftp.close()

stdin, stdout, stderr = client.exec_command('nginx -t && systemctl restart nginx')
print("NGINX TEST & RESTART:")
print("STDOUT:", stdout.read().decode('utf-8'))
print("STDERR:", stderr.read().decode('utf-8'))

client.close()
