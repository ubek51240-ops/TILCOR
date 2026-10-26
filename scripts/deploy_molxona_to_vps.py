#!/usr/bin/env python3
"""scripts/deploy_molxona_to_vps.py — Molxona kollokatsiyalari va manbalarini VPS ga joylash.

Yuklanadigan fayllar:
- data/collocations_full.json (356 ta tasdiqlangan, public_visible=True kollokatsiyalar bilan)
- sources/Molxona_kollokatsiyalar.pdf
- sources/Animal_Farm_kollokatsiyalar.pdf
- sources/Molxona_kollokatsiyalar_parallel_korpusi.docx
- content_pages.py
- ui_components.py
- server.py

Tartib: tekshiruv -> zaxira -> yuklash -> restart -> tekshiruv.
Parol kodda saqlanmaydi: TILCOR_VPS_PASSWORD muhit o'zgaruvchisidan olinadi.
"""
import hashlib
import os
import sys
import paramiko

sys.stdout.reconfigure(encoding='utf-8')

HOST = os.environ.get("TILCOR_VPS_HOST", "189.74.100.111")
USER = os.environ.get("TILCOR_VPS_USER", "root")
PASS = os.environ.get("TILCOR_VPS_PASSWORD", "")
if not PASS:
    sys.exit("[!] TILCOR_VPS_PASSWORD muhit o'zgaruvchisi berilmagan. Iltimos: $env:TILCOR_VPS_PASSWORD='...' ni kiriting.")

LOCAL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES_TO_SYNC = [
    "data/collocations_full.json",
    "sources/Molxona_kollokatsiyalar.pdf",
    "sources/Animal_Farm_kollokatsiyalar.pdf",
    "sources/Molxona_kollokatsiyalar_parallel_korpusi.docx",
    "content_pages.py",
    "ui_components.py",
    "server.py",
]

def main():
    print(f"[*] {HOST} ga ulanish...")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, username=USER, password=PASS, timeout=30)

    def run(cmd, timeout=300):
        print(f"\n[RUN] {cmd.strip().splitlines()[0][:90]} ...")
        _, o, e = c.exec_command(cmd, timeout=timeout)
        out = o.read().decode('utf-8', 'replace') + e.read().decode('utf-8', 'replace')
        res = out.strip()
        if res:
            print(res)
        return res

    # 1. Zaxira
    run("ts=$(date +%Y%m%d_%H%M%S); mkdir -p /root/tilcor_backups && "
        "cp /var/www/tilcor/data/collocations_full.json /root/tilcor_backups/collocations_full_before_molxona_$ts.json && "
        "ls -lh /root/tilcor_backups/ | tail -2")

    # 2. Yuklash
    sftp = c.open_sftp()
    run("mkdir -p /var/www/tilcor/sources /var/www/tilcor/data")
    for rel in FILES_TO_SYNC:
        loc = os.path.join(LOCAL_DIR, *rel.split('/'))
        rem = f"/var/www/tilcor/{rel}"
        rem_tmp = f"/tmp/{os.path.basename(rel)}"
        print(f"[*] Yuklanmoqda: {rel} ({os.path.getsize(loc)} bayt)...")
        sftp.put(loc, rem_tmp)
        run(f"mv {rem_tmp} {rem} && echo OK_{os.path.basename(rel)}")
    sftp.close()

    # 3. Restart va tekshiruv
    run("systemctl restart tilcor && sleep 6 && systemctl is-active tilcor")
    run("journalctl -u tilcor -n 20 --no-pager | grep -E 'Error|Traceback' || echo LOG_TOZA")
    run("python3 -c \"import json; d=json.load(open('/var/www/tilcor/data/collocations_full.json')); "
        "mol=[r for r in d if str(r.get('id','')).startswith('col-mol-')]; "
        "print('Jami kollokatsiyalar:', len(d), 'Molxona:', len(mol), 'Public:', sum(1 for r in mol if r.get('public_visible')))\"")
    run("B=https://tilcor.uz; for u in '/?lang=uz' '/kollokatsiyalar?manba=malumotnoma' '/api/stats'; do "
        "echo \"$u : $(curl -s -o /dev/null -w '%{http_code}' \"$B$u\")\"; done")
    c.close()
    print("\n[✓] Molxona kollokatsiyalari va manbalari VPS ga muvaffaqiyatli joylandi!")

if __name__ == '__main__':
    main()
