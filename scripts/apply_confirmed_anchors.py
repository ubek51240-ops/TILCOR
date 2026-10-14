import json
import sqlite3

corpus_path = 'data/full_corpus.json'
with open(corpus_path, 'r', encoding='utf-8') as f:
    corpus = json.load(f)

anchors_15 = [
    'aln-kvk-00067', 'aln-kvk-00069', 'aln-kvk-00287', 'aln-kvk-00473', 'aln-kvk-00775',
    'aln-kvk-01188', 'aln-kvk-01449', 'aln-kvk-01472', 'aln-kvk-01407', 'aln-kvk-02079',
    'aln-kvk-02342', 'aln-kvk-02936', 'aln-kvk-00011', 'aln-kvk-00022', 'aln-kvk-00043'
]

table_21b = [
    'aln-kvk-02071', 'aln-kvk-03162', 'aln-kvk-06357', 'aln-kvk-06817'
]

oms_anchors = [
    'aln-oms-06824', 'aln-oms-08355'
]

all_confirmed_ids = set(anchors_15 + table_21b + oms_anchors)

updated_count = 0
for seg in corpus:
    sid = seg.get('id')
    if sid in all_confirmed_ids:
        seg['status'] = 'tasdiqlangan'
        seg['alignment_status'] = 'tasdiqlangan'
        seg['source'] = '1.1-paragraf (tadqiqotchi)'
        updated_count += 1
    if sid == 'aln-kvk-02079':
        seg['target_equivalent_span'] = [52, 62]
        seg['target_equivalent'] = 'deep sleep'

with open(corpus_path, 'w', encoding='utf-8') as f:
    json.dump(corpus, f, ensure_ascii=False, indent=2)

print(f"Updated {updated_count} anchors to 'tasdiqlangan' in {corpus_path}")

# Also update SQLite if exists
try:
    conn = sqlite3.connect('data/corpus.db')
    cursor = conn.cursor()
    for sid in all_confirmed_ids:
        cursor.execute("UPDATE parallel_corpus SET status = 'tasdiqlangan', alignment_status = 'tasdiqlangan' WHERE id = ?", (sid,))
    conn.commit()
    conn.close()
    print("Updated corpus.db successfully.")
except Exception as e:
    print(f"SQLite update notice: {e}")
