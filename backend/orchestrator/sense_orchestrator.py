"""
Sense Orchestrator Microservice for Myntra Sense.
Coordinates Multi-Tier Caching, Feast Online Feature Store, Triton ML Inference, and Circuit Breaker Fallbacks.
Enforces P95 latency SLAs (< 60ms for Home Picks, < 40ms for PDP Confidence).
"""

import time
import logging
from typing import Dict, Any, List, Optional

from backend.cache.multi_tier_cache import MultiTierCache
from backend.cache.cache_keys import key_home_picks, key_product_confidence, key_shortlist_comparison
from backend.resilience.circuit_breaker import CircuitBreaker
from backend.resilience.fallback_engine import FallbackEngine
from backend.comparison.comparison_service import ComparisonService
from feature_store.online_store_client import SenseOnlineStoreClient
from ml_engine.serving.triton_inference_service import TritonInferenceService

logger = logging.getLogger("SenseOrchestrator")


class SenseOrchestrator:
    def __init__(
        self,
        feature_client: Optional[SenseOnlineStoreClient] = None,
        triton_service: Optional[TritonInferenceService] = None,
        cache_manager: Optional[MultiTierCache] = None
    ):
        self.feature_client = feature_client or SenseOnlineStoreClient(mock_mode=True)
        self.triton_service = triton_service or TritonInferenceService()
        self.cache = cache_manager or MultiTierCache(l1_ttl_seconds=30, l2_ttl_seconds=300, mock_mode=True)
        
        self.circuit_breaker = CircuitBreaker(
            name="SenseMLInferenceCircuitBreaker",
            failure_threshold=5,
            timeout_budget_ms=60.0
        )
        self.fallback_engine = FallbackEngine()
        self.comparison_service = ComparisonService()
        
        # Latency trackers
        self.home_picks_latencies_ms: List[float] = []
        self.pdp_confidence_latencies_ms: List[float] = []

    def get_home_picks(self, user_id: str, wishlist_items: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        GET /api/v1/sense/home-picks
        Returns Top 10 curated picks (6 Wishlist + 4 Discovery) with P95 < 60ms SLA.
        """
        start_t = time.perf_counter()
        cache_key = key_home_picks(user_id)
        
        # 1. Check Multi-Tier Cache
        cached_res = self.cache.get(cache_key)
        if cached_res:
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            self.home_picks_latencies_ms.append(elapsed_ms)
            return cached_res

        # 2. Fetch User Profile & Realtime Intent from Feast Online Store (< 5ms)
        user_features = self.feature_client.get_online_features(user_id, [])
        user_profile = user_features.get("user_profile", {})
        realtime_intent = user_features.get("realtime_intent", {})
        
        # Use provided or default mock wishlist items
        items_to_score = wishlist_items or self._get_mock_user_wishlist(user_id)
        discovery_pool = self._get_mock_discovery_pool()

        # 3. Execute Candidate Scoring with Circuit Breaker Protection
        def _execute_ml():
            return self.triton_service.infer_curated_home_picks(
                user_profile=user_profile,
                realtime_intent=realtime_intent,
                wishlist_items=items_to_score,
                catalog_discovery_pool=discovery_pool
            )

        def _execute_fallback():
            return self.fallback_engine.rank_wishlist_heuristic_fallback(
                user_profile=user_profile,
                wishlist_items=items_to_score,
                discovery_pool=discovery_pool
            )

        scored_output = self.circuit_breaker.call(_execute_ml, _execute_fallback)
        
        # Transform into standardized API response format
        response_payload = {
            "status": "success",
            "data": {
                "sectionTitle": "Myntra Sense — Your Wishlist Picks",
                "rationale": f"Curated from your {len(items_to_score)} saved items based on your recent searches for {realtime_intent.get('dominant_intent_category', 'casual wear').replace('_', ' ').lower()}.",
                "totalWishlistCount": len(items_to_score),
                "isFallbackMode": scored_output.get("isFallbackMode", False),
                "products": scored_output.get("curated_products", scored_output.get("products", []))
            }
        }
        
        # Cache result
        self.cache.set(cache_key, response_payload)
        
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        self.home_picks_latencies_ms.append(elapsed_ms)
        if len(self.home_picks_latencies_ms) > 10000:
            self.home_picks_latencies_ms.pop(0)
            
        return response_payload

    def get_product_confidence(
        self,
        product_id: str,
        user_id: str = "USR_10001",
        selected_size: Optional[str] = None,
        product_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        GET /api/v1/sense/confidence/{productId}
        Returns holistic 0-100 Confidence Score and 4 pillar signals with P95 < 40ms SLA.
        """
        start_t = time.perf_counter()
        cache_key = key_product_confidence(product_id, user_id)
        
        cached_res = self.cache.get(cache_key)
        if cached_res:
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            self.pdp_confidence_latencies_ms.append(elapsed_ms)
            return cached_res

        # Fetch features from Feast
        feature_data = self.feature_client.get_online_features(user_id, [product_id])
        user_profile = feature_data.get("user_profile", {})
        realtime_intent = feature_data.get("realtime_intent", {})
        prod_meta = product_metadata or feature_data.get("items", {}).get(product_id, {})
        prod_meta["product_id"] = product_id

        def _execute_ml():
            return self.triton_service.infer_product_confidence_dashboard(
                user_profile=user_profile,
                realtime_intent=realtime_intent,
                product_metadata=prod_meta,
                selected_size=selected_size
            )

        def _execute_fallback():
            return self.fallback_engine.generate_product_confidence_fallback(
                product_id=product_id,
                product_metadata=prod_meta
            )

        confidence_output = self.circuit_breaker.call(_execute_ml, _execute_fallback)
        
        response_payload = {
            "status": "success",
            "data": {
                "productId": product_id,
                "overallConfidenceScore": confidence_output.get("overall_confidence_score", confidence_output.get("overallConfidenceScore", 88)),
                "confidenceTier": confidence_output.get("confidence_tier", confidence_output.get("confidenceTier", "HIGH_CONFIDENCE")),
                "isFallbackMode": confidence_output.get("isFallbackMode", False),
                "xaiExplanation": confidence_output.get("xai_explanation", confidence_output.get("xaiExplanation", "")),
                "signals": confidence_output.get("signals", {}),
                "socialProof": confidence_output.get("socialProof", {
                    "averageRating": 4.5,
                    "totalRatings": 14200,
                    "verifiedReviewCount": 2180,
                    "curatedUserImages": [p.get("image_url", "") for p in confidence_output.get("curated_customer_photos", [])]
                })
            }
        }
        
        self.cache.set(cache_key, response_payload)
        
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        self.pdp_confidence_latencies_ms.append(elapsed_ms)
        if len(self.pdp_confidence_latencies_ms) > 10000:
            self.pdp_confidence_latencies_ms.pop(0)
            
        return response_payload

    def compare_products(
        self,
        products: List[Dict[str, Any]],
        user_id: str = "USR_10001"
    ) -> Dict[str, Any]:
        """
        POST /api/v1/sense/compare
        Returns side-by-side trade-off matrix with P95 < 50ms SLA.
        """
        return self.comparison_service.generate_comparison_matrix(products)

    def get_orchestrator_latency_stats(self) -> Dict[str, Any]:
        def _calc_stats(lats):
            if not lats:
                return {"p50_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0, "count": 0}
            sorted_l = sorted(lats)
            n = len(sorted_l)
            return {
                "count": n,
                "p50_ms": round(sorted_l[int(n * 0.50)], 4),
                "p95_ms": round(sorted_l[min(int(n * 0.95), n - 1)], 4),
                "p99_ms": round(sorted_l[min(int(n * 0.99), n - 1)], 4),
            }

        home_stats = _calc_stats(self.home_picks_latencies_ms)
        pdp_stats = _calc_stats(self.pdp_confidence_latencies_ms)
        
        return {
            "home_picks_latency": {
                **home_stats,
                "sla_target_p95_ms": 60.0,
                "sla_passed": home_stats["p95_ms"] < 60.0
            },
            "pdp_confidence_latency": {
                **pdp_stats,
                "sla_target_p95_ms": 40.0,
                "sla_passed": pdp_stats["p95_ms"] < 40.0
            },
            "cache_stats": self.cache.get_stats(),
            "circuit_breaker_status": self.circuit_breaker.get_status()
        }

    def _get_mock_user_wishlist(self, user_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "product_id": f"SKU_982{i}41",
                "title": f"Roadster Pure Cotton Casual Shirt {i}",
                "brand": "Roadster",
                "brand_id": "Roadster",
                "category_id": "MEN_CASUAL_SHIRTS",
                "price": 1199.0 + (i * 50),
                "in_stock": True,
                "quality_score": 0.92,
                "fit_match_pct": 96.0,
                "authenticity_score": 0.98,
                "fabricRating": 4.7
            }
            for i in range(25)
        ]

    def _get_mock_discovery_pool(self) -> List[Dict[str, Any]]:
        return [
            {
                "product_id": f"SKU_4410{k}",
                "title": f"Highlander Slim Fit Chinos {k}",
                "brand": "Highlander",
                "brand_id": "Highlander",
                "category_id": "MEN_TROUSERS",
                "price": 999.0 + (k * 100),
                "in_stock": True,
                "quality_score": 0.88,
                "fit_match_pct": 92.0
            }
            for k in range(10)
        ]
