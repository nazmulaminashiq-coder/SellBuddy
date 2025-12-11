/**
 * SellBuddy Product Catalog v3.0
 * Full SEO-optimized product listings with search, filter, reviews, and quick view
 */

const STORE_URL = 'https://nazmulaminashiq-coder.github.io/SellBuddy/store';

// Enhanced product catalog
const products = [
    {
        id: "galaxy-star-projector-pro",
        name: "Galaxy Star Projector Pro",
        category: "Smart Home",
        description: "Transform any room into a mesmerizing galaxy with 16 million colors, built-in Bluetooth speaker, and smart timer. The #1 TikTok viral product of 2025.",
        price: 34.99,
        originalPrice: 59.99,
        discount: 42,
        image: "https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=600&h=600&fit=crop&q=80",
        rating: 4.8,
        reviews: 2847,
        badge: "BESTSELLER",
        features: ["16M colors", "Bluetooth speaker", "Timer", "Remote control"],
        tags: ["viral", "tiktok", "bedroom", "gift"]
    },
    {
        id: "posture-corrector-pro",
        name: "Posture Corrector Pro",
        category: "Health & Wellness",
        description: "Fix your posture naturally with our doctor-recommended back brace. Invisible under clothes, comfortable for all-day wear.",
        price: 24.99,
        originalPrice: 44.99,
        discount: 44,
        image: "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600&h=600&fit=crop&q=80",
        rating: 4.7,
        reviews: 3421,
        badge: "TOP RATED",
        features: ["Invisible design", "Breathable mesh", "Adjustable", "Doctor recommended"],
        tags: ["health", "office", "posture", "wellness"]
    },
    {
        id: "led-strip-lights-smart",
        name: "Smart LED Strip Lights 65ft",
        category: "Smart Home",
        description: "65ft of stunning RGB LED lights with app control, music sync, and Alexa compatibility. Transform any room into an aesthetic paradise.",
        price: 29.99,
        originalPrice: 54.99,
        discount: 45,
        image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&h=600&fit=crop&q=80",
        rating: 4.6,
        reviews: 5234,
        badge: "VIRAL",
        features: ["65ft length", "Music sync", "App control", "Works with Alexa"],
        tags: ["viral", "gaming", "room-decor", "rgb"]
    },
    {
        id: "portable-blender-usb",
        name: "Portable Blender USB-C",
        category: "Kitchen",
        description: "Fresh smoothies anywhere! USB-C rechargeable blender with 6 powerful blades. Perfect for gym, office, or travel.",
        price: 27.99,
        originalPrice: 49.99,
        discount: 44,
        image: "https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=600&h=600&fit=crop&q=80",
        rating: 4.7,
        reviews: 4102,
        badge: "GYM ESSENTIAL",
        features: ["USB-C charging", "6 blades", "20oz capacity", "15+ blends/charge"],
        tags: ["fitness", "gym", "health", "smoothie"]
    },
    {
        id: "no-pull-dog-harness",
        name: "No-Pull Dog Harness",
        category: "Pet Supplies",
        description: "Adjustable, breathable mesh harness with reflective straps for night walks. Stops pulling instantly.",
        price: 24.99,
        originalPrice: 44.99,
        discount: 44,
        image: "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=600&h=600&fit=crop&q=80",
        rating: 4.8,
        reviews: 2156,
        badge: "PET FAVORITE",
        features: ["No-pull design", "Reflective", "Breathable", "All sizes"],
        tags: ["pet", "dog", "walking", "safety"]
    },
    {
        id: "photo-projection-necklace",
        name: "Photo Projection Necklace",
        category: "Accessories",
        description: "Custom photo projection pendant. Upload your favorite photo and we'll create a magical memory you can wear.",
        price: 29.99,
        originalPrice: 54.99,
        discount: 45,
        image: "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600&h=600&fit=crop&q=80",
        rating: 4.9,
        reviews: 1823,
        badge: "PERFECT GIFT",
        features: ["Custom photo", "Sterling silver", "Adjustable chain", "Gift box"],
        tags: ["gift", "personalized", "jewelry", "valentine"]
    },
    {
        id: "sunset-projection-lamp",
        name: "Sunset Projection Lamp",
        category: "Smart Home",
        description: "Instagram-famous sunset lamp. Create stunning golden hour vibes any time of day. 180 rotation, USB powered.",
        price: 22.99,
        originalPrice: 39.99,
        discount: 43,
        image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&h=600&fit=crop&q=80",
        rating: 4.6,
        reviews: 3567,
        badge: "INSTAGRAM FAMOUS",
        features: ["180 rotation", "USB powered", "Multiple colors", "Perfect for photos"],
        tags: ["instagram", "aesthetic", "photography", "decor"]
    },
    {
        id: "ice-roller-face",
        name: "Ice Roller Face Massager",
        category: "Beauty Tools",
        description: "Depuff and refresh your skin instantly with our ice roller. Reduces puffiness, tightens pores. TikTok skincare essential!",
        price: 14.99,
        originalPrice: 29.99,
        discount: 50,
        image: "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=600&h=600&fit=crop&q=80",
        rating: 4.7,
        reviews: 4521,
        badge: "50% OFF",
        features: ["Reduces puffiness", "Tightens pores", "Stainless steel", "Stays cold"],
        tags: ["skincare", "beauty", "tiktok", "self-care"]
    }
];

