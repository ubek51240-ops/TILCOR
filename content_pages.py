"""Server-rendered information pages in three interface languages:
/about_project.html, /sources_rights.html, /methodology.html, /annotation_guidelines.html,
/methodology_statistics.html.

Rules for this file:
  * every number is computed from the data at request time or taken from a cited source;
  * nothing is claimed that the platform does not do (no "verified by hash", no agreement figure
    before a second annotator has worked, no reference-corpus statistics before they are computed);
  * the methodological content follows paragraph 1.1 of the dissertation (claude/1.1-kollokatsiya-mezonlari.md).
Text fragments are written by hand and contain only simple, trusted markup (<em>, <strong>, <a>).
"""
import html
import re

import ui_components as ui

T = {}  # T[lang][key] -> HTML fragment


def tr(lang, key, **fmt):
    s = T.get(lang, {}).get(key) or T['uz'].get(key, key)
    for k, v in fmt.items():
        s = s.replace('{' + k + '}', str(v))
    return s


def n(value, lang):
    return ui.format_number(int(value or 0), lang)


# ---------------------------------------------------------------------------------------------
# Shared texts
# ---------------------------------------------------------------------------------------------
T['uz'] = {
    # about
    'about_title': 'Loyiha haqida',
    'about_lead': 'TILCOR — o‘zbek va ingliz tillaridagi badiiy asarlar va ularning tarjimalaridan tuzilgan parallel korpus. U kollokatsiyalar tarjimasini o‘rganish uchun PhD dissertatsiyasi doirasida yaratilmoqda.',
    'about_topic_label': 'Dissertatsiya mavzusi',
    'about_topic': '«Tarjima va teng matnlar parallel korpusida o‘zaro faol birikuvchi (kollokatsion) so‘zlar tadqiqi (o‘zbek va ingliz tillari misolida)»',
    'about_researcher_label': 'Tadqiqotchi',
    'about_university_label': 'Oliy ta’lim muassasasi',
    'about_university': 'Buxoro davlat universiteti',
    'about_specialty_label': 'Ixtisoslik',
    'about_specialty': '10.00.06 — Qiyosiy adabiyotshunoslik, chog‘ishtirma tilshunoslik va tarjimashunoslik',
    'about_what_title': 'Platforma nima qiladi',
    'about_what': [
        'So‘rov tilini aniqlaydi va so‘zning korpusdagi barcha shakllarini hamda bir o‘zakli so‘zlarni topadi.',
        'Har bir topilgan gapning ikkinchi kitobdagi parallel gapini asar va sahifasi bilan ko‘rsatadi.',
        'Tarjima ekvivalenti sifatida faqat tarjimonning kitobdagi so‘zlarini beradi; AI taklifi va ma’lumotnoma alohida belgilanadi.',
        'Kalit so‘zni kontekst bilan ko‘rsatadi (KWIC) va natijani CSV faylga yuklab berish imkonini beradi.',
        'Korpusdan kollokatsiya nomzodlarini avtomatik ajratadi va ularni lingvistik tekshiruvdan o‘tmagan deb belgilaydi.',
    ],
    'about_state_title': 'Hozirgi holat',
    'about_state': 'Korpusda {pairs} ta parallel juftlik bor, ulardan {confirmed} tasini tadqiqotchi tasdiqlagan. Tayanch korpus bo‘yicha statistik ko‘rsatkichlar hali hisoblanmagan. Bosma lug‘atlardan olingan yozuvlar OCR xatolari tuzatilmaguncha yopiq.',
    'about_tech_title': 'Texnik asos',
    'about_tech': 'Server Python tilida yozilgan. Korpus JSON fayllar va SQLite bazasida saqlanadi. Ingliz so‘z oilalari uchun NLTK WordNet, o‘zbek so‘zlari uchun qoidaga asoslangan normallashtirish va qo‘shimchalarni ajratish qo‘llanadi. Sahifalar server tomonida, uch tilda hosil qilinadi.',
    # sources
    'src_title': 'Manbalar va mualliflik huquqi',
    'src_lead': 'Korpus ikki asar–tarjima juftligidan iborat. Har bir matn uchun foydalanilgan nusxa, sahifa qoidasi va hajmi ko‘rsatiladi.',
    'src_pair_kvk': 'Birinchi juftlik: o‘zbekchadan inglizchaga',
    'src_pair_oms': 'Ikkinchi juftlik: inglizchadan o‘zbekchaga',
    'src_role_original': 'Asliyat',
    'src_role_translation': 'Tarjima',
    'src_edition': 'Nashr',
    'src_copy': 'Korpusdagi nusxa',
    'src_pages': 'Sahifa qoidasi',
    'src_size': 'Hajmi',
    'src_tokens_full': 'segmentlangan matnda {tokens} ta so‘z qo‘llanishi (token), {types} ta shakl',
    'src_pairs': 'parallel juftliklar: {pairs}; tadqiqotchi tasdiqlagani: {confirmed}',
    'src_kvk_uz_edition': 'Abdulhamid Cho‘lpon. «Kecha va kunduz». Toshkent: «Sharq», 2000. Birinchi nashr: 1936.',
    'src_kvk_uz_copy': 'ziyouz.com kutubxonasidagi elektron nusxa (2000-yilgi «Sharq» nashri matni; sahifalanishi bosma kitobdan farq qiladi).',
    'src_kvk_uz_pages': 'Elektron nusxaning pastki kolontitulidagi raqam; roman matni 3–265-betlar. 266–272-betlardagi maqola korpusga kirmaydi.',
    'src_kvk_en_edition': 'Cho‘lpon. «Night and Day: A Novel». Tarjimon Christopher Fort. Boston: Academic Studies Press, 2019. DOI 10.1515/9781644690482.',
    'src_kvk_en_copy': 'Nashriyot PDF fayli.',
    'src_kvk_en_pages': 'Bosma sahifa raqami (yuqori kolontitul); roman matni 45–271-betlar.',
    'src_oms_en_edition': 'Ernest Hemingway. «The Old Man and the Sea». Birinchi nashr: 1952.',
    'src_oms_en_copy': 'Asiaing.com elektron nusxasi; qaysi bosma nashrdan olingani aniqlanmagan.',
    'src_oms_en_pages': 'Matn ichidagi [N] belgilari bo‘yicha bosma sahifa: 9–125-betlar.',
    'src_oms_uz_edition': 'Ernest Xeminguey. «Chol va dengiz». Tarjimon Ibrohim G‘ofurov (titul varag‘idagi yozilishi). Toshkent: «Yosh gvardiya», 1986.',
    'src_oms_uz_copy': 'kutubxonachi.uz elektron nusxasi.',
    'src_oms_uz_pages': 'Elektron nusxa sahifasi (1–46). U 1986-yilgi bosma nashr sahifasiga mos emas, shuning uchun har doim «elektron nusxa» deb ko‘rsatiladi.',
    'src_excluded_title': 'Korpusga kiritilmagan matnlar',
    'src_excluded': 'R. L. Stivenson, «Xazinalar oroli» (A. Yoqubov tarjimasi, ruschadan) va «Animal Farm / Molxona» korpusga kiritilmaydi (tadqiqotchi qarori, 13.10.2026). Yangi asar faqat tadqiqotchi qarori bilan qo‘shiladi.',
    'src_rights_title': 'Mualliflik huquqi',
    'src_rights': 'Matnlar mualliflik huquqi egalariga tegishli. Platforma to‘liq matnni ko‘rsatmaydi va yuklab berishga ruxsat bermaydi: qidiruvda faqat so‘rov topilgan gap va uning parallel gapi, ilmiy tahlil uchun zarur hajmda ko‘rsatiladi. Ma’lumot fayllari va baza tashqaridan ochiq emas.',
    # methodology
    'm_title': 'Metodologiya',
    'm_lead': 'Bu sahifa platformada amalda qo‘llanayotgan qoidalarni bayon qiladi. Nazariy asoslash dissertatsiyaning 1.1-paragrafida berilgan.',
    'm_def_title': '1. Kollokatsiyaning ishchi ta’rifi',
    'm_def_intro': 'Birikma quyidagi to‘rt lingvistik shart bir vaqtda bajarilganda kollokatsiya deb hisoblanadi:',
    'm_def_items': [
        'u kamida ikki mustaqil so‘zdan iborat bo‘lib, komponentlari o‘zaro bevosita sintaktik aloqada bo‘ladi;',
        'asos komponenti o‘z to‘g‘ri ma’nosini saqlaydi;',
        'kollokat tanlovi til an’anasi bilan cheklangan, ya’ni uning o‘rniga ma’nodosh so‘z qo‘yilganda birikma g‘ayritabiiy bo‘ladi;',
        'birikma yaxlit obrazli ko‘chma ma’noga ega emas.',
    ],
    'm_def_note': 'Lingvistik shartlar birlikning toifasini, statistik dalil esa uning maqomini belgilaydi.',
    'm_status_title': 'Maqomlar',
    'm_statuses': [
        ('tasdiqlangan kollokatsiya', 'lingvistik shartlarga javob beradi va tildagi odatiyligi tayanch korpusdagi chastota hamda assotsiatsiya ko‘rsatkichlari bilan tasdiqlangan;'),
        ('kollokatsiya nomzodi', 'lingvistik shartlarga javob beradi, lekin statistik tasdig‘i hali olinmagan yoki tayanch korpusda ma’lumot yetarli emas;'),
        ('barqaror erkin birikma', 'kollokat erkin almashadi, lekin birikma matnda takrorlanadi va tarjimada tayyor qolip bilan beriladi;'),
        ('frazeologik birlik', 'yaxlit obrazli ko‘chma ma’noga ega;'),
        ('chegaraviy holat', 'almashtirish testi bo‘yicha bahs saqlanib qolgan; natijalar u bilan va usiz alohida hisoblanadi.'),
    ],
    'm_exclusions': '<strong>Tahlilga olinmaydi:</strong> maqol va matallar, to‘liq gaplar, o‘xshatishlar (<em>anorday qizarmoq</em>), nutq formulalari, atoqli otlar va laqablar, juft va takroriy so‘zlar, ko‘makchi fe’lli grammatik qurilmalar (<em>chiqib ketmoq</em>, <em>olib kelmoq</em>).',
    'm_unit': '<strong>Tahlil birligi</strong> — kontekstual ma’nosi bilan birga olingan kollokatsiya uchrashi. Shakldosh birikmalar (masalan, <em>katta xotin</em>: «yoshi kattaroq ayollar» va «to‘ng‘ich xotin») har bir uchrashda alohida ma’no belgisi oladi.',
    'm_corpus_title': '2. Korpus tarkibi va sahifa qoidasi',
    'm_corpus': 'Korpus ikki juftlikdan iborat: Cho‘lponning «Kecha va kunduz» romani va uning Christopher Fort qilgan inglizcha tarjimasi «Night and Day» (o‘zbekchadan inglizchaga); E. Hemingwayning «The Old Man and the Sea» qissasi va uning Ibrohim G‘ofurov qilgan o‘zbekcha tarjimasi «Chol va dengiz» (inglizchadan o‘zbekchaga). Har bir asar faqat o‘z tarjimasi bilan qiyoslanadi.',
    'm_pages': 'Sahifa har doim foydalanilgan nusxada bosilgan raqam bo‘yicha ko‘rsatiladi: «Kecha va kunduz» — ziyouz.com nusxasi (3–265); «Night and Day» — bosma sahifa (45–271); «The Old Man and the Sea» — matndagi [N] belgilari (9–125); «Chol va dengiz» — elektron nusxa sahifasi (1–46), har doim «elektron nusxa» degan izoh bilan.',
    'm_text_title': '3. Matnni qayta ishlash va so‘z oilalari',
    'm_text': [
        'Kitob matni o‘zgartirilmaydi. Qidiruv uchun matnning normallashtirilgan nusxasi tuziladi: o‘zbekcha tutuq belgilari (<em>‘ ’ ʻ ʼ \'</em>) bitta shaklga keltiriladi, kirill yozuvidagi o‘zbekcha so‘rov lotin yozuviga o‘giriladi. Topilgan so‘z belgilar o‘rni bo‘yicha asl matnning o‘zida ajratib ko‘rsatiladi.',
        'O‘zbek so‘zlari qoidaga asoslangan usulda qo‘shimchalaridan ajratiladi; fe’llar lug‘at shaklida (<em>-moq</em>), otlar bosh kelishikda beriladi. Inglizcha so‘z oilasi NLTK WordNet (lemmatizatsiya va hosila so‘zlar) hamda noto‘g‘ri fe’llar ro‘yxati bilan aniqlanadi.',
        'Topilgan shakllar to‘rt guruhga bo‘linadi: aynan shakl, grammatik shakl, yasama so‘z, qo‘shma so‘z. Interfeysda qisqartma ishlatilmaydi.',
    ],
    'm_align_title': '4. Gaplarni tekislash',
    'm_align': 'Juftliklar avtomatik tekislangan. Ikki kitob gaplari hunalign dasturi (Varga va boshq., 2007) bilan qayta tekislandi: u gap uzunligi modelini (Gale va Church, 1993) leksik dalil bilan birlashtiradi. Leksik dalil sifatida ikkala kitobda bir xil yoziladigan nomlar va sonlar olindi, dastur birinchi o‘tishdan so‘ng o‘z lug‘atini ham tuzdi. 1.1-paragrafda tahlil qilingan juftliklar va oldingi tekislashning tayanch nuqtalari qo‘zg‘almas nuqta sifatida saqlandi, shuning uchun xato ikki qo‘zg‘almas nuqta orasidan chiqmaydi. Juftlik maqomlari: «avtomatik — ikki usul mos» (oldingi uzunlik va sahifa usuli ham shu gaplarni bir juftlikka qo‘ygan) — {auto_good}; «avtomatik — faqat hunalign» — {auto_one}; «avtomatik — tayanch nuqta» (oldingi tekislashdagi qo‘zg‘almas nuqta) — {auto_pin}; 1.1-paragrafda qo‘lda tahlil qilingan — {confirmed}. Sun’iy intellekt yordamida bajarilgan tanlab tekshiruvda (14.10.2026) oldingi tekislashning 15 juftligidan 7 tasi to‘liq, 1 tasi qisman mos kelgan; yangi tekislashning 38 juftligidan 31 tasi to‘liq, 5 tasi qisman mos, 2 tasi noto‘g‘ri. Bu tekshiruv tadqiqotchi tekshiruvi o‘rnini bosmaydi.',
    'm_equiv_title': '5. Tarjima ekvivalenti tamoyili',
    'm_equiv': 'Tarjima ekvivalenti — tarjimonning kitobdagi so‘zlari, aynan ko‘chirilgan. AI yoki mashina tarjimasi hech qachon ekvivalent sifatida berilmaydi. Natijalar besh manba bo‘yicha alohida ko‘rsatiladi:',
    'm_equiv_items': [
        '<strong>Kitobdagi tarjima — tasdiqlangan</strong>: tadqiqotchi tasdiqlagan juftlikdagi, tadqiqotchi belgilagan so‘zlar (to‘liq chiziq bilan).',
        '<strong>Kitobdagi tarjima — AI taklifi</strong>: faqat tasdiqlangan juftlik ichida, tekshirilguncha punktir chiziq bilan.',
        '<strong>Lug‘atdagi tarjima</strong>: bosma lug‘at yozuvlari OCR xatolari tuzatilmaguncha ko‘rsatilmaydi.',
        '<strong>Ma’lumotnomadagi muqobil</strong>: inglizcha kollokatsiya to‘plamlaridagi yozuv; o‘zbekcha shakli AI taklifi, tekshirilmagan.',
        '<strong>Namuna gap</strong>: kitobdan olinmagan misol; har doim «kitobdan emas» deb belgilanadi.',
    ],
    'm_cand_title': '6. Kollokatsiya nomzodlarini ajratish',
    'm_cand': 'Qidirilgan so‘z topilgan gapda undan chap va o‘ngdagi 4 so‘z ko‘riladi (Uhrig va Proisl, 2012). So‘z turkumi qoliplari: o‘zbekchada ot + fe’l, ega + kesim, sifat + ot, ravish + fe’l (ot + ot qolipi alohida, faqat tadqiqotchiga ko‘rinadigan ro‘yxatga yoziladi); inglizchada adjective + noun va verb + noun. Ommaga faqat korpusda kamida 2 marta uchragan nomzod ko‘rsatiladi. Bunday birlik «Avtomatik nomzod — lingvistik tekshiruvdan o‘tmagan» deb ataladi; «kollokatsiya nomzodi» maqomini u faqat lingvistik tekshiruvdan keyin oladi.',
    'm_reference': '<strong>Ma’lumotnoma bazasi</strong> ({ref} ta ko‘rinadigan yozuv) ingliz tilidagi o‘quv kollokatsiya to‘plamlaridan olingan. U korpus ma’lumoti emas, III bob statistikasiga kiritilmaydi; undagi avvalgi MI, t-score va chastota qiymatlari hech qaysi korpusda hisoblanmagani uchun o‘chirilgan.',
    'm_stat_title': '7. Statistik tasdiq (reja)',
    'm_stat': [
        'Badiiy korpus kichik bo‘lgani uchun maqom tadqiqot korpusidagi raqamlar bilan emas, katta tayanch korpusda tasdiqlanadi (Bernardini, 2007). Inglizcha birikmalar uchun — Britaniya milliy korpusi (BNC); o‘zbekcha uchun — O‘zbek tili milliy korpusi yoki uzWaC (tanlov II bobda asoslanadi).',
        'Dastlabki parametrlar: hisob birligi — lemma; tayanch korpusda kamida 5 marta uchrash; asosiy o‘lchov — logDice (Rychlý, 2008); MI faqat chastota filtri bilan; t-score faqat ishonchlilik ko‘rsatkichi sifatida (Gablasova va boshq., 2017); chastota million so‘zga nisbatan. Chegaraviy qiymatlar oldindan belgilanmaydi, qo‘lda annotatsiya qilingan to‘plamda kalibrlanadi.',
        'Bu hisoblar hali bajarilmagan. Platformada tayanch korpus statistikasi sifatida hech qanday raqam ko‘rsatilmaydi.',
    ],
    'm_rel_title': '8. Annotatsiya ishonchliligi (protokol)',
    'm_rel': 'Annotatsiyani ikki mustaqil annotator — muallif va ikkinchi filolog — yozma yo‘riqnoma asosida bajaradi: avval 50 birlikli o‘quv to‘plami, so‘ngra birliklarning kamida 20 foizi (200 tadan kam emas) mustaqil belgilanadi. Kelishuv Koen kappasi bilan hisoblanadi (Cohen, 1960); κ ≥ 0,8 — yaxshi ishonchlilik, 0,67–0,8 — ehtiyotkor xulosa uchun yetarli (Artstein va Poesio, 2008, b. 576). Ikkinchi annotator hali ishlamagan, shuning uchun kelishuv koeffitsiyenti hozircha yo‘q.',
    'm_limits_title': '9. Cheklovlar',
    'm_limits': [
        'Juftliklarning katta qismi hali avtomatik; ulardan tarjima ekvivalenti olinmaydi.',
        'O‘zbekcha so‘z turkumi va lemma qoidaga asoslangan usulda aniqlanadi va xato berishi mumkin; avtomatik nomzodlar shuning uchun belgilab ko‘rsatiladi.',
        '«Chol va dengiz» sahifalari 1986-yilgi bosma nashrga emas, elektron nusxaga tegishli.',
        'Bosma lug‘atlar hozircha ishlatilmaydi.',
    ],
    'm_refs_title': 'Adabiyotlar',
    # annotation guidelines
    'g_title': 'Annotatsiya yo‘riqnomasi',
    'g_lead': 'Korpusdagi har bir birlik quyidagi qaror tartibi bo‘yicha belgilanadi (dissertatsiya, 1.1.4-band). Har bir savolga javob birlikning keyingi bosqichga o‘tishini yoki yakuniy maqomini belgilaydi.',
    'g_steps': [
        ('Birlik kamida ikki mustaqil so‘zdan iborat va komponentlari bevosita sintaktik aloqadami?', 'Yo‘q bo‘lsa, birlik tahlilga olinmaydi. Ha bo‘lsa, komponentlar lemma shaklida yoziladi, asos va kollokat belgilanadi.'),
        ('Birlik istisno qilinadigan toifaga kiradimi?', 'Maqol va matallar, to‘liq gaplar, o‘xshatishlar, nutq formulalari, atoqli otlar va laqablar, juft va takroriy so‘zlar, ko‘makchi fe’lli grammatik qurilmalar tahlilga olinmaydi.'),
        ('Birikma shu kontekstda yaxlit obrazli ko‘chma ma’noga egami va qayta ifodalashda asos yo‘qoladimi?', 'Ha bo‘lsa — frazeologik birlik.'),
        ('Kollokat tanlovi cheklanganmi?', 'Yo‘q bo‘lsa — erkin birikma; matnda takroriy va tarjimada tayyor qolip bilan berilgan bo‘lsa — barqaror erkin birikma. Bahs saqlansa — chegaraviy holat.'),
        ('Tayanch korpusda statistik tasdiq bormi?', 'Bor bo‘lsa — tasdiqlangan kollokatsiya; yo‘q yoki ma’lumot yetarli bo‘lmasa — kollokatsiya nomzodi.'),
        ('Uchrashning kontekstual ma’nosi va tarjimadagi muqobili qanday?', 'Ma’no belgisi (shakldosh birikmalar uchun) va muqobil turi yoziladi: kollokatsiya, bitta so‘z, tasviriy ifoda yoki tushirib qoldirish.'),
    ],
    'g_base_title': 'Asos va kollokatni aniqlash',
    'g_base_head': ['Tuzilish modeli', 'Misol', 'Asos', 'Kollokat'],
    'g_base_rows': [
        ('ot + fe’l', '<em>dasturxon solmoq</em>, <em>javob bermoq</em>', 'ot', 'fe’l'),
        ('ega + kesim', '<em>rangi o‘chmoq</em>', 'ot', 'fe’l'),
        ('sifat + ot', '<em>og‘ir uyqu</em>', 'ot', 'sifat'),
        ('ravish + fe’l', '<em>qattiq uxlamoq</em>', 'fe’l', 'ravish'),
        ('ot + ot', '<em>ko‘z yoshi</em>', '—', '—'),
    ],
    'g_base_note': 'Ma’nosi kuchsizlangan fe’l (<em>qilmoq</em>, <em>bermoq</em>, <em>olmoq</em>) har doim kollokat. Ot + ot birikmalari leksikallashgan nom sifatida alohida belgilanadi.',
    'g_equiv_title': 'Tarjimadagi muqobil turlari',
    'g_equiv': [
        ('kollokatsiya', '<em>og‘ir uyqu</em> → <em>a heavy sleep</em> (Cho‘lpon, 2000, 36-bet; 2019, 74-bet)'),
        ('bitta so‘z', '<em>hazillashib javob berdi</em> → <em>answered … with a joke</em> (2000, 23-bet; 2019, 63-bet)'),
        ('tasviriy ifoda', 'ma’no kollokatsiyasiz, so‘z birikmasi yoki gap bilan beriladi'),
        ('tushirib qoldirish', '<em>og‘ir uyquga ketdilar</em> → <em>fell asleep</em>: kuchaytiruvchi komponent tushib qolgan (2000, 65-bet; 2019, 98-bet)'),
    ],
    'g_rel_title': 'Ikki annotator va kelishuv',
    'g_status_now': 'Hozirgi holat: tasdiqlangan annotatsiyalar soni — {ann}; ikki annotator umumiy belgilagan birliklar — {shared}. Bu protokoldagi 50 birlikli o‘quv to‘plamidan kam, shuning uchun kelishuv koeffitsiyenti keltirilmaydi.',
    # statistics
    's_title': 'Korpus statistikasi',
    's_lead': 'Bu sahifadagi barcha raqamlar korpus ma’lumotidan so‘rov paytida hisoblanadi.',
    's_size_title': '1. Matnlar hajmi',
    's_size_note': 'Token — harflar ketma-ketligi, kichik harfga keltirilgan; so‘z ichidagi tutuq belgisi (<em>ko‘ngil, ma’no, didn’t</em>) va chiziqcha (<em>qah-qah</em>) so‘zni bo‘lmaydi. Bu jadval butun segmentlangan matnni sanaydi, juft topilmagan gaplar ham kiradi. 3–6-bo‘limlarda esa so‘z darajasidagi tekislash tokenlari sanaladi: faqat juftlangan gaplar, chiziqchali so‘z va inglizcha <em>’s</em>, <em>n’t</em> alohida token, shuning uchun u yerdagi sonlar bundan farq qiladi. Hapaks — matnda bir marta uchragan shakl. TTR — shakllar sonining tokenlar soniga nisbati; matn uzunligiga bog‘liq bo‘lgani uchun turli hajmdagi matnlarni bu ko‘rsatkich bilan bevosita solishtirib bo‘lmaydi.',
    's_head': ['Matn', 'Tili', 'Tokenlar', 'Shakllar', 'Hapakslar', 'TTR'],
    's_pairs_title': '2. Parallel juftliklar',
    's_pairs_head': ['Juftlik', 'Jami', '1.1-paragrafda tahlil qilingan', 'Avtomatik — ikki usul mos', 'Avtomatik — faqat hunalign', 'Avtomatik — tayanch nuqta'],
    's_assoc_title': '3. Assotsiatsiya ko‘rsatkichlari',
    's_assoc': 'Maqomni tasdiqlovchi ko‘rsatkichlar (logDice, MI, t-score) tayanch korpusda hisoblanadi va bu hisob hali bajarilmagan. Tadqiqot korpusi ichida hisoblangan raqamlar kichik hajm tufayli beqaror va maqom uchun asos bo‘lmaydi, shuning uchun bu yerda ko‘rsatilmaydi.',
    's_formulas_title': 'Formulalar',
    's_ch3_title': '4. III bob jadvallari',
    's_ch3': 'III bob jadvallari faqat tadqiqotchi tasdiqlagan annotatsiyalardan tuziladi. Hozir tasdiqlangan annotatsiyalar soni: {ann}. Bu son xulosa chiqarish uchun yetarli emas, shuning uchun foizlar ko‘rsatilmaydi.',
    'role_original': 'asliyat',
    'role_translation': 'tarjima',
    'lang_uz': 'o‘zbekcha',
    'lang_en': 'inglizcha',
}

