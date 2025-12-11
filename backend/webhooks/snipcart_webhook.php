<?php
/**
 * SellBuddy - Snipcart Webhook Handler
 *
 * This webhook automatically processes orders when Snipcart sends events.
 * Set your webhook URL in Snipcart Dashboard: https://yourdomain.com/backend/webhooks/snipcart_webhook.php
 */

declare(strict_types=1);

// Configuration
define('SNIPCART_SECRET_KEY', getenv('SNIPCART_SECRET_KEY') ?: '');
define('SNIPCART_API_KEY', getenv('SNIPCART_API_KEY') ?: '');
define('GOOGLE_SHEETS_WEBHOOK', getenv('GOOGLE_SHEETS_WEBHOOK') ?: '');
define('OWNER_EMAIL', getenv('OWNER_EMAIL') ?: 'nazmulaminashiq.coder@gmail.com');
define('STORE_NAME', 'SellBuddy');
define('LOG_FILE', __DIR__ . '/../../data/logs/webhook_' . date('Y-m-d') . '.log');
define('RATE_LIMIT_FILE', __DIR__ . '/../../data/logs/rate_limit.json');
define('MAX_REQUESTS_PER_MINUTE', 30);

// Security headers
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('X-XSS-Protection: 1; mode=block');
header('Content-Type: application/json');

// Allow CORS only for Snipcart domains
$allowedOrigins = [
    'https://app.snipcart.com',
    'https://cdn.snipcart.com',
    'https://payment.snipcart.com'
];
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if (in_array($origin, $allowedOrigins)) {
    header('Access-Control-Allow-Origin: ' . $origin);
}
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, X-Snipcart-RequestToken');

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Only accept POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

// Rate limiting
if (!checkRateLimit($_SERVER['REMOTE_ADDR'] ?? 'unknown')) {
    logMessage('SECURITY', 'Rate limit exceeded for IP: ' . ($_SERVER['REMOTE_ADDR'] ?? 'unknown'));
    http_response_code(429);
    echo json_encode(['error' => 'Too many requests']);
    exit;
}

// Get webhook payload
$payload = file_get_contents('php://input');
$data = json_decode($payload, true);

if (!$data) {
    logMessage('ERROR', 'Invalid JSON payload');
    http_response_code(400);
    echo json_encode(['error' => 'Invalid payload']);
    exit;
}

// Log incoming webhook
logMessage('INFO', 'Received webhook: ' . ($data['eventName'] ?? 'unknown'));

// Verify webhook with Snipcart API
$requestToken = $_SERVER['HTTP_X_SNIPCART_REQUESTTOKEN'] ?? '';
if (!empty(SNIPCART_API_KEY) && !empty($requestToken)) {
    if (!verifySnipcartWebhook($requestToken)) {
        logMessage('SECURITY', 'Invalid webhook signature - rejected');
        http_response_code(401);
        echo json_encode(['error' => 'Invalid webhook signature']);
        exit;
    }
    logMessage('INFO', 'Webhook signature verified');
} elseif (!empty(SNIPCART_API_KEY)) {
    logMessage('WARN', 'Missing request token in webhook - processing anyway in test mode');
}

// Handle different event types
$eventName = $data['eventName'] ?? '';
$response = ['success' => true, 'event' => $eventName];

switch ($eventName) {
    case 'order.completed':
        $response['result'] = handleOrderCompleted($data);
        break;

    case 'order.status.changed':
        $response['result'] = handleOrderStatusChanged($data);
        break;

    case 'order.refund.created':
        $response['result'] = handleRefund($data);
        break;

    case 'subscription.created':
        $response['result'] = handleSubscription($data);
        break;

    case 'customauth:customer_updated':
        $response['result'] = handleCustomerUpdate($data);
        break;

    default:
        logMessage('INFO', "Unhandled event: $eventName");
        $response['message'] = 'Event acknowledged';
}

echo json_encode($response);

/**
 * Handle completed orders
 */
