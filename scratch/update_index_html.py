import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Title & Meta robots
html = re.sub(r'<title>.*?</title>', '<title>TILCOR — O‘zbek–ingliz parallel korpusi</title>', html)
if '<meta name="robots"' not in html:
    html = html.replace(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <meta name="robots" content="noindex, nofollow">'
    )

# 2. Logo & Brand Title
html = html.replace('UZ–EN COLLOCATION CORPUS', 'TILCOR — O‘zbek–ingliz parallel korpusi')
html = html.replace('ParallelColloc', 'TILCOR v2.0')
html = html.replace(
    'PhD Tadqiqoti Uchun Parallel Korpus & Kollokatsiyalar Platformasi',
    'Kollokatsiyalar tarjimasi tadqiqoti uchun'
)

# 3. Remove "PhD Metodologiya" and "PhD Boblar" buttons from nav
html = re.sub(
    r'<button data-tab-target="chapters"[^>]*>[\s\S]*?</button>',
    '',
    html
)

# 4. Remove Section View-Chapters
html = re.sub(
    r'<!-- VIEW 2: CHAPTERS \(ILMIY ISH VA BOBLAR\) -->[\s\S]*?<section id="view-chapters" class="tab-view hidden">[\s\S]*?</section>',
    '<!-- VIEW 2: CHAPTERS unpublished per Stage 2 emergency containment -->',
    html
)

# 5. Stats bar replacement
old_stats_pattern = r'<!-- Stats Bar -->\s*<div class="grid grid-cols-2 md:grid-cols-4 gap-4">[\s\S]*?</div>\s*</div>'
new_stats_html = """<!-- Stats Bar -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="p-5 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm text-center">
                    <span id="stat-total-segments" class="text-3xl sm:text-4xl font-black text-indigo-600 dark:text-indigo-400 block font-mono">—</span>
                    <span class="text-xs uppercase font-bold text-slate-500 dark:text-slate-400 mt-1 block">Parallel Jumla & Segment</span>
                </div>
                <div class="p-5 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm text-center">
                    <span id="stat-total-collocations" class="text-3xl sm:text-4xl font-black text-emerald-600 dark:text-emerald-400 block font-mono">—</span>
                    <span class="text-xs uppercase font-bold text-slate-500 dark:text-slate-400 mt-1 block">Kollokatsiyalar Bazasi</span>
                </div>
                <div class="p-5 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm text-center">
                    <span id="stat-total-modules" class="text-3xl sm:text-4xl font-black text-blue-600 dark:text-blue-400 block font-mono">6 ta</span>
                    <span class="text-xs uppercase font-bold text-slate-500 dark:text-slate-400 mt-1 block">Asosiy Ilmiy Modul</span>
                </div>
                <div class="p-5 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm text-center">
                    <span id="stat-total-dict" class="text-3xl sm:text-4xl font-black text-amber-600 dark:text-amber-400 block font-mono">—</span>
                    <span class="text-xs uppercase font-bold text-slate-500 dark:text-slate-400 mt-1 block">Elektron Lugʻat Soʻzlari</span>
                </div>
            </div>"""

html = re.sub(old_stats_pattern, new_stats_html, html)

# 6. Book cards warning banners and quarantine
# Cho'lpon card banner
html = html.replace(
    '<h3 class="text-lg font-bold text-slate-900 dark:text-white">Choʻlpon: «Kecha va kunduz»</h3>',
    '<div class="mb-2 p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-800 dark:text-amber-300 text-[11px] font-semibold flex items-center gap-1.5"><i data-lucide="alert-triangle" class="w-3.5 h-3.5 text-amber-600 shrink-0"></i> Tekislash qayta ko‘rib chiqilmoqda — tahlil uchun foydalanmang</div>\n                            <h3 class="text-lg font-bold text-slate-900 dark:text-white">Choʻlpon: «Kecha va kunduz»</h3>'
)

