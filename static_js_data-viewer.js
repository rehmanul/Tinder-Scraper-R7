/**
 * Data Viewer functionality for the Tinder Scraper application
 * Handles profile browsing, viewing, and filtering
 */

// Global variables
let profiles = [];
let currentProfileIndex = 0;
let currentImageIndex = 0;
let currentPage = 1;
let totalPages = 1;
let itemsPerPage = 12;
let filters = {
    status: 'all',
    location: 'all',
    ethnicity: 'all'
};

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the data viewer
    initializeDataViewer();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load initial data
    loadProfiles();
});

/**
 * Initialize data viewer elements
 */
function initializeDataViewer() {
    console.log('Data viewer initialized');
}

/**
 * Set up event listeners for data viewer controls
 */
function setupEventListeners() {
    // Filter controls
    const statusFilter = document.getElementById('statusFilter');
    const locationFilter = document.getElementById('locationFilter');
    const ethnicityFilter = document.getElementById('ethnicityFilter');
    
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            filters.status = this.value;
            loadProfiles(1);
        });
    }
    
    if (locationFilter) {
        locationFilter.addEventListener('change', function() {
            filters.location = this.value;
            loadProfiles(1);
        });
    }
    
    if (ethnicityFilter) {
        ethnicityFilter.addEventListener('change', function() {
            filters.ethnicity = this.value;
            loadProfiles(1);
        });
    }
    
    // Apply filters button
    const filterButton = document.getElementById('applyFiltersBtn');
    if (filterButton) {
        filterButton.addEventListener('click', function() {
            loadProfiles(1);
        });
    }
}

/**
 * Load profiles from the API
 */
function loadProfiles(page = 1) {
    currentPage = page;
    
    // Show loading state
    const profilesGrid = document.getElementById('profilesGrid');
    if (profilesGrid) {
        profilesGrid.innerHTML = `
            <div class="loading">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading profiles...</p>
            </div>
        `;
    }
    
    // Build query parameters
    const params = new URLSearchParams({
        page: page,
        limit: itemsPerPage,
        ...filters
    });
    
    // Fetch profiles
    fetch(`/api/get-profiles?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            profiles = data.profiles || [];
            totalPages = data.total_pages || 1;
            
            renderProfiles();
            renderPagination();
        })
        .catch(error => {
            console.error('Error loading profiles:', error);
            
            if (profilesGrid) {
                profilesGrid.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-circle"></i>
                        <p>Error loading profiles: ${error.message}</p>
                    </div>
                `;
            }
        });
}

/**
 * Render profiles in the grid
 */
