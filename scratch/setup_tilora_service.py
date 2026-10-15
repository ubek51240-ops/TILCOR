import os
import sys, paramiko
sys.stdout.reconfigure(encoding='utf-8')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('189.74.100.111', 22, 'root', os.environ.get("TILCOR_VPS_PASSWORD", ""))

service_content = """[Unit]
Description=TILORA Adaptiv Ta'lim Veb-Platformasi (FastAPI + Uvicorn)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/tilora
ExecStart=/var/www/tilora/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8010 --workers 2
Restart=always
RestartSec=3
Environment=PYTHONPATH=/var/www/tilora/backend
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"""

nginx_content = """# TILORA (tilora.uz)
server {
    listen 80;
    listen [::]:80;
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
with sftp.open('/etc/systemd/system/tilora.service', 'w') as f:
    f.write(service_content)

with sftp.open('/etc/nginx/sites-available/tilora_and_tilcor', 'w') as f:
    f.write(nginx_content)
sftp.close()

cmds = """
rm -f /etc/nginx/sites-enabled/*
ln -sf /etc/nginx/sites-available/tilora_and_tilcor /etc/nginx/sites-enabled/
nginx -t
systemctl daemon-reload
systemctl enable tilora
systemctl restart tilora
systemctl restart tilcor
systemctl restart nginx
sleep 2
systemctl is-active tilora
systemctl is-active tilcor
systemctl is-active nginx
"""

_, o, e = client.exec_command(cmds)
print('STDOUT:\n', o.read().decode('utf-8'))
print('STDERR:\n', e.read().decode('utf-8'))

client.close()
