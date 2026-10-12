import fitz
import re
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. IELTS Academic Collocations List
doc_ielts = fitz.open(r'C:\Users\user\Downloads\IELTS-academic-collocations-list.pdf')
ielts_phrases = []
for p in range(len(doc_ielts)):
    text = doc_ielts[p].get_text()
    for line in text.split('\n'):
        line = line.strip()
        if not line or any(k in line for k in ['Pearson Education', 'IELTS academic', 'Photocopiable', 'Academic Collocations']):
            continue
        line = re.sub(r'\(an?\)\s*', '', line)
        line = re.sub(r'\(.*?\)', '', line).strip()
        words = line.split()
        if 2 <= len(words) <= 4 and not any(c.isdigit() for c in line) and len(line) >= 4:
            clean_p = ' '.join(words).lower()
            ielts_phrases.append(clean_p)

# 2. Cambridge Collocations in Use Intermediate
doc_inter = fitz.open(r'C:\Users\user\Downloads\Collocations in Use Intermediate [www.languagecentre.ir].pdf')
inter_phrases = []
current_head = ""
for p in range(160, len(doc_inter)):
    text = doc_inter[p].get_text()
    for line in text.split('\n'):
        line = line.strip()
        if not line or line.isdigit():
            continue
        if len(line.split()) == 1 and not line.startswith('~') and not any(c.isdigit() for c in line):
            current_head = line.lower()
            continue
        m = re.match(r'^([a-zA-Z\s\~\'\,\-]+)\s+\d+$', line)
        if m:
            phrase = m.group(1).strip().lower()
            if phrase.startswith('~') and current_head:
                phrase = phrase.replace('~', current_head).strip()
            phrase = re.sub(r'\(.*?\)', '', phrase).strip()
            words = phrase.split()
            if 2 <= len(words) <= 4 and not any(c.isdigit() for c in phrase) and len(phrase) >= 4:
                inter_phrases.append(' '.join(words))

# 3. 1000 English Collocations Ebook
doc_1000 = fitz.open(r'C:\Users\user\Downloads\1000-english-collocations-ebook.pdf')
ebook_phrases = []
for p in range(len(doc_1000)):
    page = doc_1000[p]
    d = page.get_text('dict')
    for block in d.get('blocks', []):
        for line in block.get('lines', []):
            line_bolds = []
            for span in line.get('spans', []):
                font = span.get('font', '').lower()
                flags = span.get('flags', 0)
                text = span.get('text', '').strip()
                if ('bold' in font or (flags & 2)) and text and not text.isdigit():
                    if not any(k in text.lower() for k in ['lesson', 'quiz', 'page', 'espresso', 'shayna', 'oliveira', 'copyright', 'circle', 'complete']):
                        line_bolds.append(text)
            if line_bolds:
                joined = ' '.join(line_bolds).strip()
                for sub in re.split(r'[,;/–—]', joined):
                    sub = re.sub(r'\(.*?\)', '', sub).strip()
                    sub = re.sub(r'^\d+[\.\)]\s*', '', sub).strip()
                    sub = sub.strip(' .!?:\"\'')
                    words = sub.split()
                    if 2 <= len(words) <= 4 and all(w.isalpha() for w in words) and len(sub) >= 5:
                        ebook_phrases.append(' '.join(words).lower())

# 4. Cambridge Collocations in Use Advanced
doc_adv = fitz.open(r'C:\Users\user\Downloads\English Collocation in Use 2nd Edition-Advanced.pdf')
adv_phrases = []
for p in range(5, len(doc_adv)):
    page = doc_adv[p]
    d = page.get_text('dict')
    for block in d.get('blocks', []):
        for line in block.get('lines', []):
            line_bolds = []
            for span in line.get('spans', []):
                font = span.get('font', '').lower()
                flags = span.get('flags', 0)
                text = span.get('text', '').strip()
                if ('bold' in font or (flags & 2)) and text and not text.isdigit():
                    if not any(k in text.lower() for k in ['unit', 'exercise', 'page', 'cambridge', 'zabanbook', 'table', 'section', 'contents', 'english', 'example', 'answers']):
                        line_bolds.append(text)
            if line_bolds:
                joined = ' '.join(line_bolds).strip()
                for sub in re.split(r'[,;/–—]', joined):
                    sub = re.sub(r'\(.*?\)', '', sub).strip()
                    sub = re.sub(r'^\d+[\.\)]\s*', '', sub).strip()
                    sub = sub.strip(' .!?:\"\'')
                    words = sub.split()
                    if 2 <= len(words) <= 4 and all(w.isalpha() for w in words) and len(sub) >= 5:
                        adv_phrases.append(' '.join(words).lower())

print("Natijalar:", flush=True)
print(f"IELTS: {len(ielts_phrases)} ta", flush=True)
print(f"Cambridge Intermediate: {len(inter_phrases)} ta", flush=True)
print(f"1000 Collocations Ebook: {len(ebook_phrases)} ta", flush=True)
print(f"Cambridge Advanced: {len(adv_phrases)} ta", flush=True)

all_unique = set(ielts_phrases + inter_phrases + ebook_phrases + adv_phrases)
print(f"Jami noyob kollokatsiyalar: {len(all_unique)} ta", flush=True)
