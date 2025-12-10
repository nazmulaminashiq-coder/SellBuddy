<?php
/**
 * SellBuddy Custom Checkout Page
 *
 * This page is shown to customers when they select a payment method
 */

// Get payment method and session ID
$method = $_GET['method'] ?? 'manual';
$sessionId = $_GET['sessionId'] ?? '';
$publicToken = $_GET['publicToken'] ?? '';
$amount = $_GET['amount'] ?? '0.00';
$currency = $_GET['currency'] ?? 'USD';

// Load configuration
$config = require __DIR__ . '/config.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Checkout - SellBuddy</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .checkout-container {
            background: white;
            border-radius: 16px;
            padding: 40px;
            max-width: 450px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }

        .logo {
            text-align: center;
            margin-bottom: 30px;
        }

        .logo h1 {
            color: #6366f1;
            font-size: 28px;
        }

        .logo span {
            color: #10b981;
        }

        .order-summary {
            background: #f9fafb;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
        }

        .order-summary h3 {
            color: #374151;
            margin-bottom: 15px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .order-total {
            display: flex;
            justify-content: space-between;
            font-size: 24px;
            font-weight: 700;
            color: #1f2937;
        }

        .payment-method {
            margin-bottom: 30px;
        }

        .payment-method h3 {
            color: #374151;
            margin-bottom: 15px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .method-badge {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: #eef2ff;
            color: #4f46e5;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
        }

        .method-badge img {
            width: 24px;
            height: 24px;
        }

        /* PayPal Button */
        #paypal-button-container {
            margin-bottom: 20px;
        }

        /* Manual Payment */
        .manual-instructions {
            background: #fef3c7;
            border: 1px solid #f59e0b;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .manual-instructions h4 {
            color: #92400e;
            margin-bottom: 10px;
        }

        .manual-instructions p {
            color: #78350f;
            font-size: 14px;
            line-height: 1.6;
        }

        .manual-instructions .reference {
            background: white;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 16px;
            margin-top: 10px;
            text-align: center;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            color: #374151;
            font-weight: 500;
            margin-bottom: 8px;
        }

        .form-group input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        .form-group input:focus {
            outline: none;
            border-color: #6366f1;
        }

        .btn {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }

        .btn-primary {
            background: #6366f1;
            color: white;
        }

        .btn-primary:hover {
            background: #4f46e5;
        }

        .btn-success {
            background: #10b981;
            color: white;
        }

        .btn-success:hover {
            background: #059669;
        }

        .btn-cancel {
            background: #f3f4f6;
            color: #6b7280;
            margin-top: 10px;
        }

        .btn-cancel:hover {
            background: #e5e7eb;
        }

        .secure-badge {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            color: #6b7280;
            font-size: 12px;
            margin-top: 20px;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }

        .spinner {
            border: 3px solid #f3f4f6;
            border-top: 3px solid #6366f1;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error-message {
            background: #fef2f2;
            border: 1px solid #fca5a5;
            color: #b91c1c;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }

        .success-message {
            background: #ecfdf5;
            border: 1px solid #6ee7b7;
            color: #065f46;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            display: none;
        }

        .success-message h3 {
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="checkout-container">
        <div class="logo">
            <h1>Sell<span>Buddy</span></h1>
        </div>

        <div class="order-summary">
            <h3>Order Total</h3>
            <div class="order-total">
                <span>Total:</span>
                <span id="order-amount"><?php echo $currency; ?> <?php echo $amount; ?></span>
            </div>
        </div>

        <div class="error-message" id="error-message"></div>
        <div class="success-message" id="success-message">
            <h3>Payment Successful!</h3>
            <p>Redirecting back to your order...</p>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Processing payment...</p>
        </div>

        <div id="payment-content">
            <?php if ($method === 'paypal'): ?>
                <!-- PayPal Payment -->
                <div class="payment-method">
                    <h3>Pay with PayPal</h3>
                </div>
                <div id="paypal-button-container"></div>
                <script src="https://www.paypal.com/sdk/js?client-id=<?php echo $config['paypal']['client_id']; ?>&currency=USD"></script>
                <script>
                    paypal.Buttons({
                        createOrder: function(data, actions) {
                            return actions.order.create({
                                purchase_units: [{
                                    amount: {
                                        value: '<?php echo $amount; ?>'
                                    }
                                }]
                            });
                        },
                        onApprove: function(data, actions) {
                            return actions.order.capture().then(function(details) {
                                completePayment('paypal', details.id);
                            });
                        },
                        onError: function(err) {
                            showError('PayPal payment failed. Please try again.');
                        }
                    }).render('#paypal-button-container');
                </script>

            <?php elseif ($method === 'bkash'): ?>
                <!-- Bkash Payment -->
                <div class="payment-method">
                    <h3>Pay with Bkash</h3>
                    <div class="method-badge">
                        <img src="https://www.bkash.com/sites/default/files/bKash-logo.png" alt="Bkash">
                        Bkash
                    </div>
                </div>
                <div class="manual-instructions">
                    <h4>Bkash Payment Instructions:</h4>
                    <p>1. Open Bkash app and select "Send Money"</p>
                    <p>2. Enter number: <strong>01XXXXXXXXX</strong></p>
                    <p>3. Enter amount: <strong><?php echo $currency; ?> <?php echo $amount; ?></strong></p>
                    <p>4. Enter the reference below in the message</p>
                    <div class="reference" id="payment-reference">SB-<?php echo strtoupper(substr(md5($sessionId . time()), 0, 8)); ?></div>
                </div>
                <div class="form-group">
                    <label>Bkash Transaction ID</label>
                    <input type="text" id="bkash-txn-id" placeholder="Enter your Bkash TxnID">
                </div>
                <button class="btn btn-success" onclick="submitBkash()">Confirm Payment</button>

            <?php else: ?>
                <!-- Manual Payment -->
                <div class="payment-method">
                    <h3>Manual Payment</h3>
                    <div class="method-badge">
                        PayPal / Bank Transfer
                    </div>
                </div>
                <div class="manual-instructions">
                    <h4>Payment Instructions:</h4>
                    <p><?php echo nl2br(htmlspecialchars($config['manual']['instructions'])); ?></p>
                    <p style="margin-top: 10px;"><strong>Amount:</strong> <?php echo $currency; ?> <?php echo $amount; ?></p>
                    <p><strong>Your Reference Number:</strong></p>
                    <div class="reference" id="payment-reference">SB-<?php echo strtoupper(substr(md5($sessionId . time()), 0, 8)); ?></div>
                </div>
                <div class="form-group">
                    <label>Transaction ID / Reference</label>
                    <input type="text" id="manual-txn-id" placeholder="Enter your payment reference">
                </div>
                <button class="btn btn-primary" onclick="submitManual()">I've Made the Payment</button>
            <?php endif; ?>

            <button class="btn btn-cancel" onclick="cancelPayment()">Cancel</button>
        </div>

        <div class="secure-badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
            </svg>
            Secure checkout powered by SellBuddy
        </div>
    </div>

    <script>
        const sessionId = '<?php echo $sessionId; ?>';
        const publicToken = '<?php echo $publicToken; ?>';
        const gatewayUrl = 'gateway.php';

        function showLoading() {
            document.getElementById('payment-content').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
        }

        function hideLoading() {
            document.getElementById('loading').style.display = 'none';
            document.getElementById('payment-content').style.display = 'block';
        }

        function showError(message) {
            const errorDiv = document.getElementById('error-message');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            hideLoading();
        }

        function showSuccess() {
            document.getElementById('payment-content').style.display = 'none';
            document.getElementById('loading').style.display = 'none';
            document.getElementById('success-message').style.display = 'block';
        }

        function completePayment(method, transactionId) {
            showLoading();

            fetch(gatewayUrl + '?action=process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    paymentSessionId: sessionId,
                    method: method,
                    transactionId: transactionId,
                    amount: <?php echo $amount; ?>
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.state === 'processed' || data.state === 'pending') {
                    showSuccess();
                    // Redirect back to Snipcart
                    setTimeout(() => {
                        window.location.href = 'https://pay.snipcart.com/payment-session/' + sessionId + '/confirm?transactionId=' + data.transactionId;
                    }, 2000);
                } else {
                    showError('Payment could not be processed. Please try again.');
                }
            })
            .catch(error => {
                showError('An error occurred. Please try again.');
                console.error(error);
            });
        }

        function submitBkash() {
            const txnId = document.getElementById('bkash-txn-id').value.trim();
            if (!txnId) {
                showError('Please enter your Bkash Transaction ID');
                return;
            }
            completePayment('bkash', txnId);
        }

        function submitManual() {
            const txnId = document.getElementById('manual-txn-id').value.trim();
            const reference = document.getElementById('payment-reference').textContent;
            completePayment('manual', txnId || reference);
        }

        function cancelPayment() {
            // Redirect back to store
            window.location.href = '<?php echo $config['store']['url']; ?>';
        }
    </script>
</body>
</html>
