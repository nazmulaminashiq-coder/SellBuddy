#!/usr/bin/env python3
"""
SellBuddy Influencer Outreach Bot
Finds micro-influencers, generates personalized outreach, and tracks campaigns.
"""

import json
import random
from datetime import datetime
from pathlib import Path

# Influencer scoring criteria
SCORING_WEIGHTS = {
    "engagement_rate": 0.35,
    "follower_count": 0.20,
    "niche_relevance": 0.25,
    "content_quality": 0.20
}


def load_influencers():
    """Load influencers from JSON file."""
    path = Path(__file__).parent.parent / "data" / "influencers.json"
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {"influencers": [], "campaigns": [], "outreachTemplates": []}


def save_influencers(data):
    """Save influencers to JSON file."""
    path = Path(__file__).parent.parent / "data" / "influencers.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def calculate_influencer_score(influencer):
    """Calculate value score for an influencer."""
    # Normalize metrics (0-100 scale)
    engagement = min(influencer.get("engagement_rate", 0) * 10, 100)  # 10% = 100
    followers = min(influencer.get("followers", 0) / 100000 * 100, 100)  # 100k = 100
    relevance = influencer.get("niche_relevance", 50)
    quality = influencer.get("content_quality", 50)

    score = (
        engagement * SCORING_WEIGHTS["engagement_rate"] +
        followers * SCORING_WEIGHTS["follower_count"] +
        relevance * SCORING_WEIGHTS["niche_relevance"] +
        quality * SCORING_WEIGHTS["content_quality"]
    )

    return round(score, 1)


def generate_outreach_message(influencer, product, template_type="product-review"):
    """Generate personalized outreach message."""
    templates = {
        "product-review": f"""
Hi {influencer['name']}!

I've been following your {influencer['platform']} content and absolutely love your {influencer['niche']} posts - especially the way you connect with your audience!

I'm reaching out from SellBuddy. We have a {product['name']} that I think would resonate perfectly with your followers.

Would you be interested in receiving one for free in exchange for an honest review? No scripts, no requirements - just your genuine thoughts!

If you're interested, just reply and I'll ship it out right away (free shipping to you, of course!).

Looking forward to hearing from you!

Best,
SellBuddy Team
""",
        "affiliate": f"""
Hey {influencer['name']}!

Your {influencer['platform']} content is fantastic - your engagement rate is impressive and your audience clearly trusts you.

I'd love to offer you an exclusive partnership with SellBuddy:
- 15% commission on every sale you generate
- Custom discount code for your followers
- Free products to showcase
- Priority support

Our {product['name']} has been trending and I think it would be a great fit for your audience.

Interested? Just reply and I'll send over all the details!

Cheers,
SellBuddy Team
""",
        "ugc": f"""
Hi {influencer['name']}!

We're looking for talented creators like you to help us with some UGC content.

Here's the deal:
- We send you our {product['name']} (free, of course)
- You create 2-3 short videos (TikTok/Reels style)
- We pay $50-100 per video depending on quality
- You keep the product!

Your content style is exactly what we're looking for. Would you be interested in learning more?

Let me know!

Best,
SellBuddy Team
"""
    }

    return templates.get(template_type, templates["product-review"])


