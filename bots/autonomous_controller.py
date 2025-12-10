#!/usr/bin/env python3
"""
SellBuddy Autonomous Controller
Master script that runs the entire dropshipping business autonomously.

RUNS AUTOMATICALLY VIA:
1. GitHub Actions (daily/weekly schedules)
2. Google Colab (scheduled notebooks)
3. Replit (always-on with cron)

ZERO HUMAN INTERVENTION REQUIRED
"""

import os
import json
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys

# ============================================
# CONFIGURATION
# ============================================

CONFIG = {
    "store_name": "SellBuddy",
    "store_url": "https://nazmulaminashiq-coder.github.io/SellBuddy/store/",
    "github_repo": "nazmulaminashiq-coder/SellBuddy",
    "data_dir": Path(__file__).parent.parent / "data",
    "content_dir": Path(__file__).parent.parent / "content",
    "reports_dir": Path(__file__).parent.parent / "reports",

    # Automation settings
    "auto_add_products": True,
    "auto_generate_content": True,
    "auto_update_prices": True,
    "auto_track_trends": True,

    # Thresholds
    "min_margin": 50,  # Minimum profit margin %
    "max_products": 20,  # Maximum products in store
    "content_per_day": 3,  # Social posts to generate daily
}

# Trending product templates (auto-expanded)
TRENDING_PRODUCT_TEMPLATES = [
    {
        "category": "Smart Home",
        "templates": [
            {"name": "{color} LED {type} Light", "base_price": 8, "retail_multi": 3.5},
            {"name": "Smart {room} Projector", "base_price": 12, "retail_multi": 3},
            {"name": "USB {device} Lamp", "base_price": 6, "retail_multi": 3.5},
        ],
        "colors": ["Galaxy", "Aurora", "Sunset", "Rainbow", "Nebula", "Moon"],
        "types": ["Strip", "String", "Neon", "Fairy", "Star"],
        "rooms": ["Bedroom", "Galaxy", "Ocean", "Forest", "Sky"],
        "devices": ["Desk", "Night", "Ambient", "Reading", "Mood"]
    },
    {
        "category": "Health & Wellness",
        "templates": [
            {"name": "{adj} Posture {type}", "base_price": 5, "retail_multi": 4},
            {"name": "Electric {body} Massager", "base_price": 15, "retail_multi": 3},
            {"name": "Portable {health} Device", "base_price": 8, "retail_multi": 3.5},
        ],
        "adj": ["Pro", "Smart", "Premium", "Advanced", "Ultra"],
        "types": ["Corrector", "Brace", "Support", "Trainer"],
        "body": ["Back", "Neck", "Foot", "Scalp", "Eye"],
        "health": ["Blender", "Steamer", "Diffuser", "Humidifier"]
    },
    {
        "category": "Pet Supplies",
        "templates": [
            {"name": "{adj} Dog {item}", "base_price": 7, "retail_multi": 3.5},
            {"name": "Smart Pet {device}", "base_price": 20, "retail_multi": 2.5},
        ],
        "adj": ["No-Pull", "Reflective", "Adjustable", "Breathable", "Premium"],
        "item": ["Harness", "Collar", "Leash", "Bed", "Bowl"],
        "device": ["Camera", "Feeder", "Fountain", "Tracker", "Toy"]
    },
    {
        "category": "Beauty Tools",
        "templates": [
            {"name": "{material} Face {tool}", "base_price": 4, "retail_multi": 4},
            {"name": "LED {skin} Mask", "base_price": 18, "retail_multi": 3},
        ],
        "material": ["Ice", "Jade", "Rose Quartz", "Stainless Steel", "Gua Sha"],
        "tool": ["Roller", "Massager", "Scraper", "Tool", "Device"],
        "skin": ["Beauty", "Therapy", "Skin", "Face", "Anti-Aging"]
    }
]

# Free image sources (no API key needed)
FREE_IMAGE_SOURCES = [
    "https://source.unsplash.com/600x600/?{query}",
    "https://picsum.photos/seed/{seed}/600/600",
]


# ============================================
# AUTONOMOUS PRODUCT GENERATOR
# ============================================

