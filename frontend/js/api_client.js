/**
 * Myntra Sense — Client API Service
 * Handles API calls to backend endpoints with client-side mock fallback.
 * Curates 20 Smart Picks (50% Wishlist = 10 items + 50% Complementary Discovery = 10 items).
 * Each product features realistic varied wishlist saved durations (e.g., 8d, 12d, 15d, 18d, 21d, 27d, 34d).
 */

const MOCK_HOME_PICKS = {
  sectionTitle: "Myntra Sense — Your Wishlist Picks",
  rationale: "Curated 20 smart picks (10 from your 38 saved wishlist items + 10 complementary pairs) based on your recent searches for summer casuals & cotton shirts.",
  totalWishlistCount: 38,
  products: [
    // 10 Wishlist Items (50%)
    {
      productId: "SKU-982341",
      title: "Roadster Men Pure Cotton Casual Shirt",
      brand: "Roadster",
      source: "WISHLIST",
      wishlistSavedDays: 18,
      confidenceScore: 89,
      recommendedSize: "M",
      fitConfidence: "96% Fit Match",
      price: 1199,
      originalPrice: 2499,
      discount: "52% OFF",
      rating: 4.5,
      ratingCount: "14.2k",
      image: "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=600&q=80",
      highlights: ["100% Breathable Cotton", "Low Returns (< 4%)"],
      fabricRating: 4.7,
      authenticityScore: 98
    },
    {
      productId: "SKU-772183",
      title: "Anouk Women Printed Pure Cotton Kurta",
      brand: "Anouk",
      source: "WISHLIST",
      wishlistSavedDays: 12,
      confidenceScore: 92,
      recommendedSize: "M",
      fitConfidence: "95% Fit Match",
      price: 1499,
      originalPrice: 2999,
      discount: "50% OFF",
      rating: 4.6,
      ratingCount: "21.4k",
      image: "https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=600&q=80",
      highlights: ["Colorfast Dye", "True to Size"],
      fabricRating: 4.8,
      authenticityScore: 99
    },
    {
      productId: "SKU-109284",
      title: "Puma Unisex Softride Running Shoes",
      brand: "Puma",
      source: "WISHLIST",
      wishlistSavedDays: 24,
      confidenceScore: 91,
      recommendedSize: "UK 8",
      fitConfidence: "94% Fit Match",
      price: 2899,
      originalPrice: 4999,
      discount: "42% OFF",
      rating: 4.7,
      ratingCount: "6.1k",
      image: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80",
      highlights: ["Official Puma Store", "Doorstep Return"],
      fabricRating: 4.6,
      authenticityScore: 99
    },
    {
      productId: "SKU-552910",
      title: "WROGN Men Slim Fit Checked Casual Shirt",
      brand: "WROGN",
      source: "WISHLIST",
      wishlistSavedDays: 15,
      confidenceScore: 88,
      recommendedSize: "M",
      fitConfidence: "93% Fit Match",
      price: 1699,
      originalPrice: 3299,
      discount: "48% OFF",
      rating: 4.4,
      ratingCount: "11.2k",
      image: "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=600&q=80",
      highlights: ["Pre-shrunk Fabric", "Verified Fit"],
      fabricRating: 4.6,
      authenticityScore: 97
    },
    {
      productId: "SKU-882910",
      title: "Mast & Harbour Casual Linen Trousers",
      brand: "Mast & Harbour",
      source: "WISHLIST",
      wishlistSavedDays: 8,
      confidenceScore: 85,
      recommendedSize: "32",
      fitConfidence: "91% Fit Match",
      price: 1299,
      originalPrice: 2599,
      discount: "50% OFF",
      rating: 4.2,
      ratingCount: "5.4k",
      image: "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=600&q=80",
      highlights: ["Breathable Linen", "14-Day Pickup"],
      fabricRating: 4.4,
      authenticityScore: 95
    },
    {
      productId: "SKU-661902",
      title: "Kook N Keech Men Graphic Tee",
      brand: "Kook N Keech",
      source: "WISHLIST",
      wishlistSavedDays: 21,
      confidenceScore: 84,
      recommendedSize: "L",
      fitConfidence: "Relaxed Fit",
      price: 599,
      originalPrice: 1199,
      discount: "50% OFF",
      rating: 4.3,
      ratingCount: "9.6k",
      image: "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=600&q=80",
      highlights: ["100% Bio-Wash", "Low Shrinkage"],
      fabricRating: 4.3,
      authenticityScore: 94
    },
    {
      productId: "SKU-331092",
      title: "Flying Machine Men Washed Denim Jacket",
      brand: "Flying Machine",
      source: "WISHLIST",
      wishlistSavedDays: 34,
      confidenceScore: 90,
      recommendedSize: "M",
      fitConfidence: "95% Fit Match",
      price: 2499,
      originalPrice: 4999,
      discount: "50% OFF",
      rating: 4.6,
      ratingCount: "8.3k",
      image: "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?auto=format&fit=crop&w=600&q=80",
      highlights: ["Heavy Cotton Denim", "Reinforced Seams"],
      fabricRating: 4.8,
      authenticityScore: 98
    },
    {
      productId: "SKU-554109",
      title: "Biba Women Embroidered Chanderi Dupatta",
      brand: "Biba",
      source: "WISHLIST",
      wishlistSavedDays: 10,
      confidenceScore: 87,
      recommendedSize: "Free Size",
      fitConfidence: "Pairs with Kurta",
      price: 899,
      originalPrice: 1799,
      discount: "50% OFF",
      rating: 4.5,
      ratingCount: "4.7k",
      image: "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&w=600&q=80",
      highlights: ["Pure Chanderi Silk", "Zari Embroidery"],
      fabricRating: 4.7,
      authenticityScore: 99
    },
    {
      productId: "SKU-112948",
      title: "Nike Men Court Vision Low Sneakers",
      brand: "Nike",
      source: "WISHLIST",
      wishlistSavedDays: 27,
      confidenceScore: 93,
      recommendedSize: "UK 8",
      fitConfidence: "97% Fit Match",
      price: 3995,
      originalPrice: 5995,
      discount: "33% OFF",
      rating: 4.8,
      ratingCount: "15.9k",
      image: "https://images.unsplash.com/photo-1552346154-21d32810aba3?auto=format&fit=crop&w=600&q=80",
      highlights: ["100% Genuine Nike Direct", "Cushioned Comfort"],
      fabricRating: 4.9,
      authenticityScore: 100
    },
    {
      productId: "SKU-994821",
      title: "Jack & Jones Men Solid Slim Casual Shirt",
      brand: "Jack & Jones",
      source: "WISHLIST",
      wishlistSavedDays: 16,
      confidenceScore: 86,
      recommendedSize: "M",
      fitConfidence: "92% Fit Match",
      price: 1399,
      originalPrice: 2799,
      discount: "50% OFF",
      rating: 4.4,
      ratingCount: "6.5k",
      image: "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?auto=format&fit=crop&w=600&q=80",
      highlights: ["Breathable Poplin", "Pre-Shrunk"],
      fabricRating: 4.5,
      authenticityScore: 97
    },

    // 10 Complementary Discovery Items (50%)
    {
      productId: "SKU-441092",
      title: "Highlander Slim Fit Chinos",
      brand: "Highlander",
      source: "DISCOVERY_COMPLEMENTARY",
      wishlistSavedDays: 19,
      confidenceScore: 86,
      recommendedSize: "32",
      fitConfidence: "Pairs with Cotton Shirt",
      price: 999,
      originalPrice: 1999,
      discount: "50% OFF",
      rating: 4.3,
      ratingCount: "8.9k",
      image: "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=600&q=80",
      highlights: ["Stretch Comfort", "Verified Seller"],
      fabricRating: 4.5,
      authenticityScore: 96
    },
    {
      productId: "SKU-338291",
      title: "Libas Women Ethnic Motifs Anarkali",
      brand: "Libas",
      source: "DISCOVERY_COMPLEMENTARY",
      wishlistSavedDays: 14,
      confidenceScore: 87,
      recommendedSize: "M",
      fitConfidence: "Trending Pair",
      price: 1899,
      originalPrice: 3999,
      discount: "52% OFF",
      rating: 4.6,
      ratingCount: "17.8k",
      image: "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?auto=format&fit=crop&w=600&q=80",
      highlights: ["Zari Weave", "Official Brand Direct"],
      fabricRating: 4.7,
      authenticityScore: 98
    },
    {
      productId: "SKU-229103",
      title: "Tommy Hilfiger Men Classic Leather Belt",
      brand: "Tommy Hilfiger",
      source: "DISCOVERY_COMPLEMENTARY",
      wishlistSavedDays: 22,
      confidenceScore: 90,
      recommendedSize: "34",
      fitConfidence: "Pairs with Chinos",
      price: 1899,
      originalPrice: 2999,
      discount: "36% OFF",
      rating: 4.8,
      ratingCount: "3.2k",
      image: "https://images.unsplash.com/photo-1624222247344-550fb60583dc?auto=format&fit=crop&w=600&q=80",
      highlights: ["Genuine Leather", "Official Direct"],
      fabricRating: 4.9,
      authenticityScore: 99
    },
    {
      productId: "SKU-991024",
      title: "HRX Active Running Dri-Fit Shorts",
      brand: "HRX",
      source: "DISCOVERY_COMPLEMENTARY",
      wishlistSavedDays: 9,
      confidenceScore: 86,
      recommendedSize: "M",
      fitConfidence: "Athletic Cut",
      price: 799,
      originalPrice: 1599,
      discount: "50% OFF",
      rating: 4.5,
      ratingCount: "12.8k",
      image: "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?auto=format&fit=crop&w=600&q=80",
      highlights: ["Rapid Dry Tech", "Easy Exchange"],
      fabricRating: 4.5,
      authenticityScore: 96
    },
    {
      productId: "SKU-773829",
      title: "Fossil Men Minimalist Leather Watch",
      brand: "Fossil",
      source: "DISCOVERY_COMPLEMENTARY",
      wishlistSavedDays: 31,
      confidenceScore: 94,
      recommendedSize: "Free Size",
      fitConfidence: "Styling Accessory",
      price: 6495,
      originalPrice: 9995,
      discount: "35% OFF",
      rating: 4.9,
      ratingCount: "5.1k",
      image: "https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=600&q=80",
      highlights: ["2-Year Warranty", "Official Brand Direct"],
      fabricRating: 5.0,
      authenticityScore: 100
    },
    {
      productId: "SKU-884910",
      title: "Ray-Ban Polarized Aviator Sunglasses",
      brand: "Ray-Ban",
      source: "DISCOVERY_COMPLEMENTARY",
      wishlistSavedDays: 17,
      confidenceScore: 93,
      recommendedSize: "Standard",
      fitConfidence: "Pairs with Summer Fits",
      price: 5290,
      originalPrice: 7590,
      discount: "30% OFF",
      rating: 4.8,
      ratingCount: "9.2k",
      image: "https://images.unsplash.com/photo-1572635196237-14b3f281503f?auto=format&fit=crop&w=600&q=80",
      highlights: ["UV400 Protection", "100% Genuine Barcode"],
      fabricRating: 4.9,
      authenticityScore: 100
    },
    {
      productId: "SKU-662918",
      title: "Lavie Women Structured Satchel Handbag",
      brand: "Lavie",
      source: "DISCOVERY_COMPLEMENTARY",
      wishlistSavedDays: 11,
      confidenceScore: 88,
      recommendedSize: "Medium",
      fitConfidence: "Trending Pair",
      price: 1799,
      originalPrice: 3999,
      discount: "55% OFF",
      rating: 4.5,
      ratingCount: "13.4k",
      image: "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=600&q=80",
      highlights: ["Premium Vegan Leather", "Spacious 3-Zip"],
      fabricRating: 4.6,
      authenticityScore: 97
    },
    {
      productId: "SKU-443918",
      title: "Woodland Men Rugged Leather Boots",
      brand: "Woodland",
      source: "DISCOVERY_COMPLEMENTARY",
      wishlistSavedDays: 26,
      confidenceScore: 89,
      recommendedSize: "UK 8",
      fitConfidence: "95% Fit Match",
      price: 3495,
      originalPrice: 4995,
      discount: "30% OFF",
      rating: 4.7,
      ratingCount: "8.7k",
      image: "https://images.unsplash.com/photo-1520639888713-7851133b1ed0?auto=format&fit=crop&w=600&q=80",
      highlights: ["Heavy-Duty Nubuck", "Oil Resistant Sole"],
      fabricRating: 4.8,
      authenticityScore: 99
    },
    {
      productId: "SKU-119283",
      title: "USPA Men Pique Polo T-Shirt",
      brand: "U.S. Polo Assn.",
      source: "DISCOVERY_COMPLEMENTARY",
      wishlistSavedDays: 13,
      confidenceScore: 88,
      recommendedSize: "M",
      fitConfidence: "94% Fit Match",
      price: 1199,
      originalPrice: 2199,
      discount: "45% OFF",
      rating: 4.6,
      ratingCount: "16.1k",
      image: "https://images.unsplash.com/photo-1581655353564-df123a1eb820?auto=format&fit=crop&w=600&q=80",
      highlights: ["100% Combed Cotton", "Classic Ribbed Collar"],
      fabricRating: 4.7,
      authenticityScore: 98
    },
    {
      productId: "SKU-552919",
      title: "Casio Vintage Digital Gold Watch",
      brand: "Casio",
      source: "DISCOVERY_COMPLEMENTARY",
      wishlistSavedDays: 20,
      confidenceScore: 91,
      recommendedSize: "Free Size",
      fitConfidence: "Retro Accent",
      price: 2495,
      originalPrice: 3295,
      discount: "24% OFF",
      rating: 4.8,
      ratingCount: "22.3k",
      image: "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=600&q=80",
      highlights: ["Water Resistant", "Official Casio India Warranty"],
      fabricRating: 4.9,
      authenticityScore: 100
    }
  ]
};

