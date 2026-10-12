import sqlite3
import os
import sys
import re
import time
import io
import csv
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')

DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(DIRECTORY, 'data', 'phd_corpus.db')

def normalize_apostrophes(text):
    """Normalize various apostrophes into standard single quote for search matching."""
    if not text:
        return ""
    return re.sub(r"[\u02bb\u02bc\u2018\u2019\u0060\u00b4']", "'", str(text))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.create_function("NORM_APO", 1, normalize_apostrophes)
    return conn

def get_licence_map(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, licence_status FROM texts")
    res = {}
    for tid, lic in cur.fetchall():
        bid = tid.replace("txt-", "book-")
        res[bid] = lic
        res[tid] = lic
    return res

def escape_html(text):
    if not text:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;"))

def get_real_kwic(params, user_role='admin'):
    start_time = time.time()
    keyword = params.get('q', '').strip()
    if not keyword:
        return {"success": False, "error": "Qidiruv so‘zi (keyword) kiritilmadi"}

    window = max(2, min(20, int(params.get('window', 6))))
    if user_role == 'guest':
        window = min(window, 5) # 1-sentence context constraint for guest mode
    sort_by = params.get('sort_by', 'position') # 'left', 'right', 'position'
    book = params.get('book', 'all')
    lang = params.get('lang', 'all')
    page = max(1, int(params.get('page', 1)))
    limit = max(1, min(100, int(params.get('limit', 50))))

    conn = get_db()
    cur = conn.cursor()

    where_clauses = ["1=1"]
    args = []

    if book != 'all':
        where_clauses.append("s.book_id = ?")
        args.append(book)

    if lang != 'all':
        where_clauses.append("b.language = ?")
        args.append(lang)

    # Apostrophe-insensitive pattern
    norm_kw = normalize_apostrophes(keyword).lower()
    wild_kw = f"%{norm_kw}%"
    where_clauses.append("NORM_APO(LOWER(s.clean_text)) LIKE ?")
    args.append(wild_kw)

    where_str = " AND ".join(where_clauses)

    sql = f'''
        SELECT s.id as segment_id, s.book_id, s.pdf_page_num, s.clean_text,
               b.title as book_title, b.language, b.role
        FROM segments s
        JOIN books b ON s.book_id = b.id
        WHERE {where_str}
    '''
    cur.execute(sql, args)
    rows = cur.fetchall()

    kwic_entries = []
    kw_tokens = norm_kw.split()
    kw_len = len(kw_tokens)

    for r in rows:
        text = r['clean_text']
        words = text.split()
        if kw_len == 1:
            indices = [i for i, w in enumerate(words) if norm_kw in normalize_apostrophes(re.sub(r'^[^\w\']+|[^\w\']+$', '', w)).lower()]
        else:
            indices = []
            for i in range(len(words) - kw_len + 1):
                phrase = " ".join([normalize_apostrophes(re.sub(r'^[^\w\']+|[^\w\']+$', '', words[i + j])).lower() for j in range(kw_len)])
                if norm_kw in phrase:
                    indices.append(i)

        for idx in indices:
            left_words = words[max(0, idx - window) : idx]
            node_word = " ".join(words[idx : idx + kw_len])
            right_words = words[idx + kw_len : min(len(words), idx + kw_len + window)]

            left_str = " ".join(left_words)
            right_str = " ".join(right_words)

            first_left_word = left_words[-1].lower() if left_words else ""
            first_right_word = right_words[0].lower() if right_words else ""
            kwic_entries.append({
                'segment_id': r['segment_id'],
                'role': r['role'],
                'book_id': r['book_id'],
                'book_title': r['book_title'],
                'language': r['language'],
                'pdf_page_num': r['pdf_page_num'],
                'left_context': left_str,
                'node_word': node_word,
                'right_context': right_str,
                'first_left_sort': first_left_word,
                'first_right_sort': first_right_word,
                'full_sentence': text
            })

    # Sorting
    if sort_by == 'left':
        kwic_entries.sort(key=lambda x: x['first_left_sort'], reverse=False)
    elif sort_by == 'right':
        kwic_entries.sort(key=lambda x: x['first_right_sort'], reverse=False)
    # else keep text stream position

    # Stage 10: Guest role limitation for protected texts
    lic_map = get_licence_map(conn)
    is_guest = (user_role == 'guest')
    has_protected = any(lic_map.get(e['book_id'], 'protected') == 'protected' for e in kwic_entries)
    guest_capped = False
    if is_guest and has_protected:
        if len(kwic_entries) > 50:
            kwic_entries = kwic_entries[:50]
            guest_capped = True

    total_count = len(kwic_entries)
    offset = (page - 1) * limit
    paginated_entries = kwic_entries[offset : offset + limit]

    # Look up alignments only for the paginated slice
    for item in paginated_entries:
        aln_row = cur.execute('''
            SELECT id, source_text, target_text, source_book_id
            FROM alignments
            WHERE source_segment_ids LIKE ? OR target_segment_ids LIKE ?
            LIMIT 1
        ''', (f"%{item['segment_id']}%", f"%{item['segment_id']}%")).fetchone()

        item['alignment_id'] = aln_row['id'] if aln_row else None
        item['aligned_translation'] = (aln_row['target_text'] if aln_row and item['role'] == 'source' else (aln_row['source_text'] if aln_row else ""))

    conn.close()

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "success": True,
        "query": keyword,
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit if total_count > 0 else 1,
        "window": window,
        "sort_by": sort_by,
        "response_time_ms": elapsed_ms,
        "target_response_ms": 100,
        "is_within_target": elapsed_ms <= 100,
        "is_guest_mode": is_guest,
        "guest_capped": guest_capped,
        "results": paginated_entries
    }

