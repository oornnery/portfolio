/**
 * App JavaScript - Main application scripts
 * 
 * Why: Centraliza scripts da aplicação em um arquivo separado,
 *      melhorando organização e cache do browser.
 */

(function() {
    'use strict';

    function setCurrentYear() {
        const year = String(new Date().getFullYear());
        document.querySelectorAll('[data-current-year]').forEach((node) => {
            node.textContent = year;
        });
    }

    /**
     * HTMX Configuration
     */
    function initHtmx() {
        // Add CSRF token to all HTMX requests
        document.body.addEventListener('htmx:configRequest', (event) => {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
            if (csrfToken) {
                event.detail.headers['X-CSRF-Token'] = csrfToken;
            }
        });

        // Handle HTMX errors
        document.body.addEventListener('htmx:responseError', (event) => {
            console.error('HTMX error:', event.detail);
        });

        // Log HTMX requests in development
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            document.body.addEventListener('htmx:beforeRequest', (event) => {
                console.debug('HTMX request:', event.detail);
            });
        }
    }

    /**
     * Scroll Animation Observer
     * Adds 'visible' class to elements when they enter viewport
     */
    function initScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    // Optionally unobserve after animation
                    // observer.unobserve(entry.target);
                }
            });
        }, { 
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        // Observe elements with animation classes
        const animatedElements = document.querySelectorAll(
            '.snap-section, .animate-on-scroll, [data-animate]'
        );
        
        animatedElements.forEach(el => {
            observer.observe(el);
        });
    }

    /**
     * Theme Toggle (if needed in future)
     */
    function initTheme() {
        // Check for saved theme preference or system preference
        const savedTheme = localStorage.getItem('theme');
        const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme === 'dark' || (!savedTheme && systemDark)) {
            document.documentElement.classList.add('dark');
        }
    }

    /**
     * Mobile Menu Toggle
     */
    function initMobileMenu() {
        const menuButton = document.querySelector('[data-menu-toggle]');
        const mobileMenu = document.querySelector('[data-mobile-menu]');
        
        if (menuButton && mobileMenu) {
            const menuIcon = menuButton.querySelector('.menu-icon');
            const closeIcon = menuButton.querySelector('.close-icon');
            
            menuButton.addEventListener('click', () => {
                const isHidden = mobileMenu.classList.toggle('hidden');
                menuButton.setAttribute('aria-expanded', !isHidden);
                
                // Toggle icons
                if (menuIcon && closeIcon) {
                    menuIcon.classList.toggle('hidden', !isHidden);
                    closeIcon.classList.toggle('hidden', isHidden);
                }
            });
            
            // Close menu when clicking on a link
            mobileMenu.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    mobileMenu.classList.add('hidden');
                    menuButton.setAttribute('aria-expanded', 'false');
                    if (menuIcon && closeIcon) {
                        menuIcon.classList.remove('hidden');
                        closeIcon.classList.add('hidden');
                    }
                });
            });
            
            // Close menu on window resize to desktop
            window.addEventListener('resize', () => {
                if (window.innerWidth >= 768) {
                    mobileMenu.classList.add('hidden');
                    menuButton.setAttribute('aria-expanded', 'false');
                    if (menuIcon && closeIcon) {
                        menuIcon.classList.remove('hidden');
                        closeIcon.classList.add('hidden');
                    }
                }
            });
        }
    }

    /**
     * Smooth Scroll for anchor links
     */
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                if (targetId === '#') return;
                
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    /**
     * Confirm Delete Forms
     * Handles forms with data-confirm attribute
     */
    function initConfirmForms() {
        document.addEventListener('submit', function(e) {
            const form = e.target.closest('form[data-confirm]');
            if (form) {
                const message = form.dataset.confirm || 'Are you sure?';
                if (!confirm(message)) {
                    e.preventDefault();
                }
            }
        });
    }

    /**
     * Confirm Buttons/Links
     * Handles elements with data-confirm-action attribute
     */
    function initConfirmActions() {
        document.addEventListener('click', function(e) {
            const element = e.target.closest('[data-confirm-action]');
            if (element) {
                const message = element.dataset.confirmAction || 'Are you sure?';
                if (!confirm(message)) {
                    e.preventDefault();
                    e.stopPropagation();
                }
            }
        });
    }

    /**
     * Scroll Snap Navigation
     * Keyboard navigation and scroll indicator click handling
     */
    function initScrollSnapNav() {
        const container = document.querySelector('.scroll-snap-container');
        if (!container) return;

        const sections = container.querySelectorAll('.snap-section');
        if (sections.length === 0) return;

        let currentSection = 0;

        // Update current section based on scroll position
        function updateCurrentSection() {
            const scrollTop = container.scrollTop;
            const viewportHeight = container.clientHeight;
            currentSection = Math.round(scrollTop / viewportHeight);
        }

        // Scroll to specific section
        function scrollToSection(index) {
            if (index < 0 || index >= sections.length) return;
            sections[index].scrollIntoView({ behavior: 'smooth' });
            currentSection = index;
        }

        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
            // Only handle if scroll container is in view
            if (!container.matches(':hover') && document.activeElement.tagName !== 'BODY') return;
            
            // Ignore if user is typing in an input
            if (e.target.matches('input, textarea, select')) return;

            updateCurrentSection();

            switch(e.key) {
                case 'ArrowDown':
                case 'PageDown':
                    e.preventDefault();
                    scrollToSection(currentSection + 1);
                    break;
                case 'ArrowUp':
                case 'PageUp':
                    e.preventDefault();
                    scrollToSection(currentSection - 1);
                    break;
                case 'Home':
                    e.preventDefault();
                    scrollToSection(0);
                    break;
                case 'End':
                    e.preventDefault();
                    scrollToSection(sections.length - 1);
                    break;
            }
        });

        // Click on scroll indicator to go to next section
        container.querySelectorAll('.scroll-indicator').forEach(indicator => {
            indicator.style.cursor = 'pointer';
            indicator.addEventListener('click', function() {
                updateCurrentSection();
                scrollToSection(currentSection + 1);
            });
        });

        // Update section on scroll end
        container.addEventListener('scroll', debounce(updateCurrentSection, 100));
    }

    /**
     * Debounce utility
     */
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    /**
     * Initialize all modules
     */
    function init() {
        setCurrentYear();
        initHtmx();
        initScrollAnimations();
        initTheme();
        initMobileMenu();
        initSmoothScroll();
        initConfirmForms();
        initConfirmActions();
        initScrollSnapNav();
        initShareDropdowns();
    }

    /**
     * Share Dropdowns - Handle share button dropdowns
     */
    function initShareDropdowns() {
        // Show native share button if supported
        if (navigator.share) {
            document.querySelectorAll('.share-native-btn').forEach(btn => {
                btn.style.display = 'flex';
            });
        }
        
        // Handle dropdown toggles
        document.querySelectorAll('[data-share-toggle]').forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.stopPropagation();
                const dropdown = this.closest('[data-share-dropdown]');
                const menu = dropdown.querySelector('[data-share-menu]');
                const chevron = dropdown.querySelector('.share-chevron');
                const isOpen = !menu.classList.contains('hidden');
                
                // Close all other dropdowns first
                closeAllShareDropdowns();
                
                if (!isOpen) {
                    menu.classList.remove('hidden');
                    chevron?.classList.add('rotate-180');
                    this.setAttribute('aria-expanded', 'true');
                }
            });
        });
        
        // Handle dropdown actions
        document.addEventListener('click', function(e) {
            const actionBtn = e.target.closest('[data-action]');
            if (!actionBtn) {
                // Close dropdowns when clicking outside
                closeAllShareDropdowns();
                return;
            }
            
            const action = actionBtn.dataset.action;
            
            switch(action) {
                case 'copy':
                    handleCopyAction(actionBtn);
                    break;
                case 'share':
                    handleShareAction(actionBtn);
                    break;
                case 'print':
                    window.print();
                    break;
            }
            
            // Close dropdown after action
            closeAllShareDropdowns();
        });
        
        // Close on Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeAllShareDropdowns();
            }
        });
    }
    
    function closeAllShareDropdowns() {
        document.querySelectorAll('[data-share-dropdown]').forEach(dropdown => {
            const menu = dropdown.querySelector('[data-share-menu]');
            const toggle = dropdown.querySelector('[data-share-toggle]');
            const chevron = dropdown.querySelector('.share-chevron');
            
            menu?.classList.add('hidden');
            chevron?.classList.remove('rotate-180');
            toggle?.setAttribute('aria-expanded', 'false');
        });
    }
    
    function handleCopyAction(button) {
        const url = button.dataset.url || window.location.href;
        const textSpan = button.querySelector('.copy-text');
        
        navigator.clipboard.writeText(url).then(() => {
            const originalText = textSpan?.textContent || 'Copy link';
            if (textSpan) {
                textSpan.textContent = 'Copied!';
            }
            button.classList.add('text-green-400');
            
            setTimeout(() => {
                if (textSpan) textSpan.textContent = originalText;
                button.classList.remove('text-green-400');
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy:', err);
        });
    }
    
    function handleShareAction(button) {
        const url = button.dataset.url || window.location.href;
        const title = button.dataset.title || document.title;
        const description = button.dataset.description || '';
        
        if (navigator.share) {
            navigator.share({
                title: title,
                text: description,
                url: url
            }).catch(err => {
                if (err.name !== 'AbortError') {
                    console.error('Share failed:', err);
                }
            });
        }
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose for manual re-initialization if needed (e.g., after HTMX swap)
    window.App = {
        init,
        initScrollAnimations,
        initMobileMenu
    };

})();

/**
 * Copy post link to clipboard
 */
function copyPostLink(button) {
    const url = button.dataset.url || window.location.href;
    const textSpan = button.querySelector('.copy-text');
    
    navigator.clipboard.writeText(url).then(() => {
        // Success feedback
        const originalText = textSpan.textContent;
        textSpan.textContent = 'Copied!';
        button.classList.add('text-green-400', 'border-green-600');
        
        setTimeout(() => {
            textSpan.textContent = originalText;
            button.classList.remove('text-green-400', 'border-green-600');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        textSpan.textContent = 'Failed';
        setTimeout(() => {
            textSpan.textContent = 'Copy Link';
        }, 2000);
    });
}

/**
 * Share post using Web Share API
 */
function sharePost(title, description, url) {
    if (navigator.share) {
        navigator.share({
            title: title,
            text: description,
            url: url
        }).catch(err => {
            if (err.name !== 'AbortError') {
                console.error('Share failed:', err);
            }
        });
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(url);
    }
}

/**
 * Generate PDF from resume
 */
function generateResumePDF() {
    window.print();
}
