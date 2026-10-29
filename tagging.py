"""tagging.py — Morfologik va semantik teglash (TILCOR v3.9).

Ikki qatlam:
1. MORFOLOGIK teglar — har bir so‘z shakli uchun lemma, so‘z turkumi va qo‘shimchalar zanjiri.
   O‘zbekcha: qoidaga asoslangan tahlil (o‘zbek tili grammatikasidagi atamalar bilan: kelishik, egalik,
   ko‘plik, zamon, mayl, nisbat, sifatdosh, ravishdosh, harakat nomi) va har bir belgining Universal
   Dependencies (UD) morfologik belgisi (Case=Gen, Number=Plur, Tense=Past ...). Tahlil faqat korpusda
   tasdiqlangan o‘zaklarga tayanadi: qo‘shimcha ajratilgach qolgan o‘zak korpus lug‘atida yoki matnlarda
   boshqa qo‘shimchalar bilan uchrashi shart (hech narsa o‘ylab topilmaydi, G1-qoida).
   Inglizcha: spaCy (en_core_web_sm) lemma va UPOS teglari (so‘z tekislash bosqichidan) + fleksiya
   belgilari (Number, Tense, VerbForm, Degree) UD belgilarida.
2. SEMANTIK teglar — inglizcha lemma uchun Princeton WordNet 3.0 leksikograf fayli (supersense:
   noun.body, verb.motion ...; Fellbaum, 1998); o‘zbekcha lemma uchun shu maydon tarjimonning kitobdagi
   so‘zi orqali proyeksiya qilinadi (korpus lug‘ati, KORPUS sinfi). Har bir maydon dissertatsiyaning
   3.1-bandidagi yettita semantik guruhdan biriga qoida bilan xaritalanadi (SEM_GROUP_OF).
   Kollokatsiyaning semantik guruhi asos so‘z (Hausmann, 1984: base) bo‘yicha belgilanadi.

Barcha avtomatik teglar «avtomatik — tadqiqotchi tasdig‘i kutilmoqda» maqomida ko‘rsatiladi va III bob
statistikasiga kirmaydi (S8-qoida). Semantik lug‘at data/tags_index.json da oldindan hisoblangan
(scripts/build_tags_index.py), shuning uchun serverda WordNet talab qilinmaydi.
"""
import collections
import json
import os
import re
import threading
from functools import lru_cache

from word_family import uz_norm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, 'data', 'tags_index.json')
METHOD_LABEL = 'avtomatik'          # every tag of this module is automatic until the researcher confirms it

# =====================================================================================================
# 1. TAGSETS
# =====================================================================================================
# --- so‘z turkumlari (Uzbek codes used across the platform) -> UD UPOS
UZ_POS_UD = {'ot': 'NOUN', 'fe’l': 'VERB', 'sifat': 'ADJ', 'ravish': 'ADV', 'olmosh': 'PRON', 'son': 'NUM',
             'ko‘makchi': 'ADP', 'bog‘lovchi': 'CCONJ', 'yuklama': 'PART', 'modal so‘z': 'ADV', 'undov': 'INTJ',
             'to‘liqsiz fe’l': 'AUX', 'atoqli ot': 'PROPN', 'taqlid so‘z': 'INTJ', 'so‘z turkumi aniqlanmagan': 'X'}
EN_UPOS_UZ = {'NOUN': 'ot', 'VERB': 'fe’l', 'ADJ': 'sifat', 'ADV': 'ravish', 'PRON': 'olmosh', 'NUM': 'son',
              'ADP': 'predlog', 'DET': 'aniqlovchi (determinativ)', 'AUX': 'ko‘makchi fe’l', 'CCONJ': 'bog‘lovchi',
              'SCONJ': 'ergashtiruvchi bog‘lovchi', 'PART': 'yuklama', 'PROPN': 'atoqli ot', 'INTJ': 'undov', 'X': 'aniqlanmagan'}

# --- closed classes of Uzbek (finite lists; Sayfullayeva va boshq., 2009; O‘zbek tili grammatikasi, 1975)
UZ_PRONOUNS = {'men', 'sen', 'u', 'biz', 'siz', 'ular', 'bu', 'shu', 'o‘sha', 'ana', 'mana', 'o‘z', 'kim', 'nima', 'qaysi',
               'qanday', 'qanaqa', 'qachon', 'qayer', 'qayerda', 'qayoqda', 'necha', 'nechta', 'hamma', 'barcha', 'bari',
               'har', 'hech', 'kimdir', 'nimadir', 'allakim', 'allanima', 'unday', 'bunday', 'shunday', 'o‘shanday',
               'ul', 'alar', 'bular', 'shular', 'o‘shalar'}       # o‘z-i, o‘z-lar-i ... are analysed (_pronoun_form)
UZ_NUMERALS = {'bir', 'ikki', 'uch', 'to‘rt', 'besh', 'olti', 'yetti', 'sakkiz', 'to‘qqiz', 'o‘n', 'yigirma', 'o‘ttiz', 'qirq',
               'ellik', 'oltmish', 'yetmish', 'sakson', 'to‘qson', 'yuz', 'ming', 'million', 'milliard', 'yarim', 'chorak',
               'birinchi', 'ikkinchi', 'uchinchi', 'to‘rtinchi', 'beshinchi', 'oltinchi', 'yettinchi', 'ikkala', 'uchala', 'to‘rtala',
               'ikkovi', 'uchovi', 'bitta', 'ikkita', 'uchta', 'to‘rtta', 'beshta', 'o‘nta', 'yuzta', 'mingta'}
UZ_POSTPOSITIONS = {'bilan', 'uchun', 'kabi', 'singari', 'sayin', 'qarab', 'ko‘ra', 'yarasha', 'bo‘yicha', 'qadar', 'tufayli',
                    'chog‘li', 'qaraganda', 'tomon', 'sari', 'keyin', 'so‘ng', 'oldin', 'burun', 'ilgari', 'beri', 'buyon',
                    'boshqa', 'bo‘lak', 'tashqari', 'o‘zga', 'haqida', 'to‘g‘risida', 'orqali', 'bo‘ylab', 'osha', 'uzra'}
UZ_CONJUNCTIONS = {'va', 'hamda', 'ham', 'lekin', 'ammo', 'biroq', 'chunki', 'agar', 'go‘yo', 'toki', 'yoki', 'yo', 'yoxud',
                   'na', 'balki', 'vaholanki', 'holbuki', 'shuning uchun', 'shu sababli', 'gar', 'garchi', 'basharti', 'mabodo',
                   'yohud', 'yoinki', 'binobarin', 'bas'}
UZ_PARTICLES = {'faqat', 'hatto', 'nahotki', 'axir', 'naq', 'xuddi', 'esa', 'ku', 'mi', 'chi', 'da', 'gina', 'kina', 'qina',
                'u', 'yu', 'a', 'ya', 'nahot', 'deb', 'degan'}
UZ_MODALS = {'kerak', 'lozim', 'darkor', 'mumkin', 'shart', 'zarur', 'ehtimol', 'darhaqiqat', 'afsuski', 'albatta', 'xullas',
             'shekilli', 'chog‘i', 'balki', 'haqiqatan', 'aftidan', 'chamasi', 'demak', 'masalan', 'avvalo', 'xayriyat',
             'attang', 'afsus', 'bor', 'yo‘q', 'emas'}
UZ_AUX_VERBS = {'edi', 'ekan', 'emish', 'edim', 'eding', 'edik', 'edingiz', 'edilar', 'ekanman', 'ekansan', 'ekanmiz',
                'ekansiz', 'ekanlar', 'emishlar'}
UZ_INTERJ = {'eh', 'oh', 'voy', 'uh', 'hoy', 'ey', 'obbo', 'uf', 'ha', 'xo‘sh', 'oho', 'e', 'o', 'ehe', 'iye', 'be', 'hoy-hoy',
             'voy-voy', 'xayr', 'rahmat', 'salom', 'assalomu', 'alaykum', 'marhamat', 'ofarin', 'balli', 'barakalla', 'qani'}

