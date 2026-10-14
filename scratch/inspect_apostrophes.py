import sqlite3
from collections import Counter

for db_path in ['data/corpus.db', 'data/phd_corpus.db']:
    print('=== DB:', db_path)
    try:
        conn = sqlite3.connect(db_path)
        tables = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print('Tables:', tables)
        for tbl in tables:
            # find text columns
            cols = [c[1] for c in conn.execute(f"PRAGMA table_info({tbl})").fetchall()]
            for col in cols:
                try:
                    rows = conn.execute(f"SELECT {col} FROM {tbl} WHERE {col} IS NOT NULL").fetchall()
                    apostrophes = Counter()
                    for r in rows:
                        val = str(r[0])
                        for char in val:
                            if ord(char) in [39, 96, 180, 699, 700, 712, 8216, 8217, 8218, 8220, 8221, 8242, 8245, 1370]:
                                apostrophes[char] += 1
                    if apostrophes:
                        print(f"  {tbl}.{col} apostrophes:")
                        for char, cnt in apostrophes.most_common():
                            print(f"    '{char}' (U+{ord(char):04X}): {cnt}")
                except Exception as e:
                    pass
    except Exception as e:
        print('Error reading db:', e)
