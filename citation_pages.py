"""Permanent citation pages: /soz/<word> and /kollokatsiya/<reference id>.

They show the same sections as the search page (equivalents, word forms, collocations, sentence pairs)
and add a ready citation line. Corpus collocations (/kollokatsiya/uz-…, /kollokatsiya/en-…) are rendered
by ui_components.render_collocation_detail.
"""
import html
import urllib.parse
from datetime import datetime

import ui_components as ui

SITE_URL = "https://tilcor.uz"
PLATFORM_VERSION = "3.3"


def _citation(lang, title, kind_key, path):
    date_str = datetime.now().strftime("%d.%m.%Y")
    text = 'TILCOR. (2026). %s [%s]. TILCOR, %s %s. %s%s (%s: %s)' % (
        title, ui.get_i18n(lang, kind_key), ui.get_i18n(lang, 'version_word'), PLATFORM_VERSION,
        SITE_URL, path, ui.get_i18n(lang, 'access_date'), date_str)
    return ('<section class="tc-section"><h2>%s</h2><p class="tc-panel tc-small" style="margin-top:12px;font-family:var(--serif)">%s</p></section>'
            % (ui.T(lang, 'perm_citation_page'), html.escape(text)))


def _sections(lang, res, query, path):
    def make_url(p):
        return ui.with_lang('%s?page=%d' % (path, p), lang)
    return (ui.render_equivalents(res, lang, query) + ui.render_word_forms(res, lang)
            + ui.render_collocations(res, lang) + ui.render_sentences(res, lang, make_url))


def generate_word_citation_html(lemma, res, lang='uz'):
    lang = lang if lang in ('uz', 'en', 'ru') else 'uz'
    res = res or {}
    path = '/soz/' + urllib.parse.quote(lemma)
    q_lang = res.get('selected_lang') or 'uz'
    occ = int((res.get('summary') or {}).get('corpus_occurrences') or 0)
    body = ('<p class="tc-small"><a href="%s">%s</a></p><h1 lang="%s" style="margin-top:8px">%s</h1><p class="tc-lead tc-num">%s. %s</p>'
            % (ui.with_lang('/qidiruv?q=' + urllib.parse.quote(lemma), lang), ui.T(lang, 'nav_word_search'), q_lang, html.escape(lemma),
               html.escape(ui.count_phrase(occ, 'occurrences_in_corpus', lang)), ui.T(lang, 'q_lang_uz') if q_lang == 'uz' else ui.T(lang, 'q_lang_en')))
    body += _sections(lang, res, lemma, path) + _citation(lang, lemma, 'profile_word', path)
    return ui.page(lang, lemma, body, path, False)


def generate_collocation_citation_html(colloc_id, colloc_data, search_res=None, lang='uz'):
    """A collocation of the reference collections: its source list, and how the corpus renders it (if it occurs)."""
    lang = lang if lang in ('uz', 'en', 'ru') else 'uz'
    item = colloc_data or {}
    res = search_res or {}
    name = item.get('english') or item.get('collocation') or colloc_id
    path = '/kollokatsiya/' + urllib.parse.quote(str(colloc_id))
    meta = '%s; %s: %s' % (ui.pattern_label(item.get('pattern', ''), lang), ui.get_i18n(lang, 'col_source_list'), item.get('sourceBook') or '—')
    body = ('<p class="tc-small"><a href="%s">%s</a></p><h1 lang="en" style="margin-top:8px">%s</h1><p class="tc-lead">%s</p>'
            '<p class="tc-section__note" style="margin-top:10px">%s</p>'
            % (ui.with_lang('/kollokatsiyalar?manba=malumotnoma', lang), ui.T(lang, 'ref_lists_title'), html.escape(name),
               html.escape(meta), ui.T(lang, 'ref_lists_note')))
    if (res.get('pagination') or {}).get('total_sentences'):
        body += _sections(lang, res, name, path)
    else:
        body += '<div class="tc-panel" style="margin-top:24px"><p>%s</p></div>' % ui.T(lang, 'not_in_corpus')
    body += _citation(lang, name, 'profile_collocation', path)
    return ui.page(lang, name, body, path, False)
