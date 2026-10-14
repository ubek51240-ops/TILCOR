import os
import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('189.74.100.111', username=os.environ.get('TILCOR_VPS_USER', 'root'), password=os.environ['TILCOR_VPS_PASSWORD'])

cmd = """python3 -c "
import urllib.request
h = urllib.request.urlopen('http://127.0.0.1:5050/kwic_concordance.html?q=yurak').read().decode('utf-8')
print('Matches kwicTableBody:', 'kwicTableBody' in h)
print('<tr> count:', h.count('<tr'))
print('Sample body slice:')
idx = h.find('kwicTableBody')
print(h[idx:idx+400] if idx != -1 else 'not found')
"
"""
_, o, e = c.exec_command(cmd)
print(o.read().decode('utf-8'))
print("ERR:", e.read().decode('utf-8'))
c.close()
