# So‘z darajasidagi muqobillarni tanlab tekshirish (14.10.2026) — birinchi o‘tish, tarixiy hujjat

Ishchi hujjat, dissertatsiya matniga kirmaydi. Tekshiruvni sun’iy intellekt (Claude) bajargan; natija platformaning
metodologiya sahifasida shu izoh bilan keltirilgan.

**Tanlov.** `data/word_alignment.json` dagi juftliklardan tasodifiy (random.Random(20261014)) gap va undagi mustaqil so‘z
tanlandi; platforma muqobil ko‘rsatgan hollar olindi: 25 ta o‘zbekcha so‘rov so‘zi va 25 ta inglizcha so‘rov so‘zi.
[[...]] — so‘rov so‘zi va platforma ko‘rsatgan muqobil.

**Baholash.** to‘g‘ri — ajratilgan so‘z tarjimonning shu so‘z uchun ishlatgan so‘zi (kontekstual muqobil ham to‘g‘ri hisoblanadi);
qisman — muqobil so‘z bilan birga kengroq birikmaning muqobili belgilangan yoki aksincha; noto‘g‘ri — mos emas.

**Natija.** 50 tadan 45 tasi to‘g‘ri (90 %), 3 tasi qisman (6 %), 2 tasi noto‘g‘ri (4 %). O‘zbekcha so‘rovlarda: 23 to‘g‘ri,
2 qisman, 0 noto‘g‘ri; inglizcha so‘rovlarda: 22 to‘g‘ri, 1 qisman, 2 noto‘g‘ri (ikkalasi ham ma’nosi kuchsiz so‘zlar: *have*, *though*).

**Qamrov** (butun korpus, hisoblangan): o‘zbekcha mustaqil so‘zlarning 29,7 foizi (74 164 tadan 21 998 tasi), inglizcha
mustaqil so‘zlarning 39,8 foizi (55 985 tadan 22 274 tasi) uchun muqobil ko‘rsatiladi. Qolganlarida korpus bo‘yicha
bog‘lanish chegaradan (kamida 3 marta va 3 %) o‘tmagan — tarjimon fikrni boshqacha bergan yoki tekislash ishonchli
bog‘lanish topmagan.

