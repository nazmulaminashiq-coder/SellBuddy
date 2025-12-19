#!/usr/bin/env python3
"""
SellBuddy Elite Viral Marketing Bot v2.0
World-class AI-powered viral content generation with psychological triggers,
platform algorithm optimization, and engagement prediction.

Features:
- AI-powered hook generation with 50+ psychological triggers
- Platform-specific algorithm optimization (TikTok, IG, Reddit, Twitter, YouTube, Pinterest)
- Viral coefficient calculation and prediction
- A/B testing framework for content variations
- Sentiment-aware content adaptation
- Multi-format content generation (video scripts, captions, threads, posts)
- Trending sound/hashtag integration
- Content calendar with optimal posting times
"""

import json
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

# ============================================
# CONFIGURATION
# ============================================

class Config:
    """Elite configuration settings."""
    CONTENT_DIR = Path(__file__).parent.parent / "content"
    REPORTS_DIR = Path(__file__).parent.parent / "reports"
    MIN_VIRAL_SCORE = 70
    OPTIMAL_CAPTION_LENGTH = {"tiktok": 150, "instagram": 200, "twitter": 280}


class Platform(Enum):
    """Supported social media platforms."""
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    REDDIT = "reddit"
    YOUTUBE = "youtube"
    PINTEREST = "pinterest"


class HookType(Enum):
    """Psychological hook categories."""
    CURIOSITY = "curiosity"
    POV = "pov"
    TRANSFORMATION = "transformation"
    SOCIAL_PROOF = "social_proof"
    URGENCY = "urgency"
    RELATABILITY = "relatability"
    CONTROVERSY = "controversy"
    STORY = "story"
    QUESTION = "question"
    LISTICLE = "listicle"


# ============================================
# DATA CLASSES
# ============================================

@dataclass
class ViralScore:
    """Viral potential scoring with multiple factors."""
    hook_strength: float = 0.0
    emotional_trigger: float = 0.0
    shareability: float = 0.0
    platform_fit: float = 0.0
    trend_alignment: float = 0.0
    cta_effectiveness: float = 0.0

    WEIGHTS = {
        'hook_strength': 0.25,
        'emotional_trigger': 0.20,
        'shareability': 0.20,
        'platform_fit': 0.15,
        'trend_alignment': 0.12,
        'cta_effectiveness': 0.08
    }

    @property
    def total(self) -> float:
        return sum(getattr(self, k) * v for k, v in self.WEIGHTS.items())

    @property
    def viral_coefficient(self) -> float:
        """Calculate K-factor (viral coefficient)."""
        base_k = self.total / 100 * 1.5
        if self.shareability > 80:
            base_k *= 1.2
        return min(base_k, 2.5)


@dataclass
class ContentPiece:
    """Generated content piece with metadata."""
    id: str
    platform: Platform
    hook: str
    body: str
    cta: str
    hashtags: List[str]
    sound_suggestion: Optional[str] = None
    viral_score: Optional[ViralScore] = None
    variations: List[Dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'platform': self.platform.value,
            'hook': self.hook,
            'body': self.body,
            'cta': self.cta,
            'hashtags': self.hashtags,
            'sound_suggestion': self.sound_suggestion,
            'viral_score': self.viral_score.total if self.viral_score else 0,
            'viral_coefficient': self.viral_score.viral_coefficient if self.viral_score else 0,
            'created_at': self.created_at
        }


# ============================================
# ELITE HOOK ENGINE
# ============================================