# --- nominal suffixes: (suffix, Uzbek label, UD feature)
UZ_CASE = (('ning', 'qaratqich kelishigi', 'Case=Gen'), ('ni', 'tushum kelishigi', 'Case=Acc'),
           ('dan', 'chiqish kelishigi', 'Case=Abl'), ('da', 'o‘rin-payt kelishigi', 'Case=Loc'),
           ('ga', 'jo‘nalish kelishigi', 'Case=Dat'), ('ka', 'jo‘nalish kelishigi', 'Case=Dat'), ('qa', 'jo‘nalish kelishigi', 'Case=Dat'),
           ('gacha', 'chegara ma’nosi (jo‘nalish + -cha)', 'Case=Ter'), ('dagi', 'o‘rin-payt kelishigi + -gi (sifat yasovchi)', 'Case=Loc'),
           ('niki', 'qaratqich-egalik (-niki)', 'Case=Gen'), ('dek', 'o‘xshatish (-dek)', 'Case=Equ'), ('day', 'o‘xshatish (-day)', 'Case=Equ'))
#     -lari is read as ko‘plik -lar + egalik -i (yurak-lar-i-da), as in the school grammar
UZ_POSS = (('imiz', 'egalik, I shaxs ko‘plik', 'Number[psor]=Plur|Person[psor]=1'), ('ingiz', 'egalik, II shaxs ko‘plik', 'Number[psor]=Plur|Person[psor]=2'),
           ('miz', 'egalik, I shaxs ko‘plik', 'Number[psor]=Plur|Person[psor]=1'), ('ngiz', 'egalik, II shaxs ko‘plik', 'Number[psor]=Plur|Person[psor]=2'),
           ('im', 'egalik, I shaxs birlik', 'Number[psor]=Sing|Person[psor]=1'), ('ing', 'egalik, II shaxs birlik', 'Number[psor]=Sing|Person[psor]=2'),
           ('si', 'egalik, III shaxs', 'Person[psor]=3'), ('i', 'egalik, III shaxs', 'Person[psor]=3'),
           ('m', 'egalik, I shaxs birlik', 'Number[psor]=Sing|Person[psor]=1'), ('ng', 'egalik, II shaxs birlik', 'Number[psor]=Sing|Person[psor]=2'))
# phonological condition of a suffix on the stem it follows: 'C' after a consonant, 'V' after a vowel,
# 'k' / 'q' after k / q (yurak-ka, qishloq-qa), 'nkq' after anything but k, q (jo‘nalish -ga)
UZ_SFX_AFTER = {'imiz': 'C', 'ingiz': 'C', 'im': 'C', 'ing': 'C', 'i': 'C', 'miz': 'V', 'ngiz': 'V', 'si': 'V', 'm': 'V', 'ng': 'V',
                'ka': 'k', 'qa': 'q', 'ga': 'nkq', 'gacha': 'nkq'}
# suffixes that identify a noun phrase on their own (used when the stem is not attested in the corpus)
UZ_STRONG_NOMINAL = {'lar', 'ning', 'dan', 'ga', 'ka', 'qa', 'ni', 'gacha', 'dagi', 'imiz', 'ingiz'}
UZ_PLUR = (('lar', 'ko‘plik', 'Number=Plur'),)
UZ_DEGREE = (('roq', 'qiyosiy daraja', 'Degree=Cmp'),)
UZ_PERSON = {'man': ('I shaxs birlik', 'Person=1|Number=Sing'), 'san': ('II shaxs birlik', 'Person=2|Number=Sing'),
             'miz': ('I shaxs ko‘plik', 'Person=1|Number=Plur'), 'siz': ('II shaxs ko‘plik', 'Person=2|Number=Plur'),
             'lar': ('III shaxs ko‘plik', 'Person=3|Number=Plur'), 'm': ('I shaxs birlik', 'Person=1|Number=Sing'),
             'ng': ('II shaxs birlik', 'Person=2|Number=Sing'), 'k': ('I shaxs ko‘plik', 'Person=1|Number=Plur'),
             'ngiz': ('II shaxs ko‘plik', 'Person=2|Number=Plur'), '': ('III shaxs birlik', 'Person=3|Number=Sing')}

# --- verbal endings: (ending, label, UD feats, person group)
#     person group: 'di' = -m/-ng/-k/-ngiz/-lar after -di/-sa; 'full' = -man/-san/-miz/-siz/-lar; None = no person
UZ_VERB_ENDINGS = (
    ('moqda', 'hozirgi zamon davom (-moqda)', 'Tense=Pres|Aspect=Prog', 'full'),
    ('yotir', 'hozirgi zamon davom (-yotir)', 'Tense=Pres|Aspect=Prog', 'full'),
    ('yap', 'hozirgi zamon (-yap)', 'Tense=Pres|Aspect=Prog', 'yap'),
    ('ibdi', 'o‘tgan zamon, eshitilganlik (-ibdi)', 'Tense=Past|Evident=Nfh', 'lar'),
    ('ib', 'o‘tgan zamon, eshitilganlik (-ib + shaxs)', 'Tense=Past|Evident=Nfh', 'fullonly'),
    ('ardi', 'o‘tgan zamon davom (-ar edi)', 'Tense=Past|Aspect=Hab', 'di'),
    ('rdi', 'o‘tgan zamon davom (-r edi)', 'Tense=Past|Aspect=Hab', 'di'),
    ('arkan', 'o‘tgan zamon, eshitilganlik (-ar ekan)', 'Tense=Past|Evident=Nfh', 'full'),
    ('di', 'yaqin o‘tgan zamon (-di)', 'Tense=Past', 'di'),
    ('ti', 'yaqin o‘tgan zamon (-di)', 'Tense=Past', 'di'),
    ('adigan', 'kelasi zamon sifatdoshi (-adigan)', 'VerbForm=Part|Tense=Fut', 'full'),
    ('ydigan', 'kelasi zamon sifatdoshi (-ydigan)', 'VerbForm=Part|Tense=Fut', 'full'),
    ('gan', 'sifatdosh / uzoq o‘tgan zamon (-gan)', 'VerbForm=Part|Tense=Past', 'full'),
    ('kan', 'sifatdosh / uzoq o‘tgan zamon (-kan)', 'VerbForm=Part|Tense=Past', 'full'),
    ('qan', 'sifatdosh / uzoq o‘tgan zamon (-qan)', 'VerbForm=Part|Tense=Past', 'full'),
    ('yotgan', 'hozirgi zamon sifatdoshi (-yotgan)', 'VerbForm=Part|Tense=Pres', 'full'),
    ('ayotgan', 'hozirgi zamon sifatdoshi (-ayotgan)', 'VerbForm=Part|Tense=Pres', 'full'),
    ('yotib', 'hozirgi zamon ravishdoshi (-yotib)', 'VerbForm=Conv|Tense=Pres', None),
    ('moqchi', 'maqsad mayli (-moqchi)', 'Mood=Des', 'full'),
    ('moq', 'harakat nomi (-moq)', 'VerbForm=Inf', None),
    ('mak', 'harakat nomi (-mak)', 'VerbForm=Inf', None),
    ('masdan', 'bo‘lishsiz ravishdosh (-masdan)', 'VerbForm=Conv|Polarity=Neg', None),
    ('maslik', 'bo‘lishsiz harakat nomi (-maslik)', 'VerbForm=Vnoun|Polarity=Neg', None),
    ('mas', 'bo‘lishsiz sifatdosh / kelasi zamon (-mas)', 'VerbForm=Part|Polarity=Neg', 'full'),
    ('gancha', 'ravishdosh (-gancha)', 'VerbForm=Conv', None),
    ('guncha', 'ravishdosh (-guncha)', 'VerbForm=Conv', None),
    ('kuncha', 'ravishdosh (-guncha)', 'VerbForm=Conv', None),
    ('quncha', 'ravishdosh (-guncha)', 'VerbForm=Conv', None),
    ('gach', 'ravishdosh (-gach)', 'VerbForm=Conv', None),
    ('kach', 'ravishdosh (-gach)', 'VerbForm=Conv', None),
    ('qach', 'ravishdosh (-gach)', 'VerbForm=Conv', None),
    ('gani', 'maqsad ravishdoshi (-gani)', 'VerbForm=Conv', None),
    ('gali', 'maqsad ravishdoshi (-gali)', 'VerbForm=Conv', None),
    ('aylik', 'buyruq-istak mayli, I shaxs ko‘plik (-aylik)', 'Mood=Imp|Person=1|Number=Plur', None),
    ('ylik', 'buyruq-istak mayli, I shaxs ko‘plik (-ylik)', 'Mood=Imp|Person=1|Number=Plur', None),
    ('ayin', 'buyruq-istak mayli, I shaxs birlik (-ayin)', 'Mood=Imp|Person=1|Number=Sing', None),
    ('sinlar', 'buyruq-istak mayli, III shaxs ko‘plik (-sinlar)', 'Mood=Imp|Person=3|Number=Plur', None),
    ('sin', 'buyruq-istak mayli, III shaxs (-sin)', 'Mood=Imp|Person=3', None),
    ('inglar', 'buyruq-istak mayli, II shaxs ko‘plik (-inglar)', 'Mood=Imp|Person=2|Number=Plur', None),
    ('ingiz', 'buyruq-istak mayli, II shaxs ko‘plik (-ingiz)', 'Mood=Imp|Person=2|Number=Plur', None),
    ('ing', 'buyruq-istak mayli, II shaxs (-ing)', 'Mood=Imp|Person=2', None),
    ('gin', 'buyruq-istak mayli, II shaxs birlik (-gin)', 'Mood=Imp|Person=2|Number=Sing', None),
    ('sa', 'shart mayli (-sa)', 'Mood=Cnd', 'di'),
    ('ish', 'harakat nomi (-ish)', 'VerbForm=Vnoun', None),
    ('sh', 'harakat nomi (-sh)', 'VerbForm=Vnoun', None),
    ('uv', 'harakat nomi (-uv)', 'VerbForm=Vnoun', None),
    ('ar', 'sifatdosh / kelasi zamon (-ar)', 'VerbForm=Part|Tense=Fut', 'full'),
    ('ur', 'sifatdosh / kelasi zamon (-ur)', 'VerbForm=Part|Tense=Fut', 'full'),
    ('r', 'sifatdosh / kelasi zamon (-r)', 'VerbForm=Part|Tense=Fut', 'full'),
    ('adi', 'hozirgi-kelasi zamon, III shaxs birlik (-a + -di)', 'Tense=Pres|Person=3|Number=Sing', 'lar'),
    ('ydi', 'hozirgi-kelasi zamon, III shaxs birlik (-y + -di)', 'Tense=Pres|Person=3|Number=Sing', 'lar'),
    ('aman', 'hozirgi-kelasi zamon, I shaxs birlik (-a + -man)', 'Tense=Pres|Person=1|Number=Sing', None),
    ('asan', 'hozirgi-kelasi zamon, II shaxs birlik (-a + -san)', 'Tense=Pres|Person=2|Number=Sing', None),
    ('amiz', 'hozirgi-kelasi zamon, I shaxs ko‘plik (-a + -miz)', 'Tense=Pres|Person=1|Number=Plur', None),
    ('asiz', 'hozirgi-kelasi zamon, II shaxs ko‘plik (-a + -siz)', 'Tense=Pres|Person=2|Number=Plur', None),
    ('yman', 'hozirgi-kelasi zamon, I shaxs birlik (-y + -man)', 'Tense=Pres|Person=1|Number=Sing', None),
    ('ysan', 'hozirgi-kelasi zamon, II shaxs birlik (-y + -san)', 'Tense=Pres|Person=2|Number=Sing', None),
    ('ymiz', 'hozirgi-kelasi zamon, I shaxs ko‘plik (-y + -miz)', 'Tense=Pres|Person=1|Number=Plur', None),
    ('ysiz', 'hozirgi-kelasi zamon, II shaxs ko‘plik (-y + -siz)', 'Tense=Pres|Person=2|Number=Plur', None),
    ('ib', 'ravishdosh (-ib)', 'VerbForm=Conv', None),
    ('ub', 'ravishdosh (-ib)', 'VerbForm=Conv', None),
    ('b', 'ravishdosh (-b)', 'VerbForm=Conv', None),
    ('a', 'ravishdosh (-a)', 'VerbForm=Conv', None),
    ('y', 'ravishdosh (-y)', 'VerbForm=Conv', None),
)
# endings that mark a verb form on their own; the others (-a, -y, -b, -ib, -sa, -ar, -ish ...) also end many nouns
# and adjectives and are read as verbal only when the stem has verbal evidence
UZ_STRONG_VERBAL = {'moqda', 'yotir', 'yap', 'ibdi', 'ardi', 'rdi', 'arkan', 'di', 'ti', 'gan', 'kan', 'qan', 'yotgan', 'ayotgan',
                    'adigan', 'ydigan',
                    'yotib', 'moqchi', 'moq', 'mak', 'masdan', 'maslik', 'gancha', 'guncha', 'kuncha', 'quncha', 'gach', 'kach',
                    'qach', 'adi', 'ydi', 'aman', 'asan', 'amiz', 'asiz', 'yman', 'ysan', 'ymiz', 'ysiz', 'sinlar', 'inglar'}
