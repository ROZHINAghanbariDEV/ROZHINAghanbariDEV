function formatPrice(num) {
    return '$' + num.toLocaleString('en-US');
}

function getCategoryName(cat) {
    const names = { women: 'Women', men: 'Men', kids: 'Kids', shoes: 'Shoes & Bags' };
    return names[cat] || cat;
}

function renderProducts(containerId, filter = 'all', customList = null) {
    const grid = document.getElementById(containerId);
    if (!grid) return;

    let list = customList || PRODUCTS;
    if (filter !== 'all' && !customList) list = list.filter(p => p.category === filter);

    if (list.length === 0) {
        grid.innerHTML = `
            <div class="no-results" style="grid-column:1/-1;">
                <i class="fas fa-search"></i>
                <h3>No products found</h3>
                <p>Try a different search or category</p>
            </div>`;
        return;
    }

    grid.innerHTML = list.map(p => `
        <div class="product-card">
            <div class="product-image">
                <img src="${p.img}" alt="${p.name}" onerror="this.src='https://via.placeholder.com/500x600?text=Product'">
                ${p.badge ? `<span class="product-badge ${p.badge === 'NEW' ? 'new' : ''}">${p.badge}</span>` : ''}
                <div class="product-actions">
                    <button title="Add to Wishlist" onclick="addToWishlist(${p.id})"><i class="far fa-heart"></i></button>
                    <button title="Quick View" onclick="showToast('Quick view: ${p.name.replace(/'/g, "\\'")}')"><i class="far fa-eye"></i></button>
                </div>
            </div>
            <div class="product-info">
                <div class="product-category">${getCategoryName(p.category)}</div>
                <h3 class="product-title">${p.name}</h3>
                <div class="product-rating">
                    ${'★'.repeat(Math.floor(p.rating))}${'☆'.repeat(5 - Math.floor(p.rating))}
                    <span>(${p.rating})</span>
                </div>
                <div class="product-price">
                    <span class="price-current">${formatPrice(p.price)}</span>
                    ${p.oldPrice ? `<span class="price-old">${formatPrice(p.oldPrice)}</span>` : ''}
                </div>
                <button class="add-to-cart" onclick="addToCart(${p.id})">
                    <i class="fas fa-cart-plus"></i> Add to Cart
                </button>
            </div>
        </div>
    `).join('');
}

let cart = JSON.parse(localStorage.getItem('cart')) || [];

function addToCart(id) {
    const product = PRODUCTS.find(p => p.id === id);
    const existing = cart.find(item => item.id === id);
    if (existing) existing.qty += 1;
    else cart.push({ ...product, qty: 1 });
    saveCart();
    renderCart();
    showToast(`"${product.name}" added to cart`);
}

function removeFromCart(id) {
    cart = cart.filter(item => item.id !== id);
    saveCart();
    renderCart();
}

function changeQty(id, delta) {
    const item = cart.find(i => i.id === id);
    if (!item) return;
    item.qty += delta;
    if (item.qty <= 0) { removeFromCart(id); return; }
    saveCart();
    renderCart();
}

function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
}

function updateCartCount() {
    const count = cart.reduce((sum, item) => sum + item.qty, 0);
    document.querySelectorAll('#cartCount').forEach(el => el.textContent = count);
}

function renderCart() {
    const container = document.getElementById('cartItems');
    const totalEl = document.getElementById('cartTotal');
    if (!container) return;

    if (cart.length === 0) {
        container.innerHTML = `<div class="empty-cart"><i class="fas fa-shopping-bag"></i><p>Your cart is empty</p></div>`;
        if (totalEl) totalEl.textContent = '$0';
        return;
    }

    container.innerHTML = cart.map(item => `
        <div class="cart-item">
            <img src="${item.img}" alt="${item.name}" onerror="this.src='https://via.placeholder.com/80'">
            <div class="cart-item-info">
                <h4>${item.name}</h4>
                <div class="price">${formatPrice(item.price)}</div>
                <div class="qty-control">
                    <button onclick="changeQty(${item.id}, -1)">−</button>
                    <span>${item.qty}</span>
                    <button onclick="changeQty(${item.id}, 1)">+</button>
                </div>
            </div>
            <button class="remove-item" onclick="removeFromCart(${item.id})"><i class="fas fa-trash"></i></button>
        </div>
    `).join('');

    const total = cart.reduce((sum, item) => sum + item.price * item.qty, 0);
    if (totalEl) totalEl.textContent = formatPrice(total);
}

let wishlist = JSON.parse(localStorage.getItem('wishlist')) || [];
function addToWishlist(id) {
    const product = PRODUCTS.find(p => p.id === id);
    if (wishlist.find(p => p.id === id)) {
        wishlist = wishlist.filter(p => p.id !== id);
        showToast(`"${product.name}" removed from wishlist`);
    } else {
        wishlist.push(product);
        showToast(`"${product.name}" added to wishlist`);
    }
    localStorage.setItem('wishlist', JSON.stringify(wishlist));
    updateWishlistCount();
}
function updateWishlistCount() {
    document.querySelectorAll('#wishlistCount').forEach(el => el.textContent = wishlist.length);
}

let toastTimeout;
function showToast(msg) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    document.getElementById('toastMsg').textContent = msg;
    toast.classList.add('show');
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => toast.classList.remove('show'), 3000);
}

function performSearch(query) {
    const q = query.trim();
    if (!q) return;
    window.location.href = 'search.html?q=' + encodeURIComponent(q);
}

function initSearch() {
    document.querySelectorAll('.search-box').forEach(box => {
        const input = box.querySelector('input');
        const btn = box.querySelector('button');
        if (!input || !btn) return;
        btn.addEventListener('click', e => { e.preventDefault(); performSearch(input.value); });
        input.addEventListener('keypress', e => {
            if (e.key === 'Enter') { e.preventDefault(); performSearch(input.value); }
        });
    });
}

function initCartSidebar() {
    const cartSidebar = document.getElementById('cartSidebar');
    const cartOverlay = document.getElementById('cartOverlay');
    const cartBtn = document.getElementById('cartBtn');
    const closeCart = document.getElementById('closeCart');

    if (cartBtn && cartSidebar) cartBtn.addEventListener('click', () => {
        cartSidebar.classList.add('active');
        cartOverlay.classList.add('active');
    });
    if (closeCart && cartSidebar) closeCart.addEventListener('click', () => {
        cartSidebar.classList.remove('active');
        cartOverlay.classList.remove('active');
    });
    if (cartOverlay) cartOverlay.addEventListener('click', () => {
        cartSidebar.classList.remove('active');
        cartOverlay.classList.remove('active');
    });
}

function initMobileMenu() {
    const toggle = document.getElementById('menuToggle');
    const nav = document.getElementById('navList');
    if (toggle && nav) toggle.addEventListener('click', () => nav.classList.toggle('active'));
}

function initSlider() {
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.dot');
    if (!slides.length) return;
    let current = 0;
    function goTo(i) {
        slides.forEach(s => s.classList.remove('active'));
        dots.forEach(d => d.classList.remove('active'));
        slides[i].classList.add('active');
        dots[i].classList.add('active');
        current = i;
    }
    dots.forEach((d, i) => d.addEventListener('click', () => goTo(i)));
    setInterval(() => goTo((current + 1) % slides.length), 5000);
}

document.addEventListener('DOMContentLoaded', () => {
    initSearch();
    initCartSidebar();
    initMobileMenu();
    initSlider();
    renderCart();
    updateCartCount();
    updateWishlistCount();
});