import pymupdf
import re
from word_family import uz_norm

def count_uzbek_pdf(pdf_path, start_page_1based, end_page_1based):
    doc = pymupdf.open(pdf_path)
    full_text = []
    for pno in range(start_page_1based - 1, end_page_1based):
        text = doc[pno].get_text("text")
        full_text.append(text)
    combined = "\n".join(full_text)
    norm_text = uz_norm(combined)
    
    # regexes
    c_qaror = len(re.findall(r"\bqaror[a-z\u02bb\u02bc]*\b", norm_text))
    c_yurak = len(re.findall(r"\b(?:yurak|yurag)[a-z\u02bb\u02bc]*\b", norm_text))
    c_qishloq = len(re.findall(r"\b(?:qishloq|qishlog\u02bb)[a-z\u02bb\u02bc]*\b", norm_text))
    c_kongil = len(re.findall(r"\b(?:ko\u02bbngil|ko\u02bbngl)[a-z\u02bb\u02bc]*\b", norm_text))
    return {
        "qaror": c_qaror,
        "yurak": c_yurak,
        "qishloq": c_qishloq,
        "ko'ngil": c_kongil
    }

def count_english_pdf(pdf_path, start_page_1based, end_page_1based):
    doc = pymupdf.open(pdf_path)
    full_text = []
    for pno in range(start_page_1based - 1, end_page_1based):
        text = doc[pno].get_text("text")
        # filter footnotes if KVK-EN
        lines = text.split("\n")
        clean_lines = []
        for line in lines:
            # strip headers
            if re.match(r"^(?:\d+\s+Night|Night and Day\s+\d+|Night\s+\d+|\d+\s+Night and Day)$", line.strip()):
                continue
            clean_lines.append(line)
        full_text.append("\n".join(clean_lines))
    combined = "\n".join(full_text).lower()
    c_heart = len(re.findall(r"\bheart[a-z]*\b", combined))
    c_decide = len(re.findall(r"\b(?:decid[a-z]*|decision[a-z]*)\b", combined))
    return {
        "heart": c_heart,
        "decid/decision": c_decide
    }

print("1. KVK-UZ (pp 3-265):", count_uzbek_pdf("sources/cholpon-kecha-va-kunduz.pdf", 3, 265))
print("2. KVK-EN (PDF pp 3-229):", count_english_pdf("sources/night-and-day-a-novel-9781644690482_compress-pages.pdf", 3, 229))
print("3. OMS-EN (PDF pp 1-52):", count_english_pdf("sources/oldmansea.pdf", 1, 52))
print("4. OMS-UZ (pp 3-46):", count_uzbek_pdf("sources/Chol_va_dengiz__Ernst.pdf", 3, 46))