# verb forms that can take nominal suffixes (kel-ish-i-ga, ayt-gan-lar-i)
UZ_NOMINALIZERS = {'ish', 'sh', 'uv', 'gan', 'kan', 'qan', 'yotgan', 'ayotgan', 'adigan', 'ydigan', 'moq', 'mak', 'maslik', 'mas'}
UZ_VOICE = (('tir', 'orttirma nisbat (-tir)', 'Voice=Cau'), ('dir', 'orttirma nisbat (-dir)', 'Voice=Cau'),
            ('gaz', 'orttirma nisbat (-gaz)', 'Voice=Cau'), ('kaz', 'orttirma nisbat (-kaz)', 'Voice=Cau'), ('qaz', 'orttirma nisbat (-qaz)', 'Voice=Cau'),
            ('giz', 'orttirma nisbat (-giz)', 'Voice=Cau'), ('qiz', 'orttirma nisbat (-qiz)', 'Voice=Cau'), ('kiz', 'orttirma nisbat (-kiz)', 'Voice=Cau'),
            ('ish', 'birgalik nisbati (-ish)', 'Voice=Rcp'), ('sh', 'birgalik nisbati (-sh)', 'Voice=Rcp'),
            ('il', 'majhul nisbat (-il)', 'Voice=Pass'), ('in', 'o‘zlik nisbati (-in)', 'Voice=Rfl'),
            ('l', 'majhul nisbat (-l)', 'Voice=Pass'), ('n', 'o‘zlik nisbati (-n)', 'Voice=Rfl'),
            ('t', 'orttirma nisbat (-t)', 'Voice=Cau'), ('ir', 'orttirma nisbat (-ir)', 'Voice=Cau'), ('iz', 'orttirma nisbat (-iz)', 'Voice=Cau'))
UZ_NEG = ('ma', 'bo‘lishsizlik (-ma)', 'Polarity=Neg')
# derivational suffixes shown only for information (the base must itself be attested)
UZ_DERIV = (('lik', 'ot yasovchi (-lik)'), ('chi', 'ot yasovchi (-chi)'), ('siz', 'sifat yasovchi (-siz)'), ('li', 'sifat yasovchi (-li)'),
            ('dor', 'sifat yasovchi (-dor)'), ('kor', 'sifat yasovchi (-kor)'), ('cha', 'kichraytirish / ravish yasovchi (-cha)'),
            ('gina', 'erkalash (-gina)'), ('kina', 'erkalash (-kina)'), ('qina', 'erkalash (-qina)'), ('zor', 'ot yasovchi (-zor)'),
            ('xona', 'ot yasovchi (-xona)'), ('iy', 'sifat yasovchi (-iy)'), ('viy', 'sifat yasovchi (-viy)'))

VOWELS = 'aeiou'
_VOWEL_DROP = {'koʻngl': 'koʻngil', 'oʻgʻl': 'oʻgʻil', 'burn': 'burun', 'qorn': 'qorin', 'ogʻz': 'ogʻiz', 'bagʻr': 'bagʻir',
               'shahr': 'shahar', 'singl': 'singil', 'boʻyn': 'boʻyin', 'oʻrn': 'oʻrin', 'ayr': 'ayir', 'qayn': 'qayin', 'ogʻl': 'ogʻil'}

