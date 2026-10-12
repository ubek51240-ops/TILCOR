import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('data/phd_corpus.db')
cur = conn.cursor()

print("==================================================================")
print(" STAGE 5 ALIGNMENT RESULTS & STATISTICAL BREAKDOWN")
print("==================================================================")

total_alns = cur.execute("SELECT COUNT(*) FROM alignments").fetchone()[0]
print(f"Total Aligned Pairs in DB: {total_alns:,}")

pairs = cur.execute("SELECT DISTINCT pair_id FROM alignments").fetchall()
for p in pairs:
    pid = p[0]
    total_p = cur.execute("SELECT COUNT(*) FROM alignments WHERE pair_id = ?", (pid,)).fetchone()[0]
    t_11 = cur.execute("SELECT COUNT(*) FROM alignments WHERE pair_id = ? AND alignment_type = '1:1'", (pid,)).fetchone()[0]
    t_12 = cur.execute("SELECT COUNT(*) FROM alignments WHERE pair_id = ? AND alignment_type = '1:2'", (pid,)).fetchone()[0]
    t_21 = cur.execute("SELECT COUNT(*) FROM alignments WHERE pair_id = ? AND alignment_type = '2:1'", (pid,)).fetchone()[0]
    
    stat_draft = cur.execute("SELECT COUNT(*) FROM alignments WHERE pair_id = ? AND reviewer_status = 'draft'", (pid,)).fetchone()[0]
    stat_review = cur.execute("SELECT COUNT(*) FROM alignments WHERE pair_id = ? AND reviewer_status = 'needs_review'", (pid,)).fetchone()[0]
    stat_conf = cur.execute("SELECT COUNT(*) FROM alignments WHERE pair_id = ? AND reviewer_status = 'confirmed'", (pid,)).fetchone()[0]
    
    avg_cost = cur.execute("SELECT AVG(confidence_score) FROM alignments WHERE pair_id = ?", (pid,)).fetchone()[0]
    
    print(f"\n* PAIR ID: {pid}")
    print(f"  Total Pairs: {total_p:,}")
    print(f"  Types: 1:1 = {t_11:,} ({t_11/total_p*100:.1f}%), 1:2 = {t_12:,} ({t_12/total_p*100:.1f}%), 2:1 = {t_21:,} ({t_21/total_p*100:.1f}%)")
    print(f"  Reviewer Status: draft = {stat_draft:,}, needs_review = {stat_review:,}, confirmed = {stat_conf:,}")
    print(f"  Mean Raw Cost: {avg_cost:.2f} (Gale-Church + Dict penalty score, NOT %)")

# Check FK and traceability
print(f"\n[*] Checking PDF Traceability:")
sample = cur.execute("SELECT id, source_text, target_text, source_segment_ids, target_segment_ids, confidence_score, reviewer_status FROM alignments LIMIT 3").fetchall()
for s in sample:
    s_ids = json.loads(s[3])
    t_ids = json.loads(s[4])
    s_p = cur.execute("SELECT pdf_page_num FROM segments WHERE id = ?", (s_ids[0],)).fetchone()[0]
    t_p = cur.execute("SELECT pdf_page_num FROM segments WHERE id = ?", (t_ids[0],)).fetchone()[0]
    print(f"  [{s[0]}] Cost: {s[5]} | Status: {s[6]}")
    print(f"    SRC p.{s_p}: {s[1][:80]}")
    print(f"    TGT p.{t_p}: {s[2][:80]}")

stev_count = cur.execute("SELECT COUNT(*) FROM alignments WHERE pair_id LIKE '%stevenson%'").fetchone()[0]
print(f"\n[*] Stevenson Aligned Pairs: {stev_count} (Must be 0 until real text is supplied)")

conn.close()
