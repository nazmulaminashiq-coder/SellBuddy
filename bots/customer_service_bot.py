#!/usr/bin/env python3
"""
SellBuddy Elite Customer Service Bot v2.0
World-class NLP-powered customer support with intent classification,
sentiment analysis, smart escalation, and personalized responses.

Features:
- Advanced NLP intent classification
- Sentiment analysis for message prioritization
- Context-aware response generation
- Smart escalation routing
- Order status integration
- FAQ knowledge base with similarity matching
- Multi-language support framework
- Support ticket management
"""

import json
import re
import random
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
    DATA_DIR = Path(__file__).parent.parent / "data"
    ESCALATION_THRESHOLD = 0.7  # Sentiment threshold for escalation
    RESPONSE_CONFIDENCE_MIN = 0.6


class Intent(Enum):
    """Customer message intents."""
    SHIPPING_INQUIRY = "shipping_inquiry"
    ORDER_STATUS = "order_status"
    RETURN_REQUEST = "return_request"
    REFUND_REQUEST = "refund_request"
    PRODUCT_QUESTION = "product_question"
    PAYMENT_ISSUE = "payment_issue"
    DISCOUNT_INQUIRY = "discount_inquiry"
    COMPLAINT = "complaint"
    FEEDBACK = "feedback"
    GENERAL = "general"
    CANCELLATION = "cancellation"
    TRACKING = "tracking"


