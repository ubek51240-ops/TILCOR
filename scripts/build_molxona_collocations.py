#!/usr/bin/env python3
"""scripts/build_molxona_collocations.py — Molxona / Animal Farm kollokatsiyalarini yaratish va yangilash.

356 ta sof kollokatsiya juftligi (Molxona_kollokatsiyalar_parallel_korpusi.docx):
- Har bir juftlik uchun O'zbekcha kitob (Molxona_kollokatsiyalar.pdf) va Inglizcha kitob (Animal_Farm_kollokatsiyalar.pdf)
  bo'yicha sahifa raqamlari aniqlanadi.
- Ilmiy mezonlar bo'yicha strukturaviy qolip (pattern) belgilanadi.
- public_visible: True qilib data/collocations_full.json fayliga integratsiya qilinadi.
"""

import os
import sys
import json
import re
import collections
import pymupdf
import docx

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES_DIR = os.path.join(BASE_DIR, 'sources')
DATA_DIR = os.path.join(BASE_DIR, 'data')

DOCX_PATH = os.path.join(SOURCES_DIR, 'Molxona_kollokatsiyalar_parallel_korpusi.docx')
UZ_PDF_PATH = os.path.join(SOURCES_DIR, 'Molxona_kollokatsiyalar.pdf')
EN_PDF_PATH = os.path.join(SOURCES_DIR, 'Animal_Farm_kollokatsiyalar.pdf')
COLLOC_JSON = os.path.join(DATA_DIR, 'collocations_full.json')

# 1. Load PDFs
print("[*] Kitob matnlarini yuklash...")
uz_pdf = pymupdf.open(UZ_PDF_PATH)
en_pdf = pymupdf.open(EN_PDF_PATH)

uz_pages = []
for pno in range(len(uz_pdf)):
    txt = uz_pdf[pno].get_text().lower()
    for ch in ['ʻ', '’', '‘', 'ʼ', '`']:
        txt = txt.replace(ch, "'")
    uz_pages.append((pno + 3, txt))  # Page 0 is printed page 3

en_pages = []
for pno in range(len(en_pdf)):
    txt = en_pdf[pno].get_text().lower()
    for ch in ['ʻ', '’', '‘', 'ʼ', '`']:
        txt = txt.replace(ch, "'")
    en_pages.append((pno + 1, txt))  # Page 0 is printed page 1

print(f"[+] UZ sahifalar: {len(uz_pages)}, EN sahifalar: {len(en_pages)}")

# 2. Linguistic pattern rules
ADJECTIVES = {
    'hosildor', 'tuban', 'kelgusi', 'umumiy', 'dahshatli', 'ko\'pchilik', 'xirilloq', 'hayajonli',
    'yovvoyi', 'sadoqatli', 'ulkan', 'qora', 'oq', 'qizil', 'sariq', 'yashil', 'yosh', 'qari',
    'og\'ir', 'yengil', 'chuqur', 'yuzaki', 'katta', 'kichik', 'yaxshi', 'yomon', 'yangilangan',
    'boshlang\'ich', 'oxirgi', 'so\'nggi', 'muqaddas', 'mashhur', 'muhim', 'qulay', 'noqulay',
    'shafqatsiz', 'tinch', 'osoyishta', 'zarur', 'kerakli', 'foydali', 'zararli', 'xavfli',
    'aqlli', 'ahmoqona', 'ajoyib', 'g\'alati', 'begona', 'haqiqiy', 'soxta', 'toza', 'iflos',
    'ochiq', 'yopiq', 'to\'liq', 'chala', 'qattiq', 'yumshoq', 'issiq', 'sovuq', 'shirin', 'achchiq',
    'boy', 'kambag\'al', 'kuchli', 'kuchsiz', 'zaif', 'baquvvat', 'uzoq', 'yaqin', 'tez', 'sekin',
    'birinchi', 'ikkinchi', 'uchinchi', 'yagona', 'barcha', 'butun', 'har', 'har xil', 'turli',
    'maxfiy', 'yashirin', 'ochko\'z', 'kamtar', 'g\'olib', 'mag\'lub', 'jonli', 'o\'lik',
    'mustaqil', 'erkin', 'teng', 'adolatli', 'adolatsiz', 'tarixiy', 'badiiy', 'ilmiy', 'tabiiy',
    'sun\'iy', 'doimiy', 'vaqtincha', 'oddiy', 'murakkab', 'tushunarli', 'noma\'lum', 'aniq'
}

ADVERBS = {
    'to\'satdan', 'birdaniga', 'zo\'r berib', 'astoydil', 'tezda', 'asta-sekin', 'asta',
    'ohista', 'butunlay', 'mutlaqo', 'juda', 'nihoyatda', 'orqaga', 'oldinga', 'yuqoriga', 'pastga'
}

