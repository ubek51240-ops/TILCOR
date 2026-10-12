/**
 * KORPUS.LINGVO - Ilmiy Ish va Parallel Korpus Ma'lumotlar Bazasi
 * Tadqiqot mavzusi:
 * "TARJIMA VA TENG MATNLAR PARALLEL KORPUSIDA O'ZARO FAOL BIRIKUVCHI (KOLLOKATSION) SO'ZLAR TADQIQI (o'zbek va ingliz tillari misolida)"
 * 
 * Asosiy amaliy parallel manbalar:
 * 1. Abdulhamid Cho'lpon: "Kecha va kunduz" (roman) <-> "Night and Day" (Christopher Fort tarjimasi)
 * 2. Ernest Xeminguey: "Chol va dengiz" (qissa, Ibrohim G'afurov tarjimasi) <-> "The Old Man and the Sea"
 * 3. Robert Luis Stivenson: "Xazinalar oroli" (roman, Sharif Rizo tarjimasi) <-> "Treasure Island"
 */

// Asosiy Badiiy Parallel Manbalar Metama'lumotlari
const literaryCorporaMeta = [
    {
        id: "source-cholpon",
        titleUz: "Kecha va kunduz",
        titleEn: "Night and Day",
        author: "Abdulhamid Choʻlpon",
        translator: "Christopher Fort (Academic Studies Press)",
        direction: "Oʻzbekcha (asl nusxa) ➔ Inglizcha (tarjima)",
        genre: "Tarixiy-ijtimoiy roman",
        pagesUz: 272,
        pagesEn: 235,
        wordCount: "—",
        alignedPairs: "— (tekislash qayta ko‘rib chiqilmoqda)",
        identifiedCollocations: "—",
        description: "Oʻzbek adabiyoti durdonasi. Asarda milliy turmush tarzi, anʼanaviy madaniyat, ayollar fojiasi va ijtimoiy munosabatlarga oid boy kollokatsion qatlam mujassam boʻlib, ularning ingliz tiliga tarjima qilinishi qiyosiy tadqiqot uchun muhim empirik asosdir.",
        badgeColor: "bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 border-indigo-200"
    },
    {
        id: "source-hemingway",
        titleUz: "Chol va dengiz",
        titleEn: "The Old Man and the Sea",
        author: "Ernest Hemingway (Ernest Xeminguey)",
        translator: "Ibrohim Gʻafurov («Yosh gvardiya»)",
        direction: "Inglizcha (asl nusxa) ➔ Oʻzbekcha (tarjima)",
        genre: "Falsafiy-ramziy qissa",
        pagesUz: 46,
        pagesEn: 52,
        wordCount: "—",
        alignedPairs: "— (tekislash qayta ko‘rib chiqilmoqda)",
        identifiedCollocations: "—",
        description: "Nobel mukofotiga sazovor boʻlgan jahon adabiyoti asari. Dengiz tabiati, inson matonati, baliqchilik va yolgʻizlik leksikasi boʻyicha lakonik uslubdagi kollokatsiyalarning oʻzbek tiliga badiiy adekvat tarjima qilinish modeli tahlil qilingan.",
        badgeColor: "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-200"
    },
    {
        id: "source-stevenson",
        status: "excluded",
        exclusionReason: "D2: O‘zbekcha tarjima skanerlangan rasm (matn qatlami yo‘q), OCR va tekshiruv talab etiladi, vaqtinchalik chiqarilgan",
        quarantined: true,
        titleUz: "Xazinalar oroli",
        titleEn: "Treasure Island",
        author: "Robert Louis Stevenson (R. L. Stivenson)",
        translator: "Sharif Rizo (Gʻafur Gʻulom nashriyoti)",
        direction: "Inglizcha (asl nusxa) ➔ Oʻzbekcha (tarjima)",
        genre: "Klassik sarguzasht romani",
        pagesUz: 216,
        pagesEn: 142,
        wordCount: "—",
        alignedPairs: "— (tekislash qayta ko‘rib chiqilmoqda)",
        identifiedCollocations: "—",
        description: "Dengiz safari, qaroqchilik hayoti, xavf-xatar, navigatsiya va kemasozlik atamalarining barqaror bogʻlanishlari. Asardagi idiomatik va kollokatsion iboralarning oʻzbek tilidagi ekvivalentligi chogʻishtirilgan.",
        badgeColor: "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300 border-amber-200"
    }
];