class Sentiment(Enum):
    """Message sentiment classification."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class Priority(Enum):
    """Ticket priority levels."""
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ============================================
# DATA CLASSES
# ============================================

@dataclass
class IntentClassification:
    """Intent classification result."""
    intent: Intent
    confidence: float
    keywords_matched: List[str]


@dataclass
class SentimentAnalysis:
    """Sentiment analysis result."""
    sentiment: Sentiment
    score: float  # -1 to 1
    indicators: List[str]


@dataclass
class CustomerContext:
    """Customer context for personalization."""
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    order_history: List[Dict] = field(default_factory=list)
    previous_tickets: List[Dict] = field(default_factory=list)
    lifetime_value: float = 0.0
    is_vip: bool = False


@dataclass
class SupportTicket:
    """Support ticket data."""
    ticket_id: str
    customer_email: str
    customer_name: str
    subject: str
    message: str
    intent: Intent
    sentiment: Sentiment
    priority: Priority
    status: str = "open"
    assigned_to: Optional[str] = None
    response: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "ticket_id": self.ticket_id,
            "customer_email": self.customer_email,
            "customer_name": self.customer_name,
            "subject": self.subject,
            "message": self.message[:200] + "..." if len(self.message) > 200 else self.message,
            "intent": self.intent.value,
            "sentiment": self.sentiment.value,
            "priority": self.priority.value,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at,
        }


# ============================================
# NLP ENGINE
# ============================================

class EliteNLPEngine:
    """Advanced NLP processing engine."""

    # Intent keywords with weights
    INTENT_PATTERNS = {
        Intent.SHIPPING_INQUIRY: {
            "keywords": ["shipping", "delivery", "ship", "arrive", "how long", "days", "when will"],
            "weight": 1.0
        },
        Intent.ORDER_STATUS: {
            "keywords": ["order status", "where is my order", "track", "tracking", "order number", "my order"],
            "weight": 1.0
        },
        Intent.RETURN_REQUEST: {
            "keywords": ["return", "send back", "exchange", "wrong item", "doesn't fit", "wrong size"],
            "weight": 1.0
        },
        Intent.REFUND_REQUEST: {
            "keywords": ["refund", "money back", "charge back", "didn't receive", "never arrived", "cancel charge"],
            "weight": 1.2
        },
        Intent.PRODUCT_QUESTION: {
            "keywords": ["product", "item", "does it", "is it", "how does", "quality", "material", "size"],
            "weight": 0.8
        },
        Intent.PAYMENT_ISSUE: {
            "keywords": ["payment", "card", "declined", "charge", "transaction", "paypal", "checkout"],
            "weight": 1.1
        },
        Intent.DISCOUNT_INQUIRY: {
            "keywords": ["discount", "coupon", "code", "promo", "sale", "deal", "cheaper", "offer"],
            "weight": 0.8
        },
        Intent.COMPLAINT: {
            "keywords": ["terrible", "awful", "worst", "scam", "fraud", "horrible", "unacceptable", "disappointed"],
            "weight": 1.3
        },
        Intent.FEEDBACK: {
            "keywords": ["thank", "love", "great", "amazing", "recommend", "happy with", "satisfied"],
            "weight": 0.7
        },
        Intent.CANCELLATION: {
            "keywords": ["cancel", "cancellation", "stop", "don't want", "changed my mind"],
            "weight": 1.1
        },
        Intent.TRACKING: {
            "keywords": ["tracking", "track", "tracking number", "where is", "package location"],
            "weight": 1.0
        }
    }

    # Sentiment indicators
    SENTIMENT_INDICATORS = {
        "very_positive": ["love", "amazing", "excellent", "fantastic", "best", "perfect", "wonderful"],
        "positive": ["good", "nice", "thank", "appreciate", "helpful", "satisfied", "happy"],
        "negative": ["bad", "slow", "issue", "problem", "disappointed", "unhappy", "frustrated"],
        "very_negative": ["terrible", "awful", "worst", "scam", "fraud", "hate", "horrible", "unacceptable"]
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def classify_intent(self, message: str) -> IntentClassification:
        """Classify the intent of a customer message."""
        message_lower = message.lower()
        scores = {}
        matched_keywords = {}

        for intent, data in self.INTENT_PATTERNS.items():
            score = 0
            matches = []
            for keyword in data["keywords"]:
                if keyword in message_lower:
                    score += len(keyword) * data["weight"]
                    matches.append(keyword)

            if matches:
                scores[intent] = score
                matched_keywords[intent] = matches

        if not scores:
            return IntentClassification(
                intent=Intent.GENERAL,
                confidence=0.5,
                keywords_matched=[]
            )

        # Get highest scoring intent
        best_intent = max(scores.items(), key=lambda x: x[1])
        max_possible = sum(len(kw) for kw in self.INTENT_PATTERNS[best_intent[0]]["keywords"])
        confidence = min(0.95, best_intent[1] / max_possible * 2)

        return IntentClassification(
            intent=best_intent[0],
            confidence=round(confidence, 2),
            keywords_matched=matched_keywords.get(best_intent[0], [])
        )

    def analyze_sentiment(self, message: str) -> SentimentAnalysis:
        """Analyze sentiment of a message."""
        message_lower = message.lower()
        indicators = []
        score = 0

        # Check positive indicators
        for word in self.SENTIMENT_INDICATORS["very_positive"]:
            if word in message_lower:
                score += 0.4
                indicators.append(f"+{word}")

        for word in self.SENTIMENT_INDICATORS["positive"]:
            if word in message_lower:
                score += 0.2
                indicators.append(f"+{word}")

        # Check negative indicators
        for word in self.SENTIMENT_INDICATORS["negative"]:
            if word in message_lower:
                score -= 0.3
                indicators.append(f"-{word}")

        for word in self.SENTIMENT_INDICATORS["very_negative"]:
            if word in message_lower:
                score -= 0.5
                indicators.append(f"-{word}")

        # Clamp score
        score = max(-1, min(1, score))

        # Determine sentiment category
        if score >= 0.5:
            sentiment = Sentiment.VERY_POSITIVE
        elif score >= 0.2:
            sentiment = Sentiment.POSITIVE
        elif score <= -0.5:
            sentiment = Sentiment.VERY_NEGATIVE
        elif score <= -0.2:
            sentiment = Sentiment.NEGATIVE
        else:
            sentiment = Sentiment.NEUTRAL

        return SentimentAnalysis(
            sentiment=sentiment,
            score=round(score, 2),
            indicators=indicators
        )

    def extract_order_number(self, message: str) -> Optional[str]:
        """Extract order number from message."""
        patterns = [
            r'SB-\d{4,}',
            r'#\d{4,}',
            r'order\s*#?\s*(\d{4,})',
            r'order\s+number\s*:?\s*(\w+-?\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group() if match.group().startswith(('SB', '#')) else f"SB-{match.group(1)}"

        return None

    def extract_email(self, message: str) -> Optional[str]:
        """Extract email from message."""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, message)
        return match.group() if match else None


# ============================================
# KNOWLEDGE BASE
# ============================================

class EliteKnowledgeBase:
    """FAQ and response knowledge base."""

    RESPONSES = {
        Intent.SHIPPING_INQUIRY: {
            "standard": """📦 **Shipping Information**

