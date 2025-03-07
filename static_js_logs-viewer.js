/**
 * Logs Viewer functionality for the Tinder Scraper application
 * Handles displaying and filtering log entries
 */

// Global variables
let currentTab = 'extraction-logs';
let currentPage = 1;
let totalPages = 1;
let itemsPerPage = 20;
let extractionLogs = [];
let errorLogs = [];

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the logs viewer
    initializeLogsViewer();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load initial logs
    loadLogs('extraction');
});

/**
 * Initialize logs viewer elements
 */
function initializeLogsViewer() {
    // Set default date range for the last 7 days
    const today = new Date();
    const lastWeek = new Date();
    lastWeek.setDate(today.getDate() - 7);
    
    const dateFrom = document.getElementById('dateFrom');
    const dateTo = document.getElementById('dateTo');
    
    if (dateFrom && dateTo) {
        dateFrom.valueAsDate = lastWeek;
        dateTo.valueAsDate = today;
    }
    
    console.log('Logs viewer initialized');
}

/**
 * Set up event listeners for logs viewer controls
 */
function setupEventListeners() {
    // Tab switching
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabType = this.textContent.toLowerCase().includes('extraction') ? 'extraction-logs' : 'error-logs';
            switchTab(tabType);
        });
    });
    
    // Filters
    const applyFiltersBtn = document.querySelector('.log-button.primary');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', applyFilters);
    }
    
    // Refresh button
    const refreshBtns = document.querySelectorAll('.log-button i.fa-sync-alt');
    refreshBtns.forEach(btn => {
        btn.parentElement.addEventListener('click', refreshLogs);
    });
    
    // Export buttons
    const exportBtns = document.querySelectorAll('.log-button i.fa-download');
    exportBtns.forEach(btn => {
        btn.parentElement.addEventListener('click', function() {
            const type = currentTab === 'extraction-logs' ? 'extraction' : 'error';
            exportLogs(type);
        });
    });
}

/**
 * Switch between tabs
 */
function switchTab(tab) {
    currentTab = tab;
    currentPage = 1;
    
    // Update UI
    document.querySelectorAll('.tab').forEach(tabEl => {
        tabEl.classList.toggle('active', tabEl.textContent.toLowerCase().includes(tab.replace('-', ' ')));
    });
    
    document.getElementById('extraction-logs-container').style.display = tab === 'extraction-logs' ? 'block' : 'none';
    document.getElementById('error-logs-container').style.display = tab === 'error-logs' ? 'block' : 'none';
    
    // Load logs for the selected tab
    loadLogs(tab === 'extraction-logs' ? 'extraction' : 'error');
}

/**
 * Load logs from the API
 */
