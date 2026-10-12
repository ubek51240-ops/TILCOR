import sqlite3
import json
import os
import re

DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(DIRECTORY, 'data', 'phd_corpus.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_stage7_taxonomies():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT taxonomy_name, code, label_uz, label_en, definition, examples, version
        FROM taxonomies
        WHERE version = '1.0'
        ORDER BY taxonomy_name, code
    ''')
    rows = cur.fetchall()
    conn.close()

    grouped = {}
    for r in rows:
        cat = r['taxonomy_name']
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append({
            'code': r['code'],
            'label_uz': r['label_uz'],
            'label_en': r['label_en'],
            'definition': r['definition'],
            'examples': r['examples'],
            'version': r['version']
        })
    return {"success": True, "taxonomies": grouped}

def get_stage7_occurrences(params):
    conn = get_db()
    cur = conn.cursor()

    book = params.get('book', 'all')
    status = params.get('status', 'all')
    q = params.get('q', '').strip().lower()
    page = max(1, int(params.get('page', 1)))
    limit = max(1, min(100, int(params.get('limit', 20))))

    where_clauses = ["1=1"]
    args = []

    if book != 'all':
        where_clauses.append("o.book_id = ?")
        args.append(book)

    if status == 'confirmed':
        where_clauses.append("pa.is_confirmed = 1")
    elif status == 'draft':
        where_clauses.append("pa.is_confirmed = 0 AND pa.id IS NOT NULL")
    elif status == 'unannotated':
        where_clauses.append("pa.id IS NULL")

    if q:
        where_clauses.append("(c.surface_form_en LIKE ? OR c.surface_form_uz LIKE ? OR a.source_text LIKE ? OR a.target_text LIKE ?)")
        wild = f"%{q}%"
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
            o.translation_strategy as legacy_strategy,
            o.is_verified as legacy_verified,
            c.surface_form_en,
            c.surface_form_uz,
            c.grammatical_pattern as cand_pattern,
            c.semantic_group as cand_semantic,
            c.equivalence_type as cand_equivalence,
            a.source_text,
            a.target_text,
            pa.id as annotation_id,
            pa.annotator_user,
            pa.source_span,
            pa.target_span,
            pa.has_target_equivalent,
            pa.unit_type,
            pa.structural_pattern,
            pa.semantic_group,
            pa.equivalence_type,
            pa.translation_strategy,
            pa.is_cultural,
            pa.cultural_category,
            pa.cultural_note,
            pa.confidence_level,
            pa.evidence_note,
            pa.is_ai_suggestion,
            pa.is_confirmed,
            pa.updated_at
        FROM collocation_occurrences o
        JOIN alignments a ON o.alignment_id = a.id
        JOIN collocation_candidates c ON o.candidate_id = c.id
        LEFT JOIN phd_annotations pa ON o.id = pa.occurrence_id
        WHERE {where_str}
        ORDER BY (pa.is_confirmed = 1) DESC, o.id ASC
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
        
        # Source collocation is in the source language
        if is_cholpon:
            source_colloc = r['matched_span_uz'] or r['surface_form_uz']
            target_colloc = r['matched_span_en']
        else:
            source_colloc = r['matched_span_en'] or r['surface_form_en']
            target_colloc = r['matched_span_uz']

        results.append({
            'occurrence_id': r['occurrence_id'],
            'candidate_id': r['candidate_id'],
            'alignment_id': r['alignment_id'],
            'book_id': r['book_id'],
            'pdf_page_num': r['pdf_page_num'],
            'source_lang': source_lang,
            'target_lang': target_lang,
            'source_title': "Cho‘lpon: «Kecha va kunduz» (Asl nusxa)" if is_cholpon else "Hemingway: «The Old Man and the Sea» (Original)",
            'target_title': "Cho‘lpon: «Night and Day» (Inglizcha tarjima)" if is_cholpon else "Hemingway: «Chol va dengiz» (O‘zbekcha tarjima)",
            'source_sentence': r['source_text'],
            'target_sentence': r['target_text'],
            'source_collocation': source_colloc,
            'target_collocation': target_colloc,
            'candidate_info': {
                'en': r['surface_form_en'],
                'uz': r['surface_form_uz'],
                'default_pattern': r['cand_pattern'],
                'default_semantic': r['cand_semantic'],
                'default_equivalence': r['cand_equivalence']
            },
            'annotation': {
                'id': r['annotation_id'],
                'annotator_user': r['annotator_user'],
                'source_span': r['source_span'],
                'target_span': r['target_span'],
                'has_target_equivalent': bool(r['has_target_equivalent']) if r['has_target_equivalent'] is not None else True,
                'unit_type': r['unit_type'],
                'structural_pattern': r['structural_pattern'],
                'semantic_group': r['semantic_group'],
                'equivalence_type': r['equivalence_type'],
                'translation_strategy': r['translation_strategy'],
                'is_cultural': bool(r['is_cultural']) if r['is_cultural'] is not None else False,
                'cultural_category': r['cultural_category'],
                'cultural_note': r['cultural_note'],
                'confidence_level': r['confidence_level'],
                'evidence_note': r['evidence_note'],
                'is_ai_suggestion': bool(r['is_ai_suggestion']) if r['is_ai_suggestion'] is not None else False,
                'is_confirmed': bool(r['is_confirmed']) if r['is_confirmed'] is not None else False,
                'updated_at': r['updated_at']
            } if r['annotation_id'] else None
        })

    # Stats for header
    cur.execute("SELECT count(*) FROM collocation_occurrences")
    total_occurrences = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM phd_annotations WHERE is_confirmed = 1")
    confirmed_count = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM phd_annotations WHERE is_confirmed = 0")
    draft_count = cur.fetchone()[0]

    conn.close()

    return {
        "success": True,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "stats": {
            "total_occurrences": total_occurrences,
            "confirmed_count": confirmed_count,
            "draft_count": draft_count,
            "unannotated_count": total_occurrences - (confirmed_count + draft_count)
        },
        "results": results
    }

def get_stage7_occurrence_by_id(occ_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
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
            c.grammatical_pattern as cand_pattern,
            c.semantic_group as cand_semantic,
            c.equivalence_type as cand_equivalence,
            a.source_text,
            a.target_text,
            pa.id as annotation_id,
            pa.annotator_user,
            pa.source_span,
            pa.target_span,
            pa.has_target_equivalent,
            pa.unit_type,
            pa.structural_pattern,
            pa.semantic_group,
            pa.equivalence_type,
            pa.translation_strategy,
            pa.is_cultural,
            pa.cultural_category,
            pa.cultural_note,
            pa.confidence_level,
            pa.evidence_note,
            pa.is_ai_suggestion,
            pa.is_confirmed,
            pa.updated_at
        FROM collocation_occurrences o
        JOIN alignments a ON o.alignment_id = a.id
        JOIN collocation_candidates c ON o.candidate_id = c.id
        LEFT JOIN phd_annotations pa ON o.id = pa.occurrence_id
        WHERE o.id = ?
    ''', (occ_id,))
    r = cur.fetchone()
    if not r:
        conn.close()
        return {"success": False, "error": f"Occurrence {occ_id} topilmadi"}

    is_cholpon = 'cholpon' in r['book_id']
    source_lang = 'uz' if is_cholpon else 'en'
    target_lang = 'en' if is_cholpon else 'uz'

    # Get surrounding context (+- 2 sentences)
    cur.execute('''
        SELECT id, source_text, target_text 
        FROM alignments 
        WHERE source_book_id = ?
        ORDER BY id
    ''', (r['book_id'],))
    all_alns = cur.fetchall()
    
    current_aln_idx = -1
    for idx, aln in enumerate(all_alns):
        if aln['id'] == r['alignment_id']:
            current_aln_idx = idx
            break

    context_before = []
    context_after = []
    if current_aln_idx != -1:
        start_idx = max(0, current_aln_idx - 2)
        end_idx = min(len(all_alns), current_aln_idx + 3)
        for i in range(start_idx, current_aln_idx):
            context_before.append({
                'aln_id': all_alns[i]['id'],
                'source': all_alns[i]['source_text'],
                'target': all_alns[i]['target_text']
            })
        for i in range(current_aln_idx + 1, end_idx):
            context_after.append({
                'aln_id': all_alns[i]['id'],
                'source': all_alns[i]['source_text'],
                'target': all_alns[i]['target_text']
            })

    conn.close()

    if is_cholpon:
        source_colloc = r['matched_span_uz'] or r['surface_form_uz']
        target_colloc = r['matched_span_en']
    else:
        source_colloc = r['matched_span_en'] or r['surface_form_en']
        target_colloc = r['matched_span_uz']

    return {
        "success": True,
        "occurrence": {
            'occurrence_id': r['occurrence_id'],
            'candidate_id': r['candidate_id'],
            'alignment_id': r['alignment_id'],
            'book_id': r['book_id'],
            'pdf_page_num': r['pdf_page_num'],
            'source_lang': source_lang,
            'target_lang': target_lang,
            'source_title': "Cho‘lpon: «Kecha va kunduz» (Asl nusxa)" if is_cholpon else "Hemingway: «The Old Man and the Sea» (Original)",
            'target_title': "Cho‘lpon: «Night and Day» (Inglizcha tarjima)" if is_cholpon else "Hemingway: «Chol va dengiz» (O‘zbekcha tarjima)",
            'source_sentence': r['source_text'],
            'target_sentence': r['target_text'],
            'source_collocation': source_colloc,
            'target_collocation': target_colloc,
            'context_before': context_before,
            'context_after': context_after,
            'candidate_info': {
                'en': r['surface_form_en'],
                'uz': r['surface_form_uz'],
                'default_pattern': r['cand_pattern'],
                'default_semantic': r['cand_semantic'],
                'default_equivalence': r['cand_equivalence']
            },
            'annotation': {
                'id': r['annotation_id'],
                'annotator_user': r['annotator_user'],
                'source_span': r['source_span'],
                'target_span': r['target_span'],
                'has_target_equivalent': bool(r['has_target_equivalent']) if r['has_target_equivalent'] is not None else True,
                'unit_type': r['unit_type'],
                'structural_pattern': r['structural_pattern'],
                'semantic_group': r['semantic_group'],
                'equivalence_type': r['equivalence_type'],
                'translation_strategy': r['translation_strategy'],
                'is_cultural': bool(r['is_cultural']) if r['is_cultural'] is not None else False,
                'cultural_category': r['cultural_category'],
                'cultural_note': r['cultural_note'],
                'confidence_level': r['confidence_level'],
                'evidence_note': r['evidence_note'],
                'is_ai_suggestion': bool(r['is_ai_suggestion']) if r['is_ai_suggestion'] is not None else False,
                'is_confirmed': bool(r['is_confirmed']) if r['is_confirmed'] is not None else False,
                'updated_at': r['updated_at']
            } if r['annotation_id'] else None
        }
    }

