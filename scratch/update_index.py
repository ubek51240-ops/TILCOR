import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add tokens.css if not present
if 'css/tokens.css' not in content:
    content = content.replace('<link rel="stylesheet" href="css/styles.css">', 
                              '<link rel="stylesheet" href="css/styles.css">\n    <link rel="stylesheet" href="css/tokens.css">')

# 2. Update Header & Navigation (C1)
old_header_pattern = re.compile(r'<!-- Top Header & Navigation -->.*?<!-- MAIN CONTENT CONTAINER -->', re.DOTALL)

new_header = '''<!-- Top Header & Navigation -->
    <header class="sticky top-0 z-40 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 transition-colors">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-16">
                
                <!-- Logo & Brand -->
                <div class="flex items-center gap-3 cursor-pointer" onclick="app.switchTab('home')">
                    <div class="w-10 h-10 rounded-xl bg-[#1e3a5f] flex items-center justify-center text-white shadow-md font-black tracking-tight text-sm">
                        TC
                    </div>
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="font-extrabold text-base sm:text-lg tracking-tight text-slate-900 dark:text-white">
                                TILCOR
                            </span>
                            <span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 font-mono">
                                Parallel Korpus
                            </span>
                        </div>
                        <p class="text-[11px] text-slate-500 dark:text-slate-400 leading-none">O‘zbek–ingliz parallel korpusi va leksikografik tahlil</p>
                    </div>
                </div>

                <!-- Desktop Nav Links (C1: 5-6 asosiy tugma, ixcham dropdownlar) -->
                <nav class="hidden md:flex items-center space-x-1">
                    <button data-tab-target="home" class="px-3 py-2 rounded-xl text-xs font-semibold transition nav-active flex items-center gap-1.5">
                        <i data-lucide="home" class="w-4 h-4"></i> Bosh sahifa
                    </button>

                    <!-- Korpus Dropdown -->
                    <div class="tilcor-dropdown">
                        <button class="px-3 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition flex items-center gap-1.5">
                            <i data-lucide="split" class="w-4 h-4 text-indigo-600"></i> Korpus <i data-lucide="chevron-down" class="w-3 h-3 text-slate-400"></i>
                        </button>
                        <div class="tilcor-dropdown-menu">
                            <a href="#" onclick="event.preventDefault(); app.switchTab('corpus');" class="tilcor-dropdown-item">
                                <i data-lucide="search" class="w-3.5 h-3.5 text-indigo-600"></i> Korpus Qidiruvi
                            </a>
                            <a href="kwic_concordance.html" class="tilcor-dropdown-item">
                                <i data-lucide="align-left" class="w-3.5 h-3.5 text-indigo-600"></i> KWIC Konkordans
                            </a>
                            <a href="preview_alignment_queue.html" class="tilcor-dropdown-item">
                                <i data-lucide="layers" class="w-3.5 h-3.5 text-indigo-600"></i> Segmentlar Tahlili
                            </a>
                        </div>
                    </div>

                    <!-- Kollokatsiyalar Dropdown -->
                    <div class="tilcor-dropdown">
                        <button class="px-3 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition flex items-center gap-1.5">
                            <i data-lucide="sparkles" class="w-4 h-4 text-emerald-600"></i> Kollokatsiyalar <i data-lucide="chevron-down" class="w-3 h-3 text-slate-400"></i>
                        </button>
                        <div class="tilcor-dropdown-menu">
                            <a href="#" onclick="event.preventDefault(); app.switchTab('collocations');" class="tilcor-dropdown-item">
                                <i data-lucide="list" class="w-3.5 h-3.5 text-emerald-600"></i> Barcha kollokatsiyalar
                            </a>
                            <a href="#" onclick="event.preventDefault(); app.switchTab('collocations'); document.getElementById('collocSourceFilter').value='IELTS Academic Collocations List'; collocationManager.applyFilters();" class="tilcor-dropdown-item">
                                <i data-lucide="graduation-cap" class="w-3.5 h-3.5 text-emerald-600"></i> ACL Academic
                            </a>
                            <a href="#" onclick="event.preventDefault(); app.switchTab('collocations'); document.getElementById('collocSourceFilter').value='Cambridge Collocations (Intermediate)'; collocationManager.applyFilters();" class="tilcor-dropdown-item">
                                <i data-lucide="book" class="w-3.5 h-3.5 text-emerald-600"></i> Cambridge Collocations
                            </a>
                        </div>
                    </div>

                    <!-- Lug'at -->
                    <button data-tab-target="dictionary" class="px-3 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition flex items-center gap-1.5">
                        <i data-lucide="book-a" class="w-4 h-4 text-amber-600"></i> Lug‘at
                    </button>

                    <!-- Metodologiya -->
                    <a href="methodology.html" class="px-3 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition flex items-center gap-1.5">
                        <i data-lucide="file-text" class="w-4 h-4 text-blue-600"></i> Metodologiya
                    </a>

                    <!-- Laboratoriya Dropdown -->
                    <div class="tilcor-dropdown">
                        <button class="px-3 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition flex items-center gap-1.5">
                            <i data-lucide="flask-conical" class="w-4 h-4 text-purple-600"></i> Laboratoriya <i data-lucide="chevron-down" class="w-3 h-3 text-slate-400"></i>
                        </button>
                        <div class="tilcor-dropdown-menu">
                            <a href="#" onclick="event.preventDefault(); app.switchTab('checker');" class="tilcor-dropdown-item">
                                <i data-lucide="check-circle" class="w-3.5 h-3.5 text-purple-600"></i> Kollokatsiyalar sinovchisi
                            </a>
                            <a href="#" onclick="event.preventDefault(); app.switchTab('translator');" class="tilcor-dropdown-item">
                                <i data-lucide="languages" class="w-3.5 h-3.5 text-purple-600"></i> Jonli Tarjimon
                            </a>
                            <a href="#" onclick="event.preventDefault(); app.switchTab('phd');" class="tilcor-dropdown-item">
                                <i data-lucide="bot" class="w-3.5 h-3.5 text-purple-600"></i> AI Assistent (PhD Hub)
                            </a>
                        </div>
                    </div>
                </nav>

                <!-- Right Action Buttons -->
                <div class="flex items-center gap-2">
                    <button id="themeToggleBtn" title="Rejimni almashtirish" class="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition">
                        <i data-lucide="moon" class="w-4 h-4 dark:hidden"></i>
                        <i data-lucide="sun" class="w-4 h-4 hidden dark:block text-amber-400"></i>
                    </button>

                    <!-- Mobile Menu Hamburger Button -->
                    <button id="mobileMenuBtn" onclick="document.getElementById('mobileAccordionMenu').classList.toggle('hidden')" class="md:hidden p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition">
                        <i data-lucide="menu" class="w-5 h-5"></i>
                    </button>
                </div>
            </div>

            <!-- Mobile Accordion Menu (C1: ixcham akkordeon) -->
            <div id="mobileAccordionMenu" class="hidden md:hidden py-3 border-t border-slate-200 dark:border-slate-800 space-y-2 text-xs">
                <button onclick="app.switchTab('home'); document.getElementById('mobileAccordionMenu').classList.add('hidden');" class="w-full text-left px-3 py-2 font-semibold rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800">
                    Bosh sahifa
                </button>
                
                <div class="border-t border-slate-100 dark:border-slate-800/60 pt-1">
                    <div class="font-bold text-slate-400 px-3 py-1 uppercase text-[10px]">Korpus</div>
                    <button onclick="app.switchTab('corpus'); document.getElementById('mobileAccordionMenu').classList.add('hidden');" class="w-full text-left px-5 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-800">Korpus Qidiruvi</button>
                    <a href="kwic_concordance.html" class="block px-5 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-800">KWIC Konkordans</a>
                </div>

                <div class="border-t border-slate-100 dark:border-slate-800/60 pt-1">
                    <div class="font-bold text-slate-400 px-3 py-1 uppercase text-[10px]">Kollokatsiyalar</div>
                    <button onclick="app.switchTab('collocations'); document.getElementById('mobileAccordionMenu').classList.add('hidden');" class="w-full text-left px-5 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-800">Barcha Kollokatsiyalar</button>
                </div>

                <div class="border-t border-slate-100 dark:border-slate-800/60 pt-1">
                    <button onclick="app.switchTab('dictionary'); document.getElementById('mobileAccordionMenu').classList.add('hidden');" class="w-full text-left px-3 py-2 font-semibold hover:bg-slate-100 dark:hover:bg-slate-800">Lug‘at</button>
                </div>

                <div class="border-t border-slate-100 dark:border-slate-800/60 pt-1">
                    <a href="methodology.html" class="block px-3 py-2 font-semibold hover:bg-slate-100 dark:hover:bg-slate-800">Metodologiya</a>
                </div>

                <div class="border-t border-slate-100 dark:border-slate-800/60 pt-1">
                    <div class="font-bold text-slate-400 px-3 py-1 uppercase text-[10px]">Laboratoriya</div>
                    <button onclick="app.switchTab('checker'); document.getElementById('mobileAccordionMenu').classList.add('hidden');" class="w-full text-left px-5 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-800">Kollokatsiyalar sinovchisi</button>
                    <button onclick="app.switchTab('translator'); document.getElementById('mobileAccordionMenu').classList.add('hidden');" class="w-full text-left px-5 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-800">Jonli Tarjimon</button>
                    <button onclick="app.switchTab('phd'); document.getElementById('mobileAccordionMenu').classList.add('hidden');" class="w-full text-left px-5 py-1.5 hover:bg-slate-100 dark:hover:bg-slate-800">PhD Hub (AI Assistent)</button>
                </div>
            </div>
        </div>
    </header>

    <!-- MAIN CONTENT CONTAINER -->'''

