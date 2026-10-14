/**
 * Kollokatsiyalar Matritsasi va Qidiruv Tizimi
 * 4 ta asosiy kitob bazasi (6,537 ta birikma) bilan to'liq integratsiya
 */

class CollocationManager {
    constructor() {
        this.dataset = [];
        this.currentSource = 'all';
        this.currentLang = 'all';
        this.currentPattern = 'all';
        this.currentSemantic = 'all';
        this.currentCategory = 'all';
        this.currentCultural = 'all';
        this.sortBy = 'mi';
        this.searchTerm = '';
        this.viewMode = 'grid'; // 'grid' or 'table'
        this.page = 1;
        this.limit = 60;
        this.totalFound = 0;
        this.totalDatabase = 0;
        this.isLoading = false;
        this.searchTimer = null;
        this.init();
    }

    async init() {
        this.bindEvents();
        await this.fetchCollocations(true);
    }

    bindEvents() {
        const searchInput = document.getElementById('collocSearchInput');
        const langFilter = document.getElementById('collocLangFilter');
        const sourceFilter = document.getElementById('collocSourceFilter');
        const patternFilter = document.getElementById('collocPatternFilter');
        const semanticFilter = document.getElementById('collocSemanticFilter');
        const categoryFilter = document.getElementById('collocCategoryFilter');
        const culturalFilter = document.getElementById('collocCulturalFilter');
        const sortSelect = document.getElementById('collocSortSelect');
        const exportBtn = document.getElementById('collocExportBtn');
        const exportExcelBtn = document.getElementById('collocExportExcelBtn');
        const viewToggleGrid = document.getElementById('collocViewGrid');
        const viewToggleTable = document.getElementById('collocViewTable');

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value.trim();
                clearTimeout(this.searchTimer);
                this.searchTimer = setTimeout(() => {
                    this.page = 1;
                    this.fetchCollocations(true);
                }, 280);
            });

            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.searchTerm = e.target.value.trim();
                    this.page = 1;
                    this.fetchCollocations(true);
                }
            });
        }

        if (langFilter) {
            langFilter.addEventListener('change', (e) => {
                this.currentLang = e.target.value;
                this.page = 1;
                this.fetchCollocations(true);
            });
        }

        if (sourceFilter) {
            sourceFilter.addEventListener('change', (e) => {
                this.currentSource = e.target.value;
                this.page = 1;
                this.fetchCollocations(true);
            });
        }

        if (patternFilter) {
            patternFilter.addEventListener('change', (e) => {
                this.currentPattern = e.target.value;
                this.page = 1;
                this.fetchCollocations(true);
            });
        }

        if (semanticFilter) {
            semanticFilter.addEventListener('change', (e) => {
                this.currentSemantic = e.target.value;
                this.page = 1;
                this.fetchCollocations(true);
            });
        }

        if (categoryFilter) {
            categoryFilter.addEventListener('change', (e) => {
                this.currentCategory = e.target.value;
                this.page = 1;
                this.fetchCollocations(true);
            });
        }

        if (culturalFilter) {
            culturalFilter.addEventListener('change', (e) => {
                this.currentCultural = e.target.value;
                this.page = 1;
                this.fetchCollocations(true);
            });
        }

        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                this.sortBy = e.target.value;
                this.page = 1;
                this.fetchCollocations(true);
            });
        }

        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportCSV();
            });
        }

        if (exportExcelBtn) {
            exportExcelBtn.addEventListener('click', () => {
                this.exportExcel();
            });
        }

        if (viewToggleGrid) {
            viewToggleGrid.addEventListener('click', () => {
                this.viewMode = 'grid';
                viewToggleGrid.classList.add('bg-indigo-600', 'text-white');
                viewToggleGrid.classList.remove('text-slate-600', 'dark:text-slate-300');
                if (viewToggleTable) {
                    viewToggleTable.classList.remove('bg-indigo-600', 'text-white');
                    viewToggleTable.classList.add('text-slate-600', 'dark:text-slate-300');
                }
                this.renderCollocations();
            });
        }

        if (viewToggleTable) {
            viewToggleTable.addEventListener('click', () => {
                this.viewMode = 'table';
                viewToggleTable.classList.add('bg-indigo-600', 'text-white');
                viewToggleTable.classList.remove('text-slate-600', 'dark:text-slate-300');
                if (viewToggleGrid) {
                    viewToggleGrid.classList.remove('bg-indigo-600', 'text-white');
                    viewToggleGrid.classList.add('text-slate-600', 'dark:text-slate-300');
                }
                this.renderCollocations();
            });
        }

        // DeepSeek AI So'z Tahlili va Tarjimoni Events
        const aiWordInput = document.getElementById('collocAiWordInput');
        const aiAnalyzeBtn = document.getElementById('collocAiAnalyzeBtn');

        if (aiAnalyzeBtn) {
            aiAnalyzeBtn.addEventListener('click', () => {
                this.analyzeWordWithAi();
            });
        }

        if (aiWordInput) {
            aiWordInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.analyzeWordWithAi();
                }
            });
        }
    }

    async fetchCollocations(reset = false) {
        if (this.isLoading) return;
        this.isLoading = true;

        if (reset) {
            this.dataset = [];
            this.page = 1;
        }

        const container = document.getElementById('collocContainer');
        if (reset && container) {
            container.innerHTML = `
                <div class="col-span-full text-center py-12">
                    <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-600 border-t-transparent mb-3"></div>
                    <p class="text-sm text-slate-500">Kollokatsiyalar bazasi yuklanmoqda...</p>
                </div>
            `;
        }

        const params = new URLSearchParams({
            q: this.searchTerm,
            lang: this.currentLang,
            source: this.currentSource,
            pattern: this.currentPattern,
            semantic: this.currentSemantic,
            equivalence: this.currentCategory,
            category: this.currentCategory,
            cultural: this.currentCultural,
            sort: this.sortBy,
            limit: this.limit,
            page: this.page
        });

        try {
            const resp = await fetch(`/api/collocations?${params.toString()}`);
            if (resp.ok) {
                const data = await resp.json();
                this.totalFound = data.totalFound || 0;
                this.totalDatabase = data.totalDatabase || 0;
                
                if (reset) {
                    this.dataset = data.results || [];
                } else {
                    this.dataset = [...this.dataset, ...(data.results || [])];
                }

                if (data.posAnalysis && this.searchTerm) {
                    this.renderPosAnalysisBanner(data.posAnalysis);
                } else if (!this.searchTerm) {
                    const posBox = document.getElementById('collocPosAnalysisBox');
                    if (posBox) posBox.classList.add('hidden');
                }
            } else {
                throw new Error("Serverdan javob olinmadi");
            }
        } catch (err) {
            console.warn("API orqali yuklashda xatolik, lokal fallback ishlatilmoqda:", err);
            if (typeof collocationsDatabase !== 'undefined' && collocationsDatabase.length > 0) {
                let list = [...collocationsDatabase];
                if (this.searchTerm) {
                    const norm = (str) => (window.normalizeApostrophes ? normalizeApostrophes(str) : str);
                    const normQ = norm(this.searchTerm).toLowerCase();
                    list = list.filter(item => {
                        const uz = norm(item.uzbek || '').toLowerCase();
                        const en = norm(item.english || '').toLowerCase();
                        return uz.includes(normQ) || en.includes(normQ);
                    });
                }
                this.dataset = list;
                this.totalFound = this.dataset.length;
                this.totalDatabase = collocationsDatabase.length;
            }
        } finally {
            this.isLoading = false;
            this.renderStats();
            this.renderCollocations();
        }
    }

    quickSearch(phrase) {
        const input = document.getElementById('collocSearchInput');
        if (input) {
            input.value = phrase;
            this.searchTerm = phrase;
            this.page = 1;
            this.fetchCollocations(true);
        }
    }

    renderPosAnalysisBanner(pos) {
        const box = document.getElementById('collocPosAnalysisBox');
        if (!box || !pos) return;

        const nounsHtml = pos.nouns && pos.nouns.length > 0 
            ? pos.nouns.map(n => `<span class="inline-flex items-center px-2.5 py-1 rounded-xl bg-blue-500/20 text-blue-200 border border-blue-400/40 text-xs font-bold mr-1.5 my-0.5">«${n}»</span>`).join('')
            : '<span class="text-slate-400 text-xs italic">Ushbu birikmada Ot mavjud emas</span>';

        const verbsHtml = pos.verbs && pos.verbs.length > 0 
            ? pos.verbs.map(v => `<span class="inline-flex items-center px-2.5 py-1 rounded-xl bg-emerald-500/20 text-emerald-200 border border-emerald-400/40 text-xs font-bold mr-1.5 my-0.5">«${v}»</span>`).join('')
            : '<span class="text-slate-400 text-xs italic">Ushbu birikmada Feʻl mavjud emas</span>';

        const tokensHtml = (pos.tokens || []).map(t => {
            const badgeClass = t.color === 'green' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' :
                               t.color === 'blue' ? 'bg-blue-500/20 text-blue-300 border-blue-500/30' :
                               t.color === 'amber' ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' :
                               'bg-slate-700/60 text-slate-300 border-slate-600/40';
            return `
                <div class="p-3 rounded-2xl bg-white/5 border border-white/10 hover:border-indigo-400/30 transition">
                    <div class="flex items-center justify-between gap-1.5 mb-1">
                        <span class="font-bold text-sm text-white">«${t.token}»</span>
                        <span class="px-2 py-0.5 rounded-lg text-[10px] font-bold border ${badgeClass}">
                            ${t.badge || t.pos}
                        </span>
                    </div>
                    <div class="text-[11px] text-slate-400 font-mono mb-1">Oʻzak: <span class="text-indigo-300">${t.lemma}</span></div>
                    <div class="text-[11px] text-slate-300 leading-snug">${t.details}</div>
                </div>
            `;
        }).join('');

        const targetTranslation = pos.idiomInfo ? pos.idiomInfo.en : '';

        box.innerHTML = `
            <div class="space-y-4">
                <!-- Sarlavha paneli -->
                <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-indigo-500/20">
                    <div class="flex items-center gap-2.5">
                        <div class="w-9 h-9 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center text-white shadow-md">
                            <i data-lucide="sparkles" class="w-5 h-5"></i>
                        </div>
                        <div>
                            <h3 class="font-bold text-sm sm:text-base text-white flex items-center gap-2">
                                AI Morfo-Sintaktik & Soʻz Turkumlari Tahlili: <span class="text-indigo-300 font-mono">«${pos.text}»</span>
                            </h3>
                            <p class="text-xs text-indigo-200/70 mt-0.5 flex items-center gap-2 flex-wrap">
                                <span>Til: <strong>${pos.languageName || 'Oʻzbek tili'}</strong></span>
                                <span>•</span>
                                <span>Model: <strong class="text-emerald-400 font-mono">${pos.pattern}</strong> (${pos.patternEn || ''})</span>
                            </p>
                        </div>
                    </div>

                    <div class="flex items-center gap-2">
                        <button onclick="collocationManager.triggerAiWordSearch('${pos.text.replace(/'/g, "\\'")}')" class="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white text-xs font-bold transition flex items-center gap-1.5 shadow-md">
                            <i data-lucide="bot" class="w-3.5 h-3.5"></i> Chuqur PhD Tahlili
                        </button>
                        <button onclick="document.getElementById('collocPosAnalysisBox').classList.add('hidden')" class="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-white/10 transition" title="Yopish">
                            <i data-lucide="x" class="w-4 h-4"></i>
                        </button>
                    </div>
                </div>

                <!-- OTLAR VA FE'LLAR ASOSIY AJRATISH BLOKI (User talabi bo'yicha) -->
                <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    <!-- Otlar bloki -->
                    <div class="p-4 rounded-2xl bg-gradient-to-br from-blue-950/40 to-slate-900/60 border border-blue-500/30 space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="px-2.5 py-1 rounded-lg bg-blue-500/20 text-blue-300 text-xs font-bold flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-full bg-blue-400"></span> 🔵 Ot (Noun)
                            </span>
                            <span class="text-[11px] text-slate-400 font-mono">${pos.nouns ? pos.nouns.length : 0} ta soʻz</span>
                        </div>
                        <div class="pt-1">
                            ${nounsHtml}
                        </div>
                        <p class="text-[11px] text-slate-300 leading-relaxed pt-1 border-t border-white/5">
                            ${pos.nouns && pos.nouns.length > 0 ? "Predmet, tushuncha yoki vositasiz obyektni ifodalaydi." : "Ushbu birikmada Ot mavjud emas."}
                        </p>
                    </div>

                    <!-- Fe'llar bloki -->
                    <div class="p-4 rounded-2xl bg-gradient-to-br from-emerald-950/40 to-slate-900/60 border border-emerald-500/30 space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-300 text-xs font-bold flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-full bg-emerald-400"></span> 🟢 Feʻl (Verb)
                            </span>
                            <span class="text-[11px] text-slate-400 font-mono">${pos.verbs ? pos.verbs.length : 0} ta soʻz</span>
                        </div>
                        <div class="pt-1">
                            ${verbsHtml}
                        </div>
                        <p class="text-[11px] text-slate-300 leading-relaxed pt-1 border-t border-white/5">
                            ${pos.verbs && pos.verbs.length > 0 ? "Harakat, holat yoki jarayonni ifodalaydi (shaxs-son, zamon)." : "Ushbu birikmada Feʻl mavjud emas."}
                        </p>
                    </div>

                    <!-- Model va Adekvat Tarjima -->
                    <div class="p-4 rounded-2xl bg-gradient-to-br from-purple-950/40 to-slate-900/60 border border-purple-500/30 space-y-2 sm:col-span-2 lg:col-span-1">
                        <div class="flex items-center justify-between">
                            <span class="px-2.5 py-1 rounded-lg bg-purple-500/20 text-purple-300 text-xs font-bold flex items-center gap-1.5">
                                <span class="w-2 h-2 rounded-full bg-purple-400"></span> 📐 Birikma Modeli
                            </span>
                            <span class="text-[11px] text-indigo-300 font-mono font-bold">${pos.pattern}</span>
                        </div>
                        <div class="text-xs text-white font-medium pt-1">
                            ${targetTranslation ? `🌐 Adekvat Kollokatsiya: <strong class="text-emerald-400 font-mono">${targetTranslation}</strong>` : `<span class="text-slate-300">${pos.patternEn}</span>`}
                        </div>
                        <p class="text-[11px] text-slate-300 leading-relaxed pt-1 border-t border-white/5">
                            ${pos.idiomInfo ? pos.idiomInfo.explanation : "Korpusda yuqori assotsiativ bog'lanishga ega sintaktik model."}
                        </p>
                    </div>
                </div>

                <!-- So'zma-so'z Morfologik Tahlil -->
                <div class="p-4 rounded-2xl bg-black/30 border border-white/10 space-y-2.5">
                    <span class="text-[11px] font-bold text-indigo-300 uppercase tracking-wider block">
                        Har bir soʻzning leksik-morfologik tavsifi:
                    </span>
                    <div class="grid sm:grid-cols-2 md:grid-cols-3 gap-2.5">
                        ${tokensHtml}
                    </div>
                </div>
            </div>
        `;

        box.classList.remove('hidden');
        if (window.lucide) lucide.createIcons();
    }

    renderStats() {
        const totalEl = document.getElementById('collocTotalCount');
        const badge = document.getElementById('collocBadgeCount');

        if (totalEl) totalEl.textContent = this.totalDatabase.toLocaleString();
        if (badge) {
            if (this.searchTerm || this.currentSource !== 'all' || this.currentPattern !== 'all' || this.currentCategory !== 'all') {
                badge.textContent = `${this.totalFound.toLocaleString()} ta mos kollokat topildi`;
            } else {
                badge.textContent = `${this.totalFound.toLocaleString()} ta kollokatsiya`;
            }
        }
    }

    renderCollocations() {
        const container = document.getElementById('collocContainer');
        if (!container) return;

        if (this.dataset.length === 0) {
            container.innerHTML = `
                <div class="col-span-full text-center py-16 bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700">
                    <i data-lucide="search-x" class="w-10 h-10 text-slate-400 mx-auto mb-3"></i>
                    <h3 class="text-base font-semibold text-slate-800 dark:text-slate-200">Kollokatsiyalar topilmadi</h3>
                    <p class="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                        Qidiruv so'zini o'zgartiring yoki manba va struktura filtrlarini bekor qilib ko'ring.
                    </p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        if (this.viewMode === 'table') {
            this.renderTableView(container);
        } else {
            this.renderGridView(container);
        }

        // Render Load More button if more results exist
        if (this.dataset.length < this.totalFound) {
            const loadMoreWrapper = document.createElement('div');
            loadMoreWrapper.className = 'col-span-full text-center pt-6 pb-2';
            loadMoreWrapper.innerHTML = `
                <button onclick="collocationManager.loadMore()" class="px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs transition shadow-md shadow-indigo-600/20 inline-flex items-center gap-2">
                    <i data-lucide="chevron-down" class="w-4 h-4"></i>
                    Yana ko'rsatish (${this.dataset.length} / ${this.totalFound.toLocaleString()} ko'rsatilmoqda)
                </button>
            `;
            container.appendChild(loadMoreWrapper);
        }

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    renderGridView(container) {
        container.className = "grid sm:grid-cols-2 lg:grid-cols-3 gap-4";
        container.innerHTML = this.dataset.map(item => {
            const eqType = item.equivalenceType || item.category || 'Mos ekvivalent';
            const catBadgeColor = 
                eqType.includes('Mos') || eqType.includes('Toʻliq') ? 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800' :
                eqType.includes('Qisman') ? 'bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800' :
                eqType.includes('Transformatsiya') ? 'bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800' :
                'bg-rose-50 dark:bg-rose-950/60 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-800';

            const sourceBadge = item.sourceBook || (item.sources ? item.sources.join(' & ') : 'Ilmiy manba');
            const sm = item.sourceMeta || {};

            return `
                <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm hover:shadow-md transition duration-200 flex flex-col justify-between">
                    <div>
                        <!-- 3.1 & 3.2 Tasnif Badgelari -->
                        <div class="flex flex-wrap items-center justify-between gap-1.5 mb-2.5">
                            <span class="text-[10px] font-mono px-2 py-0.5 rounded font-bold bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-600">
                                ${item.pattern || 'Birikma'}
                            </span>
                            <span class="text-[10px] font-mono px-2 py-0.5 rounded font-bold border ${catBadgeColor}">
                                ${eqType}
                            </span>
                            <span class="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border border-amber-200/60 dark:border-amber-800/60">
                                AI-taklif
                            </span>
                        </div>

                        <!-- 3.1 Semantik guruh & 3.3 Madaniy belgilar -->
                        <div class="flex flex-wrap items-center gap-1.5 mb-3">
                            ${item.semanticGroup ? `
                                <span class="text-[10px] px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-200/60 dark:border-indigo-800/60 font-medium">
                                    📁 ${item.semanticGroup}
                                </span>
                            ` : ''}
                            ${item.isLingvocultural ? `
                                <span class="text-[10px] px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800 font-bold">
                                    🏛️ Lingvomadaniy
                                </span>
                            ` : ''}
                        </div>

                        <!-- Source Badge (D-bo'lim) -->
                        <div class="mb-3">
                            <span class="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-700/70 text-slate-600 dark:text-slate-300 border border-slate-200/50 dark:border-slate-600/50 line-clamp-1" title="${sourceBadge}">
                                <i data-lucide="book-open" class="w-3 h-3 text-indigo-500"></i>
                                ${sourceBadge}
                            </span>
                        </div>

                        <!-- English and Uzbek pair -->
                        <div class="space-y-2 mb-3 bg-slate-50/70 dark:bg-slate-900/60 p-3 rounded-xl border border-slate-100 dark:border-slate-800">
                            <div>
                                <span class="text-[10px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">English Collocation</span>
                                <h4 class="text-base font-extrabold text-slate-900 dark:text-white capitalize">${item.english}</h4>
                            </div>
                            <div class="pt-1.5 border-t border-slate-200/60 dark:border-slate-800">
                                <span class="text-[10px] font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">O‘zbekcha Ekvivalent</span>
                                <h4 class="text-base font-extrabold text-slate-800 dark:text-slate-100">${item.uzbek}</h4>
                            </div>
                        </div>

                        <!-- Kalka ogohlantirishi -->
                        ${item.literalTrap ? `
                            <div class="p-2.5 rounded-lg bg-rose-50/80 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 text-[11px] text-rose-800 dark:text-rose-300 mb-3">
                                <span class="font-bold flex items-center gap-1">
                                    <i data-lucide="alert-triangle" class="w-3.5 h-3.5 text-rose-500"></i> Kalka xatosi:
                                </span>
                                <span class="mt-0.5 block leading-relaxed font-mono">${item.literalTrap}</span>
                            </div>
                        ` : ''}

                        <!-- Real Context Example (if verified) -->
                        ${item.example && item.example.book ? `
                            <div class="p-3 rounded-xl bg-indigo-50/40 dark:bg-slate-900/90 border border-indigo-100 dark:border-slate-800 space-y-2 mb-3">
                                <div class="flex items-center justify-between pb-1 border-b border-indigo-100/60 dark:border-slate-800">
                                    <span class="flex items-center gap-1 text-[11px] font-bold text-indigo-700 dark:text-indigo-400">
                                        <i data-lucide="split" class="w-3 h-3"></i> Kontekst (Parallel Jumla):
                                    </span>
                                    <span class="text-[10px] font-mono text-slate-500 dark:text-slate-400">${item.example.book}</span>
                                </div>
                                <div class="space-y-1.5 text-xs leading-relaxed">
                                    <p class="text-slate-900 dark:text-slate-100 font-medium flex items-start gap-1.5">
                                        <span class="shrink-0 text-[9px] font-bold text-indigo-700 dark:text-indigo-300 bg-indigo-100 dark:bg-indigo-950 px-1 rounded">UZ</span>
                                        <span>«${item.example.uz}»</span>
                                    </p>
                                    <p class="text-emerald-800 dark:text-emerald-300 font-normal flex items-start gap-1.5 pt-1 border-t border-indigo-50 dark:border-slate-800">
                                        <span class="shrink-0 text-[9px] font-bold text-emerald-800 dark:text-emerald-300 bg-emerald-100 dark:bg-emerald-950 px-1 rounded">EN</span>
                                        <span>«${item.example.en}»</span>
                                    </p>
                                </div>
                            </div>
                        ` : ''}
                    </div>

                    <div>
                        <!-- Statistik ko'rsatkichlar Step 10 da chiqariladi -->
                        <div class="p-2 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-slate-100 dark:border-slate-800 mb-3 text-center">
                            <span class="text-slate-500 dark:text-slate-400 text-[11px] block">Statistik maqom (logDice): <strong>10-bosqichda kalibrlanadi</strong></span>
                        </div>

                        <div class="flex items-center gap-2">
                            <button onclick="collocationManager.showDetailModal('${item.id}')" class="flex-1 py-2 px-3 text-xs font-semibold rounded-xl bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 transition text-slate-700 dark:text-slate-200 flex items-center justify-center gap-1.5">
                                <i data-lucide="info" class="w-3.5 h-3.5"></i> Tafsilot
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    renderTableView(container) {
        container.className = "w-full overflow-x-auto bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm";
        container.innerHTML = `
            <table class="w-full text-left text-xs border-collapse">
                <thead>
                    <tr class="bg-slate-50 dark:bg-slate-700/50 border-b border-slate-200 dark:border-slate-700 text-[10px] font-bold uppercase text-slate-500 dark:text-slate-400">
                        <th class="p-3">Inglizcha Kollokatsiya</th>
                        <th class="p-3">Oʻzbekcha Ekvivalent</th>
                        <th class="p-3">3.1 Qolip</th>
                        <th class="p-3">3.1 Semantika</th>
                        <th class="p-3">3.2 Ekvivalentlik</th>
                        <th class="p-3">MI</th>
                        <th class="p-3">T-Score</th>
                        <th class="p-3">LL</th>
                        <th class="p-3">Chastota</th>
                        <th class="p-3">Manba</th>
                        <th class="p-3 text-right">Amal</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 dark:divide-slate-700/60">
                    ${this.dataset.map(item => `
                        <tr class="hover:bg-slate-50/80 dark:hover:bg-slate-700/30 transition">
                            <td class="p-3 font-bold text-slate-900 dark:text-white">${item.english}</td>
                            <td class="p-3 font-semibold text-indigo-600 dark:text-indigo-400">${item.uzbek}</td>
                            <td class="p-3 font-mono text-slate-500">${item.pattern}</td>
                            <td class="p-3 text-slate-500">${item.semanticGroup || 'Leksik'}</td>
                            <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">${item.equivalenceType || item.category}</span></td>
                            <td class="p-3 font-mono font-bold text-indigo-600 dark:text-indigo-400">${item.miScore ?? "—"}</td>
                            <td class="p-3 font-mono font-bold text-emerald-600 dark:text-emerald-400">${item.tScore ?? "—"}</td>
                            <td class="p-3 font-mono font-bold text-purple-600 dark:text-purple-400">${item.logLikelihood ?? "—"}</td>
                            <td class="p-3 font-mono text-slate-500">${item.freq ?? "—"}</td>
                            <td class="p-3 text-slate-500 max-w-xs truncate">${item.sourceBook || 'Badiiy korpus'}</td>
                            <td class="p-3 text-right">
                                <div class="flex items-center justify-end gap-1">
                                    <button onclick="collocationManager.showDetailModal('${item.id}')" class="text-xs px-2 py-1 rounded bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 transition">
                                        Tafsilot
                                    </button>
                                    <button onclick="collocationManager.askAiForCollocation('${item.id}')" class="text-xs px-2 py-1 rounded bg-indigo-600 text-white hover:bg-indigo-700 transition flex items-center gap-1 font-semibold">
                                        <i data-lucide="bot" class="w-3 h-3"></i> AI
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    showDetailModal(id) {
        const item = this.dataset.find(x => x.id === id);
        if (!item) return;

        const modalContainer = document.getElementById('collocModalContent');
        const modal = document.getElementById('collocDetailModal');

        if (!modalContainer || !modal) return;

        const sourceLabel = item.sourceBook || (item.sources ? item.sources.join(' & ') : 'Ilmiy adabiyot');

        modalContainer.innerHTML = `
            <div class="space-y-5">
                <div class="flex items-start justify-between pb-3 border-b border-slate-100 dark:border-slate-700">
                    <div>
                        <span class="text-xs uppercase font-mono tracking-wider text-indigo-600 dark:text-indigo-400">${item.pattern}</span>
                        <h3 class="text-xl font-bold text-slate-900 dark:text-white mt-0.5">
                            ${item.english} ⟷ ${item.uzbek}
                        </h3>
                    </div>
                    <span class="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
                        ${item.category}
                    </span>
                </div>

                <!-- Source Book Info -->
                <div class="p-3 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200/60 dark:border-slate-800 flex items-center gap-2">
                    <i data-lucide="book" class="w-4 h-4 text-indigo-600"></i>
                    <span class="text-xs text-slate-500 dark:text-slate-400">Manba kitob:</span>
                    <strong class="text-xs text-slate-800 dark:text-slate-100 font-medium">${sourceLabel}</strong>
                </div>

                <!-- Stats Grid -->
                <div class="grid grid-cols-4 gap-2 text-center">
                    <div class="p-3 bg-slate-50 dark:bg-slate-900 rounded-xl">
                        <span class="text-[10px] uppercase text-slate-400 block">Chastota</span>
                        <span class="font-mono font-bold text-base text-slate-800 dark:text-slate-100">${item.freq ?? "—"} marta</span>
                    </div>
                    <div class="p-3 bg-slate-50 dark:bg-slate-900 rounded-xl">
                        <span class="text-[10px] uppercase text-slate-400 block">MI Score</span>
                        <span class="font-mono font-bold text-base text-indigo-600 dark:text-indigo-400">${item.miScore ?? "—"}</span>
                    </div>
                    <div class="p-3 bg-slate-50 dark:bg-slate-900 rounded-xl">
                        <span class="text-[10px] uppercase text-slate-400 block">T-Score</span>
                        <span class="font-mono font-bold text-base text-emerald-600 dark:text-emerald-400">${item.tScore ?? "—"}</span>
                    </div>
                    <div class="p-3 bg-slate-50 dark:bg-slate-900 rounded-xl">
                        <span class="text-[10px] uppercase text-slate-400 block">Ekvivalentlik</span>
                        <span class="font-mono font-bold text-xs text-amber-600 dark:text-amber-400 block mt-1">${item.category}</span>
                    </div>
                </div>

                <!-- Literal Trap Warning -->
                <div class="p-4 bg-rose-50 dark:bg-rose-950/40 rounded-xl border border-rose-200 dark:border-rose-900/60">
                    <h5 class="text-xs font-bold uppercase tracking-wider text-rose-800 dark:text-rose-300 flex items-center gap-1.5 mb-1">
                        <i data-lucide="alert-circle" class="w-4 h-4 text-rose-600"></i> Tarjimadagi tipik kalka va leksik toʻsiq:
                    </h5>
                    <p class="text-sm font-mono text-rose-700 dark:text-rose-200">${item.literalTrap || "—"}</p>
                </div>

                <!-- Translation Note -->
                <div class="p-4 bg-indigo-50 dark:bg-indigo-950/30 rounded-xl border border-indigo-100 dark:border-indigo-900/50">
                    <h5 class="text-xs font-bold uppercase tracking-wider text-indigo-800 dark:text-indigo-300 flex items-center gap-1.5 mb-1">
                        <i data-lucide="sparkles" class="w-4 h-4 text-indigo-600"></i> Chogʻishtirma tahlil va korpus tavsiyasi:
                    </h5>
                    <p class="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                        Ushbu kollokatsiya «${sourceLabel}» manbasidan ekstraksiya qilingan bo'lib, ingliz tilidagi <strong>«${item.english}»</strong> turg'un birikmasiga o'zbek tilida tabiiy ravishda <strong>«${item.uzbek}»</strong> mos keladi.
                    </p>
                </div>

                <!-- Parallel Corpus Context Example with Legible Modern Typography -->
                ${item.example ? `
                    <div class="p-4 rounded-2xl bg-indigo-50/40 dark:bg-slate-900/90 border border-indigo-100 dark:border-slate-800 space-y-2.5">
                        <div class="flex items-center justify-between pb-1.5 border-b border-indigo-100/60 dark:border-slate-800">
                            <span class="flex items-center gap-1.5 text-xs font-bold text-indigo-700 dark:text-indigo-400">
                                <i data-lucide="book-open" class="w-3.5 h-3.5"></i> Parallel Korpus Misoli:
                            </span>
                            <span class="text-[10px] font-mono px-2 py-0.5 rounded-md bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400 font-semibold border border-slate-200/60 dark:border-slate-700">${item.example.book || 'Badiiy Korpus'}</span>
                        </div>
                        <div class="space-y-2 pt-0.5 text-xs sm:text-[13px] leading-relaxed">
                            <p class="text-slate-900 dark:text-slate-100 font-medium flex items-start gap-2">
                                <span class="shrink-0 text-[10px] font-bold text-indigo-700 dark:text-indigo-300 bg-indigo-100/80 dark:bg-indigo-950 px-1.5 py-0.5 rounded">UZ</span>
                                <span class="tracking-normal font-sans">«${item.example.uz}»</span>
                            </p>
                            <p class="text-emerald-800 dark:text-emerald-300 font-normal flex items-start gap-2 pt-1.5 border-t border-indigo-50/80 dark:border-slate-800/80">
                                <span class="shrink-0 text-[10px] font-bold text-emerald-800 dark:text-emerald-300 bg-emerald-100/80 dark:bg-emerald-950 px-1.5 py-0.5 rounded">EN</span>
                                <span class="tracking-normal font-sans">«${item.example.en}»</span>
                            </p>
                        </div>
                    </div>
                ` : ''}

                <!-- DeepSeek AI Analysis Button inside Modal -->
                <button onclick="collocationManager.askAiForCollocation('${item.id}')" class="w-full py-3 px-4 rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-700 hover:from-indigo-700 hover:to-purple-700 text-white font-extrabold text-xs flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20 transition cursor-pointer">
                    <i data-lucide="sparkles" class="w-4 h-4"></i> DeepSeek AI Bilan Ushbu Birikmani Chuqur Tahlil Qilish
                </button>
            </div>
        `;

        modal.classList.remove('hidden');
        modal.classList.add('flex');
        if (window.lucide) lucide.createIcons();
    }

    async askAiForCollocation(id) {
        let item = this.dataset.find(x => x.id === id);
        if (!item && typeof collocationsList !== 'undefined') {
            item = collocationsList.find(x => x.id === id);
        }
        if (!item) return;

        const promptText = `Kollokatsiya tahlili: «${item.english}» (Oʻzbekcha ekvivalenti: «${item.uzbek}», Manbasi: «${item.sourceBook || 'Ilmiy korpus'}»). 
Iltimos, ushbu birikmaning:
1. Leksik-semantik bogʻlanish kuchi (MI va T-score mezonlari).
2. Xalqaro korpuslardagi (BNC, COCA, Sketch Engine) qoʻllanilish xususiyatlari.
3. Erkin birikmadan farqi hamda soʻzma-soʻz kalka qilish xatolari (masalan, uslubiy zaifliklar).
4. Oʻzbek tiliga adekvat tarjima qilish tavsiyalarini PhD dissertatsiyasi talablari darajasida tahlil qilib bering.`;

        this.openAiPromptModal(promptText, `«${item.english}» ⟷ «${item.uzbek}»`);
    }

    async openAiPromptModal(customPrompt = '', title = 'DeepSeek AI Kollokatsiya Tahlilchisi') {
        let modal = document.getElementById('collocAiModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'collocAiModal';
            modal.className = 'fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden items-center justify-center p-4';
            document.body.appendChild(modal);
        }

        modal.innerHTML = `
            <div class="bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 max-w-2xl w-full p-6 sm:p-8 shadow-2xl relative max-h-[90vh] overflow-y-auto space-y-4">
                <button onclick="document.getElementById('collocAiModal').classList.add('hidden'); document.getElementById('collocAiModal').classList.remove('flex');" class="absolute right-5 top-5 p-2 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700 transition">
                    <i data-lucide="x" class="w-5 h-5"></i>
                </button>

                <div class="flex items-center gap-2 pb-3 border-b border-slate-100 dark:border-slate-700">
                    <span class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
                    <h3 class="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <i data-lucide="bot" class="w-5 h-5 text-indigo-600"></i> ${title}
                    </h3>
                </div>

                <div id="collocAiModalBody" class="space-y-3">
                    <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-100 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-300">
                        <span class="font-bold text-indigo-600 block mb-1">Tahlil soʻrovi:</span>
                        <p class="font-mono text-[11px] leading-relaxed whitespace-pre-line">${customPrompt || 'Ixtiyoriy birikma tahlili'}</p>
                    </div>

                    <div id="collocAiResultContent" class="p-5 rounded-2xl bg-indigo-50/40 dark:bg-slate-900 border border-indigo-100 dark:border-slate-800 text-xs text-slate-800 dark:text-slate-200 leading-relaxed">
                        <div class="flex items-center gap-2 text-indigo-600 dark:text-indigo-400 font-semibold py-4 justify-center">
                            <span class="w-2.5 h-2.5 rounded-full bg-indigo-600 animate-ping"></span>
                            <span>DeepSeek-v4 AI & PhD Korpus Lingvisti tahlil qilmoqda...</span>
                        </div>
                    </div>
                </div>

                <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100 dark:border-slate-700">
                    <button onclick="document.getElementById('collocAiModal').classList.add('hidden'); document.getElementById('collocAiModal').classList.remove('flex');" class="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition">
                        Yopish
                    </button>
                    <button id="copyAiResultBtn" class="px-4 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white transition flex items-center gap-1.5 shadow-sm">
                        <i data-lucide="copy" class="w-3.5 h-3.5"></i> Tahlilni Nusxalash
                    </button>
                </div>
            </div>
        `;

        modal.classList.remove('hidden');
        modal.classList.add('flex');
        if (window.lucide) lucide.createIcons();

        // Send query to /api/ai
        try {
            const resp = await fetch('/api/ai', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: customPrompt || 'Kollokatsiyalar boʻyicha tahlil' })
            });
            const data = await resp.json();
            const resultContent = document.getElementById('collocAiResultContent');
            if (resultContent) {
                let formatted = (data.content || '')
                    .replace(/### (.*?)\n/g, '<h4 class="text-sm font-bold text-slate-900 dark:text-white mt-3 mb-1.5">$1</h4>')
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                    .replace(/\*(.*?)\*/g, '<em>$1</em>')
                    .replace(/- (.*?)\n/g, '<li class="ml-3 list-disc">$1</li>')
                    .replace(/\n\n/g, '<br><br>');

                resultContent.innerHTML = `
                    <div class="flex items-center justify-between pb-2 mb-2 border-b border-indigo-100 dark:border-slate-800 text-[10px] text-slate-400 font-mono">
                        <span>Provider: ${data.provider || 'DeepSeek AI'}</span>
                        <span class="text-emerald-600 font-bold">PhD Ilmiy Standarti</span>
                    </div>
                    <div class="space-y-2 text-xs leading-relaxed text-slate-800 dark:text-slate-100">
                        ${formatted}
                    </div>
                `;

                const copyBtn = document.getElementById('copyAiResultBtn');
                if (copyBtn) {
                    copyBtn.onclick = () => {
                        navigator.clipboard.writeText(data.content || '');
                        if (window.app && app.showToast) app.showToast("AI tahlili nusxalandi!", "success");
                    };
                }
            }
        } catch (e) {
            const resultContent = document.getElementById('collocAiResultContent');
            if (resultContent) {
                resultContent.innerHTML = `<span class="text-rose-600">Xatolik: ${e.message}</span>`;
            }
        }
    }

    triggerAiWordSearch(word) {
        const input = document.getElementById('collocAiWordInput');
        if (input) input.value = word;
        this.analyzeWordWithAi(word);
    }

    triggerAiFromSearchInput() {
        const searchInput = document.getElementById('collocSearchInput');
        const query = searchInput ? searchInput.value.trim() : '';
        if (!query) {
            if (window.app && app.showToast) app.showToast("Avval qidiruv maydoniga so'z yozing!", "info");
            return;
        }
        const aiInput = document.getElementById('collocAiWordInput');
        if (aiInput) aiInput.value = query;
        this.analyzeWordWithAi(query);
    }

    async analyzeWordWithAi(customWord = '') {
        const input = document.getElementById('collocAiWordInput');
        const word = (customWord || (input ? input.value : '')).trim();

        if (!word) {
            if (window.app && app.showToast) app.showToast("Iltimos, tahlil qilish uchun soʻz kiriting!", "warning");
            if (input) input.focus();
            return;
        }

        const resultBox = document.getElementById('collocAiResultBox');
        const resultTitle = document.getElementById('collocAiResultTitle');
        const resultContent = document.getElementById('collocAiResultContent');
        const copyBtn = document.getElementById('collocAiCopyBtn');
        const filterDbBtn = document.getElementById('collocAiFilterDbBtn');

        if (!resultBox || !resultContent) return;

        resultBox.classList.remove('hidden');
        if (resultTitle) {
            resultTitle.innerHTML = `
                <i data-lucide="bot" class="w-5 h-5 text-indigo-600 dark:text-indigo-400"></i>
                <span>«${word}» boʻyicha DeepSeek AI Kollokatsiyalar Tahlili</span>
            `;
        }

        resultContent.innerHTML = `
            <div class="flex flex-col items-center justify-center py-10 gap-3 text-indigo-600 dark:text-indigo-400">
                <div class="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                <div class="text-center">
                    <p class="font-bold text-sm">DeepSeek AI soʻzning kollokatsiyalarini va tarjimalarini aniqlamoqda...</p>
                    <p class="text-xs text-slate-500 mt-1">Sifat+Ot, Feʼl+Ot modellarini ajratish, kalka xatolarini tuzatish va MI/T-score hisoblash</p>
                </div>
            </div>
        `;
        if (window.lucide) lucide.createIcons();

        // Scroll to results box smoothly
        resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        try {
            const resp = await fetch(`/api/collocations/ai-analyze?word=${encodeURIComponent(word)}`);
            const data = await resp.json();

            if (!data.success) {
                throw new Error(data.error || "Noma'lum xatolik");
            }

            // Format markdown to HTML
            let formattedMd = (data.markdown || '')
                .replace(/### (.*?)\n/g, '<h4 class="text-sm font-bold text-slate-900 dark:text-white mt-4 mb-2 flex items-center gap-1.5"><i data-lucide="chevron-right" class="w-4 h-4 text-indigo-500"></i> $1</h4>')
                .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-slate-900 dark:text-white">$1</strong>')
                .replace(/\*(.*?)\*/g, '<em class="italic text-slate-600 dark:text-slate-300">$1</em>')
                .replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 font-mono text-[11px]">$1</code>')
                .replace(/- (.*?)\n/g, '<li class="ml-4 list-disc text-xs text-slate-700 dark:text-slate-300 leading-relaxed">$1</li>')
                .replace(/\n\n/g, '<br>');

            // Compact Collocations Cards (Top 4)
            let topCollocsHtml = '';
            if (data.dbMatches && data.dbMatches.length > 0) {
                topCollocsHtml = `
                    <div class="grid sm:grid-cols-2 gap-2 text-xs">
                        ${data.dbMatches.slice(0, 4).map(item => `
                            <div class="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 flex items-center justify-between">
                                <div class="min-w-0 pr-2">
                                    <div class="font-bold text-slate-900 dark:text-white truncate">${item.english}</div>
                                    <div class="text-[11px] text-slate-500 truncate">➔ ${item.uzbek}</div>
                                </div>
                                <div class="flex-shrink-0 text-right">
                                    <span class="px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 font-mono text-[10px] font-bold">MI: ${item.miScore ?? "—"}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }

            // Compact Calque Strip
            let calqueStripHtml = '';
            if (data.matchedTrap) {
                calqueStripHtml = `
                    <div class="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-900 dark:text-amber-200 text-xs flex flex-wrap items-center justify-between gap-2">
                        <div class="flex items-center gap-2">
                            <span class="px-2 py-0.5 rounded bg-rose-500/20 text-rose-600 dark:text-rose-400 font-bold text-[11px] font-mono line-through">${data.matchedTrap.calque}</span>
                            <span>➔</span>
                            <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-bold text-[11px] font-mono">${data.matchedTrap.correct}</span>
                        </div>
                        <span class="text-[11px] text-slate-500">${data.matchedTrap.explanation}</span>
                    </div>
                `;
            }

            // Compact Corpus Line
            let corpusLineHtml = '';
            if (data.corpusExample) {
                corpusLineHtml = `
                    <div class="p-2.5 rounded-xl bg-indigo-50/40 dark:bg-slate-900/40 border border-indigo-100/60 dark:border-slate-800 text-[11px] leading-relaxed text-slate-600 dark:text-slate-300">
                        <span class="font-semibold text-indigo-600 dark:text-indigo-400">[Kontekst]</span> 
                        <strong>[EN]</strong> ${data.corpusExample.en} ➔ <strong>[UZ]</strong> ${data.corpusExample.uz}
                    </div>
                `;
            }

            // Morfo-Sintaktik Ot va Fe'l bloki
            let posCardHtml = '';
            if (data.posAnalysis) {
                const pos = data.posAnalysis;
                const nounsHtml = pos.nouns && pos.nouns.length > 0
                    ? pos.nouns.map(n => `<span class="inline-flex items-center px-2 py-0.5 rounded-lg bg-blue-100 dark:bg-blue-950/70 text-blue-700 dark:text-blue-300 font-bold text-xs border border-blue-300 dark:border-blue-800">«${n}»</span>`).join(' ')
                    : '<span class="text-slate-400 italic text-xs">Ushbu birikmada Ot qatnashmagan</span>';
                const verbsHtml = pos.verbs && pos.verbs.length > 0
                    ? pos.verbs.map(v => `<span class="inline-flex items-center px-2 py-0.5 rounded-lg bg-emerald-100 dark:bg-emerald-950/70 text-emerald-700 dark:text-emerald-300 font-bold text-xs border border-emerald-300 dark:border-emerald-800">«${v}»</span>`).join(' ')
                    : '<span class="text-slate-400 italic text-xs">Ushbu birikmada Feʻl qatnashmagan</span>';

                posCardHtml = `
                    <div class="p-3.5 rounded-2xl bg-indigo-50/60 dark:bg-slate-800/80 border border-indigo-200/80 dark:border-slate-700 space-y-2">
                        <div class="flex items-center justify-between text-xs font-bold text-slate-800 dark:text-slate-200">
                            <span class="flex items-center gap-1.5"><i data-lucide="sparkles" class="w-4 h-4 text-indigo-600 dark:text-indigo-400"></i> Morfo-Sintaktik Xulosa (Ot & Feʻl):</span>
                            <span class="font-mono text-[11px] px-2 py-0.5 rounded-lg bg-indigo-600 text-white font-bold">Model: ${pos.pattern}</span>
                        </div>
                        <div class="grid sm:grid-cols-2 gap-2 text-xs">
                            <div class="p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-blue-200/70 dark:border-blue-900/40">
                                <div class="text-[11px] font-bold text-blue-600 dark:text-blue-400 mb-1 flex items-center gap-1">
                                    <span class="w-2 h-2 rounded-full bg-blue-500"></span> 🔵 Ot (Noun):
                                </div>
                                <div class="flex flex-wrap gap-1">${nounsHtml}</div>
                            </div>
                            <div class="p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-emerald-200/70 dark:border-emerald-900/40">
                                <div class="text-[11px] font-bold text-emerald-600 dark:text-emerald-400 mb-1 flex items-center gap-1">
                                    <span class="w-2 h-2 rounded-full bg-emerald-500"></span> 🟢 Feʻl (Verb):
                                </div>
                                <div class="flex flex-wrap gap-1">${verbsHtml}</div>
                            </div>
                        </div>
                    </div>
                `;
            }

            resultContent.innerHTML = `
                <!-- Compact Header -->
                <div class="flex flex-wrap items-center justify-between gap-2.5 p-3 rounded-2xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/80 text-xs">
                    <div class="flex items-center gap-2">
                        <span class="px-2.5 py-1 rounded-xl bg-indigo-600 text-white font-bold text-xs">${data.word}</span>
                        <i data-lucide="arrow-right" class="w-3.5 h-3.5 text-slate-400"></i>
                        <span class="px-2.5 py-1 rounded-xl bg-purple-600 text-white font-bold text-xs">${data.targetWord || 'tarjima'}</span>
                        <span class="text-slate-400 font-mono text-[10px]">(${data.sourceLang.toUpperCase()} ➔ ${data.targetLang.toUpperCase()})</span>
                    </div>
                    <div class="flex items-center gap-2 font-mono text-[11px]">
                        <span class="px-2 py-0.5 rounded-lg bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-bold">
                            ${data.totalMatchesInDb} ta birikma
                        </span>
                        <span class="text-slate-400">${data.provider}</span>
                    </div>
                </div>

                ${posCardHtml}

                ${calqueStripHtml}

                <!-- Top Collocations -->
                ${topCollocsHtml}

                <!-- Corpus Example -->
                ${corpusLineHtml}

                <!-- Collapsible Detailed Academic Report -->
                <details class="pt-2 border-t border-slate-100 dark:border-slate-800 text-xs group">
                    <summary class="font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 cursor-pointer flex items-center justify-between py-1 select-none">
                        <span class="flex items-center gap-1.5"><i data-lucide="file-text" class="w-3.5 h-3.5"></i> Toʻliq morfo-sintaktik va statistik matnli hisobot</span>
                        <span class="text-[10px] text-slate-400 group-open:hidden">Koʻrsatish ▼</span>
                        <span class="text-[10px] text-slate-400 hidden group-open:inline">Yashirish ▲</span>
                    </summary>
                    <div class="mt-2.5 p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-100 dark:border-slate-800 space-y-2 leading-relaxed text-slate-700 dark:text-slate-200">
                        ${formattedMd}
                    </div>
                </details>
            `;

            if (window.lucide) lucide.createIcons();

            // Setup copy
            if (copyBtn) {
                copyBtn.onclick = () => {
                    navigator.clipboard.writeText(data.markdown || '');
                    if (window.app && app.showToast) app.showToast("AI kollokatsiya tahlili nusxalandi!", "success");
                };
            }

            // Setup filter database button
            if (filterDbBtn) {
                filterDbBtn.onclick = () => {
                    const searchInput = document.getElementById('collocSearchInput');
                    if (searchInput) {
                        searchInput.value = data.word;
                        this.searchTerm = data.word;
                        this.page = 1;
                        this.fetchCollocations(true);
                        searchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        if (window.app && app.showToast) app.showToast(`«${data.word}» boʻyicha matritsa filtrlash ishga tushdi`, "info");
                    }
                };
            }

        } catch (err) {
            resultContent.innerHTML = `
                <div class="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs">
                    <p class="font-bold flex items-center gap-1.5"><i data-lucide="alert-circle" class="w-4 h-4"></i> Tahlil qilishda xatolik yuz berdi</p>
                    <p class="mt-1">${err.message}</p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
        }
    }

    closeModal() {
        const modal = document.getElementById('collocDetailModal');
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    }

    exportCSV() {
        const headers = ["ID", "Inglizcha_Kollokatsiya", "Ozbekcha_Ekvivalent", "Struktur_Semantik_Qolip_3_1", "Semantik_Guruh_3_1", "Tarjima_Ekvivalentligi_3_2", "Lingvomadaniy_Izoh_3_3", "MI_Score", "T_Score", "Log_Likelihood", "Chastota", "Manba_Kitob", "Kalka_Xatosi", "Misol_UZ", "Misol_EN"];
        const rows = this.dataset.map(item => [
            item.id,
            `"${(item.english || '').replace(/"/g, '""')}"`,
            `"${(item.uzbek || '').replace(/"/g, '""')}"`,
            `"${(item.pattern || '').replace(/"/g, '""')}"`,
            `"${(item.semanticGroup || '').replace(/"/g, '""')}"`,
            `"${(item.equivalenceType || item.category || '').replace(/"/g, '""')}"`,
            `"${(item.culturalNote || '').replace(/"/g, '""')}"`,
            item.miScore ?? '',
            item.tScore ?? '',
            item.logLikelihood ?? '',
            item.freq || 0,
            `"${(item.sourceBook || '').replace(/"/g, '""')}"`,
            `"${(item.literalTrap || '').replace(/"/g, '""')}"`,
            `"${(item.example && item.example.uz ? item.example.uz : '').replace(/"/g, '""')}"`,
            `"${(item.example && item.example.en ? item.example.en : '').replace(/"/g, '""')}"`
        ]);

        const csvContent = "data:text/csv;charset=utf-8,\uFEFF" + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `UZ_EN_Collocation_Corpus_${this.currentSource !== 'all' ? this.currentSource : 'Barchasi'}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        if (window.app && app.showToast) {
            app.showToast("Kollokatsiyalar CSV formatida yuklab olindi!", "success");
        }
    }

    exportExcel() {
        const headers = ["ID", "Inglizcha_Kollokatsiya", "Ozbekcha_Ekvivalent", "Struktur_Semantik_Qolip_3_1", "Semantik_Guruh_3_1", "Tarjima_Ekvivalentligi_3_2", "Lingvomadaniy_Izoh_3_3", "MI_Score", "T_Score", "Log_Likelihood", "Chastota", "Manba_Kitob", "Muallif", "Tarjimon", "Segment_ID", "Kalka_Tuzatishi", "Parallel_Misol_UZ", "Parallel_Misol_EN"];
        const rows = this.dataset.map(item => {
            const sm = item.sourceMeta || {};
            const ex = item.example || {};
            return [
                item.id,
                `"${(item.english || '').replace(/"/g, '""')}"`,
                `"${(item.uzbek || '').replace(/"/g, '""')}"`,
                `"${(item.pattern || '').replace(/"/g, '""')}"`,
                `"${(item.semanticGroup || '').replace(/"/g, '""')}"`,
                `"${(item.equivalenceType || item.category || '').replace(/"/g, '""')}"`,
                `"${(item.culturalNote || '').replace(/"/g, '""')}"`,
                item.miScore ?? '',
                item.tScore ?? '',
                item.logLikelihood ?? '',
                item.freq || 0,
                `"${(sm.bookName || item.sourceBook || '').replace(/"/g, '""')}"`,
                `"${(sm.author || '').replace(/"/g, '""')}"`,
                `"${(sm.translator || '').replace(/"/g, '""')}"`,
                `"${(sm.segmentId || item.id || '').replace(/"/g, '""')}"`,
                `"${(item.literalTrap || '').replace(/"/g, '""')}"`,
                `"${(ex.uz || '').replace(/"/g, '""')}"`,
                `"${(ex.en || '').replace(/"/g, '""')}"`
            ];
        });

        // Tab-delimited with UTF-8 BOM opens natively in Excel without corrupting Uzbek characters
        const tsvContent = "\uFEFF" + [headers.join('\t'), ...rows.map(e => e.join('\t'))].join('\n');
        const blob = new Blob([tsvContent], { type: 'application/vnd.ms-excel;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `UZ_EN_Collocations_Matrix_PhD_${this.currentSource !== 'all' ? this.currentSource : 'Full'}.xls`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        if (window.app && app.showToast) {
            app.showToast("Kollokatsiyalar toʻliq Excel (XLS) formatida yuklab olindi!", "success");
        }
    }
}

const collocationManager = new CollocationManager();