def search_parallel_corpus(params, user_role='admin'):
    start_time = time.time()
    q = params.get('q', '').strip()
    book = params.get('book', 'all')
    pattern = params.get('pattern', 'all')
    status = params.get('status', 'all')
    page = max(1, int(params.get('page', 1)))
    limit = max(1, min(100, int(params.get('limit', 20))))
    if user_role == 'guest':
        limit = min(limit, 50)

    conn = get_db()
    cur = conn.cursor()

    where_clauses = ["1=1"]
    args = []

    if book != 'all':
        where_clauses.append("o.book_id = ?")
        args.append(book)

    if pattern != 'all':
        where_clauses.append("pa.structural_pattern = ?")
        args.append(pattern)

    if status == 'confirmed':
        where_clauses.append("pa.is_confirmed = 1")
    elif status == 'draft':
        where_clauses.append("pa.is_confirmed = 0 AND pa.id IS NOT NULL")
    elif status == 'unannotated':
        where_clauses.append("pa.id IS NULL")

    if q:
        norm_q = normalize_apostrophes(q).lower()
        wild = f"%{norm_q}%"
        where_clauses.append('''
            (NORM_APO(LOWER(a.source_text)) LIKE ? OR
             NORM_APO(LOWER(a.target_text)) LIKE ? OR
             NORM_APO(LOWER(c.surface_form_en)) LIKE ? OR
             NORM_APO(LOWER(c.surface_form_uz)) LIKE ?)
        ''')
        args.extend([wild, wild, wild, wild])

    where_str = " AND ".join(where_clauses)

    count_sql = f'''
        SELECT count(*)
        FROM collocation_occurrences o
        JOIN alignments a ON o.alignment_id = a.id
        JOIN collocation_candidates c ON o.candidate_id = c.id
        LEFT JOIN phd_annotations pa ON o.id = pa.occurrence_id
        WHERE {where_str}
    '''
    cur.execute(count_sql, args)
    total = cur.fetchone()[0]
    if user_role == 'guest':
        total = min(total, 50)

    offset = (page - 1) * limit
    select_sql = f'''
        SELECT 
            o.id as occurrence_id,
            o.candidate_id,
            o.alignment_id,
            o.book_id,
            o.pdf_page_num,
            o.matched_span_en,
            o.matched_span_uz,
            c.surface_form_en,
            c.surface_form_uz,
            a.source_text,
            a.target_text,
            a.alignment_type,
            a.alignment_method,
            a.confidence_score as aln_score,
            pa.id as annotation_id,
            pa.annotator_user,
            pa.guideline_version,
            pa.unit_type,
            pa.structural_pattern,
            pa.semantic_group,
            pa.equivalence_type,
            pa.translation_strategy,
            pa.is_cultural,
            pa.cultural_category,
            pa.confidence_level,
            pa.is_confirmed,
            pa.source_span,
            pa.target_span
        FROM collocation_occurrences o
        JOIN alignments a ON o.alignment_id = a.id
        JOIN collocation_candidates c ON o.candidate_id = c.id
        LEFT JOIN phd_annotations pa ON o.id = pa.occurrence_id
        WHERE {where_str}
        ORDER BY (pa.is_confirmed = 1) DESC, o.pdf_page_num ASC
        LIMIT ? OFFSET ?
    '''
    args.extend([limit, offset])
    cur.execute(select_sql, args)
    rows = cur.fetchall()

    results = []
    for r in rows:
        is_cholpon = 'cholpon' in r['book_id']
        source_lang = 'uz' if is_cholpon else 'en'
        target_lang = 'en' if is_cholpon else 'uz'

        if is_cholpon:
            src_colloc = r['source_span'] or r['matched_span_uz'] or r['surface_form_uz']
            tgt_colloc = r['target_span'] or r['matched_span_en']
        else:
            src_colloc = r['source_span'] or r['matched_span_en'] or r['surface_form_en']
            tgt_colloc = r['target_span'] or r['matched_span_uz']

        results.append({
            'occurrence_id': r['occurrence_id'],
            'alignment_id': r['alignment_id'],
            'book_id': r['book_id'],
            'pdf_page_num': r['pdf_page_num'],
            'source_lang': source_lang,
            'target_lang': target_lang,
            'source_title': "Cho‘lpon: «Kecha va kunduz» (Asl)" if is_cholpon else "Hemingway: «The Old Man and the Sea» (Original)",
            'target_title': "Cho‘lpon: «Night and Day» (Tarjima)" if is_cholpon else "Hemingway: «Chol va dengiz» (Tarjima)",
            'source_sentence': r['source_text'],
            'target_sentence': r['target_text'],
            'source_collocation': src_colloc,
            'target_collocation': tgt_colloc,
            'alignment_type': r['alignment_type'],
            'alignment_method': r['alignment_method'],
            'annotation': {
                'id': r['annotation_id'],
                'annotator': r['annotator_user'],
                'guideline_version': r['guideline_version'],
                'unit_type': r['unit_type'],
                'structural_pattern': r['structural_pattern'],
                'semantic_group': r['semantic_group'],
                'equivalence_type': r['equivalence_type'],
                'translation_strategy': r['translation_strategy'],
                'cultural_category': r['cultural_category'],
                'confidence_level': r['confidence_level'],
                'is_confirmed': bool(r['is_confirmed']) if r['is_confirmed'] is not None else False
            } if r['annotation_id'] else None
        })

    conn.close()
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "success": True,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if total > 0 else 1,
        "response_time_ms": elapsed_ms,
        "is_within_target": elapsed_ms <= 100,
        "results": results
    }