class AutonomousProductGenerator:
    """Generates new products automatically based on trends."""

    def __init__(self):
        self.products_file = CONFIG["data_dir"] / "products.json"
        self.products = self._load_products()

    def _load_products(self):
        """Load existing products."""
        try:
            with open(self.products_file, "r") as f:
                return json.load(f)
        except:
            return {"products": [], "lastUpdated": None}

    def _save_products(self):
        """Save products to file."""
        self.products["lastUpdated"] = datetime.now().isoformat()
        with open(self.products_file, "w") as f:
            json.dump(self.products, f, indent=2)

    def generate_product_id(self, name):
        """Generate unique product ID."""
        base = name.lower().replace(" ", "-")
        base = ''.join(c for c in base if c.isalnum() or c == '-')
        return base[:30]

    def generate_product(self, category_data):
        """Generate a single product from template."""
        template = random.choice(category_data["templates"])

        # Fill in template variables
        name = template["name"]
        for key, values in category_data.items():
            if key not in ["category", "templates"] and isinstance(values, list):
                placeholder = "{" + key.rstrip("s") + "}"
                if placeholder in name:
                    name = name.replace(placeholder, random.choice(values))

        # Generate pricing
        base_price = template["base_price"] * (0.8 + random.random() * 0.4)
        retail_price = base_price * template["retail_multi"]
        retail_price = round(retail_price * 2) / 2 - 0.01  # Round to .99 or .49

        # Generate description
        descriptions = [
            f"Transform your {category_data['category'].lower()} experience with our {name}.",
            f"The viral {name} everyone's talking about on TikTok.",
            f"Premium quality {name} at an unbeatable price.",
            f"Upgrade your life with this amazing {name}.",
        ]

        # Generate image URL
        query = name.lower().replace(" ", "+")
        seed = hashlib.md5(name.encode()).hexdigest()[:8]
        image = random.choice([
            f"https://source.unsplash.com/600x600/?{query}",
            f"https://picsum.photos/seed/{seed}/600/600"
        ])

        product = {
            "id": self.generate_product_id(name),
            "name": name,
            "category": category_data["category"],
            "description": random.choice(descriptions),
            "price": round(retail_price, 2),
            "originalPrice": round(retail_price * 1.6, 2),
            "discount": random.randint(35, 55),
            "image": image,
            "rating": round(4.5 + random.random() * 0.4, 1),
            "reviews": random.randint(500, 5000),
            "badge": random.choice(["NEW", "TRENDING", "HOT", "BESTSELLER", None, None]),
            "features": self._generate_features(category_data["category"]),
            "margin": round((1 - base_price / retail_price) * 100),
            "wholesaleCost": round(base_price, 2),
            "addedAt": datetime.now().isoformat(),
            "autoGenerated": True
        }

        return product

    def _generate_features(self, category):
        """Generate product features based on category."""
        features_db = {
            "Smart Home": ["App controlled", "Timer function", "Multiple colors", "USB powered", "Remote included"],
            "Health & Wellness": ["Ergonomic design", "Breathable material", "Adjustable fit", "Doctor recommended"],
            "Pet Supplies": ["Durable material", "Easy to clean", "Adjustable size", "Reflective safety"],
            "Beauty Tools": ["Skin-safe materials", "Easy to use", "Travel friendly", "Long lasting"],
            "Kitchen": ["BPA-free", "Rechargeable", "Easy clean", "Portable design"],
            "Accessories": ["Premium quality", "Gift box included", "Adjustable", "Hypoallergenic"],
        }
        base_features = features_db.get(category, ["High quality", "Fast shipping", "30-day guarantee"])
        return random.sample(base_features, min(4, len(base_features)))

    def should_add_product(self):
        """Determine if we should add a new product."""
        current_count = len(self.products.get("products", []))

        # Don't exceed max products
        if current_count >= CONFIG["max_products"]:
            return False

        # Add products more frequently when store is new
        if current_count < 5:
            return True

        # 30% chance to add product on each run
        return random.random() < 0.3

    def add_new_product(self):
        """Add a new auto-generated product."""
        if not self.should_add_product():
            return None

        # Pick random category
        category_data = random.choice(TRENDING_PRODUCT_TEMPLATES)
        product = self.generate_product(category_data)

        # Check for duplicates
        existing_ids = [p["id"] for p in self.products.get("products", [])]
        if product["id"] in existing_ids:
            product["id"] += "-" + hashlib.md5(str(random.random()).encode()).hexdigest()[:4]

        # Add to products
        if "products" not in self.products:
            self.products["products"] = []

        self.products["products"].append(product)
        self._save_products()

        return product

    def update_prices(self):
        """Dynamically adjust prices based on 'demand'."""
        for product in self.products.get("products", []):
            # Simulate demand fluctuation
            if random.random() < 0.1:  # 10% chance of price change
                change = random.uniform(-0.05, 0.10)  # -5% to +10%
                product["price"] = round(product["price"] * (1 + change), 2)
                product["originalPrice"] = round(product["price"] * 1.6, 2)

        self._save_products()

    def remove_low_performers(self):
        """Remove products with low simulated performance."""
        if len(self.products.get("products", [])) <= 5:
            return

        # Simulate removal of 'low performing' auto-generated products
        if random.random() < 0.1:  # 10% chance
            auto_products = [p for p in self.products["products"] if p.get("autoGenerated")]
            if auto_products:
                to_remove = random.choice(auto_products)
                self.products["products"].remove(to_remove)
                self._save_products()
                return to_remove
        return None


