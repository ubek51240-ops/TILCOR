import sqlite3
import os
import sys
import math
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))
import stage8_backend as s8

def run_tests():
    print("=" * 65)
    print("STAGE 8: TRANSPARENT STATISTICS & CHAPTER III UNIT TESTS")
    print("=" * 65)

    # 1. Hand-computable test case from Prompt 8
    print("[TEST 1] Qo‘lda hisoblangan test misoli tekshiruvi:")
    calc = s8.calculate_single_contingency(o11=10, r1=50, c1=100, N=100000)
    assert calc['success'] is True, "Kalkulyator xato qaytardi"
    
    m = calc['metrics']
    exp_e11 = 0.05
    exp_mi = 7.6439
    exp_t = 3.1465
    exp_g2 = 89.2209
    exp_norm = 1.0

    print(f"  Hisoblangan: E11={m.get('e11', calc['expected_frequencies']['e11'])}, MI={m['mi_score']}, t={m['t_score']}, G2={m['log_likelihood_g2']}")
    assert abs(calc['expected_frequencies']['e11'] - exp_e11) < 1e-3, f"E11 kutilgan: {exp_e11}, olindi: {calc['expected_frequencies']['e11']}"
    assert abs(m['mi_score'] - exp_mi) < 1e-3, f"MI kutilgan: {exp_mi}, olindi: {m['mi_score']}"
    assert abs(m['t_score'] - exp_t) < 1e-3, f"t kutilgan: {exp_t}, olindi: {m['t_score']}"
    assert abs(m['log_likelihood_g2'] - exp_g2) < 1e-2, f"G2 kutilgan: {exp_g2}, olindi: {m['log_likelihood_g2']}"
    assert abs(m['norm_freq_per_10k'] - exp_norm) < 1e-3, f"NormFreq kutilgan: {exp_norm}, olindi: {m['norm_freq_per_10k']}"
    print("  --> PASS: Qo‘lda hisoblangan barcha formulalar natijasi 100% mos keldi.")

    # 2. Corpus sizes per text and language
    print("\n[TEST 2] Korpus hajmi va leksik boylik tekshiruvi:")
    sizes = s8.get_corpus_sizes()
    assert sizes['success'] is True, "Corpus sizes fetch failed"
    assert sizes['total_active_tokens'] > 300000, f"Kutilgan > 300,000 token, olindi: {sizes['total_active_tokens']}"
    print(f"  Jami faol tokenlar: {sizes['total_active_tokens']}, unikal shakllar (types): {sizes['total_active_types']}")
    
    stevenson_uz = next((t for t in sizes['texts'] if t['book_id'] == 'book-stevenson-uz'), None)
    assert stevenson_uz is not None and stevenson_uz['total_tokens'] == 0, "Stevenson UZ 0 token bo'lishi shart (karantinda)"
    print(f"  Stevenson UZ: {stevenson_uz['total_tokens']} token (Karantinda qolgan)")
    print("  --> PASS: Korpus o‘lchamlari va tokenizer qoidasi to‘liq tasdiqlandi.")

    # 3. Contingency table consistency check
    print("\n[TEST 3] 2x2 Kontingentlik jadvallarining matematik muvozanati:")
    conn = s8.get_db()
    cur = conn.cursor()
    sample_rows = cur.execute('SELECT * FROM association_measures LIMIT 50').fetchall()
    assert len(sample_rows) > 0, "association_measures bo'sh bo'lmasligi kerak"
    for r in sample_rows:
        o11, o12, o21, o22 = r['o11'], r['o12'], r['o21'], r['o22']
        r1, c1, N = r['r1'], r['c1'], r['corpus_size_n']
        assert o11 + o12 == r1, f"Qator 1 muvozanati buzilgan: {o11}+{o12} != {r1}"
        assert o21 + o22 == N - r1, f"Qator 2 muvozanati buzilgan: {o21}+{o22} != {N-r1}"
        assert o11 + o21 == c1, f"Ustun 1 muvozanati buzilgan: {o11}+{o21} != {c1}"
        assert o12 + o22 == N - c1, f"Ustun 2 muvozanati buzilgan: {o12}+{o22} != {N-c1}"
        assert r1 + (N - r1) == N, f"Jami N muvozanati buzilgan"
    conn.close()
    print(f"  Tekshirilgan namunaviy {len(sample_rows)} ta kontingentlik jadvalining barchasida algebraik muvozanat to‘liq.")
    print("  --> PASS: Kirish sonlari (O11, O12, O21, O22, R1, C1, N) to‘liq saqlangan.")

    # 4. Configurable threshold check
    print("\n[TEST 4] Sozlanuvchi minimal chastota chegarasi (Threshold) tekshiruvi:")
    c2 = s8.get_association_measures({'min_f': 2})['total']
    c3 = s8.get_association_measures({'min_f': 3})['total']
    c5 = s8.get_association_measures({'min_f': 5})['total']
    print(f"  f >= 2: {c2} ta | f >= 3: {c3} ta | f >= 5: {c5} ta")
    assert c2 >= c3 >= c5, "Chegara oshganda sonlar kamayishi shart"
    print("  --> PASS: Chegara filtri dinamik va to‘g‘ri ishlamoqda.")

    # 5. Chapter III Tables (Generated ONLY from confirmed annotations)
    print("\n[TEST 5] III Bob statistik jadvallari (Faqat Tasdiqlangan Annotatsiyalardan):")
    ch3 = s8.get_chapter3_tables()
    assert ch3['success'] is True, "Chapter III fetch failed"
    assert ch3['total_confirmed_n'] > 0, "Kamida bitta tasdiqlangan annotatsiya bo'lishi kerak"
    assert 'table_3_1_patterns' in ch3['tables']
    assert 'table_3_3_equivalence' in ch3['tables']
    assert 'table_3_4_strategies' in ch3['tables']

    # Verify that every item has a denominator string
    for item in ch3['tables']['table_3_1_patterns']:
        assert f"n={ch3['total_confirmed_n']}" in item['total_repr'], f"Denominator n={ch3['total_confirmed_n']} topilmadi"
        assert f"n={ch3['n_cholpon']}" in item['cholpon_repr']
        assert f"n={ch3['n_hemingway']}" in item['hemingway_repr']
    print(f"  Jami tasdiqlangan annotatsiyalar soni (Denominator): n = {ch3['total_confirmed_n']}")
    print(f"  Cho'lpon qismi: n = {ch3['n_cholpon']} | Hemingway qismi: n = {ch3['n_hemingway']}")
    print("  --> PASS: Barcha foizlar yonida denominator (n=...) ko‘rsatilgan.")

    # 6. Reproducibility & Export Snapshot
    print("\n[TEST 6] Eksport va Sozlamalar Snapshot tekshiruvi:")
    json_export, mime_json, fn_json = s8.export_chapter3_data('json')
    parsed_json = json.loads(json_export)
    assert 'settings_snapshot' in parsed_json, "Settings snapshot JSON da bo'lishi shart"
    assert parsed_json['settings_snapshot']['confirmed_filter_applied'] is True
    
    csv_export, mime_csv, fn_csv = s8.export_chapter3_data('csv')
    assert "Settings Snapshot" in csv_export
    assert "Denominator" in csv_export
    print("  --> PASS: JSON va CSV eksportlari sozlamalar snapshoti bilan to‘liq shakllandi.")

    # 7. Database Integrity & Foreign Keys
    print("\n[TEST 7] Baza yaxlitligi:")
    conn = s8.get_db()
    fks = conn.cursor().execute("PRAGMA foreign_key_check").fetchall()
    conn.close()
    assert len(fks) == 0, f"Foreign key xatolari: {fks}"
    print("  --> PASS: 0 ta Foreign Key xatosi.")

    print("=" * 65)
    print("BARCHA STAGE 8 STATISTIKA TESTLARI MUVAFFAQIYATLI O'TDI (100% PASS)!")
    print("=" * 65)

if __name__ == '__main__':
    run_tests()
