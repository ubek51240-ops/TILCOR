/**
 * TILCOR — Akademik Elektron Lug'at Moduli
 * Manba: 80,000 so‘zli Katta Lug‘at (881 bet) & 816 betlik Lug‘at (BuxDU kutubxonasi)
 * Faqat toza leksikografik maqolalar ko'rsatiladi. Barcha to'qima misollar olib tashlangan.
 */

class DictionaryManager {
    constructor() {
        this.searchTerm = '';
        this.results = [];
        this.debounceTimer = null;
        this.totalCount = 0;
        this.quickWords = ['book', 'accept', 'ability', 'active', 'anchor', 'ocean', 'decision', 'water', 'deep', 'peace', 'storm', 'courage'];
        this.init();
    }

    init() {
        this.bindEvents();
        this.renderQuickWords();
        this.search('');
    }

    bindEvents() {
        const searchInput = document.getElementById('dictSearchInput');
        const clearBtn = document.getElementById('dictClearBtn');

        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchTerm = e.target.value.trim();
                clearTimeout(this.debounceTimer);
                this.debounceTimer = setTimeout(() => {
                    this.search(this.searchTerm);
                }, 250);
            });
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                if (searchInput) searchInput.value = '';
                this.searchTerm = '';
                this.search('');
            });
        }
    }

    renderQuickWords() {
        const container = document.getElementById('dictQuickWords');
        if (!container) return;

        container.innerHTML = this.quickWords.map(w => `
            <button onclick="dictionaryManager.setSearch('${w}')" class="px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-700/60 hover:bg-indigo-50 dark:hover:bg-indigo-950 text-slate-700 dark:text-slate-300 text-xs font-mono transition">
                ${w}
            </button>
        `).join('');
    }

    setSearch(word) {
        const searchInput = document.getElementById('dictSearchInput');
        if (searchInput) searchInput.value = word;
        this.searchTerm = word;
        this.search(word);
    }

    async search(query) {
        const resultsContainer = document.getElementById('dictResultsContainer');
        const countBadge = document.getElementById('dictResultCount');

        if (countBadge) {
            countBadge.innerHTML = `<span class="inline-flex items-center gap-1.5 text-indigo-600"><span class="w-3 h-3 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></span> Lugʻatdan qidirilmoqda...</span>`;
        }

        try {
            const resp = await fetch(`/api/dictionary?q=${encodeURIComponent(query)}&limit=50`);
            if (resp.ok) {
                const data = await resp.json();
                this.results = data.results || [];
                this.totalCount = data.totalDictionary || this.results.length;
                if (countBadge) {
                    countBadge.innerHTML = query 
                        ? `<strong>«${query}»</strong> boʻyicha <strong>${data.totalFound} ta</strong> soʻz topildi`
                        : `Lugʻatdan tanlangan soʻzlar: <strong>${this.results.length} ta</strong> (Jami toza maqolalar: ${this.totalCount.toLocaleString()} ta)`;
                }
                const dictTotalEl = document.getElementById('dictTotalCountHeader');
                if (dictTotalEl) dictTotalEl.textContent = this.totalCount.toLocaleString();
                this.renderResults();
                return;
            }
        } catch (e) {
            console.error("Dictionary error:", e);
        }

        this.renderResults();
    }

    renderResults() {
        const container = document.getElementById('dictResultsContainer');
        if (!container) return;

        if (this.results.length === 0) {
            container.innerHTML = `
                <div class="col-span-full text-center py-12 bg-white dark:bg-slate-800 rounded-3xl border border-slate-200 dark:border-slate-700 p-8">
                    <div class="w-16 h-16 mx-auto mb-4 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center text-slate-400">
                        <i data-lucide="book-x" class="w-8 h-8"></i>
                    </div>
                    <h4 class="text-lg font-bold text-slate-700 dark:text-slate-300">«${this.searchTerm}» soʻzi lugʻatda topilmadi</h4>
                    <p class="text-sm text-slate-500 mt-1">Soʻz yozilishini tekshirib, qayta qidirib koʻring.</p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        container.innerHTML = this.results.map(item => `
            <div class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-4 shadow-sm hover:shadow-md transition flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between gap-2 mb-2 pb-2 border-b border-slate-100 dark:border-slate-700/60">
                        <div class="flex items-center gap-2">
                            <h4 class="text-base font-extrabold text-slate-900 dark:text-white capitalize">${item.word}</h4>
                            ${item.pos ? `<span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-bold">${item.pos}</span>` : ''}
                        </div>
                        <span class="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 border border-emerald-200/60">
                            Bosma Lugʻat
                        </span>
                    </div>

                    <p class="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-sans mt-1">
                        ${item.translation}
                    </p>

                    <div class="mt-2.5 text-[10px] text-slate-400 font-mono flex items-center justify-between">
                        <span>${item.source || "Bosma lug'at fondi"}</span>
                        ${item.page80k ? `<span>~${item.page80k}-bet</span>` : ''}
                    </div>
                </div>

                <div class="flex items-center justify-between pt-3 mt-2 border-t border-slate-100 dark:border-slate-700/60">
                    <button onclick="dictionaryManager.speakWord('${item.word.replace(/'/g, "\\'")}')" class="p-1.5 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-slate-100 dark:hover:bg-slate-700 transition" title="Talaffuz">
                        <i data-lucide="volume-2" class="w-3.5 h-3.5"></i>
                    </button>
                    <button onclick="navigator.clipboard.writeText('${item.word}: ${item.translation.replace(/'/g, "\\'")}'); if (window.app && window.app.showToast) app.showToast('Nusxalandi!', 'success');" class="text-[11px] text-slate-500 hover:text-indigo-600 flex items-center gap-1 transition">
                        <i data-lucide="copy" class="w-3 h-3"></i> Nusxalash
                    </button>
                </div>
            </div>
        `).join('');

        if (window.lucide) lucide.createIcons();
    }

    speakWord(word) {
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.lang = 'en-US';
        utterance.rate = 0.9;
        window.speechSynthesis.speak(utterance);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.dictionaryManager = new DictionaryManager();
});