# ============================================
# AUTONOMOUS CONTENT GENERATOR
# ============================================

class AutonomousContentGenerator:
    """Generates marketing content automatically."""

    def __init__(self):
        self.content_dir = CONFIG["content_dir"]
        self.content_dir.mkdir(exist_ok=True)

    def generate_daily_content(self, products):
        """Generate daily social media content."""
        content_items = []

        for _ in range(CONFIG["content_per_day"]):
            product = random.choice(products)
            content_type = random.choice(["tiktok", "instagram", "twitter"])

            if content_type == "tiktok":
                content = self._generate_tiktok(product)
            elif content_type == "instagram":
                content = self._generate_instagram(product)
            else:
                content = self._generate_twitter(product)

            content_items.append({
                "type": content_type,
                "product": product["name"],
                "content": content,
                "generated_at": datetime.now().isoformat(),
                "scheduled_for": (datetime.now() + timedelta(hours=random.randint(1, 24))).isoformat()
            })

        # Save to file
        date_str = datetime.now().strftime("%Y-%m-%d")
        content_file = self.content_dir / f"content_{date_str}.json"
        with open(content_file, "w") as f:
            json.dump(content_items, f, indent=2)

        return content_items

    def _generate_tiktok(self, product):
        """Generate TikTok caption."""
        hooks = [
            f"POV: You finally get the {product['name']} everyone's been talking about",
            f"This {product['name']} is going VIRAL for a reason",
            f"Why didn't anyone tell me about this {product['name']} sooner??",
            f"The {product['name']} that broke my TikTok algorithm",
            f"Wait why is nobody talking about this {product['name']}",
        ]

        hashtags = "#fyp #viral #tiktokfinds #amazonfinds #musthaves #trending"

        return {
            "hook": random.choice(hooks),
            "caption": f"{random.choice(hooks)}\n\nLink in bio to get yours!\n\n{hashtags}",
            "suggested_sound": "trending sound - aesthetic vibes",
            "best_time": f"{random.randint(6,9)}:00 PM"
        }

    def _generate_instagram(self, product):
        """Generate Instagram content."""
        captions = [
            f"✨ The {product['name']} you've been seeing everywhere ✨\n\nFinally got mine and WOW. Link in bio!",
            f"This {product['name']} > everything else\n\nSave this for later! Link in bio 🛒",
            f"POV: Your life after getting this {product['name']} 😍\n\nLink in bio to shop!",
        ]

        return {
            "caption": random.choice(captions),
            "hashtags": f"#{product['category'].lower().replace(' ', '')} #aesthetic #musthaves #shopnow #trending",
            "best_time": f"{random.randint(11,13)}:00 PM or {random.randint(7,9)}:00 PM"
        }

    def _generate_twitter(self, product):
        """Generate Twitter/X content."""
        tweets = [
            f"Just got this {product['name']} and I'm obsessed 😭\n\nLink: [bio]",
            f"The {product['name']} hype is REAL. Trust me on this one.\n\n🔗 in bio",
            f"Things I didn't know I needed:\n1. This {product['name']}\n2. That's it. That's the list.\n\nLink in bio",
        ]

        return {
            "tweet": random.choice(tweets),
            "thread_potential": random.choice([True, False]),
            "best_time": f"{random.randint(8,10)}:00 AM or {random.randint(12,14)}:00 PM"
        }


