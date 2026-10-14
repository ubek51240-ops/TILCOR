import json
import re
from collections import Counter, defaultdict
import sys
sys.path.append('.')
from scripts.test_uz_norm import uz_norm
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
    full_corpus = json.load(f)

# Active corpus (KVK and OMS)
active_corpus = [c for c in full_corpus if c.get('book') != 'stevenson' and c.get('status') != 'excluded']
print(f"Active corpus: {len(active_corpus)} segments")

UZBEK_STOPWORDS = {
    'bu', 'u', 'va', 'bilan', 'ham', 'uchun', 'deb', 'esa', 'kabi', 'lekin', 'ammo', 'biroq',
    'yoki', 'bir', 'shu', 'men', 'sen', 'biz', 'siz', 'ular', 'o‘sha', 'oʻsha', "o'sha",
    'o‘z', 'oʻz', "o'z", 'o‘zi', 'oʻzi', "o'zi", 'da', 'dan', 'ga', 'ni', 'ning', 'edi',
    'bo‘ldi', 'boʻldi', "bo'ldi", 'bo‘lgan', 'boʻlgan', "bo'lgan", 'ekan', 'emish',
    'yo‘q', 'yoʻq', "yo'q", 'bor', 'qildi', 'qilgan', 'etdi', 'so‘ng', 'keyin', 'yana',
    'faqat', 'hatto', 'chunki', 'go‘yo', 'hali', 'endi', 'birga', 'ko‘ra', 'oldin',
    'tomon', 'orasida', 'bo‘yicha', 'ka', 'qa'
}

ENGLISH_STOPWORDS = {
    'the', 'a', 'an', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from',
    'by', 'with', 'of', 'in', 'out', 'as', 'if', 'then', 'than', 'that', 'this',
    'these', 'those', 'it', 'its', 'he', 'she', 'they', 'his', 'her', 'their',
    'my', 'your', 'our', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'would', 'could', 'should', 'will', 'can', 'may', 'might',
    'is', 'are', 'am', 'so', 'just', 'more', 'most', 'very', 'too', 'not', 'no',
    'all', 'any', 'some', 'there', 'here', 'when', 'where', 'how', 'what', 'who',
    'which', 'why', 'up', 'down', 'over', 'under', 'into', 'about', 'him', 'them',
    'me', 'us', 'himself', 'itself', 'themselves'
}

TOKEN_UZ_RE = re.compile(r"[a-z\u02bb\u02bc]+(?:-[a-z\u02bb\u02bc]+)*")
TOKEN_EN_RE = re.compile(r"[a-z]+(?:'[a-z]+|-?[a-z]+)*")

def stem_uz(word):
    w = uz_norm(word)
    # Strip common suffixes
    changed = True
    while changed and len(w) > 3:
        changed = False
        for sfx in ['ning', 'dan', 'da', 'ni', 'ga', 'ka', 'qa', 'imiz', 'ingiz', 'lari', 'im', 'ing', 'si', 'i', 'lar', 'moqda', 'yapti', 'gan', 'kan', 'qan', 'moq', 'mak', 'dim', 'ding', 'di', 'roq', 'dek', 'day', 'siz', 'lik', 'dor', 'kor', 'chi', 'li']:
            if w.endswith(sfx) and len(w) - len(sfx) >= 3:
                w = w[:-len(sfx)]
                changed = True
                break
    # Consonant alternations
    if w.endswith('g'):
        w = w[:-1] + 'k'
    elif w.endswith('gʻ'):
        w = w[:-2] + 'q'
    elif w == 'koʻngl':
        w = 'koʻngil'
    elif w == 'oʻgʻl':
        w = 'oʻgʻil'
    return w

def stem_en(word):
    w = word.lower().strip("'")
    lemma = lemmatizer.lemmatize(w)
    lemma_v = lemmatizer.lemmatize(lemma, pos='v')
    return lemma_v

def test_extract(query, lang):
    q_norm = uz_norm(query) if lang == 'uz' else query.lower()
    pair_counts = Counter()
    pair_books = defaultdict(set)
    pair_examples = {}
    pair_raw_forms = defaultdict(Counter)

    for seg in active_corpus:
        text = seg.get('uz' if lang == 'uz' else 'en', '')
        book = seg.get('book', 'Parallel Korpus')
        if lang == 'uz':
            norm_text, offsets = uz_norm(text, return_offsets=True)
            tokens = [m.group(0) for m in TOKEN_UZ_RE.finditer(norm_text)]
            # Match query family
            matched_indices = []
            for idx, tok in enumerate(tokens):
                st = stem_uz(tok)
                if st == stem_uz(q_norm) or tok.startswith(q_norm) or (q_norm == 'koʻngil' and 'koʻngl' in tok):
                    matched_indices.append(idx)
        else:
            norm_text = text.lower()
            tokens = [m.group(0) for m in TOKEN_EN_RE.finditer(norm_text)]
            matched_indices = []
            for idx, tok in enumerate(tokens):
                st = stem_en(tok)
                if st == stem_en(q_norm) or tok.startswith(q_norm):
                    matched_indices.append(idx)

        for m_idx in matched_indices:
            q_token = tokens[m_idx]
            start_w = max(0, m_idx - 3)
            end_w = min(len(tokens), m_idx + 4)
            for w_idx in range(start_w, end_w):
                if w_idx == m_idx:
                    continue
                neighbour = tokens[w_idx]
                n_clean = neighbour.strip("'")
                if lang == 'uz':
                    n_stem = stem_uz(n_clean)
                    if n_clean in UZBEK_STOPWORDS or n_stem in UZBEK_STOPWORDS or len(n_clean) < 3 or n_clean.isdigit():
                        continue
                    # Canonical base form
                    if w_idx < m_idx:
                        base_pair = f"{n_stem} {stem_uz(q_norm)}"
                    else:
                        base_pair = f"{stem_uz(q_norm)} {n_stem}"
                else:
                    n_stem = stem_en(n_clean)
                    if n_clean in ENGLISH_STOPWORDS or n_stem in ENGLISH_STOPWORDS or len(n_clean) < 3 or n_clean.isdigit():
                        continue
                    if w_idx < m_idx:
                        base_pair = f"{n_stem} {stem_en(q_norm)}"
                    else:
                        base_pair = f"{stem_en(q_norm)} {n_stem}"

                pair_counts[base_pair] += 1
                pair_books[base_pair].add(book)
                pair_raw_forms[base_pair][f"{neighbour} {q_token}"] += 1
                if base_pair not in pair_examples:
                    pair_examples[base_pair] = text

    print(f"\n=== Top 10 Candidates for '{query}' ({lang.upper()}) ===")
    top = [p for p, c in pair_counts.most_common(20) if c >= 2][:10]
    for i, p in enumerate(top, 1):
        print(f"{i}. {p} (freq: {pair_counts[p]}, books: {list(pair_books[p])})")

test_extract("yurak", "uz")
test_extract("ko‘ngil", "uz")
test_extract("qaror", "uz")
test_extract("heart", "en")
test_extract("decision", "en")