T['en'] = {
    'about_title': 'About the project',
    'about_lead': 'TILCOR is a parallel corpus of literary works in Uzbek and English and their translations. It is being built for a PhD dissertation on the translation of collocations.',
    'about_topic_label': 'Dissertation topic',
    'about_topic': '«A study of collocational words in a parallel corpus of translations and comparable texts (on the material of Uzbek and English)»',
    'about_researcher_label': 'Researcher',
    'about_university_label': 'University',
    'about_university': 'Bukhara State University',
    'about_specialty_label': 'Specialty',
    'about_specialty': '10.00.06 — Comparative literary studies, contrastive linguistics and translation studies',
    'about_what_title': 'What the platform does',
    'about_what': [
        'It detects the language of the query and finds every form of the word in the corpus, together with words built on the same root.',
        'For every sentence found it shows the parallel sentence of the other book, with the work and the page.',
        'As a translation equivalent it gives only the translator’s own words in the book; AI suggestions and reference entries are labelled separately.',
        'It shows the keyword in context (KWIC) and lets you download the result as a CSV file.',
        'It extracts collocation candidates from the corpus automatically and labels them as not checked linguistically.',
    ],
    'about_state_title': 'Current state',
    'about_state': 'The corpus has {pairs} parallel pairs; {confirmed} of them have been confirmed by the researcher. Statistical measures against a reference corpus have not been computed yet. Entries taken from printed dictionaries stay closed until their OCR errors are corrected.',
    'about_tech_title': 'Technical basis',
    'about_tech': 'The server is written in Python. The corpus is stored in JSON files and an SQLite database. English word families use NLTK WordNet; Uzbek words use rule-based normalization and suffix stripping. Pages are generated on the server in three languages.',
    'src_title': 'Sources and copyright',
    'src_lead': 'The corpus consists of two work–translation pairs. For each text the copy used, the page rule and the size are given.',
    'src_pair_kvk': 'First pair: Uzbek to English',
    'src_pair_oms': 'Second pair: English to Uzbek',
    'src_role_original': 'Original',
    'src_role_translation': 'Translation',
    'src_edition': 'Edition',
    'src_copy': 'Copy used in the corpus',
    'src_pages': 'Page rule',
    'src_size': 'Size',
    'src_tokens_full': '{tokens} tokens in the segmented text, {types} word forms',
    'src_pairs': 'parallel pairs: {pairs}; confirmed by the researcher: {confirmed}',
    'src_kvk_uz_edition': 'Abdulhamid Cho‘lpon. «Kecha va kunduz». Tashkent: «Sharq», 2000. First edition: 1936.',
    'src_kvk_uz_copy': 'Electronic copy in the ziyouz.com library (text of the 2000 «Sharq» edition; its pagination differs from the printed book).',
    'src_kvk_uz_pages': 'Number in the bottom running footer of the electronic copy; the novel occupies pages 3–265. The article on pages 266–272 is not part of the corpus.',
    'src_kvk_en_edition': 'Cho‘lpon. «Night and Day: A Novel». Translated by Christopher Fort. Boston: Academic Studies Press, 2019. DOI 10.1515/9781644690482.',
    'src_kvk_en_copy': 'Publisher’s PDF file.',
    'src_kvk_en_pages': 'Printed page number (top running header); the novel occupies pages 45–271.',
    'src_oms_en_edition': 'Ernest Hemingway. «The Old Man and the Sea». First edition: 1952.',
    'src_oms_en_copy': 'Electronic copy from Asiaing.com; the printed edition it was taken from has not been identified.',
    'src_oms_en_pages': 'Printed page according to the [N] marks in the text: pages 9–125.',
    'src_oms_uz_edition': 'Ernest Xeminguey. «Chol va dengiz». Translated by Ibrohim G‘ofurov (spelling as on the title page). Tashkent: «Yosh gvardiya», 1986.',
    'src_oms_uz_copy': 'Electronic copy from kutubxonachi.uz.',
    'src_oms_uz_pages': 'Page of the electronic copy (1–46). It does not match the page of the 1986 printed edition, so it is always marked “electronic copy”.',
    'src_excluded_title': 'Texts not included in the corpus',
    'src_excluded': 'R. L. Stevenson, «Treasure Island» (Uzbek translation by A. Yoqubov from Russian) and «Animal Farm / Molxona» are not included (researcher’s decision, 13.10.2026). A new work is added only by the researcher’s decision.',
    'src_rights_title': 'Copyright',
    'src_rights': 'The texts belong to their copyright holders. The platform does not show or let anyone download a full text: a search shows only the sentence containing the query and its parallel sentence, to the extent needed for research. The data files and the database are not accessible from outside.',
    'm_title': 'Methodology',
    'm_lead': 'This page describes the rules the platform actually applies. The theoretical justification is given in paragraph 1.1 of the dissertation.',
    'm_def_title': '1. Working definition of a collocation',
    'm_def_intro': 'A word combination is treated as a collocation when all four linguistic conditions hold:',
    'm_def_items': [
        'it consists of at least two independent words whose components are directly linked syntactically;',
        'the base keeps its literal meaning;',
        'the choice of the collocate is restricted by convention: replacing it with a synonym makes the combination sound unnatural;',
        'the combination does not have a holistic figurative meaning.',
    ],
    'm_def_note': 'The linguistic conditions decide the category of a unit; statistical evidence decides its status.',
    'm_status_title': 'Statuses',
    'm_statuses': [
        ('confirmed collocation', 'meets the linguistic conditions, and its conventionality is confirmed by frequency and association measures in a reference corpus;'),
        ('collocation candidate', 'meets the linguistic conditions, but statistical confirmation has not been obtained yet or the reference corpus gives too little data;'),
        ('stable free combination', 'the collocate can be replaced freely, but the combination recurs in the text and is rendered with a ready-made pattern in the translation;'),
        ('phraseological unit', 'has a holistic figurative meaning;'),
        ('borderline case', 'the substitution test remains disputed; results are computed both with and without such units.'),
    ],
    'm_exclusions': '<strong>Not analysed:</strong> proverbs and sayings, complete sentences, similes (<em>anorday qizarmoq</em> “to blush like a pomegranate”), speech formulas, proper names and nicknames, paired and reduplicated words, grammatical constructions with auxiliary verbs (<em>chiqib ketmoq</em>, <em>olib kelmoq</em>).',
    'm_unit': '<strong>Unit of analysis</strong> — an occurrence of a collocation taken together with its contextual meaning. Homonymous combinations (for example <em>katta xotin</em>: “older women” and “eldest wife”) get a separate sense label in every occurrence.',
    'm_corpus_title': '2. Composition of the corpus and the page rule',
    'm_corpus': 'The corpus consists of two pairs: Cho‘lpon’s novel «Kecha va kunduz» and its English translation «Night and Day» by Christopher Fort (Uzbek to English); E. Hemingway’s «The Old Man and the Sea» and its Uzbek translation «Chol va dengiz» by Ibrohim G‘ofurov (English to Uzbek). Each work is compared only with its own translation.',
    'm_pages': 'A page is always the number printed in the copy used: «Kecha va kunduz» — the ziyouz.com copy (3–265); «Night and Day» — printed page (45–271); «The Old Man and the Sea» — the [N] marks in the text (9–125); «Chol va dengiz» — page of the electronic copy (1–46), always with the note “electronic copy”.',
    'm_text_title': '3. Text processing and word families',
    'm_text': [
        'The text of a book is never changed. A normalized copy is built for searching: the Uzbek apostrophe variants (<em>‘ ’ ʻ ʼ \'</em>) are unified, and an Uzbek query in Cyrillic script is converted to Latin script. A word that is found is highlighted in the original text itself, by character position.',
        'Uzbek words are stripped of suffixes by rules; verbs are given in the dictionary form (<em>-moq</em>), nouns in the nominative. The English word family is found with NLTK WordNet (lemmatization and derived words) and a list of irregular verbs.',
        'The forms found are split into four groups: exact form, inflected form, derived word, compound word. The interface uses no abbreviations.',
    ],
    'm_align_title': '4. Sentence alignment',
    'm_align': 'The pairs are aligned automatically. The sentences of both books were re-aligned with hunalign (Varga et al., 2007), which combines the sentence-length model (Gale & Church, 1993) with lexical evidence. The lexical evidence consists of names and numbers written the same in both books, and the program also builds its own dictionary after a first pass. The pairs analysed in paragraph 1.1 and the pins of the earlier alignment were kept as fixed points, so an error cannot run past a fixed point. Statuses: “automatic — two methods agree” (the earlier length-and-page method also put these sentences into one pair) — {auto_good}; “automatic — hunalign only” — {auto_one}; “automatic — pin” (a fixed point of the earlier alignment) — {auto_pin}; analysed by hand in paragraph 1.1 — {confirmed}. In an AI-assisted spot check (14.10.2026), 7 of 15 pairs of the earlier alignment matched fully and 1 partly; of 38 pairs of the new alignment 31 matched fully, 5 partly and 2 were wrong. This check does not replace the researcher’s own check.',
    'm_equiv_title': '5. Principle of the translation equivalent',
    'm_equiv': 'A translation equivalent is the translator’s own words in the book, copied verbatim. AI or machine translation is never given as an equivalent. Results are shown separately by five sources:',
    'm_equiv_items': [
        '<strong>Translation in the book — confirmed</strong>: words marked by the researcher in a pair the researcher confirmed (solid underline).',
        '<strong>Translation in the book — AI suggestion</strong>: only inside a confirmed pair, dashed underline until checked.',
        '<strong>Dictionary translation</strong>: entries of the printed dictionaries are not shown until their OCR errors are corrected.',
        '<strong>Equivalent in the reference source</strong>: an entry from English collocation collections; its Uzbek form is an AI suggestion, not checked.',
        '<strong>Sample sentence</strong>: an example not taken from the books; always marked “not from the books”.',
    ],
    'm_cand_title': '6. Extraction of collocation candidates',
    'm_cand': 'In a sentence containing the query word, the 4 words to its left and right are examined (Uhrig & Proisl, 2012). Part-of-speech patterns: in Uzbek noun + verb, subject + predicate, adjective + noun, adverb + verb (the noun + noun pattern is kept in a separate list visible only to the researcher); in English adjective + noun and verb + noun. Only candidates that occur at least twice in the corpus are shown publicly. Such a unit is called an “automatic candidate — not checked linguistically”; it becomes a “collocation candidate” only after the linguistic check.',
    'm_reference': '<strong>The reference base</strong> ({ref} visible entries) comes from English learner collocation collections. It is not corpus data and is not used in the statistics of chapter III; its former MI, t-score and frequency values were deleted, because they had not been computed on any corpus.',
    'm_stat_title': '7. Statistical confirmation (plan)',
    'm_stat': [
        'Because a literary corpus is small, status is confirmed in a large reference corpus rather than with the figures of the study corpus (Bernardini, 2007). For English combinations — the British National Corpus (BNC); for Uzbek — the Uzbek National Corpus or uzWaC (the choice is argued in chapter II).',
        'Initial parameters: the counting unit is the lemma; at least 5 occurrences in the reference corpus; the main measure is logDice (Rychlý, 2008); MI only together with a frequency filter; t-score only as an indicator of reliability (Gablasova et al., 2017); frequency per million words. Thresholds are not fixed in advance; they are calibrated on a manually annotated sample.',
        'These computations have not been done yet. The platform shows no figure as a reference-corpus statistic.',
    ],
    'm_rel_title': '8. Reliability of annotation (protocol)',
    'm_rel': 'Annotation is done by two independent annotators — the author and a second philologist — following written guidelines: first a training set of 50 units, then at least 20 per cent of the units (not fewer than 200) are annotated independently. Agreement is measured with Cohen’s kappa (Cohen, 1960); κ ≥ 0.8 means good reliability, 0.67–0.8 allows cautious conclusions (Artstein & Poesio, 2008, p. 576). The second annotator has not worked yet, so there is no agreement coefficient yet.',
    'm_limits_title': '9. Limitations',
    'm_limits': [
        'Most pairs are still automatic; no translation equivalent is taken from them.',
        'Uzbek part of speech and lemma are found by rules and can be wrong; this is why automatic candidates are labelled.',
        'The pages of «Chol va dengiz» belong to the electronic copy, not to the 1986 printed edition.',
        'The printed dictionaries are not used for now.',
    ],
    'm_refs_title': 'References',
    'g_title': 'Annotation guidelines',
    'g_lead': 'Every unit in the corpus is annotated with the following decision procedure (dissertation, section 1.1.4). The answer to each question decides whether the unit moves to the next step or receives its final status.',
    'g_steps': [
        ('Does the unit consist of at least two independent words whose components are directly linked syntactically?', 'If not, the unit is not analysed. If yes, the components are recorded as lemmas and the base and collocate are marked.'),
        ('Does the unit belong to an excluded category?', 'Proverbs and sayings, complete sentences, similes, speech formulas, proper names and nicknames, paired and reduplicated words, grammatical constructions with auxiliary verbs are not analysed.'),
        ('Does the combination have a holistic figurative meaning in this context, and is the base lost in a paraphrase?', 'If yes — phraseological unit.'),
        ('Is the choice of the collocate restricted?', 'If not — free combination; if it recurs in the text and is rendered with a ready-made pattern in the translation — stable free combination. If the question stays disputed — borderline case.'),
        ('Is there statistical confirmation in the reference corpus?', 'If yes — confirmed collocation; if not, or if the data are insufficient — collocation candidate.'),
        ('What is the contextual meaning of the occurrence and its counterpart in the translation?', 'The sense label (for homonymous combinations) and the type of counterpart are recorded: collocation, single word, descriptive phrase or omission.'),
    ],
    'g_base_title': 'Identifying the base and the collocate',
    'g_base_head': ['Structural model', 'Example', 'Base', 'Collocate'],
    'g_base_rows': [
        ('noun + verb', '<em>dasturxon solmoq</em>, <em>javob bermoq</em>', 'noun', 'verb'),
        ('subject + predicate', '<em>rangi o‘chmoq</em>', 'noun', 'verb'),
        ('adjective + noun', '<em>og‘ir uyqu</em>', 'noun', 'adjective'),
        ('adverb + verb', '<em>qattiq uxlamoq</em>', 'verb', 'adverb'),
        ('noun + noun', '<em>ko‘z yoshi</em>', '—', '—'),
    ],
    'g_base_note': 'A delexical verb (<em>qilmoq</em>, <em>bermoq</em>, <em>olmoq</em>) is always the collocate. Noun + noun combinations are marked separately as lexicalized names.',
    'g_equiv_title': 'Types of counterpart in the translation',
    'g_equiv': [
        ('collocation', '<em>og‘ir uyqu</em> → <em>a heavy sleep</em> (Cho‘lpon, 2000, p. 36; 2019, p. 74)'),
        ('single word', '<em>hazillashib javob berdi</em> → <em>answered … with a joke</em> (2000, p. 23; 2019, p. 63)'),
        ('descriptive phrase', 'the meaning is rendered without a collocation, by a free phrase or a clause'),
        ('omission', '<em>og‘ir uyquga ketdilar</em> → <em>fell asleep</em>: the intensifying component is lost (2000, p. 65; 2019, p. 98)'),
    ],
    'g_rel_title': 'Two annotators and agreement',
    'g_status_now': 'Current state: confirmed annotations — {ann}; units annotated by both annotators — {shared}. This is fewer than the 50-unit training set of the protocol, so no agreement coefficient is given.',
    's_title': 'Corpus statistics',
    's_lead': 'Every figure on this page is computed from the corpus data at the time of the request.',
    's_size_title': '1. Size of the texts',
    's_size_note': 'A token is a run of letters, lower-cased; an apostrophe inside a word (<em>ko‘ngil, ma’no, didn’t</em>) and a hyphen (<em>qah-qah</em>) do not split it. This table counts the whole segmented text, including the sentences that have no pair. Sections 3–6 count the tokens of the word alignment instead: paired sentences only, with the parts of a hyphenated word and English <em>’s</em>, <em>n’t</em> as separate tokens, so their figures differ from these. A hapax is a form that occurs once in the text. TTR is the number of forms divided by the number of tokens; it depends on text length, so texts of different size cannot be compared with it directly.',
    's_head': ['Text', 'Language', 'Tokens', 'Forms', 'Hapaxes', 'TTR'],
    's_pairs_title': '2. Parallel pairs',
    's_pairs_head': ['Pair', 'Total', 'Analysed in paragraph 1.1', 'Automatic — two methods agree', 'Automatic — hunalign only', 'Automatic — pin'],
    's_assoc_title': '3. Association measures',
    's_assoc': 'The measures that confirm a status (logDice, MI, t-score) are computed in a reference corpus, and this has not been done yet. Figures computed inside the study corpus are unstable because of its small size and are no basis for a status, so they are not shown here.',
    's_formulas_title': 'Formulas',
    's_ch3_title': '4. Tables of chapter III',
    's_ch3': 'The tables of chapter III are built only from annotations confirmed by the researcher. Confirmed annotations now: {ann}. This is not enough for conclusions, so no percentages are shown.',
    'role_original': 'original',
    'role_translation': 'translation',
    'lang_uz': 'Uzbek',
    'lang_en': 'English',
}

