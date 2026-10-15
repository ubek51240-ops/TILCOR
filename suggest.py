"""suggest.py — qidiruv takliflari (TILCOR).

Ikki vazifa:
  1) autocomplete(query, corpus)  — qidiruv qatorida yozilayotgan so'z uchun
     prefiks bo'yicha takliflar;
  2) similar(query, corpus)       — natija topilmaganda yaqin yozilgan real
     so'zlar ("Buni nazarda tutdingizmi?").

G1-qoidaga muvofiq takliflar hech qachon o'ylab topilmaydi: lug'at faqat
korpus gaplarida real uchragan so'z shakllaridan tuziladi va har bir taklif
korpusdagi uchrashlar soni bilan qaytadi. Taklif bosilganda oddiy /qidiruv
so'rovi bajariladi, ya'ni foydalanuvchi faqat mavjud ma'lumotga boradi.
"""

import re
import bisect
import threading
from collections import Counter

from word_family import uz_norm

# uz_norm chiqishi: kichik lotin harflari + ʻ (U+02BB) / ʼ (U+02BC)
_UZ_NORM_TOKEN_RE = re.compile(r"[a-zʻʼ]+(?:-[a-zʻʼ]+)*")
# asl matndagi ko'rinish shakli uchun (katta-kichik va apostrof turlari saqlanadi)
_UZ_RAW_TOKEN_RE = re.compile(r"[A-Za-zЀ-ӿʻʼ'’‘`-]+")
_EN_TOKEN_RE = re.compile(r"[a-zA-Z]+(?:'[a-zA-Z]+)?(?:-[a-zA-Z]+)*")

_MIN_LEN = 2          # bir harfli shakllar taklif qilinmaydi
_MIN_FREQ = 1

_lock = threading.Lock()
_V = {"corpus_len": -1}


def _build_vocab(corpus):
    """Korpusdan ikki tilli chastotali lug'at tuzadi (bir marta, keshda saqlanadi)."""
    uz_counts = Counter()
    en_counts = Counter()
    uz_display = {}   # normallashgan shakl -> asl yozuvdagi eng ko'p shakl
    uz_disp_counts = {}

    for rec in corpus:
        uz_text = rec.get('uz') or ''
        en_text = rec.get('en') or ''
        if uz_text:
            norm = uz_norm(uz_text)
            for tok in _UZ_NORM_TOKEN_RE.findall(norm):
                if len(tok) >= _MIN_LEN:
                    uz_counts[tok] += 1
            for raw in _UZ_RAW_TOKEN_RE.findall(uz_text):
                raw_l = raw.strip('-').lower()
                if len(raw_l) < _MIN_LEN:
                    continue
                key = uz_norm(raw_l)
                if not key:
                    continue
                c = uz_disp_counts.setdefault(key, Counter())
                c[raw_l] += 1
        if en_text:
            for tok in _EN_TOKEN_RE.findall(en_text.lower()):
                if len(tok) >= _MIN_LEN:
                    en_counts[tok] += 1

    for key, c in uz_disp_counts.items():
        uz_display[key] = c.most_common(1)[0][0]

    return {
        "corpus_len": len(corpus),
        "uz_counts": uz_counts,
        "en_counts": en_counts,
        "uz_display": uz_display,
        "uz_sorted": sorted(uz_counts),
        "en_sorted": sorted(en_counts),
    }


def _vocab(corpus):
    global _V
    if _V.get("corpus_len") != len(corpus):
        with _lock:
            if _V.get("corpus_len") != len(corpus):
                _V = _build_vocab(corpus)
    return _V


def _display_uz(v, word_norm):
    return v["uz_display"].get(word_norm, word_norm)


def _prefix_matches(sorted_words, counts, prefix, limit):
    """Saralangan ro'yxatdan prefiks oralig'ini bisect bilan olib, chastota bo'yicha tartiblaydi."""
    lo = bisect.bisect_left(sorted_words, prefix)
    hi = bisect.bisect_right(sorted_words, prefix + '￿')
    cand = sorted_words[lo:hi]
    cand.sort(key=lambda w: (-counts[w], w))
    return cand[:limit]


