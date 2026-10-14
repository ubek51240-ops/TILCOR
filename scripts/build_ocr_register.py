import os
import json
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def build_ocr_register():
    raw_path = os.path.join(DATA_DIR, 'raw_extracted_v2.json')
    raw = json.load(open(raw_path, encoding='utf-8'))
    oms_uz = raw['oms_uz']

    ocr_rules = [
        {"original": "chnqishim", "corrected": "chiqishim", "type": "ocr_letter_n_for_i"},
        {"original": "uchui", "corrected": "uchun", "type": "ocr_letter_i_for_n"},
        {"original": "uchup", "corrected": "uchun", "type": "ocr_letter_p_for_n"},
        {"original": "unnng", "corrected": "uning", "type": "ocr_letter_n_for_i"},
        {"original": "unnkidan", "corrected": "uningkidan", "type": "ocr_letter_n_for_i"},
        {"original": "charchashnn", "corrected": "charchashni", "type": "ocr_letter_n_for_i"},
        {"original": "kuchanmayotganinn", "corrected": "kuchanmayotganini", "type": "ocr_letter_n_for_i"},
        {"original": "yelkasinnng", "corrected": "yelkasining", "type": "ocr_letter_n_for_i"},
        {"original": "olmasliginn", "corrected": "olmasligini", "type": "ocr_letter_n_for_i"},
        {"original": "baliqnnng", "corrected": "baliqning", "type": "ocr_letter_n_for_i"},
        {"original": "harakatnni", "corrected": "harakatini", "type": "ocr_letter_n_for_i"},
        {"original": "burgutnnng", "corrected": "burgutning", "type": "ocr_letter_n_for_i"},
        {"original": "negrnnng", "corrected": "negrning", "type": "ocr_letter_n_for_i"},
        {"original": "chetinn", "corrected": "chetini", "type": "ocr_letter_n_for_i"},
        {"original": "parchalarnni", "corrected": "parchalarini", "type": "ocr_letter_n_for_i"},
        {"original": "ikknnchi", "corrected": "ikkinchi", "type": "ocr_letter_n_for_i"},
        {"original": "qismnni", "corrected": "qismini", "type": "ocr_letter_n_for_i"},
        {"original": "narsasinn", "corrected": "narsasini", "type": "ocr_letter_n_for_i"},
        {"original": "nnhoyati", "corrected": "nihoyatda", "type": "ocr_letter_n_for_i"},
        {"original": "ularnn", "corrected": "ularni", "type": "ocr_letter_n_for_i"},
        {"original": "akulalarnnng", "corrected": "akulalarning", "type": "ocr_letter_n_for_i"},
        {"original": "jag‘larinn", "corrected": "jag‘larini", "type": "ocr_letter_n_for_i"},
        {"original": "o‘znning", "corrected": "o‘zining", "type": "ocr_letter_n_for_i"},
        {"original": "voqeann", "corrected": "voqeani", "type": "ocr_letter_n_for_i"},
        {"original": "garpunnni", "corrected": "garpunni", "type": "ocr_extra_n"},
        {"original": "pkki", "corrected": "ikki", "type": "ocr_letter_p_for_i"}
    ]

    register = []
    for rule in ocr_rules:
        orig = rule["original"]
        corr = rule["corrected"]
        norm_orig = orig.replace("‘", "['`‘’]").replace("’", "['`‘’]")
        pat = re.compile(r'\b' + norm_orig + r'\b', re.IGNORECASE)
        
        matches = []
        for idx, seg in enumerate(oms_uz):
            if pat.search(seg['text']):
                matches.append({
                    "segment_id": seg.get('id', f"oms_uz_{idx}"),
                    "page": seg['page'],
                    "snippet": seg['text'][:120] + ("..." if len(seg['text']) > 120 else "")
                })
        
        register.append({
            "original": orig,
            "corrected": corr,
            "type": rule["type"],
            "occurrences": len(matches),
            "contexts": matches
        })

    out_file = os.path.join(DATA_DIR, 'ocr_errors_oms.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(register, f, indent=2, ensure_ascii=False)
    
    print(f"[+] Successfully wrote {len(register)} OCR error entries to {out_file}")
    total_found = sum(r['occurrences'] for r in register)
    print(f"[+] Total detected OCR error instances: {total_found}")

if __name__ == '__main__':
    build_ocr_register()