# =====================================================================================================
# 2. SEMANTIC TAGSET: WordNet lexicographer files (Fellbaum, 1998) -> Uzbek label, 3.1 semantic group
# =====================================================================================================
LEXNAME_UZ = {
    'noun.Tops': 'umumiy tushunchalar', 'noun.act': 'harakat, ish-faoliyat', 'noun.animal': 'hayvonot', 'noun.artifact': 'buyum, inson yaratgan narsa',
    'noun.attribute': 'belgi, xususiyat', 'noun.body': 'tana a’zolari', 'noun.cognition': 'aql, bilish', 'noun.communication': 'muloqot, nutq',
    'noun.event': 'voqea, hodisa', 'noun.feeling': 'his-tuyg‘u', 'noun.food': 'taom, oziq-ovqat', 'noun.group': 'guruh, jamoa',
    'noun.location': 'joy, makon', 'noun.motive': 'sabab, niyat', 'noun.object': 'tabiiy obyekt', 'noun.person': 'shaxs, inson',
    'noun.phenomenon': 'tabiat hodisasi', 'noun.plant': 'o‘simlik', 'noun.possession': 'mulk, egalik', 'noun.process': 'jarayon',
    'noun.quantity': 'miqdor', 'noun.relation': 'munosabat', 'noun.shape': 'shakl', 'noun.state': 'holat', 'noun.substance': 'modda',
    'noun.time': 'vaqt', 'verb.body': 'tana harakati, biologik holat', 'verb.change': 'o‘zgarish', 'verb.cognition': 'aqliy faoliyat',
    'verb.communication': 'nutqiy faoliyat', 'verb.competition': 'kurash, musobaqa', 'verb.consumption': 'iste’mol', 'verb.contact': 'jismoniy ta’sir',
    'verb.creation': 'yaratish', 'verb.emotion': 'his-tuyg‘u', 'verb.motion': 'harakat (siljish)', 'verb.perception': 'idrok, sezgi',
    'verb.possession': 'egalik, berish-olish', 'verb.social': 'ijtimoiy harakat', 'verb.stative': 'holat fe’li', 'verb.weather': 'ob-havo',
    'adj.all': 'sifat (belgi)', 'adj.pert': 'nisbiy sifat', 'adj.ppl': 'sifatdosh-sifat', 'adv.all': 'ravish',
}
# 3.1-band semantik guruhlari (data/phd_corpus.db taxonomies, semantic_group)
SEM_GROUPS = (('inson_ruhiyati', 'Inson his-tuyg‘ulari va ruhiy holati'), ('tabiat_borliq', 'Tabiat va atrof-muhit hodisalari'),
              ('harakat_holat', 'Harakat va jismoniy holat'), ('ijtimoiy_munosabat', 'Ijtimoiy-madaniy munosabatlar'),
              ('nutq_tafakkur', 'Nutqiy va aqliy faoliyat'), ('moddiy_borliq', 'Moddiy buyumlar va maishiy borliq'),
              ('boshqa', 'Boshqa semantik guruh'))
SEM_GROUP_OF = {
    'noun.feeling': 'inson_ruhiyati', 'verb.emotion': 'inson_ruhiyati', 'noun.motive': 'inson_ruhiyati', 'noun.state': 'inson_ruhiyati',
    'noun.animal': 'tabiat_borliq', 'noun.plant': 'tabiat_borliq', 'noun.object': 'tabiat_borliq', 'noun.phenomenon': 'tabiat_borliq',
    'noun.location': 'tabiat_borliq', 'noun.substance': 'tabiat_borliq', 'verb.weather': 'tabiat_borliq', 'noun.time': 'tabiat_borliq',
    'noun.body': 'harakat_holat', 'noun.act': 'harakat_holat', 'noun.event': 'harakat_holat', 'verb.motion': 'harakat_holat',
    'verb.body': 'harakat_holat', 'verb.contact': 'harakat_holat', 'verb.change': 'harakat_holat', 'verb.perception': 'harakat_holat',
    'noun.person': 'ijtimoiy_munosabat', 'noun.group': 'ijtimoiy_munosabat', 'noun.possession': 'ijtimoiy_munosabat',
    'verb.social': 'ijtimoiy_munosabat', 'verb.possession': 'ijtimoiy_munosabat', 'noun.relation': 'ijtimoiy_munosabat',
    'verb.competition': 'ijtimoiy_munosabat',
    'noun.communication': 'nutq_tafakkur', 'verb.communication': 'nutq_tafakkur', 'noun.cognition': 'nutq_tafakkur', 'verb.cognition': 'nutq_tafakkur',
    'noun.artifact': 'moddiy_borliq', 'noun.food': 'moddiy_borliq', 'verb.consumption': 'moddiy_borliq', 'verb.creation': 'moddiy_borliq',
}

# =====================================================================================================
# 3. DATA (precomputed index + corpus dictionary)
# =====================================================================================================
_lock = threading.Lock()
_D = {}


def _index():
    """data/tags_index.json: Uzbek vocabulary and verb stems of the corpus, WordNet fields of the lemmas,
    semantic tags of the collocations. Loaded once; missing file -> empty index (morphology still works)."""
    with _lock:
        if 'idx' not in _D:
            try:
                _D['idx'] = json.load(open(INDEX_PATH, encoding='utf-8'))
            except Exception as e:
                print(f"[!] tags_index.json not loaded: {e}")
                _D['idx'] = {}
            idx = _D['idx']
            _D['vocab'] = idx.get('uz_vocab') or {}
            _D['verb_stems'] = set(idx.get('uz_verb_stems') or [])
            _D['nom_stems'] = set(idx.get('uz_nom_stems') or [])
            _D['pos_stem'] = idx.get('uz_pos_stem') or {}
            _D['pos_form'] = idx.get('uz_pos_form') or {}
            _D['form_en'] = idx.get('uz_form_en') or {}
            _D['apertium'] = idx.get('uz_apertium') or {}
            _D['uz_lex'] = idx.get('uz_lex') or {}
            _D['en_lex'] = idx.get('en_lex') or {}
            _D['colls'] = idx.get('collocations') or {}
            _D['en_forms'] = idx.get('en_forms') or {}
    return _D


def index_meta():
    return (_index()['idx'] or {}).get('_meta') or {}


def _dict_entry(lang, word):
    """Corpus-dictionary entry of a headword or word form (None if absent)."""
    try:
        import corpus_dictionary as CD
        idx = CD.find(lang, word)
        if idx:
            return CD._load()[lang]['entries'][idx[0]]
    except Exception:
        return None
    return None


_DICT_POS_UZ = {'noun': 'ot', 'verb': 'fe’l', 'adj': 'sifat', 'adv': 'ravish'}


def _disp(norm_word):
    """Normalised spelling (ʻ ʼ) -> the spelling used on the site (‘ ’)."""
    return (norm_word or '').replace('ʻ', '‘').replace('ʼ', '’')


def _norm(w):
    return uz_norm((w or '').strip().lower())


def _letters(s):
    return sum(1 for ch in s if ch.isalpha())


def _dict_uz():
    """Corpus-dictionary headwords (normalised) -> (pos, set of the translator's English words)."""
    with _lock:
        if 'dict_uz' not in _D:
            heads = {}
            try:
                cd = json.load(open(os.path.join(BASE_DIR, 'data', 'corpus_dictionary.json'), encoding='utf-8'))
                for e in cd.get('uz') or []:
                    h = _norm(e['head'])
                    heads.setdefault(h, (e.get('pos'), {(t.get('text') or '').lower() for t in e.get('tr') or []}))
            except Exception as ex:
                print(f"[!] corpus_dictionary.json not loaded: {ex}")
            _D['dict_uz'] = heads
    return _D['dict_uz']


# --- phonology: phonemes of a normalised word (digraphs oʻ gʻ sh ch ng count as one sound)
VOWEL_PH = {'a', 'e', 'i', 'o', 'u', 'oʻ'}
SONORANTS = {'r', 'l', 'n', 'm', 'y', 'ng', 'v'}


def phonemes(s):
    out, i = [], 0
    while i < len(s):
        two = s[i:i + 2]
        if two in ('oʻ', 'gʻ', 'sh', 'ch', 'ng'):
            out.append(two)
            i += 2
        else:
            out.append(s[i])
            i += 1
    return out


def valid_verb_stem(stem):
    """An Uzbek verb stem does not end in obstruent + sonorant (*boshl-, *qizl-, *tanl-) or in two obstruents
    (*to‘xt-), except -st / -sht; sonorant + obstruent is allowed (ayt-, qayt-, yugurt-)."""
    ph = phonemes(stem)
    if len(ph) < 2:
        return False
    a, b = ph[-2], ph[-1]
    if a in VOWEL_PH or b in VOWEL_PH:
        return True
    if b in SONORANTS:
        return False
    if a in SONORANTS:
        return True
    return (a, b) in (('s', 't'), ('sh', 't'))


def _sfx_fits(stem, sfx):
    cond = UZ_SFX_AFTER.get(sfx)
    if not cond:
        return True
    ph = phonemes(stem)
    if not ph:
        return False
    last = ph[-1]
    if cond == 'C':
        return last not in VOWEL_PH
    if cond == 'V':
        return last in VOWEL_PH
    if cond == 'nkq':
        return last not in ('k', 'q')
    return last == cond


_NOM_SLOTS = (UZ_CASE, UZ_POSS, UZ_PLUR, UZ_DEGREE)


