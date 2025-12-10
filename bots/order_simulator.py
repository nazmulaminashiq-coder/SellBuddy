#!/usr/bin/env python3
"""
SellBuddy - Order Simulator

Simulates test orders to verify the webhook system works correctly.
Use this during setup to test your Google Sheets integration.

Usage:
    python order_simulator.py              # Simulate 1 order
    python order_simulator.py --count 5    # Simulate 5 orders
    python order_simulator.py --webhook URL # Test specific webhook
"""

import json
import random
import argparse
import requests
from datetime import datetime
from pathlib import Path

# Sample data for simulation
SAMPLE_CUSTOMERS = [
    {"name": "John Smith", "email": "john.smith@example.com", "phone": "+1-555-0101"},
    {"name": "Sarah Johnson", "email": "sarah.j@example.com", "phone": "+1-555-0102"},
    {"name": "Mike Williams", "email": "mike.w@example.com", "phone": "+1-555-0103"},
    {"name": "Emily Brown", "email": "emily.b@example.com", "phone": "+1-555-0104"},
    {"name": "David Lee", "email": "david.lee@example.com", "phone": "+1-555-0105"},
    {"name": "Jessica Davis", "email": "jess.d@example.com", "phone": "+1-555-0106"},
    {"name": "Chris Miller", "email": "chris.m@example.com", "phone": "+1-555-0107"},
    {"name": "Amanda Wilson", "email": "amanda.w@example.com", "phone": "+1-555-0108"},
]

SAMPLE_ADDRESSES = [
    "123 Main St, New York, NY 10001, USA",
    "456 Oak Ave, Los Angeles, CA 90001, USA",
    "789 Pine Rd, Chicago, IL 60601, USA",
    "321 Elm St, Houston, TX 77001, USA",
    "654 Maple Dr, Phoenix, AZ 85001, USA",
    "987 Cedar Ln, Philadelphia, PA 19101, USA",
    "147 Birch Ct, San Antonio, TX 78201, USA",
    "258 Walnut Way, San Diego, CA 92101, USA",
]

# Load products
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent


def load_products():
    """Load products from data file"""
    products_file = PROJECT_ROOT / "data" / "products.json"

    if products_file.exists():
        with open(products_file, 'r') as f:
            data = json.load(f)
            return data.get('products', [])

    # Fallback products
    return [
        {"id": "galaxy-projector", "name": "Galaxy Projector", "price": 39.99},
        {"id": "led-strip-lights", "name": "LED Strip Lights", "price": 24.99},
        {"id": "posture-corrector", "name": "Posture Corrector", "price": 29.99},
        {"id": "pet-water-fountain", "name": "Pet Water Fountain", "price": 34.99},
    ]


def generate_order_id():
    """Generate unique order ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))
    return f"SB-{timestamp}-{random_part}"


def generate_order():
    """Generate a random test order"""
    products = load_products()
    customer = random.choice(SAMPLE_CUSTOMERS)
    address = random.choice(SAMPLE_ADDRESSES)

    # Random 1-3 items
    num_items = random.randint(1, 3)
    selected_products = random.sample(products, min(num_items, len(products)))

    items = []
    subtotal = 0

    for product in selected_products:
        quantity = random.randint(1, 2)
        price = product.get('price', 29.99)
        items.append({
            "name": product.get('name', 'Unknown Product'),
            "quantity": quantity,
            "price": price,
            "sku": product.get('id', 'unknown')
        })
        subtotal += price * quantity

    shipping = 4.99 if subtotal < 50 else 0
    tax = round(subtotal * 0.08, 2)  # 8% tax
    total = round(subtotal + shipping + tax, 2)

    order = {
        "order_id": generate_order_id(),
        "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "customer_name": customer["name"],
        "customer_email": customer["email"],
        "phone": customer["phone"],
        "items": ", ".join([f"{item['name']} x{item['quantity']}" for item in items]),
        "subtotal": round(subtotal, 2),
        "shipping": shipping,
        "tax": tax,
        "total": total,
        "shipping_address": address,
        "status": "confirmed"
    }

    return order


def save_order_locally(order):
    """Save order to local JSON file"""
    orders_file = PROJECT_ROOT / "data" / "orders.json"

    orders = {"orders": [], "stats": {"revenue": 0, "orders_count": 0}}
    if orders_file.exists():
        with open(orders_file, 'r') as f:
            orders = json.load(f)

    orders["orders"].append({
        "id": order["order_id"],
        "date": order["date"],
        "customer": order["customer_name"],
        "email": order["customer_email"],
        "product": order["items"].split(',')[0] if order["items"] else "Unknown",
        "quantity": 1,
        "total": order["total"],
        "status": order["status"]
    })

    orders["stats"]["revenue"] += order["total"]
    orders["stats"]["orders_count"] += 1
    orders["stats"]["last_order"] = order["date"]

    with open(orders_file, 'w') as f:
        json.dump(orders, f, indent=2)

    return True


def send_to_webhook(order, webhook_url):
    """Send order to webhook endpoint"""
    try:
        response = requests.post(
            webhook_url,
            json=order,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return response.status_code == 200, response.text
    except Exception as e:
        return False, str(e)


def simulate_orders(count=1, webhook_url=None, verbose=True):
    """Simulate multiple orders"""
    results = []

    for i in range(count):
        order = generate_order()

        if verbose:
            print(f"\n{'='*60}")
            print(f"ORDER #{i+1}: {order['order_id']}")
            print(f"{'='*60}")
            print(f"Customer: {order['customer_name']} ({order['customer_email']})")
            print(f"Items: {order['items']}")
            print(f"Total: ${order['total']}")
            print(f"Address: {order['shipping_address']}")

        # Save locally
        save_order_locally(order)
        if verbose:
            print("✅ Saved to local orders.json")

        # Send to webhook if provided
        if webhook_url:
            success, response = send_to_webhook(order, webhook_url)
            if success:
                print(f"✅ Sent to webhook: {webhook_url}")
            else:
                print(f"❌ Webhook failed: {response}")
            results.append({"order": order, "webhook_success": success})
        else:
            results.append({"order": order, "webhook_success": None})

    return results


def main():
    parser = argparse.ArgumentParser(description='Simulate test orders for SellBuddy')
    parser.add_argument('--count', '-c', type=int, default=1, help='Number of orders to simulate')
    parser.add_argument('--webhook', '-w', type=str, help='Webhook URL to send orders to')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress output')

    args = parser.parse_args()

    print("\n🛒 SellBuddy Order Simulator")
    print("="*60)

    results = simulate_orders(
        count=args.count,
        webhook_url=args.webhook,
        verbose=not args.quiet
    )

    print(f"\n{'='*60}")
    print(f"✅ Simulated {len(results)} order(s)")

    total_revenue = sum(r['order']['total'] for r in results)
    print(f"💰 Total simulated revenue: ${total_revenue:.2f}")

    if args.webhook:
        successful = sum(1 for r in results if r['webhook_success'])
        print(f"📤 Webhook deliveries: {successful}/{len(results)}")


if __name__ == "__main__":
    main()
