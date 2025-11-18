// Poll /portal/api/analytics/ and update Study Analytics & AI Insights UI
(function(){
    const endpoint = '/portal/api/analytics/';
    let autoRefresh = (localStorage.getItem('analyticsAutoRefresh') !== 'false');
    let previousSnapshot = null;

    function updateLearningStyleChart(data) {
        if (!window.learningStyleChartInstance) return;
        const chart = window.learningStyleChartInstance;
        chart.data.labels = data.labels;
        chart.data.datasets[0].data = data.values;
        chart.update('active');
    }

    function updateAITips(tips) {
        const container = document.querySelector('.ai-tips');
        if (!container) return;
        container.innerHTML = '';
        tips.forEach(t => {
            const div = document.createElement('div');
            div.className = 'tip-item mb-2';
            div.innerHTML = `
                <div class="d-flex align-items-center gap-2 mb-1">
                    <i class="fas fa-star text-warning"></i>
                    <span class="fw-semibold">${t.title}</span>
                </div>
                <p class="text-muted small mb-0">${t.description}</p>
            `;
            container.appendChild(div);
        });
    }

    function updateAchievements(ach) {
        const grid = document.querySelector('.achievement-grid .row');
        if (!grid) return;
        grid.innerHTML = '';
        ach.forEach(a => {
            const col = document.createElement('div');
            col.className = 'col-md-3 col-6';
            col.innerHTML = `
                <div class="achievement-item text-center p-2">
                    <i class="fas fa-trophy fa-2x mb-2 text-primary"></i>
                    <div class="achievement-title small fw-semibold">${a.title}</div>
                    <div class="text-muted smaller">${a.progress}%</div>
                </div>
            `;
            grid.appendChild(col);
        });
    }

    function updateSummary(peak, avg, total) {
        const peakNode = document.querySelector('.study-metrics .fw-semibold');
        if (peakNode) peakNode.textContent = peak;
        const avgNode = document.querySelector('[data-avg-session]');
        if (avgNode) avgNode.textContent = avg + ' hours';
        const totalNode = document.querySelector('[data-weekly-total]');
        if (totalNode) totalNode.textContent = total + ' hours';
    }

    function showToast(message) {
        try {
            const toastEl = document.getElementById('analyticsToast');
            if (!toastEl) return;
            const body = toastEl.querySelector('.toast-body');
            if (body) body.textContent = message;
            const toast = new bootstrap.Toast(toastEl);
            toast.show();
        } catch (e) {
            console.log('Toast show failed', e);
        }
    }

    function hasMeaningfulChange(newData) {
        if (!previousSnapshot) return true;
        try {
            // Compare learning style arrays and achievements lengths/progress
            const a1 = previousSnapshot.learning_style?.values || [];
            const a2 = newData.learning_style?.values || [];
            if (a1.length !== a2.length) return true;
            for (let i=0;i<a1.length;i++) if (a1[i] !== a2[i]) return true;

            const ach1 = previousSnapshot.achievements || [];
            const ach2 = newData.achievements || [];
            if (ach1.length !== ach2.length) return true;
            for (let i=0;i<Math.min(ach1.length, ach2.length); i++) {
                if ((ach1[i].progress || 0) !== (ach2[i].progress || 0)) return true;
            }

            // AI tips count change
            const tips1 = previousSnapshot.ai_tips || [];
            const tips2 = newData.ai_tips || [];
            if (tips1.length !== tips2.length) return true;
        } catch (e) {
            return true;
        }
        return false;
    }

    function fetchAndUpdate() {
        fetch(endpoint, {credentials: 'same-origin'})
            .then(r => r.json())
            .then(data => {
                if (data.error) return;

                // If meaningful change, show a small toast
                const changed = hasMeaningfulChange(data);

                updateLearningStyleChart(data.learning_style || {labels:[], values:[]});
                updateAITips(data.ai_tips || []);
                updateAchievements(data.achievements || []);
                updateSummary(data.peak_hours, data.avg_session, data.weekly_total);

                const last = document.getElementById('analyticsLastUpdated');
                if (last) last.textContent = 'Last updated: ' + new Date(data.last_updated).toLocaleString();

                if (changed) {
                    showToast('Study analytics updated');
                }

                // store snapshot for next comparison (lightweight)
                previousSnapshot = {
                    learning_style: data.learning_style,
                    achievements: data.achievements,
                    ai_tips: data.ai_tips
                };
            })
            .catch(err => {
                console.error('Analytics fetch error', err);
            });
    }

    // Auto-refresh toggle UI wiring
    function setAutoRefreshEnabled(enabled) {
        autoRefresh = !!enabled;
        localStorage.setItem('analyticsAutoRefresh', autoRefresh ? 'true' : 'false');
        const btn = document.getElementById('analyticsAutoRefreshBtn');
        if (btn) btn.textContent = 'Auto-refresh: ' + (autoRefresh ? 'On' : 'Off');
    }

    document.addEventListener('DOMContentLoaded', function(){
        const btn = document.getElementById('analyticsAutoRefreshBtn');
        if (btn) {
            setAutoRefreshEnabled(autoRefresh);
            btn.addEventListener('click', function(){
                setAutoRefreshEnabled(!autoRefresh);
            });
        }

        // Allow manual refresh by clicking the last-updated text
        const last = document.getElementById('analyticsLastUpdated');
        if (last) last.addEventListener('click', fetchAndUpdate);
    });

    // Start polling every 45s
    fetchAndUpdate();
    setInterval(() => { if (autoRefresh) fetchAndUpdate(); }, 45000);
})();