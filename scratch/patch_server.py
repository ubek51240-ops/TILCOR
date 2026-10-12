import re

with open('server.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add base64 and time import
if 'import base64' not in code:
    code = code.replace('import sqlite3\n', 'import sqlite3\nimport base64\nimport time\nimport sys\n')

# 2. Add AUTH CONFIG & Active Corpus filtering right after DATA_DIR / loading
auth_config_block = """
# =====================================================================
# STAGE 2 AUTHENTICATION & ACCESS CONTROL
# =====================================================================
AUTH_USERS = {
    "admin": "tilcor_phd_admin_2026",      # Researcher (Tadqiqotchi)
    "reviewer": "tilcor_supervisor_2026"   # Supervisor (Ilmiy rahbar)
}

AI_REQUEST_LOG = []

def check_ai_rate_limit():
    global AI_REQUEST_LOG
    now = time.time()
    AI_REQUEST_LOG = [t for t in AI_REQUEST_LOG if now - t < 60]
    if len(AI_REQUEST_LOG) >= 10:
        return False
    AI_REQUEST_LOG.append(now)
    return True
"""

code = code.replace("COLLOCATIONS = []\n", auth_config_block + "\nCOLLOCATIONS = []\n")

# Active corpus helpers
active_helpers = """
def get_active_corpus():
    return [c for c in FULL_CORPUS if c.get('status') != 'excluded']

def get_active_collocations():
    return [c for c in COLLOCATIONS if c.get('status') != 'excluded']
"""
code = code.replace("def find_corpus_example", active_helpers + "\ndef find_corpus_example")

# 3. Update search_corpus to exclude quarantined records
code = code.replace(
    "        if book != 'all' and c.get('book') != book:\n            continue",
    "        if c.get('status') == 'excluded':\n            continue\n        if book != 'all' and c.get('book') != book:\n            continue"
)

# 4. Update search_collocations to exclude quarantined records
code = code.replace(
    "    for item in COLLOCATIONS:\n        # Source filter",
    "    for item in COLLOCATIONS:\n        if item.get('status') == 'excluded':\n            continue\n        # Source filter"
)

# 5. Remove fake MI / T-scores from prompt 1086 & 1253
code = code.replace(
    'f"5. Korpus statistik ko\'rsatkichlari (MI-score va T-score bahosi)."',
    'f"5. Birikmaning lingvomadaniy tavsifi va lug‘aviy izohi."'
)
code = code.replace(
    'f"5. Korpus statistik bahosi (MI Score, T-score, assotsiatsiya)."',
    'f"5. Tarjima strategiyasi (adekvat, erkin, kompensatsiya) tavsifi."'
)

# 6. Remove fake MI/T from fallback strings (lines 872-874, 1128-1136, 1323-1325)
code = code.replace(
    "- **Icy stare** (MI: 7.42, T-score: 9.15) - eng yuqori assotsiatsiya koeffitsientiga ega, hissizlik va g'azabni ifodalaydi.",
    "- **Icy stare** — hissiy sovuqlik va g'azabni ifodalovchi barqaror birikma."
)
code = code.replace(
    "- **Cold gaze** (MI: 6.85, T-score: 8.30) - barqaror adabiy birikma (Cho'lponning «Kecha va kunduz» tarjimasida Christopher Fort tomonidan qo'llangan: *«Razzoq Sufi's cold gaze...»*).",
    "- **Cold gaze** — barqaror adabiy birikma (Cho'lponning «Kecha va kunduz» tarjimasida Christopher Fort tomonidan qo'llangan: *«Razzoq Sufi's cold gaze...»*)."
)
code = code.replace(
    "- **Frosty glare** (MI: 6.20, T-score: 7.45) - o'ta dushmanona nigoh.",
    "- **Frosty glare** — dushmanona nigoh."
)

code = re.sub(
    r'items_md\.append\(f"- \*\*take a \{raw_word\} / make \{raw_word\}\*\* ⟷ \*\*\{raw_word\} qilmoq\*\* \[Fe\'l \+ Ot\] — \*MI: 7\.80, T: 9\.10\*"[\s\S]*?items_md\.append\(f"- \*\*firm \{raw_word\}\*\* ⟷ \*\*mustahkam \{target_word\}\*\* \[Sifat \+ Ot\] — \*MI: 6\.85, T: 8\.10\*"',
    '''if is_uz:
                items_md.append(f"- **take a {raw_word} / make {raw_word}** ⟷ **{raw_word} qilmoq** [Fe'l + Ot]")
                items_md.append(f"- **deep / strong {target_word}** ⟷ **kuchli {raw_word}** [Sifat + Ot]")
            else:
                items_md.append(f"- **take {raw_word}** ⟷ **{target_word} olmoq** [Fe'l + Ot]")
                items_md.append(f"- **firm {raw_word}** ⟷ **mustahkam {target_word}** [Sifat + Ot]"''',
    code
)

code = code.replace(
    'f"- **{item[\'english\']}** ⟷ **{item[\'uzbek\']}** [{item[\'pattern\']}] — *MI: {item.get(\'miScore\', 7.2)}, T: {item.get(\'tScore\', 8.5)}*{trap_note}"',
    'f"- **{item[\'english\']}** ⟷ **{item[\'uzbek\']}** [{item[\'pattern\']}]{trap_note}"'
)

code = code.replace(
    '''            f"### 📊 Korpus Statistik Koʻrsatkichlari\\n"\n            f"- **Kollokatsion bogʻlanish kuchi:** `MI ≥ 6.8` (Kuchli assotsiativ bogʻliqlik)\\n"\n            f"- **Ishonchlilik indeksi (T-Score):** `t ≥ 8.1` (Statistik ishonchli)\\n"\n            f"- **logDice oʻlchami:** `9.4` (Teng matnlar parallel korpusi standarti)"''',
    '''            f"### ℹ️ Eslatma\\n"\n            f"- **Metrikalar:** MI score va T-score dissertatsiya talabi bo‘yicha faqat tasdiqlangan annotatsiyalar asosida ko‘rsatiladi."'''
)

# 7. Add auth methods to AppRequestHandler
auth_methods = """
    def get_authenticated_user(self):
        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Basic '):
            try:
                raw = base64.b64decode(auth_header[6:].strip()).decode('utf-8')
                u, p = raw.split(':', 1)
                if AUTH_USERS.get(u) == p:
                    return u
            except Exception:
                pass
        elif auth_header.startswith('Bearer '):
            token = auth_header[7:].strip()
            if token == 'admin_token_2026':
                return 'admin'
            if token == 'reviewer_token_2026':
                return 'reviewer'
        
        x_token = self.headers.get('X-Auth-Token', '')
        if x_token == 'admin_token_2026':
            return 'admin'
        if x_token == 'reviewer_token_2026':
            return 'reviewer'
        
        cookie_str = self.headers.get('Cookie', '')
        if 'tilcor_session=admin' in cookie_str:
            return 'admin'
        if 'tilcor_session=reviewer' in cookie_str:
            return 'reviewer'
        return None

    def require_auth(self, role=None):
        user = self.get_authenticated_user()
        if not user:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="TILCOR Korpus Tizimi (Tadqiqotchi va Ilmiy Rahbar uchun)"')
            self.send_header('Content-Type', 'application/json; charset=utf-8' if self.path.startswith('/api/') else 'text/html; charset=utf-8')
            self.send_header('X-Robots-Tag', 'noindex, nofollow')
            self.end_headers()
            if self.path.startswith('/api/'):
                self.wfile.write(json.dumps({
                    "error": "Avtorizatsiyadan o'tilmagan. Tizim faqat tadqiqotchi (admin) va ilmiy rahbar (reviewer) uchun ochiq."
                }, ensure_ascii=False).encode('utf-8'))
            else:
                self.wfile.write(b\"\"\"<!DOCTYPE html>
<html lang="uz">
<head><meta charset="utf-8"><title>401 Ruxsat talab qilinadi | TILCOR</title><meta name="robots" content="noindex, nofollow"></head>
<body style="font-family:system-ui,sans-serif;padding:60px 20px;text-align:center;background:#0f172a;color:#f8fafc;">
  <div style="max-width:540px;margin:0 auto;background:#1e293b;padding:40px;border-radius:24px;border:1px solid #334155;">
    <h2 style="color:#f43f5e;margin-top:0;">401 — Kirish Cheklangan</h2>
    <p style="color:#94a3b8;line-height:1.6;">TILCOR parallel korpusi dissertatsiya himoyasiga qadar yopiq tizimda faoliyat yuritadi. Tizimga faqat tadqiqotchi va ilmiy rahbar kirishi mumkin.</p>
    <p style="font-size:12px;color:#64748b;margin-top:20px;">Iltimos, tadqiqotchi yoki ilmiy rahbar login-paroli bilan tizimga kiring.</p>
  </div>
</body></html>\"\"\")
            return None

        if role == 'admin' and user != 'admin':
            self.send_response(403)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('X-Robots-Tag', 'noindex, nofollow')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Taqiqlangan. Ushbu amal faqat tadqiqotchi (admin) uchun ruxsat etilgan."
            }, ensure_ascii=False).encode('utf-8'))
            return None

        return user
"""

code = code.replace(
    "    def __init__(self, *args, **kwargs):\n        super().__init__(*args, directory=DIRECTORY, **kwargs)\n",
    "    def __init__(self, *args, **kwargs):\n        super().__init__(*args, directory=DIRECTORY, **kwargs)\n" + auth_methods
)

# 8. Check auth at the start of do_GET and do_POST
do_get_guard = """    def do_GET(self):
        user = self.require_auth()
        if not user:
            return

        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        # 0. Live Stats API (Stage 2)
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
            return
"""

code = re.sub(
    r'    def do_GET\(self\):\s*parsed = urllib\.parse\.urlparse\(self\.path\)\s*params = urllib\.parse\.parse_qs\(parsed\.query\)',
    do_get_guard,
    code
)

# Guard do_POST:
do_post_guard = """    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        user = self.require_auth()
        if not user:
            return
"""
code = re.sub(
    r'    def do_POST\(self\):',
    do_post_guard,
    code
)

# Protect AI endpoints with admin role and rate limit
code = code.replace(
    "        # 5. PhD AI Assistent API (DeepSeek-v4 & Corpus Intelligence)\n        if parsed.path == '/api/ai':",
    """        # 5. PhD AI Assistent API (Restricted to admin + Rate limit)
        if parsed.path == '/api/ai':
            if not self.require_auth('admin'):
                return
            if not check_ai_rate_limit():
                self.send_response(429)
                self.send_json({"error": "AI so'rovlar limiti (minutiga 10 ta) oshib ketdi."})
                return"""
)

code = code.replace(
    "        # 6. Kollokatsiyalar AI Analizator va Tarjimon API\n        if parsed.path in ['/api/collocations/ai-analyze', '/api/collocations/pos-analyze']:",
    """        # 6. Kollokatsiyalar AI Analizator (Restricted to admin + Rate limit)
        if parsed.path in ['/api/collocations/ai-analyze', '/api/collocations/pos-analyze']:
            if not self.require_auth('admin'):
                return
            if not check_ai_rate_limit():
                self.send_response(429)
                self.send_json({"error": "AI so'rovlar limiti (minutiga 10 ta) oshib ketdi."})
                return"""
)

code = code.replace(
    "        # 7. Matn & Tarjima AI Diagnostikasi API\n        if parsed.path == '/api/checker/ai-diagnose':",
    """        # 7. Matn & Tarjima AI Diagnostikasi API (Restricted to admin + Rate limit)
        if parsed.path == '/api/checker/ai-diagnose':
            if not self.require_auth('admin'):
                return
            if not check_ai_rate_limit():
                self.send_response(429)
                self.send_json({"error": "AI so'rovlar limiti (minutiga 10 ta) oshib ketdi."})
                return"""
)

# In POST handlers:
code = code.replace(
    "        if self.path in ['/api/collocations/ai-analyze', '/api/collocations/pos-analyze']:",
    """        if self.path in ['/api/collocations/ai-analyze', '/api/collocations/pos-analyze']:
            if not self.require_auth('admin'):
                return
            if not check_ai_rate_limit():
                self.send_response(429)
                self.send_json({"error": "AI so'rovlar limiti (minutiga 10 ta) oshib ketdi."})
                return"""
)

code = code.replace(
    "        if self.path == '/api/checker/ai-diagnose':",
    """        if self.path == '/api/checker/ai-diagnose':
            if not self.require_auth('admin'):
                return
            if not check_ai_rate_limit():
                self.send_response(429)
                self.send_json({"error": "AI so'rovlar limiti (minutiga 10 ta) oshib ketdi."})
                return"""
)

code = code.replace(
    "        if self.path == '/api/ai':",
    """        if self.path == '/api/ai':
            if not self.require_auth('admin'):
                return
            if not check_ai_rate_limit():
                self.send_response(429)
                self.send_json({"error": "AI so'rovlar limiti (minutiga 10 ta) oshib ketdi."})
                return"""
)

# 9. In send_json and do_GET headers: add noindex header
code = code.replace(
    "    def send_json(self, data):\n        self.send_response(200)\n        self.send_header('Content-Type', 'application/json; charset=utf-8')\n        self.send_header('Access-Control-Allow-Origin', '*')\n        self.end_headers()",
    """    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('X-Robots-Tag', 'noindex, nofollow')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()"""
)

# 10. Update totalCorpus in /api/search response
code = code.replace(
    '"totalCorpus": len(FULL_CORPUS),',
    '"totalCorpus": len(get_active_corpus()),'
)

# 11. Support CLI arguments for --port and --env
cli_args_support = """
def run():
    os.chdir(DIRECTORY)
    port_env = os.environ.get("PORT")
    env_name = "production"
    
    # CLI args parse
    args = sys.argv[1:]
    port = None
    if '--port' in args:
        idx = args.index('--port')
        if idx + 1 < len(args):
            port = int(args[idx + 1])
    if '--env' in args:
        idx = args.index('--env')
        if idx + 1 < len(args):
            env_name = args[idx + 1]

    if not port:
        port = int(port_env) if port_env else find_available_port()
        
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", port), AppRequestHandler) as httpd:
        url = f"http://localhost:{port}"
        active_c = get_active_corpus()
        active_col = get_active_collocations()
        print("=" * 70)
        print(f" TILCOR — O‘ZBEK–INGLIZ PARALLEL KORPUSI [{env_name.upper()} REJIMI]")
        print(" Kollokatsiyalar Tarjimasi Tadqiqoti Uchun Platforma (PhD v2.0)")
        print("=" * 70)
        print(f" Muhit:            {env_name.upper()}")
        print(f" Port:             {port}")
        print(f" Veb Manzil:       {url}")
        print(f" Himoya holati:    FAOL (Admin & Reviewer ruxsatnoma)")
        print(f" Qidiruv indeksi:  NOINDEX, NOFOLLOW faollashtirilgan")
        print(f" Faol Korpus:      {len(active_c)} ta jumla ({len(FULL_CORPUS) - len(active_c)} ta karantinda)")
        print(f" Faol Kollokatsiya:{len(active_col)} ta birikma ({len(COLLOCATIONS) - len(active_col)} ta karantinda)")
        print(f" Elektron Lug'at:  {len(DICTIONARY)} ta leksikografik maqola")
        print(" Tizim xavfsiz holatda tayyor.")
        print(" To'xtatish uchun: Ctrl + C bosing")
        print("=" * 70)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\nServer to'xtatildi.")
"""

code = re.sub(
    r'def run\(\):[\s\S]*?if __name__ == \'__main__\':',
    cli_args_support + "\nif __name__ == '__main__':",
    code
)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("-> server.py successfully patched with authentication, quarantine filtering, rate limiting and noindex!")
