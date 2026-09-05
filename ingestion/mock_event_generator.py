"""
Synthetic Event Stream Generator for Myntra Sense Telemetry Testing.
Generates realistic multi-user clickstream, search, and wishlist event sequences.
"""

import time
import random
import uuid
from typing import Dict, Any, List
from ingestion.client_telemetry_sdk import ClientTelemetrySDK


POPULAR_QUERIES = [
    ("Linen casual shirts for men", "MEN_CASUAL_SHIRTS", ["Roadster", "Highlander", "WROGN"]),
    ("Pure cotton floral kurta", "WOMEN_ETHNIC_KURTAS", ["Anouk", "Libas", "Biba"]),
    ("Running lightweight shoes", "FOOTWEAR_SPORTS", ["Puma", "Nike", "HRX"]),
    ("Slim fit black chinos", "MEN_TROUSERS", ["Highlander", "Mast & Harbour"]),
    ("Oversized graphic tee", "MEN_CASUAL_TEES", ["Kook N Keech", "Roadster"]),
    ("Leather formal belt", "ACCESSORIES_BELTS", ["Tommy Hilfiger", "Louis Philippe"]),
]

PRODUCT_CATALOG = [
    {"product_id": "SKU-982341", "brand": "Roadster", "category": "MEN_CASUAL_SHIRTS", "price": 1199.0},
    {"product_id": "SKU-441092", "brand": "Highlander", "category": "MEN_TROUSERS", "price": 999.0},
    {"product_id": "SKU-772183", "brand": "Anouk", "category": "WOMEN_ETHNIC_KURTAS", "price": 1499.0},
    {"product_id": "SKU-109284", "brand": "Puma", "category": "FOOTWEAR_SPORTS", "price": 2899.0},
    {"product_id": "SKU-552910", "brand": "WROGN", "category": "MEN_CASUAL_SHIRTS", "price": 1699.0},
    {"product_id": "SKU-338291", "brand": "Libas", "category": "WOMEN_ETHNIC_KURTAS", "price": 1899.0},
]


def generate_user_session_events(user_id: str, event_sink_fn) -> List[Dict[str, Any]]:
    """Simulate a realistic 15-minute active shopping session for a single user."""
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    device_id = f"dev_{uuid.uuid4().hex[:8]}"
    
    sdk = ClientTelemetrySDK(
        user_id=user_id,
        session_id=session_id,
        device_id=device_id,
        platform=random.choice(["ANDROID", "IOS", "MOBILE_WEB"]),
        delivery_pincode=random.choice(["560103", "110001", "400001", "700001"]),
        event_sink=event_sink_fn
    )
    
    emitted_events = []
    
    # 1. Search Action
    query, cat, brands = random.choice(POPULAR_QUERIES)
    e1 = sdk.track_search(
        query_text=query,
        inferred_category_id=cat,
        inferred_brands=brands,
        result_count=random.randint(40, 250)
    )
    emitted_events.append(e1)
    
    # 2. PDP Views with varying dwell times
    matching_products = [p for p in PRODUCT_CATALOG if p["category"] == cat]
    if not matching_products:
        matching_products = PRODUCT_CATALOG[:2]
        
    for prod in matching_products:
        dwell_ms = random.randint(3000, 25000)
        viewed_dash = random.random() > 0.3
        score = random.randint(75, 96) if viewed_dash else 0
        
        e2 = sdk.track_pdp_view(
            product_id=prod["product_id"],
            brand_id=prod["brand"],
            category_id=prod["category"],
            dwell_time_ms=dwell_ms,
            is_wishlisted=random.random() > 0.5,
            selected_size=random.choice(["S", "M", "L", "XL"]),
            viewed_confidence_dashboard=viewed_dash,
            confidence_score=score
        )
        emitted_events.append(e2)
        
        # 3. Micro Clickstream on Confidence Badge
        if viewed_dash:
            e3 = sdk.track_clickstream(
                screen_name="PDP",
                element_type="UI_ELEMENT_CONFIDENCE_BADGE_TAP",
                interaction_type="CLICK",
                associated_product_id=prod["product_id"],
                metadata={"confidence_pillar": "FIT_AND_SIZING", "displayed_fit_pct": 96}
            )
            emitted_events.append(e3)
            
    # 4. Wishlist Mutation Action
    target_p = random.choice(PRODUCT_CATALOG)
    e4 = sdk.track_wishlist_op(
        product_id=target_p["product_id"],
        brand_id=target_p["brand"],
        category_id=target_p["category"],
        action_type=random.choice(["ADD", "COMPARE_SELECTED"]),
        target_size=random.choice(["M", "L"]),
        price=target_p["price"],
        total_count_after=random.randint(15, 45)
    )
    emitted_events.append(e4)
    
    sdk.flush()
    sdk.shutdown()
    return emitted_events