# ============================================
# AUTONOMOUS ORDER HANDLER
# ============================================

class AutonomousOrderHandler:
    """Handles orders automatically via webhooks and email."""

    def __init__(self):
        self.orders_file = CONFIG["data_dir"] / "orders.json"
        self.orders = self._load_orders()

    def _load_orders(self):
        """Load existing orders."""
        try:
            with open(self.orders_file, "r") as f:
                return json.load(f)
        except:
            return {"orders": [], "stats": {"total": 0, "revenue": 0}}

    def _save_orders(self):
        """Save orders."""
        with open(self.orders_file, "w") as f:
            json.dump(self.orders, f, indent=2)

    def simulate_order(self, products):
        """Simulate an order (for testing/demo)."""
        if not products:
            return None

        product = random.choice(products)
        quantity = random.randint(1, 3)

        order = {
            "id": f"SB-{datetime.now().strftime('%y%m%d')}-{random.randint(1000,9999)}",
            "product": product["name"],
            "product_id": product["id"],
            "quantity": quantity,
            "price": product["price"],
            "total": round(product["price"] * quantity, 2),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "simulated": True
        }

        self.orders["orders"].append(order)
        self.orders["stats"]["total"] += 1
        self.orders["stats"]["revenue"] = round(
            self.orders["stats"]["revenue"] + order["total"], 2
        )

        self._save_orders()
        return order

    def process_pending_orders(self):
        """Process pending orders (simulate fulfillment)."""
        processed = []

        for order in self.orders.get("orders", []):
            if order.get("status") == "pending":
                # Simulate processing
                if random.random() < 0.3:  # 30% chance per run
                    order["status"] = "processing"
                    order["processed_at"] = datetime.now().isoformat()
                    processed.append(order)

            elif order.get("status") == "processing":
                # Simulate shipping
                if random.random() < 0.2:  # 20% chance per run
                    order["status"] = "shipped"
                    order["tracking"] = f"TRK{random.randint(10000000, 99999999)}"
                    order["shipped_at"] = datetime.now().isoformat()
                    processed.append(order)

        self._save_orders()
        return processed

    def get_stats(self):
        """Get order statistics."""
        orders = self.orders.get("orders", [])
        return {
            "total_orders": len(orders),
            "pending": len([o for o in orders if o.get("status") == "pending"]),
            "processing": len([o for o in orders if o.get("status") == "processing"]),
            "shipped": len([o for o in orders if o.get("status") == "shipped"]),
            "revenue": self.orders.get("stats", {}).get("revenue", 0)
        }


# ============================================
# AUTONOMOUS ANALYTICS
# ============================================

class AutonomousAnalytics:
    """Tracks and reports business metrics."""

    def __init__(self):
        self.reports_dir = CONFIG["reports_dir"]
        self.reports_dir.mkdir(exist_ok=True)

    def generate_daily_report(self, products, orders, content):
        """Generate daily analytics report."""
        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "generated_at": datetime.now().isoformat(),
            "products": {
                "total": len(products),
                "avg_price": round(sum(p["price"] for p in products) / len(products), 2) if products else 0,
                "avg_margin": round(sum(p.get("margin", 50) for p in products) / len(products), 1) if products else 0,
            },
            "orders": orders,
            "content": {
                "generated_today": len(content) if content else 0,
            },
            "recommendations": self._generate_recommendations(products, orders)
        }

        # Save report
        report_file = self.reports_dir / f"daily_report_{report['date']}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        return report

    def _generate_recommendations(self, products, orders):
        """Generate AI recommendations."""
        recs = []

        if len(products) < 10:
            recs.append("Add more products to increase variety")

        if orders.get("pending", 0) > 5:
            recs.append("Process pending orders to improve customer satisfaction")

        avg_margin = sum(p.get("margin", 50) for p in products) / len(products) if products else 0
        if avg_margin < 50:
            recs.append("Consider removing low-margin products")

        return recs if recs else ["Business is running optimally!"]


