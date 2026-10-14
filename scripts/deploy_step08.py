import os
"""Targeted deploy for TILCOR_08 Stage 1: uploads only the changed files, backs up remote copies, restarts tilcor."""
import sys, time, paramiko

sys.stdout.reconfigure(encoding='utf-8')
HOST, USER, PASS = "189.74.100.111", "root", os.environ['TILCOR_VPS_PASSWORD']
LOCAL = r"C:\Users\user\Desktop\tarjimon"
REMOTE = "/var/www/tilcor"
FILES = sys.argv[1:] or ['server.py', 'ui_components.py', 'citation_pages.py', 'index.html', 'kirish.html',
                         'sources_rights.html', 'kwic_concordance.html', 'methodology_statistics.html',
                         'locales/uz.json', 'locales/en.json', 'locales/ru.json', 'PROJECT_CONTEXT.md']

c = paramiko.SSHClient(); c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username=USER, password=PASS, timeout=20)

def run(cmd):
    _, o, e = c.exec_command(cmd, timeout=120)
    out = o.read().decode('utf-8', 'replace') + e.read().decode('utf-8', 'replace')
    return out.strip()

ts = time.strftime('%Y%m%d_%H%M%S')
bdir = f"/root/tilcor_backups/step08_{ts}"
print(run(f"mkdir -p {bdir}/locales && cd {REMOTE} && for f in {' '.join(FILES)}; do [ -f $f ] && cp --parents $f {bdir}/; done; echo backup:{bdir}"))

sftp = c.open_sftp()
for f in FILES:
    sftp.put(f"{LOCAL}\\{f.replace('/', chr(92))}", f"{REMOTE}/{f}")
    print("uploaded", f)
sftp.close()

print(run(f"cd {REMOTE} && python3 -m py_compile server.py ui_components.py citation_pages.py && echo compile-ok"))
print(run("systemctl restart tilcor && sleep 4 && systemctl is-active tilcor && systemctl is-active nginx"))
print(run("journalctl -u tilcor -n 8 --no-pager"))
c.close()
