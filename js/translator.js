/**
 * TILCOR — Jonli Tarjimon va Kollokatsion Tahlil Tizimi
 * O'zbekcha <-> Inglizcha ikki tomonlama neyron tarjima
 */

class TranslatorManager {
    constructor() {
        this.sourceLang = 'uz';
        this.targetLang = 'en';
        this.debounceTimer = null;
        this.history = [];
        this.isTranslating = false;

        this.samplePhrases = [
            {
                lang: 'uz',
                text: "Chol qayiqda yolgʻiz oʻzi Golfstrimda baliq ovlardi.",
                label: "Ernest Hemingway: «Chol va dengiz» (I. G‘ofurov tarjimasi)"
            },
            {
                lang: 'uz',
                text: "Zebi onasining javobini kutar ekan, yuragi duk-duk urardi.",
                label: "Abdulhamid Cho‘lpon: «Kecha va kunduz»"
            },
            {
                lang: 'en',
                text: "He was an old man who fished alone in a skiff in the Gulf Stream.",
                label: "Ernest Hemingway: The Old Man and the Sea"
            },
            {
                lang: 'en',
                text: "The committee finally made a firm decision and took immediate steps.",
                label: "Akademik kollokatsion namuna"
            }
        ];

        this.init();
    }

    init() {
        this.bindEvents();
        this.renderSamples();
    }

