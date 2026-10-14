"""
scripts/prototype_10_pages_extraction.py
Prototype extraction of 10 pages per file across the 4 registered sources:
- KVK-UZ (PDF pp 3-12)
- KVK-EN (PDF pp 45-54)
- OMS-EN (PDF pp 2-11)
- OMS-UZ (PDF pp 3-12)
Separates page furniture (headers, footers, printed page numbers, footnotes).
Outputs structured JSON and preview HTML without touching live corpus (3,811 segments).
"""

import fitz # PyMuPDF
import re
import os
import sys
import json
import html

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('.')
from word_family import uz_norm

SOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sources')
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'staging')
os.makedirs(OUT_DIR, exist_ok=True)

# 1. KVK-UZ: cholpon-kecha-va-kunduz.pdf
def extract_kvk_uz(doc, start_p=3, count=10):
    results = []
    for p in range(start_p - 1, start_p - 1 + count):
        page = doc[p]
        text = page.get_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        running_header = None
        running_footer = None
        printed_page = None
        body_lines = []
        
        for line in lines:
            if 'Abdulhamid Cho‘lpon' in line or 'Kecha va kunduz' in line:
                running_header = line
                continue
            if 'www.ziyouz.com kutubxonasi' in line:
                running_footer = line
                m = re.search(r'(\d+)$', line)
                if m:
                    printed_page = int(m.group(1))
                continue
            body_lines.append(line)
            
        # Join lines handling soft hyphens
        raw_body = " ".join(body_lines)
        raw_body = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', raw_body)
        
        # Segment sentences
        sentences = [s.strip() for s in re.split(r'(?<=[.!?…])\s+', raw_body) if len(s.strip()) > 5]
        
        results.append({
            "pdf_page": p + 1,
            "printed_page": printed_page,
            "running_header": running_header,
            "running_footer": running_footer,
            "segments_count": len(sentences),
            "segments": sentences[:5] # sample
        })
    return results

# 2. KVK-EN: night-and-day-a-novel-9781644690482_compress-pages.pdf
def extract_kvk_en(doc, start_p=45, count=10):
    results = []
    for p in range(start_p - 1, start_p - 1 + count):
        page = doc[p]
        text = page.get_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        running_header = None
        printed_page = None
        footnotes = []
        body_lines = []
        
        for line in lines:
            if line.isdigit() and len(line) <= 3:
                printed_page = int(line)
                continue
            if 'NIGHT AND DAY' in line or 'PART ONE' in line:
                running_header = line
                continue
            # Footnotes: lines starting with number
            if re.match(r'^\d+\s+[A-Z]', line) and len(line) > 20:
                footnotes.append(line)
                continue
            body_lines.append(line)
            
        raw_body = " ".join(body_lines)
        raw_body = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', raw_body)
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+(?=[A-Z“"])', raw_body) if len(s.strip()) > 5]
        
        results.append({
            "pdf_page": p + 1,
            "printed_page": printed_page,
            "running_header": running_header,
            "footnotes": footnotes,
            "segments_count": len(sentences),
            "segments": sentences[:5]
        })
    return results

# 3. OMS-EN: oldmansea.pdf
def extract_oms_en(doc, start_p=2, count=10):
    results = []
    for p in range(start_p - 1, start_p - 1 + count):
        page = doc[p]
        text = page.get_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        running_header = None
        printed_pages_found = []
        body_lines = []
        
        for line in lines:
            if 'Asiaing.com' in line or 'The Old Man and the Sea' in line:
                running_header = line
                continue
            # Extract [9], [10] markers
            m_pages = re.findall(r'\[(\d+)\]', line)
            if m_pages:
                printed_pages_found.extend([int(x) for x in m_pages])
            # Clean markers from body
            clean_l = re.sub(r'\[\d+\]', '', line).strip()
            if clean_l:
                body_lines.append(clean_l)
                
        raw_body = " ".join(body_lines)
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+(?=[A-Z“"])', raw_body) if len(s.strip()) > 5]
        
        results.append({
            "pdf_page": p + 1,
            "printed_pages": printed_pages_found,
            "running_header": running_header,
            "segments_count": len(sentences),
            "segments": sentences[:5]
        })
    return results

# 4. OMS-UZ: Chol_va_dengiz__Ernst.pdf
def extract_oms_uz(doc, start_p=3, count=10):
    results = []
    for p in range(start_p - 1, start_p - 1 + count):
        page = doc[p]
        text = page.get_text()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        running_header = None
        printed_page = None
        body_lines = []
        
        for line in lines:
            if 'Ernest Xeminguey' in line or 'Chol va dengiz' in line:
                running_header = line
                continue
            if line.isdigit() and len(line) <= 2:
                printed_page = int(line)
                continue
            body_lines.append(line)
            
        raw_body = " ".join(body_lines)
        raw_body = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', raw_body)
        sentences = [s.strip() for s in re.split(r'(?<=[.!?…])\s+', raw_body) if len(s.strip()) > 5]
        
        results.append({
            "pdf_page": p + 1,
            "printed_page": printed_page,
            "running_header": running_header,
            "segments_count": len(sentences),
            "segments": sentences[:5]
        })
    return results

print("Extracting 10 pages prototype for 4 files...")

doc_kvk_uz = fitz.open(os.path.join(SOURCES_DIR, 'cholpon-kecha-va-kunduz.pdf'))
doc_kvk_en = fitz.open(os.path.join(SOURCES_DIR, 'night-and-day-a-novel-9781644690482_compress-pages.pdf'))
doc_oms_en = fitz.open(os.path.join(SOURCES_DIR, 'oldmansea.pdf'))
doc_oms_uz = fitz.open(os.path.join(SOURCES_DIR, 'Chol_va_dengiz__Ernst.pdf'))

kvk_uz_res = extract_kvk_uz(doc_kvk_uz, 3, 10)
kvk_en_res = extract_kvk_en(doc_kvk_en, 45, 10)
oms_en_res = extract_oms_en(doc_oms_en, 2, 10)
oms_uz_res = extract_oms_uz(doc_oms_uz, 3, 10)

all_results = {
    "KVK-UZ": kvk_uz_res,
    "KVK-EN": kvk_en_res,
    "OMS-EN": oms_en_res,
    "OMS-UZ": oms_uz_res
}

with open(os.path.join(OUT_DIR, 'extraction_prototype_10pp.json'), 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print("Prototype JSON saved to staging/extraction_prototype_10pp.json")
