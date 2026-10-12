import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

TAXONOMY_ITEMS = [
    # 1. Birlik turi (1.1)
    ("unit_type", "kollokatsiya", "Kollokatsiya", "Collocation", "Barqaror, odatiy birikuvchi so‘z birikmasi", "baliq ovlamoq, chuqur xo‘rsinmoq", "1.0"),
    ("unit_type", "erkin_birikma", "Erkin birikma", "Free combination", "Sintaktik qoidalar asosida erkin birikkan so‘zlar", "kitobni o‘qimoq, katta stol", "1.0"),
    ("unit_type", "frazeologik_birlik", "Frazeologik birlik", "Idiom", "Semantik yaxlit, ko‘chma ma'noli turg‘un ibora", "ko‘z yummoq, yuragi yorilmoq", "1.0"),
    ("unit_type", "noaniq", "Noaniq", "Ambiguous", "Birlik turi qo‘shimcha tahlilni talab qiladi", "—", "1.0"),

    # 2. Struktur qolip (3.1)
    ("structural_pattern", "Fel+Ot", "Fe’l + Ot", "Verb + Noun", "Fe’l va to‘ldiruvchi ot birikmasi", "baliq ovlamoq, qaror qabul qilmoq", "1.0"),
    ("structural_pattern", "Sifat+Ot", "Sifat + Ot", "Adj + Noun", "Sifat va aniqlanuvchi ot birikmasi", "sovuq nigoh, og‘ir mehnat", "1.0"),
    ("structural_pattern", "Ot+Fel", "Ot + Fe’l", "Noun + Verb", "Ot va unga bog‘liq fe’l birikmasi", "ko‘ngli tusamoq, yurak urmoq", "1.0"),
    ("structural_pattern", "Ravish+Fel", "Ravish + Fe’l", "Adv + Verb", "Ravish va harakat fe’li birikmasi", "chuqur xo‘rsinmoq, tez yurmoq", "1.0"),
    ("structural_pattern", "Ot+Ot", "Ot + Ot", "Noun + Noun", "Ikki otning izofali yoki bitishuvli birikmasi", "hayot tarzi, qalb amri", "1.0"),
    ("structural_pattern", "boshqa", "Boshqa qolip", "Other", "Yuqoridagi 5 asosiy qolipga kirmaydigan tuzilmalar", "—", "1.0"),

    # 3. Semantik guruh (3.1)
    ("semantic_group", "inson_ruhiyati", "Inson his-tuyg‘ulari va ruhiy holati", "Human emotions and mental state", "Ruhiy kechinmalar, his-tuyg‘ular, istak va xohishlar", "ko‘ngli tusamoq, g‘am chekmoq", "1.0"),
    ("semantic_group", "tabiat_borliq", "Tabiat va atrof-muhit hodisalari", "Nature and environment", "Tabiiy hodisalar, flora, fauna, ob-havo", "shamol esmoq, qorong‘i tushmoq", "1.0"),
    ("semantic_group", "harakat_holat", "Harakat va jismoniy holat", "Action and physical state", "Jismoniy harakatlar, tana harakatlari, biologik holat", "qadam tashlamoq, ko‘z ochmoq", "1.0"),
    ("semantic_group", "ijtimoiy_munosabat", "Ijtimoiy-madaniy munosabatlar", "Social and cultural relations", "Jamiyatdagi muloqot, huquq, axloq, oila munosabatlari", "yordam bermoq, hurmat qilmoq", "1.0"),
    ("semantic_group", "nutq_tafakkur", "Nutqiy va aqliy faoliyat", "Speech and intellectual activity", "Gapirish, fikrlash, tushunish, qaror chiqarish", "fikr bildirmoq, xulosa chiqarmoq", "1.0"),
    ("semantic_group", "moddiy_borliq", "Moddiy buyumlar va maishiy borliq", "Material world and daily life", "Mehnat qurollari, buyumlar, kiyim, taom", "choy damlamoq, olov yoqmoq", "1.0"),
    ("semantic_group", "boshqa", "Boshqa semantik guruh", "Other semantic groups", "Maxsus yoki aralash ma'noli birikmalar", "—", "1.0"),

    # 4. Ekvivalentlik turi (3.2)
    ("equivalence_type", "toliq_ekvivalent", "To‘liq ekvivalent", "Full equivalent", "Struktura va leksik semantika aynan mos kelgan holat", "take a fish -> baliq tutmoq", "1.0"),
    ("equivalence_type", "qisman_ekvivalent", "Qisman ekvivalent", "Partial equivalent", "Semantika mos, lekin leksik tarkib yoki birikuvchanlikda farq bor", "deep sigh -> og‘ir xo‘rsinish", "1.0"),
    ("equivalence_type", "strukturaviy_transformatsiya", "Strukturaviy transformatsiya", "Structural transformation", "Grammatik so‘z turkumi yoki sintaktik struktura o‘zgargan", "verb+noun -> single verb", "1.0"),
    ("equivalence_type", "obraz_almashtirish", "Boshqa obraz bilan almashtirish", "Metaphorical substitution", "Boshqa metafora yoki obraz vositasida berilgan", "break the ice -> tilga kirmoq", "1.0"),
    ("equivalence_type", "tasviriy_tarjima", "Tasviriy (izohli) tarjima", "Descriptive translation", "To‘g‘ridan-to‘g‘ri ekvivalent yo‘qligi sababli tavsifiy berilgan", "—", "1.0"),
    ("equivalence_type", "bir_sozga_siqilgan", "Bir so‘zga siqilgan", "Lexical compression", "Ikki so‘zli birikma bir dona so‘z bilan tarjima qilingan", "make a decision -> qarorlamoq", "1.0"),
    ("equivalence_type", "tushirib_qoldirilgan", "Tushirib qoldirilgan", "Omission", "Tarjimada ushbu birikma aks etmagan (tushirib qoldirilgan)", "zero target span", "1.0"),
    ("equivalence_type", "tarjimada_qoshilgan", "Tarjimada qo‘shilgan", "Addition", "Asl nusxada bo‘lmagan, lekin tarjima matnida paydo bo‘lgan", "addition in target", "1.0"),

    # 5. Tarjima strategiyasi (1.2, 3.2)
    ("translation_strategy", "kalka", "Kalka", "Calque", "So‘zma-so‘z ko‘chirish strategiyasi", "word-for-word", "1.0"),
    ("translation_strategy", "modulyatsiya", "Modulyatsiya", "Modulation", "Semantik nuqtai nazarni o‘zgartirish", "point of view shift", "1.0"),
    ("translation_strategy", "generalizatsiya", "Generalizatsiya", "Generalization", "Xususiy ma'nodan umumiy ma'noga o‘tish", "specific to general", "1.0"),
    ("translation_strategy", "konkretizatsiya", "Konkretizatsiya", "Specification", "Umumiy ma'nodan aniqroq ma'noga o‘tish", "general to specific", "1.0"),
    ("translation_strategy", "kompensatsiya", "Kompensatsiya", "Compensation", "Boshqa joyda yo‘qotilgan ma'noni to‘ldirish", "stylistic compensation", "1.0"),
    ("translation_strategy", "izoh", "Izoh", "Explication / Gloss", "Matn ichida yoki izohda kengaytirish", "explanatory gloss", "1.0"),
    ("translation_strategy", "boshqa", "Boshqa strategiya", "Other strategy", "Boshqa tarjima uslubiy vositalari", "—", "1.0"),

    # 6. Lingvomadaniy belgilar (3.3)
    ("cultural_marker", "yoq", "Realiya yo‘q", "None", "Umuminsoniy leksika, madaniy xoslik mavjud emas", "—", "1.0"),
    ("cultural_marker", "etnografik", "Etnografik realiya", "Ethnographic realia", "An'ana, milliy kiyim, oshxona, bayramlar", "do‘ppi, somsa, palov", "1.0"),
    ("cultural_marker", "geografik", "Geografik realiya", "Geographic realia", "Joy nomlari, tabiiy landshaft, daryo-tog‘lar", "Golfstrim, Zarafshon", "1.0"),
    ("cultural_marker", "ijtimoiy_siyosiy", "Ijtimoiy-siyosiy realiya", "Socio-political realia", "Tarixiy mansablar, unvonlar, idoralar", "mingboshi, qozikalon", "1.0"),
    ("cultural_marker", "diniy_mafkuraviy", "Diniy va mafkuraviy realiya", "Religious and ideological realia", "E'tiqod, ibodat, diniy marosimlar", "namoz o‘qimoq, fotiha tortmoq", "1.0"),

    # 7. Ishonch darajasi
    ("confidence_level", "yuqori", "Yuqori ishonch", "High confidence", "Matnda aniq kontekstual dalil mavjud", "—", "1.0"),
    ("confidence_level", "orta", "O‘rta ishonch", "Medium confidence", "Qisman kontekstual dalil yoki ekvivalent noaniqligi", "—", "1.0"),
    ("confidence_level", "past", "Past ishonch", "Low confidence", "Qo‘shimcha ekspert muhokamasi zarur", "—", "1.0"),
]