// Get unique categories
const categories = [...new Set(products.map(p => p.category))];

// State
let filteredProducts = [...products];
let currentCategory = 'all';
let currentSort = 'featured';
let searchQuery = '';

/**
 * Render star rating
 */
function renderStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalf = rating % 1 >= 0.5;
    let stars = '\u2605'.repeat(fullStars);
    if (hasHalf) stars += '\u00BD';
    stars += '\u2606'.repeat(5 - fullStars - (hasHalf ? 1 : 0));
    return stars;
}

/**
 * Filter and sort products
 */
function filterProducts() {
    filteredProducts = products.filter(product => {
        // Category filter
        if (currentCategory !== 'all' && product.category !== currentCategory) {
            return false;
        }

        // Search filter
        if (searchQuery) {
            const query = searchQuery.toLowerCase();
            const searchFields = [
                product.name,
                product.description,
                product.category,
                ...(product.tags || [])
            ].map(f => f.toLowerCase());

            return searchFields.some(field => field.includes(query));
        }

        return true;
    });

    // Sort
    switch (currentSort) {
        case 'price-low':
            filteredProducts.sort((a, b) => a.price - b.price);
            break;
        case 'price-high':
            filteredProducts.sort((a, b) => b.price - a.price);
            break;
        case 'rating':
            filteredProducts.sort((a, b) => b.rating - a.rating);
            break;
        case 'newest':
            filteredProducts.reverse();
            break;
        case 'discount':
            filteredProducts.sort((a, b) => b.discount - a.discount);
            break;
        default:
            break;
    }

    renderProducts(filteredProducts);
    updateResultsCount();

    // Track search
    if (searchQuery && window.SellBuddyAnalytics) {
        window.SellBuddyAnalytics.trackSearch(searchQuery);
    }
}

/**
 * Update results count
 */
function updateResultsCount() {
    const countEl = document.getElementById('resultsCount');
    if (countEl) {
        countEl.textContent = `${filteredProducts.length} product${filteredProducts.length !== 1 ? 's' : ''}`;
    }
}

/**
 * Render filter controls
 */
function renderFilters() {
    const filtersContainer = document.getElementById('productFilters');
    if (!filtersContainer) return;

    filtersContainer.innerHTML = `
        <div class="filters-bar">
            <div class="search-box">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="M21 21l-4.35-4.35"></path>
                </svg>
                <input type="text" id="searchInput" placeholder="Search products..." value="${searchQuery}">
                ${searchQuery ? '<button class="clear-search" onclick="clearSearch()">&times;</button>' : ''}
            </div>

            <div class="filter-controls">
                <div class="filter-group">
                    <label for="categoryFilter">Category:</label>
                    <select id="categoryFilter" onchange="setCategory(this.value)">
                        <option value="all" ${currentCategory === 'all' ? 'selected' : ''}>All Categories</option>
                        ${categories.map(cat =>
                            `<option value="${cat}" ${currentCategory === cat ? 'selected' : ''}>${cat}</option>`
                        ).join('')}
                    </select>
                </div>

                <div class="filter-group">
                    <label for="sortFilter">Sort by:</label>
                    <select id="sortFilter" onchange="setSort(this.value)">
                        <option value="featured" ${currentSort === 'featured' ? 'selected' : ''}>Featured</option>
                        <option value="price-low" ${currentSort === 'price-low' ? 'selected' : ''}>Price: Low to High</option>
                        <option value="price-high" ${currentSort === 'price-high' ? 'selected' : ''}>Price: High to Low</option>
                        <option value="rating" ${currentSort === 'rating' ? 'selected' : ''}>Top Rated</option>
                        <option value="discount" ${currentSort === 'discount' ? 'selected' : ''}>Biggest Discount</option>
                    </select>
                </div>

                <span id="resultsCount" class="results-count">${products.length} products</span>
            </div>
        </div>
    `;

    // Add search event listener
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener('input', function(e) {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                searchQuery = e.target.value.trim();
                filterProducts();
                renderFilters();
            }, 300);
        });

        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchQuery = e.target.value.trim();
                filterProducts();
            }
        });
    }
}

