# Korpus lug‘atining tanlab tekshiruvi (14.10.2026, v3.6 lug‘ati)

Ishchi hujjat, dissertatsiya matniga kirmaydi. Baholarni sun’iy intellekt (Claude) qo‘ygan; natija platformaning
metodologiya sahifasida (7-band) shu izoh bilan keltirilgan. Bu tadqiqotchi tekshiruvi emas: lug‘at tarjimalarining
inson tekshiruvi «Inson tekshiruvi» bo‘limidagi `dict` vazifasida (200 birlik) bajariladi.

**Nima tekshirildi.** `data/corpus_dictionary.json` (`scripts/build_corpus_dictionary.py`; 1 117 o‘zbekcha va 966 inglizcha
bosh so‘z, 3 168 tarjima) dan tasodifiy 50 ta tarjima: 25 tasi o‘zbekcha–inglizcha, 25 tasi inglizcha–o‘zbekcha qismdan.
Tanlov `scripts/sample_dictionary_check.py` bilan qayta hosil qilinadi (`random.Random(20261014)`, har bir qismdagi barcha
«bosh so‘z — tarjima» juftlari orasidan). Har bir tarjima lug‘atda ko‘rsatiladigan misol gap juftligi bilan baholandi.

**Baholash mezoni** (oldingi tekshiruvdagi bilan bir xil). *To‘g‘ri* — tarjima shu so‘zning matndagi muqobili
(kontekstga xos bo‘lsa ham). *Qisman* — tarjima ibora yoki birikmaning bir qismi, so‘zning o‘zi emas, yoki lug‘at shakli
matndagi ma’noni o‘zgartiradi. *Noto‘g‘ri* — so‘zlar bir-birining tarjimasi emas.

**Natija:** 39 tasi to‘g‘ri, 6 tasi qisman, 5 tasi noto‘g‘ri. Qisman baholarning to‘rttasi birikma yoki ibora ichidagi
so‘zlar (qayta-qayta ↔ again, nazar tashlamoq ↔ look, ovoz chiqarib ↔ aloud, o‘xshagan ↔ same), bittasi inkorning yo‘qolishi
(indamaysan ↔ are silent → indamoq), bittasi personajga ishora (husband ↔ so‘fi). Noto‘g‘ri baholarning uchtasida tarjimon
gapni boshqacha qurgan va so‘z tekislash qo‘shni so‘zni bog‘lagan (beauty ↔ ko‘zli, spend ↔ kecha ikki marta), ikkitasida
lemmalash xatosi qo‘shilgan (qursin → qurmoq; kecha → kechmoq). 2 ta to‘g‘ri tarjimada so‘z lug‘at shakliga keltirilmagan
(yer-suvi, leaned).

**Oldingi tekshiruv bilan solishtirish.** v3.5 lug‘atidagi tanlovda 40 / 8 / 2 chiqqan edi (o‘sha jadval git tarixida saqlanadi).
Lug‘at qayta tuzilgani uchun tanlov boshqa. 50 talik tanlovda bunday farq tasodifiy bo‘lishi mumkin (noto‘g‘ri ulushining
Wilson 95 % oralig‘i: hozir 4,3–21,4 %, avval 1,1–13,5 %), shuning uchun ikkala tekshiruv ham lug‘at sifati yaxshilangani
yoki yomonlashganini ko‘rsatmaydi. Qayta tuzishdagi o‘zgarishlar aniq xato turlarini olib tashlaydi:
(1) grammatik ravish (never, here, very; hech, juda) sifat va ravishdan boshqa so‘zga, yordamchi fe’l (have, make; qilmoq,
bo‘lmoq) fe’ldan boshqa so‘zga tarjima sifatida berilmaydi, teskari yo‘nalishda ham: boshqa shartlardan o‘tadigan 75 ta tarjima
(ko‘ngil ↔ never, yer ↔ here, qo‘l ↔ have kabi) shu qoida bilan chiqdi; (2) oyi «mother» oy «moon, month» dan ajratildi; (3) -si, -lari, -imiz, -ingiz egalik
qo‘shimchali tez-tez uchraydigan shakllar ham lug‘at shakliga keltiriladi (onasi → ona, yelkalari → yelka), yarmi → yarim
kabi unli tushishi ro‘yxatga qo‘shildi; (4) inglizcha n’t, ’s kabi qo‘shimchalar bosh so‘z bo‘lmaydi; (5) misol gap juftligi
ishonchliroq juftlikdan olinadi (ikkala tekislash o‘tishi mos, hunalign bahosi kamida 0,3).

