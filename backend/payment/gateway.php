<?php
/**
 * SellBuddy Custom Payment Gateway for Snipcart
 *
 * This file handles payment method returns and payment processing
 * Documentation: https://docs.snipcart.com/v3/custom-payment-gateway
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

// Handle preflight OPTIONS request
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Load configuration
$config = require __DIR__ . '/config.php';

// Get request body
$input = file_get_contents('php://input');
$data = json_decode($input, true);

// Get the action from query string
$action = $_GET['action'] ?? 'methods';

try {
    switch ($action) {
        case 'methods':
            // Return available payment methods
            echo json_encode(getPaymentMethods($config));
            break;

        case 'process':
            // Process the payment
            echo json_encode(processPayment($data, $config));
            break;

        case 'refund':
            // Handle refund
            echo json_encode(processRefund($data, $config));
            break;

        case 'confirm':
            // Confirm payment (for async payments)
            echo json_encode(confirmPayment($data, $config));
            break;

        default:
            throw new Exception('Invalid action');
    }
} catch (Exception $e) {
    http_response_code(400);
    echo json_encode([
        'errors' => [
            ['key' => 'payment_error', 'message' => $e->getMessage()]
        ]
    ]);
}

/**
 * Return available payment methods to Snipcart
 */
function getPaymentMethods(array $config): array
{
    $methods = [];

    // PayPal
    if ($config['paypal']['enabled']) {
        $methods[] = [
            'id' => 'paypal',
            'name' => 'PayPal',
            'checkoutUrl' => getBaseUrl() . '/checkout.php?method=paypal',
            'iconUrl' => 'https://www.paypalobjects.com/webstatic/icon/pp258.png',
        ];
    }

    // Bkash
    if ($config['bkash']['enabled']) {
        $methods[] = [
            'id' => 'bkash',
            'name' => 'Bkash',
            'checkoutUrl' => getBaseUrl() . '/checkout.php?method=bkash',
            'iconUrl' => 'https://www.bkash.com/sites/default/files/bKash-logo.png',
        ];
    }

    // Stripe
    if ($config['stripe']['enabled']) {
        $methods[] = [
            'id' => 'stripe_custom',
            'name' => 'Credit Card',
            'checkoutUrl' => getBaseUrl() . '/checkout.php?method=stripe',
            'iconUrl' => 'https://stripe.com/img/v3/home/twitter.png',
        ];
    }

    // Manual Payment
    if ($config['manual']['enabled']) {
        $methods[] = [
            'id' => 'manual_payment',
            'name' => 'PayPal / Bank Transfer',
            'checkoutUrl' => getBaseUrl() . '/checkout.php?method=manual',
            'iconUrl' => 'https://cdn-icons-png.flaticon.com/512/2830/2830284.png',
        ];
    }

    return $methods;
}

/**
 * Process payment
 */
function processPayment(array $data, array $config): array
{
    $paymentSessionId = $data['paymentSessionId'] ?? null;
    $method = $data['method'] ?? 'manual';
    $amount = $data['amount'] ?? 0;
    $transactionId = $data['transactionId'] ?? null;

    if (!$paymentSessionId) {
        throw new Exception('Payment session ID is required');
    }

    // Log the payment attempt
    logPayment($data);

    switch ($method) {
        case 'paypal':
            return processPayPalPayment($data, $config);

        case 'bkash':
            return processBkashPayment($data, $config);

        case 'stripe':
            return processStripePayment($data, $config);

        case 'manual':
        default:
            return processManualPayment($data, $config);
    }
}

/**
 * Process PayPal payment
 */
function processPayPalPayment(array $data, array $config): array
{
    // In production, verify the PayPal payment here
    // For now, return success if transaction ID is provided
    $transactionId = $data['transactionId'] ?? null;

    if (!$transactionId) {
        throw new Exception('PayPal transaction ID is required');
    }

    return [
        'paymentSessionId' => $data['paymentSessionId'],
        'state' => 'processed',
        'transactionId' => $transactionId,
        'instructions' => 'Payment received via PayPal. Thank you!',
    ];
}

/**
 * Process Bkash payment
 */
function processBkashPayment(array $data, array $config): array
{
    $transactionId = $data['transactionId'] ?? null;

    if (!$transactionId) {
        throw new Exception('Bkash transaction ID is required');
    }

    // In production, verify with Bkash API
    return [
        'paymentSessionId' => $data['paymentSessionId'],
        'state' => 'processed',
        'transactionId' => $transactionId,
        'instructions' => 'Payment received via Bkash. Thank you!',
    ];
}

/**
 * Process Stripe payment
 */
function processStripePayment(array $data, array $config): array
{
    $transactionId = $data['transactionId'] ?? null;

    if (!$transactionId) {
        throw new Exception('Stripe payment intent ID is required');
    }

    return [
        'paymentSessionId' => $data['paymentSessionId'],
        'state' => 'processed',
        'transactionId' => $transactionId,
        'instructions' => 'Payment received. Thank you!',
    ];
}

/**
 * Process manual payment (bank transfer, etc.)
 */
function processManualPayment(array $data, array $config): array
{
    // Generate a reference number
    $reference = 'SB-' . strtoupper(substr(md5($data['paymentSessionId']), 0, 8));

    return [
        'paymentSessionId' => $data['paymentSessionId'],
        'state' => 'pending', // Will be confirmed manually
        'transactionId' => $reference,
        'instructions' => $config['manual']['instructions'] . "\n\nReference: " . $reference,
    ];
}

/**
 * Process refund
 */
function processRefund(array $data, array $config): array
{
    $transactionId = $data['transactionId'] ?? null;
    $amount = $data['amount'] ?? 0;

    // Log refund request
    logPayment(['action' => 'refund', 'transactionId' => $transactionId, 'amount' => $amount]);

    // In production, process refund through payment gateway
    return [
        'transactionId' => $transactionId,
        'state' => 'refunded',
        'refundedAmount' => $amount,
    ];
}

/**
 * Confirm pending payment
 */
function confirmPayment(array $data, array $config): array
{
    return [
        'paymentSessionId' => $data['paymentSessionId'],
        'state' => 'processed',
        'transactionId' => $data['transactionId'],
    ];
}

/**
 * Log payment for debugging
 */
function logPayment(array $data): void
{
    $logFile = __DIR__ . '/../../data/payment_log.json';
    $log = [];

    if (file_exists($logFile)) {
        $log = json_decode(file_get_contents($logFile), true) ?? [];
    }

    $log[] = [
        'timestamp' => date('Y-m-d H:i:s'),
        'data' => $data,
    ];

    // Keep only last 100 entries
    $log = array_slice($log, -100);

    file_put_contents($logFile, json_encode($log, JSON_PRETTY_PRINT));
}

/**
 * Get base URL for this script
 */
function getBaseUrl(): string
{
    $protocol = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http';
    $host = $_SERVER['HTTP_HOST'] ?? 'localhost';
    $path = dirname($_SERVER['SCRIPT_NAME']);
    return $protocol . '://' . $host . $path;
}