def save_stage7_annotation(data, user='admin'):
    occ_id = data.get('occurrence_id')
    if not occ_id:
        return {"success": False, "error": "occurrence_id ko‘rsatilishi shart"}

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id, book_id FROM collocation_occurrences WHERE id = ?", (occ_id,))
    occ = cur.fetchone()
    if not occ:
        conn.close()
        return {"success": False, "error": f"Occurrence {occ_id} topilmadi"}

    source_span = data.get('source_span', '').strip()
    target_span = data.get('target_span', '').strip()
    has_target_equivalent = 0 if data.get('has_target_equivalent') is False else 1
    if not has_target_equivalent:
        target_span = None

    unit_type = data.get('unit_type', 'kollokatsiya')
    structural_pattern = data.get('structural_pattern', 'Fel+Ot')
    semantic_group = data.get('semantic_group', 'inson_ruhiyati')
    equivalence_type = data.get('equivalence_type', 'toliq_ekvivalent')
    translation_strategy = data.get('translation_strategy', 'kalka')
    is_cultural = 1 if data.get('is_cultural') else 0
    cultural_category = data.get('cultural_category', 'yoq')
    cultural_note = data.get('cultural_note', '')
    confidence_level = data.get('confidence_level', 'yuqori')
    evidence_note = data.get('evidence_note', '')
    is_confirmed = 1 if data.get('is_confirmed') else 0
    is_ai_suggestion = 1 if data.get('is_ai_suggestion') else 0

    cur.execute("SELECT id FROM phd_annotations WHERE occurrence_id = ? AND annotator_user = ?", (occ_id, user))
    existing = cur.fetchone()

    if existing:
        ann_id = existing['id']
        cur.execute('''
            UPDATE phd_annotations
            SET source_span = ?,
                target_span = ?,
                has_target_equivalent = ?,
                unit_type = ?,
                structural_pattern = ?,
                semantic_group = ?,
                equivalence_type = ?,
                translation_strategy = ?,
                is_cultural = ?,
                cultural_category = ?,
                cultural_note = ?,
                confidence_level = ?,
                evidence_note = ?,
                is_ai_suggestion = ?,
                is_confirmed = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            source_span, target_span, has_target_equivalent,
            unit_type, structural_pattern, semantic_group, equivalence_type,
            translation_strategy, is_cultural, cultural_category, cultural_note,
            confidence_level, evidence_note, is_ai_suggestion, is_confirmed,
            ann_id
        ))
    else:
        cur.execute("SELECT count(*) FROM phd_annotations")
        cnt = cur.fetchone()[0]
        ann_id = f"phd-ann-{cnt+1:05d}"
        cur.execute('''
            INSERT INTO phd_annotations (
                id, occurrence_id, annotator_user, guideline_version, taxonomy_version,
                source_span, target_span, has_target_equivalent,
                unit_type, structural_pattern, semantic_group, equivalence_type,
                translation_strategy, is_cultural, cultural_category, cultural_note,
                confidence_level, evidence_note, is_ai_suggestion, is_confirmed
            ) VALUES (?, ?, ?, 'v1.0', '1.0', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ann_id, occ_id, user,
            source_span, target_span, has_target_equivalent,
            unit_type, structural_pattern, semantic_group, equivalence_type,
            translation_strategy, is_cultural, cultural_category, cultural_note,
            confidence_level, evidence_note, is_ai_suggestion, is_confirmed
        ))

    # Update occurrence target span and verified state
    is_cholpon = 'cholpon' in occ['book_id']
    if is_cholpon:
        cur.execute('''
            UPDATE collocation_occurrences
            SET matched_span_en = COALESCE(?, matched_span_en),
                is_verified = ?
            WHERE id = ?
        ''', (target_span, is_confirmed, occ_id))
    else:
        cur.execute('''
            UPDATE collocation_occurrences
            SET matched_span_uz = COALESCE(?, matched_span_uz),
                is_verified = ?
            WHERE id = ?
        ''', (target_span, is_confirmed, occ_id))

    # Audit log
    cur.execute('''
        INSERT INTO audit_log (user, action, entity, entity_id, changes)
        VALUES (?, ?, 'phd_annotations', ?, ?)
    ''', (
        user,
        'CONFIRM_ANNOTATION' if is_confirmed else 'SAVE_DRAFT_ANNOTATION',
        ann_id,
        json.dumps({
            'occurrence_id': occ_id,
            'pattern': structural_pattern,
            'equivalence': equivalence_type,
            'strategy': translation_strategy,
            'target_span': target_span,
            'is_confirmed': is_confirmed
        }, ensure_ascii=False)
    ))

    conn.commit()
    conn.close()

    # Also mirror to staging if in production
    sync_to_staging(ann_id, occ_id, user, source_span, target_span, has_target_equivalent,
                    unit_type, structural_pattern, semantic_group, equivalence_type,
                    translation_strategy, is_cultural, cultural_category, cultural_note,
                    confidence_level, evidence_note, is_ai_suggestion, is_confirmed)

    return {"success": True, "annotation_id": ann_id, "occurrence_id": occ_id, "is_confirmed": bool(is_confirmed)}

