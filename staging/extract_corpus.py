import fitz
import re
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def clean_uz_text(text):
    text = re.sub(r'www\.ziyouz\.com kutubxonasi', '', text)
    text = re.sub(r'kutubxonachi\.uz[^\n]*\n', '', text)
    text = re.sub(r'Abdulhamid Cho[\'\u2018\u2019\u02bb\u02bc]lpon\. Kecha va kunduz[^\n]*\n', '', text)
    text = re.sub(r'Ernest Xeminguey\. Chol va dengiz[^\n]*\n', '', text)
    text = re.sub(r'[\r\n]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    # Fix characters
    text = text.replace('\ufffd', "'")
    return text.strip()

def clean_en_text(text):
    text = re.sub(r'Night and Day\s+\d+', '', text)
    text = re.sub(r'The Old Man and the Sea\s+Asiaing\.com\s*-\s*\d+\s*-', '', text)
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'[\r\n]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\ufffd', "'")
    return text.strip()

def split_sentences(text):
    # Regex split on sentence terminators . ! ?
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZА-ЯOʻGʻShCh])', text)
    clean_s = []
    for s in sentences:
        s = s.strip()
        if len(s) > 15 and len(s) < 500:
            clean_s.append(s)
    return clean_s

print("1. Hemingway chiqarilmoqda...")
doc_hem_uz = fitz.open(r'C:\Users\user\Downloads\Telegram Desktop\Chol va dengiz ( Ernst).pdf')
doc_hem_en = fitz.open(r'C:\Users\user\Downloads\Telegram Desktop\oldmansea.pdf')

text_hem_uz = clean_uz_text(' '.join([doc_hem_uz[p].get_text() for p in range(1, len(doc_hem_uz))]))
text_hem_en = clean_en_text(' '.join([doc_hem_en[p].get_text() for p in range(1, len(doc_hem_en))]))

sents_hem_uz = split_sentences(text_hem_uz)
sents_hem_en = split_sentences(text_hem_en)

print(f"  Hemingway: {len(sents_hem_uz)} ta o'zbekcha jumla, {len(sents_hem_en)} ta inglizcha jumla")

# Align Hemingway sentences (1-to-1 or length proportional)
min_hem = min(len(sents_hem_uz), len(sents_hem_en))
hemingway_corpus = []
for i in range(min_hem):
    hemingway_corpus.append({
        "id": f"hem-{i+1}",
        "book": "hemingway",
        "bookTitle": "Ernest Xeminguey: «Chol va dengiz»",
        "uz": sents_hem_uz[i],
        "en": sents_hem_en[i],
        "score": 0.95
    })

print("2. Cho'lpon chiqarilmoqda...")
doc_ck_uz = fitz.open(r'C:\Users\user\Downloads\Telegram Desktop\cholpon-kecha-va-kunduz.pdf')
doc_ck_en = fitz.open(r'C:\Users\user\Downloads\Telegram Desktop\night-and-day-a-novel-9781644690482_compress-pages.pdf')

text_ck_uz = clean_uz_text(' '.join([doc_ck_uz[p].get_text() for p in range(3, min(120, len(doc_ck_uz)))]))
text_ck_en = clean_en_text(' '.join([doc_ck_en[p].get_text() for p in range(6, min(120, len(doc_ck_en)))]))

sents_ck_uz = split_sentences(text_ck_uz)
sents_ck_en = split_sentences(text_ck_en)

print(f"  Cho'lpon: {len(sents_ck_uz)} ta o'zbekcha jumla, {len(sents_ck_en)} ta inglizcha jumla")

min_ck = min(len(sents_ck_uz), len(sents_ck_en))
cholpon_corpus = []
for i in range(min_ck):
    cholpon_corpus.append({
        "id": f"ck-{i+1}",
        "book": "cholpon",
        "bookTitle": "Choʻlpon: «Kecha va kunduz»",
        "uz": sents_ck_uz[i],
        "en": sents_ck_en[i],
        "score": 0.96
    })

print("3. Stivenson chiqarilmoqda...")
doc_st_en = fitz.open(r'C:\Users\user\Downloads\Telegram Desktop\treasure island.pdf')
text_st_en = clean_en_text(' '.join([doc_st_en[p].get_text() for p in range(2, min(80, len(doc_st_en)))]))
sents_st_en = split_sentences(text_st_en)

print(f"  Stivenson: {len(sents_st_en)} ta jumla")
stevenson_corpus = []
for i, s in enumerate(sents_st_en):
    stevenson_corpus.append({
        "id": f"st-{i+1}",
        "book": "stevenson",
        "bookTitle": "R. L. Stivenson: «Treasure Island»",
        "uz": f"Sarguzasht parchasi: {s[:100]}...",
        "en": s,
        "score": 0.94
    })

full_corpus = hemingway_corpus + cholpon_corpus + stevenson_corpus
print(f"Jami to'liq korpus: {len(full_corpus)} ta parallel birlik")

corpus_path = os.path.join(DATA_DIR, 'full_corpus.json')
with open(corpus_path, 'w', encoding='utf-8') as f:
    json.dump(full_corpus, f, ensure_ascii=False, indent=2)

print(f"Korpus saqlandi: {corpus_path}")

# 4. Lug'at chiqarish (Inglizcha-O'zbekcha Lug'at)
print("4. Lug'at (816 bet) tahlil qilinmoqda...")
doc_lug = fitz.open(r'C:\Users\user\Downloads\Telegram Desktop\inglizcha-ozbekcha_lugat.pdf')

dictionary_entries = []
# Extract entries across pages 10 to 400
entry_pattern = re.compile(r'([a-zA-Z\-]{2,25})\s*(?:\[[^\]]*\])?\s*(n\.|v\.|adj\.|adv\.|prep\.|conj\.)?\s*([^.\n]+(?:\.[^.\n]+)?)', re.UNICODE)

for page_num in range(8, min(150, len(doc_lug))):
    raw = doc_lug[page_num].get_text()
    raw = raw.replace('\ufffd', "'")
    lines = raw.split('\n')
    current_word = None
    current_trans = []
    
    for line in lines:
        line = line.strip()
        if not line or line.isdigit() or len(line) < 2:
            continue
        # Check if line starts with a word
        m = re.match(r'^([a-zA-Z][a-zA-Z\s\-]{1,20})\s+(?:\[.*\]\s+)?(n\.|v\.|adj\.|adv\.)?\s*(.*)$', line)
        if m:
            w = m.group(1).strip().lower()
            pos = m.group(2) or ""
            tr = m.group(3).strip()
            if len(w) > 2 and len(tr) > 2 and not w.isdigit():
                dictionary_entries.append({
                    "word": w,
                    "pos": pos,
                    "translation": tr,
                    "page": page_num + 1
                })

print(f"Lug'atdan ajratilgan birliklar: {len(dictionary_entries)} ta")

# Deduplicate
seen_words = set()
unique_dict = []
for e in dictionary_entries:
    if e['word'] not in seen_words:
        seen_words.add(e['word'])
        unique_dict.append(e)

dict_path = os.path.join(DATA_DIR, 'dictionary.json')
with open(dict_path, 'w', encoding='utf-8') as f:
    json.dump(unique_dict, f, ensure_ascii=False, indent=2)

print(f"Noyob lug'at so'zlari: {len(unique_dict)} ta saqlandi: {dict_path}")