const MOCK_TRENDING_PRODUCTS = [
  {
    productId: "SKU-TR-101",
    brand: "H&M",
    title: "Relaxed Fit Cotton Overshirt",
    wishlistSavedDays: 7,
    price: 1999,
    originalPrice: 2999,
    discount: "33% OFF",
    rating: 4.5,
    ratingCount: "4.1k",
    confidenceScore: 88,
    fitConfidence: "94% Fit Match",
    image: "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=600&q=80"
  },
  {
    productId: "SKU-TR-102",
    brand: "MANGO",
    title: "Women Floral Pleated Midi Dress",
    wishlistSavedDays: 23,
    price: 3490,
    originalPrice: 4990,
    discount: "30% OFF",
    rating: 4.6,
    ratingCount: "2.3k",
    confidenceScore: 90,
    fitConfidence: "96% Fit Match",
    image: "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=600&q=80"
  },
  {
    productId: "SKU-TR-103",
    brand: "LEVIS",
    title: "Men 511 Slim Fit Clean Jeans",
    wishlistSavedDays: 15,
    price: 2499,
    originalPrice: 4299,
    discount: "41% OFF",
    rating: 4.7,
    ratingCount: "19.5k",
    confidenceScore: 92,
    fitConfidence: "97% Fit Match",
    image: "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=600&q=80"
  },
  {
    productId: "SKU-TR-104",
    brand: "TAAVI",
    title: "Indigo Handblock Printed Pure Cotton Shirt",
    wishlistSavedDays: 29,
    price: 1299,
    originalPrice: 2599,
    discount: "50% OFF",
    rating: 4.4,
    ratingCount: "7.8k",
    confidenceScore: 87,
    fitConfidence: "93% Fit Match",
    image: "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=600&q=80"
  }
];