def nominal_splits(norm):
    """Every reading of a form as stem (+ -roq) (+ -lar) (+ egalik) (+ kelishik), read from the right, each slot optional
    and each suffix under its phonological condition. -> [(raw stem, morphs)], the unsegmented form first.
    Raw = before the k~g / vowel-drop restoration. Pure string analysis (used by build_tags_index too)."""
    out = []

    def rec(cur, slot, morphs):
        out.append((cur, morphs))
        for i in range(slot, len(_NOM_SLOTS)):
            for sfx, label, feats in _NOM_SLOTS[i]:
                if cur.endswith(sfx) and _letters(cur[:-len(sfx)]) >= 2:
                    rest = cur[:-len(sfx)]
                    if _sfx_fits(rest, sfx):
                        rec(rest, i + 1, [{'affix': '-' + sfx, 'label': label, 'ud': feats}] + morphs)

    rec(norm, 0, [])
    return out


def _stem_variants(raw, first_sfx):
    """Stems a raw stem can come from: the vowel drop (koʻngl-i -> koʻngil, oʻrn-i -> oʻrin) and the k~g / q~gʻ
    alternation (yurag-i -> yurak, qishlogʻ-i -> qishloq) before a vowel-initial suffix."""
    out = []
    if first_sfx and first_sfx[0] in VOWELS:
        if raw in _VOWEL_DROP:
            out.append((_VOWEL_DROP[raw], 'drop'))
        out.append((raw, None))
        if raw.endswith('gʻ'):
            out.append((raw[:-2] + 'q', 'alt'))
        elif raw.endswith('g') and not raw.endswith('ng'):
            out.append((raw[:-1] + 'k', 'alt'))
        ph = phonemes(raw)
        if len(ph) >= 3 and ph[-1] not in VOWEL_PH and ph[-2] not in VOWEL_PH:
            for v in ('i', 'u', 'a'):
                out.append((''.join(ph[:-1]) + v + ph[-1], 'drop'))
    else:
        out.append((raw, None))
    return out


@lru_cache(maxsize=65536)
def _dict_nominal_head(stem):
    """A noun/adjective/adverb headword of the corpus dictionary that is not merely the plural or possessive form of
    another attested word (the dictionary has some such headwords: lablari, oʻylar)."""
    h = _dict_uz().get(stem)
    if h is None or h[0] == 'verb':
        return False
    d = _index()
    for raw, morphs in nominal_splits(stem):
        if morphs and all(m['affix'] == '-lar' or m['label'].startswith('egalik') for m in morphs):
            for s, _how in _stem_variants(raw, morphs[0]['affix'][1:]):
                if _letters(s) >= 3 and (s in d['nom_stems'] or d['vocab'].get(s) or (s in _dict_uz() and s != stem)):
                    return False
    return True


def _nom_tier(stem):
    """Evidence that a nominal stem exists: 4 corpus-dictionary noun/adjective/adverb headword, 3 attested by its
    paradigm, 2 occurs as a word form, 0 not attested."""
    d = _index()
    if _dict_nominal_head(stem):
        return 4
    if stem in d['nom_stems']:
        return 3
    if d['vocab'].get(stem):
        return 2
    return 0


_VERB_DERIV = ('la', 'lan', 'lash', 'lat', 'illa')


def _verb_tier(stem):
    """Evidence that a verb stem exists: 4 corpus-dictionary -moq headword, 3 verb stem of the corpus (also with a voice
    suffix on such a stem: koʻr-in), 2 formed with a verb-forming suffix (-la, -lan, -lash; -ar/-ay on an attested
    adjective: koʻk-ar, qora-y), 0 not attested."""
    d = _index()
    if (stem + 'moq') in _dict_uz():
        return 4
    if stem in d['verb_stems']:
        return 3
    for sfx, _l, _f in UZ_VOICE:
        base = stem[:-len(sfx)]
        if stem.endswith(sfx) and _letters(base) >= 2 and (base in d['verb_stems'] or (base + 'moq') in _dict_uz()):
            return 3
    if _letters(stem) >= 4 and stem.endswith(_VERB_DERIV):
        return 2
    if stem.endswith(('ar', 'ay')) and _letters(stem) >= 4 and _nom_tier(stem[:-2]) >= 2:
        return 2
    if stem.endswith('y') and _letters(stem) >= 4 and _nom_tier(stem[:-1]) >= 2 and stem[-2] in VOWELS:
        return 2
    return 0


def _verb_spellings(stem):
    """The stem itself and, if it is not attested, its attested k~q spelling variants (qitikla- ~ qitiqla-)."""
    out = [stem]
    if _verb_tier(stem) < 3:
        for i, ch in enumerate(stem):
            if ch in 'kq':
                alt = stem[:i] + ('q' if ch == 'k' else 'k') + stem[i + 1:]
                if _verb_tier(alt) >= 3:
                    out.append(alt)
    return out


def _voice_morph(stem):
    """Voice suffix shown in the analysis when the stem itself is not a verb of the corpus but its base is."""
    d = _index()
    if stem in d['verb_stems'] or (stem + 'moq') in _dict_uz():
        return None
    for sfx, label, feats in sorted(UZ_VOICE, key=lambda t: -len(t[0])):
        base = stem[:-len(sfx)]
        if stem.endswith(sfx) and _letters(base) >= 2 and (base in d['verb_stems'] or (base + 'moq') in _dict_uz()):
            return {'affix': '-' + sfx, 'label': label, 'ud': feats}
    return None


def _persons(pgroup):
    return {'di': ['m', 'ng', 'k', 'ngiz', 'lar', ''], 'full': ['man', 'san', 'miz', 'siz', 'lar', ''],
            'fullonly': ['man', 'san', 'miz', 'siz'], 'yap': ['man', 'san', 'ti', 'miz', 'siz', 'tilar'],
            'lar': ['lar', '']}.get(pgroup, [''])


def _verb_candidates(norm):
    """Readings as verb stem (+ voice) (+ -ma) + ending (+ person) (+ nominal suffixes after a verbal noun/participle)."""
    out = []
    for rest0, nmorphs in nominal_splits(norm):
        for ending, label, feats, pgroup in UZ_VERB_ENDINGS:
            if nmorphs and ending not in UZ_NOMINALIZERS:
                continue
            for p in (_persons(pgroup) if not nmorphs else ['']):
                full = ending + p
                if not rest0.endswith(full) or len(rest0) == len(full):
                    continue
                rest = rest0[:-len(full)]
                strong = ending in UZ_STRONG_VERBAL or (bool(p) and p != 'lar')
                for neg in (False, True):
                    if neg and (not rest.endswith('ma') or ending in ('mas', 'masdan', 'maslik') or _letters(rest) < 4):
                        continue
                    stem0 = rest[:-2] if neg else rest
                    for stem in _verb_spellings(stem0):
                        pot = None
                        if _verb_tier(stem) < 3 and stem.endswith('ol') and _letters(stem) >= 4:
                            # imkoniyat shakli: oʻt-ol-ma-gan (= oʻta olmagan), the lemma is the main verb
                            base = stem[:-2]
                            if _verb_tier(base) >= 3:
                                stem, pot = base, {'affix': '-ol', 'label': 'imkoniyat shakli (-a ol)', 'ud': 'Mood=Pot'}
                        if not valid_verb_stem(stem):
                            continue
                        tier = _verb_tier(stem)
                        if tier < 2 and not (strong or neg):
                            continue
                        morphs = []
                        vm = _voice_morph(stem) if tier >= 3 else None
                        if vm:
                            morphs.append(vm)
                        if pot:
                            morphs.append(pot)
                        if neg:
                            morphs.append({'affix': '-ma', 'label': UZ_NEG[1], 'ud': UZ_NEG[2]})
                        if pgroup == 'yap':
                            plabel, pfeat = {'man': UZ_PERSON['man'], 'san': UZ_PERSON['san'], 'ti': UZ_PERSON[''], 'miz': UZ_PERSON['miz'],
                                             'siz': UZ_PERSON['siz'], 'tilar': UZ_PERSON['lar']}[p]
                            morphs.append({'affix': '-yap' + p, 'label': label + ', ' + plabel, 'ud': feats + '|' + pfeat})
                        else:
                            morphs.append({'affix': '-' + ending, 'label': label, 'ud': feats})
                            if p:
                                plabel, pfeat = UZ_PERSON[p]
                                morphs.append({'affix': '-' + p, 'label': 'shaxs-son: ' + plabel, 'ud': pfeat})
                            elif pgroup in ('di', 'full') and ending in ('di', 'ti', 'ardi', 'rdi', 'sa', 'moqda', 'yotir'):
                                morphs.append({'affix': '∅', 'label': 'shaxs-son: III shaxs birlik', 'ud': 'Person=3|Number=Sing'})
                        # a verbal noun / participle of an attested verb with case or possessive suffixes (kel-ish-i-ga)
                        nominalized = bool(nmorphs) and tier >= 3
                        out.append({'kind': 'verb', 'stem': stem, 'score': tier if tier >= 2 else 1.5, 'strong': strong or neg or nominalized,
                                    'morphs': morphs + nmorphs, 'ending': ending, 'person': p, 'order': len(full)})
    # a bare verb stem: II person imperative (kel, ber)
    t = _verb_tier(norm)
    if t >= 3:
        out.append({'kind': 'verb', 'stem': norm, 'score': t, 'strong': False, 'ending': '', 'person': '', 'order': 0,
                    'morphs': [{'affix': '∅', 'label': 'buyruq-istak mayli, II shaxs birlik (o‘zak)', 'ud': 'Mood=Imp|Person=2|Number=Sing'}]})
    return out


