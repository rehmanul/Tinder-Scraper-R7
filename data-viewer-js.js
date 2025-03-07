/**
 * data-viewer.js - Manages the profile browser and image gallery
 * 
 * This script handles profile browsing, filtering, and image viewing functionality.
 */

// Global variables
let currentPage = 1;
let totalPages = 1;
let currentProfiles = [];
let viewingProfileIndex = 0;
let viewingImageIndex = 0;
let currentFilters = {
  location: 'all',
  ethnicity: 'all',
  ageMin: '',
  ageMax: ''
};

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
  // Initialize components
  initializeComponents();
  
  // Load initial data
  loadProfiles(1);
});

/**
 * Initialize data viewer components
 */
function initializeComponents() {
  // Set up event listeners for filter inputs
  const locationFilter = document.getElementById('locationFilter');
  const ethnicityFilter = document.getElementById('ethnicityFilter');
  const ageMinFilter = document.getElementById('ageMinFilter');
  const ageMaxFilter = document.getElementById('ageMaxFilter');
  
  if (locationFilter) {
    locationFilter.addEventListener('change', () => {
      currentFilters.location = locationFilter.value;
    });
  }
  
  if (ethnicityFilter) {
    ethnicityFilter.addEventListener('change', () => {
      currentFilters.ethnicity = ethnicityFilter.value;
    });
  }
  
  if (ageMinFilter) {
    ageMinFilter.addEventListener('change', () => {
      currentFilters.ageMin = ageMinFilter.value;
    });
  }
  
  if (ageMaxFilter) {
    ageMaxFilter.addEventListener('change', () => {
      currentFilters.ageMax = ageMaxFilter.value;
    });
  }
  
  // Set up apply filters button
  const applyFiltersBtn = document.querySelector('.action-button');
  if (applyFiltersBtn) {
    applyFiltersBtn.addEventListener('click', applyFilters);
  }
}

/**
 * Load profiles from the server
 * 
 * @param {number} page - Page number to load
 */
function loadProfiles(page = 1) {
  // Build query params from filters
  const queryParams = new URLSearchParams();
  queryParams.append('page', page);
  
  if (currentFilters.location && currentFilters.location !== 'all') {
    queryParams.append('location', currentFilters.location);
  }
  
  if (currentFilters.ethnicity && currentFilters.ethnicity !== 'all') {
    queryParams.append('ethnicity', currentFilters.ethnicity);
  }
  
  if (currentFilters.ageMin) {
    queryParams.append('age_min', currentFilters.ageMin);
  }
  
  if (currentFilters.ageMax) {
    queryParams.append('age_max', currentFilters.ageMax);
  }
  
  // Show loading state
  const profilesGrid = document.getElementById('profilesGrid');
  if (profilesGrid) {
    profilesGrid.innerHTML = `
      <div class="loading-container" style="text-align: center; padding: 40px;">
        <i class="fas fa-spinner fa-spin" style="font-size: 32px; color: #fe3c72;"></i>
        <p>Loading profiles...</p>
      </div>
    `;
  }
  
  // Make API request
  fetch(`/api/get-profiles?${queryParams.toString()}`)
    .then(response => response.json())
    .then(data => {
      // Store the profiles data
      currentProfiles = data.profiles || [];
      totalPages = data.total_pages || 1;
      currentPage = page;
      
      // Render the profiles
      renderProfiles(currentProfiles);
      
      // Render pagination
      renderPagination(currentPage, totalPages);
    })
    .catch(error => {
      console.error('Error loading profiles:', error);
      
      // Show error state
      if (profilesGrid) {
        profilesGrid.innerHTML = `
          <div class="no-results">
            <i class="fas fa-exclamation-circle no-results-icon"></i>
            <div class="no-results-title">Error loading profiles</div>
            <div class="no-results-message">There was a problem loading the profiles. Please try again.</div>
          </div>
        `;
      }
    });
}

/**
 * Render profiles in the grid
 * 
 * @param {Array} profiles - Array of profile data objects
 */
