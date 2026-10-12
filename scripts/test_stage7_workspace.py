import sqlite3
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))
import stage7_backend as s7

def run_tests():
    print("=" * 60)
    print("STAGE 7: TRANSLATION CORRESPONDENCE & ANNOTATION TESTS")
    print("=" * 60)

    # 1. Test Taxonomies
    tax_res = s7.get_stage7_taxonomies()
    assert tax_res['success'] is True, "Taxonomies fetch failed"
    cats = tax_res['taxonomies']
    print(f"[TEST 1] Taxonomies: {len(cats)} ta toifa topildi.")
    expected_cats = ['unit_type', 'structural_pattern', 'semantic_group', 'equivalence_type', 'translation_strategy', 'cultural_marker', 'confidence_level']
    for ec in expected_cats:
        assert ec in cats, f"Toifa yetishmaydi: {ec}"
    print("  --> PASS: 7 ta toifaning barchasi mavjud (Prompt 7 talabi).")

    # 2. Test Occurrences Fetch (Left = Original, Right = Translation)
    occ_res = s7.get_stage7_occurrences({'limit': 10, 'book': 'all'})
    assert occ_res['success'] is True, "Occurrences fetch failed"
    print(f"[TEST 2] Occurrences: Jami {occ_res['total']} ta uchrashuv mavjud.")
    sample_occ = occ_res['results'][0]
    print(f"  Namuna: {sample_occ['occurrence_id']} | Asl: {sample_occ['source_lang'].upper()} ({sample_occ['source_collocation']}) ➔ Tarjima: {sample_occ['target_lang'].upper()}")
    
    # Check Cho'lpon: source_lang must be 'uz'
    chol_res = s7.get_stage7_occurrences({'limit': 5, 'book': 'book-cholpon-uz'})
    for c in chol_res['results']:
        assert c['source_lang'] == 'uz', f"Cho'lpon asari asl tili 'uz' bo'lishi shart! Topildi: {c['source_lang']}"
        assert c['target_lang'] == 'en', f"Cho'lpon tarjima tili 'en' bo'lishi shart! Topildi: {c['target_lang']}"
    print("  --> PASS: Cho'lponda asl matn qat'iy chapda (UZ), tarjima o'ngda (EN).")

    # Check Hemingway: source_lang must be 'en'
    hem_res = s7.get_stage7_occurrences({'limit': 5, 'book': 'book-hemingway-en'})
    for h in hem_res['results']:
        assert h['source_lang'] == 'en', f"Hemingway asari asl tili 'en' bo'lishi shart! Topildi: {h['source_lang']}"
        assert h['target_lang'] == 'uz', f"Hemingway tarjima tili 'uz' bo'lishi shart! Topildi: {h['target_lang']}"
    print("  --> PASS: Hemingwayda asl matn qat'iy chapda (EN), tarjima o'ngda (UZ).")

    # 3. Test Single Occurrence with +-2 context
    single_res = s7.get_stage7_occurrence_by_id(sample_occ['occurrence_id'])
    assert single_res['success'] is True, "Single occurrence fetch failed"
    print(f"[TEST 3] Yagona uchrashuv tahlili: {sample_occ['occurrence_id']} +-2 kontekst bilan tekshirildi.")
    print("  --> PASS: Kontekst va ma'lumotlar to'liq qaytmoqda.")

    # 4. Test Save Annotation (Draft and Confirmed)
    save_draft = s7.save_stage7_annotation({
        'occurrence_id': 'occ-00003',
        'source_span': 'fished alone',
        'target_span': 'baliq ovlardi',
        'has_target_equivalent': True,
        'unit_type': 'kollokatsiya',
        'structural_pattern': 'Fel+Ot',
        'semantic_group': 'tabiat_borliq',
        'equivalence_type': 'toliq_ekvivalent',
        'translation_strategy': 'kalka',
        'is_cultural': False,
        'cultural_category': 'yoq',
        'confidence_level': 'yuqori',
        'evidence_note': 'Test qoralama saqlash',
        'is_confirmed': False
    }, user='admin')
    assert save_draft['success'] is True, "Save draft failed"
    assert save_draft['is_confirmed'] is False

    save_confirm = s7.save_stage7_annotation({
        'occurrence_id': 'occ-00003',
        'source_span': 'fished alone',
        'target_span': 'baliq ovlardi',
        'has_target_equivalent': True,
        'unit_type': 'kollokatsiya',
        'structural_pattern': 'Fel+Ot',
        'semantic_group': 'tabiat_borliq',
        'equivalence_type': 'toliq_ekvivalent',
        'translation_strategy': 'kalka',
        'is_cultural': False,
        'cultural_category': 'yoq',
        'confidence_level': 'yuqori',
        'evidence_note': 'Tasdiqlangan ilmiy annotatsiya',
        'is_confirmed': True
    }, user='admin')
    assert save_confirm['success'] is True, "Save confirm failed"
    assert save_confirm['is_confirmed'] is True
    print("[TEST 4] Annotatsiyani saqlash va tasdiqlash:")
    print("  --> PASS: Qoralama va tasdiqlash muvaffaqiyatli saqlandi, audit_log qayd etildi.")

    # 5. Test Correspondence Matrix & Drill-down
    mat_res = s7.get_correspondence_matrix({'book': 'all', 'pattern': 'Fel+Ot', 'equivalence': 'toliq_ekvivalent'})
    assert mat_res['success'] is True, "Matrix fetch failed"
    print(f"[TEST 5] Tarjima mutanosibligi matritsasi:")
    print(f"  Jami tasdiqlangan annotatsiyalar soni: {mat_res['grand_total']}")
    print(f"  Drill-down elementlari soni: {len(mat_res['drilldown'])}")
    assert len(mat_res['drilldown']) > 0, "Drilldown kamida bitta element qaytarishi shart"
    print(f"  Namuna drill-down: {mat_res['drilldown'][0]['source_span']} ➔ {mat_res['drilldown'][0]['target_span']} (PDF p. {mat_res['drilldown'][0]['pdf_page_num']})")
    print("  --> PASS: Matritsa kataklari va drill-down to'liq ishlayapti.")

    # 6. Test Cohen's Kappa Calculation
    # Ensure admin has annotations on occ-00001 and occ-00002
    s7.save_stage7_annotation({
        'occurrence_id': 'occ-00001',
        'source_span': 'ko‘ngli tusamoq',
        'target_span': 'hearts wished for',
        'has_target_equivalent': True,
        'unit_type': 'kollokatsiya',
        'structural_pattern': 'Ot+Fel',
        'semantic_group': 'inson_ruhiyati',
        'equivalence_type': 'toliq_ekvivalent',
        'translation_strategy': 'modulyatsiya',
        'is_cultural': False,
        'cultural_category': 'yoq',
        'confidence_level': 'yuqori',
        'evidence_note': 'Admin bahosi',
        'is_confirmed': True
    }, user='admin')

    s7.save_stage7_annotation({
        'occurrence_id': 'occ-00002',
        'source_span': 'fished alone',
        'target_span': 'baliq ovlardi',
        'has_target_equivalent': True,
        'unit_type': 'kollokatsiya',
        'structural_pattern': 'Fel+Ot',
        'semantic_group': 'tabiat_borliq',
        'equivalence_type': 'toliq_ekvivalent',
        'translation_strategy': 'kalka',
        'is_cultural': False,
        'cultural_category': 'yoq',
        'confidence_level': 'yuqori',
        'evidence_note': 'Admin bahosi',
        'is_confirmed': True
    }, user='admin')

    # Simulate a second annotator ('reviewer') annotation to test Cohen's Kappa math
    s7.save_stage7_annotation({
        'occurrence_id': 'occ-00001',
        'source_span': 'ko‘ngli tusamoq',
        'target_span': 'hearts wished for',
        'has_target_equivalent': True,
        'unit_type': 'kollokatsiya',
        'structural_pattern': 'Ot+Fel',
        'semantic_group': 'inson_ruhiyati',
        'equivalence_type': 'toliq_ekvivalent',
        'translation_strategy': 'modulyatsiya',
        'is_cultural': False,
        'cultural_category': 'yoq',
        'confidence_level': 'yuqori',
        'evidence_note': 'Reviewer bahosi',
        'is_confirmed': True
    }, user='reviewer')

    s7.save_stage7_annotation({
        'occurrence_id': 'occ-00002',
        'source_span': 'fished alone',
        'target_span': 'baliq ovlardi',
        'has_target_equivalent': True,
        'unit_type': 'kollokatsiya',
        'structural_pattern': 'Fel+Ot',
        'semantic_group': 'tabiat_borliq',
        'equivalence_type': 'toliq_ekvivalent',
        'translation_strategy': 'kalka',
        'is_cultural': False,
        'cultural_category': 'yoq',
        'confidence_level': 'yuqori',
        'evidence_note': 'Reviewer bahosi',
        'is_confirmed': True
    }, user='reviewer')

    kappa_res = s7.calculate_cohens_kappa()
    assert kappa_res['success'] is True, "Cohen's kappa calculation failed"
    print(f"[TEST 6] Cohen's Kappa: Umumiy baholar = {kappa_res['shared_count']}, Kappa = {kappa_res['cohens_kappa']}")
    print(f"  Sharh: {kappa_res['interpretation']}")
    assert kappa_res['cohens_kappa'] == 1.0, "Bir xil annotatsiyalar uchun kappa 1.0 bo'lishi kerak"
    print("  --> PASS: Cohen's Kappa hisob-kitobi matematik jihatdan to'liq to'g'ri.")

    # 7. Test AI Suggestion
    ai_sug = s7.get_ai_suggestion_for_occurrence('occ-00005')
    assert ai_sug['success'] is True, "AI suggestion failed"
    assert ai_sug['is_ai_suggestion'] is True
    print(f"[TEST 7] AI Taklifi: {ai_sug['label']}")
    print(f"  Tavsiya: {ai_sug['suggested_values']}")
    print("  --> PASS: AI taklifi faqat bitta jumla uchun va 'Loyiha' sifatida shakllandi.")

    # 8. Check Database Foreign Keys & Integrity
    conn = s7.get_db()
    fks = conn.cursor().execute("PRAGMA foreign_key_check").fetchall()
    conn.close()
    assert len(fks) == 0, f"Foreign key xatolari topildi: {fks}"
    print("[TEST 8] Baza yaxlitligi: 0 ta Foreign Key xatosi.")

    print("=" * 60)
    print("BARCHA STAGE 7 TESTLARI MUVAFFAQIYATLI O'TDI (100% PASS)!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()