def _nominal_candidates(norm):
    d = _index()
    out = []
    for raw, morphs in nominal_splits(norm):
        if not morphs:
            if _dict_nominal_head(norm):
                score = 4
            else:
                pf = d['pos_form'].get(norm) or {}
                score = 3 if sum(v for k, v in pf.items() if k != 'VERB') >= 3 and \
                    sum(v for k, v in pf.items() if k != 'VERB') > pf.get('VERB', 0) else 1
            out.append({'kind': 'nom', 'stem': norm, 'score': score, 'morphs': [], 'order': 0})
            continue
        first = morphs[0]['affix'][1:]
        best = None
        for stem, how in _stem_variants(raw, first):
            if _letters(stem) < 2:
                continue
            t = _nom_tier(stem)
            if how == 'drop' and t < 2:
                continue
            if best is None or t > best[1]:
                best = (stem, t)
        if best is None:
            continue
        stem, t = best
        if first == 'i' and any((raw + 'i' + x) in d['vocab'] for x in ('si', 'sini', 'siga', 'sidan', 'sida', 'lar', 'larni', 'lari')):
            # raw+i takes -si / -lar itself (yigʻi-si, yigʻi-lar): the stem ends in i, this -i is not egalik
            continue
        if t == 0:
            # the stem is not in the corpus: the reading stands only on a suffix that marks a noun phrase by itself
            if not any(m['affix'][1:] in UZ_STRONG_NOMINAL for m in morphs) or _letters(raw) < 3:
                continue
            stem, t = raw, 1
        out.append({'kind': 'nom', 'stem': stem, 'score': t, 'morphs': morphs, 'order': len(morphs)})
    return out


_CASE_SFX = {s for s, _l, _f in UZ_CASE} - {'dagi', 'niki'}


_AFTER_STEM = ('lar', 'lari', 'larni', 'larga', 'lardan', 'larning', 'si', 'sini', 'siga', 'sidan', 'sining', 'roq')


def _lexicalized_case_form(form, reading):
    """A form that looks like stem + kelishik is a word of its own when the corpus shows it with plural or possessive
    suffixes (mayda -> maydalar, maydasi): nothing but -gi / -ki follows a case suffix in Uzbek."""
    if not reading['morphs'] or reading['morphs'][-1]['affix'][1:] not in _CASE_SFX:
        return False
    vocab = _index()['vocab']
    return any((form + x) in vocab for x in _AFTER_STEM)


def _best_reading(norm):
    noms = _nominal_candidates(norm)
    verbs = _verb_candidates(norm)
    # plural -lar outweighs the participle -(a)r (oʻy-lar, not oʻyla-r; chavandoz-lar, not chavandozla-r)
    lar = [c for c in noms if any(m['affix'] == '-lar' for m in c['morphs'])]
    if lar:
        top = max(c['score'] for c in lar)
        verbs = [v for v in verbs if not (v['ending'] in ('r', 'ar', 'ur', '') and v['person'] in ('', 'lar')
                                          and (top >= 2 or v['score'] <= 2))]
    zero = next((c for c in noms if not c['morphs']), None)
    if zero:
        for c in noms:
            if c['morphs'] and c['score'] >= zero['score'] and _lexicalized_case_form(norm, c):
                zero['score'] = c['score'] + 0.5
    cands = noms + verbs

    def key(c):
        rank = 1 if c['kind'] == 'nom' else (2 if c['strong'] else 0)
        return (c['score'], rank, c['order'])
    return max(cands, key=key) if cands else None


def _closed_class(norm):
    disp = _disp(norm)
    if disp in UZ_AUX_VERBS:
        return 'to‘liqsiz fe’l', 'AUX'
    if disp in UZ_PRONOUNS:
        return 'olmosh', 'PRON'
    if disp in UZ_NUMERALS or re.fullmatch(r'\d+(-?(nchi|inchi))?', disp):
        return 'son', 'NUM'
    if disp in UZ_POSTPOSITIONS:
        return 'ko‘makchi', 'ADP'
    if disp in UZ_CONJUNCTIONS:
        return 'bog‘lovchi', 'CCONJ'
    if disp in UZ_PARTICLES:
        return 'yuklama', 'PART'
    if disp in UZ_MODALS:
        return 'modal so‘z', 'ADV'
    if disp in UZ_INTERJ:
        return 'undov', 'INTJ'
    return None


# pronoun stems before case suffixes: u-ning but un-ga / un-da / un-dan, bu > bun-, shu > shun-; men-ing / sen-ing
_PRON_STEM = {'un': 'u', 'bun': 'bu', 'shun': 'shu', 'oʻshan': 'oʻsha'}
_PRON_SPECIAL = {'mening': ('men', '-ing'), 'sening': ('sen', '-ing'), 'meniki': ('men', '-iki'), 'seniki': ('sen', '-iki'),
                 'bizniki': ('biz', '-niki'), 'sizniki': ('siz', '-niki')}


def _pronoun_form(norm):
    """Personal / demonstrative pronoun + (-lar) + (egalik) + kelishik (menda, ularni, unga, mening) -> (lemma, morphs)."""
    if norm in _PRON_SPECIAL:
        lem, sfx = _PRON_SPECIAL[norm]
        return lem, [{'affix': sfx, 'label': 'qaratqich kelishigi' if sfx == '-ing' else 'qaratqich-egalik (-niki)', 'ud': 'Case=Gen'}]
    best = None
    splits = list(nominal_splits(norm))
    for sfx, label, feats in UZ_CASE:          # one-letter stem u (u-ni, u-ning), not produced by nominal_splits
        if norm == 'u' + sfx:
            splits.append(('u', [{'affix': '-' + sfx, 'label': label, 'ud': feats}]))
    for raw, morphs in splits:
        if not morphs:
            continue
        stem = _PRON_STEM.get(raw, raw)
        if raw in _PRON_STEM and morphs[0]['affix'] not in ('-ga', '-da', '-dan', '-day', '-dek', '-dagi', '-gacha'):
            continue
        if _disp(stem) in UZ_PRONOUNS and (best is None or len(morphs) < len(best[1])):
            if stem.endswith('lar') and _disp(stem[:-3]) in UZ_PRONOUNS:     # ular-ni -> u + -lar + -ni
                morphs = [{'affix': '-lar', 'label': 'ko‘plik', 'ud': 'Number=Plur'}] + morphs
                stem = stem[:-3]
            best = (stem, morphs)
    return best


def _deriv_note(stem):
    for sfx, label in sorted(UZ_DERIV, key=lambda t: -len(t[0])):
        if stem.endswith(sfx) and _letters(stem) - len(sfx) >= 3:
            base = stem[:-len(sfx)]
            if _nom_tier(base) >= 2 or _verb_tier(base) >= 3:
                return {'affix': '-' + sfx, 'label': label, 'ud': 'Derivation=' + sfx}
    return None


_UPOS_UZ = {'NOUN': 'ot', 'ADJ': 'sifat', 'ADV': 'ravish'}
# derivational suffixes that fix the part of speech (the base before them must be attested)
_POS_CUES = (('shunoslik', 'ot'), ('garchilik', 'ot'), ('xona', 'ot'), ('iston', 'ot'), ('lik', 'ot'), ('chi', 'ot'),
             ('zor', 'ot'), ('dosh', 'ot'), ('kash', 'ot'), ('goh', 'ot'),
             ('simon', 'sifat'), ('chan', 'sifat'), ('ona', 'sifat'), ('viy', 'sifat'), ('siz', 'sifat'), ('li', 'sifat'),
             ('iy', 'sifat'), ('dor', 'sifat'), ('kor', 'sifat'), ('lab', 'ravish'))