function renderProfiles(profiles) {
  const profilesGrid = document.getElementById('profilesGrid');
  
  if (!profilesGrid) {
    return;
  }
  
  // Check if we have profiles to display
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
  
  // Clear grid
  profilesGrid.innerHTML = '';
  
  // Add profile cards
  profiles.forEach((profile, index) => {
    const profileCard = document.createElement('div');
    profileCard.className = 'profile-card';
    
    // Get first image
    const firstImage = profile.images && profile.images.length > 0 ? 
      `/api/images/${profile.images[0].filename}` : 
      '/static/img/placeholder.png';
    
    // Calculate primary ethnicity
    const primaryEthnicity = getPrimaryEthnicity(profile.labels?.ethnicity);
    
    profileCard.innerHTML = `
      <div class="profile-header">
        <img src="${firstImage}" alt="Profile" class="profile-cover">
      </div>
      <div class="profile-info">
        <div class="profile-title">Profile ${profile.profile_id}</div>
        <div class="profile-subtitle">${profile.location}</div>
        <div class="profile-details">
          <div class="profile-detail">
            <i class="fas fa-images"></i>
            ${profile.images?.length || 0} images
          </div>
          <div class="profile-detail">
            <i class="fas fa-calendar"></i>
            Scraped on ${new Date(profile.scraped_at).toLocaleDateString()}
          </div>
          <div class="profile-badge">
            ${primaryEthnicity}
          </div>
        </div>
        
        <div class="image-gallery">
          ${generateImageGallery(profile.images)}
        </div>
        
        <div class="profile-actions">
          <button class="view-button" onclick="viewProfile(${index})">
            View Profile <i class="fas fa-arrow-right"></i>
          </button>
        </div>
      </div>
    `;
    
    profilesGrid.appendChild(profileCard);
  });
}

/**
 * Generate HTML for the image gallery
 * 
 * @param {Array} images - Array of image objects
 * @returns {string} HTML for the image gallery
 */
function generateImageGallery(images) {
  if (!images || images.length === 0) {
    return '<div class="no-images">No images available</div>';
  }
  
  return images.map(image => `
    <img src="/api/images/${image.filename}" alt="Image" class="gallery-image">
  `).join('');
}

/**
 * Get the primary ethnicity from ethnicity labels
 * 
 * @param {Array} ethnicities - Array of ethnicity objects
 * @returns {string} Primary ethnicity name
 */
function getPrimaryEthnicity(ethnicities) {
  if (!ethnicities || ethnicities.length === 0) {
    return 'Unknown';
  }
  
  // Find ethnicity with highest confidence
  const primaryEthnicity = ethnicities.reduce((max, current) => {
    const currentMax = current.value[1];
    const prevMax = max ? max.value[1] : 0;
    return currentMax > prevMax ? current : max;
  }, null);
  
  return primaryEthnicity ? primaryEthnicity.name : 'Unknown';
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
      loadProfiles(currentPage - 1);
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
    pageButton.addEventListener('click', () => loadProfiles(i));
    paginationEl.appendChild(pageButton);
  }
  
  // Next button
  const nextButton = document.createElement('button');
  nextButton.className = `page-button ${currentPage === totalPages ? 'disabled' : ''}`;
  nextButton.innerHTML = '<i class="fas fa-chevron-right"></i>';
  nextButton.disabled = currentPage === totalPages;
  nextButton.addEventListener('click', () => {
    if (currentPage < totalPages) {
      loadProfiles(currentPage + 1);
    }
  });
  paginationEl.appendChild(nextButton);
}

/**
 * Apply filters and reload profiles
 */
