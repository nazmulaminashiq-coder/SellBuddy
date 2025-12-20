/**
 * SellBuddy Performance Optimizations
 * Lazy loading, image optimization, and caching
 */

(function() {
    'use strict';

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        initLazyLoading();
        initImageOptimization();
        initResourceHints();
        initServiceWorkerCheck();
    }

    /**
     * Lazy Loading for Images
     * Uses Intersection Observer for efficient loading
     */
    function initLazyLoading() {
        // Check for native lazy loading support
        if ('loading' in HTMLImageElement.prototype) {
            // Browser supports native lazy loading
            document.querySelectorAll('img[data-src]').forEach(img => {
                img.src = img.dataset.src;
                img.loading = 'lazy';
                if (img.dataset.srcset) {
                    img.srcset = img.dataset.srcset;
                }
            });
        } else {
            // Fallback to Intersection Observer
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        loadImage(img);
                        observer.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.01
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }

        // Lazy load background images
        const bgObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    if (el.dataset.bg) {
                        el.style.backgroundImage = `url(${el.dataset.bg})`;
                        el.classList.add('bg-loaded');
                    }
                    observer.unobserve(el);
                }
            });
        }, {
            rootMargin: '100px 0px'
        });

        document.querySelectorAll('[data-bg]').forEach(el => {
            bgObserver.observe(el);
        });
    }

    /**
     * Load image from data attributes
     */
    function loadImage(img) {
        img.src = img.dataset.src;
        if (img.dataset.srcset) {
            img.srcset = img.dataset.srcset;
        }
        img.classList.add('loaded');
        delete img.dataset.src;
        delete img.dataset.srcset;
    }

    /**
     * Image Optimization
     * WebP support detection and responsive images
     */
    function initImageOptimization() {
        // Check WebP support
        checkWebPSupport().then(hasWebP => {
            if (hasWebP) {
                document.documentElement.classList.add('webp');
            } else {
                document.documentElement.classList.add('no-webp');
            }
        });

        // Add error handling for broken images
        document.querySelectorAll('img').forEach(img => {
            img.addEventListener('error', handleImageError);
        });
    }

    /**
     * Check WebP Support
     */
    function checkWebPSupport() {
        return new Promise(resolve => {
            const webP = new Image();
            webP.onload = webP.onerror = function() {
                resolve(webP.height === 2);
            };
            webP.src = 'data:image/webp;base64,UklGRjoAAABXRUJQVlA4IC4AAACyAgCdASoCAAIALmk0mk0iIiIiIgBoSygABc6WWgAA/veff/0PP8bA//LwYAAA';
        });
    }

    /**
     * Handle Image Load Errors
     */
    function handleImageError(e) {
        const img = e.target;
        if (!img.dataset.errorHandled) {
            img.dataset.errorHandled = 'true';
            // Set a placeholder image
            img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 300 300"%3E%3Crect fill="%23f0f0f0" width="300" height="300"/%3E%3Ctext fill="%23999" font-family="Arial" font-size="14" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EImage not available%3C/text%3E%3C/svg%3E';
            img.alt = 'Image not available';
        }
    }

    /**
     * Resource Hints
     * Preconnect to important domains
     */
    function initResourceHints() {
        const hints = [
            { rel: 'preconnect', href: 'https://cdn.snipcart.com' },
            { rel: 'preconnect', href: 'https://app.snipcart.com' },
            { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
            { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: true },
            { rel: 'dns-prefetch', href: 'https://www.google-analytics.com' },
            { rel: 'dns-prefetch', href: 'https://connect.facebook.net' }
        ];

        hints.forEach(hint => {
            if (!document.querySelector(`link[rel="${hint.rel}"][href="${hint.href}"]`)) {
                const link = document.createElement('link');
                link.rel = hint.rel;
                link.href = hint.href;
                if (hint.crossorigin) {
                    link.crossOrigin = 'anonymous';
                }
                document.head.appendChild(link);
            }
        });
    }

    /**
     * Service Worker Check
     * Register service worker for caching if available
     */
    function initServiceWorkerCheck() {
        if ('serviceWorker' in navigator) {
            // Only register in production
            if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
                navigator.serviceWorker.register('/sw.js').then(registration => {
                    console.log('ServiceWorker registered:', registration.scope);
                }).catch(error => {
                    // SW not available, continue without it
                    console.log('ServiceWorker not available:', error.message);
                });
            }
        }
    }

    /**
     * Debounce Helper
     */
    window.debounce = function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };

    /**
     * Throttle Helper
     */
    window.throttle = function(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    };

    /**
     * Request Idle Callback Polyfill
     */
    window.requestIdleCallback = window.requestIdleCallback || function(cb) {
        const start = Date.now();
        return setTimeout(function() {
            cb({
                didTimeout: false,
                timeRemaining: function() {
                    return Math.max(0, 50 - (Date.now() - start));
                }
            });
        }, 1);
    };

    /**
     * Defer Non-Critical CSS
     */
    function loadDeferredStyles() {
        document.querySelectorAll('link[data-href]').forEach(link => {
            link.href = link.dataset.href;
        });
    }

    // Load deferred styles after initial paint
    if (window.requestIdleCallback) {
        requestIdleCallback(loadDeferredStyles);
    } else {
        setTimeout(loadDeferredStyles, 100);
    }

})();
