/**
 * dashboard.js - Handles the main dashboard functionality
 * 
 * This script manages the dashboard UI, statistics, and scraping controls.
 */

// Global variables
let scrapingActive = false;
let statusUpdateInterval = null;
let statisticsUpdateInterval = null;

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
  // Initialize components
  initializeComponents();
  
  // Load initial data
  loadDashboardData();
  
  // Set up periodic updates
  setupPeriodicUpdates();
});

/**
 * Initialize dashboard components
 */
function initializeComponents() {
  // Set up event listeners for the scraping controls
  const startScrapingBtn = document.getElementById('startScrapingBtn');
  if (startScrapingBtn) {
    startScrapingBtn.addEventListener('click', startScraping);
  }
  
  // Set up event listeners for filter/control inputs
  const targetProfilesInput = document.getElementById('targetProfiles');
  if (targetProfilesInput) {
    targetProfilesInput.addEventListener('change', validateTargetProfiles);
  }
  
  // Set up location selector
  const locationSelect = document.getElementById('locationSelect');
  if (locationSelect) {
    populateLocationSelector(locationSelect);
  }
}

/**
 * Populate the location selector with available locations
 * 
 * @param {HTMLSelectElement} selectElement - The select element to populate
 */
function populateLocationSelector(selectElement) {
  // Add default option
  selectElement.innerHTML = '<option value="auto">Auto (Continue from current)</option>';
  
  // Fetch locations from the server
  fetch('/api/locations')
    .then(response => response.json())
    .then(data => {
      // Add locations to the selector
      data.locations.forEach(location => {
        const option = document.createElement('option');
        option.value = location.code;
        option.textContent = location.name;
        selectElement.appendChild(option);
      });
    })
    .catch(error => {
      console.error('Error fetching locations:', error);
      showToast('Error', 'Failed to load locations', 'error');
    });
}

/**
 * Validate the target profiles input
 */
function validateTargetProfiles() {
  const targetProfilesInput = document.getElementById('targetProfiles');
  let value = parseInt(targetProfilesInput.value);
  
  // Ensure the value is within the allowed range
  if (isNaN(value) || value < 1) {
    value = 1;
  } else if (value > 5000) {
    value = 5000;
  }
  
  targetProfilesInput.value = value;
}

/**
 * Load dashboard data from the server
 */
function loadDashboardData() {
  // Check scraping status
  checkScrapingStatus();
  
  // Load statistics
  loadStatistics();
  
  // Load recent activities
  loadRecentActivities();
}

/**
 * Set up periodic updates for the dashboard
 */
function setupPeriodicUpdates() {
  // Check scraping status every 5 seconds
  statusUpdateInterval = setInterval(checkScrapingStatus, 5000);
  
  // Update statistics every 30 seconds
  statisticsUpdateInterval = setInterval(loadStatistics, 30000);
  
  // Update recent activities every minute
  setInterval(loadRecentActivities, 60000);
}

/**
 * Check the current scraping status
 */
function checkScrapingStatus() {
  fetch('/api/scraping-status')
    .then(response => response.json())
    .then(data => {
      // Update global status
      scrapingActive = data.is_active;
      
      // Update UI based on status
      updateScrapingUI(data);
    })
    .catch(error => {
      console.error('Error checking scraping status:', error);
    });
}

/**
 * Update the UI based on scraping status
 * 
 * @param {Object} status - The scraping status data
 */
