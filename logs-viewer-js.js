/**
 * logs-viewer.js - Handles the logs viewing functionality
 * 
 * This script manages displaying and filtering log data in the web interface.
 */

// Global variables
let currentTab = 'extraction-logs';
let currentPage = 1;
let totalPages = 1;
let currentFilters = {
  dateFrom: '',
  dateTo: '',
  status: '',
  location: ''
};

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
  // Initialize components
  initializeComponents();
  
  // Set default date range for the last 7 days
  setDefaultDateRange();
  
  // Load initial logs
  loadLogs('extraction-logs');
});

/**
 * Initialize logs viewer components
 */
function initializeComponents() {
  // Set up tab switching
  const tabs = document.querySelectorAll('.tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const tabId = tab.textContent.toLowerCase().replace(' ', '-');
      switchTab(tabId);
    });
  });
  
  // Set up filter inputs
  const dateFrom = document.getElementById('dateFrom');
  const dateTo = document.getElementById('dateTo');
  const statusFilter = document.getElementById('statusFilter');
  const locationFilter = document.getElementById('locationFilter');
  
  if (dateFrom) {
    dateFrom.addEventListener('change', () => {
      currentFilters.dateFrom = dateFrom.value;
    });
  }
  
  if (dateTo) {
    dateTo.addEventListener('change', () => {
      currentFilters.dateTo = dateTo.value;
    });
  }
  
  if (statusFilter) {
    statusFilter.addEventListener('change', () => {
      currentFilters.status = statusFilter.value;
    });
  }
  
  if (locationFilter) {
    locationFilter.addEventListener('change', () => {
      currentFilters.location = locationFilter.value;
    });
  }
  
  // Set up apply filters button
  const applyFiltersBtn = document.querySelector('.log-button.primary');
  if (applyFiltersBtn) {
    applyFiltersBtn.addEventListener('click', applyFilters);
  }
  
  // Set up refresh button
  const refreshBtn = document.querySelectorAll('.log-button[onclick="refreshLogs()"]');
  refreshBtn.forEach(btn => {
    btn.addEventListener('click', refreshLogs);
  });
  
  // Set up export buttons
  const exportBtns = document.querySelectorAll('.log-button[onclick^="exportLogs"]');
  exportBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const type = currentTab === 'extraction-logs' ? 'extraction' : 'error';
      exportLogs(type);
    });
  });
}

/**
 * Set default date range for the last 7 days
 */
function setDefaultDateRange() {
  const dateFrom = document.getElementById('dateFrom');
  const dateTo = document.getElementById('dateTo');
  
  if (dateFrom && dateTo) {
    const today = new Date();
    const lastWeek = new Date();
    lastWeek.setDate(today.getDate() - 7);
    
    // Format dates as YYYY-MM-DD
    dateFrom.value = formatDate(lastWeek);
    dateTo.value = formatDate(today);
    
    // Update filters
    currentFilters.dateFrom = dateFrom.value;
    currentFilters.dateTo = dateTo.value;
  }
}

/**
 * Format a date as YYYY-MM-DD
 * 
 * @param {Date} date - Date to format
 * @returns {string} Formatted date string
 */
function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Switch between extraction and error logs tabs
 * 
 * @param {string} tabId - ID of the tab to switch to
 */
function switchTab(tabId) {
  // Update current tab
  currentTab = tabId;
  currentPage = 1;
  
  // Update tab UI
  const tabs = document.querySelectorAll('.tab');
  tabs.forEach(tab => {
    tab.classList.toggle('active', tab.textContent.toLowerCase().replace(' ', '-') === tabId);
  });
  
  // Show/hide containers
  document.getElementById('extraction-logs-container').style.display = tabId === 'extraction-logs' ? 'block' : 'none';
  document.getElementById('error-logs-container').style.display = tabId === 'error-logs' ? 'block' : 'none';
  
  // Load logs for the selected tab
  loadLogs(tabId);
}

/**
 * Load logs from the server
 * 
 * @param {string} tabId - ID of the current tab
 * @param {number} page - Page number to load
 */
