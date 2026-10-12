import sys, paramiko
sys.stdout.reconfigure(encoding='utf-8')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('189.74.100.111', 22, 'root', 'AcL0hzLOh16zDoM$')

nginx_content = """# TILORA (tilora.uz) - HTTP & HTTPS
server {
    listen 80;
    listen [::]:80;
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name tilora.uz;

    ssl_certificate /etc/nginx/ssl/tilora.crt;
    ssl_certificate_key /etc/nginx/ssl/tilora.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8010;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# TILCOR (Default IP / Fallback)
server {
    listen 80 default_server;
    listen [::]:80 default_server;
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
with sftp.open('/etc/nginx/sites-available/tilora_and_tilcor', 'w') as f:
    f.write(nginx_content)
sftp.close()

cmds = """
mkdir -p /etc/nginx/ssl
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/tilora.key \
  -out /etc/nginx/ssl/tilora.crt \
  -subj "/CN=tilora.uz"
nginx -t
systemctl restart nginx
sleep 1
ss -tulpn | grep 443
"""

_, o, e = client.exec_command(cmds)
print('STDOUT:\n', o.read().decode('utf-8'))
print('STDERR:\n', e.read().decode('utf-8'))

client.close()