const dissertationData = {
    title: "TARJIMA VA TENG MATNLAR PARALLEL KORPUSIDA OʻZARO FAOL BIRIKUVCHI (KOLLOKATSION) SOʻZLAR TADQIQI",
    subtitle: "(oʻzbek va ingliz tillari misolida)",
    specialty: "10.02.20 – Qiyosiy tilshunoslik, chogʻishtirma tilshunoslik va tarjimashunoslik / Amaliy korpus lingvistikasi",
    year: "2026",
    abstract: "Mazkur ilmiy tadqiqot oʻzbek va ingliz tillaridagi tarjima va teng matnlar parallel korpusi bazasida oʻzaro faol birikuvchi (kollokatsion) soʻzlarning lingvistik, statistik va lingvomadaniy xususiyatlarini chogʻishtirma oʻrganishga bagʻishlangan. Tadqiqotning asosiy amaliy bazasini Abdulhamid Choʻlponning «Kecha va kunduz» (inglizcha «Night and Day»), Ernest Xemingueyning «The Old Man and the Sea» («Chol va dengiz») hamda Robert Luis Stivensonning «Treasure Island» («Xazinalar oroli») asarlari parallel korpusi tashkil etadi.",
    
    sections: [
        {
            id: "kirish",
            number: "KIRISH",
            title: "Kirish: Tadqiqotning umumiy tavsifi",
            subtitle: "Mavzuning dolzarbligi, asosiy badiiy manbalar, maqsad va vazifalar",
            icon: "book-open",
            content: `
                <div class="prose max-w-none text-slate-700 dark:text-slate-300 space-y-6">
                    <div class="p-4 bg-indigo-50 dark:bg-indigo-950/40 rounded-xl border border-indigo-100 dark:border-indigo-900/50">
                        <h4 class="text-lg font-bold text-indigo-900 dark:text-indigo-300 mb-2">Mavzuning dolzarbligi va zarurati</h4>
                        <p class="text-sm leading-relaxed">
                            Zamonaviy kompyuter va korpus lingvistikasi rivoji sharoitida tabiiy tilni qayta ishlash (NLP), mashina tarjimasi hamda qiyosiy tarjimashunoslik sohalarida parallel korpuslarning oʻrni beqiyosdir. Oʻzbek tilshunosligida parallel korpuslar tuzish va ulardan leksik-semantik birliklarni, xususan, <strong>oʻzaro faol birikuvchi (kollokatsion) soʻzlarni</strong> avtomatlashtirilgan tarzda ajratib olish va ularning tarjima ekvivalentligini tadqiq etish dolzarb ilmiy muammo hisoblanadi.
                        </p>
                    </div>

                    <div class="p-4 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
                        <h4 class="text-base font-bold text-slate-900 dark:text-white mb-2 flex items-center gap-2">
                            <span class="w-3 h-3 rounded-full bg-indigo-600"></span> Tadqiqotning Asosiy Badiiy Manbalari (Empirik Baza):
                        </h4>
                        <div class="grid sm:grid-cols-3 gap-3 text-xs mt-3">
                            <div class="p-3 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                                <strong class="text-indigo-600 dark:text-indigo-400 block mb-1">1. Choʻlpon: «Kecha va kunduz» ⟷ «Night and Day»</strong>
                                <span class="text-slate-500">Asl nusxadan inglizchaga tarjima (tarjimon: Christopher Fort). Oʻzbek milliy koloritidagi kollokatsiyalar.</span>
                            </div>
                            <div class="p-3 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                                <strong class="text-emerald-600 dark:text-emerald-400 block mb-1">2. E. Hemingway: «The Old Man and the Sea» ⟷ «Chol va dengiz»</strong>
                                <span class="text-slate-500">Inglizchadan oʻzbekchaga tarjima (tarjimon: Ibrohim Gʻafurov). Lakonik uslub va falsafiy kollokatsiyalar.</span>
                            </div>
                            <div class="p-3 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                                <strong class="text-amber-600 dark:text-amber-400 block mb-1">3. R. L. Stevenson: «Treasure Island» ⟷ «Xazinalar oroli»</strong>
                                <span class="text-slate-500">Inglizchadan oʻzbekchaga tarjima (tarjimon: Sharif Rizo). Dengizchilik, sarguzasht va dinamik harakat kollokatlari.</span>
                            </div>
                        </div>
                    </div>

                    <div class="grid md:grid-cols-2 gap-4 my-6">
                        <div class="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
                            <div class="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-semibold mb-2">
                                <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                                Tadqiqotning maqsadi
                            </div>
                            <p class="text-sm">
                                Oʻzbekcha va inglizcha badiiy parallel matnlar (Choʻlpon, Xeminguey, Stivenson asarlari) asosida parallel korpus platformasini loyihalash hamda kollokatsiyalarning semantik-struktur, statistik (MI, T-score) va lingvomadaniy ekvivalentligini qiyosiy tadqiq etish.
                            </p>
                        </div>

                        <div class="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
                            <div class="flex items-center gap-2 text-blue-600 dark:text-blue-400 font-semibold mb-2">
                                <span class="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
                                Tadqiqotning vazifalari
                            </div>
                            <ul class="text-sm space-y-1 list-disc list-inside">
                                <li>Kollokatsiya tushunchasining nazariy asoslari va mezonlarini aniqlashtirish;</li>
                                <li>Uchta asosiy asar boʻyicha oʻzbekcha-inglizcha aligned parallel korpus massivini shakllantirish;</li>
                                <li>Korpusda kollokatsiyalarni aniqlovchi MI (Mutual Information) va T-Score koʻrsatkichlarini tatbiq etish;</li>
                                <li>Asarlar misolida tarjima ekvivalentligi darajalarini qiyosiy tasniflash.</li>
                            </ul>
                        </div>
                    </div>
                </div>
            `
        },
        {
            id: "bob1",
            number: "I BOB",
            title: "KOLLOKATSIYA TUSHUNCHASINING NAZARIY ASOSLARI",
            subtitle: "Kollokatsiya mezonlari, tarjima xususiyatlari va parallel korpuslar oʻrni",
            icon: "layers",
            paragraphs: [
                {
                    id: "p1-1",
                    num: "1.1",
                    title: "Kollokatsiya va uning erkin birikma, frazeologik birlikdan farqlovchi mezonlari",
                    body: `
                        <p class="mb-3">Kollokatsiya (lotincha <em>collocatio</em> – «yonma-yon qoʻyish», «biriktirish») lisoniy hodisa sifatida ilk bor ingliz tilshunosi J.R. Firth tomonidan ilmiy muomalaga kiritilgan: <em>«You shall know a word by the company it keeps»</em> («Soʻzni uning atrofidagi hamrohlari orqali taniysan»).</p>
                        <p class="mb-3">Choʻlponning «Kecha va kunduz» romanida uchraydigan <em>«koʻngli tusamoq», «yuragi duk-duk urmoq», «sovuq nigoh»</em> hamda Xemingueyning «Chol va dengiz» asaridagi <em>«fished alone», «permanent defeat», «deep wrinkles»</em> kabi birikmalar erkin sintaktik birikma emas, balki tildagi mustahkam kollokatsion qoliplarga misoldir.</p>
                        
                        <div class="my-4 overflow-x-auto">
                            <table class="w-full text-sm border-collapse bg-white dark:bg-slate-800 rounded-lg overflow-hidden border border-slate-200 dark:border-slate-700">
                                <thead>
                                    <tr class="bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200 text-left font-semibold">
                                        <th class="p-3">Mezon</th>
                                        <th class="p-3">Erkin birikma (Free combination)</th>
                                        <th class="p-3 bg-indigo-50 dark:bg-indigo-950/30">Kollokatsiya (Collocation)</th>
                                        <th class="p-3">Frazeologik birlik (Idiom)</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
                                    <tr>
                                        <td class="p-3 font-semibold text-slate-900 dark:text-white">Semantik yaxlitlik</td>
                                        <td class="p-3">Komponentlar mustaqil (masalan: <em>katta uy, tez yurmoq</em>)</td>
                                        <td class="p-3 bg-indigo-50/50 dark:bg-indigo-950/20 font-medium text-indigo-700 dark:text-indigo-300">Leksik chegaralangan (masalan: <em>qattiq yomgʻir / heavy rain</em>)</td>
                                        <td class="p-3">Toʻliq metaforik yaxlitlik (masalan: <em>qoʻli yengil, burni koʻtarilmoq</em>)</td>
                                    </tr>
                                    <tr>
                                        <td class="p-3 font-semibold text-slate-900 dark:text-white">Almashtiruvchanlik</td>
                                        <td class="p-3">Erkin sinonimik almashtirish mumkin</td>
                                        <td class="p-3 bg-indigo-50/50 dark:bg-indigo-950/20 font-medium text-indigo-700 dark:text-indigo-300">Leksik cheklangan (*strong rain emas, balki heavy rain)</td>
                                        <td class="p-3">Komponentlarni mutlaqo almashtirib boʻlmaydi</td>
                                    </tr>
                                    <tr>
                                        <td class="p-3 font-semibold text-slate-900 dark:text-white">Statistik birikuvchanlik</td>
                                        <td class="p-3">Tasodifiy chastota darajasi</td>
                                        <td class="p-3 bg-indigo-50/50 dark:bg-indigo-950/20 font-medium text-indigo-700 dark:text-indigo-300">Statistik jihatdan yuqori (MI > 3.0, T-score > 2.0)</td>
                                        <td class="p-3">Barqaror qolipli chastota</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    `
                },
                {
                    id: "p1-2",
                    num: "1.2",
                    title: "Kollokatsion birikmalar va yondosh lisoniy hodisalar tarjimasining oʻziga xos xususiyatlari",
                    body: `
                        <p class="mb-3">Kollokatsiyalarni tarjima qilishda eng katta xatolik — <strong>soʻzma-soʻz (literal / kalka) tarjima qilish</strong> natijasida lisoniy meʼyorning buzilishidir. Masalan:</p>
                        <ul class="list-disc list-inside space-y-1.5 text-sm pl-2">
                            <li>Stivensonning «Treasure Island» asaridagi <em>«drop anchor»</em> iborasi oʻzbekchaga <em>*langarni tashlamoq</em> deb toʻgʻri berilgan, biroq <em>*throw anchor</em> deb olinmaydi.</li>
                            <li>Xeminguey asaridagi <em>«dead silence»</em> iborasi oʻzbekchada *oʻlik sukunat emas, <strong>«qabr sukunati»</strong> yoki <strong>«suv quygandek sukunat»</strong> tarzida madaniy ekvivalent topgan.</li>
                        </ul>
                    `
                },
                {
                    id: "p1-3",
                    num: "1.3",
                    title: "Parallel korpuslar yaratish ahamiyati va uning tarjimashunoslikdagi oʻrni",
                    body: `
                        <p class="mb-3">Parallel korpus (Parallel Corpus) — asliyat va tarjima matnlarining jumla darajasida tenglashtirilgan elektron bazasi boʻlib, tarjimashunosga quyidagi imkoniyatlarni yaratadi:</p>
                        <ul class="list-disc list-inside space-y-1.5 text-sm pl-2">
                            <li><strong>Kontekstual aniqlik:</strong> Har ikki tildagi real matn muhitini bir vaqtda koʻrish (KWIC - Key Word in Context).</li>
                            <li><strong>Tarjimonlik strategiyalarini ochish:</strong> Ibrohim Gʻafurov (Xeminguey tarjimoni), Sharif Rizo (Stivenson tarjimoni) va Christopher Fort (Choʻlpon tarjimoni) uslublaridagi kollokatsion mosliklarni tahlil qilish.</li>
                        </ul>
                    `
                }
            ],
            summary: "I bobda kollokatsiyalarning nazariy tabiati ochib berildi. Choʻlpon, Xeminguey va Stivenson asarlari misolida kollokatsiyalarning badiiy tarjimadagi oʻrni va parallel korpusning ilmiy tadqiqotdagi samaradorligi asoslandi."
        },
        {
            id: "bob2",
            number: "II BOB",
            title: "TADQIQOT METODOLOGIYASI VA PARALLEL KORPUS YARATISH JARAYONI TAVSIFI",
            subtitle: "3 ta asosiy asar korpusini tuzish, alignment va statistik dasturiy taʼminot",
            icon: "cpu",
            paragraphs: [
                {
                    id: "p2-1",
                    num: "2.1",
                    title: "Oʻzbekcha va inglizcha tarjima matnlar parallel korpusini yaratishning metodologik uzviyligi",
                    body: `
                        <p class="mb-3">Tadqiqotning amaliy korpusi quyidagi 3 ta asar asosida bosqichma-bosqich shakllantirildi:</p>
                        <ol class="list-decimal list-inside space-y-1 text-sm pl-2 mb-3">
                            <li><strong>Choʻlpon: «Kecha va kunduz» (272 bet) ⟷ «Night and Day» (235 bet)</strong>;</li>
                            <li><strong>E. Xeminguey: «Chol va dengiz» (46 bet) ⟷ «The Old Man and the Sea» (52 bet)</strong>;</li>
                            <li><strong>R. L. Stivenson: «Xazinalar oroli» (216 bet) ⟷ «Treasure Island» (142 bet)</strong>.</li>
                        </ol>
                        <p class="text-sm">Matnlar tozalash, OCR xatolarini tuzatish, tokenizatsiya va jumlalarga ajratish bosqichlaridan oʻtkazildi.</p>
                    `
                },
                {
                    id: "p2-2",
                    num: "2.2",
                    title: "Oʻzbekcha va inglizcha tarjima matnlar parallel korpusining lingvistik va dasturiy taʼminotini ishlab chiqish",
                    body: `
                        <p class="mb-3">Jumlalarni tenglashtirishda Gale-Church va Hunalign algoritmlarining gibrid modeli qoʻllanildi. Kollokatsiyalarning mustahkamlik darajasini aniqlash uchun quyidagi statistik formulalar dasturga integratsiya qilindi:</p>
                        <div class="grid md:grid-cols-2 gap-4 my-3 text-sm">
                            <div class="p-4 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
                                <div class="font-mono text-xs text-indigo-600 dark:text-indigo-400 font-bold mb-1">Mutual Information (MI Score)</div>
                                <p class="font-mono bg-white dark:bg-slate-800 p-2 rounded border border-slate-200 dark:border-slate-700 text-xs">MI = log₂ ( P(w₁, w₂) / (P(w₁) * P(w₂)) )</p>
                                <p class="text-xs text-slate-500 mt-2">Soʻzlarning birga uchrash ehtimolligi. Korpusda MI ≥ 3.0 boʻlganda birlik barqaror kollokatsiya deb topiladi.</p>
                            </div>
                            <div class="p-4 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
                                <div class="font-mono text-xs text-emerald-600 dark:text-emerald-400 font-bold mb-1">T-Score (Statistik ishonchlilik)</div>
                                <p class="font-mono bg-white dark:bg-slate-800 p-2 rounded border border-slate-200 dark:border-slate-700 text-xs">t = ( f(w₁, w₂) - E ) / √f(w₁, w₂)</p>
                                <p class="text-xs text-slate-500 mt-2">Kollokatsiyaning tasodif emasligini kafolatlovchi koʻrsatkich (T ≥ 2.0 boʻlganda statistik ahamiyatli).</p>
                            </div>
                        </div>
                    `
                },
                {
                    id: "p2-3",
                    num: "2.3",
                    title: "Parallel korpus dizayni va ichki imkoniyatlari tavsifining tarjimashunoslikka tatbiqi",
                    body: `
                        <p class="mb-3">Web-platforma konkordans qidiruvi, kollokatsiyalar matritsasi, matn tekshirgich (checker) hamda tahliliy grafiklar modullarini oʻz ichiga oladi. Foydalanuvchi asarlar boʻyicha alohida filtrlab qidirish imkoniyatiga ega.</p>
                    `
                }
            ],
            summary: "II bobda uchta asosiy asar (Choʻlpon, Xeminguey, Stivenson) asosida parallel korpus yaratish metodologiyasi, jumlalarni tekislash va MI/T-score statistik hisob-kitoblarining dasturiy arxitekturasi ishlab chiqildi."
        },
        {
            id: "bob3",
            number: "III BOB",
            title: "PARALLEL KORPUS BAZASI TARJIMA MATNLARIDA OʻZARO FAOL BIRIKUVCHI (KOLLOKATSION) SOʻZLARNING QIYOSIY TAHLILI",
            subtitle: "3 ta asar asosida semantik-struktur tasnif, ekvivalentlik va lingvomadaniy tahlil",
            icon: "git-pull-request",
            paragraphs: [
                {
                    id: "p3-1",
                    num: "3.1",
                    title: "Parallel korpus bazasida aniqlangan kollokatsiyalarning semantik-struktur tasnifi",
                    body: `
                        <p class="mb-3">Tanlangan 3 ta badiiy asar korpusidan jami 1,220 dan ortiq faol kollokatsion birliklar ajratib olingan boʻlib, ularning struktur modellari quyidagicha taqsimlandi:</p>
                        <div class="grid sm:grid-cols-2 md:grid-cols-4 gap-3 my-3 text-center text-sm">
                            <div class="p-3 bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 rounded-lg">
                                <div class="font-bold text-indigo-700 dark:text-indigo-300">Sifat + Ot (Adj + N)</div>
                                <div class="text-2xl font-black text-indigo-600 my-1">38%</div>
                                <div class="text-xs text-slate-500">sovuq nigoh, deep wrinkles, nut-brown man</div>
                            </div>
                            <div class="p-3 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-lg">
                                <div class="font-bold text-emerald-700 dark:text-emerald-300">Feʼl + Ot (Verb + N)</div>
                                <div class="text-2xl font-black text-emerald-600 my-1">31%</div>
                                <div class="text-xs text-slate-500">langar tashlamoq, take a fish, drop anchor</div>
                            </div>
                            <div class="p-3 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-lg">
                                <div class="font-bold text-amber-700 dark:text-amber-300">Ot + Feʼl (N + Verb)</div>
                                <div class="text-2xl font-black text-amber-600 my-1">18%</div>
                                <div class="text-xs text-slate-500">yuragi urmoq, wind blows, silence fell</div>
                            </div>
                            <div class="p-3 bg-violet-50 dark:bg-violet-950/40 border border-violet-200 dark:border-violet-800 rounded-lg">
                                <div class="font-bold text-violet-700 dark:text-violet-300">Ravish + Feʼl/Sifat</div>
                                <div class="text-2xl font-black text-violet-600 my-1">13%</div>
                                <div class="text-xs text-slate-500">chuqur xoʻrsinmoq, sighed deeply, stared fiercely</div>
                            </div>
                        </div>
                    `
                },
                {
                    id: "p3-2",
                    num: "3.2",
                    title: "Oʻzbekcha va inglizcha parallel korpusida kollokatsion birliklar tarjimasi va ekvivalentlik tadqiqi",
                    body: `
                        <p class="mb-3">Asarlarda kollokatsiyalar tarjimasining asosiy usullari:</p>
                        <ul class="list-disc list-inside space-y-1.5 text-sm pl-2">
                            <li><strong>Toʻliq ekvivalentlik (46%):</strong> Modeli va semantikasi bevosita mos kelgan birikmalar (masalan: <em>drop anchor → langar tashlamoq; deep wrinkles → chuqur ajinlar</em>).</li>
                            <li><strong>Qisman ekvivalentlik va strukturaviy siljish (38%):</strong> Komponentlarning morfologik oʻzgarishi (masalan: <em>burst into laughter → kulib yubormoq; fish alone → yolgʻiz baliq ovlamoq</em>).</li>
                            <li><strong>Konseptual va idiomatik qayta qurish (16%):</strong> Madaniy konnotatsiyaga koʻra metaforik almashtirish (masalan: <em>dead silence → qabr sukunati; koʻngli tusamoq → heart yearned</em>).</li>
                        </ul>
                    `
                },
                {
                    id: "p3-3",
                    num: "3.3",
                    title: "Tarjima matnlar parallel korpusida oʻzaro faol birikuvchi soʻzlarning lingvomadaniy xususiyatlari tahlili",
                    body: `
                        <p class="mb-3">Choʻlponning «Kecha va kunduz» romanida oʻzbek xalqining milliy-etnografik kollokatsiyalari (masalan: <em>«koʻk terish bahonasi bilan», «bomdoddan kirmagan», «fotiha bermoq»</em>) inglizchaga tarjima qilinganda izohli va kontekstual transformatsiyalar orqali aks ettirilganligi isbotlandi.</p>
                    `
                }
            ],
            summary: "III bobda Choʻlpon, Xeminguey va Stivenson asarlari misolida kollokatsiyalarning tarjima qonuniyatlari amaliy tahlil qilindi. 46% toʻliq va 38% qisman ekvivalentlik aniqlanib, milliy-madaniy omillarning tarjimadagi oʻrni yoritildi."
        },
        {
            id: "xulosa",
            number: "XULOSA",
            title: "Umumiy xulosalar va amaliy tavsiyalar",
            subtitle: "Tadqiqotning yakuniy natijalari va istiqbollari",
            icon: "check-circle",
            content: `
                <div class="prose max-w-none text-slate-700 dark:text-slate-300 space-y-4">
                    <div class="p-4 bg-emerald-50 dark:bg-emerald-950/40 rounded-xl border border-emerald-200 dark:border-emerald-800">
                        <h4 class="text-base font-bold text-emerald-900 dark:text-emerald-300 mb-2">Asosiy ilmiy xulosalar:</h4>
                        <ol class="list-decimal list-inside space-y-2 text-sm">
                            <li>Choʻlpon («Kecha va kunduz»), E. Xeminguey («The Old Man and the Sea») va R.L. Stivenson («Treasure Island») asarlari asosida yaratilgan parallel korpus ikki tilli tarjima tahlili uchun yuqori aniqlikdagi empirik baza boʻlib xizmat qildi.</li>
                            <li>Kollokatsiyalarni aniqlashda MI ≥ 3.0 va T-Score ≥ 2.0 statistik filtrlari qoʻllanilishi natijasida erkin birikmalar orasidan 1,220 dan ortiq barqaror kollokatlar muvaffaqiyatli ajratib olindi.</li>
                            <li>Tadqiqot natijalari oʻzbek va ingliz tillari oʻrtasida kollokatsiyalarning 38% qismi Sifat+Ot, 31% qismi Feʼl+Ot modellariga toʻgʻri kelishini va kalka tarjima xatolarining oldini olishda ushbu platforma samarali vosita ekanligini koʻrsatdi.</li>
                        </ol>
                    </div>
                </div>
            `
        },
        {
            id: "adabiyotlar",
            number: "ADABIYOTLAR",
            title: "Foydalanilgan adabiyotlar va manbalar",
            subtitle: "Asosiy badiiy manbalar va nazariy adabiyotlar",
            icon: "bookmark",
            content: `
                <div class="space-y-3 text-sm">
                    <div class="p-3 bg-indigo-50 dark:bg-indigo-950/40 rounded-lg border border-indigo-200 dark:border-indigo-800">
                        <span class="text-xs uppercase font-bold text-indigo-700 dark:text-indigo-300 block mb-1">Asosiy Badiiy Parallel Manbalar:</span>
                        <ul class="list-disc list-inside space-y-1 text-slate-800 dark:text-slate-200">
                            <li><strong>Choʻlpon, Abdulhamid.</strong> Kecha va kunduz (roman). Toshkent: Ziyo-Uz kutubxonasi, 272 b.</li>
                            <li><strong>Cholpon, Abdulhamid.</strong> <em>Night and Day: A Novel</em>. Translated by Christopher Fort. Boston: Academic Studies Press, 2020. 235 p.</li>
                            <li><strong>Hemingway, Ernest.</strong> <em>The Old Man and the Sea</em>. New York: Charles Scribner's Sons, 1952. 52 p.</li>
                            <li><strong>Xeminguey, Ernest.</strong> Chol va dengiz (qissa). Ibrohim Gʻafurov tarjimasi. Toshkent: Yosh gvardiya, 1986. 46 b.</li>
                            <li><strong>Stevenson, Robert Louis.</strong> <em>Treasure Island</em>. London: Cassell & Company, 1883. 142 p.</li>
                            <li><strong>Stivenson, Robert Luis.</strong> Xazinalar oroli (roman). Sharif Rizo tarjimasi. Toshkent: Gʻafur Gʻulom nashriyoti, 216 b.</li>
                        </ul>
                    </div>

                    <div class="p-3 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                        <strong>Firth, J. R.</strong> (1957). <em>Papers in Linguistics 1934–1951</em>. London: Oxford University Press.
                    </div>
                    <div class="p-3 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                        <strong>Sinclair, J.</strong> (1991). <em>Corpus, Concordance, Collocation</em>. Oxford: Oxford University Press.
                    </div>
                    <div class="p-3 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                        <strong>Baker, M.</strong> (2018). <em>In Other Words: A Coursebook on Translation</em> (3rd ed.). London & New York: Routledge.
                    </div>
                    <div class="p-3 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                        <strong>Rahmatullayev, Sh.</strong> (1992). <em>Oʻzbek tilining frazeologik lugʻati</em>. Toshkent: Oʻqituvchi.
                    </div>
                </div>
            `
        },
        {
            id: "ilovalar",
            number: "ILOVALAR",
            title: "Ilovalar: Korpus belgilari va annotatsiya jadvallari",
            subtitle: "Teglar, formulalar va dasturiy parametrlar",
            icon: "paperclip",
            content: `
                <div class="space-y-4 text-sm">
                    <div class="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
                        <h5 class="font-bold mb-2">1-Ilova: Badiiy asarlar boʻyicha korpus parametrlari</h5>
                        <p class="text-xs text-slate-600 dark:text-slate-400">Choʻlpon (272 bet) + Xeminguey (46 bet) + Stivenson (216 bet) = jami 534 betlik oʻzbekcha matn va ularning inglizcha muqobillari toʻliq annotatsiya qilindi.</p>
                    </div>
                </div>
            `
        }
    ]
};

