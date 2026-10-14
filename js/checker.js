/**
 * Interaktiv Kollokatsiya Tekshirgich va Tahlilchi
 */

class CollocationChecker {
    constructor() {
        this.sampleTexts = [
            {
                title: "Abdulhamid Cho‘lpon («Kecha va kunduz»)",
                text: "Zebi onasining javobini kutar ekan, uning yuragi duk-duk urardi. Uzoqda qirlar koʻrinib, koʻngli olis joylarni tusay boshladi. Otasi esa unga sovuq nigohi bilan tikildi."
            },
            {
                title: "Ernest Hemingway («The Old Man and the Sea»)",
                text: "The old man fished alone in the Gulf Stream. He had deep wrinkles in his neck and looked at the sail of permanent defeat. But he still had faith in taking a fish."
            }
        ];

        this.init();
    }

    init() {
        this.bindEvents();
        this.renderSamples();
    }

    bindEvents() {
        const analyzeBtn = document.getElementById('checkerAnalyzeBtn');
        const aiDiagnoseBtn = document.getElementById('checkerAiDiagnoseBtn');
        const clearBtn = document.getElementById('checkerClearBtn');
        const textarea = document.getElementById('checkerInputText');

        if (analyzeBtn && textarea) {
            analyzeBtn.addEventListener('click', () => {
                this.analyzeText(textarea.value);
            });
        }

        if (aiDiagnoseBtn && textarea) {
            aiDiagnoseBtn.addEventListener('click', () => {
                this.analyzeWithAi(textarea.value);
            });
        }

        if (clearBtn && textarea) {
            clearBtn.addEventListener('click', () => {
                textarea.value = '';
                document.getElementById('checkerResultsContainer').innerHTML = `
                    <div class="text-center py-12 text-slate-400">
                        <i data-lucide="flask-conical" class="w-10 h-10 mx-auto mb-2 opacity-40"></i>
                        <p class="text-sm">Matnni kiriting va «Lab Ekstraksiya & Statistik Tahlil» yoki «DeepSeek AI Chuqur Diagnostika» tugmasini bosing</p>
                    </div>
                `;
                if (window.lucide) lucide.createIcons();
            });
        }
    }

    renderSamples() {
        const container = document.getElementById('checkerSamplesList');
        if (!container) return;

        container.innerHTML = this.sampleTexts.map((sample, idx) => `
            <button onclick="collocationChecker.loadSample(${idx})" class="text-left p-3 rounded-xl bg-slate-50 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 border border-slate-200 dark:border-slate-700 transition group w-full">
                <div class="text-xs font-bold text-slate-700 dark:text-slate-300 group-hover:text-indigo-600 dark:group-hover:text-indigo-400">${sample.title}</div>
                <div class="text-xs text-slate-500 truncate mt-1">${sample.text}</div>
            </button>
        `).join('');
    }

    loadSample(index) {
        const textarea = document.getElementById('checkerInputText');
        if (textarea && this.sampleTexts[index]) {
            textarea.value = this.sampleTexts[index].text;
            this.analyzeText(textarea.value);
        }
    }