def classify_collocation(uz, en):
    uz_l = uz.lower().strip()
    words = [w for w in re.findall(r"[\w']+", uz_l) if w not in ('va', 'ham', 'bir', 'bilan', 'uchun')]
    is_verb = any(uz_l.endswith(v) for v in ['moq', 'qilmoq', 'etmoq', 'bo\'lmoq', 'bermoq', 'olmoq', 'bormoq', 'kelmoq', 'qo\'ymoq', 'tushmoq', 'chiqmoq', 'ketmoq'])
    first_w = words[0] if words else ''
    if is_verb:
        if first_w in ADVERBS or first_w in ['zo\'r', 'astoydil', 'to\'satdan']:
            return "ravish + fe’l (Adv+V)"
        elif first_w in ADJECTIVES and len(words) == 2:
            return "sifat + fe’l"
        else:
            return "ot + fe’l (N+V)"
    else:
        if first_w in ADJECTIVES or first_w.endswith('li') or first_w.endswith('siz') or first_w.endswith('iy') or first_w.endswith('viy') or first_w.endswith('roq'):
            return "sifat + ot (Adj+N)"
        elif len(words) >= 2 and (words[-1].endswith('i') or words[-1].endswith('si') or words[0].endswith('ning')):
            return "ot + ot (N+N)"
        else:
            return "sifat + ot (Adj+N)"

# 3. Matchers
EN_IRR = {
    'go': ['go', 'goes', 'went', 'gone', 'going'],
    'have': ['have', 'has', 'had', 'having'],
    'give': ['give', 'gives', 'gave', 'given', 'giving'],
    'take': ['take', 'takes', 'took', 'taken', 'taking'],
    'fall': ['fall', 'falls', 'fell', 'fallen', 'falling'],
    'draw': ['draw', 'draws', 'drew', 'drawn', 'drawing'],
    'clear': ['clear', 'clears', 'cleared', 'clearing'],
    'put': ['put', 'puts', 'putting'],
    'lay': ['lay', 'lays', 'laid', 'laying'],
    'set': ['set', 'sets', 'setting'],
    'make': ['make', 'makes', 'made', 'making'],
    'keep': ['keep', 'keeps', 'kept', 'keeping'],
    'hold': ['hold', 'holds', 'held', 'holding'],
    'come': ['come', 'comes', 'came', 'coming'],
    'run': ['run', 'runs', 'ran', 'running'],
    'see': ['see', 'sees', 'saw', 'seen', 'seeing'],
    'know': ['know', 'knows', 'knew', 'known', 'knowing'],
    'think': ['think', 'thinks', 'thought', 'thinking'],
    'bring': ['bring', 'brings', 'brought', 'bringing'],
    'stand': ['stand', 'stands', 'stood', 'standing'],
    'lose': ['lose', 'loses', 'lost', 'losing'],
    'pay': ['pay', 'pays', 'paid', 'paying'],
    'lead': ['lead', 'leads', 'led', 'leading'],
    'break': ['break', 'breaks', 'broke', 'broken', 'breaking'],
    'spend': ['spend', 'spends', 'spent', 'spending'],
    'leave': ['leave', 'leaves', 'left', 'leaving'],
    'bear': ['bear', 'bears', 'bore', 'born', 'borne', 'bearing'],
    'wear': ['wear', 'wears', 'wore', 'worn', 'wearing'],
    'tear': ['tear', 'tears', 'tore', 'torn', 'tearing'],
    'catch': ['catch', 'catches', 'caught', 'catching'],
    'strike': ['strike', 'strikes', 'struck', 'striking'],
    'sing': ['sing', 'sings', 'sang', 'sung', 'singing'],
    'speak': ['speak', 'speaks', 'spoke', 'spoken', 'speaking'],
    'meet': ['meet', 'meets', 'met', 'meeting'],
    'feel': ['feel', 'feels', 'felt', 'feeling'],
    'hear': ['hear', 'hears', 'heard', 'hearing'],
    'sleep': ['sleep', 'sleeps', 'slept', 'sleeping'],
    'grow': ['grow', 'grows', 'grew', 'grown', 'growing'],
    'tell': ['tell', 'tells', 'told', 'telling'],
    'become': ['become', 'becomes', 'became', 'becoming'],
    'begin': ['begin', 'begins', 'began', 'begun', 'beginning'],
    'rise': ['rise', 'rises', 'rose', 'risen', 'rising'],
    'shake': ['shake', 'shakes', 'shook', 'shaken', 'shaking'],
    'throw': ['throw', 'throws', 'threw', 'thrown', 'throwing'],
    'fly': ['fly', 'flies', 'flew', 'flown', 'flying'],
    'drive': ['drive', 'drives', 'drove', 'driven', 'driving'],
    'fight': ['fight', 'fights', 'fought', 'fighting'],
    'win': ['win', 'wins', 'won', 'winning'],
    'write': ['write', 'writes', 'wrote', 'written', 'writing'],
    'shine': ['shine', 'shines', 'shone', 'shining'],
    'shoot': ['shoot', 'shoots', 'shot', 'shooting'],
    'shut': ['shut', 'shuts', 'shutting'],
    'wake': ['wake', 'wakes', 'woke', 'woken', 'waking'],
    'sweep': ['sweep', 'sweeps', 'swept', 'sweeping'],
    'cut': ['cut', 'cuts', 'cutting'],
    'cost': ['cost', 'costs', 'costing'],
    'sell': ['sell', 'sells', 'sold', 'selling'],
    'buy': ['buy', 'buys', 'bought', 'buying'],
    'send': ['send', 'sends', 'sent', 'sending'],
    'build': ['build', 'builds', 'built', 'building'],
    'overtake': ['overtake', 'overtakes', 'overtook', 'overtaken', 'overtaking'],
    'forsake': ['forsake', 'forsakes', 'forsook', 'forsaken', 'forsaking'],
    'arise': ['arise', 'arises', 'arose', 'arisen', 'arising'],
    'readjust': ['readjust', 'readjusts', 'readjusted', 'readjusting', 'readjustment'],
}

