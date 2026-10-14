import os
import sys
import json
import re
import pymupdf
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES_DIR = os.path.join(DIRECTORY, 'sources')
DATA_DIR = os.path.join(DIRECTORY, 'data')

def check_all_page_coverage():
    raw = json.load(open(os.path.join(DATA_DIR, 'raw_extracted_v2.json'), encoding='utf-8'))
    
    coverage_report = {}

    # 1. KVK-UZ
    doc_uz = pymupdf.open(os.path.join(SOURCES_DIR, "cholpon-kecha-va-kunduz.pdf"))
    segs_uz = defaultdict(list)
    for s in raw['kvk_uz']: segs_uz[s['page']].append(s['text'])
    
    uz_res, uz_below = [], []
    for pno in range(2, 265):
        pnum = pno + 1
        lines = doc_uz[pno].get_text("text").split('\n')
        cleaned = [ls for l in lines if (ls := l.strip()) and "Abdulhamid Cho‘lpon" not in ls and "ziyouz.com" not in ls and ls != str(pnum)]
        p_toks = len(re.findall(r'\b\w+\b', " ".join(cleaned)))
        s_toks = len(re.findall(r'\b\w+\b', " ".join(segs_uz[pnum])))
        cov = (s_toks / p_toks * 100.0) if p_toks > 0 else 100.0
        rec = {"page": pnum, "pdf_tokens": p_toks, "seg_tokens": s_toks, "coverage_pct": round(cov, 2)}
        uz_res.append(rec)
        if cov < 98.0: uz_below.append(rec)
    coverage_report['kvk_uz'] = {"total_pages": len(uz_res), "below_98_count": len(uz_below), "below_98": uz_below}

    # 2. KVK-EN
    doc_ken = pymupdf.open(os.path.join(SOURCES_DIR, "night-and-day-a-novel-9781644690482_compress-pages.pdf"))
    segs_ken = defaultdict(list)
    for s in raw['kvk_en']: segs_ken[s['page']].append(s['text'])

    ken_res, ken_below = [], []
    for idx in range(2, 229): # PDF pp 3 to 229 (printed 45 to 271)
        pnum = 45 + (idx - 2)
        lines = doc_ken[idx].get_text("text").split('\n')
        body = []
        is_fn = False
        for l in lines:
            ls = l.strip()
            if not ls or re.match(r"^(?:\d+\s+Night and Day|Night and Day\s+\d+|\d+\s+Night|Night\s+\d+|Night and Day|Night|First Book|Second Book|\d{2,3})$", ls):
                continue
            if re.match(r"^(?:[\u2002\s]*\d+\s+\t?|[0-9]+\s+[A-Z])", ls) and (len(body) > 15 or is_fn):
                is_fn = True
            if not is_fn:
                l_clean = re.sub(r'(?<=[a-zA-Z])(\d+)\b', '', l)
                l_clean = re.sub(r'(?<=[a-zA-Z][.,;:?”"’])(\d+)\b', '', l_clean)
                body.append(l_clean)
        text_body = "\n".join(body)
        text_body = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text_body)
        p_toks = len(re.findall(r'\b\w+\b', text_body))
        s_toks = len(re.findall(r'\b\w+\b', " ".join(segs_ken[pnum])))
        cov = (s_toks / p_toks * 100.0) if p_toks > 0 else 100.0
        rec = {"page": pnum, "pdf_tokens": p_toks, "seg_tokens": s_toks, "coverage_pct": round(cov, 2)}
        ken_res.append(rec)
        if cov < 98.0: ken_below.append(rec)
    coverage_report['kvk_en'] = {"total_pages": len(ken_res), "below_98_count": len(ken_below), "below_98": ken_below}

    # 3. OMS-EN
    segs_oen = defaultdict(list)
    for s in raw['oms_en']: segs_oen[s['page']].append(s['text'])
    oen_res, oen_below = [], []
    for pnum in range(9, 126): # [9] to [125]
        s_toks = len(re.findall(r'\b\w+\b', " ".join(segs_oen[pnum])))
        rec = {"page": pnum, "seg_tokens": s_toks}
        oen_res.append(rec)
        if s_toks == 0: oen_below.append(rec)
    coverage_report['oms_en'] = {"total_pages": len(oen_res), "missing_pages": len(oen_below)}

    # 4. OMS-UZ
    doc_ouz = pymupdf.open(os.path.join(SOURCES_DIR, "Chol_va_dengiz__Ernst.pdf"))
    segs_ouz = defaultdict(list)
    for s in raw['oms_uz']: segs_ouz[s['page']].append(s['text'])

    ouz_res, ouz_below = [], []
    for pno in range(0, 46):
        pnum = pno + 1
        raw_t = doc_ouz[pno].get_text("text")
        if pno == 0:
            start_anchor = "Chol qayiqda yolg‘iz o‘zi Golfstrimda baliq ovlardi"
            pos = raw_t.find(start_anchor)
            if pos != -1: raw_t = raw_t[pos:]
        lines = raw_t.split('\n')
        cleaned = [ls for l in lines if (ls := l.strip()) and "Ernest Xeminguey" not in ls and "kutubxonachi.uz" not in ls and ls != str(pnum)]
        p_toks = len(re.findall(r'\b\w+\b', " ".join(cleaned)))
        s_toks = len(re.findall(r'\b\w+\b', " ".join(segs_ouz[pnum])))
        cov = (s_toks / p_toks * 100.0) if p_toks > 0 else 100.0
        rec = {"page": pnum, "pdf_tokens": p_toks, "seg_tokens": s_toks, "coverage_pct": round(cov, 2)}
        ouz_res.append(rec)
        if cov < 98.0: ouz_below.append(rec)
    coverage_report['oms_uz'] = {"total_pages": len(ouz_res), "below_98_count": len(ouz_below), "below_98": ouz_below}

    print("\n" + "="*70)
    print("PAGE COVERAGE SUMMARY TABLE ACROSS ALL 4 TEXTS:")
    print("="*70)
    print(f"1. KVK-UZ (*Kecha va kunduz*, pp 3-265): {len(uz_res)} pages | Pages below 98%: {len(uz_below)}")
    print(f"2. KVK-EN (*Night and Day*, pp 45-271):  {len(ken_res)} pages | Pages below 98%: {len(ken_below)}")
    print(f"3. OMS-EN (*The Old Man and the Sea*, [9]-[125]): {len(oen_res)} pages | Missing pages: {len(oen_below)}")
    print(f"4. OMS-UZ (*Chol va dengiz*, pp 1-46):   {len(ouz_res)} pages | Pages below 98%: {len(ouz_below)}")

    # Save to data/page_coverage_v3.json
    out_path = os.path.join(DATA_DIR, 'page_coverage_v3.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(coverage_report, f, indent=2, ensure_ascii=False)
    print(f"\n[+] Stored coverage table to {out_path}")

    return coverage_report

if __name__ == '__main__':
    check_all_page_coverage()
