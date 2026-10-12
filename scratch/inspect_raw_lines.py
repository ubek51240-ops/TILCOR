import pymupdf

uz_pdf = pymupdf.open(r'C:\Users\user\Downloads\Telegram Desktop\cholpon-kecha-va-kunduz.pdf')
en_pdf = pymupdf.open(r'C:\Users\user\Downloads\Telegram Desktop\night-and-day-a-novel-9781644690482_compress-pages.pdf')

print("--- RAW UZ PAGE 4 (first 6 lines) ---")
for l in uz_pdf[3].get_text().splitlines()[:8]:
    print(repr(l))

print("\n--- RAW EN PAGE 4 (first 8 lines) ---")
for l in en_pdf[3].get_text().splitlines()[:10]:
    print(repr(l))

print("\n--- RAW EN PAGE 5 (first 8 lines) ---")
for l in en_pdf[4].get_text().splitlines()[:10]:
    print(repr(l))
