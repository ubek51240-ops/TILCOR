import json
import re
from word_family import uz_norm, lemmatizer, detect_query_language
from search_engine import (
    resolve_uzbek, resolve_english, TOKEN_UZ_NORM_RE, TOKEN_EN_RE,
    PROTECTED_NOUNS, COMMON_VERBS, VERB_SUFFIXES
)

def is_collocation_query(q: str) -> bool:
    words = [w for w in re.split(r"\s+", q.strip()) if w]
    return len(words) >= 2

def match_collocation_in_sentence(text: str, query: str, lang: str):
    """
    Matches multi-word collocation in sentence with up to 2 intervening tokens,
    either order where appropriate.
    Returns (match_spans, matched_tokens).
    """
    q_words = [w for w in re.split(r"\s+", query.strip()) if w]
    if len(q_words) < 2:
        return [], []

    if lang == 'uz':
        norm_s, offsets = uz_norm(text, return_offsets=True)
        if not norm_s:
            return [], []

        tokens_info = []
        for m in TOKEN_UZ_NORM_RE.finditer(norm_s):
            tok = m.group(0)
            lem, pos = resolve_uzbek(tok)
            start_n, end_n = m.span()
            orig_start = offsets[start_n]
            orig_end = offsets[end_n - 1] + 1
            tokens_info.append({
                "tok": tok,
                "lemma": lem or tok,
                "pos": pos,
                "span": (orig_start, orig_end),
                "orig_text": text[orig_start:orig_end]
            })

        # Resolve query lemmas
        q_lemmas = []
        for qw in q_words:
            qw_lem, qw_pos = resolve_uzbek(qw)
            # handle verb stem if ends in -moq
            q_norm_w = uz_norm(qw)
            stem = q_norm_w[:-3] if q_norm_w.endswith('moq') else q_norm_w
            q_lemmas.append({
                "raw": qw,
                "norm": q_norm_w,
                "lemma": qw_lem or qw,
                "stem": stem,
                "pos": qw_pos
            })

        # Match 2-word collocation:
        # q1 and q2 with intervening <= 2 tokens (i.e. distance in indices between 1 and 3)
        p1, p2 = q_lemmas[0], q_lemmas[1]
        
        def token_matches_q(t_info, q_info):
            t_tok = t_info['tok']
            t_lem = t_info['lemma']
            # direct lemma match
            if t_lem == q_info['lemma'] or t_lem == q_info['norm']:
                return True
            # stem match
            if t_tok.startswith(q_info['stem']):
                return True
            if q_info['norm'] in t_tok:
                return True
            return False

        found_spans = []
        found_tokens = []

        for i, t1 in enumerate(tokens_info):
            m1 = token_matches_q(t1, p1)
            m2 = token_matches_q(t1, p2)
            
            # Forward search up to +3 tokens (intervening <= 2)
            if m1:
                for j in range(i + 1, min(len(tokens_info), i + 4)):
                    t2 = tokens_info[j]
                    if token_matches_q(t2, p2):
                        found_spans.extend([t1['span'], t2['span']])
                        found_tokens.extend([t1['orig_text'], t2['orig_text']])
                        return found_spans, found_tokens
            # Reverse order check (e.g. "bergan qarorini")
            if m2:
                for j in range(i + 1, min(len(tokens_info), i + 4)):
                    t2 = tokens_info[j]
                    if token_matches_q(t2, p1):
                        found_spans.extend([t1['span'], t2['span']])
                        found_tokens.extend([t1['orig_text'], t2['orig_text']])
                        return found_spans, found_tokens

        return [], []

    else: # English
        # English collocation matching
        tokens_info = []
        for m in TOKEN_EN_RE.finditer(text):
            tok = m.group(0)
            lem, pos = resolve_english(tok)
            tokens_info.append({
                "tok": tok.lower(),
                "lemma": lem or tok.lower(),
                "pos": pos,
                "span": m.span(),
                "orig_text": tok
            })

        # Query words
        # Filter optional articles if 3 words like "set the table"
        q_words_clean = [w.lower() for w in q_words]
        q_lemmas = [lemmatizer.lemmatize(w, 'v') if w in ('set', 'fall', 'fell') else lemmatizer.lemmatize(w, 'n') for w in q_words_clean]

        # Check exact phrase or lemma window
        # 1. Exact phrase substring check
        q_phrase = " ".join(q_words_clean)
        text_lower = text.lower()
        if q_phrase in text_lower:
            start_idx = text_lower.find(q_phrase)
            end_idx = start_idx + len(q_phrase)
            return [(start_idx, end_idx)], [text[start_idx:end_idx]]

        # 2. Window-based lemma matching for variants (e.g. fell asleep -> fall asleep, set the table)
        # Content words in query
        content_q = [qw for qw in q_words_clean if qw not in ('the', 'a', 'an')]
        if len(content_q) >= 2:
            p1 = lemmatizer.lemmatize(content_q[0], 'v')
            p2 = lemmatizer.lemmatize(content_q[1], 'n')
            for i, t1 in enumerate(tokens_info):
                if t1['lemma'] == p1 or t1['tok'] == content_q[0] or (content_q[0] == 'fell' and t1['tok'] == 'fell'):
                    for j in range(i + 1, min(len(tokens_info), i + 4)):
                        t2 = tokens_info[j]
                        if t2['lemma'] == p2 or t2['tok'] == content_q[1] or t2['tok'].startswith(content_q[1]):
                            return [t1['span'], t2['span']], [t1['orig_text'], t2['orig_text']]

        return [], []

