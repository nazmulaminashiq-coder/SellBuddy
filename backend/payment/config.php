<?php
/**
 * SellBuddy Payment Gateway Configuration
 *
 * Configure your payment methods here
 */

return [
    // Your store details
    'store' => [
        'name' => 'SellBuddy',
        'url' => 'https://nazmulaminashiq-coder.github.io/SellBuddy/store/',
        'currency' => 'USD',
        'secret_key' => 'YOUR_SECRET_KEY_HERE', // Generate a random string
    ],

    // Snipcart settings
    'snipcart' => [
        'api_key' => 'YOUR_SNIPCART_SECRET_API_KEY',
        'test_mode' => true, // Set to false for production
    ],

    // PayPal Configuration
    'paypal' => [
        'enabled' => true,
        'client_id' => 'YOUR_PAYPAL_CLIENT_ID',
        'client_secret' => 'YOUR_PAYPAL_CLIENT_SECRET',
        'mode' => 'sandbox', // 'sandbox' or 'live'
    ],

    // Bkash Configuration (Bangladesh)
    'bkash' => [
        'enabled' => false,
        'app_key' => 'YOUR_BKASH_APP_KEY',
        'app_secret' => 'YOUR_BKASH_APP_SECRET',
        'username' => 'YOUR_BKASH_USERNAME',
        'password' => 'YOUR_BKASH_PASSWORD',
        'mode' => 'sandbox', // 'sandbox' or 'live'
    ],

    // Stripe Configuration (Alternative)
    'stripe' => [
        'enabled' => false,
        'secret_key' => 'YOUR_STRIPE_SECRET_KEY',
        'publishable_key' => 'YOUR_STRIPE_PUBLISHABLE_KEY',
    ],

    // Manual Payment (Bank Transfer, etc.)
    'manual' => [
        'enabled' => true,
        'instructions' => 'Send payment to PayPal: your@email.com. Include your order number in the note.',
    ],
];
