/**
 * js/corpus.js - TILCOR Rebuilt Unified Search & Results Manager (Step 02)
 * Strictly follows Section 2 and Section 4 of TILCOR_02.md:
 * - Strict language separation
 * - Word family matching
 * - 3-section layout:
 *     1. So‘zlar (Inflected, Derived, Compound)
 *     2. Kollokatsiyalar (Candidates / Reference with badges)
 *     3. Korpusdagi gaplar (Concordance with collapsed unverified translations)
 * - Safe HTML escaping & highlighting
 * - Desktop 2-column side-by-side, mobile stacked with sticky tabs
 * - Honest error & empty states
 */

class CorpusManager {
    constructor() {
        this.searchTerm = '';
        this.selectedLang = 'auto'; // 'auto', 'uz', 'en'
        this.currentBook = 'all';
        this.currentPage = 1;
        this.activeFilterWord = null;
        this.searchDebounce = null;
        this.lastResponse = null;

        this.init();
    }

    init() {
        this.bindEvents();
        // Initial search for default state
        const input = document.getElementById('corpusSearchInput');
        if (input && input.value.trim()) {
            this.searchTerm = input.value.trim();
            this.executeSearch();
        } else {
            this.executeSearch();
        }
    }

    bindEvents() {
        const searchInput = document.getElementById('corpusSearchInput');
        const bookFilter = document.getElementById('corpusBookFilter');
        const clearBtn = document.getElementById('corpusClearBtn');

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value.trim();
                this.currentPage = 1;
                this.activeFilterWord = null;
                clearTimeout(this.searchDebounce);
                this.searchDebounce = setTimeout(() => {
                    this.executeSearch();
                }, 300);
            });
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    clearTimeout(this.searchDebounce);
                    this.executeSearch();
                }
            });
        }

        if (bookFilter) {
            bookFilter.addEventListener('change', (e) => {
                this.currentBook = e.target.value;
                this.currentPage = 1;
                this.executeSearch();
            });
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                if (searchInput) searchInput.value = '';
                if (bookFilter) bookFilter.value = 'all';
                this.searchTerm = '';
                this.currentBook = 'all';
                this.selectedLang = 'auto';
                this.activeFilterWord = null;
                this.currentPage = 1;
                this.executeSearch();
            });
        }
    }

    search(query) {
        this.searchTerm = (query || '').trim();
        this.currentPage = 1;
        this.activeFilterWord = null;
        const input = document.getElementById('corpusSearchInput');
        if (input) input.value = this.searchTerm;
        this.executeSearch();
    }

    filterByBook(bookKey) {
        this.currentBook = bookKey;
        const bookFilter = document.getElementById('corpusBookFilter');
        if (bookFilter) bookFilter.value = bookKey;
        this.currentPage = 1;
        this.executeSearch();
    }

    setLanguage(lang) {
        this.selectedLang = lang;
        this.currentPage = 1;
        this.executeSearch();
    }

    filterByWord(word) {
        if (this.activeFilterWord === word) {
            this.activeFilterWord = null; // toggle off
        } else {
            this.activeFilterWord = word;
        }
        this.renderAll(this.lastResponse);
        // Smooth scroll to sentences section
        const sec3 = document.getElementById('results-section-sentences');
        if (sec3) sec3.scrollIntoView({ behavior: 'smooth' });
    }

    goToPage(page) {
        this.currentPage = page;
        this.executeSearch(false);
        const sec3 = document.getElementById('results-section-sentences');
        if (sec3) sec3.scrollIntoView({ behavior: 'smooth' });
    }

    async executeSearch(resetPage = true) {
        if (resetPage) {
            this.currentPage = 1;
        }

        const container = document.getElementById('corpusResultsContainer');
        const countBadge = document.getElementById('corpusResultCountBadge');

        if (countBadge) {
            countBadge.innerHTML = `<span class="inline-flex items-center gap-1.5 text-indigo-600 dark:text-indigo-400 font-semibold"><span class="w-3.5 h-3.5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></span> Qidirilmoqda...</span>`;
        }

        try {
            const params = new URLSearchParams({
                q: this.searchTerm,
                lang: this.selectedLang,
                book: this.currentBook,
                page: this.currentPage,
                limit: 50
            });

            const resp = await fetch(`/api/search?${params.toString()}`);
            if (!resp.ok) {
                this.renderError(`Server xatosi (HTTP ${resp.status}). Iltimos, qayta urinib ko‘ring.`);
                return;
            }

            const data = await resp.json();
            this.lastResponse = data;
            this.renderAll(data);
        } catch (err) {
            console.error('Search request failed:', err);
            this.renderError("Tarmoq xatosi: Korpus serveriga ulanib bo‘lmadi. Hech qanday soxta ma'lumot ko‘rsatilmaydi.");
        }
    }

    renderError(msg) {
        const container = document.getElementById('corpusResultsContainer');
        const countBadge = document.getElementById('corpusResultCountBadge');
        if (countBadge) {
            countBadge.innerHTML = `<span class="text-rose-600 font-semibold">Xatolik yuz berdi</span>`;
        }
        if (container) {
            container.innerHTML = `
                <div class="text-center py-12 bg-rose-50 dark:bg-rose-950/30 rounded-3xl border border-rose-200 dark:border-rose-900 p-8">
                    <div class="w-12 h-12 rounded-2xl bg-rose-100 dark:bg-rose-900 text-rose-600 flex items-center justify-center mx-auto mb-3">
                        <i data-lucide="alert-circle" class="w-6 h-6"></i>
                    </div>
                    <h4 class="text-base font-bold text-rose-900 dark:text-rose-200">${msg}</h4>
                    <p class="text-xs text-rose-600 dark:text-rose-400 mt-1">Haqiqiy korpus ma'lumotlariga qaytish uchun sahifani yangilang.</p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
        }
    }

    renderAll(data) {
        const container = document.getElementById('corpusResultsContainer');
        const countBadge = document.getElementById('corpusResultCountBadge');
        if (!container || !data) return;

        const summary = data.summary || { total_word_forms: 0, corpus_occurrences: 0, collocations_count: 0 };
        const query = data.query || '';
        const detectedLang = data.detected_lang || 'uz';
        const selectedLang = data.selected_lang || detectedLang;
        const isAmbiguous = data.is_ambiguous || false;

        // Update Top Count Badge
        if (countBadge) {
            countBadge.innerHTML = query
                ? `<strong>«${this.escapeHtml(query)}»</strong> bo‘yicha <strong>${summary.corpus_occurrences} ta</strong> parallel jumla, <strong>${summary.total_word_forms} ta</strong> so‘z shakli, <strong>${summary.collocations_count} ta</strong> kollokatsiya topildi`
                : `Ko‘rsatilmoqda: <strong>${summary.corpus_occurrences} ta</strong> jumla (boshlang‘ich namuna)`;
        }

        // Empty state check
        if (query && summary.corpus_occurrences === 0 && summary.total_word_forms === 0 && summary.collocations_count === 0) {
            container.innerHTML = `
                <div class="text-center py-16 bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 p-8 space-y-3">
                    <div class="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-700 text-slate-400 flex items-center justify-center mx-auto">
                        <i data-lucide="search-x" class="w-6 h-6"></i>
                    </div>
                    <h4 class="text-lg font-bold text-slate-800 dark:text-white">«${this.escapeHtml(query)}» bo‘yicha natija topilmadi</h4>
                    <p class="text-xs text-slate-500 max-w-md mx-auto">
                        Qidirilayotgan so‘z Cho‘lpon («Kecha va kunduz») yoki Hemingway («Chol va dengiz») matnlarida, shuningdek faol lug‘at va kollokatsiyalar bazasida mavjud emas. So‘z o‘zagini tekshirib ko‘ring.
                    </p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        // Build HTML
        let html = `
            <div class="space-y-6">
                <!-- 0. Header & Language Controls -->
                ${this.renderHeaderBar(query, detectedLang, selectedLang, isAmbiguous, summary)}

                <!-- SECTION A: MUQOBIL SUMMARY (PART 1.3 & PART 4.A) -->
                ${this.renderMuqobilSummary(data.muqobil_summary, query, selectedLang)}

                <!-- Mobile Sticky Navigation Tabs (Part 4) -->
                <div class="lg:hidden sticky top-16 z-30 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md p-2 rounded-2xl border border-slate-200 dark:border-slate-800 flex items-center justify-between gap-2 text-xs shadow-sm">
                    <a href="#results-section-words" class="flex-1 py-2 text-center rounded-xl bg-slate-100 dark:bg-slate-800 font-bold text-slate-700 dark:text-slate-200">
                        So‘zlar (${summary.total_word_forms})
                    </a>
                    <a href="#results-section-collocations" class="flex-1 py-2 text-center rounded-xl bg-slate-100 dark:bg-slate-800 font-bold text-slate-700 dark:text-slate-200">
                        Kollokatsiyalar (${summary.collocations_count})
                    </a>
                    <a href="#results-section-sentences" class="flex-1 py-2 text-center rounded-xl bg-indigo-50 dark:bg-indigo-950 font-bold text-indigo-700 dark:text-indigo-300">
                        Gaplar (${summary.corpus_occurrences})
                    </a>
                </div>

                <!-- Desktop 2-Column Side-by-Side (Part 4) -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
                    <!-- SECTION 1: SO'ZLAR -->
                    <div id="results-section-words">
                        ${this.renderSectionWords(data.words || [], selectedLang)}
                    </div>

                    <!-- SECTION 2: KOLLOKATSIYALAR -->
                    <div id="results-section-collocations">
                        ${this.renderSectionCollocations(data.collocations || [], selectedLang, query)}
                    </div>
                </div>

                <!-- SECTION 3: KORPUSDAGI GAPLAR (Full Width Below) -->
                <div id="results-section-sentences">
                    ${this.renderSectionSentences(data.corpus_sentences || [], data.pagination, selectedLang)}
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    renderHeaderBar(query, detectedLang, selectedLang, isAmbiguous, summary) {
        const langLabel = selectedLang === 'uz' ? 'O‘zbek tili (UZ)' : 'Ingliz tili (EN)';
        const langBadgeClass = selectedLang === 'uz'
            ? 'bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800'
            : 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800';

        let ambiguousBanner = '';
        if (isAmbiguous) {
            ambiguousBanner = `
                <div class="p-3.5 bg-amber-50 dark:bg-amber-950/50 border border-amber-200 dark:border-amber-800/80 rounded-2xl flex flex-wrap items-center justify-between gap-3 text-xs">
                    <div class="flex items-center gap-2 text-amber-900 dark:text-amber-200 font-semibold">
                        <i data-lucide="help-circle" class="w-4 h-4 text-amber-600"></i>
                        <span><strong>«${this.escapeHtml(query)}»</strong> so‘zi ham o‘zbekcha, ham inglizcha matnlarda uchraydi. Kerakli tilni tanlang:</span>
                    </div>
                    <div class="flex items-center gap-1.5">
                        <button onclick="corpusManager.setLanguage('uz')" class="px-3 py-1 rounded-xl font-bold text-xs transition ${selectedLang === 'uz' ? 'bg-indigo-600 text-white shadow-sm' : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200'}">
                            🇺🇿 O‘zbekcha
                        </button>
                        <button onclick="corpusManager.setLanguage('en')" class="px-3 py-1 rounded-xl font-bold text-xs transition ${selectedLang === 'en' ? 'bg-indigo-600 text-white shadow-sm' : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200'}">
                            🇬🇧 Inglizcha
                        </button>
                    </div>
                </div>
            `;
        }

        return `
            <div class="bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm space-y-3">
                ${ambiguousBanner}
                <div class="flex flex-wrap items-center justify-between gap-3">
                    <div class="flex items-center gap-3">
                        <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Qidiruv tili:</span>
                        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-bold border ${langBadgeClass}">
                            <span class="w-2 h-2 rounded-full ${selectedLang === 'uz' ? 'bg-blue-600' : 'bg-emerald-500'}"></span>
                            ${langLabel}
                        </span>
                        ${query ? `<span class="text-sm font-bold text-slate-800 dark:text-white">«${this.escapeHtml(query)}»</span>` : ''}
                    </div>

                    <!-- Explicit Language Switch -->
                    <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-900 p-1 rounded-xl border border-slate-200 dark:border-slate-800 text-xs">
                        <button onclick="corpusManager.setLanguage('uz')" class="px-2.5 py-1 rounded-lg font-semibold transition ${selectedLang === 'uz' ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'}">
                            UZ
                        </button>
                        <button onclick="corpusManager.setLanguage('en')" class="px-2.5 py-1 rounded-lg font-semibold transition ${selectedLang === 'en' ? 'bg-white dark:bg-slate-800 text-indigo-600 dark:text-indigo-400 shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'}">
                            EN
                        </button>
                    </div>
                </div>

                <!-- Summary Line (Section 2.3) -->
                <div class="pt-2 border-t border-slate-100 dark:border-slate-700/60 flex flex-wrap items-center gap-4 text-xs text-slate-600 dark:text-slate-300">
                    <span class="inline-flex items-center gap-1.5">
                        <i data-lucide="layers" class="w-3.5 h-3.5 text-indigo-500"></i>
                        <strong class="font-mono text-slate-900 dark:text-white">${summary.total_word_forms} ta</strong> so‘z shakli
                    </span>
                    <span>·</span>
                    <span class="inline-flex items-center gap-1.5">
                        <i data-lucide="book-open" class="w-3.5 h-3.5 text-emerald-500"></i>
                        <strong class="font-mono text-slate-900 dark:text-white">${summary.corpus_occurrences} marta</strong> korpusda
                    </span>
                    <span>·</span>
                    <span class="inline-flex items-center gap-1.5">
                        <i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-500"></i>
                        <strong class="font-mono text-slate-900 dark:text-white">${summary.collocations_count} ta</strong> kollokatsiya
                    </span>
                </div>
            </div>
        `;
    }

    renderMuqobilSummary(summary, query, lang) {
        if (!summary) return '';
        const s1 = summary.source_1_confirmed || [];
        const s2 = summary.source_2_ai_proposal || [];
        const s3 = summary.source_3_dictionary || [];
        const s4 = summary.source_4_reference || [];
        const isEmpty = summary.source_1_empty;

        const citationUrl = `https://tilcor.uz/soz/${encodeURIComponent(query)}`;
        const citationText = `TILCOR (2026). «${query}». ${citationUrl} (murojaat sanasi: 13.10.2026)`;

        return `
            <div id="results-section-muqobil" class="bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm space-y-4">
                <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-700/60">
                    <div class="flex items-center gap-2">
                        <div class="w-8 h-8 rounded-xl bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300 flex items-center justify-center font-bold">
                            <i data-lucide="layers" class="w-4 h-4"></i>
                        </div>
                        <div>
                            <h3 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                Muqobil (Ekvivalent) Xulosasi
                            </h3>
                            <p class="text-[11px] text-slate-500">Ierarxiya bo‘yicha 5 manbali haqiqiy tarjima va muqobillar</p>
                        </div>
                    </div>

                    <!-- Citation Line (Part 4.E) -->
                    <div class="text-xs font-mono bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-1.5 flex items-center gap-2 text-slate-600 dark:text-slate-300">
                        <span class="truncate max-w-xs md:max-w-md">Iqtibos: <strong>${citationText}</strong></span>
                        <button onclick="navigator.clipboard.writeText('${this.escapeQuotes(citationText)}'); alert('Iqtibos nusxalandi!')" class="shrink-0 text-[10px] font-sans font-bold px-2 py-0.5 rounded bg-white dark:bg-slate-800 border hover:bg-slate-100 dark:hover:bg-slate-700 transition">
                            Nusxalash
                        </button>
                    </div>
                </div>

                <!-- 1. Kitobdagi tarjima — tasdiqlangan (Solid colour 2) -->
                <div class="space-y-2">
                    <div class="flex items-center justify-between text-xs font-bold text-slate-700 dark:text-slate-200">
                        <span class="flex items-center gap-1.5">
                            <span class="w-2.5 h-2.5 rounded-full bg-sky-600"></span>
                            1. Kitobdagi tarjima — tasdiqlangan
                        </span>
                        <span class="font-mono text-[11px] text-slate-400">${s1.length} ta birlik</span>
                    </div>

                    ${s1.length > 0 ? `
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                            ${s1.map(it => `
                                <div class="p-3.5 rounded-2xl border border-sky-300 dark:border-sky-800 bg-sky-50/70 dark:bg-sky-950/40 space-y-1.5">
                                    <div class="flex items-start justify-between gap-2">
                                        <span class="equiv-confirmed bg-sky-100 dark:bg-sky-950 text-sky-900 dark:text-sky-100 border-b-2 border-sky-600 px-2 py-0.5 rounded font-bold text-sm">
                                            «${this.escapeHtml(it.equivalent)}»
                                        </span>
                                        <span class="text-xs font-mono font-bold text-sky-800 dark:text-sky-300 bg-sky-100 dark:bg-sky-900 px-2 py-0.5 rounded-full">
                                            ${it.count} marta
                                        </span>
                                    </div>
                                    <div class="text-[11px] text-slate-600 dark:text-slate-400 flex flex-wrap items-center gap-1.5 pt-1 border-t border-sky-200/50">
                                        <span>Shakli: <strong>${this.escapeHtml(it.form || '—')}</strong></span>
                                        <span>·</span>
                                        <span>Sahifalar: <strong>${this.escapeHtml(it.pages || '—')}</strong></span>
                                    </div>
                                    ${it.first_segment_id ? `
                                        <div class="pt-1">
                                            <a href="#gap-${it.first_segment_id}" class="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1">
                                                <span>Namuna gapni ko‘rish</span>
                                                <i data-lucide="arrow-down-right" class="w-3.5 h-3.5"></i>
                                            </a>
                                        </div>
                                    ` : ''}
                                </div>
                            `).join('')}
                        </div>
                    ` : `
                        <div class="p-3.5 rounded-2xl border border-amber-200/80 dark:border-amber-900/60 bg-amber-50/50 dark:bg-amber-950/30 text-xs text-amber-800 dark:text-amber-200 flex flex-wrap items-center justify-between gap-2">
                            <span>${this.escapeHtml(summary.empty_message || 'Kitobdagi tarjima hali tasdiqlanmagan: tekshiruv navbatida')}</span>
                            ${summary.unconfirmed_count > 0 ? `<a href="/preview_alignment_queue.html?q=${encodeURIComponent(query)}" class="text-indigo-600 dark:text-indigo-400 font-bold underline">Tekshiruv navbati (Admin)</a>` : ''}
                        </div>
                    `}
                </div>

                <!-- 2. Kitobdagi tarjima — AI-taklif (Dashed colour 2) -->
                ${s2.length > 0 ? `
                    <div class="space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                        <div class="flex items-center justify-between text-xs font-bold text-slate-500 dark:text-slate-400">
                            <span class="flex items-center gap-1.5">
                                <span class="w-2.5 h-2.5 rounded-full border border-sky-500 border-dashed"></span>
                                2. Kitobdagi tarjima — AI-taklif (tekshirilmagan)
                            </span>
                            <span class="font-mono text-[11px]">${s2.length} ta taklif</span>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                            ${s2.slice(0, 6).map(it => `
                                <div class="p-3 rounded-2xl border border-dashed border-sky-300 dark:border-sky-800 bg-sky-50/30 dark:bg-sky-950/20 space-y-1">
                                    <div class="flex items-start justify-between gap-2">
                                        <span class="equiv-proposed bg-sky-50 dark:bg-sky-950/70 text-sky-800 dark:text-sky-200 border-b-2 border-dashed border-sky-500 px-2 py-0.5 rounded font-semibold text-xs">
                                            «${this.escapeHtml(it.equivalent)}»
                                        </span>
                                        <span class="text-[11px] font-mono text-slate-500 font-bold">${it.count} marta</span>
                                    </div>
                                    <div class="text-[10px] text-slate-400">Sahifalar: ${this.escapeHtml(it.pages || '—')}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                <!-- 3. Lug‘atdagi tarjima (Grey label) -->
                ${s3.length > 0 ? `
                    <div class="space-y-1.5 pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
                        <div class="font-bold text-slate-500">3. Lug‘atdagi tarjima:</div>
                        <div class="space-y-1">
                            ${s3.map(it => `
                                <div class="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                                    <div class="font-medium text-slate-800 dark:text-slate-200">«${this.escapeHtml(it.equivalent)}»</div>
                                    <div class="text-[10px] text-slate-400 italic mt-0.5">${this.escapeHtml(it.dictionary_source || 'Lug‘at')}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                <!-- 4. Ma’lumotnomadagi muqobil (Class label) -->
                ${s4.length > 0 ? `
                    <div class="space-y-1.5 pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
                        <div class="font-bold text-slate-500">4. Ma’lumotnomadagi muqobil:</div>
                        <div class="flex flex-wrap gap-2">
                            ${s4.slice(0, 5).map(it => `
                                <span class="px-2.5 py-1 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 text-xs">
                                    «${this.escapeHtml(it.collocation || it.uzbek_translation)}»
                                    <span class="text-[9px] font-mono text-slate-400 ml-1">[${this.escapeHtml(it.class_label || 'KORPUS')}]</span>
                                </span>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderSectionWords(words, lang) {
        if (!words || words.length === 0) {
            return `
                <div class="bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm space-y-3">
                    <h3 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <i data-lucide="book-a" class="w-5 h-5 text-indigo-600"></i> 1-BO‘LIM: So‘z shakllari
                    </h3>
                    <p class="text-xs text-slate-500">Bazada ushbu so‘z oilasiga oid qo‘shimcha shakllar topilmadi.</p>
                </div>
            `;
        }

        // Group into inflected, derived, compound
        const inflected = words.filter(w => w.group === 'exact' || w.group === 'inflected');
        const derived = words.filter(w => w.group === 'derived');
        const compound = words.filter(w => w.group === 'compound');

        const renderGroupBlock = (title, items, badgeColor) => {
            if (!items || items.length === 0) return '';
            return `
                <div class="space-y-2">
                    <div class="flex items-center justify-between text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                        <span>${title}</span>
                        <span class="font-mono">${items.length} ta</span>
                    </div>
                    <div class="space-y-2">
                        ${items.map(item => this.renderWordCard(item, badgeColor)).join('')}
                    </div>
                </div>
            `;
        };

        return `
            <div class="bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm space-y-5">
                <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-700/60">
                    <div>
                        <h3 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <i data-lucide="book-a" class="w-5 h-5 text-indigo-600"></i> 1-BO‘LIM: So‘zlar (${words.length} ta shakl)
                        </h3>
                        <p class="text-[11px] text-slate-500 mt-0.5">Morfologik so‘z oilasi bo‘yicha guruhlangan birliklar</p>
                    </div>
                    ${this.activeFilterWord ? `
                        <button onclick="corpusManager.filterByWord('${this.activeFilterWord}')" class="px-2.5 py-1 rounded-xl bg-amber-50 dark:bg-amber-950 text-amber-700 dark:text-amber-300 text-xs font-semibold flex items-center gap-1 border border-amber-200">
                            Filtr: «${this.escapeHtml(this.activeFilterWord)}» <i data-lucide="x" class="w-3.5 h-3.5"></i>
                        </button>
                    ` : ''}
                </div>

                <div class="space-y-5 max-h-[680px] overflow-y-auto pr-1">
                    ${renderGroupBlock('1. Turlangan shakllar (Inflected)', inflected, 'indigo')}
                    ${renderGroupBlock('2. Yasalgan so‘zlar (Derived)', derived, 'emerald')}
                    ${renderGroupBlock('3. Qo‘shma va juft so‘zlar (Compound)', compound, 'amber')}
                </div>
            </div>
        `;
    }

    renderWordCard(item, color) {
        const isFiltered = this.activeFilterWord === item.word;
        const totalOcc = item.total_occurrences || 0;

        // Occurrences breakdown
        const bCounts = item.book_counts || {};
        const bDetails = Object.entries(bCounts).map(([k, v]) => `${k === 'cholpon' ? 'Cho‘lpon' : 'Hemingway'}: ${v}`).join(' · ');

        return `
            <div class="p-3.5 rounded-2xl border transition duration-150 ${isFiltered ? 'bg-indigo-50/80 dark:bg-indigo-950/60 border-indigo-300 dark:border-indigo-700 shadow-sm' : 'bg-slate-50 dark:bg-slate-900/60 border-slate-200/80 dark:border-slate-800 hover:border-indigo-200'}">
                <div class="flex items-center justify-between gap-2">
                    <div class="flex items-center gap-2">
                        <button onclick="corpusManager.filterByWord('${item.word}')" class="text-sm font-bold text-slate-900 dark:text-white hover:text-indigo-600 transition text-left cursor-pointer">
                            ${this.escapeHtml(item.word)}
                        </button>
                        <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold">
                            ${this.escapeHtml(item.pos || '—')}
                        </span>
                    </div>

                    <button onclick="corpusManager.filterByWord('${item.word}')" title="Ushbu so‘z qatnashgan gaplarni ko‘rish" class="text-[11px] font-mono font-bold px-2 py-0.5 rounded-lg bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 border border-indigo-200/60 hover:bg-indigo-600 hover:text-white transition flex items-center gap-1">
                        <span>${totalOcc} marta</span>
                        <i data-lucide="arrow-down" class="w-3 h-3"></i>
                    </button>
                </div>

                <div class="text-[11px] text-slate-500 mt-1">
                    ${bDetails ? `Asarlarda: ${bDetails}` : 'Korpusda uchramagan (faqat lug‘atda)'}
                </div>

                <!-- Dictionary Translation (named dictionary) -->
                <div class="mt-2 pt-2 border-t border-slate-200/60 dark:border-slate-800 text-xs space-y-1">
                    <div class="flex items-start gap-1.5 text-slate-700 dark:text-slate-300">
                        <span class="font-bold text-indigo-600 shrink-0">Lug‘atdagi tarjima:</span>
                        <span class="font-medium">${this.escapeHtml(item.dict_translation || 'Mavjud emas')}</span>
                    </div>
                    <div class="text-[10px] text-slate-400 italic">
                        Manba: ${this.escapeHtml(item.dict_source || 'Lug‘at')}
                    </div>
                    <div class="flex items-center gap-1.5 text-[11px] text-slate-400 pt-0.5">
                        <span class="font-bold text-slate-500">Kitobdagi tarjima:</span>
                        <span class="px-2 py-0.2 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 font-mono text-[10px]">
                            ${item.book_translation_status || 'Tekislash tasdiqlangach ko‘rsatiladi'}
                        </span>
                    </div>
                </div>
            </div>
        `;
    }

    renderSectionCollocations(collocations, lang, query) {
        return `
            <div class="bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm space-y-5">
                <div class="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-700/60">
                    <div>
                        <h3 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <i data-lucide="sparkles" class="w-5 h-5 text-emerald-600"></i> 2-BO‘LIM: Kollokatsiyalar (${collocations.length} ta)
                        </h3>
                        <p class="text-[11px] text-slate-500 mt-0.5">
                            ${lang === 'uz' ? 'O‘zbek matnlaridan olingan avtomatik nomzodlar' : 'Inglizcha ma’lumotnomalar va matn nomzodlari'}
                        </p>
                    </div>
                </div>

                <div class="space-y-3 max-h-[680px] overflow-y-auto pr-1">
                    ${collocations.length === 0 ? `
                        <div class="p-6 text-center text-xs text-slate-500 bg-slate-50 dark:bg-slate-900/40 rounded-2xl border border-dashed border-slate-200 dark:border-slate-800">
                            Bazada ushbu so‘z bo‘yicha kollokatsiyalar topilmadi.
                        </div>
                    ` : collocations.map(col => this.renderCollocationCard(col, lang)).join('')}
                </div>
            </div>
        `;
    }

    renderCollocationCard(col, lang) {
        const isCandidate = col.is_candidate || col.source_badge?.includes('Avtomatik nomzod');
        const badgeColor = isCandidate
            ? 'bg-amber-50 text-amber-800 dark:bg-amber-950/70 dark:text-amber-200 border-amber-200 dark:border-amber-800'
            : 'bg-emerald-50 text-emerald-800 dark:bg-emerald-950/70 dark:text-emerald-200 border-emerald-200 dark:border-emerald-800';

        return `
            <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 space-y-2.5 hover:shadow-sm transition">
                <div class="flex flex-wrap items-center justify-between gap-2">
                    <span class="inline-flex items-center px-2 py-0.5 rounded-lg text-[10px] font-bold border ${badgeColor}">
                        ${this.escapeHtml(col.source_badge || 'Kollokatsiya')}
                    </span>
                    <span class="text-[10px] font-mono text-slate-500">
                        ${col.sentences_count !== undefined ? `<strong class="text-slate-800 dark:text-slate-200">${col.sentences_count} gapda</strong> · <strong class="text-slate-800 dark:text-slate-200">${col.occurrences_count || col.corpus_frequency || 1} marta</strong>` : `Chastota: <strong>${col.corpus_frequency || 1} marta</strong>`}
                    </span>
                </div>

                <div class="flex items-center justify-between">
                    <h4 class="text-sm font-bold text-slate-900 dark:text-white">
                        ${this.escapeHtml(col.collocation || '')}
                    </h4>
                    <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                        Qolip: ${this.escapeHtml(col.pattern || '—')}
                    </span>
                </div>

                ${col.uzbek_translation ? `
                    <div class="p-2 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700/80 text-xs">
                        <div class="flex items-center justify-between text-[10px] text-slate-400 mb-0.5">
                            <span class="font-bold text-indigo-600">O‘zbekcha tarjima ekvivalenti:</span>
                            <span class="px-1.5 py-0.2 rounded bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 font-mono text-[9px]">${this.escapeHtml(col.uzbek_label || 'AI-taklif')}</span>
                        </div>
                        <div class="font-semibold text-slate-800 dark:text-slate-200">${this.escapeHtml(col.uzbek_translation)}</div>
                    </div>
                ` : ''}

                ${col.example ? `
                    <div class="text-xs text-slate-600 dark:text-slate-300 pt-1.5 border-t border-slate-200/50 dark:border-slate-800 space-y-1">
                        <div class="font-serif italic">«${this.escapeHtml(col.example.source_sentence || '')}»</div>
                        ${col.example.target_sentence ? `
                            <div class="text-[11px] font-serif text-slate-500 dark:text-slate-400 pl-2 border-l-2 border-indigo-300 dark:border-indigo-700">
                                ${col.example.target_highlighted || this.escapeHtml(col.example.target_sentence)}
                            </div>
                        ` : ''}
                        <div class="text-[10px] text-slate-400 font-normal not-italic flex items-center justify-between">
                            <span>Manba: ${this.escapeHtml(col.example.book || '')}</span>
                            ${col.example.page_source && col.example.page_target ? `
                                <span class="font-mono">Asliyat: ${col.example.page_source} · Tarjima: ${col.example.page_target}</span>
                            ` : (col.example.book?.includes('Namuna') ? '<span class="text-amber-600 font-medium">Namuna gap (kitobdan emas)</span>' : '')}
                        </div>
                    </div>
                ` : ''}

                <div class="pt-1 flex justify-end">
                    <a href="#results-section-sentences" class="text-xs text-indigo-600 dark:text-indigo-400 font-semibold hover:underline flex items-center gap-1">
                        Barcha misollar <i data-lucide="arrow-down" class="w-3 h-3"></i>
                    </a>
                </div>
            </div>
        `;
    }

    renderSectionSentences(sentences, pagination, lang) {
        // If word filter active, filter locally
        let displaySentences = sentences;
        if (this.activeFilterWord) {
            const norm = (str) => (window.normalizeApostrophes ? normalizeApostrophes(str) : str);
            const fw = norm(this.activeFilterWord).toLowerCase();
            displaySentences = sentences.filter(s => {
                const raw = norm(s.source_raw || '').toLowerCase();
                return raw.includes(fw);
            });
        }

        return `
            <div class="bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm space-y-5">
                <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-700/60">
                    <div>
                        <h3 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                            <i data-lucide="split" class="w-5 h-5 text-indigo-600"></i> 3-BO‘LIM: Korpusdagi gaplar (Jami: ${pagination ? pagination.total_sentences : displaySentences.length} ta)
                        </h3>
                        <p class="text-[11px] text-slate-500 mt-0.5">
                            So‘z oilasining barcha shakllari kontekstda ajratib ko‘rsatilgan (maksimal 50 ta ko‘rinish)
                        </p>
                    </div>

                    ${this.activeFilterWord ? `
                        <div class="text-xs font-semibold px-3 py-1 rounded-xl bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">
                            Ko‘rsatilmoqda: «${this.escapeHtml(this.activeFilterWord)}» shakli (${displaySentences.length} ta)
                        </div>
                    ` : ''}
                </div>

                <!-- List of Sentences -->
                <div class="space-y-4">
                    ${displaySentences.length === 0 ? `
                        <div class="text-center py-8 text-xs text-slate-500 bg-slate-50 dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">
                            Ushbu tanlov bo‘yicha gaplar topilmadi.
                        </div>
                    ` : displaySentences.map(s => this.renderSentenceCard(s, lang)).join('')}
                </div>

                <!-- Pagination (Part 2.3 - at most 50 with pagination) -->
                ${pagination && pagination.total_pages > 1 ? this.renderPagination(pagination) : ''}
            </div>
        `;
    }

    renderSentenceCard(item, lang) {
        const isCholpon = item.book === 'cholpon';
        const bookTitle = isCholpon ? 'Cho‘lpon: «Kecha va kunduz»' : 'E. Hemingway: «Chol va dengiz» (Tarjimon: Ibrohim G‘ofurov)';
        const bookBadge = isCholpon
            ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 border-indigo-200'
            : 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 border-emerald-200';

        let pageLabel = '';
        if (item.page_source && item.page_target) {
            pageLabel = `Asliyat: ${item.page_source} · Tarjima: ${item.page_target}`;
        } else if (item.page_source) {
            pageLabel = `Asliyat: ${item.page_source}`;
        } else {
            pageLabel = `Asliyat: sahifa belgilanmagan`;
        }

        const isMos = (item.alignment_status === 'avtomatik — ikki usul mos');
        const isConfirmed = (item.alignment_status === 'tasdiqlangan');
        const isLow = !isMos && !isConfirmed;

        return `
            <div id="gap-${this.escapeHtml(item.id || '')}" class="bg-slate-50 dark:bg-slate-900/60 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-5 space-y-3.5 hover:border-indigo-200 transition">
                <div class="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-200/50 dark:border-slate-800">
                    <div class="flex items-center gap-2">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${bookBadge}">
                            ${bookTitle}
                        </span>
                        <span class="text-xs font-mono font-bold text-slate-500">ID: #${this.escapeHtml(item.id || '')}</span>
                        <span class="text-[11px] font-mono text-slate-400">(${pageLabel})</span>
                    </div>

                    <div class="flex items-center gap-2">
                        <button onclick="corpusManager.copyText('${this.escapeQuotes(item.source_raw)}')" title="Asliyatni nusxalash" class="p-1 text-slate-400 hover:text-indigo-600 transition">
                            <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                        </button>
                        <button onclick="corpusManager.speakText('${this.escapeQuotes(item.source_raw)}', '${lang === 'uz' ? 'uz-UZ' : 'en-US'}')" title="Tinglash" class="p-1 text-slate-400 hover:text-indigo-600 transition">
                            <i data-lucide="volume-2" class="w-3.5 h-3.5"></i>
                        </button>
                    </div>
                </div>

                <!-- Source Sentence with Highlighted Query Word Family -->
                <div>
                    <span class="text-[10px] font-bold uppercase tracking-wider text-indigo-600 block mb-1">
                        Asl matn (${lang === 'uz' ? 'O‘zbekcha' : 'Inglizcha'}):
                    </span>
                    <p class="text-sm text-slate-900 dark:text-slate-100 font-serif leading-relaxed">
                        ${item.source_highlighted}
                    </p>
                </div>

                <!-- Translation Sentence per TILCOR_04 / S3 Permanent Rules -->
                ${isConfirmed ? `
                    <div class="rounded-xl border border-emerald-200 dark:border-emerald-800 bg-emerald-50/40 dark:bg-emerald-950/30 p-3 space-y-1">
                        <div class="flex items-center gap-1.5 text-xs text-emerald-800 dark:text-emerald-300 font-semibold">
                            <i data-lucide="check-circle" class="w-3.5 h-3.5 shrink-0"></i>
                            <span>Tasdiqlangan tarjima</span>
                        </div>
                        <p class="text-xs text-slate-800 dark:text-slate-200 font-serif leading-relaxed pt-0.5">
                            ${item.target_highlighted || this.escapeHtml(item.target_raw || '')}
                        </p>
                    </div>
                ` : isMos ? `
                    <div class="rounded-xl border border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-950/40 p-3 space-y-1">
                        <div class="flex items-center justify-between">
                            <span class="flex items-center gap-1.5 text-xs text-amber-700 dark:text-amber-400 font-semibold">
                                <i data-lucide="info" class="w-3.5 h-3.5 shrink-0"></i>
                                <span>Avtomatik tekislangan — tekshirilmagan</span>
                            </span>
                            <span class="text-[10px] text-slate-400 font-mono">ikkala metod mos</span>
                        </div>
                        <p class="text-xs text-slate-800 dark:text-slate-200 font-serif leading-relaxed pt-0.5">
                            ${item.target_highlighted || this.escapeHtml(item.target_raw || '')}
                        </p>
                    </div>
                ` : `
                    <details class="rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-100/60 dark:bg-slate-950/40 p-3 space-y-1 group">
                        <summary class="flex items-center justify-between text-xs text-amber-700 dark:text-amber-400 font-semibold cursor-pointer">
                            <span class="flex items-center gap-1.5">
                                <i data-lucide="alert-triangle" class="w-3.5 h-3.5 shrink-0"></i>
                                <span>Tekislash ishonchi past</span>
                            </span>
                            <span class="text-[11px] text-slate-400 font-normal group-open:hidden">Ko‘rish uchun bosing</span>
                        </summary>
                        <p class="text-xs text-slate-600 dark:text-slate-400 font-serif italic leading-relaxed pt-2 border-t border-slate-200/50 dark:border-slate-800 mt-2">
                            ${item.target_highlighted || this.escapeHtml(item.target_raw || '')}
                        </p>
                    </details>
                `}
            </div>
        `;
    }

    renderPagination(pagination) {
        const { page, total_pages } = pagination;
        return `
            <div class="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-700/60 text-xs">
                <span class="text-slate-500">
                    Sahifa <strong class="font-mono text-slate-800 dark:text-white">${page}</strong> / <strong class="font-mono text-slate-800 dark:text-white">${total_pages}</strong>
                </span>
                <div class="flex items-center gap-1.5">
                    <button onclick="corpusManager.goToPage(${page - 1})" ${page <= 1 ? 'disabled class="opacity-40 cursor-not-allowed px-3 py-1.5 rounded-xl border border-slate-200"' : 'class="px-3 py-1.5 rounded-xl border border-slate-200 hover:bg-slate-100 dark:border-slate-700 font-semibold"'}>
                        ← Oldingi
                    </button>
                    <button onclick="corpusManager.goToPage(${page + 1})" ${page >= total_pages ? 'disabled class="opacity-40 cursor-not-allowed px-3 py-1.5 rounded-xl border border-slate-200"' : 'class="px-3 py-1.5 rounded-xl border border-slate-200 hover:bg-slate-100 dark:border-slate-700 font-semibold"'}>
                        Keyingi →
                    </button>
                </div>
            </div>
        `;
    }

    escapeHtml(text) {
        if (!text) return '';
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    escapeQuotes(text) {
        if (!text) return '';
        return String(text).replace(/'/g, "\\'").replace(/"/g, '&quot;').replace(/\n/g, ' ');
    }

    copyText(text) {
        navigator.clipboard.writeText(text).then(() => {
            if (window.app && window.app.showToast) {
                window.app.showToast("Nusxalandi!", "success");
            }
        });
    }

    speakText(text, lang) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = lang;
            window.speechSynthesis.speak(utterance);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.corpusManager = new CorpusManager();
});
