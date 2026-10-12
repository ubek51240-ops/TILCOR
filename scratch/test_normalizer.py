import re, sys
sys.stdout.reconfigure(encoding='utf-8')

CANONICAL_OG = '\u02bb'     # ʻ (U+02BB modifier letter turned comma)
CANONICAL_TUTUQ = '\u02bc'  # ʼ (U+02BC modifier letter apostrophe)
APOSTROPHE_VARIANTS = r"[`'‘’ʻ´\u02bb\u02bc\u2018\u2019]"

def normalize_uzbek_text(raw_text):
    if not raw_text:
        return ''
    text = raw_text
    # 1. Map o‘ / g‘ variants to U+02BB
    text = re.sub(r'([oOgG])' + APOSTROPHE_VARIANTS, r'\g<1>' + CANONICAL_OG, text)
    # 2. Map tutuq belgisi (any other apostrophe NOT preceded by o/g) to U+02BC
    text = re.sub(r'(?<![oOgG\u02bb])' + r"[`'‘’´\u02bc\u2018\u2019]" + r'(?=\w)', CANONICAL_TUTUQ, text)
    return text.lower()

samples = [
    "o'tmoq",
    "g'olib",
    "O‘zbekiston",
    "Gʻalaba",
    "ma'no",
    "san'at",
    "ta'lim",
    "o`g`il",
    "ҳаёт"
]

for s in samples:
    norm = normalize_uzbek_text(s)
    hex_rep = ' '.join(f'U+{ord(c):04X}' for c in norm)
    print(f"{s:15} -> {norm:15} ({hex_rep})")