/**
 * Set category filter
 */
function setCategory(category) {
    currentCategory = category;
    filterProducts();
}

/**
 * Set sort order
 */
function setSort(sort) {
    currentSort = sort;
    filterProducts();
}

/**
 * Clear search
 */
function clearSearch() {
    searchQuery = '';
    filterProducts();
    renderFilters();
    document.getElementById('searchInput')?.focus();
}

/**
 * Check if product is in wishlist
 */
function isInWishlist(productId) {
    const wishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
    return wishlist.includes(productId);
}

/**
 * Toggle wishlist from product grid
 */
function toggleWishlistFromGrid(productId, event) {
    event.preventDefault();
    event.stopPropagation();

    let wishlist = JSON.parse(localStorage.getItem('wishlist') || '[]');
    const btn = event.currentTarget;
    const svg = btn.querySelector('svg');

    if (wishlist.includes(productId)) {
        wishlist = wishlist.filter(id => id !== productId);
        btn.classList.remove('active');
        svg.setAttribute('fill', 'none');
        btn.title = 'Add to wishlist';
    } else {
        wishlist.push(productId);
        btn.classList.add('active');
        svg.setAttribute('fill', 'currentColor');
        btn.title = 'Remove from wishlist';
    }

    localStorage.setItem('wishlist', JSON.stringify(wishlist));
}

/**
 * Render products to the grid
 */
function renderProducts(productList) {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;

    if (productList.length === 0) {
        grid.innerHTML = `
            <div class="no-products" style="grid-column: 1/-1; text-align: center; padding: 4rem;">
                <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" stroke-width="1.5" style="margin-bottom: 1rem;">
                    <circle cx="11" cy="11" r="8"></circle>
                    <path d="M21 21l-4.35-4.35"></path>
                </svg>
                <h3 style="color: var(--dark); margin-bottom: 0.5rem;">No products found</h3>
                <p style="color: var(--gray); margin-bottom: 1.5rem;">Try adjusting your search or filter criteria</p>
                <button class="btn btn-accent" onclick="clearSearch(); setCategory('all');">View All Products</button>
            </div>
        `;
        return;
    }

    grid.innerHTML = productList.map(product => `
        <div class="product-card" data-product-id="${product.id}">
            ${product.badge ? `<span class="product-badge">${product.badge}</span>` : ''}
            <button class="wishlist-heart ${isInWishlist(product.id) ? 'active' : ''}"
                    onclick="toggleWishlistFromGrid('${product.id}', event)"
                    title="${isInWishlist(product.id) ? 'Remove from wishlist' : 'Add to wishlist'}">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="${isInWishlist(product.id) ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                </svg>
            </button>
            <a href="product.html?id=${product.id}" class="product-image-link">
                <div class="product-image-wrapper">
                    <img src="${product.image}" alt="${product.name}" class="product-image" loading="lazy"
                         onerror="this.src='https://via.placeholder.com/400x400?text=Product'">
                </div>
            </a>
            <div class="product-info">
                <span class="product-category">${product.category}</span>
                <h3 class="product-name">
                    <a href="product.html?id=${product.id}">${product.name}</a>
                </h3>
                <p class="product-description">${product.description}</p>
                <div class="product-rating">
                    <span class="stars">${renderStars(product.rating)}</span>
                    <span class="rating-text">${product.rating} (${product.reviews.toLocaleString()})</span>
                </div>
                <div class="product-price">
                    <span class="current-price">$${product.price.toFixed(2)}</span>
                    <span class="original-price">$${product.originalPrice.toFixed(2)}</span>
                    <span class="discount-badge">${product.discount}% OFF</span>
                </div>
                <button class="add-to-cart snipcart-add-item"
                    data-item-id="${product.id}"
                    data-item-name="${product.name}"
                    data-item-price="${product.price}"
                    data-item-url="${STORE_URL}/product.html?id=${product.id}"
                    data-item-description="${product.description}"
                    data-item-image="${product.image}">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="9" cy="21" r="1"></circle>
                        <circle cx="20" cy="21" r="1"></circle>
                        <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
                    </svg>
                    Add to Cart
                </button>
            </div>
        </div>
    `).join('');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check for URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const categoryParam = urlParams.get('category');
    const searchParam = urlParams.get('search');

    if (categoryParam && categories.includes(categoryParam)) {
        currentCategory = categoryParam;
    }

    if (searchParam) {
        searchQuery = searchParam;
    }

    // Render filters and products
    renderFilters();
    filterProducts();
});

// Export for use in other scripts
window.SellBuddyProducts = {
    products,
    categories,
    filterProducts,
    setCategory,
    setSort,
    clearSearch
};