T['ru'] = {
    'about_title': 'О проекте',
    'about_lead': 'TILCOR — параллельный корпус художественных произведений на узбекском и английском языках и их переводов. Он создаётся в рамках диссертации PhD о переводе коллокаций.',
    'about_topic_label': 'Тема диссертации',
    'about_topic': '«Исследование коллокационных слов в параллельном корпусе переводов и сопоставимых текстов (на материале узбекского и английского языков)»',
    'about_researcher_label': 'Исследователь',
    'about_university_label': 'Вуз',
    'about_university': 'Бухарский государственный университет',
    'about_specialty_label': 'Специальность',
    'about_specialty': '10.00.06 — Сравнительное литературоведение, сопоставительное языкознание и переводоведение',
    'about_what_title': 'Что делает платформа',
    'about_what': [
        'Определяет язык запроса и находит все формы слова в корпусе, а также слова с тем же корнем.',
        'Для каждого найденного предложения показывает параллельное предложение другой книги с указанием произведения и страницы.',
        'В качестве переводного эквивалента даёт только собственные слова переводчика в книге; предложения ИИ и справочные записи помечаются отдельно.',
        'Показывает ключевое слово в контексте (KWIC) и позволяет скачать результат файлом CSV.',
        'Автоматически извлекает из корпуса кандидатов в коллокации и помечает их как лингвистически не проверенные.',
    ],
    'about_state_title': 'Текущее состояние',
    'about_state': 'В корпусе {pairs} параллельных пар; из них {confirmed} подтверждены исследователем. Статистические меры по опорному корпусу ещё не вычислены. Записи из печатных словарей закрыты, пока не исправлены ошибки OCR.',
    'about_tech_title': 'Техническая основа',
    'about_tech': 'Сервер написан на Python. Корпус хранится в файлах JSON и базе SQLite. Для английских словообразовательных гнёзд используется NLTK WordNet, для узбекских слов — нормализация и отделение аффиксов по правилам. Страницы формируются на сервере на трёх языках.',
    'src_title': 'Источники и авторское право',
    'src_lead': 'Корпус состоит из двух пар «произведение — перевод». Для каждого текста указаны использованная копия, правило нумерации страниц и объём.',
    'src_pair_kvk': 'Первая пара: с узбекского на английский',
    'src_pair_oms': 'Вторая пара: с английского на узбекский',
    'src_role_original': 'Оригинал',
    'src_role_translation': 'Перевод',
    'src_edition': 'Издание',
    'src_copy': 'Копия в корпусе',
    'src_pages': 'Правило страниц',
    'src_size': 'Объём',
    'src_tokens_full': 'в сегментированном тексте {tokens} словоупотреблений (токенов), {types} словоформ',
    'src_pairs': 'параллельных пар: {pairs}; подтверждено исследователем: {confirmed}',
    'src_kvk_uz_edition': 'Абдулхамид Чулпан. «Kecha va kunduz». Ташкент: «Sharq», 2000. Первое издание: 1936.',
    'src_kvk_uz_copy': 'Электронная копия библиотеки ziyouz.com (текст издания «Sharq» 2000 года; пагинация отличается от печатной книги).',
    'src_kvk_uz_pages': 'Номер в нижнем колонтитуле электронной копии; текст романа — страницы 3–265. Статья на страницах 266–272 в корпус не входит.',
    'src_kvk_en_edition': 'Cho‘lpon. «Night and Day: A Novel». Перевод Christopher Fort. Boston: Academic Studies Press, 2019. DOI 10.1515/9781644690482.',
    'src_kvk_en_copy': 'PDF-файл издательства.',
    'src_kvk_en_pages': 'Номер печатной страницы (верхний колонтитул); текст романа — страницы 45–271.',
    'src_oms_en_edition': 'Ernest Hemingway. «The Old Man and the Sea». Первое издание: 1952.',
    'src_oms_en_copy': 'Электронная копия с Asiaing.com; печатное издание, с которого она сделана, не установлено.',
    'src_oms_en_pages': 'Печатная страница по меткам [N] в тексте: страницы 9–125.',
    'src_oms_uz_edition': 'Эрнест Хемингуэй. «Chol va dengiz». Перевод Иброхима Гафурова (написание по титульному листу: G‘ofurov). Ташкент: «Yosh gvardiya», 1986.',
    'src_oms_uz_copy': 'Электронная копия с kutubxonachi.uz.',
    'src_oms_uz_pages': 'Страница электронной копии (1–46). Она не совпадает со страницей печатного издания 1986 года, поэтому всегда помечается как «электронная копия».',
    'src_excluded_title': 'Тексты, не включённые в корпус',
    'src_excluded': 'Р. Л. Стивенсон, «Остров сокровищ» (узбекский перевод А. Якубова с русского) и «Animal Farm / Molxona» в корпус не входят (решение исследователя, 13.10.2026). Новое произведение добавляется только по решению исследователя.',
    'src_rights_title': 'Авторское право',
    'src_rights': 'Тексты принадлежат правообладателям. Платформа не показывает полный текст и не даёт его скачать: при поиске показывается только предложение с запросом и его параллельное предложение в объёме, необходимом для исследования. Файлы данных и база извне недоступны.',
    'm_title': 'Методология',
    'm_lead': 'На этой странице описаны правила, которые платформа применяет на деле. Теоретическое обоснование дано в параграфе 1.1 диссертации.',
    'm_def_title': '1. Рабочее определение коллокации',
    'm_def_intro': 'Сочетание считается коллокацией, если одновременно выполняются четыре лингвистических условия:',
    'm_def_items': [
        'оно состоит не менее чем из двух самостоятельных слов, компоненты которых непосредственно связаны синтаксически;',
        'опорный компонент (база) сохраняет прямое значение;',
        'выбор коллоката ограничен языковой традицией: при замене его синонимом сочетание звучит неестественно;',
        'сочетание не имеет целостного образного переносного значения.',
    ],
    'm_def_note': 'Лингвистические условия определяют категорию единицы, статистические данные — её статус.',
    'm_status_title': 'Статусы',
    'm_statuses': [
        ('подтверждённая коллокация', 'отвечает лингвистическим условиям, а её узуальность подтверждена частотой и мерами ассоциации в опорном корпусе;'),
        ('кандидат в коллокации', 'отвечает лингвистическим условиям, но статистическое подтверждение ещё не получено или данных опорного корпуса недостаточно;'),
        ('устойчивое свободное сочетание', 'коллокат свободно заменяется, но сочетание повторяется в тексте и передаётся в переводе готовым шаблоном;'),
        ('фразеологическая единица', 'имеет целостное образное переносное значение;'),
        ('пограничный случай', 'по тесту замены сохраняется спор; результаты считаются с такими единицами и без них.'),
    ],
    'm_exclusions': '<strong>Не анализируются:</strong> пословицы и поговорки, целые предложения, сравнения (<em>anorday qizarmoq</em> «покраснеть как гранат»), речевые формулы, имена собственные и прозвища, парные и повторные слова, грамматические конструкции со вспомогательными глаголами (<em>chiqib ketmoq</em>, <em>olib kelmoq</em>).',
    'm_unit': '<strong>Единица анализа</strong> — употребление коллокации вместе с его контекстуальным значением. Омонимичные сочетания (например, <em>katta xotin</em>: «пожилые женщины» и «старшая жена») получают отдельную помету значения в каждом употреблении.',
    'm_corpus_title': '2. Состав корпуса и правило страниц',
    'm_corpus': 'Корпус состоит из двух пар: роман Чулпана «Kecha va kunduz» и его английский перевод «Night and Day» Кристофера Форта (с узбекского на английский); повесть Э. Хемингуэя «The Old Man and the Sea» и её узбекский перевод «Chol va dengiz» Иброхима Гафурова (с английского на узбекский). Каждое произведение сопоставляется только со своим переводом.',
    'm_pages': 'Страница всегда указывается по номеру, напечатанному в использованной копии: «Kecha va kunduz» — копия ziyouz.com (3–265); «Night and Day» — печатная страница (45–271); «The Old Man and the Sea» — метки [N] в тексте (9–125); «Chol va dengiz» — страница электронной копии (1–46), всегда с пометой «электронная копия».',
    'm_text_title': '3. Обработка текста и словообразовательные гнёзда',
    'm_text': [
        'Текст книги не изменяется. Для поиска строится нормализованная копия: варианты узбекского апострофа (<em>‘ ’ ʻ ʼ \'</em>) приводятся к одному, узбекский запрос кириллицей переводится в латиницу. Найденное слово выделяется в самом исходном тексте по позиции символов.',
        'У узбекских слов аффиксы отделяются по правилам; глаголы даются в словарной форме (<em>-moq</em>), существительные — в именительном падеже. Английское гнездо определяется с помощью NLTK WordNet (лемматизация и производные слова) и списка неправильных глаголов.',
        'Найденные формы делятся на четыре группы: точная форма, словоформа, производное слово, сложное слово. В интерфейсе не используются сокращения.',
    ],
    'm_align_title': '4. Выравнивание предложений',
    'm_align': 'Пары выровнены автоматически. Предложения обеих книг заново выровнены программой hunalign (Varga et al., 2007), которая объединяет модель длины предложений (Gale & Church, 1993) с лексическими данными. Лексические данные — имена и числа, одинаково записанные в обеих книгах; после первого прохода программа также строит собственный словарь. Пары, разобранные в параграфе 1.1, и якоря прежнего выравнивания сохранены как неподвижные точки, поэтому ошибка не выходит за пределы участка между ними. Статусы: «автоматически — оба метода совпали» (прежний метод по длине и страницам тоже объединил эти предложения в одну пару) — {auto_good}; «автоматически — только hunalign» — {auto_one}; «автоматически — якорь» (неподвижная точка прежнего выравнивания) — {auto_pin}; разобрано вручную в параграфе 1.1 — {confirmed}. При выборочной проверке с помощью ИИ (14.10.2026) из 15 пар прежнего выравнивания 7 совпали полностью и 1 частично; из 38 пар нового выравнивания 31 совпала полностью, 5 частично, 2 неверны. Эта проверка не заменяет проверку исследователем.',
    'm_equiv_title': '5. Принцип переводного эквивалента',
    'm_equiv': 'Переводной эквивалент — собственные слова переводчика в книге, приведённые дословно. Перевод ИИ или машинный перевод никогда не выдаётся за эквивалент. Результаты показываются отдельно по пяти источникам:',
    'm_equiv_items': [
        '<strong>Перевод в книге — подтверждён</strong>: слова, отмеченные исследователем в подтверждённой им паре (сплошное подчёркивание).',
        '<strong>Перевод в книге — предложение ИИ</strong>: только внутри подтверждённой пары, пунктир до проверки.',
        '<strong>Перевод в словаре</strong>: записи печатных словарей не показываются, пока не исправлены ошибки OCR.',
        '<strong>Эквивалент в справочном источнике</strong>: запись из английских сборников коллокаций; узбекская форма — предложение ИИ, не проверено.',
        '<strong>Пример</strong>: пример не из книг; всегда помечается «не из книг».',
    ],
    'm_cand_title': '6. Извлечение кандидатов в коллокации',
    'm_cand': 'В предложении с искомым словом рассматриваются 4 слова слева и справа от него (Uhrig & Proisl, 2012). Частеречные шаблоны: в узбекском существительное + глагол, подлежащее + сказуемое, прилагательное + существительное, наречие + глагол (шаблон существительное + существительное ведётся отдельным списком, видимым только исследователю); в английском adjective + noun и verb + noun. Публично показываются только кандидаты, встретившиеся в корпусе не менее 2 раз. Такая единица называется «автоматический кандидат — лингвистически не проверен»; статус «кандидат в коллокации» она получает только после лингвистической проверки.',
    'm_reference': '<strong>Справочная база</strong> ({ref} видимых записей) взята из английских учебных сборников коллокаций. Это не данные корпуса, в статистику главы III она не входит; прежние значения MI, t-score и частоты удалены, так как они не были вычислены ни на одном корпусе.',
    'm_stat_title': '7. Статистическое подтверждение (план)',
    'm_stat': [
        'Поскольку художественный корпус мал, статус подтверждается в большом опорном корпусе, а не цифрами исследуемого корпуса (Bernardini, 2007). Для английских сочетаний — Британский национальный корпус (BNC); для узбекских — Национальный корпус узбекского языка или uzWaC (выбор обосновывается во II главе).',
        'Исходные параметры: единица счёта — лемма; не менее 5 употреблений в опорном корпусе; основная мера — logDice (Rychlý, 2008); MI только вместе с частотным фильтром; t-score только как показатель надёжности (Gablasova et al., 2017); частота на миллион слов. Пороговые значения заранее не задаются, а калибруются на размеченной вручную выборке.',
        'Эти расчёты ещё не выполнены. Платформа не показывает ни одной цифры в качестве статистики опорного корпуса.',
    ],
    'm_rel_title': '8. Надёжность разметки (протокол)',
    'm_rel': 'Разметку выполняют два независимых аннотатора — автор и второй филолог — по письменной инструкции: сначала обучающая выборка из 50 единиц, затем не менее 20 процентов единиц (не меньше 200) размечаются независимо. Согласие измеряется каппой Коэна (Cohen, 1960); κ ≥ 0,8 — хорошая надёжность, 0,67–0,8 — допустимы осторожные выводы (Artstein & Poesio, 2008, с. 576). Второй аннотатор ещё не работал, поэтому коэффициента согласия пока нет.',
    'm_limits_title': '9. Ограничения',
    'm_limits': [
        'Большинство пар пока автоматические; переводной эквивалент из них не берётся.',
        'Часть речи и лемма узбекских слов определяются по правилам и могут быть ошибочными; поэтому автоматические кандидаты помечаются.',
        'Страницы «Chol va dengiz» относятся к электронной копии, а не к печатному изданию 1986 года.',
        'Печатные словари пока не используются.',
    ],
    'm_refs_title': 'Литература',
    'g_title': 'Инструкция по разметке',
    'g_lead': 'Каждая единица корпуса размечается по следующему порядку решений (диссертация, раздел 1.1.4). Ответ на каждый вопрос определяет, переходит ли единица к следующему шагу или получает окончательный статус.',
    'g_steps': [
        ('Состоит ли единица не менее чем из двух самостоятельных слов, компоненты которых непосредственно связаны синтаксически?', 'Если нет, единица не анализируется. Если да, компоненты записываются в форме леммы, отмечаются база и коллокат.'),
        ('Относится ли единица к исключаемой категории?', 'Пословицы и поговорки, целые предложения, сравнения, речевые формулы, имена собственные и прозвища, парные и повторные слова, грамматические конструкции со вспомогательными глаголами не анализируются.'),
        ('Имеет ли сочетание в данном контексте целостное образное переносное значение и теряется ли база при перефразировании?', 'Если да — фразеологическая единица.'),
        ('Ограничен ли выбор коллоката?', 'Если нет — свободное сочетание; если оно повторяется в тексте и передаётся в переводе готовым шаблоном — устойчивое свободное сочетание. Если спор сохраняется — пограничный случай.'),
        ('Есть ли статистическое подтверждение в опорном корпусе?', 'Если да — подтверждённая коллокация; если нет или данных недостаточно — кандидат в коллокации.'),
        ('Каково контекстуальное значение употребления и его соответствие в переводе?', 'Записываются помета значения (для омонимичных сочетаний) и тип соответствия: коллокация, одно слово, описательный оборот или опущение.'),
    ],
    'g_base_title': 'Определение базы и коллоката',
    'g_base_head': ['Структурная модель', 'Пример', 'База', 'Коллокат'],
    'g_base_rows': [
        ('существительное + глагол', '<em>dasturxon solmoq</em>, <em>javob bermoq</em>', 'существительное', 'глагол'),
        ('подлежащее + сказуемое', '<em>rangi o‘chmoq</em>', 'существительное', 'глагол'),
        ('прилагательное + существительное', '<em>og‘ir uyqu</em>', 'существительное', 'прилагательное'),
        ('наречие + глагол', '<em>qattiq uxlamoq</em>', 'глагол', 'наречие'),
        ('существительное + существительное', '<em>ko‘z yoshi</em>', '—', '—'),
    ],
    'g_base_note': 'Глагол с ослабленным значением (<em>qilmoq</em>, <em>bermoq</em>, <em>olmoq</em>) всегда является коллокатом. Сочетания существительное + существительное отмечаются отдельно как лексикализованные наименования.',
    'g_equiv_title': 'Типы соответствий в переводе',
    'g_equiv': [
        ('коллокация', '<em>og‘ir uyqu</em> → <em>a heavy sleep</em> (Cho‘lpon, 2000, с. 36; 2019, с. 74)'),
        ('одно слово', '<em>hazillashib javob berdi</em> → <em>answered … with a joke</em> (2000, с. 23; 2019, с. 63)'),
        ('описательный оборот', 'значение передано без коллокации, свободным сочетанием или предложением'),
        ('опущение', '<em>og‘ir uyquga ketdilar</em> → <em>fell asleep</em>: усилительный компонент утрачен (2000, с. 65; 2019, с. 98)'),
    ],
    'g_rel_title': 'Два аннотатора и согласие',
    'g_status_now': 'Текущее состояние: подтверждённых аннотаций — {ann}; единиц, размеченных обоими аннотаторами, — {shared}. Это меньше обучающей выборки протокола (50 единиц), поэтому коэффициент согласия не приводится.',
    's_title': 'Статистика корпуса',
    's_lead': 'Все цифры на этой странице вычисляются из данных корпуса в момент запроса.',
    's_size_title': '1. Объём текстов',
    's_size_note': 'Токен — последовательность букв в нижнем регистре; апостроф внутри слова (<em>ko‘ngil, ma’no, didn’t</em>) и дефис (<em>qah-qah</em>) слово не разделяют. Таблица считает весь сегментированный текст, включая предложения без пары. В разделах 3–6 считаются токены пословного выравнивания: только выровненные предложения, части слова через дефис и английские <em>’s</em>, <em>n’t</em> — отдельные токены, поэтому там числа другие. Гапакс — форма, встретившаяся в тексте один раз. TTR — отношение числа форм к числу токенов; оно зависит от длины текста, поэтому тексты разного объёма по нему напрямую не сравниваются.',
    's_head': ['Текст', 'Язык', 'Токены', 'Формы', 'Гапаксы', 'TTR'],
    's_pairs_title': '2. Параллельные пары',
    's_pairs_head': ['Пара', 'Всего', 'Разобрано в параграфе 1.1', 'Автоматически — оба метода совпали', 'Автоматически — только hunalign', 'Автоматически — якорь'],
    's_assoc_title': '3. Меры ассоциации',
    's_assoc': 'Меры, подтверждающие статус (logDice, MI, t-score), вычисляются в опорном корпусе, и это ещё не сделано. Цифры, вычисленные внутри исследуемого корпуса, неустойчивы из-за его малого объёма и не служат основанием для статуса, поэтому здесь они не показываются.',
    's_formulas_title': 'Формулы',
    's_ch3_title': '4. Таблицы главы III',
    's_ch3': 'Таблицы главы III строятся только из аннотаций, подтверждённых исследователем. Подтверждённых аннотаций сейчас: {ann}. Этого недостаточно для выводов, поэтому проценты не показываются.',
    'role_original': 'оригинал',
    'role_translation': 'перевод',
    'lang_uz': 'узбекский',
    'lang_en': 'английский',
}

# ---- v3 texts: word alignment, corpus collocations, equivalents in every sentence pair
T['uz'].update({
    'about_what': [
        'So‘rov tilini aniqlaydi va so‘zning korpusdagi barcha shakllarini hamda bir o‘zakli so‘zlarni topadi.',
        'Har bir uchrashni ikkinchi kitobdagi parallel gap bilan, ikkala tomonda asar va sahifasi bilan ko‘rsatadi.',
        'So‘z darajasidagi tekislash orqali tarjimonning o‘sha so‘z uchun ishlatgan so‘zini topib, uni ajratib ko‘rsatadi va muqobillar ulushini hisoblaydi.',
        'Korpusdagi kollokatsiyalarni tuzilish qolipi, uchrash soni, tarjimadagi muqobili va misoli bilan beradi.',
        'Kalit so‘zni kontekst bilan ko‘rsatadi (KWIC) va natijani CSV faylga yuklab beradi.',
    ],
    'about_state': 'Korpusda {pairs} ta parallel juftlik bor. Dissertatsiyaning 1.1-paragrafida tahlil qilingan {confirmed} ta juftlik alohida belgilangan. Tayanch korpus bo‘yicha statistik ko‘rsatkichlar keyingi bosqichda hisoblanadi. Bosma lug‘atlardan olingan yozuvlar OCR xatolari tuzatilgunga qadar ishlatilmaydi.',
    'm_walign_title': '5. So‘z darajasidagi tekislash va tarjima muqobili',
    'm_walign': [
        'Tarjima muqobili — tarjimonning kitobdagi so‘zlari, aynan ko‘chirilgan; AI yoki mashina tarjimasi muqobil sifatida berilmaydi. Har bir juftlikda qaysi so‘z qaysi so‘zga to‘g‘ri kelishi eflomal dasturi (Östling va Tiedemann, 2016) bilan topildi: u IBM tipidagi bayes modeli asosida ikki yo‘nalishda ishlaydi, natijalar grow-diag-final-and qoidasi bilan birlashtiriladi (fast_align vositalari, Dyer va boshq., 2013).',
        'Tekislashdan oldin inglizcha gaplar spaCy (en_core_web_sm) bilan tahlil qilinadi va so‘zlar lemmaga keltiriladi; o‘zbekcha so‘zlar qo‘shimchalaridan ehtiyotkorlik bilan ajratiladi (yuragi → yurak, ko‘ngli → ko‘ngil). Butun korpus bo‘yicha qaysi o‘zak qaysi lemma bilan necha marta bog‘langani jadvalga yoziladi. Muqobil sifatida faqat shu juftlik korpusda kamida 3 marta bog‘langan va u so‘rov so‘zi bog‘lanishlarining kamida 3 foizini tashkil etgan hollar ko‘rsatiladi; tasodifiy bitta bog‘lanish muqobil bo‘lmaydi.',
        'Natija sahifasida muqobillar uchrash soni va ulushi bilan, har biri kitobdan olingan misol bilan beriladi. Muqobil topilmagan gaplar ham ko‘rsatiladi: bunday joylarda tarjimon fikrni boshqa so‘zlar bilan bergan yoki tushirib qoldirgan. Dissertatsiyaning 1.1-paragrafida qo‘lda tahlil qilingan juftliklar «dissertatsiyada tahlil qilingan» belgisi bilan ajratiladi va ularda tadqiqotchi belgilagan muqobil ko‘rsatiladi.',
    ],
    'm_equiv_title': '6. Kollokatsiyalarni ajratish',
    'm_equiv': 'Kollokatsiyalar har ikki tilda, korpusning o‘zidan ajratiladi va kamida ikki marta uchraganlari olinadi (Bernardini, 2007, b. 8 dagi chastota > 1 chegarasi bilan bir xil).',
    'm_equiv_items': [
        '<strong>Inglizcha</strong>: spaCy sintaktik bog‘lanish tahlili bo‘yicha (Uhrig va Proisl, 2012, bog‘lanishga asoslangan ajratishni oynaga nisbatan aniqroq deb ko‘rsatgan): sifat + ot (amod), fe’l + to‘ldiruvchi (dobj), ega + fe’l (nsubj), fe’l + ravish, ravish + sifat, fe’l + predlog + ot, ot + ot.',
        '<strong>O‘zbekcha</strong>: o‘zbek tili hokim so‘zi oxirida keladigan til bo‘lgani uchun qoliplar yonma-yon so‘zlarda o‘qiladi (ot va fe’l orasida «ham», «bir» kabi bitta yuklama bo‘lishi mumkin): sifat + ot, ot + fe’l, ega + kesim, ravish + fe’l, ot + ot. So‘z turkumi uch manbadan aniqlanadi: fe’l qo‘shimchalari; tekislangan inglizcha so‘zning turkumini o‘zbekcha o‘zakka ko‘chirish (annotatsiya proyeksiyasi, Yarowsky va boshq., 2001); platformaning yopiq so‘z ro‘yxatlari. Boshqaruvdagi kelishik qo‘shimchasi qolipning bir qismi sifatida saqlanadi (uyga kirmoq, o‘rnidan turmoq), egalik qo‘shimchali ega + kesim qolipi ham shunday (rangi o‘chmoq).',
        'Har bir kollokatsiyaning tarjimadagi muqobili 5-banddagi usul bilan topiladi va uchrash soni bo‘yicha tartiblanadi. Korpus ichidagi logDice faqat ro‘yxatni tartiblash uchun ishlatiladi, maqom uchun asos bo‘lmaydi.',
    ],
    'm_cand_title': '7. Ma’lumotnoma to‘plamlari',
    'm_cand': 'Inglizcha o‘quv kollokatsiya to‘plamlaridan (Academic Collocation List, English Collocations in Use, 1000 English Collocations) olingan ro‘yxat alohida bo‘limda beriladi. U korpus ma’lumoti emas va statistikaga kirmaydi; avvalgi MI, t-score va chastota qiymatlari hech qaysi korpusda hisoblanmagani uchun o‘chirilgan, AI tomonidan tuzilgan o‘zbekcha shakllar esa ko‘rsatilmaydi.',
    'm_reference': 'Ommaviy ro‘yxatda {ref} ta yozuv bor.',
    'm_stat_title': '8. Statistik tasdiq',
    'm_rel_title': '9. Annotatsiya ishonchliligi',
    'm_limits_title': '10. Cheklovlar',
    'm_limits': [
        'Gap va so‘z darajasidagi tekislash avtomatik; tanlab tekshiruvda gap juftliklarining katta qismi mos keldi, lekin xato juftlik ham uchraydi (4-band).',
        'So‘z darajasidagi muqobil asosan leksik moslikni ko‘rsatadi; tarjimon fikrni tasviriy yo‘l bilan bergan joylarda muqobil topilmasligi mumkin.',
        'O‘zbekcha so‘z turkumi va lemma qoidalar hamda proyeksiya bilan aniqlanadi; ayrim kollokatsiyalar noto‘g‘ri qolipga tushishi mumkin.',
        '«Chol va dengiz» sahifalari 1986-yilgi bosma nashrga emas, elektron nusxaga tegishli.',
    ],
})
T['en'].update({
    'about_what': [
        'It detects the language of the query and finds every form of the word in the corpus, together with words built on the same root.',
        'It shows every occurrence with its parallel sentence from the other book, with the work and the page on both sides.',
        'Through word alignment it finds the words the translator used for the searched word, highlights them and computes the share of each equivalent.',
        'It lists the collocations of the corpus with their structural pattern, frequency, counterpart in the translation and an example.',
        'It shows the keyword in context (KWIC) and lets you download the result as a CSV file.',
    ],
    'about_state': 'The corpus has {pairs} parallel pairs. The {confirmed} pairs analysed in paragraph 1.1 of the dissertation are marked separately. Statistical measures against a reference corpus will be computed at the next stage. Entries from printed dictionaries are not used until their OCR errors are corrected.',
    'm_walign_title': '5. Word alignment and the translation equivalent',
    'm_walign': [
        'A translation equivalent is the translator’s own words in the book, copied verbatim; AI or machine translation is never given as an equivalent. Which word of a pair corresponds to which was found with eflomal (Östling & Tiedemann, 2016), a Bayesian aligner of the IBM type, run in both directions; the two directions are combined with the grow-diag-final-and heuristic (fast_align tools, Dyer et al., 2013).',
        'Before alignment, English sentences are parsed with spaCy (en_core_web_sm) and reduced to lemmas; Uzbek words are carefully stripped of their endings (yuragi → yurak, ko‘ngli → ko‘ngil). Across the whole corpus, a table records how often each stem is linked to each lemma. A link is shown as an equivalent only if that pair is linked at least 3 times in the corpus and makes up at least 3 per cent of the links of the searched word; a single accidental link is never an equivalent.',
        'The result page gives the equivalents with their counts and shares, each with an example from the book. Sentences without a word-level equivalent are shown too: there the translator expressed the idea with other words or left it out. The pairs analysed by hand in paragraph 1.1 of the dissertation carry the mark “analysed in the dissertation” and show the equivalent marked by the researcher.',
    ],
    'm_equiv_title': '6. Extraction of collocations',
    'm_equiv': 'Collocations are extracted from the corpus itself in both languages; those occurring at least twice are kept (the same as the frequency > 1 threshold of Bernardini, 2007, p. 8).',
    'm_equiv_items': [
        '<strong>English</strong>: by spaCy dependency relations (Uhrig & Proisl, 2012, showed dependency-based extraction to be more accurate than a window): adjective + noun (amod), verb + object (dobj), subject + verb (nsubj), verb + adverb, adverb + adjective, verb + preposition + noun, noun + noun.',
        '<strong>Uzbek</strong>: Uzbek is head-final, so patterns are read on adjacent words (one particle such as “ham” or “bir” may stand between a noun and its verb): adjective + noun, noun + verb, subject + predicate, adverb + verb, noun + noun. Part of speech comes from three sources: verb endings; the part of speech of the aligned English word projected onto the Uzbek stem (annotation projection, Yarowsky et al., 2001); the closed word lists of the platform. A governing case ending stays part of the pattern (uyga kirmoq, o‘rnidan turmoq), and so does the possessive ending of subject + predicate (rangi o‘chmoq).',
        'The counterpart of each collocation in the translation is found with the method of section 5 and ranked by frequency. The within-corpus logDice only orders the list; it is no basis for a status.',
    ],
    'm_cand_title': '7. Reference collections',
    'm_cand': 'A list from English learner collocation collections (Academic Collocation List, English Collocations in Use, 1000 English Collocations) is given in a separate section. It is not corpus data and is not used in the statistics; its former MI, t-score and frequency values were deleted because they had not been computed on any corpus, and Uzbek forms composed by AI are not shown.',
    'm_reference': 'The public list has {ref} entries.',
    'm_stat_title': '8. Statistical confirmation',
    'm_rel_title': '9. Reliability of annotation',
    'm_limits_title': '10. Limitations',
    'm_limits': [
        'Sentence and word alignment are automatic; in the spot check most sentence pairs matched, but wrong pairs occur (section 4).',
        'A word-level equivalent mainly shows lexical correspondence; where the translator rendered the idea descriptively, no equivalent may be found.',
        'Uzbek part of speech and lemma are found by rules and projection; some collocations may get a wrong pattern.',
        'The pages of «Chol va dengiz» belong to the electronic copy, not to the 1986 printed edition.',
    ],
})
T['ru'].update({
    'about_what': [
        'Определяет язык запроса и находит все формы слова в корпусе, а также слова с тем же корнем.',
        'Показывает каждое употребление с параллельным предложением другой книги, с произведением и страницей на обеих сторонах.',
        'С помощью пословного выравнивания находит слова, которыми переводчик передал искомое слово, выделяет их и считает долю каждого эквивалента.',
        'Даёт коллокации корпуса со структурной моделью, частотой, соответствием в переводе и примером.',
        'Показывает ключевое слово в контексте (KWIC) и позволяет скачать результат файлом CSV.',
    ],
    'about_state': 'В корпусе {pairs} параллельных пар. {confirmed} пар, разобранных в параграфе 1.1 диссертации, отмечены отдельно. Статистические меры по опорному корпусу будут вычислены на следующем этапе. Записи печатных словарей не используются, пока не исправлены ошибки OCR.',
    'm_walign_title': '5. Пословное выравнивание и переводной эквивалент',
    'm_walign': [
        'Переводной эквивалент — собственные слова переводчика в книге, приведённые дословно; перевод ИИ или машинный перевод никогда не выдаётся за эквивалент. Какое слово пары чему соответствует, найдено программой eflomal (Östling & Tiedemann, 2016) — байесовским выравнивателем типа IBM, запущенным в обоих направлениях; направления объединены эвристикой grow-diag-final-and (инструменты fast_align, Dyer et al., 2013).',
        'Перед выравниванием английские предложения разбираются spaCy (en_core_web_sm) и приводятся к леммам; у узбекских слов осторожно отделяются окончания (yuragi → yurak, ko‘ngli → ko‘ngil). По всему корпусу составляется таблица: сколько раз каждая основа связана с каждой леммой. Связь показывается как эквивалент, только если эта пара связана в корпусе не менее 3 раз и составляет не менее 3 процентов связей искомого слова; одна случайная связь эквивалентом не считается.',
        'На странице результатов эквиваленты даны с числом и долей употреблений, каждый — с примером из книги. Предложения без пословного эквивалента тоже показываются: там переводчик передал мысль другими словами или опустил её. Пары, разобранные вручную в параграфе 1.1 диссертации, имеют помету «разобрано в диссертации» и показывают эквивалент, отмеченный исследователем.',
    ],
    'm_equiv_title': '6. Извлечение коллокаций',
    'm_equiv': 'Коллокации извлекаются из самого корпуса на обоих языках; сохраняются встретившиеся не менее двух раз (так же, как порог частоты > 1 у Bernardini, 2007, с. 8).',
    'm_equiv_items': [
        '<strong>Английский</strong>: по синтаксическим связям spaCy (Uhrig & Proisl, 2012, показали, что извлечение по зависимостям точнее окна): прилагательное + существительное (amod), глагол + дополнение (dobj), подлежащее + глагол (nsubj), глагол + наречие, наречие + прилагательное, глагол + предлог + существительное, существительное + существительное.',
        '<strong>Узбекский</strong>: узбекский — язык с вершиной в конце, поэтому модели читаются на соседних словах (между существительным и глаголом может стоять одна частица — «ham», «bir»): прилагательное + существительное, существительное + глагол, подлежащее + сказуемое, наречие + глагол, существительное + существительное. Часть речи определяется по трём источникам: глагольные окончания; перенос части речи выровненного английского слова на узбекскую основу (проекция разметки, Yarowsky et al., 2001); закрытые списки слов платформы. Падежное окончание управления сохраняется как часть модели (uyga kirmoq, o‘rnidan turmoq), так же как притяжательное окончание в модели подлежащее + сказуемое (rangi o‘chmoq).',
        'Соответствие каждой коллокации в переводе находится методом раздела 5 и упорядочивается по частоте. logDice внутри корпуса лишь упорядочивает список и не служит основанием для статуса.',
    ],
    'm_cand_title': '7. Справочные сборники',
    'm_cand': 'Список из английских учебных сборников коллокаций (Academic Collocation List, English Collocations in Use, 1000 English Collocations) дан отдельным разделом. Это не данные корпуса, в статистику он не входит; прежние значения MI, t-score и частоты удалены, так как не были вычислены ни на одном корпусе, а узбекские формы, составленные ИИ, не показываются.',
    'm_reference': 'В открытом списке {ref} записей.',
    'm_stat_title': '8. Статистическое подтверждение',
    'm_rel_title': '9. Надёжность разметки',
    'm_limits_title': '10. Ограничения',
    'm_limits': [
        'Выравнивание предложений и слов автоматическое; при выборочной проверке большинство пар совпало, но встречаются и ошибочные (раздел 4).',
        'Пословный эквивалент показывает прежде всего лексическое соответствие; там, где переводчик передал мысль описательно, эквивалент может не найтись.',
        'Часть речи и лемма узбекских слов определяются правилами и проекцией; отдельные коллокации могут получить неверную модель.',
        'Страницы «Chol va dengiz» относятся к электронной копии, а не к печатному изданию 1986 года.',
    ],
})

