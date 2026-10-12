import sqlite3
import json

db_path = r'C:\Users\user\Desktop\tarjimon\data\phd_corpus.db'

def test_occurrences_query(q='', pattern='all', semantic='all', equivalence='all', limit=10, page=1):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = '''
        SELECT o.id, o.candidate_id, o.alignment_id, o.book_id, o.pdf_page_num,
               o.matched_span_en, o.matched_span_uz, o.translation_strategy, o.is_verified,
               c.surface_form_en, c.surface_form_uz, c.grammatical_pattern, c.semantic_group,
               c.equivalence_type, c.is_lingvocultural, c.cultural_note, c.mi_score, c.t_score,
               c.log_dice, c.literal_trap,
               a.source_text, a.target_text, a.confidence_score, a.alignment_type,
               b.title as book_title, b.language as book_lang
        FROM collocation_occurrences o
        JOIN collocation_candidates c ON o.candidate_id = c.id
        JOIN alignments a ON o.alignment_id = a.id
        JOIN books b ON o.book_id = b.id
        WHERE 1=1
    '''
    params = []
    if q:
        sql += ' AND (c.surface_form_en LIKE ? OR c.surface_form_uz LIKE ? OR o.matched_span_en LIKE ? OR a.source_text LIKE ? OR a.target_text LIKE ?)'
        wild = f'%{q}%'
        params.extend([wild, wild, wild, wild, wild])
    if pattern != 'all':
        sql += ' AND c.grammatical_pattern LIKE ?'
        params.append(f'%{pattern}%')
    if semantic != 'all':
        sql += ' AND c.semantic_group LIKE ?'
        params.append(f'%{semantic}%')
    if equivalence != 'all':
        sql += ' AND c.equivalence_type LIKE ?'
        params.append(f'%{equivalence}%')

    # Count
    count_sql = f"SELECT COUNT(*) FROM ({sql})"
    cursor.execute(count_sql, params)
    total_found = cursor.fetchone()[0]

    sql += ' ORDER BY c.mi_score DESC LIMIT ? OFFSET ?'
    params.extend([limit, (page - 1) * limit])

    cursor.execute(sql, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return total_found, rows

def test_kwic_query(word='wrinkles', window=6, limit=10):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = '''
        SELECT s.id, s.book_id, s.pdf_page_num, s.clean_text, b.title as book_title
        FROM segments s
        JOIN books b ON s.book_id = b.id
        WHERE s.clean_text LIKE ?
        LIMIT ?
    '''
    cursor.execute(sql, (f'%{word}%', limit))
    rows = cursor.fetchall()

    kwic_results = []
    for r in rows:
        text = r['clean_text']
        # Find word position
        words = text.split()
        kw_idx = -1
        for i, w in enumerate(words):
            if word.lower() in w.lower():
                kw_idx = i
                break
        if kw_idx != -1:
            left = " ".join(words[max(0, kw_idx - window) : kw_idx])
            kw = words[kw_idx]
            right = " ".join(words[kw_idx + 1 : min(len(words), kw_idx + 1 + window)])
            kwic_results.append({
                'id': r['id'],
                'book': r['book_title'],
                'page': r['pdf_page_num'],
                'left': left,
                'keyword': kw,
                'right': right,
                'full': text
            })
    conn.close()
    return kwic_results

cnt, res = test_occurrences_query(q='wrinkles')
print(f"Occurrences found for 'wrinkles': {cnt}")
for r in res:
    print(f"  [{r['id']}] {r['surface_form_en']} <-> {r['surface_form_uz']} (p.{r['pdf_page_num']})")

kwic_res = test_kwic_query('wrinkles')
print(f"\nKWIC results for 'wrinkles': {len(kwic_res)}")
for k in kwic_res:
    print(f"  {k['left']:>25} | {k['keyword']:^15} | {k['right']:<25} (p.{k['page']})")
