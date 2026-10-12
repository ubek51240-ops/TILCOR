import fitz, sys
sys.stdout.reconfigure(encoding='utf-8')

pdf_uz = 'C:/Users/user/Downloads/Telegram Desktop/Chol va dengiz ( Ernst).pdf'
doc_uz = fitz.open(pdf_uz)
print(f"UZ PDF opened: {doc_uz.page_count} pages.")

for p_num in range(3, 8):  # inspect pages 3 to 7
    page = doc_uz[p_num - 1] # 0-indexed
    text = page.get_text()
    print(f"\n--- UZ PAGE {p_num} (chars: {len(text)}) ---")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for l in lines[:6]:
        print("  ", l)
    print("   ...")
    for l in lines[-3:]:
        print("  ", l)

pdf_en = 'C:/Users/user/Downloads/Telegram Desktop/oldmansea.pdf'
doc_en = fitz.open(pdf_en)
print(f"\nEN PDF opened: {doc_en.page_count} pages.")
for p_num in range(3, 8):
    page = doc_en[p_num - 1]
    text = page.get_text()
    print(f"\n--- EN PAGE {p_num} (chars: {len(text)}) ---")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for l in lines[:6]:
        print("  ", l)
    print("   ...")
    for l in lines[-3:]:
        print("  ", l)
