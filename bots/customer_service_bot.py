#!/usr/bin/env python3
"""
SellBuddy Customer Service Bot
Handles automated FAQ responses, order status, and support ticket management.
"""

import json
import re
from datetime import datetime
from pathlib import Path

# FAQ Database
FAQ_DATABASE = {
    "shipping": {
        "keywords": ["shipping", "delivery", "ship", "arrive", "how long", "track", "tracking", "days"],
        "response": """**Shipping Information**

Our standard shipping takes 7-15 business days depending on your location.

- **US Orders**: 7-12 business days
- **Canada/UK**: 10-15 business days
- **Other Countries**: 12-20 business days

You'll receive a tracking number via email once your order ships (usually within 1-2 business days).

Free shipping on orders over $50!"""
    },
    "returns": {
        "keywords": ["return", "refund", "money back", "exchange", "wrong item", "damaged", "broken"],
        "response": """**Returns & Refunds**

We offer a 30-day money-back guarantee on all products!

**To request a return:**
1. Email support@sellbuddy.com with your order number
2. Include reason for return and photos if damaged
3. We'll process your refund within 48 hours

**Note:** For damaged items, please keep the original packaging for potential carrier claims."""
    },
    "order_status": {
        "keywords": ["order status", "where is my order", "track order", "order number", "when will"],
        "response": """**Checking Your Order Status**

To check your order status:
1. Look for the tracking email we sent after your order shipped
2. Click the tracking link to see real-time updates

Can't find your tracking email? Reply with your order number (starts with SB-) and we'll look it up for you!

Orders typically process within 1-2 business days before shipping."""
    },
    "payment": {
        "keywords": ["payment", "pay", "credit card", "paypal", "checkout", "secure", "card declined"],
        "response": """**Payment Information**

We accept:
- PayPal (recommended)
- All major credit cards (Visa, Mastercard, Amex)
- Apple Pay & Google Pay

Your payment is 100% secure with SSL encryption. We never store your card details.

Having trouble checking out? Try using PayPal or a different browser."""
    },
    "product_quality": {
        "keywords": ["quality", "real", "authentic", "legit", "fake", "good", "reviews", "trustworthy"],
        "response": """**Product Quality**

All SellBuddy products are:
- Carefully sourced from vetted suppliers
- Quality-tested before listing
- Backed by our 30-day guarantee

We have thousands of happy customers! While we source products globally, we ensure each item meets our quality standards.

Not satisfied? We'll make it right with a full refund."""
    },
    "discount": {
        "keywords": ["discount", "coupon", "code", "sale", "promo", "deal", "cheaper"],
        "response": """**Discounts & Deals**

Current offers:
- **WELCOME10** - 10% off your first order
- **FREE SHIPPING** on orders $50+

Sign up for our newsletter to get exclusive deals!

Follow us on TikTok and Instagram for flash sales and giveaways."""
    },
    "contact": {
        "keywords": ["contact", "email", "phone", "support", "help", "talk", "human", "agent", "speak"],
        "response": """**Contact Us**

**Email:** support@sellbuddy.com
**Response Time:** Within 24 hours (usually faster!)

For faster service, include:
- Your order number (if applicable)
- Clear description of your issue
- Any relevant photos

Our team is here Monday-Friday, 9 AM - 6 PM EST."""
    },
    "cancel": {
        "keywords": ["cancel", "cancellation", "stop order", "don't want"],
        "response": """**Order Cancellation**

To cancel an order:
1. Email support@sellbuddy.com ASAP with your order number
2. Include "CANCEL ORDER" in the subject line

**Important:** We process orders quickly! If your order has already shipped, we cannot cancel it, but you can return it for a full refund once received.

Cancellation requests within 2 hours of ordering are usually successful."""
    }
}

# Default response when no match found
DEFAULT_RESPONSE = """Thanks for reaching out!

I couldn't find a specific answer to your question, but I'd be happy to help.

**Quick links:**
- Shipping info: 7-15 business days
- Returns: 30-day money-back guarantee
- Contact: support@sellbuddy.com

Please reply with more details or email us directly, and we'll get back to you within 24 hours!"""


def find_best_response(message):
    """Find the best FAQ response for a customer message."""
    message_lower = message.lower()

    best_match = None
    best_score = 0

    for category, data in FAQ_DATABASE.items():
        score = 0
        for keyword in data["keywords"]:
            if keyword in message_lower:
                # Weight longer keyword matches higher
                score += len(keyword)

        if score > best_score:
            best_score = score
            best_match = category

    if best_match and best_score > 3:
        return FAQ_DATABASE[best_match]["response"], best_match
    return DEFAULT_RESPONSE, "unknown"