function loadLogs(type, page = 1) {
    currentPage = page;
    
    // Show loading state
    const tableBody = document.getElementById(`${type}-logs-body`);
    if (tableBody) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6">
                    <div style="display: flex; justify-content: center; padding: 20px;">
                        <i class="fas fa-spinner fa-spin" style="font-size: 24px;"></i>
                    </div>
                </td>
            </tr>
        `;
    }
    
    // Get filter values
    const dateFrom = document.getElementById('dateFrom')?.value || '';
    const dateTo = document.getElementById('dateTo')?.value || '';
    const statusFilter = document.getElementById('statusFilter')?.value || '';
    const locationFilter = document.getElementById('locationFilter')?.value || '';
    
    // Build query parameters
    const params = new URLSearchParams({
        type: type,
        page: page,
        limit: itemsPerPage,
        date_from: dateFrom,
        date_to: dateTo,
        status: statusFilter,
        location: locationFilter
    });
    
    // Fetch logs
    fetch(`/api/get-logs?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (type === 'extraction') {
                extractionLogs = data.logs || [];
                renderExtractionLogs(extractionLogs, page);
            } else {
                errorLogs = data.logs || [];
                renderErrorLogs(errorLogs, page);
            }
            
            totalPages = data.total_pages || 1;
            renderPagination(page, totalPages);
        })
        .catch(error => {
            console.error(`Error loading ${type} logs:`, error);
            
            if (tableBody) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="6">
                            <div style="text-align: center; padding: 20px; color: var(--error-color);">
                                <i class="fas fa-exclamation-circle"></i>
                                <p>Error loading logs: ${error.message}</p>
                            </div>
                        </td>
                    </tr>
                `;
            }
        });
}

/**
 * Render extraction logs
 */
function renderExtractionLogs(logs, page = 1) {
    const tableBody = document.getElementById('extraction-logs-body');
    if (!tableBody) return;
    
    // Clear the table
    tableBody.innerHTML = '';
    
    // Check if we have logs
    if (!logs || logs.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="no-results">
                        <i class="fas fa-search no-results-icon"></i>
                        <div class="no-results-title">No logs found</div>
                        <div class="no-results-message">Try adjusting your filters to see more results.</div>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    // Render each log entry
    logs.forEach(log => {
        const row = document.createElement('tr');
        
        // Timestamp
        const timestampCell = document.createElement('td');
        timestampCell.textContent = log.Timestamp || log.timestamp || '';
        row.appendChild(timestampCell);
        
        // Profile ID
        const profileIdCell = document.createElement('td');
        profileIdCell.textContent = log['Profile ID'] || log.profile_id || 'N/A';
        row.appendChild(profileIdCell);
        
        // Location
        const locationCell = document.createElement('td');
        locationCell.textContent = log.Location || log.location || '';
        row.appendChild(locationCell);
        
        // Status
        const statusCell = document.createElement('td');
        const status = log.Status || log.status || '';
        const statusClass = status === 'SCRAPED' ? 'status-success' : 
                           (status === 'SKIPPED' ? 'status-warning' : 
                           (status === 'ERROR' ? 'status-error' : 'status-info'));
        
        const statusBadge = document.createElement('span');
        statusBadge.className = `log-status ${statusClass}`;
        statusBadge.textContent = status;
        statusCell.appendChild(statusBadge);
        row.appendChild(statusCell);
        
        // Details
        const detailsCell = document.createElement('td');
        detailsCell.className = 'log-details';
        const details = log.Details || log.details || '';
        
        if (details.length > 30) {
            detailsCell.textContent = details.substring(0, 30) + '...';
            
            const expandButton = document.createElement('button');
            expandButton.className = 'expand-button';
            expandButton.textContent = 'More';
            expandButton.onclick = (e) => {
                e.stopPropagation();
                viewLogDetails('extraction', log);
            };
            
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
        viewButton.onclick = (e) => {
            e.stopPropagation();
            viewLogDetails('extraction', log);
        };
        
        actionsCell.appendChild(viewButton);
        row.appendChild(actionsCell);
        
        tableBody.appendChild(row);
    });
}

/**
 * Render error logs
 */
function renderErrorLogs(logs, page = 1) {
    const tableBody = document.getElementById('error-logs-body');
    if (!tableBody) return;
    
    // Clear the table
    tableBody.innerHTML = '';
    
    // Check if we have logs
    if (!logs || logs.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6">
                    <div class="no-results">
                        <i class="fas fa-check-circle no-results-icon"></i>
                        <div class="no-results-title">No errors found</div>
                        <div class="no-results-message">Good news! There are no error logs matching your filters.</div>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    // Render each log entry
    logs.forEach(log => {
        const row = document.createElement('tr');
        
        // Timestamp
        const timestampCell = document.createElement('td');
        timestampCell.textContent = log.Timestamp || log.timestamp || '';
        row.appendChild(timestampCell);
        
        // Error Type
        const errorTypeCell = document.createElement('td');
        errorTypeCell.textContent = log['Error Type'] || log.error_type || '';
        row.appendChild(errorTypeCell);
        
        // Location
        const locationCell = document.createElement('td');
        locationCell.textContent = log.Location || log.location || '';
        row.appendChild(locationCell);
        
        // Profile ID
        const profileIdCell = document.createElement('td');
        profileIdCell.textContent = log['Profile ID'] || log.profile_id || 'N/A';
        row.appendChild(profileIdCell);
        
        // Error Message
        const errorMsgCell = document.createElement('td');
        errorMsgCell.className = 'log-details';
        const errorMsg = log['Error Message'] || log.error_message || '';
        
        if (errorMsg.length > 30) {
            errorMsgCell.textContent = errorMsg.substring(0, 30) + '...';
            
            const expandButton = document.createElement('button');
            expandButton.className = 'expand-button';
            expandButton.textContent = 'More';
            expandButton.onclick = (e) => {
                e.stopPropagation();
                viewLogDetails('error', log);
            };
            
            errorMsgCell.appendChild(expandButton);
        } else {
            errorMsgCell.textContent = errorMsg;
        }
        
        row.appendChild(errorMsgCell);
        
        // Actions
        const actionsCell = document.createElement('td');
        
        const viewButton = document.createElement('button');
        viewButton.className = 'log-button';
        viewButton.innerHTML = '<i class="fas fa-eye"></i>';
        viewButton.onclick = (e) => {
            e.stopPropagation();
            viewLogDetails('error', log);
        };
        
        actionsCell.appendChild(viewButton);
        row.appendChild(actionsCell);
        
        tableBody.appendChild(row);
    });
}

/**
 * Render pagination controls
 */
function renderPagination(currentPage, totalPages) {
    const paginationEl = document.getElementById('pagination');
    if (!paginationEl) return;
    
    // Clear pagination
    paginationEl.innerHTML = '';
    
    // Previous button
    const prevButton = document.createElement('button');
    prevButton.className = `page-button ${currentPage === 1 ? 'disabled' : ''}`;
    prevButton.innerHTML = '<i class="fas fa-chevron-left"></i>';
    prevButton.disabled = currentPage === 1;
    prevButton.onclick = () => goToPage(currentPage - 1);
    paginationEl.appendChild(prevButton);
    
    // Page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, startPage + 4);
    
    for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement('button');
        pageButton.className = `page-button ${i === currentPage ? 'active' : ''}`;
        pageButton.textContent = i;
        pageButton.onclick = () => goToPage(i);
        paginationEl.appendChild(pageButton);
    }
    
    // Next button
    const nextButton = document.createElement('button');
    nextButton.className = `page-button ${currentPage === totalPages ? 'disabled' : ''}`;
    nextButton.innerHTML = '<i class="fas fa-chevron-right"></i>';
    nextButton.disabled = currentPage === totalPages;
    nextButton.onclick = () => goToPage(currentPage + 1);
    paginationEl.appendChild(nextButton);
}

/**
 * Go to specific page
 */
function goToPage(page) {
    currentPage = page;
    const type = currentTab === 'extraction-logs' ? 'extraction' : 'error';
    loadLogs(type, page);
}

/**
 * Apply filters
 */
function applyFilters() {
    currentPage = 1;
    const type = currentTab === 'extraction-logs' ? 'extraction' : 'error';
    loadLogs(type, 1);
}

/**
 * Refresh logs
 */
function refreshLogs() {
    const type = currentTab === 'extraction-logs' ? 'extraction' : 'error';
    loadLogs(type, currentPage);
}

/**
 * Export logs
 */
function exportLogs(type) {
    // Get filter values
    const dateFrom = document.getElementById('dateFrom')?.value || '';
    const dateTo = document.getElementById('dateTo')?.value || '';
    const statusFilter = document.getElementById('statusFilter')?.value || '';
    const locationFilter = document.getElementById('locationFilter')?.value || '';
    
    // Build query parameters
    const params = new URLSearchParams({
        type: type,
        export: 'true',
        date_from: dateFrom,
        date_to: dateTo,
        status: statusFilter,
        location: locationFilter
    });
    
    // Create export URL
    const exportUrl = `/api/export-logs?${params.toString()}`;
    
    // Trigger download
    window.location.href = exportUrl;
}

/**
 * View log details
 */
function viewLogDetails(type, log) {
    const modalTitle = document.getElementById('modal-title');
    const logDetailsContent = document.getElementById('log-details-content');
    
    if (!modalTitle || !logDetailsContent) return;
    
    // Set modal title
    modalTitle.textContent = type === 'extraction' ? 'Extraction Log Details' : 'Error Log Details';
    
    // Format log details
    if (type === 'extraction') {
        logDetailsContent.innerHTML = `
            <div class="detail-row">
                <div class="detail-label">Timestamp:</div>
                <div class="detail-value">${log.Timestamp || log.timestamp || ''}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Profile ID:</div>
                <div class="detail-value">${log['Profile ID'] || log.profile_id || 'N/A'}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Location:</div>
                <div class="detail-value">${log.Location || log.location || ''}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Status:</div>
                <div class="detail-value">
                    <span class="log-status ${getStatusClass(log.Status || log.status || '')}">
                        ${log.Status || log.status || ''}
                    </span>
                </div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Details:</div>
                <div class="detail-value">${log.Details || log.details || ''}</div>
            </div>
        `;
    } else {
        logDetailsContent.innerHTML = `
            <div class="detail-row">
                <div class="detail-label">Timestamp:</div>
                <div class="detail-value">${log.Timestamp || log.timestamp || ''}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Error Type:</div>
                <div class="detail-value">${log['Error Type'] || log.error_type || ''}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Location:</div>
                <div class="detail-value">${log.Location || log.location || ''}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Profile ID:</div>
                <div class="detail-value">${log['Profile ID'] || log.profile_id || 'N/A'}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Error Message:</div>
                <div class="detail-value">${log['Error Message'] || log.error_message || ''}</div>
            </div>
        `;
    }
    
    // Show modal
    showModal('logDetailsModal');
}

/**
 * Get status class for a log status
 */
function getStatusClass(status) {
    switch (status) {
        case 'SCRAPED':
            return 'status-success';
        case 'SKIPPED':
            return 'status-warning';
        case 'ERROR':
            return 'status-error';
        default:
            return 'status-info';
    }
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