def autocomplete(query, corpus, limit=8):
    """Qidiruv qatori uchun takliflar. Ko'p so'zli so'rovda oxirgi so'z to'ldiriladi.

    Qaytaradi: [{"text": to'liq taklif, "count": uchrashlar soni, "lang": "uz"|"en"}]
    """
    q = (query or '').strip()
    if len(q) < _MIN_LEN:
        return []
    v = _vocab(corpus)

    parts = q.split()
    head = ' '.join(parts[:-1])
    last = parts[-1]

    out = []
    seen = set()

    last_uz = uz_norm(last.lower())
    last_en = last.lower()

    uz_hits = _prefix_matches(v["uz_sorted"], v["uz_counts"], last_uz, limit) if last_uz else []
    en_hits = _prefix_matches(v["en_sorted"], v["en_counts"], last_en, limit) if re.fullmatch(r"[a-zA-Z'-]+", last) else []

    # ikkala tildan aralashtirib, chastota bo'yicha birlashtiramiz
    merged = ([(w, v["uz_counts"][w], 'uz') for w in uz_hits]
              + [(w, v["en_counts"][w], 'en') for w in en_hits])
    merged.sort(key=lambda t: -t[1])

    for w, n, lng in merged:
        disp = _display_uz(v, w) if lng == 'uz' else w
        full = (head + ' ' + disp).strip()
        if full.lower() in seen:
            continue
        seen.add(full.lower())
        out.append({"text": full, "count": n, "lang": lng})
        if len(out) >= limit:
            break
    return out


def _bounded_levenshtein(a, b, max_d):
    """Levenshteyn masofasi; max_d dan oshsa None qaytaradi (erta to'xtash bilan)."""
    la, lb = len(a), len(b)
    if abs(la - lb) > max_d:
        return None
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur = [i] + [0] * lb
        row_min = cur[0]
        ca = a[i - 1]
        for j in range(1, lb + 1):
            cost = 0 if ca == b[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
            if cur[j] < row_min:
                row_min = cur[j]
        if row_min > max_d:
            return None
        prev = cur
    return prev[lb] if prev[lb] <= max_d else None


def _similar_in(sorted_words, counts, q, limit, display=None, lang='uz'):
    max_d = 1 if len(q) <= 4 else 2
    found = []
    for w in sorted_words:
        if abs(len(w) - len(q)) > max_d:
            continue
        # arzon oldindan filtr: umumiy harflar soni
        if len(set(w) & set(q)) < max(1, len(set(q)) - max_d - 1):
            continue
        d = _bounded_levenshtein(q, w, max_d)
        if d is not None and d > 0:
            found.append((d, -counts[w], w))
    found.sort()
    out = []
    for d, negn, w in found[:limit]:
        out.append({"text": display(w) if display else w, "count": -negn, "distance": d, "lang": lang})
    return out


def similar(query, corpus, limit=5):
    """Natija topilmaganda yaqin yozilgan real korpus so'zlari.

    Faqat bir so'zli so'rovlar uchun; [{"text", "count", "distance"}] qaytaradi.
    """
    q = (query or '').strip()
    if not q or ' ' in q or len(q) < _MIN_LEN or len(q) > 30:
        return []
    v = _vocab(corpus)

    q_uz = uz_norm(q.lower())
    res_uz = _similar_in(v["uz_sorted"], v["uz_counts"], q_uz, limit,
                         display=lambda w: _display_uz(v, w), lang='uz') if q_uz else []
    res_en = (_similar_in(v["en_sorted"], v["en_counts"], q.lower(), limit, lang='en')
              if re.fullmatch(r"[a-zA-Z'-]+", q) else [])

    merged = res_uz + res_en
    merged.sort(key=lambda r: (r["distance"], -r["count"]))
    seen, out = set(), []
    for r in merged:
        key = r["text"].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
        if len(out) >= limit:
            break
    return out
