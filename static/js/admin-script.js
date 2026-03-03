// ===================================
// Admin Panel Scripts
// ===================================

// ===================================
// Session Management
// ===================================
function getAdminSession() {
    try {
        const session = localStorage.getItem('adminSession');
        if (!session) throw new Error('missing session');
        
        const data = JSON.parse(session);
        // Session is valid for 24 hours
        if (Date.now() - data.timestamp > 24 * 60 * 60 * 1000) {
            localStorage.removeItem('adminSession');
            throw new Error('expired session');
        }
        return data;
    } catch (e) {
        const body = document.body;
        if (body && body.dataset && body.dataset.hospitalId) {
            return {
                hospitalId: body.dataset.hospitalId,
                adminName: body.dataset.adminName || '',
                timestamp: Date.now()
            };
        }

        return null;
    }
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('adminSession');
        logActivity('Admin logout', 'success');
        window.location.href = getAdminLoginUrl();
    }
}

function getAdminLoginUrl() {
    if (window.ADMIN_LOGIN_URL) {
        return window.ADMIN_LOGIN_URL;
    }
    return '/portal/';
}

// ===================================
// Hospital Data Management
// ===================================
function getHospitalData() {
    const session = getAdminSession();
    if (!session) return null;

    const key = `hospital_${session.hospitalId}`;
    const data = localStorage.getItem(key);

    if (data) {
        return JSON.parse(data);
    }

    // Default hospital data
    return {
        id: session.hospitalId,
        name: getHospitalName(session.hospitalId),
        type: 'General Hospital',
        description: 'A leading healthcare provider',
        phone: '(555) 000-0000',
        emergency: '911',
        email: 'info@hospital.com',
        address: '123 Hospital Street',
        website: 'www.hospital.com',
        hours: '24/7',
        staff: [],
        beds: {
            general: { total: 120, available: 45, reserved: 0, bookingDisabled: false },
            hdu: { total: 40, available: 12, reserved: 0, bookingDisabled: false },
            icu: { total: 60, available: 8, reserved: 0, bookingDisabled: false },
            emergency: { total: 30, available: 5, reserved: 0, bookingDisabled: false }
        },
        settings: {
            reservationDuration: 45,
            allowEmergencyBooking: false,
            requireMinBeds: true
        }
    };
}

function saveHospitalData(data) {
    const session = getAdminSession();
    if (!session) return false;

    const key = `hospital_${session.hospitalId}`;
    localStorage.setItem(key, JSON.stringify(data));
    return true;
}

function loadHospitalData() {
    const session = getAdminSession();
    if (!session) return;

    const hospitalData = getHospitalData();
    const nameElement = document.getElementById('hospitalName');
    if (nameElement) {
        nameElement.textContent = hospitalData.name;
    }
}

function getHospitalName(hospitalId) {
    const names = {
        '1': 'City General Hospital',
        '2': 'Riverside Medical Center',
        '3': 'St. Mary\'s Healthcare',
        '4': 'North End Hospital'
    };
    return names[hospitalId] || 'Hospital';
}

// ===================================
// Bookings Management
// ===================================
function getBookings() {
    const session = getAdminSession();
    if (!session) return [];

    const key = `bookings_${session.hospitalId}`;
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : [];
}

function saveBookings(bookings) {
    const session = getAdminSession();
    if (!session) return false;

    const key = `bookings_${session.hospitalId}`;
    localStorage.setItem(key, JSON.stringify(bookings));
    return true;
}

function getTimeRemaining(expiresAt) {
    return expiresAt - Date.now();
}