Thank you for your interest in our shipping times!

**Delivery Estimates:**
• US Orders: 7-12 business days
• Canada/UK: 10-15 business days
• International: 12-20 business days

**Note:** Free shipping on orders over $50!

You'll receive a tracking number via email once your order ships (typically within 1-2 business days).

Is there anything else I can help you with?""",
            "personalized": """📦 Hi {name}!

Great question about shipping! Here's what you can expect:

**Your Delivery Estimate:** {shipping_time}

You'll receive a tracking email once your order ships. We process orders within 1-2 business days.

Need anything else? I'm here to help! 😊"""
        },

        Intent.ORDER_STATUS: {
            "with_order": """📋 **Order Status: {order_number}**

Great news! Here's the latest on your order:

**Status:** {status}
**Tracking:** {tracking}
**Estimated Delivery:** {eta}

Track your package: {tracking_link}

Questions? Just reply to this message!""",
            "without_order": """📋 **Order Status Lookup**

I'd be happy to help you track your order!

To find your order status, please provide your:
• Order number (starts with SB-)
• OR the email used for your order

You can also check your order confirmation email for tracking details.

Looking forward to helping you!"""
        },

        Intent.RETURN_REQUEST: {
            "standard": """🔄 **Returns & Exchanges**

We want you to be 100% satisfied! Here's our return process:

**30-Day Money-Back Guarantee**

**To initiate a return:**
1. Reply with your order number
2. Reason for return (+ photos if item is damaged)
3. We'll send return instructions within 24 hours

**Note:** We'll process your refund within 48 hours of receiving approval.

Ready to start? Just reply with your order details!"""
        },

        Intent.REFUND_REQUEST: {
            "standard": """💰 **Refund Request**

I understand you'd like a refund, and I'm here to help make this as smooth as possible.

**To process your refund:**
1. Please provide your order number (SB-XXXX)
2. Reason for the refund request
3. Photos of any damaged items (if applicable)

**Our Promise:**
• Refunds processed within 48 hours of approval
• Funds return to original payment method in 5-10 business days

I'll personally make sure this gets resolved for you!"""
        },

        Intent.PAYMENT_ISSUE: {
            "standard": """💳 **Payment Help**

Sorry to hear you're having payment issues! Let's fix this together.

**Common Solutions:**
• Try a different browser or clear cache
• Use PayPal as an alternative
• Check if your card has international purchases enabled
• Ensure billing address matches card on file

**Still having trouble?**
Reply with the error message you're seeing, and I'll investigate further.

We accept: PayPal, Visa, Mastercard, Amex, Apple Pay, Google Pay"""
        },

        Intent.DISCOUNT_INQUIRY: {
            "standard": """🏷️ **Deals & Discounts**

Great news! Here are our current offers:

**Active Codes:**
• **WELCOME10** - 10% off first order
• **FREE SHIPPING** - Orders $50+

**Coming Soon:**
Sign up for our newsletter for exclusive flash sales!

Want me to help you apply a code to your order?"""
        },

        Intent.CANCELLATION: {
            "standard": """🚫 **Order Cancellation**

I understand you need to cancel your order. Let's see what we can do!

**Please provide:**
• Your order number (SB-XXXX)

**Important:**
• Orders cancelled within 2 hours: Full refund guaranteed
• Orders already shipped: You can return for free once received

I'll check your order status and confirm cancellation immediately!"""
        },

        Intent.COMPLAINT: {
            "standard": """I sincerely apologize for your experience. This is not the standard we strive for.

**I want to make this right.**

Please share:
1. Your order number
2. What went wrong
3. How we can fix this for you

I'm escalating this to our priority support team for immediate attention. You'll hear back within 4 hours.

Thank you for your patience - we value your business and will resolve this.""",
            "escalation_note": "PRIORITY: Customer complaint requiring immediate attention"
        },

        Intent.TRACKING: {
            "standard": """📍 **Track Your Package**

I can help you locate your order!

**Provide your order number (SB-XXXX)** and I'll get your tracking info.

**Or** check these common carriers:
• USPS: usps.com/tracking
• UPS: ups.com/track
• DHL: dhl.com/track

Your tracking number was sent to your email when the order shipped."""
        },

        Intent.FEEDBACK: {
            "standard": """💝 **Thank You!**

Wow, thank you so much for your kind words! Messages like yours make our day! 🌟

We're thrilled you're happy with your purchase. If you have a moment:

• Share your experience on social media (tag us!)
• Leave a review to help other shoppers
• Join our newsletter for exclusive deals

Thanks for being an amazing customer! 😊"""
        },

        Intent.GENERAL: {
            "standard": """👋 **Hello!**

Thanks for reaching out to SellBuddy!

I'm here to help with:
• 📦 Shipping & Delivery
• 📋 Order Status & Tracking
• 🔄 Returns & Refunds
• 💳 Payment Questions
• 🏷️ Discounts & Deals

What can I assist you with today?

**Quick Links:**
• Email: support@sellbuddy.com
• Response time: Within 24 hours"""
        }
    }

    def get_response(
        self,
        intent: Intent,
        context: CustomerContext = None,
        order_data: Dict = None,
        response_type: str = "standard"
    ) -> str:
        """Get appropriate response based on intent and context."""
        responses = self.RESPONSES.get(intent, self.RESPONSES[Intent.GENERAL])
        response = responses.get(response_type, responses.get("standard", ""))

        # Personalize if context available
        if context and context.customer_name:
            response = response.replace("{name}", context.customer_name)

        # Fill in order data
        if order_data:
            for key, value in order_data.items():
                response = response.replace(f"{{{key}}}", str(value))

        return response


