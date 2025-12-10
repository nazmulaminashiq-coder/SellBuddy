# SellBuddy Payment Gateway Backend

Custom payment gateway for Snipcart integration.

## Setup Instructions

### 1. Upload to Your Server

Upload the `backend/payment/` folder to your PHP hosting:
- Free options: InfinityFree, 000webhost, Hostinger free tier
- Or use your existing hosting at remoteforce.site

Example: `https://yoursite.com/sellbuddy/payment/`

### 2. Configure Settings

Edit `config.php` and update:

```php
'store' => [
    'url' => 'https://your-github-pages-url/store/',
    'secret_key' => 'generate-a-random-string',
],

'paypal' => [
    'enabled' => true,
    'client_id' => 'YOUR_PAYPAL_CLIENT_ID',  // Get from PayPal Developer
    'client_secret' => 'YOUR_PAYPAL_SECRET',
    'mode' => 'sandbox',  // Change to 'live' for production
],
```

### 3. Configure Snipcart

1. Go to Snipcart Dashboard → Payment Gateway
2. Add Custom Payment Gateway
3. Set the URL to: `https://yoursite.com/sellbuddy/payment/gateway.php?action=methods`

### 4. Test the Integration

1. Add a product to cart on your store
2. Proceed to checkout
3. Select your custom payment method
4. Complete a test payment

## Payment Methods

| Method | Status | Notes |
|--------|--------|-------|
| PayPal | Ready | Requires PayPal Business account |
| Bkash | Optional | For Bangladesh customers |
| Manual | Ready | Bank transfer / manual confirmation |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `gateway.php?action=methods` | Returns available payment methods |
| `gateway.php?action=process` | Processes a payment |
| `gateway.php?action=refund` | Handles refunds |
| `checkout.php?method=X` | Customer checkout page |

## Getting PayPal Credentials

1. Go to [developer.paypal.com](https://developer.paypal.com)
2. Create/Login to your account
3. Go to Dashboard → My Apps & Credentials
4. Create a new app (Sandbox for testing, Live for production)
5. Copy Client ID and Secret

## Security Notes

- Never commit `config.php` with real credentials
- Use HTTPS in production
- Keep `secret_key` private
- Validate all payments server-side

## File Structure

```
backend/payment/
├── config.php      # Configuration (edit this)
├── gateway.php     # Main API endpoint
├── checkout.php    # Customer checkout page
├── .htaccess       # Security & CORS
└── README.md       # This file
```