def extract_order_number(message):
    """Extract order number from message."""
    patterns = [
        r'SB-\d+',
        r'#\d{4,}',
        r'order\s*#?\s*(\d{4,})',
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group()
    return None


def lookup_order(order_number):
    """Look up order status (simulated)."""
    # In production, query your order database
    statuses = ["Processing", "Shipped", "In Transit", "Out for Delivery", "Delivered"]
    import random
    return {
        "order_number": order_number,
        "status": random.choice(statuses),
        "tracking": "TRK" + str(random.randint(100000000, 999999999)),
        "estimated_delivery": "December 20-25, 2025"
    }


def generate_auto_response(message):
    """Generate automated response to customer inquiry."""
    # Check for order number
    order_number = extract_order_number(message)
    if order_number:
        order_info = lookup_order(order_number)
        return f"""**Order Status: {order_info['order_number']}**

Status: **{order_info['status']}**
Tracking: {order_info['tracking']}
Estimated Delivery: {order_info['estimated_delivery']}

Track your package: https://track.example.com/{order_info['tracking']}

Questions? Reply to this message or email support@sellbuddy.com"""

    # Find FAQ match
    response, category = find_best_response(message)
    return response


def generate_email_template(template_type, order_data=None):
    """Generate email templates for various scenarios."""
    templates = {
        "order_confirmation": f"""
Subject: Order Confirmed! #{order_data.get('order_number', 'SB-XXXX')}

Hi {order_data.get('customer_name', 'there')}!

Thank you for your order! We're excited to get your items to you.

**Order Details:**
- Order Number: {order_data.get('order_number', 'SB-XXXX')}
- Items: {order_data.get('items', 'Your items')}
- Total: ${order_data.get('total', '0.00')}

**What's Next:**
1. We'll process your order within 1-2 business days
2. You'll receive a tracking number once it ships
3. Delivery takes 7-15 business days

Questions? Reply to this email!

Thanks for shopping with SellBuddy!
""",
        "shipping_notification": f"""
Subject: Your Order Has Shipped! #{order_data.get('order_number', 'SB-XXXX')}

Great news, {order_data.get('customer_name', 'there')}!

Your order is on its way!

**Tracking Information:**
- Tracking Number: {order_data.get('tracking', 'TRKXXXXXXX')}
- Carrier: {order_data.get('carrier', 'Standard Shipping')}
- Estimated Delivery: {order_data.get('eta', '7-15 business days')}

Track your package: https://track.example.com/{order_data.get('tracking', '')}

Thanks for your patience!

SellBuddy Team
""",
        "refund_processed": f"""
Subject: Refund Processed - #{order_data.get('order_number', 'SB-XXXX')}

Hi {order_data.get('customer_name', 'there')},

Your refund has been processed!

**Refund Details:**
- Order Number: {order_data.get('order_number', 'SB-XXXX')}
- Refund Amount: ${order_data.get('refund_amount', '0.00')}
- Method: Original payment method

Refunds typically appear within 5-10 business days.

We're sorry this purchase didn't work out. We hope to see you again!

SellBuddy Team
"""
    }
    return templates.get(template_type, templates["order_confirmation"])


def process_support_ticket(ticket):
    """Process and categorize a support ticket."""
    response = generate_auto_response(ticket["message"])
    _, category = find_best_response(ticket["message"])

    return {
        "ticket_id": ticket.get("id", f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
        "customer_email": ticket.get("email", "unknown"),
        "category": category,
        "auto_response": response,
        "needs_human": category == "unknown",
        "priority": "high" if any(w in ticket["message"].lower() for w in ["urgent", "asap", "refund", "damaged"]) else "normal",
        "created": datetime.now().isoformat()
    }


def main():
    """Main function to demonstrate customer service bot."""
    print("=" * 50)
    print("SellBuddy Customer Service Bot")
    print("=" * 50)
    print()

    # Test messages
    test_messages = [
        "How long does shipping take?",
        "I want to return my order SB-1234",
        "Where is my order? Order number is SB-5678",
        "Do you have any discount codes?",
        "Is this product authentic?",
        "I need to speak to someone about a damaged item",
    ]

    print("TESTING AUTOMATED RESPONSES:")
    print("-" * 30)

    for msg in test_messages:
        print(f"\nCustomer: \"{msg}\"")
        print("\nBot Response:")
        response = generate_auto_response(msg)
        print(response[:300] + "..." if len(response) > 300 else response)
        print("-" * 30)

    # Test email template
    print("\n\nSAMPLE EMAIL TEMPLATE:")
    print("-" * 30)
    order_data = {
        "order_number": "SB-1234",
        "customer_name": "John",
        "items": "Galaxy Star Projector x1",
        "total": "34.99"
    }
    email = generate_email_template("order_confirmation", order_data)
    print(email)

    print("\n" + "=" * 50)
    print("Customer service bot ready!")
    print("=" * 50)


if __name__ == "__main__":
    main()
