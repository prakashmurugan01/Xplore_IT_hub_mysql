// Live updates handling
function fetchLiveUpdates() {
    // Fetch updates from the server
    fetch('/portal/api/live-updates/')
        .then(response => response.json())
        .then(data => {
            const container = document.querySelector('.live-updates-container');
            if (!container) return;

            // Clear existing updates
            container.innerHTML = '';

            // Add new updates
            if (data.updates && data.updates.length > 0) {
                data.updates.forEach((update, index) => {
                    const updateElement = document.createElement('div');
                    updateElement.className = `live-update-item ${update.is_new ? 'new-update' : ''}`;
                    updateElement.innerHTML = `
                        <div class="d-flex align-items-center gap-2">
                            <div class="update-indicator" data-type="${update.type}"></div>
                            <div>
                                <div class="update-title">${update.title}</div>
                                <div class="update-time">${update.timestamp}</div>
                            </div>
                        </div>
                    `;
                    container.appendChild(updateElement);
                });
            } else {
                // Show empty state
                container.innerHTML = `
                    <div class="text-muted text-center py-3">
                        <i class="fas fa-info-circle"></i>
                        No recent updates
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error fetching updates:', error);
            // Show error state
            const container = document.querySelector('.live-updates-container');
            if (container) {
                container.innerHTML = `
                    <div class="text-danger text-center py-3">
                        <i class="fas fa-exclamation-circle"></i>
                        Failed to fetch updates
                    </div>
                `;
            }
        });
}

// Initialize live updates
fetchLiveUpdates();

// Refresh updates every minute
setInterval(fetchLiveUpdates, 60000);

// Manual refresh function
function refreshLiveUpdates() {
    const button = document.querySelector('.live-updates button');
    if (button) {
        const icon = button.querySelector('i');
        if (icon) {
            // Add spinning animation
            icon.classList.add('fa-spin');
            // Remove it after refresh
            setTimeout(() => icon.classList.remove('fa-spin'), 1000);
        }
    }
    fetchLiveUpdates();
}

// Initialize tooltips for update items
document.addEventListener('DOMContentLoaded', () => {
    // Enable Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});