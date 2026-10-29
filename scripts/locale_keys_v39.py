#!/usr/bin/env python3
"""scripts/locale_keys_v39.py — v3.9 (teglash) uchun interfeys kalitlarini uz/en/ru locale fayllariga qo‘shadi.
S7-qoida: har bir kalit uch tilda mavjud; matn ichida so‘z almashtirish yo‘q."""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KEYS = {
    'tags_title': ('Teglar (avtomatik)', 'Tags (automatic)', 'Теги (автоматические)'),
    'tags_badge': ('Avtomatik teg — tadqiqotchi tasdig‘i kutilmoqda', 'Automatic tag — awaiting researcher confirmation',
                   'Автоматический тег — ожидает подтверждения исследователя'),
    'tags_note': ('Morfologik tahlil: o‘zbekcha — qoidaga asoslangan (o‘zak faqat korpusda tasdiqlangan bo‘lsa), inglizcha — '
                  'spaCy lemmalari; belgilar Universal Dependencies (UD) tizimida. Semantik maydon: Princeton WordNet 3.0 '
                  'leksikograf fayllari; o‘zbekcha so‘z uchun tarjimonning kitobdagi so‘zi orqali proyeksiya. Teglar III bob '
                  'statistikasiga kirmaydi.',
                  'Morphological analysis: Uzbek — rule-based (a stem counts only when the corpus attests it), English — spaCy '
                  'lemmas; features in the Universal Dependencies (UD) scheme. Semantic field: Princeton WordNet 3.0 '
                  'lexicographer files; for an Uzbek word it is projected through the translator’s word in the book. Tags do '
                  'not enter the Chapter III statistics.',
                  'Морфологический разбор: узбекский — по правилам (основа учитывается, только если она засвидетельствована в '
                  'корпусе), английский — леммы spaCy; признаки в схеме Universal Dependencies (UD). Семантическое поле: файлы '
                  'лексикографа Princeton WordNet 3.0; для узбекского слова проецируется через слово переводчика в книге. Теги '
                  'не входят в статистику главы III.'),
    'tags_word': ('So‘z', 'Word', 'Слово'),
    'tags_lemma': ('Lemma', 'Lemma', 'Лемма'),
    'tags_morph': ('Morfologiya', 'Morphology', 'Морфология'),
    'tags_sem_field': ('Semantik maydon', 'Semantic field', 'Семантическое поле'),
    'tags_sem_group': ('Semantik guruh (3.1)', 'Semantic group (3.1)', 'Семантическая группа (3.1)'),
    'tags_via': ('inglizcha muqobil orqali', 'via the English counterpart', 'через английское соответствие'),
    'tags_no_sem': ('semantik maydon aniqlanmagan', 'semantic field not determined', 'семантическое поле не определено'),
    'tags_component': ('Komponent', 'Component', 'Компонент'),
    'tags_role': ('Rol', 'Role', 'Роль'),
    'tags_role_base': ('asos', 'base', 'база'),
    'tags_role_coll': ('kollokat', 'collocate', 'коллокат'),
    'tags_group_by_base': ('Kollokatsiyaning semantik guruhi asos so‘z bo‘yicha belgilanadi.',
                           'The semantic group of a collocation is set by its base word.',
                           'Семантическая группа коллокации определяется по базовому слову.'),
    'tags_forms_gloss': ('Matndagi shakllar tahlili', 'Analysis of the forms in the text', 'Разбор форм в тексте'),
    'tags_source': ('Teglar manbasi', 'Tag source', 'Источник тегов'),
    'sem_all': ('Barcha semantik guruhlar', 'All semantic groups', 'Все семантические группы'),
    'sem_inson_ruhiyati': ('Inson his-tuyg‘ulari va ruhiy holati', 'Human feelings and mental state',
                           'Чувства и душевное состояние человека'),
    'sem_tabiat_borliq': ('Tabiat va atrof-muhit hodisalari', 'Nature and the environment', 'Природа и окружающая среда'),
    'sem_harakat_holat': ('Harakat va jismoniy holat', 'Movement and physical state', 'Движение и физическое состояние'),
    'sem_ijtimoiy_munosabat': ('Ijtimoiy-madaniy munosabatlar', 'Social and cultural relations', 'Социально-культурные отношения'),
    'sem_nutq_tafakkur': ('Nutqiy va aqliy faoliyat', 'Speech and mental activity', 'Речевая и мыслительная деятельность'),
    'sem_moddiy_borliq': ('Moddiy buyumlar va maishiy borliq', 'Material objects and everyday life', 'Материальные предметы и быт'),
    'sem_boshqa': ('Boshqa semantik guruh', 'Other semantic group', 'Другая семантическая группа'),
    'pos_pron': ('olmosh', 'pronoun', 'местоимение'),
    'pos_num': ('son', 'numeral', 'числительное'),
    'pos_postp': ('ko‘makchi', 'postposition', 'послелог'),
    'pos_conj': ('bog‘lovchi', 'conjunction', 'союз'),
    'pos_sconj': ('ergashtiruvchi bog‘lovchi', 'subordinating conjunction', 'подчинительный союз'),
    'pos_part': ('yuklama', 'particle', 'частица'),
    'pos_modal': ('modal so‘z', 'modal word', 'модальное слово'),
    'pos_intj': ('undov', 'interjection', 'междометие'),
    'pos_aux': ('to‘liqsiz fe’l', 'defective (auxiliary) verb', 'неполный (вспомогательный) глагол'),
    'pos_aux_verb': ('ko‘makchi fe’l', 'auxiliary verb', 'вспомогательный глагол'),
    'pos_propn': ('atoqli ot', 'proper noun', 'имя собственное'),
    'pos_onom': ('taqlid so‘z', 'onomatopoeic word', 'звукоподражательное слово'),
    'pos_paired': ('juft / takroriy so‘z', 'paired / reduplicated word', 'парное / редуплицированное слово'),
    'pos_prep': ('predlog', 'preposition', 'предлог'),
    'pos_det': ('aniqlovchi (determinativ)', 'determiner', 'детерминатив'),
    # v3.9.1 — researcher-marked parallel pairs in the search results
    'verified_pairs_title': ('Tadqiqotchi belgilagan parallel juftliklar', 'Researcher-marked parallel pairs',
                             'Параллельные пары, отмеченные исследователем'),
    'verified_pairs_note': ('Asar va uning tarjimasidan tadqiqotchi saralagan kollokatsiya juftliklari, ikki kitobdagi sahifa '
                            'raqamlari bilan. Ular korpus gaplari bo‘yicha emas, tadqiqotchi ro‘yxati bo‘yicha topiladi; '
                            'o‘zbekcha va inglizcha tomoni bir xil maqomda.',
                            'Collocation pairs selected by the researcher from a work and its translation, with the page numbers '
                            'in both books. They are found through the researcher’s list, not through corpus sentences; the Uzbek '
                            'and English sides have the same status.',
                            'Пары коллокаций, отобранные исследователем из произведения и его перевода, с номерами страниц в обеих '
                            'книгах. Они находятся по списку исследователя, а не по предложениям корпуса; узбекская и английская '
                            'стороны имеют одинаковый статус.'),
    'verified_pair_badge': ('tadqiqotchi belgilagan', 'researcher-marked', 'отмечено исследователем'),
}


def main():
    for i, code in enumerate(('uz', 'en', 'ru')):
        path = os.path.join(ROOT, 'locales', code + '.json')
        with open(path, encoding='utf-8') as f:
            d = json.load(f)
        added = 0
        for k, vals in KEYS.items():
            if k not in d:
                d[k] = vals[i]
                added += 1
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
            f.write('\n')
        print(f'{code}: {added} ta yangi kalit, jami {len(d)}')


if __name__ == '__main__':
    main()