def setup_db(db_path):
    print(f"[*] Bazani yangilash: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. Clear old taxonomies and insert full Prompt 7 set
    cur.execute("DELETE FROM taxonomies WHERE version = '1.0'")
    for cat, code, uz, en, df, ex, ver in TAXONOMY_ITEMS:
        item_id = f"tax-{cat}-{code}"
        cur.execute("""
            INSERT OR REPLACE INTO taxonomies (id, taxonomy_name, code, label_uz, label_en, definition, examples, version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (item_id, cat, code, uz, en, df, ex, ver))
    
    print(f"  [+] Taxonomies yangilandi: {len(TAXONOMY_ITEMS)} ta parametr kiritildi.")

    # 2. Create phd_annotations table if not exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phd_annotations (
            id TEXT PRIMARY KEY,
            occurrence_id TEXT NOT NULL REFERENCES collocation_occurrences(id),
            annotator_user TEXT NOT NULL,
            guideline_version TEXT NOT NULL DEFAULT 'v1.0',
            taxonomy_version TEXT NOT NULL DEFAULT 'v1.0',
            source_span TEXT NOT NULL,
            target_span TEXT,
            has_target_equivalent INTEGER DEFAULT 1,
            unit_type TEXT NOT NULL,
            structural_pattern TEXT NOT NULL,
            semantic_group TEXT NOT NULL,
            equivalence_type TEXT NOT NULL,
            translation_strategy TEXT NOT NULL,
            is_cultural INTEGER DEFAULT 0,
            cultural_category TEXT,
            cultural_note TEXT,
            confidence_level TEXT NOT NULL DEFAULT 'yuqori',
            evidence_note TEXT,
            is_ai_suggestion INTEGER DEFAULT 0,
            is_confirmed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_phd_ann_occ ON phd_annotations(occurrence_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_phd_ann_user ON phd_annotations(annotator_user)")
    print("  [+] phd_annotations jadvali tayyorlandi.")

    # 3. Clean legacy placeholder text in collocation_occurrences
    cur.execute("""
        UPDATE collocation_occurrences
        SET matched_span_uz = ''
        WHERE matched_span_uz = 'Kontekstdan tasdiqlanmoqda'
    """)
    cur.execute("""
        UPDATE collocation_occurrences
        SET matched_span_en = ''
        WHERE matched_span_en = 'Kontekstdan tasdiqlanmoqda'
    """)
    
    cur.execute("SELECT count(*) FROM collocation_occurrences WHERE matched_span_uz != '' AND matched_span_en != ''")
    both_spans = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM collocation_occurrences")
    total_occ = cur.fetchone()[0]

    # Create initial confirmed baseline annotations
    cur.execute("""
        INSERT OR REPLACE INTO phd_annotations (
            id, occurrence_id, annotator_user, guideline_version, taxonomy_version,
            source_span, target_span, has_target_equivalent,
            unit_type, structural_pattern, semantic_group, equivalence_type,
            translation_strategy, is_cultural, cultural_category, cultural_note,
            confidence_level, evidence_note, is_ai_suggestion, is_confirmed
        ) VALUES (
            'phd-ann-00001', 'occ-00002', 'admin', 'v1.0', '1.0',
            'fished alone', 'baliq ovlardi', 1,
            'kollokatsiya', 'Fel+Ot', 'tabiat_borliq', 'toliq_ekvivalent',
            'kalka', 0, 'yoq', '',
            'yuqori', '1-sahifa: Chol qayiqda yolg‘iz o‘zi Golfstrimda baliq ovlardi.', 0, 1
        )
    """)

    cur.execute("""
        INSERT OR REPLACE INTO phd_annotations (
            id, occurrence_id, annotator_user, guideline_version, taxonomy_version,
            source_span, target_span, has_target_equivalent,
            unit_type, structural_pattern, semantic_group, equivalence_type,
            translation_strategy, is_cultural, cultural_category, cultural_note,
            confidence_level, evidence_note, is_ai_suggestion, is_confirmed
        ) VALUES (
            'phd-ann-00002', 'occ-00001', 'admin', 'v1.0', '1.0',
            'ko‘ngli tusamoq', 'hearts wished for', 1,
            'kollokatsiya', 'Ot+Fel', 'inson_ruhiyati', 'toliq_ekvivalent',
            'modulyatsiya', 0, 'yoq', '',
            'yuqori', 'Kecha va kunduz, 1-bob: ko‘ngillari tusagan barcha narsa...', 0, 1
        )
    """)

    conn.commit()
    conn.close()
    print(f"  [+] Baza muvaffaqiyatli yangilandi: {total_occ} ta uchrashuv ({both_spans} tasida to‘liq spanlar mavjud).")

if __name__ == '__main__':
    setup_db('data/phd_corpus.db')
    if os.path.exists('staging/data/phd_corpus.db'):
        setup_db('staging/data/phd_corpus.db')
    print("[*] Stage 7 taksonomiyalari va annotatsiya jadvallari muvaffaqiyatli o‘rnatildi.")
