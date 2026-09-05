# 🏗️ Myntra Sense — System Architecture Document

---

## 1. Executive Architecture Summary

**Myntra Sense** is an AI-powered personalized confidence and intent-scoring engine designed to solve the wishlist-to-purchase conversion drop-off. It operates across **4 core user touchpoints**:
1. **Home Page Screen:** Showcases curated wishlist picks and trending products.
2. **Product Detail Page (PDP):** Delivers multi-dimensional confidence signals (Authenticity, Quality, Fit, Returns) and real customer photos.
3. **Checkout / Shopping Bag Screen:** Re-engages purchase intent by curating complementary high-confidence wishlist add-ons directly below cart items.
4. **Wishlist & Comparison Screen:** Provides side-by-side trade-off matrices to eliminate choice paralysis.

---

## 2. End-to-End Multi-Screen System Architecture

```mermaid
flowchart TD
    subgraph ClientLayer["1. Client Layer (4 Core Screens)"]
        S1["Screen 1: Home Page\n(Brand Showcase + Sense Banner + Wishlist Picks + Clickable Fashion Grid)"]
        S2["Screen 2: Product Detail Page (PDP)\n(Gallery + Gauge /100 + 4 Pillars + Real Photos + XAI)"]
        S3["Screen 3: Checkout / Bag Page\n(Cart Items + Order Summary + Sense Wishlist Add-ons)"]
        S4["Screen 4: Wishlist & Compare Screen\n(38 Saved Grid + Side-by-Side Trade-off Matrix)"]
    end

    subgraph EdgeLayer["2. API Gateway & Edge Routing"]
        AG["Kong / Envoy API Gateway\n(Auth, Rate Limiting, Route Dispatcher)"]
    end

    subgraph OrchestrationLayer["3. Serving & Orchestration Microservices"]
        SO["Sense Orchestrator Service (Golang / gRPC)\n- Candidate Aggregation\n- Multi-Tier Caching (L1/L2)"]
        CO["Confidence Score Synthesizer (0-100)\n- 4 Pillar Signal Formulator"]
        CO_COMP["Shortlist Comparison Service\n- Differential Trade-off Matrix"]
        CO_CART["Cart Contextual Recommender\n- Wishlist-to-Cart Pairing Engine"]
    end

    subgraph AIEngineLayer["4. AI / ML Intelligence Core (Triton Serving)"]
        IPS["Two-Tower Transformer & GBDT Intent Ranker"]
        FPS["Bayesian Collaborative Sizing Matcher"]
        NLP["RoBERTa Aspect-Based Sentiment Extractor"]
        CVM["CLIP Visual Customer Photo Verifier"]
        XAI["Template-Constrained XAI Explainer"]
    end

    subgraph StorageLayer["5. Data & Storage Tier"]
        RD["Redis Cluster (Feature Store Online & Score Cache)"]
        FS["Feast Feature Store (User Profiles & Realtime Intent)"]
        CDB["Primary Catalog & User Wishlist Store (Cassandra)"]
    end

    %% Client to Edge
    S1 & S2 & S3 & S4 --> AG
    AG --> SO
    SO --> CO
    SO --> CO_COMP
    SO --> CO_CART
    
    %% Microservices to AI & Storage
    SO <--> FS
    SO <--> IPS
    CO <--> FPS
    CO <--> NLP
    CO <--> CVM
    CO <--> XAI
    SO <--> RD
    CO_CART <--> CDB
```

---