# ---- v3.1 texts: statistics analysis, association measures, spot check, neutral wording
T['uz'].update({
    'src_pairs': 'parallel juftliklar: {pairs}; ulardan 1.1-paragrafda tahlil qilingani: {confirmed}',
    'g_status_now': 'Hozirgi holat: yakunlangan annotatsiyalar — {ann}; ikki annotator umumiy belgilagan birliklar — {shared}. Kelishuv koeffitsiyenti protokoldagi 50 birlikli o‘quv to‘plami to‘lgach hisoblanadi.',
    'm_walign': [
        'Tarjima ekvivalenti (interfeysda — «tarjimadagi muqobil») — tarjimonning kitobdagi so‘zlari, aynan ko‘chirilgan; AI yoki mashina tarjimasi ekvivalent sifatida berilmaydi. Har bir juftlikda qaysi so‘z qaysi so‘zga to‘g‘ri kelishi eflomal dasturi (Östling va Tiedemann, 2016) bilan topildi: u IBM tipidagi bayes modeli asosida ikki yo‘nalishda ishlaydi, natijalar grow-diag-final-and qoidasi bilan birlashtiriladi (fast_align vositalari, Dyer va boshq., 2013).',
        'Tekislashdan oldin inglizcha gaplar spaCy (en_core_web_sm) bilan tahlil qilinadi va so‘zlar lemmaga keltiriladi; o‘zbekcha so‘zlar qo‘shimchalaridan ehtiyotkorlik bilan ajratiladi (yuragi → yurak, ko‘ngli → ko‘ngil). Butun korpus bo‘yicha qaysi o‘zak qaysi lemma bilan necha marta bog‘langani jadvalga yoziladi. Ekvivalent sifatida faqat shu juftlik korpusda kamida 3 marta bog‘langan va u so‘rov so‘zi bog‘lanishlarining kamida 3 foizini tashkil etgan hollar ko‘rsatiladi; tasodifiy bitta bog‘lanish ekvivalent bo‘lmaydi.',
        'Natija sahifasida ekvivalentlar uchrash soni va ulushi bilan, har biri kitobdan olingan misol bilan beriladi. Ekvivalent topilmagan gaplar ham ko‘rsatiladi: bunday joylarda tarjimon fikrni boshqa so‘zlar bilan bergan yoki tushirib qoldirgan. Dissertatsiyaning 1.1-paragrafida qo‘lda tahlil qilingan juftliklar «dissertatsiyada tahlil qilingan» belgisi bilan ajratiladi va ularda tadqiqotchi belgilagan ekvivalent ko‘rsatiladi.',
        'Sun’iy intellekt yordamida bajarilgan tanlab tekshiruvda (14.10.2026; platforma ko‘rsatgan 50 ta tasodifiy ekvivalent, 25 tasi o‘zbekcha va 25 tasi inglizcha so‘rov so‘zi uchun) 45 tasi to‘g‘ri, 3 tasi qisman to‘g‘ri, 2 tasi noto‘g‘ri chiqdi; ikkala xato ham ma’nosi kuchsiz inglizcha so‘zlarda (<em>have</em>, <em>though</em>) uchradi. Ekvivalent butun korpus bo‘yicha o‘zbekcha mustaqil so‘zlarning 29,7 foizi va inglizcha mustaqil so‘zlarning 39,8 foizi uchun topiladi: chegaralar aniqlikni qamrovdan ustun qo‘yish uchun qat’iy tanlangan.',
    ],
    'm_align': 'Juftliklar avtomatik tekislangan. Ikki kitob gaplari hunalign dasturi (Varga va boshq., 2007) bilan qayta tekislandi: u gap uzunligi modelini (Gale va Church, 1993) leksik dalil bilan birlashtiradi. Leksik dalil sifatida ikkala kitobda bir xil yoziladigan nomlar va sonlar olindi, dastur birinchi o‘tishdan so‘ng o‘z lug‘atini ham tuzdi. 1.1-paragrafda tahlil qilingan juftliklar va oldingi tekislashning tayanch nuqtalari qo‘zg‘almas nuqta sifatida saqlandi, shuning uchun xato ikki qo‘zg‘almas nuqta orasidan chiqmaydi. Juftlik maqomlari: «avtomatik — ikki usul mos» (oldingi uzunlik va sahifa usuli ham shu gaplarni bir juftlikka qo‘ygan) — {auto_good}; «avtomatik — faqat hunalign» — {auto_one}; «avtomatik — tayanch nuqta» (oldingi tekislashdagi qo‘zg‘almas nuqta) — {auto_pin}; 1.1-paragrafda qo‘lda tahlil qilingan — {confirmed}. Sun’iy intellekt yordamida bajarilgan tanlab tekshiruvda (14.10.2026) yangi tekislashning 38 juftligidan 31 tasi to‘liq, 5 tasi qisman mos, 2 tasi noto‘g‘ri chiqdi (oldingi tekislashda 15 juftlikdan 7 tasi to‘liq, 1 tasi qisman mos edi).',
    'm_equiv_items': [
        '<strong>Inglizcha</strong>: spaCy sintaktik bog‘lanish tahlili bo‘yicha (Uhrig va Proisl, 2012, bog‘lanishga asoslangan ajratishni oynaga nisbatan aniqroq deb ko‘rsatgan): sifat + ot (amod), fe’l + to‘ldiruvchi (dobj), ega + fe’l (nsubj), fe’l + ravish, ravish + sifat, fe’l + predlog + ot, ot + ot.',
        '<strong>O‘zbekcha</strong>: o‘zbek tilida hokim so‘z oxirida keladi, shuning uchun qoliplar yonma-yon so‘zlarda o‘qiladi (ot va fe’l orasida «ham», «bir» kabi bitta yuklama bo‘lishi mumkin): sifat + ot, ot + fe’l, ega + kesim, ravish + fe’l, ot + ot. So‘z turkumi uch manbadan aniqlanadi: fe’l qo‘shimchalari; tekislangan inglizcha so‘zning turkumini o‘zbekcha o‘zakka ko‘chirish (annotatsiya proyeksiyasi, Yarowsky va boshq., 2001); platformaning yopiq so‘z ro‘yxatlari. Boshqaruvdagi kelishik qo‘shimchasi qolipning bir qismi sifatida saqlanadi (<em>uyga kirmoq</em>, <em>o‘rnidan turmoq</em>).',
        'Metodologiyaning 1-bandidagi istisnolar avtomatik qo‘llanadi: juft va takroriy so‘zlar (<em>yonma-yon</em>, <em>ota-ona</em>) hamda ravishdosh + ko‘makchi fe’l qurilmalari (<em>tutib turmoq</em>, <em>qila olmoq</em>, <em>ko‘tara tushmoq</em>) kollokatsiya sifatida olinmaydi.',
        'Har bir kollokatsiyaning tarjimadagi ekvivalenti 5-banddagi usul bilan uning barcha uchrashlarida topiladi va uchrash soni bo‘yicha tartiblanadi. Korpus ichidagi assotsiatsiya ko‘rsatkichlari «Statistika» sahifasida o‘lchovlarni qiyoslash uchun beriladi va maqom uchun asos bo‘lmaydi.',
    ],
    'm_stat_title': '8. Tayanch korpus statistikasi',
    'm_stat': [
        'Badiiy korpus kichik bo‘lgani uchun maqom tadqiqot korpusidagi raqamlar bilan emas, katta tayanch korpusdagi ko‘rsatkichlar bilan belgilanadi (Bernardini, 2007). Inglizcha birikmalar uchun — Britaniya milliy korpusi (BNC); o‘zbekcha uchun — O‘zbek tili milliy korpusi yoki uzWaC (tanlov II bobda asoslanadi).',
        'Dastlabki parametrlar: hisob birligi — lemma; tayanch korpusda kamida 5 marta uchrash; asosiy o‘lchov — logDice (Rychlý, 2008); MI faqat chastota filtri bilan; t-score faqat ishonchlilik ko‘rsatkichi sifatida (Gablasova va boshq., 2017); chastota million so‘zga nisbatan. Chegaraviy qiymatlar oldindan belgilanmaydi, qo‘lda annotatsiya qilingan to‘plamda kalibrlanadi.',
        'Tayanch korpus bo‘yicha hisob keyingi bosqichda bajariladi. Platformadagi MI, t-score, logDice va G² qiymatlari tadqiqot korpusining o‘zida hisoblangan; ular «Statistika» sahifasida o‘lchovlar bir xil birikmalarni qanday tartiblashini qiyoslash uchun beriladi.',
    ],
    's_auto_title': '3. Kollokatsiyalarning tarjimada berilishi',
    's_auto_note': 'Jadval korpusdagi barcha kollokatsiyalar (kamida 2 marta uchraganlar) va ularning har bir uchrashi bo‘yicha avtomatik hisoblangan. Ekvivalent metodologiyaning 5-bandidagi so‘z darajasidagi tekislash bilan topiladi va har doim tarjimonning kitobdagi so‘zidir.',
    's_auto_cols': '«Ekvivalent topilgan» — tarjimadan ekvivalent topilgan uchrashlar ulushi; qolgan uchrashlarda tarjimon fikrni tasviriy yo‘l bilan bergan, tushirib qoldirgan yoki tekislash ishonchli bog‘lanish topmagan. «Bitta so‘z bilan» va «So‘z birikmasi bilan» ulushlari ekvivalent topilgan uchrashlarga nisbatan hisoblanadi va ekvivalentdagi mustaqil so‘zlar soniga qarab ajratiladi.',
    's_dir_head': ['Yo‘nalish', 'Qolip', 'Kollokatsiyalar', 'Uchrashlar', 'Ekvivalent topilgan', 'Bitta so‘z bilan', 'So‘z birikmasi bilan'],
    's_dir_uz_src': 'Cho‘lpon asliyati (o‘zbekcha) → «Night and Day»',
    's_dir_en_src': 'Hemingway asliyati (inglizcha) → «Chol va dengiz»',
    's_dir_en_tgt': 'Fort tarjimasi (inglizcha) → asliyatdagi o‘zbekcha manba',
    's_dir_uz_tgt': 'G‘ofurov tarjimasi (o‘zbekcha) → asliyatdagi inglizcha manba',
    's_total': 'jami',
    's_top_head': ['Kollokatsiya', 'Qolip', 'Uchrashlar', 'Ekvivalent topilgan', 'Tarjimadagi asosiy ekvivalentlar (uchrash soni)'],
    's_top_title_s_dir_uz_src': 'Cho‘lpon asliyatida eng ko‘p uchragan kollokatsiyalar va ularning «Night and Day»dagi ekvivalentlari',
    's_top_title_s_dir_en_src': 'Hemingway asliyatida eng ko‘p uchragan kollokatsiyalar va ularning «Chol va dengiz»dagi ekvivalentlari',
    's_assoc_title': '4. Assotsiatsiya o‘lchovlarini qiyoslash',
    's_assoc': 'Kollokatsiyaning maqomi 1.1-paragrafga ko‘ra katta tayanch korpusdagi ko‘rsatkichlar bilan belgilanadi. Bu bo‘limdagi qiymatlar tadqiqot korpusining o‘zida hisoblangan va boshqa savolga javob beradi: bir xil birikmalar to‘plamini to‘rt o‘lchov — MI, t-score, logDice va log-likelihood (G², Dunning, 1993) — qanday tartiblaydi. O₁₁ — birikmaning uchrash soni, R₁ va C₁ — birinchi va oxirgi komponentning shu tildagi matnlarda uchrash soni, N — shu tildagi tokenlar soni (Evert, 2008).',
    's_meas_uz': 'O‘zbekcha kollokatsiyalar (Cho‘lpon asliyati va G‘ofurov tarjimasi)',
    's_meas_en': 'Inglizcha kollokatsiyalar (Hemingway asliyati va Fort tarjimasi)',
    's_meas_n': '{types} ta kollokatsiya; N = {tokens} token.',
    's_meas_corr': 'O‘lchovlar bergan tartiblar o‘rtasidagi Spirmen korrelyatsiyasi (ρ)',
    's_meas_profile': 'Har bir o‘lchov bo‘yicha birinchi 50 kollokatsiya',
    's_meas_profile_head': ['O‘lchov', 'O‘rtacha uchrash soni', 'Ikki marta uchraganlar ulushi'],
    's_meas_top': 'Har bir o‘lchov bo‘yicha birinchi 8 kollokatsiya (qavs ichida — uchrash soni)',
    's_meas_top_head': ['O‘lchov', 'Kollokatsiyalar'],
    's_meas_reading': 'Jadvallarni o‘qish: MI komponentlari kam uchraydigan, ammo deyarli faqat birga keladigan birikmalarni yuqoriga chiqaradi, shuning uchun uning ro‘yxati boshida korpusda ikki marta uchragan nomlar va atamalar turadi; t-score va G² yuqori chastotali birikmalarni afzal ko‘radi va chastota ro‘yxatiga yaqin tartib beradi; logDice ikki chekka orasida turadi. Bu farq MI va t-score haqida adabiyotda aytilgan kuzatishga mos keladi (Gablasova va boshq., 2017). Kichik korpusda MI ikki-uch uchrashga tayanadi, shuning uchun dissertatsiyada u faqat chastota filtri bilan qo‘llanadi (metodologiya, 9-band).',
    's_ch3_title': '5. III bob uchun ma’lumot',
    's_ch3': 'III bobdagi miqdoriy tahlil uchun 3- va 4-bo‘limlardagi jadvallar asos bo‘ladi: ular korpusdagi barcha kollokatsiyalar bo‘yicha avtomatik hisoblangan, har bir raqam ortidagi gaplarni esa kollokatsiya sahifasida ko‘rish mumkin. Dissertatsiyaning 1.1-paragrafida qo‘lda tahlil qilingan birliklar sifat tahlili uchun namuna sifatida alohida belgilangan.',
})
T['en'].update({
    'src_pairs': 'parallel pairs: {pairs}; analysed in paragraph 1.1: {confirmed}',
    'g_status_now': 'Current state: completed annotations — {ann}; units annotated by both annotators — {shared}. The agreement coefficient is computed once the 50-unit training set of the protocol is complete.',
    'm_walign': [
        'A translation equivalent (in the interface, “counterpart in the translation”) is the translator’s own words in the book, copied verbatim; AI or machine translation is never given as an equivalent. Which word of a pair corresponds to which was found with eflomal (Östling & Tiedemann, 2016), a Bayesian aligner of the IBM type, run in both directions; the two directions are combined with the grow-diag-final-and heuristic (fast_align tools, Dyer et al., 2013).',
        'Before alignment, English sentences are parsed with spaCy (en_core_web_sm) and reduced to lemmas; Uzbek words are carefully stripped of their endings (yuragi → yurak, ko‘ngli → ko‘ngil). Across the whole corpus, a table records how often each stem is linked to each lemma. A link is shown as an equivalent only if that pair is linked at least 3 times in the corpus and makes up at least 3 per cent of the links of the searched word; a single accidental link is never an equivalent.',
        'The result page gives the equivalents with their counts and shares, each with an example from the book. Sentences without a word-level equivalent are shown too: there the translator expressed the idea with other words or left it out. The pairs analysed by hand in paragraph 1.1 of the dissertation carry the mark “analysed in the dissertation” and show the equivalent marked by the researcher.',
        'In an AI-assisted spot check (14.10.2026; 50 random equivalents shown by the platform, 25 for Uzbek and 25 for English query words), 45 were correct, 3 partly correct and 2 wrong; both errors concerned semantically light English words (<em>have</em>, <em>though</em>). Across the whole corpus an equivalent is found for 29.7 per cent of Uzbek content words and 39.8 per cent of English content words: the thresholds are strict on purpose, to put precision before coverage.',
    ],
    'm_align': 'The pairs are aligned automatically. The sentences of both books were re-aligned with hunalign (Varga et al., 2007), which combines the sentence-length model (Gale & Church, 1993) with lexical evidence. The lexical evidence consists of names and numbers written the same in both books, and the program also builds its own dictionary after a first pass. The pairs analysed in paragraph 1.1 and the pins of the earlier alignment were kept as fixed points, so an error cannot run past a fixed point. Statuses: “automatic — two methods agree” (the earlier length-and-page method also put these sentences into one pair) — {auto_good}; “automatic — hunalign only” — {auto_one}; “automatic — pin” (a fixed point of the earlier alignment) — {auto_pin}; analysed by hand in paragraph 1.1 — {confirmed}. In an AI-assisted spot check (14.10.2026), of 38 pairs of the new alignment 31 matched fully, 5 partly and 2 were wrong (in the earlier alignment, 7 of 15 pairs had matched fully and 1 partly).',
    'm_equiv_items': [
        '<strong>English</strong>: by spaCy dependency relations (Uhrig & Proisl, 2012, showed dependency-based extraction to be more accurate than a window): adjective + noun (amod), verb + object (dobj), subject + verb (nsubj), verb + adverb, adverb + adjective, verb + preposition + noun, noun + noun.',
        '<strong>Uzbek</strong>: Uzbek is head-final, so patterns are read on adjacent words (one particle such as “ham” or “bir” may stand between a noun and its verb): adjective + noun, noun + verb, subject + predicate, adverb + verb, noun + noun. Part of speech comes from three sources: verb endings; the part of speech of the aligned English word projected onto the Uzbek stem (annotation projection, Yarowsky et al., 2001); the closed word lists of the platform. A governing case ending stays part of the pattern (<em>uyga kirmoq</em>, <em>o‘rnidan turmoq</em>).',
        'The exclusions of section 1 are applied automatically: paired and reduplicated words (<em>yonma-yon</em>, <em>ota-ona</em>) and converb + auxiliary verb constructions (<em>tutib turmoq</em>, <em>qila olmoq</em>, <em>ko‘tara tushmoq</em>) are not taken as collocations.',
        'The equivalent of each collocation in the translation is found with the method of section 5 in all its occurrences and ranked by frequency. Within-corpus association measures are given on the Statistics page to compare the measures; they are no basis for a status.',
    ],
    'm_stat_title': '8. Reference corpus statistics',
    'm_stat': [
        'Because a literary corpus is small, status is decided by the measures of a large reference corpus rather than by the figures of the study corpus (Bernardini, 2007). For English combinations — the British National Corpus (BNC); for Uzbek — the Uzbek National Corpus or uzWaC (the choice is argued in chapter II).',
        'Initial parameters: the counting unit is the lemma; at least 5 occurrences in the reference corpus; the main measure is logDice (Rychlý, 2008); MI only together with a frequency filter; t-score only as an indicator of reliability (Gablasova et al., 2017); frequency per million words. Thresholds are not fixed in advance; they are calibrated on a manually annotated sample.',
        'The reference-corpus computation is the next stage. The MI, t-score, logDice and G² values on the platform are computed within the study corpus; the Statistics page gives them to compare how the measures rank the same combinations.',
    ],
    's_auto_title': '3. How collocations are rendered in translation',
    's_auto_note': 'The table is computed automatically over all collocations of the corpus (those occurring at least twice) and every one of their occurrences. The equivalent is found with the word alignment of section 5 of the methodology and is always the translator’s own word in the book.',
    's_auto_cols': '“Equivalent found” is the share of occurrences for which an equivalent was found in the translation; in the others the translator rendered the idea descriptively, left it out, or the alignment found no reliable link. “By one word” and “by a word combination” are shares of the occurrences with an equivalent, split by the number of content words in the equivalent.',
    's_dir_head': ['Direction', 'Pattern', 'Collocations', 'Occurrences', 'Equivalent found', 'By one word', 'By a word combination'],
    's_dir_uz_src': 'Cho‘lpon’s original (Uzbek) → «Night and Day»',
    's_dir_en_src': 'Hemingway’s original (English) → «Chol va dengiz»',
    's_dir_en_tgt': 'Fort’s translation (English) → the Uzbek source',
    's_dir_uz_tgt': 'G‘ofurov’s translation (Uzbek) → the English source',
    's_total': 'total',
    's_top_head': ['Collocation', 'Pattern', 'Occurrences', 'Equivalent found', 'Main equivalents in the translation (occurrences)'],
    's_top_title_s_dir_uz_src': 'The most frequent collocations of Cho‘lpon’s original and their equivalents in «Night and Day»',
    's_top_title_s_dir_en_src': 'The most frequent collocations of Hemingway’s original and their equivalents in «Chol va dengiz»',
    's_assoc_title': '4. Comparison of association measures',
    's_assoc': 'According to paragraph 1.1, the status of a collocation is decided by the measures of a large reference corpus. The values in this section are computed within the study corpus and answer a different question: how four measures — MI, t-score, logDice and log-likelihood (G², Dunning, 1993) — rank the same set of combinations. O₁₁ is the frequency of the combination, R₁ and C₁ the frequencies of its first and last component in the texts of that language, N the number of tokens of that language (Evert, 2008).',
    's_meas_uz': 'Uzbek collocations (Cho‘lpon’s original and G‘ofurov’s translation)',
    's_meas_en': 'English collocations (Hemingway’s original and Fort’s translation)',
    's_meas_n': '{types} collocations; N = {tokens} tokens.',
    's_meas_corr': 'Spearman correlation (ρ) between the rankings of the measures',
    's_meas_profile': 'The first 50 collocations by each measure',
    's_meas_profile_head': ['Measure', 'Mean frequency', 'Share occurring twice'],
    's_meas_top': 'The first 8 collocations by each measure (frequency in brackets)',
    's_meas_top_head': ['Measure', 'Collocations'],
    's_meas_reading': 'Reading the tables: MI promotes combinations whose components are rare but occur almost only together, so its list opens with names and terms that occur twice in the corpus; t-score and G² prefer frequent combinations and give an order close to plain frequency; logDice lies between the two. This matches what the literature says about MI and t-score (Gablasova et al., 2017). In a small corpus MI rests on two or three occurrences, which is why the dissertation uses it only with a frequency filter (methodology, section 9).',
    's_ch3_title': '5. Data for chapter III',
    's_ch3': 'The tables of sections 3 and 4 are the basis of the quantitative analysis in chapter III: they are computed automatically over all collocations of the corpus, and the sentences behind each figure can be seen on the page of the collocation. The units analysed by hand in paragraph 1.1 of the dissertation are marked separately as a sample for the qualitative analysis.',
})
T['ru'].update({
    'src_pairs': 'параллельных пар: {pairs}; из них разобрано в параграфе 1.1: {confirmed}',
    'g_status_now': 'Текущее состояние: завершённых аннотаций — {ann}; единиц, размеченных обоими аннотаторами, — {shared}. Коэффициент согласия вычисляется после того, как будет набрана обучающая выборка протокола (50 единиц).',
    'm_walign': [
        'Переводной эквивалент (в интерфейсе — «соответствие в переводе») — собственные слова переводчика в книге, приведённые дословно; перевод ИИ или машинный перевод никогда не выдаётся за эквивалент. Какое слово пары чему соответствует, найдено программой eflomal (Östling & Tiedemann, 2016) — байесовским выравнивателем типа IBM, запущенным в обоих направлениях; направления объединяются эвристикой grow-diag-final-and (инструменты fast_align, Dyer et al., 2013).',
        'Перед выравниванием английские предложения разбираются spaCy (en_core_web_sm) и приводятся к леммам; у узбекских слов осторожно отделяются окончания (yuragi → yurak, ko‘ngli → ko‘ngil). По всему корпусу составляется таблица: сколько раз каждая основа связана с каждой леммой. Связь показывается как эквивалент, только если эта пара связана в корпусе не менее 3 раз и составляет не менее 3 процентов всех связей искомого слова; одна случайная связь эквивалентом не считается.',
        'На странице результатов эквиваленты даны с числом и долей употреблений, каждый — с примером из книги. Предложения без пословного эквивалента тоже показываются: там переводчик передал мысль другими словами или опустил её. Пары, разобранные вручную в параграфе 1.1 диссертации, имеют помету «разобрано в диссертации» и показывают эквивалент, отмеченный исследователем.',
        'При выборочной проверке с помощью ИИ (14.10.2026; 50 случайных эквивалентов, показанных платформой, — 25 для узбекских и 25 для английских слов запроса) 45 оказались верными, 3 — частично верными, 2 — неверными; обе ошибки касаются семантически слабых английских слов (<em>have</em>, <em>though</em>). По всему корпусу эквивалент находится для 29,7 процента узбекских и 39,8 процента английских знаменательных слов: пороги выбраны строгими, чтобы точность стояла выше полноты.',
    ],
    'm_align': 'Пары выровнены автоматически. Предложения обеих книг заново выровнены программой hunalign (Varga et al., 2007), которая объединяет модель длины предложений (Gale & Church, 1993) с лексическими данными. Лексические данные — имена и числа, одинаково записанные в обеих книгах; после первого прохода программа также строит собственный словарь. Пары, разобранные в параграфе 1.1, и якоря прежнего выравнивания сохранены как неподвижные точки, поэтому ошибка не выходит за пределы участка между ними. Статусы: «автоматически — оба метода совпали» (прежний метод по длине и страницам тоже объединил эти предложения в одну пару) — {auto_good}; «автоматически — только hunalign» — {auto_one}; «автоматически — якорь» (неподвижная точка прежнего выравнивания) — {auto_pin}; разобрано вручную в параграфе 1.1 — {confirmed}. При выборочной проверке с помощью ИИ (14.10.2026) из 38 пар нового выравнивания 31 совпала полностью, 5 — частично, 2 неверны (в прежнем выравнивании из 15 пар полностью совпали 7 и частично 1).',
    'm_equiv_items': [
        '<strong>Английский</strong>: по синтаксическим связям spaCy (Uhrig & Proisl, 2012, показали, что извлечение по зависимостям точнее окна): прилагательное + существительное (amod), глагол + дополнение (dobj), подлежащее + глагол (nsubj), глагол + наречие, наречие + прилагательное, глагол + предлог + существительное, существительное + существительное.',
        '<strong>Узбекский</strong>: в узбекском вершина стоит в конце, поэтому модели читаются на соседних словах (между существительным и глаголом может стоять одна частица — «ham», «bir»): прилагательное + существительное, существительное + глагол, подлежащее + сказуемое, наречие + глагол, существительное + существительное. Часть речи определяется по трём источникам: глагольные окончания; часть речи выровненного английского слова, перенесённая на узбекскую основу (проекция разметки, Yarowsky et al., 2001); закрытые списки слов платформы. Падежное окончание управления сохраняется в модели (<em>uyga kirmoq</em>, <em>o‘rnidan turmoq</em>).',
        'Исключения раздела 1 применяются автоматически: парные и повторные слова (<em>yonma-yon</em>, <em>ota-ona</em>) и конструкции «деепричастие + вспомогательный глагол» (<em>tutib turmoq</em>, <em>qila olmoq</em>, <em>ko‘tara tushmoq</em>) коллокациями не считаются.',
        'Эквивалент каждой коллокации в переводе находится методом раздела 5 во всех её употреблениях и упорядочивается по частоте. Меры ассоциации внутри корпуса даны на странице «Статистика» для сравнения мер и не служат основанием для статуса.',
    ],
    'm_stat_title': '8. Статистика опорного корпуса',
    'm_stat': [
        'Поскольку художественный корпус мал, статус определяется мерами большого опорного корпуса, а не цифрами исследуемого корпуса (Bernardini, 2007). Для английских сочетаний — Британский национальный корпус (BNC); для узбекских — Национальный корпус узбекского языка или uzWaC (выбор обосновывается во II главе).',
        'Исходные параметры: единица счёта — лемма; не менее 5 употреблений в опорном корпусе; основная мера — logDice (Rychlý, 2008); MI только вместе с частотным фильтром; t-score только как показатель надёжности (Gablasova et al., 2017); частота на миллион слов. Пороговые значения заранее не задаются, а калибруются на размеченной вручную выборке.',
        'Расчёт по опорному корпусу — следующий этап. Значения MI, t-score, logDice и G² на платформе вычислены внутри исследуемого корпуса; страница «Статистика» даёт их, чтобы сравнить, как меры упорядочивают одни и те же сочетания.',
    ],
    's_auto_title': '3. Как коллокации переданы в переводе',
    's_auto_note': 'Таблица вычислена автоматически по всем коллокациям корпуса (встретившимся не менее двух раз) и каждому их употреблению. Эквивалент находится пословным выравниванием (раздел 5 методологии) и всегда является собственным словом переводчика в книге.',
    's_auto_cols': '«Эквивалент найден» — доля употреблений, для которых в переводе найден эквивалент; в остальных переводчик передал мысль описательно, опустил её или выравнивание не нашло надёжной связи. Доли «одним словом» и «сочетанием слов» считаются от употреблений с эквивалентом и различаются по числу знаменательных слов в эквиваленте.',
    's_dir_head': ['Направление', 'Модель', 'Коллокаций', 'Употреблений', 'Эквивалент найден', 'Одним словом', 'Сочетанием слов'],
    's_dir_uz_src': 'Оригинал Чулпана (узбекский) → «Night and Day»',
    's_dir_en_src': 'Оригинал Хемингуэя (английский) → «Chol va dengiz»',
    's_dir_en_tgt': 'Перевод Форта (английский) → узбекский источник',
    's_dir_uz_tgt': 'Перевод Гафурова (узбекский) → английский источник',
    's_total': 'итого',
    's_top_head': ['Коллокация', 'Модель', 'Употреблений', 'Эквивалент найден', 'Основные эквиваленты в переводе (употреблений)'],
    's_top_title_s_dir_uz_src': 'Самые частые коллокации оригинала Чулпана и их эквиваленты в «Night and Day»',
    's_top_title_s_dir_en_src': 'Самые частые коллокации оригинала Хемингуэя и их эквиваленты в «Chol va dengiz»',
    's_assoc_title': '4. Сравнение мер ассоциации',
    's_assoc': 'Согласно параграфу 1.1, статус коллокации определяется мерами большого опорного корпуса. Значения этого раздела вычислены внутри исследуемого корпуса и отвечают на другой вопрос: как четыре меры — MI, t-score, logDice и логарифмическое правдоподобие (G², Dunning, 1993) — упорядочивают один и тот же набор сочетаний. O₁₁ — частота сочетания, R₁ и C₁ — частоты первого и последнего компонента в текстах этого языка, N — число токенов этого языка (Evert, 2008).',
    's_meas_uz': 'Узбекские коллокации (оригинал Чулпана и перевод Гафурова)',
    's_meas_en': 'Английские коллокации (оригинал Хемингуэя и перевод Форта)',
    's_meas_n': '{types} коллокаций; N = {tokens} токенов.',
    's_meas_corr': 'Корреляция Спирмена (ρ) между ранжированиями мер',
    's_meas_profile': 'Первые 50 коллокаций по каждой мере',
    's_meas_profile_head': ['Мера', 'Средняя частота', 'Доля встретившихся дважды'],
    's_meas_top': 'Первые 8 коллокаций по каждой мере (в скобках — частота)',
    's_meas_top_head': ['Мера', 'Коллокации'],
    's_meas_reading': 'Как читать таблицы: MI поднимает сочетания, компоненты которых редки, но встречаются почти только вместе, поэтому его список открывают имена и термины, встретившиеся в корпусе дважды; t-score и G² предпочитают частые сочетания и дают порядок, близкий к простой частоте; logDice находится между ними. Это согласуется с тем, что говорится в литературе о MI и t-score (Gablasova et al., 2017). В малом корпусе MI опирается на два-три употребления, поэтому в диссертации он применяется только с частотным фильтром (методология, раздел 9).',
    's_ch3_title': '5. Данные для главы III',
    's_ch3': 'Таблицы разделов 3 и 4 служат основой количественного анализа главы III: они вычислены автоматически по всем коллокациям корпуса, а предложения, стоящие за каждой цифрой, видны на странице коллокации. Единицы, разобранные вручную в параграфе 1.1 диссертации, отмечены отдельно как выборка для качественного анализа.',
})

