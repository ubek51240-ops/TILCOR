import sys, os, pymupdf, re
sys.stdout.reconfigure(encoding='utf-8')

pdf_dir = r'C:\Users\user\Downloads\Telegram Desktop'

def test_cholpon_uz(pno):
    doc = pymupdf.open(os.path.join(pdf_dir, 'cholpon-kecha-va-kunduz.pdf'))
    t = doc[pno - 1].get_text()
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    headers = []
    footers = []
    body = []
    page_num = None
    
    # Process top lines
    idx = 0
    while idx < min(4, len(lines)):
        l = lines[idx]
        if 'Abdulhamid Cho‘lpon' in l or 'Kecha va kunduz' in l or 'ziyouz.com' in l:
            headers.append(l)
            idx += 1
        elif re.match(r'^\d+$', l):
            page_num = int(l)
            idx += 1
        else:
            break
            
    body = lines[idx:]
    print(f"[Cholpon UZ p.{pno}] PNum: {page_num} | Headers: {headers} | Body lines: {len(body)}")
    if body:
        print(f"  First body line: {body[0][:60]}")
        print(f"  Last body line:  {body[-1][:60]}")

def test_cholpon_en(pno):
    doc = pymupdf.open(os.path.join(pdf_dir, 'night-and-day-a-novel-9781644690482_compress-pages.pdf'))
    t = doc[pno - 1].get_text()
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    headers = []
    footers = []
    page_num = None
    
    idx = 0
    while idx < min(4, len(lines)):
        l = lines[idx]
        if re.match(r'^\d+$', l):
            page_num = int(l)
            idx += 1
        elif l in ['Night and Day', 'Night and Day: Night', 'Night', 'First Book', 'Second Book', 'Glossary'] or re.match(r'^(?:Night and Day|Night|Glossary).*$', l):
            headers.append(l)
            idx += 1
        else:
            break
            
    cand_body = lines[idx:]
    body = []
    # Check bottom for footnotes
    b_idx = len(cand_body) - 1
    found_footnotes = []
    while b_idx >= 0 and b_idx >= len(cand_body) - 6:
        l = cand_body[b_idx]
        if re.match(r'^\d+[\t\s]+', l):
            # footnote start
            found_footnotes = cand_body[b_idx:]
            cand_body = cand_body[:b_idx]
            break
        b_idx -= 1
        
    print(f"[Cholpon EN p.{pno}] PNum: {page_num} | Headers: {headers} | Footnotes: {len(found_footnotes)} | Body: {len(cand_body)}")
    if cand_body:
        print(f"  First body line: {cand_body[0][:60]}")
        print(f"  Last body line:  {cand_body[-1][:60]}")
    if found_footnotes:
        print(f"  Footnote sample: {found_footnotes[0][:60]}")

def test_stevenson_en(pno):
    doc = pymupdf.open(os.path.join(pdf_dir, 'treasure island.pdf'))
    t = doc[pno - 1].get_text()
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    headers = []
    footers = []
    page_num = None
    
    idx = 0
    while idx < min(3, len(lines)):
        l = lines[idx]
        if 'Treasure Island-Robert Louis Stevenson' in l:
            headers.append(l)
            idx += 1
        else:
            break
            
    cand_body = lines[idx:]
    clean_body = []
    for l in cand_body:
        if l in ['Treasure Island', 'Robert Louis Stevenson']:
            footers.append(l)
        elif re.match(r'^Page\s+(\d+)/\d+$', l):
            m = re.match(r'^Page\s+(\d+)/\d+$', l)
            page_num = int(m.group(1))
            footers.append(l)
        else:
            clean_body.append(l)
            
    print(f"[Stevenson EN p.{pno}] PNum: {page_num} | Headers: {headers} | Footers: {footers} | Body: {len(clean_body)}")
    if clean_body:
        print(f"  First body: {clean_body[0][:60]}")
        print(f"  Last body:  {clean_body[-1][:60]}")

test_cholpon_uz(3)
test_cholpon_uz(10)
test_cholpon_uz(136)

test_cholpon_en(3)
test_cholpon_en(4)
test_cholpon_en(10)

test_stevenson_en(3)
test_stevenson_en(10)
test_stevenson_en(70)
