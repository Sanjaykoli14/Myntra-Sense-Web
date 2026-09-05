"""
Offline Historical Training Dataset Generator for Myntra Sense.
Links past Wishlist additions to 30-Day Purchase Conversion outcomes with historical feature point-in-time joins.
Prepares dataset for Phase 2 GBDT and Two-Tower Intent Ranker.
"""

import time
import random
import uuid
import json
from typing import Dict, Any, List


def generate_synthetic_historical_training_data(
    num_samples: int = 1000,
    positive_conversion_ratio: float = 0.18
) -> List[Dict[str, Any]]:
    """
    Generate point-in-time correct training records matching Feast Offline Store export.
    Each record represents an item added to a wishlist with its historical features and whether it was purchased within 30 days.
    """
    records: List[Dict[str, Any]] = []
    
    categories = [
        "MEN_CASUAL_SHIRTS", "WOMEN_ETHNIC_KURTAS", "FOOTWEAR_SPORTS",
        "MEN_TROUSERS", "MEN_CASUAL_TEES", "ACCESSORIES_BELTS"
    ]
    brands = ["Roadster", "Highlander", "Anouk", "Puma", "WROGN", "Libas", "Nike"]
    sizes = ["S", "M", "L", "XL", "32", "34", "8", "9"]
    
    for i in range(num_samples):
        user_id = f"USR_{random.randint(10000, 99999)}"
        product_id = f"SKU_{random.randint(100000, 999999)}"
        category = random.choice(categories)
        brand = random.choice(brands)
        user_pref_size = random.choice(sizes)
        
        # User profile features at event timestamp
        historical_return_rate = round(random.uniform(0.01, 0.25), 3)
        user_aov = round(random.uniform(800.0, 3500.0), 2)
        total_orders = random.randint(1, 40)
        
        # Real-time intent features at event timestamp
        search_query_match = random.random() > 0.4
        dwell_time_seconds = random.randint(5, 300)
        pdp_views_prior = random.randint(1, 15)
        cosine_query_sim = round(random.uniform(0.3, 0.95), 4) if search_query_match else round(random.uniform(0.05, 0.4), 4)
        
        # Item confidence features at event timestamp
        authenticity_index = round(random.uniform(0.88, 0.99), 3)
        quality_score = round(random.uniform(0.70, 0.98), 3)
        fabric_score = round(random.uniform(0.75, 0.98), 3)
        size_consensus = round(random.uniform(80.0, 98.0), 1)
        item_rating = round(random.uniform(3.8, 4.8), 2)
        
        # Purchase propensity calculation (ground truth simulator)
        propensity = (
            0.30 * cosine_query_sim +
            0.25 * quality_score +
            0.20 * (size_consensus / 100.0) +
            0.15 * min(dwell_time_seconds / 120.0, 1.0) -
            0.15 * historical_return_rate
        )
        
        # Label: Purchased within 30 days (1 or 0)
        purchased_30d = 1 if (propensity > 0.45 and random.random() < 0.65) or (random.random() < positive_conversion_ratio) else 0
        days_to_purchase = random.randint(1, 28) if purchased_30d else None
        
        record = {
            "wishlist_event_id": str(uuid.uuid4()),
            "user_id": user_id,
            "product_id": product_id,
            "category_id": category,
            "brand_id": brand,
            "user_primary_size": user_pref_size,
            "user_return_rate_30d": historical_return_rate,
            "user_avg_order_value": user_aov,
            "user_lifetime_orders": total_orders,
            "realtime_query_similarity": cosine_query_sim,
            "session_dwell_time_sec": dwell_time_seconds,
            "session_pdp_views_count": pdp_views_prior,
            "item_authenticity_index": authenticity_index,
            "item_quality_score": quality_score,
            "item_fabric_score": fabric_score,
            "item_size_accuracy_pct": size_consensus,
            "item_average_rating": item_rating,
            "target_purchased_within_30d": purchased_30d,
            "days_to_purchase": days_to_purchase,
            "timestamp_iso": "2026-08-01T10:00:00Z"
        }
        records.append(record)
        
    return records


if __name__ == "__main__":
    data = generate_synthetic_historical_training_data(10)
    print(f"Generated {len(data)} sample historical records.")
    print("Sample record:", json.dumps(data[0], indent=2))