    async analyzeText(text) {
        if (!text || !text.trim()) {
            if (window.app && app.showToast) app.showToast("Iltimos, tahlil qilish uchun matn kiriting", "warning");
            return;
        }

        const container = document.getElementById('checkerResultsContainer');
        if (container) {
            container.innerHTML = `
                <div class="p-8 text-center bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 space-y-3">
                    <div class="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
                    <p class="text-xs font-bold text-slate-700 dark:text-slate-300">Collocation Research Lab: Matn segmentlanmoqda va statistik ko'rsatkichlar hisoblanmoqda...</p>
                </div>
            `;
        }

        let labData = null;
        try {
            const resp = await fetch('/api/lab/extract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            if (resp.ok) {
                labData = await resp.json();
            }
        } catch (e) {
            console.warn("Lab API offline or failed, using local fallback", e);
        }

        const norm = (s) => (window.normalizeApostrophes ? normalizeApostrophes(s) : s);
        const lowerText = norm(text.toLowerCase());
        const foundCollocations = [];
        const detectedTraps = [];

        // Check against collocations database
        if (window.collocationsDatabase && Array.isArray(collocationsDatabase)) {
            collocationsDatabase.forEach(item => {
                const uzTerms = norm(item.uzbek || '').toLowerCase().split('/').map(s => s.trim());
                const enTerms = norm(item.english || '').toLowerCase().split('/').map(s => s.trim());

                uzTerms.forEach(term => {
                    if (!term) return;
                    const words = term.split(' ').filter(w => w.length > 2);
                    if (words.length > 0 && words.every(w => lowerText.includes(w))) {
                        foundCollocations.push({ matched: term, type: 'uzbek', data: item });
                    }
                });

                enTerms.forEach(term => {
                    if (!term) return;
                    const words = term.split(' ').filter(w => w.length > 2);
                    if (words.length > 0 && words.every(w => lowerText.includes(w))) {
                        foundCollocations.push({ matched: term, type: 'english', data: item });
                    }
                });
            });
        }

        // Dedicated translation traps and calque detector (PDF 8-bo'lim)
        const calqueRules = [
            {
                pattern: "cold look",
                correction: "cold gaze / icy stare / frosty glare",
                note: "«Sovuq nigoh» birikmasida «cold look» soʻzma-soʻz kalka boʻlib, uslubiy gʻayritabiylik tugʻdiradi. Badiiy-akademik korpuslarda «cold gaze» yoki «icy stare» barqaror kollokatsiya hisoblanadi."
            },
            {
                pattern: "strong rain",
                correction: "heavy rain / pouring rain",
                note: "«Kuchli yomgʻir» uchun «strong rain» notoʻgʻri kalka hisoblanadi; ingliz tilida faqat «heavy rain» qoʻllanadi."
            },
            {
                pattern: "do a crime",
                correction: "commit a crime",
                note: "«Jinoyat qilmoq» birikmasida do feʼli kalka hisoblanadi, turgʻun birikma «commit a crime»."
            },
            {
                pattern: "accept a decision",
                correction: "make a decision",
                note: "«Qaror qabul qilmoq» ingliz tilida «make a decision» tarzida kollokatsiyalanadi."
            },
            {
                pattern: "throw anchor",
                correction: "drop anchor / cast anchor",
                note: "«Langar tashlamoq» turgʻun dengizchilik termini «drop anchor» hisoblanadi."
            },
            {
                pattern: "deeply breath",
                correction: "take a deep breath / breathe deeply",
                note: "«Chuqur nafas olmoq» barqaror grammatik va kollokatsion modeli «take a deep breath»."
            },
            {
                pattern: "heart wants",
                correction: "heart yearns / heart desires",
                note: "«Koʻngil tusamoq» iboraviy ifodasida «heart wants» uslubiy jihatdan zaif, «heart yearns/longs» tavsiya etiladi."
            }
        ];

        calqueRules.forEach(rule => {
            if (lowerText.includes(rule.pattern)) {
                detectedTraps.push({
                    trapText: rule.pattern,
                    correction: rule.correction,
                    note: rule.note
                });
            }
        });

        // Deduplicate
        const uniqueCollocations = [];
        const seenIds = new Set();
        foundCollocations.forEach(item => {
            if (item.data && !seenIds.has(item.data.id)) {
                seenIds.add(item.data.id);
                uniqueCollocations.push(item);
            }
        });

        this.currentLabCandidates = (labData && labData.candidates) ? labData.candidates : [];
        this.renderAnalysisResult(text, uniqueCollocations, detectedTraps, labData);
    }

