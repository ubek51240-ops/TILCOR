import sys, paramiko, threading, time, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('189.74.100.111', 22, 'root', 'AcL0hzLOh16zDoM$')

def trigger():
    time.sleep(2)
    try:
        print("Sending request to https://tilora.uz ...")
        urllib.request.urlopen('https://tilora.uz', timeout=5)
    except Exception as e:
        print("Request finished:", e)

t = threading.Thread(target=trigger)
t.start()

_, o, _ = client.exec_command('timeout 6 tcpdump -i any -n "port 443 or port 80" -c 10')
print('TCPDUMP OUTPUT:\n', o.read().decode('utf-8'))
t.join()
client.close()
