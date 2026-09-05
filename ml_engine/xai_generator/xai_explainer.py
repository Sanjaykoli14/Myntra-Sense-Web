"""
Explainable AI (XAI) Rationale Generator for Myntra Sense.
Synthesizes user intent, Bayesian fit, and review aspect scores into concise natural-language rationales.
"""

from typing import Dict, Any, Optional
from ml_engine.xai_generator.template_engine import XAITemplateEngine


class XAIExplainer:
    def __init__(self):
        self.template_engine = XAITemplateEngine()

    def generate_recommendation_rationale(
        self,
        user_profile: Dict[str, Any],
        realtime_intent: Dict[str, Any],
        product_metadata: Dict[str, Any],
        fit_result: Dict[str, Any],
        quality_result: Dict[str, Any]
    ) -> str:
        """
        Generates contextual natural-language explanation for why this product is curated and recommended.
        """
        recent_queries = realtime_intent.get("recent_search_terms", [])
        search_term = recent_queries[0] if recent_queries else "casuals"
        
        is_cold_start = user_profile.get("is_cold_start", False)
        
        if is_cold_start:
            return self.template_engine.format_explanation(
                "WISDOM_OF_CROWD_COLD_START",
                {
                    "category_name": product_metadata.get("category_id", "Shirts"),
                }
            )
            
        fit_score = fit_result.get("fit_confidence_score", 95)
        quality_score = quality_result.get("overall_quality_score", 92)
        brand = product_metadata.get("brand_id", product_metadata.get("brand", "Roadster"))
        
        if recent_queries:
            return self.template_engine.format_explanation(
                "SEARCH_AND_FIT_MATCH",
                {
                    "search_term": search_term,
                    "fit_score": fit_score,
                    "fabric_feature": "pure cotton fabric",
                    "brand": brand,
                    "quality_score": quality_score
                }
            )
        else:
            return self.template_engine.format_explanation(
                "WISHLIST_HIGH_QUALITY",
                {
                    "brand": brand,
                    "quality_score": quality_score
                }
            )
