import sys, paramiko
sys.stdout.reconfigure(encoding='utf-8')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('189.74.100.111', 22, 'root', 'AcL0hzLOh16zDoM$')

cmds = """
cd /var/www/tilora
export PYTHONPATH=/var/www/tilora/backend
/var/www/tilora/venv/bin/python3 -c "from app.main import app; print('TILORA IMPORT OK!')"
"""

_, o, e = client.exec_command(cmds)
print('STDOUT:\n', o.read().decode('utf-8'))
print('STDERR:\n', e.read().decode('utf-8'))
client.close()
