import re
import os

BASE_DIR = r"C:\Users\user\Desktop\tarjimon"

# 1. Clean index.html
index_path = os.path.join(BASE_DIR, "index.html")
with open(index_path, "r", encoding="utf-8") as f:
    idx_content = f.read()

# Remove view-translator, view-checker, view-phd
idx_content = re.sub(r'<!--\s*=+\s*-->\s*<!--\s*VIEW:\s*TRANSLATOR.*?<!--\s*=+\s*-->\s*<!--\s*VIEW\s*10:', '<!-- ============================================== -->\n        <!-- VIEW 10:', idx_content, flags=re.DOTALL)
# In case the regex didn't catch both or boundaries differed:
for sec_id in ['view-translator', 'view-checker', 'view-phd']:
    idx_content = re.sub(rf'<section\s+id=["\']{sec_id}["\'].*?</section>', '', idx_content, flags=re.DOTALL)

# Remove nav-laboratoriya from desktop and mobile in index.html
idx_content = re.sub(r'<div\s+id=["\']nav-laboratoriya["\'].*?</div>\s*</div>', '', idx_content, flags=re.DOTALL)
idx_content = re.sub(r'<div\s+id=["\']nav-laboratoriya-mobile["\'].*?</div>', '', idx_content, flags=re.DOTALL)

# Remove Stage warning banner and Stage comments
idx_content = re.sub(r'<!--\s*Warning Banner required by Stage 2 Stage Gate\s*-->.*?</div>\s*</div>', '', idx_content, flags=re.DOTALL)
idx_content = re.sub(r'<!--.*?Stage.*?-->', '', idx_content)
idx_content = re.sub(r'<strong>Diqqat \(Stage 2–4\):</strong>.*?</div>', '', idx_content)

# Update action buttons to real links with data-i18n
idx_content = re.sub(
    r'<button\s+onclick=["\']app\.switchTab\(.corpus.\)["\'][^>]*>\s*Korpusni ochish.*?</button>',
    '<a href="/korpus" class="w-full py-2 rounded-xl bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-bold text-xs hover:bg-indigo-600 hover:text-white transition flex items-center justify-center gap-1.5" data-i18n="btn_open_corpus">Korpusni ochish <i data-lucide="arrow-right" class="w-3 h-3"></i></a>',
    idx_content
)
idx_content = re.sub(
    r'<button\s+onclick=["\']app\.switchTab\(.collocations.\)["\'][^>]*>\s*Kollokatsiyalarni ko‘rish.*?</button>',
    '<a href="/kollokatsiyalar" class="w-full py-2 rounded-xl bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 font-bold text-xs hover:bg-emerald-600 hover:text-white transition flex items-center justify-center gap-1.5" data-i18n="btn_view_collocations">Kollokatsiyalarni ko‘rish <i data-lucide="arrow-right" class="w-3 h-3"></i></a>',
    idx_content
)
idx_content = re.sub(
    r'<button\s+onclick=["\']app\.switchTab\(.dictionary.\)["\'][^>]*>\s*Lug‘atni ochish.*?</button>',
    '<a href="/lugat" class="w-full py-2 rounded-xl bg-amber-50 dark:bg-amber-950 text-amber-700 dark:text-amber-300 font-bold text-xs hover:bg-amber-600 hover:text-white transition flex items-center justify-center gap-1.5" data-i18n="btn_open_dictionary">Lug‘atni ochish <i data-lucide="arrow-right" class="w-3 h-3"></i></a>',
    idx_content
)
idx_content = re.sub(
    r'<a\s+href=["\']methodology\.html["\'][^>]*>\s*<span>Metodologiya sahifasiga o‘tish</span>.*?</a>',
    '<a href="/methodology.html" class="inline-flex items-center gap-1.5 font-bold text-indigo-600 dark:text-indigo-400 hover:underline shrink-0" data-i18n="btn_go_methodology"><span>Metodologiya sahifasiga o‘tish</span> <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i></a>',
    idx_content
)
idx_content = re.sub(
    r'<button\s+onclick=["\']app\.switchTab\(.corpus.\);\s*corpusManager\.filterByBook\(.cholpon.\);["\'][^>]*>\s*Ushbu romandan qidirish\s*→\s*</button>',
    '<a href="/qidiruv?kitob=kvk" class="mt-3 text-xs text-indigo-600 font-semibold hover:underline flex items-center gap-1" data-i18n="btn_search_novel">Ushbu romandan qidirish →</a>',
    idx_content
)
idx_content = re.sub(
    r'<button\s+onclick=["\']app\.switchTab\(.corpus.\);\s*corpusManager\.filterByBook\(.hemingway.\);["\'][^>]*>\s*Ushbu qissadan qidirish\s*→\s*</button>',
    '<a href="/qidiruv?kitob=oms" class="mt-3 text-xs text-emerald-600 font-semibold hover:underline flex items-center gap-1" data-i18n="btn_search_novella">Ushbu qissadan qidirish →</a>',
    idx_content
)

