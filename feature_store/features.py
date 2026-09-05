"""
Feast Feature Views and Schema Definitions for Myntra Sense.
Encapsulates User Profile, Real-Time Intent, and Item Confidence Features.
"""

from typing import Dict, Any, List


# 1. User Profile Feature Schema (Batch Materialized Daily into Redis)
USER_PROFILE_FEATURE_SCHEMA = {
    "name": "user_profile_features",
    "entity": "user_id",
    "ttl_days": 30,
    "features": {
        "gender_affinity": "STRING",             # "MEN", "WOMEN", "UNISEX"
        "primary_apparel_size": "STRING",        # "M", "L", "S", "32"
        "secondary_apparel_size": "STRING",      # "L"
        "historical_30d_return_rate": "FLOAT",   # e.g. 0.04 (4%)
        "brand_affinities_json": "STRING",       # JSON map: {"Roadster": 0.85, "Highlander": 0.60}
        "avg_order_value_inr": "FLOAT",          # e.g. 1450.00
        "total_lifetime_orders": "INT64",        # e.g. 24
        "size_sensitivity_score": "FLOAT",       # Propensity to return due to size issues
        "is_chronic_returner": "BOOL",           # Return rate > 60% guardrail
    }
}

# 2. Real-Time Intent Feature Schema (Updated via Flink Streaming into Redis)
USER_REALTIME_INTENT_FEATURE_SCHEMA = {
    "name": "user_realtime_intent_features",
    "entity": "user_id",
    "ttl_minutes": 15,
    "features": {
        "dominant_intent_category": "STRING",     # "MEN_CASUAL_SHIRTS"
        "session_dwell_time_seconds": "INT64",   # Accumulated session dwell time
        "session_pdp_views_count": "INT64",      # Number of PDPs inspected in 15 mins
        "recent_search_terms_json": "STRING",    # ["linen casual shirt", "cotton shirt"]
        "top_engaged_brands_json": "STRING",     # ["Roadster", "Highlander"]
        "intent_shift_score": "FLOAT",           # 0.0 to 1.0
        "wishlist_activity_spike": "BOOL",       # True if recent wishlist op occurred
        "search_intent_vector_16d": "STRING",    # Serialized 16-d semantic embedding
    }
}

# 3. Item Confidence Feature Schema (Catalog-level Confidence Metrics)
ITEM_CONFIDENCE_FEATURE_SCHEMA = {
    "name": "item_confidence_features",
    "entity": "product_id",
    "ttl_days": 7,
    "features": {
        "authenticity_index": "FLOAT",           # 0.0 to 1.0 (e.g. 0.98)
        "is_brand_verified": "BOOL",             # True if official brand fulfillment
        "overall_quality_score": "FLOAT",        # 0.0 to 1.0 (e.g. 0.91)
        "fabric_sentiment_score": "FLOAT",       # Aspect score for fabric hand-feel (e.g. 0.94)
        "color_fastness_score": "FLOAT",         # Aspect score for color retention
        "stitch_durability_score": "FLOAT",      # Aspect score for stitching
        "size_accuracy_consensus_pct": "FLOAT",  # e.g. 96.0 (% true to size)
        "category_30d_return_rate": "FLOAT",     # e.g. 0.038 (3.8%)
        "doorstep_pickup_available": "BOOL",     # Return ease badge
        "verified_review_count": "INT64",        # Total verified reviews mined
        "average_customer_rating": "FLOAT",      # e.g. 4.5
    }
}


def get_all_feature_schemas() -> Dict[str, Any]:
    return {
        "user_profile": USER_PROFILE_FEATURE_SCHEMA,
        "realtime_intent": USER_REALTIME_INTENT_FEATURE_SCHEMA,
        "item_confidence": ITEM_CONFIDENCE_FEATURE_SCHEMA,
    }