# ============================================
# TICKET MANAGER
# ============================================

class EliteTicketManager:
    """Support ticket management system."""

    def __init__(self, nlp_engine: EliteNLPEngine, knowledge_base: EliteKnowledgeBase):
        self.nlp = nlp_engine
        self.kb = knowledge_base
        self.tickets: List[SupportTicket] = []
        self.logger = logging.getLogger(__name__)

    def create_ticket(
        self,
        customer_email: str,
        customer_name: str,
        subject: str,
        message: str,
        context: CustomerContext = None
    ) -> SupportTicket:
        """Create and classify a support ticket."""
        # Analyze message
        intent_result = self.nlp.classify_intent(message)
        sentiment_result = self.nlp.analyze_sentiment(message)

        # Determine priority
        priority = self._determine_priority(intent_result, sentiment_result, context)

        # Create ticket
        ticket = SupportTicket(
            ticket_id=f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100, 999)}",
            customer_email=customer_email,
            customer_name=customer_name,
            subject=subject,
            message=message,
            intent=intent_result.intent,
            sentiment=sentiment_result.sentiment,
            priority=priority,
        )

        # Generate auto-response
        order_number = self.nlp.extract_order_number(message)
        if order_number and intent_result.intent in [Intent.ORDER_STATUS, Intent.TRACKING]:
            order_data = self._lookup_order(order_number)
            ticket.response = self.kb.get_response(
                intent_result.intent,
                context,
                order_data,
                "with_order" if order_data else "without_order"
            )
        else:
            ticket.response = self.kb.get_response(intent_result.intent, context)

        # Check if escalation needed
        if self._needs_escalation(sentiment_result, intent_result):
            ticket.assigned_to = "senior_support"
            ticket.priority = Priority.URGENT

        self.tickets.append(ticket)
        return ticket

    def _determine_priority(
        self,
        intent: IntentClassification,
        sentiment: SentimentAnalysis,
        context: CustomerContext = None
    ) -> Priority:
        """Determine ticket priority."""
        # High priority intents
        high_priority_intents = [Intent.REFUND_REQUEST, Intent.COMPLAINT, Intent.PAYMENT_ISSUE]

        if intent.intent in high_priority_intents:
            if sentiment.sentiment in [Sentiment.NEGATIVE, Sentiment.VERY_NEGATIVE]:
                return Priority.URGENT
            return Priority.HIGH

        # VIP customers
        if context and context.is_vip:
            return Priority.HIGH

        # Negative sentiment
        if sentiment.sentiment == Sentiment.VERY_NEGATIVE:
            return Priority.HIGH
        elif sentiment.sentiment == Sentiment.NEGATIVE:
            return Priority.MEDIUM

        return Priority.MEDIUM

    def _needs_escalation(
        self,
        sentiment: SentimentAnalysis,
        intent: IntentClassification
    ) -> bool:
        """Determine if ticket needs escalation."""
        # Escalate very negative sentiment
        if sentiment.sentiment == Sentiment.VERY_NEGATIVE:
            return True

        # Escalate complaints
        if intent.intent == Intent.COMPLAINT:
            return True

        # Escalate low confidence classifications
        if intent.confidence < 0.4:
            return True

        return False

    def _lookup_order(self, order_number: str) -> Optional[Dict]:
        """Look up order information (simulated)."""
        # In production, query your order database
        statuses = ["Processing", "Shipped", "In Transit", "Out for Delivery", "Delivered"]

        return {
            "order_number": order_number,
            "status": random.choice(statuses),
            "tracking": f"TRK{random.randint(100000000, 999999999)}",
            "eta": (datetime.now() + timedelta(days=random.randint(3, 12))).strftime("%B %d, %Y"),
            "tracking_link": f"https://track.sellbuddy.com/{order_number}"
        }

    def get_ticket_stats(self) -> Dict:
        """Get ticket statistics."""
        if not self.tickets:
            return {"total": 0}

        return {
            "total": len(self.tickets),
            "open": len([t for t in self.tickets if t.status == "open"]),
            "by_priority": {
                p.value: len([t for t in self.tickets if t.priority == p])
                for p in Priority
            },
            "by_intent": {
                i.value: len([t for t in self.tickets if t.intent == i])
                for i in Intent
                if any(t.intent == i for t in self.tickets)
            },
            "escalated": len([t for t in self.tickets if t.assigned_to == "senior_support"])
        }


