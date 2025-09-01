// TradeSOS Main JavaScript File - Emergency Trade Services Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeAlerts();
    initializeFormValidation();
    initializeFileUploads();
    initializeMessaging();
    initializeLocationServices();
    initializeNotifications();
    initializeSearchFilters();
    initializePremiumFeatures();
    
    // Initialize tooltips and popovers if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
});

// Alert Management
function initializeAlerts() {
    // Auto-hide success alerts after 5 seconds
    const successAlerts = document.querySelectorAll('.alert-success');
    successAlerts.forEach(alert => {
        setTimeout(() => {
            if (alert && alert.parentNode) {
                fadeOut(alert, 500);
            }
        }, 5000);
    });
    
    // Auto-hide info alerts after 7 seconds
    const infoAlerts = document.querySelectorAll('.alert-info');
    infoAlerts.forEach(alert => {
        setTimeout(() => {
            if (alert && alert.parentNode) {
                fadeOut(alert, 500);
            }
        }, 7000);
    });
}

// Enhanced Form Validation
function initializeFormValidation() {
    // UK Postcode validation
    const postcodeInputs = document.querySelectorAll('input[name="postcode"]');
    postcodeInputs.forEach(input => {
        input.addEventListener('input', function() {
            this.value = this.value.toUpperCase().replace(/\s+/g, ' ').trim();
            validatePostcode(this);
        });
        
        input.addEventListener('blur', function() {
            validatePostcode(this);
        });
    });
    
    // Phone number formatting
    const phoneInputs = document.querySelectorAll('input[name="phone"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            formatPhoneNumber(this);
        });
    });
    
    // Real-time character counters
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        const counter = document.createElement('div');
        counter.className = 'form-text text-end';
        counter.innerHTML = `<span class="char-count">0</span> / ${maxLength} characters`;
        textarea.parentNode.appendChild(counter);
        
        textarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            const charCount = counter.querySelector('.char-count');
            charCount.textContent = currentLength;
            
            if (currentLength > maxLength * 0.9) {
                charCount.className = 'char-count text-warning';
            } else if (currentLength > maxLength * 0.95) {
                charCount.className = 'char-count text-danger';
            } else {
                charCount.className = 'char-count';
            }
        });
    });
    
    // Skills input enhancement with suggestions
    const skillsInputs = document.querySelectorAll('input[name="skills"]');
    skillsInputs.forEach(input => {
        initializeSkillsAutocomplete(input);
    });
}

// File Upload Enhancements
function initializeFileUploads() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        // Create enhanced upload area
        const uploadArea = createUploadArea(input);
        
        // Handle file selection
        input.addEventListener('change', function() {
            handleFileSelection(this, uploadArea);
        });
        
        // Drag and drop functionality
        setupDragAndDrop(uploadArea, input);
    });
}

// Messaging System
function initializeMessaging() {
    const messageContainer = document.getElementById('messageContainer');
    if (messageContainer) {
        // Auto-scroll to bottom
        messageContainer.scrollTop = messageContainer.scrollHeight;
        
        // Setup auto-refresh for new messages
        setupMessageAutoRefresh();
    }
    
    // Message form handling
    const messageForm = document.querySelector('form[action*="send-message"]');
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendMessage(this);
        });
    }
}

// Location Services (Mock for MVP)
function initializeLocationServices() {
    const trackingMap = document.getElementById('trackingMap');
    if (trackingMap) {
        // Initialize mock tracking display
        setupMockTracking(trackingMap);
    }
    
    // Handle location sharing requests
    const shareLocationBtns = document.querySelectorAll('.share-location-btn');
    shareLocationBtns.forEach(btn => {
        btn.addEventListener('click', handleLocationSharing);
    });
}

// Notification System
function initializeNotifications() {
    // Request notification permissions for job alerts
    if ('Notification' in window && Notification.permission === 'default') {
        // Only request for trade users
        const userRole = document.body.getAttribute('data-user-role');
        if (userRole === 'trade') {
            requestNotificationPermission();
        }
    }
    
    // Setup notification sound
    setupNotificationSound();
}

