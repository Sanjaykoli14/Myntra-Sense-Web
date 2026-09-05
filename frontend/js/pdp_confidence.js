/**
 * Myntra Sense — Product Detail Page Component (Screen 2)
 */

class PDPConfidenceDashboard {
  constructor() {
    this.container = document.getElementById("pdp-dynamic-content-root");
    this.selectedSize = "M";
    this.currentProduct = null;
  }

  async renderProduct(productId) {
    if (!this.container) return;
    this.container.innerHTML = `
      <div style="text-align: center; padding: 5rem; color: var(--text-secondary);">
        <div style="font-size: 1.25rem; font-weight: 700;">Loading Product & AI Confidence Signals...</div>
      </div>
    `;

    const data = await window.senseAPI.getProductConfidence(productId);
    this.currentProduct = data;
    this.selectedSize = data.signals?.fitAndSizing?.recommendedSize || "M";

    const score = data.overallConfidenceScore || 89;
    const strokeOffset = Math.max(0, 283 - (283 * (score / 100)));

    const auth = data.signals?.authenticity || { score: 98, badge: "100% Genuine Brand Assurance" };
    const qual = data.signals?.quality || { score: 91, fabricRating: 4.7, sentimentSummary: "89% praise fabric quality." };
    const fit = data.signals?.fitAndSizing || { fitMatchPercentage: 96, recommendedSize: "M", sizeFeedback: "True to Size" };
    const ret = data.signals?.returnConfidence || { returnEaseScore: 95, badge: "14-Day Doorstep Pickup" };

    this.container.innerHTML = `
      <div class="pdp-breadcrumbs">
        <a href="#" onclick="window.appRouter.navigateTo('HOME')">Home</a> / 
        <a href="#" onclick="window.appRouter.navigateTo('HOME')">Fashion</a> / 
        <span>${data.brand}</span> / 
        <span style="color: var(--text-primary); font-weight: 600;">${data.title}</span>
      </div>

      <div class="pdp-layout-grid">
        
        <!-- Left: Image Gallery -->
        <div class="pdp-gallery-column">
          <div class="pdp-main-image-box">
            <div class="pdp-wishlist-age-photo-badge">
              <span>❤️</span> <span>Wishlist • Saved ${data.wishlistSavedDays || 18}d ago</span>
            </div>
            <img src="${data.image}" alt="${data.title}" class="pdp-main-img" id="pdp-main-gallery-img" />
          </div>
          <div class="pdp-thumbnails-row">
            <img src="${data.image}" class="pdp-thumb active" onclick="document.getElementById('pdp-main-gallery-img').src='${data.image}'" />
            <img src="${data.customerPhotos?.[0]?.url || data.image}" class="pdp-thumb" onclick="document.getElementById('pdp-main-gallery-img').src='${data.customerPhotos?.[0]?.url || data.image}'" />
            <img src="${data.customerPhotos?.[1]?.url || data.image}" class="pdp-thumb" onclick="document.getElementById('pdp-main-gallery-img').src='${data.customerPhotos?.[1]?.url || data.image}'" />
          </div>
        </div>

        <!-- Right: Details & Confidence Dashboard -->
        <div class="pdp-info-column">
          
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.65rem;">
            <span class="wishlist-saved-duration-chip">
              <span>❤️</span> <span>Wishlist • Saved ${data.wishlistSavedDays || 18}d ago</span>
            </span>
            <span style="font-size: 0.78rem; color: var(--confidence-high); font-weight: 700;">✓ In Stock in Size ${fit.recommendedSize || 'M'}</span>
          </div>

          <div class="pdp-header-block">
            <h1 class="pdp-brand-title">${data.brand}</h1>
            <p class="pdp-product-name">${data.title}</p>
            <div class="pdp-rating-badge">
              <span>★ ${data.rating}</span> <span style="color: var(--text-muted);">| ${data.ratingCount} Ratings</span>
            </div>
          </div>

          <div class="pdp-pricing-block">
            <span class="pdp-current-price">₹${data.price}</span>
            <span class="pdp-original-mrp">MRP ₹${data.originalPrice}</span>
            <span class="pdp-discount-highlight">(${data.discount})</span>
          </div>
          <div class="pdp-tax-note">inclusive of all taxes</div>

          <!-- Size Selector -->
          <div class="pdp-size-section">
            <div class="pdp-size-header">
              <span class="size-header-title">Select Size</span>
              <span class="size-chart-link">Size Chart ></span>
            </div>

            <div class="size-buttons-row">
              ${['S', 'M', 'L', 'XL', 'XXL'].map(sz => `
                <button class="size-btn ${sz === this.selectedSize ? 'selected' : ''}" onclick="window.sensePDP.selectSize('${sz}')">
                  ${sz}
                  ${sz === fit.recommendedSize ? '<span class="size-recommended-badge">Best Fit</span>' : ''}
                </button>
              `).join('')}
            </div>
            <div style="font-size: 0.8rem; color: var(--confidence-high); font-weight: 600;">
              ✓ Recommended Size <strong>${fit.recommendedSize}</strong> (${fit.fitMatchPercentage}% Match for your profile)
            </div>
          </div>

          <!-- Action CTAs -->
          <div class="pdp-action-buttons-row">
            <button class="btn-pdp-add-to-bag" onclick="window.sensePDP.addToBagAndStay()">
              <span>🛍️</span> <span>ADD TO BAG</span>
            </button>
            <button class="btn-pdp-add-to-bag" style="background: var(--text-primary);" onclick="window.sensePDP.buyNow()">
              <span>⚡</span> <span>BUY NOW</span>
            </button>
          </div>

          <!-- ==========================================================
               MYNTRA SENSE CONFIDENCE DASHBOARD EMBEDDED ON PDP
               ========================================================== -->
          <div class="pdp-sense-confidence-dashboard">
            <div class="sense-dash-header">
              <div class="sense-dash-title">
                <img src="assets/myntra_sense_logo.png" alt="Myntra Sense" style="height: 24px;" />
                <span>Confidence Dashboard</span>
              </div>
              <span class="badge-ai-pill">Verified AI Analysis</span>
            </div>

            <!-- Score Hero Card -->
            <div class="sense-pdp-hero">
              <div class="pdp-gauge-box">
                <svg class="pdp-gauge-svg" viewBox="0 0 100 100">
                  <circle class="pdp-gauge-bg" cx="50" cy="50" r="45"></circle>
                  <circle class="pdp-gauge-fill" cx="50" cy="50" r="45" style="stroke-dashoffset: ${strokeOffset};"></circle>
                </svg>
                <div class="pdp-gauge-text">
                  <span class="pdp-gauge-num">${score}</span>
                  <span class="pdp-gauge-lbl">Score / 100</span>
                </div>
              </div>

              <div class="sense-pdp-xai-text">
                <strong>Why this is recommended for you:</strong><br />
                "${data.xaiExplanation}"
              </div>
            </div>

            <!-- 4 Signal Pillars -->
            <div class="pdp-pillars-grid">
              
              <!-- Pillar 1: Authenticity -->
              <div class="pdp-pillar-box">
                <div class="pdp-pillar-title-row">
                  <span>🛡️ Authenticity</span>
                  <span style="color: var(--confidence-high);">${auth.score}/100</span>
                </div>
                <p class="pdp-pillar-desc">${auth.badge}</p>
              </div>

              <!-- Pillar 2: Quality & Fabric -->
              <div class="pdp-pillar-box">
                <div class="pdp-pillar-title-row">
                  <span>⭐ Quality & Fabric</span>
                  <span style="color: var(--confidence-purple);">${qual.fabricRating} ★</span>
                </div>
                <p class="pdp-pillar-desc">${qual.sentimentSummary}</p>
              </div>

              <!-- Pillar 3: Fit & Sizing -->
              <div class="pdp-pillar-box">
                <div class="pdp-pillar-title-row">
                  <span>📏 Fit & Sizing</span>
                  <span style="color: var(--confidence-cyan);">${fit.fitMatchPercentage}% Match</span>
                </div>
                <p class="pdp-pillar-desc">${fit.userSpecificNote}</p>
              </div>

              <!-- Pillar 4: Return Confidence -->
              <div class="pdp-pillar-box">
                <div class="pdp-pillar-title-row">
                  <span>🔄 Return Friction</span>
                  <span style="color: var(--confidence-high);">${ret.returnEaseScore}/100</span>
                </div>
                <p class="pdp-pillar-desc">${ret.badge} (${ret.categoryReturnRate} returns)</p>
              </div>

            </div>

            <!-- Real Customer Review Photos -->
            <div class="pdp-real-photos-box">
              <div class="pdp-real-photos-heading">
                <span>📸</span> <span>Real Photos from Verified Size M Buyers</span>
              </div>
              <div class="pdp-real-photos-row">
                ${(data.customerPhotos || []).map(cp => `
                  <div class="pdp-real-photo-card">
                    <img src="${cp.url}" alt="Verified Customer Photo" />
                    <span class="pdp-real-photo-tag">${cp.wearerSize} • ${cp.clarity}</span>
                  </div>
                `).join('')}
              </div>
            </div>

          </div>

        </div>

      </div>

      <!-- ==========================================================
           CUSTOMER PHOTOS & FIT PROOF + TOP REVIEW INSIGHTS TELEMETRY
           ========================================================== -->
      <div class="pdp-review-telemetry-container">
        
        <!-- Left: Customer Photos & Fit Proof -->
        <div class="review-telemetry-card">
          <div class="telemetry-card-header">
            <h3 class="telemetry-card-title">CUSTOMER PHOTOS & FIT PROOF</h3>
            <span class="telemetry-verified-badge-label">VERIFIED BUYERS</span>
          </div>

          <div class="verified-buyers-list">
            ${(data.reviewTelemetry?.buyers || []).map(b => `
              <div class="verified-buyer-card-row">
                <img src="${b.avatar}" alt="${b.name}" class="verified-buyer-avatar-img" />
                <div class="verified-buyer-info">
                  <div class="verified-buyer-name-row">
                    <span class="buyer-name">${b.name}</span>
                    <span class="buyer-verified-tag">VERIFIED BUYER</span>
                  </div>
                  <div class="buyer-stats-row">
                    ${b.stats}
                  </div>
                  <p class="buyer-quote-text">
                    ${b.quote}
                  </p>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Right: Top Review Insights Telemetry -->
        <div class="review-telemetry-card">
          <div class="telemetry-card-header">
            <h3 class="telemetry-card-title">TOP REVIEW INSIGHTS TELEMETRY</h3>
          </div>

          <!-- Top Metric Tiles -->
          <div class="telemetry-metrics-grid">
            ${(data.reviewTelemetry?.metrics || []).map(m => `
              <div class="telemetry-metric-tile">
                <div class="metric-tile-title-row">
                  <span>${m.title}</span>
                  <span class="metric-tile-pct">${m.pct}</span>
                </div>
                <span class="metric-tile-subtext">${m.sub}</span>
              </div>
            `).join('')}
          </div>

          <!-- Bottom Strengths & Care Breakdown -->
          <div class="telemetry-breakdown-row">
            <div class="breakdown-column">
              <div class="breakdown-col-heading strengths">
                <span>✓</span> <span>KEY STRENGTHS</span>
              </div>
              <ul class="breakdown-list">
                ${(data.reviewTelemetry?.strengths || []).map(s => `
                  <li class="breakdown-list-item">${s}</li>
                `).join('')}
              </ul>
            </div>

            <div class="breakdown-column">
              <div class="breakdown-col-heading care">
                <span>!</span> <span>THINGS TO NOTE (CARE / FIT)</span>
              </div>
              <ul class="breakdown-list">
                ${(data.reviewTelemetry?.care || []).map(c => `
                  <li class="breakdown-list-item">${c}</li>
                `).join('')}
              </ul>
            </div>
          </div>

        </div>

      </div>
    `;
  }

  selectSize(size) {
    this.selectedSize = size;
    const btns = document.querySelectorAll(".size-btn");
    btns.forEach(b => {
      if (b.textContent.trim().startsWith(size)) {
        b.classList.add("selected");
      } else {
        b.classList.remove("selected");
      }
    });
  }

  addToBagAndStay() {
    if (!this.currentProduct) return;
    window.checkoutSense.addToCart({
      productId: this.currentProduct.productId,
      brand: this.currentProduct.brand,
      title: this.currentProduct.title,
      price: this.currentProduct.price,
      originalPrice: this.currentProduct.originalPrice,
      discount: this.currentProduct.discount,
      size: this.selectedSize,
      image: this.currentProduct.image
    });
    alert(`🎉 Added "${this.currentProduct.title}" (Size ${this.selectedSize}) to your Bag!`);
  }

  buyNow() {
    this.addToBagAndStay();
    window.appRouter.navigateTo("CHECKOUT");
  }
}

window.sensePDP = new PDPConfidenceDashboard();
