import fitz
import re

# 1. KVK-UZ: pages 3 to 265
doc_uz = fitz.open("sources/cholpon-kecha-va-kunduz.pdf")
print("KVK-UZ total pages:", len(doc_uz))
# Sample page 3 footer and header
p3 = doc_uz[2].get_text("text")
lines_p3 = [l.strip() for l in p3.split("\n") if l.strip()]
print("KVK-UZ p3 first 3 lines:", lines_p3[:3])
print("KVK-UZ p3 last 3 lines:", lines_p3[-3:])

# Sample page 265
p265 = doc_uz[264].get_text("text")
lines_p265 = [l.strip() for l in p265.split("\n") if l.strip()]
print("KVK-UZ p265 last 3 lines:", lines_p265[-3:])

# 2. KVK-EN: PDF pages 3 to 229 (indices 2 to 228)
doc_en = fitz.open("sources/cholpon-night-and-day.pdf")
print("\nKVK-EN total pages:", len(doc_en))
p_en_first = doc_en[2].get_text("text")
lines_en_first = [l.strip() for l in p_en_first.split("\n") if l.strip()]
print("KVK-EN PDF p3 (idx 2) first 3 lines:", lines_en_first[:3])
print("KVK-EN PDF p3 last 3 lines:", lines_en_first[-3:])

p_en_last = doc_en[228].get_text("text")
lines_en_last = [l.strip() for l in p_en_last.split("\n") if l.strip()]
print("KVK-EN PDF p229 (idx 228) first 3 lines:", lines_en_last[:3])
print("KVK-EN PDF p229 last 3 lines:", lines_en_last[-3:])

# 3. OMS-EN
doc_oms_en = fitz.open("sources/hemingway-the-old-man-and-the-sea.pdf")
print("\nOMS-EN total pages:", len(doc_oms_en))
p_oms_en1 = doc_oms_en[0].get_text("text")
lines_oms_en1 = [l.strip() for l in p_oms_en1.split("\n") if l.strip()]
print("OMS-EN p1 first 5 lines:", lines_oms_en1[:5])

# 4. OMS-UZ
doc_oms_uz = fitz.open("sources/hemingway-chol-va-dengiz.pdf")
print("\nOMS-UZ total pages:", len(doc_oms_uz))
p_oms_uz3 = doc_oms_uz[2].get_text("text")
lines_oms_uz3 = [l.strip() for l in p_oms_uz3.split("\n") if l.strip()]
print("OMS-UZ p3 first 3 lines:", lines_oms_uz3[:3])
print("OMS-UZ p3 last 3 lines:", lines_oms_uz3[-3:])
