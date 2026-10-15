"""Server-rendered pages of the public TILCOR site (Uzbek, English, Russian interface).

Design: a facing-page edition. The original and the translation stand side by side; gold marks the
searched word in the original, Bukhara turquoise marks the translator's equivalent. Styles: css/tilcor.css.
Every interface string comes from locales/<lang>.json; numbers are passed in from live data.
The code avoids f-string features newer than Python 3.8, so it runs on older servers too.
"""
import os
import json
import html
import re
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCALES_DIR = os.path.join(BASE_DIR, 'locales')
CSS_VERSION = '3.7.1'

_LOCALES = {}
for _l in ('uz', 'en', 'ru'):
    _lp = os.path.join(LOCALES_DIR, _l + '.json')
    if os.path.exists(_lp):
        with open(_lp, 'r', encoding='utf-8') as f:
            _LOCALES[_l] = json.load(f)


def get_i18n(lang, key, default=""):
    lang = lang if lang in ('uz', 'en', 'ru') else 'uz'
    return _LOCALES.get(lang, {}).get(key) or _LOCALES.get('uz', {}).get(key) or default or key


def T(lang, key):
    """Escaped interface string."""
    return html.escape(get_i18n(lang, key))


def format_number(n, lang='uz'):
    s = "{:,}".format(int(n or 0))
    return s if lang == 'en' else s.replace(',', ' ')


def count_phrase(n, key, lang):
    """'4 раза', '1 time', '5 marta': the locale value holds the plural forms separated by '|'
    (English: one|other; Russian: one|few|many; Uzbek: one form)."""
    forms = get_i18n(lang, key).split('|')
    n = int(n or 0)
    num = format_number(n, lang)
    if len(forms) == 1:
        return num + ' ' + forms[0]
    if lang == 'ru' and len(forms) >= 3:
        n10, n100 = n % 10, n % 100
        f = forms[0] if (n10 == 1 and n100 != 11) else (forms[1] if (2 <= n10 <= 4 and not 12 <= n100 <= 14) else forms[2])
        return num + ' ' + f
    return num + ' ' + (forms[0] if n == 1 else forms[-1])


def format_occurrences(n, lang='uz'):
    return count_phrase(n, 'occurrences_in_corpus', lang)


def with_lang(url, lang):
    if lang == 'uz':
        return url
    base, _, frag = url.partition('#')
    sep = '&' if '?' in base else '?'
    return base + sep + 'lang=' + lang + ('#' + frag if frag else '')


def cur_attr(flag, value='true'):
    return ' aria-current="%s"' % value if flag else ''


# ---------------------------------------------------------------------
# Labels for stored codes (patterns, statuses, equivalent forms)
# ---------------------------------------------------------------------
_PATTERN_RULES = [
    ('verb + preposition + noun', 'pat_verb_prep_noun'), ('noun + of + noun', 'pat_noun_of_noun'),
    ('adjective + noun', 'pat_adj_noun'), ('adj + noun', 'pat_adj_noun'), ('verb + noun', 'pat_verb_noun'),
    ('adverb + verb', 'pat_adv_verb'), ('verb + adverb', 'pat_verb_adv'), ('adv + adj', 'pat_adv_adj'),
    ('adverb + adjective', 'pat_adv_adj'), ('noun + noun', 'pat_noun_noun'), ('noun + verb', 'pat_noun_verb'),
    ('ega + kesim', 'pat_subj_pred'), ('sifat + ot', 'pat_adj_noun'), ('ot + fe’l', 'pat_noun_verb'),
    ('fe’l + ot', 'pat_verb_noun'), ('ravish + fe’l', 'pat_adv_verb'), ('fe’l + ravish', 'pat_verb_adv'),
    ('ravish + sifat', 'pat_adv_adj'), ('ot + ot', 'pat_noun_noun'),
]


def pattern_key(pattern):
    p = (pattern or '').lower().replace('ʼ', '’').replace("'", '’').replace('ʻ', '‘')
    for needle, key in _PATTERN_RULES:
        if needle in p:
            return key
    return 'pat_unknown'


def pattern_label(pattern, lang):
    return get_i18n(lang, pattern_key(pattern))


def colloc_status_label(item, lang):
    if (item.get('status') or '').lower() == 'tasdiqlangan':
        return get_i18n(lang, 'colloc_status_confirmed')
    return get_i18n(lang, 'ref_entry_label')


_EQ_FORM_TERMS = [('kuchaytiruvchi komponent tushib qolgan', 'eqf_intens_lost'), ('tushirib qoldirish', 'eqf_omission'),
                  ('kollokatsiya', 'eqf_collocation'), ('bitta so‘z', 'eqf_single_word'), ('1.1 xulosasi', 'eqf_11_conclusion')]


def eq_form_label(form, lang):
    out = form or ''
    if lang != 'uz':
        for term, key in _EQ_FORM_TERMS:
            out = out.replace(term, get_i18n(lang, key))
    return out


# ---------------------------------------------------------------------
# Books, pages and the side labels of a sentence pair
# ---------------------------------------------------------------------
BOOKS = {
    'cholpon': {'uz': ('label_original', 'Cho‘lpon', '«Kecha va kunduz»', 'ziyouz.com'),
                'en': ('label_translation', 'Christopher Fort', '«Night and Day»', '')},
    'hemingway': {'en': ('label_original', 'Hemingway', '«The Old Man and the Sea»', ''),
                  'uz': ('label_translation', 'Ibrohim G‘ofurov', '«Chol va dengiz»', 'e_copy')},
}
BOOK_FILTERS = {'kvk': ('cholpon', 'Cho‘lpon, «Kecha va kunduz» — «Night and Day»'),
                'oms': ('hemingway', 'Hemingway, «The Old Man and the Sea» — «Chol va dengiz»')}
_BOOK_FILTERS = BOOK_FILTERS
SEARCH_SAMPLES = (('yurak', 'uz'), ('og‘ir uyqu', 'uz'), ('javob bermoq', 'uz'), ('rangi o‘chmoq', 'uz'),
                  ('heart', 'en'), ('set the table', 'en'), ('shark', 'en'))
HOME_SAMPLES = (('og‘ir uyqu', 'uz'), ('javob bermoq', 'uz'), ('heavy sleep', 'en'), ('yurak', 'uz'))
TITLE_BY_SIDE = {('cholpon', 'uz'): '«Kecha va kunduz»', ('cholpon', 'en'): '«Night and Day»',
                 ('hemingway', 'en'): '«The Old Man and the Sea»', ('hemingway', 'uz'): '«Chol va dengiz»'}


def page_text(lang, page):
    if page in (None, '', 0):
        return ''
    return get_i18n(lang, 'page_fmt').replace('{p}', str(page))


def _num_page(page_str):
    if isinstance(page_str, int):
        return page_str
    m = re.search(r'(\d+)', str(page_str or ''))
    return int(m.group(1)) if m else None


def other_lang(code):
    return 'en' if code == 'uz' else 'uz'


def _side_parts(lang, book, side_lang, page):
    role, author, title, note = BOOKS.get(book, {}).get(side_lang, ('label_original', '', book, ''))
    pg = page_text(lang, page)
    if note == 'e_copy':
        pg = (get_i18n(lang, 'e_copy_short') + ', ' + pg) if pg else get_i18n(lang, 'e_copy_short')
        note = ''
    return role, author, title, note, pg


def side_label(lang, book, side_lang, page):
    """Plain text: 'Asliyat: Cho‘lpon, «Kecha va kunduz», 36-bet (ziyouz.com)'."""
    role, author, title, note, pg = _side_parts(lang, book, side_lang, page)
    s = get_i18n(lang, role) + ': ' + author + ', ' + title + (', ' + pg if pg else '')
    return s + (' (' + note + ')' if note else '')


def side_label_html(lang, book, side_lang, page):
    role, author, title, note, pg = _side_parts(lang, book, side_lang, page)
    out = '<span>%s</span> <b>%s, %s</b>' % (T(lang, role), html.escape(author), html.escape(title))
    if pg:
        out += ' <span class="tc-num">%s</span>' % html.escape(pg)
    if note:
        out += ' <span>%s</span>' % html.escape(note)
    return out


# Editorial apparatus of the e-copies that is not part of the author's or translator's text:
# printed page markers ("- 31 -") and note numbers glued to a word ("Hast1", "all!76").
# The stored text is not changed (character offsets of the alignment depend on it); only the display is.
_PAGE_MARK_RE = re.compile(r'(^|\s)[-–—]\s?\d{1,3}\s?[-–—](?=\s|$)')
_NOTE_RE = re.compile(r'(?<=[^\W\d_])(\d{1,3})(?=[\s,.;:!?»”"…)]|$)'
                      r'|(?<=[^\W\d_]</mark>)(\d{1,3})(?=[\s,.;:!?»”"…)]|$)'
                      r'|(?<=[!?])(\d{1,3})(?=\s|$)'
                      r'|(?<=[^\W\d_]["”»])(\d{1,2})(?=\s|$)')


def clean_display(html_text):
    if not html_text:
        return html_text
    t = _PAGE_MARK_RE.sub(lambda m: m.group(1), html_text)
    t = _NOTE_RE.sub('', t)
    return re.sub(r'  +', ' ', t).strip()


def pair_html(lang, book, q_lang, q_html, q_page, o_html, o_page, foot='', compact=False, anchor=''):
    """The facing-page pair: the side in the query language first, the parallel side next to it.
    A sentence without a counterpart (an unpaired sentence) gets a note on the other side."""
    o_lang = other_lang(q_lang)
    cls = 'tc-pair tc-pair--compact' if compact else 'tc-pair'
    aid = ' id="%s"' % anchor if anchor else ''
    q_html, o_html = clean_display(q_html), clean_display(o_html)
    if o_html:
        other = '<p class="tc-pair__text" lang="%s">%s</p>' % (o_lang, o_html)
        o_label = side_label_html(lang, book, o_lang, o_page)
    else:
        q_is_original = (book == 'cholpon') == (q_lang == 'uz')
        other = '<p class="tc-pair__text tc-pair__none">%s</p>' % T(lang, 'pair_none_translation' if q_is_original else 'pair_none_original')
        o_label = side_label_html(lang, book, o_lang, None)
    out = ('<article class="%s"%s>' % (cls, aid)
           + '<div class="tc-pair__side"><div class="tc-pair__src">%s</div><p class="tc-pair__text" lang="%s">%s</p></div>'
           % (side_label_html(lang, book, q_lang, q_page), q_lang, q_html)
           + '<div class="tc-pair__side"><div class="tc-pair__src">%s</div>%s</div>' % (o_label, other))
    if foot:
        out += '<div class="tc-pair__foot">%s</div>' % foot
    return out + '</article>'


def legend(lang):
    return ('<div class="tc-legend"><span><mark class="q">%s</mark></span><span><mark class="e">%s</mark></span></div>'
            % (T(lang, 'legend_query_word'), T(lang, 'legend_equivalent')))


# ---------------------------------------------------------------------
# Page frame
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# Icons, emblem and flags (inline SVG drawn for TILCOR)
# ---------------------------------------------------------------------
_ICON_PATHS = {
    'search': '<circle cx="11" cy="11" r="7"/><path d="m20.5 20.5-4.6-4.6"/>',
    'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
    'close': '<path d="M6 6l12 12M18 6 6 18"/>',
    'pin': '<path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0C18.5 15.4 12 21 12 21z"/><circle cx="12" cy="10" r="2.4"/>',
    'book': '<path d="M3.5 5.5c3-1.2 5.8-1.2 8.5.6v13c-2.7-1.8-5.5-1.8-8.5-.6zM20.5 5.5c-3-1.2-5.8-1.2-8.5.6v13c2.7-1.8 5.5-1.8 8.5-.6z"/>',
    'file': '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    'arrow': '<path d="M5 12h14M13 6l6 6-6 6"/>',
    'up': '<path d="M12 19V5M6 11l6-6 6 6"/>',
    'chart': '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    'nodes': '<circle cx="6" cy="12" r="3"/><circle cx="18" cy="6" r="3"/><circle cx="18" cy="18" r="3"/><path d="M8.7 10.6 15.3 7.4M8.7 13.4l6.6 3.2"/>',
    'columns': '<path d="M4 6h6M4 10h6M4 14h6M4 18h6M14 6h6M14 10h6M14 14h6M14 18h6"/>',
    'info': '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
    'lock': '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    'star': '<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z" fill="currentColor" stroke="none"/>',
    'layers': '<path d="m12 3 9 5-9 5-9-5z"/><path d="m3 13 9 5 9-5"/>',
    'sparkle': '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>',
}


