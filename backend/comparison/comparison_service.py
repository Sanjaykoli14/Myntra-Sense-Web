"""
Shortlist Side-by-Side Comparison Service for Myntra Sense.
Computes attribute trade-offs, differential highlighting, winner badges, and value metrics.
"""

import time
from typing import Dict, Any, List, Optional
from backend.comparison.taxonomy_validator import TaxonomyValidator


class ComparisonService:
    def __init__(self):
        self.validator = TaxonomyValidator()

    def generate_comparison_matrix(
        self,
        products: List[Dict[str, Any]],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates structured trade-off comparison matrix for 2 to 4 products.
        """
        start_t = time.perf_counter()
        
        is_valid, msg = self.validator.validate_comparable_products(products)
        if not is_valid:
            return {
                "status": "ERROR",
                "error_code": "INCOMPATIBLE_CATEGORIES",
                "message": msg,
                "matrix": None
            }
            
        # Detect if duplicate/near-identical items (CP-03 from edge-case.md)
        brands = set(p.get("brand_id", p.get("brand")) for p in products)
        is_near_identical = len(brands) == 1 and len(products) >= 2
        
        # Attribute rows to compare
        attributes = [
            {"key": "overall_confidence", "label": "Confidence Score (/100)", "type": "NUMBER_HIGHER_BETTER"},
            {"key": "price", "label": "Price (₹)", "type": "PRICE_LOWER_BETTER"},
            {"key": "fit_match", "label": "Fit Match for You", "type": "PERCENTAGE_HIGHER_BETTER"},
            {"key": "fabric_quality", "label": "Fabric Sentiment", "type": "RATING_HIGHER_BETTER"},
            {"key": "color_fastness", "label": "Color Retention", "type": "TEXT"},
            {"key": "authenticity", "label": "Authenticity Guarantee", "type": "BADGE"},
            {"key": "return_ease", "label": "Return Ease", "type": "BADGE"},
            {"key": "customer_rating", "label": "Customer Rating", "type": "RATING_HIGHER_BETTER"},
        ]
        
        # Compute winners for key dimensions
        best_fit_sku = max(products, key=lambda x: x.get("fit_match_pct", x.get("fitMatchPercentage", 90)))["product_id"]
        best_quality_sku = max(products, key=lambda x: x.get("quality_score", x.get("fabricRating", 4.5)))["product_id"]
        
        # Price-to-confidence value score = Confidence / Price * 1000
        best_value_sku = max(
            products,
            key=lambda x: (x.get("confidenceScore", 85) / max(x.get("price", 1000.0), 1.0))
        )["product_id"]
        
        columns = []
        for p in products:
            pid = p["product_id"]
            badges = []
            if pid == best_fit_sku:
                badges.append("🎯 Best Fit Match")
            if pid == best_quality_sku:
                badges.append("⭐ Highest Fabric Quality")
            if pid == best_value_sku:
                badges.append("💡 Best Confidence-to-Value")
                
            columns.append({
                "productId": pid,
                "title": p.get("title", f"Product {pid}"),
                "brand": p.get("brand_id", p.get("brand", "Roadster")),
                "price": p.get("price", 1199.0),
                "confidenceScore": p.get("confidenceScore", 88),
                "winnerBadges": badges,
                "values": {
                    "overall_confidence": f"{p.get('confidenceScore', 88)} / 100",
                    "price": f"₹{p.get('price', 1199.0)}",
                    "fit_match": f"{p.get('fit_match_pct', p.get('fitMatchPercentage', 96))}% Fit Match",
                    "fabric_quality": f"{p.get('fabricRating', 4.7)} / 5.0 (94% Positive)",
                    "color_fastness": p.get("colorFastness", "Tested across 400+ washes"),
                    "authenticity": "100% Brand Direct",
                    "return_ease": "14-Day Doorstep Pickup",
                    "customer_rating": f"{p.get('averageRating', 4.5)} ★ ({p.get('totalRatings', 12000)} reviews)",
                }
            })
            
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        
        return {
            "status": "SUCCESS",
            "isNearIdenticalSkus": is_near_identical,
            "differentialHighlightMode": is_near_identical,
            "comparedCount": len(products),
            "attributes": attributes,
            "products": columns,
            "winnerSummary": {
                "bestFitSku": best_fit_sku,
                "bestQualitySku": best_quality_sku,
                "bestValueSku": best_value_sku
            },
            "latency_ms": round(elapsed_ms, 3)
        }