def find_micro_influencers(niche, min_followers=1000, max_followers=50000):
    """
    Find potential micro-influencers (simulated).
    In production, integrate with social media APIs.
    """
    # Simulated influencer discovery
    platforms = ["TikTok", "Instagram", "YouTube"]
    niches_keywords = {
        "smart_home": ["room decor", "home aesthetic", "LED setup", "cozy room"],
        "health_wellness": ["fitness", "wellness", "self care", "healthy living"],
        "pet_products": ["dog mom", "pet life", "puppy", "fur baby"],
        "beauty_tools": ["skincare", "beauty routine", "glow up", "makeup"],
    }

    # Generate sample influencers
    sample_influencers = []
    for i in range(10):
        platform = random.choice(platforms)
        followers = random.randint(min_followers, max_followers)
        engagement = random.uniform(3.0, 15.0)  # 3-15% engagement rate

        sample_influencers.append({
            "id": f"inf_{i+1}",
            "name": f"Creator_{i+1}",
            "username": f"@creator{i+1}",
            "platform": platform,
            "niche": niche.replace("_", " ").title(),
            "followers": followers,
            "engagement_rate": round(engagement, 2),
            "niche_relevance": random.randint(60, 95),
            "content_quality": random.randint(60, 95),
            "email": f"creator{i+1}@example.com",
            "status": "Not Contacted"
        })

    # Calculate scores and sort
    for inf in sample_influencers:
        inf["score"] = calculate_influencer_score(inf)

    sample_influencers.sort(key=lambda x: x["score"], reverse=True)
    return sample_influencers


def track_campaign(campaign_name, influencers, product):
    """Create and track an influencer campaign."""
    campaign = {
        "id": f"camp_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "name": campaign_name,
        "product": product["name"],
        "created": datetime.now().isoformat(),
        "status": "Active",
        "influencers": len(influencers),
        "outreach_sent": 0,
        "responses": 0,
        "accepted": 0,
        "content_received": 0,
        "sales_generated": 0,
        "revenue": 0
    }
    return campaign


def generate_campaign_report(campaign, influencers):
    """Generate a campaign performance report."""
    report = f"""
INFLUENCER CAMPAIGN REPORT
{'=' * 50}

Campaign: {campaign['name']}
Product: {campaign['product']}
Created: {campaign['created'][:10]}
Status: {campaign['status']}

METRICS:
---------
Total Influencers: {campaign['influencers']}
Outreach Sent: {campaign['outreach_sent']}
Responses: {campaign['responses']} ({campaign['responses']/max(campaign['outreach_sent'],1)*100:.1f}% response rate)
Accepted: {campaign['accepted']} ({campaign['accepted']/max(campaign['responses'],1)*100:.1f}% acceptance rate)
Content Received: {campaign['content_received']}
Sales Generated: {campaign['sales_generated']}
Revenue: ${campaign['revenue']:.2f}

TOP INFLUENCERS:
---------
"""
    for i, inf in enumerate(influencers[:5], 1):
        report += f"{i}. {inf['name']} (@{inf['username']}) - {inf['platform']}\n"
        report += f"   Followers: {inf['followers']:,} | Engagement: {inf['engagement_rate']}% | Score: {inf['score']}\n"

    return report


def main():
    """Main function to run influencer outreach bot."""
    print("=" * 50)
    print("SellBuddy Influencer Outreach Bot")
    print("=" * 50)
    print()

    # Sample product
    product = {
        "name": "Galaxy Star Projector",
        "niche": "smart_home",
        "price": 34.99
    }

    # Find influencers
    print(f"Finding micro-influencers for: {product['niche']}")
    print("-" * 30)
    influencers = find_micro_influencers(product["niche"])

    print(f"\nFound {len(influencers)} potential influencers:")
    print()
    for i, inf in enumerate(influencers[:5], 1):
        print(f"{i}. {inf['name']} ({inf['platform']})")
        print(f"   Followers: {inf['followers']:,} | Engagement: {inf['engagement_rate']}%")
        print(f"   Score: {inf['score']}/100")
        print()

    # Generate outreach message
    print("\nSAMPLE OUTREACH MESSAGE:")
    print("-" * 30)
    message = generate_outreach_message(influencers[0], product, "product-review")
    print(message)

    # Create campaign
    print("\nCREATING CAMPAIGN:")
    print("-" * 30)
    campaign = track_campaign("Star Projector Launch", influencers[:10], product)
    campaign["outreach_sent"] = 10
    campaign["responses"] = 3
    campaign["accepted"] = 2

    report = generate_campaign_report(campaign, influencers)
    print(report)

    print("=" * 50)
    print("Influencer outreach complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
