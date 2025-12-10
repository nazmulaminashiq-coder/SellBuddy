# SellBuddy - Zero-Budget Dropshipping Automation

A complete dropshipping automation system built with free tools. Start your e-commerce business with under $200.

## Live Store

Visit: [https://nazmulaminashiq-coder.github.io/SellBuddy/store/](https://nazmulaminashiq-coder.github.io/SellBuddy/store/)

## Features

- **Free Store Hosting** - GitHub Pages
- **Shopping Cart** - Snipcart integration
- **6 Automation Bots** - Product research, social media, analytics
- **Daily Reports** - Automated via GitHub Actions
- **24/7 Chat Widget** - Customer support automation

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/nazmulaminashiq-coder/SellBuddy.git
cd SellBuddy
```

### 2. Configure Snipcart

1. Go to [Snipcart](https://snipcart.com/) and create a free account
2. Get your public API key
3. Replace `YOUR_SNIPCART_PUBLIC_API_KEY` in `store/index.html`

### 3. Enable GitHub Pages

1. Go to repository Settings > Pages
2. Set Source to "Deploy from a branch"
3. Select `main` branch and `/store` folder
4. Save and wait for deployment

### 4. Set Up PayPal

1. Create a [PayPal Business](https://www.paypal.com/business) account
2. Link it to Snipcart for payment processing

## Project Structure

```
SellBuddy/
├── store/                    # Frontend store
│   ├── index.html           # Main store page
│   ├── products.js          # Product catalog
│   └── chat_widget.js       # Support chat
├── bots/                     # Automation scripts
│   ├── product_research_bot.py
│   ├── social_media_bot.py
│   ├── supplier_bot.py
│   ├── analytics_dashboard.py
│   ├── influencer_bot.py
│   └── customer_service_bot.py
├── data/                     # Data storage
│   ├── products.json
│   ├── orders.json
│   └── influencers.json
├── reports/                  # Generated reports
│   ├── daily_report.html
│   └── dashboard.html
└── .github/workflows/        # Automation
    ├── daily_research.yml
    ├── weekly_report.yml
    └── social_posting.yml
```

## Automation Bots

### Product Research Bot
Finds trending products, analyzes margins, generates daily reports.

```bash
python bots/product_research_bot.py
```

### Social Media Bot
Generates TikTok captions, video scripts, and weekly content schedules.

```bash
python bots/social_media_bot.py
```

### Supplier Bot
Tracks supplier prices, calculates actual profit after fees.

```bash
python bots/supplier_bot.py
```

### Analytics Dashboard
Creates visual dashboard with revenue, orders, and performance metrics.

```bash
python bots/analytics_dashboard.py
```

### Influencer Bot
Finds micro-influencers, generates personalized outreach messages.

```bash
python bots/influencer_bot.py
```

### Customer Service Bot
Automated FAQ responses, order tracking, email templates.

```bash
python bots/customer_service_bot.py
```

## GitHub Actions

Automated workflows run on schedule:

| Workflow | Schedule | Description |
|----------|----------|-------------|
| Daily Research | 8 AM UTC | Product trend analysis |
| Weekly Report | Monday 9 AM | Analytics & supplier analysis |
| Social Content | 6 AM UTC | Generate daily content |

## Free Tools Stack

| Function | Tool | Cost |
|----------|------|------|
| Hosting | GitHub Pages | Free |
| Cart | Snipcart | Free (test mode) |
| Payments | PayPal | 2.9% + $0.30 |
| Email | Zoho Mail | Free (5 users) |
| Marketing | Mailchimp | Free (500 contacts) |
| Chat | Tawk.to | Free |
| Analytics | Google Analytics | Free |
| Graphics | Canva | Free |
| Scheduling | Buffer | Free (3 channels) |

## Recommended Products

| Product | Cost | Retail | Margin |
|---------|------|--------|--------|
| Galaxy Star Projector | $12 | $35 | 66% |
| LED Strip Lights | $8 | $28 | 71% |
| Posture Corrector | $6 | $20 | 70% |
| Photo Necklace | $10 | $30 | 67% |
| Portable Blender | $8 | $25 | 68% |

## 60-Day Roadmap

**Week 1-2:** Deploy store, set up accounts, start content posting
**Week 3-4:** Target 5-15 orders, $150-500 revenue
**Week 5-8:** Scale to 40-100 orders, $1,000-2,500 revenue

## Legal Notes

- Start informal, register after $500+/month
- Avoid branded/trademarked items
- No electronics without proper certification
- Use product images legally (request from suppliers)

## Support

- Email: support@sellbuddy.com
- Response time: Within 24 hours

## License

MIT License - Free to use and modify.

---

Built with automation in mind. Start selling today!