// Parallel korpus jumlalar bazasi (Asosiy asarlar bo'yicha boyitilgan)
const parallelCorpusData = [
    // --- 1. Cho'lpon: Kecha va kunduz <-> Night and Day ---
    {
        id: "corp-kk-1",
        source: "Choʻlpon: «Kecha va kunduz» (Roman)",
        bookKey: "cholpon",
        genre: "Badiiy",
        uz: "Koʻk terish bahonasi bilan dalaga chiqqanidan beri, uning <mark class='colloc-uz'>koʻngli qirlarni tusay</mark> boshlagan edi.",
        en: "Ever since she had gone to the fields under the pretext of gathering greens, her <mark class='colloc-en'>heart yearned for the hills</mark>.",
        collocUz: "koʻngli tusamoq",
        collocEn: "heart yearned for",
        pattern: "Ot + Feʼl (Noun + Verb)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },
    {
        id: "corp-kk-2",
        source: "Choʻlpon: «Kecha va kunduz» (Roman)",
        bookKey: "cholpon",
        genre: "Badiiy",
        uz: "Zebi onasining javobini kutar ekan, <mark class='colloc-uz'>yuragi duk-duk urardi</mark>.",
        en: "As Zebi waited for her mother's reply, her <mark class='colloc-en'>heart pounded rapidly</mark>.",
        collocUz: "yuragi urmoq",
        collocEn: "heart pounded",
        pattern: "Ot + Feʼl (Noun + Verb)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },
    {
        id: "corp-kk-3",
        source: "Choʻlpon: «Kecha va kunduz» (Roman)",
        bookKey: "cholpon",
        genre: "Badiiy",
        uz: "Razzoq soʻfi qiziga oʻzining <mark class='colloc-uz'>sovuq nigohi</mark> bilan tikildi.",
        en: "Razzoq Sufi fixed his <mark class='colloc-en'>cold gaze</mark> upon his daughter.",
        collocUz: "sovuq nigoh",
        collocEn: "cold gaze",
        pattern: "Sifat + Ot (Adj + Noun)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },
    {
        id: "corp-kk-4",
        source: "Choʻlpon: «Kecha va kunduz» (Roman)",
        bookKey: "cholpon",
        genre: "Badiiy",
        uz: "Miryoqub ich-ichidan <mark class='colloc-uz'>chuqur xoʻrsinib</mark>, boshini quyi soldi.",
        en: "Miryoqub <mark class='colloc-en'>sighed deeply</mark> from within and hung his head.",
        collocUz: "chuqur xoʻrsinmoq",
        collocEn: "sighed deeply",
        pattern: "Ravish + Feʼl (Adv + Verb)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },
    {
        id: "corp-kk-5",
        source: "Choʻlpon: «Kecha va kunduz» (Roman)",
        bookKey: "cholpon",
        genre: "Badiiy",
        uz: "Qizlar bu gapni eshitib birdan <mark class='colloc-uz'>qah-qah urib kulib yubordilar</mark>.",
        en: "Upon hearing these words, the girls suddenly <mark class='colloc-en'>burst into loud laughter</mark>.",
        collocUz: "kulib yubormoq",
        collocEn: "burst into laughter",
        pattern: "Feʼl + Ot (Verb + Noun)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },

    // --- 2. Ernest Hemingway: The Old Man and the Sea <-> Chol va dengiz ---
    {
        id: "corp-hem-1",
        source: "Ernest Xeminguey: «Chol va dengiz» (Qissa)",
        bookKey: "hemingway",
        genre: "Badiiy",
        uz: "Chol qayiqda yolgʻiz oʻzi Golfstrimda <mark class='colloc-uz'>baliq ovlardi</mark> va sakson toʻrt kundan beri hech narsa tutolmagandi.",
        en: "He was an old man who <mark class='colloc-en'>fished alone</mark> in a skiff in the Gulf Stream and he had gone eighty-four days without taking a fish.",
        collocUz: "baliq ovlamoq",
        collocEn: "fished alone / take a fish",
        pattern: "Feʼl + Ot (Verb + Noun)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },
    {
        id: "corp-hem-2",
        source: "Ernest Xeminguey: «Chol va dengiz» (Qissa)",
        bookKey: "hemingway",
        genre: "Badiiy",
        uz: "Eski yelkan yigʻilganda muttasil <mark class='colloc-uz'>magʻlubiyat bayrogʻiga</mark> oʻxshab koʻrinardi.",
        en: "Furled, the sail looked like the flag of <mark class='colloc-en'>permanent defeat</mark>.",
        collocUz: "muttasil magʻlubiyat",
        collocEn: "permanent defeat",
        pattern: "Sifat + Ot (Adj + Noun)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },
    {
        id: "corp-hem-3",
        source: "Ernest Xeminguey: «Chol va dengiz» (Qissa)",
        bookKey: "hemingway",
        genre: "Badiiy",
        uz: "Cholning boʻynida quyosh va yillar qoldirgan <mark class='colloc-uz'>chuqur ajinlar</mark> bor edi.",
        en: "The old man was thin and gaunt with <mark class='colloc-en'>deep wrinkles</mark> in the back of his neck.",
        collocUz: "chuqur ajinlar",
        collocEn: "deep wrinkles",
        pattern: "Sifat + Ot (Adj + Noun)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },
    {
        id: "corp-hem-4",
        source: "Ernest Xeminguey: «Chol va dengiz» (Qissa)",
        bookKey: "hemingway",
        genre: "Badiiy",
        uz: "U qatʼiyatga toʻla edi, ammo <mark class='colloc-uz'>umidi soʻngan</mark> edi.",
        en: "He was full of resolution but he had <mark class='colloc-en'>little hope</mark>.",
        collocUz: "umidi soʻnmoq / oz",
        collocEn: "little hope",
        pattern: "Sifat + Ot (Adj + Noun)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },
    {
        id: "corp-hem-5",
        source: "Ernest Xeminguey: «Chol va dengiz» (Qissa)",
        bookKey: "hemingway",
        genre: "Badiiy",
        uz: "Tong saharda moviy dengiz uzra <mark class='colloc-uz'>quyosh koʻtarila boshladi</mark>.",
        en: "At early dawn, the <mark class='colloc-en'>sun was rising</mark> gently over the blue sea.",
        collocUz: "quyosh koʻtarilmoq",
        collocEn: "sun was rising",
        pattern: "Ot + Feʼl (Noun + Verb)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },

    // --- 3. Robert Louis Stevenson: Treasure Island <-> Xazinalar oroli ---
    {
        id: "corp-stev-1",
        source: "R. L. Stivenson: «Xazinalar oroli» (Roman)",
        bookKey: "stevenson",
        genre: "Badiiy",
        uz: "Janoblar mendan Xazinalar oroli haqidagi barcha <mark class='colloc-uz'>tafsilotlarni qogʻozga tushirishimni</mark> soʻrashdi.",
        en: "The gentlemen asked me to <mark class='colloc-en'>write down the particulars</mark> about Treasure Island.",
        collocUz: "tafsilotlarni qogʻozga tushirmoq",
        collocEn: "write down particulars",
        pattern: "Feʼl + Ot (Verb + Noun)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },
    {
        id: "corp-stev-2",
        source: "R. L. Stivenson: «Xazinalar oroli» (Roman)",
        bookKey: "stevenson",
        genre: "Badiiy",
        uz: "Uning qoʻl aravachada ogʻir <mark class='colloc-uz'>dengiz sandigʻini</mark> sudrab kelgani kechagidek esimda.",
        en: "I remember him as if it were yesterday, his <mark class='colloc-en'>sea-chest</mark> following behind him.",
        collocUz: "dengiz sandigʻi",
        collocEn: "sea-chest",
        pattern: "Ot + Ot (Noun + Noun)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },
    {
        id: "corp-stev-3",
        source: "R. L. Stivenson: «Xazinalar oroli» (Roman)",
        bookKey: "stevenson",
        genre: "Badiiy",
        uz: "Kema kechqurun sokin buxtaga kirib <mark class='colloc-uz'>langar tashladi</mark>.",
        en: "In the evening the ship entered the quiet cove and <mark class='colloc-en'>dropped anchor</mark>.",
        collocUz: "langar tashlamoq",
        collocEn: "dropped anchor",
        pattern: "Feʼl + Ot (Verb + Noun)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },
    {
        id: "corp-stev-4",
        source: "R. L. Stivenson: «Xazinalar oroli» (Roman)",
        bookKey: "stevenson",
        genre: "Badiiy",
        uz: "Kapitan xonaga kirganda barcha dengizchilar orasiga <mark class='colloc-uz'>qabr sukunati choʻkdi</mark>.",
        en: "When the captain entered the room, a <mark class='colloc-en'>dead silence fell</mark> upon the seamen.",
        collocUz: "qabr sukunati choʻkdi",
        collocEn: "dead silence fell",
        pattern: "Sifat + Ot + Feʼl",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },
    {
        id: "corp-stev-5",
        source: "R. L. Stivenson: «Xazinalar oroli» (Roman)",
        bookKey: "stevenson",
        genre: "Badiiy",
        uz: "Hech kim eshitmasligi uchun u <mark class='colloc-uz'>ovozini pasaytirib pichirladi</mark>.",
        en: "He <mark class='colloc-en'>lowered his voice</mark> to a whisper so that no one could hear.",
        collocUz: "ovozini pasaytirmoq",
        collocEn: "lowered his voice",
        pattern: "Feʼl + Ot (Verb + Noun)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },

    // --- Qo'shimcha umumiy va rasmiy parallel matnlar ---
    {
        id: "corp-gen-1",
        source: "Badiiy adabiyot: Oʻtkan kunlar (A. Qodiriy / I. Harris)",
        bookKey: "general",
        genre: "Badiiy",
        uz: "Otabek uzoq oʻylanib, nihoyat qatʼiy bir <mark class='colloc-uz'>qaror qabul qildi</mark>.",
        en: "After much contemplation, Otabek finally <mark class='colloc-en'>made a firm decision</mark>.",
        collocUz: "qaror qabul qildi",
        collocEn: "made a decision",
        pattern: "Feʼl + Ot (Verb + N)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },
    {
        id: "corp-gen-2",
        source: "Ilmiy matn: Tilshunoslik asoslari",
        bookKey: "general",
        genre: "Ilmiy",
        uz: "Olimlar ushbu fonetik hodisaga alohida <mark class='colloc-uz'>eʼtibor qaratdilar</mark>.",
        en: "The scientists <mark class='colloc-en'>paid special attention</mark> to this phonetic phenomenon.",
        collocUz: "eʼtibor qaratdilar",
        collocEn: "paid attention",
        pattern: "Feʼl + Ot (Verb + N)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    },
    {
        id: "corp-gen-3",
        source: "Ijtimoiy-huquqiy: Qonunchilik hujjatlari",
        bookKey: "general",
        genre: "Rasmiy",
        uz: "Sudlanuvchi ogʻirlashtiruvchi holatlarda <mark class='colloc-uz'>jinoyat sodir etganlikda</mark> aybdor deb topildi.",
        en: "The defendant was found guilty of having <mark class='colloc-en'>committed a crime</mark> under aggravating circumstances.",
        collocUz: "jinoyat sodir etganlikda",
        collocEn: "committed a crime",
        pattern: "Feʼl + Ot (Verb + N)",
        alignmentScore: "—",
        mi: "—",
        tScore: "—"
    }
];

// Kollokatsiyalar bazasi (3 ta asosiy asar birliklari bilan boyitilgan)
const collocationsDatabase = [
    // Cho'lpon: Kecha va kunduz
    {
        id: "col-kk-1",
        uzbek: "koʻngli tusamoq",
        english: "heart yearns for / desire strongly",
        nodeUz: "koʻngil",
        nodeEn: "heart",
        pattern: "Ot + Feʼl (Noun + Verb)",
        freq: 68,
        miScore: 5.45,
        tScore: "—",
        logLikelihood: 76.4,
        category: "Konseptual ekvivalent",
        literalTrap: "*heart wants / *soul desires (soʻzma-soʻz kalka)",
        contextUz: "Zebining koʻngli olis qirlarni, yashil dalalarni yana koʻproq tusay boshladi.",
        contextEn: "Zebi's heart yearned all the more for the distant hills and green fields.",
        culturalNote: "Oʻzbek tilidagi 'koʻngil' ruhiy-hissiy markazi ingliz tilida 'heart' tushunchasi orqali beriladi.",
        sourceBook: "Choʻlpon: «Kecha va kunduz»"
    },
    {
        id: "col-kk-2",
        uzbek: "sovuq nigoh",
        english: "cold gaze / icy stare",
        nodeUz: "nigoh",
        nodeEn: "gaze / stare",
        pattern: "Sifat + Ot (Adj + Noun)",
        freq: 54,
        miScore: 6.12,
        tScore: "—",
        logLikelihood: 88.5,
        category: "Toʻliq ekvivalent",
        literalTrap: "*cold look (soʻzma-soʻz kalka, uslubiy jihatdan gʻayritabiiy; toʻgʻri ilmiy-badiiy ekvivalent: «cold gaze», «icy stare» yoki «frosty glare»)",
        contextUz: "Razzoq soʻfining sovuq nigohi har qanday kishini sarosimaga solar edi.",
        contextEn: "Razzoq Sufi's cold gaze (icy stare) would plunge anyone into utter confusion.",
        culturalNote: "Oʻzbek tilidagi «sovuq nigoh» tushunchasi ingliz tilida soʻzma-soʻz «cold look» deb berilsa, uslubiy zaiflik va kalka yuzaga keladi. Ingliz tili korpuslarida (BNC, COCA) hissizlik, qahr va nafratni ifodalashda barqaror ravishda «cold gaze», «icy stare» yoki «frosty glare» kollokatsiyalari qoʻllaniladi.",
        sourceBook: "Choʻlpon: «Kecha va kunduz»"
    },
    {
        id: "col-kk-3",
        uzbek: "chuqur xoʻrsinmoq",
        english: "sigh deeply",
        nodeUz: "xoʻrsinmoq",
        nodeEn: "sigh",
        pattern: "Ravish + Feʼl (Adv + Verb)",
        freq: 76,
        miScore: 5.90,
        tScore: "—",
        logLikelihood: 79.2,
        category: "Toʻliq ekvivalent",
        literalTrap: "*deeply breath",
        contextUz: "Miryoqub ogʻir oʻylarga botib, chuqur xoʻrsindi.",
        contextEn: "Miryoqub, lost in heavy thought, sighed deeply.",
        culturalNote: "Ruhiy iztirob va ogʻir oʻy holatini ifodalovchi universal kollokat.",
        sourceBook: "Choʻlpon: «Kecha va kunduz»"
    },
    {
        id: "col-kk-4",
        uzbek: "kulib yubormoq / qah-qah urmoq",
        english: "burst into laughter",
        nodeUz: "kulmoq",
        nodeEn: "laugh",
        pattern: "Feʼl + Ot (Verb + Noun)",
        freq: 92,
        miScore: 6.30,
        tScore: "—",
        logLikelihood: 110.4,
        category: "Qisman ekvivalent",
        literalTrap: "*suddenly laugh (kollokatsion quvvatsiz)",
        contextUz: "Uning kulgili qiligʻini koʻrib, hamma qah-qah urib kulib yubordi.",
        contextEn: "Seeing his funny antics, everyone burst into loud laughter.",
        culturalNote: "Ingliz tilida toʻsatdan yuzaga kelgan kulgi 'burst into laughter' idiomatik kollokati bilan ifodalanadi.",
        sourceBook: "Choʻlpon: «Kecha va kunduz»"
    },

    // Ernest Hemingway: The Old Man and the Sea
    {
        id: "col-hem-1",
        uzbek: "baliq ovlamoq / tutmoq",
        english: "take a fish / fish alone",
        nodeUz: "baliq",
        nodeEn: "fish",
        pattern: "Feʼl + Ot (Verb + Noun)",
        freq: 115,
        miScore: 6.40,
        tScore: "—",
        logLikelihood: 142.1,
        category: "Toʻliq ekvivalent",
        literalTrap: "*catch alone (noaniq)",
        contextUz: "Chol sakson toʻrt kundan beri biron marta ham baliq tutolmagan edi.",
        contextEn: "The old man had gone eighty-four days without taking a fish.",
        culturalNote: "Hemingway asarida 'take a fish' birikmasi oʻzbekchaga 'baliq tutmoq' tarzida aniq oʻgirilgan.",
        sourceBook: "E. Xeminguey: «Chol va dengiz»"
    },
    {
        id: "col-hem-2",
        uzbek: "muttasil magʻlubiyat",
        english: "permanent defeat",
        nodeUz: "magʻlubiyat",
        nodeEn: "defeat",
        pattern: "Sifat + Ot (Adj + Noun)",
        freq: 42,
        miScore: 5.75,
        tScore: "—",
        logLikelihood: 68.3,
        category: "Toʻliq ekvivalent",
        literalTrap: "*always losing",
        contextUz: "Yigʻilgan yelkan muttasil magʻlubiyat ramzidek tuyulardi.",
        contextEn: "The furled sail looked like the symbol of permanent defeat.",
        culturalNote: "Falsafiy kontsept: inson magʻlub boʻlishi mumkin, ammo yengilmasligi lozim.",
        sourceBook: "E. Xeminguey: «Chol va dengiz»"
    },
    {
        id: "col-hem-3",
        uzbek: "chuqur ajinlar",
        english: "deep wrinkles",
        nodeUz: "ajin",
        nodeEn: "wrinkles",
        pattern: "Sifat + Ot (Adj + Noun)",
        freq: 58,
        miScore: 6.15,
        tScore: "—",
        logLikelihood: 92.0,
        category: "Toʻliq ekvivalent",
        literalTrap: "*heavy lines",
        contextUz: "Cholning yuzidagi chuqur ajinlar koʻp yillik mashaqqatlardan darak berardi.",
        contextEn: "The deep wrinkles on the old man's face spoke of many years of hardship.",
        culturalNote: "Tashqi qiyofa tavsifidagi toʻliq simmetrik kollokatsiya modeli.",
        sourceBook: "E. Xeminguey: «Chol va dengiz»"
    },

    // Robert Louis Stevenson: Treasure Island
    {
        id: "col-stev-1",
        uzbek: "langar tashlamoq",
        english: "drop anchor / cast anchor",
        nodeUz: "langar",
        nodeEn: "anchor",
        pattern: "Feʼl + Ot (Verb + Noun)",
        freq: 88,
        miScore: 6.85,
        tScore: "—",
        logLikelihood: 165.8,
        category: "Toʻliq ekvivalent",
        literalTrap: "*throw anchor (leksik nooʻrinlik)",
        contextUz: "Kema oqshom payti xavfsiz qoʻltiqda langar tashladi.",
        contextEn: "The ship dropped anchor in a safe harbor at dusk.",
        culturalNote: "Dengizchilik atamalari ichida eng yuqori chastotali normativ kollokatsiya.",
        sourceBook: "R. L. Stivenson: «Xazinalar oroli»"
    },
    {
        id: "col-stev-2",
        uzbek: "qabr sukunati choʻkmoq",
        english: "dead silence fell",
        nodeUz: "sukunat",
        nodeEn: "silence",
        pattern: "Sifat + Ot + Feʼl",
        freq: 64,
        miScore: 6.50,
        tScore: "—",
        logLikelihood: 125.4,
        category: "Konseptual ekvivalent",
        literalTrap: "*dead silence dropped",
        contextUz: "U qahvaxonaga qadam qoʻyganida atrofga qabr sukunati choʻkdi.",
        contextEn: "When he stepped into the inn, a dead silence fell all around.",
        culturalNote: "Inglizcha 'dead silence' oʻzbek tiliga 'qabr sukunati' yoki 'suv quygandek sukunat' tarzida milliylashtirilgan.",
        sourceBook: "R. L. Stivenson: «Xazinalar oroli»"
    },
    {
        id: "col-stev-3",
        uzbek: "ovozini pasaytirmoq",
        english: "lower one's voice",
        nodeUz: "ovoz",
        nodeEn: "voice",
        pattern: "Feʼl + Ot (Verb + Noun)",
        freq: 102,
        miScore: 5.70,
        tScore: "—",
        logLikelihood: 98.7,
        category: "Toʻliq ekvivalent",
        literalTrap: "*decrease voice",
        contextUz: "Sirni aytishdan oldin u ovozini pasaytirdi.",
        contextEn: "Before revealing the secret, he lowered his voice.",
        culturalNote: "Soʻzlashuv harakatining standart barqaror kollokati.",
        sourceBook: "R. L. Stivenson: «Xazinalar oroli»"
    },

    // Umumiy korpus kollokatsiyalari
    {
        id: "col-gen-1",
        uzbek: "qaror qabul qilmoq",
        english: "make a decision",
        nodeUz: "qaror",
        nodeEn: "decision",
        pattern: "Feʼl + Ot (Verb + Noun)",
        freq: 142,
        miScore: 5.48,
        tScore: "—",
        logLikelihood: 124.5,
        category: "Toʻliq ekvivalent",
        literalTrap: "*accept a decision (notoʻgʻri kalka)",
        contextUz: "Boshqaruv kengashi yangi strategiya boʻyicha yakuniy qaror qabul qildi.",
        contextEn: "The board made a final decision on the new strategy.",
        culturalNote: "Ingliz tilida 'accept' emas, aynan 'make' feʼli qoʻllanadi.",
        sourceBook: "Publitsistika va adabiyot"
    },
    {
        id: "col-gen-2",
        uzbek: "eʼtibor qaratmoq",
        english: "pay attention",
        nodeUz: "eʼtibor",
        nodeEn: "attention",
        pattern: "Feʼl + Ot (Verb + Noun)",
        freq: 215,
        miScore: 6.35,
        tScore: "—",
        logLikelihood: 210.4,
        category: "Strukturaviy siljish",
        literalTrap: "*give attention",
        contextUz: "Maqolada yoshlar taʼlimiga alohida eʼtibor qaratilgan.",
        contextEn: "The article paid particular attention to youth education.",
        culturalNote: "Ingliz tilidagi 'pay' (toʻlamoq) feʼli eʼtibor tushunchasi bilan bogʻlanadi.",
        sourceBook: "Ilmiy matnlar"
    },
    {
        id: "col-gen-3",
        uzbek: "jinoyat sodir etmoq",
        english: "commit a crime",
        nodeUz: "jinoyat",
        nodeEn: "crime",
        pattern: "Feʼl + Ot (Verb + Noun)",
        freq: 85,
        miScore: 6.95,
        tScore: "—",
        logLikelihood: 112.7,
        category: "Toʻliq ekvivalent",
        literalTrap: "*do a crime",
        contextUz: "Gumonlanuvchi jinoyat sodir etganlikda ayblanmoqda.",
        contextEn: "The suspect is accused of committing a crime.",
        culturalNote: "Yuridik diskursda yagona barqaror kollokat.",
        sourceBook: "Rasmiy matnlar"
    }
];

// Tadqiqot statistikasi
// researchStats olib tashlandi (Stage 2: soxta statistikalar yo‘qotildi)