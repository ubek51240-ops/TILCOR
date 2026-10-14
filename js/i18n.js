/**
 * js/i18n.js - Interface Internationalization (Oʻzbekcha · English · Русский)
 * Compliant with Part 4 of TILCOR_03-1.
 * Supports independent UI language switch (Oʻz · En · Ру),
 * URL parameter (?lang=uz|en|ru), localStorage, cookie, and <html lang>.
 */

(function() {
    window.TILCOR_I18N = {
        currentLang: 'uz',
        locales: {},

        async init() {
            // 1. Detect language: URL param > localStorage > cookie > 'uz'
            const urlParams = new URLSearchParams(window.location.search);
            const urlLang = urlParams.get('lang');
            const savedLang = localStorage.getItem('tilcor_ui_lang');
            
            let chosen = 'uz';
            if (urlLang && ['uz', 'en', 'ru'].includes(urlLang.toLowerCase())) {
                chosen = urlLang.toLowerCase();
            } else if (savedLang && ['uz', 'en', 'ru'].includes(savedLang)) {
                chosen = savedLang;
            }

            await this.loadLocale(chosen);
            this.setLanguage(chosen, false);
        },

        async loadLocale(lang) {
            if (this.locales[lang]) return;
            try {
                const res = await fetch(`/locales/${lang}.json`);
                if (res.ok) {
                    this.locales[lang] = await res.json();
                }
            } catch (e) {
                console.warn(`[i18n] Failed to load locale for ${lang}:`, e);
            }
        },

        t(key, fallback = '') {
            const loc = this.locales[this.currentLang];
            if (loc && loc[key]) {
                return loc[key];
            }
            // Fallback to uzbek
            const uzLoc = this.locales['uz'];
            if (uzLoc && uzLoc[key]) {
                return uzLoc[key];
            }
            return fallback || key;
        },

        formatNumber(n) {
            if (typeof n !== 'number') return n;
            if (this.currentLang === 'en') {
                return n.toLocaleString('en-US');
            } else if (this.currentLang === 'ru') {
                return n.toLocaleString('ru-RU');
            } else {
                // Uzbek standard: space separator
                return n.toLocaleString('uz-UZ').replace(/,/g, ' ');
            }
        },

        async setLanguage(lang, updateUrl = true) {
            if (!['uz', 'en', 'ru'].includes(lang)) return;
            this.currentLang = lang;
            await this.loadLocale(lang);

            // Persist
            localStorage.setItem('tilcor_ui_lang', lang);
            document.cookie = `tilcor_ui_lang=${lang};path=/;max-age=31536000;SameSite=Lax`;
            document.documentElement.lang = lang;

            if (updateUrl) {
                const url = new URL(window.location);
                url.searchParams.set('lang', lang);
                window.history.replaceState({}, '', url);
            }

            // Update UI Switcher buttons active state
            ['uz', 'en', 'ru'].forEach(l => {
                const btn = document.getElementById(`langBtn-${l}`);
                if (btn) {
                    if (l === lang) {
                        btn.className = "px-2 py-1 rounded-lg transition font-bold bg-white dark:bg-slate-700 shadow-sm text-indigo-600 dark:text-indigo-400";
                    } else {
                        btn.className = "px-2 py-1 rounded-lg transition font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white";
                    }
                }
            });

            // Translate all elements with data-i18n
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                const translation = this.t(key);
                if (translation) {
                    if (el.tagName === 'INPUT' && el.getAttribute('placeholder')) {
                        el.placeholder = translation;
                    } else {
                        el.textContent = translation;
                    }
                }
            });
        }
    };

    window.setInterfaceLang = function(lang) {
        window.TILCOR_I18N.setLanguage(lang);
    };

    document.addEventListener('DOMContentLoaded', () => {
        window.TILCOR_I18N.init();
    });
})();
