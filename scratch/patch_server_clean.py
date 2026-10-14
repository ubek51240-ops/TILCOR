import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('server.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Clean find_corpus_example
old_find = """    # 3. Clean contextual sentence
    clean_uz = uz_hint.split(';')[0].split(',')[0].strip() if uz_hint else ''
    if clean_uz and clean_uz != q:
        return {
            "en": f"The term '{q}' plays a vital semantic role in literary context.",
            "uz": f"Asarda «{clean_uz}» birligi muhim mazmuniy va uslubiy vazifani bajargan.",
            "book": "Ilmiy-adabiy korpus",
            "source": "Kontekstual qiyosiy model"
        }
    else:
        return {
            "en": f"In parallel corpus analysis, '{q}' illustrates high collocational strength.",
            "uz": f"Parallel korpus tahlilida «{q}» birikmasi yuqori kollokatsion bogʻlanishga ega.",
            "book": "Xalqaro Korpus Standarti",
            "source": "Leksik-assotsiativ tahlil"
        }"""

new_find = """    # No fabrication: if not found in real corpus, return None per EQUIVALENT PRINCIPLE
    return None"""

if old_find in code:
    code = code.replace(old_find, new_find)
    print("find_corpus_example cleaned.")
else:
    print("WARNING: old_find not found!")

# 2. Clean search_corpus
old_search_corpus = """def search_corpus(query='', book='all', limit=100):
    if not FULL_CORPUS:
        return []
    q = query.lower().strip() if query else ''
    matches = []
    for c in FULL_CORPUS:
        if c.get('status') == 'excluded':
            continue
        if book != 'all' and c.get('book') != book:
            continue
        uz = (c.get('uzbek') or c.get('uz') or '')
        en = (c.get('english') or c.get('en') or '')
        cid = (c.get('segmentId') or c.get('id') or '')
        if q:
            if q not in uz.lower() and q not in en.lower() and q not in cid.lower():
                continue
        item = dict(c)
        item['uzbek'] = uz
        item['uz'] = uz
        item['english'] = en
        item['en'] = en
        item['segmentId'] = cid
        item['id'] = cid
        matches.append(item)
        if len(matches) >= limit:
            break
    return matches"""

new_search_corpus = """def search_corpus(query='', book='all', limit=50):
    active = get_active_corpus()
    if not active:
        return []
    limit = min(max(1, limit), 50)
    q = query.lower().strip() if query else ''
    matches = []
    for c in active:
        b_key = (c.get('book') or '').lower()
        if c.get('status') in ['excluded', 'removed_by_researcher'] or b_key == 'stevenson':
            continue
        if book != 'all' and b_key != book.lower():
            continue
        uz = (c.get('uzbek') or c.get('uz') or '')
        en = (c.get('english') or c.get('en') or '')
        cid = (c.get('segmentId') or c.get('id') or '')
        if q:
            if q not in uz.lower() and q not in en.lower() and q not in cid.lower():
                continue
        item = {
            "id": cid,
            "segmentId": cid,
            "book": b_key,
            "bookTitle": c.get('bookTitle', ''),
            "author": c.get('author', ''),
            "translator": c.get('translator', ''),
            "pubYear": c.get('pubYear', ''),
            "publisher": c.get('publisher', ''),
            "license": c.get('license', 'Mualliflik huquqi egalariga tegishli. Faqat ilmiy tadqiqot uchun cheklangan parcha.'),
            "direction": c.get('direction', 'UZ → EN' if b_key == 'cholpon' else 'EN → UZ'),
            "uz": uz,
            "uzbek": uz,
            "en": en,
            "english": en
        }
        matches.append(item)
        if len(matches) >= limit:
            break
    return matches"""

if old_search_corpus in code:
    code = code.replace(old_search_corpus, new_search_corpus)
    print("search_corpus cleaned.")
else:
    print("WARNING: old_search_corpus not found!")

# 3. Clean CALQUE_TRAPS_KNOWLEDGE: remove Stevenson mention
code = code.replace(" (Stivenson, «Treasure Island»)", "")
code = code.replace("Stivenson, «Treasure Island»", "Dengizchilik leksikasi")

# 4. Clean generate_phd_linguistic_response
old_resp = """def generate_phd_linguistic_response(user_prompt):
    prompt_lower = user_prompt.lower()
    
    # Check if asking about collocations, MI, t-score, or calque
    if any(k in prompt_lower for k in ['cold look', 'sovuq nigoh', 'kalka', 'calque']):
        return (
            "### 🎯 PhD Ilmiy Tahlili: «Sovuq nigoh» va Uslubiy Kalkalar\\n\\n"
            "**1. Leksik-semantik muammo:**\\n"
            "Oʻzbek tilidagi *«sovuq nigoh»* metaforik birikmasini ingliz tiliga soʻzma-soʻz ***cold look*** deb tarjima qilish jiddiy **uslubiy zaiflik va kalka (calque)** hisoblanadi. Erkin nutqda tushunarli boʻlsa-da, badiiy va akademik korpuslarda gʻayritabiiy tuyuladi.\\n\\n"
            "**2. Korpus mezonlari (BNC, COCA, Sketch Engine):**\\n"
            "- **Icy stare** (MI: 7.42, T-score: 9.15) — eng yuqori assotsiatsiya koeffitsientiga ega, hissizlik va gʻazabni ifodalaydi.\\n"
            "- **Cold gaze** (MI: 6.85, T-score: 8.30) — barqaror adabiy birikma (Choʻlponning «Kecha va kunduz» tarjimasida Christopher Fort tomonidan qoʻllangan: *«Razzoq Sufi's cold gaze...»*).\\n"
            "- **Frosty glare** (MI: 6.20, T-score: 7.45) — oʻta dushmanona nigoh.\\n\\n"
            "**3. Dissertatsiya tavsiyasi:**\\n"
            "Teng matnlar parallel korpusida kollokatsiyalarni tarjima qilishda *soʻzma-soʻz komponental tarjima* emas, balki *kollokatsion invariantlik prinsipi* qoʻllanishi lozim."
        )
        
    if any(k in prompt_lower for k in ['mi', 't-score', 'tscore', 'formula', 'metod']):
        return (
            "### 📊 PhD Statistik Metodologiyasi: MI va T-Score\\n\\n"
            "**1. Mutual Information (MI-Score):**\\n"
            "$$MI(x,y) = \\\\log_2 \\\\frac{P(x,y)}{P(x)P(y)}$$\\n"
            "- Vazifasi: Ikki soʻzning bir-biriga leksik tortishish kuchini oʻlchaydi.\\n"
            "- Mezon: $MI \\\\ge 3.0$ boʻlsa, turgʻun birikma (kollokatsiya) deb eʼtirof etiladi.\\n\\n"
            "**2. T-Score (Student's t-test):**\\n"
            "$$t = \\\\frac{O - E}{\\\\sqrt{O}}$$\\n"
            "- Vazifasi: Leksik bogʻlanishning korpusdagi statistik ishonchliligini (chastotaliligini) koʻrsatadi.\\n"
            "- Mezon: $t \\\\ge 2.0$ boʻlsa, assotsiatsiya tasodifiy emas deb hisoblanadi.\\n\\n"
            "**3. Parallel Korpusda Qoʻllanishi:**\\n"
            "Tadqiqotimizdagi 5,157 parallel jumla va 6,533 ta ilmiy kollokatsiya aynan ushbu ikki mezon filtridan oʻtkazilgan."
        )

    # General expert response
    return (
        f"### 🎓 PhD Ilmiy Korpus Assistentining Xulosasi\\n\\n"
        f"**Soʻrov tahlili:** «{user_prompt}»\\n\\n"
        "**Ilmiy-lingvistik sharh:**\\n"
        "Oʻzaro faol birikuvchi (kollokatsion) soʻzlar tadqiqi parallel korpus lingvistikasining eng dolzarb yoʻnalishlaridan biridir. "
        "Matnlarni chogʻishtirishda leksik birliklarning valentlik imkoniyatlari, kontekstual semantikasi va turgʻun birikish qonuniyatlari asosiy oʻrin tutadi.\\n\\n"
        "**Korpus maʼlumotlari:**\\n"
        "- Choʻlpon («Kecha va kunduz»), Hemingway («Chol va dengiz») hamda Stevenson («Xazinalar oroli») asarlarining parallel tahlili shuni koʻrsatadiki, kollokatsiyalarning 68% qismi toʻliq yoki konseptual ekvivalentlar orqali beriladi, 32% holatda esa kalka xatolariga yoʻl qoʻyish xavfi mavjud.\\n\\n"
        "**Xulosa:** Badiiy va ilmiy tarjimada erkin soʻz birikmasi bilan kollokatsiyani farqlash tarjima adekvatligining garovidir."
    )"""

new_resp = """def generate_phd_linguistic_response(user_prompt):
    prompt_lower = user_prompt.lower()
    
    if any(k in prompt_lower for k in ['cold look', 'sovuq nigoh', 'kalka', 'calque']):
        return (
            "### 🎯 Leksik-Semantik Tahlil: «Sovuq nigoh» va Uslubiy Kalkalar\\n\\n"
            "**1. Leksik-semantik muammo:**\\n"
            "Oʻzbek tilidagi *«sovuq nigoh»* birikmasini ingliz tiliga soʻzma-soʻz *cold look* deb tarjima qilish uslubiy kalka hisoblanadi. Badiiy asarlarda *cold gaze* yoki *icy stare* barqaror adekvat ekvivalent hisoblanadi.\\n\\n"
            "**2. Asliyatdan dalil:**\\n"
            "Abdulhamid Cho‘lponning «Kecha va kunduz» romani tarjimasida (Christopher Fort): *«cold gaze»* qoʻllangan.\\n\\n"
            "**3. Ekvivalentlik tamoyili:**\\n"
            "Tarjima ekvivalenti faqat tarjimonning kitobdagi real qo'llagan so'zlari asosida qayd etiladi."
        )
        
    if any(k in prompt_lower for k in ['mi', 't-score', 'tscore', 'formula', 'metod', 'logdice']):
        return (
            "### 📊 Statistik Mezonlar Metodologiyasi (1-bob)\\n\\n"
            "**1. logDice va Assotsiatsiya o'lchovlari:**\\n"
            "Kollokatsiyalarning turg'unlik maqomi ma'lumotnoma korpuslar (BNC, O'zbek milliy korpusi / uzWaC) chastotasi asosida baholanadi.\\n\\n"
            "**2. Dissertatsiya standarti:**\\n"
            "Kichik badiiy korpusning xom statistikasi maqomni belgilamaydi. Barcha statistik metrikalar 10-bosqichda kalibrlangan namunalar asosida ko'rsatiladi."
        )

    return (
        f"### 🎓 Lingvistik Tahlil Xulosasi (AI-taklif)\\n\\n"
        f"**Soʻrov:** «{user_prompt}»\\n\\n"
        "**Nazariy sharh:**\\n"
        "Oʻzaro faol birikuvchi (kollokatsion) soʻzlar tadqiqida leksik birliklarning kontekstual ma'nosi va tarjima ekvivalentligi solishtiriladi.\\n"
        "Qiyosiy tahlil faqat bitta asarni o'z tarjimasi bilan jumla-ba-jumla taqqoslash tamoyiliga tayanadi."
    )"""

if old_resp in code:
    code = code.replace(old_resp, new_resp)
    print("generate_phd_linguistic_response cleaned.")
else:
    print("WARNING: old_resp not found!")

# 5. Clean diagnose_text_with_ai fallback
old_diag_fallback = """            traps_md = "- Matnda aniq qoʻpol kalka xatolari aniqlanmadi. Biroq tarjimada erkin soʻz birikmalari oʻrniga leksikografik turgʻun kollokatsiyalarni saqlash zarur."

        # Collocations text
        collocs_md = ""
        if found_collocs:
            collocs_md = "\\n".join([
                f"- **{c['english']}** ⟷ **{c['uzbek']}** [{c['pattern']}] — *MI: {c.get('miScore', 7.2)}, T: {c.get('tScore', 8.5)}*"
                for c in found_collocs
            ])"""

new_diag_fallback = """            traps_md = "- Matnda aniq qoʻpol kalka xatolari aniqlanmadi. Biroq tarjimada erkin soʻz birikmalari oʻrniga leksikografik turgʻun kollokatsiyalarni saqlash zarur."

        # Collocations text
        collocs_md = ""
        if found_collocs:
            collocs_md = "\\n".join([
                f"- **{c['english']}** ⟷ **{c['uzbek']}** [{c.get('pattern', 'Qolip')}]"
                for c in found_collocs
            ])"""

if old_diag_fallback in code:
    code = code.replace(old_diag_fallback, new_diag_fallback)
    print("diagnose_text_with_ai fallback cleaned.")
else:
    print("WARNING: old_diag_fallback not found!")

# 6. Make translate and lab/extract require admin authentication in do_GET and do_POST
old_get_translate = """        # 1. Tarjimon API
        if parsed.path == '/api/translate':
            text = params.get('text', [''])[0]
            sl = params.get('sl', ['uz'])[0]
            tl = params.get('tl', ['en'])[0]
            result = translate_text(text, sl, tl)
            self.send_json(result)
            return"""

new_get_translate = """        # 1. Tarjimon API (Admin only, rate limited)
        if parsed.path == '/api/translate':
            if not self.require_auth('admin'):
                return
            if not check_ai_rate_limit():
                self.send_response(429)
                self.send_json({"error": "Tarjima so'rovlar limiti oshdi."})
                return
            text = params.get('text', [''])[0]
            sl = params.get('sl', ['uz'])[0]
            tl = params.get('tl', ['en'])[0]
            result = translate_text(text, sl, tl)
            self.send_json(result)
            return"""

if old_get_translate in code:
    code = code.replace(old_get_translate, new_get_translate)
    print("do_GET /api/translate protected.")
else:
    print("WARNING: old_get_translate not found!")

old_get_lab = """        # 4.1 Collocation Research Lab: Nomzodlarni ajratish API
        if parsed.path == '/api/lab/extract':
            text = params.get('text', [''])[0]
            result = extract_collocation_candidates(text)
            self.send_json(result)
            return"""

new_get_lab = """        # 4.1 Collocation Research Lab: Nomzodlarni ajratish API (Admin only)
        if parsed.path == '/api/lab/extract':
            if not self.require_auth('admin'):
                return
            text = params.get('text', [''])[0]
            result = extract_collocation_candidates(text)
            self.send_json(result)
            return"""

if old_get_lab in code:
    code = code.replace(old_get_lab, new_get_lab)
    print("do_GET /api/lab/extract protected.")
else:
    print("WARNING: old_get_lab not found!")

old_post_translate = """        if self.path == '/api/translate':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                data = json.loads(body)
                text = data.get('text', '')
                sl = data.get('sl', 'uz')
                tl = data.get('tl', 'en')
                result = translate_text(text, sl, tl)
            except Exception as e:
                result = {"success": False, "error": str(e)}
            self.send_json(result)
            return"""

new_post_translate = """        if self.path == '/api/translate':
            if not self.require_auth('admin'):
                return
            if not check_ai_rate_limit():
                self.send_response(429)
                self.send_json({"error": "Tarjima so'rovlar limiti oshdi."})
                return
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                data = json.loads(body)
                text = data.get('text', '')
                sl = data.get('sl', 'uz')
                tl = data.get('tl', 'en')
                result = translate_text(text, sl, tl)
            except Exception as e:
                result = {"success": False, "error": str(e)}
            self.send_json(result)
            return"""

if old_post_translate in code:
    code = code.replace(old_post_translate, new_post_translate)
    print("do_POST /api/translate protected.")
else:
    print("WARNING: old_post_translate not found!")

old_post_lab = """        if self.path == '/api/lab/extract':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                data = json.loads(body)
                text = data.get('text', '')
                result = extract_collocation_candidates(text)
            except Exception as e:
                result = {"success": False, "error": str(e)}
            self.send_json(result)
            return"""

new_post_lab = """        if self.path == '/api/lab/extract':
            if not self.require_auth('admin'):
                return
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                data = json.loads(body)
                text = data.get('text', '')
                result = extract_collocation_candidates(text)
            except Exception as e:
                result = {"success": False, "error": str(e)}
            self.send_json(result)
            return"""

if old_post_lab in code:
    code = code.replace(old_post_lab, new_post_lab)
    print("do_POST /api/lab/extract protected.")
else:
    print("WARNING: old_post_lab not found!")

# 7. Update /api/stats to compute live numbers without Stevenson
old_stats = """        # 0. Live Stats API (Stage 2)
        if parsed.path == '/api/stats':
            active_c = get_active_corpus()
            active_col = get_active_collocations()
            self.send_json({
                "totalSegments": len(active_c),
                "totalCollocations": len(active_col),
                "totalDictionary": len(DICTIONARY),
                "quarantinedSegments": len(FULL_CORPUS) - len(active_c),
                "quarantinedCollocations": len(COLLOCATIONS) - len(active_col),
                "authenticatedUser": user
            })
            return"""

new_stats = """        # 0. Live Stats API
        if parsed.path == '/api/stats':
            active_c = [c for c in FULL_CORPUS if c.get('status') == 'active' and c.get('book') != 'stevenson']
            active_col = [c for c in COLLOCATIONS if c.get('status') == 'active' and c.get('public_visible') != False]
            active_d = [d for d in DICTIONARY if d.get('status') == 'active' and d.get('public_visible') != False]
            self.send_json({
                "totalSegments": len(active_c),
                "totalCollocations": len(active_col),
                "totalDictionary": len(active_d),
                "booksCount": 2,
                "authenticatedUser": user
            })
            return"""

if old_stats in code:
    code = code.replace(old_stats, new_stats)
    print("/api/stats updated.")
else:
    print("WARNING: old_stats not found!")

# 8. Clamp limit in /api/search
old_search_limit = """        # 2. To'liq Korpus Qidiruv API
        if parsed.path == '/api/search':
            query = params.get('q', [''])[0]
            book = params.get('book', ['all'])[0]
            limit = int(params.get('limit', ['100'])[0])
            results = search_corpus(query, book, limit)
            self.send_json({
                "query": query,
                "book": book,
                "totalFound": len(results),
                "totalCorpus": len(get_active_corpus()),
                "results": results
            })
            return"""

new_search_limit = """        # 2. To'liq Korpus Qidiruv API (≤ 50 results)
        if parsed.path == '/api/search':
            query = params.get('q', [''])[0]
            book = params.get('book', ['all'])[0]
            raw_limit = int(params.get('limit', ['50'])[0])
            limit = min(max(1, raw_limit), 50)
            results = search_corpus(query, book, limit)
            active_c = [c for c in FULL_CORPUS if c.get('status') == 'active' and c.get('book') != 'stevenson']
            self.send_json({
                "query": query,
                "book": book,
                "totalFound": len(results),
                "totalCorpus": len(active_c),
                "results": results
            })
            return"""

if old_search_limit in code:
    code = code.replace(old_search_limit, new_search_limit)
    print("/api/search clamped.")
else:
    print("WARNING: old_search_limit not found!")

# Save patched server.py
with open('server.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("server.py updated successfully.")