// Search and Filter Enhancement
function initializeSearchFilters() {
    const searchForm = document.querySelector('form[method="GET"]');
    if (searchForm && !searchForm.hasAttribute('data-no-auto-submit')) {
        const inputs = searchForm.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.addEventListener('change', debounce(function() {
                if (this.form.querySelector('input[name="search"]').value.length > 2 || this.type !== 'text') {
                    // Auto-submit form for better UX
                    updateURLWithFilters(this.form);
                }
            }, 500));
        });
    }
}

// Premium Features
function initializePremiumFeatures() {
    // Highlight premium features
    const premiumFeatures = document.querySelectorAll('[data-premium="true"]');
    premiumFeatures.forEach(feature => {
        feature.classList.add('premium-feature');
        
        // Add premium tooltip
        if (typeof bootstrap !== 'undefined') {
            feature.setAttribute('data-bs-toggle', 'tooltip');
            feature.setAttribute('data-bs-placement', 'top');
            feature.setAttribute('title', 'Premium Feature - Upgrade to access');
            new bootstrap.Tooltip(feature);
        }
    });
    
    // Premium countdown timer
    initializePremiumCountdown();
}

// Utility Functions

function validatePostcode(input) {
    const postcodeRegex = /^[A-Z]{1,2}[0-9][A-Z0-9]?\s?[0-9][A-Z]{2}$/;
    const value = input.value.trim();
    
    if (value && !postcodeRegex.test(value)) {
        input.setCustomValidity('Please enter a valid UK postcode (e.g., M1 1AA)');
        input.classList.add('is-invalid');
    } else {
        input.setCustomValidity('');
        input.classList.remove('is-invalid');
        if (value) input.classList.add('is-valid');
    }
}

function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    
    // Basic UK phone number formatting
    if (value.startsWith('44')) {
        value = '+44 ' + value.slice(2);
    } else if (value.startsWith('0')) {
        value = value;
    }
    
    input.value = value;
}

function createUploadArea(input) {
    const uploadArea = document.createElement('div');
    uploadArea.className = 'file-upload-area';
    uploadArea.innerHTML = `
        <div class="upload-icon">
            <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
        </div>
        <h5>Drop files here or click to upload</h5>
        <p class="text-muted">Maximum file size: 16MB per file</p>
        <div class="upload-progress" style="display: none;">
            <div class="progress mb-2">
                <div class="progress-bar" role="progressbar" style="width: 0%"></div>
            </div>
            <small class="text-muted">Uploading...</small>
        </div>
    `;
    
    input.parentNode.insertBefore(uploadArea, input);
    input.style.display = 'none';
    
    uploadArea.addEventListener('click', () => input.click());
    
    return uploadArea;
}

function setupDragAndDrop(uploadArea, input) {
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            input.files = files;
            handleFileSelection(input, uploadArea);
        }
    });
}

function handleFileSelection(input, uploadArea) {
    const files = input.files;
    const fileList = document.createElement('div');
    fileList.className = 'file-list mt-3';
    
    // Remove existing file list
    const existingList = uploadArea.querySelector('.file-list');
    if (existingList) {
        existingList.remove();
    }
    
    // Display selected files
    Array.from(files).forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item d-flex justify-content-between align-items-center p-2 border rounded mb-2';
        
        const fileInfo = document.createElement('div');
        fileInfo.innerHTML = `
            <i class="fas fa-file me-2"></i>
            <span class="file-name">${file.name}</span>
            <small class="text-muted ms-2">(${formatFileSize(file.size)})</small>
        `;
        
        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn btn-sm btn-outline-danger';
        removeBtn.innerHTML = '<i class="fas fa-times"></i>';
        removeBtn.onclick = () => removeFile(input, index, uploadArea);
        
        fileItem.appendChild(fileInfo);
        fileItem.appendChild(removeBtn);
        fileList.appendChild(fileItem);
    });
    
    uploadArea.appendChild(fileList);
    
    // Validate file sizes
    validateFileUploads(files);
}

function sendMessage(form) {
    const messageInput = form.querySelector('input[name="message"]');
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // Disable form temporarily
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    submitBtn.disabled = true;
    
    // Simulate sending message (in real app, would use fetch)
    setTimeout(() => {
        // Add message to UI immediately for better UX
        addMessageToUI(message, true);
        
        // Clear input and re-enable form
        messageInput.value = '';
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        messageInput.focus();
        
        // Submit form for real
        form.submit();
    }, 500);
}