def export_all_filtered_rows(params, format_type='xlsx', user_role='admin'):
    if user_role == 'guest':
        raise PermissionError("Mehmon (guest) foydalanuvchilar uchun korpus ma'lumotlarini ommaviy eksport qilish taqiqlangan. Ruxsat faqat tadqiqotchi (admin) va ilmiy rahbar (reviewer) uchun berilgan.")

    # Run full search without pagination
    conn = get_db()
    cur = conn.cursor()

    q = params.get('q', '').strip()
    book = params.get('book', 'all')
    pattern = params.get('pattern', 'all')
    status = params.get('status', 'all')

    where_clauses = ["1=1"]
    args = []

    if book != 'all':
        where_clauses.append("o.book_id = ?")
        args.append(book)

    if pattern != 'all':
        where_clauses.append("pa.structural_pattern = ?")
        args.append(pattern)

    if status == 'confirmed':
        where_clauses.append("pa.is_confirmed = 1")
    elif status == 'draft':
        where_clauses.append("pa.is_confirmed = 0 AND pa.id IS NOT NULL")
    elif status == 'unannotated':
        where_clauses.append("pa.id IS NULL")

    if q:
        norm_q = normalize_apostrophes(q).lower()
        wild = f"%{norm_q}%"
        where_clauses.append('''
            (NORM_APO(LOWER(a.source_text)) LIKE ? OR
             NORM_APO(LOWER(a.target_text)) LIKE ?)
        ''')
        args.extend([wild, wild])

    where_str = " AND ".join(where_clauses)

    sql = f'''
        SELECT 
            o.id as record_id,
            b.title as work_title,
            b.publisher as edition_info,
            CASE WHEN o.book_id LIKE '%cholpon%' THEN 'UZ ➔ EN' ELSE 'EN ➔ UZ' END as direction,
            CASE WHEN o.book_id LIKE '%cholpon%' THEN 'uz' ELSE 'en' END as source_language,
            a.source_text as source_segment,
            a.target_text as target_segment,
            COALESCE(pa.source_span, CASE WHEN o.book_id LIKE '%cholpon%' THEN o.matched_span_uz ELSE o.matched_span_en END) as matched_span,
            COALESCE(pa.target_span, CASE WHEN o.book_id LIKE '%cholpon%' THEN o.matched_span_en ELSE o.matched_span_uz END) as equivalent_span,
            o.pdf_page_num as pdf_page,
            a.alignment_type,
            CASE WHEN pa.is_confirmed = 1 THEN 'confirmed' WHEN pa.id IS NOT NULL THEN 'draft' ELSE 'unannotated' END as alignment_status,
            a.alignment_method,
            COALESCE(pa.unit_type, '—') as unit_type,
            COALESCE(pa.structural_pattern, '—') as structural_pattern,
            COALESCE(pa.semantic_group, '—') as semantic_group,
            COALESCE(pa.equivalence_type, '—') as equivalence_type,
            COALESCE(pa.translation_strategy, '—') as translation_strategy,
            COALESCE(pa.cultural_category, '—') as cultural_category,
            COALESCE(pa.guideline_version, 'v1.0') as guideline_version,
            COALESCE(pa.annotator_user, '—') as annotator,
            CURRENT_TIMESTAMP as export_timestamp,
            ? as query_and_settings
        FROM collocation_occurrences o
        JOIN alignments a ON o.alignment_id = a.id
        JOIN books b ON o.book_id = b.id
        LEFT JOIN phd_annotations pa ON o.id = pa.occurrence_id
        WHERE {where_str}
        ORDER BY o.pdf_page_num ASC
    '''
    settings_str = json.dumps({"q": q, "book": book, "pattern": pattern, "status": status})
    args.append(settings_str)

    cur.execute(sql, args)
    rows = cur.fetchall()
    conn.close()

    headers = [
        "Record_ID", "Work", "Edition", "Direction", "Source_Language",
        "Source_Segment", "Target_Segment", "Matched_Span", "Equivalent_Span",
        "PDF_Page", "Alignment_Type", "Alignment_Status", "Alignment_Method",
        "Unit_Type", "Structural_Pattern", "Semantic_Group", "Equivalence_Type",
        "Translation_Strategy", "Cultural_Category", "Guideline_Version",
        "Annotator", "Export_Timestamp", "Query_Settings"
    ]

    if format_type == 'csv':
        output = io.StringIO()
        # UTF-8 with BOM prefix
        writer = csv.writer(output)
        writer.writerow(headers)
        for r in rows:
            d = dict(r)
            writer.writerow([d.get(h.lower(), d.get(h, '')) for h in headers])
        csv_bytes = b'\xef\xbb\xbf' + output.getvalue().encode('utf-8')
        return csv_bytes, "text/csv; charset=utf-8", "tilcor_parallel_corpus_stage9.csv"

    # Excel (.xlsx) using openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Corpus_Occurrences"

    # Header styling
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws.append(headers)
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align

    # Add data rows
    for r in rows:
        d = dict(r)
        row_vals = [d.get(h.lower(), d.get(h, '')) for h in headers]
        ws.append(row_vals)

    # Auto-adjust column widths
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = min(50, max(12, max_len + 2))

    excel_buffer = io.BytesIO()
    wb.save(excel_buffer)
    excel_buffer.seek(0)

    return excel_buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "tilcor_parallel_corpus_stage9.xlsx"