# Hemingway card banner
html = html.replace(
    '<h3 class="text-lg font-bold text-slate-900 dark:text-white">E. Hemingway: «The Old Man and the Sea»</h3>',
    '<div class="mb-2 p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-800 dark:text-amber-300 text-[11px] font-semibold flex items-center gap-1.5"><i data-lucide="alert-triangle" class="w-3.5 h-3.5 text-amber-600 shrink-0"></i> Tekislash qayta ko‘rib chiqilmoqda — tahlil uchun foydalanmang</div>\n                            <h3 class="text-lg font-bold text-slate-900 dark:text-white">E. Hemingway: «The Old Man and the Sea»</h3>'
)

# Stevenson quarantine
html = html.replace(
    '1,346 ta Jumla',
    'Karantinda (D2)'
)
html = html.replace(
    'bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300 border border-amber-200 dark:border-amber-800">\n                                    Karantinda (D2)',
    'bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-300 border border-rose-200 dark:border-rose-800">\n                                    Karantinda (D2)'
)
html = html.replace(
    '<h3 class="text-lg font-bold text-slate-900 dark:text-white">R. L. Stevenson: «Treasure Island»</h3>',
    '<div class="mb-2 p-2 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-800 dark:text-rose-300 text-[11px] font-semibold flex items-center gap-1.5"><i data-lucide="shield-alert" class="w-3.5 h-3.5 text-rose-600 shrink-0"></i> O‘zbekcha tarjima skanerlangan rasm (matn qatlami yo‘q). OCR va tekshiruvgacha chiqarilgan.</div>\n                            <h3 class="text-lg font-bold text-slate-900 dark:text-white">R. L. Stevenson: «Treasure Island»</h3>'
)

# Stevenson button disabled
html = html.replace(
    '<button onclick="app.switchTab(\'corpus\'); corpusManager.filterByBook(\'stevenson\');" class="mt-4 w-full py-2.5 rounded-xl bg-amber-50 dark:bg-amber-950 text-amber-700 dark:text-amber-300 font-bold text-xs hover:bg-indigo-600 hover:text-white transition flex items-center justify-center gap-1.5">\n                            <i data-lucide="search" class="w-3.5 h-3.5"></i> Stivenson asaridan qidirish\n                        </button>',
    '<button disabled class="mt-4 w-full py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-400 font-bold text-xs cursor-not-allowed flex items-center justify-center gap-1.5"><i data-lucide="lock" class="w-3.5 h-3.5"></i> Karantinda (Qidiruv o‘chirilgan)</button>'
)

# 7. Replace Fair Use labels with neutral notice
html = html.replace("PhD ilmiy-tadqiqot (Fair Use)", "Cheklangan ilmiy parcha")
html = html.replace("Jamoat mulki & Fair Use", "Cheklangan ilmiy parcha")

# 8. Add warning banner in Parallel Corpus View
html = html.replace(
    '<section id="view-corpus" class="tab-view hidden space-y-6">',
    '''<section id="view-corpus" class="tab-view hidden space-y-6">
            <!-- Warning Banner required by Stage 2 Stage Gate -->
            <div class="p-4 bg-amber-500/10 border border-amber-500/30 rounded-2xl text-amber-900 dark:text-amber-200 text-xs sm:text-sm font-semibold flex items-center gap-3">
                <i data-lucide="alert-triangle" class="w-5 h-5 text-amber-600 shrink-0"></i>
                <div>
                    <strong>Diqqat (Stage 2–4):</strong> Hemingway va Cho‘lpon parallel jumlalari tekislashi (alignment) qayta ko‘rib chiqilmoqda — ilmiy tahlil uchun foydalanmang.
                </div>
            </div>'''
)

# 9. Neutral legal notice in Footer
neutral_notice = "Korpusdagi matnlar mualliflik huquqi egalariga tegishli. Ular faqat ilmiy tadqiqot maqsadida, cheklangan parchalar ko‘rinishida ko‘rsatiladi. Nusxa ko‘chirish va tarqatish taqiqlanadi."
html = re.sub(
    r'<div class="pt-6 border-t border-slate-100 dark:border-slate-800 text-center text-xs text-slate-400">[\s\S]*?</div>',
    f'<div class="pt-6 border-t border-slate-100 dark:border-slate-800 text-center text-xs text-slate-500 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">{neutral_notice}</div>',
    html
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("-> index.html successfully updated with all Stage 2 requirements!")
