# Interface strings added in v3.1 (merged into locales/*.json by this script).
K = {
 'coll_order_label': ('Tartib', 'Order', 'Порядок'),
 'coll_order_freq': ('uchrash soni', 'frequency', 'частота'),
 'coll_order_note': ('Assotsiatsiya ko‘rsatkichi tadqiqot korpusining o‘zida hisoblangan; u kollokatsiya maqomini belgilamaydi, o‘lchovlarni qiyoslash uchun beriladi.',
                     'The association measure is computed within the study corpus; it does not decide the status of a collocation and is given to compare the measures.',
                     'Мера ассоциации вычислена внутри исследуемого корпуса; она не определяет статус коллокации и дана для сравнения мер.'),
 'coll_assoc_title': ('Korpus ichidagi assotsiatsiya ko‘rsatkichlari', 'Association measures within the corpus', 'Меры ассоциации внутри корпуса'),
 'coll_assoc_note': ('O₁₁ — birikmaning uchrash soni; R₁ va C₁ — birinchi va oxirgi komponentning shu tildagi matnlarda uchrash soni; N — shu tildagi tokenlar soni. Formulalar va o‘lchovlarni qiyoslash «Statistika» sahifasida.',
                     'O₁₁ is the frequency of the combination; R₁ and C₁ the frequencies of its first and last component in the texts of that language; N the number of tokens of that language. Formulas and the comparison of the measures are on the Statistics page.',
                     'O₁₁ — частота сочетания; R₁ и C₁ — частоты первого и последнего компонента в текстах этого языка; N — число токенов этого языка. Формулы и сравнение мер — на странице «Статистика».'),
 'coll_eq_found': ('Tarjimada muqobil topilgan uchrashlar: {a} / {b}.', 'Occurrences with a counterpart found in the translation: {a} of {b}.', 'Употреблений с найденным соответствием в переводе: {a} из {b}.'),
 'coll_examples_first': ('Birinchi {n} ta uchrash ko‘rsatilgan.', 'The first {n} occurrences are shown.', 'Показаны первые {n} употреблений.'),
 'pair_none_translation': ('Gaplarni tekislashda bu gapga tarjimadan juft topilmadi: tarjimon uni tushirib qoldirgan, qo‘shni gap bilan birlashtirgan yoki gap tekislashda ajralib qolgan.',
                           'Sentence alignment found no counterpart in the translation: the translator left the sentence out, merged it with a neighbouring one, or it was left over in the alignment.',
                           'При выравнивании предложений для этого предложения не найдено соответствия в переводе: переводчик опустил его, объединил с соседним, или оно осталось без пары при выравнивании.'),
 'pair_none_original': ('Gaplarni tekislashda bu gapga asliyatdan juft topilmadi: tarjimon gapni qo‘shgan, asliyatdagi gapni bo‘lib bergan yoki gap tekislashda ajralib qolgan.',
                        'Sentence alignment found no counterpart in the original: the translator added the sentence, split a sentence of the original, or it was left over in the alignment.',
                        'При выравнивании предложений для этого предложения не найдено соответствия в оригинале: переводчик добавил его, разделил предложение оригинала, или оно осталось без пары при выравнивании.'),
 'coll_in_translation_of': ('Tarjimada ({a} ta uchrashdan {b} tasida):', 'In the translation ({b} of {a} occurrences):', 'В переводе ({b} из {a} употреблений):'),
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
