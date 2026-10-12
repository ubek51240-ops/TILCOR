import sys
import sqlite3
import os

sys.stdout.reconfigure(encoding='utf-8')

db_path = r'C:\Users\user\Desktop\tarjimon\data\phd_corpus.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("==================================================================")
print(" STAGE 4 EXTRACTION VERIFICATION & INTEGRITY REPORT")
print("==================================================================")

# 1. Total counts
total_pages = cur.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
total_segments = cur.execute("SELECT COUNT(*) FROM segments").fetchone()[0]
total_tokens = cur.execute("SELECT SUM(token_count) FROM pages").fetchone()[0]
print(f"Total Pages in DB:    {total_pages:,}")
print(f"Total Segments in DB: {total_segments:,}")
print(f"Total Tokens in DB:   {total_tokens:,}")

# 2. Per-text breakdown
print("\n--- PER-TEXT STATISTICAL SUMMARY ---")
books = cur.execute("SELECT id, title, language, total_pages FROM books ORDER BY id").fetchall()
for b_id, title, lang, b_pages in books:
    p_cnt = cur.execute("SELECT COUNT(*) FROM pages WHERE book_id = ?", (b_id,)).fetchone()[0]
    s_cnt = cur.execute("SELECT COUNT(*) FROM segments WHERE book_id = ?", (b_id,)).fetchone()[0]
    tok_cnt = cur.execute("SELECT SUM(token_count) FROM pages WHERE book_id = ?", (b_id,)).fetchone()[0] or 0
    char_cnt = cur.execute("SELECT SUM(char_count) FROM pages WHERE book_id = ?", (b_id,)).fetchone()[0] or 0
    fn_cnt = cur.execute("SELECT COUNT(*) FROM segments WHERE book_id = ? AND segment_type = 'footnote'", (b_id,)).fetchone()[0]
    dlg_cnt = cur.execute("SELECT COUNT(*) FROM segments WHERE book_id = ? AND segment_type = 'dialogue'", (b_id,)).fetchone()[0]
    hd_cnt = cur.execute("SELECT COUNT(*) FROM segments WHERE book_id = ? AND segment_type = 'heading'", (b_id,)).fetchone()[0]
    body_cnt = cur.execute("SELECT COUNT(*) FROM segments WHERE book_id = ? AND segment_type = 'body'", (b_id,)).fetchone()[0]
    
    print(f"\n* Book ID: {b_id} | {title} [{lang.upper()}]")
    print(f"  Pages: {p_cnt} | Tokens: {tok_cnt:,} | Characters: {char_cnt:,}")
    print(f"  Segments: {s_cnt:,} (Body: {body_cnt:,}, Dialogue: {dlg_cnt:,}, Headings: {hd_cnt:,}, Footnotes: {fn_cnt:,})")
    
    # Flags breakdown
    cur.execute("SELECT quality_flag, COUNT(*) FROM pages WHERE book_id = ? GROUP BY quality_flag", (b_id,))
    flags = cur.fetchall()
    print(f"  Quality Flags: {dict(flags)}")

# 3. Check orphaned segments (FK validation)
orphaned = cur.execute("""
    SELECT COUNT(*) FROM segments s
    LEFT JOIN pages p ON s.page_id = p.id
    WHERE p.id IS NULL
""").fetchone()[0]
print(f"\n[*] Orphaned segments (not linked to page): {orphaned} (Must be 0)")

# 4. Check foreign keys
fk_errors = cur.execute("PRAGMA foreign_key_check").fetchall()
print(f"[*] Foreign Key Violations: {len(fk_errors)} (Must be 0)")

# 5. Check segments with char_start / char_end
null_offsets = cur.execute("SELECT COUNT(*) FROM segments WHERE char_start IS NULL OR char_end IS NULL").fetchone()[0]
print(f"[*] Segments with missing char offsets: {null_offsets} (Must be 0)")

conn.close()