def _stem_pos(stem):
    """Part of speech of a nominal stem: a derivational suffix on an attested base (birlik, chiroyli, ertalab); then the
    word alignment (UPOS of the translator's English word for the bare form) when it rests on at least three links;
    then the corpus dictionary and the platform's resolver; ot by default.
    Uzbek adjectives are routinely rendered by English adverbs (qattiq 'hard', yolgʻiz 'alone'), so the alignment
    makes a word ravish only when four fifths of its adjective/adverb links are adverbs."""
    d = _index()
    for sfx, pos in _POS_CUES:
        if stem.endswith(sfx) and _letters(stem) - len(sfx) >= 2:
            base = stem[:-len(sfx)]
            if _nom_tier(base) >= 2 or _verb_tier(base) >= 3:
                return pos
    c = collections.Counter()
    src = d['pos_form'].get(stem) or {}
    if sum(v for k, v in src.items() if k in _UPOS_UZ) < 3:
        src = d['pos_stem'].get(stem) or src
    for k, v in src.items():
        if k in _UPOS_UZ:
            c[k] += v
    n = sum(c.values())

    def from_alignment():
        """(pos, share of the links behind it) or (None, 0)."""
        q = c['ADJ'] + c['ADV']
        if q > c['NOUN']:
            return ('ravish' if c['ADV'] >= 0.8 * q else 'sifat'), q / n
        if c['NOUN'] / n >= 0.6:
            return 'ot', c['NOUN'] / n
        return None, 0
    ap = d['apertium'].get(stem) or {}
    cur = [_UPOS_UZ[p] for p in ap.get('cur', []) if p in _UPOS_UZ]
    if n >= 3:
        al, share = from_alignment()
        # the hand-made Apertium entry decides unless the alignment agrees with it or is overwhelming (3/4 of the links)
        if al and (not cur or al in cur or share >= 0.75):
            return al
    if len(cur) == 1:
        return cur[0]
    if cur:
        return max(cur, key=lambda p: c[{'ot': 'NOUN', 'sifat': 'ADJ', 'ravish': 'ADV'}[p]])
    h = _dict_uz().get(stem)
    if h is not None and h[0] in _DICT_POS_UZ and h[0] != 'verb':
        return _DICT_POS_UZ[h[0]]
    if n >= 2:
        return from_alignment()[0] or 'ot'
    auto = [_UPOS_UZ[p] for p in ap.get('auto', []) if p in _UPOS_UZ]
    if len(auto) == 1:
        # an automatically added Apertium entry: weakest evidence, used only when nothing else is known
        return auto[0]
    try:
        from search_engine import resolve_uzbek
        _lem, p = resolve_uzbek(_disp(stem))
        if p in ('ot', 'sifat', 'ravish'):
            return p
    except Exception:
        pass
    return 'ot'


def _feats(morphs):
    return '|'.join(sorted(set(f for m in morphs for f in m['ud'].split('|') if f and not f.startswith('Derivation'))))


@lru_cache(maxsize=65536)
def uz_analyze(surface):
    """Morphological analysis of one Uzbek word form.
    -> {'surface', 'lemma', 'pos', 'upos', 'morphs': [{'affix','label','ud'}], 'ud': 'feat|feat', 'method'}"""
    raw = (surface or '').strip(' .,;:!?«»"“”()')
    norm = _norm(raw)
    out = {'surface': raw, 'lemma': _disp(norm), 'pos': 'so‘z turkumi aniqlanmagan', 'upos': 'X', 'morphs': [], 'ud': '', 'method': METHOD_LABEL}
    if not norm or not re.search(r'[a-zʻʼ]', norm):
        return out
    if '-' in norm:
        a, b = norm.split('-', 1)
        if a == b:
            out.update(pos='ravish', upos='ADV',
                       morphs=[{'affix': '-', 'label': 'takroriy so‘z (to‘liq takror)', 'ud': ''}])
        elif len(a) >= 2 and a[-1] in 'pmbs' and b.startswith(a[:-1]) and '-' not in b:
            # intensive form of an adjective (koʻm-koʻk, qip-qizil, op-oq): the lemma is the adjective
            sub = uz_analyze(_disp(b))
            out.update(lemma=sub['lemma'], pos='sifat', upos='ADJ',
                       morphs=[{'affix': _disp(a) + '-', 'label': 'kuchaytirma shakl (qisman takror)', 'ud': 'Degree=Abs'}] + sub['morphs'])
            out['ud'] = _feats(out['morphs'])
        else:
            out.update(pos='juft / takroriy so‘z', upos='X',
                       morphs=[{'affix': '-', 'label': 'juft yoki takroriy so‘z (tahlilga olinmaydi, 1.1.4)', 'ud': ''}])
        return out
    cc = _closed_class(norm)
    if cc:
        out['pos'], out['upos'] = cc
        if norm.endswith('lar') and _disp(norm[:-3]) in UZ_PRONOUNS:
            out['lemma'] = _disp(norm[:-3])
            out['morphs'] = [{'affix': '-lar', 'label': 'ko‘plik', 'ud': 'Number=Plur'}]
            out['ud'] = 'Number=Plur'
        return out
    pr = _pronoun_form(norm)
    if pr:
        out.update(lemma=_disp(pr[0]), pos='olmosh', upos='PRON', morphs=pr[1], ud=_feats(pr[1]))
        return out
    try:
        from search_engine import KNOWN_NAMES
        if raw[:1].isupper() and (_disp(norm) in KNOWN_NAMES or norm in KNOWN_NAMES):
            out['pos'], out['upos'] = 'atoqli ot', 'PROPN'
            return out
    except Exception:
        pass
    best = _best_reading(norm)
    if best is None:
        return out
    morphs = list(best['morphs'])
    if best['kind'] == 'verb':
        out.update(lemma=_disp(best['stem']) + 'moq', pos='fe’l', upos='VERB', morphs=morphs)
    else:
        stem = best['stem']
        # plural, possessive and case suffixes make the word a noun (an adjective with them is substantivised)
        inflected = any(m['affix'] != '-dagi' and (m['affix'] == '-lar' or m['label'].startswith(
            ('egalik', 'qaratqich', 'tushum', 'jo‘nalish', 'chiqish', 'o‘rin-payt', 'chegara'))) for m in morphs)
        pos = 'ot' if inflected else _stem_pos(stem)
        dn = _deriv_note(stem)
        if dn:
            morphs.insert(0, dn)
        out.update(lemma=_disp(stem), pos=pos, upos=UZ_POS_UD.get(pos, 'X'), morphs=morphs)
    out['ud'] = _feats(morphs)
    out['score'] = best['score']
    return out


# =====================================================================================================
# 5. ENGLISH MORPHOLOGICAL ANALYSIS (spaCy lemma/UPOS from the alignment stage + inflection features)
# =====================================================================================================
_IRREG_PAST = {'was', 'were', 'went', 'came', 'saw', 'took', 'gave', 'made', 'said', 'thought', 'felt', 'knew', 'got', 'had',
               'did', 'stood', 'sat', 'ran', 'held', 'began', 'brought', 'caught', 'fell', 'found', 'kept', 'left', 'lost', 'met',
               'put', 'read', 'rose', 'sent', 'shook', 'slept', 'spoke', 'struck', 'swam', 'threw', 'told', 'understood', 'woke', 'wore',
               'won', 'wrote', 'ate', 'drank', 'drew', 'drove', 'flew', 'forgot', 'grew', 'heard', 'hit', 'hung', 'laid', 'lay', 'led',
               'let', 'lit', 'meant', 'paid', 'rode', 'sang', 'sank', 'shone', 'shot', 'showed', 'sold', 'spent', 'spread', 'sprang',
               'stuck', 'swung', 'taught', 'tore', 'bent', 'bit', 'blew', 'broke', 'built', 'burst', 'bought', 'chose', 'clung', 'cut',
               'dug', 'fed', 'fought', 'froze', 'hid', 'knelt', 'lent', 'set', 'shut', 'slid', 'smelt', 'spat', 'spun', 'stole', 'stung',
               'swept', 'swore', 'thrust', 'trod', 'wound', 'bore', 'beat', 'became', 'bled', 'bound', 'bred', 'crept', 'dealt', 'dreamt',
               'leant', 'leapt', 'lain', 'slew', 'sought', 'strode', 'strove', 'sweated', 'wept', 'wrung'}
