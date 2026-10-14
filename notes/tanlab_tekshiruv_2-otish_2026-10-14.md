# Ikkinchi o‘tish tekislashining tanlab tekshiruvi (14.10.2026)

Ishchi hujjat, dissertatsiya matniga kirmaydi. Baholarni sun’iy intellekt (Claude) qo‘ygan; natijalar platformaning
metodologiya sahifasida shu izoh bilan keltirilgan. Birinchi o‘tish bo‘yicha oldingi tekshiruv:
`notes/tanlab_tekshiruv_muqobillar_2026-10-14.md` (u endi tarixiy hujjat).

**Ikkinchi o‘tish.** `scripts/build_hunalign_lexicon.py` birinchi o‘tish juftliklarining so‘z tekislashidan 1 114 ta
so‘z juftini oldi (kamida 4 marta va ikkala so‘z bog‘lanishlarining kamida 10 foizi); `scripts/realign_hunalign.py
--lexicon data/hunalign_lexicon.json --base full_corpus.before_hunalign.json` shu lug‘at bilan qayta tekisladi.
Natija: 10 076 juftlik (birinchi o‘tishda 10 096); 9 018 juftlik ikkala o‘tishda bir xil, taxminan 1 000 tasi o‘zgardi.

## A. Ikki o‘tish farq qilgan 30 ta tasodifiy joy (random.Random(7))

Natija: 22 tasida ikkinchi o‘tish to‘g‘riroq, 6 tasida birinchi o‘tish to‘g‘riroq, 2 tasida farq yo‘q.
Birinchi o‘tish yutgan hollarning ko‘pi — ikkinchi o‘tish 2:1 juftlikni 1:1 qilib, bir gapni juftsiz qoldirgan joylar.