    renderAnalysisResult(originalText, collocations, traps, labData) {
        const container = document.getElementById('checkerResultsContainer');
        if (!container) return;

        let markedText = originalText;
        collocations.forEach(col => {
            const regex = new RegExp(`(${col.matched})`, 'gi');
            markedText = markedText.replace(regex, `<span class="bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 font-semibold px-1 rounded border border-indigo-300 dark:border-indigo-700">$1</span>`);
        });

        traps.forEach(trap => {
            const regex = new RegExp(`(${trap.trapText})`, 'gi');
            markedText = markedText.replace(regex, `<span class="bg-rose-100 dark:bg-rose-900/60 text-rose-700 dark:text-rose-300 font-semibold px-1 rounded line-through border border-rose-300">$1</span>`);
        });

        const candidates = (labData && labData.candidates) ? labData.candidates : [];
        const tokensCount = labData ? labData.tokens_count : originalText.split(/\s+/).filter(Boolean).length;
        const sentencesCount = labData ? labData.sentences_count : originalText.split(/[.!?]+/).filter(Boolean).length;

        container.innerHTML = `
            <div class="space-y-6">
                <!-- Summary Metrics Bar -->
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div class="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                        <span class="text-[10px] uppercase font-bold text-slate-400 block">Jami Tokenlar</span>
                        <span class="text-lg font-black font-mono text-indigo-600 dark:text-indigo-400">${tokensCount}</span>
                    </div>
                    <div class="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                        <span class="text-[10px] uppercase font-bold text-slate-400 block">Jumlalar Soni</span>
                        <span class="text-lg font-black font-mono text-slate-800 dark:text-slate-200">${sentencesCount}</span>
                    </div>
                    <div class="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                        <span class="text-[10px] uppercase font-bold text-slate-400 block">Aniqlangan Baza Birliklari</span>
                        <span class="text-lg font-black font-mono text-emerald-600 dark:text-emerald-400">${collocations.length}</span>
                    </div>
                    <div class="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                        <span class="text-[10px] uppercase font-bold text-slate-400 block">Kalka Xatolari</span>
                        <span class="text-lg font-black font-mono ${traps.length > 0 ? 'text-rose-600' : 'text-slate-400'}">${traps.length}</span>
                    </div>
                </div>

                <!-- 1 & 4-BO'LIM: RESEARCH LAB STATISTIK JADVALI -->
                <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 space-y-3">
                    <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100 dark:border-slate-800">
                        <div>
                            <h3 class="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                                <i data-lucide="calculator" class="w-4 h-4 text-indigo-600"></i>
                                N-gram Nomzodlar va Statistik Ko‘rsatkichlar (Chastota, MI, T-Score, LL)
                            </h3>
                            <p class="text-xs text-slate-500 mt-0.5">Avtomatik segmentatsiyalangan birikma nomzodlari va ularning assotsiatsiya ko‘rsatkichlari</p>
                        </div>
                        <div class="flex items-center gap-2">
                            <button onclick="collocationChecker.exportLabCSV()" class="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-xs font-semibold text-slate-700 dark:text-slate-300 transition flex items-center gap-1">
                                <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5 text-emerald-600"></i> CSV Eksport
                            </button>
                            <button onclick="collocationChecker.exportLabExcel()" class="px-3 py-1.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 hover:bg-indigo-100 text-xs font-semibold text-indigo-700 dark:text-indigo-300 transition flex items-center gap-1">
                                <i data-lucide="download" class="w-3.5 h-3.5 text-indigo-600"></i> Excel (XLS)
                            </button>
                        </div>
                    </div>

                    ${candidates.length > 0 ? `
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs">
                                <thead>
                                    <tr class="border-b border-slate-200 dark:border-slate-800 text-[11px] font-mono text-slate-500 uppercase bg-slate-50 dark:bg-slate-950/40">
                                        <th class="py-2.5 px-3">Nomzod Birikma (N-gram)</th>
                                        <th class="py-2.5 px-2">Qolip (3.1)</th>
                                        <th class="py-2.5 px-2 font-mono">Chastota (f)</th>
                                        <th class="py-2.5 px-2 font-mono">MI Score</th>
                                        <th class="py-2.5 px-2 font-mono">T-Score</th>
                                        <th class="py-2.5 px-2 font-mono">Log-Likelihood</th>
                                        <th class="py-2.5 px-2">Holat / Ekvivalent (3.2)</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-slate-100 dark:divide-slate-800/60 font-sans">
                                    ${candidates.map(c => `
                                        <tr class="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition">
                                            <td class="py-2 px-3 font-semibold text-slate-900 dark:text-slate-100">
                                                ${c.ngram}
                                            </td>
                                            <td class="py-2 px-2">
                                                <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">${c.pattern || 'Erkin'}</span>
                                            </td>
                                            <td class="py-2 px-2 font-mono font-bold text-slate-700 dark:text-slate-300">${c.freq}</td>
                                            <td class="py-2 px-2 font-mono text-emerald-600 dark:text-emerald-400 font-semibold">${c.mi_score}</td>
                                            <td class="py-2 px-2 font-mono text-indigo-600 dark:text-indigo-400 font-semibold">${c.t_score}</td>
                                            <td class="py-2 px-2 font-mono text-purple-600 dark:text-purple-400 font-semibold">${c.log_likelihood}</td>
                                            <td class="py-2 px-2 text-[11px]">
                                                ${c.status === 'Verifikatsiyalangan' ? `
                                                    <span class="px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-bold border border-emerald-200">
                                                        ✓ ${c.status}
                                                    </span>
                                                    ${c.equivalent ? `<div class="text-[11px] text-slate-500 mt-0.5">⟷ ${c.equivalent}</div>` : ''}
                                                ` : `
                                                    <span class="text-slate-400 italic">${c.status || 'Nomzod'}</span>
                                                `}
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    ` : `
                        <p class="text-xs text-slate-400 italic py-4 text-center">Matndan statistik N-gram nomzodlar ajratilmadi. Iltimos, uzunroq jumla yoki xatboshi kiriting.</p>
                    `}
                </div>

                <!-- Highlighted text -->
                <div class="p-4 bg-slate-50 dark:bg-slate-900/70 rounded-2xl border border-slate-200 dark:border-slate-800">
                    <span class="text-xs uppercase font-bold text-slate-400 block mb-2">Matndagi aniqlangan kollokatsion birliklar va kalkalar:</span>
                    <p class="text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-sans">${markedText}</p>
                </div>

                <!-- Traps alert if any -->
                ${traps.length > 0 ? `
                    <div class="p-4 bg-rose-50 dark:bg-rose-950/40 rounded-2xl border border-rose-200 dark:border-rose-900/60">
                        <h4 class="text-sm font-bold text-rose-800 dark:text-rose-300 flex items-center gap-2 mb-2">
                            <i data-lucide="alert-triangle" class="w-4 h-4 text-rose-600"></i> Diqqat! Kalka (notoʻgʻri birikma) aniqlandi:
                        </h4>
                        <div class="space-y-2">
                            ${traps.map(t => `
                                <div class="text-xs text-rose-700 dark:text-rose-200 bg-white/60 dark:bg-slate-900/60 p-2.5 rounded-lg border border-rose-200/50">
                                    Notoʻgʻri: <span class="line-through font-mono font-bold">${t.trapText}</span> ➔ Tavsiya etilgan kollokat: <span class="font-mono font-bold text-emerald-600 dark:text-emerald-400">${t.correction}</span>
                                    <p class="text-[11px] text-slate-500 mt-1">${t.note}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                <!-- AI Deep Diagnosis Banner -->
                <div class="p-4 bg-gradient-to-r from-purple-500/10 via-indigo-500/10 to-transparent rounded-2xl border border-purple-500/20 flex flex-wrap items-center justify-between gap-3">
                    <div class="flex items-center gap-2.5 text-xs text-purple-950 dark:text-purple-200">
                        <span class="w-2.5 h-2.5 rounded-full bg-purple-600 animate-pulse"></span>
                        <span class="font-bold">DeepSeek AI orqali toʻliq ilmiy diagnostika, kalka xatolarini tuzatish va akademik tarjima varianti:</span>
                    </div>
                    <button onclick="collocationChecker.analyzeWithAi()" class="px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white text-xs font-bold shadow-md shadow-purple-500/20 transition flex items-center gap-1.5 cursor-pointer active:scale-95">
                        <i data-lucide="bot" class="w-3.5 h-3.5"></i> DeepSeek AI Chuqur Diagnostika
                    </button>
                </div>

                <!-- Detected collocations list -->
                <div>
                    <h4 class="text-sm font-bold text-slate-800 dark:text-slate-200 mb-3 flex items-center justify-between">
                        <span>Bazada Mos Kelgan Birikmalar (${collocations.length} ta):</span>
                        <span class="text-xs text-slate-400 font-normal">Tarkibiy qolip & Ekvivalentlik</span>
                    </h4>

                    ${collocations.length === 0 ? `
                        <p class="text-sm text-slate-500 italic p-4 bg-slate-50 dark:bg-slate-900/40 rounded-xl">Matnda faol kollokatsiyalar bazasidan toʻgʻridan-toʻgʻri mos kelgan birliklar topilmadi.</p>
                    ` : `
                        <div class="grid sm:grid-cols-2 gap-3">
                            ${collocations.map(col => `
                                <div class="p-3 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-1.5">
                                    <div class="flex items-center justify-between">
                                        <span class="text-[11px] font-mono font-semibold px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">${col.data.pattern}</span>
                                        <div class="flex items-center gap-1.5 text-xs font-mono">
                                            <span class="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 text-[10px]">Statistika: 10-bosqichda</span>
                                        </div>
                                    </div>
                                    <div class="font-bold text-sm text-slate-900 dark:text-white">
                                        ${col.data.uzbek}
                                    </div>
                                    <div class="text-xs text-emerald-600 dark:text-emerald-400 font-medium">
                                        ⟷ ${col.data.english}
                                    </div>
                                    <div class="text-[10px] text-slate-400 font-semibold flex items-center justify-between">
                                        <span>Manba: ${col.data.sourceMeta || col.data.sourceBook || "Manba aniqlanmagan"}</span>
                                        <span class="text-indigo-500">${col.data.equivalenceType || 'Mos ekvivalent'}</span>
                                    </div>
                                    <p class="text-[11px] text-slate-500 border-t border-slate-100 dark:border-slate-700/60 pt-1 mt-1">
                                        ${col.data.culturalNote || col.data.literalTrap || "Barqaror ekvivalentlik modeli"}
                                    </p>
                                </div>
                            `).join('')}
                        </div>
                    `}
                </div>
            </div>
        `;

        if (window.lucide) lucide.createIcons();
    }

    exportLabCSV() {
        if (!this.currentLabCandidates || this.currentLabCandidates.length === 0) {
            if (window.app && app.showToast) app.showToast("Eksport qilish uchun nomzodlar mavjud emas", "warning");
            return;
        }

        const headers = ["Nomzod Birikma", "Qolip (3.1)", "Chastota (f)", "MI Score", "T-Score", "Log-Likelihood", "Holat", "Ekvivalent"];
        const rows = this.currentLabCandidates.map(c => [
            `"${(c.ngram || '').replace(/"/g, '""')}"`,
            `"${(c.pattern || '').replace(/"/g, '""')}"`,
            c.freq || 1,
            c.mi_score || 0,
            c.t_score || 0,
            c.log_likelihood || 0,
            `"${(c.status || '').replace(/"/g, '""')}"`,
            `"${(c.equivalent || '').replace(/"/g, '""')}"`
        ]);

        const csvContent = "\uFEFF" + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.setAttribute("download", `collocation_lab_candidates_${new Date().toISOString().slice(0, 10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        if (window.app && app.showToast) app.showToast("Lab nomzodlari CSV formatida yuklab olindi", "success");
    }

    exportLabExcel() {
        if (!this.currentLabCandidates || this.currentLabCandidates.length === 0) {
            if (window.app && app.showToast) app.showToast("Eksport qilish uchun nomzodlar mavjud emas", "warning");
            return;
        }

        const headers = ["Nomzod Birikma", "Qolip (3.1)", "Chastota (f)", "MI Score", "T-Score", "Log-Likelihood", "Holat", "Ekvivalent"];
        const rows = this.currentLabCandidates.map(c => [
            c.ngram || '',
            c.pattern || '',
            c.freq || 1,
            c.mi_score || 0,
            c.t_score || 0,
            c.log_likelihood || 0,
            c.status || '',
            c.equivalent || ''
        ]);

        const tsvContent = "\uFEFF" + [headers.join('\t'), ...rows.map(r => r.join('\t'))].join('\n');
        const blob = new Blob([tsvContent], { type: 'application/vnd.ms-excel;charset=utf-8;' });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.setAttribute("download", `collocation_lab_candidates_${new Date().toISOString().slice(0, 10)}.xls`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        if (window.app && app.showToast) app.showToast("Lab nomzodlari Excel (XLS) formatida yuklab olindi", "success");
    }

    async analyzeWithAi(customText = '') {
        const textarea = document.getElementById('checkerInputText');
        const text = (customText || (textarea ? textarea.value : '')).trim();

        if (!text) {
            if (window.app && app.showToast) app.showToast("Iltimos, tahlil qilish uchun matn kiriting!", "warning");
            if (textarea) textarea.focus();
            return;
        }

        const container = document.getElementById('checkerResultsContainer');
        if (!container) return;

        container.innerHTML = `
            <div class="p-10 text-center bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 space-y-4">
                <div class="w-10 h-10 border-3 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
                <div>
                    <h4 class="font-bold text-sm text-slate-900 dark:text-white">DeepSeek-v4 AI Chuqur Matn Diagnostikasini Oʻtkazmoqda...</h4>
                    <p class="text-xs text-slate-500 mt-1">Leksik qatlamlar, turgʻun birikmalar, kalka xatoliklari (*cold look, *strong rain) va akademik tarjima tahlili</p>
                </div>
            </div>
        `;
        container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        try {
            const resp = await fetch('/api/checker/ai-diagnose', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            const data = await resp.json();
            if (!data.success) throw new Error(data.error || "Noma'lum xatolik");

            let formattedMd = (data.markdown || '')
                .replace(/### (.*?)\n/g, '<h4 class="text-sm font-bold text-slate-900 dark:text-white mt-4 mb-2 flex items-center gap-1.5"><i data-lucide="chevron-right" class="w-4 h-4 text-purple-600"></i> $1</h4>')
                .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-slate-900 dark:text-white">$1</strong>')
                .replace(/\*(.*?)\*/g, '<em class="italic text-slate-600 dark:text-slate-300">$1</em>')
                .replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-purple-600 dark:text-purple-400 font-mono text-[11px]">$1</code>')
                .replace(/- (.*?)\n/g, '<li class="ml-4 list-disc text-xs text-slate-700 dark:text-slate-300 leading-relaxed">$1</li>')
                .replace(/\n\n/g, '<br>');

            container.innerHTML = `
                <div class="space-y-6">
                    <!-- Top Diagnostics Bar -->
                    <div class="flex flex-wrap items-center justify-between gap-3 p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-xs">
                        <div class="flex items-center gap-2">
                            <span class="px-2.5 py-1 rounded-md bg-amber-500 text-white font-bold text-[11px]">AI-taklif (tekshirilmagan)</span>
                            <span class="font-bold text-slate-900 dark:text-white">Leksik & Kollokatsion Diagnostika</span>
                            <span class="px-2 py-0.5 rounded-lg bg-amber-100 dark:bg-amber-900/60 text-amber-800 dark:text-amber-200 font-mono text-[11px]">
                                ${data.sourceLang.toUpperCase()} ➔ ${data.targetLang.toUpperCase()}
                            </span>
                        </div>
                        <div class="flex items-center gap-2">
                            <span class="text-slate-500 font-mono text-[11px]">Model tavsiyasi (ekspert tasdig'isiz qabul qilinmaydi)</span>
                            <button id="checkerCopyAiBtn" class="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs flex items-center gap-1 shadow-sm transition">
                                <i data-lucide="copy" class="w-3.5 h-3.5"></i> Nusxalash
                            </button>
                        </div>
                    </div>

                    <!-- Side-by-side Translation Comparison -->
                    <div class="grid md:grid-cols-2 gap-4">
                        <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                            <span class="text-xs uppercase font-bold text-slate-400 block mb-1.5">Asl Matn (${data.sourceLang.toUpperCase()}):</span>
                            <p class="text-sm text-slate-900 dark:text-white leading-relaxed font-sans">${data.originalText}</p>
                        </div>
                        <div class="p-4 rounded-2xl bg-emerald-50/60 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800">
                            <span class="text-xs uppercase font-bold text-emerald-700 dark:text-emerald-400 block mb-1.5">Adekvat Akademik/Badiiy Tarjima (${data.targetLang.toUpperCase()}):</span>
                            <p class="text-sm font-semibold text-emerald-900 dark:text-emerald-200 leading-relaxed font-sans">${data.translatedText}</p>
                        </div>
                    </div>

                    <!-- AI Markdown Report -->
                    <div class="bg-white dark:bg-slate-800/90 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm space-y-2 text-xs sm:text-sm text-slate-800 dark:text-slate-200 leading-relaxed">
                        ${formattedMd}
                    </div>
                </div>
            `;

            if (window.lucide) lucide.createIcons();

            const copyBtn = document.getElementById('checkerCopyAiBtn');
            if (copyBtn) {
                copyBtn.onclick = () => {
                    navigator.clipboard.writeText(data.markdown || '');
                    if (window.app && app.showToast) app.showToast("AI diagnostika hisoboti nusxalandi!", "success");
                };
            }

        } catch (err) {
            container.innerHTML = `
                <div class="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs">
                    <p class="font-bold flex items-center gap-1.5"><i data-lucide="alert-circle" class="w-4 h-4"></i> AI tahlilida xatolik yuz berdi</p>
                    <p class="mt-1">${err.message}</p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
        }
    }
}

const collocationChecker = new CollocationChecker();
