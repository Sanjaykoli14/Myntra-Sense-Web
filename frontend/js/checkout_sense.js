/**
 * Myntra Sense — Checkout / Shopping Bag Component (Screen 3)
 * Manages cart state and renders the dedicated Myntra Sense Wishlist Add-ons segment.
 */

class CheckoutSenseController {
  constructor() {
    this.cartItems = [
      {
        productId: "SKU-982341",
        brand: "Roadster",
        title: "Men Pure Cotton Casual Shirt",
        price: 1199,
        originalPrice: 2499,
        discount: "52% OFF",
        size: "M",
        qty: 1,
        image: "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=600&q=80"
      }
    ];
    this.container = document.getElementById("checkout-dynamic-content-root");
  }

  addToCart(item) {
    const existing = this.cartItems.find(c => c.productId === item.productId && c.size === item.size);
    if (existing) {
      existing.qty += 1;
    } else {
      this.cartItems.push({
        productId: item.productId,
        brand: item.brand,
        title: item.title,
        price: item.price,
        originalPrice: item.originalPrice || item.price * 2,
        discount: item.discount || "50% OFF",
        size: item.size || "M",
        qty: 1,
        image: item.image
      });
    }
    this._updateBadge();
    this.render();
  }

  removeFromCart(index) {
    this.cartItems.splice(index, 1);
    this._updateBadge();
    this.render();
  }

  _updateBadge() {
    const totalCount = this.cartItems.reduce((acc, curr) => acc + curr.qty, 0);
    const badges = document.querySelectorAll("#nav-bag-count-badge");
    badges.forEach(b => b.textContent = totalCount);
  }

  async render() {
    if (!this.container) return;

    const totalMrp = this.cartItems.reduce((acc, c) => acc + (c.originalPrice * c.qty), 0);
    const totalCurrent = this.cartItems.reduce((acc, c) => acc + (c.price * c.qty), 0);
    const totalDiscount = totalMrp - totalCurrent;

    // Fetch wishlist items that pair with current cart items
    const cartSkus = this.cartItems.map(c => c.productId);
    const addOnPicks = await window.senseAPI.getCheckoutPicks(cartSkus);

    this.container.innerHTML = `
      <div class="checkout-steps-header">
        <span class="checkout-step active">1. BAG (${this.cartItems.length})</span>
        <span>-----------</span>
        <span class="checkout-step">2. ADDRESS</span>
        <span>-----------</span>
        <span class="checkout-step">3. PAYMENT</span>
      </div>

      <div class="checkout-layout-grid">
        
        <!-- Left Column -->
        <div class="checkout-left-col">
          
          <!-- Delivery Address Banner -->
          <div class="delivery-address-card">
            <div class="delivery-details">
              <strong>Deliver to: Rahul Sharma, 560103</strong>
              <p>Green Glen Layout, Bellandur, Bangalore • Express Delivery by Tomorrow</p>
            </div>
            <button class="btn-change-address">CHANGE ADDRESS</button>
          </div>

          <!-- Active Cart Items -->
          <div class="cart-items-section">
            <div class="cart-section-title">Items in Shopping Bag (${this.cartItems.length})</div>

            ${this.cartItems.length === 0 ? `
              <div style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
                Your shopping bag is empty. Explore items from your Wishlist below!
              </div>
            ` : this.cartItems.map((item, idx) => `
              <div class="cart-item-card">
                <img src="${item.image}" alt="${item.title}" class="cart-item-img" />
                <div class="cart-item-details">
                  <span class="cart-item-brand">${item.brand}</span>
                  <span class="cart-item-title">${item.title}</span>
                  <div class="cart-item-size-qty-row">
                    <span>Size: ${item.size}</span>
                    <span>Qty: ${item.qty}</span>
                  </div>
                  <div class="cart-item-price-row">
                    <span class="card-price-current">₹${item.price}</span>
                    <span class="card-price-original">₹${item.originalPrice}</span>
                    <span class="card-discount-tag">${item.discount}</span>
                  </div>
                  <div class="cart-item-actions">
                    <button class="cart-action-link" onclick="window.checkoutSense.removeFromCart(${idx})">Remove</button>
                    <span style="color: var(--border-subtle);">|</span>
                    <button class="cart-action-link" onclick="window.checkoutSense.removeFromCart(${idx}); alert('Moved item back to Wishlist!');">Move to Wishlist</button>
                  </div>
                </div>
              </div>
            `).join('')}
          </div>

          <!-- ==========================================================
               MYNTRA SENSE WISHLIST ADD-ONS SEGMENT (BELOW CART ITEMS)
               ========================================================== -->
          <div class="checkout-sense-segment">
            <div class="checkout-sense-header">
              <div>
                <div class="checkout-sense-title">
                  <img src="assets/myntra_sense_logo.png" alt="Myntra Sense" style="height: 22px;" />
                  <span>High-Confidence Wishlist Add-ons</span>
                </div>
                <div class="checkout-sense-sub">
                  Saved favorites from your 38 wishlist items that pair with items in your cart.
                </div>
              </div>
              <span class="badge-ai-pill">AI Curated</span>
            </div>

            <div class="checkout-sense-products-grid">
              ${addOnPicks.map(p => `
                <div class="checkout-sense-card" onclick="window.appRouter.navigateToPDP('${p.productId}')">
                  <div class="checkout-sense-img-box">
                    <img src="${p.image}" alt="${p.title}" class="checkout-sense-img" />
                    <div class="card-confidence-chip">
                      <span>★</span> <span>${p.confidenceScore}/100</span>
                    </div>
                  </div>
                  <div class="checkout-sense-info">
                    <span class="checkout-sense-brand">${p.brand}</span>
                    <span class="checkout-sense-pname">${p.title}</span>
                    <span class="checkout-sense-price">₹${p.price}</span>
                    <button class="btn-checkout-add-to-cart" onclick="event.stopPropagation(); window.checkoutSense.addToCart({ productId: '${p.productId}', brand: '${p.brand}', title: '${p.title}', price: ${p.price}, originalPrice: ${p.originalPrice || p.price * 2}, discount: '${p.discount || '50% OFF'}', size: '${p.recommendedSize || 'M'}', image: '${p.image}' });">
                      + Add to Bag
                    </button>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>

        </div>

        <!-- Right Column: Price Details -->
        <div class="checkout-right-col">
          <div class="price-details-card">
            <span class="price-details-heading">PRICE DETAILS (${this.cartItems.length} Items)</span>
            
            <div class="price-row">
              <span>Total MRP</span>
              <span>₹${totalMrp}</span>
            </div>

            <div class="price-row">
              <span>Discount on MRP</span>
              <span style="color: var(--confidence-high);">- ₹${totalDiscount}</span>
            </div>

            <div class="price-row">
              <span>Convenience Fee</span>
              <span style="color: var(--confidence-high);">FREE</span>
            </div>

            <div class="price-total-row">
              <span>Total Amount</span>
              <span>₹${totalCurrent}</span>
            </div>

            <button class="btn-place-order" onclick="alert('🎉 Order Placed Successfully with Myntra Sense Guaranteed Fit & Quality!')">
              PLACE ORDER
            </button>
          </div>
        </div>

      </div>
    `;
  }
}

window.checkoutSense = new CheckoutSenseController();