function handleOrderCompleted(array $data): array {
    $order = $data['content'] ?? [];

    // Extract order details
    $orderData = [
        'order_id' => $order['token'] ?? generateOrderId(),
        'invoice_number' => $order['invoiceNumber'] ?? '',
        'date' => date('Y-m-d H:i:s'),
        'customer_name' => ($order['billingAddress']['fullName'] ?? '') ?: ($order['user']['billingAddress']['fullName'] ?? 'Guest'),
        'customer_email' => $order['email'] ?? $order['user']['email'] ?? '',
        'phone' => $order['billingAddress']['phone'] ?? '',
        'items' => extractItems($order['items'] ?? []),
        'subtotal' => $order['itemsTotal'] ?? 0,
        'shipping' => $order['shippingFees'] ?? 0,
        'tax' => $order['taxesTotal'] ?? 0,
        'total' => $order['grandTotal'] ?? 0,
        'currency' => $order['currency'] ?? 'USD',
        'shipping_address' => formatAddress($order['shippingAddress'] ?? []),
        'payment_method' => $order['paymentMethod'] ?? 'unknown',
        'status' => 'confirmed'
    ];

    logMessage('ORDER', "New order: {$orderData['order_id']} - \${$orderData['total']}");

    // 1. Save to local JSON
    saveOrderLocally($orderData);

    // 2. Send to Google Sheets
    sendToGoogleSheets($orderData);

    // 3. Send customer confirmation email
    sendCustomerEmail($orderData);

    // 4. Send owner notification
    sendOwnerNotification($orderData);

    // 5. Update analytics
    updateAnalytics($orderData);

    return [
        'order_id' => $orderData['order_id'],
        'processed' => true,
        'actions' => ['saved', 'sheets', 'email_customer', 'email_owner', 'analytics']
    ];
}

/**
 * Handle order status changes
 */
function handleOrderStatusChanged(array $data): array {
    $order = $data['content'] ?? [];
    $oldStatus = $data['from'] ?? '';
    $newStatus = $data['to'] ?? '';

    logMessage('STATUS', "Order {$order['token']} changed: $oldStatus -> $newStatus");

    // Update local records
    updateOrderStatus($order['token'] ?? '', $newStatus);

    // Notify customer of status change
    if ($newStatus === 'Shipped') {
        sendShippingNotification($order);
    }

    return [
        'order_id' => $order['token'] ?? '',
        'old_status' => $oldStatus,
        'new_status' => $newStatus
    ];
}

/**
 * Handle refunds
 */
function handleRefund(array $data): array {
    $refund = $data['content'] ?? [];

    logMessage('REFUND', "Refund processed for order: " . ($refund['orderToken'] ?? 'unknown'));

    // Update order status
    updateOrderStatus($refund['orderToken'] ?? '', 'refunded');

    return [
        'refund_id' => $refund['id'] ?? '',
        'amount' => $refund['amount'] ?? 0
    ];
}

/**
 * Handle new subscriptions
 */
function handleSubscription(array $data): array {
    $subscription = $data['content'] ?? [];

    logMessage('SUBSCRIPTION', "New subscription: " . ($subscription['id'] ?? 'unknown'));

    return [
        'subscription_id' => $subscription['id'] ?? '',
        'status' => 'active'
    ];
}

/**
 * Handle customer updates
 */
function handleCustomerUpdate(array $data): array {
    logMessage('CUSTOMER', 'Customer data updated');
    return ['updated' => true];
}

/**
 * Extract items from order
 */
function extractItems(array $items): array {
    $extracted = [];
    foreach ($items as $item) {
        $extracted[] = [
            'name' => $item['name'] ?? '',
            'quantity' => $item['quantity'] ?? 1,
            'price' => $item['price'] ?? 0,
            'sku' => $item['id'] ?? ''
        ];
    }
    return $extracted;
}

/**
 * Format address for display
 */
function formatAddress(array $address): string {
    $parts = array_filter([
        $address['address1'] ?? '',
        $address['address2'] ?? '',
        $address['city'] ?? '',
        $address['province'] ?? '',
        $address['postalCode'] ?? '',
        $address['country'] ?? ''
    ]);
    return implode(', ', $parts);
}

/**
 * Save order to local JSON file
 */
