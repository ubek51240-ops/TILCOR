with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix regex lines
text = text.replace(
    'html_str = re.sub(r\'<html\\s+lang=["\'][^"\']*["\']\', f\'<html lang="{lang}"\', html_str, count=1)',
    'html_str = re.sub(r\'<html\\s+lang=[\"\\\'][^\"\\\']*[\"\\\']\', f\'<html lang="{lang}"\', html_str, count=1)'
)
# Let's fix line 1696 directly
bad_line = 'html_str = re.sub(r\'<html\\s+lang=[\"\'][^\"\']*[\"\']\', f\'<html lang=\"{lang}\"\', html_str, count=1)'
# Or let's replace the whole render_localized_html function with pure clean code
start_idx = text.find('def render_localized_html(')
end_idx = text.find('class AppRequestHandler', start_idx)

clean_func = '''def render_localized_html(html_str, lang='uz', is_admin=False, query_params=None, req_path='/'):
    if not query_params:
        query_params = {}

    locales_file = os.path.join(DIRECTORY, 'locales', f'{lang}.json')
    loc = {}
    if os.path.exists(locales_file):
        try:
            with open(locales_file, 'r', encoding='utf-8') as f:
                loc = json.load(f)
        except Exception:
            pass

    # 1. Update <html lang="...">
    html_str = re.sub(r'<html\\s+lang=[\'"][^\'"]*[\'"]', f'<html lang="{lang}"', html_str, count=1)
    if lang == 'en':
        html_str = re.sub(r'<title>.*?TILCOR.*?</title>', '<title>TILCOR — Uzbek–English Parallel Corpus</title>', html_str, flags=re.DOTALL)
    elif lang == 'ru':
        html_str = re.sub(r'<title>.*?TILCOR.*?</title>', '<title>TILCOR — Узбекско-английский параллельный корпус</title>', html_str, flags=re.DOTALL)

    # 2. Add hreflang tags and Tailwind script if not present
    if '</head>' in html_str:
        if '<link rel="alternate" hreflang="uz"' not in html_str:
            hreflang_tags = (
                '\\n    <link rel="alternate" hreflang="uz" href="?lang=uz" />'
                '\\n    <link rel="alternate" hreflang="en" href="?lang=en" />'
                '\\n    <link rel="alternate" hreflang="ru" href="?lang=ru" />\\n'
            )
            html_str = html_str.replace('</head>', f'{hreflang_tags}</head>', 1)
        if 'cdn.tailwindcss.com' not in html_str:
            tw_tag = '\\n    <script src="https://cdn.tailwindcss.com"></script>\\n'
            html_str = html_str.replace('</head>', f'{tw_tag}</head>', 1)

    # 3. Replace Navigation Header with Unified Nav Component
    nav_html = ui_components.render_nav(lang, req_path, is_admin)
    html_str = re.sub(r'<header\\b[^>]*>.*?</header>', nav_html, html_str, count=1, flags=re.DOTALL)

    # 4. Replace Footer with Unified Footer Component
    footer_html = ui_components.render_footer(lang)
    html_str = re.sub(r'<footer\\b[^>]*>.*?</footer>', footer_html, html_str, count=1, flags=re.DOTALL)

    # 5. Remove Admin sections for logged-out visitors per Task 2
    if not is_admin:
        html_str = re.sub(r'<div[^>]*id=[\'"]nav-laboratoriya[\'"][^>]*>.*?</div>\\s*</div>', '', html_str, flags=re.DOTALL)
        html_str = re.sub(r'<div[^>]*id=[\'"]nav-laboratoriya-mobile[\'"][^>]*>.*?</div>', '', html_str, flags=re.DOTALL)
        html_str = re.sub(r'<section[^>]*id=[\'"]view-translator[\'"][^>]*>.*?</section>', '', html_str, flags=re.DOTALL)
        html_str = re.sub(r'<section[^>]*id=[\'"]view-checker[\'"][^>]*>.*?</section>', '', html_str, flags=re.DOTALL)
        html_str = re.sub(r'<section[^>]*id=[\'"]view-phd[\'"][^>]*>.*?</section>', '', html_str, flags=re.DOTALL)
        html_str = re.sub(r'<div[^>]*class=[\'"][^\'"]*security-section[^\'"]*[\'"][^>]*>.*?</div>\\s*</div>', '', html_str, flags=re.DOTALL)
        html_str = re.sub(r'<h3>🛡️ Kirish Huquqlari va Xavfsizlik Arxitekturasi.*?</div>\\s*</div>\\s*</div>', '', html_str, flags=re.DOTALL)
        html_str = re.sub(r'<div id=[\'"]licenceModal[\'"].*?</div>\\s*</div>', '', html_str, flags=re.DOTALL)
        for admin_term in ['admin_collocations', 'preview_alignment_queue', 'Jonli Tarjimon', 'PhD Hub', 'sinovchisi']:
            if admin_term in html_str:
                html_str = re.sub(rf'<[^>]*href=[\'"][^\'"]*{admin_term}[^\'"]*[\'"][^>]*>.*?</[^>]+>', '', html_str)

    # 6. Live numbers from database on home page per Part 12.1
    active_c = get_active_corpus()
    cholpon_count = sum(1 for s in active_c if s.get('book') == 'cholpon')
    hemingway_count = sum(1 for s in active_c if s.get('book') == 'hemingway')
    total_segments = len(active_c)

    c_fmt_sp = ui_components.format_number(cholpon_count, lang)
    h_fmt_sp = ui_components.format_number(hemingway_count, lang)
    t_fmt_sp = ui_components.format_number(total_segments, lang)

    for old_c in ['2 471', '2,471', '6 823', '6,823']:
        html_str = html_str.replace(old_c, c_fmt_sp)
    for old_h in ['1 340', '1,340', '1 532', '1,532']:
        html_str = html_str.replace(old_h, h_fmt_sp)
    for old_t in ['3 811', '3,811', '8 355', '8,355']:
        html_str = html_str.replace(old_t, t_fmt_sp)
    html_str = html_str.replace('Ibrohim G‘afurov', 'Ibrohim G‘ofurov')

    # 7. Replace data-i18n attributes
    def repl_i18n(m):
        tag_start = m.group(1)
        key = m.group(2)
        tag_close = m.group(3)
        inner = m.group(4)
        tag_end = m.group(5)
        trans = loc.get(key)
        if trans:
            icon_match = re.search(r'(<i\\s+data-lucide=[^>]+></i>)', inner)
            if icon_match:
                return f"{tag_start}{key}{tag_close}{icon_match.group(1)} {trans}{tag_end}"
            return f"{tag_start}{key}{tag_close}{trans}{tag_end}"
        return m.group(0)

    html_str = re.sub(r'(<[^>]*\\bdata-i18n=[\'"])([^\'"]+)([\'"][^>]*>)(.*?)(</[^>]+>)', repl_i18n, html_str, flags=re.DOTALL)

    # 8. Replace data-i18n-placeholder
    def repl_placeholder(m):
        key = m.group(1)
        trans = loc.get(key)
        if trans:
            return f'placeholder="{trans}" data-i18n-placeholder="{key}"'
        return m.group(0)
    html_str = re.sub(r'placeholder=[\'"][^\'"]*[\'"]\\s+data-i18n-placeholder=[\'"]([^\'"]+)[\'"]', repl_placeholder, html_str)

    return html_str

'''

text = text[:start_idx] + clean_func + text[end_idx:]
with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Fixed render_localized_html')
