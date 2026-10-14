import json
import re

TOKEN_EN_RE = re.compile(r"[a-zA-Z]+(?:'[a-zA-Z]+|-?[a-zA-Z]+)*")

def check():
    with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
        corpus = json.load(f)

    for term in ['decide', 'shark', 'heart']:
        kvk_cnt = 0
        oms_cnt = 0
        pages_target = []
        for s in corpus:
            en = s.get('en', '')
            found = False
            for m in TOKEN_EN_RE.finditer(en):
                tok = m.group(0).lower()
                if term == 'decide':
                    if tok in ('decide', 'decides', 'decided', 'deciding', 'decision', 'decisions'):
                        found = True
                        if tok == 'decided' and s.get('book') == 'cholpon':
                            pages_target.append(s.get('en_page'))
                elif term == 'shark':
                    if tok in ('shark', 'sharks'):
                        found = True
                elif term == 'heart':
                    if tok in ('heart', 'hearts'):
                        found = True
                        if s.get('book') == 'cholpon':
                            pages_target.append(s.get('en_page'))
            if found:
                if s.get('book') == 'cholpon':
                    kvk_cnt += 1
                else:
                    oms_cnt += 1
        print(f"{term}: KVK={kvk_cnt}, OMS={oms_cnt}")
        if term == 'decide':
            print("  decided includes p.111:", 111 in pages_target)
        if term == 'heart':
            print("  heart includes p.132, 152:", 132 in pages_target, 152 in pages_target)

if __name__ == '__main__':
    check()
