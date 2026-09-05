/**
 * Myntra Sense — Wishlist & Comparison Component (Screen 4)
 */

class WishlistComparisonController {
  constructor() {
    this.selectedForCompare = new Set();
    this.container = document.getElementById("wishlist-dynamic-content-root");
    this.modal = document.getElementById("comparison-modal-overlay");
  }

  async render() {
    if (!this.container) return;
    const picks = await window.senseAPI.getHomePicks();
    const products = picks.products || [];

    this.container.innerHTML = `
      <div class="wishlist-header-row">
        <div class="wishlist-title-group">
          <h2>My Wishlist <span style="font-weight: 400; color: var(--text-muted);">(${products.length} Items)</span></h2>
          <p>Select multiple items below to trigger AI side-by-side trade-off comparison.</p>
        </div>
        <button class="btn-myntra-primary" id="btn-trigger-compare" onclick="window.wishlistCompare.openComparisonModal()">
          <span>⚖️</span> <span>Compare Selected (${this.selectedForCompare.size})</span>
        </button>
      </div>

      <div class="wishlist-grid-4col">
        ${products.map(p => `
          <div class="wishlist-card">
            <div class="wishlist-card-img-box" onclick="window.appRouter.navigateToPDP('${p.productId}')">
              <img src="${p.image}" alt="${p.title}" class="wishlist-card-img" />
              <div class="card-confidence-chip">
                <span>★</span> <span>${p.confidenceScore}/100</span>
              </div>
              <label class="wishlist-compare-chk-box" onclick="event.stopPropagation()">
                <input type="checkbox" ${this.selectedForCompare.has(p.productId) ? 'checked' : ''} onchange="window.wishlistCompare.toggleCompare('${p.productId}', event)" />
                <span>Compare</span>
              </label>
            </div>
            <div class="card-info-box" onclick="window.appRouter.navigateToPDP('${p.productId}')" style="cursor: pointer;">
              <span class="card-brand-name">${p.brand}</span>
              <span class="card-product-title">${p.title}</span>
              <div class="card-price-container">
                <span class="card-price-current">₹${p.price}</span>
                <span class="card-price-original">₹${p.originalPrice || p.price * 2}</span>
                <span class="card-discount-tag">(${p.discount || '50% OFF'})</span>
              </div>
              <span class="card-fit-note">✓ ${p.fitConfidence || '96% Fit Match'}</span>
            </div>
            <button class="btn-move-to-bag-full" onclick="window.checkoutSense.addToCart({ productId: '${p.productId}', brand: '${p.brand}', title: '${p.title}', price: ${p.price}, originalPrice: ${p.originalPrice || p.price * 2}, discount: '${p.discount || '50% OFF'}', size: '${p.recommendedSize || 'M'}', image: '${p.image}' }); alert('Added to Bag!');">
              MOVE TO BAG
            </button>
          </div>
        `).join('')}
      </div>
    `;
  }

  toggleCompare(productId, event) {
    if (event.target.checked) {
      if (this.selectedForCompare.size >= 4) {
        alert("You can select up to 4 items to compare.");
        event.target.checked = false;
        return;
      }
      this.selectedForCompare.add(productId);
    } else {
      this.selectedForCompare.delete(productId);
    }
    const btn = document.getElementById("btn-trigger-compare");
    if (btn) btn.innerHTML = `<span>⚖️</span> <span>Compare Selected (${this.selectedForCompare.size})</span>`;
  }

  async openComparisonModal() {
    if (this.selectedForCompare.size < 2) {
      // Auto-select first 2 if none selected for instant demo delight
      const picks = await window.senseAPI.getHomePicks();
      this.selectedForCompare.add(picks.products[0].productId);
      this.selectedForCompare.add(picks.products[1].productId);
    }

    const picks = await window.senseAPI.getHomePicks();
    const selectedProds = picks.products.filter(p => this.selectedForCompare.has(p.productId));

    const matrix = await window.senseAPI.compareProducts(selectedProds);
    this._renderMatrixTable(matrix);

    if (this.modal) this.modal.classList.add("active");
  }

  closeModal() {
    if (this.modal) this.modal.classList.remove("active");
  }

  _renderMatrixTable(data) {
    const tableBody = document.getElementById("comparison-table-mount");
    if (!tableBody) return;

    const prods = data.products || [];
    const attrs = [
      { key: "overall_confidence", label: "Confidence Score" },
      { key: "price", label: "Price" },
      { key: "fit_match", label: "Fit Match for You" },
      { key: "fabric_quality", label: "Fabric Rating" },
      { key: "color_fastness", label: "Colorfastness" },
      { key: "authenticity", label: "Authenticity" },
      { key: "return_ease", label: "Return Ease" }
    ];

    tableBody.innerHTML = `
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Feature Matrix</th>
            ${prods.map(p => `
              <th class="compare-product-col-head">
                <img src="${p.image}" alt="${p.title}" />
                <div style="font-weight: 800;">${p.brand}</div>
                <div style="font-size: 0.8rem; color: var(--text-secondary);">${p.title}</div>
                <div>
                  ${(p.winnerBadges || []).map(b => {
                    const bClass = b.includes("Fit") ? "fit" : (b.includes("Quality") ? "quality" : "value");
                    return `<span class="winner-badge-pill ${bClass}">${b}</span>`;
                  }).join('')}
                </div>
                <button class="btn-myntra-primary" style="margin-top: 0.75rem; font-size: 0.75rem; padding: 0.4rem 0.8rem;" onclick="window.checkoutSense.addToCart({ productId: '${p.productId}', brand: '${p.brand}', title: '${p.title}', price: ${p.price}, originalPrice: ${p.price * 2}, discount: '50% OFF', size: 'M', image: '${p.image}' }); window.wishlistCompare.closeModal(); window.appRouter.navigateTo('CHECKOUT');">
                  Select & Buy
                </button>
              </th>
            `).join('')}
          </tr>
        </thead>
        <tbody>
          ${attrs.map(attr => `
            <tr>
              <td>${attr.label}</td>
              ${prods.map(p => `
                <td class="${attr.key === 'overall_confidence' || attr.key === 'fit_match' ? 'highlight-cell' : ''}">
                  ${p.values[attr.key] || '-'}
                </td>
              `).join('')}
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  }
}

window.wishlistCompare = new WishlistComparisonController();