## 3. Screen Lifecycle & User Navigation Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Home as Screen 1: Home Page
    participant PDP as Screen 2: Product Detail Page
    participant Bag as Screen 3: Checkout / Bag Page
    participant Gateway as API Gateway / Orchestrator
    participant ML as Triton ML Engine

    User->>Home: Opens App & views "Myntra Sense" Banner
    Home->>Gateway: GET /api/v1/sense/home-picks
    Gateway->>ML: Rank 38 Wishlist items -> Top 10 Wishlist Picks + 10 Discovery
    ML-->>Home: Return 20 Curated Products (50% Wishlist) with Confidence Badges
    
    User->>Home: Clicks Roadster Pure Cotton Shirt
    Home->>PDP: Navigate to Screen 2 (PDP)
    PDP->>Gateway: GET /api/v1/sense/confidence/SKU-982341
    Gateway->>ML: Compute 4 Pillars, Circular Gauge (89/100), Photos & XAI
    ML-->>PDP: Render Confidence Dashboard
    
    User->>PDP: Taps "Add to Bag" & opens Cart
    PDP->>Bag: Navigate to Screen 3 (Checkout / Bag)
    Bag->>Gateway: GET /api/v1/sense/checkout-picks?cart_skus=SKU-982341
    Gateway->>ML: Fetch Wishlist items pairing with Cotton Shirt (e.g. Chinos)
    ML-->>Bag: Render "Myntra Sense Wishlist Add-ons" Below Cart
    
    User->>Bag: Clicks on Wishlisted Chinos card
    Bag->>PDP: Opens PDP for Chinos with Verified Fit Match
```

---

## 4. API Endpoints & Contracts

### 4.1. Get Curated Home Picks
* **Endpoint:** `GET /api/v1/sense/home-picks?user_id={userId}`
* **Response (JSON):**
```json
{
  "status": "success",
  "data": {
    "sectionTitle": "Myntra Sense — Your Wishlist Picks",
    "rationale": "Curated from your 38 saved items based on your recent searches for summer casuals.",
    "totalWishlistCount": 38,
    "products": [
      {
        "productId": "SKU-982341",
        "title": "Roadster Men Pure Cotton Casual Shirt",
        "brand": "Roadster",
        "source": "WISHLIST",
        "confidenceScore": 89,
        "recommendedSize": "M",
        "fitConfidence": "96% Fit Match",
        "price": 1199,
        "highlights": ["100% Breathable Cotton", "Low Returns (< 4%)"]
      }
    ]
  }
}
```

---

### 4.2. Get Product Confidence Dashboard
* **Endpoint:** `GET /api/v1/sense/confidence/{productId}?user_id={userId}&size={size}`
* **Response (JSON):**
```json
{
  "status": "success",
  "data": {
    "productId": "SKU-982341",
    "overallConfidenceScore": 89,
    "confidenceTier": "HIGH_CONFIDENCE",
    "xaiExplanation": "Recommended for you because you recently searched for casual shirts, and this saved item has a 96% fit confidence with top-rated pure cotton fabric.",
    "signals": {
      "authenticity": { "score": 98, "badge": "100% Genuine Brand Assurance" },
      "quality": { "score": 91, "fabricRating": 4.7, "sentimentSummary": "89% praise fabric hand-feel." },
      "fitAndSizing": { "recommendedSize": "M", "fitMatchPercentage": 96, "sizeFeedback": "True to Size" },
      "returnConfidence": { "returnEaseScore": 95, "badge": "Hassle-Free 14-Day Doorstep Pickup" }
    },
    "customerPhotos": [
      { "url": "https://assets.myntassets.com/reviews/curated_pdp_1.jpg", "wearerSize": "Size M" }
    ]
  }
}
```

---

### 4.3. Get Checkout / Bag Wishlist Add-ons
* **Endpoint:** `GET /api/v1/sense/checkout-picks?user_id={userId}&cart_skus={skuList}`
* **Response (JSON):**
```json
{
  "status": "success",
  "data": {
    "sectionTitle": "Myntra Sense — Add from your Wishlist with High Confidence",
    "rationale": "High-confidence items from your 38 saved favorites that pair perfectly with items in your bag.",
    "products": [
      {
        "productId": "SKU-441092",
        "title": "Highlander Slim Fit Chinos",
        "brand": "Highlander",
        "confidenceScore": 86,
        "recommendedSize": "32",
        "fitConfidence": "Pairs with Cotton Shirt",
        "price": 999,
        "highlights": ["Stretch Comfort", "Verified Seller"]
      }
    ]
  }
}
```

---

### 4.4. Shortlist Comparison Service
* **Endpoint:** `POST /api/v1/sense/compare`
* **Response (JSON):** Side-by-side trade-off matrix with differential highlighting and winner badges.
