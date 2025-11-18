// Learning Style Chart
function initLearningStyleChart() {
    const ctx = document.getElementById('learningStyleChart').getContext('2d');
    const data = {
        labels: ['Visual', 'Auditory', 'Reading', 'Kinesthetic'],
        datasets: [{
            data: [35, 25, 20, 20],
            backgroundColor: [
                'rgba(40, 167, 69, 0.8)',
                'rgba(0, 123, 255, 0.8)',
                'rgba(255, 193, 7, 0.8)',
                'rgba(220, 53, 69, 0.8)'
            ],
            borderColor: 'rgba(255, 255, 255, 0.8)',
            borderWidth: 1
        }]
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    boxWidth: 12,
                    padding: 15,
                    color: '#6c757d',
                    font: {
                        size: 11
                    }
                }
            }
        }
    };

    new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: options
    });
}

// Study Timer
class StudyTimer {
    constructor() {
        this.timeLeft = 1500; // 25 minutes in seconds
        this.timerId = null;
        this.isRunning = false;

        this.display = document.getElementById('timerDisplay');
        this.startBtn = document.getElementById('startTimer');
        this.pauseBtn = document.getElementById('pauseTimer');
        this.resetBtn = document.getElementById('resetTimer');
        this.presetSelect = document.getElementById('timerPreset');

        this.initializeEventListeners();
        this.updateDisplay();
    }

    initializeEventListeners() {
        this.startBtn.addEventListener('click', () => this.start());
        this.pauseBtn.addEventListener('click', () => this.pause());
        this.resetBtn.addEventListener('click', () => this.reset());
        this.presetSelect.addEventListener('change', () => {
            this.timeLeft = parseInt(this.presetSelect.value);
            this.updateDisplay();
        });
    }

    formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
    }

    updateDisplay() {
        this.display.textContent = this.formatTime(this.timeLeft);
    }

    start() {
        if (!this.isRunning) {
            this.isRunning = true;
            this.startBtn.disabled = true;
            this.pauseBtn.disabled = false;
            
            this.timerId = setInterval(() => {
                this.timeLeft--;
                this.updateDisplay();
                
                if (this.timeLeft <= 0) {
                    this.complete();
                }
            }, 1000);
        }
    }

    pause() {
        if (this.isRunning) {
            this.isRunning = false;
            this.startBtn.disabled = false;
            this.pauseBtn.disabled = true;
            clearInterval(this.timerId);
        }
    }

    reset() {
        this.pause();
        this.timeLeft = parseInt(this.presetSelect.value);
        this.updateDisplay();
    }

    complete() {
        this.pause();
        // Play notification sound
        const audio = new Audio('/static/audio/timer-complete.mp3');
        audio.play();
        
        // Show notification
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Study Timer Complete', {
                body: 'Time for a break! Great job staying focused.',
                icon: '/static/img/logo.png'
            });
        }
    }
}

// Analytics Period Selector
document.querySelectorAll('.dropdown-item[data-period]').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const period = e.target.getAttribute('data-period');
        updateAnalytics(period);
    });
});

function updateAnalytics(period) {
    // Simulate API call to get data for the selected period
    const periodData = {
        week: {
            productiveTime: '9 AM - 11 AM',
            avgSession: '1.5 hours',
            total: '28.5 hours',
            improvement: 15
        },
        month: {
            productiveTime: '10 AM - 12 PM',
            avgSession: '2 hours',
            total: '120 hours',
            improvement: 22
        },
        year: {
            productiveTime: 'Varies',
            avgSession: '1.8 hours',
            total: '960 hours',
            improvement: 45
        }
    };

    const data = periodData[period];
    
    // Update the metrics display
    document.querySelector('.study-metrics').innerHTML = `
        <div class="d-flex justify-content-between mb-2">
            <span class="text-muted">Most Productive Time:</span>
            <span class="fw-semibold">${data.productiveTime}</span>
        </div>
        <div class="d-flex justify-content-between mb-2">
            <span class="text-muted">Average Session:</span>
            <span class="fw-semibold">${data.avgSession}</span>
        </div>
        <div class="d-flex justify-content-between">
            <span class="text-muted">Total Hours:</span>
            <span class="fw-semibold">${data.total}</span>
        </div>
    `;

    // Update improvement text
    document.querySelector('.text-success.small').innerHTML = `
        <i class="fas fa-arrow-up"></i>
        ${data.improvement}% improvement in focus time
    `;
}

// Initialize components
document.addEventListener('DOMContentLoaded', () => {
    initLearningStyleChart();
    new StudyTimer();
});

// Ask for notification permission
if ('Notification' in window && Notification.permission !== 'granted') {
    Notification.requestPermission();
}