def clean_en_tokens(phrase):
    phrase = phrase.lower()
    for ch in ['ʻ', '’', '‘', 'ʼ', '`']:
        phrase = phrase.replace(ch, "'")
    raw = re.findall(r"[a-z]+", phrase)
    stopwords = {'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'from', 
                 'one', 'ones', 'his', 'her', 'their', 'its', 'my', 'our', 'is', 'are', 'was', 'were', 'be', 'been',
                 'sb', 'sth', 'somebody', 'something', 'oneself'}
    return [w for w in raw if w not in stopwords]

def get_en_variants(token):
    for base, forms in EN_IRR.items():
        if token in forms or token == base:
            return forms
    variants = {token}
    if token.endswith('ies') and len(token) > 4:
        variants.add(token[:-3] + 'y')
    if token.endswith('y') and len(token) > 2:
        variants.add(token[:-1] + 'ies')
    if token.endswith('es') and len(token) > 3:
        stem = token[:-2]
        variants.update([stem, stem + 'e', stem + 'ed', stem + 'ing'])
    if token.endswith('s') and len(token) > 3:
        stem = token[:-1]
        variants.update([stem, stem + 'ed', stem + 'ing'])
    if token.endswith('ed') and len(token) > 3:
        stem = token[:-2]
        variants.update([stem, stem + 'e', stem + 'ing', stem + 's'])
    if token.endswith('ing') and len(token) > 4:
        stem = token[:-3]
        variants.update([stem, stem + 'e', stem + 'ed', stem + 's'])
    if token.endswith('e'):
        variants.update([token + 'd', token[:-1] + 'ing', token + 's'])
    else:
        variants.update([token + 's', token + 'ed', token + 'ing'])
    return list(variants)

def match_en_pages(phrase):
    tokens = clean_en_tokens(phrase)
    if not tokens:
        return []
    var_lists = [get_en_variants(tok) for tok in tokens]
    found = []
    for pno, txt in en_pages:
        ok = True
        for vars_ in var_lists:
            pat = r'\b(?:' + '|'.join(re.escape(v) for v in vars_) + r')\b'
            if not re.search(pat, txt):
                ok = False
                break
        if ok:
            found.append(pno)
    return found

def clean_uz_tokens(phrase):
    phrase = phrase.lower()
    for ch in ['ʻ', '’', '‘', 'ʼ', '`']:
        phrase = phrase.replace(ch, "'")
    raw_tokens = re.findall(r"[\w']+", phrase)
    tokens = []
    for t in raw_tokens:
        if t.endswith('moq') and len(t) > 4:
            tokens.append(t[:-3])
        elif t.endswith('qilmoq') and len(t) > 7:
            tokens.append(t[:-6])
            tokens.append('qil')
        elif t.endswith('etmoq') and len(t) > 6:
            tokens.append(t[:-5])
            tokens.append('et')
        elif t.endswith('bo\'lmoq') and len(t) > 8:
            tokens.append(t[:-7])
            tokens.append('bo\'l')
        else:
            tokens.append(t)
    return [t for t in tokens if len(t) > 1 and t not in ('va', 'ham', 'bir')]

