import os, re, json

print("=== EXECUTING STAGE 2 EMERGENCY CONTAINMENT ===")

# -------------------------------------------------------------
# 1. Update js/data.js
# -------------------------------------------------------------
with open('js/data.js', 'r', encoding='utf-8') as f:
    data_js = f.read()

# Replace numeric claims in literaryCorporaMeta
data_js = re.sub(r'wordCount:\s*"[^"]*"', 'wordCount: "—"', data_js)
data_js = re.sub(r'alignedPairs:\s*"[^"]*"', 'alignedPairs: "— (tekislash qayta ko‘rib chiqilmoqda)"', data_js)
data_js = re.sub(r'identifiedCollocations:\s*"[^"]*"', 'identifiedCollocations: "—"', data_js)

# Mark Stevenson as quarantined
data_js = data_js.replace(
    'id: "source-stevenson",',
    'id: "source-stevenson",\n        status: "excluded",\n        exclusionReason: "D2: O‘zbekcha tarjima skanerlangan rasm (matn qatlami yo‘q), OCR va tekshiruv talab etiladi, vaqtinchalik chiqarilgan",\n        quarantined: true,'
)

# Remove dissertationData object
# dissertationData starts at const dissertationData = { ... }; and goes until const parallelCorpusData
data_js = re.sub(r'const dissertationData\s*=\s*\{[\s\S]*?\n\};\s*\nconst parallelCorpusData', '// dissertationData unpublished per Stage 2 Stage Gate (PhD Boblar yashirildi)\nconst parallelCorpusData', data_js)

# Remove researchStats at the end
data_js = re.sub(r'const researchStats\s*=\s*\{[\s\S]*?\};\s*$', '// researchStats olib tashlandi (Stage 2: soxta statistikalar yo‘qotildi)', data_js)

# Replace hardcoded metric numbers in parallelCorpusData
data_js = re.sub(r'alignmentScore:\s*"[0-9.]+"', 'alignmentScore: "—"', data_js)
data_js = re.sub(r'mi:\s*[0-9.]+', 'mi: "—"', data_js)
data_js = re.sub(r'tScore:\s*[0-9.]+', 'tScore: "—"', data_js)

with open('js/data.js', 'w', encoding='utf-8') as f:
    f.write(data_js)
print("-> js/data.js updated: dissertationData & researchStats removed, numbers replaced with '—'")

# -------------------------------------------------------------
# 2. Update js/app.js
# -------------------------------------------------------------
with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Remove chapter rendering calls from init
app_js = app_js.replace("this.renderChaptersNav();", "// this.renderChaptersNav();")
app_js = app_js.replace("this.renderActiveChapter();", "// this.renderActiveChapter();")
app_js = app_js.replace("this.bindChapterControls();", "// this.bindChapterControls();")

# Replace renderChaptersNav and renderActiveChapter bodies with no-ops
app_js = re.sub(r'renderChaptersNav\(\)\s*\{[\s\S]*?\n    \}', 'renderChaptersNav() { /* unpublished */ }', app_js)
app_js = re.sub(r'renderActiveChapter\(\)\s*\{[\s\S]*?\n    \}', 'renderActiveChapter() { /* unpublished */ }', app_js)

# Add loadLiveStats to init and definition
if 'loadLiveStats' not in app_js:
    app_js = app_js.replace(
        "this.setupModals();",
        "this.setupModals();\n        this.loadLiveStats();"
    )
    live_stats_code = """
    async loadLiveStats() {
        try {
            const resp = await fetch('/api/stats');
            if (resp.ok) {
                const data = await resp.json();
                const elSeg = document.getElementById('stat-total-segments');
                if (elSeg) elSeg.innerText = data.totalSegments ? data.totalSegments.toLocaleString() : '—';
                const elCol = document.getElementById('stat-total-collocations');
                if (elCol) elCol.innerText = data.totalCollocations ? data.totalCollocations.toLocaleString() : '—';
                const elDic = document.getElementById('stat-total-dict');
                if (elDic) elDic.innerText = data.totalDictionary ? data.totalDictionary.toLocaleString() : '—';
                const elMod = document.getElementById('stat-total-modules');
                if (elMod) elMod.innerText = '6 ta';
            }
        } catch(e) {
            console.warn('Live stats fetch failed:', e);
        }
    }
"""
    app_js = app_js.replace("selectChapter(chapterId) {", live_stats_code + "\n    selectChapter(chapterId) {")

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)
print("-> js/app.js updated: chapter calls removed, loadLiveStats added")

# -------------------------------------------------------------
# 3. Update js/charts.js
# -------------------------------------------------------------
with open('js/charts.js', 'r', encoding='utf-8') as f:
    charts_js = f.read()

# Replace renderPatternChart, renderEquivalenceChart, renderGenreChart with clean pending notices
safe_charts = """/**
 * Tadqiqot Statistikasi va Grafiklar Vizualizatsiyasi (Chart.js)
 * Eslatma: Himoya talablari bo'yicha grafiklar faqat tasdiqlangan annotatsiyalar asosida chiziladi.
 */

class AnalyticsManager {
    constructor() {
        this.charts = {};
    }

    initCharts() {
        this.showNotice('patternChart', "Strukturaviy modellar statistikasi hisoblanmoqda (tasdiqlangan annotatsiyalar kutilmoqda)");
        this.showNotice('equivalenceChart', "Tarjima ekvivalentligi turlari empirik tahlil jarayonida");
        this.showNotice('genreChart', "Asarlar bo'yicha haqiqiy taqsimot tekislashdan so'ng hisoblanadi");
    }

    showNotice(canvasId, text) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const parent = canvas.parentElement;
        if (!parent) return;
        parent.innerHTML = `<div class="h-64 flex flex-col items-center justify-center p-6 text-center text-slate-400 bg-slate-100/50 dark:bg-slate-800/50 rounded-xl border border-dashed border-slate-300 dark:border-slate-700">
            <span class="text-2xl mb-2 font-mono">—</span>
            <p class="text-xs font-medium text-slate-500 dark:text-slate-400">${text}</p>
        </div>`;
    }

    renderPatternChart() {}
    renderEquivalenceChart() {}
    renderGenreChart() {}
    updateTheme() {}
}

const analyticsManager = new AnalyticsManager();
"""