| № | So‘rov tili | Juftlik | So‘rov tomoni | Tarjima tomoni | Baho |
|---|---|---|---|---|---|
| 1 | uz | aln2-oms-00572 | Ular bizga xuddi [[uchar]] baliqlar singari yaqin. | They are our brothers like the [[flying]] fish.” | to‘g‘ri |
| 2 | uz | aln2-oms-01316 | U akulaning yaqinroq kelishini kutarkan, garpunni shaylab, arqonning oxirini [[mahkamlab]] qo‘ydi. | He prepared the harpoon and made the rope [[fast]] while he watched the shark come on. | to‘g‘ri |
| 3 | uz | aln2-kvk-05850 | — [[dedim]]. | I [[asked]]. | to‘g‘ri |
| 4 | uz | aln2-kvk-02481 | Nima [[deydi]]? | What did he [[say]]?” | to‘g‘ri |
| 5 | uz | aln2-kvk-07070 | — «Xotintaloq», demasalar, hech kim [[tegmas]] edi ularga. Hammamizni | “If they hadn’t called us bastards, then we wouldn’t have [[touched]] them.” | to‘g‘ri |
| 6 | uz | aln2-kvk-03860 | [[Keng]] ko‘rpada yolg‘iz o‘zim qaltirab yotaman... | I lie down on my [[wide]] mat by myself. | to‘g‘ri |
| 7 | uz | aln2-kvk-08231 | — Odam o‘ldirgan bolaning otasiga qanday maslahat bo‘ladi, [[so‘fi]]? | “What advice can there be for the father of a murderer, [[Razzoq]]? | to‘g‘ri — tarjimon murojaatni ism bilan bergan |
| 8 | uz | aln2-kvk-01587 | — Nima [[deding]]?! | “What did you [[say]]? | to‘g‘ri |
| 9 | uz | aln2-kvk-00773 | Uning jonlanganini ko‘rganlar ixtiyorsiz yoyilib kular va [[chin]] ko‘ngildan sevinardilar. | The girls, seeing her vibrancy, couldn’t control their laughter and [[sincerely]] rejoiced. | qisman — «chin ko‘ngildan» birikmasi bir so‘z bilan berilgan |
| 10 | uz | aln2-kvk-04449 | So‘ngra sekin [[kelib]], kartga o‘tirdi: | Then she slowly [[came over]] and sat on the bed. | to‘g‘ri |
| 11 | uz | aln2-kvk-00016 | Otasining odatdagi tomoq qirish va yo‘talishlar bilan, katta eshikning og‘ir [[zanjirini]] sharaq-shuruq qilib tushirib, namozga chiqib ketganiga hali ko‘p o‘tmagan edi. | It couldn’t have been her father since not much time had passed since he had left for the prayer, having closed the big door on a heavy [[chain]] while coughing and cl… | to‘g‘ri |
| 12 | uz | aln2-kvk-01589 | Bu nima [[deganing]]? | What do you [[mean]]?” | to‘g‘ri |
| 13 | uz | aln2-kvk-00093 | Zebi supurgini qo‘ldan oldirdi, lekin [[o‘rtog‘i]] supura boshlagandan so‘ng: | She understood so well that she didn’t bother to answer Zebi, but suddenly grabbed the broom in her [[friend]]’s hands. | to‘g‘ri |
| 14 | uz | aln2-kvk-00271 | Uni ham olamiz. [[Hali]] bardamsiz, birgalashib ishlaymiz. | You’re [[still]] healthy, we can work together. | to‘g‘ri |
| 15 | uz | aln2-kvk-00148 | — Eshon bobom sizdan [[dilgir]] emishlar, — deydi bir kun Qurvonbibi so‘figa. | “They say your elder master is quite [[upset]] with you,” Qurvonbibi said to Razzoq-sufi one day. | to‘g‘ri |
| 16 | uz | aln2-kvk-03929 | [[Zarur]] ishi bor ekan... | He had something [[urgent]] to do.” | to‘g‘ri |
| 17 | uz | aln2-kvk-00352 | Kart ustiga dasturxon yozilib, bir mistovoq non bilan piyolada [[qiyom]] qo‘yilgan edi. | The table was set for breakfast, and a dish with bread and a teacup with [[jam]] sat upon it. | to‘g‘ri |
| 18 | uz | aln2-kvk-04322 | Bo‘lmasa, undan ilgari [[xonim]] bilan gaplashib, gapni bir joyga qo‘yganmiz... | Of course, we had already discussed this with the [[lady]].” | to‘g‘ri |
| 19 | uz | aln2-kvk-08073 | — Shaharda... Shaharda... [[ota]]-onam... bor... ko‘rsatarmikin? | “In the city … the city … my [[parents]] are there. | qisman — «ota-onam» → parents: juft so‘zning bir qismi |
| 20 | uz | aln2-kvk-06488 | — Nimaga imoning o‘chdi birdaniga? — deb qichqirdi [[mingboshi]] haybatli ovoz bilan. | “Why are you all suddenly mute?” screamed [[mingboshi]] in a booming, authoritative voice. | to‘g‘ri |
| 21 | uz | aln2-kvk-03824 | Bir oz choy ichib, [[gaplashib]] borarsan. | Have some tea and [[talk]]. | to‘g‘ri |
| 22 | uz | aln2-kvk-07099 | Biz bilmasak, [[taqsir]]... | We don’t know what they do with it, [[sir]]. | to‘g‘ri |
| 23 | uz | aln2-kvk-01724 | Uning qarshisida o‘tkir va serhavas [[ko‘zlarini]] o‘ynatib, yosh bir yigit turgan kabi bo‘lardi... | The young man across from her opened and closed his glowing and passionate [[eyes]]. | to‘g‘ri |
| 24 | uz | aln2-kvk-03396 | O‘zi yarim qadah [[aroq]] quydi. — Ich! | He poured half a glass of [[vodka]] for himself. | to‘g‘ri |
| 25 | uz | aln2-kvk-00800 | — Razzoq [[so‘fi]] degan bir odamning... | “A man named Razzoq-[[sufi]]. …” | to‘g‘ri |
| 26 | en | aln2-kvk-00829 | “Yes, [[auntie]]. | — Ha, [[xola]], uyda nima qilasiz? | to‘g‘ri |
| 27 | en | aln2-kvk-06871 | Everyone [[laughed]]. | Hamma [[kulib]] yubordi. | to‘g‘ri |
| 28 | en | aln2-kvk-03967 | Should we stay up [[waiting]]? | [[Kutib]] o‘tiraylikmi? | to‘g‘ri |
| 29 | en | aln2-kvk-01187 | “I came home last [[night]] tired and went right to sleep. | — [[Kechasi]] charchab kelib, uxlab qolibman. | to‘g‘ri |
| 30 | en | aln2-oms-00269 | He only dreamed of places now and of the [[lions]] on the beach. | Endi tushida uzoq o‘lkalar va qirg‘oqqa chiqayotgan [[sher]] bolalarinigina ko‘rardi, xolos. | to‘g‘ri |
| 31 | en | aln2-kvk-00461 | “Among you is a much-famed singer. [[Strange]] that you’re so obsessed with me!” he said. | — Orangizda dong‘i ketgan ashulachingiz bor turib, menga osilganlaring  [[qiziq]]! | to‘g‘ri |
| 32 | en | aln2-oms-01361 | I cannot know. I never had anything [[wrong]] with my heel except the time the sting ray stung it when I stepped on him when swimming and paralyzed the lower leg and m… | marta ham hech [[balo]] urgan emas, faqat bir safar cho‘milayotib elektr skatini bilmay bosib olganimda, uni ilon chaqqanday bo‘lgan edi; o‘shanda oyog‘im tizzam-gacha… | to‘g‘ri |
| 33 | en | aln2-kvk-05627 | Maybe they’ll help you find a teacher, they’ll [[show]] the way.” | Balki muallim, muallima xususida sizga yordam beradilar, yo‘l [[ko‘rsatadilar]]. | to‘g‘ri |
| 34 | en | aln2-kvk-07016 | “My ambler was at [[home]], sir. | — Mening qashqa yo‘rg‘am [[uyda]] qoldi, taqsir. | to‘g‘ri |
| 35 | en | aln2-kvk-01541 | …” As mingboshi trailed off, his [[brow]] furrowed, and Miryoqub saw his narrow eyes repeatedly blink. | Shu yerga kelganda, mingboshining [[qovog‘i]] solina boshlagan edi, qisiq ko‘zlarining tez-tez yumilib parpirayotganday bo‘lganini Miryoqub ham payqadi. | to‘g‘ri |
| 36 | en | aln2-kvk-00670 | the ground. The [[old]] woman started to run her fingers over the wood of the ladder, while Enaxon squeezed the chewing resin she took from her mouth into a ball. | [[Kampir]] shotining yon yog‘ochini silab o‘ynar, Enaxon og‘zidan olgan saqichni qo‘lida ezib, «soqqa» yasar, kelinchak bo‘lsa, bir cho‘p bilan yerni chizg‘alar, uchal… | qisman — «old woman» → kampir: birikmaning muqobili belgilangan |
| 37 | en | aln2-kvk-07208 | Getting dressed however I could, I came with my seven [[men]]. | Apil-tapil kiyinib, otga otlanib, yetti-sakkiz [[yigitim]] bilan keldim. | to‘g‘ri |
| 38 | en | aln2-kvk-04090 | Oh God, who should I [[ask]]? | Azbaroyi xudo, kimdan [[so‘rasam]]? | to‘g‘ri |
| 39 | en | aln2-kvk-03816 | “That would be [[good]].” | — [[Yaxshi]] bo‘lardi. | to‘g‘ri |
| 40 | en | aln2-kvk-04444 | Miryoqub [[lifted]] his head from the pillow, attempting to get up. | Miryoqub o‘rnidan turmoqchi bo‘lib yostiqdan boshini [[ko‘tardi]]. | to‘g‘ri |
| 41 | en | aln2-oms-00202 | “They [[have]] other men on the team.” | — Komandada uning bir [[o‘zi]] emas-da. | noto‘g‘ri — mos emas |
| 42 | en | aln2-kvk-08280 | “What’s wrong with you, [[Razzoq]]? | — Nima bo‘ldi senga, [[so‘fi]]? | to‘g‘ri |
| 43 | en | aln2-oms-01263 | But I think the [[great]] DiMaggio would be proud of me today. | Ammo, fahmimcha, [[ulug]]‘ Di Mad-jio bugun men bilan faxrlansa arziydi. | to‘g‘ri — muqobil to‘g‘ri; so‘z oxiridagi ‘ belgisi ajratilmagan edi — tuzatildi |
| 44 | en | aln2-kvk-00939 | Hurry up, for the love of [[God]]!” | Imillamay qoling, [[ilohim]]! — dedi. | to‘g‘ri |
| 45 | en | aln2-kvk-03419 | “What is this [[strange]] Asian saying? | «Nimalar deydi bu [[g‘alati]] aziat? | to‘g‘ri |
| 46 | en | aln2-kvk-06804 | “He’s an important [[person]]. | — Katta [[odam]]. | to‘g‘ri |
| 47 | en | aln2-oms-00156 | The old man’s head was very old [[though]] and with his eyes closed there was no life in his face. | Ammo cholning yuzi harqalay ancha qarimsiq [[bo‘lib]] qolgan va hozir ko‘zlari yumilib uyquga ketganda, xuddi jonsizga o‘xshab ko‘rinardi. | noto‘g‘ri — mos emas |
| 48 | en | aln2-kvk-02705 | The poor [[woman]] struck her head with clenched fists. | Bechora [[kampir]] boshlariga mushtlardi. — Mushtla boshingni, Fitna! | to‘g‘ri |
| 49 | en | aln2-oms-01157 | “He can’t be that [[big]].” | Ammo baliq chindan ham [[ulkan]] edi. | to‘g‘ri |
| 50 | en | aln2-kvk-01853 | Those who [[saw]] him were frightened. | Odam [[ko‘rsa]] qo‘rqadi... | to‘g‘ri |
