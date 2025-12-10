#!/usr/bin/env python3
"""
SellBuddy Supplier Sourcing Bot
Tracks supplier prices, calculates margins, and manages fulfillment queue.
"""

import json
import csv
from datetime import datetime
from pathlib import Path

# Fee structure
FEES = {
    "paypal": 0.029,  # 2.9%
    "paypal_fixed": 0.30,  # $0.30 per transaction
    "snipcart": 0.02,  # 2% on free plan
    "shipping_avg": 3.50,  # Average shipping cost from supplier
}

# Simulated supplier data
SUPPLIERS = {
    "aliexpress": {
        "name": "AliExpress",
        "shipping_time": "15-30 days",
        "shipping_methods": ["Standard", "ePacket", "AliExpress Standard"],
        "reliability": 85
    },
    "cjdropshipping": {
        "name": "CJ Dropshipping",
        "shipping_time": "8-15 days",
        "shipping_methods": ["CJPacket", "USPS", "DHL"],
        "reliability": 90
    },
    "spocket": {
        "name": "Spocket",
        "shipping_time": "3-7 days",
        "shipping_methods": ["US Suppliers", "EU Suppliers"],
        "reliability": 95
    }
}


def calculate_profit(retail_price, supplier_cost, shipping_cost=None):
    """Calculate actual profit after all fees."""
    if shipping_cost is None:
        shipping_cost = FEES["shipping_avg"]

    # Revenue
    gross_revenue = retail_price

    # Costs
    product_cost = supplier_cost + shipping_cost
    paypal_fee = (retail_price * FEES["paypal"]) + FEES["paypal_fixed"]
    snipcart_fee = retail_price * FEES["snipcart"]

    total_costs = product_cost + paypal_fee + snipcart_fee

    # Profit
    net_profit = gross_revenue - total_costs
    margin = (net_profit / retail_price) * 100 if retail_price > 0 else 0

    return {
        "gross_revenue": round(retail_price, 2),
        "product_cost": round(supplier_cost, 2),
        "shipping_cost": round(shipping_cost, 2),
        "paypal_fee": round(paypal_fee, 2),
        "snipcart_fee": round(snipcart_fee, 2),
        "total_costs": round(total_costs, 2),
        "net_profit": round(net_profit, 2),
        "margin": round(margin, 1)
    }


def analyze_product_profitability(products):
    """Analyze profitability for a list of products."""
    results = []
    for p in products:
        profit_data = calculate_profit(p["retail"], p["cost"], p.get("shipping", FEES["shipping_avg"]))
        results.append({
            "product": p["name"],
            "supplier": p.get("supplier", "AliExpress"),
            **profit_data,
            "recommendation": "Good" if profit_data["margin"] > 40 else "Review" if profit_data["margin"] > 25 else "Avoid"
        })
    return results


def generate_fulfillment_csv(orders):
    """Generate CSV file for order fulfillment."""
    output_path = Path(__file__).parent.parent / "data" / "fulfillment_queue.csv"

    fieldnames = [
        "order_id", "customer_name", "email", "product", "variant",
        "quantity", "address_line1", "address_line2", "city", "state",
        "zip_code", "country", "supplier", "supplier_sku", "status"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for order in orders:
            writer.writerow(order)

    print(f"Fulfillment CSV saved to: {output_path}")
    return str(output_path)


def check_price_changes(products, threshold=10):
    """Check for significant price changes from suppliers."""
    alerts = []
    for p in products:
        # Simulated price check (in production, scrape actual prices)
        current_price = p["cost"]
        previous_price = p.get("previous_cost", current_price)

        if previous_price > 0:
            change_pct = ((current_price - previous_price) / previous_price) * 100

            if abs(change_pct) >= threshold:
                alerts.append({
                    "product": p["name"],
                    "previous": previous_price,
                    "current": current_price,
                    "change": round(change_pct, 1),
                    "action": "PRICE INCREASE" if change_pct > 0 else "PRICE DROP"
                })

    return alerts


def compare_suppliers(product_name, supplier_data):
    """Compare prices and shipping times across suppliers."""
    comparison = []
    for supplier, data in supplier_data.items():
        comparison.append({
            "supplier": data["name"],
            "price": data.get("price", 0),
            "shipping_time": data["shipping_time"],
            "reliability": data["reliability"],
            "total_cost": data.get("price", 0) + data.get("shipping", FEES["shipping_avg"])
        })

    comparison.sort(key=lambda x: x["total_cost"])
    return comparison


def main():
    """Main function to run supplier analysis."""
    print("=" * 50)
    print("SellBuddy Supplier Sourcing Bot")
    print("=" * 50)
    print()

    # Sample products
    products = [
        {"name": "Galaxy Star Projector", "cost": 12.00, "retail": 34.99, "supplier": "AliExpress"},
        {"name": "LED Strip Lights", "cost": 8.00, "retail": 27.99, "supplier": "AliExpress"},
        {"name": "Posture Corrector", "cost": 6.00, "retail": 19.99, "supplier": "CJ Dropshipping"},
        {"name": "Photo Necklace", "cost": 10.00, "retail": 29.99, "supplier": "AliExpress"},
        {"name": "Portable Blender", "cost": 8.00, "retail": 24.99, "supplier": "CJ Dropshipping"},
    ]

    # Analyze profitability
    print("PROFITABILITY ANALYSIS:")
    print("-" * 30)
    results = analyze_product_profitability(products)
    for r in results:
        print(f"\n{r['product']}:")
        print(f"  Retail: ${r['gross_revenue']} | Cost: ${r['product_cost']} | Shipping: ${r['shipping_cost']}")
        print(f"  Fees: PayPal ${r['paypal_fee']} + Snipcart ${r['snipcart_fee']}")
        print(f"  Net Profit: ${r['net_profit']} ({r['margin']}% margin)")
        print(f"  Recommendation: {r['recommendation']}")

    # Check price changes
    print("\n" + "=" * 50)
    print("PRICE ALERTS:")
    print("-" * 30)
    products_with_history = [
        {"name": "Galaxy Star Projector", "cost": 13.00, "previous_cost": 12.00},
        {"name": "LED Strip Lights", "cost": 7.00, "previous_cost": 8.00},
    ]
    alerts = check_price_changes(products_with_history, threshold=5)
    if alerts:
        for a in alerts:
            print(f"  {a['action']}: {a['product']} - ${a['previous']} -> ${a['current']} ({a['change']:+.1f}%)")
    else:
        print("  No significant price changes detected.")

    # Generate sample fulfillment queue
    print("\n" + "=" * 50)
    print("FULFILLMENT QUEUE:")
    print("-" * 30)
    sample_orders = [
        {
            "order_id": "SB-001",
            "customer_name": "John Doe",
            "email": "john@example.com",
            "product": "Galaxy Star Projector",
            "variant": "Blue",
            "quantity": 1,
            "address_line1": "123 Main St",
            "address_line2": "",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "country": "US",
            "supplier": "AliExpress",
            "supplier_sku": "SKU123456",
            "status": "Pending"
        }
    ]
    csv_path = generate_fulfillment_csv(sample_orders)
    print(f"  Generated fulfillment CSV: {csv_path}")

    print("\n" + "=" * 50)
    print("Supplier analysis complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
