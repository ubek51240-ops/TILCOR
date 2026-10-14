"""
scripts/test_uz_norm.py - Prototype and unit test for uz_norm() with offset map
"""

import re
import sys
from typing import Tuple, List, Dict, Optional

sys.stdout.reconfigure(encoding='utf-8')

APOSTROPHE_CHARS = set("ʻ‘'`’´ʼ\u02bb\u2018\u0027\u0060\u2019\u00b4\u02bc")
RUSSIAN_ONLY_CHARS = set("ыщ") # ы and щ are strictly Russian; э and ь in Russian context

# Cyrillic vowels for 'e' -> 'ye' rule
CYRILLIC_VOWELS = set("аеёиоуэюяўАЕЁИОУЭЮЯЎ")

CYRILLIC_TO_LATIN_BASE = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
    'ж': 'j', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
    'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
    'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f',
    'х': 'x', 'ч': 'ch', 'ш': 'sh', 'ъ': 'ʼ', 'ь': '',
    'э': 'e', 'ю': 'yu', 'я': 'ya', 'ё': 'yo',
    'ў': 'oʻ', 'ғ': 'gʻ', 'қ': 'q', 'ҳ': 'h'
}

def uz_norm(text: str, return_offsets: bool = False):
    """
    Normalizes Uzbek text following TILCOR_03-1 Part 1:
    1. Letters o‘ / g‘: after 'o' or 'g' (any case), apostrophe -> ʻ (U+02BB)
    2. Tutuq belgisi: after any other letter, apostrophe -> ʼ (U+02BC)
    3. Cyrillic Uzbek -> Latin using official correspondence
    4. Lowercase, collapse repeated spaces.
    5. Returns (normalized_text, offset_map) where offset_map[norm_idx] = orig_idx.
    """
    if not text:
        return ("", []) if return_offsets else ""

    # Phase 1: Handle Cyrillic to Latin with character-by-character tracking
    # Each output char tracks its orig_index
    chars_with_idx = []
    n = len(text)
    i = 0
    while i < n:
        c = text[i]
        c_low = c.lower()
        
        # Check 'e' / 'Е'
        if c_low == 'е':
            # At start of text, start of word, or after a vowel/ъ
            is_start_or_vowel = (i == 0) or (text[i-1] in ' \t\n\r"\'(«[—–-.,!?;:') or (text[i-1] in CYRILLIC_VOWELS) or (text[i-1] in 'ъЪ')
            lat = 'ye' if is_start_or_vowel else 'e'
            for lc in lat:
                chars_with_idx.append((lc, i))
            i += 1
            continue
            
        # Check 'ц' / 'Ц'
        if c_low == 'ц':
            # After vowel -> ts, otherwise -> s (or standard 'ts')
            is_after_vowel = (i > 0 and text[i-1] in CYRILLIC_VOWELS)
            lat = 'ts' if is_after_vowel else 's'
            for lc in lat:
                chars_with_idx.append((lc, i))
            i += 1
            continue

        if c_low in CYRILLIC_TO_LATIN_BASE:
            lat = CYRILLIC_TO_LATIN_BASE[c_low]
            for lc in lat:
                chars_with_idx.append((lc, i))
            i += 1
            continue

        # Otherwise keep character as is (lowercase)
        chars_with_idx.append((c_low, i))
        i += 1

    # Phase 2: Handle o‘/g‘ vs tutuq belgisi on Latin characters
    norm_chars = []
    offsets = []
    m = len(chars_with_idx)
    j = 0
    while j < m:
        ch, orig_i = chars_with_idx[j]
        
        if ch in APOSTROPHE_CHARS:
            # Look at previous non-space character
            prev_char = norm_chars[-1] if norm_chars else None
            if prev_char in ('o', 'g'):
                # Rule a: after o or g -> ʻ (U+02BB)
                norm_chars.append('\u02bb')
                offsets.append(orig_i)
            else:
                # Rule b: after any other letter -> ʼ (U+02BC)
                norm_chars.append('\u02bc')
                offsets.append(orig_i)
            j += 1
            continue

        # Rule d: collapse spaces
        if ch == ' ' and norm_chars and norm_chars[-1] == ' ':
            j += 1
            continue

        norm_chars.append(ch)
        offsets.append(orig_i)
        j += 1

    res_str = "".join(norm_chars)
    if return_offsets:
        return res_str, offsets
    return res_str

def test_norm():
    test_cases = [
        ("o‘zbek", "oʻzbek"),
        ("o'zbek", "oʻzbek"),
        ("oʻzbek", "oʻzbek"),
        ("o`zbek", "oʻzbek"),
        ("o’zbek", "oʻzbek"),
        ("ўзбек", "oʻzbek"),
        ("bog‘", "bogʻ"),
        ("боғ", "bogʻ"),
        ("ko‘ngil", "koʻngil"),
        ("ko'ngil", "koʻngil"),
        ("koʻngil", "koʻngil"),
        ("ko`ngil", "koʻngil"),
        ("кўнгил", "koʻngil"),
        ("ta’lim", "taʼlim"),
        ("ta'lim", "taʼlim"),
        ("таълим", "taʼlim"),
        ("ma’no", "maʼno"),
        ("маъно", "maʼno"),
        ("qishloq", "qishloq"),
        ("қишлоғи", "qishlogʻi"),
        ("qishlog‘i", "qishlogʻi"),
        ("qishlog'i", "qishlogʻi"),
        ("qishlogʻi", "qishlogʻi")
    ]

    all_passed = True
    for inp, expected in test_cases:
        res = uz_norm(inp)
        if res != expected:
            print(f"FAIL: uz_norm('{inp}') -> '{res}' (expected '{expected}')")
            all_passed = False
        else:
            print(f"PASS: uz_norm('{inp}') -> '{res}'")

    print("\nOffset map verification for 'кўнгил':")
    norm_txt, offsets = uz_norm("кўнгил", return_offsets=True)
    print(f"Result: {norm_txt}, Offsets: {offsets}")

    print(f"\nALL PASSED: {all_passed}")

if __name__ == '__main__':
    test_norm()