function loadLogs(tabId, page = 1) {
  // Determine log type
  const logType = tabId === 'extraction-logs' ? 'extraction' : 'error';
  
  // Build query params
  const queryParams = new URLSearchParams();
  queryParams.append('type', logType);
  queryParams.append('page', page);
  queryParams.append('limit', 20);
  
  if (currentFilters.dateFrom) {
    queryParams.append('date_from', currentFilters.dateFrom);
  }
  
  if (currentFilters.dateTo) {
    queryParams.append('date_to', currentFilters.dateTo);
  }
  
  if (currentFilters.status) {
    queryParams.append('status', currentFilters.status);
  }
  
  if (currentFilters.location) {
    queryParams.append('location', currentFilters.location);
  }
  
  // Show loading state
  const tableBody = document.getElementById(`${logType}-logs-body`);
  if (tableBody) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align: center; padding: 20px;">
          <i class="fas fa-spinner fa-spin" style="font-size: 24px;"></i>
          <div style="margin-top: 10px;">Loading logs...</div>
        </td>
      </tr>
    `;
  }
  
  // Make API request
  fetch(`/api/get-logs?${queryParams.toString()}`)
    .then(response => response.json())
    .then(data => {
      // Update current page and total pages
      currentPage = page;
      totalPages = Math.ceil(data.total / 20) || 1;
      
      // Render logs
      if (logType === 'extraction') {
        renderExtractionLogs(data.logs);
      } else {
        renderErrorLogs(data.logs);
      }
      
      // Render pagination
      renderPagination(currentPage, totalPages);
    })
    .catch(error => {
      console.error(`Error loading ${logType} logs:`, error);
      
      // Show error state
      if (tableBody) {
        tableBody.innerHTML = `
          <tr>
            <td colspan="6" style="text-align: center; padding: 20px;">
              <i class="fas fa-exclamation-circle" style="font-size: 24px; color: #dc3545;"></i>
              <div style="margin-top: 10px;">Error loading logs. Please try again.</div>
            </td>
          </tr>
        `;
      }
    });
}

/**
 * Render extraction logs
 * 
 * @param {Array} logs - Array of extraction log entries
 */
function renderExtractionLogs(logs) {
  const tableBody = document.getElementById('extraction-logs-body');
  
  if (!tableBody) {
    return;
  }
  
  // Check if we have logs to display
  if (!logs || logs.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="6">
          <div class="no-results">
            <i class="fas fa-search no-results-icon"></i>
            <div class="no-results-title">No logs found</div>
            <div class="no-results-message">There are no extraction logs matching your filters.</div>
          </div>
        </td>
      </tr>
    `;
    return;
  }
  
  // Clear table body
  tableBody.innerHTML = '';
  
  // Add log rows
  logs.forEach(log => {
    const row = document.createElement('tr');
    
    // Timestamp
    const timestampCell = document.createElement('td');
    timestampCell.textContent = log.Timestamp || '';
    row.appendChild(timestampCell);
    
    // Profile ID
    const profileIdCell = document.createElement('td');
    profileIdCell.textContent = log['Profile ID'] || '';
    row.appendChild(profileIdCell);
    
    // Location
    const locationCell = document.createElement('td');
    locationCell.textContent = log.Location || '';
    row.appendChild(locationCell);
    
    // Status
    const statusCell = document.createElement('td');
    const statusBadge = document.createElement('span');
    statusBadge.className = 'log-status';
    
    switch (log.Status) {
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
        statusBadge.innerHTML = '<i class="fas fa-info-circle"></i> ' + (log.Status || 'Unknown');
    }
    
    statusCell.appendChild(statusBadge);
    row.appendChild(statusCell);
    
    // Details
    const detailsCell = document.createElement('td');
    detailsCell.className = 'log-details';
    
    const details = log.Details || '';
    if (details.length > 30) {
      detailsCell.textContent = details.substring(0, 30) + '...';
      
      const expandButton = document.createElement('button');
      expandButton.className = 'expand-button';
      expandButton.textContent = 'More';
      expandButton.addEventListener('click', () => viewLogDetails('extraction', log));
      
      detailsCell.appendChild(expandButton);
    } else {
      detailsCell.textContent = details;
    }
    
    row.appendChild(detailsCell);
    
    // Actions
    const actionsCell = document.createElement('td');
    
    const viewButton = document.createElement('button');
    viewButton.className = 'log-button';
    viewButton.innerHTML = '<i class="fas fa-eye"></i>';
    viewButton.addEventListener('click', () => viewLogDetails('extraction', log));
    
    actionsCell.appendChild(viewButton);
    row.appendChild(actionsCell);
    
    tableBody.appendChild(row);
  });
}

/**
 * Render error logs
 * 
 * @param {Array} logs - Array of error log entries
 */
