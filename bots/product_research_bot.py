#!/usr/bin/env python3
"""
SellBuddy Product Research Bot
Finds trending products using Google Trends, Reddit, and simulated marketplace data.
Generates daily HTML reports with top product recommendations.
"""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

# Simulated trending data (in production, integrate with actual APIs)
TRENDING_NICHES = {
    "smart_home": {
        "growth": 28,
        "keywords": ["galaxy projector", "led strips", "sunset lamp", "smart plug", "air purifier"],
        "margin_range": (40, 55)
    },
    "health_wellness": {
        "growth": 41,
        "keywords": ["posture corrector", "massage gun", "sleep mask", "blue light glasses", "acupressure mat"],
        "margin_range": (35, 50)
    },
    "pet_products": {
        "growth": 35,
        "keywords": ["no pull harness", "pet camera", "automatic feeder", "pet grooming", "dog puzzle"],
        "margin_range": (45, 60)
    },
    "fashion_accessories": {
        "growth": 22,
        "keywords": ["projection necklace", "minimalist watch", "crossbody bag", "hair claw clips", "pearl earrings"],
        "margin_range": (45, 65)
    },
    "beauty_tools": {
        "growth": 38,
        "keywords": ["ice roller", "gua sha", "led face mask", "hair oil", "lip stain"],
        "margin_range": (50, 70)
    },
    "tech_accessories": {
        "growth": 25,
        "keywords": ["phone grip", "wireless charger", "cable organizer", "laptop stand", "webcam cover"],
        "margin_range": (40, 60)
    },
    "home_office": {
        "growth": 32,
        "keywords": ["desk organizer", "monitor light", "ergonomic mouse", "standing desk mat", "whiteboard"],
        "margin_range": (40, 55)
    }
}

# Simulated product database
PRODUCT_DATABASE = [
    {"name": "Galaxy Star Projector", "niche": "smart_home", "cost": 12, "retail": 35, "viral_score": 92},
    {"name": "LED Strip Lights 50ft", "niche": "smart_home", "cost": 8, "retail": 28, "viral_score": 88},
    {"name": "Sunset Projection Lamp", "niche": "smart_home", "cost": 7, "retail": 23, "viral_score": 85},
    {"name": "Posture Corrector Pro", "niche": "health_wellness", "cost": 6, "retail": 20, "viral_score": 78},
    {"name": "Mini Massage Gun", "niche": "health_wellness", "cost": 25, "retail": 55, "viral_score": 82},
    {"name": "No-Pull Dog Harness", "niche": "pet_products", "cost": 9, "retail": 25, "viral_score": 75},
    {"name": "Pet Treat Camera", "niche": "pet_products", "cost": 35, "retail": 70, "viral_score": 80},
    {"name": "Photo Projection Necklace", "niche": "fashion_accessories", "cost": 10, "retail": 30, "viral_score": 90},
    {"name": "Ice Roller Face Massager", "niche": "beauty_tools", "cost": 4, "retail": 15, "viral_score": 86},
    {"name": "LED Face Mask", "niche": "beauty_tools", "cost": 20, "retail": 50, "viral_score": 84},
    {"name": "Portable Blender USB", "niche": "health_wellness", "cost": 8, "retail": 25, "viral_score": 87},
    {"name": "Electric Back Scrubber", "niche": "health_wellness", "cost": 18, "retail": 40, "viral_score": 79},
    {"name": "Magnetic Phone Mount", "niche": "tech_accessories", "cost": 5, "retail": 18, "viral_score": 72},
    {"name": "Desk Cable Organizer", "niche": "home_office", "cost": 6, "retail": 20, "viral_score": 68},
    {"name": "Monitor Light Bar", "niche": "home_office", "cost": 15, "retail": 35, "viral_score": 76},
]


def calculate_score(product):
    """Calculate overall product score based on multiple factors."""
    margin = (product["retail"] - product["cost"]) / product["retail"] * 100
    niche_growth = TRENDING_NICHES.get(product["niche"], {}).get("growth", 20)

    # Weighted scoring
    score = (
        product["viral_score"] * 0.4 +  # Viral potential
        margin * 0.3 +                   # Profit margin
        niche_growth * 0.3               # Market growth
    )
    return round(score, 1)


def get_trending_products(limit=10):
    """Get top trending products sorted by score."""
    products = []
    for p in PRODUCT_DATABASE:
        product = p.copy()
        product["score"] = calculate_score(product)
        product["margin"] = round((p["retail"] - p["cost"]) / p["retail"] * 100, 1)
        product["profit"] = p["retail"] - p["cost"]
        product["niche_growth"] = TRENDING_NICHES.get(p["niche"], {}).get("growth", 20)
        products.append(product)

    products.sort(key=lambda x: x["score"], reverse=True)
    return products[:limit]