function formatTimeRemaining(ms) {
    if (ms <= 0) return '00:00:00 (Expired)';

    const totalSeconds = Math.floor(ms / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

// ===================================
// Activity Logging
// ===================================
function getActivityLogs() {
    const session = getAdminSession();
    if (!session) return [];

    const key = `logs_${session.hospitalId}`;
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : [];
}

function saveActivityLogs(logs) {
    const session = getAdminSession();
    if (!session) return false;

    const key = `logs_${session.hospitalId}`;
    localStorage.setItem(key, JSON.stringify(logs));
    return true;
}

function logActivity(description, status = 'success', type = 'general') {
    const logs = getActivityLogs();
    
    logs.push({
        timestamp: Date.now(),
        description: description,
        status: status,
        type: type
    });

    // Keep only last 1000 logs
    if (logs.length > 1000) {
        logs.shift();
    }

    saveActivityLogs(logs);
}

// ===================================
// Notifications
// ===================================
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// ===================================
// Utility Functions
// ===================================
function getUrlParameter(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

// Return a safe percentage (0-100). Avoid NaN/divide-by-zero.
function safePercent(numerator, denominator) {
    const d = Number(denominator) || 0;
    if (d <= 0) return 0;
    const p = (Number(numerator) || 0) / d * 100;
    if (!isFinite(p) || isNaN(p)) return 0;
    return Math.max(0, Math.min(100, Math.round(p)));
}

// ===================================
// Slider Controls for bed overview
// ===================================
function slideNext() {
    const container = document.querySelector('.slider-container');
    if (!container) return;
    const stride = getCardStride(container);
    const currentIndex = Math.round(container.scrollLeft / stride);
    const nextIndex = currentIndex + 1;
    const target = Math.round(nextIndex * stride);
    container.scrollTo({ left: target, behavior: 'smooth' });
    setTimeout(updateSliderButtons, 300);
}

function slidePrev() {
    const container = document.querySelector('.slider-container');
    if (!container) return;
    const stride = getCardStride(container);
    const currentIndex = Math.round(container.scrollLeft / stride);
    const prevIndex = Math.max(0, currentIndex - 1);
    const target = Math.round(prevIndex * stride);
    container.scrollTo({ left: target, behavior: 'smooth' });
    setTimeout(updateSliderButtons, 300);
}

function updateSliderButtons() {
    const container = document.querySelector('.slider-container');
    const prev = document.querySelector('.slider-prev');
    const next = document.querySelector('.slider-next');
    if (!container || !prev || !next) return;

    // Show or hide arrows based on overflow
    if (container.scrollWidth <= container.clientWidth + 1) {
        prev.style.display = 'none';
        next.style.display = 'none';
    } else {
        prev.style.display = 'flex';
        next.style.display = 'flex';
    }

    // Style prev when at leftmost (NO disabled attribute!)
    if (container.scrollLeft <= 5) {
        prev.style.opacity = '0.4';
        prev.style.pointerEvents = 'none';
    } else {
        prev.style.opacity = '1';
        prev.style.pointerEvents = 'auto';
    }

    // Style next when at rightmost (NO disabled attribute!)
    if (container.scrollLeft + container.clientWidth >= container.scrollWidth - 5) {
        next.style.opacity = '0.4';
        next.style.pointerEvents = 'none';
    } else {
        next.style.opacity = '1';
        next.style.pointerEvents = 'auto';
    }
}

function getCardStride(container) {
    const track = container.querySelector('.slider-track') || container.querySelector('.bed-overview-grid');
    const card = container.querySelector('.bed-card');
    if (!card) return Math.round(container.clientWidth * 0.98);
    const cardRect = card.getBoundingClientRect();
    const style = window.getComputedStyle(track || container);
    const gapVal = parseFloat(style.gap || style.columnGap || '0') || 0;
    // stride equals card width plus gap between cards
    return Math.round(cardRect.width + gapVal);
}

// Pointer/touch swipe support
function bindSliderPointerDrag() {
    const container = document.querySelector('.slider-container');
    if (!container) return;

    let isDown = false;
    let startX = 0;
    let startScrollLeft = 0;

    container.addEventListener('pointerdown', (e) => {
        // Only left button
        if (e.button && e.button !== 0) return;
        isDown = true;
        startX = e.clientX;
        startScrollLeft = container.scrollLeft;
        container.setPointerCapture(e.pointerId);
        container.style.cursor = 'grabbing';
    });

    container.addEventListener('pointermove', (e) => {
        if (!isDown) return;
        const dx = e.clientX - startX;
        container.scrollLeft = startScrollLeft - dx;
    });

    function endDrag(e) {
        if (!isDown) return;
        isDown = false;
        container.style.cursor = 'grab';
        try { container.releasePointerCapture && container.releasePointerCapture(e.pointerId); } catch (err) {}
        // Snap to nearest card
        snapToNearest(container);
        setTimeout(updateSliderButtons, 200);
    }

    container.addEventListener('pointerup', endDrag);
    container.addEventListener('pointercancel', endDrag);
    container.addEventListener('pointerleave', endDrag);
}

function snapToNearest(container) {
    const stride = getCardStride(container);
    const index = Math.round(container.scrollLeft / stride);
    const target = Math.round(index * stride);
    container.scrollTo({ left: target, behavior: 'smooth' });
}

window.addEventListener('load', function() {
    // wire slider updates
    const container = document.querySelector('.slider-container');
    if (container) {
        container.addEventListener('scroll', function() {
            // throttle-ish
            window.requestAnimationFrame(updateSliderButtons);
        });
            // bind pointer drag once ready
            bindSliderPointerDrag();
    }

    window.addEventListener('resize', function() {
        updateSliderButtons();
    });

    // initial check
    setTimeout(updateSliderButtons, 250);
});

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString();
}

// ===================================
// Page Navigation
// ===================================
function navigateTo(page) {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.classList.remove('active');
    });

    const activeItem = document.querySelector(`[data-page="${page}"]`);
    if (activeItem) {
        activeItem.classList.add('active');
    }
}

