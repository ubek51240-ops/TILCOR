/**
 * Tadqiqot Statistikasi va Grafiklar Vizualizatsiyasi (Chart.js)
 */

class AnalyticsManager {
    constructor() {
        this.charts = {};
    }

    initCharts() {
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js yuklanmagan');
            return;
        }

        this.renderPatternChart();
        this.renderEquivalenceChart();
        this.renderGenreChart();
    }

    renderPatternChart() {
        const ctx = document.getElementById('patternChart');
        if (!ctx) return;

        if (this.charts.pattern) this.charts.pattern.destroy();

        const labels = researchStats.patterns.map(p => p.name);
        const data = researchStats.patterns.map(p => p.percentage);

        this.charts.pattern = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: ['#6366f1', '#10b981', '#f59e0b', '#8b5cf6'],
                    borderWidth: 2,
                    borderColor: document.documentElement.classList.contains('dark') ? '#1e293b' : '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: document.documentElement.classList.contains('dark') ? '#cbd5e1' : '#475569',
                            font: { family: 'Plus Jakarta Sans', size: 12 },
                            boxWidth: 12,
                            padding: 15
                        }
                    }
                },
                cutout: '68%'
            }
        });
    }

    renderEquivalenceChart() {
        const ctx = document.getElementById('equivalenceChart');
        if (!ctx) return;

        if (this.charts.equivalence) this.charts.equivalence.destroy();

        const labels = researchStats.equivalence.map(e => e.name);
        const data = researchStats.equivalence.map(e => e.percentage);
        const colors = researchStats.equivalence.map(e => e.color);

        this.charts.equivalence = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Ulush (%)',
                    data: data,
                    backgroundColor: colors,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 60,
                        ticks: {
                            color: document.documentElement.classList.contains('dark') ? '#94a3b8' : '#64748b',
                            callback: value => value + '%'
                        },
                        grid: {
                            color: document.documentElement.classList.contains('dark') ? '#334155' : '#f1f5f9'
                        }
                    },
                    x: {
                        ticks: {
                            color: document.documentElement.classList.contains('dark') ? '#cbd5e1' : '#475569',
                            font: { size: 11 }
                        },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    renderGenreChart() {
        const ctx = document.getElementById('genreChart');
        if (!ctx) return;

        if (this.charts.genre) this.charts.genre.destroy();

        const labels = researchStats.genres.map(g => g.name);
        const data = researchStats.genres.map(g => g.percentage);

        this.charts.genre = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: ['#3b82f6', '#ec4899', '#14b8a6'],
                    borderWidth: 2,
                    borderColor: document.documentElement.classList.contains('dark') ? '#1e293b' : '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: document.documentElement.classList.contains('dark') ? '#cbd5e1' : '#475569',
                            font: { family: 'Plus Jakarta Sans', size: 12 },
                            boxWidth: 12,
                            padding: 15
                        }
                    }
                }
            }
        });
    }

    updateTheme() {
        // Re-render when dark/light mode toggles
        if (typeof Chart !== 'undefined') {
            this.initCharts();
        }
    }
}

const analyticsManager = new AnalyticsManager();
