/**
 * SellBuddy Analytics Integration
 * Google Analytics 4 and Facebook Pixel setup
 */

(function() {
    'use strict';

    // Configuration - Replace with your actual IDs
    // These can be set via environment or updated directly
    window.GA_MEASUREMENT_ID = 'G-XXXXXXXXXX'; // Replace with your GA4 ID
    window.FB_PIXEL_ID = 'XXXXXXXXXXXXXXX'; // Replace with your FB Pixel ID

    /**
     * Track page view
     */
    function trackPageView(pagePath, pageTitle) {
        // Google Analytics
        if (window.gtag) {
            gtag('event', 'page_view', {
                page_path: pagePath || window.location.pathname,
                page_title: pageTitle || document.title
            });
        }

        // Facebook Pixel
        if (window.fbq) {
            fbq('track', 'PageView');
        }
    }

    /**
     * Track product view
     */
    function trackProductView(product) {
        // Google Analytics
        if (window.gtag) {
            gtag('event', 'view_item', {
                currency: 'USD',
                value: product.price,
                items: [{
                    item_id: product.id,
                    item_name: product.name,
                    item_category: product.category,
                    price: product.price,
                    quantity: 1
                }]
            });
        }

        // Facebook Pixel
        if (window.fbq) {
            fbq('track', 'ViewContent', {
                content_ids: [product.id],
                content_name: product.name,
                content_type: 'product',
                value: product.price,
                currency: 'USD'
            });
        }
    }

    /**
     * Track add to cart
     */
    function trackAddToCart(product, quantity) {
        // Google Analytics
        if (window.gtag) {
            gtag('event', 'add_to_cart', {
                currency: 'USD',
                value: product.price * quantity,
                items: [{
                    item_id: product.id,
                    item_name: product.name,
                    item_category: product.category,
                    price: product.price,
                    quantity: quantity
                }]
            });
        }

        // Facebook Pixel
        if (window.fbq) {
            fbq('track', 'AddToCart', {
                content_ids: [product.id],
                content_name: product.name,
                content_type: 'product',
                value: product.price * quantity,
                currency: 'USD'
            });
        }
    }

    /**
     * Track begin checkout
     */
    function trackBeginCheckout(cart) {
        const value = cart.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);

        // Google Analytics
        if (window.gtag) {
            gtag('event', 'begin_checkout', {
                currency: 'USD',
                value: value,
                items: cart.items.map(item => ({
                    item_id: item.id,
                    item_name: item.name,
                    price: item.price,
                    quantity: item.quantity
                }))
            });
        }

        // Facebook Pixel
        if (window.fbq) {
            fbq('track', 'InitiateCheckout', {
                content_ids: cart.items.map(item => item.id),
                num_items: cart.items.reduce((sum, item) => sum + item.quantity, 0),
                value: value,
                currency: 'USD'
            });
        }
    }

    /**
     * Track purchase
     */
    function trackPurchase(order) {
        // Google Analytics
        if (window.gtag) {
            gtag('event', 'purchase', {
                transaction_id: order.id,
                value: order.total,
                currency: 'USD',
                shipping: order.shipping || 0,
                tax: order.tax || 0,
                items: order.items.map(item => ({
                    item_id: item.id,
                    item_name: item.name,
                    price: item.price,
                    quantity: item.quantity
                }))
            });
        }

        // Facebook Pixel
        if (window.fbq) {
            fbq('track', 'Purchase', {
                content_ids: order.items.map(item => item.id),
                content_type: 'product',
                num_items: order.items.reduce((sum, item) => sum + item.quantity, 0),
                value: order.total,
                currency: 'USD'
            });
        }
    }

    /**
     * Track newsletter signup
     */
    function trackNewsletterSignup(email) {
        // Google Analytics
        if (window.gtag) {
            gtag('event', 'sign_up', {
                method: 'newsletter'
            });
        }

        // Facebook Pixel
        if (window.fbq) {
            fbq('track', 'Lead', {
                content_name: 'newsletter_signup'
            });
        }
    }

    /**
     * Track search
     */
    function trackSearch(searchTerm) {
        // Google Analytics
        if (window.gtag) {
            gtag('event', 'search', {
                search_term: searchTerm
            });
        }

        // Facebook Pixel
        if (window.fbq) {
            fbq('track', 'Search', {
                search_string: searchTerm
            });
        }
    }

    /**
     * Track custom event
     */
    function trackEvent(eventName, params) {
        // Google Analytics
        if (window.gtag) {
            gtag('event', eventName, params);
        }

        // Facebook Pixel custom event
        if (window.fbq) {
            fbq('trackCustom', eventName, params);
        }
    }

    // Public API
    window.SellBuddyAnalytics = {
        trackPageView,
        trackProductView,
        trackAddToCart,
        trackBeginCheckout,
        trackPurchase,
        trackNewsletterSignup,
        trackSearch,
        trackEvent
    };

    // Auto-track page views
    document.addEventListener('DOMContentLoaded', function() {
        trackPageView();
    });

    // Listen for Snipcart events
    document.addEventListener('snipcart.ready', function() {
        Snipcart.events.on('item.added', function(item) {
            trackAddToCart({
                id: item.uniqueId,
                name: item.name,
                price: item.price,
                category: 'Products'
            }, item.quantity);
        });

        Snipcart.events.on('cart.opened', function() {
            const cart = Snipcart.store.getState().cart;
            if (cart.items.count > 0) {
                trackBeginCheckout({
                    items: cart.items.items.map(item => ({
                        id: item.uniqueId,
                        name: item.name,
                        price: item.price,
                        quantity: item.quantity
                    }))
                });
            }
        });

        Snipcart.events.on('order.completed', function(order) {
            trackPurchase({
                id: order.token,
                total: order.total,
                shipping: order.shippingInformation?.cost || 0,
                tax: order.taxesTotal || 0,
                items: order.items.items.map(item => ({
                    id: item.uniqueId,
                    name: item.name,
                    price: item.price,
                    quantity: item.quantity
                }))
            });
        });
    });
})();
