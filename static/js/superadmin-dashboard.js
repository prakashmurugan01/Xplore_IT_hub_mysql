/**
 * Superadmin Dashboard JavaScript
 * Handles all dashboard interactions, data fetching, and UI updates
 */

(function SuperadminDashboard() {
  'use strict';

  // ==========================================================================
  // Configuration
  // ==========================================================================
  const CONFIG = {
    POLL_INTERVAL_MS: 10000, // 10 seconds
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY_MS: 1000,
    DEBOUNCE_DELAY_MS: 300,
    DATE_FORMAT: 'YYYY-MM-DD'
  };

  // ==========================================================================
  // State Management
  // ==========================================================================
  const state = {
    attendanceCache: new Map(),
    chart: null,
    pollInterval: null,
    modals: {},
    isVisible: true
  };

  // ==========================================================================
  // Utility Functions
  // ==========================================================================

  /**
   * Escape HTML to prevent XSS
   */
  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  /**
   * Get CSRF token from DOM or cookies
   */
  function getCsrfToken() {
    // Try to get from hidden input first
    const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (tokenInput) {
      return tokenInput.value;
    }
    
    // Fallback to cookie
    const cookie = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='));
    
    return cookie ? cookie.split('=')[1] : '';
  }

  /**
   * Debounce function calls
   */
  function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
  }

  /**
   * Fetch with retry logic
   */
  async function fetchWithRetry(url, options = {}, retries = CONFIG.RETRY_ATTEMPTS) {
    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch(url, options);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response;
      } catch (error) {
        console.error(`Fetch attempt ${i + 1} failed:`, error);
        if (i === retries - 1) throw error;
        await new Promise(resolve => setTimeout(resolve, CONFIG.RETRY_DELAY_MS * (i + 1)));
      }
    }
  }

  /**
   * Build URL with query parameters
   */
  function buildUrl(baseUrl, params = {}) {
    const url = new URL(baseUrl, window.location.origin);
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        url.searchParams.set(key, value);
      }
    });
    return url.toString();
  }

  // ==========================================================================
  // Toast Notifications
  // ==========================================================================

  const Toast = {
    show(message, type = 'info', title = 'Notification') {
      const toastEl = document.getElementById('notificationToast');
      if (!toastEl) return;

      const toastBody = document.getElementById('toastBody');
      const toastTitle = document.getElementById('toastTitle');
      const toastIcon = document.getElementById('toastIcon');

      // Set content
      toastBody.textContent = message;
      toastTitle.textContent = title;

      // Set icon based on type
      const iconMap = {
        success: 'fa-check-circle text-success',
        error: 'fa-exclamation-circle text-danger',
        warning: 'fa-exclamation-triangle text-warning',
        info: 'fa-info-circle text-info'
      };
      
      toastIcon.className = `fas ${iconMap[type] || iconMap.info} me-2`;
      toastEl.classList.add(`toast-${type}`);

      // Show toast
      const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 5000
      });
      toast.show();

      // Clean up class after hidden
      toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.classList.remove(`toast-${type}`);
      }, { once: true });
    },

    success(message, title = 'Success') {
      this.show(message, 'success', title);
    },

    error(message, title = 'Error') {
      this.show(message, 'error', title);
    },

    warning(message, title = 'Warning') {
      this.show(message, 'warning', title);
    },

    info(message, title = 'Info') {
      this.show(message, 'info', title);
    }
  };

  // ==========================================================================
  // Theme Management
  // ==========================================================================

  const Theme = {
    init() {
      const toggleBtn = document.getElementById('theme-toggle');
      if (!toggleBtn) return;

      // Load saved theme
      const savedTheme = localStorage.getItem('theme');
      if (savedTheme === 'light') {
        this.setLight();
      }

      // Add event listener
      toggleBtn.addEventListener('click', () => this.toggle());
    },

    toggle() {
      const isLight = document.body.classList.contains('light-mode');
      if (isLight) {
        this.setDark();
      } else {
        this.setLight();
      }
    },

    setLight() {
      document.body.classList.add('light-mode');
      const toggleBtn = document.getElementById('theme-toggle');
      if (toggleBtn) {
        toggleBtn.innerHTML = '<i class="fas fa-sun" aria-hidden="true"></i>';
        toggleBtn.setAttribute('aria-label', 'Switch to dark theme');
      }
      localStorage.setItem('theme', 'light');
    },

    setDark() {
      document.body.classList.remove('light-mode');
      const toggleBtn = document.getElementById('theme-toggle');
      if (toggleBtn) {
        toggleBtn.innerHTML = '<i class="fas fa-moon" aria-hidden="true"></i>';
        toggleBtn.setAttribute('aria-label', 'Switch to light theme');
      }
      localStorage.setItem('theme', 'dark');
    }
  };

  // ==========================================================================
  // Chart Management
  // ==========================================================================

  const ChartManager = {
    init() {
      const ctx = document.getElementById('signupsChart');
      if (!ctx) return;

      try {
        const labels = JSON.parse(document.getElementById('signup-labels-json')?.textContent || '[]');
        const data = JSON.parse(document.getElementById('signup-counts-json')?.textContent || '[]');

        state.chart = new Chart(ctx.getContext('2d'), {
          type: 'bar',
          data: {
            labels: labels,
            datasets: [{
              label: 'Signups',
              data: data,
              backgroundColor: '#4F46E5',
              borderRadius: 6,
              borderWidth: 0
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
              legend: {
                display: false
              },
              tooltip: {
                mode: 'index',
                intersect: false,
                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                titleColor: '#e2e8f0',
                bodyColor: '#e2e8f0',
                borderColor: 'rgba(148, 163, 184, 0.2)',
                borderWidth: 1
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                grid: {
                  color: 'rgba(148, 163, 184, 0.1)'
                },
                ticks: {
                  color: '#94a3b8'
                }
              },
              x: {
                grid: {
                  display: false
                },
                ticks: {
                  color: '#94a3b8'
                }
              }
            }
          }
        });
      } catch (error) {
        console.error('Failed to initialize chart:', error);
        Toast.error('Failed to load signup chart');
      }
    },

    update(labels, data) {
      if (!state.chart) return;
      
      try {
        state.chart.data.labels = labels;
        state.chart.data.datasets[0].data = data;
        state.chart.update('none'); // Update without animation for performance
      } catch (error) {
        console.error('Failed to update chart:', error);
      }
    },

    destroy() {
      if (state.chart) {
        state.chart.destroy();
        state.chart = null;
      }
    }
  };

  // ==========================================================================
  // Dashboard Updates
  // ==========================================================================

  const DashboardUpdates = {
    async fetch() {
      try {
        const response = await fetchWithRetry('/superadmin/api/updates/');
        if (!response.ok) return;

        const data = await response.json();
        this.updateStats(data);
        this.updateRecentUsers(data.recent_users || []);
        this.updateChart(data.signup_labels || [], data.signup_counts || []);
      } catch (error) {
        console.warn('Dashboard updates failed:', error);
        // Don't show error toast for background polling failures
      }
    },

    updateStats(data) {
      const elements = {
        su_total_students: data.total_students,
        su_total_teachers: data.total_teachers,
        su_total_courses: data.total_courses,
        su_other_count: data.other_count
      };

      Object.entries(elements).forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (el && value !== undefined) {
          this.animateNumber(el, parseInt(value) || 0);
        }
      });
    },

    animateNumber(element, targetValue) {
      const currentValue = parseInt(element.textContent) || 0;
      if (currentValue === targetValue) return;

      const duration = 500;
      const steps = 20;
      const stepValue = (targetValue - currentValue) / steps;
      const stepDuration = duration / steps;
      let currentStep = 0;

      const timer = setInterval(() => {
        currentStep++;
        const newValue = Math.round(currentValue + (stepValue * currentStep));
        element.textContent = newValue;

        if (currentStep >= steps) {
          element.textContent = targetValue;
          clearInterval(timer);
        }
      }, stepDuration);
    },

    updateRecentUsers(users) {
      const tbody = document.getElementById('su_recent_users');
      if (!tbody) return;

      const reportTemplate = tbody.dataset.reportUrlTemplate || '/superadmin/download-report/0/';
      tbody.innerHTML = '';

      users.forEach(user => {
        const tr = document.createElement('tr');
        tr.setAttribute('data-user-id', user.id);
        
        const reportUrl = reportTemplate.replace('/0/', `/${user.id}/`);
        
        tr.innerHTML = `
          <td>${escapeHtml(user.username)}</td>
          <td>${escapeHtml(user.email)}</td>
          <td>${escapeHtml(user.role || '-')}</td>
          <td>${escapeHtml(user.joined || '-')}</td>
          <td>
            <a class="btn btn-sm btn-light" 
               href="${reportUrl}"
               aria-label="Download report for ${escapeHtml(user.username)}">
              <i class="fas fa-download"></i> Report
            </a>
          </td>
        `;
        
        tbody.appendChild(tr);
      });
    },

    updateChart(labels, counts) {
      ChartManager.update(labels, counts);
    }
  };

  // ==========================================================================
  // Attendance Management
  // ==========================================================================

  const Attendance = {
    init() {
      const dateInput = document.getElementById('attendanceDate');
      if (dateInput) {
        dateInput.value = new Date().toISOString().slice(0, 10);
      }

      // Event listeners
      const refreshBtn = document.getElementById('attendanceRefresh');
      if (refreshBtn) {
        refreshBtn.addEventListener('click', () => this.fetch());
      }

      // Initial fetch
      this.fetch();
    },

    async fetch() {
      try {
        const dateInput = document.getElementById('attendanceDate');
        const deptInput = document.getElementById('attendanceDept');
        const daysSelect = document.getElementById('historyDays');

        const params = {
          date: dateInput?.value || '',
          department: deptInput?.value || '',
          days: daysSelect?.value || '7'
        };

        const url = buildUrl('/admin2/api/attendance/list/', params);
        
        // Show loading state
        this.showLoading();

        const response = await fetchWithRetry(url);
        if (!response.ok) throw new Error('Failed to fetch attendance');

        const data = await response.json();
        this.render(data.records || []);
        this.updateExportLink(params);
      } catch (error) {
        console.error('Attendance fetch failed:', error);
        Toast.error('Failed to load attendance data. Please try again.');
        this.showError();
      }
    },

    showLoading() {
      const tbody = document.getElementById('attendanceBody');
      if (!tbody) return;

      tbody.innerHTML = `
        <tr>
          <td colspan="6" class="text-center text-muted">
            <div class="spinner-border spinner-border-sm" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            Loading attendance...
          </td>
        </tr>
      `;
    },

    showError() {
      const tbody = document.getElementById('attendanceBody');
      if (!tbody) return;

      tbody.innerHTML = `
        <tr>
          <td colspan="6" class="text-center text-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            Failed to load attendance data
          </td>
        </tr>
      `;
    },

    render(records) {
      // Update summary counts
      const totalCount = records.length;
      const presentCount = records.filter(r => r.status === 'present').length;
      const absentCount = records.filter(r => r.status === 'absent').length;

      const totalEl = document.getElementById('totalStaffCount');
      const presentEl = document.getElementById('presentCount');
      const absentEl = document.getElementById('absentCount');

      if (totalEl) totalEl.textContent = totalCount;
      if (presentEl) presentEl.textContent = presentCount;
      if (absentEl) absentEl.textContent = absentCount;

      // Update table
      const tbody = document.getElementById('attendanceBody');
      if (!tbody) return;

      tbody.innerHTML = '';

      if (records.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="6" class="text-center text-muted">
              No attendance records found for the selected criteria
            </td>
          </tr>
        `;
        return;
      }

      records.forEach(record => {
        // Cache record for details view
        state.attendanceCache.set(record.staff_id, record);

        const tr = document.createElement('tr');
        
        const photoHtml = record.photo_url 
          ? `<img src="${escapeHtml(record.photo_url)}" 
                  alt="${escapeHtml(record.full_name || record.username)}"
                  style="width:36px; height:36px; object-fit:cover; border-radius:50%; margin-right:8px;">` 
          : '<i class="fas fa-user-circle" style="font-size:36px; margin-right:8px; color:#64748b;"></i>';

        const statusBadge = record.status === 'present' 
          ? '<span class="badge bg-success">Present</span>'
          : '<span class="badge bg-danger">Absent</span>';

        const lastAttendance = record.last_attendance 
          ? new Date(record.last_attendance).toLocaleString()
          : '-';

        tr.innerHTML = `
          <td>
            ${photoHtml}
            <div class="d-inline-block align-middle">
              <strong>${escapeHtml(record.full_name || record.username)}</strong>
              <div class="small text-muted">${escapeHtml(record.username)}</div>
            </div>
          </td>
          <td>${escapeHtml(record.department || '-')}</td>
          <td>${escapeHtml(record.position || '-')}</td>
          <td>${statusBadge}</td>
          <td><small>${lastAttendance}</small></td>
          <td>
            <button class="btn btn-sm btn-light view-details" 
                    data-staff-id="${record.staff_id}"
                    aria-label="View details for ${escapeHtml(record.full_name || record.username)}">
              <i class="fas fa-info-circle"></i> Details
            </button>
          </td>
        `;
        
        tbody.appendChild(tr);
      });
    },

    updateExportLink(params) {
      const exportLink = document.getElementById('attendanceExport');
      if (!exportLink) return;

      const url = buildUrl('/admin2/export/attendance/', params);
      exportLink.href = url;
    },

    async showDetails(staffId) {
      try {
        // Check cache first
        const cachedRecord = state.attendanceCache.get(staffId);
        
        if (cachedRecord) {
          this.renderDetailsModal(cachedRecord);
          return;
        }

        // Fetch from server if not in cache
        const dateInput = document.getElementById('attendanceDate');
        const daysSelect = document.getElementById('historyDays');

        const params = {
          date: dateInput?.value || '',
          days: daysSelect?.value || '7',
          staff_id: staffId
        };

        const url = buildUrl('/admin2/api/attendance/list/', params);
        const response = await fetchWithRetry(url);
        
        if (!response.ok) throw new Error('Failed to fetch staff details');

        const data = await response.json();
        const record = (data.records || [])[0];

        if (!record) {
          Toast.warning('Staff details not found');
          return;
        }

        this.renderDetailsModal(record);
      } catch (error) {
        console.error('Failed to fetch staff details:', error);
        Toast.error('Failed to load staff details');
      }
    },

    renderDetailsModal(record) {
      const modalEl = document.getElementById('detailsModal');
      const modalBody = document.getElementById('detailsModalBody');
      const modalTitle = document.getElementById('detailsModalLabel');

      if (!modalEl || !modalBody || !modalTitle) return;

      modalTitle.textContent = `${record.full_name || record.username} - Attendance Details`;

      const photoHtml = record.photo_url 
        ? `<img src="${escapeHtml(record.photo_url)}" 
                alt="${escapeHtml(record.full_name || record.username)}"
                class="rounded-circle mb-3"
                style="width:80px; height:80px; object-fit:cover;">` 
        : '';

      const historyHtml = (record.history_dates || []).map((date, index) => {
        const status = record.history[index] || '-';
        const statusClass = status === 'present' ? 'text-success' : status === 'absent' ? 'text-danger' : 'text-muted';
        return `
          <tr>
            <td>${escapeHtml(date)}</td>
            <td class="${statusClass}">${escapeHtml(status)}</td>
          </tr>
        `;
      }).join('');

      modalBody.innerHTML = `
        <div class="text-center">
          ${photoHtml}
        </div>
        <div class="row mb-3">
          <div class="col-md-6">
            <strong>Name:</strong> ${escapeHtml(record.full_name || record.username)}
          </div>
          <div class="col-md-6">
            <strong>Username:</strong> ${escapeHtml(record.username)}
          </div>
        </div>
        <div class="row mb-3">
          <div class="col-md-6">
            <strong>Department:</strong> ${escapeHtml(record.department || '-')}
          </div>
          <div class="col-md-6">
            <strong>Position:</strong> ${escapeHtml(record.position || '-')}
          </div>
        </div>
        <div class="row mb-3">
          <div class="col-md-6">
            <strong>Today's Status:</strong> 
            ${record.status === 'present' 
              ? '<span class="badge bg-success">Present</span>'
              : '<span class="badge bg-danger">Absent</span>'}
          </div>
          <div class="col-md-6">
            <strong>Last Attendance:</strong> 
            ${record.last_attendance ? new Date(record.last_attendance).toLocaleString() : '-'}
          </div>
        </div>
        <hr>
        <h6>Recent History</h6>
        <div class="table-responsive">
          <table class="table table-sm table-striped">
            <thead>
              <tr>
                <th>Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              ${historyHtml || '<tr><td colspan="2" class="text-muted text-center">No history available</td></tr>'}
            </tbody>
          </table>
        </div>
      `;

      const modal = new bootstrap.Modal(modalEl);
      modal.show();
    }
  };

  // ==========================================================================
  // Polling Management
  // ==========================================================================

  const Polling = {
    start() {
      this.stop();
      
      // Initial fetch
      DashboardUpdates.fetch();

      // Set up interval
      state.pollInterval = setInterval(() => {
        if (state.isVisible) {
          DashboardUpdates.fetch();
        }
      }, CONFIG.POLL_INTERVAL_MS);
    },

    stop() {
      if (state.pollInterval) {
        clearInterval(state.pollInterval);
        state.pollInterval = null;
      }
    }
  };

  // ==========================================================================
  // Event Handlers
  // ==========================================================================

  function setupEventListeners() {
    // Attendance details button delegation
    document.body.addEventListener('click', (event) => {
      if (event.target.closest('.view-details')) {
        const button = event.target.closest('.view-details');
        const staffId = button.dataset.staffId;
        if (staffId) {
          Attendance.showDetails(staffId);
        }
      }
    });

    // Visibility change - pause polling when tab is hidden
    document.addEventListener('visibilitychange', () => {
      state.isVisible = !document.hidden;
      
      if (state.isVisible) {
        // Resume polling and fetch latest data
        Polling.start();
      }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (event) => {
      // Ctrl/Cmd + K to focus search
      if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.getElementById('suSearchInput');
        if (searchInput) {
          const modal = bootstrap.Modal.getInstance(document.getElementById('suListModal'));
          if (modal) {
            searchInput.focus();
          }
        }
      }

      // Ctrl/Cmd + R to refresh attendance
      if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
        event.preventDefault();
        Attendance.fetch();
      }
    });

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
      Polling.stop();
      ChartManager.destroy();
    });
  }

  // ==========================================================================
  // Initialization
  // ==========================================================================

  function init() {
    console.log('Initializing Superadmin Dashboard...');

    try {
      Theme.init();
      ChartManager.init();
      Attendance.init();
      setupEventListeners();
      Polling.start();

      console.log('Superadmin Dashboard initialized successfully');
    } catch (error) {
      console.error('Failed to initialize dashboard:', error);
      Toast.error('Failed to initialize dashboard. Please refresh the page.');
    }
  }

  // Start when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Export for debugging (optional)
  window.SuperadminDashboard = {
    state,
    Theme,
    ChartManager,
    Attendance,
    Toast
  };

})();