import paramiko
import os
import sys

HOST = "189.74.100.111"
USER = "root"
PASS = "AcL0hzLOh16zDoM$"

def run():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOST}...")
    client.connect(HOST, username=USER, password=PASS, timeout=15)
    print("Connected successfully!")

    commands = [
        "ls -la /var/www/tilcor",
        "ls -la /var/www/tilora",
        "systemctl status tilcor --no-pager",
        "systemctl status tilora --no-pager",
        "systemctl status nginx --no-pager",
        "curl -I http://127.0.0.1:5050",
        "curl -I http://127.0.0.1:8010"
    ]

    for cmd in commands:
        print(f"\n--- RUNNING: {cmd} ---")
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='replace')
        err = stderr.read().decode('utf-8', errors='replace')
        if out:
            print(out.strip())
        if err:
            print("[ERR]", err.strip())

    client.close()

if __name__ == '__main__':
    run()
