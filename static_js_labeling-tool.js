/**
 * Labeling Tool functionality for the Tinder Scraper application
 * Handles profile labeling interface and data submission
 */

// Global variables
let profiles = [];
let currentProfileIndex = 0;
let currentImageIndex = 0;
let isLabelsDirty = false;
let darkTheme = false;

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the labeling tool
    initializeLabelingTool();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load initial profiles
    loadProfiles();
});

/**
 * Initialize labeling tool
 */
function initializeLabelingTool() {
    // Initialize theme
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (prefersDark) {
        toggleTheme();
    }
    
    // Initialize range sliders
    initRangeSliders();
    
    console.log('Labeling tool initialized');
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Theme toggle
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Status filter
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            loadProfiles();
        });
    }
    
    // Location filter
    const locationFilter = document.getElementById('locationFilter');
    if (locationFilter) {
        locationFilter.addEventListener('change', function() {
            loadProfiles();
        });
    }
    
    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadProfiles);
    }
    
    // Save labels button
    const saveBtn = document.querySelector('.editor-button.primary');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveLabels);
    }
    
    // Skip button
    const skipBtn = document.querySelector('.editor-button.secondary');
    if (skipBtn) {
        skipBtn.addEventListener('click', skipProfile);
    }
    
    // Reset button
    const resetBtn = document.querySelector('.status-button[onclick="resetLabels()"]');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetLabels);
    }
    
    // Export labels button
    const exportBtn = document.querySelector('.status-button.primary');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportLabels);
    }
    
    // Set up form change detection
    setupFormChangeDetection();
    
    // Set up before unload warning
    window.addEventListener('beforeunload', function(e) {
        if (isLabelsDirty) {
            const message = 'You have unsaved changes. Are you sure you want to leave?';
            e.returnValue = message;
            return message;
        }
    });
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
}

/**
 * Navigate to another page
 */
