/**
 * App JavaScript - Main application scripts
 * 
 * Why: Centraliza scripts da aplicação em um arquivo separado,
 *      melhorando organização e cache do browser.
 */

(function() {
    'use strict';

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
            menuButton.addEventListener('click', () => {
                mobileMenu.classList.toggle('hidden');
                menuButton.setAttribute(
                    'aria-expanded', 
                    mobileMenu.classList.contains('hidden') ? 'false' : 'true'
                );
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
        initHtmx();
        initScrollAnimations();
        initTheme();
        initMobileMenu();
        initSmoothScroll();
        initConfirmForms();
        initConfirmActions();
        initScrollSnapNav();
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
