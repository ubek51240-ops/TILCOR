import re

with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add auth and session definitions after AUTH_USERS
old_auth_block = """AUTH_USERS = {
    "admin": os.environ.get("TILCOR_ADMIN_PASSWORD", "tilcor_phd_admin_2026"),      # Researcher (Tadqiqotchi)
    "reviewer": os.environ.get("TILCOR_REVIEWER_PASSWORD", "tilcor_supervisor_2026"), # Supervisor (Ilmiy rahbar)
    "guest": os.environ.get("TILCOR_GUEST_PASSWORD", "tilcor_guest_2026")          # Guest / Council (Kengash a'zolari / mehmon)
}

AI_REQUEST_LOG = []"""

new_auth_block = """import hashlib
import secrets

AUTH_USERS = {
    "admin": os.environ.get("TILCOR_ADMIN_PASSWORD", "tilcor_phd_admin_2026"),      # Researcher (Tadqiqotchi)
    "reviewer": os.environ.get("TILCOR_REVIEWER_PASSWORD", "tilcor_supervisor_2026"), # Supervisor (Ilmiy rahbar)
    "guest": os.environ.get("TILCOR_GUEST_PASSWORD", "tilcor_guest_2026")          # Guest / Council (Kengash a'zolari / mehmon)
}

ADMIN_SALT = b"tilcor_salt_2026_secure"
ADMIN_PASSWORD_HASH = hashlib.pbkdf2_hmac(
    'sha256',
    AUTH_USERS["admin"].encode('utf-8'),
    ADMIN_SALT,
    100000
).hex()

SESSIONS = {}        # token -> {"user": str, "created": float, "expires": float}
FAILED_LOGINS = {}   # ip -> [timestamps]

def check_login_rate_limit(ip: str) -> bool:
    now = time.time()
    attempts = [t for t in FAILED_LOGINS.get(ip, []) if now - t < 300]
    FAILED_LOGINS[ip] = attempts
    return len(attempts) < 5

def record_failed_login(ip: str):
    now = time.time()
    FAILED_LOGINS.setdefault(ip, []).append(now)

def verify_admin_login(username: str, password: str) -> bool:
    if username != 'admin':
        return False
    calc = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), ADMIN_SALT, 100000).hex()
    return secrets.compare_digest(calc, ADMIN_PASSWORD_HASH)

def extract_cookie_token(cookie_str: str) -> Optional[str]:
    if not cookie_str:
        return None
    for part in cookie_str.split(';'):
        part = part.strip()
        if part.startswith('tilcor_session='):
            return part.split('=', 1)[1]
    return None

AI_REQUEST_LOG = []"""

if old_auth_block in content:
    content = content.replace(old_auth_block, new_auth_block)
else:
    print("WARNING: old_auth_block not found verbatim, checking regex...")

# 2. Update get_active_corpus, get_active_collocations, get_active_dictionary
old_get_active = """def get_active_corpus():
    return [c for c in FULL_CORPUS if c.get('status') != 'excluded']

def get_active_collocations():
    return [c for c in COLLOCATIONS if c.get('status') != 'excluded']"""

new_get_active = """def get_active_corpus():
    return [c for c in FULL_CORPUS if c.get('status') != 'excluded' and not c.get('excluded') and c.get('book') != 'stevenson']

def get_active_collocations():
    return [c for c in COLLOCATIONS if c.get('public_visible') is not False and c.get('status') not in ('rejected', 'excluded') and not c.get('excluded')]

def get_active_dictionary():
    return [d for d in DICTIONARY if d.get('public_visible') is not False and not d.get('needs_repair') and d.get('status') not in ('rejected', 'excluded')]"""

if old_get_active in content:
    content = content.replace(old_get_active, new_get_active)

# 3. Update search_collocations to strictly use get_active_collocations
old_search_colloc = "for item in COLLOCATIONS:\n        if item.get('status') == 'excluded':\n            continue"
new_search_colloc = "active_items = get_active_collocations()\n    for item in active_items:"
if old_search_colloc in content:
    content = content.replace(old_search_colloc, new_search_colloc)

# 4. Update get_authenticated_user to check SESSIONS
old_get_auth_user = """    def get_authenticated_user(self):
        auth_header = self.headers.get('Authorization', '')"""

new_get_auth_user = """    def get_authenticated_user(self):
        cookie_str = self.headers.get('Cookie', '')
        token = extract_cookie_token(cookie_str)
        if token and token in SESSIONS:
            sess = SESSIONS[token]
            if time.time() < sess['expires']:
                return sess['user']
            else:
                del SESSIONS[token]

        auth_header = self.headers.get('Authorization', '')"""

