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
        this.renderChaptersNav();
        this.renderActiveChapter();
        this.bindChapterControls();
        this.setupModals();
        
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

    renderChaptersNav() {
        const navContainer = document.getElementById('chaptersNavList');
        if (!navContainer) return;

        navContainer.innerHTML = dissertationData.sections.map(section => {
            const isActive = section.id === this.activeChapterId;
            return `
                <button onclick="app.selectChapter('${section.id}')" class="w-full text-left p-3 rounded-xl transition flex items-start gap-3 ${
                    isActive 
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20' 
                    : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                }">
                    <span class="p-2 rounded-lg ${isActive ? 'bg-indigo-500/50 text-white' : 'bg-slate-100 dark:bg-slate-800 text-indigo-600 dark:text-indigo-400'}">
                        <i data-lucide="${section.icon || 'book'}" class="w-4 h-4"></i>
                    </span>
                    <div class="overflow-hidden">
                        <span class="text-[11px] uppercase tracking-wider font-bold block ${isActive ? 'text-indigo-200' : 'text-slate-400'}">${section.number}</span>
                        <span class="text-xs font-semibold block truncate">${section.title}</span>
                    </div>
                </button>
            `;
        }).join('');
    }

    selectChapter(chapterId) {
        this.activeChapterId = chapterId;
        this.renderChaptersNav();
        this.renderActiveChapter();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    renderActiveChapter() {
        const container = document.getElementById('chapterContentContainer');
        if (!container) return;

        const section = dissertationData.sections.find(s => s.id === this.activeChapterId);
        if (!section) return;

        let contentHtml = '';

        if (section.content) {
            contentHtml = section.content;
        } else if (section.paragraphs) {
            contentHtml = `
                <div class="space-y-8">
                    ${section.paragraphs.map(p => `
                        <article class="p-6 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm" id="${p.id}">
                            <div class="flex items-center gap-2 mb-3">
                                <span class="px-2.5 py-0.5 rounded-full text-xs font-bold font-mono bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
                                    ${p.num}
                                </span>
                                <h3 class="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
                                    ${p.title}
                                </h3>
                            </div>
                            <div class="prose max-w-none text-slate-700 dark:text-slate-300 leading-relaxed font-sans text-sm sm:text-base">
                                ${p.body}
                            </div>
                        </article>
                    `).join('')}

                    ${section.summary ? `
                        <div class="p-5 bg-gradient-to-r from-indigo-500/10 via-emerald-500/10 to-transparent rounded-2xl border border-indigo-200 dark:border-indigo-900">
                            <h4 class="text-sm font-bold text-indigo-900 dark:text-indigo-300 flex items-center gap-2 mb-1.5">
                                <i data-lucide="check-circle" class="w-4 h-4 text-emerald-500"></i> Bob boʻyicha ilmiy xulosalar:
                            </h4>
                            <p class="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">${section.summary}</p>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        container.innerHTML = `
            <div class="mb-6 pb-4 border-b border-slate-200 dark:border-slate-700">
                <span class="text-xs uppercase font-mono tracking-widest font-bold text-indigo-600 dark:text-indigo-400">${section.number}</span>
                <h2 class="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white mt-1">${section.title}</h2>
                <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">${section.subtitle || ''}</p>
            </div>
            ${contentHtml}
        `;

        if (window.lucide) lucide.createIcons();
    }

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
                const uz = document.getElementById('inputNewUz').value;
                const en = document.getElementById('inputNewEn').value;
                const source = document.getElementById('inputNewSource').value;
                const genre = document.getElementById('inputNewGenre').value;
                const collocUz = document.getElementById('inputNewCollocUz').value;
                const collocEn = document.getElementById('inputNewCollocEn').value;
                const pattern = document.getElementById('inputNewPattern').value;

                corpusManager.addCustomSentence(uz, en, source, genre, collocUz, collocEn, pattern);

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
        toast.innerHTML = `<span>${message}</span>`;
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
