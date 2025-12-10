#!/usr/bin/env python3
"""
SellBuddy Social Media Bot
Generates TikTok/Instagram captions, video scripts, and content schedules.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Viral hooks that work
HOOKS = {
    "curiosity": [
        "You won't believe what I just found...",
        "This changed everything for me",
        "Nobody is talking about this...",
        "I've been using this wrong my whole life",
        "Wait until you see what happens next...",
    ],
    "pov": [
        "POV: You finally discover the {product}",
        "POV: Your room after getting {product}",
        "POV: When you realize {product} exists",
        "POV: Life before vs after {product}",
    ],
    "listicle": [
        "Things that will make your life 10x easier",
        "Best purchases I made this year",
        "Things I wish I knew sooner",
        "Products that are actually worth it",
        "Amazon finds that changed my life",
    ],
    "challenge": [
        "I tried {product} for a week and...",
        "Testing viral TikTok products so you don't have to",
        "Is {product} worth the hype?",
        "Honest review: {product}",
    ],
    "emotional": [
        "I can't stop crying over this {product}",
        "Best gift I've ever received",
        "My boyfriend surprised me with this",
        "Every girl needs this",
    ]
}

# Trending hashtags by niche
HASHTAGS = {
    "smart_home": ["#roomdecor", "#homedecor", "#aestheticroom", "#ledlights", "#roomtransformation", "#cozyroom"],
    "health_wellness": ["#selfcare", "#wellness", "#healthylifestyle", "#selfcareroutine", "#healthtok", "#fitness"],
    "pet_products": ["#dogsoftiktok", "#pettok", "#dogmom", "#puppylove", "#petlife", "#furbaby"],
    "fashion_accessories": ["#jewelry", "#accessories", "#fashion", "#ootd", "#style", "#trendy"],
    "beauty_tools": ["#beautytok", "#skincare", "#glowup", "#beautyhacks", "#skincareroutine", "#makeup"],
    "tech_accessories": ["#techtok", "#gadgets", "#tech", "#amazonfinds", "#musthaves", "#techreview"],
    "home_office": ["#wfh", "#homeoffice", "#desksetup", "#productivity", "#remotework", "#officeinspo"]
}

# CTA options
CTAS = [
    "Link in bio!",
    "Save this for later!",
    "Comment 'LINK' and I'll DM you!",
    "Follow for more finds!",
    "Tag someone who needs this!",
    "Which color would you get?",
]


def generate_caption(product_name, niche, hook_type="random"):
    """Generate a viral TikTok/Instagram caption."""
    if hook_type == "random":
        hook_type = random.choice(list(HOOKS.keys()))

    hook = random.choice(HOOKS.get(hook_type, HOOKS["curiosity"]))
    hook = hook.replace("{product}", product_name)

    hashtags = HASHTAGS.get(niche, HASHTAGS["smart_home"])
    selected_hashtags = random.sample(hashtags, min(4, len(hashtags)))
    selected_hashtags.extend(["#tiktokfinds", "#amazonfinds", "#musthaves"])

    cta = random.choice(CTAS)

    caption = f"""{hook}

This {product_name} is literally a game changer!

{cta}

{' '.join(selected_hashtags)}"""

    return caption


def generate_video_script(product_name, key_features, price):
    """Generate a TikTok video script."""
    script = f"""
VIDEO SCRIPT: {product_name}
Duration: 15-30 seconds
Style: POV/Unboxing/Demo

---

HOOK (0-3 sec):
[Show product packaging or dramatic reveal]
Audio: Trending sound or voiceover
Text on screen: "I found the best {product_name}..."

PROBLEM (3-7 sec):
[Show common frustration or before scenario]
Voiceover: "I used to struggle with..."

SOLUTION (7-15 sec):
[Demo the product in action]
Voiceover: "But then I found this {product_name}!"
Show features:
{chr(10).join(f'- {f}' for f in key_features[:3])}

RESULT (15-20 sec):
[Show satisfied reaction, aesthetic shot]
Text: "Only ${price}!"

CTA (20-25 sec):
[Point to link in bio]
Voiceover: "Link in bio, trust me you need this!"

---

