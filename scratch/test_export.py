import sqlite3
import io, csv

db_path = r'C:\Users\user\Desktop\tarjimon\data\phd_corpus.db'

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('''
    SELECT o.id as occ_id, c.surface_form_en, c.surface_form_uz,
           c.grammatical_pattern, c.semantic_group, c.equivalence_type,
           c.mi_score, c.t_score, c.log_dice,
           o.matched_span_en, o.matched_span_uz, o.translation_strategy,
           b.title as book_title, o.pdf_page_num,
           a.source_text, a.target_text
    FROM collocation_occurrences o
    JOIN collocation_candidates c ON o.candidate_id = c.id
    JOIN alignments a ON o.alignment_id = a.id
    JOIN books b ON o.book_id = b.id
    ORDER BY c.mi_score DESC
''')
rows = cursor.fetchall()
output = io.StringIO()
writer = csv.writer(output)
writer.writerow(['Occurrence_ID', 'Collocation_EN', 'Collocation_UZ', 'Pattern', 'Semantic_Group', 'Equivalence', 'MI', 'Book', 'Page'])
for r in rows[:5]:
    writer.writerow([r['occ_id'], r['surface_form_en'], r['surface_form_uz'], r['grammatical_pattern'], r['semantic_group'], r['equivalence_type'], r['mi_score'], r['book_title'], r['pdf_page_num']])

conn.close()
print("CSV Output Sample:")
print(output.getvalue())
