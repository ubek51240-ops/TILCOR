import json
import re
from word_family import uz_norm, lemmatizer
from search_engine import resolve_uzbek, resolve_english, TOKEN_UZ_NORM_RE, TOKEN_EN_RE

def test():
    with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
        corpus = json.load(f)

    # Let's check the test queries in KVK:
    # 1. og‘ir uyqu: expected 3 (pages 36, 65, 93)
    # 2. javob bermoq: expected about 56 (pages 5, 15, 23, ...)
    # 3. qaror bermoq: expected 10 (80, 117, 119, 123, 183, 191, 198, 224, 238 x2)
    # 4. dasturxon solmoq: expected 4 (6, 29, 44, 63)
    # 5. rangi o‘chmoq: expected 9 (38, 66, 71, 138, 184, 231, 239, 256, 259)
    # 6. yuragi o‘ynamoq: expected 4 (34, 104, 127, 201)
    # 7. katta xotin: expected 10 (4, 54, 63 x4, 64, 78, 228, 265)

    cholpon_corpus = [s for s in corpus if s.get('book') == 'cholpon']
    print(f"Total Cholpon segments: {len(cholpon_corpus)}")

    # Let's check how words appear in segments
    queries = [
        ("og‘ir uyqu", [("og‘ir", "sifat"), ("uyqu", "ot")]),
        ("javob bermoq", [("javob", "ot"), ("ber", "fe’l")]),
        ("qaror bermoq", [("qaror", "ot"), ("ber", "fe’l")]),
        ("dasturxon solmoq", [("dasturxon", "ot"), ("sol", "fe’l")]),
        ("rangi o‘chmoq", [("rang", "ot"), ("o‘ch", "fe’l")]),
        ("yuragi o‘ynamoq", [("yurak", "ot"), ("o‘yna", "fe’l")]),
        ("katta xotin", [("katta", "sifat"), ("xotin", "ot")]),
    ]

    for q_name, parts in queries:
        matches = []
        for s in cholpon_corpus:
            uz_text = s.get('uz', '')
            norm_s, offsets = uz_norm(uz_text, return_offsets=True)
            if not norm_s:
                continue

            tokens_with_pos = []
            for m in TOKEN_UZ_NORM_RE.finditer(norm_s):
                tok = m.group(0)
                lemma, pos = resolve_uzbek(tok)
                start_n, end_n = m.span()
                orig_start = offsets[start_n]
                orig_end = offsets[end_n - 1] + 1
                tokens_with_pos.append({
                    "tok": tok,
                    "lemma": lemma,
                    "pos": pos,
                    "span": (orig_start, orig_end)
                })

            # Check if parts appear with intervening <= 2
            # Parts could be in either order if allowed
            part1_lemma, part1_type = parts[0]
            part2_lemma, part2_type = parts[1]

            # Matching logic:
            # Does lemma match?
            found_pair = False
            for i, t1 in enumerate(tokens_with_pos):
                l1 = t1['lemma'] or t1['tok']
                # Check match with part 1 or part 2
                match_p1 = (l1 == part1_lemma or t1['tok'].startswith(uz_norm(part1_lemma)))
                match_p2 = (l1 == part2_lemma or t1['tok'].startswith(uz_norm(part2_lemma)))

                if match_p1:
                    # look forward up to +3 tokens (intervening <= 2)
                    for j in range(i + 1, min(len(tokens_with_pos), i + 4)):
                        t2 = tokens_with_pos[j]
                        l2 = t2['lemma'] or t2['tok']
                        if l2 == part2_lemma or t2['tok'].startswith(uz_norm(part2_lemma)):
                            found_pair = True
                            break
                if not found_pair and match_p2: # reverse order (e.g. bergan qarorini)
                    for j in range(i + 1, min(len(tokens_with_pos), i + 4)):
                        t2 = tokens_with_pos[j]
                        l2 = t2['lemma'] or t2['tok']
                        if l2 == part1_lemma or t2['tok'].startswith(uz_norm(part1_lemma)):
                            found_pair = True
                            break
                if found_pair:
                    break

            if found_pair:
                matches.append(s)

        pages = [m.get('uz_page') for m in matches]
        print(f"\nQuery: '{q_name}' -> Matches: {len(matches)} segments. Pages: {sorted(pages)}")

if __name__ == '__main__':
    test()
