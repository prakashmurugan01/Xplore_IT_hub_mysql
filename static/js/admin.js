// Admin Dashboard Charts using Chart.js
// User Distribution Chart
const userCtx = document.getElementById('userChart').getContext('2d');
// Read server-provided totals from a safe global object injected by the template.
const totalStudents = (window.DASHBOARD && Number(window.DASHBOARD.total_students)) || 0;
const totalTeachers = (window.DASHBOARD && Number(window.DASHBOARD.total_teachers)) || 0;

new Chart(userCtx, {
    type: 'doughnut',
    data: {
        labels: ['Students', 'Teachers'],
        datasets: [{
            data: [ totalStudents, totalTeachers ],
            backgroundColor: ['#0d6efd', '#198754'],
            borderWidth: 2
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                position: 'bottom'
            }
        }
    }
});

// Activity Chart
const activityCtx = document.getElementById('activityChart').getContext('2d');
new Chart(activityCtx, {
    type: 'line',
    data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
            label: 'Active Users',
            data: [65, 59, 80, 81, 56, 55, 40],
            borderColor: '#0d6efd',
            backgroundColor: 'rgba(13, 110, 253, 0.1)',
            tension: 0.4,
            fill: true
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                display: true,
                position: 'bottom'
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});