    bindEvents() {
        const sourceTextarea = document.getElementById('transSourceInput');
        const translateBtn = document.getElementById('transSubmitBtn');
        const swapBtn = document.getElementById('transSwapBtn');
        const clearBtn = document.getElementById('transClearBtn');
        const copyBtn = document.getElementById('transCopyBtn');
        const speakSourceBtn = document.getElementById('transSpeakSourceBtn');
        const speakTargetBtn = document.getElementById('transSpeakTargetBtn');
        const sourceLangSelect = document.getElementById('transSourceLang');
        const targetLangSelect = document.getElementById('transTargetLang');

        if (sourceTextarea) {
            sourceTextarea.addEventListener('input', (e) => {
                this.updateCharCount(e.target.value);
                
                // Debounced auto-translate (800ms)
                clearTimeout(this.debounceTimer);
                if (e.target.value.trim().length > 1) {
                    this.debounceTimer = setTimeout(() => {
                        this.translate();
                    }, 800);
                } else {
                    this.clearOutput();
                }
            });
        }

        if (translateBtn) {
            translateBtn.addEventListener('click', () => {
                this.translate();
            });
        }

        if (swapBtn) {
            swapBtn.addEventListener('click', () => {
                this.swapLanguages();
            });
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                if (sourceTextarea) sourceTextarea.value = '';
                this.updateCharCount('');
                this.clearOutput();
            });
        }

        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                const targetText = document.getElementById('transTargetOutput');
                if (targetText && targetText.textContent) {
                    navigator.clipboard.writeText(targetText.textContent).then(() => {
                        if (window.app && typeof window.app.showToast === 'function') {
                            window.app.showToast("Tarjima nusxalandi!", "success");
                        }
                    });
                }
            });
        }

        if (speakSourceBtn) {
            speakSourceBtn.addEventListener('click', () => {
                const text = sourceTextarea ? sourceTextarea.value : '';
                if (text) this.speak(text, this.sourceLang === 'uz' ? 'uz-UZ' : 'en-US');
            });
        }

        if (speakTargetBtn) {
            speakTargetBtn.addEventListener('click', () => {
                const targetEl = document.getElementById('transTargetOutput');
                const text = targetEl ? targetEl.textContent : '';
                if (text) this.speak(text, this.targetLang === 'en' ? 'en-US' : 'uz-UZ');
            });
        }

        if (sourceLangSelect) {
            sourceLangSelect.addEventListener('change', (e) => {
                this.sourceLang = e.target.value;
                this.targetLang = this.sourceLang === 'uz' ? 'en' : 'uz';
                if (targetLangSelect) targetLangSelect.value = this.targetLang;
                this.updateLangLabels();
                this.translate();
            });
        }

        if (targetLangSelect) {
            targetLangSelect.addEventListener('change', (e) => {
                this.targetLang = e.target.value;
                this.sourceLang = this.targetLang === 'en' ? 'uz' : 'en';
                if (sourceLangSelect) sourceLangSelect.value = this.sourceLang;
                this.updateLangLabels();
                this.translate();
            });
        }
    }

    swapLanguages() {
        const sourceTextarea = document.getElementById('transSourceInput');
        const targetOutput = document.getElementById('transTargetOutput');
        
        const tempText = sourceTextarea ? sourceTextarea.value : '';
        const tempOutput = targetOutput && !targetOutput.classList.contains('italic') ? targetOutput.textContent : '';

        // Swap language state
        const tempLang = this.sourceLang;
        this.sourceLang = this.targetLang;
        this.targetLang = tempLang;

        const sourceSelect = document.getElementById('transSourceLang');
        const targetSelect = document.getElementById('transTargetLang');
        if (sourceSelect) sourceSelect.value = this.sourceLang;
        if (targetSelect) targetSelect.value = this.targetLang;

        this.updateLangLabels();

        // Swap texts if there was a translation
        if (tempOutput) {
            if (sourceTextarea) sourceTextarea.value = tempOutput;
            this.updateCharCount(tempOutput);
            this.translate();
        } else if (tempText) {
            this.translate();
        }
    }

    updateLangLabels() {
        const sourceBadge = document.getElementById('transSourceBadge');
        const targetBadge = document.getElementById('transTargetBadge');

        if (sourceBadge) {
            sourceBadge.textContent = this.sourceLang === 'uz' ? 'Oʻzbek tili' : 'English (Ingliz tili)';
        }
        if (targetBadge) {
            targetBadge.textContent = this.targetLang === 'en' ? 'English (Ingliz tili)' : 'Oʻzbek tili';
        }
    }

    updateCharCount(text) {
        const charCountEl = document.getElementById('transCharCount');
        if (charCountEl) {
            charCountEl.textContent = `${text.length} ta belgi`;
        }
    }

    renderSamples() {
        const container = document.getElementById('transSamplesList');
        if (!container) return;

        container.innerHTML = this.samplePhrases.map((sample, idx) => `
            <button onclick="translatorManager.loadSample(${idx})" class="text-left p-3 rounded-xl bg-slate-50 dark:bg-slate-800/80 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 border border-slate-200 dark:border-slate-700 transition group w-full">
                <span class="text-[10px] uppercase font-bold text-indigo-600 dark:text-indigo-400 block">${sample.label}</span>
                <p class="text-xs text-slate-700 dark:text-slate-300 truncate mt-1">${sample.text}</p>
            </button>
        `).join('');
    }

    loadSample(index) {
        const sample = this.samplePhrases[index];
        if (!sample) return;

        this.sourceLang = sample.lang;
        this.targetLang = sample.lang === 'uz' ? 'en' : 'uz';

        const sourceSelect = document.getElementById('transSourceLang');
        const targetSelect = document.getElementById('transTargetLang');
        if (sourceSelect) sourceSelect.value = this.sourceLang;
        if (targetSelect) targetSelect.value = this.targetLang;
        this.updateLangLabels();

        const sourceTextarea = document.getElementById('transSourceInput');
        if (sourceTextarea) {
            sourceTextarea.value = sample.text;
            this.updateCharCount(sample.text);
            this.translate();
        }
    }

    clearOutput() {
        const outputEl = document.getElementById('transTargetOutput');
        const intelEl = document.getElementById('transCollocIntel');
        if (outputEl) {
            outputEl.innerHTML = `<span class="text-slate-400 italic">Tarjima bu yerda avtomatik paydo boʻladi...</span>`;
        }
        if (intelEl) {
            intelEl.innerHTML = '';
            intelEl.classList.add('hidden');
        }
    }

    async translate() {
        const sourceTextarea = document.getElementById('transSourceInput');
        const outputEl = document.getElementById('transTargetOutput');
        if (!sourceTextarea || !outputEl) return;

        const text = sourceTextarea.value.trim();
        if (!text) {
            this.clearOutput();
            return;
        }

        if (this.isTranslating) return;
        this.isTranslating = true;

        outputEl.innerHTML = `
            <div class="flex items-center gap-2 text-indigo-600 dark:text-indigo-400 py-4">
                <div class="w-4 h-4 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                <span class="text-sm">Tarjima qilinmoqda...</span>
            </div>
        `;

        try {
            let translated = null;

            // Strategy 1: Local Server Proxy (/api/translate)
            try {
                const proxyResp = await fetch(`/api/translate?text=${encodeURIComponent(text)}&sl=${this.sourceLang}&tl=${this.targetLang}`);
                if (proxyResp.ok) {
                    const data = await proxyResp.json();
                    if (data.success && data.translatedText) {
                        translated = data.translatedText;
                    }
                }
            } catch (e) {
                // Ignore and fallback to client-side
            }

            // Strategy 2: Direct Google Translate free endpoint
            if (!translated) {
                try {
                    const gUrl = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${this.sourceLang}&tl=${this.targetLang}&dt=t&q=${encodeURIComponent(text)}`;
                    const gResp = await fetch(gUrl);
                    if (gResp.ok) {
                        const gData = await gResp.json();
                        translated = gData[0].map(item => item[0]).join('');
                    }
                } catch (e) {
                    // Fallback to strategy 3
                }
            }

            // Strategy 3: MyMemory API fallback
            if (!translated) {
                try {
                    const pair = `${this.sourceLang}|${this.targetLang}`;
                    const mUrl = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${pair}`;
                    const mResp = await fetch(mUrl);
                    if (mResp.ok) {
                        const mData = await mResp.json();
                        if (mData.responseData && mData.responseData.translatedText) {
                            translated = mData.responseData.translatedText;
                        }
                    }
                } catch (e) {
                    // Final fallback
                }
            }

            if (translated) {
                outputEl.innerHTML = `
                    <div class="mb-2 px-2.5 py-1 rounded-lg bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-300 text-xs font-semibold inline-block">
                        Mashina tarjimasi (Google / MyMemory) — tekshirilmagan
                    </div>
                    <div class="text-slate-900 dark:text-white leading-relaxed">${translated}</div>
                `;
                this.analyzeTranslationCollocations(text, translated);
                this.saveHistory(text, translated);
            } else {
                outputEl.innerHTML = `<span class="text-rose-500 text-sm">Internetga ulanishda nosozlik yoki tarjima xizmati javob bermadi. Iltimos, qayta urinib koʻring.</span>`;
            }
        } catch (err) {
            outputEl.innerHTML = `<span class="text-rose-500 text-sm">Xatolik yuz berdi: ${err.message}</span>`;
        } finally {
            this.isTranslating = false;
        }
    }

    analyzeTranslationCollocations(sourceText, targetText) {
        const intelEl = document.getElementById('transCollocIntel');
        if (!intelEl) return;

        const norm = (s) => (window.normalizeApostrophes ? normalizeApostrophes(s) : s);
        const combinedText = norm(`${sourceText} ${targetText}`).toLowerCase();
        const matched = [];
        const traps = [];

        if (typeof collocationsDatabase !== 'undefined' && Array.isArray(collocationsDatabase)) {
            collocationsDatabase.forEach(item => {
                const uzKey = norm(item.nodeUz || item.uzbek || '').toLowerCase();
                const enKey = norm(item.nodeEn || item.english || '').toLowerCase();
                if (uzKey && combinedText.includes(uzKey)) matched.push(item);
                else if (enKey && combinedText.includes(enKey)) matched.push(item);

                // Check if user's text contains literal trap
                const trapList = ["accept a decision", "strong rain", "do a crime", "heart wants"];
                trapList.forEach(t => {
                    if (combinedText.includes(t)) {
                        traps.push({ trap: t, correct: item.english, explanation: item.literalTrap });
                    }
                });
            });
        }

        if (matched.length === 0 && traps.length === 0) {
            intelEl.classList.add('hidden');
            intelEl.innerHTML = '';
            return;
        }

        intelEl.classList.remove('hidden');
        intelEl.innerHTML = `
            <div class="p-4 bg-indigo-50/70 dark:bg-indigo-950/40 rounded-2xl border border-indigo-100 dark:border-indigo-900/60 space-y-3">
                <div class="flex items-center justify-between">
                    <span class="text-xs font-bold uppercase tracking-wider text-indigo-700 dark:text-indigo-300 flex items-center gap-1.5">
                        <i data-lucide="sparkles" class="w-4 h-4 text-indigo-600"></i> Korpus intellekti: Aniqlangan kollokatsiyalar (${matched.length})
                    </span>
                    <span class="text-[10px] font-mono text-slate-400">Ilmiy baza bilan solishtirildi</span>
                </div>

                ${traps.length > 0 ? `
                    <div class="p-2.5 bg-rose-100/70 dark:bg-rose-950/60 rounded-xl border border-rose-200 dark:border-rose-900 text-xs text-rose-800 dark:text-rose-200">
                        <strong>Eslatma (Kalka xatosi):</strong> Matnda nomaqbul kalka birikma mavjud! Tavsiya etiladi: 
                        <span class="font-bold underline">${traps[0].correct}</span>
                    </div>
                ` : ''}

                <div class="grid sm:grid-cols-2 gap-2">
                    ${matched.slice(0, 4).map(item => `
                        <div class="p-2.5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200/80 dark:border-slate-700 text-xs space-y-1">
                            <div class="flex justify-between items-center">
                                <strong class="text-slate-900 dark:text-white">${item.uzbek}</strong>
                                <span class="font-mono text-[10px] text-emerald-600 dark:text-emerald-400 font-bold">MI: ${item.miScore}</span>
                            </div>
                            <div class="text-emerald-700 dark:text-emerald-300 font-medium">⟷ ${item.english}</div>
                            <div class="text-[10px] text-slate-400">${item.pattern} | ${item.sourceBook || "Parallel korpus"}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        if (window.lucide) lucide.createIcons();
    }

    saveHistory(source, target) {
        if (!source || !target) return;
        this.history.unshift({
            source,
            target,
            from: this.sourceLang,
            to: this.targetLang,
            time: new Date().toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' })
        });

        if (this.history.length > 6) this.history.pop();
        this.renderHistory();
    }

    renderHistory() {
        const container = document.getElementById('transHistoryList');
        if (!container) return;

        if (this.history.length === 0) {
            container.innerHTML = `<span class="text-xs text-slate-400 italic">Tarjimalar tarixi boʻsh</span>`;
            return;
        }

        container.innerHTML = this.history.map(item => `
            <div class="p-3 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 text-xs space-y-1">
                <div class="flex justify-between text-[10px] text-slate-400 font-mono">
                    <span>${item.from.toUpperCase()} ➔ ${item.to.toUpperCase()}</span>
                    <span>${item.time}</span>
                </div>
                <p class="text-slate-700 dark:text-slate-300 font-medium truncate">${item.source}</p>
                <p class="text-emerald-600 dark:text-emerald-400 font-medium truncate">${item.target}</p>
            </div>
        `).join('');
    }

    speak(text, lang) {
        if (!('speechSynthesis' in window)) {
            app.showToast("Brauzerda ovozli oʻqish qoʻllab-quvvatlanmaydi", "warning");
            return;
        }
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang;
        utterance.rate = 0.95;
        window.speechSynthesis.speak(utterance);
    }
}

const translatorManager = new TranslatorManager();
