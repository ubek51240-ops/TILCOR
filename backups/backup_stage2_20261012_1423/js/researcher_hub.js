/**
 * Researcher Annotation & KWIC Concordance Hub (PhD Gate 6)
 * Real korpusdagi kollokatsiya qo'llanilishlari, KWIC va 7 parametrli ilmiy annotatsiya
 */

class ResearcherHub {
    constructor() {
        this.activeTab = 'occurrences'; // 'occurrences' | 'kwic'
        this.currentQuery = '';
        this.currentBook = 'all';
        this.currentPattern = 'all';
        this.currentSemantic = 'all';
        this.currentEquivalence = 'all';
        this.page = 1;
        this.limit = 25;
        this.totalOccurrences = 0;
        this.selectedOccurrence = null;
        
        this.kwicKeyword = '';
        this.kwicWindow = 6;
        
        this.init();
    }

    init() {
        this.renderHubUI();
        this.bindEvents();
        this.loadOccurrences();
    }

    renderHubUI() {
        const container = document.getElementById('phdResearcherHubContainer');
        if (!container) return;

        container.innerHTML = `
            <div class="bg-slate-900/90 border border-slate-700/80 rounded-2xl p-4 sm:p-6 shadow-2xl backdrop-blur-xl mb-6">
                <!-- Yuqori Tab Paneli -->
                <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4 mb-5">
                    <div class="flex items-center gap-2">
                        <button id="tabBtnOccurrences" class="px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 bg-indigo-600 text-white shadow-lg shadow-indigo-500/25">
                            <span>🔍 Real Korpus Qo'llanilishlari</span>
                            <span id="occCountBadge" class="bg-indigo-900/80 text-indigo-200 text-xs px-2 py-0.5 rounded-full">469 ta</span>
                        </button>
                        <button id="tabBtnKwic" class="px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 bg-slate-800 text-slate-300 hover:bg-slate-700">
                            <span>📑 KWIC Konkordans Dasturi</span>
                            <span class="bg-slate-700 text-slate-300 text-xs px-2 py-0.5 rounded-full">19,505 jumla</span>
                        </button>
                    </div>

                    <!-- Eksport Tugmasi -->
                    <div class="flex items-center gap-2">
                        <a href="/api/export?type=occurrences" download="phd_collocation_occurrences.csv" class="px-3.5 py-2 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 rounded-xl text-xs font-medium flex items-center gap-1.5 transition-all">
                            <span>📥</span>
                            <span>Eksport (CSV/Excel)</span>
                        </a>
                    </div>
                </div>

                <!-- 1. OCCURRENCES SECTION -->
                <div id="sectionOccurrences" class="space-y-4">
                    <!-- Filtrlar qatori -->
                    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
                        <div class="lg:col-span-1">
                            <label class="block text-xs text-slate-400 mb-1">Izlash (so'z, jumla)</label>
                            <input type="text" id="occSearchInput" placeholder="Masalan: deep wrinkles, qiz..." 
                                class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500">
                        </div>
                        <div>
                            <label class="block text-xs text-slate-400 mb-1">Manba Kitob</label>
                            <select id="occBookFilter" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500">
                                <option value="all">Barcha kitoblar (4 ta)</option>
                                <option value="book-cholpon-uz">Cho'lpon: «Kecha va kunduz» (UZ)</option>
                                <option value="book-cholpon-en">Cho'lpon: «Night and Day» (EN)</option>
                                <option value="book-hemingway-en">Hemingway: «The Old Man and the Sea»</option>
                                <option value="book-hemingway-uz">Hemingway: «Chol va dengiz»</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs text-slate-400 mb-1">Grammatik Model (3.1)</label>
                            <select id="occPatternFilter" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500">
                                <option value="all">Barcha modellar</option>
                                <option value="Sifat + Ot">Sifat + Ot (Adj + Noun)</option>
                                <option value="Feʼl + Ot">Fe'l + Ot (Verb + Noun)</option>
                                <option value="Ravish + Sifat">Ravish + Sifat (Adv + Adj)</option>
                                <option value="Feʼl + Ravish">Fe'l + Ravish (Verb + Adv)</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs text-slate-400 mb-1">Semantik Guruh (3.1)</label>
                            <select id="occSemanticFilter" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500">
                                <option value="all">Barcha guruhlar</option>
                                <option value="Tabiat">Tabiat va borliq</option>
                                <option value="Ijtimoiy">Ijtimoiy munosabatlar</option>
                                <option value="Ilmiy">Ilmiy-akademik</option>
                                <option value="Hissiyot">Hissiyot va ruhiy</option>
                                <option value="Harakat">Harakat va holat</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs text-slate-400 mb-1">Ekvivalentlik (3.2)</label>
                            <select id="occEquivalenceFilter" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500">
                                <option value="all">Barchasi</option>
                                <option value="Toʻliq">To'liq ekvivalent</option>
                                <option value="Transformatsiya">Transformatsiya</option>
                            </select>
                        </div>
                    </div>

                    <!-- Natijalar Ro'yxati -->
                    <div id="occResultsList" class="space-y-3 min-h-[200px]">
                        <div class="text-center py-10 text-slate-500 text-sm">Yuklanmoqda...</div>
                    </div>

                    <!-- Pagination -->
                    <div id="occPagination" class="flex items-center justify-between pt-2 border-t border-slate-800 text-xs text-slate-400">
                        <span id="occPageInfo">Sahifa 1</span>
                        <div class="flex items-center gap-1.5">
                            <button id="occPrevBtn" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-40">Oldingi</button>
                            <button id="occNextBtn" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 disabled:opacity-40">Keyingi</button>
                        </div>
                    </div>
                </div>

                <!-- 2. KWIC SECTION -->
                <div id="sectionKwic" class="space-y-4 hidden">
                    <div class="flex flex-wrap items-center gap-3 bg-slate-950/60 p-3.5 rounded-xl border border-slate-800">
                        <div class="flex-1 min-w-[200px]">
                            <label class="block text-xs text-slate-400 mb-1">Kalit so'z (Keyword)</label>
                            <input type="text" id="kwicKeywordInput" placeholder="Masalan: wrinkles, bahor, fish, sea, ko'ngil..." 
                                class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500">
                        </div>
                        <div class="w-36">
                            <label class="block text-xs text-slate-400 mb-1">Kontekst kengligi</label>
                            <select id="kwicWindowSelect" class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2 py-1.5 text-xs text-white focus:outline-none">
                                <option value="4">4 so'z</option>
                                <option value="6" selected>6 so'z</option>
                                <option value="8">8 so'z</option>
                                <option value="10">10 so'z</option>
                            </select>
                        </div>
                        <div class="self-end">
                            <button id="kwicSearchBtn" class="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow">
                                Qidirish
                            </button>
                        </div>
                    </div>

                    <!-- KWIC Konkordans Jadvali -->
                    <div class="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/80">
                        <table class="w-full text-xs">
                            <thead class="bg-slate-900 text-slate-400 font-semibold border-b border-slate-800">
                                <tr>
                                    <th class="py-2 px-3 text-right w-[42%]">Chap Kontekst (Left Span)</th>
                                    <th class="py-2 px-2 text-center w-[16%] text-indigo-300">Kalit So'z</th>
                                    <th class="py-2 px-3 text-left w-[42%]">O'ng Kontekst (Right Span)</th>
                                    <th class="py-2 px-3 text-center whitespace-nowrap">Manba / Bet</th>
                                </tr>
                            </thead>
                            <tbody id="kwicTableBody" class="divide-y divide-slate-800/60 font-mono">
                                <tr>
                                    <td colspan="4" class="text-center py-8 text-slate-500 font-sans">
                                        Kalit so'z kiritib, «Qidirish» tugmasini bosing (19,505 ta segment ichidan qidiriladi).
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- 3. RESEARCHER 7-FIELD ANNOTATION MODAL -->
            <div id="annotationModal" class="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md hidden flex items-center justify-center p-4">
                <div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full p-5 sm:p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
                    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                        <div class="flex items-center gap-2">
                            <span class="p-2 bg-indigo-500/20 text-indigo-400 rounded-lg text-base">✏️</span>
                            <div>
                                <h3 class="text-base font-bold text-white">Tadqiqotchi Ilmiy Annotatsiyasi (PhD Hub)</h3>
                                <p class="text-xs text-slate-400">II va III boblar bo'yicha ilmiy tasniflash va qaydlar kiritish</p>
                            </div>
                        </div>
                        <button id="modalCloseBtn" class="text-slate-400 hover:text-white text-lg">&times;</button>
                    </div>

                    <!-- Tanlangan birikma konteksti -->
                    <div id="modalContextBox" class="bg-slate-950/70 p-3 rounded-xl border border-slate-800 text-xs space-y-1.5 font-mono">
                    </div>

                    <!-- 7-PARAMETRLI FORMA -->
                    <form id="annotationForm" class="space-y-3 text-xs">
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <div>
                                <label class="block text-slate-300 font-medium mb-1">1. Grammatik Model (3.1-bob)</label>
                                <select id="annPattern" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white">
                                    <option value="Sifat + Ot (Adj + Noun)">Sifat + Ot (Adj + Noun)</option>
                                    <option value="Feʼl + Ot (Verb + Noun)">Fe'l + Ot (Verb + Noun)</option>
                                    <option value="Ot + Ot (Noun + Noun)">Ot + Ot (Noun + Noun)</option>
                                    <option value="Feʼl + Ravish (Verb + Adv)">Fe'l + Ravish (Verb + Adv)</option>
                                    <option value="Ravish + Sifat (Adv + Adj)">Ravish + Sifat (Adv + Adj)</option>
                                    <option value="Ot + Feʼl (Noun + Verb)">Ot + Fe'l (Noun + Verb)</option>
                                </select>
                            </div>

                            <div>
                                <label class="block text-slate-300 font-medium mb-1">2. Semantik Guruh (3.1-bob)</label>
                                <select id="annSemantic" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white">
                                    <option value="Tabiat, muhit va borliq hodisalari">Tabiat, muhit va borliq hodisalari</option>
                                    <option value="Ijtimoiy munosabatlar va jamiyat">Ijtimoiy munosabatlar va jamiyat</option>
                                    <option value="Ilmiy-akademik va mantiqiy munosabatlar">Ilmiy-akademik va mantiqiy munosabatlar</option>
                                    <option value="Hissiyot va ruhiy kechinmalar">Hissiyot va ruhiy kechinmalar</option>
                                    <option value="Harakat va jismoniy holat">Harakat va jismoniy holat</option>
                                    <option value="Nutq, muloqot va tafakkur">Nutq, muloqot va tafakkur</option>
                                    <option value="Tana a’zolari va tashqi koʻrinish">Tana a’zolari va tashqi koʻrinish</option>
                                </select>
                            </div>

                            <div>
                                <label class="block text-slate-300 font-medium mb-1">3. Ekvivalentlik Turi (3.2-bob)</label>
                                <select id="annEquivalence" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white">
                                    <option value="Mos ekvivalent (Toʻliq ekvivalent)">Toʻliq ekvivalent</option>
                                    <option value="Qisman ekvivalent">Qisman ekvivalent</option>
                                    <option value="Kontekstual muqobil">Kontekstual muqobil</option>
                                    <option value="Transformatsiya (Leksik-grammatik almashtirish)">Transformatsiya</option>
                                </select>
                            </div>

                            <div>
                                <label class="block text-slate-300 font-medium mb-1">4. Tarjima Strategiyasi</label>
                                <select id="annStrategy" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white">
                                    <option value="direct_adequate">Toʻgʻridan-toʻgʻri adekvat tarjima</option>
                                    <option value="lexical_substitution">Leksik oʻrin almashish</option>
                                    <option value="descriptive_paraphrase">Tasviriy / tavsifiy tarjima</option>
                                    <option value="calque_corrected">Kalka tuzatilgan adekvat shakl</option>
                                    <option value="omission">Kontekstual tushirib qoldirish</option>
                                </select>
                            </div>
                        </div>

                        <div class="flex items-center gap-4 py-1">
                            <label class="flex items-center gap-2 cursor-pointer text-slate-300">
                                <input type="checkbox" id="annLingvocultural" class="rounded bg-slate-950 border-slate-700 text-indigo-600 focus:ring-0">
                                <span>5. Lingvomadaniy konnotatsiyaga ega (3.3-bob milliy xususiyat)</span>
                            </label>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <div>
                                <label class="block text-slate-300 font-medium mb-1">6. Verifikatsiya Holati</label>
                                <select id="annVerified" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white">
                                    <option value="1">✅ Tasdiqlangan (Human Verified)</option>
                                    <option value="0">⏳ Kutilmoqda (Draft / Unreviewed)</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-slate-300 font-medium mb-1">Tadqiqotchi F.I.Sh.</label>
                                <input type="text" id="annResearcherName" value="PhD Izlanuvchi" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white">
                            </div>
                        </div>

                        <div>
                            <label class="block text-slate-300 font-medium mb-1">7. Ilmiy Izoh & Tahliliy Xulosa (Dissertatsiya uchun)</label>
                            <textarea id="annScientificNote" rows="3" placeholder="Ushbu kollokatsiyaning korpusdagi uslubiy, semantik yoki madaniy xususiyatlari..."
                                class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-white focus:outline-none focus:border-indigo-500"></textarea>
                        </div>

                        <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
                            <button type="button" id="modalCancelBtn" class="px-3.5 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700">Bekor qilish</button>
                            <button type="submit" id="modalSaveBtn" class="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold shadow">💾 Saqlash va Muhrlash</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
    }

    bindEvents() {
        // Tab switching
        const btnOcc = document.getElementById('tabBtnOccurrences');
        const btnKwic = document.getElementById('tabBtnKwic');
        const secOcc = document.getElementById('sectionOccurrences');
        const secKwic = document.getElementById('sectionKwic');

        if (btnOcc && btnKwic) {
            btnOcc.addEventListener('click', () => {
                this.activeTab = 'occurrences';
                btnOcc.className = 'px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 bg-indigo-600 text-white shadow-lg shadow-indigo-500/25';
                btnKwic.className = 'px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 bg-slate-800 text-slate-300 hover:bg-slate-700';
                secOcc.classList.remove('hidden');
                secKwic.classList.add('hidden');
            });

            btnKwic.addEventListener('click', () => {
                this.activeTab = 'kwic';
                btnKwic.className = 'px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 bg-indigo-600 text-white shadow-lg shadow-indigo-500/25';
                btnOcc.className = 'px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-2 bg-slate-800 text-slate-300 hover:bg-slate-700';
                secKwic.classList.remove('hidden');
                secOcc.classList.add('hidden');
            });
        }

        // Filters
        const sInput = document.getElementById('occSearchInput');
        if (sInput) {
            let timer;
            sInput.addEventListener('input', (e) => {
                clearTimeout(timer);
                timer = setTimeout(() => {
                    this.currentQuery = e.target.value.trim();
                    this.page = 1;
                    this.loadOccurrences();
                }, 300);
            });
        }

        ['occBookFilter', 'occPatternFilter', 'occSemanticFilter', 'occEquivalenceFilter'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('change', () => {
                    if (id === 'occBookFilter') this.currentBook = el.value;
                    if (id === 'occPatternFilter') this.currentPattern = el.value;
                    if (id === 'occSemanticFilter') this.currentSemantic = el.value;
                    if (id === 'occEquivalenceFilter') this.currentEquivalence = el.value;
                    this.page = 1;
                    this.loadOccurrences();
                });
            }
        });

        // Pagination
        const prevBtn = document.getElementById('occPrevBtn');
        const nextBtn = document.getElementById('occNextBtn');
        if (prevBtn) prevBtn.addEventListener('click', () => { if (this.page > 1) { this.page--; this.loadOccurrences(); } });
        if (nextBtn) nextBtn.addEventListener('click', () => { this.page++; this.loadOccurrences(); });

        // KWIC search
        const kwicBtn = document.getElementById('kwicSearchBtn');
        const kwicInput = document.getElementById('kwicKeywordInput');
        if (kwicBtn && kwicInput) {
            kwicBtn.addEventListener('click', () => this.searchKwic());
            kwicInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') this.searchKwic(); });
        }

        // Modal close
        const closeBtn = document.getElementById('modalCloseBtn');
        const cancelBtn = document.getElementById('modalCancelBtn');
        const modal = document.getElementById('annotationModal');
        if (closeBtn) closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
        if (cancelBtn) cancelBtn.addEventListener('click', () => modal.classList.add('hidden'));

        // Form submit
        const form = document.getElementById('annotationForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveAnnotation();
            });
        }
    }

    async loadOccurrences() {
        const listContainer = document.getElementById('occResultsList');
        if (!listContainer) return;
        listContainer.innerHTML = '<div class="text-center py-8 text-slate-500 text-xs">Yuklanmoqda...</div>';

        const params = new URLSearchParams({
            q: this.currentQuery,
            book: this.currentBook,
            pattern: this.currentPattern,
            semantic: this.currentSemantic,
            equivalence: this.currentEquivalence,
            page: this.page,
            limit: this.limit
        });

        try {
            const resp = await fetch(`/api/occurrences?${params.toString()}`);
            const data = await resp.json();
            if (!data.success) throw new Error(data.error);

            this.totalOccurrences = data.total;
            const badge = document.getElementById('occCountBadge');
            if (badge) badge.innerText = `${data.total} ta`;

            const pageInfo = document.getElementById('occPageInfo');
            if (pageInfo) pageInfo.innerText = `${data.total} tadan ${(this.page-1)*this.limit + 1}–${Math.min(this.page*this.limit, data.total)} ko'rsatilmoqda (Sahifa ${this.page})`;

            const prevBtn = document.getElementById('occPrevBtn');
            const nextBtn = document.getElementById('occNextBtn');
            if (prevBtn) prevBtn.disabled = this.page <= 1;
            if (nextBtn) nextBtn.disabled = this.page * this.limit >= data.total;

            if (data.results.length === 0) {
                listContainer.innerHTML = '<div class="text-center py-8 text-slate-500 text-xs">Hech qanday qo\'llanish topilmadi.</div>';
                return;
            }

            listContainer.innerHTML = data.results.map(item => this.renderOccurrenceCard(item)).join('');

            // Attach event listener to edit buttons
            data.results.forEach(item => {
                const btn = document.getElementById(`editBtn_${item.id}`);
                if (btn) {
                    btn.addEventListener('click', () => this.openAnnotationModal(item));
                }
            });

        } catch (err) {
            listContainer.innerHTML = `<div class="text-center py-8 text-rose-400 text-xs">Xatolik yuz berdi: ${err.message}</div>`;
        }
    }

    renderOccurrenceCard(item) {
        const isVerified = item.is_verified === 1;
        const verifiedBadge = isVerified 
            ? `<span class="bg-emerald-500/20 text-emerald-300 text-[10px] px-2 py-0.5 rounded-full border border-emerald-500/30">✅ Tasdiqlangan</span>`
            : `<span class="bg-amber-500/20 text-amber-300 text-[10px] px-2 py-0.5 rounded-full border border-amber-500/30">⏳ Kutilmoqda</span>`;

        // Highlight matched span in sentences
        let srcTxt = item.source_text || '';
        let tgtTxt = item.target_text || '';
        if (item.matched_span_en) {
            const re = new RegExp(`(${item.matched_span_en})`, 'gi');
            srcTxt = srcTxt.replace(re, '<mark class="bg-indigo-500/30 text-indigo-200 px-1 rounded font-semibold">$1</mark>');
            tgtTxt = tgtTxt.replace(re, '<mark class="bg-indigo-500/30 text-indigo-200 px-1 rounded font-semibold">$1</mark>');
        }

        return `
            <div class="bg-slate-950/70 border border-slate-800 hover:border-slate-700/80 rounded-xl p-4 transition-all space-y-3">
                <div class="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/60 pb-2.5">
                    <div class="flex items-center gap-2 flex-wrap">
                        <span class="text-white font-bold text-sm tracking-wide">${item.surface_form_en}</span>
                        <span class="text-slate-500">⇄</span>
                        <span class="text-indigo-300 font-semibold text-sm">${item.surface_form_uz}</span>
                        ${verifiedBadge}
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-[11px] text-slate-400 font-mono bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                            📖 ${item.book_title} (PDF: ${item.pdf_page_num}-bet)
                        </span>
                        <button id="editBtn_${item.id}" class="px-2.5 py-1 bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 rounded-lg text-xs font-medium transition-all flex items-center gap-1">
                            <span>✏️</span>
                            <span>Annotatsiya</span>
                        </button>
                    </div>
                </div>

                <!-- Kontekst jumlalari -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs bg-slate-900/60 p-3 rounded-lg border border-slate-800/80 font-mono">
                    <div>
                        <span class="text-[10px] text-slate-400 block mb-1 uppercase font-sans">Asl matn / Manba:</span>
                        <p class="text-slate-200 leading-relaxed">${srcTxt}</p>
                    </div>
                    <div>
                        <span class="text-[10px] text-slate-400 block mb-1 uppercase font-sans">Tarjima matn:</span>
                        <p class="text-slate-300 leading-relaxed">${tgtTxt}</p>
                    </div>
                </div>

                <!-- Ilmiy parametrlar satri -->
                <div class="flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-400 pt-1">
                    <div class="flex items-center gap-3 flex-wrap">
                        <span>Model: <b class="text-slate-200">${item.grammatical_pattern || 'Sifat + Ot'}</b></span>
                        <span>•</span>
                        <span>Semantika: <b class="text-slate-200">${item.semantic_group || 'Umumiy'}</b></span>
                        <span>•</span>
                        <span>Ekvivalentlik: <b class="text-slate-200">${item.equivalence_type || 'Toʻliq'}</b></span>
                    </div>
                    <div class="flex items-center gap-2 font-mono text-[10px] text-slate-500">
                        <span>MI: <b>${item.mi_score || 6.5}</b></span>
                        <span>T-Score: <b>${item.t_score || 8.0}</b></span>
                    </div>
                </div>

                ${item.annotation && item.annotation.scientific_note ? `
                    <div class="text-[11px] bg-indigo-950/30 border border-indigo-900/40 text-indigo-200 p-2 rounded-lg">
                        <b>📝 Tadqiqotchi qaydi (${item.annotation.annotator_name || 'Izlanuvchi'}):</b> ${item.annotation.scientific_note}
                    </div>
                ` : ''}
            </div>
        `;
    }

    openAnnotationModal(item) {
        this.selectedOccurrence = item;
        const modal = document.getElementById('annotationModal');
        const box = document.getElementById('modalContextBox');
        if (!modal || !box) return;

        box.innerHTML = `
            <div class="flex justify-between items-center text-slate-400 border-b border-slate-800 pb-1 mb-1.5">
                <span>ID: <b class="text-white">${item.id}</b></span>
                <span>Kitob: <b class="text-white">${item.book_title} (${item.pdf_page_num}-bet)</b></span>
            </div>
            <div><b>EN:</b> ${item.source_text}</div>
            <div><b>UZ:</b> ${item.target_text}</div>
            <div class="text-amber-300 pt-1"><b>Aniq qamrov:</b> "${item.matched_span_en}" ⇄ "${item.matched_span_uz}"</div>
        `;

        document.getElementById('annPattern').value = item.grammatical_pattern || 'Sifat + Ot (Adj + Noun)';
        document.getElementById('annSemantic').value = item.semantic_group || 'Tabiat, muhit va borliq hodisalari';
        document.getElementById('annEquivalence').value = item.equivalence_type || 'Mos ekvivalent (Toʻliq ekvivalent)';
        document.getElementById('annStrategy').value = item.translation_strategy || 'direct_adequate';
        document.getElementById('annLingvocultural').checked = item.is_lingvocultural === 1;
        document.getElementById('annVerified').value = item.is_verified || '1';
        document.getElementById('annScientificNote').value = (item.annotation && item.annotation.scientific_note) ? item.annotation.scientific_note : (item.cultural_note || '');

        modal.classList.remove('hidden');
    }

    async saveAnnotation() {
        if (!this.selectedOccurrence) return;
        const saveBtn = document.getElementById('modalSaveBtn');
        if (saveBtn) { saveBtn.innerText = 'Saqlanmoqda...'; saveBtn.disabled = true; }

        const payload = {
            occurrence_id: this.selectedOccurrence.id,
            grammatical_pattern: document.getElementById('annPattern').value,
            semantic_group: document.getElementById('annSemantic').value,
            equivalence_type: document.getElementById('annEquivalence').value,
            translation_strategy: document.getElementById('annStrategy').value,
            is_lingvocultural: document.getElementById('annLingvocultural').checked ? 1 : 0,
            is_verified: parseInt(document.getElementById('annVerified').value),
            annotator_name: document.getElementById('annResearcherName').value.trim() || 'PhD Izlanuvchi',
            scientific_note: document.getElementById('annScientificNote').value.trim()
        };

        try {
            const resp = await fetch('/api/annotate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();
            if (!data.success) throw new Error(data.error);

            // Close modal and refresh list
            document.getElementById('annotationModal').classList.add('hidden');
            await this.loadOccurrences();
        } catch (err) {
            alert('Xatolik: ' + err.message);
        } finally {
            if (saveBtn) { saveBtn.innerText = '💾 Saqlash va Muhrlash'; saveBtn.disabled = false; }
        }
    }

    async searchKwic() {
        const input = document.getElementById('kwicKeywordInput');
        const tbody = document.getElementById('kwicTableBody');
        const winSelect = document.getElementById('kwicWindowSelect');
        if (!input || !tbody) return;

        const kw = input.value.trim();
        if (!kw) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center py-6 text-slate-500 font-sans text-xs">Kalit so\'zni kiriting.</td></tr>';
            return;
        }

        tbody.innerHTML = '<tr><td colspan="4" class="text-center py-6 text-slate-500 font-sans text-xs">Qidirilmoqda...</td></tr>';

        try {
            const resp = await fetch(`/api/kwic?q=${encodeURIComponent(kw)}&window=${winSelect.value}&limit=60`);
            const data = await resp.json();

            if (!data.success || data.results.length === 0) {
                tbody.innerHTML = `<tr><td colspan="4" class="text-center py-6 text-slate-500 font-sans text-xs">«${kw}» bo'yicha hech qanday natija topilmadi.</td></tr>`;
                return;
            }

            tbody.innerHTML = data.results.map(r => `
                <tr class="hover:bg-slate-900/60 transition-colors">
                    <td class="py-2 px-3 text-right text-slate-400 select-none">${r.left}</td>
                    <td class="py-2 px-2 text-center text-amber-300 font-bold bg-amber-500/10 rounded">${r.keyword}</td>
                    <td class="py-2 px-3 text-left text-slate-300 select-none">${r.right}</td>
                    <td class="py-2 px-3 text-center text-slate-500 whitespace-nowrap text-[11px] font-sans">
                        ${r.book_title ? r.book_title.split(':')[0] : 'Kitob'} (p.${r.page})
                    </td>
                </tr>
            `).join('');
        } catch (err) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center py-6 text-rose-400 font-sans text-xs">Xatolik: ${err.message}</td></tr>`;
        }
    }
}

// Global initialization
window.researcherHub = null;
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('phdResearcherHubContainer')) {
        window.researcherHub = new ResearcherHub();
    }
});
