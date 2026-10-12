import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('data/phd_corpus.db')
cur = conn.cursor()

def show_side_by_side(pair_title, src_book, tgt_book, src_p_range, tgt_p_range, limit=8):
    print(f"\n==================================================================")
    print(f" {pair_title}")
    print(f"==================================================================")
    src_segs = cur.execute("""
        SELECT id, pdf_page_num, segment_order, clean_text
        FROM segments WHERE book_id = ? AND pdf_page_num BETWEEN ? AND ?
        ORDER BY pdf_page_num, segment_order LIMIT ?
    """, (src_book, src_p_range[0], src_p_range[1], limit)).fetchall()

    tgt_segs = cur.execute("""
        SELECT id, pdf_page_num, segment_order, clean_text
        FROM segments WHERE book_id = ? AND pdf_page_num BETWEEN ? AND ?
        ORDER BY pdf_page_num, segment_order LIMIT ?
    """, (tgt_book, tgt_p_range[0], tgt_p_range[1], limit)).fetchall()

    for i in range(max(len(src_segs), len(tgt_segs))):
        s = src_segs[i] if i < len(src_segs) else (None, None, None, '')
        t = tgt_segs[i] if i < len(tgt_segs) else (None, None, None, '')
        print(f"[{i+1:02d}] SRC p.{s[1]}: {s[3][:70]}")
        print(f"     TGT p.{t[1]}: {t[3][:70]}")

# 1. Hemingway Beginning
show_side_by_side("HEMINGWAY BEGINNING", "book-hemingway-en", "book-hemingway-uz", (2, 3), (1, 2), 6)

# 2. Cho'lpon Beginning
show_side_by_side("CHO'LPON BEGINNING", "book-cholpon-uz", "book-cholpon-en", (3, 4), (3, 4), 6)

conn.close()
