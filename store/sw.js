/**
 * SellBuddy Service Worker
 * Provides offline support and caching
 */

const CACHE_NAME = 'sellbuddy-v1';
const STATIC_CACHE = 'sellbuddy-static-v1';
const DYNAMIC_CACHE = 'sellbuddy-dynamic-v1';

// Assets to cache immediately
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/styles.css',
    '/products.js',
    '/js/performance.js',
    '/js/cookie-consent.js',
    '/404.html',
    '/data/products.json'
];

// Install event - cache static assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Caching static assets');
                return cache.addAll(STATIC_ASSETS.map(url => {
                    return new Request(url, { cache: 'reload' });
                })).catch(err => {
                    console.log('Some assets failed to cache:', err);
                    // Continue even if some assets fail
                    return Promise.resolve();
                });
            })
            .then(() => self.skipWaiting())
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames
                        .filter(name => name !== STATIC_CACHE && name !== DYNAMIC_CACHE)
                        .map(name => caches.delete(name))
                );
            })
            .then(() => self.clients.claim())
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Skip external requests (except CDNs we want to cache)
    if (url.origin !== location.origin) {
        // Allow caching of CDN resources
        if (!url.hostname.includes('snipcart') &&
            !url.hostname.includes('googleapis') &&
            !url.hostname.includes('gstatic')) {
            return;
        }
    }

    // Skip API requests
    if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/backend/')) {
        return;
    }

    // Cache-first for static assets
    if (isStaticAsset(url.pathname)) {
        event.respondWith(cacheFirst(request));
    }
    // Network-first for HTML pages
    else if (request.headers.get('accept')?.includes('text/html')) {
        event.respondWith(networkFirst(request));
    }
    // Stale-while-revalidate for everything else
    else {
        event.respondWith(staleWhileRevalidate(request));
    }
});

/**
 * Check if URL is a static asset
 */
function isStaticAsset(pathname) {
    const staticExtensions = ['.css', '.js', '.woff', '.woff2', '.ttf', '.eot', '.ico', '.svg'];
    return staticExtensions.some(ext => pathname.endsWith(ext));
}

/**
 * Cache-first strategy
 */
async function cacheFirst(request) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }

    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        // Return offline fallback if available
        return caches.match('/404.html');
    }
}

/**
 * Network-first strategy
 */
async function networkFirst(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        // Return offline page
        return caches.match('/404.html');
    }
}

/**
 * Stale-while-revalidate strategy
 */
async function staleWhileRevalidate(request) {
    const cache = await caches.open(DYNAMIC_CACHE);
    const cachedResponse = await cache.match(request);

    const fetchPromise = fetch(request).then(networkResponse => {
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    }).catch(() => cachedResponse);

    return cachedResponse || fetchPromise;
}

// Handle messages from main thread
self.addEventListener('message', event => {
    if (event.data === 'skipWaiting') {
        self.skipWaiting();
    }
    if (event.data === 'clearCache') {
        caches.keys().then(names => {
            names.forEach(name => caches.delete(name));
        });
    }
});
