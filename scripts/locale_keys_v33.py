# Interface strings of the v3.3 "night navy" interface (merged into locales/*.json by this script).
K = {
 'topbar_place': ('Buxoro', 'Bukhara', 'Бухара'),
 'topbar_research': ('PhD tadqiqoti, 10.00.06', 'PhD research, 10.00.06', 'Исследование PhD, 10.00.06'),
 'topbar_books': ('Cho‘lpon va Hemingway asarlari', 'Works by Cho‘lpon and Hemingway', 'Произведения Чулпана и Хемингуэя'),
 'brand_sub': ('Parallel korpus', 'Parallel corpus', 'Параллельный корпус'),
 'so_title': ('Korpusdan qidiring…', 'Search the corpus…', 'Поиск по корпусу…'),
 'so_placeholder': ('So‘z yoki kollokatsiyani kiriting…', 'Type a word or a collocation…', 'Введите слово или коллокацию…'),
 'so_t_search': ('So‘z va kollokatsiya', 'Word and collocation', 'Слово и коллокация'),
 'so_t_kwic': ('KWIC konkordans', 'KWIC concordance', 'Конкорданс KWIC'),
 'so_t_colls': ('Kollokatsiyalar ro‘yxati', 'List of collocations', 'Список коллокаций'),
 'so_ask': ('Nimani qidiryapsiz?', 'What are you looking for?', 'Что вы ищете?'),
 'so_hint': ('O‘zbekcha yoki inglizcha so‘z, so‘z shakli yoki kollokatsiyani yozing', 'Type an Uzbek or English word, word form or collocation',
             'Введите узбекское или английское слово, словоформу или коллокацию'),
 'so_samples': ('Namuna so‘rovlar', 'Sample queries', 'Примеры запросов'),
 'so_open': ('Qidiruvni ochish', 'Open search', 'Открыть поиск'),
 'so_close': ('Yopish', 'Close', 'Закрыть'),
 'menu_open': ('Bo‘limlar menyusi', 'Sections menu', 'Меню разделов'),
 'to_top': ('Yuqoriga', 'Back to top', 'Наверх'),
 'home_stat_note': ('Raqamlar korpus ma’lumotidan so‘rov paytida hisoblanadi.', 'The figures are computed from the corpus data at the time of the request.',
                    'Цифры вычисляются из данных корпуса в момент запроса.'),
 'home_stat_pairs': ('Parallel juftliklar', 'Parallel pairs', 'Параллельные пары'),
 'home_stat_tokens': ('So‘z qo‘llanishlari (token)', 'Tokens', 'Словоупотребления (токены)'),
 'home_stat_collocations': ('Korpus kollokatsiyalari', 'Corpus collocations', 'Коллокации корпуса'),
 'home_stat_works': ('Asar juftliklari', 'Work pairs', 'Пары произведений'),
 'home_example_title': ('Bir misol', 'An example', 'Пример'),
 'hs_uz': ('O‘zbekcha', 'Uzbek', 'Узбекские'),
 'hs_en': ('Inglizcha', 'English', 'Английские'),
 'hs_total': ('Jami', 'Total', 'Всего'),
 'hs_pairs': ('Juftliklar', 'Pairs', 'Пары'),
 'hs_tokens': ('Tokenlar', 'Tokens', 'Токены'),
 'hs_works': ('Asarlar', 'Works', 'Произведения'),
 'eq_note_all': ('Muqobil — tarjimonning kitobdagi so‘zlari. Ular {total} ta gapning hammasida so‘z darajasidagi tekislash orqali topildi.',
                 'A counterpart is the translator’s own words in the book. It was found by word alignment in all {total} sentences.',
                 'Соответствие — собственные слова переводчика в книге. Оно найдено пословным выравниванием во всех {total} предложениях.'),
 'eq_pending_count': ('uchrash', 'occurrences', 'употреблений'),
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
