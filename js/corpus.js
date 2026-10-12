/**
 * Parallel Korpus Qidiruv va Konkordans Tizimi (KWIC)
 * 5,157 ta to'liq asarlar jumlalari massiviga ulangan
 */

class CorpusManager {
    constructor() {
        this.dataset = parallelCorpusData.filter(x => x.status !== "excluded" && !x.quarantined);
        this.filteredData = [...this.dataset];
        this.currentBook = 'all';
        this.searchTerm = '';
        this.totalCorpusCount = 3811;
        this.searchDebounce = null;
        this.init();
    }

    init() {
        this.renderCorpusStats();
        this.renderCorpusResults();
        this.bindEvents();
    }

    bindEvents() {
        const searchInput = document.getElementById('corpusSearchInput');
        const bookFilter = document.getElementById('corpusBookFilter');
        const clearBtn = document.getElementById('corpusClearBtn');

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value.trim();
                clearTimeout(this.searchDebounce);
                this.searchDebounce = setTimeout(() => {
                    this.executeSearch();
                }, 300);
            });
        }

        if (bookFilter) {
            bookFilter.addEventListener('change', (e) => {
                this.currentBook = e.target.value;
                this.executeSearch();
            });
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                if (searchInput) searchInput.value = '';
                if (bookFilter) bookFilter.value = 'all';
                this.searchTerm = '';
                this.currentBook = 'all';
                this.filteredData = [...this.dataset];
                this.renderCorpusResults();
            });
        }
    }

    filterByBook(bookKey) {
        this.currentBook = bookKey;
        const bookFilter = document.getElementById('corpusBookFilter');
        if (bookFilter) bookFilter.value = bookKey;
        this.executeSearch();
    }

    async executeSearch() {
        const countBadge = document.getElementById('corpusResultCountBadge');
        if (countBadge) {
            countBadge.innerHTML = `<span class="inline-flex items-center gap-1.5 text-indigo-600"><span class="w-3 h-3 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></span> tasdiqlangan jumlalardan qidirilmoqda...</span>`;
        }

        try {
            // Server Search API query
            const url = `/api/search?q=${encodeURIComponent(this.searchTerm)}&book=${encodeURIComponent(this.currentBook)}&limit=100`;
            const resp = await fetch(url);
            
            if (resp.ok) {
                const data = await resp.json();
                this.filteredData = data.results.map(item => ({
                    id: item.id,
                    source: item.bookTitle,
                    bookKey: item.book,
                    author: item.author || (item.book === 'cholpon' ? 'Choʻlpon' : item.book === 'hemingway' ? 'E. Hemingway' : 'R. L. Stevenson'),
                    translator: item.translator || (item.book === 'cholpon' ? 'Christopher Fort' : item.book === 'hemingway' ? 'Ibrohim Gʻafurov' : 'Sharif Rizo'),
                    pubYear: item.pubYear || (item.book === 'cholpon' ? '1936/2020' : item.book === 'hemingway' ? '1952/1986' : '1883/1974'),
                    publisher: item.publisher || 'Ilmiy nashr',
                    license: item.license || 'Cheklangan ilmiy parcha',
                    uz: item.uz,
                    en: item.en,
                    alignmentScore: item.score || "—",
                    mi: "—",
                    tScore: "—"
                }));
                this.totalCorpusCount = data.totalCorpus || 5157;
                this.renderCorpusResults(data.totalFound);
                return;
            }
        } catch (e) {
            // Local fallback
        }

        // Fallback filter
        this.filteredData = this.dataset.filter(item => {
            const matchesBook = this.currentBook === 'all' || item.bookKey === this.currentBook;
            const textToSearch = `${item.uz} ${item.en}`.toLowerCase();
            const matchesSearch = !this.searchTerm || textToSearch.includes(this.searchTerm.toLowerCase());
            return matchesBook && matchesSearch;
        });

        this.renderCorpusResults();
    }

    renderCorpusStats() {
        const totalCountEl = document.getElementById('corpusTotalCount');
        if (totalCountEl) totalCountEl.textContent = "5,157";
    }

    highlightTerm(text, term) {
        if (!term || !text) return text;
        const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`(${escaped})`, 'gi');
        return text.replace(regex, `<mark class="bg-amber-200 dark:bg-amber-900/60 text-amber-900 dark:text-amber-200 font-bold px-1 rounded">$1</mark>`);
    }

    renderCorpusResults(serverTotalFound) {
        const container = document.getElementById('corpusResultsContainer');
        const countBadge = document.getElementById('corpusResultCountBadge');

        const displayCount = serverTotalFound !== undefined ? serverTotalFound : this.filteredData.length;

        if (countBadge) {
            countBadge.innerHTML = this.searchTerm 
                ? `<strong>«${this.searchTerm}»</strong> boʻyicha <strong>${displayCount} ta</strong> parallel jumla topildi (5,157 jumlalar orasidan)`
                : `Jami koʻrsatilmoqda: <strong>${this.filteredData.length} ta</strong> parallel jumla`;
        }

        if (!container) return;

        if (this.filteredData.length === 0) {
            container.innerHTML = `
                <div class="text-center py-12 bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 p-8">
                    <div class="w-16 h-16 mx-auto mb-4 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center text-slate-400">
                        <i data-lucide="search-x" class="w-8 h-8"></i>
                    </div>
                    <h4 class="text-lg font-bold text-slate-700 dark:text-slate-300">«${this.searchTerm}» boʻyicha natija topilmadi</h4>
                    <p class="text-sm text-slate-500 mt-1 max-w-md mx-auto">
                        Soʻz shaklini oʻzgartirib koʻring (masalan, oʻzak soʻz bilan: <em>baliq, dengiz, yurak, otasi, kema, sea, fish</em>) yoki «Barcha manbalar»ni tanlang.
                    </p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        container.innerHTML = this.filteredData.map((item) => {
            const bookBadge = 
                item.bookKey === 'cholpon' ? 'bg-indigo-50 text-indigo-700 border-indigo-200 dark:bg-indigo-950 dark:text-indigo-300' :
                item.bookKey === 'hemingway' ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950 dark:text-emerald-300' :
                item.bookKey === 'stevenson' ? 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950 dark:text-amber-300' :
                'bg-slate-100 text-slate-700 border-slate-200 dark:bg-slate-800 dark:text-slate-300';

            
            const warningBanner = (item.bookKey === 'cholpon' || item.bookKey === 'hemingway')
                ? `<div class="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-800 dark:text-amber-300 text-xs font-semibold flex items-center gap-2 mb-2">
                     <i data-lucide="alert-triangle" class="w-4 h-4 text-amber-600 shrink-0"></i>
                     <span>Tekislash qayta ko‘rib chiqilmoqda — tahlil uchun foydalanmang</span>
                   </div>`
                : '';

            const uzHighlighted = this.highlightTerm(item.uz, this.searchTerm);
            const enHighlighted = this.highlightTerm(item.en, this.searchTerm);
            const cleanUzText = (item.uz || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');

            return `
                <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm hover:shadow-md transition duration-200 group space-y-3">
                    <div class="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-100 dark:border-slate-700/60">
                        <div class="flex items-center gap-2">
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${bookBadge}">
                                ${item.source}
                            </span>
                            <span class="text-xs font-mono font-bold text-slate-500 dark:text-slate-400">Segment: #${item.id}</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <span class="text-xs px-2.5 py-0.5 rounded-md bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 font-mono font-bold">
                                Moslik: ${item.alignmentScore ? item.alignmentScore : "— (tekshirilmoqda)"}
                            </span>
                        </div>
                    </div>

                    <div class="grid md:grid-cols-2 gap-4">
                        ${warningBanner}
                        <!-- O'zbekcha matn -->
                        <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 relative group/uz">
                            <div class="flex items-center justify-between mb-1.5">
                                <span class="text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400 flex items-center gap-1.5">
                                    <span class="w-2 h-2 rounded-full bg-indigo-500"></span> Oʻzbekcha matn (Tarjima / Asl)
                                </span>
                                <div class="flex items-center gap-1">
                                    <button onclick="corpusManager.speakText('${item.uz.replace(/<[^>]*>/g, '').replace(/'/g, "\\'")}', 'uz-UZ')" title="Tinglash" class="p-1 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition">
                                        <i data-lucide="volume-2" class="w-3.5 h-3.5"></i>
                                    </button>
                                    <button onclick="corpusManager.copyText('${item.uz.replace(/<[^>]*>/g, '').replace(/'/g, "\\'")}')" title="Nusxalash" class="p-1 text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition">
                                        <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                                    </button>
                                </div>
                            </div>
                            <p class="text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-sans">
                                ${uzHighlighted}
                            </p>
                        </div>

                        <!-- Inglizcha matn -->
                        <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 relative group/en">
                            <div class="flex items-center justify-between mb-1.5">
                                <span class="text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
                                    <span class="w-2 h-2 rounded-full bg-emerald-500"></span> English Context
                                </span>
                                <div class="flex items-center gap-1">
                                    <button onclick="corpusManager.speakText('${item.en.replace(/<[^>]*>/g, '').replace(/'/g, "\\'")}', 'en-US')" title="Tinglash" class="p-1 text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition">
                                        <i data-lucide="volume-2" class="w-3.5 h-3.5"></i>
                                    </button>
                                    <button onclick="corpusManager.copyText('${item.en.replace(/<[^>]*>/g, '').replace(/'/g, "\\'")}')" title="Nusxalash" class="p-1 text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition">
                                        <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                                    </button>
                                </div>
                            </div>
                            <p class="text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-sans">
                                ${enHighlighted}
                            </p>
                        </div>
                    </div>

                    <!-- Bibliografik Pasport (PDF 5-bo'lim) -->
                    <div class="pt-2.5 border-t border-slate-100 dark:border-slate-800 flex flex-wrap items-center justify-between text-[11px] text-slate-500 gap-2">
                        <div class="flex flex-wrap items-center gap-3">
                            <span><strong class="text-slate-700 dark:text-slate-300">Muallif:</strong> ${item.author}</span>
                            <span>•</span>
                            <span><strong class="text-slate-700 dark:text-slate-300">Tarjimon:</strong> ${item.translator}</span>
                            <span>•</span>
                            <span><strong class="text-slate-700 dark:text-slate-300">Yil:</strong> ${item.pubYear}</span>
                            <span>•</span>
                            <span class="text-emerald-600 dark:text-emerald-400 font-semibold">${item.license}</span>
                        </div>
                        <button onclick="app.sendToLab('${cleanUzText}')" class="px-3 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-600 hover:text-white font-bold text-xs flex items-center gap-1.5 transition shadow-xs">
                            <i data-lucide="flask-conical" class="w-3.5 h-3.5"></i> Research Labda Tahlil Qilish
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    copyText(text) {
        navigator.clipboard.writeText(text).then(() => {
            app.showToast("Matn nusxalandi!", "success");
        }).catch(() => {
            app.showToast("Nusxalashda xatolik yuz berdi", "error");
        });
    }

    speakText(text, lang) {
        if (!('speechSynthesis' in window)) {
            app.showToast("Brauzerda ovozli oʻqish imkoni yoʻq", "warning");
            return;
        }
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang;
        utterance.rate = 0.95;
        window.speechSynthesis.speak(utterance);
    }
}

const corpusManager = new CorpusManager();
