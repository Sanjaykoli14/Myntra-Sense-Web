"""
Standardized Cache Key Patterns for Myntra Sense Backend.
"""

def key_home_picks(user_id: str) -> str:
    return f"sense:v1:home_picks:{user_id}"

def key_product_confidence(product_id: str, user_id: str = "GLOBAL") -> str:
    return f"sense:v1:confidence:{product_id}:{user_id}"

def key_shortlist_comparison(product_ids_hash: str) -> str:
    return f"sense:v1:compare:{product_ids_hash}"

def key_seller_authenticity(seller_id: str) -> str:
    return f"sense:v1:auth:{seller_id}"
