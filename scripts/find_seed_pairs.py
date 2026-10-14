import json
import re
import sys

def norm(text):
    if not text:
        return ""
    text = text.lower()
    for q in ["‘", "’", "`", "ʻ", "ʼ", "'"]:
        text = text.replace(q, "'")
    return " ".join(text.split())

def main():
    with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
        corpus = json.load(f)

    # 16 target pairs
    # (num, uz_page, uz_span, en_page, en_span, status, eq_form)
    seeds = [
        (1, 3, "salqin shabada", 46, "the cool wind", "chegaraviy holat", "aniqlanmagan — tadqiqotchi belgilaydi"),
        (2, 4, "katta xotinlarning", 46, "older women", "erkin so‘z birikmasi", "aniqlanmagan — tadqiqotchi belgilaydi"),
        (3, 5, "otangiz javob bermadi", 47, "your father didn’t reply to my invitation", "kollokatsiya nomzodi; kontekstual ma’nosi bahsli", "aniqlanmagan — tadqiqotchi belgilaydi"),
        (4, 6, "dasturxon sol", 48, "set the table", "kollokatsiya nomzodi (Ot + fe’l)", "kollokatsiya"),
        (5, 6, "choyni so‘rida ichib", 48, "over tea", "barqaror erkin birikma", "aniqlanmagan — tadqiqotchi belgilaydi"),
        (6, 15, "javob ham bermadi", 56, "didn’t give an answer", "kollokatsiya nomzodi (Ot + fe’l)", "kollokatsiya"),
        (7, 23, "hazillashib javob berdi", 63, ["answered", "with a joke"], "kollokatsiya nomzodi (Ot + fe’l)", "bitta so‘z"),
        (8, 36, "og‘ir uyqudan", 74, "a heavy sleep", "kollokatsiya nomzodi (Sifat + ot)", "kollokatsiya (1.1 xulosasi)"),
        (9, 54, "katta xotinidan", 89, "his eldest wife’s", "kollokatsiya nomzodi (atamaga yaqin)", "aniqlanmagan — tadqiqotchi belgilaydi"),
        (10, 65, "og‘ir uyquga ketdilar", 98, "fell asleep", "kollokatsiya nomzodi (Sifat + ot)", "tushirib qoldirish (1.1 xulosasi: the intensifying component is lost)"),
        (11, 66, "rangi o‘chgan", 100, "her face had become pale", "kollokatsiya nomzodi (ko‘chma kollokatli)", "aniqlanmagan — tadqiqotchi belgilaydi"),
        (12, 78, "katta xotin", 110, "the elder wife", "kollokatsiya nomzodi (atamaga yaqin)", "aniqlanmagan — tadqiqotchi belgilaydi"),
        (13, 93, "og‘ir uyquda", 123, "a deep sleep", "kollokatsiya nomzodi (Sifat + ot)", "kollokatsiya (1.1 xulosasi)"),
        (14, 104, "yuragi o‘ynab", 132, "her heart fluttering", "frazeologik birlik", "aniqlanmagan — tadqiqotchi belgilaydi"),
        (15, 127, "yuragi o‘ynab", 152, "his heart began to flutter", "frazeologik birlik", "aniqlanmagan — tadqiqotchi belgilaydi"),
        (16, 80, "qaror berildi", 111, "they decided", "tasdiqlangan pair, equivalent AI-taklif", "aniqlanmagan — tadqiqotchi belgilaydi")
    ]

    cholpon_corpus = [s for s in corpus if s.get('book') == 'cholpon']
    print(f"Total Cholpon segments: {len(cholpon_corpus)}")

    results = []

    for num, uz_p, uz_span, en_p, en_span, status, eq_form in seeds:
        # Search strategy:
        # First check if any segment matches both uz_span and en_span
        best_match = None
        
        uz_norm_span = norm(uz_span)
        if isinstance(en_span, list):
            en_norm_spans = [norm(x) for x in en_span]
        else:
            en_norm_spans = [norm(en_span)]

        # Search for candidate segments
        matched_both = []
        uz_matched = []
        en_matched = []

        for s in cholpon_corpus:
            uz_text_norm = norm(s.get('uz', ''))
            en_text_norm = norm(s.get('en', ''))

            uz_has = uz_norm_span in uz_text_norm
            en_has = all(part in en_text_norm for part in en_norm_spans)

            if uz_has and en_has:
                matched_both.append(s)
            elif uz_has:
                uz_matched.append(s)
            elif en_has:
                en_matched.append(s)

        print(f"\n--- Row #{num}: UZ p.{uz_p} [{uz_span}] <-> EN p.{en_p} [{en_span}] ---")
        if matched_both:
            print(f"  Matched BOTH in {len(matched_both)} segment(s):")
            for m in matched_both:
                print(f"    ID: {m['id']} | uz_page: {m.get('uz_page')} (expected {uz_p}) | en_page: {m.get('en_page')} (expected {en_p})")
                print(f"      UZ: {m.get('uz')}")
                print(f"      EN: {m.get('en')}")
                best_match = m
        else:
            print(f"  No single segment matched both!")
            print(f"  UZ matched: {len(uz_matched)} segments:")
            for m in uz_matched[:3]:
                print(f"    UZ match ID: {m['id']} (uz_p={m.get('uz_page')}, en_p={m.get('en_page')}): {m.get('uz')[:80]}... | EN: {m.get('en')[:80]}...")
            print(f"  EN matched: {len(en_matched)} segments:")
            for m in en_matched[:3]:
                print(f"    EN match ID: {m['id']} (uz_p={m.get('uz_page')}, en_p={m.get('en_page')}): {m.get('uz')[:80]}... | EN: {m.get('en')[:80]}...")

if __name__ == '__main__':
    main()