_IRREG_PART = {'been', 'gone', 'seen', 'taken', 'given', 'known', 'done', 'begun', 'broken', 'chosen', 'drunk', 'driven', 'eaten',
               'fallen', 'flown', 'forgotten', 'frozen', 'grown', 'hidden', 'ridden', 'risen', 'shaken', 'shown', 'spoken', 'stolen',
               'sworn', 'thrown', 'torn', 'woken', 'worn', 'written', 'swum', 'sung', 'sunk', 'struck', 'bitten', 'beaten', 'blown',
               'borne', 'born', 'lain', 'laid', 'sewn', 'sown', 'swollen', 'trodden', 'woven', 'arisen', 'awoken', 'bound', 'drawn'}


def _en_lookup(surface):
    """(lemma, UPOS) of an English surface form as the alignment stage saw it most often; None if unseen."""
    r = _index()['en_forms'].get(surface.lower())
    return tuple(r) if r else None


@lru_cache(maxsize=65536)
def en_analyze(surface, lemma=None, upos=None):
    raw = (surface or '').strip(' .,;:!?"“”()')
    low = raw.lower()
    out = {'surface': raw, 'lemma': low, 'pos': 'aniqlanmagan', 'upos': 'X', 'morphs': [], 'ud': '', 'method': METHOD_LABEL}
    if not low:
        return out
    if not (lemma and upos):
        seen = _en_lookup(low)
        if seen:
            lemma, upos = seen
    if not (lemma and upos):
        try:
            from search_engine import resolve_english
            lem, p = resolve_english(low)
            lemma = lem or low
            upos = {'noun': 'NOUN', 'verb': 'VERB', 'adjective': 'ADJ', 'adverb': 'ADV'}.get(p, 'X')
        except Exception:
            lemma, upos = low, 'X'
    lemma = (lemma or low).lower()
    morphs = []
    if upos == 'NOUN':
        if low != lemma and low.endswith('s'):
            morphs.append({'affix': '-s', 'label': 'ko‘plik', 'ud': 'Number=Plur'})
        elif low != lemma and low.endswith(('ren', 'men', 'ice', 'eeth', 'eet', 'ese')):
            morphs.append({'affix': '(ichki o‘zgarish)', 'label': 'ko‘plik (noto‘g‘ri shakl)', 'ud': 'Number=Plur'})
        else:
            morphs.append({'affix': '∅', 'label': 'birlik', 'ud': 'Number=Sing'})
    elif upos in ('VERB', 'AUX'):
        if low.endswith('ing') and low != lemma:
            morphs.append({'affix': '-ing', 'label': 'gerundiy / hozirgi zamon sifatdoshi', 'ud': 'VerbForm=Ger|Tense=Pres'})
        elif low in _IRREG_PART and low not in ('was', 'were'):
            morphs.append({'affix': '(noto‘g‘ri shakl)', 'label': 'o‘tgan zamon sifatdoshi', 'ud': 'VerbForm=Part|Tense=Past'})
        elif low.endswith('ed') and low != lemma or low in _IRREG_PAST:
            morphs.append({'affix': '-ed' if low.endswith('ed') else '(noto‘g‘ri shakl)', 'label': 'o‘tgan zamon', 'ud': 'Tense=Past|VerbForm=Fin'})
        elif low.endswith('s') and low != lemma:
            morphs.append({'affix': '-s', 'label': 'hozirgi zamon, III shaxs birlik', 'ud': 'Tense=Pres|Person=3|Number=Sing|VerbForm=Fin'})
        else:
            morphs.append({'affix': '∅', 'label': 'asosiy shakl (hozirgi zamon / infinitiv)', 'ud': 'VerbForm=Inf'})
    elif upos == 'ADJ':
        if low.endswith('est') and low != lemma:
            morphs.append({'affix': '-est', 'label': 'orttirma daraja', 'ud': 'Degree=Sup'})
        elif low.endswith('er') and low != lemma:
            morphs.append({'affix': '-er', 'label': 'qiyosiy daraja', 'ud': 'Degree=Cmp'})
        else:
            morphs.append({'affix': '∅', 'label': 'oddiy daraja', 'ud': 'Degree=Pos'})
    elif upos == 'ADV' and low.endswith('ly') and len(low) > 4:
        morphs.append({'affix': '-ly', 'label': 'ravish yasovchi', 'ud': 'Derivation=ly'})
    out.update(lemma=lemma, pos=EN_UPOS_UZ.get(upos, 'aniqlanmagan'), upos=upos, morphs=morphs)
    out['ud'] = '|'.join(sorted(set(f for m in morphs for f in m['ud'].split('|') if f and not f.startswith('Derivation'))))
    return out


def analyze(lang, surface):
    return uz_analyze(surface) if lang == 'uz' else en_analyze(surface)


# =====================================================================================================
# 6. SEMANTIC TAGS
# =====================================================================================================
def _lex_entry(lang, lemma):
    d = _index()
    table = d['uz_lex'] if lang == 'uz' else d['en_lex']
    key = _norm(lemma) if lang == 'uz' else (lemma or '').lower()
    r = table.get(key)
    if r is None and lang == 'uz' and key.endswith('moq'):
        r = table.get(key[:-3])
    return r


def semantic(lang, lemma):
    """-> {'field': 'noun.body', 'field_uz': 'tana a’zolari', 'group': 'harakat_holat', 'group_uz': '...',
           'method': 'WordNet 3.0 leksikograf fayli' | 'proyeksiya ...', 'via': english word (uz only)} or None"""
    r = _lex_entry(lang, lemma)
    if not r or not r.get('field'):
        return None
    field = r['field']
    group = SEM_GROUP_OF.get(field, 'boshqa')
    out = {'field': field, 'field_uz': LEXNAME_UZ.get(field, field), 'group': group, 'group_uz': dict(SEM_GROUPS)[group],
           'status': 'avtomatik'}
    if lang == 'uz':
        out['via'] = r.get('via')
        out['method'] = 'proyeksiya'
    else:
        out['method'] = 'wordnet'
    return out


def word_tags(lang, surface):
    """Morphology + semantics of one word form, as the pages show it."""
    m = analyze(lang, surface)
    m = dict(m)
    m['sem'] = semantic(lang, m['lemma']) if m['upos'] in ('NOUN', 'VERB', 'ADJ', 'ADV', 'PROPN') or lang == 'uz' else None
    return m


def collocation_tags(item):
    """Tags of a corpus collocation (index entry): precomputed semantic group + live component analyses."""
    d = _index()
    pre = d['colls'].get(item.get('id') or '') or {}
    lang = item.get('lang') or 'uz'
    comps = []
    words = (item.get('lemma') or '').split()
    base = item.get('base') or ''
    for w in words:
        a = dict(analyze(lang, w))
        a['role'] = 'asos' if (w == base or (lang == 'uz' and _norm(w) == _norm(base))) else 'kollokat'
        a['sem'] = semantic(lang, a['lemma'])
        comps.append(a)
    if base and not any(c['role'] == 'asos' for c in comps):
        # base stored with possessive (o‘rni) or as a different form: mark the component whose stem matches
        for c in comps:
            if _norm(c['lemma']).startswith(_norm(base)[:4]) or _norm(base).startswith(_norm(c['lemma'])[:4]):
                c['role'] = 'asos'
                break
    return {'group': pre.get('group'), 'group_uz': dict(SEM_GROUPS).get(pre.get('group') or '', ''), 'field': pre.get('field'),
            'field_uz': LEXNAME_UZ.get(pre.get('field') or '', ''), 'method': pre.get('method'), 'status': 'avtomatik',
            'base_pos': pre.get('base_pos'), 'components': comps,
            'forms': [(f, analyze_form_chain(lang, f)) for f in list((item.get('forms') or {}).keys())[:6]]}


def analyze_form_chain(lang, phrase):
    """Short morphological gloss of a multi-word surface form: 'yuragi = yurak + -i (egalik, III shaxs)'."""
    parts = []
    for w in re.findall(r"[\wʻʼ‘’'-]+", phrase):
        a = analyze(lang, w)
        if a['morphs'] and any(m['affix'] not in ('∅',) for m in a['morphs']):
            parts.append('%s = %s %s' % (w, a['lemma'], ' '.join('+ %s' % m['affix'] for m in a['morphs'] if m['affix'] != '∅')))
    return '; '.join(parts)


def group_counts(items):
    """Number of collocations of the index per semantic group (for the filter chips)."""
    d = _index()
    c = collections.Counter()
    for it in items:
        g = (d['colls'].get(it['id']) or {}).get('group')
        if g:
            c[g] += 1
    return c


def group_of(item_id):
    return (_index()['colls'].get(item_id) or {}).get('group')