def sync_to_staging(ann_id, occ_id, user, source_span, target_span, has_target_equivalent,
                    unit_type, structural_pattern, semantic_group, equivalence_type,
                    translation_strategy, is_cultural, cultural_category, cultural_note,
                    confidence_level, evidence_note, is_ai_suggestion, is_confirmed):
    staging_db = os.path.join(DIRECTORY, 'staging', 'data', 'phd_corpus.db')
    if not os.path.exists(staging_db):
        return
    try:
        conn = sqlite3.connect(staging_db)
        cur = conn.cursor()
        cur.execute('''
            INSERT OR REPLACE INTO phd_annotations (
                id, occurrence_id, annotator_user, guideline_version, taxonomy_version,
                source_span, target_span, has_target_equivalent,
                unit_type, structural_pattern, semantic_group, equivalence_type,
                translation_strategy, is_cultural, cultural_category, cultural_note,
                confidence_level, evidence_note, is_ai_suggestion, is_confirmed
            ) VALUES (?, ?, ?, 'v1.0', '1.0', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ann_id, occ_id, user,
            source_span, target_span, has_target_equivalent,
            unit_type, structural_pattern, semantic_group, equivalence_type,
            translation_strategy, is_cultural, cultural_category, cultural_note,
            confidence_level, evidence_note, is_ai_suggestion, is_confirmed
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[!] Staging sync error: {e}")

def get_correspondence_matrix(params):
    conn = get_db()
    cur = conn.cursor()

    book = params.get('book', 'all')
    pattern_drill = params.get('pattern')
    equiv_drill = params.get('equivalence')

    where_clauses = ["pa.is_confirmed = 1"]
    args = []

    if book != 'all':
        where_clauses.append("o.book_id = ?")
        args.append(book)

    # Patterns and equivalences definition
    patterns = ['Fel+Ot', 'Sifat+Ot', 'Ot+Fel', 'Ravish+Fel', 'Ot+Ot', 'boshqa']
    equivalences = [
        'toliq_ekvivalent', 'qisman_ekvivalent', 'strukturaviy_transformatsiya',
        'obraz_almashtirish', 'tasviriy_tarjima', 'bir_sozga_siqilgan',
        'tushirib_qoldirilgan', 'tarjimada_qoshilgan'
    ]

    where_str = " AND ".join(where_clauses)
    matrix_sql = f'''
        SELECT 
            pa.structural_pattern,
            pa.equivalence_type,
            count(*) as cnt
        FROM phd_annotations pa
        JOIN collocation_occurrences o ON pa.occurrence_id = o.id
        WHERE {where_str}
        GROUP BY pa.structural_pattern, pa.equivalence_type
    '''
    cur.execute(matrix_sql, args)
    counts = cur.fetchall()

    grid = {p: {e: 0 for e in equivalences} for p in patterns}
    row_totals = {p: 0 for p in patterns}
    col_totals = {e: 0 for e in equivalences}
    grand_total = 0

    for r in counts:
        p = r['structural_pattern']
        e = r['equivalence_type']
        c = r['cnt']
        if p in grid and e in grid[p]:
            grid[p][e] = c
            row_totals[p] += c
            col_totals[e] += c
            grand_total += c

    drilldown_items = []
    if pattern_drill and equiv_drill:
        drill_sql = f'''
            SELECT 
                o.id as occurrence_id,
                o.book_id,
                o.pdf_page_num,
                pa.source_span,
                pa.target_span,
                pa.translation_strategy,
                pa.evidence_note,
                a.source_text,
                a.target_text
            FROM phd_annotations pa
            JOIN collocation_occurrences o ON pa.occurrence_id = o.id
            JOIN alignments a ON o.alignment_id = a.id
            WHERE {where_str} AND pa.structural_pattern = ? AND pa.equivalence_type = ?
            ORDER BY o.pdf_page_num ASC
        '''
        drill_args = list(args) + [pattern_drill, equiv_drill]
        cur.execute(drill_sql, drill_args)
        for r in cur.fetchall():
            drilldown_items.append({
                'occurrence_id': r['occurrence_id'],
                'book_id': r['book_id'],
                'pdf_page_num': r['pdf_page_num'],
                'source_span': r['source_span'],
                'target_span': r['target_span'],
                'translation_strategy': r['translation_strategy'],
                'evidence_note': r['evidence_note'],
                'source_sentence': r['source_text'],
                'target_sentence': r['target_text']
            })

    conn.close()
    return {
        "success": True,
        "book": book,
        "patterns": patterns,
        "equivalences": equivalences,
        "matrix": grid,
        "row_totals": row_totals,
        "col_totals": col_totals,
        "grand_total": grand_total,
        "drilldown": drilldown_items
    }

def calculate_cohens_kappa():
    conn = get_db()
    cur = conn.cursor()

    # Find occurrences annotated by both 'admin' and 'reviewer'
    cur.execute('''
        SELECT 
            a1.occurrence_id,
            a1.equivalence_type as cat1,
            a2.equivalence_type as cat2
        FROM phd_annotations a1
        JOIN phd_annotations a2 ON a1.occurrence_id = a2.occurrence_id
        WHERE a1.annotator_user = 'admin' AND a2.annotator_user = 'reviewer'
    ''')
    pairs = cur.fetchall()
    conn.close()

    n = len(pairs)
    if n == 0:
        return {
            "success": True,
            "shared_count": 0,
            "cohens_kappa": None,
            "interpretation": "Ikki annotator tomonidan birgalikda belgilangan yozuvlar mavjud emas (kamida 1 ta umumiy yozuv talab qilinadi).",
            "observed_agreement": None,
            "expected_agreement": None
        }

    # Count categories
    cats = [
        'toliq_ekvivalent', 'qisman_ekvivalent', 'strukturaviy_transformatsiya',
        'obraz_almashtirish', 'tasviriy_tarjima', 'bir_sozga_siqilgan',
        'tushirib_qoldirilgan', 'tarjimada_qoshilgan'
    ]

    agree_count = sum(1 for p in pairs if p['cat1'] == p['cat2'])
    p_o = agree_count / n

    freq1 = {c: 0 for c in cats}
    freq2 = {c: 0 for c in cats}
    for p in pairs:
        if p['cat1'] in freq1: freq1[p['cat1']] += 1
        if p['cat2'] in freq2: freq2[p['cat2']] += 1

    p_e = sum((freq1[c] / n) * (freq2[c] / n) for c in cats)

    if p_e == 1.0:
        kappa = 1.0
    else:
        kappa = (p_o - p_e) / (1.0 - p_e)

    # Landis & Koch scale
    if kappa < 0:
        interp = "Muvofiqlik yo‘q (Poor agreement)"
    elif kappa <= 0.20:
        interp = "Juda past muvofiqlik (Slight agreement)"
    elif kappa <= 0.40:
        interp = "Qoniqarli muvofiqlik (Fair agreement)"
    elif kappa <= 0.60:
        interp = "O‘rtacha muvofiqlik (Moderate agreement)"
    elif kappa <= 0.80:
        interp = "Yetarli darajada yuqori muvofiqlik (Substantial agreement)"
    else:
        interp = "Deyarli to‘liq bir xil muvofiqlik (Almost perfect agreement)"

    return {
        "success": True,
        "shared_count": n,
        "agree_count": agree_count,
        "observed_agreement": round(p_o, 4),
        "expected_agreement": round(p_e, 4),
        "cohens_kappa": round(kappa, 4),
        "interpretation": interp
    }

def get_ai_suggestion_for_occurrence(occ_id):
    # Rule 6: clearly labeled "taklif", admin-only, never writes statistics or confirmed labels, never receives full book text
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT o.id, o.book_id, c.surface_form_en, c.surface_form_uz, a.source_text, a.target_text
        FROM collocation_occurrences o
        JOIN collocation_candidates c ON o.candidate_id = c.id
        JOIN alignments a ON o.alignment_id = a.id
        WHERE o.id = ?
    ''', (occ_id,))
    r = cur.fetchone()
    conn.close()

    if not r:
        return {"success": False, "error": "Occurrence topilmadi"}

    is_cholpon = 'cholpon' in r['book_id']
    src_phrase = r['surface_form_uz'] if is_cholpon else r['surface_form_en']
    tgt_phrase = r['surface_form_en'] if is_cholpon else r['surface_form_uz']

    # Heuristic suggestion for single occurrence:
    return {
        "success": True,
        "occurrence_id": occ_id,
        "is_ai_suggestion": True,
        "label": "AI Taklifi (Loyiha / Faqat tavsiya)",
        "suggested_values": {
            "unit_type": "kollokatsiya",
            "structural_pattern": "Fel+Ot" if any(k in src_phrase.lower() for k in ['moq', 'ish', 'take', 'fish', 'make', 'do']) else "Sifat+Ot",
            "semantic_group": "inson_ruhiyati" if any(k in src_phrase.lower() for k in ['heart', 'ko‘ngil', 'yurak', 'alam', 'qayg‘u']) else "tabiat_borliq",
            "equivalence_type": "toliq_ekvivalent" if tgt_phrase.lower() in r['target_text'].lower() else "qisman_ekvivalent",
            "translation_strategy": "kalka" if tgt_phrase.lower() in r['target_text'].lower() else "modulyatsiya",
            "confidence_level": "orta",
            "evidence_note": "AI taklifi: faqat ushbu parallel jumla asosida shakllantirilgan qoralama. Inson tasdig‘i talab qilinadi."
        }
    }
