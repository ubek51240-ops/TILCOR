import json
import re

def norm(text):
    if not text:
        return ""
    text = text.lower()
    for q in ["‘", "’", "`", "ʻ", "ʼ", "'"]:
        text = text.replace(q, "'")
    return " ".join(text.split())

def find_substring_span(text, sub):
    """Finds exact substring span (start, end) in text, case-insensitive if needed, or fallback."""
    idx = text.find(sub)
    if idx != -1:
        return idx, idx + len(sub)
    idx_lower = text.lower().find(sub.lower())
    if idx_lower != -1:
        return idx_lower, idx_lower + len(sub)
    # try normalized quote matching
    sub_norm = norm(sub)
    for i in range(len(text)):
        for j in range(i + len(sub) - 3, min(len(text) + 1, i + len(sub) + 4)):
            if norm(text[i:j]) == sub_norm:
                return i, j
    return None

def main():
    with open('data/full_corpus.json', 'r', encoding='utf-8') as f:
        corpus = json.load(f)

    # 16 target pairs:
    # (num, seg_id, uz_p, uz_span, en_p, en_span, status, eq_form, is_ai_proposal)
    seeds = [
        (1, "aln-kvk-00011", 3, "salqin shabada", 46, "the cool wind", "chegaraviy holat", "aniqlanmagan — tadqiqotchi belgilaydi", False),
        (2, "aln-kvk-00022", 4, "katta xotinlarning", 46, "older women", "erkin so‘z birikmasi", "aniqlanmagan — tadqiqotchi belgilaydi", False),
        (3, "aln-kvk-00043", 5, "otangiz javob bermadi", 47, "your father didn’t reply to my invitation", "kollokatsiya nomzodi; kontekstual ma’nosi bahsli", "aniqlanmagan — tadqiqotchi belgilaydi", False),
        (4, "aln-kvk-00067", 6, "dasturxon sol", 48, "set the table", "kollokatsiya nomzodi (Ot + fe’l)", "kollokatsiya", False),
        (5, "aln-kvk-00068", 6, "choyni so‘rida ichib", 48, "over tea", "barqaror erkin birikma", "aniqlanmagan — tadqiqotchi belgilaydi", False),
        (6, "aln-kvk-00287", 15, "javob ham bermadi", 56, "didn’t give an answer", "kollokatsiya nomzodi (Ot + fe’l)", "kollokatsiya", False),
        (7, "aln-kvk-00473", 23, "hazillashib javob berdi", 63, ["answered", "with a joke"], "kollokatsiya nomzodi (Ot + fe’l)", "bitta so‘z", False),
        (8, "aln-kvk-00775", 36, "og‘ir uyqudan", 74, "a heavy sleep", "kollokatsiya nomzodi (Sifat + ot)", "kollokatsiya (1.1 xulosasi)", False),
        (9, "aln-kvk-01188", 54, "katta xotinidan", 89, "his eldest wife’s", "kollokatsiya nomzodi (atamaga yaqin)", "aniqlanmagan — tadqiqotchi belgilaydi", False),
        (10, "aln-kvk-01449", 65, "og‘ir uyquga ketdilar", 98, "fell asleep", "kollokatsiya nomzodi (Sifat + ot)", "tushirib qoldirish (1.1 xulosasi: the intensifying component is lost)", False),
        (11, "aln-kvk-01472", 66, "rangi o‘chgan", 100, "her face had become pale", "kollokatsiya nomzodi (ko‘chma kollokatli)", "aniqlanmagan — tadqiqotchi belgilaydi", False),
        (12, "aln-kvk-01753", 78, "katta xotin", 110, "the elder wife", "kollokatsiya nomzodi (atamaga yaqin)", "aniqlanmagan — tadqiqotchi belgilaydi", False),
        (13, "aln-kvk-02079", 93, "og‘ir uyquda", 123, "a deep sleep", "kollokatsiya nomzodi (Sifat + ot)", "kollokatsiya (1.1 xulosasi)", False),
        (14, "aln-kvk-02342", 104, "yuragi o‘ynab", 132, "her heart fluttering", "frazeologik birlik", "aniqlanmagan — tadqiqotchi belgilaydi", False),
        (15, "aln-kvk-02936", 127, "yuragi o‘ynab", 152, "his heart began to flutter", "frazeologik birlik", "aniqlanmagan — tadqiqotchi belgilaydi", False),
        (16, "aln-kvk-01789", 80, "qaror berildi", 111, "they decided", "tasdiqlangan pair, equivalent AI-taklif", "aniqlanmagan — tadqiqotchi belgilaydi", True)
    ]

    corpus_map = {s['id']: s for s in corpus}

    # Special adjustments for split lines:
    # aln-kvk-00043: "otangiz javob ber-madi" -> "otangiz javob bermadi"
    if "aln-kvk-00043" in corpus_map:
        corpus_map["aln-kvk-00043"]["uz"] = corpus_map["aln-kvk-00043"]["uz"].replace("ber-madi", "bermadi")

    # aln-kvk-00068: needs English translation from 69:
    # "I’ll speak with your father over tea and tell him what you told me."
    if "aln-kvk-00068" in corpus_map and "aln-kvk-00069" in corpus_map:
        tea_trans = "I’ll speak with your father over tea and tell him what you told me."
        corpus_map["aln-kvk-00068"]["en"] = tea_trans
        corpus_map["aln-kvk-00068"]["en_page"] = 48
        corpus_map["aln-kvk-00068"]["page_target"] = "48-bet"
        # And clean 69:
        c69_en = corpus_map["aln-kvk-00069"]["en"]
        if "I’ll speak with your father over tea" in c69_en:
            clean_69 = c69_en.split("what you told me.”")[-1].strip()
            if clean_69:
                corpus_map["aln-kvk-00069"]["en"] = clean_69

    report_rows = []

    for num, sid, uz_p, uz_span, en_p, en_span, status, eq_form, is_ai_proposal in seeds:
        seg = corpus_map.get(sid)
        if not seg:
            report_rows.append({
                "num": num,
                "status_report": "topilmadi",
                "sid": sid,
                "reason": "Segment ID korpusda yo‘q"
            })
            continue

        uz_text = seg.get('uz', '')
        en_text = seg.get('en', '')

        # Check UZ span
        uz_span_loc = find_substring_span(uz_text, uz_span)
        if not uz_span_loc:
            report_rows.append({
                "num": num,
                "status_report": "topilmadi",
                "sid": sid,
                "reason": f"O‘zbekcha matnda '{uz_span}' topilmadi: {uz_text[:50]}"
            })
            continue

        # Check EN span(s)
        en_spans_locs = []
        if isinstance(en_span, list):
            all_found = True
            for part in en_span:
                loc = find_substring_span(en_text, part)
                if loc:
                    en_spans_locs.append(loc)
                else:
                    all_found = False
                    break
            if not all_found:
                report_rows.append({
                    "num": num,
                    "status_report": "topilmadi",
                    "sid": sid,
                    "reason": f"Inglizcha matnda qismlardan biri topilmadi: {en_text[:50]}"
                })
                continue
        else:
            loc = find_substring_span(en_text, en_span)
            if not loc:
                report_rows.append({
                    "num": num,
                    "status_report": "topilmadi",
                    "sid": sid,
                    "reason": f"Inglizcha matnda '{en_span}' topilmadi: {en_text[:50]}"
                })
                continue
            en_spans_locs.append(loc)

        # Update segment metadata
        seg["status"] = "tasdiqlangan"
        seg["alignment_status"] = "tasdiqlangan"
        seg["is_confirmed"] = True
        seg["source"] = "1.1-paragraf, tadqiqotchi" if not is_ai_proposal else "tashqi tekshiruv, tadqiqotchi tasdiqlashi kutilmoqda"
        seg["uz_page"] = uz_p
        seg["en_page"] = en_p
        seg["page_source"] = f"{uz_p}-bet (ziyouz.com)"
        seg["page_target"] = f"{en_p}-bet"
        
        # Source label in hierarchy:
        # Source 1: "Kitobdagi tarjima — tasdiqlangan"
        # Source 2: "Kitobdagi tarjima — AI-taklif (tekshirilmagan)"
        source_label = "Kitobdagi tarjima — AI-taklif (tekshirilmagan)" if is_ai_proposal else "Kitobdagi tarjima — tasdiqlangan"
        
        seg["confirmed_equivalent"] = {
            "uz_span": uz_span,
            "uz_span_offsets": [uz_span_loc[0], uz_span_loc[1]],
            "en_span": en_span,
            "en_span_offsets": en_spans_locs,
            "status": status,
            "equivalent_form": eq_form,
            "source_label": source_label,
            "is_ai_proposal": is_ai_proposal,
            "source_type": 2 if is_ai_proposal else 1
        }
        
        # Also store target_equivalent_span for highlight rendering
        # If discontinuous, store all spans
        seg["target_equivalent_spans"] = en_spans_locs
        seg["target_equivalent_span"] = en_spans_locs[0] if en_spans_locs else None
        seg["target_equivalent_label"] = source_label
        seg["source_equivalent_span"] = uz_span_loc

        report_rows.append({
            "num": num,
            "status_report": "kiritildi",
            "sid": sid,
            "uz_p": uz_p,
            "uz_span": uz_span,
            "en_p": en_p,
            "en_span": en_span,
            "status": status,
            "eq_form": eq_form,
            "source_label": source_label
        })

    with open('data/full_corpus.json', 'w', encoding='utf-8') as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    print(f"Seeding completed. Total rows: {len(report_rows)}")
    for r in report_rows:
        if r['status_report'] == 'kiritildi':
            print(f"Row #{r['num']}: kiritildi | {r['sid']} | UZ p.{r['uz_p']} '{r['uz_span']}' <-> EN p.{r['en_p']} '{r['en_span']}' | {r['source_label']}")
        else:
            print(f"Row #{r['num']}: topilmadi | {r['sid']} | Sabab: {r['reason']}")

if __name__ == '__main__':
    main()