content = old_header_pattern.sub(new_header, content)

# 3. Update view-home (C2: Compact Home Page)
old_home_pattern = re.compile(r'<section id="view-home" class="tab-view space-y-10">.*?</section>\s*<!-- ==============================================\s*-->\s*<!-- VIEW: TRANSLATOR', re.DOTALL)

new_home = '''<section id="view-home" class="tab-view space-y-8">
            <!-- C2: Compact Hero & Universal Search -->
            <div class="rounded-3xl bg-[#1e3a5f] text-white p-6 sm:p-10 shadow-xl border border-slate-700/40">
                <div class="max-w-3xl space-y-4">
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-xs font-semibold tracking-wide text-indigo-100">
                        <i data-lucide="graduation-cap" class="w-3.5 h-3.5 text-teal-300"></i>
                        <span>Ilmiy dissertatsiya tadqiqot platformasi</span>
                    </div>

                    <h1 class="text-2xl sm:text-4xl font-extrabold tracking-tight leading-tight">
                        TILCOR — Inglizcha-o‘zbekcha parallel korpus va leksikografik tahlil platformasi
                    </h1>
                    <p class="text-xs sm:text-sm text-slate-200 font-normal leading-relaxed">
                        Inglizcha va o‘zbekcha badiiy asarlar matnlarini parallel qiyoslash, kollokatsiyalarni aniqlash hamda tarjima ekvivalentlarini tadqiq etish uchun yaratilgan ilmiy tizim.
                    </p>

                    <!-- Universal Search Box with UZ / EN Language Switch -->
                    <div class="pt-2">
                        <div class="bg-white rounded-2xl p-2 shadow-lg flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                            <div class="flex items-center pl-3 text-slate-400">
                                <i data-lucide="search" class="w-5 h-5 text-indigo-600"></i>
                            </div>
                            <input type="text" id="homeSearchInput" placeholder="Parallel korpusdan so‘z yoki ibora qidiring (masalan: baliq, sea, yurak, dark)..." class="flex-grow px-3 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none">
                            <div class="flex items-center gap-1.5 border-t sm:border-t-0 sm:border-l border-slate-200 pt-2 sm:pt-0 sm:pl-2">
                                <select id="homeSearchLang" class="text-xs py-2 px-2 bg-slate-50 rounded-lg text-slate-700 border border-slate-200 focus:outline-none font-semibold">
                                    <option value="all">UZ / EN</option>
                                    <option value="en">English (EN)</option>
                                    <option value="uz">O‘zbekcha (UZ)</option>
                                </select>
                                <button onclick="app.executeHomeSearch()" class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 whitespace-nowrap">
                                    <span>Qidirish</span>
                                    <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- C2: Jonli Raqamlar Tasmasi (Statik emas, API dan) -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div class="p-4 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-4">
                    <div class="w-12 h-12 rounded-xl bg-indigo-50 dark:bg-indigo-950/80 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold text-xl shrink-0">
                        <i data-lucide="split" class="w-6 h-6"></i>
                    </div>
                    <div>
                        <span id="stat-total-segments" class="text-2xl font-black text-indigo-600 dark:text-indigo-400 block font-mono">3,811</span>
                        <span class="text-xs font-medium text-slate-500 dark:text-slate-400">Faol parallel gaplar</span>
                    </div>
                </div>

                <div class="p-4 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-4">
                    <div class="w-12 h-12 rounded-xl bg-emerald-50 dark:bg-emerald-950/80 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold text-xl shrink-0">
                        <i data-lucide="sparkles" class="w-6 h-6"></i>
                    </div>
                    <div>
                        <span id="stat-total-collocations" class="text-2xl font-black text-emerald-600 dark:text-emerald-400 block font-mono">6,537</span>
                        <span class="text-xs font-medium text-slate-500 dark:text-slate-400">Ilmiy kollokatsiyalar</span>
                    </div>
                </div>

                <div class="p-4 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-4">
                    <div class="w-12 h-12 rounded-xl bg-amber-50 dark:bg-amber-950/80 text-amber-600 dark:text-amber-400 flex items-center justify-center font-bold text-xl shrink-0">
                        <i data-lucide="book-a" class="w-6 h-6"></i>
                    </div>
                    <div>
                        <span id="stat-total-dict" class="text-2xl font-black text-amber-600 dark:text-amber-400 block font-mono">23,566</span>
                        <span class="text-xs font-medium text-slate-500 dark:text-slate-400">Toza lug‘at maqolalari</span>
                    </div>
                </div>
            </div>

            <!-- C2: 3 ta asosiy kartochka (ixcham) -->
            <div class="grid md:grid-cols-3 gap-5">
                <!-- Card 1: Parallel Korpus -->
                <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm hover:shadow-md transition flex flex-col justify-between space-y-3">
                    <div class="space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="text-[11px] font-bold px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">II bob tadqiqoti</span>
                            <i data-lucide="split" class="w-4 h-4 text-indigo-600"></i>
                        </div>
                        <h3 class="text-base font-bold text-slate-900 dark:text-white">Parallel korpus</h3>
                        <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                            Cho‘lpon («Kecha va kunduz») va Hemingway («Chol va dengiz») asarlarining inglizcha-o‘zbekcha parallel matnlari (3 811 faol segment).
                        </p>
                    </div>
                    <button onclick="app.switchTab('corpus')" class="w-full py-2 rounded-xl bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-bold text-xs hover:bg-indigo-600 hover:text-white transition flex items-center justify-center gap-1.5">
                        Korpusni ochish <i data-lucide="arrow-right" class="w-3 h-3"></i>
                    </button>
                </div>

                <!-- Card 2: Kollokatsiyalar Bazasi -->
                <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm hover:shadow-md transition flex flex-col justify-between space-y-3">
                    <div class="space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="text-[11px] font-bold px-2 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">I–II bob tadqiqoti</span>
                            <i data-lucide="sparkles" class="w-4 h-4 text-emerald-600"></i>
                        </div>
                        <h3 class="text-base font-bold text-slate-900 dark:text-white">Kollokatsiyalar bazasi</h3>
                        <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                            Ilmiy va akademik nutq birikmalari (6 537 ta birikma: ACL, Cambridge Collocations, 1000 Collocations). O‘zbekcha tarjimalari ilmiy tahlil uchun tavsiya qilingan.
                        </p>
                    </div>
                    <button onclick="app.switchTab('collocations')" class="w-full py-2 rounded-xl bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-bold text-xs hover:bg-emerald-600 hover:text-white transition flex items-center justify-center gap-1.5">
                        Kollokatsiyalarni ko‘rish <i data-lucide="arrow-right" class="w-3 h-3"></i>
                    </button>
                </div>

                <!-- Card 3: Lug'at -->
                <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm hover:shadow-md transition flex flex-col justify-between space-y-3">
                    <div class="space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="text-[11px] font-bold px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-950 text-amber-700 dark:text-amber-300">I bob tadqiqoti</span>
                            <i data-lucide="book-a" class="w-4 h-4 text-amber-600"></i>
                        </div>
                        <h3 class="text-base font-bold text-slate-900 dark:text-white">Lug‘at bazasi</h3>
                        <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                            23 566 ta tozalangan leksik birlik. Qog‘oz nashrlar («Niso Poligraf» va «80 000 so‘zli lug‘at») asosida tuzilgan elektron lug‘at maqolalari.
                        </p>
                    </div>
                    <button onclick="app.switchTab('dictionary')" class="w-full py-2 rounded-xl bg-amber-50 dark:bg-amber-950 text-amber-700 dark:text-amber-300 font-bold text-xs hover:bg-amber-600 hover:text-white transition flex items-center justify-center gap-1.5">
                        Lug‘atni ochish <i data-lucide="arrow-right" class="w-3 h-3"></i>
                    </button>
                </div>
            </div>

            <!-- C2 Pastki qism: Loyiha haqida 2 qator va Metodologiya havolasi -->
            <div class="p-5 rounded-2xl bg-slate-100 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 text-xs sm:text-sm text-slate-600 dark:text-slate-300 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                <div>
                    <strong class="text-slate-900 dark:text-white">Loyiha haqida:</strong> Ushbu platforma doktorlik dissertatsiyasi doirasida inglizcha-o‘zbekcha parallel matnlarda kollokatsiyalar semantikasi va tarjima ekvivalentlarini ilmiy tahlil qilish uchun ishlab chiqilgan.
                </div>
                <a href="methodology.html" class="inline-flex items-center gap-1.5 font-bold text-indigo-600 dark:text-indigo-400 hover:underline shrink-0">
                    <span>Metodologiya sahifasiga o‘tish</span>
                    <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
                </a>
            </div>

            <!-- Badiiy Korpus Pasporti (Faqat Cho'lpon va Hemingway, Stevenson yo'q!) -->
            <div class="space-y-3 pt-2">
                <h3 class="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <i data-lucide="book-open" class="w-4 h-4 text-indigo-600"></i> Empirik Badiiy Korpus Manbalari
                </h3>
                <div class="grid sm:grid-cols-2 gap-4">
                    <div class="p-4 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                        <div class="flex items-center justify-between mb-1.5">
                            <span class="text-xs font-bold text-slate-900 dark:text-white">Cho‘lpon: «Kecha va kunduz»</span>
                            <span class="text-[11px] font-mono text-indigo-600 font-bold">2 471 jumla</span>
                        </div>
                        <p class="text-xs text-slate-500">Tarjima: «Night and Day» (C. Fort, 2020). Cheklangan ilmiy parcha.</p>
                        <button onclick="app.switchTab('corpus'); corpusManager.filterByBook('cholpon');" class="mt-3 text-xs text-indigo-600 font-semibold hover:underline flex items-center gap-1">
                            Ushbu romandan qidirish →
                        </button>
                    </div>

                    <div class="p-4 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                        <div class="flex items-center justify-between mb-1.5">
                            <span class="text-xs font-bold text-slate-900 dark:text-white">E. Hemingway: «The Old Man and the Sea»</span>
                            <span class="text-[11px] font-mono text-emerald-600 font-bold">1 340 jumla</span>
                        </div>
                        <p class="text-xs text-slate-500">Tarjima: «Chol va dengiz» (I. G‘afurov, 1986). Cheklangan ilmiy parcha.</p>
                        <button onclick="app.switchTab('corpus'); corpusManager.filterByBook('hemingway');" class="mt-3 text-xs text-emerald-600 font-semibold hover:underline flex items-center gap-1">
                            Ushbu qissadan qidirish →
                        </button>
                    </div>
                </div>
            </div>
        </section>

        <!-- ============================================== -->
        <!-- VIEW: TRANSLATOR'''