// ===================================
// Automatic Session Check
// ===================================
// Django handles admin session validation server-side.

// ===================================
// Form Helpers
// ===================================
function validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function validatePhone(phone) {
    const regex = /^[\d\s\-\+\(\)]{10,}$/;
    return regex.test(phone);
}

// ===================================
// Export/Import Data
// ===================================
function exportHospitalData() {
    const hospitalData = getHospitalData();
    const bookings = getBookings();
    const logs = getActivityLogs();

    const data = {
        hospital: hospitalData,
        bookings: bookings,
        logs: logs,
        exportedAt: new Date().toISOString()
    };

    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `hospital-backup-${Date.now()}.json`;
    a.click();
    window.URL.revokeObjectURL(url);

    showNotification('Data exported successfully', 'success');
}

// ===================================
// Data Validation
// ===================================
function validateBedData(beds) {
    // Validate that available + reserved <= total
    for (const bedType in beds) {
        const bed = beds[bedType];
        if ((bed.available + bed.reserved) > bed.total) {
            return false;
        }
    }
    return true;
}

// ===================================
// Chart Data Helpers (for future use)
// ===================================
function getBedUtilizationData() {
    const hospitalData = getHospitalData();
    const data = {
        labels: [],
        available: [],
        occupied: [],
        reserved: []
    };

    Object.entries(hospitalData.beds).forEach(([key, bed]) => {
        data.labels.push(key.charAt(0).toUpperCase() + key.slice(1));
        data.available.push(bed.available);
        data.occupied.push(bed.total - bed.available - bed.reserved);
        data.reserved.push(bed.reserved);
    });

    return data;
}

function getBookingTrendData() {
    const logs = getActivityLogs();
    const bookingLogs = logs.filter(log => log.type === 'booking');

    const data = {
        today: 0,
        thisWeek: 0,
        thisMonth: 0
    };

    const now = Date.now();
    const dayMs = 24 * 60 * 60 * 1000;
    const weekMs = 7 * dayMs;
    const monthMs = 30 * dayMs;

    bookingLogs.forEach(log => {
        const age = now - log.timestamp;
        if (age < dayMs) data.today++;
        if (age < weekMs) data.thisWeek++;
        if (age < monthMs) data.thisMonth++;
    });

    return data;
}

// ===================================
// Auto-save Timer (future enhancement)
// ===================================
let autoSaveInterval = null;

function startAutoSave() {
    autoSaveInterval = setInterval(function() {
        // Auto-save functionality can be implemented here
        console.log('Auto-save: Data backed up at', new Date().toLocaleTimeString());
    }, 5 * 60 * 1000); // Every 5 minutes
}

function stopAutoSave() {
    if (autoSaveInterval) {
        clearInterval(autoSaveInterval);
    }
}

// ===================================
// Bed Release on Expiration
// ===================================
function checkAndReleaseExpiredBookings() {
    const bookings = getBookings();
    const hospitalData = getHospitalData();
    let changesOccurred = false;

    bookings.forEach((booking, index) => {
        if (getTimeRemaining(booking.expiresAt) <= 0 && booking.status !== 'confirmed') {
            // Release the bed
            const bedType = booking.bedType.toLowerCase();
            if (hospitalData.beds[bedType] && booking.status !== 'released') {
                hospitalData.beds[bedType].available++;
                hospitalData.beds[bedType].reserved--;
                booking.status = 'released';
                changesOccurred = true;
            }
        }
    });

    if (changesOccurred) {
        saveHospitalData(hospitalData);
        saveBookings(bookings);
    }
}

// Check expired bookings every minute
setInterval(checkAndReleaseExpiredBookings, 60 * 1000);
