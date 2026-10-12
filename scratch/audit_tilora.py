import py_compile, os, glob, sqlite3, sys

tilora_dir = r"C:\Users\user\Desktop\TILORA"
backend_dir = os.path.join(tilora_dir, "backend")
frontend_dir = os.path.join(tilora_dir, "frontend")

print("=== 1. TESTING PYTHON SYNTAX IN TILORA ===")
py_files = []
for root, dirs, files in os.walk(backend_dir):
    if ".pytest_cache" in root or "__pycache__" in root: continue
    for f in files:
        if f.endswith(".py"):
            py_files.append(os.path.join(root, f))

for f in py_files:
    try:
        py_compile.compile(f, doraise=True)
        rel = os.path.relpath(f, tilora_dir)
        print(f"[OK] {rel}")
    except Exception as e:
        rel = os.path.relpath(f, tilora_dir)
        print(f"[ERROR] {rel}: {e}")

print("\n=== 2. TESTING TILORA FASTAPI APP IMPORT ===")
sys.path.insert(0, backend_dir)
try:
    from app.main import app
    print(f"[OK] FastAPI app imported successfully! Routes count: {len(app.routes)}")
except Exception as e:
    print(f"[ERROR] FastAPI app import failed: {e}")

print("\n=== 3. TESTING TILORA DATABASE ===")
db_path = os.path.join(tilora_dir, "tilora.db")
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        cnt = cur.fetchone()[0]
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        print(f"[OK] tilora.db: {cnt} tables ({', '.join(tables[:5])}...)")
        conn.close()
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
else:
    print("[WARNING] tilora.db not found in root")

print("\n=== 4. TESTING FRONTEND ASSETS IN TILORA ===")
for item in ["index.html", "css/style.css", "js/app.js"]:
    p = os.path.join(frontend_dir, item.replace('/', os.sep))
    status = "OK" if os.path.exists(p) else "MISSING!"
    print(f"[{status}] Frontend: {item}")
