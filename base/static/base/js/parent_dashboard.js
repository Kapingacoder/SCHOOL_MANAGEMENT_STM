// Parent Dashboard - Core Functionality

// Global function to initialize the dashboard
window.initParentDashboard = function() {
    try {
        // Initialize core components
        initThemeSwitcher();
        initNavigation();
        initDashboardCards();
        initMobileNavigation();
        
        // Set current date in the header
        updateCurrentDate();
        
        // Hide loading overlay
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            setTimeout(() => {
                loadingOverlay.style.display = 'none';
            }, 300);
        }
        
        console.log('Parent dashboard initialized successfully');
    } catch (error) {
        console.error('Error initializing parent dashboard:', error);
        if (window.console && window.console.error) {
            window.console.error(error);
        }
    }
};

// Initialize when DOM is fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initParentDashboard);
} else {
    window.initParentDashboard();
}

// Initialize dashboard card interactions
function initDashboardCards() {
    const cards = document.querySelectorAll('.dashboard-card');
    
    cards.forEach(card => {
        card.addEventListener('click', function() {
            const section = this.getAttribute('data-section');
            if (section) {
                loadSection(section);
                updateActiveCard(this);
                
                // Update URL hash without page reload
                window.history.pushState({}, '', `#${section}`);
                
                // Close mobile menu if open
                document.body.classList.remove('menu-open');
            }
        });
        
        // Add hover effect
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
}

// Initialize mobile navigation
function initMobileNavigation() {
    const navItems = document.querySelectorAll('.bottom-nav .nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            if (section) {
                // Update active state
                navItems.forEach(nav => nav.classList.remove('active'));
                this.classList.add('active');
                
                // Load the section
                loadSection(section);
                
                // Scroll to top
                window.scrollTo(0, 0);
            }
        });
    });
    
    // Show/hide bottom nav based on scroll
    let lastScrollTop = 0;
    const bottomNav = document.getElementById('bottomNav');
    
    if (bottomNav) {
        window.addEventListener('scroll', function() {
            const st = window.pageYOffset || document.documentElement.scrollTop;
            
            if (st > lastScrollTop) {
                // Scrolling down
                bottomNav.style.transform = 'translateY(100%)';
            } else {
                // Scrolling up
                bottomNav.style.transform = 'translateY(0)';
            }
            
            lastScrollTop = st <= 0 ? 0 : st;
        }, { passive: true });
    }
}

// Initialize theme switcher
function initThemeSwitcher() {
    const themeToggle = document.getElementById('themeToggle');
    
    // Check for saved theme preference or use system preference
    const savedTheme = localStorage.getItem('theme') || 
                      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    
    // Apply the saved theme
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        if (themeToggle) {
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            themeToggle.setAttribute('title', 'Switch to Light Mode');
        }
    }
    
    // Toggle theme when button is clicked
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const isDarkMode = document.body.classList.toggle('dark-mode');
            
            // Update button icon and save preference
            if (isDarkMode) {
                themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
                themeToggle.setAttribute('title', 'Switch to Light Mode');
                localStorage.setItem('theme', 'dark');
            } else {
                themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
                themeToggle.setAttribute('title', 'Switch to Dark Mode');
                localStorage.setItem('theme', 'light');
            }
        });
    }
}

// Initialize navigation between sections
function initNavigation() {
    // Handle initial load with hash
    const initialSection = window.location.hash.substring(1) || 'overview';
    loadSection(initialSection);
    updateActiveCard(document.querySelector(`[data-section="${initialSection}"]`));
    
    // Handle back/forward navigation
    window.addEventListener('popstate', function() {
        const section = window.location.hash.substring(1) || 'overview';
        loadSection(section);
        updateActiveCard(document.querySelector(`[data-section="${section}"]`));
    });
    
    // Listen for section changes from other components
    document.addEventListener('sectionChange', function(e) {
        const section = e.detail.section;
        loadSection(section);
        updateActiveCard(document.querySelector(`[data-section="${section}"]`));
    });
}