with open('js/charts.js', 'w', encoding='utf-8') as f:
    f.write(safe_charts)
print("-> js/charts.js updated: fake percentage charts replaced with authentic pending notices")

# -------------------------------------------------------------
# 4. Update js/corpus.js
# -------------------------------------------------------------
with open('js/corpus.js', 'r', encoding='utf-8') as f:
    corpus_js = f.read()

# Remove fallback numbers (5.40, 7.80, 0.96)
corpus_js = corpus_js.replace('alignmentScore: item.score || "0.96"', 'alignmentScore: item.score || "—"')
corpus_js = corpus_js.replace('mi: "5.40"', 'mi: "—"')
corpus_js = corpus_js.replace('tScore: "7.80"', 'tScore: "—"')
corpus_js = corpus_js.replace("this.totalCorpusCount = 5157;", "this.totalCorpusCount = 3811;")
corpus_js = corpus_js.replace("5,157 ta jumladan qidirilmoqda...", "tasdiqlangan jumlalardan qidirilmoqda...")

# Replace Fair Use with neutral notice
neutral_notice = "Korpusdagi matnlar mualliflik huquqi egalariga tegishli. Ular faqat ilmiy tadqiqot maqsadida, cheklangan parchalar ko‘rinishida ko‘rsatiladi. Nusxa ko‘chirish va tarqatish taqiqlanadi."
corpus_js = corpus_js.replace("PhD ilmiy-tadqiqot (Fair Use)", "Cheklangan ilmiy parcha")
corpus_js = corpus_js.replace("item.license || 'PhD ilmiy-tadqiqot (Fair Use)'", "item.license || 'Cheklangan ilmiy parcha'")

# Add warning banner for Hemingway and Cho'lpon pairs in renderCorpusResults
# Inside container.innerHTML = this.filteredData.map...
# Add warning badge for alignment review:
banner_html = """
            const warningBanner = (item.bookKey === 'cholpon' || item.bookKey === 'hemingway')
                ? `<div class="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-800 dark:text-amber-300 text-xs font-semibold flex items-center gap-2 mb-2">
                     <i data-lucide="alert-triangle" class="w-4 h-4 text-amber-600 shrink-0"></i>
                     <span>Tekislash qayta ko‘rib chiqilmoqda — tahlil uchun foydalanmang</span>
                   </div>`
                : '';
"""
corpus_js = corpus_js.replace("const uzHighlighted = this.highlightTerm(item.uz, this.searchTerm);", banner_html + "\n            const uzHighlighted = this.highlightTerm(item.uz, this.searchTerm);")

# Inject warningBanner above content
corpus_js = corpus_js.replace(
    '<!-- O\'zbekcha matn -->',
    '${warningBanner}\n                        <!-- O\'zbekcha matn -->'
)

# Remove fake percentage in match badge:
corpus_js = corpus_js.replace(
    'Moslik: ${(parseFloat(item.alignmentScore || 0.95) * 100).toFixed(0)}%',
    'Moslik: ${item.alignmentScore ? item.alignmentScore : "— (tekshirilmoqda)"}'
)

# Filter out excluded items from dataset
corpus_js = corpus_js.replace(
    'this.dataset = [...parallelCorpusData];',
    'this.dataset = parallelCorpusData.filter(x => x.status !== "excluded" && !x.quarantined);'
)

with open('js/corpus.js', 'w', encoding='utf-8') as f:
    f.write(corpus_js)
print("-> js/corpus.js updated: banner added for Hemingway/Cho'lpon, fake scores removed, neutral notice added")

# -------------------------------------------------------------
# 5. Update js/collocations.js
# -------------------------------------------------------------
with open('js/collocations.js', 'r', encoding='utf-8') as f:
    colloc_js = f.read()

# Replace hardcoded fallbacks
colloc_js = colloc_js.replace("c.miScore || 5.4", "c.miScore || '—'")
colloc_js = colloc_js.replace("c.tScore || 7.8", "c.tScore || '—'")
colloc_js = colloc_js.replace("c.freq || 25", "c.freq || '—'")
colloc_js = colloc_js.replace("c.logLikelihood || 24.5", "c.logLikelihood || '—'")
colloc_js = colloc_js.replace("PhD Fair Use", "Cheklangan ilmiy parcha")

with open('js/collocations.js', 'w', encoding='utf-8') as f:
    f.write(colloc_js)
print("-> js/collocations.js updated: hardcoded defaults removed")

# -------------------------------------------------------------
# 6. Update js/collocations_list.js
# -------------------------------------------------------------
with open('js/collocations_list.js', 'r', encoding='utf-8') as f:
    colloc_list_js = f.read()

colloc_list_js = colloc_list_js.replace("PhD Fair Use", "Cheklangan ilmiy parcha")
colloc_list_js = colloc_list_js.replace("Public Domain / Fair Use", "Cheklangan ilmiy parcha")

with open('js/collocations_list.js', 'w', encoding='utf-8') as f:
    f.write(colloc_list_js)
print("-> js/collocations_list.js updated: Fair Use labels replaced")

print("=== ALL CLIENT JS FILES SUCCESSFULLY CONTAINED ===")
