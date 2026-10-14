/**
 * Global Helper: Normalise all apostrophe variants (ʻ ‘ ' ` ’ ʼ ´ ʹ ՚ ′ ‵ ˈ) to standard ASCII single quote '
 * Ensures unified matching across phones (iOS/Android ’), keyboards (ASCII ', backtick `), books/OCR (‘, ’, ʻ, ʼ).
 */
window.normalizeApostrophes = function(str) {
    if (!str) return '';
    return String(str).replace(/['’‘`ʻʼ´ʹ՚′‵ˈ]/g, "'");
};

class App {
    constructor() {
        this.currentTab = 'home';
        this.activeChapterId = 'kirish';
        this.fontSizeLevel = 1; // 0: small, 1: normal, 2: large
        this.init();
    }

    async init() {
        this.setupTheme();
        this.bindNavigation();
        this.setupModals();
        this.loadLiveStats();
        await this.checkAuth();
        
        // Lucide icons
        if (window.lucide) lucide.createIcons();
    }

    setupTheme() {
        const savedTheme = localStorage.getItem('korpus_theme') || 
            (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
        
        this.setTheme(savedTheme);

        const themeBtn = document.getElementById('themeToggleBtn');
        if (themeBtn) {
            themeBtn.addEventListener('click', () => {
                const current = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
                const next = current === 'dark' ? 'light' : 'dark';
                this.setTheme(next);
            });
        }
    }

    setTheme(theme) {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
            localStorage.setItem('korpus_theme', 'dark');
        } else {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('korpus_theme', 'light');
        }

        if (window.analyticsManager) {
            analyticsManager.updateTheme();
        }
    }

    bindNavigation() {
        const navLinks = document.querySelectorAll('[data-tab-target]');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = link.getAttribute('data-tab-target');
                this.switchTab(target);
            });
        });
    }

    switchTab(tabId) {
        // Guard Laboratoriya tabs from anonymous access (Part 1, Item 1)
        const labTabs = ['checker', 'translator', 'phd'];
        if (labTabs.includes(tabId) && !window.isAdmin) {
            this.showToast("Laboratoriya bo‘limi faqat tadqiqotchi (admin) uchun ochiq. Iltimos, pastdagi «Kirish» orqali kiring.", "warning");
            this.openLoginModal();
            return;
        }

        this.currentTab = tabId;

        // Update nav styles
        document.querySelectorAll('[data-tab-target]').forEach(link => {
            const isTarget = link.getAttribute('data-tab-target') === tabId;
            if (isTarget) {
                link.classList.add('nav-active');
            } else {
                link.classList.remove('nav-active');
            }
        });

        // Hide all views, show active
        document.querySelectorAll('.tab-view').forEach(view => {
            view.classList.add('hidden');
        });

        const activeView = document.getElementById(`view-${tabId}`);
        if (activeView) {
            activeView.classList.remove('hidden');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        // Initialize charts if entering analytics
        if (tabId === 'analytics') {
            setTimeout(() => {
                if (window.analyticsManager) analyticsManager.initCharts();
            }, 50);
        }

        if (window.lucide) lucide.createIcons();
    }

    async checkAuth() {
        try {
            const resp = await fetch('/api/auth/me');
            if (resp.ok) {
                const data = await resp.json();
                window.isAdmin = data.isAdmin === true;
                this.updateAuthUI(data);
            }
        } catch(e) {
            console.warn('Auth check failed:', e);
        }
    }

    updateAuthUI(data) {
        const isAdmin = data && data.isAdmin === true;
        const navLab = document.getElementById('nav-laboratoriya');
        const navLabMob = document.getElementById('nav-laboratoriya-mobile');

        if (navLab) {
            if (isAdmin) navLab.classList.remove('hidden');
            else navLab.classList.add('hidden');
        }
        if (navLabMob) {
            if (isAdmin) navLabMob.classList.remove('hidden');
            else navLabMob.classList.add('hidden');
        }

        const footerAuth = document.getElementById('footerAuthContainer');
        if (footerAuth) {
            if (isAdmin) {
                footerAuth.innerHTML = `
                    <span class="inline-flex items-center gap-1.5 font-bold text-indigo-600 dark:text-indigo-400">
                        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        Admin (Tadqiqotchi)
                        <button onclick="app.logout()" class="text-xs text-rose-500 hover:underline ml-1 font-semibold">Chiqish</button>
                    </span>
                `;
            } else {
                footerAuth.innerHTML = `
                    <button onclick="app.openLoginModal()" class="text-slate-400 hover:text-indigo-600 transition underline text-[11px]">Kirish</button>
                `;
            }
        }
        if (window.lucide) lucide.createIcons();
    }

    openLoginModal() {
        const modal = document.getElementById('adminLoginModal');
        const err = document.getElementById('loginErrorMsg');
        if (err) err.classList.add('hidden');
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            setTimeout(() => {
                document.getElementById('loginUsername')?.focus();
            }, 100);
        }
    }

    closeLoginModal() {
        const modal = document.getElementById('adminLoginModal');
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    }

    async submitLogin() {
        const u = (document.getElementById('loginUsername')?.value || '').trim();
        const p = document.getElementById('loginPassword')?.value || '';
        const err = document.getElementById('loginErrorMsg');
        const btn = document.getElementById('loginSubmitBtn');

        if (btn) btn.disabled = true;
        if (err) err.classList.add('hidden');

        try {
            const resp = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: u, password: p })
            });
            const data = await resp.json();
            if (resp.ok && data.success) {
                this.closeLoginModal();
                await this.checkAuth();
                this.showToast("Muvaffaqiyatli kirildi! Laboratoriya bo‘limi faollashtirildi.", "success");
            } else {
                if (err) {
                    err.textContent = data.error || "Noto‘g‘ri login yoki parol.";
                    err.classList.remove('hidden');
                }
            }
        } catch(e) {
            if (err) {
                err.textContent = "Tarmoq xatosi. Qayta urinib ko‘ring.";
                err.classList.remove('hidden');
            }
        } finally {
            if (btn) btn.disabled = false;
        }
    }

    async logout() {
        try {
            await fetch('/api/auth/logout', { method: 'POST' });
        } catch(e) {}
        await this.checkAuth();
        this.switchTab('home');
        this.showToast("Tizimdan chiqildi.", "info");
    }

    async loadLiveStats() {
        try {
            const resp = await fetch('/api/stats');
            if (resp.ok) {
                const data = await resp.json();
                const elSeg = document.getElementById('stat-total-segments');
                if (elSeg) elSeg.innerText = data.totalSegments ? data.totalSegments.toLocaleString() : '3,811';
                const elCol = document.getElementById('stat-total-collocations');
                if (elCol) elCol.innerText = data.totalCollocations ? data.totalCollocations.toLocaleString() : '5,377';
                const elDic = document.getElementById('stat-total-dict');
                if (elDic) elDic.innerText = data.totalDictionary ? data.totalDictionary.toLocaleString() : '10,898';
            }
        } catch(e) {
            console.warn('Live stats fetch failed:', e);
        }
    }

    setupModals() {
        const closeDetailBtn = document.getElementById('closeCollocModalBtn');
        if (closeDetailBtn) {
            closeDetailBtn.addEventListener('click', () => {
                if (window.collocationManager) collocationManager.closeModal();
            });
        }
    }

    setQuickSearch(word, lang = 'all') {
        const inp = document.getElementById('homeSearchInput');
        const sl = document.getElementById('homeSearchLang');
        if (inp) inp.value = word;
        if (sl && (lang === 'uz' || lang === 'en')) sl.value = lang;
        this.executeHomeSearch();
    }

    executeHomeSearch() {
        const query = (document.getElementById('homeSearchInput')?.value || '').trim();
        const lang = document.getElementById('homeSearchLang')?.value || 'all';
        this.switchTab('corpus');
        const corpusInput = document.getElementById('corpusSearchInput');
        if (corpusInput) {
            corpusInput.value = query;
        }
        if (window.corpusManager) {
            if (lang === 'uz' || lang === 'en') {
                corpusManager.selectedLang = lang;
                const cSelect = document.getElementById('corpusSearchLang');
                if (cSelect) cSelect.value = lang;
            }
            corpusManager.search(query);
        }
    }

    filterCollocs(sourceName) {
        this.switchTab('collocations');
        const filterSelect = document.getElementById('collocSourceFilter');
        if (filterSelect) {
            for (let i = 0; i < filterSelect.options.length; i++) {
                if (filterSelect.options[i].text.toLowerCase().includes(sourceName.toLowerCase()) || 
                    filterSelect.options[i].value.toLowerCase().includes(sourceName.toLowerCase())) {
                    filterSelect.selectedIndex = i;
                    break;
                }
            }
            if (window.collocationManager) {
                collocationManager.applyFilters();
            }
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        const bg = type === 'success' ? 'bg-emerald-600' :
                   type === 'warning' ? 'bg-amber-600' :
                   type === 'error' ? 'bg-rose-600' : 'bg-indigo-600';

        toast.className = `fixed bottom-6 right-6 ${bg} text-white px-4 py-3 rounded-2xl shadow-xl flex items-center gap-2 text-sm z-50 transition transform duration-300 translate-y-10 opacity-0`;
        const span = document.createElement('span');
        span.textContent = message;
        toast.appendChild(span);
        document.body.appendChild(toast);

        requestAnimationFrame(() => {
            toast.classList.remove('translate-y-10', 'opacity-0');
        });

        setTimeout(() => {
            toast.classList.add('translate-y-10', 'opacity-0');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Global instance
let app;
window.addEventListener('DOMContentLoaded', () => {
    app = new App();
});
