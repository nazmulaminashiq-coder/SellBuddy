<?php
/**
 * SellBuddy Newsletter API Handler
 * Handles newsletter subscriptions
 */

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Only accept POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

// Get input
$input = file_get_contents('php://input');
$data = json_decode($input, true);

// Validate email
$email = filter_var($data['email'] ?? '', FILTER_VALIDATE_EMAIL);

if (!$email) {
    http_response_code(400);
    echo json_encode(['success' => false, 'error' => 'Invalid email address']);
    exit;
}

// Sanitize email
$email = strtolower(trim($email));

// Load existing subscribers
$subscribersFile = __DIR__ . '/../../data/newsletter_subscribers.json';
$subscribers = [];

if (file_exists($subscribersFile)) {
    $content = file_get_contents($subscribersFile);
    $subscribers = json_decode($content, true) ?: ['subscribers' => [], 'total_count' => 0];
}

// Check for duplicates
$existingEmails = array_column($subscribers['subscribers'] ?? [], 'email');
if (in_array($email, $existingEmails)) {
    echo json_encode([
        'success' => true,
        'message' => 'You are already subscribed!',
        'already_subscribed' => true
    ]);
    exit;
}

// Add new subscriber
$newSubscriber = [
    'email' => $email,
    'subscribed_at' => date('Y-m-d H:i:s'),
    'source' => $data['source'] ?? 'website',
    'ip' => $_SERVER['REMOTE_ADDR'] ?? 'unknown',
    'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown',
    'status' => 'active',
    'discount_code' => 'WELCOME10'
];

$subscribers['subscribers'][] = $newSubscriber;
$subscribers['total_count'] = count($subscribers['subscribers']);
$subscribers['last_updated'] = date('Y-m-d\TH:i:s\Z');

// Save to file
if (file_put_contents($subscribersFile, json_encode($subscribers, JSON_PRETTY_PRINT))) {
    // Log subscription
    logSubscription($email);

    echo json_encode([
        'success' => true,
        'message' => 'Successfully subscribed! Check your email for your 10% discount code.',
        'discount_code' => 'WELCOME10'
    ]);
} else {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Failed to save subscription']);
}

/**
 * Log subscription for analytics
 */
function logSubscription(string $email): void {
    $logFile = __DIR__ . '/../../data/logs/newsletter_' . date('Y-m') . '.log';
    $logDir = dirname($logFile);

    if (!is_dir($logDir)) {
        mkdir($logDir, 0755, true);
    }

    $logEntry = sprintf(
        "[%s] New subscription: %s\n",
        date('Y-m-d H:i:s'),
        $email
    );

    file_put_contents($logFile, $logEntry, FILE_APPEND);
}
