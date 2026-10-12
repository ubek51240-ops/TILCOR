import py_compile, os, glob, json, sqlite3

print("=== 1. TESTING PYTHON SYNTAX IN TARJIMON ===")
for f in glob.glob(r"C:\Users\user\Desktop\tarjimon\*.py"):
    try:
        py_compile.compile(f, doraise=True)
        print(f"[OK] {os.path.basename(f)}")
    except Exception as e:
        print(f"[ERROR] {os.path.basename(f)}: {e}")

print("\n=== 2. TESTING DATA INTEGRITY IN TARJIMON ===")
data_dir = r"C:\Users\user\Desktop\tarjimon\data"
for jf in ["full_corpus.json", "dictionary.json", "collocations_full.json"]:
    p = os.path.join(data_dir, jf)
    try:
        with open(p, "r", encoding="utf-8") as fp:
            d = json.load(fp)
            print(f"[OK] {jf}: {len(d)} records loaded successfully")
    except Exception as e:
        print(f"[ERROR] {jf}: {e}")

for db in ["corpus.db", "phd_corpus.db"]:
    p = os.path.join(data_dir, db)
    try:
        conn = sqlite3.connect(p)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        cnt = cur.fetchone()[0]
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        print(f"[OK] {db}: {cnt} tables ({', '.join(tables[:4])}...)")
        conn.close()
    except Exception as e:
        print(f"[ERROR] {db}: {e}")

print("\n=== 3. TESTING JS & CSS FILES REFERENCED IN INDEX.HTML ===")
index_path = r"C:\Users\user\Desktop\tarjimon\index.html"
with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()

import re
scripts = re.findall(r'<script\s+src=[\"\'](.*?)[\"\']', html)
styles = re.findall(r'<link\s+rel=[\"\']stylesheet[\"\']\s+href=[\"\'](.*?)[\"\']', html)

for s in scripts:
    if s.startswith("http"): continue
    p = os.path.join(r"C:\Users\user\Desktop\tarjimon", s.replace('/', os.sep))
    exists = os.path.exists(p)
    status = "OK" if exists else "MISSING!"
    print(f"[{status}] Script: {s}")

for st in styles:
    if st.startswith("http"): continue
    p = os.path.join(r"C:\Users\user\Desktop\tarjimon", st.replace('/', os.sep))
    exists = os.path.exists(p)
    status = "OK" if exists else "MISSING!"
    print(f"[{status}] Style: {st}")