def icon(name, cls='tc-ico'):
    return ('<svg class="%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % (cls, _ICON_PATHS[name]))


# The emblem: a round seal with two facing pages; the gold line is the searched word in the original,
# the turquoise line on the other page is the translator's equivalent.
_LOGO = ('<svg viewBox="0 0 64 64" aria-hidden="true">'
         '<circle cx="32" cy="32" r="30.5" fill="#0b2b6b" stroke="#ffffff" stroke-width="2.4"/>'
         '<circle cx="32" cy="32" r="25.5" fill="none" stroke="#ffffff" stroke-opacity=".32" stroke-width="1"/>'
         '<path d="M13.5 21.5c6-2.6 11.6-2.4 16.8.8v21.5c-5.2-3.2-10.8-3.4-16.8-.8z" fill="#ffffff"/>'
         '<path d="M50.5 21.5c-6-2.6-11.6-2.4-16.8.8v21.5c5.2-3.2 10.8-3.4 16.8-.8z" fill="#dbe9ff"/>'
         '<path d="M17 27.5h9.5M17 35.5h9.5M37.5 27.5H47M37.5 35.5H47" stroke="#0b2b6b" stroke-width="1.7" stroke-linecap="round"/>'
         '<path d="M17 31.5h9.5" stroke="#e0a526" stroke-width="2.6" stroke-linecap="round"/>'
         '<path d="M37.5 31.5H47" stroke="#13a594" stroke-width="2.6" stroke-linecap="round"/>'
         '<path d="M26.5 31.5c3.5-3 7.5-3 11 0" fill="none" stroke="#ffffff" stroke-width="1.3" stroke-dasharray="1.6 1.8"/></svg>')

_FLAGS = {
    'uz': ('<svg viewBox="0 0 30 20" aria-hidden="true"><rect width="30" height="20" fill="#fff"/>'
           '<rect width="30" height="6.4" fill="#0099b5"/><rect y="13.6" width="30" height="6.4" fill="#1eb53a"/>'
           '<rect y="6.4" width="30" height=".6" fill="#ce1126"/><rect y="13" width="30" height=".6" fill="#ce1126"/>'
           '<circle cx="5.2" cy="3.2" r="2.1" fill="#fff"/><circle cx="6" cy="3.2" r="1.8" fill="#0099b5"/>'
           '<circle cx="9" cy="2" r=".42" fill="#fff"/><circle cx="10.6" cy="2" r=".42" fill="#fff"/><circle cx="12.2" cy="2" r=".42" fill="#fff"/>'
           '<circle cx="10.6" cy="3.5" r=".42" fill="#fff"/><circle cx="12.2" cy="3.5" r=".42" fill="#fff"/><circle cx="12.2" cy="5" r=".42" fill="#fff"/></svg>'),
    'en': ('<svg viewBox="0 0 30 20" aria-hidden="true"><rect width="30" height="20" fill="#012169"/>'
           '<path d="M0 0l30 20M30 0 0 20" stroke="#fff" stroke-width="4"/><path d="M0 0l30 20M30 0 0 20" stroke="#c8102e" stroke-width="1.6"/>'
           '<path d="M15 0v20M0 10h30" stroke="#fff" stroke-width="6"/><path d="M15 0v20M0 10h30" stroke="#c8102e" stroke-width="3.4"/></svg>'),
    'ru': ('<svg viewBox="0 0 30 20" aria-hidden="true"><rect width="30" height="20" fill="#fff"/>'
           '<rect y="6.67" width="30" height="6.67" fill="#0039a6"/><rect y="13.33" width="30" height="6.67" fill="#d52b1e"/></svg>'),
}

_HERO_ART = ('<svg class="tc-hero__art" viewBox="0 0 760 520" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
             '<path d="M40 70c105-42 205-40 330 14v380c-125-54-225-56-330-14z"/>'
             '<path d="M720 70c-105-42-205-40-330 14v380c125-54 225-56 330-14z"/>'
             + ''.join('<path d="M80 %dh%d"/>' % (130 + 34 * k, 230 - (k % 3) * 34) for k in range(9))
             + ''.join('<path d="M430 %dh%d"/>' % (130 + 34 * k, 240 - ((k + 1) % 3) * 30) for k in range(9))
             + '<path d="M80 232h120" stroke-width="7" stroke-linecap="round"/><path d="M430 232h150" stroke-width="7" stroke-linecap="round"/>'
             '<path d="M210 232c60-40 160-40 210 0" stroke-dasharray="6 8"/></svg>')

FONTS = ('https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600;700;800'
         '&family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&display=swap')


def _page_head(lang, title, description=''):
    desc = html.escape(description or get_i18n(lang, 'site_description'))
    return ('<!DOCTYPE html>\n<html lang="%s">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta name="robots" content="noindex, nofollow">\n<meta name="description" content="%s">\n'
            '<meta name="theme-color" content="#061a45">\n<title>%s</title>\n'
            '<link rel="icon" href="/assets/tilcor-emblem.svg" type="image/svg+xml">\n'
            '<link rel="alternate" hreflang="uz" href="?lang=uz">\n<link rel="alternate" hreflang="en" href="?lang=en">\n'
            '<link rel="alternate" hreflang="ru" href="?lang=ru">\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link rel="stylesheet" href="%s">\n<link rel="stylesheet" href="/css/tilcor.css?v=%s">\n</head>'
            % (lang, desc, html.escape(title), html.escape(FONTS), CSS_VERSION))


def _nav_items(lang, is_admin):
    """(href, label key, current paths, sub links) of every section; used by the header and the drawer."""
    items = [
        ('/', 'nav_home', ('/',), ()),
        ('/qidiruv', 'nav_search', ('/qidiruv', '/kwic', '/soz'),
         (('/qidiruv', 'nav_word_search', 'nav_word_search_desc'), ('/kwic', 'nav_kwic', 'nav_kwic_desc'))),
        ('/kollokatsiyalar', 'nav_collocations', ('/kollokatsiyalar', '/kollokatsiya'), ()),
        ('/lugat', 'nav_dictionary', ('/lugat',), ()),
        ('/korpus', 'nav_corpus', ('/korpus', '/sources_rights.html', '/manbalar'),
         (('/korpus', 'nav_corpus_overview', ''), ('/sources_rights.html', 'nav_sources', ''))),
        ('/methodology.html', 'nav_analysis', ('/methodology', '/annotation_guidelines', '/statistika', '/metodologiya', '/yoriqnoma'),
         (('/methodology.html', 'nav_methodology', ''), ('/methodology_statistics.html', 'nav_statistics', ''),
          ('/annotation_guidelines.html', 'nav_guidelines', ''))),
        ('/about_project.html', 'about_project', ('/about_project.html', '/loyiha-haqida'), ()),
    ]
    if is_admin:
        items.append(('/admin_collocations.html', 'nav_lab', ('/admin_', '/preview_', '/annotation_workspace', '/baholash'),
                      (('/baholash', 'nav_lab_validation', ''), ('/admin_collocations.html', 'nav_lab_collocations', ''),
                       ('/preview_alignment_queue.html', 'nav_lab_alignment', ''), ('/annotation_workspace.html', 'nav_lab_annotation', ''))))
    return items


_FRAME_JS = ('<script>(function(){var d=document;function q(s){return d.querySelector(s)}'
             'function op(el){el.classList.add("is-open");d.body.style.overflow="hidden";var i=el.querySelector("input[type=search]");'
             'if(i)setTimeout(function(){i.focus()},40)}'
             'function cl(el){el.classList.remove("is-open");d.body.style.overflow=""}'
             'd.addEventListener("click",function(e){var t=e.target.closest&&e.target.closest("[data-open],[data-close]");if(!t)return;'
             'var el=q("#"+(t.getAttribute("data-open")||t.getAttribute("data-close")));if(!el)return;e.preventDefault();'
             't.hasAttribute("data-open")?op(el):cl(el)});'
             'd.addEventListener("keydown",function(e){if(e.key==="Escape"){["#tc-so","#tc-drawer"].forEach(function(s){var el=q(s);if(el)cl(el)})}'
             'else if(e.key==="/"&&!/^(INPUT|TEXTAREA|SELECT)$/.test((d.activeElement||{}).tagName||"")){var so=q("#tc-so");if(so){e.preventDefault();op(so)}}});'
             'd.addEventListener("DOMContentLoaded",function(){'
             'var f=q("#tc-so form");if(f){f.addEventListener("change",function(e){if(e.target.name==="tc-target")f.action=e.target.value})}'
             'var tp=q("#tc-totop");if(tp){window.addEventListener("scroll",function(){tp.classList.toggle("is-shown",window.scrollY>700)},{passive:true});'
             'tp.addEventListener("click",function(){window.scrollTo({top:0,behavior:"smooth"})})}'
             'd.querySelectorAll(".tc-range input[type=range]").forEach(function(r){var o=r.parentNode.querySelector("output"),tpl=o.getAttribute("data-tpl");'
             'function u(){var p=(r.value-r.min)/(r.max-r.min)*100;r.style.setProperty("--fill",p+"%");o.textContent=tpl.replace("{n}",r.value)}'
             'r.addEventListener("input",u);r.addEventListener("change",function(){if(r.form&&r.form.q&&r.form.q.value.trim())r.form.submit()});u()});'
             # qidiruv qatori takliflari (/api/suggest — faqat korpusdagi real so'z shakllari)
             'd.querySelectorAll("form[role=search] input[type=search][name=q]").forEach(function(inp){'
             'var wrap=inp.parentNode,box=d.createElement("div"),items=[],sel=-1,acT;'
             'box.className="tc-ac";box.setAttribute("role","listbox");wrap.appendChild(box);'
             'function hide(){box.classList.remove("is-open");box.innerHTML="";items=[];sel=-1}'
             'function pick(t){inp.value=t;hide();if(inp.form)inp.form.submit()}'
             'function render(list){if(!list.length){hide();return}items=list;sel=-1;box.innerHTML="";'
             'list.forEach(function(s){var b=d.createElement("button");b.type="button";b.className="tc-ac__item";b.setAttribute("role","option");'
             'var w=d.createElement("span");w.textContent=s.text;w.lang=s.lang||"";var n=d.createElement("small");n.className="tc-num";n.textContent=s.count;'
             'b.appendChild(w);b.appendChild(n);b.addEventListener("mousedown",function(e){e.preventDefault();pick(s.text)});box.appendChild(b)});'
             'box.classList.add("is-open")}'
             'inp.setAttribute("autocomplete","off");'
             'inp.addEventListener("input",function(){var v=inp.value.trim();clearTimeout(acT);if(v.length<2){hide();return}'
             'acT=setTimeout(function(){fetch("/api/suggest?q="+encodeURIComponent(v)).then(function(r){return r.ok?r.json():null})'
             '.then(function(j){if(inp.value.trim()===v)render((j&&j.suggestions)||[])}).catch(function(){hide()})},180)});'
             'inp.addEventListener("keydown",function(e){if(!items.length)return;'
             'if(e.key==="ArrowDown"||e.key==="ArrowUp"){e.preventDefault();sel=(sel+(e.key==="ArrowDown"?1:items.length-1))%items.length;'
             'box.querySelectorAll(".tc-ac__item").forEach(function(b,i){b.classList.toggle("is-sel",i===sel)})}'
             'else if(e.key==="Enter"&&sel>=0){e.preventDefault();pick(items[sel].text)}'
             'else if(e.key==="Escape"){hide()}});'
             'inp.addEventListener("blur",function(){setTimeout(hide,150)})})'
             '})})();</script>')


def render_nav(lang='uz', current_path='/', is_admin=False):
    lang = lang if lang in ('uz', 'en', 'ru') else 'uz'
    base_path = current_path.split('?')[0].rstrip('/') or '/'
    query = urllib.parse.parse_qsl(current_path.split('?', 1)[1]) if '?' in current_path else []
    query = [(k, v) for k, v in query if k != 'lang']

    def is_current(paths):
        return any(base_path == p or (p != '/' and base_path.startswith(p)) for p in paths)

    def lang_href(code):
        return html.escape(base_path + '?' + urllib.parse.urlencode(query + [('lang', code)]))

    names = (('uz', 'Oʻzbekcha', 'Oʻz'), ('en', 'English', 'En'), ('ru', 'Русский', 'Ру'))
    flags = ''.join('<a href="%s" hreflang="%s" title="%s"%s>%s<span class="tc-sr">%s</span></a>'
                    % (lang_href(c), c, full, cur_attr(c == lang), _FLAGS[c], full) for c, full, _s in names)
    pills = ''.join('<a href="%s" hreflang="%s"%s>%s</a>' % (lang_href(c), c, cur_attr(c == lang), short) for c, _f, short in names)
    sign = '<a class="tc-signin" href="%s">%s</a>' % (with_lang('/kirish', lang), T(lang, 'nav_logout') if is_admin else T(lang, 'nav_login'))
    topbar = ('<div class="tc-topbar"><div class="tc-topbar__in">'
              '<div class="tc-topbar__info"><span>%s%s</span><span>%s%s</span><span>%s%s</span></div>'
              '<nav class="tc-topbar__links" aria-label="%s"><a href="%s">%s</a><a href="%s">%s</a><a href="%s">%s</a></nav>'
              '<div class="tc-flags" role="group" aria-label="%s">%s</div>%s</div></div>'
              % (icon('pin'), T(lang, 'topbar_place'), icon('file'), T(lang, 'topbar_research'), icon('book'), T(lang, 'topbar_books'),
                 T(lang, 'nav_analysis'), with_lang('/metodologiya', lang), T(lang, 'nav_methodology'),
                 with_lang('/statistika', lang), T(lang, 'nav_statistics'), with_lang('/sources_rights.html', lang), T(lang, 'nav_sources'),
                 T(lang, 'interface_language'), flags, sign))

    items = _nav_items(lang, is_admin)
    nav = []
    drawer = []
    for href, key, paths, menu in items:
        sub = ''
        if menu:
            sub = '<div class="tc-nav__menu">%s</div>' % ''.join(
                '<a href="%s">%s%s</a>' % (with_lang(h, lang), T(lang, k), ('<small>%s</small>' % T(lang, d)) if d else '') for h, k, d in menu)
        nav.append('<div class="tc-nav__item"><a class="tc-nav__link" href="%s"%s>%s</a>%s</div>'
                   % (with_lang(href, lang), cur_attr(is_current(paths), 'page'), T(lang, key), sub))
        drawer.append('<div class="tc-drawer__group"><a href="%s">%s</a>%s</div>'
                      % (with_lang(href, lang), T(lang, key),
                         ('<div>%s</div>' % ''.join('<a href="%s">%s</a>' % (with_lang(h, lang), T(lang, k)) for h, k, _d in menu)) if menu else ''))
    brand = ('<a class="tc-brand" href="%s">%s<span class="tc-brand__text"><span class="tc-brand__name">TILCOR</span> '
             '<span class="tc-brand__sub">%s</span></span></a>' % (with_lang('/', lang), _LOGO, T(lang, 'brand_sub')))
    header = ('<header class="tc-header"><div class="tc-header__in">%s<nav class="tc-nav" aria-label="%s">%s</nav>'
              '<div class="tc-tools"><a class="tc-round" href="%s" data-open="tc-so" title="%s">%s<span class="tc-sr">%s</span></a>'
              '<a class="tc-round" href="#tc-drawer" data-open="tc-drawer" title="%s">%s<span class="tc-sr">%s</span></a></div></div></header>'
              % (brand, T(lang, 'nav_menu'), ''.join(nav), with_lang('/qidiruv', lang), T(lang, 'so_open'), icon('search'), T(lang, 'so_open'),
                 T(lang, 'menu_open'), icon('menu'), T(lang, 'menu_open')))
    drawer_html = ('<div class="tc-drawer" id="tc-drawer" role="dialog" aria-modal="true" aria-label="%s">'
                   '<div class="tc-drawer__shade" data-close="tc-drawer"></div><div class="tc-drawer__panel">'
                   '<div class="tc-drawer__top"><div class="tc-lang" role="group" aria-label="%s">%s</div>'
                   '<button class="tc-round" type="button" data-close="tc-drawer" aria-label="%s">%s</button></div>%s'
                   '<div class="tc-drawer__group">%s</div></div></div>'
                   % (T(lang, 'menu_open'), T(lang, 'interface_language'), pills, T(lang, 'so_close'), icon('close'), ''.join(drawer), sign))
    # the search overlay
    hidden = '' if lang == 'uz' else '<input type="hidden" name="lang" value="%s">' % lang
    targets = ''.join('<label><input type="radio" name="tc-target" value="%s"%s> %s</label>' % (a, ' checked' if a == '/qidiruv' else '', T(lang, k))
                      for a, k in (('/qidiruv', 'so_t_search'), ('/kwic', 'so_t_kwic'), ('/kollokatsiyalar', 'so_t_colls'), ('/lugat', 'so_t_dict')))
    samples = ''.join('<a href="%s" lang="%s">%s</a>' % (with_lang('/qidiruv?q=' + urllib.parse.quote(s), lang), l_, html.escape(s))
                      for s, l_ in SEARCH_SAMPLES + (('old man', 'en'), ('qishloq', 'uz')))
    overlay = ('<div class="tc-so" id="tc-so" role="dialog" aria-modal="true" aria-label="%s">'
               '<button class="tc-so__close" type="button" data-close="tc-so" aria-label="%s">%s</button><div class="tc-so__in">'
               '<h2>%s</h2><form action="/qidiruv" method="get" role="search"><div class="tc-so__field">'
               '<input type="search" name="q" placeholder="%s" aria-label="%s" autocomplete="off">%s'
               '<button type="submit" aria-label="%s">%s</button></div><div class="tc-so__targets">%s</div></form>'
               '<div class="tc-so__ask"><div class="tc-so__orb">%s</div><b>%s</b><span>%s</span></div>'
               '<div class="tc-so__samples"><h3>%s%s</h3><div class="tc-so__grid">%s</div></div></div></div>'
               % (T(lang, 'so_title'), T(lang, 'so_close'), icon('close'), T(lang, 'so_title'), T(lang, 'so_placeholder'), T(lang, 'search_label'),
                  hidden, T(lang, 'search_button'), icon('search'), targets, icon('search'), T(lang, 'so_ask'), T(lang, 'so_hint'),
                  icon('star'), T(lang, 'so_samples'), samples))
    return topbar + header + drawer_html + overlay + _FRAME_JS


def render_footer(lang='uz'):
    return ('<footer class="tc-footer"><div class="tc-footer__in"><span class="tc-footer__brand">%s<span>TILCOR, 2026. %s</span></span>'
            '<span>%s <a href="%s">%s</a></span></div></footer>'
            '<button class="tc-totop" id="tc-totop" type="button" aria-label="%s">%s</button>'
            % (_LOGO, T(lang, 'footer_brand'), T(lang, 'footer_rights'), with_lang('/sources_rights.html', lang), T(lang, 'nav_sources'),
               T(lang, 'to_top'), icon('up')))


# the title block of an inner page is shown in a full-width band under the header
_BAND_RE = re.compile(r'^\s*(?:<header>)?\s*((?:<p class="tc-small">(?:(?!</p>).)*</p>)?\s*<h1\b[^>]*>.*?</h1>\s*'
                      r'(?:<p class="tc-lead">.*?</p>)?\s*(?:<div class="tc-herostats">.*?<!--/herostats-->)?)\s*(?:</header>)?', re.S)
_BAND_SECTIONS = (
    (('/qidiruv', '/kwic', '/soz'), 'search', 'nav_search'),
    (('/kollokatsiya',), 'nodes', 'nav_collocations'),
    (('/korpus', '/sources_rights', '/manbalar'), 'book', 'nav_corpus'),
    (('/methodology', '/metodologiya', '/statistika', '/annotation_guidelines', '/yoriqnoma'), 'chart', 'nav_analysis'),
    (('/about_project', '/loyiha-haqida'), 'info', 'about_project'),
    (('/lugat',), 'book', 'nav_dictionary'),
    (('/kirish',), 'lock', 'nav_login'),
    (('/baholash',), 'layers', 'nav_lab_validation'),
)


def _band(lang, path, body):
    m = _BAND_RE.match(body)
    if not m:
        return '', body
    base = path.split('?')[0]
    ico, key = next(((i, k) for prefixes, i, k in _BAND_SECTIONS if any(base.startswith(p) for p in prefixes)), ('sparkle', 'nav_home'))
    title = m.group(1).replace('<p class="tc-small">', '<p class="tc-small tc-crumb">', 1)
    band = ('<section class="tc-band"><div class="tc-band__in"><span class="tc-pill">%s%s</span>%s</div></section>'
            % (icon(ico), T(lang, key), title))
    return band, body[m.end():]


def hero_stats(rows):
    """Small stat cards in the page band: [(icon name, label, value), ...]."""
    return ('<div class="tc-herostats">%s</div><!--/herostats-->'
            % ''.join('<div class="tc-hstat"><i>%s</i><span><small>%s</small><b class="tc-num">%s</b></span></div>' % (icon(i), lbl, v)
                      for i, lbl, v in rows))


def page(lang, title, body, path='/', is_admin=False, narrow=False, description='', hero=''):
    full_title = (title + ' — TILCOR') if title else get_i18n(lang, 'site_title')
    band, rest = ('', body) if hero else _band(lang, path, body)
    return (_page_head(lang, full_title, description) + '\n<body class="tc">' + render_nav(lang, path, is_admin)
            + hero + band + '<main class="tc-main%s" id="main">%s</main>' % (' tc-main--narrow' if narrow else '', rest)
            + render_footer(lang) + '</body></html>')


def _pager(lang, cur, total_pages, make_url):
    if total_pages <= 1:
        return ''
    prev = '<a href="%s">%s</a>' % (make_url(cur - 1), T(lang, 'btn_prev')) if cur > 1 else '<span></span>'
    nxt = '<a href="%s">%s</a>' % (make_url(cur + 1), T(lang, 'btn_next')) if cur < total_pages else '<span></span>'
    return ('<nav class="tc-pager" aria-label="%s">%s<span class="tc-num">%s %s / %s</span>%s</nav>'
            % (T(lang, 'page_word'), prev, T(lang, 'page_word'), format_number(cur, lang), format_number(total_pages, lang), nxt))


def search_form(lang, query='', book='', action='/qidiruv', extra_html='', autofocus=False):
    """The search box of the inner pages: the same white pill with a round button as on the home page."""
    hidden = '' if lang == 'uz' else '<input type="hidden" name="lang" value="%s">' % lang
    if book in BOOK_FILTERS:
        hidden += '<input type="hidden" name="kitob" value="%s">' % html.escape(book)
    chips = ''
    if not query:
        chips = '<nav class="tc-hchips" aria-label="%s">%s</nav>' % (T(lang, 'so_samples'), ''.join(
            '<a href="%s" lang="%s">%s%s</a>' % (with_lang(action + '?q=' + urllib.parse.quote(q), lang), l_, html.escape(q), icon('arrow'))
            for q, l_ in SEARCH_SAMPLES))
    return ('<form class="tc-sform" action="%s" method="get" role="search"><div class="tc-hsearch">'
            '<input type="search" name="q" value="%s" placeholder="%s" aria-label="%s" autocomplete="off"%s>%s'
            '<button type="submit" aria-label="%s">%s</button></div>%s%s</form>'
            % (action, html.escape(query), T(lang, 'home_search_placeholder'), T(lang, 'search_label'),
               ' autofocus' if autofocus else '', hidden, T(lang, 'search_button'), icon('search'), chips, extra_html))


# ---------------------------------------------------------------------
# HOME
# ---------------------------------------------------------------------
def render_home_page(lang='uz', stats=None, is_admin=False, featured=None):
    lang = lang if lang in ('uz', 'en', 'ru') else 'uz'
    st = stats or {}

    def n(k):
        return format_number(st.get(k, 0), lang)

    hidden = '' if lang == 'uz' else '<input type="hidden" name="lang" value="%s">' % lang
    chips = ''.join('<a href="%s" lang="%s">%s%s</a>' % (with_lang('/qidiruv?q=' + urllib.parse.quote(q), lang), l_, html.escape(q), icon('arrow'))
                    for q, l_ in HOME_SAMPLES)
    search = ('<form class="tc-hsearch" action="/qidiruv" method="get" role="search">'
              '<input type="search" name="q" placeholder="%s" aria-label="%s" autocomplete="off">%s'
              '<button type="submit" aria-label="%s">%s</button></form>'
              '<nav class="tc-hchips" aria-label="%s">%s</nav>'
              % (T(lang, 'home_search_placeholder'), T(lang, 'search_label'), hidden, T(lang, 'search_button'), icon('arrow'),
                 T(lang, 'so_samples'), chips))
    hero = ('<section class="tc-hero">%s<div class="tc-hero__in"><div class="tc-hero__text">'
            '<p class="tc-eyebrow">%s</p><h1>%s <span>%s</span></h1><p class="tc-lead">%s</p>%s</div>'
            '<div class="tc-stats"><h2 class="tc-stats__title">%s</h2>'
            '<div class="tc-stat tc-stat--big"><small>%s</small><b class="tc-num">%s</b><p>%s</p></div>'
            '<div class="tc-stat tc-stat--wide"><small>%s</small><b class="tc-num">%s</b></div>'
            '<div class="tc-stat"><small>%s</small><b class="tc-num">%s</b></div>'
            '<div class="tc-stat"><small>%s</small><b class="tc-num">%s</b></div></div></div></section>'
            % (_HERO_ART, T(lang, 'home_eyebrow'), T(lang, 'home_h1_a'), T(lang, 'home_h1_b'), T(lang, 'home_lead2'), search,
               T(lang, 'home_stats_title'), T(lang, 'home_stat_pairs'), n('pairs_total'), T(lang, 'home_stat_note'),
               T(lang, 'home_stat_tokens'), n('tokens_total'), T(lang, 'home_stat_collocations'), n('collocations_index'),
               T(lang, 'home_stat_works'), format_number(2, lang)))

    feat = ''
    if featured:
        feat = ('<figure class="tc-section" style="margin:0"><h2 style="margin-bottom:6px">%s</h2><figcaption class="tc-section__note">%s</figcaption>%s%s</figure>'
                % (T(lang, 'home_example_title'), T(lang, 'home_example_caption'),
                   pair_html(lang, featured['book'], featured['q_lang'], featured['q_html'], featured['q_page'],
                             featured['o_html'], featured['o_page']), legend(lang)))

    def book(pair_key, dir_key, rows, href):
        dl = ''.join('<dt>%s</dt><dd>%s</dd>' % (T(lang, a), b) for a, b in rows)
        return ('<section class="tc-book"><h3>%s</h3><p class="tc-muted tc-small" style="margin-top:6px">%s</p><dl>%s</dl>'
                '<p style="margin-top:14px"><a href="%s">%s</a></p></section>'
                % (T(lang, pair_key), T(lang, dir_key), dl, with_lang(href, lang), T(lang, 'btn_search_work')))

    kvk = book('home_pair_kvk', 'dir_uz_en', [
        ('label_original', 'Abdulhamid Cho‘lpon, «Kecha va kunduz». Toshkent: «Sharq», 2000'),
        ('label_translation', 'Cho‘lpon, «Night and Day», Christopher Fort. Boston: Academic Studies Press, 2019'),
        ('label_pairs', '<span class="tc-num">%s</span>' % n('pairs_kvk')),
        ('label_tokens', '<span class="tc-num">%s / %s</span>' % (n('tokens_kvk_uz'), n('tokens_kvk_en')))], '/qidiruv?kitob=kvk')
    oms = book('home_pair_oms', 'dir_en_uz', [
        ('label_original', 'Ernest Hemingway, «The Old Man and the Sea» (1952)'),
        ('label_translation', 'Ernest Xeminguey, «Chol va dengiz», Ibrohim G‘ofurov. Toshkent: «Yosh gvardiya», 1986'),
        ('label_pairs', '<span class="tc-num">%s</span>' % n('pairs_oms')),
        ('label_tokens', '<span class="tc-num">%s / %s</span>' % (n('tokens_oms_en'), n('tokens_oms_uz')))], '/qidiruv?kitob=oms')
    links = ''.join('<a href="%s"><i>%s</i><span><b>%s</b><span>%s</span></span></a>' % (with_lang(h, lang), icon(ic), T(lang, k), T(lang, d))
                    for h, ic, k, d in (('/kollokatsiyalar', 'nodes', 'nav_collocations', 'home_link_colloc'),
                                        ('/lugat', 'book', 'dict_title', 'home_link_dict'),
                                        ('/kwic', 'columns', 'nav_kwic', 'home_link_kwic'),
                                        ('/metodologiya', 'file', 'nav_methodology', 'home_link_method'),
                                        ('/statistika', 'chart', 'nav_statistics', 'home_link_stats'),
                                        ('/korpus', 'layers', 'nav_corpus_overview', 'home_link_corpus')))
    body = ('%s<section class="tc-section"><h2>%s</h2><div class="tc-books" style="margin-top:16px">%s%s</div></section>'
            '<section class="tc-section"><h2>%s</h2><div class="tc-links" style="margin-top:16px">%s</div></section>'
            % (feat, T(lang, 'home_sources_title'), kvk, oms, T(lang, 'home_more_title'), links))
    return page(lang, '', body, '/', is_admin, hero=hero)


# ---------------------------------------------------------------------
# SEARCH RESULTS
# ---------------------------------------------------------------------
def render_equivalents(res, lang, query):
    eqs = res.get('equivalents') or []
    cov = res.get('equivalent_coverage') or {}
    head = '<div class="tc-section__head"><h2>%s</h2><a class="tc-small" href="%s">%s</a></div>' % (
        T(lang, 'sec_equivalents'), with_lang('/methodology.html#tekislash', lang), T(lang, 'eq_how'))
    if not eqs:
        return '<section class="tc-section">%s<p class="tc-section__note">%s</p></section>' % (head, T(lang, 'eq_none_found'))
    q_lang = res.get('selected_lang') or 'uz'
    o_lang = other_lang(q_lang)
    total = sum(e['count'] for e in eqs) or 1
    bar = '<div class="tc-dist" role="img" aria-label="%s">%s</div>' % (T(lang, 'eq_distribution'), ''.join(
        '<span style="width:%.2f%%" title="%s: %d"></span>' % (100.0 * e['count'] / total, html.escape(e['text']), e['count']) for e in eqs[:8]))
    rows = []
    for e in eqs[:12]:
        kind = T(lang, 'eq_kind_phrase') if len(e['key'].split()) > 1 else T(lang, 'eq_kind_word')
        badges = '<span class="tc-badge">%s</span>' % kind
        if e.get('researcher'):
            badges += ' <span class="tc-badge tc-badge--tile">%s</span>' % T(lang, 'eq_in_dissertation')
        forms = [f for f in e.get('forms', []) if f.lower() != e['text'].lower()]
        forms_html = ('<span class="tc-eq__forms">%s %s</span>' % (T(lang, 'eq_also'), ', '.join(html.escape(f) for f in forms[:4]))) if forms else ''
        ex = e.get('example') or {}
        ex_html = ''
        if ex:
            ex_html = pair_html(lang, ex.get('book'), q_lang, ex.get('query_highlighted') or html.escape(ex.get('query_raw', '')),
                                ex.get('query_page'), ex.get('other_highlighted') or html.escape(ex.get('other_raw', '')),
                                ex.get('other_page'), compact=True)
        rows.append('<div class="tc-eq"><div class="tc-eq__head"><span class="tc-eq__word" lang="%s">%s</span>'
                    '<span class="tc-eq__meta tc-num">%s, %d%%</span>%s%s</div>%s</div>'
                    % (o_lang, html.escape(e['text']), html.escape(count_phrase(e['count'], 'label_sentences', lang)), e['share'], badges, forms_html, ex_html))
    key = 'eq_note_all' if cov.get('total') and cov.get('with', 0) >= cov.get('total', 0) else 'eq_note'
    note = get_i18n(lang, key).replace('{with}', format_number(cov.get('with', 0), lang)).replace('{total}', format_number(cov.get('total', 0), lang))
    return '<section class="tc-section">%s<p class="tc-section__note">%s</p>%s%s</section>' % (head, html.escape(note), bar, ''.join(rows))


def render_word_forms(res, lang):
    words = res.get('words') or []
    if not words:
        return ''
    q_lang = res.get('selected_lang') or 'uz'
    rows = []
    for w in words[:40]:
        grp = w.get('group', 'exact')
        grp_txt = T(lang, 'grp_' + grp) if grp in ('exact', 'inflected', 'derived', 'compound') else html.escape(grp)
        counts = '<br>'.join('%s <span class="tc-num">%s</span>' % (TITLE_BY_SIDE.get((b, q_lang), b), format_number(c, lang))
                             for b, c in (w.get('book_counts') or {}).items())
        trs = w.get('translations') or []
        tr_html = ', '.join('<span class="tc-serif" lang="%s">%s</span> <span class="tc-muted tc-num">(%s)</span>'
                            % (other_lang(q_lang), html.escape(t['text']), format_number(t['count'], lang)) for t in trs) or '<span class="tc-muted">—</span>'
        rows.append('<tr><td class="tc-serif" lang="%s"><mark class="q">%s</mark></td><td>%s</td><td class="tc-small">%s</td><td>%s</td></tr>'
                    % (q_lang, html.escape(w.get('word', '')), grp_txt, counts, tr_html))
    return ('<section class="tc-section"><div class="tc-section__head"><h2>%s <span class="tc-count tc-num">%s</span></h2></div>'
            '<p class="tc-section__note">%s</p><div class="tc-panel tc-scroll" style="padding:4px 8px"><table class="tc-table">'
            '<thead><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div></section>'
            % (T(lang, 'sec_words'), format_number(len(words), lang), T(lang, 'sec_words_note'), T(lang, 'col_form'),
               T(lang, 'col_kind'), T(lang, 'col_in_corpus'), T(lang, 'col_book_translation'), ''.join(rows)))


MEASURE_LABELS = (('log_dice', 'logDice'), ('mi', 'MI'), ('t', 't-score'), ('g2', 'G²'))


def format_decimal(x, lang, digits=2):
    if x is None:
        return '—'
    t = ('%.' + str(digits) + 'f') % x
    return t if lang == 'en' else t.replace('.', ',').replace('-', '−')


def collocation_block(c, lang, show_example=True, open_example=False, measure=''):
    q_lang = c.get('lang') or 'uz'
    o_lang = other_lang(q_lang)
    where = ', '.join('%s %s' % (TITLE_BY_SIDE.get((b, q_lang), b), format_number(v, lang)) for b, v in (c.get('books') or {}).items())
    trs = c.get('translations') or []
    tr_html = ''
    if trs:
        st = c.get('eq_stats') or {}
        n_occ = sum(v.get('occ', 0) for v in st.values())
        n_eq = sum(v.get('eq', 0) for v in st.values())
        label = T(lang, 'coll_in_translation')
        if n_occ and n_eq < n_occ:
            label = T(lang, 'coll_in_translation_of').replace('{a}', format_number(n_occ, lang)).replace('{b}', format_number(n_eq, lang))
        tr_html = '<p class="tc-coll__tr">%s %s</p>' % (label, ', '.join(
            '<span lang="%s">%s</span> <span class="tc-muted tc-num">(%s)</span>' % (o_lang, html.escape(t['text']), format_number(t['count'], lang)) for t in trs[:4]))
    ex_html = ''
    ex = c.get('example')
    if show_example and ex:
        pair = pair_html(lang, ex['book'], q_lang, ex['query_html'], ex.get('query_page'), ex['other_html'], ex.get('other_page'), compact=True)
        ex_html = '<details%s><summary>%s</summary>%s</details>' % (' open' if open_example else '', T(lang, 'coll_show_example'), pair)
    link = with_lang('/kollokatsiya/' + urllib.parse.quote(c['id']), lang)
    meta = html.escape(pattern_label(c.get('pattern', ''), lang)) + '; ' + html.escape(count_phrase(c.get('freq', 0), 'occurrences_word', lang))
    if where:
        meta += '; ' + html.escape(where)
    if measure and (c.get('assoc') or {}).get(measure) is not None:
        meta += '; %s %s' % (dict(MEASURE_LABELS)[measure], format_decimal(c['assoc'][measure], lang, 1 if measure == 'g2' else 2))
    return ('<div class="tc-coll"><div class="tc-coll__head"><a class="tc-coll__name" lang="%s" href="%s">%s</a></div>'
            '<div class="tc-coll__meta">%s</div>%s%s</div>'
            % (q_lang, link, html.escape(c.get('display') or c.get('lemma') or ''), meta, tr_html, ex_html))


def render_collocations(res, lang):
    colls = res.get('corpus_collocations') or []
    refs = res.get('reference_collocations') or []
    if not colls and not refs:
        return ''
    out = ('<section class="tc-section"><div class="tc-section__head"><h2>%s <span class="tc-count tc-num">%s</span></h2>'
           '<a class="tc-small" href="%s">%s</a></div><p class="tc-section__note">%s</p>'
           % (T(lang, 'sec_collocations'), format_number(len(colls), lang), with_lang('/kollokatsiyalar', lang),
              T(lang, 'coll_browse_all'), T(lang, 'sec_collocations_note')))
    if colls:
        out += '<div class="tc-colls">%s</div>' % ''.join(collocation_block(c, lang) for c in colls[:40])
    else:
        out += '<p class="tc-muted">%s</p>' % T(lang, 'coll_none_in_corpus')
    if refs:
        items = ''.join('<li><span class="tc-serif" lang="en">%s</span> <span class="tc-muted tc-small">%s</span>%s</li>'
                        % (html.escape(r.get('collocation') or ''), html.escape((r.get('source_badge') or '').split(':', 1)[-1].strip()),
                           (' <span class="tc-small">%s: %s</span>' % (T(lang, 'label_sample_sentence'), html.escape((r.get('example') or {}).get('source_sentence', ''))))
                           if (r.get('example') or {}).get('source_sentence') else '')
                        for r in refs[:16])
        out += ('<details style="margin-top:18px"><summary class="tc-small" style="cursor:pointer;color:var(--lapis)">%s (%s)</summary>'
                '<p class="tc-section__note" style="margin-top:8px">%s</p><ul class="tc-prose">%s</ul></details>'
                % (T(lang, 'ref_lists_title'), format_number(len(refs), lang), T(lang, 'ref_lists_note'), items))
    return out + '</section>'


def render_sentences(res, lang, make_url):
    sents = res.get('corpus_sentences') or []
    pag = res.get('pagination') or {}
    q_lang = res.get('selected_lang') or 'uz'
    total = int(pag.get('total_sentences') or len(sents))
    cards = []
    for s in sents:
        foot = ('<span class="tc-badge tc-badge--tile">%s</span>' % T(lang, 'eq_in_dissertation')) if s.get('equiv_confirmed') else ''
        cards.append(pair_html(lang, s.get('book'), q_lang, s.get('query_highlighted') or html.escape(s.get('query_raw', '')),
                               s.get('query_page'), s.get('other_highlighted') or html.escape(s.get('other_raw', '')),
                               s.get('other_page'), foot=foot, anchor='gap-' + html.escape(str(s.get('id', '')))))
    return ('<section class="tc-section"><div class="tc-section__head"><h2>%s <span class="tc-count tc-num">%s</span></h2></div>%s'
            '<div style="margin-top:12px">%s</div>%s</section>'
            % (T(lang, 'sec_sentences'), format_number(total, lang), legend(lang), ''.join(cards),
               _pager(lang, int(pag.get('page') or 1), int(pag.get('total_pages') or 1), make_url)))


def render_qidiruv_page(lang='uz', query='', book='', search_res=None, is_admin=False, page=1, **_):
    lang = lang if lang in ('uz', 'en', 'ru') else 'uz'
    book = book if book in BOOK_FILTERS else ''
    res = search_res or {}
    qs = [(k, v) for k, v in (('q', query), ('kitob', book)) if v]

    def url(**extra):
        q2 = dict(qs)
        q2.update(dict((k, v) for k, v in extra.items() if v))
        return with_lang('/qidiruv' + ('?' + urllib.parse.urlencode(q2) if q2 else ''), lang)

    opts = ''.join('<option value="%s"%s>%s</option>' % (k, ' selected' if k == book else '', html.escape(v[1])) for k, v in BOOK_FILTERS.items())
    filters = ('<div class="tc-filters"><label>%s<select name="kitob" onchange="this.form.submit()"><option value="">%s</option>%s</select></label></div>'
               % (T(lang, 'kwic_book'), T(lang, 'kwic_all_books'), opts)) if query or book else ''
    body = '' if query else '<h1 style="margin-bottom:16px">%s</h1>' % T(lang, 'nav_word_search')
    body += search_form(lang, query, book, extra_html=filters, autofocus=not query)
    q_lang = res.get('selected_lang') or 'uz'
    if not query:
        body += '<p class="tc-section__note" style="margin-top:22px">%s</p>' % T(lang, 'search_intro')
    elif res.get('error') or res.get('detected_lang') == 'ru':
        body += '<div class="tc-panel" style="margin-top:24px">%s</div>' % T(lang, 'search_lang_error')
    else:
        total = int((res.get('pagination') or {}).get('total_sentences') or 0)
        occ = int((res.get('summary') or {}).get('corpus_occurrences') or 0)
        lang_note = T(lang, 'q_lang_uz') if q_lang == 'uz' else T(lang, 'q_lang_en')
        if res.get('is_ambiguous') and q_lang == 'uz':
            lang_note += ' <a href="%s">%s</a>' % (url(til='en'), T(lang, 'q_lang_force_en'))
        if lang == 'uz':
            summary = 'Korpusda %s marta uchraydi, %s ta gapda.' % (format_number(occ, lang), format_number(total, lang))
        else:
            summary = '%s, %s.' % (count_phrase(occ, 'occurrences_in_corpus', lang), count_phrase(total, 'label_sentences', lang))
        pm = res.get('per_million')
        if pm:
            pm_s = ('%.1f' % pm if lang == 'en' else ('%.1f' % pm).replace('.', ',')) if isinstance(pm, float) else format_number(pm, lang)
            summary += ' ' + get_i18n(lang, 'freq_pm').replace('{n}', pm_s)
        body += ('<header style="margin-top:32px"><h1 lang="%s">%s</h1><p class="tc-lead tc-num" style="margin-top:6px">%s %s</p></header>'
                 % (q_lang, html.escape(query), html.escape(summary), lang_note))
        if not total:
            dym = res.get('did_you_mean') or []
            dym_html = ''
            if dym:
                chips = ''.join('<a class="tc-chip" href="%s" lang="%s">%s <span class="tc-num tc-muted">%s</span></a>'
                                % (url(q=s['text']), 'uz' if s.get('lang') != 'en' else 'en', html.escape(s['text']),
                                   format_number(s.get('count', 0), lang)) for s in dym)
                dym_html = ('<p style="margin-top:14px">%s</p><div class="tc-chips" style="margin-top:8px">%s</div>'
                            % (T(lang, 'did_you_mean'), chips))
            body += '<div class="tc-panel" style="margin-top:24px"><p>%s</p>%s</div>' % (T(lang, 'not_in_corpus'), dym_html)
            body += render_collocations(res, lang)
        else:
            body += (render_equivalents(res, lang, query) + render_word_forms(res, lang) + render_collocations(res, lang)
                     + render_sentences(res, lang, lambda p: url(page=p)))
    path = '/qidiruv' + ('?' + urllib.parse.urlencode(qs) if qs else '')
    return globals()['page'](lang, query or get_i18n(lang, 'nav_word_search'), body, path, is_admin)


# ---------------------------------------------------------------------
# COLLOCATIONS (browse the corpus collocation index)
# ---------------------------------------------------------------------
UZ_PATTERNS = ('sifat + ot', 'ot + fe’l', 'ega + kesim', 'ravish + fe’l', 'ot + ot')
EN_PATTERNS = ('adjective + noun', 'verb + noun', 'noun + verb', 'verb + adverb', 'verb + preposition + noun',
               'adverb + adjective', 'noun + noun')


def render_kollokatsiyalar_page(lang='uz', is_admin=False, pattern='', status='', page=1, items=None, til='uz', q='', order='', **_):
    lang = lang if lang in ('uz', 'en', 'ru') else 'uz'
    til = til if til in ('uz', 'en') else 'uz'
    order = order if order in dict(MEASURE_LABELS) else ''
    all_items = items or []
    n_uz = sum(1 for it in all_items if it['lang'] == 'uz')
    n_en = len(all_items) - n_uz
    stats = hero_stats([('book', T(lang, 'hs_uz'), format_number(n_uz, lang)), ('book', T(lang, 'hs_en'), format_number(n_en, lang)),
                        ('layers', T(lang, 'hs_total'), format_number(len(all_items), lang))])
    items = [it for it in all_items if it['lang'] == til]
    if order:
        items = sorted(items, key=lambda it: (-((it.get('assoc') or {}).get(order) or 0), -it['freq'], it['lemma']))
    pats = UZ_PATTERNS if til == 'uz' else EN_PATTERNS
    counts = dict((p, sum(1 for it in items if it['pattern'] == p)) for p in pats)
    if pattern in pats:
        items = [it for it in items if it['pattern'] == pattern]
    else:
        pattern = ''
    if q:
        ql = q.lower()
        items = [it for it in items if ql in (it.get('display') or '').lower() or ql in it['lemma'].lower()]
    per = 30
    total_pages = max(1, (len(items) + per - 1) // per)
    page_no = max(1, min(int(page or 1), total_pages))
    chunk = items[(page_no - 1) * per: page_no * per]

    def url(**kw):
        params = {'til': til, 'qolip': pattern, 'q': q, 'tartib': order}
        params.update(kw)
        return with_lang('/kollokatsiyalar?' + urllib.parse.urlencode(dict((k, v) for k, v in params.items() if v)), lang)

    tabs = ''.join('<a class="tc-chip" href="%s"%s>%s</a>' % (url(til=code, qolip='', page=''), cur_attr(til == code), T(lang, key))
                   for code, key in (('uz', 'coll_tab_uz'), ('en', 'coll_tab_en')))
    chips = '<a class="tc-chip" href="%s"%s>%s</a>' % (url(qolip='', page=''), cur_attr(not pattern), T(lang, 'pat_all'))
    chips += ''.join('<a class="tc-chip" href="%s"%s>%s <span class="tc-num tc-muted">%s</span></a>'
                     % (url(qolip=p, page=''), cur_attr(pattern == p), html.escape(pattern_label(p, lang)), format_number(counts[p], lang))
                     for p in pats if counts.get(p))
    sorts = '<span class="tc-small tc-muted" style="align-self:center">%s:</span>' % T(lang, 'coll_order_label')
    sorts += '<a class="tc-chip" href="%s"%s>%s</a>' % (url(tartib='', page=''), cur_attr(not order), T(lang, 'coll_order_freq'))
    sorts += ''.join('<a class="tc-chip" href="%s"%s>%s</a>' % (url(tartib=k, page=''), cur_attr(order == k), lbl) for k, lbl in MEASURE_LABELS)
    hidden = '<input type="hidden" name="til" value="%s">' % til
    if order:
        hidden += '<input type="hidden" name="tartib" value="%s">' % order
    if pattern:
        hidden += '<input type="hidden" name="qolip" value="%s">' % html.escape(pattern)
    if lang != 'uz':
        hidden += '<input type="hidden" name="lang" value="%s">' % lang
    find = ('<form method="get" action="/kollokatsiyalar" class="tc-search" style="max-width:520px;margin-top:16px">'
            '<input type="search" name="q" value="%s" placeholder="%s" aria-label="%s">%s'
            '<button class="tc-btn tc-btn--ghost" type="submit">%s</button></form>'
            % (html.escape(q), T(lang, 'coll_filter_placeholder'), T(lang, 'coll_filter_placeholder'), hidden, T(lang, 'btn_apply')))
    order_note = ('<p class="tc-small tc-muted" style="margin-top:8px">%s</p>' % T(lang, 'coll_order_note')) if order else ''
    body = ('<h1>%s</h1><p class="tc-lead">%s</p>%s<div class="tc-chips" style="margin-top:4px">%s</div>'
            '<div class="tc-chips" id="qoliplar" style="margin-top:12px">%s</div><div class="tc-chips" style="margin-top:12px">%s</div>%s%s'
            '<p class="tc-muted tc-small tc-num" style="margin-top:14px">%s</p><div class="tc-colls" style="margin-top:6px">%s</div>%s'
            '<p class="tc-section__note" style="margin-top:30px"><a href="%s">%s</a>. %s</p>'
            % (T(lang, 'coll_page_title'), T(lang, 'coll_page_lead'), stats, tabs, chips, sorts, order_note, find,
               html.escape(count_phrase(len(items), 'coll_count_word', lang)), ''.join(collocation_block(c, lang, measure=order) for c in chunk),
               _pager(lang, page_no, total_pages, lambda p: url(page=p)),
               with_lang('/kollokatsiyalar?manba=malumotnoma', lang), T(lang, 'ref_lists_title'), T(lang, 'ref_lists_note')))
    return globals()['page'](lang, get_i18n(lang, 'coll_page_title'), body, '/kollokatsiyalar', is_admin)


def render_reference_page(lang='uz', is_admin=False, items=None, page_no=1):
    items = items or []
    per = 50
    total_pages = max(1, (len(items) + per - 1) // per)
    page_no = max(1, min(int(page_no or 1), total_pages))
    rows = ''.join('<tr><td class="tc-serif" lang="en">%s</td><td>%s</td><td class="tc-small tc-muted">%s</td></tr>'
                   % (html.escape(it.get('english') or ''), html.escape(pattern_label(it.get('pattern', ''), lang)), html.escape(it.get('sourceBook') or ''))
                   for it in items[(page_no - 1) * per: page_no * per])
    body = ('<p class="tc-small"><a href="%s">%s</a></p><h1 style="margin-top:8px">%s</h1><p class="tc-lead">%s</p>'
            '<div class="tc-panel tc-scroll" style="margin-top:22px;padding:4px 8px"><table class="tc-table"><thead><tr>'
            '<th>%s</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div>%s'
            % (with_lang('/kollokatsiyalar', lang), T(lang, 'coll_page_title'), T(lang, 'ref_lists_title'), T(lang, 'ref_lists_note'),
               T(lang, 'col_english'), T(lang, 'label_pattern'), T(lang, 'col_source_list'), rows,
               _pager(lang, page_no, total_pages, lambda p: with_lang('/kollokatsiyalar?manba=malumotnoma&page=%d' % p, lang))))
    return page(lang, get_i18n(lang, 'ref_lists_title'), body, '/kollokatsiyalar', is_admin)


def _uniq_forms(forms, exclude=''):
    """Word forms without case variants (Chol, chol) and without the form shown as the head."""
    out, seen = [], {exclude.lower()}
    for f in forms:
        low = f.lower()
        if low not in seen:
            seen.add(low)
            out.append(f[:1].lower() + f[1:] if f[:1].isupper() and not f.isupper() else f)
    return out


def render_collocation_detail(lang, is_admin, item, pairs):
    """All stored occurrences of one corpus collocation, each as a facing pair."""
    q_lang = item['lang']
    o_lang = other_lang(q_lang)
    trs = item.get('translations') or []
    tr_rows = ''.join('<tr><td class="tc-serif" lang="%s">%s</td><td class="tc-num">%s</td><td class="tc-small tc-muted">%s</td></tr>'
                      % (o_lang, html.escape(t['text']), format_number(t['count'], lang),
                         html.escape(', '.join(_uniq_forms(t.get('forms') or {}, t['text'])))) for t in trs)
    cards = ''.join(pair_html(lang, p['book'], q_lang, p['query_html'], p['query_page'], p['other_html'], p['other_page'], compact=True) for p in pairs)
    seen_forms = []
    for f_ in (item.get('forms') or {}):
        if f_.lower() not in [x.lower() for x in seen_forms]:
            seen_forms.append(f_[:1].lower() + f_[1:] if f_[:1].isupper() and not f_.isupper() else f_)
    forms = ', '.join(html.escape(f) for f in seen_forms)
    cite = 'TILCOR. (2026). %s [%s]. https://tilcor.uz/kollokatsiya/%s' % (item.get('display'), get_i18n(lang, 'profile_collocation'), item['id'])
    lead = html.escape(pattern_label(item.get('pattern', ''), lang)) + '; ' + html.escape(count_phrase(item.get('freq', 0), 'occurrences_word', lang)) + '.'
    if forms:
        lead += ' %s <span class="tc-serif" lang="%s">%s</span>.' % (T(lang, 'coll_forms'), q_lang, forms)
    eq_occ = sum(v.get('occ', 0) for v in (item.get('eq_stats') or {}).values())
    eq_found = sum(v.get('eq', 0) for v in (item.get('eq_stats') or {}).values())
    cover = ''
    if eq_occ:
        cover = '<p class="tc-section__note tc-num">%s</p>' % (T(lang, 'coll_eq_found').replace('{a}', format_number(eq_found, lang))
                                                              .replace('{b}', format_number(eq_occ, lang)))
    tr_sec = ''
    if trs:
        tr_sec = ('<section class="tc-section"><h2>%s</h2>%s<div class="tc-panel tc-scroll" style="padding:4px 8px;margin-top:12px">'
                  '<table class="tc-table"><thead><tr><th>%s</th><th>%s</th><th>%s</th></tr></thead><tbody>%s</tbody></table></div></section>'
                  % (T(lang, 'coll_translations_title'), cover, T(lang, 'col_book_translation'), T(lang, 'col_count'), T(lang, 'col_other_forms'), tr_rows))
    a = item.get('assoc') or {}
    assoc_sec = ''
    if a:
        def cell(k, v):
            return '<div><div class="tc-small tc-muted">%s</div><div class="tc-num" style="font-size:1.15rem">%s</div></div>' % (k, v)
        corp = [('O₁₁', format_number(item.get('freq', 0), lang)), ('R₁', format_number(a.get('f1', 0), lang)),
                ('C₁', format_number(a.get('f2', 0), lang)), ('N', format_number(a.get('n', 0), lang))]
        corp += [(lbl, format_decimal(a.get(k), lang, 1 if k == 'g2' else 2)) for k, lbl in MEASURE_LABELS]
        groups = '<h3 style="margin:4px 0 10px">%s</h3><div class="tc-statgrid">%s</div>' % (T(lang, 'coll_ref_corpus'), ''.join(cell(k, v) for k, v in corp))
        ref = item.get('ref')
        if ref is not None:
            if ref.get('f'):
                rc = [('f', format_number(ref['f'], lang)), ('R₁', format_number(ref.get('f1', 0), lang)), ('C₁', format_number(ref.get('f2', 0), lang)),
                      ('N', format_number(ref.get('n', 0), lang))]
                rc += [(lbl, format_decimal(ref.get(k), lang, 1 if k == 'g2' else 2)) for k, lbl in MEASURE_LABELS]
                note = T(lang, 'coll_ref_min') if ref['f'] >= 5 else T(lang, 'coll_ref_low')
                groups += ('<h3 style="margin:18px 0 10px">%s</h3><div class="tc-statgrid">%s</div><p class="tc-small tc-muted" style="margin-top:8px">%s. '
                           '<a href="%s">%s</a></p>' % (T(lang, 'coll_ref_ref'), ''.join(cell(k, v) for k, v in rc), note,
                                                        with_lang('/statistika#tayanch', lang), T(lang, 'coll_ref_more')))
            else:
                groups += ('<h3 style="margin:18px 0 6px">%s</h3><p class="tc-small tc-muted">%s. <a href="%s">%s</a></p>'
                           % (T(lang, 'coll_ref_ref'), T(lang, 'coll_ref_none'), with_lang('/statistika#tayanch', lang), T(lang, 'coll_ref_more')))
        elif q_lang == 'uz':
            groups += '<p class="tc-small tc-muted" style="margin-top:12px">%s</p>' % T(lang, 'coll_ref_uz')
        judged = ''
        try:
            import validation as V
            import validation_pages as VP
            rec = V.annotations()['records'].get('colloc_' + q_lang, {})
            cats = [r_.get('A', {}).get('labels', {}).get('category') for iid, r_ in rec.items() if iid.startswith('c:%s:' % item['id'])]
            cats = [c_ for c_ in cats if c_]
            if cats:
                judged = '<p style="margin-top:14px"><span class="tc-badge tc-badge--tile">%s: %s</span></p>' % (
                    T(lang, 'coll_judged'), html.escape(VP.L[lang]['cat_' + cats[0]]))
        except Exception:
            judged = ''
        assoc_sec = ('<section class="tc-section"><h2>%s</h2><p class="tc-section__note">%s</p><div class="tc-panel" style="margin-top:12px">%s%s</div></section>'
                     % (T(lang, 'coll_ref_title'), T(lang, 'coll_assoc_note'), groups, judged))
    shown_note = ''
    if item.get('freq', 0) > len(pairs):
        shown_note = '<p class="tc-section__note tc-num">%s</p>' % T(lang, 'coll_examples_first').replace('{n}', format_number(len(pairs), lang))
    body = ('<p class="tc-small"><a href="%s">%s</a></p><h1 lang="%s" style="margin-top:8px">%s</h1><p class="tc-lead">%s</p>%s'
            '%s<section class="tc-section"><h2>%s <span class="tc-count tc-num">%s</span></h2>%s%s<div style="margin-top:12px">%s</div></section>'
            '<section class="tc-section"><h2>%s</h2><p class="tc-panel tc-small" style="margin-top:12px;font-family:var(--serif)">%s</p></section>'
            % (with_lang('/kollokatsiyalar?til=' + q_lang, lang), T(lang, 'coll_page_title'), q_lang, html.escape(item.get('display') or ''),
               lead, tr_sec, assoc_sec, T(lang, 'sec_sentences'), format_number(len(pairs), lang), shown_note, legend(lang), cards,
               T(lang, 'perm_citation_page'), html.escape(cite)))
    return page(lang, item.get('display') or '', body, '/kollokatsiyalar', is_admin)


# ---------------------------------------------------------------------
# CORPUS, DICTIONARY, LOGIN
# ---------------------------------------------------------------------
def render_korpus_page(lang='uz', is_admin=False, stats=None):
    st = stats or {}

    def n(k):
        return format_number(st.get(k, 0), lang)

    def pw(a, b):
        return get_i18n(lang, 'pages_range').replace('{a}', str(a)).replace('{b}', str(b))

    def text_row(role, title, edition, copy, pages, tokens):
        return ('<tr><td>%s</td><td class="tc-serif">%s</td><td class="tc-small">%s<br><span class="tc-muted">%s</span></td>'
                '<td class="tc-small">%s</td><td class="tc-num">%s</td></tr>' % (T(lang, role), title, edition, copy, pages, tokens))

    rows1 = (text_row('label_original', '«Kecha va kunduz»', 'Toshkent: «Sharq», 2000', 'ziyouz.com', pw(3, 265), n('tokens_kvk_uz'))
             + text_row('label_translation', '«Night and Day»', 'Boston: Academic Studies Press, 2019', 'DOI 10.1515/9781644690482', pw(45, 271), n('tokens_kvk_en')))
    rows2 = (text_row('label_original', '«The Old Man and the Sea»', T(lang, 'first_edition') + ': 1952', 'Asiaing.com', pw(9, 125), n('tokens_oms_en'))
             + text_row('label_translation', '«Chol va dengiz»', 'Toshkent: «Yosh gvardiya», 1986', 'kutubxonachi.uz, ' + T(lang, 'e_copy_short'), pw(1, 46), n('tokens_oms_uz')))
    head = '<thead><tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr></thead>' % (
        T(lang, 'col_role'), T(lang, 'col_text'), T(lang, 'col_edition'), T(lang, 'col_pages'), T(lang, 'label_tokens'))

    def section(h, d, rows, pairs_key, href):
        return ('<section class="tc-section"><h2>%s</h2><p class="tc-section__note">%s, %s</p>'
                '<div class="tc-panel tc-scroll" style="padding:4px 8px"><table class="tc-table">%s<tbody>%s</tbody></table></div>'
                '<p style="margin-top:10px"><a href="%s">%s</a></p></section>'
                % (T(lang, h), T(lang, d), html.escape(count_phrase(st.get(pairs_key, 0), 'label_pairs_word', lang)), head, rows,
                   with_lang(href, lang), T(lang, 'btn_search_work')))
    stats = hero_stats([('layers', T(lang, 'hs_pairs'), n('pairs_total')), ('columns', T(lang, 'hs_tokens'), n('tokens_total')),
                        ('book', T(lang, 'hs_works'), format_number(2, lang))])
    body = ('<h1>%s</h1><p class="tc-lead">%s</p>%s%s%s<section class="tc-section"><h2>%s</h2><p class="tc-prose" style="margin-top:8px">%s</p>'
            '<p style="margin-top:14px"><a href="%s">%s</a></p></section>'
            % (T(lang, 'korpus_title'), T(lang, 'korpus_lead'), stats,
               section('home_pair_kvk', 'dir_uz_en', rows1, 'pairs_kvk', '/qidiruv?kitob=kvk'),
               section('home_pair_oms', 'dir_en_uz', rows2, 'pairs_oms', '/qidiruv?kitob=oms'),
               T(lang, 'korpus_pages_title'), T(lang, 'korpus_pages_text'), with_lang('/sources_rights.html', lang), T(lang, 'nav_sources')))
    return page(lang, get_i18n(lang, 'korpus_title'), body, '/korpus', is_admin)


POS_KEYS = {'noun': 'pos_noun', 'verb': 'pos_verb', 'adj': 'pos_adj', 'adv': 'pos_adv'}


def _dict_url(lang, d, **kw):
    params = [('yo', d)] + [(k, v) for k, v in kw.items() if v]
    return with_lang('/lugat?' + urllib.parse.urlencode(params), lang)


def _dict_word_tile(lang, d, e, n_tr=2):
    o = other_lang(d)
    pos = ('<i>%s</i>' % T(lang, POS_KEYS[e['pos']])) if e.get('pos') in POS_KEYS else ''
    top_n = e['tr'][0]['count'] if e['tr'] else 0
    trs = ', '.join(html.escape(t['text']) for t in e['tr'][:n_tr] if t['count'] >= 0.3 * top_n)
    return ('<a class="tc-dword" href="%s"><b lang="%s">%s</b>%s<span lang="%s">%s</span><small class="tc-num">%s</small></a>'
            % (_dict_url(lang, d, q=e['head']), d, html.escape(e['head']), pos, o, trs, format_number(e['freq'], lang)))


def render_lugat_page(lang='uz', is_admin=False, model=None, **_):
    """The corpus dictionary: Uzbek–English and English–Uzbek, built from the translators' own words."""
    lang = lang if lang in ('uz', 'en', 'ru') else 'uz'
    m = model or {}
    d = m.get('dir') or 'uz'
    o = other_lang(d)
    st = m.get('stats') or {}
    q = m.get('q') or ''
    stats = hero_stats([('book', T(lang, 'hs_dict_uz'), format_number(st.get('uz', 0), lang)),
                        ('book', T(lang, 'hs_dict_en'), format_number(st.get('en', 0), lang)),
                        ('layers', T(lang, 'hs_dict_tr'), format_number(st.get('pairs', 0), lang))])
    seg = ''.join('<label><input type="radio" name="yo" value="%s"%s><span>%s%s</span></label>'
                  % (code, ' checked' if code == d else '', '<b class="tc-seg__flag">%s</b>' % _FLAGS[code], T(lang, 'dict_dir_' + code))
                  for code in ('uz', 'en'))
    hidden = '' if lang == 'uz' else '<input type="hidden" name="lang" value="%s">' % lang
    form = ('<form class="tc-dform" action="/lugat" method="get" role="search">'
            '<fieldset class="tc-seg"><legend class="tc-sr">%s</legend>%s</fieldset>'
            '<div class="tc-hsearch"><input type="search" name="q" value="%s" placeholder="%s" aria-label="%s" autocomplete="off"%s>%s'
            '<button type="submit" aria-label="%s">%s</button></div></form>'
            % (T(lang, 'dict_dir_label'), seg, html.escape(q), T(lang, 'dict_placeholder_' + d), T(lang, 'dict_placeholder_' + d),
               '' if q else ' autofocus', hidden, T(lang, 'dict_find'), icon('search')))
    present = m.get('present') or set()
    abc = ''.join(('<a href="%s"%s>%s</a>' % (_dict_url(lang, d, harf=l_), cur_attr(l_ == m.get('letter')), html.escape(l_)))
                  if l_ in present else '<span aria-hidden="true">%s</span>' % html.escape(l_) for l_ in (m.get('letters') or ()))
    abc = '<nav class="tc-abc" aria-label="%s" lang="%s">%s</nav>' % (T(lang, 'dict_letters'), d, abc)
    mode = m.get('mode')
    out = ''
    if mode == 'entry':
        if m.get('switched') and m.get('explicit'):
            out += '<p class="tc-dnote">%s</p>' % T(lang, 'dict_switched_' + d)
        for item in m.get('entries') or []:
            out += _dict_entry(lang, d, item)
        if m.get('other_hit') and not m.get('switched'):
            out += ('<p class="tc-dnote"><a href="%s">%s: <span lang="%s">%s</span></a></p>'
                    % (_dict_url(lang, o, q=q), T(lang, 'dict_also_other_' + o), o, html.escape(q)))
    elif mode == 'notfound':
        sug = m.get('suggest') or []
        out += ('<div class="tc-panel tc-dmiss"><h2>%s</h2><p class="tc-prose tc-muted" style="margin-top:8px">%s</p>'
                % (html.escape(get_i18n(lang, 'dict_not_found').replace('{q}', q)), T(lang, 'dict_not_found_hint')))
        links = '<a class="tc-btn tc-btn--ghost" href="%s">%s%s</a>' % (with_lang('/qidiruv?q=' + urllib.parse.quote(q), lang), icon('search'), T(lang, 'dict_search_corpus'))
        if m.get('other_hit'):
            links = '<a class="tc-btn" href="%s">%s</a>' % (_dict_url(lang, o, q=q), T(lang, 'dict_also_other_' + o)) + links
        out += '<div class="tc-hero__btns" style="margin-top:18px">%s</div></div>' % links
        if sug:
            out += ('<section class="tc-section"><h2>%s</h2><div class="tc-dwords" style="margin-top:14px">%s</div></section>'
                    % (T(lang, 'dict_suggest'), ''.join(_dict_word_tile(lang, d, e) for e in sug)))
    elif mode == 'letter':
        n_items = m.get('n_items', 0)
        out += ('<section class="tc-section"><div class="tc-section__head"><h2>%s <span class="tc-count tc-num">%s</span></h2></div>'
                '<div class="tc-dwords">%s</div>%s</section>'
                % (html.escape(get_i18n(lang, 'dict_letter_head').replace('{letter}', m['letter'])),
                   html.escape(count_phrase(n_items, 'dict_words', lang)),
                   ''.join(_dict_word_tile(lang, d, e) for e in m.get('items') or []),
                   _pager(lang, m.get('page', 1), m.get('total_pages', 1), lambda p: _dict_url(lang, d, harf=m['letter'], sahifa=p))))
    else:
        out += ('<section class="tc-section"><div class="tc-section__head"><h2>%s</h2></div><p class="tc-section__note">%s</p>'
                '<div class="tc-dwords">%s</div></section>'
                % (T(lang, 'dict_top'), T(lang, 'dict_top_note'), ''.join(_dict_word_tile(lang, d, e) for e in m.get('top') or [])))
        out += ('<section class="tc-section"><div class="tc-panel"><h2>%s</h2><p class="tc-prose" style="margin-top:10px">%s</p>'
                '<p style="margin-top:12px"><a href="%s">%s</a></p></div></section>'
                % (T(lang, 'dict_method_title'), T(lang, 'dict_method_text'), with_lang('/methodology.html#lugat', lang), T(lang, 'dict_method_link')))
    js = ('<script>(function(){var f=document.querySelector(".tc-dform");if(!f)return;'
          'f.querySelectorAll("input[name=yo]").forEach(function(r){r.addEventListener("change",function(){'
          'var i=f.querySelector("input[name=q]");i.placeholder=r.value=="uz"?%s:%s;'
          'if(!i.value.trim()){f.submit()}else{i.focus()}})})})();</script>'
          % (json.dumps(get_i18n(lang, 'dict_placeholder_uz')), json.dumps(get_i18n(lang, 'dict_placeholder_en'))))
    head = ('<h1>%s</h1><p class="tc-lead">%s</p>%s' % (T(lang, 'dict_title'), T(lang, 'dict_lead'), stats) if mode == 'home'
            else '<h1>%s</h1>' % T(lang, 'dict_title'))
    body = head + '<div class="tc-dbar">%s%s</div>%s%s' % (form, abc, out, js)
    title = q if q else get_i18n(lang, 'dict_title')
    path = '/lugat' + ('?q=' + urllib.parse.quote(q) if q else '')
    return page(lang, title, body, path, is_admin)


def _dict_entry(lang, d, item):
    e = item['e']
    o = other_lang(d)
    pos = ('<span class="tc-entry__pos">%s</span>' % T(lang, POS_KEYS[e['pos']])) if e.get('pos') in POS_KEYS else ''
    forms = ', '.join('<span lang="%s">%s</span> <span class="tc-num">%s</span>' % (d, html.escape(f), format_number(c, lang))
                      for f, c in list((e.get('forms') or {}).items())[:8])
    total = sum(t['count'] for t in item['tr']) or 1
    senses = []
    for k, t in enumerate(item['tr']):
        pct = 100.0 * t['count'] / total
        tforms = ', '.join('%s <span class="tc-num">%s</span>' % (html.escape(f), format_number(c, lang)) for f, c in (t.get('forms') or {}).items())
        rev = ('<a class="tc-sense__rev" href="%s">%s%s</a>' % (_dict_url(lang, o, q=t['text']), icon('arrow'), T(lang, 'dict_reverse_' + o))
               if t.get('reverse') else '')
        pair = ''
        p = t.get('pair')
        if p:
            foot = ('<span class="tc-badge tc-badge--tile">%s</span>' % T(lang, 'eq_in_dissertation')) if p.get('researcher') else ''
            pair = pair_html(lang, p['book'], d, p['q_html'], p['q_page'], p['o_html'], p['o_page'], foot=foot, compact=True)
            pair = ('<div class="tc-sense__ex"><p class="tc-small tc-muted">%s</p>%s</div>' % (T(lang, 'dict_example'), pair) if k == 0
                    else '<details class="tc-sense__ex"><summary>%s</summary>%s</details>' % (T(lang, 'dict_more_example'), pair))
        senses.append('<li class="tc-sense"><div class="tc-sense__head"><span class="tc-sense__word" lang="%s">%s</span>'
                      '<span class="tc-sense__n tc-num">%s</span><span class="tc-sense__bar" title="%s"><span style="width:%.0f%%"></span></span>%s</div>'
                      '<p class="tc-sense__forms">%s: <span lang="%s">%s</span></p>%s</li>'
                      % (o, html.escape(t['text']), html.escape(count_phrase(t['count'], 'occurrences_word', lang)),
                         html.escape(get_i18n(lang, 'dict_tr_share').replace('{p}', '%.0f' % pct)), max(pct, 3), rev,
                         T(lang, 'dict_tr_forms'), o, tforms, pair))
    colls = item.get('colls') or []
    if colls:
        lis = ''.join('<li><a href="%s" lang="%s">%s</a> <span class="tc-muted tc-small tc-num">%s</span>%s</li>'
                      % (with_lang('/kollokatsiya/' + urllib.parse.quote(c['id']), lang), d, html.escape(c.get('display') or c.get('lemma') or ''),
                         format_number(c.get('freq', 0), lang),
                         ('<br><span class="tc-small" lang="%s">%s</span>' % (o, html.escape(c['translations'][0]['text']))) if c.get('translations') else '')
                      for c in colls)
        coll_html = '<ul class="tc-dlist">%s</ul>' % lis
    else:
        coll_html = '<p class="tc-small tc-muted">%s</p>' % T(lang, 'dict_colls_none')
    rel = item.get('related') or []
    rel_html = ('<div class="tc-panel"><h3>%s</h3><div class="tc-chips">%s</div></div>'
                % (T(lang, 'dict_related'), ''.join('<a class="tc-chip" href="%s" lang="%s">%s</a>' % (_dict_url(lang, d, q=r['head']), d, html.escape(r['head']))
                                                     for r in rel))) if rel else ''
    head_q = urllib.parse.quote(e['head'][:-3] if d == 'uz' and e.get('pos') == 'verb' and e['head'].endswith('moq') else e['head'])
    more = ('<div class="tc-panel"><h3>%s</h3><ul class="tc-dlist"><li><a href="%s">%s%s</a></li><li><a href="%s">%s%s</a></li></ul></div>'
            % (T(lang, 'dict_more'), with_lang('/qidiruv?q=' + urllib.parse.quote(e['head']), lang), icon('search'), T(lang, 'dict_all_sentences'),
               with_lang('/kwic?q=' + head_q, lang), icon('columns'), T(lang, 'dict_kwic')))
    return ('<article class="tc-entry"><div class="tc-entry__main"><header class="tc-entry__head"><h2 lang="%s">%s</h2>%s'
            '<p class="tc-entry__meta"><span class="tc-num">%s</span></p><p class="tc-entry__forms">%s: %s</p></header>'
            '<h3 class="tc-entry__sub">%s</h3><ol class="tc-senses">%s</ol></div>'
            '<aside class="tc-aside"><div class="tc-panel"><h3>%s</h3>%s</div>%s%s</aside></article>'
            % (d, html.escape(e['head']), pos, html.escape(get_i18n(lang, 'dict_in_corpus').replace('{n}', count_phrase(e['freq'], 'occurrences_word', lang))),
               T(lang, 'dict_forms'), forms, T(lang, 'dict_tr_title'), ''.join(senses), T(lang, 'dict_colls'), coll_html, rel_html, more))


def render_login_page(lang='uz', user=None, next_url=''):
    if user:
        logout = "fetch('/api/auth/logout',{method:'POST'}).then(function(){location.href='/'})"
        links = ''
        if user in ('admin', 'annotator', 'reviewer'):
            links += '<a class="tc-btn" href="%s">%s</a>' % (with_lang('/baholash', lang), T(lang, 'nav_lab_validation'))
        if user == 'admin':
            links += '<a class="tc-btn tc-btn--ghost" href="/admin_collocations.html">%s</a>' % T(lang, 'nav_lab')
        body = ('<h1>%s</h1><p class="tc-lead">%s</p><div class="tc-hero__btns" style="margin-top:18px">%s'
                '<button class="tc-btn tc-btn--ghost" type="button" onclick="%s">%s</button></div>'
                % (T(lang, 'login_title'), html.escape(get_i18n(lang, 'login_signed_in').replace('{user}', user)), links, logout, T(lang, 'nav_logout')))
    else:
        msgs = json.dumps({'fail': get_i18n(lang, 'error_login_failed'), 'rate': get_i18n(lang, 'login_rate_limited'),
                           'net': get_i18n(lang, 'login_network_error'), 'home': next_url or with_lang('/', lang)}, ensure_ascii=False)
        script = ("<script>var TC_MSG=%s;function tcLogin(e){e.preventDefault();var f=e.target,err=document.getElementById('tc-login-error');"
                  "err.textContent='';fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},"
                  "body:JSON.stringify({username:f.username.value,password:f.password.value})}).then(function(r){return r.json()"
                  ".then(function(d){return [r.status,d]})}).then(function(x){if(x[1]&&x[1].success){location.href=TC_MSG.home}"
                  "else{err.textContent=x[0]===429?TC_MSG.rate:TC_MSG.fail}}).catch(function(){err.textContent=TC_MSG.net});return false}</script>"
                  % msgs.replace('</', '<\\/'))
        body = ('<h1>%s</h1><p class="tc-lead">%s</p><form class="tc-form" style="margin-top:24px" onsubmit="return tcLogin(event)">'
                '<label>%s<input name="username" autocomplete="username" required></label>'
                '<label>%s<input name="password" type="password" autocomplete="current-password" required></label>'
                '<p class="tc-error" id="tc-login-error" role="alert"></p><button class="tc-btn" type="submit">%s</button></form>%s'
                % (T(lang, 'login_title'), T(lang, 'login_lead'), T(lang, 'login_user'), T(lang, 'login_password'), T(lang, 'login_submit'), script))
    return page(lang, get_i18n(lang, 'login_title'), body, '/kirish', bool(user), narrow=True)


# ---------------------------------------------------------------------
# KWIC
# ---------------------------------------------------------------------
_KWIC_WORD_RE = re.compile(r"\w+(?:['‘’ʻʼ`]\w+)*", re.UNICODE)


def _cut_words(text, n, from_end):
    words = list(_KWIC_WORD_RE.finditer(text))
    if len(words) <= n:
        return text.strip()
    if from_end:
        return '… ' + text[words[-n].start():].strip()
    return text[:words[n - 1].end()].strip() + ' …'


def build_kwic_lines(sentences, window=6, multi=False):
    lines = []
    for s in sentences:
        text = s.get('query_raw') or s.get('source_raw') or ''
        spans = sorted(tuple(sp) for sp in (s.get('match_spans') or []))
        if not text or not spans:
            continue
        groups = [spans] if multi else [[sp] for sp in spans]
        for g in groups:
            a, b = g[0][0], g[-1][1]
            lines.append({
                'id': s.get('id', ''), 'book': s.get('book', ''), 'query_lang': s.get('query_lang') or s.get('lang') or 'uz',
                'query_page': s.get('query_page'), 'other_page': s.get('other_page'),
                'left': clean_display(_cut_words(text[:a], window, True)), 'node': text[a:b],
                'right': clean_display(re.sub(r'^\d{1,3}(?=[\s,.;:!?»”"…)]|$)', '', _cut_words(text[b:], window, False))
                                       if text[a:b][-1:].isalpha() else _cut_words(text[b:], window, False)),
                'other_raw': clean_display(s.get('other_raw') or ''),
                'other_html': clean_display(s.get('other_highlighted') or html.escape(s.get('other_raw') or '')),
                'equivalent': s.get('equivalent_text') or '',
                'order': (0 if s.get('book') == 'cholpon' else 1, int(s.get('query_page') or 0), s.get('id', ''), a),
            })
    return lines


def sort_kwic_lines(lines, order):
    def word(t, last=False):
        ws = _KWIC_WORD_RE.findall(t or '')
        return (ws[-1] if last else ws[0]).lower() if ws else ''
    if order == 'chap':
        return sorted(lines, key=lambda l: (word(l['left'], True), l['order']))
    if order == 'ong':
        return sorted(lines, key=lambda l: (word(l['right']), l['order']))
    return sorted(lines, key=lambda l: l['order'])


def kwic_csv(lines, lang):
    import csv
    import io
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(['ID', get_i18n(lang, 'kwic_source'), get_i18n(lang, 'kwic_left'), get_i18n(lang, 'kwic_node'),
                get_i18n(lang, 'kwic_right'), get_i18n(lang, 'col_book_translation'), get_i18n(lang, 'kwic_parallel_sentence')])
    for l in lines:
        w.writerow([l['id'], side_label(lang, l['book'], l['query_lang'], l['query_page']), l['left'], l['node'], l['right'],
                    l.get('equivalent', ''), l['other_raw']])
    return '﻿' + out.getvalue()


def render_kwic_page(lang='uz', is_admin=False, query='', book='', window=6, order='matn', page=1, lines=None, q_lang='uz', error=''):
    lang = lang if lang in ('uz', 'en', 'ru') else 'uz'
    book = book if book in BOOK_FILTERS else ''
    window = window if isinstance(window, int) and 1 <= window <= 15 else 6
    order = order if order in ('matn', 'chap', 'ong') else 'matn'
    base = [(k, v) for k, v in (('q', query), ('kitob', book), ('oyna', window if query else ''), ('tartib', order if order != 'matn' else '')) if v]
    lines = lines or []

    def url(**extra):
        q2 = dict(base)
        q2.update(dict((k, v) for k, v in extra.items() if v))
        return with_lang('/kwic?' + urllib.parse.urlencode(q2), lang)

    def opt(value, label, cur):
        return '<option value="%s"%s>%s</option>' % (value, ' selected' if str(value) == str(cur) else '', label)

    books = opt('', T(lang, 'kwic_all_books'), book) + ''.join(opt(k, html.escape(v[1]), book) for k, v in BOOK_FILTERS.items())
    tpl = get_i18n(lang, 'kwic_words_n')
    slider = ('<div class="tc-range"><span>%s</span><div class="tc-range__row">'
              '<input type="range" name="oyna" min="1" max="15" step="1" value="%d" aria-label="%s">'
              '<output data-tpl="%s">%s</output></div><div class="tc-range__ticks" aria-hidden="true"><span>±1</span><span>±15</span></div></div>'
              % (T(lang, 'kwic_window'), window, T(lang, 'kwic_window'), html.escape(tpl), html.escape(tpl.replace('{n}', str(window)))))
    orders = opt('matn', T(lang, 'kwic_sort_text'), order) + opt('chap', T(lang, 'kwic_sort_left'), order) + opt('ong', T(lang, 'kwic_sort_right'), order)
    filters = ('<div class="tc-filters"><label>%s<select name="kitob">%s</select></label>%s'
               '<label>%s<select name="tartib">%s</select></label></div>'
               % (T(lang, 'kwic_book'), books, slider, T(lang, 'kwic_sort'), orders))
    body = ('<h1>%s</h1><p class="tc-lead">%s</p><div style="margin-top:20px">%s</div>'
            % (T(lang, 'kwic_title'), T(lang, 'kwic_intro'), search_form(lang, query, '', action='/kwic', extra_html=filters)))
    per = 50
    total_pages = max(1, (len(lines) + per - 1) // per)
    page_no = max(1, min(int(page or 1), total_pages))
    if query and error:
        body += '<div class="tc-panel" style="margin-top:24px">%s</div>' % T(lang, 'search_lang_error')
    elif query and not lines:
        body += '<div class="tc-panel" style="margin-top:24px"><p>%s</p></div>' % T(lang, 'not_in_corpus')
    elif query:
        chunk = lines[(page_no - 1) * per: page_no * per]
        rows = []
        for l in chunk:
            ql, ol = l['query_lang'], other_lang(l['query_lang'])
            rows.append('<tr><td class="l" lang="%s">%s</td><td class="n" lang="%s"><mark class="q">%s</mark></td><td class="r" lang="%s">%s</td>'
                        '<td class="s">%s<br>%s</td><td class="s e" lang="%s" style="white-space:normal;font-family:var(--serif);font-size:14px;color:var(--ink)">%s</td></tr>'
                        % (ql, html.escape(l['left']), ql, html.escape(l['node']), ql, html.escape(l['right']),
                           html.escape(TITLE_BY_SIDE.get((l['book'], ql), '')), html.escape(page_text(lang, l['query_page'])),
                           ol, html.escape(l.get('equivalent') or '—')))
        parallel = ''.join(pair_html(lang, l['book'], l['query_lang'],
                                     html.escape(l['left']) + ' <mark class="q">' + html.escape(l['node']) + '</mark> ' + html.escape(l['right']),
                                     l['query_page'], l['other_html'], l['other_page'], compact=True) for l in chunk)
        body += ('<section class="tc-section"><div class="tc-section__head"><h2 class="tc-num">%s</h2>'
                 '<a class="tc-btn tc-btn--ghost" href="%s">%s</a></div>'
                 '<div class="tc-panel tc-scroll" style="padding:4px 6px;margin-top:10px"><table class="tc-kwic"><thead><tr>'
                 '<th class="tc-small tc-muted" style="text-align:right;padding:8px 10px">%s</th><th class="tc-small tc-muted">%s</th>'
                 '<th class="tc-small tc-muted" style="text-align:left">%s</th><th class="tc-small tc-muted" style="text-align:left">%s</th>'
                 '<th class="tc-small tc-muted" style="text-align:left">%s</th></tr></thead><tbody>%s</tbody></table></div>'
                 '<details style="margin-top:18px"><summary style="cursor:pointer;color:var(--lapis)">%s</summary><div style="margin-top:12px">%s</div></details>%s</section>'
                 % (html.escape(count_phrase(len(lines), 'kwic_results_word', lang)), url(format='csv'), T(lang, 'kwic_export_csv'),
                    T(lang, 'kwic_left'), T(lang, 'kwic_node'), T(lang, 'kwic_right'), T(lang, 'kwic_source'), T(lang, 'col_book_translation'),
                    ''.join(rows), T(lang, 'kwic_view_parallel'), parallel, _pager(lang, page_no, total_pages, lambda p: url(page=p))))
    path = '/kwic' + ('?' + urllib.parse.urlencode(base) if base else '')
    return globals()['page'](lang, query or get_i18n(lang, 'kwic_title'), body, path, is_admin)
