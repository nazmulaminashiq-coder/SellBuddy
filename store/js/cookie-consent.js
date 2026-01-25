/**
 * SellBuddy Cookie Consent Banner
 * GDPR/CCPA compliant cookie consent management
 */

(function() {
    'use strict';

    const CONSENT_KEY = 'sellbuddy_cookie_consent';
    const CONSENT_VERSION = '1.0';

    // Cookie consent configuration
    const config = {
        necessary: true, // Always required
        analytics: false,
        marketing: false,
        preferences: false
    };

    // Check if consent already given
    function hasConsent() {
        const consent = localStorage.getItem(CONSENT_KEY);
        if (!consent) return false;

        try {
            const parsed = JSON.parse(consent);
            return parsed.version === CONSENT_VERSION;
        } catch {
            return false;
        }
    }

    // Get current consent settings
    function getConsent() {
        const consent = localStorage.getItem(CONSENT_KEY);
        if (!consent) return null;

        try {
            return JSON.parse(consent);
        } catch {
            return null;
        }
    }

    // Save consent
    function saveConsent(settings) {
        const consent = {
            version: CONSENT_VERSION,
            timestamp: new Date().toISOString(),
            settings: settings
        };
        localStorage.setItem(CONSENT_KEY, JSON.stringify(consent));

        // Enable/disable scripts based on consent
        applyConsent(settings);

        // Remove banner
        const banner = document.getElementById('cookie-consent-banner');
        if (banner) {
            banner.classList.add('hidden');
            setTimeout(() => banner.remove(), 300);
        }
    }

    // Apply consent settings
    function applyConsent(settings) {
        // Analytics (Google Analytics, etc.)
        if (settings.analytics) {
            enableAnalytics();
        }

        // Marketing (Facebook Pixel, etc.)
        if (settings.marketing) {
            enableMarketing();
        }
    }

    // Enable analytics scripts
    function enableAnalytics() {
        // Google Analytics 4
        if (window.GA_MEASUREMENT_ID) {
            const script = document.createElement('script');
            script.async = true;
            script.src = `https://www.googletagmanager.com/gtag/js?id=${window.GA_MEASUREMENT_ID}`;
            document.head.appendChild(script);

            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', window.GA_MEASUREMENT_ID);
        }
    }

    // Enable marketing scripts
    function enableMarketing() {
        // Facebook Pixel
        if (window.FB_PIXEL_ID) {
            !function(f,b,e,v,n,t,s)
            {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
            n.callMethod.apply(n,arguments):n.queue.push(arguments)};
            if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
            n.queue=[];t=b.createElement(e);t.async=!0;
            t.src=v;s=b.getElementsByTagName(e)[0];
            s.parentNode.insertBefore(t,s)}(window, document,'script',
            'https://connect.facebook.net/en_US/fbevents.js');
            fbq('init', window.FB_PIXEL_ID);
            fbq('track', 'PageView');
        }
    }

    // Create consent banner
    function createBanner() {
        const banner = document.createElement('div');
        banner.id = 'cookie-consent-banner';
        banner.innerHTML = `
            <div class="cookie-consent-container">
                <div class="cookie-consent-content">
                    <div class="cookie-consent-text">
                        <h3>We value your privacy</h3>
                        <p>We use cookies to enhance your browsing experience, analyze site traffic, and personalize content.
                        By clicking "Accept All", you consent to our use of cookies.
                        <a href="privacy.html" target="_blank">Learn more</a></p>
                    </div>
                    <div class="cookie-consent-actions">
                        <button class="cookie-btn cookie-btn-settings" onclick="window.SellBuddyCookies.showSettings()">
                            Customize
                        </button>
                        <button class="cookie-btn cookie-btn-reject" onclick="window.SellBuddyCookies.rejectAll()">
                            Reject All
                        </button>
                        <button class="cookie-btn cookie-btn-accept" onclick="window.SellBuddyCookies.acceptAll()">
                            Accept All
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(banner);

        // Add styles
        addStyles();
    }

    // Create settings modal
    function createSettingsModal() {
        const modal = document.createElement('div');
        modal.id = 'cookie-settings-modal';
        modal.className = 'cookie-modal hidden';
        modal.innerHTML = `
            <div class="cookie-modal-overlay" onclick="window.SellBuddyCookies.hideSettings()"></div>
            <div class="cookie-modal-content">
                <h3>Cookie Settings</h3>
                <p>Manage your cookie preferences below. Necessary cookies are always enabled as they are essential for the website to function.</p>

                <div class="cookie-options">
                    <div class="cookie-option">
                        <div class="cookie-option-header">
                            <label>
                                <input type="checkbox" id="cookie-necessary" checked disabled>
                                <span>Necessary Cookies</span>
                            </label>
                            <span class="cookie-badge">Always Active</span>
                        </div>
                        <p>Essential for the website to function properly. Cannot be disabled.</p>
                    </div>

                    <div class="cookie-option">
                        <div class="cookie-option-header">
                            <label>
                                <input type="checkbox" id="cookie-analytics">
                                <span>Analytics Cookies</span>
                            </label>
                        </div>
                        <p>Help us understand how visitors interact with our website by collecting anonymous information.</p>
                    </div>

                    <div class="cookie-option">
                        <div class="cookie-option-header">
                            <label>
                                <input type="checkbox" id="cookie-marketing">
                                <span>Marketing Cookies</span>
                            </label>
                        </div>
                        <p>Used to track visitors across websites to display relevant advertisements.</p>
                    </div>

                    <div class="cookie-option">
                        <div class="cookie-option-header">
                            <label>
                                <input type="checkbox" id="cookie-preferences">
                                <span>Preference Cookies</span>
                            </label>
                        </div>
                        <p>Allow the website to remember choices you make and provide enhanced features.</p>
                    </div>
                </div>

                <div class="cookie-modal-actions">
                    <button class="cookie-btn cookie-btn-reject" onclick="window.SellBuddyCookies.hideSettings()">
                        Cancel
                    </button>
                    <button class="cookie-btn cookie-btn-accept" onclick="window.SellBuddyCookies.saveSettings()">
                        Save Preferences
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    // Add CSS styles
    function addStyles() {
        if (document.getElementById('cookie-consent-styles')) return;

        const style = document.createElement('style');
        style.id = 'cookie-consent-styles';
        style.textContent = `
            #cookie-consent-banner {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: #1f2937;
                color: #fff;
                z-index: 99999;
                padding: 1rem;
                box-shadow: 0 -4px 20px rgba(0,0,0,0.15);
                animation: slideUp 0.3s ease;
            }
            #cookie-consent-banner.hidden {
                animation: slideDown 0.3s ease forwards;
            }
            @keyframes slideUp {
                from { transform: translateY(100%); }
                to { transform: translateY(0); }
            }
            @keyframes slideDown {
                from { transform: translateY(0); }
                to { transform: translateY(100%); }
            }
            .cookie-consent-container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .cookie-consent-content {
                display: flex;
                align-items: center;
                gap: 2rem;
                flex-wrap: wrap;
            }
            .cookie-consent-text {
                flex: 1;
                min-width: 300px;
            }
            .cookie-consent-text h3 {
                margin: 0 0 0.5rem 0;
                font-size: 1.1rem;
            }
            .cookie-consent-text p {
                margin: 0;
                font-size: 0.9rem;
                color: #9ca3af;
                line-height: 1.5;
            }
            .cookie-consent-text a {
                color: #818cf8;
                text-decoration: underline;
            }
            .cookie-consent-actions {
                display: flex;
                gap: 0.75rem;
                flex-wrap: wrap;
            }
            .cookie-btn {
                padding: 0.75rem 1.5rem;
                border: none;
                border-radius: 8px;
                font-size: 0.9rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .cookie-btn-accept {
                background: #6366f1;
                color: white;
            }
            .cookie-btn-accept:hover {
                background: #4f46e5;
            }
            .cookie-btn-reject {
                background: #374151;
                color: white;
            }
            .cookie-btn-reject:hover {
                background: #4b5563;
            }
            .cookie-btn-settings {
                background: transparent;
                color: #9ca3af;
                border: 1px solid #4b5563;
            }
            .cookie-btn-settings:hover {
                background: #374151;
                color: white;
            }
            .cookie-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: 100000;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .cookie-modal.hidden {
                display: none;
            }
            .cookie-modal-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.5);
            }
            .cookie-modal-content {
                position: relative;
                background: white;
                padding: 2rem;
                border-radius: 16px;
                max-width: 500px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
            }
            .cookie-modal-content h3 {
                margin: 0 0 0.5rem 0;
                color: #1f2937;
            }
            .cookie-modal-content > p {
                color: #6b7280;
                font-size: 0.9rem;
                margin-bottom: 1.5rem;
            }
            .cookie-options {
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }
            .cookie-option {
                padding: 1rem;
                background: #f9fafb;
                border-radius: 8px;
            }
            .cookie-option-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.5rem;
            }
            .cookie-option-header label {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-weight: 600;
                color: #1f2937;
                cursor: pointer;
            }
            .cookie-option-header input {
                width: 18px;
                height: 18px;
                cursor: pointer;
            }
            .cookie-badge {
                font-size: 0.75rem;
                padding: 0.25rem 0.5rem;
                background: #10b981;
                color: white;
                border-radius: 4px;
            }
            .cookie-option p {
                margin: 0;
                font-size: 0.85rem;
                color: #6b7280;
            }
            .cookie-modal-actions {
                display: flex;
                justify-content: flex-end;
                gap: 0.75rem;
                margin-top: 1.5rem;
            }
            @media (max-width: 768px) {
                .cookie-consent-content {
                    flex-direction: column;
                    text-align: center;
                }
                .cookie-consent-actions {
                    width: 100%;
                    justify-content: center;
                }
            }
        `;
        document.head.appendChild(style);
    }

    // Public API
    window.SellBuddyCookies = {
        acceptAll: function() {
            saveConsent({
                necessary: true,
                analytics: true,
                marketing: true,
                preferences: true
            });
        },

        rejectAll: function() {
            saveConsent({
                necessary: true,
                analytics: false,
                marketing: false,
                preferences: false
            });
        },

        showSettings: function() {
            let modal = document.getElementById('cookie-settings-modal');
            if (!modal) {
                createSettingsModal();
                modal = document.getElementById('cookie-settings-modal');
            }
            modal.classList.remove('hidden');
        },

        hideSettings: function() {
            const modal = document.getElementById('cookie-settings-modal');
            if (modal) {
                modal.classList.add('hidden');
            }
        },

        saveSettings: function() {
            const settings = {
                necessary: true,
                analytics: document.getElementById('cookie-analytics').checked,
                marketing: document.getElementById('cookie-marketing').checked,
                preferences: document.getElementById('cookie-preferences').checked
            };
            saveConsent(settings);
            this.hideSettings();
        },

        getConsent: getConsent,

        hasConsent: hasConsent
    };

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        if (!hasConsent()) {
            createBanner();
        } else {
            // Apply existing consent
            const consent = getConsent();
            if (consent && consent.settings) {
                applyConsent(consent.settings);
            }
        }
    });
})();
