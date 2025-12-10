#!/usr/bin/env python3
"""
SellBuddy Analytics Dashboard
Generates visual analytics dashboard with revenue, profit, and performance metrics.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import random

def load_orders():
    """Load orders from JSON file or return sample data."""
    orders_path = Path(__file__).parent.parent / "data" / "orders.json"
    try:
        with open(orders_path, "r") as f:
            data = json.load(f)
            return data.get("orders", [])
    except:
        # Return sample data for demo
        return generate_sample_data()


def generate_sample_data():
    """Generate sample order data for demonstration."""
    products = [
        {"name": "Galaxy Star Projector", "price": 34.99, "cost": 12.00},
        {"name": "LED Strip Lights", "price": 27.99, "cost": 8.00},
        {"name": "Posture Corrector", "price": 19.99, "cost": 6.00},
        {"name": "Photo Necklace", "price": 29.99, "cost": 10.00},
        {"name": "Portable Blender", "price": 24.99, "cost": 8.00},
    ]

    orders = []
    today = datetime.now()

    for i in range(30):
        date = today - timedelta(days=random.randint(0, 30))
        product = random.choice(products)
        quantity = random.randint(1, 3)

        orders.append({
            "id": f"SB-{1000 + i}",
            "date": date.strftime("%Y-%m-%d"),
            "product": product["name"],
            "quantity": quantity,
            "revenue": round(product["price"] * quantity, 2),
            "cost": round(product["cost"] * quantity, 2),
            "profit": round((product["price"] - product["cost"]) * quantity, 2),
            "status": random.choice(["delivered", "shipped", "processing", "pending"])
        })

    return orders


def calculate_metrics(orders):
    """Calculate key business metrics."""
    if not orders:
        return {
            "total_orders": 0,
            "total_revenue": 0,
            "total_profit": 0,
            "avg_order_value": 0,
            "profit_margin": 0,
            "orders_by_status": {},
            "top_products": [],
            "daily_revenue": []
        }

    total_revenue = sum(o["revenue"] for o in orders)
    total_cost = sum(o["cost"] for o in orders)
    total_profit = sum(o["profit"] for o in orders)

    # Status breakdown
    status_counts = {}
    for o in orders:
        status = o["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    # Top products
    product_sales = {}
    for o in orders:
        product = o["product"]
        if product not in product_sales:
            product_sales[product] = {"units": 0, "revenue": 0}
        product_sales[product]["units"] += o["quantity"]
        product_sales[product]["revenue"] += o["revenue"]

    top_products = sorted(
        [{"name": k, **v} for k, v in product_sales.items()],
        key=lambda x: x["revenue"],
        reverse=True
    )[:5]

    # Daily revenue (last 7 days)
    today = datetime.now()
    daily = {}
    for i in range(7):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        daily[day] = 0

    for o in orders:
        if o["date"] in daily:
            daily[o["date"]] += o["revenue"]

    daily_revenue = [{"date": k, "revenue": round(v, 2)} for k, v in sorted(daily.items())]

    return {
        "total_orders": len(orders),
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2),
        "avg_order_value": round(total_revenue / len(orders), 2) if orders else 0,
        "profit_margin": round((total_profit / total_revenue) * 100, 1) if total_revenue > 0 else 0,
        "orders_by_status": status_counts,
        "top_products": top_products,
        "daily_revenue": daily_revenue
    }


def generate_dashboard_html(metrics):
    """Generate HTML dashboard."""
    today = datetime.now().strftime("%B %d, %Y")

    # Status cards HTML
    status_html = ""
    status_colors = {
        "delivered": "#10b981",
        "shipped": "#6366f1",
        "processing": "#f59e0b",
        "pending": "#6b7280"
    }
    for status, count in metrics["orders_by_status"].items():
        color = status_colors.get(status, "#6b7280")
        status_html += f'<div class="status-badge" style="background: {color}20; color: {color};">{status.title()}: {count}</div>'

    # Top products HTML
    products_html = ""
    for p in metrics["top_products"]:
        products_html += f"""
        <tr>
            <td>{p['name']}</td>
            <td>{p['units']}</td>
            <td>${p['revenue']:.2f}</td>
        </tr>
        """

    # Chart data for daily revenue
    chart_labels = [d["date"][-5:] for d in metrics["daily_revenue"]]
    chart_values = [d["revenue"] for d in metrics["daily_revenue"]]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SellBuddy - Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}

        header {{
            background: linear-gradient(135deg, #6366f1, #4f46e5);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        header h1 {{ margin-bottom: 10px; }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .metric-card h3 {{ color: #6b7280; font-size: 14px; margin-bottom: 10px; }}
        .metric-card .value {{ font-size: 32px; font-weight: 700; color: #1f2937; }}
        .metric-card .positive {{ color: #10b981; }}
        .metric-card .subtext {{ font-size: 12px; color: #6b7280; margin-top: 5px; }}

        .card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .card h2 {{ color: #1f2937; margin-bottom: 20px; }}

        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; font-weight: 600; }}

        .status-badges {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }}
        .status-badge {{ padding: 8px 16px; border-radius: 20px; font-weight: 600; font-size: 14px; }}

        .chart-container {{ height: 300px; }}

        .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }}
        @media (max-width: 768px) {{ .two-col {{ grid-template-columns: 1fr; }} }}

        footer {{ text-align: center; color: #6b7280; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Analytics Dashboard</h1>
            <p>Updated: {today} | SellBuddy Store Performance</p>
        </header>

        <div class="metrics-grid">
            <div class="metric-card">
                <h3>TOTAL ORDERS</h3>
                <div class="value">{metrics['total_orders']}</div>
                <div class="subtext">All time</div>
            </div>
            <div class="metric-card">
                <h3>TOTAL REVENUE</h3>
                <div class="value positive">${metrics['total_revenue']:,.2f}</div>
                <div class="subtext">Gross sales</div>
            </div>
            <div class="metric-card">
                <h3>TOTAL PROFIT</h3>
                <div class="value positive">${metrics['total_profit']:,.2f}</div>
                <div class="subtext">After costs</div>
            </div>
            <div class="metric-card">
                <h3>AVG ORDER VALUE</h3>
                <div class="value">${metrics['avg_order_value']:.2f}</div>
                <div class="subtext">Per order</div>
            </div>
            <div class="metric-card">
                <h3>PROFIT MARGIN</h3>
                <div class="value positive">{metrics['profit_margin']}%</div>
                <div class="subtext">Net margin</div>
            </div>
        </div>

        <div class="card">
            <h2>Order Status</h2>
            <div class="status-badges">
                {status_html}
            </div>
        </div>

        <div class="two-col">
            <div class="card">
                <h2>Revenue (Last 7 Days)</h2>
                <div class="chart-container">
                    <canvas id="revenueChart"></canvas>
                </div>
            </div>

            <div class="card">
                <h2>Top Products</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Units</th>
                            <th>Revenue</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products_html}
                    </tbody>
                </table>
            </div>
        </div>

        <footer>
            <p>SellBuddy Analytics Dashboard v1.0 | Auto-refreshes daily</p>
        </footer>
    </div>

    <script>
        const ctx = document.getElementById('revenueChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {chart_labels},
                datasets: [{{
                    label: 'Revenue ($)',
                    data: {chart_values},
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

    return html


def save_dashboard(html_content):
    """Save dashboard HTML to reports folder."""
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    dashboard_path = reports_dir / "dashboard.html"
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Dashboard saved to: {dashboard_path}")
    return str(dashboard_path)


def main():
    """Main function to generate analytics dashboard."""
    print("=" * 50)
    print("SellBuddy Analytics Dashboard")
    print("=" * 50)
    print()

    # Load orders
    print("Loading order data...")
    orders = load_orders()
    print(f"Found {len(orders)} orders")

    # Calculate metrics
    print("Calculating metrics...")
    metrics = calculate_metrics(orders)

    # Print summary
    print("\nKEY METRICS:")
    print("-" * 30)
    print(f"  Total Orders: {metrics['total_orders']}")
    print(f"  Total Revenue: ${metrics['total_revenue']:,.2f}")
    print(f"  Total Profit: ${metrics['total_profit']:,.2f}")
    print(f"  Avg Order Value: ${metrics['avg_order_value']:.2f}")
    print(f"  Profit Margin: {metrics['profit_margin']}%")

    print("\nORDER STATUS:")
    for status, count in metrics["orders_by_status"].items():
        print(f"  {status.title()}: {count}")

    print("\nTOP PRODUCTS:")
    for p in metrics["top_products"][:3]:
        print(f"  {p['name']}: {p['units']} units (${p['revenue']:.2f})")

    # Generate and save dashboard
    print("\nGenerating HTML dashboard...")
    html = generate_dashboard_html(metrics)
    dashboard_path = save_dashboard(html)

    print("\n" + "=" * 50)
    print("Dashboard generation complete!")
    print(f"View at: {dashboard_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