| № | Asliyatdagi gap | Ikkinchi o‘tish | Birinchi o‘tish | To‘g‘riroq |
|---|---|---|---|---|
| 1 | Bu nomerga keladigan kishilar faqat ayshu ishrat uchungina to‘xtalardilar. | People stopped here solely for debauchery. | For that reason, behind the front gates were several small rooms. | ikkinchi |
| 2 | But there was not much of it. | Ammo tezda hammasi o‘tib ketdi. | U okeanga tupurib dedi: | ikkinchi |
| 3 | Oradan bir hafta o‘tar-o‘tmas, bezovtalik harakatga va ishga aylandi. | Not a week went by before Miryoqub set to work. | (no old pair with this source) | ikkinchi |
| 4 | Sevganiga qovushgan yosh | It is the song of a young creature who has finally been linked with her love! | It is the song of a young creature who has finally been linked with her love! | birinchi |
| 5 | — Avaxtaga olib borgandan keyin ko‘rsatadi. | “They’ll let you see them after you have been processed.” | … Can I see them?” | ikkinchi |
| 6 | Salti zo‘r bilan o‘zini bosib oldi. Ikkalasi yana — ko‘zlarini miltillatib | Saltanat controlled herself only with difficulty. | (no old pair with this source) | ikkinchi |
| 7 | Arava yakka qanotli kichkinagina bir eshik oldida to‘xtab, aravakash bola qamchi sopi bilan eshikni qoqqanda va ichkaridan bir kampirning i… | O’lmasjon knocked on the door with the hilt of his knout and the tiny, weak voice of an old woman called out “Who’s there?” The village was… | The cart stopped in front of a small door. O’lmasjon knocked on the door with the hilt of his knout and the tiny, weak voice of an old woma… | birinchi |
| 8 | The bird had flown up when the line jerked and the old man had not even seen him go. He felt the line | Chilvir yulqingan paytda qush uchib ketgan edi. Uning qanday g‘oyib bo‘lganini chol hatto payqamay qoldi. | Chilvir yulqingan paytda qush uchib ketgan edi. | ikkinchi |
| 9 | — Obbo, yana bitga arizachi keldi. | “Oh-ho, another petitioner. | …” “Oh-ho, another petitioner. | farq yo‘q |
| 10 | — Mayli, siz o‘zingiz bilasiz, oyi. | You know best, Mother. | “Agreed. | ikkinchi |
| 11 | Bu — bir. | That was the first thing. | To stop her inapposite shivering on this stifling summer night. | ikkinchi |
| 12 | O‘ylar bulut ustiga mingashgan bulutday mujmal va rangsiz edilar. | But he still couldn’t gather his vague and ill-defined thoughts, which were like clouds mounting clouds. | He lay down on the rug and put his hands under his head. | ikkinchi |
| 13 | — Ha barakalla, bor ekansizlar-ku! O‘rtaga olinglar ashulachini! | “Yes, very good, she is among you! | (no old pair with this source) | ikkinchi |
| 14 | He leaned over the side and pulled loose a piece of the meat of the fish where the shark had cut him. | U bortdan egilib, baliqning akula g‘ajigan yeridan bir luqma go‘sht uzib oldi. | (no old pair with this source) | ikkinchi |
| 15 | Maryamga va’dam bor edi, vagonda chirog‘lar yoqilgach, xayrlashib, uyimga ketdim». | When they started turning the lights on in the car, I left for our compartment. | I made a promise to Maryam. When they started turning the lights on in the car, I left for our compartment. | birinchi |
| 16 | Ota u tomonda qah-qah otib kuldi. | The father could only laugh vociferously. | Source: Turkestanskii al’bom: Chast’ etnograficheskaia, 1871–2. | ikkinchi |
| 17 | Qurvonbibi so‘zdan to‘xtamay, balki ovozini yana ham ko‘tara tushgan edi, so‘fi o‘zining odatdagi kalta so‘zlaridan bittasini arang og‘zida… | Qurvonbibi didn’t relent; she raised her voice further still. | Qurvonbibi didn’t relent; she raised her voice further still. Razzoq-sufi almost let out one of his laconicisms, but decided it would be be… | birinchi |
| 18 | boshlariga ko‘taradilar. Har to‘g‘rida uning talablariga xursandlik bilan ko‘nib, hech bir ishda ko‘nglini qoldirmaslikka tirishadilar. | Xolmat put so much energy into his work, and because he was supporting the household by himself, the two women tried to accept his every de… | (no old pair with this source) | ikkinchi |
| 19 | O‘zi ham, 27— 28 dan nari emasdir? — 27 da bo‘lsa kerak. | She can’t be too much older than twenty-seven or twenty-eight.” | (no old pair with this source) | ikkinchi |
| 20 | Lekin buning uchun uylanib o‘tirish kerakmi? Bekorchi xarxashani | But do you really have to get married again and again? | (no old pair with this source) | ikkinchi |
| 21 | Bir marta boshlangandan keyin undan narisi o‘zi keta beradi, deb o‘ylardi Salti. | Moreover, she managed a promise from Zebi that if the other girls began singing first, then Zebi would join. | Saltanat managed to calm her friend. Moreover, she managed a promise from Zebi that if the other girls began singing first, then Zebi would… | farq yo‘q |
| 22 | — Bilib gapirasizmi, xo‘jayin? | “Do you think about what you’re saying, master? | “Do you think about what you’re saying, master? | ikkinchi |
| 23 | Ularning injiqliklarini butunlay haqsiz deyish to‘g‘ri bo‘lmasa kerak. | It wouldn’t be right to say that their caprices were completely without merit. | After all, they were young; and, like their peers, they had dreams and aspirations. | ikkinchi |
| 24 | Men chidayolmadim: «Yo‘q, dedim, musulmon odamdan «millating nima?» deb so‘ralsa, «Millatim Ibrohim Halillullo» deb javob berishi vojib. Di… | ‘No,’ I told him, ‘if you ask a Muslim what his nation is, it is incumbent upon him to say the nation of Ibrahim. | At first, he said Islam, then he said Islamic and Turkic, adding Turkic for some reason. | ikkinchi |
| 25 | Bitta choy damlab beray. | I’ll give you some tea. | (no old pair with this source) | ikkinchi |
| 26 | — degandan keyingina Zebining tillari qaldiradi: | Bring your singer here!” he said. | Zebi finally moved her tongue, “Let’s just talk. | birinchi |
| 27 | And I do not know whether the sun will rot or dry what is left, so I had better eat it all although I am not hungry. | Shuning uchun, och bo‘lmasam ham, yaxshisi uni yeb qo‘ya qolay. | Bu qolgan bo‘laklar oftobda nima balo bo‘ladi — qoqlanadimi, yoqi hidlanib qoladimi, bilmayman. Shuning uchun, och bo‘lmasam ham, yaxshisi … | birinchi |
| 28 | — dedi mingboshi. | “How can you ride that jade without shame, like a woman, stork?!” barked mingboshi. | Do I need another ten?!” he bellowed so even those who had exited could hear. | ikkinchi |
| 29 | — Yo‘g‘-e, ovozi soz deyman-da, ovozi! | “Nooo, I was just saying that her voice is wonderful—her voice!” he said. | Xolmat’s words embarrassed O’lmasjon, and he started to argue. | ikkinchi |
| 30 | Darvozabonlik qiluvchi mirshabga: «Arzga kelganlarning hech birini qo‘ymaysan. | He told the guard at the gate, “Don’t let any petitioners in. | The master’s mood has soured.” | ikkinchi |

