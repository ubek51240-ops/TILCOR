"""Pages of the human evaluation (/baholash): overview with progress and results, and the annotation screen
that follows the decision procedure of paragraph 1.1.4."""
import html
import json
import urllib.parse

import ui_components as ui
import validation as V

L = {
 'uz': {
  'title': 'Inson tekshiruvi',
  'lead': 'Platforma natijalarining qo‘lda bahosi: tanlanma, ikki annotator, aniqlik va kelishuv (dissertatsiya, 1.1.4-band).',
  'task_pairs': 'Gap juftliklari', 'task_equiv': 'So‘z muqobillari', 'task_colloc_uz': 'O‘zbekcha kollokatsiya nomzodlari',
  'task_colloc_en': 'Inglizcha kollokatsiya nomzodlari', 'task_dict': 'Korpus lug‘ati tarjimalari',
  'd_pairs': 'Avtomatik tekislangan gap juftligi to‘g‘rimi.', 'd_equiv': 'Qidiruv sahifasi ko‘rsatgan muqobil tarjimonning shu so‘z uchun bergan so‘zimi.',
  'd_colloc_uz': 'Nomzodning bir uchrashi qaror tartibi bo‘yicha (1–4 va 6-savollar).', 'd_colloc_en': 'Nomzodning bir uchrashi qaror tartibi bo‘yicha (1–4 va 6-savollar).',
  'd_dict': 'Lug‘atdagi tarjima misoldagi to‘g‘ri tarjimami.',
  'set_train': 'O‘quv to‘plami', 'set_main': 'Asosiy tanlanma', 'col_task': 'Vazifa', 'open': 'Ochish',
  'annot_a': 'A (tadqiqotchi)', 'annot_b': 'B (ikkinchi annotator)', 'you_are': 'Siz: annotator {w}.',
  'res_title': 'Natijalar (asosiy tanlanma)', 'res_none': 'Asosiy tanlanmada hali baho yo‘q. Avval o‘quv to‘plamini bajaring: 50 ta birlik yo‘riqnomani sinash uchun.',
  'res_correct': 'to‘g‘ri', 'res_cop': 'to‘g‘ri yoki qisman', 'res_coll': 'kollokatsiya', 'res_kappa': 'Koen kappasi', 'res_po': 'kuzatilgan kelishuv',
  'res_ci': '95 % ishonch oralig‘i', 'res_n': 'baholangan', 'export': 'Barcha baholarni CSV faylda yuklab olish',
  'guide': 'Yo‘riqnoma va qaror tartibi', 'b_login': 'Ikkinchi annotator tizimga «annotator» foydalanuvchi nomi bilan kiradi; uning parolini server administratori yaratadi (DEPLOY yo‘riqnomasi). Annotatorlar bir-birining bahosini ko‘rmaydi.',
  'item_of': '{k}-birlik, jami {n}', 'done_all': 'Bu to‘plamdagi barcha birliklar baholandi.', 'back': 'Inson tekshiruvi',
  'save_next': 'Saqlash va keyingisi', 'skip': 'Keyingisi', 'note': 'Izoh (ixtiyoriy)', 'saved_before': 'Avvalgi bahongiz saqlangan; o‘zgartirsangiz, yangisi yoziladi.',
  'q_pairs': 'Bu ikki matn bir-birining tarjimasimi?',
  'v_correct_pairs': 'To‘g‘ri — ikki tomon bir-birining to‘liq tarjimasi', 'v_partial_pairs': 'Qisman — bir tomonda ortiqcha yoki yetishmayotgan gap bor',
  'v_wrong_pairs': 'Noto‘g‘ri — tarjima emas',
  'q_equiv': 'Firuza bilan belgilangan so‘z tarjimonning oltin bilan belgilangan so‘z uchun bergan muqobilimi?',
  'v_correct_equiv': 'To‘g‘ri', 'v_partial_equiv': 'Qisman — muqobilning bir qismi yoki ortiqcha so‘z bilan', 'v_wrong_equiv': 'Noto‘g‘ri',
  'q_dict': 'Lug‘atdagi tarjima bosh so‘zning shu misoldagi tarjimasimi?',
  'v_correct_dict': 'To‘g‘ri', 'v_partial_dict': 'Qisman — ibora yoki birikmaning bir qismi', 'v_wrong_dict': 'Noto‘g‘ri',
  'cand': 'Nomzod', 'pattern': 'qolip', 'ref': 'Tayanch korpusda', 'ref_none': 'tayanch korpusda uchramaydi',
  'q1': '1. Birlik kamida ikki mustaqil so‘zdan iborat va komponentlari bevosita sintaktik aloqadami?',
  'q1_yes': 'Ha', 'q1_no': 'Yo‘q — tahlilga olinmaydi',
  'q2': '2. Birlik istisno qilinadigan toifaga kiradimi?',
  'q2_none': 'Yo‘q', 'q2_proverb': 'Maqol yoki matal', 'q2_sentence': 'To‘liq gap', 'q2_simile': 'O‘xshatish', 'q2_formula': 'Nutq formulasi',
  'q2_name': 'Atoqli ot yoki laqab', 'q2_paired': 'Juft yoki takroriy so‘z', 'q2_auxiliary': 'Ko‘makchi fe’lli qurilma',
  'q3': '3. Birikma shu kontekstda yaxlit obrazli ko‘chma ma’noga egami va qayta ifodalashda asos yo‘qoladimi?',
  'q3_no': 'Yo‘q', 'q3_yes': 'Ha — frazeologik birlik',
  'q4': '4. Kollokat tanlovi cheklanganmi (ma’nodosh so‘z qo‘yilsa, birikma g‘ayritabiiy bo‘ladimi)?',
  'q4_yes': 'Ha', 'q4_no': 'Yo‘q', 'q4_disputed': 'Bahsli — chegaraviy',
  'q4b': '4a. Matnda takroriy va tarjimada tayyor qolip bilan berilganmi?', 'q4b_no': 'Yo‘q — erkin birikma', 'q4b_yes': 'Ha — barqaror erkin birikma',
  'q6': '6. Tarjimadagi muqobil turi', 'q6_collocation': 'Kollokatsiya', 'q6_single': 'Bitta so‘z', 'q6_descriptive': 'Tasviriy ifoda', 'q6_omitted': 'Tushirib qoldirilgan',
  'eq': 'Platforma belgilagan muqobil', 'eq_correct': 'To‘g‘ri', 'eq_partial': 'Qisman', 'eq_wrong': 'Noto‘g‘ri', 'eq_none': 'Belgilanmagan',
  'cat': 'Natija', 'cat_collocation': 'kollokatsiya (5-savol: tayanch korpus)', 'cat_borderline': 'chegaraviy birlik', 'cat_stable_free': 'barqaror erkin birikma',
  'cat_free': 'erkin birikma', 'cat_phraseological': 'frazeologik birlik', 'cat_excluded': 'istisno toifa', 'cat_not_unit': 'tahlil birligi emas',
  'calib_title': 'logDice chegarasini kalibrlash (inglizcha nomzodlar)',
  'calib_note': 'Tadqiqotchi «kollokatsiya» deb baholagan nomzodlar bo‘yicha: «tayanch korpusda kamida {f} marta va logDice ≥ t» qoidasining aniqligi, to‘liqligi va F1. Eng yaxshi F1: t = {t}.',
  'c_t': 't', 'c_p': 'aniqlik', 'c_r': 'to‘liqlik', 'c_f': 'F1',
  'forbidden': 'Bu sahifa tadqiqotchi va ikkinchi annotator uchun.',
 },
 'en': {
  'title': 'Human evaluation',
  'lead': 'Manual evaluation of the platform’s output: samples, two annotators, precision and agreement (dissertation, section 1.1.4).',
  'task_pairs': 'Sentence pairs', 'task_equiv': 'Word equivalents', 'task_colloc_uz': 'Uzbek collocation candidates',
  'task_colloc_en': 'English collocation candidates', 'task_dict': 'Corpus dictionary translations',
  'd_pairs': 'Is the automatically aligned sentence pair right?', 'd_equiv': 'Is the equivalent shown by the search page the translator’s word for this word?',
  'd_colloc_uz': 'One occurrence of the candidate through the decision procedure (questions 1–4 and 6).', 'd_colloc_en': 'One occurrence of the candidate through the decision procedure (questions 1–4 and 6).',
  'd_dict': 'Is the dictionary translation the right translation in the example?',
  'set_train': 'Training set', 'set_main': 'Main sample', 'col_task': 'Task', 'open': 'Open',
  'annot_a': 'A (researcher)', 'annot_b': 'B (second annotator)', 'you_are': 'You are annotator {w}.',
  'res_title': 'Results (main sample)', 'res_none': 'The main sample has no judgements yet. Start with the training set: 50 units to try out the guide.',
  'res_correct': 'correct', 'res_cop': 'correct or partly', 'res_coll': 'collocation', 'res_kappa': 'Cohen’s kappa', 'res_po': 'observed agreement',
  'res_ci': '95% confidence interval', 'res_n': 'judged', 'export': 'Download all judgements as CSV',
  'guide': 'Guide and decision procedure', 'b_login': 'The second annotator signs in with the user name “annotator”; the server administrator creates the password (DEPLOY guide). The annotators do not see each other’s judgements.',
  'item_of': 'unit {k} of {n}', 'done_all': 'All units of this set are judged.', 'back': 'Human evaluation',
  'save_next': 'Save and next', 'skip': 'Next', 'note': 'Note (optional)', 'saved_before': 'Your earlier judgement is stored; if you change it, the new one replaces it.',
  'q_pairs': 'Are the two texts translations of each other?',
  'v_correct_pairs': 'Correct — the two sides fully translate each other', 'v_partial_pairs': 'Partly — one side has an extra or a missing sentence',
  'v_wrong_pairs': 'Wrong — not a translation',
  'q_equiv': 'Is the word marked in turquoise the translator’s equivalent of the word marked in gold?',
  'v_correct_equiv': 'Correct', 'v_partial_equiv': 'Partly — part of the equivalent or with an extra word', 'v_wrong_equiv': 'Wrong',
  'q_dict': 'Is the dictionary translation the translation of the headword in this example?',
  'v_correct_dict': 'Correct', 'v_partial_dict': 'Partly — part of an idiom or a combination', 'v_wrong_dict': 'Wrong',
  'cand': 'Candidate', 'pattern': 'pattern', 'ref': 'In the reference corpus', 'ref_none': 'not in the reference corpus',
  'q1': '1. Does the unit consist of at least two content words in a direct syntactic relation?',
  'q1_yes': 'Yes', 'q1_no': 'No — not analysed',
  'q2': '2. Does the unit belong to an excluded type?',
  'q2_none': 'No', 'q2_proverb': 'Proverb or saying', 'q2_sentence': 'Full sentence', 'q2_simile': 'Simile', 'q2_formula': 'Speech formula',
  'q2_name': 'Proper name or nickname', 'q2_paired': 'Paired or reduplicated word', 'q2_auxiliary': 'Auxiliary verb construction',
  'q3': '3. Has the combination a holistic figurative meaning here, and is the base lost in a paraphrase?',
  'q3_no': 'No', 'q3_yes': 'Yes — phraseological unit',
  'q4': '4. Is the choice of the collocate restricted (does a synonym make the combination unnatural)?',
  'q4_yes': 'Yes', 'q4_no': 'No', 'q4_disputed': 'Disputed — borderline',
  'q4b': '4a. Is it recurrent in the text and rendered with a ready-made pattern in the translation?', 'q4b_no': 'No — free combination', 'q4b_yes': 'Yes — stable free combination',
  'q6': '6. Type of the equivalent in the translation', 'q6_collocation': 'Collocation', 'q6_single': 'Single word', 'q6_descriptive': 'Descriptive rendering', 'q6_omitted': 'Omitted',
  'eq': 'Equivalent marked by the platform', 'eq_correct': 'Correct', 'eq_partial': 'Partly', 'eq_wrong': 'Wrong', 'eq_none': 'None marked',
  'cat': 'Result', 'cat_collocation': 'collocation (question 5: reference corpus)', 'cat_borderline': 'borderline unit', 'cat_stable_free': 'stable free combination',
  'cat_free': 'free combination', 'cat_phraseological': 'phraseological unit', 'cat_excluded': 'excluded type', 'cat_not_unit': 'not a unit of analysis',
  'calib_title': 'Calibrating the logDice threshold (English candidates)',
  'calib_note': 'Against the candidates the researcher judged “collocation”: precision, recall and F1 of the rule “at least {f} times in the reference corpus and logDice ≥ t”. Best F1: t = {t}.',
  'c_t': 't', 'c_p': 'precision', 'c_r': 'recall', 'c_f': 'F1',
  'forbidden': 'This page is for the researcher and the second annotator.',
 },
 'ru': {
  'title': 'Экспертная проверка',
  'lead': 'Ручная оценка результатов платформы: выборки, два аннотатора, точность и согласие (диссертация, раздел 1.1.4).',
  'task_pairs': 'Пары предложений', 'task_equiv': 'Пословные эквиваленты', 'task_colloc_uz': 'Узбекские кандидаты в коллокации',
  'task_colloc_en': 'Английские кандидаты в коллокации', 'task_dict': 'Переводы корпусного словаря',
  'd_pairs': 'Верна ли автоматически выровненная пара предложений?', 'd_equiv': 'Является ли эквивалент со страницы поиска словом переводчика для этого слова?',
  'd_colloc_uz': 'Одно употребление кандидата по порядку решений (вопросы 1–4 и 6).', 'd_colloc_en': 'Одно употребление кандидата по порядку решений (вопросы 1–4 и 6).',
  'd_dict': 'Верен ли перевод из словаря в данном примере?',
  'set_train': 'Обучающий набор', 'set_main': 'Основная выборка', 'col_task': 'Задача', 'open': 'Открыть',
  'annot_a': 'A (исследователь)', 'annot_b': 'B (второй аннотатор)', 'you_are': 'Вы — аннотатор {w}.',
  'res_title': 'Результаты (основная выборка)', 'res_none': 'В основной выборке ещё нет оценок. Начните с обучающего набора: 50 единиц для проверки инструкции.',
  'res_correct': 'верно', 'res_cop': 'верно или частично', 'res_coll': 'коллокация', 'res_kappa': 'каппа Коэна', 'res_po': 'наблюдаемое согласие',
  'res_ci': '95%-й доверительный интервал', 'res_n': 'оценено', 'export': 'Скачать все оценки в CSV',
  'guide': 'Инструкция и порядок решений', 'b_login': 'Второй аннотатор входит под именем «annotator»; пароль создаёт администратор сервера (инструкция DEPLOY). Аннотаторы не видят оценок друг друга.',
  'item_of': 'единица {k} из {n}', 'done_all': 'Все единицы этого набора оценены.', 'back': 'Экспертная проверка',
  'save_next': 'Сохранить и далее', 'skip': 'Далее', 'note': 'Примечание (необязательно)', 'saved_before': 'Ваша прежняя оценка сохранена; при изменении она будет заменена.',
  'q_pairs': 'Являются ли эти тексты переводом друг друга?',
  'v_correct_pairs': 'Верно — стороны полностью соответствуют', 'v_partial_pairs': 'Частично — на одной стороне лишнее или недостающее предложение',
  'v_wrong_pairs': 'Неверно — не перевод',
  'q_equiv': 'Является ли слово, отмеченное бирюзовым, эквивалентом переводчика для слова, отмеченного золотым?',
  'v_correct_equiv': 'Верно', 'v_partial_equiv': 'Частично — часть эквивалента или с лишним словом', 'v_wrong_equiv': 'Неверно',
  'q_dict': 'Является ли перевод из словаря переводом заглавного слова в этом примере?',
  'v_correct_dict': 'Верно', 'v_partial_dict': 'Частично — часть идиомы или сочетания', 'v_wrong_dict': 'Неверно',
  'cand': 'Кандидат', 'pattern': 'модель', 'ref': 'В опорном корпусе', 'ref_none': 'в опорном корпусе не встречается',
  'q1': '1. Состоит ли единица минимум из двух знаменательных слов в прямой синтаксической связи?',
  'q1_yes': 'Да', 'q1_no': 'Нет — не анализируется',
  'q2': '2. Относится ли единица к исключаемому типу?',
  'q2_none': 'Нет', 'q2_proverb': 'Пословица или поговорка', 'q2_sentence': 'Полное предложение', 'q2_simile': 'Сравнение', 'q2_formula': 'Речевая формула',
  'q2_name': 'Имя собственное или прозвище', 'q2_paired': 'Парное или повторное слово', 'q2_auxiliary': 'Конструкция со вспомогательным глаголом',
  'q3': '3. Имеет ли сочетание здесь целостное образное значение, и теряется ли основа при перефразировании?',
  'q3_no': 'Нет', 'q3_yes': 'Да — фразеологическая единица',
  'q4': '4. Ограничен ли выбор коллоката (делает ли синоним сочетание неестественным)?',
  'q4_yes': 'Да', 'q4_no': 'Нет', 'q4_disputed': 'Спорно — пограничный случай',
  'q4b': '4а. Повторяется ли оно в тексте и передано ли готовым шаблоном в переводе?', 'q4b_no': 'Нет — свободное сочетание', 'q4b_yes': 'Да — устойчивое свободное сочетание',
  'q6': '6. Тип эквивалента в переводе', 'q6_collocation': 'Коллокация', 'q6_single': 'Одно слово', 'q6_descriptive': 'Описательный перевод', 'q6_omitted': 'Опущено',
  'eq': 'Эквивалент, отмеченный платформой', 'eq_correct': 'Верно', 'eq_partial': 'Частично', 'eq_wrong': 'Неверно', 'eq_none': 'Не отмечен',
  'cat': 'Результат', 'cat_collocation': 'коллокация (вопрос 5: опорный корпус)', 'cat_borderline': 'пограничная единица', 'cat_stable_free': 'устойчивое свободное сочетание',
  'cat_free': 'свободное сочетание', 'cat_phraseological': 'фразеологическая единица', 'cat_excluded': 'исключаемый тип', 'cat_not_unit': 'не единица анализа',
  'calib_title': 'Калибровка порога logDice (английские кандидаты)',
  'calib_note': 'По кандидатам, оценённым исследователем как «коллокация»: точность, полнота и F1 правила «не менее {f} раз в опорном корпусе и logDice ≥ t». Лучший F1: t = {t}.',
  'c_t': 't', 'c_p': 'точность', 'c_r': 'полнота', 'c_f': 'F1',
  'forbidden': 'Эта страница для исследователя и второго аннотатора.',
 },
}


