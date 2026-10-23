#!/usr/bin/env python3
"""scripts/deploy_colloc_alt_to_vps.py — tekshirilgan kollokatsiya muqobillarini VPS ga joylash.

Faqat quyidagi fayllar yuboriladi (ishchi papkadagi boshqa o'zgarishlar yuborilmaydi):
search_plus.py, ui_components.py, data/collocation_alternatives.json, scripts/build_collocation_alternatives.py

Tartib: zaxira -> yuklash -> rsync (--delete YO'Q) -> kompilyatsiya -> restart -> tekshiruvlar.
Parol kodda saqlanmaydi: TILCOR_VPS_PASSWORD muhit o'zgaruvchisidan olinadi.
"""
import os
import sys
import zipfile
import paramiko

sys.stdout.reconfigure(encoding='utf-8')

HOST = os.environ.get("TILCOR_VPS_HOST", "189.74.100.111")
USER = os.environ.get("TILCOR_VPS_USER", "root")
PASS = os.environ.get("TILCOR_VPS_PASSWORD", "")
if not PASS:
    sys.exit("[!] TILCOR_VPS_PASSWORD muhit o'zgaruvchisi berilmagan.")

LOCAL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_NAME = "tilcor_colloc_alt_2026-10-23.zip"
LOCAL_ZIP = os.path.join(LOCAL_DIR, "backups", ZIP_NAME)
REMOTE_ZIP = f"/tmp/{ZIP_NAME}"

FILES = [
    "search_plus.py",
    "ui_components.py",
    "data/collocation_alternatives.json",
    "scripts/build_collocation_alternatives.py",
]


def build_zip():
    print(f"[*] Arxiv tuzilmoqda: {LOCAL_ZIP}")
    with zipfile.ZipFile(LOCAL_ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
        for rel in FILES:
            p = os.path.join(LOCAL_DIR, *rel.split('/'))
            if not os.path.isfile(p):
                sys.exit(f"[!] fayl topilmadi: {rel}")
            z.write(p, rel)
    print(f"[+] {len(FILES)} ta fayl, {os.path.getsize(LOCAL_ZIP)/1e3:.1f} KB")


def main():
    build_zip()

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

    # 0. Darvoza: VPS dagi tasdiqlangan juftliklar soni
    gate = run("python3 -c \"import json; d=json.load(open('/var/www/tilcor/data/full_corpus.json')); "
               "print(sum(1 for r in d if r.get('status')=='tasdiqlangan'))\"")
    if gate.strip() not in ('15', ''):
        print(f"[!] DIQQAT: VPS da tasdiqlangan juftliklar {gate} ta (15 kutilgan edi). Davom etilmoqda.")

    # 1. Zaxira
    run("ts=$(date +%Y%m%d_%H%M%S); mkdir -p /root/tilcor_backups && "
        "tar -czf /root/tilcor_backups/tilcor_before_colloc_alt_$ts.tar.gz -C /var/www tilcor && "
        "ls -lh /root/tilcor_backups/ | tail -3")

    # 2. Yuklash
    print(f"\n[*] Arxiv yuklanmoqda ({os.path.getsize(LOCAL_ZIP)/1e3:.1f} KB)...")
    sftp = c.open_sftp()
    sftp.put(LOCAL_ZIP, REMOTE_ZIP)
    sftp.close()
    print("[+] Yuklandi.")

    # 3. Ochish va sinxronlash (--delete YO'Q)
    run(f"rm -rf /tmp/tilcor_colloc && mkdir -p /tmp/tilcor_colloc && "
        f"python3 -c \"import zipfile; zipfile.ZipFile('{REMOTE_ZIP}').extractall('/tmp/tilcor_colloc')\" && "
        f"rsync -a /tmp/tilcor_colloc/ /var/www/tilcor/ && "
        f"find /var/www/tilcor -name __pycache__ -type d -prune -exec rm -rf {{}} + && echo SYNC_OK")

    # 4. Kompilyatsiya
    run("cd /var/www/tilcor && python3 -m py_compile search_plus.py ui_components.py && echo COMPILE_OK")

    # 5. Restart
    run("systemctl restart tilcor && sleep 6 && systemctl is-active tilcor")
    run("journalctl -u tilcor -n 20 --no-pager | grep -E 'not loaded|Error|Traceback' || echo LOG_TOZA")

    # 6. Tekshiruvlar
    run("B=https://tilcor.uz; for u in '/?lang=uz' '/?lang=en' '/qidiruv?q=yurak' '/kollokatsiyalar' '/statistika'; do "
        "echo \"$u : $(curl -s -o /dev/null -w '%{http_code}' \"$B$u\")\"; done")
    run("curl -s 'https://tilcor.uz/qidiruv?q=fished+alone' | grep -c 'baliq ovlardi' || true")
    run("curl -s 'https://tilcor.uz/qidiruv?q=deep+wrinkles' | grep -c 'chuqur ajinlar' || true")
    run("curl -s 'https://tilcor.uz/qidiruv?q=fish' | grep -c 'Tekshirilgan muqobillar' || true")
    c.close()
    print("\n[✓] Kollokatsiya muqobillari joylash yakunlandi.")


if __name__ == '__main__':
    main()
