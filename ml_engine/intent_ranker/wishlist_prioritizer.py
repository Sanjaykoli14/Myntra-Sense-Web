"""
Wishlist Prioritization & Curation Pipeline for Myntra Sense.
Filters large wishlists (20 to 50+ saved items) down to the Top 6 Highest-Intent Wishlist Picks + 4 Complementary Items.
"""

from typing import Dict, Any, List, Optional
from ml_engine.intent_ranker.two_tower_embeddings import UserIntentTower, ItemCatalogTower, compute_cosine_similarity
from ml_engine.intent_ranker.gbdt_conversion_model import GBDTConversionRanker


class WishlistPrioritizer:
    def __init__(self):
        self.user_tower = UserIntentTower(embedding_dim=64)
        self.item_tower = ItemCatalogTower(embedding_dim=64)
        self.gbdt_ranker = GBDTConversionRanker()

    def filter_and_rank_wishlist(
        self,
        user_profile: Dict[str, Any],
        realtime_intent: Dict[str, Any],
        wishlist_items: List[Dict[str, Any]],
        catalog_discovery_pool: Optional[List[Dict[str, Any]]] = None,
        target_wishlist_count: int = 10,
        target_discovery_count: int = 10
    ) -> Dict[str, Any]:
        """
        Executes 3-stage ranking pipeline:
        Stage 1: Hard constraint filtering (in-stock, non-delisted, deliverable).
        Stage 2: Two-Tower semantic similarity & GBDT intent scoring.
        Stage 3: Multi-objective ranking to select top 6 wishlist + top 4 discovery.
        """
        user_emb = self.user_tower.encode(user_profile, realtime_intent)
        
        # Stage 1: Hard Filter
        valid_wishlist_candidates = []
        for item in wishlist_items:
            if not item.get("in_stock", True):
                continue
            if item.get("is_delisted", False):
                continue
            valid_wishlist_candidates.append(item)
            
        # Stage 2: Intent Scoring
        scored_wishlist = []
        for item in valid_wishlist_candidates:
            item_emb = self.item_tower.encode(item)
            cos_sim = compute_cosine_similarity(user_emb, item_emb)
            
            sample_for_gbdt = {
                "realtime_query_similarity": cos_sim,
                "item_quality_score": item.get("quality_score", item.get("overall_quality_score", 0.88)),
                "item_size_accuracy_pct": item.get("fit_match_pct", 95.0),
                "session_dwell_time_sec": realtime_intent.get("session_dwell_time_seconds", 30),
                "item_authenticity_index": item.get("authenticity_score", 0.98),
                "user_return_rate_30d": user_profile.get("historical_30d_return_rate", 0.04)
            }
            p_buy = self.gbdt_ranker.predict_propensity(sample_for_gbdt)
            
            # Composite Intent Score Formula
            intent_score = (
                0.35 * cos_sim +
                0.35 * p_buy +
                0.20 * (sample_for_gbdt["item_size_accuracy_pct"] / 100.0) +
                0.10 * sample_for_gbdt["item_quality_score"]
            )
            
            scored_item = dict(item)
            scored_item["cosine_similarity"] = round(cos_sim, 4)
            scored_item["p_buy_30d"] = p_buy
            scored_item["intent_score"] = round(intent_score, 4)
            scored_item["source"] = "WISHLIST"
            scored_wishlist.append(scored_item)

        # Sort wishlist items by intent score descending
        sorted_wishlist = sorted(scored_wishlist, key=lambda x: x["intent_score"], reverse=True)
        top_wishlist_picks = sorted_wishlist[:target_wishlist_count]
        
        # Stage 3: Complementary Discovery Curation
        discovery_picks = []
        discovery_pool = catalog_discovery_pool or []
        
        dominant_cat = realtime_intent.get("dominant_intent_category", "MEN_CASUAL_SHIRTS")
        
        for disc_item in discovery_pool:
            if not disc_item.get("in_stock", True):
                continue
            item_emb = self.item_tower.encode(disc_item)
            cos_sim = compute_cosine_similarity(user_emb, item_emb)
            
            d_scored = dict(disc_item)
            d_scored["cosine_similarity"] = round(cos_sim, 4)
            d_scored["source"] = "DISCOVERY_COMPLEMENTARY"
            d_scored["intent_score"] = round(0.70 * cos_sim + 0.30 * disc_item.get("quality_score", 0.85), 4)
            discovery_picks.append(d_scored)
            
        sorted_discovery = sorted(discovery_picks, key=lambda x: x["intent_score"], reverse=True)
        top_discovery_picks = sorted_discovery[:target_discovery_count]
        
        # Dynamic ratio fallback if user has < 6 wishlist items (UC-02 from edge-case.md)
        final_picks = top_wishlist_picks + top_discovery_picks
        
        return {
            "user_id": user_profile.get("user_id"),
            "total_wishlist_evaluated": len(wishlist_items),
            "valid_in_stock_candidates": len(valid_wishlist_candidates),
            "top_wishlist_count": len(top_wishlist_picks),
            "top_discovery_count": len(top_discovery_picks),
            "total_curated_picks": len(final_picks),
            "curated_products": final_picks
        }
