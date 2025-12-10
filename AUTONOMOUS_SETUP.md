# SellBuddy Autonomous System Setup Guide

This guide will help you set up a **100% autonomous dropshipping system** that runs on FREE platforms.

## Quick Overview

| Component | Platform | Cost |
|-----------|----------|------|
| Store Hosting | GitHub Pages | FREE |
| Shopping Cart | Snipcart | FREE (2% fee on sales) |
| Automation | GitHub Actions | FREE (2000 min/month) |
| Notebooks | Google Colab | FREE |
| Order Tracking | Google Sheets | FREE |
| Payments | PayPal Business | ~3% fee |

---

## Step 1: Enable GitHub Pages

1. Go to your repository: https://github.com/nazmulaminashiq-coder/SellBuddy
2. Click **Settings** → **Pages** (left sidebar)
3. Under "Source", select **GitHub Actions**
4. Your store will be live at: `https://nazmulaminashiq-coder.github.io/SellBuddy/store/`

---

## Step 2: Set Up Snipcart

1. Go to https://app.snipcart.com/register
2. Create a FREE account
3. Go to **Account** → **API Keys**
4. Copy your **Public API Key**
5. Update `store/index.html` line 288 with your key:
   ```html
   data-api-key="YOUR_PUBLIC_API_KEY"
   ```

### Configure Webhooks (Optional but Recommended)
1. In Snipcart Dashboard → **Webhooks**
2. Add URL: `https://yourdomain.com/backend/webhooks/snipcart_webhook.php`
3. Select events: `order.completed`, `order.status.changed`

---

## Step 3: Set Up Google Sheets Order Tracking

### Create the Spreadsheet
1. Go to https://sheets.google.com
2. Create a new spreadsheet named "SellBuddy Orders"

### Add the Apps Script
1. Click **Extensions** → **Apps Script**
2. Delete any existing code
3. Copy entire contents from `backend/webhooks/google_sheets_setup.js`
4. Click **Save** (Ctrl+S)

### Deploy as Web App
1. Click **Deploy** → **New deployment**
2. Type: **Web app**
3. Execute as: **Me**
4. Who has access: **Anyone**
5. Click **Deploy**
6. Copy the Web App URL (looks like: `https://script.google.com/macros/s/XXXXX/exec`)

### Add to Environment
Set the `GOOGLE_SHEETS_WEBHOOK` environment variable to your Web App URL.

---

## Step 4: Enable GitHub Actions

GitHub Actions run automatically. To verify:

1. Go to your repository
2. Click **Actions** tab
3. You should see these workflows:
   - **Deploy Store to GitHub Pages** - Runs on push & daily
   - **Autonomous Daily Operations** - Runs daily at 8 AM UTC
   - **Daily Product Research** - Runs daily at 6 AM UTC
   - **Social Media Posting** - Runs every 6 hours

### Enable Workflows (if disabled)
1. Click on each workflow
2. Click **Enable workflow** button

### Add Secrets (for auto-push)
1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   - `GOOGLE_SHEETS_WEBHOOK` - Your Apps Script URL
   - `OWNER_EMAIL` - Your email for notifications

---

## Step 5: Run Google Colab Notebook (Optional)

For more control, use the Colab notebook:

1. Open: https://colab.research.google.com
2. File → **Open notebook** → **GitHub**
3. Enter: `nazmulaminashiq-coder/SellBuddy`
4. Select `notebooks/SellBuddy_Autonomous.ipynb`
5. Run all cells

### Schedule Colab (Colab Pro only)
- Enable scheduled execution in Colab settings
- Set to run daily

---

## Step 6: Set Up PayPal Business

1. Go to https://www.paypal.com/bizsignup
2. Create a Business account
3. Get your **Client ID** and **Secret**
4. In Snipcart: **Payment Methods** → Add PayPal

---

## How the Autonomous System Works

### Daily Operations (8 AM UTC)
1. **Product Research Bot** - Finds trending products
2. **Image Fetcher** - Gets free images from Unsplash/Pexels
3. **Content Generator** - Creates viral social media content
4. **Analytics Update** - Generates daily reports
5. **Auto-commit** - Pushes changes to GitHub

### On Each Order
1. Snipcart sends webhook to your endpoint
2. Webhook saves order to `data/orders.json`
3. Order sent to Google Sheets
4. Customer receives confirmation email
5. Owner receives notification

### Weekly
- Performance report generated
- Low-performing products flagged
- Prices automatically adjusted

---

## Customization

### Add New Products
Edit `data/products.json`:
```json
{
  "products": [
    {
      "id": "unique-id",
      "name": "Product Name",
      "description": "Description here",
      "price": 29.99,
      "cost": 12.00,
      "category": "smart-home",
      "images": ["url1", "url2"],
      "rating": 4.5
    }
  ]
}
```

### Change Marketing Hooks
Edit `bots/viral_marketing_bot.py`:
```python
VIRAL_HOOKS_2025 = [
    "your custom hooks here"
]
```

### Adjust Automation Schedule
Edit `.github/workflows/autonomous-daily.yml`:
```yaml
schedule:
  - cron: '0 8 * * *'  # Change time here (UTC)
```

---

## Monitoring

### Check Store
- Live: https://nazmulaminashiq-coder.github.io/SellBuddy/store/

### Check Orders
- Google Sheets: Your "SellBuddy Orders" spreadsheet
- Local: `data/orders.json`

### Check Automation
- GitHub: Actions tab → See workflow runs
- Logs: `data/logs/` folder

### Check Analytics
- Reports: `reports/` folder
- Dashboard: `data/analytics.json`

---

## Troubleshooting

### GitHub Pages Not Working
1. Check Settings → Pages → Ensure "GitHub Actions" is selected
2. Check Actions tab for deployment errors

### Workflows Not Running
1. Check Actions tab → Enable workflow if disabled
2. Verify cron syntax is correct

### Webhooks Not Received
1. Check Snipcart webhook settings
2. Verify your backend is accessible
3. Check `data/logs/` for errors

### Google Sheets Not Updating
1. Re-deploy the Apps Script
2. Check the Web App URL is correct
3. Test with: `curl YOUR_WEBHOOK_URL`

---

## Cost Breakdown (Monthly)

| Item | Cost |
|------|------|
| GitHub Pages | $0 |
| GitHub Actions (2000 min) | $0 |
| Google Sheets | $0 |
| Snipcart | 2% per sale |
| PayPal | ~3% per sale |
| **Total Fixed** | **$0/month** |
| **Per $100 sale** | ~$5 in fees |

---

## Next Steps

1. ✅ Enable GitHub Pages
2. ✅ Set up Snipcart account
3. ✅ Create Google Sheets webhook
4. ✅ Enable GitHub Actions
5. ✅ Set up PayPal Business
6. 🚀 Start promoting your store!

---

## Support

- GitHub Issues: https://github.com/nazmulaminashiq-coder/SellBuddy/issues
- Email: nazmulaminashiq.coder@gmail.com

---

*Last Updated: December 2024*