T['uz'].update({'s_by_pattern': 'Qoliplar bo‘yicha', 's_col_pattern': 'Qolip'})
T['en'].update({'s_by_pattern': 'By pattern', 's_col_pattern': 'Pattern'})
T['ru'].update({'s_by_pattern': 'По моделям', 's_col_pattern': 'Модель'})

T['uz'].update({
    's_freq': 'Chastota',
    's_meas_reading': 'Jadvallarni o‘qish. MI komponentlari kam uchraydigan, ammo deyarli faqat birga keladigan birikmalarni yuqoriga chiqaradi: uning ro‘yxati boshida korpusda ikki marta uchragan atamalar va kam qo‘llanadigan birikmalar turadi (<em>pattalik soliq</em>, <em>milch cow</em>). t-score butun ro‘yxat bo‘yicha chastotaga eng yaqin o‘lchov. G² ro‘yxatining boshida ham yuqori chastotali birikmalar turadi, lekin butun tartib bo‘yicha u MI va logDice bilan ko‘proq mos keladi. logDice ro‘yxatining boshida ham ikki marta uchragan birikmalar ko‘pchilikni tashkil etadi, ammo MI dan farqli ravishda u yerda chastotali birikmalar ham uchraydi. MI va t-score o‘rtasidagi bu farq adabiyotda ham qayd etilgan (Gablasova va boshq., 2017). Kichik korpusda MI ikki-uch uchrashga tayanadi, shuning uchun dissertatsiyada u faqat chastota filtri bilan qo‘llanadi (metodologiya, 9-band).',
})
T['en'].update({
    's_freq': 'Frequency',
    's_meas_reading': 'Reading the tables. MI promotes combinations whose components are rare but occur almost only together: its list opens with terms and uncommon combinations that occur twice in the corpus (<em>pattalik soliq</em>, <em>milch cow</em>). Over the whole list, t-score is the measure closest to frequency. The top of the G² list also consists of frequent combinations, but over the whole ranking G² agrees more with MI and logDice. Combinations occurring twice also make up most of the top of the logDice list, but unlike MI it also contains frequent ones there. This difference between MI and t-score is also noted in the literature (Gablasova et al., 2017). In a small corpus MI rests on two or three occurrences, which is why the dissertation uses it only with a frequency filter (methodology, section 9).',
})
T['ru'].update({
    's_freq': 'Частота',
    's_meas_reading': 'Как читать таблицы. MI поднимает сочетания, компоненты которых редки, но встречаются почти только вместе: его список открывают термины и редкие сочетания, встретившиеся в корпусе дважды (<em>pattalik soliq</em>, <em>milch cow</em>). По всему списку ближе всего к частоте t-score. В начале списка G² тоже стоят частые сочетания, но по всему ранжированию G² больше согласуется с MI и logDice. В начале списка logDice большинство также составляют сочетания, встретившиеся дважды, но, в отличие от MI, там есть и частые. Это различие между MI и t-score отмечается и в литературе (Gablasova et al., 2017). В малом корпусе MI опирается на два-три употребления, поэтому в диссертации он применяется только с частотным фильтром (методология, раздел 9).',
})

T['uz'].update({'m_unpaired': 'Tekislashda juft topilmagan {unpaired} ta gap (hunalign 1–0 va 0–1 bog‘lamlari) ham qidiruvga kiritilgan: ular izoh bilan ko‘rsatiladi va juftliklar soniga kirmaydi. Bunday gap tarjimaning o‘zi haqida ham dalil bo‘lishi mumkin — tushirib qoldirish, qo‘shish yoki gaplarni birlashtirish.'})
T['en'].update({'m_unpaired': 'The {unpaired} sentences for which the alignment found no counterpart (hunalign 1–0 and 0–1 beads) are included in the search: they are shown with a note and are not counted as pairs. Such a sentence can itself be evidence about the translation — an omission, an addition or a merger of sentences.'})
T['ru'].update({'m_unpaired': '{unpaired} предложений, для которых выравнивание не нашло соответствия (звенья hunalign 1–0 и 0–1), тоже включены в поиск: они показываются с пометой и не входят в число пар. Такое предложение само может свидетельствовать о переводе — опущении, добавлении или объединении предложений.'})

# ---- v3.2: second hunalign pass with a word list learnt from the word alignment; new spot checks
T['uz'].update({
    'm_align': 'Juftliklar avtomatik tekislangan. Ikki kitob gaplari hunalign dasturi (Varga va boshq., 2007) bilan ikki o‘tishda tekislandi: dastur gap uzunligi modelini (Gale va Church, 1993) leksik dalil bilan birlashtiradi. Birinchi o‘tishda leksik dalil sifatida ikkala kitobda bir xil yoziladigan nomlar va sonlar olindi. Birinchi o‘tish juftliklari so‘z darajasida tekislangach (5-band), butun korpus bo‘yicha ko‘p marta va barqaror bog‘langan 1 114 ta so‘z juftidan lug‘at tuzildi va ikkinchi o‘tish shu lug‘at bilan bajarildi. 1.1-paragrafda tahlil qilingan juftliklar va oldingi tekislashning tayanch nuqtalari qo‘zg‘almas nuqta sifatida saqlandi, shuning uchun xato ikki qo‘zg‘almas nuqta orasidan chiqmaydi. Juftlik maqomlari: «avtomatik — ikki usul mos» (dastlabki uzunlik va sahifa usuli ham shu gaplarni bir juftlikka qo‘ygan) — {auto_good}; «avtomatik — faqat hunalign» — {auto_one}; «avtomatik — tayanch nuqta» — {auto_pin}; 1.1-paragrafda qo‘lda tahlil qilingan — {confirmed}. Sun’iy intellekt yordamida bajarilgan tanlab tekshiruvda (14.10.2026) ikki o‘tish natijasi farq qilgan 30 ta tasodifiy joyning 22 tasida ikkinchi o‘tish to‘g‘riroq, 6 tasida birinchisi to‘g‘riroq chiqdi, 2 tasida farq yo‘q; ikkinchi o‘tishdan olingan 40 ta tasodifiy juftlikning 39 tasi to‘liq, 1 tasi qisman mos keldi. Tanlov kichik: bu natija noto‘g‘ri juftliklar ulushi 95 % ishonch bilan 7,5 foizdan kam ekanini bildiradi.',
    'm_walign_check': 'Sun’iy intellekt yordamida bajarilgan tanlab tekshiruvda (14.10.2026; platforma ko‘rsatgan 50 ta tasodifiy ekvivalent, 25 tasi o‘zbekcha va 25 tasi inglizcha so‘rov so‘zi uchun) 43 tasi to‘g‘ri, 2 tasi qisman to‘g‘ri, 5 tasi noto‘g‘ri chiqdi. Xatolar asosan ma’nosi kuchsiz fe’llarda (<em>qilmoq</em>, <em>demoq</em>) va ko‘chma birikma ichidagi so‘zda (<em>quloq solmoq</em>) uchradi. Ekvivalent butun korpus bo‘yicha o‘zbekcha mustaqil so‘zlarning 30,7 foizi va inglizcha mustaqil so‘zlarning 41,2 foizi uchun topiladi: chegaralar aniqlikni qamrovdan ustun qo‘yish uchun qat’iy tanlangan.',
})
T['en'].update({
    'm_align': 'The pairs are aligned automatically. The sentences of both books were aligned with hunalign (Varga et al., 2007) in two passes; the program combines the sentence-length model (Gale & Church, 1993) with lexical evidence. In the first pass the lexical evidence was names and numbers written the same in both books. After the pairs of the first pass had been word-aligned (section 5), a word list of 1,114 word pairs that are linked often and consistently across the corpus was compiled, and the second pass was run with this list. The pairs analysed in paragraph 1.1 and the pins of the earlier alignment were kept as fixed points, so an error cannot run past a fixed point. Statuses: “automatic — two methods agree” (the initial length-and-page method also put these sentences into one pair) — {auto_good}; “automatic — hunalign only” — {auto_one}; “automatic — pin” — {auto_pin}; analysed by hand in paragraph 1.1 — {confirmed}. In an AI-assisted spot check (14.10.2026), at 30 random places where the two passes differ the second pass was better at 22, the first at 6, and there was no difference at 2; of 40 random pairs of the second pass, 39 matched fully and 1 partly. The sample is small: this result means that the share of wrong pairs is below 7.5 per cent with 95 per cent confidence.',
    'm_walign_check': 'In an AI-assisted spot check (14.10.2026; 50 random equivalents shown by the platform, 25 for Uzbek and 25 for English query words), 43 were correct, 2 partly correct and 5 wrong. The errors mostly concern semantically light verbs (<em>qilmoq</em>, <em>demoq</em>) and a word inside an idiom (<em>quloq solmoq</em>). Across the whole corpus an equivalent is found for 30.7 per cent of Uzbek content words and 41.2 per cent of English content words: the thresholds are strict on purpose, to put precision before coverage.',
})
T['ru'].update({
    'm_align': 'Пары выровнены автоматически. Предложения обеих книг выровнены программой hunalign (Varga et al., 2007) в два прохода; программа объединяет модель длины предложений (Gale & Church, 1993) с лексическими данными. В первом проходе лексическими данными служили имена и числа, одинаково записанные в обеих книгах. После пословного выравнивания пар первого прохода (раздел 5) был составлен список из 1 114 пар слов, часто и устойчиво связанных по всему корпусу, и второй проход выполнен с этим списком. Пары, разобранные в параграфе 1.1, и якоря прежнего выравнивания сохранены как неподвижные точки, поэтому ошибка не выходит за пределы участка между ними. Статусы: «автоматически — оба метода совпали» (исходный метод по длине и страницам тоже объединил эти предложения в одну пару) — {auto_good}; «автоматически — только hunalign» — {auto_one}; «автоматически — якорь» — {auto_pin}; разобрано вручную в параграфе 1.1 — {confirmed}. При выборочной проверке с помощью ИИ (14.10.2026) в 30 случайных местах, где проходы расходятся, второй проход оказался точнее в 22, первый — в 6, в 2 различия нет; из 40 случайных пар второго прохода 39 совпали полностью и 1 частично. Выборка мала: этот результат означает, что доля ошибочных пар ниже 7,5 процента с доверием 95 процентов.',
    'm_walign_check': 'При выборочной проверке с помощью ИИ (14.10.2026; 50 случайных эквивалентов, показанных платформой, — 25 для узбекских и 25 для английских слов запроса) 43 оказались верными, 2 — частично верными, 5 — неверными. Ошибки касаются в основном семантически слабых глаголов (<em>qilmoq</em>, <em>demoq</em>) и слова внутри идиомы (<em>quloq solmoq</em>). По всему корпусу эквивалент находится для 30,7 процента узбекских и 41,2 процента английских знаменательных слов: пороги выбраны строгими, чтобы точность стояла выше полноты.',
})
for _l in ('uz', 'en', 'ru'):
    T[_l]['m_walign'] = T[_l]['m_walign'][:3] + [T[_l]['m_walign_check']]

# v3.5: the corpus dictionary is section 7; the sections after it move down by one
T['uz']['about_what'] = T['uz']['about_what'] + ['Tarjimonlar qo‘llagan so‘zlardan avtomatik tuzilgan o‘zbekcha–inglizcha va inglizcha–o‘zbekcha korpus lug‘atini beradi: har bir tarjima soni va kitobdagi misoli bilan.']
T['en']['about_what'] = T['en']['about_what'] + ['It offers an Uzbek–English and English–Uzbek corpus dictionary built automatically from the words the translators used: every translation with its count and an example from the book.']
T['ru']['about_what'] = T['ru']['about_what'] + ['Он предлагает узбекско-английский и англо-узбекский корпусный словарь, автоматически построенный по словам переводчиков: каждый перевод с частотой и примером из книги.']
T['uz'].update({
    'm_dict_title': '7. Korpus lug‘ati',
    'm_dict': [
        '«Lug‘at» bo‘limidagi o‘zbekcha–inglizcha va inglizcha–o‘zbekcha lug‘at bosma lug‘atdan ham, mashina tarjimasidan ham olinmagan: har bir tarjima — ikki kitob tarjimonlari shu so‘z o‘rnida qo‘llagan so‘z. Lug‘at 5-banddagi so‘z tekislashidan avtomatik tuziladi.',
        'O‘zbekcha so‘z shakllari lug‘at shakliga keltiriladi. Fe’l shakli o‘zak va -moq ko‘rinishida beriladi (dedi, degan, deydi → demoq); o‘zak platformaning fe’llar ro‘yxatida bo‘lishi yoki matnlarda bir necha fe’l qo‘shimchasi bilan uchrashi kerak. Boshqa so‘zlarda kelishik, egalik va ko‘plik qo‘shimchalari olib tashlanadi, ammo qolgan asos matnlarda boshqa qo‘shimchalar bilan ham uchrashi shart (xotini → xotin, yuragi → yurak, ko‘ngli → ko‘ngil). Ham fe’l, ham ot oxirida kela oladigan qo‘shimcha (-di, -gan, -ar, -sa) fe’l deb faqat tekislangan inglizcha so‘z fe’l bo‘lganda o‘qiladi: oldi «took» → olmoq, oldida «in front of» → oldi. Chiziqcha bilan yozilgan so‘z butunligicha olinadi (qah-qah, tez-tez, co-wife).',
        'Tarjima lug‘atga kiradi, agar juftlik korpusda kamida 3 marta bog‘langan bo‘lsa, bosh so‘z bog‘lanishlarining kamida 3 foizini tashkil etsa va ikki tomonlama bog‘liq bo‘lsa: Dice = 2n / (bosh so‘z bog‘lanishlari + tarjima bog‘lanishlari) ≥ 0,05. Oxirgi shart juda ko‘p uchraydigan so‘zning (demoq, kelmoq, now) hamma so‘zga «tarjima» bo‘lib chiqishiga yo‘l qo‘ymaydi. Grammatik ravish (never, here, very; hech, juda) sifat va ravishdan boshqa so‘zga, yordamchi fe’l (have, make; qilmoq, bo‘lmoq) fe’ldan boshqa so‘zga tarjima sifatida berilmaydi, teskari yo‘nalishda ham: bunday bog‘lanish so‘zga emas, birikmaga tegishli (ko‘nglim bormaydi ↔ I would never, bu yerda ↔ here). Tarjimalar n · Dice bo‘yicha tartiblanadi; kishi va joy nomlari kirmaydi. Har bir tarjimaga kitobdan bitta misol gap juftligi beriladi: avval 1.1-paragrafda tahlil qilingan juftliklar, keyin ikkala tekislash o‘tishi mos kelgan va hunalign bahosi past bo‘lmagan (kamida 0,3) juftliklar tanlanadi.',
        'Lug‘atda {uz} ta o‘zbekcha va {en} ta inglizcha bosh so‘z bor. U shu ikki tarjimonning tanlovini ko‘rsatadi, so‘zning umumiy tildagi barcha ma’nolarini emas: masalan, ko‘ngil so‘zi uchun «heart», «soul» va «calm» chiqadi, oxirgisi ko‘nglini tinchitmoq birikmasidan.',
        'Sun’iy intellekt yordamida bajarilgan tanlab tekshiruvda (14.10.2026; lug‘atning ikki qismidan 50 ta tasodifiy tarjima, har biri lug‘atdagi misoli bilan) 39 tasi to‘g‘ri, 6 tasi qisman to‘g‘ri, 5 tasi noto‘g‘ri chiqdi. Qisman to‘g‘ri tarjimalarning ko‘pi birikma ichidagi so‘zlar (nazar tashlamoq ↔ look, ovoz chiqarib ↔ aloud): so‘z darajasidagi tekislash birikmani bir butun deb ko‘rmaydi, shuning uchun lug‘at sahifasida har bir so‘zning yonida u qatnashgan kollokatsiya nomzodlari ham beriladi. Noto‘g‘ri tarjimalar tarjimon gapni boshqacha qurgan joylarda qo‘shni so‘z bog‘langanidan kelib chiqqan (blue-eyed beauty ↔ moviy ko‘zli dilbar: beauty ↔ ko‘zli). Bu tadqiqotchi tekshiruvi emas; lug‘at tarjimalari inson tekshiruvining alohida vazifasi (statistika, 7-bo‘lim).',
    ],
    'm_dict_limit': 'Korpus lug‘ati avtomatik tuzilgan. Lemmalashtirish qoidalarga tayangani uchun ayrim bosh so‘z qo‘shimchasi bilan qolishi (yer-suvi), so‘z noto‘g‘ri o‘zakka keltirilishi (qursin → qurmoq) yoki omonimlar bitta bosh so‘zga tushishi mumkin (yosh «young» va yosh «tear»). Kam uchraydigan so‘zlarning tarjimasi kam misolga tayanadi.',
})
T['en'].update({
    'm_dict_title': '7. Corpus dictionary',
    'm_dict': [
        'The Uzbek–English and English–Uzbek dictionary of the “Dictionary” section is taken neither from a printed dictionary nor from machine translation: every translation is a word the translators of the two books used for this word. It is built automatically from the word alignment of section 5.',
        'Uzbek word forms are brought to a dictionary form. A verb form is given as stem + -moq (dedi, degan, deydi → demoq); the stem must be in the platform’s verb list or occur in the texts with several verb endings. In other words case, possessive and plural endings are removed, but the base that remains must itself occur in the texts with other endings (xotini → xotin, yuragi → yurak, ko‘ngli → ko‘ngil). An ending that can close both a verb and a noun (-di, -gan, -ar, -sa) is read as a verb ending only when the aligned English word is a verb: oldi “took” → olmoq, oldida “in front of” → oldi. A hyphenated word is kept whole (qah-qah, tez-tez, co-wife).',
        'A translation is included if the pair is linked at least 3 times in the corpus, makes up at least 3 per cent of the links of the headword and is associated in both directions: Dice = 2n / (links of the headword + links of the translation) ≥ 0.05. The last condition keeps a very frequent word (demoq, kelmoq, now) from turning up as the “translation” of everything. A grammatical adverb (never, here, very; hech, juda) is not given as the translation of a word that is not an adjective or an adverb, nor a light verb (have, make; qilmoq, bo‘lmoq) as the translation of a word that is not a verb, and the other way round: such a link belongs to a combination, not to the word (ko‘nglim bormaydi ↔ I would never, bu yerda ↔ here). Translations are ordered by n · Dice; names of persons and places are left out. Each translation has one example sentence pair from the book: the pairs analysed in paragraph 1.1 first, then pairs on which both alignment passes agree and whose hunalign score is not low (at least 0.3).',
        'The dictionary has {uz} Uzbek and {en} English headwords. It shows the choices of these two translators, not every meaning the word has in the language: for ko‘ngil it gives “heart”, “soul” and “calm”, the last from the combination ko‘nglini tinchitmoq.',
        'In an AI-assisted spot check (14.10.2026; 50 random translations from the two parts of the dictionary, each with its example in the dictionary) 39 were correct, 6 partly correct and 5 wrong. Most of the partly correct ones are words inside a combination (nazar tashlamoq ↔ look, ovoz chiqarib ↔ aloud): word alignment does not see a combination as a whole, which is why the dictionary page lists the collocation candidates of each word next to it. The wrong ones come from places where the translator built the sentence differently and a neighbouring word was linked (blue-eyed beauty ↔ moviy ko‘zli dilbar: beauty ↔ ko‘zli). This is not the researcher’s evaluation; the dictionary translations are a separate task of the human evaluation (statistics, section 7).',
    ],
    'm_dict_limit': 'The corpus dictionary is built automatically. As the lemmatisation is rule-based, a headword may keep an ending (yer-suvi), be brought to a wrong stem (qursin → qurmoq), or homonyms may fall under one headword (yosh “young” and yosh “tear”). The translations of rare words rest on few examples.',
})
T['ru'].update({
    'm_dict_title': '7. Корпусный словарь',
    'm_dict': [
        'Узбекско-английский и англо-узбекский словарь раздела «Словарь» не взят ни из печатного словаря, ни из машинного перевода: каждый перевод — слово, которым переводчики двух книг передали это слово. Он автоматически строится по пословному выравниванию из раздела 5.',
        'Узбекские словоформы приводятся к словарной форме. Глагольная форма даётся как основа + -moq (dedi, degan, deydi → demoq); основа должна быть в списке глаголов платформы или встречаться в текстах с несколькими глагольными окончаниями. У остальных слов отсекаются падежные, притяжательные окончания и окончание множественного числа, но оставшаяся основа сама должна встречаться в текстах с другими окончаниями (xotini → xotin, yuragi → yurak, ko‘ngli → ko‘ngil). Окончание, которое может закрывать и глагол, и имя (-di, -gan, -ar, -sa), читается как глагольное, только если выровненное английское слово — глагол: oldi «took» → olmoq, oldida «in front of» → oldi. Слово через дефис берётся целиком (qah-qah, tez-tez, co-wife).',
        'Перевод включается, если пара связана в корпусе не менее 3 раз, составляет не менее 3 процентов связей заглавного слова и связана в обе стороны: Dice = 2n / (связи заглавного слова + связи перевода) ≥ 0,05. Последнее условие не даёт очень частому слову (demoq, kelmoq, now) оказаться «переводом» всего. Грамматическое наречие (never, here, very; hech, juda) не даётся как перевод слова, которое не является прилагательным или наречием, а лёгкий глагол (have, make; qilmoq, bo‘lmoq) — как перевод не глагола, и наоборот: такая связь относится к сочетанию, а не к слову (ko‘nglim bormaydi ↔ I would never, bu yerda ↔ here). Переводы упорядочены по n · Dice; имена людей и названия мест не включаются. Для каждого перевода дана одна пара предложений из книги: сначала пары, разобранные в параграфе 1.1, затем пары, на которых совпали оба прохода выравнивания и оценка hunalign не низкая (не меньше 0,3).',
        'В словаре {uz} узбекских и {en} английских заглавных слов. Он показывает выбор этих двух переводчиков, а не все значения слова в языке: для ko‘ngil даются «heart», «soul» и «calm», последнее — из сочетания ko‘nglini tinchitmoq.',
        'При выборочной проверке с помощью ИИ (14.10.2026; 50 случайных переводов из двух частей словаря, каждый со своим примером в словаре) 39 оказались верными, 6 — частично верными, 5 — неверными. Частично верные — в основном слова внутри сочетания (nazar tashlamoq ↔ look, ovoz chiqarib ↔ aloud): пословное выравнивание не видит сочетание как целое, поэтому на странице словаря рядом с каждым словом даны кандидаты в коллокации с ним. Неверные возникли там, где переводчик построил предложение иначе и связано соседнее слово (blue-eyed beauty ↔ moviy ko‘zli dilbar: beauty ↔ ko‘zli). Она не заменяет оценку исследователя: переводы словаря — отдельное задание экспертной оценки (статистика, раздел 7).',
    ],
    'm_dict_limit': 'Корпусный словарь составлен автоматически. Поскольку лемматизация основана на правилах, заглавное слово может сохранить окончание (yer-suvi), получить неверную основу (qursin → qurmoq) или омонимы могут попасть в одно заглавное слово (yosh «young» и yosh «tear»). Переводы редких слов опираются на немногие примеры.',
})
for _l in ('uz', 'en', 'ru'):
    for _k, _n in (('m_cand_title', 8), ('m_stat_title', 9), ('m_rel_title', 10), ('m_limits_title', 11)):
        T[_l][_k] = re.sub(r'^\d+\.', '%d.' % _n, T[_l][_k])
    T[_l]['m_limits'] = T[_l]['m_limits'] + [T[_l]['m_dict_limit']]