def t(lang, k):
    return html.escape(L.get(lang, L['uz']).get(k) or L['uz'].get(k, k))


def pct(x, lang):
    return ui.format_decimal(100 * x, lang, 1) + ' %' if x is not None else '—'


def ci_text(w, lang):
    if not w:
        return '—'
    p, lo, hi = w
    return '%s <span class="tc-muted tc-small">(%s–%s)</span>' % (pct(p, lang), pct(lo, lang), pct(hi, lang))


def results_html(lang, res, calib=None):
    """Results of the main sample; used on this page and on the statistics page."""
    rows = []
    for task in V.TASKS:
        r = res.get(task) or {}
        a, b, ag = r.get('A') or {}, r.get('B') or {}, r.get('agreement')
        if not a.get('n') and not b.get('n'):
            continue
        key = 'collocation' if task.startswith('colloc') else 'correct'
        lbl = t(lang, 'res_coll') if task.startswith('colloc') else t(lang, 'res_correct')
        cop = '' if task.startswith('colloc') else ci_text(a.get('correct_or_partial'), lang)
        rows.append('<tr><td>%s</td><td class="r tc-num">%s / %s</td><td class="tc-num">%s: %s</td><td class="tc-num">%s</td>'
                    '<td class="r tc-num">%s</td><td class="r tc-num">%s</td></tr>'
                    % (t(lang, 'task_' + task), ui.format_number(a.get('n', 0), lang), ui.format_number(r.get('n_items', 0), lang),
                       lbl, ci_text(a.get(key), lang), cop, ui.format_number(b.get('n', 0), lang),
                       ('κ = %s; %s %s' % (ui.format_decimal(ag['kappa'], lang, 2), t(lang, 'res_po'), pct(ag['po'], lang))) if ag else '—'))
    if not rows:
        return '<p class="tc-muted">%s</p>' % t(lang, 'res_none')
    out = ('<div class="tc-panel tc-scroll" style="padding:4px 8px"><table class="tc-table"><thead><tr><th>%s</th><th class="r">A: %s</th><th>A: %s</th>'
           '<th>A: %s</th><th class="r">B: %s</th><th class="r">%s</th></tr></thead><tbody>%s</tbody></table></div>'
           '<p class="tc-section__note" style="margin-top:8px">%s</p>'
           % (t(lang, 'col_task'), t(lang, 'res_n'), t(lang, 'res_ci'), t(lang, 'res_cop'), t(lang, 'res_n'), t(lang, 'res_kappa'), ''.join(rows),
              html.escape({'uz': 'Ishonch oralig‘i — Uilson usuli (Wilson, 1927). Kappa ikki annotator umumiy baholagan birliklar bo‘yicha (Cohen, 1960); κ ≥ 0,8 yaxshi, 0,67–0,8 ehtiyotkor xulosa uchun yetarli (Artstein va Poesio, 2008, b. 576).',
                           'en': 'Interval by the Wilson method (Wilson, 1927). Kappa over the units judged by both annotators (Cohen, 1960); κ ≥ 0.8 good, 0.67–0.8 enough for tentative conclusions (Artstein & Poesio, 2008, p. 576).',
                           'ru': 'Интервал по методу Уилсона (Wilson, 1927). Каппа по единицам, оценённым обоими аннотаторами (Cohen, 1960); κ ≥ 0,8 — хорошо, 0,67–0,8 — достаточно для осторожных выводов (Artstein & Poesio, 2008, p. 576).'}[lang])))
    if calib:
        crow = ''.join('<tr%s><td class="tc-num">%s</td><td class="r tc-num">%s</td><td class="r tc-num">%s</td><td class="r tc-num">%s</td><td class="r tc-num">%s / %s</td></tr>'
                       % (' class="tc-total"' if r_ is calib['best'] else '', ui.format_decimal(r_['t'], lang, 1),
                          pct(r_['precision'], lang) if r_['precision'] is not None else '—', pct(r_['recall'], lang) if r_['recall'] is not None else '—',
                          ui.format_decimal(r_['f1'], lang, 2), r_['tp'], r_['fp']) for r_ in calib['rows'] if r_['t'] >= 4)
        out += ('<h3 style="margin-top:22px">%s</h3><p class="tc-section__note">%s</p><div class="tc-panel tc-scroll" style="padding:4px 8px"><table class="tc-table">'
                '<thead><tr><th>%s</th><th class="r">%s</th><th class="r">%s</th><th class="r">%s</th><th class="r">TP / FP</th></tr></thead><tbody>%s</tbody></table></div>'
                % (t(lang, 'calib_title'), t(lang, 'calib_note').replace('{f}', str(calib['min_f'])).replace('{t}', ui.format_decimal(calib['best']['t'], lang, 1)),
                   t(lang, 'c_t'), t(lang, 'c_p'), t(lang, 'c_r'), t(lang, 'c_f'), crow))
    return out