function saveOrderLocally(array $order): void {
    $ordersFile = __DIR__ . '/../../data/orders.json';

    $orders = [];
    if (file_exists($ordersFile)) {
        $orders = json_decode(file_get_contents($ordersFile), true) ?: [];
    }

    // Add to orders list
    $orders['orders'][] = [
        'id' => $order['order_id'],
        'date' => $order['date'],
        'customer' => $order['customer_name'],
        'email' => $order['customer_email'],
        'product' => $order['items'][0]['name'] ?? 'Multiple Items',
        'quantity' => array_sum(array_column($order['items'], 'quantity')),
        'total' => $order['total'],
        'status' => $order['status']
    ];

    // Update stats
    if (!isset($orders['stats'])) {
        $orders['stats'] = ['revenue' => 0, 'orders_count' => 0];
    }
    $orders['stats']['revenue'] += $order['total'];
    $orders['stats']['orders_count']++;
    $orders['stats']['last_order'] = $order['date'];

    file_put_contents($ordersFile, json_encode($orders, JSON_PRETTY_PRINT));
}

/**
 * Send order data to Google Sheets
 */
function sendToGoogleSheets(array $order): void {
    if (empty(GOOGLE_SHEETS_WEBHOOK)) {
        logMessage('WARN', 'Google Sheets webhook not configured');
        return;
    }

    $itemsList = implode(', ', array_map(function($item) {
        return "{$item['name']} x{$item['quantity']}";
    }, $order['items']));

    $sheetData = [
        'order_id' => $order['order_id'],
        'date' => $order['date'],
        'customer_name' => $order['customer_name'],
        'customer_email' => $order['customer_email'],
        'phone' => $order['phone'],
        'items' => $itemsList,
        'subtotal' => $order['subtotal'],
        'shipping' => $order['shipping'],
        'tax' => $order['tax'],
        'total' => $order['total'],
        'shipping_address' => $order['shipping_address'],
        'status' => $order['status']
    ];

    $ch = curl_init(GOOGLE_SHEETS_WEBHOOK);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($sheetData),
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 10
    ]);

    $result = curl_exec($ch);
    $error = curl_error($ch);
    curl_close($ch);

    if ($error) {
        logMessage('ERROR', "Google Sheets webhook failed: $error");
    } else {
        logMessage('INFO', 'Order sent to Google Sheets');
    }
}

/**
 * Send confirmation email to customer
 */
function sendCustomerEmail(array $order): void {
    $to = $order['customer_email'];
    if (empty($to)) return;

    $subject = STORE_NAME . " - Order Confirmed #{$order['order_id']}";

    $itemsHtml = '';
    foreach ($order['items'] as $item) {
        $itemsHtml .= "<tr>
            <td style='padding: 10px; border-bottom: 1px solid #eee;'>{$item['name']}</td>
            <td style='padding: 10px; border-bottom: 1px solid #eee; text-align: center;'>{$item['quantity']}</td>
            <td style='padding: 10px; border-bottom: 1px solid #eee; text-align: right;'>\${$item['price']}</td>
        </tr>";
    }

    $body = "
    <html>
    <body style='font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;'>
        <div style='background: linear-gradient(135deg, #6366f1, #4f46e5); padding: 30px; text-align: center;'>
            <h1 style='color: white; margin: 0;'>Thank You for Your Order!</h1>
        </div>

        <div style='padding: 30px;'>
            <p>Hi {$order['customer_name']},</p>
            <p>Great news! Your order has been confirmed and is being prepared for shipment.</p>

            <div style='background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;'>
                <h3 style='margin-top: 0;'>Order #{$order['order_id']}</h3>
                <p><strong>Date:</strong> {$order['date']}</p>
            </div>

            <table style='width: 100%; border-collapse: collapse;'>
                <thead>
                    <tr style='background: #f1f5f9;'>
                        <th style='padding: 10px; text-align: left;'>Item</th>
                        <th style='padding: 10px; text-align: center;'>Qty</th>
                        <th style='padding: 10px; text-align: right;'>Price</th>
                    </tr>
                </thead>
                <tbody>
                    $itemsHtml
                </tbody>
            </table>

            <div style='text-align: right; margin-top: 20px;'>
                <p>Subtotal: \${$order['subtotal']}</p>
                <p>Shipping: \${$order['shipping']}</p>
                <p>Tax: \${$order['tax']}</p>
                <p style='font-size: 1.2em; font-weight: bold;'>Total: \${$order['total']} {$order['currency']}</p>
            </div>

            <div style='background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;'>
                <h4 style='margin-top: 0;'>Shipping Address</h4>
                <p>{$order['shipping_address']}</p>
            </div>

            <p><strong>What's Next?</strong></p>
            <ul>
                <li>You'll receive a shipping confirmation email with tracking info within 1-2 business days</li>
                <li>Estimated delivery: 7-15 business days</li>
                <li>Questions? Reply to this email or visit our FAQ</li>
            </ul>

            <p>Thanks for shopping with us!</p>
            <p>The " . STORE_NAME . " Team</p>
        </div>

        <div style='background: #1e293b; color: #94a3b8; padding: 20px; text-align: center; font-size: 12px;'>
            <p>&copy; " . date('Y') . " " . STORE_NAME . ". All rights reserved.</p>
        </div>
    </body>
    </html>";

    $headers = [
        'MIME-Version: 1.0',
        'Content-type: text/html; charset=UTF-8',
        'From: ' . STORE_NAME . ' <noreply@sellbuddy.store>',
        'Reply-To: ' . OWNER_EMAIL
    ];

    if (mail($to, $subject, $body, implode("\r\n", $headers))) {
        logMessage('EMAIL', "Confirmation sent to: $to");
    } else {
        logMessage('ERROR', "Failed to send email to: $to");
    }
}