POSTING TIPS:
- Post between 7-9 PM local time
- Use trending sounds (check TikTok Creative Center)
- Reply to comments within first hour
- Pin a comment with the link
"""
    return script


def generate_weekly_schedule():
    """Generate a weekly content posting schedule."""
    today = datetime.now()
    schedule = []

    content_types = [
        {"type": "Product Demo", "platform": "TikTok", "best_time": "7:00 PM"},
        {"type": "Before/After", "platform": "Instagram Reels", "best_time": "8:00 PM"},
        {"type": "Unboxing", "platform": "TikTok", "best_time": "12:00 PM"},
        {"type": "Review", "platform": "TikTok", "best_time": "6:00 PM"},
        {"type": "Lifestyle Shot", "platform": "Instagram Feed", "best_time": "9:00 AM"},
        {"type": "Behind the Scenes", "platform": "Instagram Stories", "best_time": "2:00 PM"},
        {"type": "User Testimonial", "platform": "TikTok", "best_time": "8:00 PM"},
    ]

    for i in range(7):
        day = today + timedelta(days=i)
        day_content = content_types[i % len(content_types)]
        schedule.append({
            "date": day.strftime("%A, %B %d"),
            "content_type": day_content["type"],
            "platform": day_content["platform"],
            "posting_time": day_content["best_time"],
            "status": "Scheduled" if i > 0 else "Post Today"
        })

    return schedule


def generate_reddit_post(product_name, subreddit, post_type="recommendation"):
    """Generate Reddit-appropriate posts (non-spammy)."""
    posts = {
        "recommendation": f"""
**Title:** Has anyone tried {product_name}? Looking for honest opinions

**Body:**
Hey everyone! I've been seeing {product_name} all over social media lately and I'm curious if it's actually worth it or just hype.

For context, I'm looking for something that [describe use case]. My budget is around $30-50.

Has anyone here actually used one? Would love to hear your honest experiences - the good AND the bad.

Thanks in advance!

---
*Note: Engage authentically in comments, don't immediately link to your store*
""",
        "discussion": f"""
**Title:** What's your favorite recent purchase under $50?

**Body:**
I've been trying to be more mindful about what I buy, focusing on things that actually improve my daily life.

Recently picked up a {product_name} and it's been surprisingly useful for [use case].

What about you all? Any purchases lately that you'd recommend?

---
*Note: Share value first, only mention your product naturally if asked*
""",
        "question": f"""
**Title:** Best gift ideas for [target audience] around $30?

**Body:**
Hey! Looking for gift recommendations for [person]. They're into [interests].

I was thinking maybe a {product_name}? Has anyone gifted one before?

Open to other suggestions too!

---
*Note: Position as someone seeking recommendations, not selling*
"""
    }

    return posts.get(post_type, posts["recommendation"])


def calculate_viral_potential(engagement_rate, follower_count, content_quality):
    """Calculate viral potential score for content."""
    # Simplified scoring model
    engagement_score = min(engagement_rate * 10, 30)  # Max 30 points
    reach_score = min(follower_count / 10000, 30)  # Max 30 points
    quality_score = content_quality * 0.4  # Max 40 points

    total = engagement_score + reach_score + quality_score
    return round(total, 1)


def main():
    """Main function to generate social media content."""
    print("=" * 50)
    print("SellBuddy Social Media Bot")
    print("=" * 50)
    print()

    # Example product
    product = {
        "name": "Galaxy Star Projector",
        "niche": "smart_home",
        "features": ["16 color modes", "Bluetooth speaker", "Timer function", "Remote control"],
        "price": 34.99
    }

    # Generate caption
    print("GENERATED TIKTOK CAPTION:")
    print("-" * 30)
    caption = generate_caption(product["name"], product["niche"], "curiosity")
    print(caption)
    print()

    # Generate video script
    print("GENERATED VIDEO SCRIPT:")
    print("-" * 30)
    script = generate_video_script(product["name"], product["features"], product["price"])
    print(script)

    # Generate weekly schedule
    print("\nWEEKLY CONTENT SCHEDULE:")
    print("-" * 30)
    schedule = generate_weekly_schedule()
    for day in schedule:
        print(f"{day['date']}: {day['content_type']} on {day['platform']} at {day['posting_time']} - {day['status']}")

    # Generate Reddit post
    print("\nREDDIT POST TEMPLATE:")
    print("-" * 30)
    reddit = generate_reddit_post(product["name"], "r/BuyItForLife", "recommendation")
    print(reddit)

    print("\n" + "=" * 50)
    print("Content generation complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
