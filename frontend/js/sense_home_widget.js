/**
 * Myntra Sense — Home Screen Component (Screen 1)
 */

class SenseHomeWidget {
  constructor() {
    this.showcaseContainer = document.getElementById("home-showcase-carousel-track");
    this.curatedContainer = document.getElementById("home-curated-carousel-track");
    this.trendingGrid = document.getElementById("home-trending-products-grid");
  }

  render(data) {
    this._renderShowcaseCarousel();
    this._renderCuratedPicks(data.products || []);
    this._renderTrendingFashionGrid();
  }

  _renderShowcaseCarousel() {
    if (!this.showcaseContainer) return;
    const showcases = [
      { img: "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=400&q=80", discount: "UP TO 60% OFF", sub: "Everyday Styles", brands: "H&M • ZARA" },
      { img: "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?auto=format&fit=crop&w=400&q=80", discount: "MIN. 50% OFF", sub: "Tailored Looks", brands: "MANGO • NAUTICA" },
      { img: "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=400&q=80", discount: "MIN. 55% OFF", sub: "Style On Point", brands: "LEVIS • PEPE" },
      { img: "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=400&q=80", discount: "MIN. 55% OFF", sub: "Classic Ethnic", brands: "TAAVI • ANOUK" },
      { img: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=400&q=80", discount: "STARTING ₹199", sub: "Performance Ready", brands: "DECATHLON • HRX" },
      { img: "https://images.unsplash.com/photo-1533867617858-e7b97e060509?auto=format&fit=crop&w=400&q=80", discount: "MIN. 50% OFF", sub: "Classic Collection", brands: "MOCHI • METRO" }
    ];

    this.showcaseContainer.innerHTML = showcases.map(s => `
      <div class="showcase-card">
        <img src="${s.img}" alt="${s.sub}" class="showcase-img" />
        <div class="showcase-overlay-bottom">
          <span class="showcase-discount">${s.discount}</span>
          <span class="showcase-subtitle">${s.sub}</span>
          <span class="showcase-brand-logos">${s.brands}</span>
        </div>
      </div>
    `).join('');
  }

  _renderCuratedPicks(products) {
    if (!this.curatedContainer) return;
    this.curatedContainer.innerHTML = "";

    products.forEach(p => {
      const card = document.createElement("div");
      card.className = "ecom-product-card";
      card.onclick = () => window.appRouter.navigateToPDP(p.productId);

      const isWishlist = p.source === "WISHLIST";

      card.innerHTML = `
        <div class="card-img-box">
          <img src="${p.image}" alt="${p.title}" class="card-img" loading="lazy" />
          <div class="card-source-tag ${isWishlist ? 'wishlist' : ''}">
            ${isWishlist ? `❤️ Saved ${p.wishlistSavedDays || 18}d ago` : '✨ AI Discovery'}
          </div>
          <div class="card-confidence-chip">
            <span>★</span> <span>${p.confidenceScore}/100</span>
          </div>
        </div>
        <div class="card-info-box">
          <div class="card-brand-name">${p.brand}</div>
          <div class="card-product-title">${p.title}</div>
          <div class="card-price-container">
            <span class="card-price-current">₹${p.price}</span>
            <span class="card-price-original">₹${p.originalPrice || p.price * 2}</span>
            <span class="card-discount-tag">(${p.discount || '50% OFF'})</span>
          </div>
          <div class="card-fit-note">
            ✓ ${p.fitConfidence || '96% Fit Match'}
          </div>
        </div>
      `;

      this.curatedContainer.appendChild(card);
    });
  }

  _renderTrendingFashionGrid() {
    if (!this.trendingGrid) return;
    const trending = window.senseAPI.getTrendingProducts();

    this.trendingGrid.innerHTML = trending.map(p => `
      <div class="ecom-product-card" onclick="window.appRouter.navigateToPDP('${p.productId}')">
        <div class="card-img-box">
          <img src="${p.image}" alt="${p.title}" class="card-img" loading="lazy" />
          <div class="card-confidence-chip">
            <span>★</span> <span>${p.confidenceScore}/100</span>
          </div>
        </div>
        <div class="card-info-box">
          <div class="card-brand-name">${p.brand}</div>
          <div class="card-product-title">${p.title}</div>
          <div class="card-price-container">
            <span class="card-price-current">₹${p.price}</span>
            <span class="card-price-original">₹${p.originalPrice}</span>
            <span class="card-discount-tag">(${p.discount})</span>
          </div>
          <div class="card-fit-note">
            ✓ ${p.fitConfidence}
          </div>
        </div>
      </div>
    `).join('');
  }
}

window.senseHome = new SenseHomeWidget();