## B. Ikkinchi o‘tishdan 40 ta tasodifiy juftlik (random.Random(20261014); 1.1 juftliklari olinmagan)

Natija: 39 tasi to‘liq, 1 tasi qisman mos; noto‘g‘ri juftlik uchramadi. Tanlov kichik: 0/40 natija noto‘g‘ri
juftliklar ulushi 95 % ishonch bilan 7,5 foizdan kam ekanini bildiradi («uchlik qoidasi»).

| № | Juftlik | Asliyat | Tarjima | Baho |
|---|---|---|---|---|
| 1 | aln2-oms-00597 | And no one to help either one of us. | Na unga va na menga hech kim yordam qo‘lini cho‘za olmaydi». | to‘liq |
| 2 | aln2-kvk-02865 | Uning behollik va uyqusizlikdan yumilgan ko‘zlarini qayta boshdan ochirdi. | Her eyes, closed from exhaustion and sleeplessness, were suddenly opened. | to‘liq |
| 3 | aln2-kvk-02450 | Dam bo‘lsa, suhbat hofizlari singari asta-asta xirgoyi qiladi. | … Other times, he would sing softly like a hafiz. | to‘liq |
| 4 | aln2-kvk-07891 | Tilmoch bu buyruqni Zebiga tushuntirib berdi. | The translator explained the demand to Zebi. | to‘liq |
| 5 | aln2-oms-01341 | But I was more intelligent than he was. | Ammo men undan ko‘ra ham aqlliroq bo‘lib chiqdim. | to‘liq |
| 6 | aln2-kvk-08322 | Eshonga aytdilar: «haydab yuboraylikmi?» deb so‘radilar. | The murids asked their eshon, “Should we kick him out now?” | to‘liq |
| 7 | aln2-kvk-05419 | Oppoq, shi-rin suti bor... | It has the whitest, sweetest milk.” | to‘liq |
| 8 | aln2-kvk-05865 | Maskovda no‘g‘oylarning machiti borligini toshkentlik yigitdan eshitgan edim. | The sart told me that the Tatars have a mosque in Moscow. | to‘liq |
| 9 | aln2-kvk-05235 | «Sharafuddin Xodjaev», dedi. | “Sharafuddin Xo’jaev” he said. | to‘liq |
| 10 | aln2-oms-00279 | “Qua Va,” the boy said. | —  Qu e Va! — dedi bola. | to‘liq |
| 11 | aln2-kvk-05809 | Faqat bir ozdan so‘ng qo‘lini bo‘ynimdan olib qo‘yib: | … After a while, I took her hand from my neck. | qisman |
| 12 | aln2-kvk-02496 | — Yaxshi bo‘libdi, aylanay, bolam, otangning og‘ir jussasini eshonboboday odam ko‘tarmasa, kim ko‘tara oladi? | “What a good thing, my dear child. If the eshon can’t lift your father’s lazy body, then who can?” | to‘liq |
| 13 | aln2-oms-00592 | When once, through my treachery, it had been necessary to him to make a choice, the old man thought. | — Mening hiylam tufayli u o‘z fikrini o‘zgartishga majbur bo‘ldi, aql ham bovar qilmaydi bunga! | to‘liq |
| 14 | aln2-kvk-07146 | — Shovqin solmay gapiring. | “Stop it with the screaming, Yodgor. | to‘liq |
| 15 | aln2-kvk-05088 | Nima holdaman? | What am I doing? | to‘liq |
| 16 | aln2-kvk-07257 | Bu kecha Hakimjon qancha kam uxlagan bo‘lsa, mingboshi undan ham kam uxladi. | As little as Hakimjon slept, mingboshi slept even less. | to‘liq |
| 17 | aln2-kvk-07085 | Boshqalar birni birga bersa, bu birni beshga, o‘nga beradi. | Others just lend you things, one to one, but he wants five, ten times back what he’s given. | to‘liq |
| 18 | aln2-kvk-04430 | Yana ichdilar... | They drank again. | to‘liq |
| 19 | aln2-kvk-03875 | — Yaxshi, men aytay. | “Fine, I’ll tell him.” | to‘liq |
| 20 | aln2-kvk-00983 | — Men o‘lgur, o‘sha kuni Zebixonning ovoziga mast bo‘lib, hech narsani o‘ylayolmabman-da! | “Damn me, Zebi’s voice was such ecstasy that I couldn’t think of anything! | to‘liq |
| 21 | aln2-kvk-07329 | — Yo‘q. | “No. | to‘liq |
| 22 | aln2-kvk-05148 | Poezd tez yurib ketayotir. | The train keeps on moving. | to‘liq |
| 23 | aln2-kvk-08246 | Aravakashlarning «po‘sht, po‘sht» degan ovozlari — «o‘la, o‘l!» degan kabi, ta’na shaklida eshitildi va xuddi yelkasi oldida to‘xtagan otni… | The cart-drivers’ “Get, get!” sounded like “Die already!” He stared at the snout of a horse that stopped near his shoulder and said, as if … | to‘liq |
| 24 | aln2-oms-01220 | Then it spread like a cloud. | Keyin bu dog‘ yoyilib ketdi va pag‘a-pag‘a bulutga o‘xshab qoldi. | to‘liq |
| 25 | aln2-kvk-06602 | — Hammasiga soldat beshotari bermoqchi... | “We’ll give them all rifles. | to‘liq |
| 26 | aln2-kvk-05153 | Odamni zeriktiradigan quruq cho‘lga kirib boramiz. | Now we’re headed into the miserable , boring steppe. | to‘liq |
| 27 | aln2-kvk-04319 | — Qiziq ekansiz, Miryoqub aka. | “You are a strange one, Miryoqub. | to‘liq |
| 28 | aln2-kvk-06914 | Topshirmay nima qilsin? | What could she have done otherwise? | to‘liq |
| 29 | aln2-oms-00975 | They sleep and the moon and the sun sleep and even the ocean sleeps sometimes on certain days when there is no current and a flat calm. | Yulduzlar ham uxlaydi, oy ham uxlaydi, quyosh ham uxlaydi va hatto oqim bo‘lmagan, jimjit sukunat cho‘kkan kezlari okean ham uxlaydi. | to‘liq |
| 30 | aln2-kvk-03290 | Miryoqub hali boya nomer egasining uyida bergan qarorini quvvatlash uchun xotinning moviy ko‘zlaridan quvvatli dalillar topgan edi. | Miryoqub saw in her eyes confirmation of everything he had thought about when he first saw her among the eleven. | to‘liq |
| 31 | aln2-kvk-01219 | — Muncha eslik ekan Sultonxon ayang! | “How thoughtful Sultonxon is!” | to‘liq |
| 32 | aln2-kvk-05500 | «Qarta o‘ynab-o‘ynab zerikdim. | Even fortune cards have gotten boring. | to‘liq |
| 33 | aln2-kvk-03533 | Men — Miryoqubman, Miryoqub!..» | I am Miryoqub, Miryoqub. | to‘liq |
| 34 | aln2-kvk-01818 | Qishloq odamlaridan ko‘p narsani eshitdim... | I heard many things from the villagers. | to‘liq |
| 35 | aln2-kvk-06256 | O‘zim to‘g‘rilab yuboraman. | I’ll take care of it.” | to‘liq |
| 36 | aln2-kvk-01602 | — To‘y? | “Wedding?” | to‘liq |
| 37 | aln2-kvk-00197 | Hovling boshingdan qolsin, Fitna! | May you lose your house, Fitna!” | to‘liq |
| 38 | aln2-kvk-00788 | Yigitcha bu so‘zdan o‘ng‘aysizlandi va tona boshladi: | Xolmat’s words embarrassed O’lmasjon, and he started to argue. | to‘liq |
| 39 | aln2-kvk-06062 | Endi nima qilish kerak? | What could she do now? | to‘liq |
| 40 | aln2-kvk-04538 | Akbarali boshqa odam. Miryoqub butunlay boshqacha odam...» | Akbarali is one person, and Miryoqub is another.” | to‘liq |