# ---------------------------------------------------------------------------------------------
# v3.6: tests for chapter III, the open reference corpus, comparable texts, human evaluation
# ---------------------------------------------------------------------------------------------
T['uz'].update({
    's_auto_title': '3. Kollokatsiya nomzodlarining tarjimada berilishi',
    's_assoc_title': '4. Assotsiatsiya o‘lchovlarini qiyoslash (tadqiqot korpusi ichida)',
    's_test_title': 'Yo‘nalishlar orasidagi farqning statistik testi',
    's_test_note': 'Jadvaldagi har bir qator — kontingensiya jadvali bo‘yicha Pirson xi-kvadrati va log-likelihood (G², Dunning, 1993) testi, ta’sir kattaligi — Kramer V (Cramér, 1946). Uchrashlar nomzod turlari ichida guruhlanadi (bir nomzodning bir necha uchrashi mustaqil emas), shuning uchun p qiymatlari taxminiy; ta’sir kattaligi va «tur darajasida» qatori (har bir nomzod bir marta: uchrashlarining kamida yarmida muqobil topilganmi) ishonchliroq ko‘rsatkich.',
    's_test_head': ['Taqqoslash', 'n', 'χ² (df)', 'G²', 'p', 'Kramer V', 'Imkoniyatlar nisbati (95 % oraliq)'],
    's_t_eq4': 'Muqobil topilgan ulushi: to‘rt yo‘nalish',
    's_t_eq2': 'Muqobil topilgan ulushi: Cho‘lpon asliyati → Fort va Hemingway asliyati → G‘ofurov',
    's_t_eq2t': 'Xuddi shu, tur darajasida',
    's_t_sm4': 'Bitta so‘z yoki so‘z birikmasi bilan berilish: to‘rt yo‘nalish',
    's_t_sm2': 'Bitta so‘z yoki so‘z birikmasi: Cho‘lpon → Fort va Hemingway → G‘ofurov',
    's_ref_title': '5. Tayanch korpus: inglizcha nomzodlarning tildagi odatiyligi',
    's_ref_lead': '1.1.4-bandga ko‘ra kollokatsiya maqomi tayanch korpusdagi chastota va assotsiatsiya bilan belgilanadi. BNC platformaga ulanguncha ochiq tarqatiladigan korpuslardan tayanch korpus tuzildi va u tadqiqot korpusidagi bilan bir xil usulda — spaCy (en_core_web_sm) sintaktik tahlili va bir xil bog‘lanish qoliplari bilan — sanaldi (scripts/build_reference_en.py).',
    's_ref_head': ['Qism', 'Tokenlar'],
    's_ref_cov': 'Inglizcha nomzodlar: {all}; tayanch korpusda uchraydi: {any}; kamida 5 marta (1.1.4-band, 3-jadval): {five}. Kamida 5 marta uchraganlarda tadqiqot korpusidagi va tayanch korpusdagi logDice o‘rtasidagi Spirmen korrelyatsiyasi: {rho}.',
    's_ref_top': 'Tayanch korpusda logDice eng yuqori bo‘lgan nomzodlar (tayanchda kamida 5 marta)',
    's_ref_top_head': ['Nomzod', 'Qolip', 'Korpusda', 'Tayanchda', 'logDice (tayanch)', 'MI (tayanch)'],
    's_ref_caveat': 'Cheklovlar: tayanch korpus ({tokens} token) BNC dan (100 mln so‘z) ancha kichik va asosan amerika ingliz tilidan iborat; Gutenberg qismi XIX asr va XX asr boshi nasri. Shuning uchun past chastotali birikmalar bu yerda «uchramaydi» bo‘lib chiqishi mumkin; maqom uchun chegaraviy logDice qiymati «Inson tekshiruvi» natijalarida kalibrlanadi. O‘zbekcha nomzodlar uchun tayanch korpus hali ulanmagan: skript tadqiqotchi bergan matn fayllari (masalan, Leipzig korpuslari yoki milliy korpusdan olingan matnlar) bilan ishlaydi.',
    's_cmp_title': '6. Teng (qiyosiy) matnlar: asliyat va tarjima tili',
    's_cmp_lead': 'Korpus har bir tilda bitta asliyat va bitta tarjima matnini o‘z ichiga oladi. Bu Bernardini (2007) tavsiflagan dizaynni — parallel, teng (qiyosiy) va tayanch korpusni birlashtirishni — qo‘llash imkonini beradi: bir tildagi asliyat va tarjima matnlari bir xil ko‘rsatkichlar bilan solishtiriladi (scripts/build_comparable_stats.py).',
    's_cmp_head': ['Matn', 'Tili', 'Tokenlar', 'STTR', 'Mustaqil so‘zlar ulushi', 'Nomzod uchrashi / 1 000 token'],
    's_cmp_en_head': ['Matn', 'Bog‘lanish qolipi uchrashlari / 1 000 token', 'Tayanch korpusda ≥ 5 marta', 'Tayanchda logDice ≥ 7', 'Matnda bir marta uchragan birikmalar'],
    's_cmp_tests_head': ['Ko‘rsatkich', 'Til', 'χ² (df)', 'p', 'Kramer V'],
    's_cmp_t_cand': 'Nomzod uchrashlari zichligi', 's_cmp_t_density': 'Mustaqil so‘zlar ulushi', 's_cmp_t_attested': 'Tayanchda ≥ 5 marta uchraydigan birikmalar ulushi',
    's_cmp_t_typical': 'Tayanchda logDice ≥ 7 bo‘lgan birikmalar ulushi', 's_cmp_t_once': 'Bir marta uchragan birikmalar ulushi',
    's_cmp_note': 'Tokenlar — juftlangan gaplardagi so‘z tekislashi tokenlari (1-bo‘limdagi izohga qarang). Ko‘rsatkichlar faqat bir til ichida, asliyat va tarjima o‘rtasida solishtiriladi: o‘zbek va ingliz tillarida so‘zning chegarasi va yordamchi so‘zlar ulushi turlicha. STTR — 1 000 tokenli ketma-ket bo‘laklardagi shakllar/tokenlar nisbatining o‘rtachasi (butun matnlarning TTR i uzunlik farqi tufayli qiyoslanmaydi). Ingliz tilida bog‘lanish qoliplarining barcha uchrashlari (bir marta uchraganlari ham) tayanch korpus bilan tekshirildi.',
    's_cmp_caveat': 'Talqin uchun ogohlantirish: har bir katakda bitta asar bor, shuning uchun asliyat va tarjima tili farqi muallif uslubi, janr va davr farqidan ajratilmaydi (masalan, Hemingway uslubidagi takrorlar). Natijalar gipoteza uchun asos bo‘ladi, umumlashma uchun esa har bir tilda bir nechta asliyat va tarjima matni kerak.',
    's_val_title': '7. Inson tekshiruvi natijalari',
    's_val_ready': 'Tanlanmalar tayyor: besh vazifa (gap juftliklari, so‘z muqobillari, o‘zbekcha va inglizcha kollokatsiya nomzodlari, lug‘at tarjimalari), har birida 50 birlikli o‘quv to‘plami va 200 birlikli asosiy tanlanma (qat’iy urug‘ {seed}). Baholar tadqiqotchi kabinetida qo‘yiladi; aniqlik, ishonch oralig‘i va Koen kappasi shu bo‘limda avtomatik chiqadi.',
    's_ch3_title': '8. III bob uchun ma’lumot',
    's_ch3': 'III bobdagi miqdoriy tahlil uchun 3–6-bo‘limlardagi jadvallar asos bo‘ladi: ular korpusdagi barcha nomzodlar bo‘yicha avtomatik hisoblangan, har bir raqam ortidagi gaplarni esa nomzod sahifasida ko‘rish mumkin. Qaysi nomzod kollokatsiya ekanini 1.1.4-banddagi qaror tartibi belgilaydi: lingvistik baho «Inson tekshiruvi» bo‘limida, statistik tasdiq tayanch korpusda.',
})
T['en'].update({
    's_auto_title': '3. How the collocation candidates are rendered in translation',
    's_assoc_title': '4. Comparing association measures (within the research corpus)',
    's_test_title': 'Significance of the differences between the directions',
    's_test_note': 'Each row is Pearson’s chi-square and the log-likelihood test (G², Dunning, 1993) on a contingency table; the effect size is Cramér’s V (Cramér, 1946). Occurrences are grouped within candidate types (several occurrences of one candidate are not independent), so the p-values are approximate; the effect size and the “type level” row (every candidate counted once: is an equivalent found in at least half of its occurrences?) are the more reliable figures.',
    's_test_head': ['Comparison', 'n', 'χ² (df)', 'G²', 'p', 'Cramér’s V', 'Odds ratio (95% interval)'],
    's_t_eq4': 'Share with an equivalent found: four directions',
    's_t_eq2': 'Share with an equivalent: Cho‘lpon original → Fort and Hemingway original → G‘ofurov',
    's_t_eq2t': 'The same, type level',
    's_t_sm4': 'Rendered by a single word or by a word combination: four directions',
    's_t_sm2': 'Single word or word combination: Cho‘lpon → Fort and Hemingway → G‘ofurov',
    's_ref_title': '5. Reference corpus: how usual the English candidates are in the language',
    's_ref_lead': 'By section 1.1.4 the status of a collocation is set by its frequency and association in a reference corpus. Until the BNC is connected to the platform, a reference corpus was assembled from openly distributed corpora and counted in the same way as the research corpus — with the spaCy parser (en_core_web_sm) and the same dependency patterns (scripts/build_reference_en.py).',
    's_ref_head': ['Part', 'Tokens'],
    's_ref_cov': 'English candidates: {all}; found in the reference corpus: {any}; at least 5 times (section 1.1.4, table 3): {five}. Spearman correlation of the logDice in the research corpus and in the reference corpus, over the candidates found at least 5 times: {rho}.',
    's_ref_top': 'Candidates with the highest logDice in the reference corpus (at least 5 times there)',
    's_ref_top_head': ['Candidate', 'Pattern', 'In the corpus', 'In the reference', 'logDice (reference)', 'MI (reference)'],
    's_ref_caveat': 'Limitations: the reference corpus ({tokens} tokens) is much smaller than the BNC (100 million words) and mostly American English; its Gutenberg part is 19th and early 20th century prose. Rare combinations may therefore come out as “not found”; the threshold of logDice for the status is calibrated on the results of the human evaluation. For the Uzbek candidates no reference corpus is connected yet: the script works with text files supplied by the researcher (for example the Leipzig corpora or texts taken from the national corpus).',
    's_cmp_title': '6. Comparable texts: original and translated language',
    's_cmp_lead': 'The corpus holds one original and one translated text in each language. This allows the design described by Bernardini (2007) — a parallel, a comparable and a reference corpus combined: the original and the translated text of a language are compared with the same measures (scripts/build_comparable_stats.py).',
    's_cmp_head': ['Text', 'Language', 'Tokens', 'STTR', 'Share of content words', 'Candidate occurrences / 1,000 tokens'],
    's_cmp_en_head': ['Text', 'Dependency-pattern occurrences / 1,000 tokens', 'At least 5 times in the reference', 'Reference logDice ≥ 7', 'Combinations occurring once in the text'],
    's_cmp_tests_head': ['Measure', 'Language', 'χ² (df)', 'p', 'Cramér’s V'],
    's_cmp_t_cand': 'Density of candidate occurrences', 's_cmp_t_density': 'Share of content words', 's_cmp_t_attested': 'Share of combinations found ≥ 5 times in the reference',
    's_cmp_t_typical': 'Share of combinations with reference logDice ≥ 7', 's_cmp_t_once': 'Share of combinations occurring once',
    's_cmp_note': 'Tokens are the word-alignment tokens of the paired sentences (see the note to section 1). The measures are compared only within a language, between the original and the translation: Uzbek and English differ in what counts as a word and in the share of function words. STTR is the mean form/token ratio of consecutive 1,000-token chunks (the TTR of whole texts is not comparable because of their different length). In English every occurrence of the dependency patterns (also those occurring once) was checked in the reference corpus.',
    's_cmp_caveat': 'A warning for interpretation: every cell holds one work, so the difference between original and translated language cannot be separated from the author’s style, the genre and the period (for example Hemingway’s repetitions). The results ground a hypothesis; a generalisation needs several original and translated texts in each language.',
    's_val_title': '7. Results of the human evaluation',
    's_val_ready': 'The samples are ready: five tasks (sentence pairs, word equivalents, Uzbek and English collocation candidates, dictionary translations), each with a training set of 50 units and a main sample of 200 (fixed seed {seed}). The judgements are made in the researcher’s area; precision, confidence intervals and Cohen’s kappa appear in this section automatically.',
    's_ch3_title': '8. Data for chapter III',
    's_ch3': 'The tables of sections 3–6 are the basis of the quantitative analysis in chapter III: they are computed automatically over all candidates of the corpus, and the sentences behind each figure can be seen on the candidate’s page. Which candidate is a collocation is decided by the procedure of section 1.1.4: the linguistic judgement in the human evaluation, the statistical confirmation in the reference corpus.',
})
T['ru'].update({
    's_auto_title': '3. Передача кандидатов в коллокации в переводе',
    's_assoc_title': '4. Сравнение мер ассоциации (внутри исследовательского корпуса)',
    's_test_title': 'Статистическая значимость различий между направлениями',
    's_test_note': 'Каждая строка — критерий хи-квадрат Пирсона и логарифмического правдоподобия (G², Dunning, 1993) по таблице сопряжённости; мера эффекта — V Крамера (Cramér, 1946). Употребления сгруппированы внутри типов кандидатов (несколько употреблений одного кандидата не независимы), поэтому значения p приблизительны; мера эффекта и строка «на уровне типов» (каждый кандидат учитывается один раз: найден ли эквивалент не менее чем в половине употреблений) надёжнее.',
    's_test_head': ['Сравнение', 'n', 'χ² (df)', 'G²', 'p', 'V Крамера', 'Отношение шансов (95%-й интервал)'],
    's_t_eq4': 'Доля с найденным эквивалентом: четыре направления',
    's_t_eq2': 'Доля с эквивалентом: оригинал Чулпана → Форт и оригинал Хемингуэя → Гафуров',
    's_t_eq2t': 'То же на уровне типов',
    's_t_sm4': 'Передача одним словом или сочетанием слов: четыре направления',
    's_t_sm2': 'Одно слово или сочетание: Чулпан → Форт и Хемингуэй → Гафуров',
    's_ref_title': '5. Опорный корпус: насколько обычны английские кандидаты в языке',
    's_ref_lead': 'По разделу 1.1.4 статус коллокации определяется её частотой и ассоциацией в опорном корпусе. Пока BNC не подключён к платформе, опорный корпус собран из открыто распространяемых корпусов и подсчитан тем же способом, что и исследовательский, — синтаксическим анализатором spaCy (en_core_web_sm) и теми же моделями связей (scripts/build_reference_en.py).',
    's_ref_head': ['Часть', 'Токены'],
    's_ref_cov': 'Английских кандидатов: {all}; встречаются в опорном корпусе: {any}; не менее 5 раз (раздел 1.1.4, таблица 3): {five}. Корреляция Спирмена между logDice в исследовательском и в опорном корпусе для кандидатов, встретившихся не менее 5 раз: {rho}.',
    's_ref_top': 'Кандидаты с наибольшим logDice в опорном корпусе (не менее 5 раз в нём)',
    's_ref_top_head': ['Кандидат', 'Модель', 'В корпусе', 'В опорном', 'logDice (опорный)', 'MI (опорный)'],
    's_ref_caveat': 'Ограничения: опорный корпус ({tokens} токенов) намного меньше BNC (100 млн слов) и в основном представляет американский английский; часть Gutenberg — проза XIX и начала XX века. Поэтому редкие сочетания могут оказаться «не найденными»; порог logDice для статуса калибруется по результатам экспертной проверки. Для узбекских кандидатов опорный корпус пока не подключён: скрипт работает с текстовыми файлами исследователя (например, корпусами Лейпцига или текстами из национального корпуса).',
    's_cmp_title': '6. Сопоставимые тексты: оригинальный и переводной язык',
    's_cmp_lead': 'Корпус содержит в каждом языке один оригинальный и один переводной текст. Это позволяет применить схему, описанную Бернардини (2007), — объединение параллельного, сопоставимого и опорного корпусов: оригинальный и переводной тексты одного языка сравниваются по одним и тем же показателям (scripts/build_comparable_stats.py).',
    's_cmp_head': ['Текст', 'Язык', 'Токены', 'STTR', 'Доля знаменательных слов', 'Употребления кандидатов / 1 000 токенов'],
    's_cmp_en_head': ['Текст', 'Употребления моделей связей / 1 000 токенов', 'Не менее 5 раз в опорном', 'logDice в опорном ≥ 7', 'Сочетания, встретившиеся в тексте один раз'],
    's_cmp_tests_head': ['Показатель', 'Язык', 'χ² (df)', 'p', 'V Крамера'],
    's_cmp_t_cand': 'Плотность употреблений кандидатов', 's_cmp_t_density': 'Доля знаменательных слов', 's_cmp_t_attested': 'Доля сочетаний, встречающихся в опорном ≥ 5 раз',
    's_cmp_t_typical': 'Доля сочетаний с logDice в опорном ≥ 7', 's_cmp_t_once': 'Доля сочетаний, встретившихся один раз',
    's_cmp_note': 'Токены — токены пословного выравнивания выровненных предложений (см. примечание к разделу 1). Показатели сравниваются только внутри одного языка, между оригиналом и переводом: в узбекском и английском по-разному определяются границы слова и доля служебных слов. STTR — среднее отношение форм к токенам по последовательным отрезкам в 1 000 токенов (TTR целых текстов несопоставим из-за разной длины). В английском все употребления моделей связей (и встретившиеся один раз) проверены по опорному корпусу.',
    's_cmp_caveat': 'Предупреждение для интерпретации: в каждой ячейке одно произведение, поэтому различие оригинального и переводного языка не отделяется от стиля автора, жанра и эпохи (например, повторов у Хемингуэя). Результаты дают основание для гипотезы; для обобщения нужны несколько оригинальных и переводных текстов в каждом языке.',
    's_val_title': '7. Результаты экспертной проверки',
    's_val_ready': 'Выборки готовы: пять задач (пары предложений, пословные эквиваленты, узбекские и английские кандидаты в коллокации, переводы словаря), в каждой обучающий набор из 50 единиц и основная выборка из 200 (фиксированное зерно {seed}). Оценки ставятся в кабинете исследователя; точность, доверительные интервалы и каппа Коэна появляются в этом разделе автоматически.',
    's_ch3_title': '8. Данные для главы III',
    's_ch3': 'Основой количественного анализа в главе III служат таблицы разделов 3–6: они вычислены автоматически по всем кандидатам корпуса, а предложения за каждой цифрой можно увидеть на странице кандидата. Что является коллокацией, определяет порядок решений раздела 1.1.4: лингвистическая оценка — в экспертной проверке, статистическое подтверждение — в опорном корпусе.',
})

