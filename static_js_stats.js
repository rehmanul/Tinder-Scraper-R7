/**
 * Statistics Dashboard functionality for the Tinder Scraper application
 * Handles data visualization and statistics reporting
 */

// Global variables
let locationChart = null;
let ageChart = null;
let locationData = [];
let ageData = [];
let darkTheme = false;

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the statistics dashboard
    initializeStatsDashboard();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load initial data
    loadStatistics();
});

/**
 * Initialize statistics dashboard
 */
function initializeStatsDashboard() {
    // Check theme preference
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (prefersDark) {
        toggleTheme();
    }
    
    console.log('Statistics dashboard initialized');
}

/**
 * Set up event listeners for controls
 */
function setupEventListeners() {
    // Theme toggle
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Filter controls
    const milestoneFilter = document.getElementById('milestoneFilter');
    if (milestoneFilter) {
        milestoneFilter.addEventListener('change', applyFilters);
    }
    
    const locationFilter = document.getElementById('locationFilter');
    if (locationFilter) {
        locationFilter.addEventListener('change', applyFilters);
    }
    
    // Filter button
    const filterButton = document.querySelector('.filter-button');
    if (filterButton) {
        filterButton.addEventListener('click', applyFilters);
    }
}

/**
 * Toggle between light and dark theme
 */
function toggleTheme() {
    darkTheme = !darkTheme;
    document.body.classList.toggle('dark-theme', darkTheme);
    
    const icon = document.querySelector('.theme-toggle i');
    if (icon) {
        icon.className = darkTheme ? 'fas fa-sun' : 'fas fa-moon';
    }
    
    // Update charts for theme
    updateChartsTheme();
}

/**
 * Update charts with theme-specific colors
 */
function updateChartsTheme() {
    const gridColor = getComputedStyle(document.body).getPropertyValue('--chart-grid-color').trim();
    const textColor = getComputedStyle(document.body).getPropertyValue('--chart-text-color').trim();
    
    if (locationChart) {
        locationChart.options.scales.x.grid.color = gridColor;
        locationChart.options.scales.y.grid.color = gridColor;
        locationChart.options.scales.x.ticks.color = textColor;
        locationChart.options.scales.y.ticks.color = textColor;
        locationChart.update();
    }
    
    if (ageChart) {
        ageChart.options.scales.x.grid.color = gridColor;
        ageChart.options.scales.y.grid.color = gridColor;
        ageChart.options.scales.x.ticks.color = textColor;
        ageChart.options.scales.y.ticks.color = textColor;
        ageChart.update();
    }
}

/**
 * Navigate to another page
 */
function navigateTo(page) {
    switch (page) {
        case 'dashboard':
            window.location.href = '/';
            break;
        case 'data-center':
            window.location.href = '/data-center';
            break;
        case 'logs':
            window.location.href = '/logs';
            break;
        case 'stryke-center':
            window.location.href = '/stryke-center';
            break;
        default:
            console.error('Unknown page:', page);
    }
}

/**
 * Load statistics from the API
 */