function applyFilters() {
  // Update filter values from inputs
  const locationFilter = document.getElementById('locationFilter');
  const ethnicityFilter = document.getElementById('ethnicityFilter');
  const ageMinFilter = document.getElementById('ageMinFilter');
  const ageMaxFilter = document.getElementById('ageMaxFilter');
  
  if (locationFilter) {
    currentFilters.location = locationFilter.value;
  }
  
  if (ethnicityFilter) {
    currentFilters.ethnicity = ethnicityFilter.value;
  }
  
  if (ageMinFilter) {
    currentFilters.ageMin = ageMinFilter.value;
  }
  
  if (ageMaxFilter) {
    currentFilters.ageMax = ageMaxFilter.value;
  }
  
  // Load profiles with filter applied
  loadProfiles(1);
}

/**
 * View profile details in the modal
 * 
 * @param {number} index - Index of the profile to view
 */
function viewProfile(index) {
  if (index < 0 || index >= currentProfiles.length) {
    console.error('Invalid profile index:', index);
    return;
  }
  
  // Set current viewing indexes
  viewingProfileIndex = index;
  viewingImageIndex = 0;
  
  const profile = currentProfiles[index];
  const profileViewerModal = document.getElementById('profileViewerModal');
  const profileViewer = document.getElementById('profileViewer');
  
  if (!profileViewerModal || !profileViewer) {
    console.error('Profile viewer elements not found');
    return;
  }
  
  // Prepare profile images
  const images = profile.images || [];
  const firstImageSrc = images.length > 0 ? 
    `/api/images/${images[0].filename}` : 
    '/static/img/placeholder.png';
  
  // Set profile viewer content
  profileViewer.innerHTML = `
    <div class="profile-image-section">
      <img src="${firstImageSrc}" alt="Profile" class="profile-main-image" id="mainProfileImage">
      <button class="image-nav prev-image" onclick="prevImage()" ${viewingImageIndex === 0 ? 'disabled' : ''}>
        <i class="fas fa-chevron-left"></i>
      </button>
      <button class="image-nav next-image" onclick="nextImage()" ${viewingImageIndex === images.length - 1 ? 'disabled' : ''}>
        <i class="fas fa-chevron-right"></i>
      </button>
      <div class="profile-image-count">
        <span id="currentImageIndex">1</span> / ${images.length}
      </div>
    </div>
    
    <div class="profile-thumbnails">
      ${images.map((image, i) => `
        <img src="/api/images/${image.filename}" alt="Thumbnail" class="profile-thumbnail ${i === 0 ? 'active' : ''}" onclick="selectImage(${i})">
      `).join('')}
    </div>
    
    <div class="profile-details-section">
      <div class="profile-id">Profile ID: ${profile.profile_id} • ${profile.location}</div>
      
      <div class="labels-section">
        <div class="labels-title">Profile Labels</div>
        
        ${renderLabelsGrid(profile.labels)}
        
        <div class="labels-title" style="margin-top: 24px;">Ethnicity</div>
        ${renderEthnicityLabels(profile.labels?.ethnicity)}
      </div>
    </div>
  `;
  
  // Show the modal
  profileViewerModal.classList.add('active');
}

/**
 * Render the labels grid
 * 
 * @param {Object} labels - Labels object
 * @returns {string} HTML for the labels grid
 */
function renderLabelsGrid(labels) {
  if (!labels) {
    return '<div class="no-labels">No labels available</div>';
  }
  
  const labelsToDisplay = [
    { key: 'age', name: 'Age Range', unit: 'years', scale: 50 },
    { key: 'height', name: 'Height Range', unit: 'cm', scale: 200, offset: 140 },
    { key: 'weight', name: 'Weight Range', unit: 'kg', scale: 100, offset: 40 },
    { key: 'intelligence', name: 'Intelligence', unit: '%', scale: 100 },
    { key: 'cooperativeness', name: 'Cooperativeness', unit: '%', scale: 100 },
    { key: 'confidence', name: 'Confidence', unit: '%', scale: 100 }
  ];
  
  return `
    <div class="labels-grid">
      ${labelsToDisplay.map(label => {
        if (!labels[label.key] || !Array.isArray(labels[label.key]) || labels[label.key].length !== 2) {
          return '';
        }
        
        const min = labels[label.key][0];
        const max = labels[label.key][1];
        const offset = label.offset || 0;
        
        // Calculate percentages for the visual elements
        const minPercent = ((min - offset) / label.scale) * 100;
        const maxPercent = ((max - offset) / label.scale) * 100;
        const width = maxPercent - minPercent;
        
        return `
          <div class="label-item">
            <div class="label-field-name">${label.name}</div>
            <div class="label-field-value">${min}-${max} ${label.unit}</div>
            <div class="label-range">
              <div class="label-range-fill" style="left: ${minPercent}%; width: ${width}%"></div>
              <div class="label-range-min" style="left: ${minPercent}%"></div>
              <div class="label-range-max" style="left: ${maxPercent}%"></div>
            </div>
          </div>
        `;
      }).join('')}
    </div>
  `;
}

