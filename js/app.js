/**
 * KORPUS.LINGVO Asosiy Ilova Kontrolleri
 */

class App {
    constructor() {
        this.currentTab = 'home';
        this.activeChapterId = 'kirish';
        this.fontSizeLevel = 1; // 0: small, 1: normal, 2: large
        this.init();
    }

    init() {
        this.setupTheme();
        this.bindNavigation();
        // this.renderChaptersNav();
        // this.renderActiveChapter();
        // this.bindChapterControls();
        this.setupModals();
        this.loadLiveStats();
        
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
                analyticsManager.initCharts();
            }, 50);
        }

        if (window.lucide) lucide.createIcons();
    }

    renderChaptersNav() { /* unpublished */ }

    
    async loadLiveStats() {
        try {
            const resp = await fetch('/api/stats');
            if (resp.ok) {
                const data = await resp.json();
                const elSeg = document.getElementById('stat-total-segments');
                if (elSeg) elSeg.innerText = data.totalSegments ? data.totalSegments.toLocaleString() : '—';
                const elCol = document.getElementById('stat-total-collocations');
                if (elCol) elCol.innerText = data.totalCollocations ? data.totalCollocations.toLocaleString() : '—';
                const elDic = document.getElementById('stat-total-dict');
                if (elDic) elDic.innerText = data.totalDictionary ? data.totalDictionary.toLocaleString() : '—';
                const elMod = document.getElementById('stat-total-modules');
                if (elMod) elMod.innerText = '6 ta';
            }
        } catch(e) {
            console.warn('Live stats fetch failed:', e);
        }
    }

    selectChapter(chapterId) {
        this.activeChapterId = chapterId;
        // this.renderChaptersNav();
        // this.renderActiveChapter();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    renderActiveChapter() { /* unpublished */ }

    bindChapterControls() {
        const fontDecreaseBtn = document.getElementById('readerFontDecrease');
        const fontIncreaseBtn = document.getElementById('readerFontIncrease');
        const printBtn = document.getElementById('readerPrintBtn');

        if (fontDecreaseBtn) {
            fontDecreaseBtn.addEventListener('click', () => {
                const content = document.getElementById('chapterContentContainer');
                if (content) {
                    content.classList.remove('text-lg', 'text-xl');
                    content.classList.add('text-sm');
                    this.showToast("Shrift kichraytirildi", "info");
                }
            });
        }

        if (fontIncreaseBtn) {
            fontIncreaseBtn.addEventListener('click', () => {
                const content = document.getElementById('chapterContentContainer');
                if (content) {
                    content.classList.remove('text-sm');
                    content.classList.add('text-lg');
                    this.showToast("Shrift kattalashtirildi", "info");
                }
            });
        }

        if (printBtn) {
            printBtn.addEventListener('click', () => {
                window.print();
            });
        }
    }

    setupModals() {
        // Collocation detail modal close
        const closeDetailBtn = document.getElementById('closeCollocModalBtn');
        if (closeDetailBtn) {
            closeDetailBtn.addEventListener('click', () => {
                collocationManager.closeModal();
            });
        }

        // Add sentence modal
        const openAddModalBtn = document.getElementById('openAddSentenceModalBtn');
        const addModal = document.getElementById('addSentenceModal');
        const closeAddModalBtn = document.getElementById('closeAddSentenceModalBtn');
        const addSentenceForm = document.getElementById('addSentenceForm');

        if (openAddModalBtn && addModal) {
            openAddModalBtn.addEventListener('click', () => {
                addModal.classList.remove('hidden');
                addModal.classList.add('flex');
            });
        }

        if (closeAddModalBtn && addModal) {
            closeAddModalBtn.addEventListener('click', () => {
                addModal.classList.add('hidden');
                addModal.classList.remove('flex');
            });
        }

        if (addSentenceForm) {
            addSentenceForm.addEventListener('submit', (e) => {
                e.preventDefault();
                // Fix D12: Arbitrary unverified additions to scientific corpus disabled
                this.showToast("Ilmiy korpusga erkin jumla kiritish cheklangan. Barcha ma'lumotlar faqat verifikatsiyalangan nashrlardan olinadi.", "warning");
                addModal.classList.add('hidden');
                addModal.classList.remove('flex');
                addSentenceForm.reset();
            });
        }
    }

    sendToLab(text) {
        if (!text) return;
        this.switchTab('checker');
        const textarea = document.getElementById('checkerInputText');
        if (textarea) {
            textarea.value = text;
            if (window.collocationChecker) {
                collocationChecker.analyzeText(text);
            }
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        const bg = type === 'success' ? 'bg-emerald-600' :
                   type === 'warning' ? 'bg-amber-600' :
                   type === 'error' ? 'bg-rose-600' : 'bg-indigo-600';

        toast.className = `fixed bottom-6 right-6 ${bg} text-white px-4 py-3 rounded-2xl shadow-xl flex items-center gap-2 text-sm z-50 transition transform duration-300 translate-y-10 opacity-0`;
        // Fix D12: Safe textContent rendering to prevent XSS
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