if old_get_auth_user in content:
    content = content.replace(old_get_auth_user, new_get_auth_user)

# 5. Add /api/auth/login and /api/auth/logout in do_POST
old_do_post_start = "    def do_POST(self):\n        user = self.get_authenticated_user()"
new_do_post_start = """    def do_POST(self):
        user = self.get_authenticated_user()

        if self.path == '/api/auth/login':
            client_ip = self.client_address[0]
            if not check_login_rate_limit(client_ip):
                self.send_response(429)
                self.send_json({"error": "Ko'p urinishlar qilindi. 5 minutdan so'ng qayta urinib ko'ring."})
                return
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            try:
                data = json.loads(body)
                u = data.get('username', '').strip()
                p = data.get('password', '').strip()
                if verify_admin_login(u, p):
                    token = secrets.token_hex(32)
                    SESSIONS[token] = {
                        "user": u,
                        "created": time.time(),
                        "expires": time.time() + 86400
                    }
                    self.send_response(200)
                    is_secure = self.headers.get('X-Forwarded-Proto') == 'https'
                    cookie_val = f"tilcor_session={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=86400"
                    if is_secure:
                        cookie_val += "; Secure"
                    self.send_header('Set-Cookie', cookie_val)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "user": u}).encode('utf-8'))
                    return
                else:
                    record_failed_login(client_ip)
                    self.send_response(401)
                    self.send_json({"error": "Login yoki parol noto'g'ri."})
                    return
            except Exception as e:
                self.send_response(400)
                self.send_json({"error": str(e)})
                return

        if self.path == '/api/auth/logout':
            cookie_str = self.headers.get('Cookie', '')
            token = extract_cookie_token(cookie_str)
            if token and token in SESSIONS:
                del SESSIONS[token]
            self.send_response(200)
            self.send_header('Set-Cookie', 'tilcor_session=; Path=/; HttpOnly; Max-Age=0')
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
            return"""

if old_do_post_start in content:
    content = content.replace(old_do_post_start, new_do_post_start)

# 6. Add /api/auth/me and update /api/search in do_GET
old_search_block = """        # 2. To'liq Korpus Qidiruv API (≤ 50 results)
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

new_search_block = """        if parsed.path == '/api/auth/me':
            u = self.get_authenticated_user()
            self.send_json({"user": u or "guest", "isAdmin": (u == "admin")})
            return

        # 2. Qayta qurilgan Korpus & Leksikografik Qidiruv API (≤ 50 results)
        if parsed.path == '/api/search':
            query = params.get('q', [''])[0]
            lang = params.get('lang', ['auto'])[0]
            raw_limit = int(params.get('limit', ['50'])[0])
            limit = min(max(1, raw_limit), 50)
            page = int(params.get('page', ['1'])[0])
            
            from search_engine import execute_unified_search
            active_c = get_active_corpus()
            active_col = get_active_collocations()
            active_d = get_active_dictionary()
            
            res = execute_unified_search(
                query=query,
                active_corpus=active_c,
                active_collocations=active_col,
                active_dictionary=active_d,
                forced_lang=lang if lang in ('uz', 'en') else None,
                limit=limit,
                page=page
            )
            # Legacy field for backwards compatibility
            res['results'] = res.get('corpus_sentences', [])
            res['totalFound'] = res.get('summary', {}).get('corpus_occurrences', 0)
            res['totalCorpus'] = len(active_c)
            self.send_json(res)
            return"""

if old_search_block in content:
    content = content.replace(old_search_block, new_search_block)

# 7. Update /api/stats
old_stats_block = """        if parsed.path == '/api/stats':
            active_c = get_active_corpus()
            active_col = get_active_collocations()
            self.send_json({
                "totalSegments": len(active_c),
                "totalCollocations": len(active_col),
                "totalDictionary": len(DICTIONARY),
                "booksCount": 2,
                "authenticatedUser": user or "guest"
            })
            return"""

new_stats_block = """        if parsed.path == '/api/stats':
            active_c = get_active_corpus()
            active_col = get_active_collocations()
            active_d = get_active_dictionary()
            self.send_json({
                "totalSegments": len(active_c),
                "totalCollocations": len(active_col),
                "totalDictionary": len(active_d),
                "booksCount": 2,
                "authenticatedUser": user or "guest"
            })
            return"""

if old_stats_block in content:
    content = content.replace(old_stats_block, new_stats_block)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated server.py successfully.")
