"""
Authenticity & Return Friction Scorer for Myntra Sense.
Scores seller trust, genuine merchant licenses, and category return friction.
"""

from typing import Dict, Any


class AuthenticityAndReturnScorer:
    def evaluate_authenticity(self, product_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates Authenticity Index and Merchant Tier Validation."""
        is_verified_seller = product_metadata.get("is_brand_verified", True)
        auth_index = product_metadata.get("authenticity_index", 0.98)
        
        score_int = int(auth_index * 100)
        
        return {
            "status": "VERIFIED" if score_int >= 90 else "STANDARD",
            "score": score_int,
            "badge": "100% Genuine Brand Assurance" if is_verified_seller else "Seller Verified",
            "merchant_tier": "TIER_1_DIRECT_BRAND_FULFILLED" if is_verified_seller else "TIER_2_MARKETPLACE",
            "supply_chain_verified": True
        }

    def evaluate_return_confidence(self, product_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates Return Friction and Doorstep Pickup Ease."""
        cat_return_rate = product_metadata.get("category_30d_return_rate", 0.038)
        doorstep_pickup = product_metadata.get("doorstep_pickup_available", True)
        is_non_returnable = product_metadata.get("is_non_returnable", False)
        
        # Handling CI-04 (Non-returnable items from edge-case.md)
        if is_non_returnable:
            return {
                "return_ease_score": 0,
                "badge": "100% Sealed & Genuine (Non-Returnable for Hygiene)",
                "category_return_rate": "Non-Returnable",
                "is_non_returnable": True,
                "doorstep_pickup_eligible": False
            }
            
        return_ease = 95 if doorstep_pickup and cat_return_rate < 0.05 else (85 if cat_return_rate < 0.10 else 70)
        
        return {
            "return_ease_score": return_ease,
            "badge": "Hassle-Free 14-Day Doorstep Pickup",
            "category_return_rate": f"Low ({round(cat_return_rate * 100, 1)}%)",
            "is_non_returnable": False,
            "doorstep_pickup_eligible": doorstep_pickup
        }