def match_uz_pages(phrase):
    tokens = clean_uz_tokens(phrase)
    if not tokens:
        return []
    found = []
    for pno, txt in uz_pages:
        ok = True
        for tok in tokens:
            stem = tok[:4] if len(tok) >= 5 else tok
            if not re.search(r'\b' + re.escape(stem), txt):
                ok = False
                break
        if ok:
            found.append(pno)
    if not found:
        # Fallback with hyphen split
        alt_tokens = [w for w in re.findall(r"[\w']+", phrase.replace('-', ' ').lower()) if len(w) > 2 and w not in ('va', 'ham', 'bir', 'moq')]
        if alt_tokens:
            for pno, txt in uz_pages:
                if all(re.search(r'\b' + re.escape(w[:4] if len(w) >= 5 else w), txt) for w in alt_tokens):
                    found.append(pno)
    return found

def format_pages_dict(found_pages):
    if not found_pages:
        return "—"
    unique_pages = sorted(list(dict.fromkeys(found_pages)))
    count = len(found_pages)
    if len(unique_pages) <= 5:
        p_str = ", ".join(str(p) for p in unique_pages)
    else:
        p_str = ", ".join(str(p) for p in unique_pages[:5]) + "..."
    return f"{p_str} ({count})"

# 4. Process DOCX and produce records
print("[*] DOCX jadvalidan kollokatsiyalarni o'qish...")
doc = docx.Document(DOCX_PATH)
table = doc.tables[0]

mol_records = []
for i in range(1, len(table.rows)):
    row_idx = int(table.rows[i].cells[0].text.strip())
    uz_text = table.rows[i].cells[1].text.strip()
    en_text = table.rows[i].cells[2].text.strip()
    
    pattern = classify_collocation(uz_text, en_text)
    uz_matches = match_uz_pages(uz_text)
    en_matches = match_en_pages(en_text)
    
    uz_p_str = format_pages_dict(uz_matches)
    en_p_str = format_pages_dict(en_matches)
    
    rec = {
        "id": f"col-mol-{row_idx:03d}",
        "class": "KORPUS",
        "category": "Badiiy korpus (tadqiqotchi belgilagan)",
        "sourceBook": "Asosiy Badiiy Korpus: Oruell: «Molxona» / «Animal Farm»",
        "sources": [
            "Jorj Oruell: «Molxona» (tr. Karim Bahriyev)",
            "George Orwell: «Animal Farm»"
        ],
        "sourceMeta": f"Oruell «Animal Farm» / «Molxona» (tr. K. Bahriyev), tadqiqotchi belgilagan juftliklar (DOCX, №{row_idx})",
        "review_status": f"Tadqiqotchi belgilagan (DOCX, MOL-{row_idx:03d})",
        "status": "active",
        "public_visible": True,
        "pattern": pattern,
        "uzbek": uz_text,
        "english": en_text,
        "pages": {
            "uz": uz_p_str,
            "en": en_p_str
        },
        "page_match": {
            "uz": "stem" if uz_matches else "none",
            "en": "stem" if en_matches else "none"
        },
        "example": None,
        "culturalNote": "",
        "semanticGroup": "",
        "literalTrap": "",
        "equivalenceType": "",
        "freq": None,
        "freq_display": None,
        "miScore": None,
        "miScore_display": None,
        "tScore": None,
        "tScore_display": None,
        "logLikelihood": None,
        "logLikelihood_display": None,
        "corpus_occurrences": None,
        "uzbek_variants": [],
        "isLingvocultural": False,
        "is_sample_100": False,
        "quality_checks": None,
        "rejection_reason": None,
        "repair_reason": None,
        "stats_status": None
    }
    mol_records.append(rec)

print(f"[+] Tayyorlangan yozuvlar: {len(mol_records)}")
uz_has = sum(1 for r in mol_records if r['pages']['uz'] != '—')
en_has = sum(1 for r in mol_records if r['pages']['en'] != '—')
print(f"[+] UZ sahifasi aniqlanganlar: {uz_has}/{len(mol_records)}")
print(f"[+] EN sahifasi aniqlanganlar: {en_has}/{len(mol_records)}")

# 5. Merge into data/collocations_full.json
print(f"[*] {COLLOC_JSON} yuklanmoqda...")
with open(COLLOC_JSON, 'r', encoding='utf-8') as f:
    existing = json.load(f)

# Filter out previous col-mol entries if any
clean_list = [r for r in existing if not str(r.get('id', '')).startswith('col-mol-')]
print(f"[*] Eski bazadan Molxonasiz qolgan yozuvlar: {len(clean_list)}")

# Append new mol_records
merged = clean_list + mol_records
print(f"[*] Yangi jami yozuvlar soni: {len(merged)}")

with open(COLLOC_JSON, 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"[✓] {COLLOC_JSON} muvaffaqiyatli saqlandi!")