function updateScrapingUI(status) {
  const startBtn = document.getElementById('startScrapingBtn');
  
  if (status.is_active) {
    // Scraping is active
    startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scraping...';
    startBtn.disabled = true;
    
    // Update progress if available
    if (status.profiles_scraped && status.target_profiles) {
      const progress = Math.round((status.profiles_scraped / status.target_profiles) * 100);
      startBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Scraping (${progress}%)`;
    }
    
    // Update current location if available
    if (status.current_location) {
      document.getElementById('currentLocation').textContent = status.current_location.split(',')[0];
    }
  } else {
    // Scraping is not active
    startBtn.innerHTML = '<i class="fas fa-play"></i> Start Scraping';
    startBtn.disabled = false;
    
    // If there were errors, show them
    if (status.errors && status.errors.length > 0) {
      showToast('Error', status.errors[0], 'error');
    }
  }
}

/**
 * Load statistics from the server
 */
function loadStatistics() {
  fetch('/api/get-stats')
    .then(response => response.json())
    .then(data => {
      // Update total profiles
      const totalProfiles = document.getElementById('totalProfiles');
      totalProfiles.textContent = numberWithCommas(data.totalProfiles);
      
      // Update progress bar
      const totalProgress = (data.totalProfiles / 25000) * 100;
      document.getElementById('totalProfilesProgress').style.width = `${totalProgress}%`;
      
      // Update current milestone
      document.getElementById('currentMilestone').textContent = data.currentMilestone;
      
      // Update profiles in milestone
      document.getElementById('profilesInMilestone').textContent = numberWithCommas(data.profilesInCurrentMilestone);
      
      // Update milestone progress
      const milestoneProgress = (data.profilesInCurrentMilestone / 5000) * 100;
      document.getElementById('milestoneProgress').style.width = `${milestoneProgress}%`;
      
      // Update location
      const currentLocationElement = document.getElementById('currentLocation');
      if (currentLocationElement && data.currentLocation) {
        currentLocationElement.textContent = data.currentLocation.split(',')[0];
      }
      
      const profilesAtLocationElement = document.getElementById('profilesAtLocation');
      if (profilesAtLocationElement) {
        profilesAtLocationElement.textContent = `${numberWithCommas(data.profilesAtCurrentLocation || 0)} profiles scraped at this location`;
      }
    })
    .catch(error => {
      console.error('Error updating stats:', error);
    });
}

/**
 * Load recent activities from the server
 */
function loadRecentActivities() {
  fetch('/api/get-logs?type=extraction&limit=10')
    .then(response => response.json())
    .then(data => {
      renderRecentActivities(data.logs);
    })
    .catch(error => {
      console.error('Error loading recent activities:', error);
    });
}

/**
 * Render recent activities in the table
 * 
 * @param {Array} activities - Array of activity log entries
 */
function renderRecentActivities(activities) {
  const tableBody = document.getElementById('recentActivitiesTable');
  
  if (!tableBody || !activities) {
    return;
  }
  
  // Clear the table
  tableBody.innerHTML = '';
  
  // Add activity rows
  activities.forEach(activity => {
    const row = document.createElement('tr');
    
    // Timestamp
    const timestampCell = document.createElement('td');
    timestampCell.textContent = activity.Timestamp;
    row.appendChild(timestampCell);
    
    // Profile ID
    const profileIdCell = document.createElement('td');
    profileIdCell.textContent = activity['Profile ID'];
    row.appendChild(profileIdCell);
    
    // Location
    const locationCell = document.createElement('td');
    locationCell.textContent = activity.Location;
    row.appendChild(locationCell);
    
    // Status
    const statusCell = document.createElement('td');
    const statusBadge = document.createElement('span');
    statusBadge.className = 'log-status';
    
    switch (activity.Status) {
      case 'SCRAPED':
        statusBadge.classList.add('status-success');
        statusBadge.innerHTML = '<i class="fas fa-check-circle"></i> Scraped';
        break;
      case 'SKIPPED':
        statusBadge.classList.add('status-warning');
        statusBadge.innerHTML = '<i class="fas fa-exclamation-circle"></i> Skipped';
        break;
      case 'LOCATION_CHANGE':
        statusBadge.classList.add('status-info');
        statusBadge.innerHTML = '<i class="fas fa-map-marker-alt"></i> Location Changed';
        break;
      case 'ERROR':
        statusBadge.classList.add('status-error');
        statusBadge.innerHTML = '<i class="fas fa-times-circle"></i> Error';
        break;
      default:
        statusBadge.classList.add('status-info');
        statusBadge.innerHTML = '<i class="fas fa-info-circle"></i> ' + activity.Status;
    }
    
    statusCell.appendChild(statusBadge);
    row.appendChild(statusCell);
    
    tableBody.appendChild(row);
  });
}

/**
 * Start the scraping process
 */
function startScraping() {
  if (scrapingActive) {
    showToast('Warning', 'A scraping session is already running', 'error');
    return;
  }
  
  // Get form values
  const targetProfiles = document.getElementById('targetProfiles').value;
  const locationSelectElement = document.getElementById('locationSelect');
  const locationSelect = locationSelectElement.value;
  const selectedLocation = locationSelectElement.options[locationSelectElement.selectedIndex].text;
  
  // Show confirmation modal
  const scrapingParams = document.getElementById('scrapingParams');
  scrapingParams.innerHTML = `
    <li><strong>Target Profiles:</strong> ${targetProfiles}</li>
    <li><strong>Starting Location:</strong> ${selectedLocation}</li>
  `;
  
  // Set up confirm button
  const confirmBtn = document.getElementById('confirmScrapingBtn');
  confirmBtn.onclick = () => {
    // Close modal
    closeModal('startScrapingModal');
    
    // Prepare request data
    const requestData = {
      target_profiles: parseInt(targetProfiles),
      location: locationSelect === 'auto' ? null : locationSelect
    };
    
    // Call the API to start scraping
    fetch('/api/start-scraping', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        // Update UI
        const startBtn = document.getElementById('startScrapingBtn');
        startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scraping...';
        startBtn.disabled = true;
        scrapingActive = true;
        
        // Show success message
        showToast('Success', 'Scraping session started successfully');
        
        // Refresh status after a short delay
        setTimeout(checkScrapingStatus, 1000);
      } else {
        showToast('Error', data.message || 'Failed to start scraping', 'error');
      }
    })
    .catch(error => {
      console.error('Error starting scraping:', error);
      showToast('Error', 'Failed to start scraping session', 'error');
    });
  };
  
  // Show modal
  showModal('startScrapingModal');
}

/**
 * Show a modal dialog
 * 
 * @param {string} modalId - ID of the modal to show
 */
function showModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
  }
}

/**
 * Close a modal dialog
 * 
 * @param {string} modalId - ID of the modal to close
 */
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
  }
}

/**
 * Show a toast notification
 * 
 * @param {string} title - Title of the notification
 * @param {string} message - Message content
 * @param {string} type - Notification type ('success' or 'error')
 */
function showToast(title, message, type = 'success') {
  const toastContainer = document.getElementById('toastContainer');
  
  if (!toastContainer) {
    console.warn('Toast container not found');
    return;
  }
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  const iconClass = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';
  
  toast.innerHTML = `
    <div class="toast-icon">
      <i class="${iconClass}"></i>
    </div>
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      <div class="toast-message">${message}</div>
    </div>
    <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
  `;
  
  toastContainer.appendChild(toast);
  
  // Make toast visible after a small delay (for animation)
  setTimeout(() => {
    toast.classList.add('active');
  }, 10);
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    toast.classList.remove('active');
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 5000);
}

/**
 * Format a number with commas
 * 
 * @param {number} x - Number to format
 * @returns {string} Formatted number string
 */
function numberWithCommas(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
