import paramiko

HOST = "189.74.100.111"
USER = "root"
PASS = "AcL0hzLOh16zDoM$"

def make_public():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS, timeout=15)
    
    # 1. Update tilcor server.py to not require password
    sftp = client.open_sftp()
    with sftp.open('/var/www/tilcor/server.py', 'r') as f:
        content = f.read().decode('utf-8')
    
    old_code = "    def require_auth(self, role=None):\n        user = self.get_authenticated_user()"
    new_code = "    def require_auth(self, role=None):\n        return 'admin'\n        user = self.get_authenticated_user()"
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        with sftp.open('/var/www/tilcor/server.py', 'w') as f:
            f.write(content.encode('utf-8'))
        print("tilcor server.py auth disabled successfully!")
    else:
        print("Already updated or pattern not found.")
        
    sftp.close()
    
    # 2. Restart tilcor
    stdin, stdout, stderr = client.exec_command('systemctl restart tilcor && systemctl is-active tilcor')
    print("tilcor service status:", stdout.read().decode('utf-8').strip())
    
    client.close()

if __name__ == '__main__':
    make_public()