| № | Qism | Bosh so‘z | Tarjima (soni) | Misol: bosh so‘z tomoni | Misol: tarjima tomoni | Baho | Izoh |
|---|---|---|---|---|---|---|---|
| 1 | uz→en | yer-suvi | land (3) | — Uning otasi ham, nihoyati bir ayronchi, **yer-suvi** yo‘q, dastgohi yo‘q. | “Saltanat’s father is just a milk salesman; he has no **land**, no shop. | to‘g‘ri | bosh so‘z lug‘at shakliga keltirilmagan (yer-suv) |
| 2 | uz→en | sarjin | fathom (5) | …a tashladim deb o‘ylagan qarmoqlari ayrim paytlarda oltmish **sarjin** chuqurlikka zo‘rg‘a yetgan bo‘lardi.… | Others let them drift with the current and sometimes they were at sixty **fathoms** when the fishermen thought they were at a hundred. | to‘g‘ri |  |
| 3 | uz→en | foniy | ephemeral (3) | …lg‘ay-to‘lg‘ay, butun vujudi bilan silkina-silkina kuyladi: **Foniy** dunyo be-esh kundir, be-esh kundir, ho-ov, So‘filik ahdi-in sindur, ahdin sindur, ho-ov.… | …ying his head to and fro. He opened his mouth to sing: This **ephemeral** world is ours for five days, only five days, ho-ov, Break your Sufi oath, break it quickly now, … | to‘g‘ri |  |
| 4 | uz→en | uzmoq | cut (4) | U kelinining og‘zidan gapini **uzib** olganday tez gapirardi. | She spoke quickly, **cutting** off her daughter-in-law. | to‘g‘ri | gapini uzmoq ↔ cut off |
| 5 | uz→en | yuzlanmoq | address (4) | Sud raisi, nihoyat, tilmochga **yuzlandi**: | The judge **addressed** the translator. | to‘g‘ri | kontekstga xos: tilmochga yuzlandi ↔ addressed the translator |
| 6 | uz→en | egilmoq | leaned (3) | Miryoqubning qulog‘iga **egildi** | …” Mingboshi **leaned** towards Miryoqub’s ear. | to‘g‘ri | inglizcha so‘z lug‘at shakliga keltirilmagan (lean) |
| 7 | uz→en | qayta-qayta | again (7) | … qattiq yulqib, bir yardcha4     tortib chiqardi, keyin esa **qayta-qayta** yulqib, har yulqishda qo‘llari va jismining bor quvvat-madorini ishga solib, o‘ramni sigir soq… | …hard with both hands, gained a yard of line and then struck **again** and again, swinging with each arm alternately on the cord with all the strength of his arms and the … | qisman | qayta-qayta ↔ again and again: birikmaning bir qismi |
| 8 | uz→en | suyak | bone (8) | **Suyak** qadog‘ining o‘zi nima? | What is a **bone** spur? | to‘g‘ri |  |
| 9 | uz→en | qoramtir | dark (3) | Baliqni tizzasiga siqib oldi va uning **qoramtir** qizil tusli go‘shtini bo‘ynidan tortib to dumigacha uzunasiga tilimlab chiqdi. | He put one knee on the fish and cut strips of **dark** red meat longitudinally from the back of the head to the tail. | to‘g‘ri |  |
| 10 | uz→en | loyiq | worthy (4) | Juda **loyiq**, qobil joyini topib, badavlat, obro‘lik odamga beraman!» | Someone wealthy and esteemed with a **worthy** house for this daughter !” | to‘g‘ri |  |
| 11 | uz→en | to‘g‘ri | correct (4) | Hakimjonning Miryoqubga aytgan quyidagi so‘zlari **to‘g‘ri** edi: «Endi, birdaniga juda boshqacha bo‘lib kelibdi. | Hakimjon had been **correct** when he told Miryoqub: “Sultonxon has returned a different person. | to‘g‘ri |  |
| 12 | uz→en | muallim | teacher (4) | Balki **muallim**, muallima xususida sizga yordam beradilar, yo‘l ko‘rsatadilar. | Maybe they’ll help you find a **teacher**, they’ll show the way.” | to‘g‘ri |  |
| 13 | uz→en | kulish | smile (6) | Zebi kuldi, Xadichaxon ham kuldi: bu **kulishning** ma’nosini faqat kun-dosh ahli o‘zi anglaydi... | Only a co-wife can understand what that **smile** means. | to‘g‘ri | kontekstga xos: kulish «laughing», tarjimonda smile |
| 14 | uz→en | qurmoq | hell (6) | Kambag‘allik **qursin**, ilohim! | Damn poverty to **hell**! | noto‘g‘ri | «qursin» — qarg‘ish (qurimoq), «qurmoq» emas; hell — «damn … to hell» iborasining qismi |
| 15 | uz→en | miya | brain (4) | — E, voy, hali shunaqami?—dedi chol aa pichoqni **miya** bnlan umurtqalar orasiga urdi. | “No?” the old man said and he drove the blade between the vertebrae and the **brain**. | to‘g‘ri |  |
| 16 | uz→en | ehtiyot | carefully (3) | Chol qopni o‘rnashtiribroq qo‘ydi, chilvirni **ehtiyot** bilan yelkasinnng hali lat yemagan qismiga o‘tkazib, butun og‘irlikni yelkasiga tushirdi-yu, baliqning qanchalik … | He adjusted the sack and **carefully** worked the line so that it came across a new part of his shoulders and, holding it anchored with his shoulders, he carefully felt t… | to‘g‘ri | ehtiyot bilan ↔ carefully |
| 17 | uz→en | sariq | yellow (9) | Bu o‘sha, tunda yaltirab ko‘rinadigan **sariq** suv o‘tlarining o‘zginasi edi. | It was the **yellow** Gulf weed that had made so much phosphorescence in the night. | to‘g‘ri |  |
| 18 | uz→en | o‘rtoqjon | friend (4) | — Nimaga, **o‘rtoqjon**? | “Why, **friend**?” | to‘g‘ri |  |
| 19 | uz→en | ko‘z | eye (185) | Odamlarning **ko‘zini** ochsam, deyman. | I want to open people’s **eyes**. | to‘g‘ri |  |
| 20 | uz→en | o‘xshamoq | same (3) | Faqat Maryam allaqaysi bir uyda bir xotin bilan tanishib olib, bizga **o‘xshagan** suhbat boshladi. | Maryam made friends with some woman and is having the **same** kind of conversations that we are. | qisman | bizga o‘xshagan ↔ the same kind of: birikmaning bir qismi |
| 21 | uz→en | o‘rganmoq | learn (7) | Ular yosh turklardan **o‘rgangan**, dedi. | ‘They **learned** from the Young Turks,’ he said. | to‘g‘ri |  |
| 22 | uz→en | kecha | evening (5) | Yerga tushgan uch-to‘rtta xazon yaproqlari kuz **kechasining** sovuq shabadasi bilan yer betida shitir-shitir surinardilar. | The few autumn leaves that had fallen to the ground rustled in the cold **evening** breeze. | to‘g‘ri | kontekstga xos: kuz kechasi ↔ evening |
| 23 | uz→en | itlik | dog (17) | «**Itlik**» bosh ko‘tarib kelardi...» | The **dog** inside him raised its head.” | to‘g‘ri | kontekstga xos: «itlik» ↔ the dog inside him |
| 24 | uz→en | binafsha | purple (9) | Suv to‘q ko‘kimtir, deyarli **binafsha** rang tusga kirdi. | The water was a dark blue now, so dark that it was almost **purple**. | to‘g‘ri |  |
| 25 | uz→en | xonaqo | eshon (4) | Dasturxonni kutmasdan darhol yo‘lga chiqdi va yarim yo‘lni arava bilan bosib, to‘ppa-to‘g‘ri **xonaqoga** bordi. | He took the same cart back to the city and then walked straight to the mosque, but his **eshon** wasn’t there. | noto‘g‘ri | misolda xonaqo «mosque» ga, eshon esa boshqa gapga tegishli |
| 26 | en→uz | oar | eshkak (23) | He shipped his **oars** and brought a small line from under the bow. | U **eshkaklarni** suvdan ko‘tarib qo‘ydi va qayiq burnidagi taxta kat ostidan chilvir oldi. | to‘g‘ri |  |
| 27 | en→uz | trip | safar (3) | …tanat’s home, and only now understood just how costly their **trip** to the village had been for these poor families.… | … joylarini eshitgan, o‘z boshiga balo keltirayozgan qishloq **safarining** bu yo‘qsil xonadonlar uchun juda qimmatga tushganini endi bilgan edi.… | to‘g‘ri |  |
| 28 | en→uz | husband | so‘fi (7) | With one word, she would not just upset her **husband**: she would enrage him. | Buning uchun **so‘fining** achchig‘ini keltiradigan emas, uning bir oz g‘ashini qo‘zg‘ataturgan bir gap aytib qo‘yadi. | qisman | tarjimon personajning unvoni (so‘fi) o‘rniga husband deb bergan: ishora, lug‘aviy tarjima emas |
| 29 | en→uz | table | dasturxon (14) | He won’t refuse me.” Then she looked at Zebi: “You, dear, prepare the house, see your friend in, and set the **table**. | … yuzlandi: — Sen, qizim, uyga joy qil, o‘rtog‘ingni o‘tqiz, **dasturxon** sol.… | to‘g‘ri |  |
| 30 | en→uz | question | so‘roq (5) | O’lmasjon answered the old woman’s **question** with a joke: “I’ve brought a cart of guests from the city! | * * * Kampirchaning **so‘rog‘iga** aravakash hazillashib javob berdi: | to‘g‘ri |  |
| 31 | en→uz | spend | kechmoq (5) | Jakob **spent** the night with me. | «Bu **kecha** Jakob men bilan bo‘ldi. | noto‘g‘ri | spent the night ↔ bu kecha … bo‘ldi: «kecha» «night» ning muqobili va «kechmoq» deb noto‘g‘ri lemmalangan |
| 32 | en→uz | silent | indamoq (5) | “Why are the rest of you **silent**? | — Nega boshqalaring **indamaysan**? | qisman | indamaysan ↔ are silent: lug‘at shakli (indamoq) inkorni yo‘qotadi |
| 33 | en→uz | spend | kecha (5) | “How did I **spend** a whole night with this?” said the woman to herself, biting her lips again. | «Nechuk men butun bir **kechani** shu bilan o‘tkaza oldim?..» dedi xotin 10 Bosma ayilli shim – tasmali (podtyajkali) shim. | noto‘g‘ri | spend a whole night ↔ butun bir kechani o‘tkazmoq: «kecha» «night» ning muqobili |
| 34 | en→uz | meat | go‘sht (14) | Towards the end they served pilaf with flaxseed oil … a little **meat** here and there—not much.” | Oxirida zig‘ir yog‘i palov... bitta-yarimta **go‘sht** uchrasa bor, bo‘lmasa yo‘q... | to‘g‘ri |  |
| 35 | en→uz | ice | muz (5) | The water in the canals has already peeped out from under the **ice**.” | Ariqdagi suv ham **muzning** tagidan chiqdi-ku. | to‘g‘ri |  |
| 36 | en→uz | give | berilmoq (5) | Not much time passed before two of the men mounted new horses and set off again for Qumariq: the order to release Yodgor had been **given**. | Hayal o‘tmay, yigitlardan ikkitasi charchamagan otlardan ikkitasini olib, yana Qumariqqa jo‘nadilar, Yodgorxo‘jani bo‘shatib yuborishga farmon **berilgan** edi. | to‘g‘ri | majhul nisbat: had been given ↔ berilgan edi |
| 37 | en→uz | word | so‘z (76) | Their **words** were inaudible. | **So‘zlari** eshitilmasdi. | to‘g‘ri |  |
| 38 | en→uz | mosque | machit (18) | “Who started the whole mess at the **mosque**? | — **Machitda** gap boshlagan kim bo‘ldi? | to‘g‘ri |  |
| 39 | en→uz | shameful | uyat (3) | He flirts with all of them, saying **shameful** things.” | O‘tgan xotinga gap tashlaydi. **Uyat** gaplarni gapiradi... | to‘g‘ri |  |
| 40 | en→uz | epaulette | pogon (4) | Empire is the **epaulettes**, they say; epaulettes continuously demand money. | — «**pogon**» demak, «pogon» shunday narsaki, doim «pul, pul!» deb turadi. | to‘g‘ri |  |
| 41 | en→uz | break | sindirmoq (5) | We brought Zebi here, and after days and weeks of hardship, we **broke** her will, turned her into a sweet, little lamb and gave her to mingboshi. | Zebixonni keltirdik: qancha qiyinchiliklardan so‘ng uning qaysarligini **sindirib**, qo‘ziday yumshoq-yuvosh va muloyim qilib, mingboshiga topshirdik. | to‘g‘ri |  |
| 42 | en→uz | train | poezd (13) | However it happened, just a few years after the **train** began running, Miryoqub had very little land left. Everything had passed to other people. | Har qalay, **poezd** o‘tgandan keyin, bir necha yil orasida Miryoqubning qo‘lida juda oz yer qoldi, hammasi har kimga o‘tib ketdi. | to‘g‘ri |  |
| 43 | en→uz | kill | o‘ldirmoq (17) | Then I **killed** a June bug, crushed it like a walnut. | Undan keyin xuddi yong‘oqday bitta buzoqboshini **o‘ldirdim**. | to‘g‘ri |  |
| 44 | en→uz | family | oila (16) | 3 Enaxon was the daughter of a poor **family**. | III Enaxon yo‘qsul bir **oilaning** qizi edi. | to‘g‘ri |  |
| 45 | en→uz | close | yaqinroq (7) | Miryoqub moved his chair **closer**; he poured himself some thick tea and put two candies on his plate. | Miryoqub kursini **yaqinroq** jildirdi, chiroyli bir chinayoqqa12 samovardan quyuqqina choy quygach, chinayoq likopchasiga ikkita konfet olib qo‘ydi. | to‘g‘ri | closer ↔ yaqinroq |
| 46 | en→uz | look | nazar (8) | Then he **looked** behind him and saw that no land was visible. | Keyin chol kelgan yo‘liga **nazar** tashladi va yer allaqachon ko‘rinmay ketganini ko‘rdi. | qisman | «nazar tashlamoq» birikmasining qismi |
| 47 | en→uz | chair | kursi (13) | The **chairs** were new and clean. | **Kursilar** — yangi va toza. | to‘g‘ri |  |
| 48 | en→uz | aloud | chiqarmoq (19) | “Galanos,” he said **aloud**. | — Galanos9 , — dedi u ovoz **chiqarib**. | qisman | «ovoz chiqarib» ↔ aloud: birikmaning qismi |
| 49 | en→uz | walk | yurmoq (8) | The girls got up from their spots and began to **walk** around. | Qizlar o‘rinlaridan turib, u yoq-bu yoqqa **yurishib** qoldilar. | to‘g‘ri |  |
| 50 | en→uz | beauty | ko‘zli (3) | Hell, that blue-eyed **beauty** from Petrograd is a witness to the difference! | Ana, Petrograddan kelgan moviy **ko‘zli** dilbar bunga guvoh! | noto‘g‘ri | beauty ↔ dilbar; ko‘zli «eyed» ga tegishli |