def render_overview(lang, user, is_admin, index_items):
    prog = V.progress()
    who = V.ANNOTATORS.get(user)
    rows = []
    for task in V.TASKS:
        p = prog[task]
        cells = ''.join('<td class="r tc-num">%s / %s</td>' % (p[w][s], p[s]) for s in ('train', 'main') for w in ('A', 'B'))
        btns = ''
        if who:
            btns = ' '.join('<a class="tc-chip" href="%s">%s</a>' % (ui.with_lang('/baholash/%s?set=%s' % (task, s), lang), t(lang, 'set_' + s))
                            for s in ('train', 'main'))
        rows.append('<tr><td><b>%s</b><br><span class="tc-small tc-muted">%s</span></td>%s<td>%s</td></tr>'
                    % (t(lang, 'task_' + task), t(lang, 'd_' + task), cells, btns))
    head = ('<tr><th rowspan="2">%s</th><th class="r" colspan="2">%s</th><th class="r" colspan="2">%s</th><th rowspan="2"></th></tr>'
            '<tr><th class="r">A</th><th class="r">B</th><th class="r">A</th><th class="r">B</th></tr>'
            % (t(lang, 'col_task'), t(lang, 'set_train'), t(lang, 'set_main')))
    me = ('<p class="tc-dnote">%s</p>' % t(lang, 'you_are').replace('{w}', who)) if who else ''
    extra = ''
    if is_admin:
        extra = ('<p style="margin-top:14px"><a href="/api/baholash/export.csv">%s</a></p><p class="tc-section__note" style="margin-top:6px">%s</p>'
                 % (t(lang, 'export'), t(lang, 'b_login')))
    body = ('<h1>%s</h1><p class="tc-lead">%s</p>%s<section class="tc-section"><div class="tc-panel tc-scroll" style="padding:4px 8px">'
            '<table class="tc-table"><thead>%s</thead><tbody>%s</tbody></table></div>'
            '<p style="margin-top:12px"><a href="%s">%s</a></p>%s</section>'
            '<section class="tc-section"><h2>%s</h2>%s</section>'
            % (t(lang, 'title'), t(lang, 'lead'), me, head, ''.join(rows), ui.with_lang('/yoriqnoma', lang), t(lang, 'guide'), extra,
               t(lang, 'res_title'), results_html(lang, V.results(), V.calibration(index_items))))
    return ui.page(lang, L[lang]['title'], body, '/baholash', is_admin)