// Load section content dynamically
function loadSection(section) {
    const contentArea = document.getElementById('contentArea');
    const loadingOverlay = document.getElementById('loadingOverlay');
    
    if (!contentArea) return;
    
    // Show loading overlay
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }
    
    // Update URL hash without page reload
    if (window.location.hash.substring(1) !== section) {
        window.history.pushState({}, '', `#${section}`);
    }
    
    // Determine the API endpoint based on the section
    let apiUrl = `/api/parent/${section}/`;
    
    // Make AJAX call to load section content
    fetch(apiUrl, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Update the content area with the received HTML
        contentArea.innerHTML = data.html || `
            <div class="welcome-screen">
                <i class="fas fa-${getSectionIcon(section)}"></i>
                <h2>${getSectionTitle(section)}</h2>
                <p>${getSectionDescription(section)}</p>
            </div>
        `;
        
        // Initialize any section-specific components
        initSectionComponents(section);
        
        // Update the document title
        document.title = `${getSectionTitle(section)} | Parent Portal`;
    })
    .catch(error => {
        console.error('Error loading section:', error);
        contentArea.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Failed to load ${section}. Please try again later.</p>
            </div>
        `;
    })
    .finally(() => {
        // Hide loading overlay
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
        
        // Scroll to top
        window.scrollTo(0, 0);
        
        // Dispatch event that section has changed
        const event = new CustomEvent('sectionChanged', {
            detail: { section: section }
        });
        document.dispatchEvent(event);
    });
}

// Helper function to get section icon
function getSectionIcon(section) {
    const icons = {
        'overview': 'home',
        'children': 'users',
        'reports': 'chart-line',
        'messages': 'envelope',
        'documents': 'file-alt',
        'payments': 'credit-card',
        'notifications': 'bell',
        'events': 'calendar-alt',
        'settings': 'cog'
    };
    return icons[section] || 'info-circle';
}

// Helper function to get section title
function getSectionTitle(section) {
    const titles = {
        'overview': 'Dashboard Overview',
        'children': 'My Children',
        'reports': 'Academic Reports',
        'messages': 'Messages',
        'documents': 'Documents',
        'payments': 'Payment History',
        'notifications': 'Notifications',
        'events': 'School Events',
        'settings': 'Account Settings'
    };
    return titles[section] || section.charAt(0).toUpperCase() + section.slice(1);
}

// Helper function to get section description
function getSectionDescription(section) {
    const descriptions = {
        'overview': 'Welcome to your parent dashboard',
        'children': 'View and manage your children\'s information',
        'reports': 'Track academic performance and progress',
        'messages': 'Communicate with teachers and staff',
        'documents': 'Access important school documents',
        'payments': 'View and manage school fee payments',
        'notifications': 'Stay updated with school announcements',
        'events': 'View upcoming school events and activities',
        'settings': 'Manage your account preferences'
    };
    return descriptions[section] || `This is the ${section} section`;
}

// Update active card in the dashboard
function updateActiveCard(activeCard) {
    if (!activeCard) return;
    
    // Remove active class from all cards
    document.querySelectorAll('.dashboard-card, .nav-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Add active class to the clicked card
    activeCard.classList.add('active');
    
    // Also update the corresponding bottom nav item
    const section = activeCard.getAttribute('data-section');
    if (section) {
        const navItem = document.querySelector(`.bottom-nav [data-section="${section}"]`);
        if (navItem) {
            navItem.classList.add('active');
        }
    }
}

// Update current date in the header
function updateCurrentDate() {
    const dateElements = document.querySelectorAll('.current-date');
    if (dateElements.length > 0) {
        const options = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        };
        const today = new Date().toLocaleDateString('en-US', options);
        dateElements.forEach(el => {
            el.textContent = today;
        });
    }
}

// Initialize section-specific components
function initSectionComponents(section) {
    switch (section) {
        case 'reports':
            initReportsSection();
            break;
        case 'messages':
            initMessagesSection();
            break;
        case 'documents':
            initDocumentsSection();
            break;
        case 'events':
            initEventsSection();
            break;
        case 'children':
            initChildrenSection();
            break;
        default:
            break;
    }
}

// Initialize search functionality
function initSearch() {
    const searchInput = document.getElementById('globalSearch');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim().toLowerCase();
            
            // In a real app, this would be an AJAX call to search the entire application
            console.log('Searching for:', query);
            
            // You would update the UI with search results here
        });
    }
}

// Initialize modals
function initModals() {
    // Initialize all Bootstrap modals
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modalEl => {
        // Initialize modal
        const modal = new bootstrap.Modal(modalEl);
        
        // Handle modal shown event
        modalEl.addEventListener('shown.bs.modal', function() {
            // Focus the first input in the modal
            const input = this.querySelector('input, textarea, select');
            if (input) input.focus();
        });
        
        // Handle modal hidden event
        modalEl.addEventListener('hidden.bs.modal', function() {
            // Reset form if it exists
            const form = this.querySelector('form');
            if (form) form.reset();
        });
    });
}

// Initialize tooltips
function initTooltips() {
    // Initialize all Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Update unread message count
function updateUnreadCount(change) {
    const unreadCountEl = document.querySelector('.notification-badge');
    const unreadNavItem = document.querySelector('.nav-item[data-section="messages"] .badge');
    
    if (unreadCountEl) {
        let currentCount = parseInt(unreadCountEl.textContent) || 0;
        currentCount += change;
        
        if (currentCount > 0) {
            unreadCountEl.textContent = currentCount;
            unreadCountEl.style.display = 'flex';
            
            if (unreadNavItem) {
                unreadNavItem.textContent = currentCount;
                unreadNavItem.style.display = 'inline-flex';
            }
        } else {
            unreadCountEl.style.display = 'none';
            
            if (unreadNavItem) {
                unreadNavItem.style.display = 'none';
            }
        }
    }
}

// Helper function to format dates
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Helper function to format file sizes
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
