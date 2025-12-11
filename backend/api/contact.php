<?php
/**
 * SellBuddy Contact Form API Handler
 * Handles contact form submissions with validation and storage
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

// Validate required fields
$requiredFields = ['name', 'email', 'subject', 'message'];
$errors = [];

foreach ($requiredFields as $field) {
    if (empty($data[$field])) {
        $errors[] = ucfirst($field) . ' is required';
    }
}

// Validate email
$email = filter_var($data['email'] ?? '', FILTER_VALIDATE_EMAIL);
if (!$email) {
    $errors[] = 'Invalid email address';
}

// Validate message length
if (strlen($data['message'] ?? '') < 10) {
    $errors[] = 'Message must be at least 10 characters';
}

if (strlen($data['message'] ?? '') > 5000) {
    $errors[] = 'Message must not exceed 5000 characters';
}

// Check for spam patterns
if (containsSpam($data['message'] ?? '')) {
    $errors[] = 'Message appears to contain spam';
}

if (!empty($errors)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'errors' => $errors]);
    exit;
}

// Sanitize inputs
$submission = [
    'id' => 'CT-' . date('Ymd') . '-' . strtoupper(substr(md5(uniqid()), 0, 6)),
    'name' => htmlspecialchars(trim($data['name']), ENT_QUOTES, 'UTF-8'),
    'email' => strtolower(trim($email)),
    'order_number' => htmlspecialchars(trim($data['orderNumber'] ?? ''), ENT_QUOTES, 'UTF-8'),
    'subject' => htmlspecialchars(trim($data['subject']), ENT_QUOTES, 'UTF-8'),
    'message' => htmlspecialchars(trim($data['message']), ENT_QUOTES, 'UTF-8'),
    'submitted_at' => date('Y-m-d H:i:s'),
    'ip' => $_SERVER['REMOTE_ADDR'] ?? 'unknown',
    'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown',
    'status' => 'new'
];

// Load existing submissions
$submissionsFile = __DIR__ . '/../../data/contact_submissions.json';
$submissions = [];

if (file_exists($submissionsFile)) {
    $content = file_get_contents($submissionsFile);
    $submissions = json_decode($content, true) ?: ['submissions' => [], 'total_count' => 0];
}

// Add new submission
$submissions['submissions'][] = $submission;
$submissions['total_count'] = count($submissions['submissions']);
$submissions['last_updated'] = date('Y-m-d\TH:i:s\Z');

// Save to file
if (file_put_contents($submissionsFile, json_encode($submissions, JSON_PRETTY_PRINT))) {
    // Log submission
    logContactSubmission($submission);

    // Send notification email to owner
    sendOwnerNotification($submission);

    echo json_encode([
        'success' => true,
        'message' => 'Thank you for your message! We will get back to you within 24 hours.',
        'reference' => $submission['id']
    ]);
} else {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Failed to save submission']);
}

/**
 * Check for spam patterns
 */
function containsSpam(string $message): bool {
    $spamPatterns = [
        '/\b(viagra|cialis|casino|lottery|winner|prince|inheritance)\b/i',
        '/\b(click here|buy now|limited time|act now)\b/i',
        '/(http[s]?:\/\/){3,}/i', // Multiple URLs
    ];

    foreach ($spamPatterns as $pattern) {
        if (preg_match($pattern, $message)) {
            return true;
        }
    }

    return false;
}

/**
 * Log contact submission
 */
function logContactSubmission(array $submission): void {
    $logFile = __DIR__ . '/../../data/logs/contact_' . date('Y-m') . '.log';
    $logDir = dirname($logFile);

    if (!is_dir($logDir)) {
        mkdir($logDir, 0755, true);
    }

    $logEntry = sprintf(
        "[%s] Contact submission #%s from %s <%s> - Subject: %s\n",
        $submission['submitted_at'],
        $submission['id'],
        $submission['name'],
        $submission['email'],
        $submission['subject']
    );

    file_put_contents($logFile, $logEntry, FILE_APPEND);
}

/**
 * Send notification email to store owner
 */
function sendOwnerNotification(array $submission): void {
    $ownerEmail = getenv('OWNER_EMAIL') ?: 'nazmulaminashiq.coder@gmail.com';
    $subject = "[SellBuddy Contact] {$submission['subject']} - #{$submission['id']}";

    $body = "
New Contact Form Submission
============================

Reference: {$submission['id']}
Date: {$submission['submitted_at']}

From: {$submission['name']}
Email: {$submission['email']}
Order Number: {$submission['order_number']}

Subject: {$submission['subject']}

Message:
{$submission['message']}

---
Reply directly to this email to respond to the customer.
";

    $headers = [
        'From: SellBuddy Support <noreply@sellbuddy.store>',
        'Reply-To: ' . $submission['email']
    ];

    @mail($ownerEmail, $subject, $body, implode("\r\n", $headers));
}