/**
 * Render ethnicity labels
 * 
 * @param {Array} ethnicities - Array of ethnicity objects
 * @returns {string} HTML for ethnicity labels
 */
function renderEthnicityLabels(ethnicities) {
  if (!ethnicities || ethnicities.length === 0) {
    return '<div class="no-ethnicities">No ethnicity data available</div>';
  }
  
  // Filter to ethnicities with significant probability
  const significantEthnicities = ethnicities.filter(e => e.value[1] > 20);
  
  // Sort by confidence (max value)
  significantEthnicities.sort((a, b) => b.value[1] - a.value[1]);
  
  if (significantEthnicities.length === 0) {
    return '<div class="no-ethnicities">No significant ethnicities detected</div>';
  }
  
  return `
    <div class="ethnicity-items">
      ${significantEthnicities.map(ethnicity => `
        <div class="ethnicity-item">
          ${ethnicity.name}: ${ethnicity.value[0]}-${ethnicity.value[1]}%
        </div>
      `).join('')}
    </div>
  `;
}

/**
 * Navigate to previous image
 */
function prevImage() {
  if (viewingImageIndex > 0) {
    viewingImageIndex--;
    updateCurrentImage();
  }
}

/**
 * Navigate to next image
 */
function nextImage() {
  const profile = currentProfiles[viewingProfileIndex];
  const images = profile.images || [];
  
  if (viewingImageIndex < images.length - 1) {
    viewingImageIndex++;
    updateCurrentImage();
  }
}

/**
 * Select specific image by index
 * 
 * @param {number} index - Index of the image to select
 */
function selectImage(index) {
  const profile = currentProfiles[viewingProfileIndex];
  const images = profile.images || [];
  
  if (index >= 0 && index < images.length) {
    viewingImageIndex = index;
    updateCurrentImage();
  }
}

/**
 * Update the current image display
 */
function updateCurrentImage() {
  const profile = currentProfiles[viewingProfileIndex];
  const images = profile.images || [];
  
  if (images.length === 0) {
    return;
  }
  
  // Update main image
  const mainImage = document.getElementById('mainProfileImage');
  if (mainImage) {
    mainImage.src = `/api/images/${images[viewingImageIndex].filename}`;
  }
  
  // Update counter
  const counter = document.getElementById('currentImageIndex');
  if (counter) {
    counter.textContent = (viewingImageIndex + 1).toString();
  }
  
  // Update navigation buttons
  const prevButton = document.querySelector('.prev-image');
  const nextButton = document.querySelector('.next-image');
  
  if (prevButton) {
    prevButton.disabled = viewingImageIndex === 0;
  }
  
  if (nextButton) {
    nextButton.disabled = viewingImageIndex === images.length - 1;
  }
  
  // Update thumbnails
  const thumbnails = document.querySelectorAll('.profile-thumbnail');
  thumbnails.forEach((thumbnail, i) => {
    thumbnail.classList.toggle('active', i === viewingImageIndex);
  });
}

/**
 * Close the profile viewer modal
 */
function closeProfileViewer() {
  const profileViewerModal = document.getElementById('profileViewerModal');
  if (profileViewerModal) {
    profileViewerModal.classList.remove('active');
  }
}
