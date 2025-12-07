/**
 * Client-side Fingerprinting & Analytics
 * 
 * Why: Coleta fingerprint único do browser para identificação
 *      de visitantes anônimos e tracking de analytics.
 * 
 * How: Combina múltiplas características do browser/dispositivo
 *      para criar um identificador único sem cookies.
 */

(function() {
    'use strict';

    const Analytics = {
        visitorId: null,
        sessionId: null,
        initialized: false,
        pageLoadTime: null,
        
        /**
         * Initialize analytics
         */
        async init() {
            if (this.initialized) return;
            
            this.pageLoadTime = Date.now();
            
            // Check if we should track (respect DNT)
            if (navigator.doNotTrack === '1') {
                console.debug('Analytics: DNT enabled, minimal tracking');
            }
            
            try {
                // Collect fingerprint
                const fingerprint = await this.collectFingerprint();
                
                // Identify visitor
                const response = await this.identify(fingerprint);
                
                if (response) {
                    this.visitorId = response.visitor_id;
                    this.sessionId = response.session_id;
                    
                    // Store in cookie for subsequent requests
                    this.setCookie('_visitor_id', this.visitorId, 365);
                    
                    // Track initial pageview
                    this.trackPageview();
                    
                    // Setup event listeners
                    this.setupEventListeners();
                }
                
                this.initialized = true;
            } catch (err) {
                console.debug('Analytics init error:', err);
            }
        },
        
        /**
         * Collect browser fingerprint data
         */
        async collectFingerprint() {
            const fp = {
                // Screen
                screen_width: screen.width,
                screen_height: screen.height,
                viewport_width: window.innerWidth,
                viewport_height: window.innerHeight,
                color_depth: screen.colorDepth,
                pixel_ratio: window.devicePixelRatio || 1,
                
                // Timezone/Language
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                timezone_offset: new Date().getTimezoneOffset(),
                language: navigator.language,
                
                // Features
                has_touch: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
                has_cookies: navigator.cookieEnabled,
                has_local_storage: this.hasLocalStorage(),
                has_session_storage: this.hasSessionStorage(),
                
                // Connection
                connection_type: this.getConnectionType(),
            };
            
            // WebGL fingerprint
            const webgl = this.getWebGLInfo();
            fp.has_webgl = webgl.supported;
            fp.webgl_vendor = webgl.vendor;
            fp.webgl_renderer = webgl.renderer;
            
            // Canvas fingerprint
            fp.canvas_hash = await this.getCanvasHash();
            
            // Audio fingerprint
            fp.audio_hash = await this.getAudioHash();
            
            // Fonts fingerprint
            fp.fonts_hash = this.getFontsHash();
            
            // Plugins hash
            fp.plugins_hash = this.getPluginsHash();
            
            return fp;
        },
        
        /**
         * Check localStorage availability
         */
        hasLocalStorage() {
            try {
                localStorage.setItem('_test', '1');
                localStorage.removeItem('_test');
                return true;
            } catch {
                return false;
            }
        },
        
        /**
         * Check sessionStorage availability
         */
        hasSessionStorage() {
            try {
                sessionStorage.setItem('_test', '1');
                sessionStorage.removeItem('_test');
                return true;
            } catch {
                return false;
            }
        },
        
        /**
         * Get connection type
         */
        getConnectionType() {
            const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
            return conn ? conn.effectiveType : null;
        },
        
        /**
         * Get WebGL info
         */
        getWebGLInfo() {
            try {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                
                if (!gl) {
                    return { supported: false, vendor: null, renderer: null };
                }
                
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                
                return {
                    supported: true,
                    vendor: debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : null,
                    renderer: debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : null,
                };
            } catch {
                return { supported: false, vendor: null, renderer: null };
            }
        },
        
        /**
         * Generate canvas fingerprint hash
         */
        async getCanvasHash() {
            try {
                const canvas = document.createElement('canvas');
                canvas.width = 200;
                canvas.height = 50;
                
                const ctx = canvas.getContext('2d');
                if (!ctx) return null;
                
                // Draw text with various styles
                ctx.textBaseline = 'top';
                ctx.font = '14px Arial';
                ctx.fillStyle = '#f60';
                ctx.fillRect(0, 0, 100, 50);
                ctx.fillStyle = '#069';
                ctx.fillText('Canvas FP 🎨', 2, 15);
                ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
                ctx.fillText('Canvas FP 🎨', 4, 17);
                
                const dataUrl = canvas.toDataURL();
                return await this.hashString(dataUrl);
            } catch {
                return null;
            }
        },
        
        /**
         * Generate audio fingerprint hash
         */
        async getAudioHash() {
            try {
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                if (!AudioContext) return null;
                
                const context = new AudioContext();
                const oscillator = context.createOscillator();
                const analyser = context.createAnalyser();
                const gain = context.createGain();
                const processor = context.createScriptProcessor(4096, 1, 1);
                
                gain.gain.value = 0; // Mute
                oscillator.type = 'triangle';
                oscillator.connect(analyser);
                analyser.connect(processor);
                processor.connect(gain);
                gain.connect(context.destination);
                
                oscillator.start(0);
                
                return new Promise((resolve) => {
                    processor.onaudioprocess = (e) => {
                        const data = e.inputBuffer.getChannelData(0);
                        const slice = Array.from(data.slice(0, 100));
                        
                        oscillator.disconnect();
                        processor.disconnect();
                        gain.disconnect();
                        context.close();
                        
                        this.hashString(JSON.stringify(slice)).then(resolve);
                    };
                    
                    // Timeout fallback
                    setTimeout(() => resolve(null), 1000);
                });
            } catch {
                return null;
            }
        },
        
        /**
         * Generate fonts fingerprint hash
         */
        getFontsHash() {
            // List of fonts to test
            const testFonts = [
                'Arial', 'Verdana', 'Times New Roman', 'Courier New', 'Georgia',
                'Comic Sans MS', 'Impact', 'Trebuchet MS', 'Palatino Linotype',
                'Lucida Console', 'Tahoma', 'Segoe UI', 'Roboto', 'Open Sans'
            ];
            
            const baseFonts = ['monospace', 'sans-serif', 'serif'];
            const testString = 'mmmmmmmmmmlli';
            const testSize = '72px';
            
            const span = document.createElement('span');
            span.style.position = 'absolute';
            span.style.left = '-9999px';
            span.style.fontSize = testSize;
            span.innerHTML = testString;
            document.body.appendChild(span);
            
            const baseWidths = {};
            baseFonts.forEach(font => {
                span.style.fontFamily = font;
                baseWidths[font] = span.offsetWidth;
            });
            
            const detected = [];
            testFonts.forEach(font => {
                for (const baseFont of baseFonts) {
                    span.style.fontFamily = `'${font}', ${baseFont}`;
                    if (span.offsetWidth !== baseWidths[baseFont]) {
                        detected.push(font);
                        break;
                    }
                }
            });
            
            document.body.removeChild(span);
            
            // Simple hash of detected fonts
            return detected.join(',').split('').reduce((a, b) => {
                a = ((a << 5) - a) + b.charCodeAt(0);
                return a & a;
            }, 0).toString(16);
        },
        
        /**
         * Generate plugins fingerprint hash
         */
        getPluginsHash() {
            const plugins = Array.from(navigator.plugins || [])
                .map(p => `${p.name}|${p.filename}`)
                .join(',');
            
            return plugins.split('').reduce((a, b) => {
                a = ((a << 5) - a) + b.charCodeAt(0);
                return a & a;
            }, 0).toString(16);
        },
        
        /**
         * Hash a string using SHA-256
         */
        async hashString(str) {
            const encoder = new TextEncoder();
            const data = encoder.encode(str);
            const hashBuffer = await crypto.subtle.digest('SHA-256', data);
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        },
        
        /**
         * Identify visitor with server
         */
        async identify(fingerprint) {
            try {
                const response = await fetch('/api/v1/analytics/identify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ fingerprint }),
                    credentials: 'same-origin',
                });
                
                if (response.ok) {
                    return await response.json();
                }
            } catch (err) {
                console.debug('Identify error:', err);
            }
            return null;
        },
        
        /**
         * Track a pageview
         */
        trackPageview() {
            this.track('page_view', {
                page_url: window.location.href,
                page_title: document.title,
                referrer_url: document.referrer || null,
            });
        },
        
        /**
         * Track an event
         */
        async track(eventType, data = {}) {
            if (!this.initialized && eventType !== 'page_view') return;
            
            const payload = {
                event_type: eventType,
                page_url: data.page_url || window.location.href,
                page_title: data.page_title || document.title,
                referrer_url: data.referrer_url,
                event_data: data.event_data || {},
                scroll_depth: data.scroll_depth,
                time_on_page: data.time_on_page,
            };
            
            try {
                // Use sendBeacon for reliability (especially on page unload)
                const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
                
                if (navigator.sendBeacon) {
                    navigator.sendBeacon('/api/v1/analytics/track', blob);
                } else {
                    await fetch('/api/v1/analytics/track', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload),
                        keepalive: true,
                    });
                }
            } catch (err) {
                console.debug('Track error:', err);
            }
        },
        
        /**
         * Track click event
         */
        trackClick(element, eventData = {}) {
            this.track('click', {
                event_data: {
                    element_id: element.id,
                    element_class: element.className,
                    element_text: element.textContent?.substring(0, 100),
                    element_href: element.href,
                    ...eventData,
                },
            });
        },
        
        /**
         * Setup event listeners for automatic tracking
         */
        setupEventListeners() {
            // Track scroll depth
            let maxScrollDepth = 0;
            window.addEventListener('scroll', this.debounce(() => {
                const scrollTop = window.scrollY;
                const docHeight = document.documentElement.scrollHeight - window.innerHeight;
                const scrollPercent = Math.round((scrollTop / docHeight) * 100);
                
                if (scrollPercent > maxScrollDepth) {
                    maxScrollDepth = scrollPercent;
                }
            }, 250));
            
            // Track time on page and scroll depth on page unload
            window.addEventListener('beforeunload', () => {
                const timeOnPage = Math.round((Date.now() - this.pageLoadTime) / 1000);
                
                this.track('page_view', {
                    event_data: { action: 'exit' },
                    scroll_depth: maxScrollDepth,
                    time_on_page: timeOnPage,
                });
            });
            
            // Track outbound links
            document.addEventListener('click', (e) => {
                const link = e.target.closest('a[href]');
                if (!link) return;
                
                const href = link.href;
                const isExternal = href && !href.startsWith(window.location.origin);
                
                if (isExternal) {
                    this.track('click', {
                        event_data: {
                            type: 'outbound_link',
                            url: href,
                            text: link.textContent?.substring(0, 100),
                        },
                    });
                }
            });
            
            // Track share button clicks
            document.addEventListener('click', (e) => {
                const shareBtn = e.target.closest('[data-action="share"], [data-action="copy"]');
                if (shareBtn) {
                    this.track('share', {
                        event_data: {
                            action: shareBtn.dataset.action,
                            url: shareBtn.dataset.url,
                        },
                    });
                }
            });
        },
        
        /**
         * Debounce utility
         */
        debounce(func, wait) {
            let timeout;
            return (...args) => {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        },
        
        /**
         * Set cookie
         */
        setCookie(name, value, days) {
            const expires = new Date(Date.now() + days * 864e5).toUTCString();
            document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
        },
        
        /**
         * Get cookie
         */
        getCookie(name) {
            const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
            return match ? decodeURIComponent(match[2]) : null;
        },
    };
    
    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => Analytics.init());
    } else {
        Analytics.init();
    }
    
    // Expose for manual use
    window.Analytics = Analytics;
    
})();