function addMessageToUI(message, isSent) {
    const messageContainer = document.getElementById('messageContainer');
    if (!messageContainer) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-bubble ${isSent ? 'sent' : 'received'} mb-2`;
    
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-GB', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    messageDiv.innerHTML = `
        <div class="d-flex ${isSent ? 'justify-content-end' : 'justify-content-start'}">
            <div class="message-content ${isSent ? 'bg-primary text-white' : 'bg-light'} p-2 rounded" style="max-width: 70%;">
                <p class="mb-1">${escapeHtml(message)}</p>
                <small class="${isSent ? 'text-white-50' : 'text-muted'}">${timeString}</small>
            </div>
        </div>
    `;
    
    messageContainer.appendChild(messageDiv);
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

function setupMockTracking(trackingMap) {
    // Mock tracking display with animated marker
    trackingMap.innerHTML = `
        <div class="tracking-display bg-light rounded p-4 text-center position-relative">
            <div class="tracking-header mb-3">
                <h6><i class="fas fa-map-marker-alt text-primary me-2"></i>Trade Professional Location</h6>
                <small class="text-muted">Last updated: <span class="update-time">${new Date().toLocaleTimeString()}</span></small>
            </div>
            <div class="tracking-map-placeholder bg-secondary rounded" style="height: 200px; position: relative; background: linear-gradient(45deg, #e9ecef 25%, transparent 25%, transparent 75%, #e9ecef 75%), linear-gradient(45deg, #e9ecef 25%, transparent 25%, transparent 75%, #e9ecef 75%); background-size: 20px 20px; background-position: 0 0, 10px 10px;">
                <div class="trade-marker position-absolute" style="top: 50%; left: 50%; transform: translate(-50%, -50%);">
                    <i class="fas fa-map-marker-alt text-primary fa-2x animate-bounce"></i>
                </div>
                <div class="eta-info position-absolute bottom-0 start-0 end-0 p-2 bg-white bg-opacity-90">
                    <small><strong>ETA: 15-20 minutes</strong> | Distance: 3.2 miles</small>
                </div>
            </div>
            <div class="tracking-status mt-3">
                <span class="badge bg-info">
                    <i class="fas fa-route me-1"></i>En Route
                </span>
            </div>
        </div>
    `;
    
    // Update time every minute
    setInterval(() => {
        const timeElement = trackingMap.querySelector('.update-time');
        if (timeElement) {
            timeElement.textContent = new Date().toLocaleTimeString();
        }
    }, 60000);
}

function initializePremiumCountdown() {
    const countdownElements = document.querySelectorAll('.premium-countdown');
    
    countdownElements.forEach(element => {
        const targetTime = new Date(Date.now() + 3 * 60 * 1000); // 3 minutes from now
        
        const updateCountdown = () => {
            const now = new Date();
            const timeLeft = targetTime - now;
            
            if (timeLeft > 0) {
                const minutes = Math.floor(timeLeft / (1000 * 60));
                const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
                
                element.innerHTML = `
                    <i class="fas fa-clock me-1"></i>
                    Premium Early Access: ${minutes}:${seconds.toString().padStart(2, '0')} remaining
                `;
                element.className = 'badge bg-warning text-dark premium-countdown';
            } else {
                element.innerHTML = '<i class="fas fa-users me-1"></i>Now available to all members';
                element.className = 'badge bg-info premium-countdown';
            }
        };
        
        updateCountdown();
        setInterval(updateCountdown, 1000);
    });
}

function setupNotificationSound() {
    // Create audio element for notification sound
    const notificationSound = document.createElement('audio');
    notificationSound.id = 'notificationSound';
    notificationSound.preload = 'auto';
    
    // Using a simple beep sound (data URI)
    notificationSound.src = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmEaAjuTz/PGbCUCJHa+7N2PQQXM';
    document.body.appendChild(notificationSound);
}

function requestNotificationPermission() {
    if (Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                showNotification('Notifications Enabled', 'You will now receive job alerts from TradeSOS');
            }
        });
    }
}

function showNotification(title, body) {
    if (Notification.permission === 'granted') {
        const notification = new Notification(title, {
            body: body,
            icon: '/static/images/logo-icon.png',
            badge: '/static/images/logo-badge.png',
            tag: 'tradesos-job-alert',
            requireInteraction: true
        });
        
        // Play notification sound
        const sound = document.getElementById('notificationSound');
        if (sound) {
            sound.play().catch(() => {}); // Ignore if play fails
        }
        
        notification.onclick = function() {
            window.focus();
            this.close();
        };
        
        setTimeout(() => notification.close(), 10000);
    }
}

function initializeSkillsAutocomplete(input) {
    const commonSkills = [
        'plumbing', 'heating', 'electrical', 'gas safety', 'boiler repair',
        'locksmith', 'glazing', 'roofing', 'drainage', 'emergency plumber',
        'central heating', 'radiator repair', 'bathroom fitting', 'kitchen fitting',
        'tiling', 'flooring', 'painting', 'decorating', 'carpentry', 'joinery'
    ];
    
    const datalist = document.createElement('datalist');
    datalist.id = 'skillsSuggestions';
    
    commonSkills.forEach(skill => {
        const option = document.createElement('option');
        option.value = skill;
        datalist.appendChild(option);
    });
    
    document.body.appendChild(datalist);
    input.setAttribute('list', 'skillsSuggestions');
}

function setupMessageAutoRefresh() {
    // Auto-refresh messages every 30 seconds
    setInterval(() => {
        const messageContainer = document.getElementById('messageContainer');
        if (messageContainer && document.visibilityState === 'visible') {
            // In a real app, this would fetch new messages via AJAX
            console.log('Checking for new messages...');
        }
    }, 30000);
}

// Utility Helper Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function fadeOut(element, duration) {
    element.style.transition = `opacity ${duration}ms`;
    element.style.opacity = '0';
    setTimeout(() => {
        if (element.parentNode) {
            element.parentNode.removeChild(element);
        }
    }, duration);
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function validateFileUploads(files) {
    const maxSize = 16 * 1024 * 1024; // 16MB
    let hasError = false;
    
    Array.from(files).forEach(file => {
        if (file.size > maxSize) {
            alert(`File "${file.name}" is too large. Maximum size is 16MB.`);
            hasError = true;
        }
    });
    
    return !hasError;
}

function removeFile(input, index, uploadArea) {
    const dt = new DataTransfer();
    const files = Array.from(input.files);
    
    files.forEach((file, i) => {
        if (i !== index) {
            dt.items.add(file);
        }
    });
    
    input.files = dt.files;
    handleFileSelection(input, uploadArea);
}

function updateURLWithFilters(form) {
    const formData = new FormData(form);
    const params = new URLSearchParams();
    
    for (let [key, value] of formData.entries()) {
        if (value.trim()) {
            params.append(key, value);
        }
    }
    
    const newURL = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, '', newURL);
}

function handleLocationSharing() {
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const { latitude, longitude } = position.coords;
                console.log('Location shared:', latitude, longitude);
                // In real app, would send to server
                alert(`Location shared: ${latitude.toFixed(6)}, ${longitude.toFixed(6)}`);
            },
            error => {
                console.error('Location sharing failed:', error);
                alert('Unable to share location. Please check your browser settings.');
            }
        );
    } else {
        alert('Location sharing is not supported by your browser.');
    }
}

// Emergency contact quick dial
function quickDial(number) {
    if ('navigator' in window && 'userAgent' in navigator && /Mobi|Android/i.test(navigator.userAgent)) {
        window.location.href = `tel:${number}`;
    } else {
        alert(`Emergency Number: ${number}\n\nOn mobile devices, this would dial automatically.`);
    }
}

// Global error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    
    // Don't show errors to users in production, but log them
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log('Development error details:', e);
    }
});

// Online/offline status handling
window.addEventListener('online', function() {
    const offlineAlert = document.getElementById('offlineAlert');
    if (offlineAlert) {
        offlineAlert.remove();
    }
    console.log('Connection restored');
});

window.addEventListener('offline', function() {
    const offlineAlert = document.createElement('div');
    offlineAlert.id = 'offlineAlert';
    offlineAlert.className = 'alert alert-warning position-fixed top-0 start-50 translate-middle-x mt-5';
    offlineAlert.style.zIndex = '9999';
    offlineAlert.innerHTML = `
        <i class="fas fa-wifi me-2"></i>
        <strong>Connection Lost</strong> - Some features may not work properly.
    `;
    document.body.appendChild(offlineAlert);
    console.log('Connection lost');
});