content = old_home_pattern.sub(new_home, content)

# 4. Remove Stevenson from corpus filter dropdown and update text
content = content.replace('<option value="stevenson">R.L. Stevenson: «Treasure Island» (1,346 jumla)</option>', '')
content = content.replace('Choʻlpon, Xeminguey va Stivenson asarlarining <strong>toʻliq matnidan</strong>', 
                          'Choʻlpon va Hemingway asarlarining <strong>toʻliq matnidan</strong>')
content = content.replace('5,157 Ta Toʻliq Parallel Jumla Konkordansi', 'Ilmiy Parallel Matnlar Konkordansi')
content = content.replace('Jami: 5,157 Jumla', 'Jami: <span id="corpusTotalCountBadge">3,811</span> Jumla')
content = content.replace('Barcha manbalar (5,157 jumla)', 'Barcha manbalar (3,811 jumla)')
content = content.replace('Barcha 5,157 jumladan qidirishga tayyor', 'Barcha segmentlardan qidirishga tayyor')
content = content.replace('>5,157<', '>3,811<')

# 5. Remove Stevenson from collocations source filter
content = content.replace('<option value="Xazinalar">R. L. Stevenson: «Treasure Island» (Parallel)</option>', '')
content = content.replace('Barcha manbalar (6,546 ta)', 'Barcha manbalar (6,537 ta)')
content = content.replace('6,546 ta turgʻun birikma', '6,537 ta turgʻun birikma')

# 6. Dictionary header count updates
content = content.replace('24,554+ soʻzdan iborat katta elektron lugʻat bazasi', '23,500+ soʻzdan iborat tozalangan elektron lugʻat bazasi')
content = content.replace('24,554 Ta Elektron Soʻz', '23,566 Ta Elektron Soʻz')
content = content.replace('24,554 ta soʻz', '23,566 ta soʻz')

# 7. Update Footer to C3: "TILCOR · 2026"
old_footer_pattern = re.compile(r'<!-- FOOTER -->.*?</footer>', re.DOTALL)
new_footer = '''<!-- FOOTER -->
    <footer class="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 py-6 mt-12 transition-colors">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 dark:text-slate-400">
            <div>
                <strong>TILCOR · 2026</strong> — Parallel korpus va leksikografik tahlil platformasi.
            </div>
            <div>
                Mualliflik huquqi egalariga tegishli. Faqat ilmiy tadqiqot uchun cheklangan parcha.
            </div>
        </div>
    </footer>'''
content = old_footer_pattern.sub(new_footer, content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated index.html successfully.')