function renderProfiles() {
    const profilesGrid = document.getElementById('profilesGrid');
    if (!profilesGrid) return;
    
    // Clear the grid
    profilesGrid.innerHTML = '';
    
    // Check if we have profiles
    if (!profiles || profiles.length === 0) {
        profilesGrid.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search no-results-icon"></i>
                <div class="no-results-title">No profiles found</div>
                <div class="no-results-message">Try adjusting your filters to see more results.</div>
            </div>
        `;
        return;
    }
    
    // Render each profile
    profiles.forEach((profile, index) => {
        const card = document.createElement('div');
        card.className = 'profile-card';
        card.onclick = () => viewProfile(index);
        
        // Get cover image URL
        const coverImage = profile.images && profile.images.length > 0 ? 
            `/api/images/${profile.images[0].filename}` : 
            'https://via.placeholder.com/300x400?text=No+Image';
        
        // Get profile status
        const statusClass = profile.status === 'labeled' ? 'status-labeled' : 
                           (profile.status === 'unlabeled' ? 'status-unlabeled' : 'status-skipped');
        
        // Format the status text
        const statusText = profile.status ? 
            profile.status.charAt(0).toUpperCase() + profile.status.slice(1) : 
            'Unlabeled';
        
        card.innerHTML = `
            <div class="profile-header">
                <img src="${coverImage}" alt="Profile" class="profile-cover">
            </div>
            <div class="profile-info">
                <div class="profile-title">Profile ${profile.profile_id}</div>
                <div class="profile-subtitle">${profile.location || 'Unknown location'}</div>
                <div class="profile-details">
                    <div class="profile-detail">
                        <i class="fas fa-images"></i>
                        ${profile.images ? profile.images.length : 0} images
                    </div>
                    <div class="profile-detail">
                        <i class="fas fa-calendar"></i>
                        ${profile.scraped_at || 'Unknown date'}
                    </div>
                    <div class="profile-badge">
                        ${profile.primary_ethnicity || 'Unknown ethnicity'}
                    </div>
                </div>
                
                <div class="image-gallery">
                    ${profile.images ? profile.images.map(image => `
                        <img src="/api/images/${image.filename}" alt="Image" class="gallery-image">
                    `).join('') : ''}
                </div>
                
                <div class="profile-actions">
                    <span class="profile-item-status ${statusClass}">
                        ${statusText}
                    </span>
                    <button class="view-button">
                        View Profile <i class="fas fa-arrow-right"></i>
                    </button>
                </div>
            </div>
        `;
        
        profilesGrid.appendChild(card);
    });
}

/**
 * Render pagination controls
 */
function renderPagination() {
    const paginationEl = document.getElementById('pagination');
    if (!paginationEl) return;
    
    // Clear pagination
    paginationEl.innerHTML = '';
    
    // Previous button
    const prevButton = document.createElement('button');
    prevButton.className = `page-button ${currentPage === 1 ? 'disabled' : ''}`;
    prevButton.innerHTML = '<i class="fas fa-chevron-left"></i>';
    prevButton.disabled = currentPage === 1;
    prevButton.onclick = () => loadProfiles(currentPage - 1);
    paginationEl.appendChild(prevButton);
    
    // Page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, startPage + 4);
    
    for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement('button');
        pageButton.className = `page-button ${i === currentPage ? 'active' : ''}`;
        pageButton.textContent = i;
        pageButton.onclick = () => loadProfiles(i);
        paginationEl.appendChild(pageButton);
    }
    
    // Next button
    const nextButton = document.createElement('button');
    nextButton.className = `page-button ${currentPage === totalPages ? 'disabled' : ''}`;
    nextButton.innerHTML = '<i class="fas fa-chevron-right"></i>';
    nextButton.disabled = currentPage === totalPages;
    nextButton.onclick = () => loadProfiles(currentPage + 1);
    paginationEl.appendChild(nextButton);
}

/**
 * View a profile in detail
 */
function viewProfile(index) {
    currentProfileIndex = index;
    currentImageIndex = 0;
    
    const profile = profiles[index];
    if (!profile) return;
    
    // Show the modal
    showModal('profileViewerModal');
    
    // Set up viewer content
    const profileViewer = document.getElementById('profileViewer');
    if (!profileViewer) return;
    
    // Get main image URL
    const mainImageUrl = profile.images && profile.images.length > 0 ? 
        `/api/images/${profile.images[0].filename}` : 
        'https://via.placeholder.com/800x600?text=No+Image';
    
    // Create profile viewer content
    profileViewer.innerHTML = `
        <div class="profile-image-section">
            <img src="${mainImageUrl}" alt="Profile Image" id="mainImage" class="profile-main-image">
            <div class="image-controls">
                <button class="image-nav prev-image" id="prevImageBtn" onclick="prevImage()" disabled>
                    <i class="fas fa-chevron-left"></i>
                </button>
                <button class="image-nav next-image" id="nextImageBtn" onclick="nextImage()" ${profile.images && profile.images.length > 1 ? '' : 'disabled'}>
                    <i class="fas fa-chevron-right"></i>
                </button>
            </div>
            <div class="image-counter">
                <span id="currentImageIndex">1</span> / <span id="totalImages">${profile.images ? profile.images.length : 0}</span>
            </div>
        </div>
        
        <div class="profile-thumbnails" id="imageThumbnails">
            ${profile.images ? profile.images.map((image, idx) => `
                <img src="/api/images/${image.filename}" alt="Thumbnail" 
                     class="profile-thumbnail ${idx === 0 ? 'active' : ''}" 
                     onclick="selectImage(${idx})">
            `).join('') : ''}
        </div>
        
        <div class="profile-details">
            <div class="profile-detail">
                <div class="profile-detail-label">Profile ID</div>
                <div class="profile-detail-value">${profile.profile_id || 'Unknown'}</div>
            </div>
            <div class="profile-detail">
                <div class="profile-detail-label">Location</div>
                <div class="profile-detail-value">${profile.location || 'Unknown'}</div>
            </div>
            <div class="profile-detail">
                <div class="profile-detail-label">Scraped At</div>
                <div class="profile-detail-value">${profile.scraped_at || 'Unknown'}</div>
            </div>
            <div class="profile-detail">
                <div class="profile-detail-label">Status</div>
                <div class="profile-detail-value">${profile.status || 'Unlabeled'}</div>
            </div>
            ${profile.bio ? `
            <div class="profile-detail">
                <div class="profile-detail-label">Bio</div>
                <div class="profile-detail-value">${profile.bio}</div>
            </div>
            ` : ''}
        </div>
    `;
    
    // If the profile has labels, display them
    if (profile.labels) {
        renderLabels(profile.labels);
    }
}

/**
 * Render profile labels
 */
function renderLabels(labels) {
    const profileViewer = document.getElementById('profileViewer');
    if (!profileViewer) return;
    
    // Create labels section
    const labelsSection = document.createElement('div');
    labelsSection.className = 'labels-section';
    labelsSection.innerHTML = `<div class="labels-title">Profile Labels</div>`;
    
    // Render labels grid
    const labelsGrid = document.createElement('div');
    labelsGrid.className = 'labels-grid';
    
    // Range fields (age, height, weight)
    const rangeFields = [
        { id: 'age', name: 'Age Range', unit: 'years', min: 18, max: 50 },
        { id: 'height', name: 'Height Range', unit: 'cm', min: 140, max: 200 },
        { id: 'weight', name: 'Weight Range', unit: 'kg', min: 40, max: 100 }
    ];
    
    rangeFields.forEach(field => {
        if (labels[field.id]) {
            const [min, max] = labels[field.id];
            const percentage = {
                min: ((min - field.min) / (field.max - field.min)) * 100,
                max: ((max - field.min) / (field.max - field.min)) * 100
            };
            
            const rangeEl = document.createElement('div');
            rangeEl.className = 'label-item';
            rangeEl.innerHTML = `
                <div class="label-field-header">
                    <div class="label-field-name">${field.name}</div>
                    <div class="label-field-value">${min} - ${max} ${field.unit}</div>
                </div>
                <div class="label-range">
                    <div class="label-range-fill" style="left: ${percentage.min}%; width: ${percentage.max - percentage.min}%"></div>
                    <div class="label-range-min" style="left: ${percentage.min}%"></div>
                    <div class="label-range-max" style="left: ${percentage.max}%"></div>
                </div>
                <div class="label-range-labels">
                    <div>${field.min}</div>
                    <div>${field.max}</div>
                </div>
            `;
            
            labelsGrid.appendChild(rangeEl);
        }
    });
    
    // Percentage fields
    const percentageFields = [
        { id: 'intelligence', name: 'Intelligence' },
        { id: 'cooperativeness', name: 'Cooperativeness' },
        { id: 'confidence', name: 'Confidence' },
        { id: 'presentable', name: 'Presentable' },
        { id: 'dominance', name: 'Dominance' }
    ];
    
    percentageFields.forEach(field => {
        if (labels[field.id]) {
            const [min, max] = labels[field.id];
            
            const rangeEl = document.createElement('div');
            rangeEl.className = 'label-item';
            rangeEl.innerHTML = `
                <div class="label-field-header">
                    <div class="label-field-name">${field.name}</div>
                    <div class="label-field-value">${min} - ${max}%</div>
                </div>
                <div class="label-range">
                    <div class="label-range-fill" style="left: ${min}%; width: ${max - min}%"></div>
                    <div class="label-range-min" style="left: ${min}%"></div>
                    <div class="label-range-max" style="left: ${max}%"></div>
                </div>
                <div class="label-range-labels">
                    <div>0%</div>
                    <div>100%</div>
                </div>
            `;
            
            labelsGrid.appendChild(rangeEl);
        }
    });
    
    labelsSection.appendChild(labelsGrid);
    
    // Add ethnicity section if available
    if (labels.ethnicity && labels.ethnicity.length > 0) {
        const ethnicitySection = document.createElement('div');
        ethnicitySection.className = 'labels-section';
        ethnicitySection.innerHTML = `<div class="labels-title" style="margin-top: 24px;">Ethnicity</div>`;
        
        const ethnicityItems = document.createElement('div');
        ethnicityItems.className = 'ethnicity-items';
        
        // Sort ethnicities by value and filter out low values
        const sortedEthnicities = [...labels.ethnicity]
            .filter(e => e.value && e.value[1] > 20)
            .sort((a, b) => (b.value ? b.value[1] : 0) - (a.value ? a.value[1] : 0));
        
        sortedEthnicities.forEach(ethnicity => {
            const item = document.createElement('div');
            item.className = 'ethnicity-item';
            item.innerHTML = `
                ${ethnicity.name}: ${ethnicity.value[0]}-${ethnicity.value[1]}%
            `;
            ethnicityItems.appendChild(item);
        });
        
        ethnicitySection.appendChild(ethnicityItems);
        labelsSection.appendChild(ethnicitySection);
    }
    
    profileViewer.appendChild(labelsSection);
}

/**
 * Navigate to previous image
 */
function prevImage() {
    if (currentImageIndex > 0) {
        currentImageIndex--;
        updateImageDisplay();
    }
}

/**
 * Navigate to next image
 */
function nextImage() {
    const profile = profiles[currentProfileIndex];
    if (profile && profile.images && currentImageIndex < profile.images.length - 1) {
        currentImageIndex++;
        updateImageDisplay();
    }
}

/**
 * Select a specific image
 */
function selectImage(index) {
    currentImageIndex = index;
    updateImageDisplay();
}

/**
 * Update the image display
 */
function updateImageDisplay() {
    const profile = profiles[currentProfileIndex];
    if (!profile || !profile.images || profile.images.length === 0) return;
    
    // Update main image
    const mainImage = document.getElementById('mainImage');
    if (mainImage) {
        mainImage.src = `/api/images/${profile.images[currentImageIndex].filename}`;
    }
    
    // Update image counter
    const currentIndexEl = document.getElementById('currentImageIndex');
    if (currentIndexEl) {
        currentIndexEl.textContent = currentImageIndex + 1;
    }
    
    // Update navigation buttons
    const prevButton = document.getElementById('prevImageBtn');
    const nextButton = document.getElementById('nextImageBtn');
    
    if (prevButton) {
        prevButton.disabled = currentImageIndex === 0;
    }
    
    if (nextButton) {
        nextButton.disabled = currentImageIndex === profile.images.length - 1;
    }
    
    // Update thumbnails
    const thumbnails = document.querySelectorAll('.profile-thumbnail');
    thumbnails.forEach((thumb, idx) => {
        thumb.classList.toggle('active', idx === currentImageIndex);
    });
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