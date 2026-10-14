import os
import sys
import paramiko

HOST = "189.74.100.111"
USER = "root"
PASS = os.environ['TILCOR_VPS_PASSWORD']

TARJIMON_LOCAL = r"C:\Users\user\Desktop\tarjimon"
TILORA_LOCAL = r"C:\Users\user\Desktop\TILORA"

TARJIMON_REMOTE = "/var/www/tilcor"
TILORA_REMOTE = "/var/www/tilora"

def sync_dir(sftp, local_dir, remote_dir, ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = {'.git', '__pycache__', 'venv', '.idea', '.vscode', 'backups', 'scratch', '.system_generated'}
    
    try:
        sftp.stat(remote_dir)
    except FileNotFoundError:
        print(f"Creating remote dir {remote_dir}")
        sftp.mkdir(remote_dir)

    for root, dirs, files in os.walk(local_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        rel_path = os.path.relpath(root, local_dir).replace('\\', '/')
        if rel_path == '.':
            current_remote_dir = remote_dir
        else:
            current_remote_dir = f"{remote_dir}/{rel_path}"

        try:
            sftp.stat(current_remote_dir)
        except FileNotFoundError:
            # make dirs incrementally
            parts = current_remote_dir.split('/')
            cur = ""
            for p in parts:
                if not p: continue
                cur += "/" + p
                try:
                    sftp.stat(cur)
                except FileNotFoundError:
                    sftp.mkdir(cur)

        for f in files:
            if f.endswith('.pyc') or f.endswith('.log'):
                continue
            local_file = os.path.join(root, f)
            remote_file = f"{current_remote_dir}/{f}"
            
            # Check if exists and size/time differs
            need_upload = True
            try:
                r_stat = sftp.stat(remote_file)
                l_stat = os.stat(local_file)
                if r_stat.st_size == l_stat.st_size:
                    need_upload = False
            except FileNotFoundError:
                need_upload = True
                
            if need_upload:
                print(f"Uploading {local_file} -> {remote_file}...")
                sftp.put(local_file, remote_file)

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOST} via SSH...")
    client.connect(HOST, username=USER, password=PASS, timeout=20)
    print("SSH bog'landi!")

    sftp = client.open_sftp()
    
    print("\n>>> 1. TILCOR (tarjimon) fayllarini serverga sinxronizatsiya qilish...")
    sync_dir(sftp, TARJIMON_LOCAL, TARJIMON_REMOTE)
    print("TILCOR fayllari serverga yuklandi!")

    print("\n>>> 2. TILORA fayllarini serverga sinxronizatsiya qilish...")
    sync_dir(sftp, TILORA_LOCAL, TILORA_REMOTE)
    print("TILORA fayllari serverga yuklandi!")

    sftp.close()

    print("\n>>> 3. Serverdagi xizmatlarni qayta yuklash (restart)...")
    commands = [
        "systemctl restart tilcor",
        "systemctl restart tilora",
        "systemctl restart nginx",
        "systemctl is-active tilcor",
        "systemctl is-active tilora",
        "systemctl is-active nginx"
    ]

    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        print(f"[{cmd}] -> {out if out else 'OK'}")
        if err:
            print(f"  [ERR] {err}")

    client.close()
    print("\n==============================================")
    print("HAMMASI MUVAFFAQIN SERVERGA YUKLANDI VA ISHGA TUSHIRILDI!")
    print("==============================================")

if __name__ == '__main__':
    main()
