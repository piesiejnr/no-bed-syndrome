// ===================================
// Global Script for Hospital System
// ===================================

// Initialize animations and interactions
document.addEventListener('DOMContentLoaded', function() {
    // Add scroll animations
    addScrollAnimations();
    
    // Initialize tooltips
    initializeTooltips();
});

// ===================================
// Scroll Animations
// ===================================
function addScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all cards and sections
    document.querySelectorAll(
        '.service-card, .hospital-card, .info-card, .quick-access-card, .nearby-hospital-card'
    ).forEach(el => {
        observer.observe(el);
    });
}

// ===================================
// CSS Animations
// ===================================
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
`;
document.head.appendChild(style);

// ===================================
// Tooltips
// ===================================
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(el => {
        el.addEventListener('mouseenter', showTooltip);
        el.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = e.target.dataset.tooltip;
    document.body.appendChild(tooltip);
    
    const rect = e.target.getBoundingClientRect();
    tooltip.style.position = 'fixed';
    tooltip.style.left = rect.left + 'px';
    tooltip.style.top = (rect.top - 10) + 'px';
    tooltip.style.zIndex = '1000';
}

function hideTooltip(e) {
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(tooltip => tooltip.remove());
}

// ===================================
// Bed Availability Status
// ===================================
function getBedStatus(available, total) {
    if (available === 0) return 'full';
    if (available < total * 0.2) return 'limited';
    return 'available';
}

// ===================================
// Distance Calculator (Mock)
// ===================================
function calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = 
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return (R * c).toFixed(1);
}

// ===================================
// Reservation Manager
// ===================================
class ReservationManager {
    constructor() {
        this.reservations = JSON.parse(localStorage.getItem('reservations')) || [];
    }

    addReservation(hospitalId, bedType, duration = 45) {
        const reservation = {
            id: Date.now(),
            hospitalId,
            bedType,
            timestamp: Date.now(),
            duration: duration * 60 * 1000 // Convert to milliseconds
        };

        this.reservations.push(reservation);
        this.save();
        return reservation;
    }

    getActiveReservations() {
        const now = Date.now();
        return this.reservations.filter(res => {
            return (now - res.timestamp) < res.duration;
        });
    }

    removeExpiredReservations() {
        const now = Date.now();
        this.reservations = this.reservations.filter(res => {
            return (now - res.timestamp) < res.duration;
        });
        this.save();
    }

    save() {
        localStorage.setItem('reservations', JSON.stringify(this.reservations));
    }
}

// ===================================
// Utility Functions
// ===================================

// Format time remaining
function formatTimeRemaining(ms) {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

// Get URL parameters
function getUrlParameter(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

// Sort hospitals by distance
function sortByDistance(hospitals) {
    return hospitals.sort((a, b) => a.distance - b.distance);
}

// Filter available hospitals
function filterAvailableHospitals(hospitals, bedType = null) {
    return hospitals.filter(hospital => {
        if (!bedType) return true;
        return hospital.beds[bedType].available > 0;
    });
}

// ===================================
// Search Functionality
// ===================================
function performSearch() {
    const query = document.getElementById('searchInput').value.toLowerCase();
    
    if (!query) {
        showEmptyState('Enter a search term');
        return;
    }

    // Simulate search with slight delay
    setTimeout(() => {
        // Search logic is in individual page scripts
    }, 300);
}

function showEmptyState(message) {
    const container = document.getElementById('resultsContainer');
    if (container) {
        container.innerHTML = `<p class="empty-state">${message}</p>`;
    }
}

// ===================================
// Notification System
// ===================================
class NotificationManager {
    static show(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${this.getBackground(type)};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }

    static getBackground(type) {
        const backgrounds = {
            'success': '#6FCF97',
            'error': '#EF5350',
            'warning': '#FFA726',
            'info': '#4A90E2'
        };
        return backgrounds[type] || backgrounds['info'];
    }
}

// ===================================
// Hospital Data Manager
// ===================================
class HospitalDataManager {
    static getAllHospitals() {
        return JSON.parse(localStorage.getItem('hospitals')) || [];
    }

    static getHospitalById(id) {
        const hospitals = this.getAllHospitals();
        return hospitals.find(h => h.id === id);
    }

    static updateBedAvailability(hospitalId, bedType, available) {
        const hospitals = this.getAllHospitals();
        const hospital = hospitals.find(h => h.id === hospitalId);
        
        if (hospital && hospital.beds[bedType]) {
            hospital.beds[bedType].available = available;
            hospital.beds[bedType].status = this.getStatus(available, hospital.beds[bedType].total);
            localStorage.setItem('hospitals', JSON.stringify(hospitals));
        }
    }

    static getStatus(available, total) {
        if (available === 0) return 'full';
        if (available < total * 0.2) return 'limited';
        return 'available';
    }
}

// ===================================
// Form Validation
// ===================================
class FormValidator {
    static validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    static validatePhone(phone) {
        const phoneRegex = /^[\d\s\-\+\(\)]{10,}$/;
        return phoneRegex.test(phone);
    }

    static validateSearchInput(input) {
        return input.trim().length >= 2;
    }
}

// ===================================
// Local Storage Helpers
// ===================================
const StorageManager = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('Storage error:', e);
            return false;
        }
    },

    get: function(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.error('Storage error:', e);
            return null;
        }
    },

    remove: function(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (e) {
            console.error('Storage error:', e);
            return false;
        }
    },

    clear: function() {
        try {
            localStorage.clear();
            return true;
        } catch (e) {
            console.error('Storage error:', e);
            return false;
        }
    }
};

// ===================================
// Analytics Tracking (Mock)
// ===================================
class AnalyticsTracker {
    static trackPageView(pageName) {
        console.log(`Page viewed: ${pageName}`);
    }

    static trackEvent(eventName, eventData = {}) {
        console.log(`Event tracked: ${eventName}`, eventData);
    }

    static trackSearch(query) {
        this.trackEvent('search', { query });
    }

    static trackHospitalView(hospitalId) {
        this.trackEvent('hospital_view', { hospitalId });
    }

    static trackBooking(hospitalId, bedType) {
        this.trackEvent('bed_booking', { hospitalId, bedType });
    }
}

// ===================================
// Print Functionality
// ===================================
function printDirections() {
    window.print();
}

// ===================================
// Export Data
// ===================================
function exportReservationAsCSV(reservation) {
    const headers = ['Reservation ID', 'Hospital ID', 'Bed Type', 'Timestamp', 'Duration'];
    const values = [
        reservation.id,
        reservation.hospitalId,
        reservation.bedType,
        new Date(reservation.timestamp).toLocaleString(),
        reservation.duration
    ];

    const csv = [headers, values].map(row => row.join(',')).join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reservation-${reservation.id}.csv`;
    a.click();
}

// ===================================
// Initialize on Page Load
// ===================================
window.addEventListener('load', function() {
    // Track page view
    const pageName = document.title;
    AnalyticsTracker.trackPageView(pageName);

    // Check for expired reservations
    const reservationManager = new ReservationManager();
    reservationManager.removeExpiredReservations();
});

// ===================================
// Service Worker Registration (Optional)
// ===================================
if ('serviceWorker' in navigator) {
    // Uncomment to enable service worker for offline functionality
    // navigator.serviceWorker.register('sw.js').catch(err => console.log('SW registration failed'));
}