function navigateTo(page) {
    if (isLabelsDirty) {
        const confirmed = confirm('You have unsaved changes. Do you want to leave this page?');
        if (!confirmed) {
            return;
        }
    }
    
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
 * Load unlabeled profiles
 */
function loadProfiles() {
    // Get filter values
    const statusFilter = document.getElementById('statusFilter')?.value || 'unlabeled';
    const locationFilter = document.getElementById('locationFilter')?.value || '';
    
    // Build query parameters
    const params = new URLSearchParams({
        status: statusFilter,
        location: locationFilter
    });
    
    // Show loading state in profile list
    const profileList = document.getElementById('profileList');
    if (profileList) {
        profileList.innerHTML = `
            <div style="display: flex; justify-content: center; padding: 20px;">
                <i class="fas fa-spinner fa-spin" style="font-size: 24px;"></i>
            </div>
        `;
    }
    
    // Fetch profiles
    fetch(`/api/get-unlabeled-profiles?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            profiles = data.profiles || [];
            
            // Update dashboard stats
            updateDashboardStats(data.stats);
            
            // Render profile list
            renderProfileList();
            
            // Load first profile if available
            if (profiles.length > 0) {
                loadProfile(0);
            } else {
                showEmptyState();
            }
        })
        .catch(error => {
            console.error('Error loading profiles:', error);
            
            if (profileList) {
                profileList.innerHTML = `
                    <div style="text-align: center; padding: 20px; color: var(--error-color);">
                        <i class="fas fa-exclamation-circle"></i>
                        <p>Error loading profiles: ${error.message}</p>
                    </div>
                `;
            }
        });
}

/**
 * Update dashboard statistics
 */
function updateDashboardStats(stats) {
    if (!stats) return;
    
    // Update counts
    document.getElementById('totalProfiles').textContent = formatNumber(stats.total || 0);
    document.getElementById('unlabeledProfiles').textContent = formatNumber(stats.unlabeled || 0);
    document.getElementById('labeledProfiles').textContent = formatNumber(stats.labeled || 0);
    
    // Update completion percentage
    const completion = stats.total > 0 ? ((stats.labeled / stats.total) * 100).toFixed(1) : '0.0';
    document.getElementById('completionPercentage').textContent = `${completion}%`;
}

/**
 * Format a number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Render profile list
 */
function renderProfileList() {
    const profileList = document.getElementById('profileList');
    if (!profileList) return;
    
    // Clear the list
    profileList.innerHTML = '';
    
    // Check if we have profiles
    if (!profiles || profiles.length === 0) {
        profileList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search empty-icon"></i>
                <div class="empty-title">No profiles found</div>
                <div class="empty-message">Try adjusting your filters or import more profiles.</div>
            </div>
        `;
        return;
    }
    
    // Render each profile
    profiles.forEach((profile, index) => {
        const profileItem = document.createElement('div');
        profileItem.className = `profile-item ${index === currentProfileIndex ? 'active' : ''}`;
        profileItem.onclick = () => {
            if (isLabelsDirty) {
                const confirmed = confirm('You have unsaved changes. Do you want to load a different profile?');
                if (!confirmed) {
                    return;
                }
            }
            loadProfile(index);
        };
        
        // Get cover image URL
        const coverImage = profile.images && profile.images.length > 0 ? 
            `/api/images/${profile.images[0].filename}` : 
            'https://via.placeholder.com/60x60?text=No+Image';
        
        // Get status class
        const statusClass = profile.status === 'labeled' ? 'status-labeled' : 
                           (profile.status === 'unlabeled' ? 'status-unlabeled' : 'status-skipped');
        
        // Format the status text
        const statusText = profile.status ? 
            profile.status.charAt(0).toUpperCase() + profile.status.slice(1) : 
            'Unlabeled';
        
        profileItem.innerHTML = `
            <img src="${coverImage}" alt="Profile" class="profile-item-image">
            <div class="profile-item-info">
                <div class="profile-item-title">Profile ${profile.profile_id}</div>
                <div class="profile-item-subtitle">${profile.location || 'Unknown location'}</div>
                <span class="profile-item-status ${statusClass}">${statusText}</span>
            </div>
        `;
        
        profileList.appendChild(profileItem);
    });
}

/**
 * Load a profile into the editor
 */
function loadProfile(index) {
    currentProfileIndex = index;
    currentImageIndex = 0;
    isLabelsDirty = false;
    
    const profile = profiles[index];
    if (!profile) return;
    
    // Update editor title
    document.getElementById('editorTitle').textContent = `Profile ${profile.profile_id}`;
    
    // Update profile details
    document.getElementById('profileId').textContent = profile.profile_id || 'Unknown';
    document.getElementById('profileLocation').textContent = profile.location || 'Unknown';
    document.getElementById('scrapedAt').textContent = profile.scraped_at || 'Unknown';
    document.getElementById('profileBio').textContent = profile.bio || 'No bio available';
    
    // Update images
    if (profile.images && profile.images.length > 0) {
        document.getElementById('mainImage').src = `/api/images/${profile.images[0].filename}`;
        document.getElementById('currentImageIndex').textContent = '1';
        document.getElementById('totalImages').textContent = profile.images.length;
        
        // Update image navigation buttons
        document.getElementById('prevImageBtn').disabled = true;
        document.getElementById('nextImageBtn').disabled = profile.images.length <= 1;
        
        // Render thumbnails
        const thumbnailsContainer = document.getElementById('imageThumbnails');
        if (thumbnailsContainer) {
            thumbnailsContainer.innerHTML = '';
            
            profile.images.forEach((image, idx) => {
                const thumbnail = document.createElement('img');
                thumbnail.className = `profile-thumbnail ${idx === 0 ? 'active' : ''}`;
                thumbnail.src = `/api/images/${image.filename}`;
                thumbnail.alt = `Thumbnail ${idx + 1}`;
                thumbnail.onclick = () => selectImage(idx);
                thumbnailsContainer.appendChild(thumbnail);
            });
        }
    } else {
        // No images available
        document.getElementById('mainImage').src = 'https://via.placeholder.com/800x600?text=No+Image';
        document.getElementById('currentImageIndex').textContent = '0';
        document.getElementById('totalImages').textContent = '0';
        document.getElementById('prevImageBtn').disabled = true;
        document.getElementById('nextImageBtn').disabled = true;
        
        const thumbnailsContainer = document.getElementById('imageThumbnails');
        if (thumbnailsContainer) {
            thumbnailsContainer.innerHTML = '';
        }
    }
    
    // Update label fields
    if (profile.labels) {
        updateLabelFields(profile.labels);
    } else {
        // If no labels, use defaults
        const defaultLabels = {
            age: [25, 30],
            height: [165, 175],
            weight: [55, 65],
            gender: [
                { name: 'female', value: [85, 95] },
                { name: 'male', value: [5, 15] }
            ],
            intelligence: [75, 90],
            cooperativeness: [60, 85],
            confidence: [70, 90],
            ethnicity: [
                { name: 'European', value: [75, 90] },
                { name: 'East Asian', value: [5, 15] },
                { name: 'South Asian', value: [3, 8] },
                { name: 'African', value: [2, 7] },
                { name: 'Middle Eastern', value: [3, 8] },
                { name: 'Mixed/Other', value: [10, 20] }
            ]
        };
        
        updateLabelFields(defaultLabels);
    }
    
    // Update active item in the list
    const items = document.querySelectorAll('.profile-item');
    items.forEach((item, idx) => {
        item.classList.toggle('active', idx === currentProfileIndex);
    });
}

/**
 * Show empty state when no profiles are available
 */
function showEmptyState() {
    const profileEditor = document.getElementById('profileEditor');
    if (!profileEditor) return;
    
    profileEditor.innerHTML = `
        <div class="empty-state">
            <i class="fas fa-image empty-icon"></i>
            <div class="empty-title">No profiles available</div>
            <div class="empty-message">Import profiles to start labeling or try adjusting your filters.</div>
        </div>
    `;
}

/**
 * Update label fields with profile data
 */
function updateLabelFields(labels) {
    // Basic attributes
    updateRangeField('age', labels.age[0], labels.age[1], 18, 50);
    updateRangeField('height', labels.height[0], labels.height[1], 140, 200);
    updateRangeField('weight', labels.weight[0], labels.weight[1], 40, 100);
    
    // Gender
    const female = labels.gender.find(g => g.name === 'female') || { value: [0, 0] };
    const male = labels.gender.find(g => g.name === 'male') || { value: [0, 0] };
    
    document.getElementById('femaleMin').value = female.value[0];
    document.getElementById('femaleMax').value = female.value[1];
    document.getElementById('maleMin').value = male.value[0];
    document.getElementById('maleMax').value = male.value[1];
    
    // Personality attributes
    updateRangeField('intelligence', labels.intelligence[0], labels.intelligence[1], 0, 100);
    updateRangeField('cooperativeness', labels.cooperativeness[0], labels.cooperativeness[1], 0, 100);
    updateRangeField('confidence', labels.confidence[0], labels.confidence[1], 0, 100);
    
    // Ethnicity
    const ethnicityMap = {
        'European': ['european', 0],
        'East Asian': ['eastAsian', 1],
        'South Asian': ['southAsian', 2],
        'African': ['african', 3],
        'Middle Eastern': ['middleEastern', 4],
        'Mixed/Other': ['mixed', 5]
    };
    
    labels.ethnicity.forEach(ethnicity => {
        const [id, _] = ethnicityMap[ethnicity.name] || ['', -1];
        if (id) {
            document.getElementById(`${id}Min`).value = ethnicity.value[0];
            document.getElementById(`${id}Max`).value = ethnicity.value[1];
        }
    });
}

/**
 * Update a range field with the given values
 */
function updateRangeField(id, minValue, maxValue, minRange, maxRange) {
    // Update text displays
    document.getElementById(`${id}Min`).textContent = minValue;
    document.getElementById(`${id}Max`).textContent = maxValue;
    
    // Calculate percentages for the visual elements
    const range = maxRange - minRange;
    const minPercent = ((minValue - minRange) / range) * 100;
    const maxPercent = ((maxValue - minRange) / range) * 100;
    const width = maxPercent - minPercent;
    
    // Update visual elements
    document.getElementById(`${id}Fill`).style.width = `${width}%`;
    document.getElementById(`${id}Fill`).style.left = `${minPercent}%`;
    document.getElementById(`${id}MinHandle`).style.left = `${minPercent}%`;
    document.getElementById(`${id}MaxHandle`).style.left = `${maxPercent}%`;
}

/**
 * Initialize range sliders
 */
function initRangeSliders() {
    // Basic attributes
    initRangeSlider('age', 18, 50);
    initRangeSlider('height', 140, 200);
    initRangeSlider('weight', 40, 100);
    
    // Personality attributes
    initRangeSlider('intelligence', 0, 100);
    initRangeSlider('cooperativeness', 0, 100);
    initRangeSlider('confidence', 0, 100);
}

/**
 * Initialize a range slider with drag functionality
 */
function initRangeSlider(id, min, max) {
    const minHandle = document.getElementById(`${id}MinHandle`);
    const maxHandle = document.getElementById(`${id}MaxHandle`);
    
    if (!minHandle || !maxHandle) return;
    
    const track = minHandle.parentElement;
    
    // Variables for drag state
    let isDragging = false;
    let activeHandle = null;
    let startX = 0;
    let startLeft = 0;
    
    // Helper to update the display
    const updateDisplay = (handle, left) => {
        // Ensure the left position is within bounds
        left = Math.max(0, Math.min(100, left));
        
        // Check handle constraints (min handle can't go past max, max can't go before min)
        if (handle === minHandle) {
            const maxLeft = parseFloat(maxHandle.style.left);
            left = Math.min(left, maxLeft - 5);
        } else {
            const minLeft = parseFloat(minHandle.style.left);
            left = Math.max(left, minLeft + 5);
        }
        
        // Update handle position
        handle.style.left = `${left}%`;
        
        // Update the fill element
        const fillElement = document.getElementById(`${id}Fill`);
        const minLeft = parseFloat(minHandle.style.left);
        const maxLeft = parseFloat(maxHandle.style.left);
        
        if (fillElement) {
            fillElement.style.left = `${minLeft}%`;
            fillElement.style.width = `${maxLeft - minLeft}%`;
        }
        
        // Calculate and update the value display
        const value = Math.round(min + (left / 100) * (max - min));
        
        if (handle === minHandle) {
            const minLabel = document.getElementById(`${id}Min`);
            if (minLabel) minLabel.textContent = value;
        } else {
            const maxLabel = document.getElementById(`${id}Max`);
            if (maxLabel) maxLabel.textContent = value;
        }
        
        // Mark form as dirty
        isLabelsDirty = true;
    };
    
    // Mouse down event for both handles
    const handleMouseDown = (e, handle) => {
        isDragging = true;
        activeHandle = handle;
        startX = e.clientX;
        startLeft = parseFloat(handle.style.left);
        
        // Prevent text selection during drag
        document.body.style.userSelect = 'none';
        
        // Add event listeners for drag and release
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
        
        // Prevent default behavior
        e.preventDefault();
    };
    
    // Mouse move event (during drag)
    const handleMouseMove = (e) => {
        if (!isDragging) return;
        
        // Calculate new position
        const deltaX = e.clientX - startX;
        const trackWidth = track.offsetWidth;
        const deltaPercent = (deltaX / trackWidth) * 100;
        const newLeft = startLeft + deltaPercent;
        
        // Update display
        updateDisplay(activeHandle, newLeft);
    };
    
    // Mouse up event (end drag)
    const handleMouseUp = () => {
        isDragging = false;
        document.body.style.userSelect = '';
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
    };
    
    // Add event listeners to handles
    minHandle.addEventListener('mousedown', (e) => handleMouseDown(e, minHandle));
    maxHandle.addEventListener('mousedown', (e) => handleMouseDown(e, maxHandle));
    
    // Handle click on track
    track.addEventListener('click', (e) => {
        if (e.target !== track) return;
        
        const rect = track.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickPercent = (clickX / rect.width) * 100;
        
        // Determine which handle to move (closest one)
        const minLeft = parseFloat(minHandle.style.left);
        const maxLeft = parseFloat(maxHandle.style.left);
        const handle = Math.abs(clickPercent - minLeft) < Math.abs(clickPercent - maxLeft) ? minHandle : maxHandle;
        
        // Update display
        updateDisplay(handle, clickPercent);
    });
}

/**
 * Set up form change detection for inputs
 */
function setupFormChangeDetection() {
    // Listen for changes in ethnicity inputs
    document.querySelectorAll('.ethnicity-input').forEach(input => {
        input.addEventListener('change', () => {
            isLabelsDirty = true;
        });
    });
    
    // Listen for changes in gender inputs
    document.querySelectorAll('.gender-input').forEach(input => {
        input.addEventListener('change', () => {
            isLabelsDirty = true;
        });
    });
}

/**
 * Navigate to previous image
 */
function prevImage() {
    if (currentImageIndex > 0) {
        currentImageIndex--;
        updateCurrentImage();
    }
}

/**
 * Navigate to next image
 */
function nextImage() {
    const profile = profiles[currentProfileIndex];
    if (profile && profile.images && currentImageIndex < profile.images.length - 1) {
        currentImageIndex++;
        updateCurrentImage();
    }
}

/**
 * Select a specific image
 */
function selectImage(index) {
    currentImageIndex = index;
    updateCurrentImage();
}

/**
 * Update the current image display
 */
function updateCurrentImage() {
    const profile = profiles[currentProfileIndex];
    if (!profile || !profile.images || profile.images.length === 0) return;
    
    // Update main image
    const mainImage = document.getElementById('mainImage');
    if (mainImage) {
        mainImage.src = `/api/images/${profile.images[currentImageIndex].filename}`;
    }
    
    // Update counter
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
 * Skip the current profile for later
 */
function skipProfile() {
    if (profiles.length === 0 || currentProfileIndex >= profiles.length) return;
    
    const profile = profiles[currentProfileIndex];
    
    // Mark as skipped
    fetch(`/api/skip-profile/${profile.profile_id}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update profile status
            profile.status = 'skipped';
            
            // Update UI
            const items = document.querySelectorAll('.profile-item');
            const currentItem = items[currentProfileIndex];
            
            if (currentItem) {
                const statusBadge = currentItem.querySelector('.profile-item-status');
                
                if (statusBadge) {
                    statusBadge.className = 'profile-item-status status-skipped';
                    statusBadge.textContent = 'Skipped';
                }
            }
            
            // Load next profile if available
            isLabelsDirty = false;
            
            if (currentProfileIndex < profiles.length - 1) {
                loadProfile(currentProfileIndex + 1);
            } else {
                // Reload profiles if this was the last one
                loadProfiles();
            }
        } else {
            alert(`Error: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error skipping profile:', error);
        alert('Failed to skip profile. Please try again.');
    });
}

/**
 * Reset labels to original values
 */
function resetLabels() {
    if (!isLabelsDirty) return;
    
    const confirmed = confirm('Are you sure you want to reset all labels to their original values?');
    if (!confirmed) return;
    
    const profile = profiles[currentProfileIndex];
    if (!profile) return;
    
    if (profile.labels) {
        updateLabelFields(profile.labels);
    } else {
        // If no labels, use defaults
        const defaultLabels = {
            age: [25, 30],
            height: [165, 175],
            weight: [55, 65],
            gender: [
                { name: 'female', value: [85, 95] },
                { name: 'male', value: [5, 15] }
            ],
            intelligence: [75, 90],
            cooperativeness: [60, 85],
            confidence: [70, 90],
            ethnicity: [
                { name: 'European', value: [75, 90] },
                { name: 'East Asian', value: [5, 15] },
                { name: 'South Asian', value: [3, 8] },
                { name: 'African', value: [2, 7] },
                { name: 'Middle Eastern', value: [3, 8] },
                { name: 'Mixed/Other', value: [10, 20] }
            ]
        };
        
        updateLabelFields(defaultLabels);
    }
    
    isLabelsDirty = false;
}

/**
 * Save the current labels
 */
function saveLabels() {
    if (profiles.length === 0 || currentProfileIndex >= profiles.length) return;
    
    const profile = profiles[currentProfileIndex];
    
    // Collect all label values
    const labels = {
        age: [
            parseInt(document.getElementById('ageMin').textContent),
            parseInt(document.getElementById('ageMax').textContent)
        ],
        height: [
            parseInt(document.getElementById('heightMin').textContent),
            parseInt(document.getElementById('heightMax').textContent)
        ],
        weight: [
            parseInt(document.getElementById('weightMin').textContent),
            parseInt(document.getElementById('weightMax').textContent)
        ],
        gender: [
            {
                name: 'female',
                value: [
                    parseInt(document.getElementById('femaleMin').value),
                    parseInt(document.getElementById('femaleMax').value)
                ]
            },
            {
                name: 'male',
                value: [
                    parseInt(document.getElementById('maleMin').value),
                    parseInt(document.getElementById('maleMax').value)
                ]
            }
        ],
        intelligence: [
            parseInt(document.getElementById('intelligenceMin').textContent),
            parseInt(document.getElementById('intelligenceMax').textContent)
        ],
        cooperativeness: [
            parseInt(document.getElementById('cooperativenessMin').textContent),
            parseInt(document.getElementById('cooperativenessMax').textContent)
        ],
        confidence: [
            parseInt(document.getElementById('confidenceMin').textContent),
            parseInt(document.getElementById('confidenceMax').textContent)
        ],
        ethnicity: [
            {
                name: 'European',
                value: [
                    parseInt(document.getElementById('europeanMin').value),
                    parseInt(document.getElementById('europeanMax').value)
                ]
            },
            {
                name: 'East Asian',
                value: [
                    parseInt(document.getElementById('eastAsianMin').value),
                    parseInt(document.getElementById('eastAsianMax').value)
                ]
            },
            {
                name: 'South Asian',
                value: [
                    parseInt(document.getElementById('southAsianMin').value),
                    parseInt(document.getElementById('southAsianMax').value)
                ]
            },
            {
                name: 'African',
                value: [
                    parseInt(document.getElementById('africanMin').value),
                    parseInt(document.getElementById('africanMax').value)
                ]
            },
            {
                name: 'Middle Eastern',
                value: [
                    parseInt(document.getElementById('middleEasternMin').value),
                    parseInt(document.getElementById('middleEasternMax').value)
                ]
            },
            {
                name: 'Mixed/Other',
                value: [
                    parseInt(document.getElementById('mixedMin').value),
                    parseInt(document.getElementById('mixedMax').value)
                ]
            }
        ]
    };
    
    // Save labels
    fetch(`/api/save-labels/${profile.profile_id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ labels })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update profile
            profile.labels = labels;
            profile.status = 'labeled';
            
            // Update UI
            const items = document.querySelectorAll('.profile-item');
            const currentItem = items[currentProfileIndex];
            
            if (currentItem) {
                const statusBadge = currentItem.querySelector('.profile-item-status');
                
                if (statusBadge) {
                    statusBadge.className = 'profile-item-status status-labeled';
                    statusBadge.textContent = 'Labeled';
                }
            }
            
            // Reset dirty flag
            isLabelsDirty = false;
            
            // Show success message
            alert('Labels saved successfully!');
            
            // Load next profile if available
            if (currentProfileIndex < profiles.length - 1) {
                loadProfile(currentProfileIndex + 1);
            } else {
                // Reload profiles if this was the last one
                loadProfiles();
            }
        } else {
            alert(`Error: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error saving labels:', error);
        alert('Failed to save labels. Please try again.');
    });
}

/**
 * Export labels for all labeled profiles
 */
function exportLabels() {
    fetch('/api/export-labels')
        .then(response => {
            if (response.ok) {
                return response.blob();
            }
            throw new Error('Network response was not ok');
        })
        .then(blob => {
            // Create a link and click it to trigger download
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `tinder_labels_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            console.error('Error exporting labels:', error);
            alert('Failed to export labels. Please try again.');
        });
}