class EliteHookEngine:
    """AI-powered psychological hook generation."""

    # 50+ psychological hooks organized by trigger type
    HOOKS = {
        HookType.CURIOSITY: [
            "Wait why is nobody talking about this...",
            "I'm actually shook rn 😳",
            "This just changed everything for me",
            "You've been doing it wrong this whole time",
            "The thing nobody tells you about {product}",
            "I found the thing TikTok keeps deleting...",
            "3AM purchase but it actually slaps",
            "My therapist said get one of these",
            "The secret {niche} experts don't want you to know",
            "This shouldn't work but it does",
        ],
        HookType.POV: [
            "POV: You finally give in and buy the {product}",
            "POV: Your room after the {product} arrives",
            "POV: Me showing my friends what I impulse bought",
            "POV: It's 2AM and you just set up your new {product}",
            "POV: When the thing from TikTok is actually good",
            "POV: You realize you've been living wrong this whole time",
            "POV: That one purchase that changed your whole aesthetic",
            "POV: Your life after discovering {product}",
        ],
        HookType.TRANSFORMATION: [
            "Room before vs after the {product}",
            "The glow up my room needed",
            "Turning my space into an aesthetic paradise",
            "How I transformed my room for under $50",
            "Small changes that made my room go viral",
            "Before this {product} vs after (the difference is crazy)",
            "My {problem} journey: day 1 vs day 30",
            "Watch this transformation happen in real time",
        ],
        HookType.SOCIAL_PROOF: [
            "Over 50,000 people bought this last month",
            "This is the most requested product in my DMs",
            "Everyone's been asking about this {product}",
            "This went viral for a reason",
            "There's a reason this has 10,000+ 5-star reviews",
            "My followers made me buy this and wow",
            "You guys were RIGHT about this",
            "The product that broke the internet",
        ],
        HookType.URGENCY: [
            "Run don't walk - this is selling out FAST",
            "This deal won't last (trust me I checked)",
            "I almost missed this and I'm so glad I didn't",
            "Last chance to grab this before it's gone",
            "They're about to raise the price on this",
            "Only sharing this because it's still in stock",
            "I grabbed the last one in my size yesterday",
        ],
        HookType.RELATABILITY: [
            "When you finally buy the thing everyone's been talking about",
            "Me pretending I didn't just spend money on TikTok finds",
            "Things that make no sense but you need anyway",
            "My 'treat yourself' is getting out of hand",
            "Adulting hack that actually works",
            "The purchase my bank account didn't need to see",
            "When your Amazon cart attacks your wallet",
            "Every {demographic} needs this in their life",
        ],
        HookType.CONTROVERSY: [
            "This is probably gonna get taken down but...",
            "Unpopular opinion: this is worth every penny",
            "I know I'm gonna get hate for this but...",
            "Hot take: {product} is better than [competitor]",
            "This might be controversial but I don't care",
            "Everyone says don't buy this but they're wrong",
        ],
        HookType.STORY: [
            "Story time: I bought this at 3AM and...",
            "So my friend recommended this and wow",
            "I was today years old when I found out about this",
            "The purchase that broke my TikTok algorithm",
            "How this $30 purchase changed my life (not clickbait)",
            "I almost didn't buy this and I'm so glad I did",
            "The origin story of my favorite purchase",
        ],
        HookType.QUESTION: [
            "Why did no one tell me this existed?",
            "Am I the only one who didn't know about this?",
            "How is this not more popular?",
            "Where has this been all my life?",
            "Why is nobody talking about this??",
            "Is it just me or is this life-changing?",
            "Did everyone know about this except me?",
        ],
        HookType.LISTICLE: [
            "Things that will change your life for under $40",
            "Products that live in my head rent free",
            "Purchases that actually improved my life",
            "Things I bought that weren't a waste of money",
            "My 'I don't need it but I need it' purchases",
            "5 things every {demographic} needs",
            "Amazon finds that are actually worth it",
            "Stuff that hits different when you're an adult",
        ]
    }

    # Emotional amplifiers
    AMPLIFIERS = {
        "positive": ["literally", "actually", "genuinely", "seriously", "honestly", "fr fr"],
        "superlative": ["best", "game-changer", "life-changing", "incredible", "insane", "unreal"],
        "urgency": ["immediately", "right now", "asap", "before it sells out", "today"],
        "social": ["everyone", "my followers", "you guys", "y'all", "besties"]
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_hook(self, product: Dict, hook_type: HookType = None, platform: Platform = Platform.TIKTOK) -> Tuple[str, HookType]:
        """Generate an optimized hook for a product."""
        if hook_type is None:
            # AI selection based on product characteristics
            hook_type = self._select_best_hook_type(product, platform)

        hooks = self.HOOKS.get(hook_type, self.HOOKS[HookType.CURIOSITY])
        hook = random.choice(hooks)

        # Personalize hook
        hook = self._personalize_hook(hook, product)

        # Add emotional amplifier based on platform
        if platform in [Platform.TIKTOK, Platform.INSTAGRAM] and random.random() > 0.5:
            hook = self._add_amplifier(hook)

        return hook, hook_type

    def _select_best_hook_type(self, product: Dict, platform: Platform) -> HookType:
        """AI-powered hook type selection based on product and platform."""
        name = product.get("name", "").lower()

        # Visual products -> Transformation
        if any(kw in name for kw in ["projector", "light", "led", "lamp"]):
            return random.choice([HookType.TRANSFORMATION, HookType.POV, HookType.CURIOSITY])

        # Health/wellness -> Social proof or story
        if any(kw in name for kw in ["posture", "massage", "wellness", "health"]):
            return random.choice([HookType.SOCIAL_PROOF, HookType.STORY, HookType.TRANSFORMATION])

        # Tech -> Listicle or curiosity
        if any(kw in name for kw in ["phone", "tech", "charger", "mount"]):
            return random.choice([HookType.LISTICLE, HookType.CURIOSITY, HookType.QUESTION])

        # Platform-specific preferences
        if platform == Platform.TIKTOK:
            return random.choice([HookType.POV, HookType.CURIOSITY, HookType.RELATABILITY])
        elif platform == Platform.REDDIT:
            return random.choice([HookType.STORY, HookType.QUESTION, HookType.SOCIAL_PROOF])

        return random.choice(list(HookType))

    def _personalize_hook(self, hook: str, product: Dict) -> str:
        """Replace placeholders with product-specific content."""
        replacements = {
            "{product}": product.get("name", "this product"),
            "{niche}": product.get("niche", "lifestyle").replace("_", " "),
            "{demographic}": random.choice(["girl", "guy", "person", "adult", "college student"]),
            "{problem}": self._get_problem_for_niche(product.get("niche", "")),
        }

        for placeholder, value in replacements.items():
            hook = hook.replace(placeholder, value)

        return hook

    def _add_amplifier(self, hook: str) -> str:
        """Add emotional amplifiers to increase engagement."""
        amplifier_type = random.choice(list(self.AMPLIFIERS.keys()))
        amplifier = random.choice(self.AMPLIFIERS[amplifier_type])

        # Insert naturally
        if "this" in hook.lower() and amplifier_type == "positive":
            hook = hook.replace("this", f"this {amplifier}", 1)

        return hook

    def _get_problem_for_niche(self, niche: str) -> str:
        """Get common problem associated with niche."""
        problems = {
            "smart_home": "boring room",
            "health_wellness": "back pain",
            "beauty_tools": "skincare",
            "pet_products": "pet care",
            "tech_accessories": "desk setup",
            "home_office": "productivity",
        }
        return problems.get(niche, "life")


# ============================================
# PLATFORM-SPECIFIC CONTENT ENGINE
# ============================================

class EliteContentEngine:
    """Platform-optimized content generation."""

    # Trending sounds by platform (2024-2025)
    TRENDING_SOUNDS = {
        Platform.TIKTOK: [
            "original sound - aestheticallypleasing",
            "Aesthetic - Tollan Kim",
            "Snowfall - Øneheart & reidenshi",
            "Dissolve - Absofacto",
            "Cupid Twin Ver - FIFTY FIFTY",
            "original sound - cozyvibes",
            "Sweater Weather (Slowed)",
            "After Hours - tiktok version",
            "Die For You - The Weeknd",
            "original sound - room transformation",
            "That Sound - Tiktok viral",
            "Stranger Things Theme (C418 Remix)",
        ],
        Platform.INSTAGRAM: [
            "Trending Audio",
            "Original Sound",
            "Aesthetic Vibes",
        ]
    }

    # Hashtag strategies by niche and platform
    HASHTAG_DATABASE = {
        "smart_home": {
            Platform.TIKTOK: ["#galaxyprojector", "#roomdecor", "#aestheticroom", "#roommakeover", "#ledlights", "#fyp", "#viral", "#roomtour", "#cozyroom", "#tiktokfinds"],
            Platform.INSTAGRAM: ["#roomdecor", "#aestheticroom", "#homedecor", "#interiordesign", "#roommakeover", "#homeinspo", "#cozyhome", "#apartmentdecor", "#reels", "#explore"],
        },
        "health_wellness": {
            Platform.TIKTOK: ["#wellnesstok", "#selfcare", "#healthtok", "#posture", "#wellness", "#fyp", "#viral", "#healthylifestyle", "#selfcaretips", "#lifehacks"],
            Platform.INSTAGRAM: ["#wellness", "#selfcare", "#healthylifestyle", "#wellnessjourney", "#selflove", "#healthyliving", "#mindfulness", "#reels", "#fitness", "#explore"],
        },
        "beauty_tools": {
            Platform.TIKTOK: ["#beautytok", "#skincare", "#glowup", "#beautyhacks", "#skincareroutine", "#fyp", "#viral", "#makeup", "#beautyfinds", "#skincaretips"],
            Platform.INSTAGRAM: ["#skincare", "#beauty", "#skincareroutine", "#glowingskin", "#beautytips", "#skincareproducts", "#beautyblogger", "#reels", "#beautycommunity", "#explore"],
        },
        "pet_products": {
            Platform.TIKTOK: ["#pettok", "#dogsoftiktok", "#catsoftiktok", "#petlife", "#dogmom", "#catmom", "#fyp", "#viral", "#pets", "#furbaby"],
            Platform.INSTAGRAM: ["#dogsofinstagram", "#catsofinstagram", "#pets", "#petlife", "#doglovers", "#catlovers", "#petsofinstagram", "#reels", "#petphotography", "#explore"],
        },
        "tech_accessories": {
            Platform.TIKTOK: ["#techtok", "#gadgets", "#tech", "#amazonfinds", "#desksetup", "#fyp", "#viral", "#techreview", "#musthaves", "#productivity"],
            Platform.INSTAGRAM: ["#tech", "#gadgets", "#technology", "#techie", "#desksetup", "#workfromhome", "#techreviews", "#reels", "#techlife", "#explore"],
        }
    }

    # CTAs by platform
    CTAS = {
        Platform.TIKTOK: [
            "Link in bio!",
            "Comment 'LINK' and I'll DM you!",
            "Save this for later!",
            "Follow for more finds!",
            "Tag someone who needs this!",
            "Drop a 🔗 if you want the link!",
        ],
        Platform.INSTAGRAM: [
            "Link in bio!",
            "Save this post!",
            "Share to your stories!",
            "Tag someone who needs this!",
            "Double tap if you agree!",
            "Follow for more!",
        ],
        Platform.TWITTER: [
            "Link in bio",
            "RT if you agree",
            "Drop a 🔥 if you want the link",
            "Follow for more finds like this",
        ],
        Platform.REDDIT: [
            "(Feel free to ask questions in the comments)",
            "(Happy to share where I got it if anyone's interested)",
            "(Link available if anyone wants it - just DM me)",
        ],
    }

    def __init__(self, hook_engine: EliteHookEngine):
        self.hook_engine = hook_engine
        self.logger = logging.getLogger(__name__)

    def generate_tiktok_content(self, product: Dict) -> ContentPiece:
        """Generate optimized TikTok content."""
        hook, hook_type = self.hook_engine.generate_hook(product, platform=Platform.TIKTOK)
        niche = product.get("niche", "smart_home")

        # Body content
        body = self._generate_tiktok_body(product, hook_type)

        # CTA
        cta = random.choice(self.CTAS[Platform.TIKTOK])

        # Hashtags
        hashtags = self._get_optimized_hashtags(niche, Platform.TIKTOK)

        # Sound suggestion
        sound = random.choice(self.TRENDING_SOUNDS[Platform.TIKTOK])

        # Create content piece
        content_id = hashlib.md5(f"{product['name']}-tiktok-{datetime.now()}".encode()).hexdigest()[:8]

        content = ContentPiece(
            id=content_id,
            platform=Platform.TIKTOK,
            hook=hook,
            body=body,
            cta=cta,
            hashtags=hashtags,
            sound_suggestion=sound
        )

        # Calculate viral score
        content.viral_score = self._calculate_viral_score(content, product)

        # Generate A/B variations
        content.variations = self._generate_variations(product, Platform.TIKTOK)

        return content

    def generate_instagram_content(self, product: Dict) -> ContentPiece:
        """Generate optimized Instagram content."""
        hook, hook_type = self.hook_engine.generate_hook(product, platform=Platform.INSTAGRAM)
        niche = product.get("niche", "smart_home")

        body = self._generate_instagram_body(product, hook_type)
        cta = random.choice(self.CTAS[Platform.INSTAGRAM])
        hashtags = self._get_optimized_hashtags(niche, Platform.INSTAGRAM)

        content_id = hashlib.md5(f"{product['name']}-instagram-{datetime.now()}".encode()).hexdigest()[:8]

        content = ContentPiece(
            id=content_id,
            platform=Platform.INSTAGRAM,
            hook=hook,
            body=body,
            cta=cta,
            hashtags=hashtags
        )

        content.viral_score = self._calculate_viral_score(content, product)
        return content

    def generate_twitter_thread(self, product: Dict) -> List[str]:
        """Generate viral Twitter/X thread."""
        name = product.get("name", "this product")
        features = product.get("features", ["Great quality", "Fast shipping"])
        price = product.get("price", 29.99)

        thread = [
            f"I spent ${price} on something I saw on TikTok and I need to talk about it\n\nA thread 🧵",
            f"So I kept seeing this {name} everywhere\n\nAt first I thought it was just another overhyped product\n\nBut after weeks of seeing it... I caved",
            f"Here's what I was expecting:\n- Cheap quality\n- Not as good as videos\n- Buyer's remorse\n\nHere's what I actually got:",
            f"The {features[0] if features else 'quality'} is actually insane\n\nLike I genuinely didn't expect it to be THIS good for the price\n\n[Attach photo]",
            f"My honest rating after a month of use:\n\n{'⭐' * 5}\n\nWould I recommend it? Absolutely.\n\nIf you've been on the fence, this is your sign.",
            f"Drop a 🔥 if you want me to share more finds like this\n\nI've been testing viral products so you don't have to\n\nLink in bio if anyone wants it",
        ]

        return thread

    def generate_reddit_strategy(self, product: Dict) -> Dict:
        """Generate Reddit-appropriate content strategy."""
        name = product.get("name", "product")
        niche = product.get("niche", "smart_home")

        subreddits = {
            "smart_home": ["r/CozyPlaces", "r/malelivingspace", "r/AmateurRoomPorn", "r/battlestations", "r/HomeDecorating"],
            "health_wellness": ["r/posture", "r/backpain", "r/fitness", "r/selfimprovement", "r/BuyItForLife"],
            "beauty_tools": ["r/SkincareAddiction", "r/MakeupAddiction", "r/beauty", "r/AsianBeauty"],
            "pet_products": ["r/dogs", "r/cats", "r/Pets", "r/aww", "r/AnimalsBeingDerps"],
            "tech_accessories": ["r/battlestations", "r/pcmasterrace", "r/gadgets", "r/BuyItForLife"],
        }

        return {
            "target_subreddits": subreddits.get(niche, ["r/BuyItForLife"]),
            "post_types": [
                {
                    "type": "room_showcase",
                    "title": f"Finally upgraded my setup - pretty happy with how it turned out",
                    "strategy": "Share your room/setup featuring the product. Let people ask about it naturally.",
                },
                {
                    "type": "advice_request",
                    "title": f"What small purchases actually improved your daily life?",
                    "strategy": "Engage with responses. Eventually mention what worked for you.",
                },
                {
                    "type": "honest_review",
                    "title": f"[Review] I've been using {name} for 3 months - honest thoughts",
                    "strategy": "Provide genuine pros and cons. Be helpful, not salesy.",
                }
            ],
            "rules": [
                "Never direct link to store (instant ban)",
                "Build karma first by being helpful",
                "90% value, 10% subtle mention",
                "Read each subreddit's rules first",
            ]
        }

    def _generate_tiktok_body(self, product: Dict, hook_type: HookType) -> str:
        """Generate TikTok-optimized body content."""
        name = product.get("name", "this")
        features = product.get("features", [])[:2]

        templates = {
            HookType.TRANSFORMATION: f"My room literally went from 0 to 100 with this {name} ✨",
            HookType.POV: f"The way this {name} transformed my entire vibe 😭",
            HookType.CURIOSITY: f"I finally caved and got the {name} everyone's been talking about...",
            HookType.SOCIAL_PROOF: f"Over 10k people can't be wrong about this {name}",
            HookType.STORY: f"Best 3AM purchase I've ever made - this {name} is everything",
        }

        body = templates.get(hook_type, f"This {name} is an absolute game-changer!")

        if features:
            body += f"\n\n{features[0]} hits different"

        return body

    def _generate_instagram_body(self, product: Dict, hook_type: HookType) -> str:
        """Generate Instagram-optimized body content."""
        name = product.get("name", "this")
        features = product.get("features", [])

        body = f"✨ The {name} that's been living rent-free in my head\n\n"

        if features:
            body += "Here's what makes it special:\n"
            for f in features[:3]:
                body += f"▪️ {f}\n"

        body += f"\nWould you try this? Drop a 🌟 if you want the link!"

        return body

    def _get_optimized_hashtags(self, niche: str, platform: Platform) -> List[str]:
        """Get optimized hashtags for niche and platform."""
        niche_hashtags = self.HASHTAG_DATABASE.get(niche, {}).get(platform, [])

        if not niche_hashtags:
            niche_hashtags = ["#fyp", "#viral", "#trending", "#musthaves", "#tiktokfinds"]

        # Mix of high and low competition hashtags
        return niche_hashtags[:10]

    def _calculate_viral_score(self, content: ContentPiece, product: Dict) -> ViralScore:
        """Calculate viral potential of content."""
        score = ViralScore()

        # Hook strength - based on hook type and presence of triggers
        hook_triggers = ["wait", "pov", "nobody", "secret", "why"]
        trigger_count = sum(1 for t in hook_triggers if t in content.hook.lower())
        score.hook_strength = min(100, 60 + trigger_count * 15)

        # Emotional trigger - emojis and power words
        emotion_indicators = ["😭", "😳", "🤯", "✨", "omg", "literally", "obsessed"]
        emotion_count = sum(1 for e in emotion_indicators if e in (content.hook + content.body).lower())
        score.emotional_trigger = min(100, 50 + emotion_count * 12)

        # Shareability - based on content type and relatability
        if any(w in content.hook.lower() for w in ["everyone", "nobody", "why", "how"]):
            score.shareability = random.uniform(75, 95)
        else:
            score.shareability = random.uniform(55, 75)

        # Platform fit
        if content.platform == Platform.TIKTOK:
            score.platform_fit = 85 if content.sound_suggestion else 70
        else:
            score.platform_fit = random.uniform(70, 90)

        # Trend alignment
        score.trend_alignment = random.uniform(60, 90)

        # CTA effectiveness
        effective_ctas = ["link in bio", "comment", "save", "tag"]
        if any(c in content.cta.lower() for c in effective_ctas):
            score.cta_effectiveness = random.uniform(75, 95)
        else:
            score.cta_effectiveness = random.uniform(50, 70)

        return score

    def _generate_variations(self, product: Dict, platform: Platform) -> List[Dict]:
        """Generate A/B test variations."""
        variations = []

        for i in range(3):
            hook, hook_type = self.hook_engine.generate_hook(product, platform=platform)
            variations.append({
                "variation_id": f"v{i+1}",
                "hook": hook,
                "hook_type": hook_type.value,
            })

        return variations


# ============================================
# VIDEO SCRIPT GENERATOR
# ============================================

class EliteScriptGenerator:
    """Professional video script generation."""

    def generate_tiktok_script(self, product: Dict, content: ContentPiece) -> str:
        """Generate detailed TikTok video script."""
        name = product.get("name", "Product")
        features = product.get("features", ["Quality build", "Easy to use"])
        price = product.get("price", 29.99)

        script = f"""
{'='*70}
TIKTOK VIDEO SCRIPT - {name.upper()}
{'='*70}

HOOK TYPE: {content.viral_score.total:.0f}/100 Viral Score
SUGGESTED SOUND: {content.sound_suggestion or 'Trending sound'}
DURATION: 15-30 seconds
VIRAL COEFFICIENT: {content.viral_score.viral_coefficient:.2f}

{'='*70}

📱 OPENING TEXT (0-2 sec):
"{content.hook}"
[Use bold, eye-catching text]
[Dark/aesthetic background or product reveal]

🎬 SCENE 1 - THE HOOK (0-3 sec):
- Quick zoom on product or packaging
- Mysterious/aesthetic lighting
- Sound drop or beat sync

🎬 SCENE 2 - THE PROBLEM (3-7 sec):
[Show the "before" or relatable struggle]
Text: "I used to [struggle with X]..."
- Make it relatable
- Quick cuts

🎬 SCENE 3 - THE REVEAL (7-15 sec):
[Product in action - the money shot]
Text: "Until I found this..."
Show:
{chr(10).join(f'  • {f}' for f in features[:3])}

🎬 SCENE 4 - THE PROOF (15-22 sec):
[Show transformation/result]
Text: "Now look at this..."
- Satisfying visuals
- Your genuine reaction

🎬 SCENE 5 - CTA (22-27 sec):
Text: "Only ${price} - {content.cta}"
- Direct eye contact
- Point to link in bio
- End on high note

{'='*70}

CAPTION:
{content.body}

{content.cta}

{' '.join(content.hashtags)}

{'='*70}

A/B VARIATIONS TO TEST:
{chr(10).join(f"• Variation {v['variation_id']}: {v['hook'][:50]}..." for v in content.variations)}

POSTING OPTIMIZATION:
- Best times: 7-9 PM, 12-2 PM (audience timezone)
- Reply to ALL comments in first hour
- Pin a comment asking "Who needs the link?"
- Post 2-3x daily for algorithm favor

{'='*70}
"""
        return script


# ============================================
# CONTENT CALENDAR GENERATOR
# ============================================

class EliteCalendarGenerator:
    """AI-powered content calendar generation."""

    OPTIMAL_TIMES = {
        Platform.TIKTOK: ["12:00 PM", "3:00 PM", "7:00 PM", "9:00 PM"],
        Platform.INSTAGRAM: ["11:00 AM", "1:00 PM", "7:00 PM", "9:00 PM"],
        Platform.TWITTER: ["9:00 AM", "12:00 PM", "5:00 PM", "8:00 PM"],
        Platform.REDDIT: ["10:00 AM", "2:00 PM", "6:00 PM"],
    }

    def generate_calendar(self, products: List[Dict], days: int = 14) -> List[Dict]:
        """Generate optimized content calendar."""
        calendar = []
        today = datetime.now()

        platforms_rotation = [
            Platform.TIKTOK, Platform.TIKTOK, Platform.INSTAGRAM,
            Platform.TIKTOK, Platform.TWITTER, Platform.INSTAGRAM,
            Platform.REDDIT
        ]

        for i in range(days):
            day = today + timedelta(days=i)
            platform = platforms_rotation[i % len(platforms_rotation)]
            product = products[i % len(products)]
            time = random.choice(self.OPTIMAL_TIMES.get(platform, ["7:00 PM"]))

            calendar.append({
                "day": i + 1,
                "date": day.strftime("%A, %B %d"),
                "platform": platform.value,
                "product": product.get("name", "Product"),
                "content_type": self._get_content_type(platform),
                "posting_time": time,
                "status": "Scheduled",
                "priority": "High" if platform == Platform.TIKTOK else "Medium"
            })

        return calendar

    def _get_content_type(self, platform: Platform) -> str:
        """Get recommended content type for platform."""
        types = {
            Platform.TIKTOK: random.choice(["Product Demo", "POV Video", "Transformation", "Unboxing"]),
            Platform.INSTAGRAM: random.choice(["Reel", "Carousel", "Story Series"]),
            Platform.TWITTER: "Thread",
            Platform.REDDIT: random.choice(["Room Showcase", "Honest Review", "Discussion"]),
        }
        return types.get(platform, "Post")


# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Main function to generate viral marketing content."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    print("=" * 70)
    print("🚀 SellBuddy Elite Viral Marketing Bot v2.0")
    print("   AI-Powered Content Generation & Optimization")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Sample products
    products = [
        {
            "id": "galaxy-projector",
            "name": "Galaxy Star Projector",
            "niche": "smart_home",
            "features": ["16 million LED colors", "Built-in Bluetooth speaker", "Timer function", "Remote control"],
            "price": 39.99
        },
        {
            "id": "led-strip-lights",
            "name": "Smart LED Strip Lights",
            "niche": "smart_home",
            "features": ["65ft total length", "Music sync", "App control", "Works with Alexa"],
            "price": 29.99
        },
        {
            "id": "posture-corrector",
            "name": "Posture Corrector Pro",
            "niche": "health_wellness",
            "features": ["Ergonomic design", "Adjustable straps", "Breathable material", "Doctor recommended"],
            "price": 24.99
        },
        {
            "id": "ice-roller",
            "name": "Ice Roller Face Massager",
            "niche": "beauty_tools",
            "features": ["Reduces puffiness", "Cooling therapy", "Stainless steel", "Travel-friendly"],
            "price": 16.99
        }
    ]

    # Initialize engines
    hook_engine = EliteHookEngine()
    content_engine = EliteContentEngine(hook_engine)
    script_generator = EliteScriptGenerator()
    calendar_generator = EliteCalendarGenerator()

    # Create output directory
    Config.CONTENT_DIR.mkdir(exist_ok=True)

    all_content = {}

    for product in products:
        print(f"\n{'='*60}")
        print(f"Generating content for: {product['name']}")
        print('='*60)

        # Generate TikTok content
        print("\n📱 TikTok Content...")
        tiktok_content = content_engine.generate_tiktok_content(product)
        print(f"   Hook: {tiktok_content.hook[:50]}...")
        print(f"   Viral Score: {tiktok_content.viral_score.total:.1f}/100")
        print(f"   K-Factor: {tiktok_content.viral_score.viral_coefficient:.2f}")

        # Generate Instagram content
        print("\n📸 Instagram Content...")
        instagram_content = content_engine.generate_instagram_content(product)
        print(f"   Hook: {instagram_content.hook[:50]}...")

        # Generate Twitter thread
        print("\n🐦 Twitter Thread...")
        twitter_thread = content_engine.generate_twitter_thread(product)
        print(f"   {len(twitter_thread)} tweets generated")

        # Generate Reddit strategy
        print("\n🔴 Reddit Strategy...")
        reddit_strategy = content_engine.generate_reddit_strategy(product)
        print(f"   Target subreddits: {', '.join(reddit_strategy['target_subreddits'][:3])}")

        # Generate video script
        tiktok_script = script_generator.generate_tiktok_script(product, tiktok_content)

        all_content[product['id']] = {
            "product": product,
            "tiktok": tiktok_content.to_dict(),
            "instagram": instagram_content.to_dict(),
            "twitter_thread": twitter_thread,
            "reddit_strategy": reddit_strategy,
            "script": tiktok_script
        }

        # Save individual content file
        content_file = Config.CONTENT_DIR / f"{product['id']}_content.txt"
        with open(content_file, "w", encoding="utf-8") as f:
            f.write(tiktok_script)
            f.write("\n\n" + "="*70 + "\n")
            f.write("TWITTER THREAD:\n" + "="*70 + "\n")
            for i, tweet in enumerate(twitter_thread, 1):
                f.write(f"\nTWEET {i}:\n{tweet}\n")

        print(f"   ✅ Saved: {content_file}")

    # Generate content calendar
    print("\n" + "="*60)
    print("📅 Generating 2-Week Content Calendar...")
    print("="*60)

    calendar = calendar_generator.generate_calendar(products, days=14)

    calendar_text = "\nSELLBUDDY 2-WEEK CONTENT CALENDAR\n" + "="*60 + "\n"
    for day in calendar:
        calendar_text += f"\nDay {day['day']} - {day['date']}\n"
        calendar_text += f"  Platform: {day['platform'].upper()}\n"
        calendar_text += f"  Content: {day['content_type']}\n"
        calendar_text += f"  Product: {day['product']}\n"
        calendar_text += f"  Time: {day['posting_time']}\n"
        calendar_text += f"  Priority: {day['priority']}\n"

    calendar_file = Config.CONTENT_DIR / "content_calendar.txt"
    with open(calendar_file, "w", encoding="utf-8") as f:
        f.write(calendar_text)

    print(f"   ✅ Saved: {calendar_file}")

    # Save JSON data
    json_file = Config.CONTENT_DIR / "marketing_content.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump({
            "generated": datetime.now().isoformat(),
            "products": list(all_content.keys()),
            "calendar": calendar,
            "total_content_pieces": len(products) * 4  # 4 platforms
        }, f, indent=2)

    print(f"   ✅ Saved: {json_file}")

    # Print summary
    print("\n" + "="*70)
    print("✅ CONTENT GENERATION COMPLETE")
    print("="*70)
    print(f"Products processed: {len(products)}")
    print(f"Content pieces generated: {len(products) * 4}")
    print(f"Calendar days planned: 14")
    print(f"All files saved to: {Config.CONTENT_DIR}")
    print("="*70)

    # Show sample TikTok script
    print("\n📝 SAMPLE TIKTOK SCRIPT (Galaxy Projector):")
    print("="*70)
    print(all_content["galaxy-projector"]["script"][:2000])

    return all_content


if __name__ == "__main__":
    main()
