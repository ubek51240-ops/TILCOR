# Interface strings of v3.6 (merged into locales/*.json by this script).
K = {
 'home_eyebrow': ('Parallel korpus · Tadqiqot vositasi', 'Parallel corpus · Research tool', 'Параллельный корпус · Инструмент исследования'),
 'home_h1_a': ('So‘zlar', 'Words', 'Слова'),
 'home_h1_b': ('kontekstda.', 'in context.', 'в контексте.'),
 'home_lead2': ('O‘zbekcha va inglizcha parallel matnlarda so‘zlar, kollokatsiyalar va tarjima muqobillarini tadqiq qiling.',
                'Explore words, collocations and translation equivalents in Uzbek and English parallel texts.',
                'Исследуйте слова, коллокации и переводные соответствия в узбекских и английских параллельных текстах.'),
 'nav_lab_validation': ('Inson tekshiruvi', 'Human evaluation', 'Экспертная проверка'),
 'home_stats_title': ('Korpus statistikasi', 'Corpus statistics', 'Статистика корпуса'),
 'coll_page_title': ('Kollokatsiya nomzodlari', 'Collocation candidates', 'Кандидаты в коллокации'),
 'coll_page_lead': ('Ikki kitob juftligidan avtomatik ajratilgan va kamida ikki marta uchragan nomzodlar: tuzilish qolipi, uchrash soni, tarjimadagi muqobillari va misollari bilan. Nomzodning kollokatsiya ekanini dissertatsiyaning 1.1.4-bandidagi qaror tartibi belgilaydi: lingvistik baho va tayanch korpusdagi statistik tasdiq.',
                    'Candidates extracted automatically from the two book pairs and occurring at least twice, with their structural pattern, frequency, counterparts in the translation and examples. Whether a candidate is a collocation is decided by the procedure of section 1.1.4 of the dissertation: the linguistic judgement and the statistical confirmation in a reference corpus.',
                    'Кандидаты, автоматически извлечённые из двух пар книг и встретившиеся не менее двух раз: структурная модель, частота, соответствия в переводе и примеры. Является ли кандидат коллокацией, решает порядок раздела 1.1.4 диссертации: лингвистическая оценка и статистическое подтверждение в опорном корпусе.'),
 'home_stat_collocations': ('Kollokatsiya nomzodlari', 'Collocation candidates', 'Кандидаты в коллокации'),
 'sec_collocations': ('Kollokatsiya nomzodlari', 'Collocation candidates', 'Кандидаты в коллокации'),
 'sec_collocations_note': ('Nomzodlar korpusdan ajratilgan: inglizchada sintaktik bog‘lanish, o‘zbekchada tuzilish qoliplari bo‘yicha; kamida ikki marta uchraganlari olingan. Har biri yonida tarjimadagi muqobili va misoli bor.',
                           'The candidates are extracted from the corpus: by dependency relations in English, by structural patterns in Uzbek; those occurring at least twice are kept. Each comes with its counterpart in the translation and an example.',
                           'Кандидаты извлечены из корпуса: в английском — по синтаксическим связям, в узбекском — по структурным моделям; сохранены встретившиеся не менее двух раз. У каждого — соответствие в переводе и пример.'),
 'coll_browse_all': ('Barcha nomzodlar', 'All candidates', 'Все кандидаты'),
 'coll_none_in_corpus': ('Bu so‘z bilan kamida ikki marta uchragan kollokatsiya nomzodi korpusda yo‘q.', 'The corpus has no collocation candidate with this word occurring at least twice.', 'В корпусе нет кандидата в коллокации с этим словом, встретившегося не менее двух раз.'),
 'coll_count_word': ('nomzod', 'candidate|candidates', 'кандидат|кандидата|кандидатов'),
 'coll_filter_placeholder': ('Nomzodlar ichidan qidirish', 'Search the candidates', 'Поиск среди кандидатов'),
 'home_link_colloc': ('Korpusdan ajratilgan kollokatsiya nomzodlari, tuzilish qolipi bo‘yicha', 'The collocation candidates of the corpus by structural pattern', 'Кандидаты в коллокации корпуса по структурным моделям'),
 'so_t_colls': ('Kollokatsiya nomzodlari', 'Collocation candidates', 'Кандидаты в коллокации'),
 'dict_colls': ('Kollokatsiya nomzodlari', 'Collocation candidates', 'Кандидаты в коллокации'),
 'dict_colls_none': ('Bu so‘z korpusdagi kollokatsiya nomzodlari tarkibida yo‘q.', 'This word is not part of a collocation candidate of the corpus.', 'Это слово не входит в кандидаты в коллокации корпуса.'),
 'coll_ref_title': ('Statistik ko‘rsatkichlar', 'Statistics', 'Статистика'),
 'coll_ref_corpus': ('Tadqiqot korpusida', 'In the research corpus', 'В исследовательском корпусе'),
 'coll_ref_ref': ('Tayanch korpusda', 'In the reference corpus', 'В опорном корпусе'),
 'coll_ref_none': ('tayanch korpusda uchramaydi', 'not found in the reference corpus', 'в опорном корпусе не встречается'),
 'coll_ref_min': ('1.1.4-banddagi minimal chastota (kamida 5 marta) bajarilgan', 'the minimum frequency of section 1.1.4 (at least 5 times) is met', 'минимальная частота раздела 1.1.4 (не менее 5 раз) соблюдена'),
 'coll_ref_low': ('1.1.4-banddagi minimal chastotadan (5 marta) kam', 'below the minimum frequency of section 1.1.4 (5 times)', 'ниже минимальной частоты раздела 1.1.4 (5 раз)'),
 'coll_ref_uz': ('O‘zbekcha tayanch korpus hali ulanmagan.', 'No Uzbek reference corpus is connected yet.', 'Узбекский опорный корпус пока не подключён.'),
 'coll_ref_more': ('Tayanch korpus haqida', 'About the reference corpus', 'Об опорном корпусе'),
 'coll_judged': ('Inson tekshiruvidagi baho', 'Judgement in the human evaluation', 'Оценка в экспертной проверке'),
 'home_search_placeholder': ('So‘z yoki kollokatsiyani kiriting…', 'Type a word or a collocation…', 'Введите слово или коллокацию…'),
}

if __name__ == '__main__':
    import json, os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for i, l in enumerate(('uz', 'en', 'ru')):
        p = os.path.join(root, 'locales', l + '.json')
        d = json.load(open(p, encoding='utf-8'))
        for k, v in K.items():
            d[k] = v[i]
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(len(K), 'keys merged')
