import json
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
from test_uz_norm import uz_norm

with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
    corpus = [c for c in json.load(f) if c.get('book') != 'stevenson']

# Function to test candidate extraction on actual corpus
UZ_STOPWORDS = {
    'va', 'ham', 'bilan', 'uchun', 'deb', 'esa', 'kabi', 'lekin', 'ammo', 'biroq',
    'yoki', 'bir', 'bu', 'shu', 'u', 'men', 'sen', 'biz', 'siz', 'ular', 'o‘sha',
    'oʻsha', "o'sha", 'o‘z', 'oʻz', "o'z", 'o‘zi', 'oʻzi', "o'zi", 'da', 'dan', 'ga',
    'ni', 'ning', 'edi', 'bo‘ldi', 'boʻldi', "bo'ldi", 'bo‘lgan', 'boʻlgan', "bo'lgan",
    'ekan', 'emish', 'yo‘q', 'yoʻq', "yo'q", 'bor', 'qildi', 'qilgan', 'etdi', 'so‘ng',
    'keyin', 'yana', 'faqat', 'hatto', 'chunki', 'go‘yo', 'hali', 'endi', 'birga',
    'ko‘ra', 'oldin', 'tomon', 'orasida', 'bo‘yicha', 'nima', 'qanday', 'hech',
    'har', 'allaqachon', 'bunday', 'shunday', 'oʻsha', 'ana', 'mana'
}

EN_STOPWORDS = {
    'the', 'a', 'an', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from',
    'by', 'with', 'of', 'in', 'out', 'as', 'if', 'then', 'than', 'that', 'this',
    'these', 'those', 'it', 'its', 'he', 'she', 'they', 'his', 'her', 'their',
    'my', 'your', 'our', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'would', 'could', 'should', 'will', 'can', 'may', 'might',
    'is', 'are', 'am', 'so', 'just', 'more', 'most', 'very', 'too', 'not', 'no',
    'all', 'any', 'some', 'there', 'here', 'when', 'where', 'how', 'what', 'who',
    'which', 'why', 'up', 'down', 'over', 'under', 'into', 'about', 'him', 'them', 'me', 'us'
}

def extract_candidates(target_word, lang):
    q_norm = uz_norm(target_word) if lang == 'uz' else target_word.lower()
    stopwords = UZ_STOPWORDS if lang == 'uz' else EN_STOPWORDS
    
    neighbour_counts = Counter()
    neighbour_examples = {}
    neighbour_books = defaultdict(set)
    
    for c in corpus:
        text = c.get('uz' if lang == 'uz' else 'en', '')
        book = c.get('book', '')
        if lang == 'uz':
            t_norm, offsets = uz_norm(text, return_offsets=True)
            tokens = re.findall(r'\b[a-z\u02bb\u02bc-]+\b', t_norm)
        else:
            tokens = re.findall(r'\b[a-z\'-]+\b', text.lower())
            
        # Check if query matches any token
        q_indices = []
        for idx, tok in enumerate(tokens):
            if lang == 'uz':
                # Check match with target_word (e.g. yurak, ko'ngil, qaror)
                if tok.startswith(q_norm[:4]) or tok.startswith('koʻngl'):
                    q_indices.append(idx)
            else:
                if tok.startswith(q_norm[:4]):
                    q_indices.append(idx)
                    
        for q_idx in q_indices:
            q_tok = tokens[q_idx]
            start_w = max(0, q_idx - 3)
            end_w = min(len(tokens), q_idx + 4)
            for w_idx in range(start_w, end_w):
                if w_idx == q_idx:
                    continue
                w_tok = tokens[w_idx]
                if w_tok in stopwords or len(w_tok) < 3 or w_tok.isdigit():
                    continue
                    
                # Canonical pair
                pair_key = (w_tok, q_norm) if w_idx < q_idx else (q_norm, w_tok)
                neighbour_counts[pair_key] += 1
                neighbour_books[pair_key].add(book)
                if pair_key not in neighbour_examples:
                    neighbour_examples[pair_key] = text
                    
    results = []
    for pair, cnt in neighbour_counts.most_common(15):
        if cnt >= 2:
            results.append({
                'pair': f"{pair[0]} {pair[1]}",
                'count': cnt,
                'books': list(neighbour_books[pair]),
                'example': neighbour_examples[pair][:80] + '...'
            })
    return results

print("=== Candidates for 'yurak' (UZ) ===")
for cand in extract_candidates('yurak', 'uz'):
    print(f"  {cand['pair']:<25} | n = {cand['count']} | books: {cand['books']}")

print("\n=== Candidates for 'ko‘ngil' (UZ) ===")
for cand in extract_candidates('ko‘ngil', 'uz'):
    print(f"  {cand['pair']:<25} | n = {cand['count']} | books: {cand['books']}")

print("\n=== Candidates for 'qaror' (UZ) ===")
for cand in extract_candidates('qaror', 'uz'):
    print(f"  {cand['pair']:<25} | n = {cand['count']} | books: {cand['books']}")

print("\n=== Candidates for 'heart' (EN) ===")
for cand in extract_candidates('heart', 'en'):
    print(f"  {cand['pair']:<25} | n = {cand['count']} | books: {cand['books']}")

print("\n=== Candidates for 'decision' (EN) ===")
for cand in extract_candidates('decision', 'en'):
    print(f"  {cand['pair']:<25} | n = {cand['count']} | books: {cand['books']}")