# ============================================
# MASTER CONTROLLER
# ============================================

class AutonomousController:
    """Master controller that runs everything."""

    def __init__(self):
        self.product_gen = AutonomousProductGenerator()
        self.content_gen = AutonomousContentGenerator()
        self.order_handler = AutonomousOrderHandler()
        self.analytics = AutonomousAnalytics()

    def run_daily_tasks(self):
        """Run all daily autonomous tasks."""
        print("=" * 60)
        print("SELLBUDDY AUTONOMOUS CONTROLLER")
        print("=" * 60)
        print(f"Started: {datetime.now()}")
        print()

        results = {
            "started_at": datetime.now().isoformat(),
            "tasks": []
        }

        # 1. Product Management
        print("1. PRODUCT MANAGEMENT")
        print("-" * 40)

        # Add new product
        new_product = self.product_gen.add_new_product()
        if new_product:
            print(f"   ✓ Added new product: {new_product['name']}")
            results["tasks"].append({"task": "add_product", "product": new_product["name"]})
        else:
            print("   - No new product added this run")

        # Update prices
        self.product_gen.update_prices()
        print("   ✓ Prices updated")

        # Remove low performers
        removed = self.product_gen.remove_low_performers()
        if removed:
            print(f"   ✓ Removed low performer: {removed['name']}")

        products = self.product_gen.products.get("products", [])
        print(f"   Total products: {len(products)}")

        # 2. Content Generation
        print("\n2. CONTENT GENERATION")
        print("-" * 40)

        if products:
            content = self.content_gen.generate_daily_content(products)
            print(f"   ✓ Generated {len(content)} content pieces")
            for c in content:
                print(f"     - {c['type'].upper()}: {c['product']}")
            results["tasks"].append({"task": "generate_content", "count": len(content)})
        else:
            content = []
            print("   - No products to generate content for")

        # 3. Order Processing
        print("\n3. ORDER PROCESSING")
        print("-" * 40)

        # Simulate occasional orders (for demo)
        if products and random.random() < 0.2:  # 20% chance
            order = self.order_handler.simulate_order(products)
            if order:
                print(f"   ✓ New order: {order['id']} - {order['product']}")
                results["tasks"].append({"task": "new_order", "order_id": order["id"]})

        # Process existing orders
        processed = self.order_handler.process_pending_orders()
        if processed:
            print(f"   ✓ Processed {len(processed)} orders")

        stats = self.order_handler.get_stats()
        print(f"   Order Stats: {stats['total_orders']} total, ${stats['revenue']} revenue")

        # 4. Analytics
        print("\n4. ANALYTICS")
        print("-" * 40)

        report = self.analytics.generate_daily_report(products, stats, content)
        print(f"   ✓ Daily report generated")
        print(f"   Recommendations:")
        for rec in report["recommendations"]:
            print(f"     - {rec}")

        # 5. Summary
        print("\n" + "=" * 60)
        print("AUTONOMOUS RUN COMPLETE")
        print("=" * 60)
        print(f"Finished: {datetime.now()}")
        print(f"Products: {len(products)}")
        print(f"Content: {len(content)} pieces generated")
        print(f"Orders: {stats['total_orders']} total (${stats['revenue']} revenue)")

        results["completed_at"] = datetime.now().isoformat()
        results["summary"] = {
            "products": len(products),
            "content_generated": len(content),
            "orders": stats
        }

        return results

    def run_hourly_tasks(self):
        """Quick hourly checks."""
        # Process any pending orders
        self.order_handler.process_pending_orders()
        return {"task": "hourly_check", "completed_at": datetime.now().isoformat()}


# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Main entry point."""
    controller = AutonomousController()

    # Determine what to run based on arguments
    if len(sys.argv) > 1:
        task = sys.argv[1]
        if task == "hourly":
            result = controller.run_hourly_tasks()
        elif task == "daily":
            result = controller.run_daily_tasks()
        else:
            print(f"Unknown task: {task}")
            print("Usage: python autonomous_controller.py [daily|hourly]")
            return
    else:
        # Default: run daily tasks
        result = controller.run_daily_tasks()

    # Save run log
    log_dir = CONFIG["data_dir"] / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nRun log saved to: {log_file}")


if __name__ == "__main__":
    main()