def run_tests():
    with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
        corpus = json.load(f)

    test_queries = [
        ("og‘ir uyqu", "uz"),
        ("heavy sleep", "en"),
        ("javob bermoq", "uz"),
        ("dasturxon solmoq", "uz"),
        ("qaror bermoq", "uz"),
        ("rangi o‘chmoq", "uz"),
        ("yuragi o‘ynamoq", "uz"),
        ("katta xotin", "uz"),
        ("set the table", "en"),
        ("fell asleep", "en"),
        ("deep sleep", "en")
    ]

    for q, lang in test_queries:
        matched = []
        source1_muqobils = []
        for s in corpus:
            b = s.get('book', 'cholpon')
            query_in_orig = (lang == 'uz' and b == 'cholpon') or (lang == 'en' and b == 'hemingway')
            s_text = s.get('uz') if lang == 'uz' else s.get('en')
            if not s_text:
                continue

            spans, tokens = match_collocation_in_sentence(s_text, q, lang)
            if spans:
                matched.append(s)
                # Check Source 1 confirmed equivalent
                if s.get('status') == 'tasdiqlangan' and s.get('confirmed_equivalent'):
                    conf = s['confirmed_equivalent']
                    if conf.get('source_type') == 1:
                        target_span = conf.get('en_span') if lang == 'uz' else conf.get('uz_span')
                        if isinstance(target_span, list):
                            eq_str = " … ".join(target_span)
                        else:
                            eq_str = str(target_span)
                        source1_muqobils.append({
                            "text": eq_str,
                            "form": conf.get('equivalent_form'),
                            "uz_p": s.get('uz_page'),
                            "en_p": s.get('en_page'),
                            "id": s.get('id')
                        })

        print(f"\n==========================================")
        print(f"QUERY: '{q}' ({lang.upper()}) -> Matched: {len(matched)} sentences")
        print(f"Source 1 Confirmed Muqobils ({len(source1_muqobils)}):")
        for m in source1_muqobils:
            print(f"  - '{m['text']}' (UZ p.{m['uz_p']} -> EN p.{m['en_p']}) | Form: {m['form']} | ID: {m['id']}")

if __name__ == '__main__':
    run_tests()
