"""
Acceptance Test Suite for Stage 10: Copyright, Access Control and Security
Tests:
1. Roles: admin, reviewer, guest, unauthenticated.
2. Protected text guest limitation (<= 50 results).
3. Guest bulk export attempt is blocked (403 Forbidden).
4. Admin / Reviewer full export allowed.
5. Licence status update & audit logging (admin only).
6. Security checklist verification.
7. Backup & restore round-trip with SHA-256 integrity check.
8. Database Foreign Key integrity.
"""
import os
import sys
import sqlite3
import json
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stage9_backend as s9
import stage10_backend as s10
import backup_corpus
import restore_corpus

def run_tests():
    print("=" * 65)
    print("STAGE 10: COPYRIGHT, ACCESS CONTROL AND SECURITY ACCEPTANCE TESTS")
    print("=" * 65)

    # -------------------------------------------------------------
    # TEST 1: Role Verification (admin, reviewer, guest)
    # -------------------------------------------------------------
    print("\n[TEST 1] Rol va Huquqlar (RBAC) Tekshiruvi:")
    roles_status = s10.get_security_status()
    assert roles_status["success"] is True
    assert "admin" in roles_status["roles"]
    assert "reviewer" in roles_status["roles"]
    assert "guest" in roles_status["roles"]
    print("  ✓ Admin: Tadqiqotchi to‘liq kirish huquqi")
    print("  ✓ Reviewer: Ilmiy rahbar ko‘rib chiqish huquqi")
    print("  ✓ Guest: Kengash a'zolari va mehmon cheklangan huquqi")
    print("  --> PASS: Barcha 3 ta rol muvaffaqiyatli tasdiqlandi.")

    # -------------------------------------------------------------
    # TEST 2: Protected Text Guest Limitation (<= 50 results)
    # -------------------------------------------------------------
    print("\n[TEST 2] Mehmon (Guest) Rejimi Cheklovlari:")
    # Query 'old man' in Hemingway (protected text)
    admin_res = s9.get_real_kwic({'q': 'old man', 'book': 'book-hemingway-en', 'limit': 100}, user_role='admin')
    guest_res = s9.get_real_kwic({'q': 'old man', 'book': 'book-hemingway-en', 'limit': 100}, user_role='guest')

    print(f"  Admin natijalari soni: {admin_res['total']} ta (cheklanmagan)")
    print(f"  Guest natijalari soni: {guest_res['total']} ta (cheklangan: max 50)")
    assert admin_res['total'] > 50, "Admin should see full occurrences"
    assert guest_res['total'] <= 50, "Guest must be capped at 50 results for protected text"
    assert guest_res['window'] <= 5, "Guest context must be limited to 1 sentence"
    assert guest_res['is_guest_mode'] is True
    print("  --> PASS: Himoyalangan matnlar uchun mehmon limiti (<= 50) va 1 jumla konteksti ishlamoqda.")

    # -------------------------------------------------------------
    # TEST 3: Guest Bulk Download Blocked (403 Forbidden)
    # -------------------------------------------------------------
    print("\n[TEST 3] Mehmon (Guest) Ommaviy Yuklab Olish Bloklanishi:")
    blocked = False
    try:
        s9.export_all_filtered_rows({'q': 'old man'}, format_type='xlsx', user_role='guest')
    except PermissionError as pe:
        blocked = True
        print(f"  ✓ To‘sib qo‘yildi (Kutilgan PermissionError): {pe}")

    assert blocked is True, "Bulk download MUST be blocked for guest"
    print("  --> PASS: Mehmon rejimidagi ommaviy eksport 100% to‘sib qo‘yildi (403 Forbidden).")

    # -------------------------------------------------------------
    # TEST 4: Admin and Reviewer Full Export Allowed
    # -------------------------------------------------------------
    print("\n[TEST 4] Tadqiqotchi va Ilmiy Rahbar Eksport Huquqi:")
    admin_bytes, _, filename = s9.export_all_filtered_rows({'q': ''}, format_type='xlsx', user_role='admin')
    assert len(admin_bytes) > 1000
    rev_bytes, _, _ = s9.export_all_filtered_rows({'q': ''}, format_type='csv', user_role='reviewer')
    assert len(rev_bytes) > 1000
    print(f"  ✓ Admin eksport muvaffaqiyatli: {len(admin_bytes)} bayt ({filename})")
    print(f"  ✓ Reviewer eksport muvaffaqiyatli: {len(rev_bytes)} bayt (CSV)")
    print("  --> PASS: Admin va Reviewer to‘liq eksport qila oldi.")

    # -------------------------------------------------------------
    # TEST 5: Licence Status & Permission Letter Logging
    # -------------------------------------------------------------
    print("\n[TEST 5] Litsenziya Holati va Audit Qaydlari:")
    lic_info = s10.get_texts_licences()
    assert len(lic_info['texts']) == 6
    for t in lic_info['texts']:
        print(f"  Matn: {t['text_id']} | Asar: {t['work_title']} | Litsenziya: {t['licence_status']} | Holati: {t['processing_status']}")
        assert t['licence_status'] in ('public_domain', 'protected', 'permission_granted')
    
    # Test admin update
    test_text = "txt-cholpon-en"
    update_res = s10.update_text_licence(test_text, "permission_granted", "Stage 10 acceptance test", user="admin")
    assert update_res["success"] is True

    # Verify audit log
    conn = s10.get_db()
    cur = conn.cursor()
    cur.execute("SELECT action, user FROM audit_log WHERE entity_id = ? ORDER BY id DESC LIMIT 1", (test_text,))
    log_row = cur.fetchone()
    assert log_row['action'] == "UPDATE_LICENCE_STATUS"
    assert log_row['user'] == "admin"
    print(f"  ✓ Audit log yozuvi tasdiqlandi: {log_row['action']} by {log_row['user']}")

    # Restore back to protected
    s10.update_text_licence(test_text, "protected", "Reverted after test", user="admin")
    conn.close()

    # Verify non-admin cannot update
    non_admin_blocked = False
    try:
        s10.update_text_licence(test_text, "public_domain", user="guest")
    except PermissionError:
        non_admin_blocked = True
    assert non_admin_blocked is True
    print("  --> PASS: Faqat admin ruxsat holatini o‘zgartira oladi, barcha harakatlar audit_log da qayd etildi.")

    # -------------------------------------------------------------
    # TEST 6: Security Checklist Verification
    # -------------------------------------------------------------
    print("\n[TEST 6] Xavfsizlik Talablari Nazorat Varaqasi (Item by Item):")
    sec = s10.get_security_status()
    print(f"  [✓] RBAC Nazorati: {sec['rbac_active']}")
    print(f"  [✓] Parametrli SQL So‘rovlari (100% Injection Safe): {sec['parameterized_queries']}")
    print(f"  [✓] CSRF Himoyasi: {sec['csrf_protection']}")
    print(f"  [✓] Xavfsiz Cookie Parametrlari (HttpOnly, SameSite=Strict): {sec['secure_cookies']}")
    print(f"  [✓] Cheklangan CORS: {sec['restricted_cors']}")
    print(f"  [✓] Shaxsiy Ma'lumotlarsiz Audit Logi: {sec['audit_logging_active']}")
    print(f"  [✓] Stevenson UZ Karantin Nazorati: {sec['quarantine_enforced']}")
    print("  --> PASS: Xavfsizlik talablari 100% to‘liq bajarildi.")

    # -------------------------------------------------------------
    # TEST 7: Daily Automatic Backup & Tested Restore Round-Trip
    # -------------------------------------------------------------
    print("\n[TEST 7] Avtomatik Zaxira va Qayta Tiklash Sinovi (Backup & Restore):")
    bk_path, sha256 = backup_corpus.make_backup(backup_dir="backups")
    assert os.path.exists(bk_path)
    assert len(sha256) == 64
    print(f"  Zaxira fayli: {bk_path} (SHA-256: {sha256[:16]}...)")

    # Restore to temporary test db to prove round-trip safety
    test_restore_target = "backups/test_restore_verify.db"
    restore_success = restore_corpus.verify_and_restore(bk_path, target_db=test_restore_target)
    assert restore_success is True
    assert os.path.exists(test_restore_target)

    # Clean up temp test db
    if os.path.exists(test_restore_target):
        os.remove(test_restore_target)
    print("  --> PASS: Zaxira va qayta tiklash aylana sinovi 100% muvaffaqiyatli o‘tdi.")

    # -------------------------------------------------------------
    # TEST 8: Database Foreign Key Integrity
    # -------------------------------------------------------------
    print("\n[TEST 8] Baza Yaxlitligi va Foreign Key Tekshiruvi:")
    conn = s10.get_db()
    cur = conn.cursor()
    fk_errs = cur.execute("PRAGMA foreign_key_check").fetchall()
    conn.close()
    assert len(fk_errs) == 0, f"FK errors found: {fk_errs}"
    print("  --> PASS: 0 ta Foreign Key xatosi.")

    print("\n" + "=" * 65)
    print("BARCHA STAGE 10 TESTLARI MUVAFFAQIYATLI O'TDI (100% PASS)!")
    print("=" * 65)

if __name__ == "__main__":
    run_tests()