## C. Platforma ko‘rsatgan 50 ta tasodifiy muqobil (25 o‘zbekcha, 25 inglizcha so‘rov so‘zi)

Natija: 43 tasi to‘g‘ri (86 %), 2 tasi qisman (4 %), 5 tasi noto‘g‘ri (10 %). O‘zbekcha so‘rovlarda 21 / 1 / 3,
inglizchada 22 / 1 / 2. Xatolar asosan ma’nosi kuchsiz fe’llarda (qilmoq, demoq) va ko‘chma birikma ichidagi so‘zda
(quloq solmoq). Qamrov (butun korpus): o‘zbekcha mustaqil so‘zlarning 30,7 foizi (74 476 tadan 22 866 tasi),
inglizchaning 41,2 foizi (56 087 tadan 23 086 tasi).

| № | Tili | Juftlik | So‘rov tomoni | Tarjima tomoni | Baho |
|---|---|---|---|---|---|
| 1 | uz | U, bir safar [[qarmoqda]] moda marlin tutganini esladi. | He remembered the time he had [[hooked]] one of a pair of marlin. | to‘g‘ri |
| 2 | uz | Mingboshi to‘g‘risidagi dovruq bir xil daydi shamollarday to‘satdan kelib qolgan, so‘ngra so‘fining ma’lum so‘zlaridan keyin butunlay [[jimib]] ketgan edi. | Like fierce winds that accompany the coming of spring, mingboshi had come and gone, and their home had become [[quiet]]. | to‘g‘ri |
| 3 | uz | Erta-kech gapiga quloq solaman, [[qulog‘imni]] uning og‘zidan uzib ololmayman... | I [[listen]] to him day and night; I can’t take my ear away. | noto‘g‘ri — «quloq solmoq» qismi bog‘langan; to‘g‘risi — ear |
| 4 | uz | U kirib [[keldi]]! | And he [[came in]]! | to‘g‘ri |
| 5 | uz | Bu orada [[Miryoqub]] bardosh qilib o‘tirsa ham, xo‘jayin tajanglanib besh-o‘n marta borib keldi. | Although [[Miryoqub]] sat calmly waiting, the owner, nervous, checked on him repeatedly. | to‘g‘ri |
| 6 | uz | — deb e’tiroz [[qildi]] ota. | “You think other work would be easier, [[do]] you?” interjected the father again. | noto‘g‘ri — «do» — so‘roq qo‘shimchasi |
| 7 | uz | — [[Hakimjon]], ho, Hakimjon! | “[[Hakimjon]], hey, Hakimjon!” | to‘g‘ri |
| 8 | uz | — dedi eshikdan chiqa turib. Miryoqub [[kiyinib]] tashqariga chiqqan vaqtida tong yorishib kelardi. | By the time Miryoqub [[dressed]] himself and stepped outside, the sun had already peaked over the horizon. | to‘g‘ri |
| 9 | uz | [[Yosh]] juvon boshini quyi egib, yuzini chapga burgan va borgan sari qaltirashi kuchaygan lablarini o‘tkir va oppoq tishlari o‘rtasida qisardi... | The [[young]] girl lowered her head and bit her still quivering lips. | to‘g‘ri |
| 10 | uz | Otasining odatdagi tomoq qirish va yo‘talishlar bilan, katta eshikning og‘ir [[zanjirini]] sharaq-shuruq qilib tushirib, namozga chiqib ketganiga hali ko‘p o‘tmagan edi. | It couldn’t have been her father since not much time had passed since he had left for the prayer, having closed the big door on a heavy [[chain]] while coughing and clea… | to‘g‘ri |
| 11 | uz | Kechalari uning hovlisida bir-ikki mirshabning poyloqchilik qilib chiqqanini gapiradilar, faqat muni o‘z [[ko‘zi]] bilan ko‘rgan kishi yo‘q, bo‘lsa ham ochib gapirmaydi,… | They say that his house was guarded every night by one or two policemen, only no one had ever [[seen]] them, and even if they had seen them, they wouldn’t, no, couldn’t … | qisman — «o‘z ko‘zi bilan ko‘rgan» → seen |
| 12 | uz | Uni ham olamiz. [[Hali]] bardamsiz, birgalashib ishlaymiz. | You’re [[still]] healthy, we can work together. | to‘g‘ri |
| 13 | uz | Faqat Miryoqub «...[[sog‘ligiga]]» deganinigina anglab qoldi. | To’ra started to toast, but all Miryoqub heard him say was, “To the [[health]] of …,” before he swallowed the rest of the words along with the vodka. | to‘g‘ri |
| 14 | uz | Uning ildizlari [[Miryoqubning]] badanida hali juda kuchli! | Its roots still have ample power in [[Miryoqub]]’s body! | to‘g‘ri |
| 15 | uz | Bo‘lsa ham [[esimda]] turadi, deysanmi? | Even if he did, do you think I’d [[remember]] it?” | to‘g‘ri |
| 16 | uz | Bu ham Akbaraliga o‘xshagan [[minglarcha]] itlarning biri! | “He is one of those [[thousands]] of dogs that are just like Akbarali! | to‘g‘ri |
| 17 | uz | Yana kim [[biladi]]? | But who [[knows]]? | to‘g‘ri |
| 18 | uz | Kart ustiga dasturxon yozilib, bir mistovoq non bilan piyolada [[qiyom]] qo‘yilgan edi. | The table was set for breakfast, and a dish with bread and a teacup with [[jam]] sat upon it. | to‘g‘ri |
| 19 | uz | Boshqalarga besh-to‘rt ta-nob yerni tirikligimda o‘tkazib berib, qolgan davlatimni batamom shunga qoldiraman». Mingboshining katta davlatidan katta meros kutgani uchungi… | Give the others each a few acres of land, but everything else to her.’ Didn’t Miryoqub, with his black eyes, take Poshshaxon in his [[arms]] and tell her that everything… | to‘g‘ri |
| 20 | uz | [[Berkitib]] qo‘ysangiz bo‘l-maydimi? | Can’t you [[close]] it?” | to‘g‘ri |
| 21 | uz | Boshqalar [[jim]] qoldilar. | The others were still [[silent]]. | to‘g‘ri |
| 22 | uz | Undan keyin: «Aybdorning qilgan gunohi og‘ir bo‘lib, hozirgi urush vaqtida va nozik sharoitlar ichida davlat odamiga qasd qilgani uchun falon moddalar bo‘yicha oliy jazo… | The travelling delegation of the territory’s military court has duly considered the fact that the convicted is a [[member]] of an inferior, uncultured people, is young a… | noto‘g‘ri — to‘g‘risi — delegation |
| 23 | uz | — Uch kun orasida [[yurtga]] eshittirib, bo‘lgan gapni menga ma’lum qilasanlar. | “You’ll inform the [[people]] within three days and tell me what happens.” | to‘g‘ri |
| 24 | uz | Teskari [[dunyo]]!» | This fickle [[world]]!” | to‘g‘ri |
| 25 | uz | Uyiga allaqanday bir no‘g‘oy [[xotinni]] oldirib, yangicha maktab ochgan ekan: erkak bolalarga ham yangicha maktab ochmoqchi bo‘lib, Toshkentdan bir po‘rim maktabdorni c… | He hired a Tatar [[woman]] and opened a new-method school; he even sent an invitation to Tashkent for a teacher so he could open a new-method school for boys. | to‘g‘ri |
| 26 | en | His mouth was too dry to speak but he could not reach for the [[water]] now. | Og‘zi shunday ham qaqrab ketgan ediki, hatto labini labiga qovushtirishga majoli yetmas, [[suv]] solingan shishani cho‘zilib olish uchun esa madori yo‘q edi. | to‘g‘ri |
| 27 | en | The two were [[silent]] for a moment. | Ikkalasi ham bir nafas [[jim]] qolishdi. | to‘g‘ri |
| 28 | en | [[maryam]]. | M a r [[ya]] m. | qisman — harflab yozilgan ism |
| 29 | en | She [[slowly]] and carefully sat down. | [[Sekingina]] va ehtiyot bilangina o‘tirdi. | to‘g‘ri |
| 30 | en | “Well, out with it,” seconded [[Poshshaxon]] quickly. | — Qani, gapirib bering-chi, — dedi [[Poshshaxon]]. | to‘g‘ri |
| 31 | en | “[[Now]],” he said, when his hand had dried, “I must eat the small tuna. | — [[Endi]],— dedi u qo‘li qurigach,— tunetsni yeb olishim kerak.— Uni bu yoqqa changak bilan tortib ololaman, kiftini keltirib qorin to‘ydirish ham qo‘limdai keladi. | to‘g‘ri |
| 32 | en | You all are [[young]], enjoy yourselves. | Sizlar [[yosh]]-yalang, o‘ynab-kulib ko‘ngillarni yozinglar. | to‘g‘ri |
| 33 | en | “Have you lost it, [[Hakimjon]]?!” exclaimed mingboshi. | — Sira esing kirmadi-da, [[Hakimjon]]! — dedi mingboshi. | to‘g‘ri |
| 34 | en | Becoming [[cultured]]. | [[Madaniylashadi]]. | to‘g‘ri |
| 35 | en | Someone like you does not enter into any [[business]] without thinking it over thoroughly. | Shunday bo‘lgandan keyin, senday ulug‘ bir odam bir [[ishni]] chuqur o‘ylamasdan qilmaydi. | to‘g‘ri |
| 36 | en | She even played [[snow]] letters with three of the women. | Uchta bilan «[[qor]] xati» o‘ynab yutdi... | to‘g‘ri |
| 37 | en | [[Poshshaxon]] disagreed: “‘Shiny on the surface, but sharp underneath,’ they say. | [[Poshshaxon]] bu fikrga qo‘shilmadi: — «Tashi yaltiroq, ichi qaltiroq» degan gap bor, — dedi u. | to‘g‘ri |
| 38 | en | Zunnun sat down beside [[Miryoqub]]. | Zunnun [[Miryoqubning]] yonginasiga o‘tirdi. | to‘g‘ri |
| 39 | en | Does a person [[cry]] for nothing?” | Bekorga yig‘laydimi kishi? — [[dedi]] u. | noto‘g‘ri — to‘g‘risi — yig‘laydimi |
| 40 | en | The young woman stood in the middle of the [[room]], washed up and dressed in fine silk. | Yosh juvon harir va chiroylik kiyimlari bilan yuvinib-taranib [[uyning]] o‘rtasida turardi. | to‘g‘ri |
| 41 | en | “[[Idiot]]!” he said. | — [[Ahmoq]]! — dedi u. | to‘g‘ri |
| 42 | en | Razzoq-sufi’s head wouldn’t [[rise]] from his pillow for another few weeks. | Endi yana haftalarcha so‘fining boshi uydagi yostiqdan [[ko‘tarilmaydi]]. | to‘g‘ri |
| 43 | en | “I have to tell you about [[Umarali]] and Yodgor. | — Shu [[Umaraliboy]] bilan Yodgorxo‘jani aytaman. | to‘g‘ri |
| 44 | en | Did your O’lmasjon eat through that much [[money]] already?” | O‘lmasing, hali, shuncha [[pulni]] yeb keldimi? | to‘g‘ri |
| 45 | en | Rumors [[began]] circulating. | Duv-duv gap [[ketdi]]. | to‘g‘ri |
| 46 | en | “There’s a [[letter]] from Miryoqub,” said Hakimjon. | — Miryoqub akamdan [[xat]] bor, — dedi Hakimjon. | to‘g‘ri |
| 47 | en | [[Tomorrow]] …” | [[Erta]] qachon... | to‘g‘ri |
| 48 | en | One of her co-wives outside probably asked Umrinisabibi what she was doing in the house and for that reason she set one foot back in the courtyard and cried out, “Sulton… | Tashqarida kundoshlardan biri Umrinisabibidan nima qilib yurganini so‘ragan bo‘lsa kerak, u kichkina darichani ochib, bir oyog‘ini o‘z hovlisiga qo‘yarkan, baland ovoz b… | to‘g‘ri |
| 49 | en | “You said that Akbarali is [[here]]. | — Hali «Akbarali shu [[yerda]]», deding. | to‘g‘ri |
| 50 | en | Zebi, still sleepy, [[lit]] the lamp. | Zebi uyqusirab kelib, yana [[fonarni]] balandlatdi. | noto‘g‘ri — to‘g‘risi — balandlatdi |