class SenseAPIClient {
  constructor(baseUrl = "http://localhost:8080/api/v1/sense") {
    this.baseUrl = baseUrl;
  }

  async getHomePicks(userId = "USR_10001") {
    try {
      const resp = await fetch(`${this.baseUrl}/home-picks?user_id=${userId}`, { signal: AbortSignal.timeout(1500) });
      if (resp.ok) {
        const json = await resp.json();
        return json.data;
      }
    } catch (e) {
      console.warn("Backend unavailable, using local intelligence engine cache:", e);
    }
    return MOCK_HOME_PICKS;
  }

  getTrendingProducts() {
    return MOCK_TRENDING_PRODUCTS;
  }

  getAllCatalogProducts() {
    return [...MOCK_HOME_PICKS.products, ...MOCK_TRENDING_PRODUCTS];
  }

  async getProductConfidence(productId, userId = "USR_10001", size = "M") {
    const all = this.getAllCatalogProducts();
    const baseProduct = all.find(p => p.productId === productId) || all[0];
    const categoryInsights = this._generateProductReviewInsights(baseProduct);
    
    // Compute unique wishlist saved days
    const savedDays = baseProduct.wishlistSavedDays || (((productId.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)) % 26) + 6);
    
    return {
      productId: baseProduct.productId,
      title: baseProduct.title,
      brand: baseProduct.brand,
      source: baseProduct.source || "WISHLIST",
      wishlistSavedDays: savedDays,
      price: baseProduct.price,
      originalPrice: baseProduct.originalPrice || baseProduct.price * 2,
      discount: baseProduct.discount || "50% OFF",
      rating: baseProduct.rating || 4.5,
      ratingCount: baseProduct.ratingCount || "10.4k",
      image: baseProduct.image,
      overallConfidenceScore: baseProduct.confidenceScore || 89,
      confidenceTier: "HIGH_CONFIDENCE",
      xaiExplanation: `Recommended for you because you recently browsed ${baseProduct.brand} & ${baseProduct.title.toLowerCase()}, and this item has a ${baseProduct.fitConfidence || '96% Fit Match'} in Size M with colorfast fabric tested across 400+ washes.`,
      signals: {
        authenticity: {
          status: "VERIFIED",
          badge: "100% Genuine Brand Direct Assurance",
          score: baseProduct.authenticityScore || 98,
          merchantTier: "TIER_1_DIRECT_BRAND_FULFILLED"
        },
        quality: {
          score: Math.round((baseProduct.fabricRating || 4.7) * 20),
          fabricRating: baseProduct.fabricRating || 4.7,
          colorFastness: "Excellent (Tested across 400+ washes)",
          sentimentSummary: `89% of verified buyers praise the authentic hand-feel and durable stitching.`,
          aspects: [
            { label: "Fabric Quality", rating: (baseProduct.fabricRating || 4.7) + " ★" },
            { label: "Colorfastness", rating: "Tested (400+ washes)" },
            { label: "Stitch Durability", rating: "Reinforced Seams" }
          ]
        },
        fitAndSizing: {
          recommendedSize: baseProduct.recommendedSize || "M",
          fitMatchPercentage: parseInt(baseProduct.fitConfidence) || 96,
          sizeFeedback: "True to Size (88% consensus)",
          userSpecificNote: `Matches your previous ${baseProduct.brand} & Levi's ${baseProduct.recommendedSize || 'M'} purchases.`
        },
        returnConfidence: {
          returnEaseScore: 95,
          badge: "Hassle-Free 14-Day Doorstep Pickup",
          categoryReturnRate: "Low (< 3.8%)"
        }
      },
      customerPhotos: [
        {
          url: baseProduct.image,
          wearerSize: `Size ${baseProduct.recommendedSize || 'M'}`,
          clarity: "96% Verified Clarity"
        },
        {
          url: "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=400&q=80",
          wearerSize: `Size ${baseProduct.recommendedSize || 'M'}`,
          clarity: "92% Fabric Detail"
        }
      ],
      reviewTelemetry: categoryInsights
    };
  }

  _generateProductReviewInsights(product) {
    const title = (product.title || "").toLowerCase();

    if (title.includes("kurta") || title.includes("anarkali") || title.includes("dress") || title.includes("dupatta")) {
      return {
        buyers: [
          {
            name: "Priya R.",
            stats: "5'4\" • 56 kg • Bought Size M",
            quote: `"Drapes beautifully and the color is exactly as shown. Pure soft fabric with zero shrinkage after multiple delicate washes."`,
            avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80"
          },
          {
            name: "Ananya K.",
            stats: "5'6\" • 61 kg • Bought Size M",
            quote: `"Flattering A-line cut with intricate stitch finishing. Extremely comfortable for all-day festive or casual wear."`,
            avatar: "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=300&q=80"
          }
        ],
        metrics: [
          { title: "Colorfastness Retention", pct: "98%", sub: "Tested across 400+ delicate washes" },
          { title: "Embroidery & Seam Finish", pct: "94%", sub: "Reinforced micro-zari interlining" },
          { title: "Bust & Waist Drape", pct: "92%", sub: "True to Indian ethnic sizing chart" }
        ],
        strengths: [
          "100% Breathable pure combed cotton blend",
          "Colorfast reactive dyes that resist fading",
          "Graceful silhouette designed for effortless movement"
        ],
        care: [
          "Hand wash or mild machine cycle recommended for zari longevity",
          "Medium heat iron inside out to preserve delicate print luster"
        ]
      };
    } else if (title.includes("shoe") || title.includes("sneaker") || title.includes("boot")) {
      return {
        buyers: [
          {
            name: "Vikram T.",
            stats: "Bought UK 8 • Normal Arch • Regular Fit",
            quote: `"Ultra-responsive sole cushioning. Zero heel slip during runs and high durability on urban pavements."`,
            avatar: "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=300&q=80"
          },
          {
            name: "Siddharth P.",
            stats: "Bought UK 8 • Daily Commuter",
            quote: `"Lightweight upper mesh breathes really well. Feet stayed fresh even after 8 hours of continuous wear."`,
            avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80"
          }
        ],
        metrics: [
          { title: "Midsole Cushioning", pct: "97%", sub: "High-rebound shock absorption" },
          { title: "Anti-Slip Grip", pct: "95%", sub: "Multi-surface rubber traction" },
          { title: "True to Size Fit", pct: "91%", sub: "Matches standard UK/India foot molds" }
        ],
        strengths: [
          "Engineered breathable mesh upper for maximum airflow",
          "Reinforced heel counter providing lateral stability",
          "Durable abrasion-resistant rubber outsole"
        ],
        care: [
          "Wipe clean with a damp cloth; avoid soaking in water",
          "Air dry at room temperature away from direct intense sunlight"
        ]
      };
    } else if (title.includes("trouser") || title.includes("chino") || title.includes("jean") || title.includes("short")) {
      return {
        buyers: [
          {
            name: "Aman D.",
            stats: "5'10\" • 32 Waist • Bought Size 32",
            quote: `"Spot-on waist fit with the perfect amount of stretch. Tapers cleanly at the ankle without feeling tight."`,
            avatar: "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=300&q=80"
          },
          {
            name: "Rohit V.",
            stats: "6'0\" • 76 kg • Bought Size 32",
            quote: `"Thick, durable fabric that holds its shape all day. Looks crisp for office casuals and weekend outings."`,
            avatar: "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=300&q=80"
          }
        ],
        metrics: [
          { title: "Waistband Stretch Comfort", pct: "95%", sub: "2% Lycra elastane flex blend" },
          { title: "Seam & Pocket Durability", pct: "93%", sub: "Reinforced bar-tack stitching" },
          { title: "Inseam & Drape Accuracy", pct: "90%", sub: "Clean European tapered silhouette" }
        ],
        strengths: [
          "Pre-washed cotton twill offering instant broken-in comfort",
          "Deep reinforced pocket bags securing smartphones and wallets",
          "Versatile clean cut suitable for tuck or untuck styling"
        ],
        care: [
          "Wash inside out in cold water to prevent color wash-down",
          "Warm iron or hang dry to maintain sharp front crease"
        ]
      };
    } else if (title.includes("belt") || title.includes("watch") || title.includes("sunglass") || title.includes("handbag")) {
      return {
        buyers: [
          {
            name: "Arjun K.",
            stats: "Bought Free Size • Verified Brand Direct",
            quote: `"Exceptional build quality and authentic weight. Delivered with original manufacturer warranty barcode certificate."`,
            avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80"
          },
          {
            name: "Sneha M.",
            stats: "Bought Standard Size • Verified Purchase",
            quote: `"Hardware finish and stitching are immaculate. Looks even more premium in person than in the photos."`,
            avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80"
          }
        ],
        metrics: [
          { title: "Hardware & Build Finish", pct: "98%", sub: "High-grade scratch-resistant alloy" },
          { title: "Material Authenticity", pct: "99%", sub: "100% Genuine Brand Direct certified" },
          { title: "Ergonomic Comfort", pct: "94%", sub: "Precision weighted and balanced" }
        ],
        strengths: [
          "100% Authentic product sourced directly from official brand warehouse",
          "Rust-proof premium hardware with satin finish",
          "Comes in official brand presentation gift box"
        ],
        care: [
          "Store in the provided microfiber protective pouch when not in use",
          "Clean with a dry, soft lint-free cloth to maintain shine"
        ]
      };
    } else {
      // Default: Shirts & Tops (Roadster, WROGN, H&M, Taavi, etc.)
      return {
        buyers: [
          {
            name: "Rohan S.",
            stats: "5'10\" • 71 kg • Bought Size M",
            quote: `"Fits like it was custom stitched. Fabric breathes wonderfully in humid weather, zero scratchiness on skin."`,
            avatar: "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=300&q=80"
          },
          {
            name: "Karan M.",
            stats: "5'11\" • 74 kg • Bought Size M",
            quote: `"Great collar stiffness without being rigid. Sleeves hit right above wrist joint for a sharp silhouette."`,
            avatar: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80"
          }
        ],
        metrics: [
          { title: "Fabric Breathability", pct: "96%", sub: "Ideal for warm tropical climate" },
          { title: "Collar & Seam Finish", pct: "93%", sub: "Double-reinforced interlining" },
          { title: "True to Size Drape", pct: "88%", sub: "Matches standard European sizing" }
        ],
        strengths: [
          "Naturally moisture-wicking 100% pure combed fabric",
          "Reinforced mother-of-pearl buttons with cross-stitching",
          "Curved hemline designed to look sharp both tucked and untucked"
        ],
        care: [
          "Natural fabric texture develops charming micro-creases when worn",
          "Requires steam ironing or damp hang-dry for crisp look"
        ]
      };
    }
  }

  async getCheckoutPicks(cartSkus = ["SKU-982341"]) {
    // Return high confidence wishlist items that complement cart
    return [
      MOCK_HOME_PICKS.products[10], // Highlander Chinos (Discovery)
      MOCK_HOME_PICKS.products[12], // Tommy Hilfiger Belt (Discovery)
      MOCK_HOME_PICKS.products[2]   // Puma Shoes (Wishlist)
    ];
  }

  async compareProducts(products) {
    const bestFit = products.reduce((prev, curr) => (curr.confidenceScore > prev.confidenceScore ? curr : prev), products[0]);
    const bestValue = products.reduce((prev, curr) => ((curr.confidenceScore / curr.price) > (prev.confidenceScore / prev.price) ? curr : prev), products[0]);

    return {
      status: "SUCCESS",
      products: products.map(p => ({
        productId: p.productId,
        title: p.title,
        brand: p.brand,
        price: p.price,
        image: p.image,
        confidenceScore: p.confidenceScore,
        winnerBadges: p.productId === bestFit.productId ? ["🎯 Best Fit Match"] : (p.productId === bestValue.productId ? ["💡 Best Value"] : []),
        values: {
          overall_confidence: `${p.confidenceScore} / 100`,
          price: `₹${p.price}`,
          fit_match: p.fitConfidence,
          fabric_quality: `${p.fabricRating || 4.6} / 5.0 ★`,
          color_fastness: "Tested across 400+ washes",
          authenticity: "100% Brand Direct",
          return_ease: "14-Day Doorstep Pickup"
        }
      }))
    };
  }
}

window.senseAPI = new SenseAPIClient();
