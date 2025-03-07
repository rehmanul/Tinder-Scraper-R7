/**
 * Dashboard functionality for the Tinder Scraper application
 * Handles status updates, statistics, and control interactions
 */

// Global variables
let scrapingActive = false;
let statsRefreshInterval = null;

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the dashboard
    initializeDashboard();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load initial data
    updateStatistics();
    loadRecentActivities();
    
    // Set up periodic updates
    startPeriodicUpdates();
});

/**
 * Initialize dashboard elements
 */
function initializeDashboard() {
    // Check for scraping status
    checkScrapingStatus();
    
    console.log('Dashboard initialized');
}

/**
 * Set up event listeners for dashboard controls
 */
function setupEventListeners() {
    // Start scraping button
    const startButton = document.getElementById('startScrapingBtn');
    if (startButton) {
        startButton.addEventListener('click', handleStartScraping);
    }
    
    // Filter controls
    const locationFilter = document.getElementById('locationFilter');
    if (locationFilter) {
        locationFilter.addEventListener('change', handleFilterChange);
    }
    
    // Refresh button
    const refreshButton = document.getElementById('refreshBtn');
    if (refreshButton) {
        refreshButton.addEventListener('click', handleRefresh);
    }
}

/**
 * Check the current scraping status
 */
function checkScrapingStatus() {
    fetch('/api/scraping-status')
        .then(response => response.json())
        .then(data => {
            updateScrapingStatusUI(data);
        })
        .catch(error => {
            console.error('Error fetching scraping status:', error);
            showToast('Error', 'Failed to fetch scraping status', 'error');
        });
}

/**
 * Update the UI based on scraping status
 */
function updateScrapingStatusUI(status) {
    const startButton = document.getElementById('startScrapingBtn');
    scrapingActive = status.is_active;
    
    if (scrapingActive) {
        // Update button state
        if (startButton) {
            startButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scraping...';
            startButton.disabled = true;
        }
        
        // Update progress indicators
        document.getElementById('totalProfiles').textContent = status.profiles_scraped || 0;
        
        // Calculate and update progress bars
        const totalProgress = (status.profiles_scraped / 25000) * 100;
        document.getElementById('totalProfilesProgress').style.width = `${totalProgress}%`;
        
        const milestoneNum = Math.floor(status.profiles_scraped / 5000) + 1;
        document.getElementById('currentMilestone').textContent = Math.min(milestoneNum, 5);
        
        const profilesInMilestone = status.profiles_scraped % 5000;
        document.getElementById('profilesInMilestone').textContent = profilesInMilestone;
        
        const milestoneProgress = (profilesInMilestone / 5000) * 100;
        document.getElementById('milestoneProgress').style.width = `${milestoneProgress}%`;
        
        // Show current location
        if (status.current_location) {
            document.getElementById('currentLocation').textContent = status.current_location.split(',')[0];
        }
    } else {
        // Reset button state if needed
        if (startButton && startButton.disabled) {
            startButton.innerHTML = '<i class="fas fa-play"></i> Start Scraping';
            startButton.disabled = false;
        }
    }
}

/**
 * Handle start scraping button click
 */
function handleStartScraping() {
    if (scrapingActive) {
        showToast('Warning', 'A scraping session is already running', 'warning');
        return;
    }
    
    // Show confirmation dialog
    const targetProfiles = document.getElementById('targetProfiles').value;
    const locationSelect = document.getElementById('locationFilter');
    const selectedLocation = locationSelect.options[locationSelect.selectedIndex].text;
    
    // Populate modal with parameters
    document.getElementById('scrapingParams').innerHTML = `
        <li><strong>Target Profiles:</strong> ${targetProfiles}</li>
        <li><strong>Starting Location:</strong> ${selectedLocation}</li>
    `;
    
    // Show the modal
    showModal('startScrapingModal');
    
    // Set up confirmation button
    document.getElementById('confirmScrapingBtn').onclick = function() {
        startScraping(targetProfiles, locationSelect.value);
    };
}

/**
 * Start the scraping process
 */
function startScraping(targetProfiles, location) {
    // Close the modal
    closeModal('startScrapingModal');
    
    // Update UI
    const startBtn = document.getElementById('startScrapingBtn');
    startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scraping...';
    startBtn.disabled = true;
    scrapingActive = true;
    
    // Prepare location data
    let locations = null;
    if (location && location !== 'auto') {
        locations = [location];
    }
    
    // Call the API
    fetch('/api/start-scraping', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            target_profiles: parseInt(targetProfiles),
            locations: locations
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showToast('Success', data.message, 'success');
            
            // Start periodic updates if not already running
            if (!statsRefreshInterval) {
                startPeriodicUpdates();
            }
        } else {
            showToast('Error', data.message, 'error');
            resetScrapingButton();
        }
    })
    .catch(error => {
        console.error('Error starting scraping:', error);
        showToast('Error', 'Failed to start scraping process', 'error');
        resetScrapingButton();
    });
}