/**
 * Send notification to store owner
 */
function sendOwnerNotification(array $order): void {
    $to = OWNER_EMAIL;
    $subject = "[" . STORE_NAME . "] New Order #{$order['order_id']} - \${$order['total']}";

    $itemsList = implode("\n", array_map(function($item) {
        return "  - {$item['name']} x{$item['quantity']} @ \${$item['price']}";
    }, $order['items']));

    $body = "
NEW ORDER RECEIVED!

Order ID: {$order['order_id']}
Date: {$order['date']}

CUSTOMER:
Name: {$order['customer_name']}
Email: {$order['customer_email']}
Phone: {$order['phone']}

ITEMS:
$itemsList

TOTALS:
Subtotal: \${$order['subtotal']}
Shipping: \${$order['shipping']}
Tax: \${$order['tax']}
TOTAL: \${$order['total']} {$order['currency']}

SHIPPING ADDRESS:
{$order['shipping_address']}

---
Action Required: Process this order within 24 hours.
";

    $headers = [
        'From: ' . STORE_NAME . ' Orders <orders@sellbuddy.store>',
        'Reply-To: ' . $order['customer_email']
    ];

    mail($to, $subject, $body, implode("\r\n", $headers));
    logMessage('EMAIL', "Owner notification sent");
}

/**
 * Send shipping notification
 */
function sendShippingNotification(array $order): void {
    $email = $order['email'] ?? $order['user']['email'] ?? '';
    if (empty($email)) return;

    $subject = STORE_NAME . " - Your Order Has Shipped!";
    $body = "Great news! Your order is on its way. You'll receive tracking information shortly.";

    mail($email, $subject, $body);
    logMessage('EMAIL', "Shipping notification sent to: $email");
}

/**
 * Update order status in local storage
 */
function updateOrderStatus(string $orderId, string $status): void {
    $ordersFile = __DIR__ . '/../../data/orders.json';

    if (!file_exists($ordersFile)) return;

    $orders = json_decode(file_get_contents($ordersFile), true) ?: [];

    foreach ($orders['orders'] as &$order) {
        if ($order['id'] === $orderId) {
            $order['status'] = $status;
            $order['updated_at'] = date('Y-m-d H:i:s');
            break;
        }
    }

    file_put_contents($ordersFile, json_encode($orders, JSON_PRETTY_PRINT));
}

/**
 * Update analytics with new order
 */
