import json
import os

locales_dir = 'locales'
uz = json.load(open(os.path.join(locales_dir, 'uz.json'), encoding='utf-8'))
en = json.load(open(os.path.join(locales_dir, 'en.json'), encoding='utf-8'))
ru = json.load(open(os.path.join(locales_dir, 'ru.json'), encoding='utf-8'))

# New key additions
new_entries = {
    "hero_title": {
        "uz": "TILCOR — O‘zbek–ingliz parallel korpusi",
        "en": "TILCOR — Uzbek–English Parallel Corpus",
        "ru": "TILCOR — Узбекско-английский параллельный корпус"
    },
    "hero_subtitle": {
        "uz": "Kollokatsiyalar tarjimasi tadqiqoti: o‘zbekchadan inglizchaga va inglizchadan o‘zbekchaga",
        "en": "Collocation translation research: Uzbek-to-English and English-to-Uzbek",
        "ru": "Исследование перевода коллокаций: с узбекского на английский и с английского на узбекский"
    },
    "search_chips_label": {
        "uz": "Namunaviy so‘rovlar:",
        "en": "Sample queries:",
        "ru": "Примеры запросов:"
    },
    "nav_corpus": {
        "uz": "Korpus",
        "en": "Corpus",
        "ru": "Корпус"
    },
    "nav_corpus_search": {
        "uz": "Korpus qidiruvi",
        "en": "Corpus search",
        "ru": "Поиск по корпусу"
    },
    "nav_kwic": {
        "uz": "KWIC konkordans",
        "en": "KWIC concordance",
        "ru": "KWIC-конкорданс"
    },
    "nav_collocations": {
        "uz": "Kollokatsiyalar",
        "en": "Collocations",
        "ru": "Коллокации"
    },
    "nav_colloc_search": {
        "uz": "Kollokatsiya qidiruvi",
        "en": "Collocation search",
        "ru": "Поиск коллокаций"
    },
    "nav_dictionary": {
        "uz": "Lug‘at",
        "en": "Dictionary",
        "ru": "Словарь"
    },
    "nav_statistics": {
        "uz": "Statistika",
        "en": "Statistics",
        "ru": "Статистика"
    }
}

for k, trans in new_entries.items():
    uz[k] = trans['uz']
    en[k] = trans['en']
    ru[k] = trans['ru']

# Fixes according to TILCOR_04
uz["site_title"] = "TILCOR — O‘zbek–ingliz parallel korpusi"
en["site_title"] = "TILCOR — Uzbek–English Parallel Corpus"
ru["site_title"] = "TILCOR — Узбекско-английский параллельный корпус"

uz["site_subtitle"] = "Kollokatsiyalar tarjimasi tadqiqoti: o‘zbekchadan inglizchaga va inglizchadan o‘zbekchaga"
en["site_subtitle"] = "Collocation translation research: Uzbek-to-English and English-to-Uzbek"
ru["site_subtitle"] = "Исследование перевода коллокаций: с узбекского на английский и с английского на узбекский"

uz["subsec_corpus_candidates"] = "Korpus nomzodlari (±4 soʻz)"
en["subsec_corpus_candidates"] = "Corpus candidates (±4 words)"
ru["subsec_corpus_candidates"] = "Кандидаты из корпуса (±4 слова)"

uz["badge_automatic_candidate"] = "Avtomatik nomzod — lingvistik tekshiruvdan o‘tmagan"
en["badge_automatic_candidate"] = "Automatic candidate — linguistically unverified"
ru["badge_automatic_candidate"] = "Автоматический кандидат — лингвистически не проверен"

with open(os.path.join(locales_dir, 'uz.json'), 'w', encoding='utf-8') as f:
    json.dump(uz, f, ensure_ascii=False, indent=2)

with open(os.path.join(locales_dir, 'en.json'), 'w', encoding='utf-8') as f:
    json.dump(en, f, ensure_ascii=False, indent=2)

with open(os.path.join(locales_dir, 'ru.json'), 'w', encoding='utf-8') as f:
    json.dump(ru, f, ensure_ascii=False, indent=2)

print("Updated locales successfully!")