function loadStatistics() {
    // Get filter values
    const milestoneFilter = document.getElementById('milestoneFilter')?.value || 'all';
    const locationFilter = document.getElementById('locationFilter')?.value || 'all';
    
    // Build query parameters
    const params = new URLSearchParams({
        milestone: milestoneFilter,
        location: locationFilter
    });
    
    // Fetch statistics
    fetch(`/api/get-statistics?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            // Update statistics cards
            updateStatCards(data);
            
            // Update charts
            updateCharts(data);
            
            // Update ethnicity grid
            updateEthnicityGrid(data.ethnicityDistribution);
            
            // Update label distribution
            updateLabelDistribution(data.labelAverages);
        })
        .catch(error => {
            console.error('Error loading statistics:', error);
        });
}

/**
 * Update statistics cards
 */
function updateStatCards(data) {
    // Update total profiles
    document.getElementById('totalProfiles').textContent = formatNumber(data.totalProfiles || 0);
    
    // Update total images
    document.getElementById('totalImages').textContent = formatNumber(data.totalImages || 0);
    
    // Update locations count
    document.getElementById('totalLocations').textContent = Object.keys(data.locations || {}).length;
    
    // Update completion percentage
    const completion = ((data.totalProfiles / 25000) * 100).toFixed(1);
    document.getElementById('completionPercentage').textContent = completion + '%';
}

/**
 * Format a number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Update charts with new data
 */
function updateCharts(data) {
    // Process location data
    locationData = Object.entries(data.locations || {})
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8);
    
    // Process age data
    ageData = Object.entries(data.ageDistribution || {})
        .sort((a, b) => {
            const ageA = parseInt(a[0].split('-')[0]);
            const ageB = parseInt(b[0].split('-')[0]);
            return ageA - ageB;
        });
    
    // Initialize or update charts
    initCharts();
}

/**
 * Initialize or update charts
 */
function initCharts() {
    const primaryColor = getComputedStyle(document.body).getPropertyValue('--chart-color-1').trim();
    const gridColor = getComputedStyle(document.body).getPropertyValue('--chart-grid-color').trim();
    const textColor = getComputedStyle(document.body).getPropertyValue('--chart-text-color').trim();
    
    // Location chart
    const locationChartCtx = document.getElementById('locationChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (locationChart) {
        locationChart.destroy();
    }
    
    // Create new location chart
    locationChart = new Chart(locationChartCtx, {
        type: 'bar',
        data: {
            labels: locationData.map(item => item[0].split(',')[0]),
            datasets: [{
                label: 'Profiles Count',
                data: locationData.map(item => item[1]),
                backgroundColor: primaryColor,
                borderColor: primaryColor,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                }
            }
        }
    });
    
    // Age distribution chart
    const ageChartCtx = document.getElementById('ageChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (ageChart) {
        ageChart.destroy();
    }
    
    // Create new age chart
    ageChart = new Chart(ageChartCtx, {
        type: 'line',
        data: {
            labels: ageData.map(item => item[0]),
            datasets: [{
                label: 'Number of Profiles',
                data: ageData.map(item => item[1]),
                fill: true,
                backgroundColor: 'rgba(254, 60, 114, 0.1)',
                borderColor: primaryColor,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: gridColor
                    },
                    ticks: {
                        color: textColor
                    }
                }
            }
        }
    });
}

/**
 * Update ethnicity grid with distribution data
 */
function updateEthnicityGrid(ethnicityData) {
    const ethnicityGrid = document.getElementById('ethnicityGrid');
    if (!ethnicityGrid) return;
    
    // Clear the grid
    ethnicityGrid.innerHTML = '';
    
    // Sort ethnicities by percentage
    const sortedEthnicities = Object.entries(ethnicityData || {})
        .sort((a, b) => b[1] - a[1]);
    
    // Create cards for each ethnicity
    sortedEthnicities.forEach(([ethnicity, percentage]) => {
        const card = document.createElement('div');
        card.className = 'ethnicity-card';
        card.innerHTML = `
            <div class="ethnicity-percentage">${percentage.toFixed(1)}%</div>
            <div class="ethnicity-name">${ethnicity}</div>
        `;
        
        ethnicityGrid.appendChild(card);
    });
}

/**
 * Update label distribution visualization
 */
function updateLabelDistribution(labelAverages) {
    const labelContainer = document.getElementById('labelDistribution');
    if (!labelContainer) return;
    
    // Clear container
    labelContainer.innerHTML = '';
    
    // Define which labels to display
    const labelsToShow = [
        { id: 'intelligence', name: 'Intelligence' },
        { id: 'cooperativeness', name: 'Cooperativeness' },
        { id: 'confidence', name: 'Confidence' },
        { id: 'celibacy', name: 'Celibacy' },
        { id: 'presentable', name: 'Presentable' },
        { id: 'dominance', name: 'Dominance' },
        { id: 'muscle_percentage', name: 'Muscle %' },
        { id: 'fat_percentage', name: 'Fat %' }
    ];
    
    // Create visualization for each label
    labelsToShow.forEach(label => {
        if (labelAverages && labelAverages[label.id]) {
            const [min, max] = labelAverages[label.id];
            
            const row = document.createElement('div');
            row.className = 'label-row';
            row.innerHTML = `
                <div class="label-name">${label.name}</div>
                <div class="label-bar-container">
                    <div class="label-bar-min" style="width: ${min}%"></div>
                    <div class="label-bar-max" style="width: ${max - min}%; left: ${min}%"></div>
                </div>
                <div class="label-values">${min}% - ${max}%</div>
            `;
            
            labelContainer.appendChild(row);
        }
    });
}

/**
 * Apply filters and reload statistics
 */
function applyFilters() {
    loadStatistics();
}