# Wrap hero search in form
old_search_box = re.search(r'(<div class="bg-white rounded-2xl p-2 shadow-lg flex flex-col sm:flex-row items-stretch sm:items-center gap-2">.*?</div>\s*</div>)', idx_content, flags=re.DOTALL)
if old_search_box:
    new_search_form = '''<form action="/qidiruv" method="GET" class="bg-white rounded-2xl p-2 shadow-lg flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                            <div class="flex items-center pl-3 text-slate-400">
                                <i data-lucide="search" class="w-5 h-5 text-indigo-600"></i>
                            </div>
                            <input type="text" name="q" id="homeSearchInput" data-i18n-placeholder="search_placeholder" placeholder="So‘z yoki birikmani qidiring (masalan: yurak, ko‘ngil, qaror, heart, decision)..." class="flex-grow px-3 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none">
                            <div class="flex items-center gap-1.5 border-t sm:border-t-0 sm:border-l border-slate-200 pt-2 sm:pt-0 sm:pl-2">
                                <select name="lang_filter" id="homeSearchLang" class="text-xs py-2 px-2 bg-slate-50 rounded-lg text-slate-700 border border-slate-200 focus:outline-none font-semibold">
                                    <option value="all">UZ / EN</option>
                                    <option value="en">English (EN)</option>
                                    <option value="uz">O‘zbekcha (UZ)</option>
                                </select>
                                <button type="submit" class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 whitespace-nowrap">
                                    <span data-i18n="search_button">Qidirish</span>
                                    <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
                                </button>
                            </div>
                        </form>'''
    idx_content = idx_content.replace(old_search_box.group(1), new_search_form, 1)

with open(index_path, "w", encoding="utf-8") as f:
    f.write(idx_content)
print("Updated index.html")

# 2. Clean kirish.html
kirish_path = os.path.join(BASE_DIR, "kirish.html")
with open(kirish_path, "r", encoding="utf-8") as f:
    kirish_content = f.read()

kirish_content = kirish_content.replace('placeholder="admin / reviewer / guest"', 'data-i18n-placeholder="username_password" placeholder="Foydalanuvchi nomi"')
kirish_content = re.sub(r'<div class="border-t border-slate-700/60 pt-4 text-center">.*?</div>', '', kirish_content, flags=re.DOTALL)
kirish_content = kirish_content.replace("Tadqiqotchi Portali", "Xavfsiz Kirish")
kirish_content = kirish_content.replace("Dissertatsiya platformasi maʼmuriy boshqaruv kabineti", "Dissertatsiya platformasiga kirish")

with open(kirish_path, "w", encoding="utf-8") as f:
    f.write(kirish_content)
print("Updated kirish.html")

# 3. Clean sources_rights.html
sources_path = os.path.join(BASE_DIR, "sources_rights.html")
with open(sources_path, "r", encoding="utf-8") as f:
    src_content = f.read()

src_content = src_content.replace("Stage 4 bosqichida", "tadqiqot davomida")
src_content = src_content.replace(" (Stage 10)", "")
src_content = re.sub(r'<div class="security-section">.*?<!-- \/security-section -->', '', src_content, flags=re.DOTALL)
src_content = re.sub(r'<h3>🛡️ Kirish Huquqlari va Xavfsizlik Arxitekturasi.*?</div>\s*</div>\s*</div>', '', src_content, flags=re.DOTALL)
src_content = re.sub(r'<div id="licenceModal".*?</div>\s*</div>', '', src_content, flags=re.DOTALL)

with open(sources_path, "w", encoding="utf-8") as f:
    f.write(src_content)
print("Updated sources_rights.html")