# v3.6: the automatically extracted units are "collocation candidates" (1.1.4): their status is set by the
# linguistic judgement and by the reference corpus, so the statistics and methodology texts name them so.
T['uz'].update({
    'm_equiv_title': '6. Kollokatsiya nomzodlarini ajratish',
    'm_equiv': 'Kollokatsiya nomzodlari har ikki tilda korpusning o‘zidan ajratiladi va kamida ikki marta uchraganlari olinadi (Bernardini, 2007, b. 8 dagi chastota > 1 chegarasi bilan bir xil). Nomzod hali kollokatsiya degani emas: uning toifasini 1.1.4-banddagi lingvistik shartlar, maqomini tayanch korpusdagi statistik tasdiq belgilaydi (9- va 10-bandlar).',
    's_auto_note': 'Jadval korpusdagi barcha kollokatsiya nomzodlari (kamida 2 marta uchraganlar) va ularning har bir uchrashi bo‘yicha avtomatik hisoblangan. Ekvivalent metodologiyaning 5-bandidagi so‘z darajasidagi tekislash bilan topiladi va har doim tarjimonning kitobdagi so‘zidir.',
    's_top_title_s_dir_uz_src': 'Cho‘lpon asliyatida eng ko‘p uchragan nomzodlar va ularning «Night and Day»dagi ekvivalentlari',
    's_top_title_s_dir_en_src': 'Hemingway asliyatida eng ko‘p uchragan nomzodlar va ularning «Chol va dengiz»dagi ekvivalentlari',
    's_meas_uz': 'O‘zbekcha nomzodlar (Cho‘lpon asliyati va G‘ofurov tarjimasi)',
    's_meas_en': 'Inglizcha nomzodlar (Hemingway asliyati va Fort tarjimasi)',
    's_meas_n': '{types} ta nomzod; N = {tokens} token.',
    's_meas_profile': 'Har bir o‘lchov bo‘yicha birinchi 50 nomzod',
    's_meas_top': 'Har bir o‘lchov bo‘yicha birinchi 8 nomzod (qavs ichida — uchrash soni)',
    's_assoc': 'Nomzodning maqomi 1.1-paragrafga ko‘ra katta tayanch korpusdagi ko‘rsatkichlar bilan belgilanadi (5-bo‘lim). Bu bo‘limdagi qiymatlar tadqiqot korpusining o‘zida hisoblangan va boshqa savolga javob beradi: bir xil birikmalar to‘plamini to‘rt o‘lchov — MI, t-score, logDice va log-likelihood (G², Dunning, 1993) — qanday tartiblaydi. O₁₁ — birikmaning uchrash soni, R₁ va C₁ — birinchi va oxirgi komponentning shu tildagi matnlarda uchrash soni, N — shu tildagi tokenlar soni (Evert, 2008).',
})
T['en'].update({
    'm_equiv_title': '6. Extraction of collocation candidates',
    'm_equiv': 'Collocation candidates are extracted from the corpus itself in both languages; those occurring at least twice are kept (the same as the frequency > 1 threshold of Bernardini, 2007, p. 8). A candidate is not yet a collocation: its category is set by the linguistic conditions of section 1.1.4, its status by the statistical confirmation in a reference corpus (sections 9 and 10).',
    's_auto_note': 'The table is computed automatically over all collocation candidates of the corpus (those occurring at least twice) and every one of their occurrences. The equivalent is found with the word alignment of section 5 of the methodology and is always the translator’s own word in the book.',
    's_top_title_s_dir_uz_src': 'The most frequent candidates of Cho‘lpon’s original and their equivalents in «Night and Day»',
    's_top_title_s_dir_en_src': 'The most frequent candidates of Hemingway’s original and their equivalents in «Chol va dengiz»',
    's_meas_uz': 'Uzbek candidates (Cho‘lpon’s original and G‘ofurov’s translation)',
    's_meas_en': 'English candidates (Hemingway’s original and Fort’s translation)',
    's_meas_n': '{types} candidates; N = {tokens} tokens.',
    's_meas_profile': 'The first 50 candidates by each measure',
    's_meas_top': 'The first 8 candidates by each measure (frequency in brackets)',
    's_assoc': 'According to paragraph 1.1, the status of a candidate is decided by the measures of a large reference corpus (section 5). The values in this section are computed within the research corpus and answer another question: how the four measures — MI, t-score, logDice and log-likelihood (G², Dunning, 1993) — order the same set of combinations. O₁₁ is the frequency of the combination, R₁ and C₁ the frequencies of its first and last component in the texts of that language, N the number of tokens of that language (Evert, 2008).',
})
T['ru'].update({
    'm_equiv_title': '6. Извлечение кандидатов в коллокации',
    'm_equiv': 'Кандидаты в коллокации извлекаются из самого корпуса на обоих языках; сохраняются встретившиеся не менее двух раз (так же, как порог частоты > 1 у Bernardini, 2007, с. 8). Кандидат ещё не коллокация: его категорию определяют лингвистические условия раздела 1.1.4, статус — статистическое подтверждение в опорном корпусе (разделы 9 и 10).',
    's_auto_note': 'Таблица вычислена автоматически по всем кандидатам в коллокации (встретившимся не менее двух раз) и каждому их употреблению. Эквивалент находится пословным выравниванием (раздел 5 методологии) и всегда является собственным словом переводчика в книге.',
    's_top_title_s_dir_uz_src': 'Самые частые кандидаты оригинала Чулпана и их эквиваленты в «Night and Day»',
    's_top_title_s_dir_en_src': 'Самые частые кандидаты оригинала Хемингуэя и их эквиваленты в «Chol va dengiz»',
    's_meas_uz': 'Узбекские кандидаты (оригинал Чулпана и перевод Гафурова)',
    's_meas_en': 'Английские кандидаты (оригинал Хемингуэя и перевод Форта)',
    's_meas_n': '{types} кандидатов; N = {tokens} токенов.',
    's_meas_profile': 'Первые 50 кандидатов по каждой мере',
    's_meas_top': 'Первые 8 кандидатов по каждой мере (в скобках — частота)',
    's_assoc': 'Согласно параграфу 1.1, статус кандидата определяется мерами большого опорного корпуса (раздел 5). Значения этого раздела вычислены внутри исследуемого корпуса и отвечают на другой вопрос: как четыре меры — MI, t-score, logDice и логарифмическое правдоподобие (G², Dunning, 1993) — упорядочивают один и тот же набор сочетаний. O₁₁ — частота сочетания, R₁ и C₁ — частоты его первого и последнего компонента в текстах этого языка, N — число токенов этого языка (Evert, 2008).',
})
for _l, (a, b) in {'uz': ('Kollokatsiyalar', 'Nomzodlar'), 'en': ('Collocations', 'Candidates'), 'ru': ('Коллокаций', 'Кандидатов')}.items():
    T[_l]['s_dir_head'] = [b if x == a else x for x in T[_l]['s_dir_head']]
for _l, (a, b) in {'uz': ('Kollokatsiya', 'Nomzod'), 'en': ('Collocation', 'Candidate'), 'ru': ('Коллокация', 'Кандидат')}.items():
    T[_l]['s_top_head'] = [b if x == a else x for x in T[_l]['s_top_head']]
for _l, (a, b) in {'uz': ('Kollokatsiyalar', 'Nomzodlar'), 'en': ('Collocations', 'Candidates'), 'ru': ('Коллокации', 'Кандидаты')}.items():
    T[_l]['s_meas_top_head'] = [b if x == a else x for x in T[_l]['s_meas_top_head']]

# v3.6: methodology texts on the reference corpus, the comparable design and the human evaluation
T['uz'].update({
    'm_corpus': 'Korpus ikki juftlikdan iborat: Cho‘lponning «Kecha va kunduz» romani va uning Christopher Fort qilgan inglizcha tarjimasi «Night and Day» (o‘zbekchadan inglizchaga); E. Hemingwayning «The Old Man and the Sea» qissasi va uning Ibrohim G‘ofurov qilgan o‘zbekcha tarjimasi «Chol va dengiz» (inglizchadan o‘zbekchaga). Parallel tahlilda har bir asar faqat o‘z tarjimasi bilan qiyoslanadi. Shu bilan birga har bir tilda bitta asliyat va bitta tarjima matni bor, shuning uchun korpus teng (qiyosiy) korpus sifatida ham ishlaydi: bir tildagi asliyat va tarjima matnlari bir xil ko‘rsatkichlar bilan solishtiriladi (Bernardini, 2007; «Statistika», 6-bo‘lim).',
    'm_stat': [
        'Badiiy korpus kichik bo‘lgani uchun maqom tadqiqot korpusidagi raqamlar bilan emas, katta tayanch korpusdagi ko‘rsatkichlar bilan belgilanadi (Bernardini, 2007). Rejada inglizcha birikmalar uchun Britaniya milliy korpusi (BNC), o‘zbekcha birikmalar uchun O‘zbek tili milliy korpusi yoki uzWaC (tanlov II bobda asoslanadi).',
        'Dastlabki parametrlar: hisob birligi — lemma; tayanch korpusda kamida 5 marta uchrash; asosiy o‘lchov — logDice (Rychlý, 2008); MI faqat chastota filtri bilan; t-score faqat ishonchlilik ko‘rsatkichi sifatida (Gablasova va boshq., 2017); chastota million so‘zga nisbatan. Chegaraviy qiymatlar oldindan belgilanmaydi, qo‘lda annotatsiya qilingan to‘plamda kalibrlanadi.',
        'BNC ulanguncha inglizcha nomzodlar uchun ochiq tarqatiladigan korpuslardan tuzilgan tayanch korpus ishlatiladi: Brown korpusi (Francis va Kučera, 1979), MASC (Ide va boshq., 2010) va NLTK dagi Project Gutenberg tanlovining nasriy badiiy qismi (Bird va boshq., 2009) — jami {ref_tokens} token. U tadqiqot korpusidagi bilan bir xil usulda — spaCy sintaktik tahlili va bir xil bog‘lanish qoliplari bilan — sanaladi, shuning uchun ikki korpusdagi ko‘rsatkichlar qiyoslanadi. Har bir inglizcha nomzod sahifasida uning tayanch korpusdagi chastotasi va o‘lchovlari ko‘rsatiladi; logDice chegarasi inson tekshiruvi natijasida kalibrlanadi (10-band). O‘zbekcha tayanch korpus uchun skript tayyor, unga matn fayllari kerak.',
    ],
    'm_rel': 'Annotatsiyani ikki mustaqil annotator — muallif va ikkinchi filolog — yozma yo‘riqnoma asosida bajaradi: avval 50 birlikli o‘quv to‘plami, so‘ngra birliklarning kamida 20 foizi (200 tadan kam emas) mustaqil belgilanadi. Kelishuv Koen kappasi bilan hisoblanadi (Cohen, 1960); κ ≥ 0,8 — yaxshi ishonchlilik, 0,67–0,8 — ehtiyotkor xulosa uchun yetarli (Artstein va Poesio, 2008, b. 576). Platformaning «Inson tekshiruvi» bo‘limida beshta vazifa bo‘yicha qat’iy tasodifiy tanlanmalar (har birida 50 + 200 birlik) va ikki annotator uchun alohida kirish bor; kollokatsiya nomzodlari 1.1.4-banddagi qaror tartibining 1–4 va 6-savollari bo‘yicha baholanadi. Aniqlik Uilson usulidagi 95 % ishonch oralig‘i bilan (Wilson, 1927), kelishuv Koen kappasi bilan avtomatik hisoblanadi va «Statistika» sahifasining 7-bo‘limida chiqadi.',
    'm_ref_limit': 'Inglizcha tayanch korpus vaqtinchalik: u BNC dan ancha kichik, asosan amerika ingliz tili va XIX asr nasridan iborat; shuning uchun kam uchraydigan birikmalar unda topilmasligi mumkin.',
    'm_cmp_limit': 'Teng matnlar qiyosida har bir tilda bitta asliyat va bitta tarjima bor: asliyat va tarjima tili farqi muallif uslubi, janr va davr farqidan ajratilmaydi.',
})
T['en'].update({
    'm_corpus': 'The corpus consists of two pairs: Cho‘lpon’s novel «Kecha va kunduz» and its English translation «Night and Day» by Christopher Fort (Uzbek into English); E. Hemingway’s novella «The Old Man and the Sea» and its Uzbek translation «Chol va dengiz» by Ibrohim G‘ofurov (English into Uzbek). In the parallel analysis each work is compared only with its own translation. At the same time each language has one original and one translated text, so the corpus also works as a comparable corpus: the original and the translated text of a language are compared with the same measures (Bernardini, 2007; Statistics, section 6).',
    'm_stat': [
        'Because the literary corpus is small, the status is set not by the figures of the research corpus but by the measures of a large reference corpus (Bernardini, 2007). The plan is the British National Corpus (BNC) for English combinations and the Uzbek National Corpus or uzWaC for Uzbek ones (the choice is argued in chapter II).',
        'Preliminary parameters: the unit of counting is the lemma; at least 5 occurrences in the reference corpus; the main measure is logDice (Rychlý, 2008); MI only with a frequency filter; t-score only as an indicator of reliability (Gablasova et al., 2017); frequency per million words. Thresholds are not fixed in advance but calibrated on a manually annotated set.',
        'Until the BNC is connected, the English candidates are checked in a reference corpus assembled from openly distributed corpora: the Brown Corpus (Francis & Kučera, 1979), MASC (Ide et al., 2010) and the prose fiction of the Project Gutenberg selection in NLTK (Bird et al., 2009) — {ref_tokens} tokens in all. It is counted in the same way as the research corpus — with the spaCy parser and the same dependency patterns — so the figures of the two corpora are comparable. The page of every English candidate shows its frequency and measures in the reference corpus; the threshold of logDice is calibrated on the human evaluation (section 10). The script for an Uzbek reference corpus is ready; it needs text files.',
    ],
    'm_rel': 'The annotation is done by two independent annotators — the author and a second philologist — with a written guide: first a training set of 50 units, then at least 20 per cent of the units (not fewer than 200) are annotated independently. Agreement is measured with Cohen’s kappa (Cohen, 1960); κ ≥ 0.8 means good reliability, 0.67–0.8 is enough for tentative conclusions (Artstein & Poesio, 2008, p. 576). The platform’s “Human evaluation” area holds fixed random samples for five tasks (50 + 200 units each) and separate sign-ins for the two annotators; collocation candidates are judged with questions 1–4 and 6 of the decision procedure of section 1.1.4. Precision with a 95% Wilson interval (Wilson, 1927) and agreement with Cohen’s kappa are computed automatically and shown in section 7 of the Statistics page.',
    'm_ref_limit': 'The English reference corpus is provisional: it is much smaller than the BNC and consists mostly of American English and 19th-century prose, so rare combinations may not be found in it.',
    'm_cmp_limit': 'The comparison of comparable texts has one original and one translated text per language: the difference between original and translated language cannot be separated from the author’s style, the genre and the period.',
})
T['ru'].update({
    'm_corpus': 'Корпус состоит из двух пар: роман Чулпана «Kecha va kunduz» и его английский перевод «Night and Day» Кристофера Форта (с узбекского на английский); повесть Э. Хемингуэя «The Old Man and the Sea» и её узбекский перевод «Chol va dengiz» Иброхима Гафурова (с английского на узбекский). В параллельном анализе каждое произведение сравнивается только со своим переводом. Вместе с тем в каждом языке есть один оригинальный и один переводной текст, поэтому корпус работает и как сопоставимый: оригинальный и переводной тексты одного языка сравниваются по одним показателям (Bernardini, 2007; «Статистика», раздел 6).',
    'm_stat': [
        'Поскольку художественный корпус мал, статус определяется не цифрами исследуемого корпуса, а показателями большого опорного корпуса (Bernardini, 2007). По плану — Британский национальный корпус (BNC) для английских сочетаний и Национальный корпус узбекского языка или uzWaC для узбекских (выбор обосновывается во II главе).',
        'Предварительные параметры: единица счёта — лемма; не менее 5 употреблений в опорном корпусе; основная мера — logDice (Rychlý, 2008); MI — только с частотным фильтром; t-score — только как показатель надёжности (Gablasova et al., 2017); частота на миллион слов. Пороги заранее не задаются, а калибруются на вручную размеченном наборе.',
        'Пока BNC не подключён, английские кандидаты проверяются по опорному корпусу из открыто распространяемых корпусов: Brown Corpus (Francis & Kučera, 1979), MASC (Ide et al., 2010) и художественная проза из выборки Project Gutenberg в NLTK (Bird et al., 2009) — всего {ref_tokens} токенов. Он подсчитан тем же способом, что и исследуемый корпус, — анализатором spaCy и теми же моделями связей, поэтому показатели двух корпусов сопоставимы. На странице каждого английского кандидата показаны его частота и меры в опорном корпусе; порог logDice калибруется по экспертной проверке (раздел 10). Скрипт для узбекского опорного корпуса готов; ему нужны текстовые файлы.',
    ],
    'm_rel': 'Разметку выполняют два независимых аннотатора — автор и второй филолог — по письменной инструкции: сначала обучающий набор из 50 единиц, затем не менее 20 процентов единиц (не менее 200) размечаются независимо. Согласие измеряется каппой Коэна (Cohen, 1960); κ ≥ 0,8 — хорошая надёжность, 0,67–0,8 — достаточно для осторожных выводов (Artstein & Poesio, 2008, p. 576). В разделе платформы «Экспертная проверка» есть фиксированные случайные выборки для пяти задач (по 50 + 200 единиц) и отдельные входы для двух аннотаторов; кандидаты в коллокации оцениваются по вопросам 1–4 и 6 порядка решений раздела 1.1.4. Точность с 95%-м интервалом Уилсона (Wilson, 1927) и согласие по каппе Коэна вычисляются автоматически и показываются в разделе 7 страницы «Статистика».',
    'm_ref_limit': 'Английский опорный корпус временный: он намного меньше BNC и состоит в основном из американского английского и прозы XIX века, поэтому редкие сочетания в нём могут не найтись.',
    'm_cmp_limit': 'В сравнении сопоставимых текстов на каждый язык приходится один оригинальный и один переводной текст: различие оригинального и переводного языка не отделяется от стиля автора, жанра и эпохи.',
})
for _l in ('uz', 'en', 'ru'):
    T[_l]['m_limits'] = T[_l]['m_limits'] + [T[_l]['m_ref_limit'], T[_l]['m_cmp_limit']]

T['uz']['g_status_v2'] = 'Hozirgi holat: inson tekshiruvining {total} birligidan annotator A {a} tasini, annotator B {b} tasini baholagan. Natijalar «Statistika» sahifasining 7-bo‘limida chiqadi.'
T['en']['g_status_v2'] = 'Current state: of the {total} units of the human evaluation, annotator A has judged {a} and annotator B {b}. The results appear in section 7 of the Statistics page.'
T['ru']['g_status_v2'] = 'Текущее состояние: из {total} единиц экспертной проверки аннотатор A оценил {a}, аннотатор B — {b}. Результаты появляются в разделе 7 страницы «Статистика».'

REFERENCES = [
    'Artstein, R., & Poesio, M. (2008). Inter-coder agreement for computational linguistics. <em>Computational Linguistics, 34</em>(4), 555–596. https://doi.org/10.1162/coli.07-034-R2',
    'Bernardini, S. (2007). Collocations in translated language: Combining parallel, comparable and reference corpora. In <em>Proceedings of the Corpus Linguistics Conference (CL2007)</em> (pp. 1–16). University of Birmingham.',
    'Cho‘lpon, A. (2000). <em>Kecha va kunduz</em>. Sharq. [Elektron nusxa: ziyouz.com]',
    'Cho‘lpon, A. (2019). <em>Night and day: A novel</em> (C. Fort, Trans.). Academic Studies Press. https://doi.org/10.1515/9781644690482',
    'Cohen, J. (1960). A coefficient of agreement for nominal scales. <em>Educational and Psychological Measurement, 20</em>(1), 37–46.',
    'Gale, W. A., & Church, K. W. (1993). A program for aligning sentences in bilingual corpora. <em>Computational Linguistics, 19</em>(1), 75–102.',
    'Gablasova, D., Brezina, V., & McEnery, T. (2017). Collocations in corpus-based language learning research: Identifying, comparing, and interpreting the evidence. <em>Language Learning, 67</em>(S1), 155–179. https://doi.org/10.1111/lang.12225',
    'Rychlý, P. (2008). A lexicographer-friendly association score. In P. Sojka & A. Horák (Eds.), <em>Proceedings of Recent Advances in Slavonic Natural Language Processing, RASLAN 2008</em> (pp. 6–9). Masaryk University.',
    'Uhrig, P., & Proisl, T. (2012). Less hay, more needles: Using dependency-annotated corpora to provide lexicographers with more accurate lists of collocation candidates. <em>Lexicographica, 28</em>, 141–180. https://doi.org/10.1515/LEXI.2012-0009',
    'Varga, D., Halácsy, P., Kornai, A., Nagy, V., Németh, L., & Trón, V. (2007). Parallel corpora for medium density languages. In <em>Recent advances in natural language processing IV: Selected papers from RANLP 2005</em> (pp. 247–258). John Benjamins. https://www.jbe-platform.com/content/books/9789027291288-cilt.292.32var',
    'Dunning, T. (1993). Accurate methods for the statistics of surprise and coincidence. <em>Computational Linguistics, 19</em>(1), 61–74.',
    'Dyer, C., Chahuneau, V., & Smith, N. A. (2013). A simple, fast, and effective reparameterization of IBM Model 2. In <em>Proceedings of the 2013 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies</em> (pp. 644–648). Association for Computational Linguistics.',
    'Evert, S. (2008). Corpora and collocations. In A. Lüdeling & M. Kytö (Eds.), <em>Corpus linguistics: An international handbook</em> (Vol. 2, pp. 1212–1248). Mouton de Gruyter.',
    'Hemingway, E. (1952). <em>The old man and the sea</em>. Charles Scribner’s Sons. [Elektron nusxa: Asiaing.com]',
    'Xeminguey, E. (1986). <em>Chol va dengiz</em> (I. G‘ofurov, Tarj.). Yosh gvardiya. [Elektron nusxa: kutubxonachi.uz]',
    'Östling, R., & Tiedemann, J. (2016). Efficient word alignment with Markov chain Monte Carlo. <em>The Prague Bulletin of Mathematical Linguistics, 106</em>, 125–146. https://doi.org/10.1515/pralin-2016-0013',
    'Bird, S., Klein, E., & Loper, E. (2009). <em>Natural language processing with Python</em>. O’Reilly Media.',
    'Cramér, H. (1946). <em>Mathematical methods of statistics</em>. Princeton University Press.',
    'Francis, W. N., & Kučera, H. (1979). <em>Brown corpus manual: Manual of information to accompany a standard corpus of present-day edited American English, for use with digital computers</em> (Rev. ed.). Department of Linguistics, Brown University.',
    'Ide, N., Baker, C., Fellbaum, C., & Passonneau, R. (2010). The Manually Annotated Sub-Corpus: A community resource for and by the people. In <em>Proceedings of the ACL 2010 Conference Short Papers</em> (pp. 68–73). Association for Computational Linguistics. https://aclanthology.org/P10-2013/',
    'Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. <em>Journal of the American Statistical Association, 22</em>(158), 209–212.',
    'Yarowsky, D., Ngai, G., & Wicentowski, R. (2001). Inducing multilingual text analysis tools via robust projection across aligned corpora. In <em>Proceedings of the First International Conference on Human Language Technology Research</em>. https://aclanthology.org/H01-1035/',
]
REFERENCES.sort(key=lambda r: re.sub('<[^>]+>', '', r).replace('Ö', 'O').lower())


_REF_NOTES = {
    'en': (('[Elektron nusxa: ', '[Electronic copy: '), (', Tarj.)', ', Trans.)')),
    'ru': (('[Elektron nusxa: ', '[Электронная копия: '), (', Tarj.)', ', пер.)'), (', Trans.)', ', пер.)')),
    'uz': ((', Trans.)', ', Tarj.)'),),
}


def localize_reference(ref, lang):
    """The bibliographic notes added in square brackets and the translator mark follow the interface language;
    the reference itself (APA 7) is not translated."""
    for a, b in _REF_NOTES.get(lang, ()):
        ref = ref.replace(a, b)
    return ref


# ---------------------------------------------------------------------------------------------
# Page shell
# ---------------------------------------------------------------------------------------------
def _shell(lang, path, is_admin, title, body):
    return ui.page(lang, title, body, path, is_admin, narrow=True)


def _h1(text, lead=''):
    return '<header><h1>%s</h1>%s</header>' % (text, '<p class="tc-lead">%s</p>' % lead if lead else '')


def _section(title, inner, anchor='', prose=True):
    aid = ' id="%s"' % anchor if anchor else ''
    cls = 'tc-section tc-prose' if prose else 'tc-section'
    return '<section class="%s"%s><h2>%s</h2><div style="margin-top:10px">%s</div></section>' % (cls, aid, title, inner)


def _p(text):
    return '<p>%s</p>' % text


def _ul(items, ordered=False):
    tag = 'ol' if ordered else 'ul'
    return '<%s>%s</%s>' % (tag, ''.join('<li>%s</li>' % i for i in items), tag)