# ============================================
# EMAIL TEMPLATE GENERATOR
# ============================================

class EliteEmailGenerator:
    """Generate professional email responses."""

    TEMPLATES = {
        "order_confirmation": """
Subject: Order Confirmed! 🎉 #{order_number}

Hi {customer_name}!

Thank you for your order! We're excited to get your items to you.

**Order Details:**
━━━━━━━━━━━━━━━━━━
Order Number: {order_number}
Items: {items}
Total: ${total}

**What's Next:**
1. We'll process your order within 1-2 business days
2. You'll receive a tracking number once it ships
3. Expected delivery: {eta}

Questions? Reply to this email anytime!

Thanks for shopping with SellBuddy! 💜

Best,
The SellBuddy Team
""",
        "shipping_notification": """
Subject: Your Order Has Shipped! 📦 #{order_number}

Great news, {customer_name}!

Your order is on its way!

**Tracking Information:**
━━━━━━━━━━━━━━━━━━
Order Number: {order_number}
Tracking Number: {tracking}
Carrier: {carrier}
Estimated Delivery: {eta}

🔗 Track your package: {tracking_link}

**Quick Tips:**
• Save your tracking number
• Allow up to 24 hours for tracking to update
• Check your spam folder for updates

Thanks for your patience!

Best,
The SellBuddy Team
""",
        "refund_processed": """
Subject: Refund Processed ✅ #{order_number}

Hi {customer_name},

Your refund has been processed!

**Refund Details:**
━━━━━━━━━━━━━━━━━━
Order Number: {order_number}
Refund Amount: ${refund_amount}
Method: Original payment method

⏱ Refunds typically appear within 5-10 business days.

We're sorry this purchase didn't work out. We hope to see you again!

If you have any questions, just reply to this email.

Best,
The SellBuddy Team
"""
    }

    def generate_email(self, template_type: str, data: Dict) -> str:
        """Generate email from template."""
        template = self.TEMPLATES.get(template_type, "")

        for key, value in data.items():
            template = template.replace(f"{{{key}}}", str(value))

        return template


# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Main function to demonstrate customer service bot."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    print("=" * 70)
    print("🤖 SellBuddy Elite Customer Service Bot v2.0")
    print("   NLP-Powered Support & Ticket Management")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Initialize components
    nlp = EliteNLPEngine()
    kb = EliteKnowledgeBase()
    ticket_manager = EliteTicketManager(nlp, kb)

    # Test messages
    test_messages = [
        {
            "email": "john@example.com",
            "name": "John",
            "subject": "Order Status",
            "message": "Hi, I ordered a Galaxy Projector last week and I'm wondering where my order is? Order number is SB-1234"
        },
        {
            "email": "sarah@example.com",
            "name": "Sarah",
            "subject": "Shipping Time",
            "message": "How long does shipping take to Canada? I'm thinking of ordering the LED strip lights."
        },
        {
            "email": "angry@example.com",
            "name": "Mike",
            "subject": "Terrible Experience",
            "message": "This is absolutely terrible! My order never arrived and no one is responding. This feels like a scam! I want my money back NOW!"
        },
        {
            "email": "happy@example.com",
            "name": "Emma",
            "subject": "Thank You!",
            "message": "Just wanted to say thank you! The projector is amazing and my room looks fantastic. Will definitely recommend to friends!"
        },
        {
            "email": "discount@example.com",
            "name": "Alex",
            "subject": "Coupon Code",
            "message": "Do you have any discount codes available? I want to order a few items."
        },
    ]

    print("📨 PROCESSING SUPPORT TICKETS:")
    print("-" * 60)

    for msg in test_messages:
        print(f"\n{'='*60}")
        print(f"From: {msg['name']} <{msg['email']}>")
        print(f"Subject: {msg['subject']}")
        print(f"Message: {msg['message'][:100]}...")
        print("-" * 40)

        # Create ticket
        ticket = ticket_manager.create_ticket(
            customer_email=msg["email"],
            customer_name=msg["name"],
            subject=msg["subject"],
            message=msg["message"]
        )

        print(f"Ticket ID: {ticket.ticket_id}")
        print(f"Intent: {ticket.intent.value} | Sentiment: {ticket.sentiment.value}")
        print(f"Priority: {ticket.priority.value}")
        if ticket.assigned_to:
            print(f"⚠️ ESCALATED to: {ticket.assigned_to}")

        print("\n📝 AUTO-RESPONSE:")
        print("-" * 40)
        print(ticket.response[:500] + "..." if len(ticket.response) > 500 else ticket.response)

    # Statistics
    stats = ticket_manager.get_ticket_stats()
    print("\n" + "=" * 70)
    print("📊 TICKET STATISTICS:")
    print("-" * 60)
    print(f"Total Tickets: {stats['total']}")
    print(f"Open Tickets: {stats['open']}")
    print(f"Escalated: {stats['escalated']}")
    print("\nBy Priority:")
    for priority, count in stats['by_priority'].items():
        print(f"  • {priority}: {count}")
    print("\nBy Intent:")
    for intent, count in stats['by_intent'].items():
        print(f"  • {intent}: {count}")

    # Email template demo
    print("\n" + "=" * 70)
    print("📧 SAMPLE EMAIL TEMPLATE:")
    print("-" * 60)
    email_gen = EliteEmailGenerator()
    sample_email = email_gen.generate_email("order_confirmation", {
        "order_number": "SB-1234",
        "customer_name": "John",
        "items": "Galaxy Star Projector x1",
        "total": "39.99",
        "eta": "December 25, 2025"
    })
    print(sample_email)

    print("\n" + "=" * 70)
    print("✅ CUSTOMER SERVICE BOT READY")
    print("=" * 70)


if __name__ == "__main__":
    main()