/**
 * Reset the scraping button state
 */
function resetScrapingButton() {
    const startBtn = document.getElementById('startScrapingBtn');
    startBtn.innerHTML = '<i class="fas fa-play"></i> Start Scraping';
    startBtn.disabled = false;
    scrapingActive = false;
}

/**
 * Start periodic updates of statistics and activities
 */
function startPeriodicUpdates() {
    // Clear any existing intervals
    if (statsRefreshInterval) {
        clearInterval(statsRefreshInterval);
    }
    
    // Set up new interval
    statsRefreshInterval = setInterval(function() {
        updateStatistics();
        loadRecentActivities();
        checkScrapingStatus();
    }, 10000); // Update every 10 seconds
}

/**
 * Update statistics from the API
 */
function updateStatistics() {
    fetch('/api/get-stats')
        .then(response => response.json())
        .then(data => {
            // Update total profiles
            document.getElementById('totalProfiles').textContent = data.totalProfiles;
            
            // Update progress bar
            const totalProgress = (data.totalProfiles / 25000) * 100;
            document.getElementById('totalProfilesProgress').style.width = `${totalProgress}%`;
            
            // Update current milestone
            document.getElementById('currentMilestone').textContent = data.currentMilestone;
            
            // Update profiles in milestone
            document.getElementById('profilesInMilestone').textContent = data.profilesInCurrentMilestone;
            
            // Update milestone progress
            const milestoneProgress = (data.profilesInCurrentMilestone / 5000) * 100;
            document.getElementById('milestoneProgress').style.width = `${milestoneProgress}%`;
            
            // Update location information
            document.getElementById('currentLocation').textContent = data.currentLocation.split(',')[0];
            document.getElementById('profilesAtLocation').textContent = 
                `${data.profilesAtCurrentLocation} profiles scraped at this location`;
        })
        .catch(error => {
            console.error('Error updating statistics:', error);
        });
}

/**
 * Load recent activities from the API
 */
function loadRecentActivities() {
    fetch('/api/get-logs?type=extraction&limit=5')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('recentActivitiesTable');
            if (!tableBody) return;
            
            tableBody.innerHTML = '';
            
            if (!data.logs || data.logs.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="4">No recent activities found</td>
                    </tr>
                `;
                return;
            }
            
            data.logs.forEach(log => {
                const row = document.createElement('tr');
                
                // Create timestamp cell
                const timestampCell = document.createElement('td');
                timestampCell.textContent = log.Timestamp || 'N/A';
                row.appendChild(timestampCell);
                
                // Create profile ID cell
                const profileIdCell = document.createElement('td');
                profileIdCell.textContent = log['Profile ID'] || 'N/A';
                row.appendChild(profileIdCell);
                
                // Create location cell
                const locationCell = document.createElement('td');
                locationCell.textContent = log.Location || 'N/A';
                row.appendChild(locationCell);
                
                // Create status cell with appropriate formatting
                const statusCell = document.createElement('td');
                const statusBadge = document.createElement('span');
                statusBadge.className = 'status-badge';
                
                const status = log.Status || 'UNKNOWN';
                let badgeClass = 'status-info';
                let badgeIcon = 'info-circle';
                
                if (status === 'SCRAPED') {
                    badgeClass = 'status-success';
                    badgeIcon = 'check-circle';
                } else if (status === 'SKIPPED') {
                    badgeClass = 'status-warning';
                    badgeIcon = 'exclamation-circle';
                } else if (status === 'ERROR') {
                    badgeClass = 'status-error';
                    badgeIcon = 'times-circle';
                } else if (status === 'LOCATION_CHANGE') {
                    badgeClass = 'status-info';
                    badgeIcon = 'map-marker-alt';
                }
                
                statusBadge.className += ' ' + badgeClass;
                statusBadge.innerHTML = `<i class="fas fa-${badgeIcon}"></i> ${status}`;
                statusCell.appendChild(statusBadge);
                row.appendChild(statusCell);
                
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error loading recent activities:', error);
            
            const tableBody = document.getElementById('recentActivitiesTable');
            if (tableBody) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="4">Error loading activities: ${error.message}</td>
                    </tr>
                `;
            }
        });
}

/**
 * Handle filter change
 */
function handleFilterChange() {
    loadRecentActivities();
}

/**
 * Handle refresh button click
 */
function handleRefresh() {
    updateStatistics();
    loadRecentActivities();
    checkScrapingStatus();
}

/**
 * Show a modal
 */
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

/**
 * Close a modal
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

/**
 * Show a toast notification
 */
function showToast(title, message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const iconClass = type === 'success' ? 'check-circle' : 
                      type === 'error' ? 'times-circle' : 'exclamation-circle';
    
    toast.innerHTML = `
        <div class="toast-icon">
            <i class="fas fa-${iconClass}"></i>
        </div>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Show with animation
    setTimeout(() => toast.classList.add('active'), 10);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        toast.classList.remove('active');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}