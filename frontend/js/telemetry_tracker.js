/**
 * Myntra Sense — Client Telemetry Tracker & 60 FPS Monitor
 * Instruments Search, PDP View, Wishlist Ops, and Micro-interactions.
 */

class SenseTelemetryTracker {
  constructor() {
    this.userId = "USR_10001";
    this.sessionId = "sess_" + Math.random().toString(36).substring(2, 11);
    this.deviceId = "dev_" + Math.random().toString(36).substring(2, 8);
    this.platform = "DESKTOP_WEB";
    this.recentEvents = [];
    
    // FPS Monitor
    this.fps = 60;
    this.frameCount = 0;
    this.lastFpsUpdate = performance.now();
    this._startFpsMeter();
  }

  setUserId(userId) {
    this.userId = userId;
  }

  _emit(eventType, topic, payload) {
    const startT = performance.now();
    const event = {
      eventId: "evt_" + Math.random().toString(36).substring(2, 10),
      eventType: eventType,
      topic: topic,
      userId: this.userId,
      sessionId: this.sessionId,
      timestampMs: Date.now(),
      payload: payload,
      clientLatencyMs: +(performance.now() - startT).toFixed(3)
    };

    this.recentEvents.unshift(event);
    if (this.recentEvents.length > 50) this.recentEvents.pop();

    this._renderDrawerEvent(event);
    return event;
  }

  trackSearch(queryText, categoryId = null, brands = []) {
    return this._emit("SEARCH", "myntra.sense.search_events.v1", {
      queryText: queryText,
      inferredCategoryId: categoryId,
      inferredBrands: brands
    });
  }

  trackPDPView(productId, brandId, categoryId, confidenceScore = 88, viewedDashboard = true) {
    return this._emit("PDP_VIEW", "myntra.sense.pdp_views.v1", {
      productId: productId,
      brandId: brandId,
      categoryId: categoryId,
      confidenceScoreDisplayed: confidenceScore,
      viewedSenseConfidenceDashboard: viewedDashboard
    });
  }

  trackWishlistOp(productId, actionType = "COMPARE_SELECTED", price = 1199) {
    return this._emit("WISHLIST_OP", "myntra.sense.wishlist_ops.v1", {
      productId: productId,
      actionType: actionType,
      priceAtAction: price
    });
  }

  trackClickstream(elementType, interactionType, metadata = {}) {
    return this._emit("CLICKSTREAM", "myntra.sense.clickstream_events.v1", {
      elementType: elementType,
      interactionType: interactionType,
      metadata: metadata
    });
  }

  _renderDrawerEvent(event) {
    const list = document.getElementById("telemetry-events-list");
    if (!list) return;

    const div = document.createElement("div");
    div.className = "telemetry-event-item";
    div.innerHTML = `
      <div>
        <span class="event-type-badge">${event.eventType}</span>
        <span class="event-topic">${event.topic.split('.').slice(-2).join('.')}</span>
      </div>
      <div style="color: #cbd5e1;">${JSON.stringify(event.payload).substring(0, 80)}...</div>
      <div style="color: #64748b; font-size: 0.65rem;">User: ${event.userId} | Latency: ${event.clientLatencyMs}ms</div>
    `;

    list.insertBefore(div, list.firstChild);
    if (list.children.length > 25) {
      list.removeChild(list.lastChild);
    }
  }

  _startFpsMeter() {
    const loop = () => {
      this.frameCount++;
      const now = performance.now();
      if (now - this.lastFpsUpdate >= 1000) {
        this.fps = Math.round((this.frameCount * 1000) / (now - this.lastFpsUpdate));
        this.frameCount = 0;
        this.lastFpsUpdate = now;
        
        const fpsDisplay = document.getElementById("live-fps-val");
        if (fpsDisplay) {
          fpsDisplay.textContent = `${this.fps} FPS`;
          fpsDisplay.style.color = this.fps >= 55 ? "var(--confidence-high)" : "var(--confidence-mid)";
        }
      }
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }
}

window.senseTelemetry = new SenseTelemetryTracker();
