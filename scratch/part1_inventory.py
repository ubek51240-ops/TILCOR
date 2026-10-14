import os
import sys
import json
import sqlite3
import glob

def check_databases():
    print("=== DATABASES ===")
    dbs = glob.glob("data/**/*.db", recursive=True) + glob.glob("backups/**/*.db", recursive=True) + glob.glob("*.db")
    for db in sorted(list(set(dbs))):
        print(f"\nDatabase: {db} ({os.path.getsize(db):,} bytes)")
        try:
            conn = sqlite3.connect(db)
            c = conn.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = c.fetchall()
            for t in tables:
                tname = t[0]
                try:
                    c.execute(f"SELECT COUNT(*) FROM \"{tname}\"")
                    cnt = c.fetchone()[0]
                    print(f"  - Table {tname}: {cnt:,} rows")
                except Exception as e:
                    print(f"  - Table {tname}: error {e}")
            conn.close()
        except Exception as e:
            print(f"  Error opening: {e}")

def search_535():
    print("\n=== SEARCHING FOR 535 MANUALLY ANNOTATED PAIRS FOR KECHA VA KUNDUZ ===")
    for root, dirs, files in os.walk('.'):
        if any(ignored in root for ignored in ['.git', 'venv', '__pycache__']):
            continue
        for f in files:
            p = os.path.join(root, f)
            # check json files
            if f.endswith('.json') or f.endswith('.txt') or f.endswith('.csv') or f.endswith('.md'):
                try:
                    with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                        content = fl.read()
                        if '535' in content:
                            print(f"Found '535' in file: {p}")
                            for line in content.splitlines():
                                if '535' in line and any(k in line.lower() for k in ['kecha', 'kunduz', 'pair', 'annotat', 'juft', 'gold']):
                                    print(f"   Line: {line.strip()[:150]}")
                except Exception:
                    pass

def check_json_data():
    print("\n=== JSON DATA FILES ===")
    data_files = glob.glob("data/*.json")
    for df in data_files:
        sz = os.path.getsize(df)
        print(f"\nFile: {df} ({sz:,} bytes)")
        try:
            with open(df, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    print(f"  Type: List, Length: {len(data):,}")
                    if len(data) > 0 and isinstance(data[0], dict):
                        print(f"  Keys of item 0: {list(data[0].keys())}")
                        # Sample
                        sample = {k: str(data[0][k])[:60] for k in list(data[0].keys())[:8]}
                        print(f"  Sample 0: {sample}")
                elif isinstance(data, dict):
                    print(f"  Type: Dict, Keys: {list(data.keys())[:10]}")
        except Exception as e:
            print(f"  Error loading: {e}")

if __name__ == "__main__":
    check_databases()
    check_json_data()
    search_535()
