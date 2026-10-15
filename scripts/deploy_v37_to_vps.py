#!/usr/bin/env python3
"""scripts/deploy_v37_to_vps.py — TILCOR v3.6+v3.7 ni VPS ga joylash.

Tartib DEPLOY_v3.6_UZ.md va DEPLOY_v3.7_UZ.md bo'yicha:
zaxira -> yuklash -> rsync (--delete YO'Q) -> kompilyatsiya -> restart -> tekshiruvlar.
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
ZIP_NAME = "tilcor_v3.7_2026-10-15.zip"
LOCAL_ZIP = os.path.join(LOCAL_DIR, "backups", ZIP_NAME)
REMOTE_ZIP = f"/tmp/{ZIP_NAME}"

EXCLUDE_DIRS = {'backups', 'scratch', 'staging', 'sources', '.git', '__pycache__', 'secrets', '.system_generated'}
EXCLUDE_EXT = {'.pyc', '.zip', '.log'}


def build_zip():
    print(f"[*] Arxiv tuzilmoqda: {LOCAL_ZIP}")
    n = 0
    with zipfile.ZipFile(LOCAL_ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(LOCAL_DIR):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for f in files:
                if os.path.splitext(f)[1].lower() in EXCLUDE_EXT:
                    continue
                p = os.path.join(root, f)
                rel = os.path.relpath(p, LOCAL_DIR).replace('\\', '/')
                z.write(p, rel)
                n += 1
    print(f"[+] {n} ta fayl, {os.path.getsize(LOCAL_ZIP)/1e6:.1f} MB")


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
        print(f"[!] DIQQAT: VPS da tasdiqlangan juftliklar {gate} ta (15 kutilgan edi). Davom etilmoqda, "
              "lekin tadqiqotchiga xabar bering.")

    # 1. Zaxira
    run("ts=$(date +%Y%m%d_%H%M%S); mkdir -p /root/tilcor_backups && "
        "tar -czf /root/tilcor_backups/tilcor_before_v37_$ts.tar.gz -C /var/www tilcor && "
        "ls -lh /root/tilcor_backups/ | tail -3")

    # 2. Yuklash
    print(f"\n[*] Arxiv yuklanmoqda ({os.path.getsize(LOCAL_ZIP)/1e6:.1f} MB)...")
    sftp = c.open_sftp()
    sftp.put(LOCAL_ZIP, REMOTE_ZIP)
    sftp.close()
    print("[+] Yuklandi.")

    # 3. Ochish va sinxronlash (--delete YO'Q: secrets/, sources/, baholar saqlanadi)
    run(f"rm -rf /tmp/tilcor_v37 && mkdir -p /tmp/tilcor_v37 && "
        f"python3 -c \"import zipfile; zipfile.ZipFile('{REMOTE_ZIP}').extractall('/tmp/tilcor_v37')\" && "
        f"rsync -a /tmp/tilcor_v37/ /var/www/tilcor/ && "
        f"find /var/www/tilcor -name __pycache__ -type d -prune -exec rm -rf {{}} + && echo SYNC_OK")

    # 4. Kompilyatsiya
    run("cd /var/www/tilcor && python3 -m py_compile server.py ui_components.py content_pages.py "
        "search_engine.py search_plus.py suggest.py corpus_dictionary.py analysis.py validation.py "
        "validation_pages.py && echo COMPILE_OK")

    # 5. Restart
    run("systemctl restart tilcor && sleep 6 && systemctl is-active tilcor")
    run("journalctl -u tilcor -n 20 --no-pager | grep -E 'korpus yuklandi|not loaded|Error|Traceback' || echo LOG_TOZA")

    # 6. Tekshiruvlar
    run("B=https://tilcor.uz; for u in /server.py /suggest.py /data/full_corpus.json /secrets/admin.password /.git/config; do "
        "echo \"$u (404 kerak): $(curl -s -o /dev/null -w '%{http_code}' $B$u)\"; done")
    run("B=https://tilcor.uz; for u in '/?lang=uz' '/?lang=en' '/?lang=ru' /lugat '/lugat?q=yurak' '/qidiruv?q=yurak' "
        "'/kwic?q=yurak' /kollokatsiyalar /metodologiya /statistika '/css/tilcor.css?v=3.7'; do "
        "echo \"$u : $(curl -s -o /dev/null -w '%{http_code}' \"$B$u\")\"; done")
    run("curl -s 'https://tilcor.uz/api/suggest?q=yura' | head -c 200; echo")
    run("curl -s 'https://tilcor.uz/qidiruv?q=yurok' | grep -c 'nazarda tutdingizmi' || true")
    run("curl -s 'https://tilcor.uz/' | grep -c 'tc-ac' || true")
    run("curl -s 'https://tilcor.uz/qidiruv?q=yurak' | grep -c 'Million so' || true")

    c.close()
    print("\n[✓] v3.7 joylash yakunlandi.")


if __name__ == '__main__':
    main()
