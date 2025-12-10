// SellBuddy Product Catalog
// Products are loaded from data/products.json

const STORE_URL = window.location.origin;

// Default products (fallback)
const defaultProducts = [
    {
        id: "galaxy-star-projector",
        name: "Galaxy Star Projector",
        category: "Smart Home",
        description: "Transform any room into a mesmerizing galaxy. 16 colors, Bluetooth speaker, timer function.",
        price: 34.99,
        originalPrice: 59.99,
        image: "https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=400&h=400&fit=crop",
        discount: 42
    },
    {
        id: "electric-back-scrubber",
        name: "Electric Back Scrubber",
        category: "Personal Care",
        description: "Long handle electric body brush. Waterproof, rechargeable, 2 speed settings.",
        price: 39.99,
        originalPrice: 69.99,
        image: "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400&h=400&fit=crop",
        discount: 43
    },
    {
        id: "led-strip-lights",
        name: "LED Strip Lights RGB",
        category: "Smart Home",
        description: "50ft smart LED strips with app control. Music sync, 16M colors, works with Alexa.",
        price: 27.99,
        originalPrice: 49.99,
        image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop",
        discount: 44
    },
    {
        id: "no-pull-dog-harness",
        name: "No-Pull Dog Harness",
        category: "Pet Supplies",
        description: "Adjustable, breathable mesh harness. Reflective straps for night walks. All sizes.",
        price: 24.99,
        originalPrice: 44.99,
        image: "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=400&h=400&fit=crop",
        discount: 44
    },
    {
        id: "photo-projection-necklace",
        name: "Photo Projection Necklace",
        category: "Accessories",
        description: "Custom photo projection pendant. Upload your photo, we'll create your memory.",
        price: 29.99,
        originalPrice: 54.99,
        image: "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=400&h=400&fit=crop",
        discount: 45
    },
    {
        id: "portable-blender",
        name: "Portable Blender USB",
        category: "Kitchen",
        description: "Personal size blender. USB rechargeable, 6 blades, perfect for smoothies on-the-go.",
        price: 24.99,
        originalPrice: 44.99,
        image: "https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=400&h=400&fit=crop",
        discount: 44
    },
    {
        id: "posture-corrector",
        name: "Posture Corrector Pro",
        category: "Health & Wellness",
        description: "Adjustable back brace for better posture. Breathable, invisible under clothes.",
        price: 19.99,
        originalPrice: 39.99,
        image: "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop",
        discount: 50
    },
    {
        id: "sunset-lamp",
        name: "Sunset Projection Lamp",
        category: "Smart Home",
        description: "Instagram-famous sunset lamp. 180 degree rotation, USB powered, multiple colors.",
        price: 22.99,
        originalPrice: 39.99,
        image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop",
        discount: 43
    }
];

// Render products to the grid
function renderProducts(products) {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    grid.innerHTML = products.map(product => `
        <div class="product-card">
            <img src="${product.image}" alt="${product.name}" class="product-image" loading="lazy"
                 onerror="this.src='https://via.placeholder.com/400x400?text=Product+Image'">
            <div class="product-info">
                <span class="product-category">${product.category}</span>
                <h3 class="product-name">${product.name}</h3>
                <p class="product-description">${product.description}</p>
                <div class="product-price">
                    <span class="current-price">$${product.price.toFixed(2)}</span>
                    ${product.originalPrice ? `
                        <span class="original-price">$${product.originalPrice.toFixed(2)}</span>
                        <span class="discount-badge">${product.discount}% OFF</span>
                    ` : ''}
                </div>
                <button class="add-to-cart snipcart-add-item"
                    data-item-id="${product.id}"
                    data-item-name="${product.name}"
                    data-item-price="${product.price}"
                    data-item-url="${STORE_URL}/store/index.html"
                    data-item-description="${product.description}"
                    data-item-image="${product.image}">
                    Add to Cart
                </button>
            </div>
        </div>
    `).join('');
}

// Load products from JSON file or use defaults
async function loadProducts() {
    try {
        const response = await fetch('../data/products.json');
        if (response.ok) {
            const data = await response.json();
            renderProducts(data.products || defaultProducts);
        } else {
            renderProducts(defaultProducts);
        }
    } catch (error) {
        console.log('Loading default products');
        renderProducts(defaultProducts);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', loadProducts);