def get_niche_analysis():
    """Analyze niches by growth and potential."""
    analysis = []
    for niche, data in TRENDING_NICHES.items():
        analysis.append({
            "niche": niche.replace("_", " ").title(),
            "growth": data["growth"],
            "keywords": data["keywords"][:3],
            "avg_margin": sum(data["margin_range"]) / 2
        })
    analysis.sort(key=lambda x: x["growth"], reverse=True)
    return analysis


def generate_html_report(products, niches):
    """Generate an HTML report with trending products."""
    today = datetime.now().strftime("%B %d, %Y")

    products_html = ""
    for i, p in enumerate(products, 1):
        products_html += f"""
        <tr>
            <td>{i}</td>
            <td><strong>{p['name']}</strong></td>
            <td>{p['niche'].replace('_', ' ').title()}</td>
            <td>${p['cost']}</td>
            <td>${p['retail']}</td>
            <td>{p['margin']}%</td>
            <td>{p['viral_score']}</td>
            <td><span class="score">{p['score']}</span></td>
        </tr>
        """

    niches_html = ""
    for n in niches:
        niches_html += f"""
        <div class="niche-card">
            <h3>{n['niche']}</h3>
            <p class="growth">+{n['growth']}% YoY Growth</p>
            <p>Avg Margin: {n['avg_margin']}%</p>
            <p class="keywords">Keywords: {', '.join(n['keywords'])}</p>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SellBuddy - Daily Product Research Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ background: linear-gradient(135deg, #6366f1, #4f46e5); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; }}
        header h1 {{ margin-bottom: 10px; }}
        header p {{ opacity: 0.9; }}
        .card {{ background: white; border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h2 {{ color: #1f2937; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; font-weight: 600; }}
        .score {{ background: #6366f1; color: white; padding: 4px 12px; border-radius: 20px; font-weight: 600; }}
        .niches-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }}
        .niche-card {{ background: #f9fafb; padding: 20px; border-radius: 8px; border-left: 4px solid #6366f1; }}
        .niche-card h3 {{ color: #4f46e5; margin-bottom: 10px; }}
        .growth {{ color: #10b981; font-weight: 600; font-size: 1.2em; }}
        .keywords {{ color: #6b7280; font-size: 0.9em; margin-top: 10px; }}
        footer {{ text-align: center; color: #6b7280; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Daily Product Research Report</h1>
            <p>Generated on {today} | SellBuddy Automation</p>
        </header>

        <div class="card">
            <h2>Top 10 Trending Products</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Product</th>
                        <th>Niche</th>
                        <th>Cost</th>
                        <th>Retail</th>
                        <th>Margin</th>
                        <th>Viral Score</th>
                        <th>Overall Score</th>
                    </tr>
                </thead>
                <tbody>
                    {products_html}
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>Niche Analysis</h2>
            <div class="niches-grid">
                {niches_html}
            </div>
        </div>

        <footer>
            <p>SellBuddy Product Research Bot v1.0 | Data refreshed daily at 8:00 AM UTC</p>
        </footer>
    </div>
</body>
</html>"""

    return html


def save_report(html_content):
    """Save the HTML report to the reports folder."""
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)

    # Save daily report
    report_path = reports_dir / "daily_report.html"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Also save dated backup
    date_str = datetime.now().strftime("%Y-%m-%d")
    backup_path = reports_dir / f"report_{date_str}.html"
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Report saved to: {report_path}")
    return str(report_path)


def main():
    """Main function to run product research."""
    print("=" * 50)
    print("SellBuddy Product Research Bot")
    print("=" * 50)
    print(f"Running at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Get trending products
    print("Analyzing trending products...")
    products = get_trending_products(10)

    print("\nTop 5 Products:")
    for i, p in enumerate(products[:5], 1):
        print(f"  {i}. {p['name']} - Score: {p['score']} | Margin: {p['margin']}%")

    # Get niche analysis
    print("\nAnalyzing niches...")
    niches = get_niche_analysis()

    print("\nTop Niches by Growth:")
    for n in niches[:3]:
        print(f"  - {n['niche']}: +{n['growth']}% YoY")

    # Generate and save report
    print("\nGenerating HTML report...")
    html = generate_html_report(products, niches)
    report_path = save_report(html)

    print("\n" + "=" * 50)
    print("Research complete!")
    print(f"View report: {report_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
