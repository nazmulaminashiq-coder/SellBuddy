// SellBuddy Customer Support Chat Widget
// 24/7 automated FAQ responses

(function() {
    // FAQ Database
    const faqs = {
        shipping: {
            keywords: ['shipping', 'delivery', 'arrive', 'ship', 'how long', 'track', 'tracking'],
            response: "Shipping takes 7-15 business days depending on your location. You'll receive a tracking number via email once your order ships. Free shipping on orders over $50!"
        },
        returns: {
            keywords: ['return', 'refund', 'money back', 'exchange', 'wrong', 'damaged'],
            response: "We offer a 30-day money-back guarantee! If you're not satisfied, contact us at support@sellbuddy.com with your order number and we'll process your refund within 48 hours."
        },
        order: {
            keywords: ['order', 'status', 'where is', 'my order', 'purchased', 'bought'],
            response: "To check your order status, look for the tracking email we sent after shipping. Can't find it? Reply with your order number and we'll look it up for you!"
        },
        payment: {
            keywords: ['payment', 'pay', 'credit card', 'paypal', 'checkout', 'secure'],
            response: "We accept PayPal and all major credit cards. Your payment is 100% secure with SSL encryption. We never store your card details."
        },
        contact: {
            keywords: ['contact', 'email', 'phone', 'support', 'help', 'human', 'agent'],
            response: "You can reach us at support@sellbuddy.com. We respond within 24 hours, usually much faster! For urgent issues, include 'URGENT' in your subject line."
        },
        products: {
            keywords: ['quality', 'real', 'authentic', 'legit', 'good', 'reviews'],
            response: "All our products are carefully sourced and quality-tested. We have thousands of happy customers! Check out our reviews on each product page."
        },
        discount: {
            keywords: ['discount', 'coupon', 'code', 'sale', 'promo', 'deal'],
            response: "Subscribe to our newsletter for 10% off your first order! We also run seasonal sales - follow us on social media to never miss a deal."
        }
    };

    const defaultResponse = "Thanks for your message! For specific questions, please email us at support@sellbuddy.com and we'll get back to you within 24 hours. Meanwhile, check our FAQ section below the chat!";

    // Create chat widget HTML
    const chatHTML = `
        <div id="sellbuddy-chat-widget" style="
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        ">
            <!-- Chat Button -->
            <button id="chat-toggle" style="
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
                border: none;
                cursor: pointer;
                box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.3s, box-shadow 0.3s;
            ">
                <svg id="chat-icon" width="28" height="28" viewBox="0 0 24 24" fill="white">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                </svg>
                <svg id="close-icon" width="28" height="28" viewBox="0 0 24 24" fill="white" style="display: none;">
                    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
            </button>

            <!-- Chat Window -->
            <div id="chat-window" style="
                display: none;
                position: absolute;
                bottom: 70px;
                right: 0;
                width: 350px;
                height: 450px;
                background: white;
                border-radius: 16px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.15);
                overflow: hidden;
                flex-direction: column;
            ">
                <!-- Header -->
                <div style="
                    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
                    color: white;
                    padding: 16px;
                ">
                    <div style="font-weight: 600; font-size: 16px;">SellBuddy Support</div>
                    <div style="font-size: 12px; opacity: 0.9;">We typically reply instantly</div>
                </div>

                <!-- Messages -->
                <div id="chat-messages" style="
                    flex: 1;
                    padding: 16px;
                    overflow-y: auto;
                    background: #f9fafb;
                "></div>

                <!-- Input -->
                <div style="
                    padding: 12px;
                    border-top: 1px solid #e5e7eb;
                    background: white;
                ">
                    <form id="chat-form" style="display: flex; gap: 8px;">
                        <input id="chat-input" type="text" placeholder="Type your question..." style="
                            flex: 1;
                            padding: 10px 14px;
                            border: 1px solid #e5e7eb;
                            border-radius: 8px;
                            font-size: 14px;
                            outline: none;
                        ">
                        <button type="submit" style="
                            background: #6366f1;
                            color: white;
                            border: none;
                            padding: 10px 16px;
                            border-radius: 8px;
                            cursor: pointer;
                            font-weight: 500;
                        ">Send</button>
                    </form>
                </div>
            </div>
        </div>
    `;

    // Inject chat widget
    document.body.insertAdjacentHTML('beforeend', chatHTML);

    // Elements
    const chatToggle = document.getElementById('chat-toggle');
    const chatWindow = document.getElementById('chat-window');
    const chatIcon = document.getElementById('chat-icon');
    const closeIcon = document.getElementById('close-icon');
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');

    let isOpen = false;

    // Add message to chat
    function addMessage(text, isBot = false) {
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            margin-bottom: 12px;
            display: flex;
            ${isBot ? '' : 'justify-content: flex-end;'}
        `;
        messageDiv.innerHTML = `
            <div style="
                max-width: 80%;
                padding: 10px 14px;
                border-radius: ${isBot ? '4px 12px 12px 12px' : '12px 12px 4px 12px'};
                background: ${isBot ? 'white' : '#6366f1'};
                color: ${isBot ? '#1f2937' : 'white'};
                font-size: 14px;
                line-height: 1.5;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            ">${text}</div>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Find matching FAQ
    function findResponse(message) {
        const lowerMessage = message.toLowerCase();
        for (const [key, faq] of Object.entries(faqs)) {
            if (faq.keywords.some(keyword => lowerMessage.includes(keyword))) {
                return faq.response;
            }
        }
        return defaultResponse;
    }

    // Toggle chat window
    chatToggle.addEventListener('click', () => {
        isOpen = !isOpen;
        chatWindow.style.display = isOpen ? 'flex' : 'none';
        chatIcon.style.display = isOpen ? 'none' : 'block';
        closeIcon.style.display = isOpen ? 'block' : 'none';

        if (isOpen && chatMessages.children.length === 0) {
            setTimeout(() => {
                addMessage("Hi there! I'm here to help. Ask me about shipping, returns, orders, or anything else!", true);
            }, 500);
        }
    });

    // Handle message send
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;

        addMessage(message, false);
        chatInput.value = '';

        // Simulate typing delay
        setTimeout(() => {
            const response = findResponse(message);
            addMessage(response, true);
        }, 800);
    });

    // Hover effect on toggle button
    chatToggle.addEventListener('mouseenter', () => {
        chatToggle.style.transform = 'scale(1.1)';
    });
    chatToggle.addEventListener('mouseleave', () => {
        chatToggle.style.transform = 'scale(1)';
    });

})();