def _pair(lang, p, q_lang, q_spans, o_spans):
    import search_plus as SP
    o_lang = 'en' if q_lang == 'uz' else 'uz'
    return ui.pair_html(lang, p.get('book'), q_lang, SP.highlight(p.get(q_lang) or '', q_spans, SP.QUERY_CLASS),
                        p.get('uz_page') if q_lang == 'uz' else p.get('en_page'),
                        SP.highlight(p.get(o_lang) or '', o_spans, SP.EQUIV_CLASS),
                        p.get('en_page') if q_lang == 'uz' else p.get('uz_page'))


def _radios(lang, name, options, prefix, current=None, disabled=False):
    return ''.join('<label class="tc-opt"><input type="radio" name="%s" value="%s"%s%s> <span>%s</span><kbd>%d</kbd></label>'
                   % (name, o, ' checked' if o == current else '', ' disabled' if disabled else '', t(lang, prefix + o), i + 1)
                   for i, o in enumerate(options))


def render_item(lang, user, is_admin, task, which, item_id, corpus_by_id, index_items):
    import equivalents as E
    who = V.ANNOTATORS.get(user)
    rows = V.items(task, which)
    it = V.item(task, item_id) if item_id else V.next_item(task, user, which)
    back = '<p class="tc-small tc-crumb"><a href="%s">%s</a></p>' % (ui.with_lang('/baholash', lang), t(lang, 'back'))
    title = '%s: %s' % (L[lang]['task_' + task], L[lang]['set_' + which])
    if not it:
        body = back + '<h1>%s</h1><div class="tc-panel" style="margin-top:20px"><p>%s</p></div>' % (html.escape(title), t(lang, 'done_all'))
        return ui.page(lang, title, body, '/baholash', is_admin, narrow=True)
    k = next((i for i, r in enumerate(rows) if r['id'] == it['id']), 0) + 1
    prev = (V.annotations()['records'].get(task, {}).get(it['id'], {}) or {}).get(who)
    labels = (prev or {}).get('labels', {})
    p = corpus_by_id.get(it['pid']) or {}
    if task == 'pairs':
        content = _pair(lang, p, 'uz', [], [])
        form = ('<fieldset class="tc-q"><legend>%s</legend>%s</fieldset>'
                % (t(lang, 'q_pairs'), ''.join('<label class="tc-opt"><input type="radio" name="verdict" value="%s"%s> <span>%s</span><kbd>%d</kbd></label>'
                                               % (v, ' checked' if v == labels.get('verdict') else '', t(lang, 'v_%s_pairs' % v), i + 1) for i, v in enumerate(V.VERDICTS))))
    elif task in ('equiv', 'dict'):
        q_lang = it['lang']
        o_sp = [tuple(x) for x in it['o']] if task == 'equiv' else [tuple(it['o'])]
        content = ''
        if task == 'dict':
            content = ('<p class="tc-entry__meta"><span class="tc-serif" lang="%s" style="font-size:1.6rem">%s</span> → '
                       '<span class="tc-serif" lang="%s" style="font-size:1.6rem">%s</span> <span class="tc-muted tc-num">(%s)</span></p>'
                       % (q_lang, html.escape(it['head']), 'en' if q_lang == 'uz' else 'uz', html.escape(it['text']), it['count']))
        content += _pair(lang, p, q_lang, [tuple(it['q'])], o_sp)
        form = ('<fieldset class="tc-q"><legend>%s</legend>%s</fieldset>'
                % (t(lang, 'q_' + task), ''.join('<label class="tc-opt"><input type="radio" name="verdict" value="%s"%s> <span>%s</span><kbd>%d</kbd></label>'
                                                % (v, ' checked' if v == labels.get('verdict') else '', t(lang, 'v_%s_%s' % (v, task)), i + 1)
                                                for i, v in enumerate(V.VERDICTS))))
    else:
        q_lang = task[-2:]
        cand = next((c for c in index_items if c['id'] == it['cid']), {})
        spans = [tuple(x) for x in it['spans']]
        o_spans, _ = E.equivalent_spans(it['pid'], q_lang, spans)
        ref = cand.get('ref')
        ref_txt = ''
        if ref is not None:
            ref_txt = (' %s: f = %s%s' % (t(lang, 'ref'), ui.format_number(ref.get('f', 0), lang),
                                         (', logDice %s' % ui.format_decimal(ref['log_dice'], lang, 2)) if ref.get('log_dice') is not None else '')
                       if ref.get('f') else '; ' + t(lang, 'ref_none'))
        content = ('<p class="tc-entry__meta">%s: <a class="tc-serif" lang="%s" style="font-size:1.4rem" href="%s">%s</a> '
                   '<span class="tc-muted">(%s %s; %s)%s</span></p>'
                   % (t(lang, 'cand'), q_lang, ui.with_lang('/kollokatsiya/' + urllib.parse.quote(cand.get('id', '')), lang),
                      html.escape(cand.get('display') or ''), t(lang, 'pattern'), html.escape(ui.pattern_label(cand.get('pattern', ''), lang)),
                      html.escape(ui.count_phrase(cand.get('freq', 0), 'occurrences_word', lang)), html.escape(ref_txt)))
        content += _pair(lang, p, q_lang, spans, o_spans)
        qs = [('q1', 'q1_'), ('q2', 'q2_'), ('q3', 'q3_'), ('q4', 'q4_'), ('q4b', 'q4b_'), ('q6', 'q6_'), ('eq', 'eq_')]
        form = ''.join('<fieldset class="tc-q" data-q="%s"><legend>%s</legend>%s</fieldset>'
                       % (name, t(lang, name), _radios(lang, name, V.COLLOC_FIELDS[name], pre, labels.get(name))) for name, pre in qs)
        form += '<p class="tc-q__result" id="tc-cat" aria-live="polite"></p>'
    cats = json.dumps({c: L[lang]['cat_' + c] for c in V.CATEGORIES}, ensure_ascii=False)
    nxt_skip = V.items(task, which)
    after = next((r for r in nxt_skip[k:]), None)
    skip_url = ui.with_lang('/baholash/%s?set=%s&item=%s' % (task, which, urllib.parse.quote(after['id'])), lang) if after else ''
    js = ('<script>(function(){var f=document.getElementById("tc-ann");var cats=%s,lblCat=%s;'
          'function val(n){var e=f.querySelector("input[name="+n+"]:checked");return e?e.value:null}'
          'function cat(){var q1=val("q1");if(!q1)return null;if(q1=="no")return"not_unit";var q2=val("q2");if(q2&&q2!="none")return"excluded";'
          'if(val("q3")=="yes")return"phraseological";var q4=val("q4");if(q4=="no")return val("q4b")=="yes"?"stable_free":"free";'
          'if(q4=="disputed")return"borderline";if(q4=="yes")return"collocation";return null}'
          'function upd(){var c=f.querySelector("[data-q]");if(!c)return;var q1=val("q1"),q2=val("q2"),q3=val("q3"),q4=val("q4");'
          'function show(n,on){var e=f.querySelector("[data-q="+n+"]");if(e){e.hidden=!on;e.querySelectorAll("input").forEach(function(i){i.disabled=!on})}}'
          'var stop1=q1=="no",stop2=stop1||(q2&&q2!="none"),stop3=stop2||q3=="yes";show("q2",!stop1);show("q3",!stop2);show("q4",!stop3);'
          'show("q4b",!stop3&&q4=="no");show("q6",!stop1);show("eq",!stop1);var k=cat();document.getElementById("tc-cat").textContent=k?lblCat+": "+cats[k]:""}'
          'f.addEventListener("change",upd);upd();'
          'document.addEventListener("keydown",function(e){if(e.target.tagName=="TEXTAREA")return;var n=parseInt(e.key,10);if(n>=1&&n<=9){'
          'var groups=[].slice.call(f.querySelectorAll("fieldset")).filter(function(g){return!g.hidden});'
          'var g=groups.filter(function(g){return!g.querySelector("input:checked")})[0]||groups[groups.length-1];if(!g)return;'
          'var opts=g.querySelectorAll("input");if(opts[n-1]){opts[n-1].checked=true;upd()}}if(e.key=="Enter"&&!e.shiftKey){e.preventDefault();f.requestSubmit()}});'
          'f.addEventListener("submit",function(e){e.preventDefault();var labels={};f.querySelectorAll("input[type=radio]:checked:not(:disabled)").forEach(function(i){labels[i.name]=i.value});'
          'var err=document.getElementById("tc-ann-err");err.textContent="";'
          'fetch("/api/baholash",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({task:f.dataset.task,item:f.dataset.item,'
          'labels:labels,note:f.note.value})}).then(function(r){return r.json()}).then(function(d){if(d.ok){location.href=f.dataset.next}else{err.textContent=d.error||"error"}})'
          '.catch(function(){err.textContent="network"})})})();</script>'
          % (cats, json.dumps(L[lang]['cat'], ensure_ascii=False)))
    nxt = ui.with_lang('/baholash/%s?set=%s' % (task, which), lang)
    body = ('%s<h1>%s</h1><p class="tc-lead tc-num">%s</p>%s<div style="margin-top:18px">%s</div>'
            '<form class="tc-ann" id="tc-ann" data-task="%s" data-item="%s" data-next="%s">%s'
            '<label class="tc-ann__note">%s<textarea name="note" rows="2" maxlength="500">%s</textarea></label>'
            '<p class="tc-error" id="tc-ann-err" role="alert"></p><div class="tc-hero__btns" style="margin-top:6px">'
            '<button class="tc-btn" type="submit">%s</button>%s</div></form>%s'
            % (back, html.escape(title), t(lang, 'item_of').replace('{k}', str(k)).replace('{n}', str(len(rows))),
               ('<p class="tc-dnote">%s</p>' % t(lang, 'saved_before')) if prev else '', content,
               task, html.escape(it['id']), html.escape(nxt), form, t(lang, 'note'), html.escape((prev or {}).get('note', '')), t(lang, 'save_next'),
               ('<a class="tc-btn tc-btn--ghost" href="%s">%s</a>' % (html.escape(skip_url), t(lang, 'skip'))) if skip_url else '', js))
    return ui.page(lang, title, body, '/baholash', is_admin, narrow=True)