function renderErrorLogs(logs) {
  const tableBody = document.getElementById('error-logs-body');
  
  if (!tableBody) {
    return;
  }
  
  // Check if we have logs to display
  if (!logs || logs.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="6">
          <div class="no-results">
            <i class="fas fa-check-circle no-results-icon"></i>
            <div class="no-results-title">No errors found</div>
            <div class="no-results-message">There are no error logs matching your filters.</div>
          </div>
        </td>
      </tr>
    `;
    return;
  }
  
  // Clear table body
  tableBody.innerHTML = '';
  
  // Add log rows
  logs.forEach(log => {
    const row = document.createElement('tr');
    
    // Timestamp
    const timestampCell = document.createElement('td');
    timestampCell.textContent = log.Timestamp || '';
    row.appendChild(timestampCell);
    
    // Error Type
    const errorTypeCell = document.createElement('td');
    errorTypeCell.textContent = log['Error Type'] || '';
    row.appendChild(errorTypeCell);
    
    // Location
    const locationCell = document.createElement('td');
    locationCell.textContent = log.Location || '';
    row.appendChild(locationCell);
    
    // Profile ID
    const profileIdCell = document.createElement('td');
    profileIdCell.textContent = log['Profile ID'] || 'N/A';
    row.appendChild(profileIdCell);
    
    // Error Message
    const messageCell = document.createElement('td');
    messageCell.className = 'log-details';
    
    const message = log['Error Message'] || '';
    if (message.length > 30) {
      messageCell.textContent = message.substring(0, 30) + '...';
      
      const expandButton = document.createElement('button');
      expandButton.className = 'expand-button';
      expandButton.textContent = 'More';
      expandButton.addEventListener('click', () => viewLogDetails('error', log));
      
      messageCell.appendChild(expandButton);
    } else {
      messageCell.textContent = message;
    }
    
    row.appendChild(messageCell);
    
    // Actions
    const actionsCell = document.createElement('td');
    
    const viewButton = document.createElement('button');
    viewButton.className = 'log-button';
    viewButton.innerHTML = '<i class="fas fa-eye"></i>';
    viewButton.addEventListener('click', () => viewLogDetails('error', log));
    
    actionsCell.appendChild(viewButton);
    row.appendChild(actionsCell);
    
    tableBody.appendChild(row);
  });
}

/**
 * Render pagination controls
 * 
 * @param {number} currentPage - Current page number
 * @param {number} totalPages - Total number of pages
 */
function renderPagination(currentPage, totalPages) {
  const paginationEl = document.getElementById('pagination');
  
  if (!paginationEl) {
    return;
  }
  
  // Clear pagination
  paginationEl.innerHTML = '';
  
  // Previous button
  const prevButton = document.createElement('button');
  prevButton.className = `page-button ${currentPage === 1 ? 'disabled' : ''}`;
  prevButton.innerHTML = '<i class="fas fa-chevron-left"></i>';
  prevButton.disabled = currentPage === 1;
  prevButton.addEventListener('click', () => {
    if (currentPage > 1) {
      goToPage(currentPage - 1);
    }
  });
  paginationEl.appendChild(prevButton);
  
  // Page buttons
  const startPage = Math.max(1, currentPage - 2);
  const endPage = Math.min(totalPages, startPage + 4);
  
  for (let i = startPage; i <= endPage; i++) {
    const pageButton = document.createElement('button');
    pageButton.className = `page-button ${i === currentPage ? 'active' : ''}`;
    pageButton.textContent = i;
    pageButton.addEventListener('click', () => goToPage(i));
    paginationEl.appendChild(pageButton);
  }
  
  // Next button
  const nextButton = document.createElement('button');
  nextButton.className = `page-button ${currentPage === totalPages ? 'disabled' : ''}`;
  nextButton.innerHTML = '<i class="fas fa-chevron-right"></i>';
  nextButton.disabled = currentPage === totalPages;
  nextButton.addEventListener('click', () => {
    if (currentPage < totalPages) {
      goToPage(currentPage + 1);
    }
  });
  paginationEl.appendChild(nextButton);
}

/**
 * Go to a specific page of logs
 * 
 * @param {number} page - Page number to go to
 */
function goToPage(page) {
  loadLogs(currentTab, page);
}

/**
 * Apply filters and reload logs
 */
function applyFilters() {
  // Get filter input values
  const dateFrom = document.getElementById('dateFrom');
  const dateTo = document.getElementById('dateTo');
  const statusFilter = document.getElementById('statusFilter');
  const locationFilter = document.getElementById('locationFilter');
  
  // Update filter values
  currentFilters.dateFrom = dateFrom ? dateFrom.value : '';
  currentFilters.dateTo = dateTo ? dateTo.value : '';
  currentFilters.status = statusFilter ? statusFilter.value : '';
  currentFilters.location = locationFilter ? locationFilter.value : '';
  
  // Reload logs with filters applied
  loadLogs(currentTab, 1);
}

/**
 * Refresh logs
 */
function refreshLogs() {
  loadLogs(currentTab, currentPage);
}

/**
 * Export logs to CSV
 * 
 * @param {string} type - Type of logs to export ('extraction' or 'error')
 */
function exportLogs(type) {
  // Build query params
  const queryParams = new URLSearchParams();
  queryParams.append('type', type);
  queryParams.append('format', 'csv');
  
  if (currentFilters.dateFrom) {
    queryParams.append('date_from', currentFilters.dateFrom);
  }
  
  if (currentFilters.dateTo) {
    queryParams.append('date_to', currentFilters.dateTo);
  }
  
  if (currentFilters.status) {
    queryParams.append('status', currentFilters.status);
  }
  
  if (currentFilters.location) {
    queryParams.append('location', currentFilters.location);
  }
  
  // Create export URL
  const exportUrl = `/api/export-logs?${queryParams.toString()}`;
  
  // Trigger download
  window.location.href = exportUrl;
}

/**
 * View log details in a modal
 * 
 * @param {string} type - Type of log ('extraction' or 'error')
 * @param {Object} log - Log entry data
 */
function viewLogDetails(type, log) {
  const modal = document.getElementById('logDetailsModal');
  const modalTitle = document.getElementById('modal-title');
  const modalContent = document.getElementById('log-details-content');
  
  if (!modal || !modalTitle || !modalContent) {
    return;
  }
  
  // Set modal title
  modalTitle.textContent = type === 'extraction' ? 'Extraction Log Details' : 'Error Log Details';
  
  // Build modal content based on log type
  let content = '';
  
  if (type === 'extraction') {
    content = `
      <div class="detail-row">
        <div class="detail-label">Timestamp:</div>
        <div class="detail-value">${log.Timestamp || ''}</div>
      </div>
      <div class="detail-row">
        <div class="detail-label">Profile ID:</div>
        <div class="detail-value">${log['Profile ID'] || ''}</div>
      </div>
      <div class="detail-row">
        <div class="detail-label">Location:</div>
        <div class="detail-value">${log.Location || ''}</div>
      </div>
      <div class="detail-row">
        <div class="detail-label">Status:</div>
        <div class="detail-value">
          <span class="log-status ${getStatusClass(log.Status)}">
            ${getStatusIcon(log.Status)} ${log.Status || ''}
          </span>
        </div>
      </div>
      <div class="detail-row">
        <div class="detail-label">Details:</div>
        <div class="detail-value">${log.Details || ''}</div>
      </div>
    `;
  } else {
    content = `
      <div class="detail-row">
        <div class="detail-label">Timestamp:</div>
        <div class="detail-value">${log.Timestamp || ''}</div>
      </div>
      <div class="detail-row">
        <div class="detail-label">Error Type:</div>
        <div class="detail-value">${log['Error Type'] || ''}</div>
      </div>
      <div class="detail-row">
        <div class="detail-label">Location:</div>
        <div class="detail-value">${log.Location || ''}</div>
      </div>
      <div class="detail-row">
        <div class="detail-label">Profile ID:</div>
        <div class="detail-value">${log['Profile ID'] || 'N/A'}</div>
      </div>
      <div class="detail-row">
        <div class="detail-label">Error Message:</div>
        <div class="detail-value">${log['Error Message'] || ''}</div>
      </div>
    `;
  }
  
  // Set modal content
  modalContent.innerHTML = content;
  
  // Show modal
  modal.classList.add('active');
}

/**
 * Get CSS class for status badge
 * 
 * @param {string} status - Status value
 * @returns {string} CSS class for the status
 */
function getStatusClass(status) {
  switch (status) {
    case 'SCRAPED':
      return 'status-success';
    case 'SKIPPED':
      return 'status-warning';
    case 'LOCATION_CHANGE':
      return 'status-info';
    case 'ERROR':
      return 'status-error';
    default:
      return 'status-info';
  }
}

/**
 * Get icon for status badge
 * 
 * @param {string} status - Status value
 * @returns {string} HTML for the status icon
 */
function getStatusIcon(status) {
  switch (status) {
    case 'SCRAPED':
      return '<i class="fas fa-check-circle"></i>';
    case 'SKIPPED':
      return '<i class="fas fa-exclamation-circle"></i>';
    case 'LOCATION_CHANGE':
      return '<i class="fas fa-map-marker-alt"></i>';
    case 'ERROR':
      return '<i class="fas fa-times-circle"></i>';
    default:
      return '<i class="fas fa-info-circle"></i>';
  }
}

/**
 * Close the log details modal
 */
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
  }
}