function updateAnalytics(array $order): void {
    $analyticsFile = __DIR__ . '/../../data/analytics.json';

    $analytics = [];
    if (file_exists($analyticsFile)) {
        $analytics = json_decode(file_get_contents($analyticsFile), true) ?: [];
    }

    $today = date('Y-m-d');

    if (!isset($analytics['daily'][$today])) {
        $analytics['daily'][$today] = ['orders' => 0, 'revenue' => 0, 'items_sold' => 0];
    }

    $analytics['daily'][$today]['orders']++;
    $analytics['daily'][$today]['revenue'] += $order['total'];
    $analytics['daily'][$today]['items_sold'] += array_sum(array_column($order['items'], 'quantity'));

    // Update totals
    if (!isset($analytics['totals'])) {
        $analytics['totals'] = ['orders' => 0, 'revenue' => 0];
    }
    $analytics['totals']['orders']++;
    $analytics['totals']['revenue'] += $order['total'];

    // Track product sales
    if (!isset($analytics['products'])) {
        $analytics['products'] = [];
    }
    foreach ($order['items'] as $item) {
        $sku = $item['sku'];
        if (!isset($analytics['products'][$sku])) {
            $analytics['products'][$sku] = ['name' => $item['name'], 'sold' => 0, 'revenue' => 0];
        }
        $analytics['products'][$sku]['sold'] += $item['quantity'];
        $analytics['products'][$sku]['revenue'] += $item['price'] * $item['quantity'];
    }

    file_put_contents($analyticsFile, json_encode($analytics, JSON_PRETTY_PRINT));
}

/**
 * Generate unique order ID
 */
function generateOrderId(): string {
    return 'SB-' . date('Ymd') . '-' . strtoupper(substr(md5(uniqid()), 0, 6));
}

/**
 * Log message to file
 */
function logMessage(string $level, string $message): void {
    $logDir = dirname(LOG_FILE);
    if (!is_dir($logDir)) {
        mkdir($logDir, 0755, true);
    }

    $timestamp = date('Y-m-d H:i:s');
    $logLine = "[$timestamp] [$level] $message\n";

    file_put_contents(LOG_FILE, $logLine, FILE_APPEND);
}

/**
 * Verify Snipcart webhook signature
 * https://docs.snipcart.com/v3/webhooks/introduction#validating-webhooks
 */
function verifySnipcartWebhook(string $requestToken): bool {
    if (empty(SNIPCART_API_KEY)) {
        return true; // Skip verification if no API key configured
    }

    // Verify with Snipcart API
    $ch = curl_init('https://app.snipcart.com/api/requestvalidation/' . $requestToken);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => [
            'Authorization: Basic ' . base64_encode(SNIPCART_API_KEY . ':'),
            'Accept: application/json'
        ],
        CURLOPT_TIMEOUT => 10
    ]);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($httpCode !== 200) {
        logMessage('SECURITY', "Webhook validation failed with HTTP $httpCode");
        return false;
    }

    $result = json_decode($response, true);
    return ($result['token'] ?? '') === $requestToken;
}

/**
 * Rate limiting to prevent abuse
 */
function checkRateLimit(string $ip): bool {
    $rateFile = RATE_LIMIT_FILE;
    $rateDir = dirname($rateFile);

    if (!is_dir($rateDir)) {
        mkdir($rateDir, 0755, true);
    }

    $rateData = [];
    if (file_exists($rateFile)) {
        $rateData = json_decode(file_get_contents($rateFile), true) ?: [];
    }

    $now = time();
    $minute = floor($now / 60);

    // Clean old entries (older than 5 minutes)
    foreach ($rateData as $key => $data) {
        if ($data['minute'] < $minute - 5) {
            unset($rateData[$key]);
        }
    }

    $key = md5($ip);
    if (!isset($rateData[$key]) || $rateData[$key]['minute'] !== $minute) {
        $rateData[$key] = ['minute' => $minute, 'count' => 0];
    }

    $rateData[$key]['count']++;

    file_put_contents($rateFile, json_encode($rateData));

    return $rateData[$key]['count'] <= MAX_REQUESTS_PER_MINUTE;
}

/**
 * Sanitize string input
 */
function sanitizeInput(string $input): string {
    return htmlspecialchars(trim($input), ENT_QUOTES, 'UTF-8');
}

/**
 * Validate email address
 */
function validateEmail(string $email): ?string {
    $email = filter_var(trim($email), FILTER_VALIDATE_EMAIL);
    return $email !== false ? $email : null;
}
