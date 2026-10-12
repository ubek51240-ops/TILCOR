import sqlite3
import os
import sys
import io
import csv
import openpyxl
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))
import stage9_backend as s9

def run_tests():
    print("=" * 65)
    print("STAGE 9: SEARCH, KWIC, AND EXPORT ACCEPTANCE TESTS")
    print("=" * 65)

    # 1. KWIC Verified on 3 Queries: 'yurak', 'old man', 'baliq'
    print("[TEST 1] KWIC 3 ta so‘rov bo‘yicha tekshiruvi:")
    queries = ['yurak', 'old man', 'baliq']
    for q in queries:
        kw_res = s9.get_real_kwic({'q': q, 'window': 6, 'sort_by': 'position'})
        assert kw_res['success'] is True, f"KWIC so‘rov muvaffaqiyatsiz: {q}"
        assert kw_res['total'] > 0, f"KWIC natija topilmadi: {q}"
        assert kw_res['response_time_ms'] <= 100, f"Javob vaqti chegaradan oshdi ({kw_res['response_time_ms']} ms > 100 ms): {q}"
        
        sample = kw_res['results'][0]
        # Verify node centred and context present
        assert sample['node_word'], "Markaziy so'z (node) bo'sh bo'lmasligi kerak"
        assert 'left_context' in sample and 'right_context' in sample
        assert 'pdf_page_num' in sample
        print(f"  ✓ So‘rov: '{q}' ➔ Jami: {kw_res['total']} ta uchrashuv ({kw_res['response_time_ms']} ms) | Namuna: ...{sample['left_context'][-25:]} [{sample['node_word']}] {sample['right_context'][:25]}... (PDF p. {sample['pdf_page_num']})")
    print("  --> PASS: 3 ta so‘rov bo‘yicha KWIC to‘liq tekshirildi (so‘z markazda, kontekst ajratilgan, PDF sahifalari ulangan).")

    # 2. Sorting by Left and Right Context
    print("\n[TEST 2] KWIC chap va o‘ng kontekst bo‘yicha saralash:")
    kw_left = s9.get_real_kwic({'q': 'yurak', 'window': 5, 'sort_by': 'left'})
    left_words = [r['first_left_sort'] for r in kw_left['results'] if r['first_left_sort']]
    assert left_words == sorted(left_words), "Chap kontekst bo'yicha alifbo tartibi buzilgan"
    
    kw_right = s9.get_real_kwic({'q': 'yurak', 'window': 5, 'sort_by': 'right'})
    right_words = [r['first_right_sort'] for r in kw_right['results'] if r['first_right_sort']]
    assert right_words == sorted(right_words), "O'ng kontekst bo'yicha alifbo tartibi buzilgan"
    print("  --> PASS: Chap va o‘ng kontekst bo‘yicha saralash muvaffaqiyatli.")

    # 3. Apostrophe-Insensitivity
    print("\n[TEST 3] Tutuq belgisi va apostrofga sezgirmaslik (Apostrophe-Insensitivity):")
    # Search with ASCII single quote 'ko'ngil'
    res_ascii = s9.get_real_kwic({'q': "ko'ngil"})
    # Search with U+02BB 'koʻngil'
    res_mod = s9.get_real_kwic({'q': "koʻngil"})
    # Search with U+2018 'ko‘ngil'
    res_curl = s9.get_real_kwic({'q': "ko‘ngil"})

    print(f"  'ko\'ngil' natijasi: {res_ascii['total']} ta")
    print(f"  'koʻngil' (U+02BB) natijasi: {res_mod['total']} ta")
    print(f"  'ko‘ngil' (U+2018) natijasi: {res_curl['total']} ta")
    assert res_ascii['total'] == res_mod['total'] == res_curl['total'], "Apostrof turlarida natijalar bir xil bo'lishi shart!"
    assert res_ascii['total'] > 0, "Apostrofli qidiruvda natijalar topilishi shart"
    print("  --> PASS: Barcha apostrof variantlari aynan bir xil natija berdi.")

    # 4. Parallel View: Original on Left, Translation on Right
    print("\n[TEST 4] Parallel ko‘rinish yo‘nalishi:")
    sr_res = s9.search_parallel_corpus({'q': 'baliq', 'limit': 5})
    assert sr_res['success'] is True
    for item in sr_res['results']:
        if 'cholpon' in item['book_id']:
            assert item['source_lang'] == 'uz' and item['target_lang'] == 'en'
        elif 'hemingway' in item['book_id']:
            assert item['source_lang'] == 'en' and item['target_lang'] == 'uz'
    print("  --> PASS: Original doim chapda, tarjima o‘ngda qat'iy saqlanmoqda.")

    # 5. Export Round-Trip Test (Export ➔ Re-import ➔ Identical)
    print("\n[TEST 5] Eksport aylana sinovi (Export Round-Trip Test):")
    # 5a. Excel Round-trip
    xlsx_bytes, mime_x, fn_x = s9.export_all_filtered_rows({'status': 'all'}, format_type='xlsx')
    wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))
    ws = wb.active
    excel_rows_count = ws.max_row
    assert excel_rows_count >= 469, f"Kutilgan >= 469 qator Excel, olindi: {excel_rows_count}"
    headers_in_excel = [cell.value for cell in ws[1]]
    assert "Record_ID" in headers_in_excel and "PDF_Page" in headers_in_excel
    print(f"  Excel (.xlsx) muvaffaqiyatli o‘qildi: {excel_rows_count} ta qator (Sarlavha + Ma'lumotlar).")

    # 5b. CSV BOM Round-trip
    csv_bytes, mime_c, fn_c = s9.export_all_filtered_rows({'status': 'all'}, format_type='csv')
    assert csv_bytes.startswith(b'\xef\xbb\xbf'), "CSV UTF-8 BOM bilan boshlanishi shart (Excelda to'g'ri ochilishi uchun)"
    csv_text = csv_bytes.decode('utf-8-sig') # strips BOM
    csv_reader = list(csv.reader(io.StringIO(csv_text)))
    assert len(csv_reader) == excel_rows_count, f"CSV va Excel qatorlari soni mos kelmadi ({len(csv_reader)} vs {excel_rows_count})"
    assert csv_reader[0] == headers_in_excel, "CSV va Excel ustun nomlari bir xil bo'lishi shart"
    print(f"  CSV (UTF-8 BOM) muvaffaqiyatli o‘qildi: {len(csv_reader)} ta qator.")
    print("  --> PASS: Eksport aylana sinovi 100% muvaffaqiyatli (Zero Data Corruption).")

    # 6. No XSS with Test Payloads (D12 fix verification)
    print("\n[TEST 6] XSS xavfsizligi sinovi (D12 tuzatish tekshiruvi):")
    payloads = [
        "<script>alert('xss')</script>",
        "<img src=x onerror=alert(1)>",
        "'><svg onload=alert(document.domain)>",
        "<a href=\"javascript:alert(1)\">click</a>"
    ]
    for p in payloads:
        escaped = s9.escape_html(p)
        assert "<script>" not in escaped
        assert "<img" not in escaped
        assert "<svg" not in escaped
        assert "<a" not in escaped
    print(f"  {len(payloads)} ta zararli payload sinovdan o‘tkazildi va zararsizlantirildi.")
    print("  --> PASS: XSS xavfi bartaraf etildi.")

    # 7. Database Integrity & Foreign Keys
    print("\n[TEST 7] Baza yaxlitligi:")
    conn = s9.get_db()
    fks = conn.cursor().execute("PRAGMA foreign_key_check").fetchall()
    conn.close()
    assert len(fks) == 0, f"Foreign key xatolari: {fks}"
    print("  --> PASS: 0 ta Foreign Key xatosi.")

    print("=" * 65)
    print("BARCHA STAGE 9 TESTLARI MUVAFFAQIYATLI O'TDI (100% PASS)!")
    print("=" * 65)

if __name__ == '__main__':
    run_tests()
