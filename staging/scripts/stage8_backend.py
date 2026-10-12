import sqlite3
import os
import sys
import math
import json
import io
import csv

sys.stdout.reconfigure(encoding='utf-8')

DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(DIRECTORY, 'data', 'phd_corpus.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_corpus_sizes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT s.book_id, b.title, b.role, s.language, s.total_tokens, s.total_types,
               s.type_token_ratio, s.hapax_legomena, s.tokenizer_rule
        FROM corpus_statistics_snapshot s
        JOIN books b ON s.book_id = b.id
        ORDER BY b.role DESC, s.total_tokens DESC
    ''')
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    total_active_tokens = sum(r['total_tokens'] for r in rows if r['total_tokens'] > 0)
    total_active_types = sum(r['total_types'] for r in rows if r['total_types'] > 0)

    return {
        "success": True,
        "texts": rows,
        "total_active_tokens": total_active_tokens,
        "total_active_types": total_active_types,
        "formula_normalized": "NormFreq = (RawFreq / N) * 10000",
        "tokenizer_rule": r"\b[\w\u02bb\u02bc'-]+\b (kichik harfga keltirilgan, tutuq belgilari saqlangan)"
    }

def get_association_measures(params):
    conn = get_db()
    cur = conn.cursor()

    min_f = int(params.get('min_f', 3))
    lang = params.get('lang', 'all')
    q = params.get('q', '').strip().lower()
    page = max(1, int(params.get('page', 1)))
    limit = max(1, min(100, int(params.get('limit', 25))))

    where_clauses = ["o11 >= ?"]
    args = [min_f]

    if lang != 'all':
        where_clauses.append("language = ?")
        args.append(lang)

    if q:
        where_clauses.append("(node_token LIKE ? OR collocate_token LIKE ?)")
        wild = f"%{q}%"
        args.extend([wild, wild])

    where_str = " AND ".join(where_clauses)

    count_sql = f"SELECT count(*) FROM association_measures WHERE {where_str}"
    cur.execute(count_sql, args)
    total = cur.fetchone()[0]

    offset = (page - 1) * limit
    select_sql = f'''
        SELECT id, candidate_id, language, node_token, collocate_token,
               o11, o12, o21, o22, r1, c1, corpus_size_n, expected_e11,
               mi_score, t_score, log_likelihood_g2, normalized_freq_per_10k
        FROM association_measures
        WHERE {where_str}
        ORDER BY log_likelihood_g2 DESC, mi_score DESC
        LIMIT ? OFFSET ?
    '''
    args.extend([limit, offset])
    cur.execute(select_sql, args)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    return {
        "success": True,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "min_f_threshold": min_f,
        "results": rows,
        "academic_note": "MI ko‘rsatkichi kam uchraydigan (kamchilik) so‘z birikmalariga yuqori ball berishga moyil; t-score esa yuqori chastotali grammatik kollokatsiyalarni afzal ko‘radi. Shu sababli Dunning Log-Likelihood (G2) umumiy korpus uchun asosiy mezon hisoblanadi (1.1 va 2.2-fasllar)."
    }

def calculate_single_contingency(o11, r1, c1, N):
    if o11 <= 0 or r1 <= 0 or c1 <= 0 or N <= 0 or o11 > r1 or o11 > c1 or r1 > N or c1 > N:
        return {"success": False, "error": "Noto‘g‘ri kirish sonlari (o11 <= r1, c1 <= N bo‘lishi shart)"}

    o12 = r1 - o11
    o21 = c1 - o11
    o22 = N - r1 - c1 + o11

    e11 = (r1 * c1) / N
    e12 = (r1 * (N - c1)) / N
    e21 = ((N - r1) * c1) / N
    e22 = ((N - r1) * (N - c1)) / N

    mi = math.log2((o11 * N) / (r1 * c1))
    t_score = (o11 - e11) / math.sqrt(o11)

    cells = [(o11, e11), (o12, e12), (o21, e21), (o22, e22)]
    g2 = 0.0
    for o, e in cells:
        if o > 0 and e > 0:
            g2 += 2.0 * o * math.log(o / e)

    norm_10k = (o11 / N) * 10000.0

    return {
        "success": True,
        "inputs": {"o11": o11, "r1": r1, "c1": c1, "N": N},
        "contingency_table": {
            "o11": o11, "o12": o12, "row1_total": r1,
            "o21": o21, "o22": o22, "row2_total": N - r1,
            "col1_total": c1, "col2_total": N - c1, "grand_total_N": N
        },
        "expected_frequencies": {
            "e11": round(e11, 4), "e12": round(e12, 4),
            "e21": round(e21, 4), "e22": round(e22, 4)
        },
        "metrics": {
            "mi_score": round(mi, 4),
            "t_score": round(t_score, 4),
            "log_likelihood_g2": round(g2, 4),
            "norm_freq_per_10k": round(norm_10k, 4)
        }
    }

def get_chapter3_tables():
    conn = get_db()
    cur = conn.cursor()

    # Query ONLY confirmed annotations (Prompt 8 Rule 3)
    cur.execute('''
        SELECT 
            pa.id, pa.occurrence_id, pa.structural_pattern, pa.semantic_group,
            pa.equivalence_type, pa.translation_strategy, pa.is_cultural,
            pa.cultural_category, pa.confidence_level,
            o.book_id
        FROM phd_annotations pa
        JOIN collocation_occurrences o ON pa.occurrence_id = o.id
        WHERE pa.is_confirmed = 1
    ''')
    rows = cur.fetchall()
    conn.close()

    total_confirmed = len(rows)
    if total_confirmed == 0:
        return {
            "success": True,
            "total_confirmed": 0,
            "denominator_text": "n = 0 (Hech qanday tasdiqlangan annotatsiya mavjud emas)",
            "tables": {}
        }

    # Split by book / direction
    cholpon_rows = [r for r in rows if 'cholpon' in r['book_id']]
    hemingway_rows = [r for r in rows if 'hemingway' in r['book_id']]

    n_total = total_confirmed
    n_chol = len(cholpon_rows)
    n_hem = len(hemingway_rows)

    def dist_table(key_col):
        # Collect distinct values
        vals = sorted(list(set(r[key_col] for r in rows if r[key_col])))
        items = []
        for v in vals:
            c_chol = sum(1 for r in cholpon_rows if r[key_col] == v)
            p_chol = round((c_chol / n_chol) * 100, 2) if n_chol > 0 else 0.0

            c_hem = sum(1 for r in hemingway_rows if r[key_col] == v)
            p_hem = round((c_hem / n_hem) * 100, 2) if n_hem > 0 else 0.0

            c_tot = sum(1 for r in rows if r[key_col] == v)
            p_tot = round((c_tot / n_total) * 100, 2)

            items.append({
                "category": v,
                "cholpon_count": c_chol,
                "cholpon_pct": p_chol,
                "cholpon_repr": f"{c_chol} ({p_chol}%, n={n_chol})",
                "hemingway_count": c_hem,
                "hemingway_pct": p_hem,
                "hemingway_repr": f"{c_hem} ({p_hem}%, n={n_hem})",
                "total_count": c_tot,
                "total_pct": p_tot,
                "total_repr": f"{c_tot} ({p_tot}%, n={n_total})"
            })
        return items

    table_3_1 = dist_table('structural_pattern')
    table_3_2 = dist_table('semantic_group')
    table_3_3 = dist_table('equivalence_type')
    table_3_4 = dist_table('translation_strategy')
    table_3_5 = dist_table('cultural_category')

    # Cross-tabulation: Structural Pattern x Equivalence Type
    patterns = sorted(list(set(r['structural_pattern'] for r in rows)))
    equivs = sorted(list(set(r['equivalence_type'] for r in rows)))
    cross_grid = []
    for p in patterns:
        row_dict = {"pattern": p, "cells": {}, "row_total": 0}
        for eq in equivs:
            cnt = sum(1 for r in rows if r['structural_pattern'] == p and r['equivalence_type'] == eq)
            pct = round((cnt / n_total) * 100, 2)
            row_dict["cells"][eq] = {"count": cnt, "pct": pct, "repr": f"{cnt} ({pct}%, n={n_total})"}
            row_dict["row_total"] += cnt
        cross_grid.append(row_dict)

    # Dispersion analysis
    # Percentage difference between UZ->EN and EN->UZ distributions
    dispersion = []
    for item in table_3_1:
        diff = abs(item['cholpon_pct'] - item['hemingway_pct'])
        dispersion.append({
            "pattern": item['category'],
            "cholpon_pct": item['cholpon_pct'],
            "hemingway_pct": item['hemingway_pct'],
            "dispersion_delta": round(diff, 2),
            "direction_dominant": "UZ ➔ EN" if item['cholpon_pct'] > item['hemingway_pct'] else "EN ➔ UZ"
        })

    return {
        "success": True,
        "total_confirmed_n": n_total,
        "n_cholpon": n_chol,
        "n_hemingway": n_hem,
        "denominators": {
            "total": f"n = {n_total}",
            "cholpon_uz_en": f"n = {n_chol}",
            "hemingway_en_uz": f"n = {n_hem}"
        },
        "tables": {
            "table_3_1_patterns": table_3_1,
            "table_3_2_semantics": table_3_2,
            "table_3_3_equivalence": table_3_3,
            "table_3_4_strategies": table_3_4,
            "table_3_5_culture": table_3_5,
            "table_3_6_cross_tabulation": cross_grid,
            "dispersion_patterns": dispersion
        },
        "settings_snapshot": {
            "corpus_version": "v2.0",
            "guideline_version": "v1.0",
            "taxonomy_version": "1.0",
            "confirmed_filter_applied": True,
            "unconfirmed_excluded": True,
            "generated_at": "2026-10-12T16:40:00+05:00"
        }
    }

def export_chapter3_data(format_type='json'):
    data = get_chapter3_tables()
    if format_type == 'json':
        return json.dumps(data, indent=2, ensure_ascii=False), "application/json", "chapter3_statistical_tables_snapshot.json"
    
    # CSV format
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["# TILCOR v2.0 Chapter III Statistical Tables Export"])
    writer.writerow([f"# Total Confirmed Denominator: {data['denominators']['total']}"])
    writer.writerow([f"# Settings Snapshot: {json.dumps(data['settings_snapshot'])}"])
    writer.writerow([])

    # Table 3.1
    writer.writerow(["--- TABLE 3.1: STRUKTUR QOLIPLAR TAQSIMOTI ---"])
    writer.writerow(["Struktur Qolip", "Cho'lpon (UZ->EN) Son", "Cho'lpon %", "Hemingway (EN->UZ) Son", "Hemingway %", "Jami Son", "Jami %", "Denominator"])
    for r in data['tables'].get('table_3_1_patterns', []):
        writer.writerow([r['category'], r['cholpon_count'], r['cholpon_pct'], r['hemingway_count'], r['hemingway_pct'], r['total_count'], r['total_pct'], f"n={data['total_confirmed_n']}"])
    writer.writerow([])

    # Table 3.3
    writer.writerow(["--- TABLE 3.3: EKVIVALENTLIK TURLARI TAQSIMOTI ---"])
    writer.writerow(["Ekvivalentlik Turi", "Cho'lpon (UZ->EN) Son", "Cho'lpon %", "Hemingway (EN->UZ) Son", "Hemingway %", "Jami Son", "Jami %", "Denominator"])
    for r in data['tables'].get('table_3_3_equivalence', []):
        writer.writerow([r['category'], r['cholpon_count'], r['cholpon_pct'], r['hemingway_count'], r['hemingway_pct'], r['total_count'], r['total_pct'], f"n={data['total_confirmed_n']}"])
    writer.writerow([])

    # Table 3.4
    writer.writerow(["--- TABLE 3.4: TARJIMA STRATEGIYALARI TAQSIMOTI ---"])
    writer.writerow(["Strategiya", "Cho'lpon (UZ->EN) Son", "Cho'lpon %", "Hemingway (EN->UZ) Son", "Hemingway %", "Jami Son", "Jami %", "Denominator"])
    for r in data['tables'].get('table_3_4_strategies', []):
        writer.writerow([r['category'], r['cholpon_count'], r['cholpon_pct'], r['hemingway_count'], r['hemingway_pct'], r['total_count'], r['total_pct'], f"n={data['total_confirmed_n']}"])

    return output.getvalue(), "text/csv; charset=utf-8", "chapter3_statistical_tables.csv"