def _table(head, rows, align='', total_last=False):
    """align: one letter per column, 'r' = right-aligned number column, 'n' = no wrap, anything else = left."""
    def cls(i):
        a = align[i] if i < len(align) else ''
        return {'r': ' class="r tc-num"', 'n': ' class="nw"'}.get(a, '')
    th = ''.join('<th%s>%s</th>' % (cls(i), h) for i, h in enumerate(head))
    trs = []
    for k, r in enumerate(rows):
        tr_cls = ' class="tc-total"' if total_last and k == len(rows) - 1 else ''
        trs.append('<tr%s>%s</tr>' % (tr_cls, ''.join('<td%s>%s</td>' % (cls(i), c) for i, c in enumerate(r))))
    return ('<div class="tc-panel tc-scroll" style="padding:4px 8px"><table class="tc-table"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            % (th, ''.join(trs)))


# ---------------------------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------------------------
def _dl(rows):
    return ('<dl style="display:grid;grid-template-columns:minmax(120px,max-content) 1fr;gap:8px 18px;margin:0">'
            + ''.join('<dt class="tc-muted">%s</dt><dd style="margin:0">%s</dd>' % (a, b) for a, b in rows) + '</dl>')


def render_about(lang, is_admin, st):
    rows = [
        (tr(lang, 'about_topic_label'), tr(lang, 'about_topic')),
        (tr(lang, 'about_researcher_label'), 'Voxitov Ibrohim Sodiq o‘g‘li'),
        (tr(lang, 'about_university_label'), tr(lang, 'about_university')),
        (tr(lang, 'about_specialty_label'), tr(lang, 'about_specialty')),
    ]
    body = (_h1(tr(lang, 'about_title'), tr(lang, 'about_lead'))
            + '<section class="tc-section"><div class="tc-panel">%s</div></section>' % _dl(rows)
            + _section(tr(lang, 'about_what_title'), _ul(T[lang]['about_what']))
            + _section(tr(lang, 'about_state_title'), _p(tr(lang, 'about_state', pairs=n(st['pairs_total'], lang), confirmed=n(st['pairs_confirmed'], lang))))
            + _section(tr(lang, 'about_tech_title'), _p(tr(lang, 'about_tech'))))
    return _shell(lang, '/about_project.html', is_admin, tr(lang, 'about_title'), body)


def render_sources(lang, is_admin, st, sizes):
    def text_card(role_key, title, prefix, size_key, pairs_key, confirmed_key):
        sz = sizes.get(size_key) or {}
        size_line = tr(lang, 'src_tokens_full', tokens=n(sz.get('tokens'), lang), types=n(sz.get('types'), lang)) if sz else '—'
        size_line += '; ' + tr(lang, 'src_pairs', pairs=n(st.get(pairs_key), lang), confirmed=n(st.get(confirmed_key), lang))
        rows = [(tr(lang, 'src_edition'), tr(lang, prefix + '_edition')), (tr(lang, 'src_copy'), tr(lang, prefix + '_copy')),
                (tr(lang, 'src_pages'), tr(lang, prefix + '_pages')), (tr(lang, 'src_size'), size_line)]
        return ('<section class="tc-book"><p class="tc-muted tc-small">%s</p><h3>%s</h3><div style="margin-top:10px">%s</div></section>'
                % (tr(lang, role_key), title, _dl(rows)))
    pair1 = ('<div class="tc-books">' + text_card('src_role_original', '«Kecha va kunduz»', 'src_kvk_uz', 'book-cholpon-uz', 'pairs_kvk', 'confirmed_kvk')
             + text_card('src_role_translation', '«Night and Day»', 'src_kvk_en', 'book-cholpon-en', 'pairs_kvk', 'confirmed_kvk') + '</div>')
    pair2 = ('<div class="tc-books">' + text_card('src_role_original', '«The Old Man and the Sea»', 'src_oms_en', 'book-hemingway-en', 'pairs_oms', 'confirmed_oms')
             + text_card('src_role_translation', '«Chol va dengiz»', 'src_oms_uz', 'book-hemingway-uz', 'pairs_oms', 'confirmed_oms') + '</div>')
    body = (_h1(tr(lang, 'src_title'), tr(lang, 'src_lead'))
            + '<section class="tc-section"><h2>%s</h2><div style="margin-top:14px">%s</div></section>' % (tr(lang, 'src_pair_kvk'), pair1)
            + '<section class="tc-section"><h2>%s</h2><div style="margin-top:14px">%s</div></section>' % (tr(lang, 'src_pair_oms'), pair2)
            + _section(tr(lang, 'src_excluded_title'), _p(tr(lang, 'src_excluded')))
            + _section(tr(lang, 'src_rights_title'), _p(tr(lang, 'src_rights'))))
    return ui.page(lang, tr(lang, 'src_title'), body, '/sources_rights.html', is_admin)


def render_methodology(lang, is_admin, st):
    L = T[lang]
    statuses = _ul(['<strong>%s</strong> — %s' % (a, b) for a, b in L['m_statuses']])
    body = (_h1(tr(lang, 'm_title'), tr(lang, 'm_lead'))
            + _section(tr(lang, 'm_def_title'), _p(tr(lang, 'm_def_intro')) + _ul(L['m_def_items'], ordered=True) + _p(tr(lang, 'm_def_note'))
                       + '<h3 style="margin-top:18px">%s</h3>' % tr(lang, 'm_status_title') + statuses + _p(tr(lang, 'm_exclusions')) + _p(tr(lang, 'm_unit')), 'tarif')
            + _section(tr(lang, 'm_corpus_title'), _p(tr(lang, 'm_corpus')) + _p(tr(lang, 'm_pages')), 'korpus')
            + _section(tr(lang, 'm_text_title'), ''.join(_p(x) for x in L['m_text']), 'matn')
            + _section(tr(lang, 'm_align_title'), _p(tr(lang, 'm_align', confirmed=n(st['pairs_confirmed'], lang),
                                                          auto_good=n(st.get('pairs_auto_good'), lang), auto_one=n(st.get('pairs_auto_one'), lang),
                                                          auto_pin=n(st.get('pairs_auto_pin'), lang)))
                       + _p(tr(lang, 'm_unpaired', unpaired=n(st.get('unpaired'), lang))), 'gaplar')
            + _section(tr(lang, 'm_walign_title'), ''.join(_p(x) for x in L['m_walign']), 'tekislash')
            + _section(tr(lang, 'm_equiv_title'), _p(tr(lang, 'm_equiv')) + _ul(L['m_equiv_items']), 'kollokatsiyalar')
            + _section(tr(lang, 'm_dict_title'), ''.join(_p(x.replace('{uz}', n(st.get('dict_uz'), lang)).replace('{en}', n(st.get('dict_en'), lang)))
                                                         for x in L['m_dict']), 'lugat')
            + _section(tr(lang, 'm_cand_title'), _p(tr(lang, 'm_cand')) + _p(tr(lang, 'm_reference', ref=n(st['reference_active'], lang))), 'malumotnoma')
            + _section(tr(lang, 'm_stat_title'), ''.join(_p(x.replace('{ref_tokens}', n(st.get('ref_tokens'), lang))) for x in L['m_stat']), 'statistika')
            + _section(tr(lang, 'm_rel_title'), _p(tr(lang, 'm_rel')), 'ishonchlilik')
            + _section(tr(lang, 'm_limits_title'), _ul(L['m_limits']), 'cheklovlar')
            + _section(tr(lang, 'm_refs_title'), '<ul class="tc-small" style="list-style:none;padding:0">' + ''.join(
                '<li style="padding-left:2em;text-indent:-2em">%s</li>' % localize_reference(r, lang) for r in REFERENCES) + '</ul>', 'adabiyotlar'))
    return _shell(lang, '/methodology.html', is_admin, tr(lang, 'm_title'), body)


def _validation_status(lang):
    import validation as V
    prog = V.progress()
    a = sum(p['A']['train'] + p['A']['main'] for p in prog.values())
    b = sum(p['B']['train'] + p['B']['main'] for p in prog.values())
    total = sum(p['train'] + p['main'] for p in prog.values())
    return tr(lang, 'g_status_v2', a=n(a, lang), b=n(b, lang), total=n(total, lang))


def render_guidelines(lang, is_admin, ann):
    L = T[lang]
    steps = '<ol>' + ''.join('<li><strong>%s</strong><br><span class="tc-muted">%s</span></li>' % (q, a) for q, a in L['g_steps']) + '</ol>'
    equiv = _ul(['<strong>%s</strong>: %s' % (a, b) for a, b in L['g_equiv']])
    body = (_h1(tr(lang, 'g_title'), tr(lang, 'g_lead'))
            + _section(tr(lang, 'm_def_title'), _ul(L['m_def_items'], ordered=True))
            + _section(tr(lang, 'g_title'), steps)
            + _section(tr(lang, 'g_base_title'), _table(L['g_base_head'], L['g_base_rows']) + '<p style="margin-top:12px">%s</p>' % tr(lang, 'g_base_note'))
            + _section(tr(lang, 'g_equiv_title'), equiv)
            + _section(tr(lang, 'g_rel_title'), _p(tr(lang, 'm_rel')) + _p(_validation_status(lang))))
    return _shell(lang, '/annotation_guidelines.html', is_admin, tr(lang, 'g_title'), body)


def _pct(a, b, lang):
    if not b:
        return '—'
    v = 100.0 * a / b
    return ('%.0f%%' % v) if lang == 'en' else ('%.0f %%' % v)


DIRECTIONS = (('uz', 'kvk', 's_dir_uz_src'), ('en', 'oms', 's_dir_en_src'),
              ('en', 'kvk', 's_dir_en_tgt'), ('uz', 'oms', 's_dir_uz_tgt'))


def collocation_translation_tables(colls, lang):
    """How the collocations of each text are rendered in its parallel text: computed from the per-book
    equivalent counts stored in the collocation index (every occurrence, word alignment of section 5)."""
    summary, details, top = [], '', {}
    for c_lang, book, label_key in DIRECTIONS:
        by_pat = {}
        tot = {'types': 0, 'occ': 0, 'eq': 0, 'single': 0, 'multi': 0}
        for it in colls:
            st = (it.get('eq_stats') or {}).get(book)
            if it['lang'] != c_lang or not st:
                continue
            d = by_pat.setdefault(it['pattern'], {'types': 0, 'occ': 0, 'eq': 0, 'single': 0, 'multi': 0})
            for dd in (d, tot):
                dd['types'] += 1
                for k in ('occ', 'eq', 'single', 'multi'):
                    dd[k] += st[k]
            top.setdefault(label_key, []).append((st['occ'], st['eq'], it))
        if not by_pat:
            continue

        def row(first, d):
            return (first, n(d['types'], lang), n(d['occ'], lang), _pct(d['eq'], d['occ'], lang),
                    _pct(d['single'], d['eq'], lang), _pct(d['multi'], d['eq'], lang))
        summary.append(row(tr(lang, label_key), tot))
        rows = [row(html.escape(ui.pattern_label(pat, lang)), d) for pat, d in sorted(by_pat.items(), key=lambda kv: -kv[1]['occ'])]
        rows.append(row('<em>%s</em>' % tr(lang, 's_total'), tot))
        details += ('<details class="tc-details" style="margin-top:10px"><summary>%s</summary><div style="margin-top:10px">%s</div></details>'
                    % (tr(lang, label_key), _table([tr(lang, 's_col_pattern')] + T[lang]['s_dir_head'][2:], rows, 'nrrrrr', total_last=True)))
    head = [T[lang]['s_dir_head'][0]] + T[lang]['s_dir_head'][2:]
    summary_html = _table(head, summary, 'lrrrrr')
    top_html = ''
    for c_lang, book, label_key in DIRECTIONS[:2]:
        t_rows = []
        for occ, eq, it in sorted(top.get(label_key, []), key=lambda x: (-x[0], x[2]['lemma']))[:15]:
            trs = it.get('translations') or []
            o_lang = 'en' if it['lang'] == 'uz' else 'uz'
            main = ', '.join('<span class="tc-serif" lang="%s">%s</span>&nbsp;<span class="tc-muted tc-num">(%s)</span>'
                             % (o_lang, html.escape(t['text']), n(t['count'], lang)) for t in trs[:3])
            t_rows.append(('<a class="tc-serif" lang="%s" href="%s">%s</a>' % (it['lang'], ui.with_lang('/kollokatsiya/' + it['id'], lang),
                                                                             html.escape(it.get('display') or '')),
                           html.escape(ui.pattern_label(it['pattern'], lang)), n(occ, lang), _pct(eq, occ, lang), main or '—'))
        top_html += '<h3 style="margin:28px 0 10px">%s</h3>' % tr(lang, 's_top_title_' + label_key) + _table(T[lang]['s_top_head'], t_rows, 'nnrrl')
    return summary_html, details, top_html


def _ranks(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    r = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2.0 + 1
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = _ranks(a), _ranks(b)
    m = len(a)
    if m < 3:
        return None
    ma, mb = sum(ra) / m, sum(rb) / m
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra)
    vb = sum((y - mb) ** 2 for y in rb)
    return cov / (va * vb) ** 0.5 if va and vb else None


MEASURES = (('freq', None), ('mi', 'MI'), ('t', 't-score'), ('log_dice', 'logDice'), ('g2', 'G²'))


def _mlabel(lbl, lang):
    return lbl or tr(lang, 's_freq')


def _mval(it, m):
    return it['freq'] if m == 'freq' else (it.get('assoc') or {}).get(m)


def measure_comparison(colls, lang):
    """Within-corpus comparison of association measures over the corpus collocations (f >= 2)."""
    def num(x, d=2):
        if x is None:
            return '—'
        t = ('%.' + str(d) + 'f') % x
        return t if lang == 'en' else t.replace('.', ',').replace('-', '−')
    out = ''
    for c_lang, key in (('uz', 's_meas_uz'), ('en', 's_meas_en')):
        items = [it for it in colls if it['lang'] == c_lang and it.get('assoc')]
        if not items:
            continue
        vals = dict((m, [_mval(it, m) for it in items]) for m, _ in MEASURES)
        # correlation matrix
        head = [''] + [_mlabel(lbl, lang) for _, lbl in MEASURES]
        corr_rows = []
        for m1, l1 in MEASURES:
            corr_rows.append(['<strong>%s</strong>' % _mlabel(l1, lang)] + [num(spearman(vals[m1], vals[m2])) if m1 != m2 else '1' for m2, _ in MEASURES])
        # top-50 profile and top-8 lists
        prof_rows, list_rows = [], []
        for m, lbl in MEASURES:
            ranked = sorted(items, key=lambda it: (-_mval(it, m), it['lemma']))
            top50 = ranked[:50]
            mean_f = sum(it['freq'] for it in top50) / float(len(top50))
            share2 = sum(1 for it in top50 if it['freq'] == 2) / float(len(top50)) * 100
            prof_rows.append(('<strong>%s</strong>' % _mlabel(lbl, lang), num(mean_f, 1), _pct(share2, 100, lang)))
            list_rows.append(('<strong>%s</strong>' % _mlabel(lbl, lang), ', '.join(
                '<a class="tc-serif" lang="%s" href="%s">%s</a> <span class="tc-muted tc-num">(%s)</span>'
                % (c_lang, ui.with_lang('/kollokatsiya/' + it['id'], lang), html.escape(it.get('display') or ''), n(it['freq'], lang))
                for it in ranked[:8])))
        out += ('<h3 style="margin:26px 0 6px">%s</h3><p class="tc-small tc-muted">%s</p>'
                % (tr(lang, key), tr(lang, 's_meas_n', types=n(len(items), lang), tokens=n(items[0]['assoc']['n'], lang))))
        out += ('<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:0 24px">'
                '<div><h4 style="margin:14px 0 8px">%s</h4>%s</div><div><h4 style="margin:14px 0 8px">%s</h4>%s</div></div>'
                % (tr(lang, 's_meas_corr'), _table(head, corr_rows, 'nrrrrr'), tr(lang, 's_meas_profile'),
                   _table(T[lang]['s_meas_profile_head'], prof_rows, 'nrr')))
        out += '<h4 style="margin:18px 0 8px">%s</h4>' % tr(lang, 's_meas_top') + _table(T[lang]['s_meas_top_head'], list_rows, 'nl')
    return out



def _num(x, lang, d=2):
    if x is None:
        return '—'
    t = ('%.' + str(d) + 'f') % x
    return t if lang == 'en' else t.replace('.', ',').replace('-', '−')


def _test_row(label, res, lang, orr=None):
    import analysis as A
    if not res:
        return (label, '—', '—', '—', '—', '—', '—')
    return (label, n(res['n'], lang), '%s (%d)' % (_num(res['chi2'], lang, 1), res['df']), _num(res['g2'], lang, 1),
            A.fmt_p(res['p_chi2'], lang), _num(res['v'], lang, 3),
            ('%s (%s–%s)' % (_num(orr[0], lang), _num(orr[1], lang), _num(orr[2], lang))) if orr else '—')


def direction_tests(colls, lang):
    """Chi-square / G² tests of the direction differences of section 3."""
    import analysis as A
    agg = {}
    types = {}
    for c_lang, book, key in DIRECTIONS:
        d = {'occ': 0, 'eq': 0, 'single': 0, 'multi': 0}
        tt = [0, 0]
        for it in colls:
            st = (it.get('eq_stats') or {}).get(book)
            if it['lang'] != c_lang or not st:
                continue
            for k in d:
                d[k] += st[k]
            if st['occ']:
                tt[0 if st['eq'] * 2 >= st['occ'] else 1] += 1
        agg[key], types[key] = d, tt
    keys = [k for _, _, k in DIRECTIONS]
    eq_tab = [[agg[k]['eq'], agg[k]['occ'] - agg[k]['eq']] for k in keys]
    sm_tab = [[agg[k]['single'], agg[k]['multi']] for k in keys]
    a, b = 's_dir_uz_src', 's_dir_en_src'
    rows = [
        _test_row(tr(lang, 's_t_eq4'), A.contingency(eq_tab), lang),
        _test_row(tr(lang, 's_t_eq2'), A.contingency([eq_tab[0], eq_tab[1]]), lang, A.odds_ratio(*eq_tab[0], *eq_tab[1])),
        _test_row(tr(lang, 's_t_eq2t'), A.contingency([types[a], types[b]]), lang, A.odds_ratio(*types[a], *types[b])),
        _test_row(tr(lang, 's_t_sm4'), A.contingency(sm_tab), lang),
        _test_row(tr(lang, 's_t_sm2'), A.contingency([sm_tab[0], sm_tab[1]]), lang, A.odds_ratio(*sm_tab[0], *sm_tab[1])),
    ]
    return ('<h3 style="margin:28px 0 6px">%s</h3><p class="tc-section__note">%s</p>' % (tr(lang, 's_test_title'), tr(lang, 's_test_note'))
            + _table(T[lang]['s_test_head'], rows, 'lrrrrrr'))


def reference_section(colls, ref_info, lang):
    if not ref_info:
        return ''
    en = [it for it in colls if it['lang'] == 'en']
    with_ref = [it for it in en if (it.get('ref') or {}).get('f')]
    five = [it for it in with_ref if it['ref']['f'] >= 5 and it['ref'].get('log_dice') is not None]
    rho = spearman([it['assoc']['log_dice'] for it in five], [it['ref']['log_dice'] for it in five]) if len(five) > 3 else None
    parts = _table(T[lang]['s_ref_head'], [(html.escape(p['name']), n(p['tokens'], lang)) for p in ref_info['parts']]
                   + [('<em>%s</em>' % tr(lang, 's_total'), n(ref_info['n'], lang))], 'lr', total_last=True)
    top = sorted(five, key=lambda it: (-it['ref']['log_dice'], it['lemma']))[:15]
    top_rows = [('<a class="tc-serif" lang="en" href="%s">%s</a>' % (ui.with_lang('/kollokatsiya/' + it['id'], lang), html.escape(it.get('display') or '')),
                 html.escape(ui.pattern_label(it['pattern'], lang)), n(it['freq'], lang), n(it['ref']['f'], lang),
                 _num(it['ref']['log_dice'], lang), _num(it['ref'].get('mi'), lang)) for it in top]
    body = ('<div class="tc-prose">%s</div>' % _p(tr(lang, 's_ref_lead')) + parts
            + '<p class="tc-prose" style="margin-top:14px">%s</p>' % tr(lang, 's_ref_cov', all=n(len(en), lang), any=n(len(with_ref), lang),
                                                                       five=n(len(five), lang), rho=_num(rho, lang))
            + '<h3 style="margin:24px 0 10px">%s</h3>' % tr(lang, 's_ref_top') + _table(T[lang]['s_ref_top_head'], top_rows, 'nnrrrr')
            + '<p class="tc-small tc-muted tc-prose" style="margin-top:12px">%s</p>' % tr(lang, 's_ref_caveat', tokens=n(ref_info['n'], lang)))
    return _section(tr(lang, 's_ref_title'), body, 'tayanch', prose=False)


def comparable_section(cmp, lang):
    if not cmp:
        return ''
    import analysis as A
    names = {('en', 'hemingway'): '«The Old Man and the Sea»', ('en', 'cholpon'): '«Night and Day»',
             ('uz', 'cholpon'): '«Kecha va kunduz»', ('uz', 'hemingway'): '«Chol va dengiz»'}
    role = {'original': tr(lang, 'role_original'), 'translated': tr(lang, 'role_translation')}
    rows, en_rows = [], []
    for r in cmp['texts']:
        title = '%s <span class="tc-muted">(%s)</span>' % (names[(r['lang'], r['book'])], role[r['role']])
        def p1(a, b):
            return (_num(100.0 * a / b, lang, 1) + (' %' if lang != 'en' else '%')) if b else '—'
        rows.append((title, tr(lang, 'lang_' + r['lang']), n(r['tokens'], lang), _num(r['sttr'], lang, 3), p1(r['density'], 1),
                     _num(r['cand_per_1000'], lang, 1)))
        if r['lang'] == 'en':
            en_rows.append((title, _num(r['pairs_per_1000'], lang, 1), p1(r['ref_attested'], r['pair_occ']),
                            p1(r['ref_typical'], r['pair_occ']), p1(r['once_types'], r['pair_types'])))
    trows = []
    for lg in ('en', 'uz'):
        for k in ('cand', 'density', 'attested', 'typical', 'once'):
            res = (cmp['tests'].get(lg) or {}).get(k)
            if res:
                trows.append((tr(lang, 's_cmp_t_' + k), tr(lang, 'lang_' + lg), '%s (%d)' % (_num(res['chi2'], lang, 1), res['df']),
                              A.fmt_p(res['p_chi2'], lang), _num(res['v'], lang, 3)))
    body = ('<div class="tc-prose">%s</div>' % _p(tr(lang, 's_cmp_lead')) + _table(T[lang]['s_cmp_head'], rows, 'lnrrrr')
            + '<div style="margin-top:16px">%s</div>' % _table(T[lang]['s_cmp_en_head'], en_rows, 'lrrrr')
            + '<p class="tc-small tc-muted tc-prose" style="margin-top:10px">%s</p>' % tr(lang, 's_cmp_note')
            + '<div style="margin-top:16px">%s</div>' % _table(T[lang]['s_cmp_tests_head'], trows, 'lnrrr')
            + '<p class="tc-prose" style="margin-top:14px">%s</p>' % tr(lang, 's_cmp_caveat'))
    return _section(tr(lang, 's_cmp_title'), body, 'teng-matnlar', prose=False)


def validation_section(lang, colls):
    import validation as V
    import validation_pages as VP
    res = V.results()
    has = any((res.get(t_) or {}).get('A', {}).get('n') for t_ in V.TASKS)
    body = '<div class="tc-prose">%s</div>' % _p(tr(lang, 's_val_ready', seed=V.samples().get('seed', '—')))
    if has:
        body += '<div style="margin-top:14px">%s</div>' % VP.results_html(lang, res, V.calibration(colls or []))
    return _section(tr(lang, 's_val_title'), body, 'inson-tekshiruvi', prose=False)

def render_statistics(lang, is_admin, st, sizes, ann, colls=None, ref_info=None, cmp=None):
    L = T[lang]
    order = [('book-cholpon-uz', '«Kecha va kunduz»', 'role_original', 'lang_uz'),
             ('book-cholpon-en', '«Night and Day»', 'role_translation', 'lang_en'),
             ('book-hemingway-en', '«The Old Man and the Sea»', 'role_original', 'lang_en'),
             ('book-hemingway-uz', '«Chol va dengiz»', 'role_translation', 'lang_uz')]
    rows = []
    for key, title, role, lng in order:
        sz = sizes.get(key)
        if not sz:
            continue
        ttr = (sz['types'] / sz['tokens']) if sz.get('tokens') else 0
        ttr_txt = ('%.4f' % ttr) if lang == 'en' else ('%.4f' % ttr).replace('.', ',')
        rows.append(('%s <span class="tc-muted">(%s)</span>' % (title, tr(lang, role)), tr(lang, lng),
                     n(sz['tokens'], lang), n(sz['types'], lang), n(sz['hapax'], lang), ttr_txt))
    pair_rows = [(title, n(st.get('pairs_' + k), lang), n(st.get('confirmed_' + k), lang), n(st.get('auto_good_' + k), lang),
                  n(st.get('auto_one_' + k), lang), n(st.get('auto_pin_' + k), lang))
                 for k, title in (('kvk', 'Cho‘lpon: «Kecha va kunduz» — «Night and Day»'),
                                  ('oms', 'Hemingway: «The Old Man and the Sea» — «Chol va dengiz»'))]
    formulas = ('<div class="tc-panel" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:8px 24px;font-family:var(--serif)">'
                '<div>MI = log₂ (O₁₁ · N / (R₁ · C₁))</div><div>t = (O₁₁ − E₁₁) / √O₁₁, E₁₁ = R₁ · C₁ / N</div>'
                '<div>logDice = 14 + log₂ (2 · O₁₁ / (R₁ + C₁))</div><div>G² = 2 Σ Oᵢⱼ · ln (Oᵢⱼ / Eᵢⱼ)</div>'
                '<div>NormFreq = RawFreq / N × 1 000 000</div></div>')
    auto_sec = meas_sec = ''
    if colls:
        summary_html, details, top_html = collocation_translation_tables(colls, lang)
        auto_sec = _section(tr(lang, 's_auto_title'),
                            '<div class="tc-prose">%s</div>' % _p(tr(lang, 's_auto_note')) + summary_html
                            + '<p class="tc-small tc-muted tc-prose" style="margin-top:10px">%s</p>' % tr(lang, 's_auto_cols')
                            + direction_tests(colls, lang)
                            + '<h3 style="margin:24px 0 4px">%s</h3>' % tr(lang, 's_by_pattern') + details + top_html, 'tarjima-tahlili', prose=False)
        meas_sec = _section(tr(lang, 's_assoc_title'),
                            '<div class="tc-prose">%s</div>' % _p(tr(lang, 's_assoc')) + '<h3 style="margin:16px 0 10px">%s</h3>' % tr(lang, 's_formulas_title')
                            + formulas + measure_comparison(colls, lang) + '<div class="tc-prose" style="margin-top:18px">%s</div>' % _p(tr(lang, 's_meas_reading')),
                            'assotsiatsiya', prose=False)
    body = (_h1(tr(lang, 's_title'), tr(lang, 's_lead'))
            + _section(tr(lang, 's_size_title'), _table(L['s_head'], rows, 'lnrrrr') + '<p class="tc-small tc-muted tc-prose" style="margin-top:10px">%s</p>' % tr(lang, 's_size_note'), prose=False)
            + _section(tr(lang, 's_pairs_title'), _table(L['s_pairs_head'], pair_rows, 'lrrrrr'), prose=False)
            + auto_sec + meas_sec + reference_section(colls or [], ref_info, lang) + comparable_section(cmp, lang) + validation_section(lang, colls)
            + _section(tr(lang, 's_ch3_title'), _p(tr(lang, 's_ch3', ann=n(ann.get('confirmed'), lang)))))
    return ui.page(lang, tr(lang, 's_title'), body, '/methodology_statistics.html', is_admin)
