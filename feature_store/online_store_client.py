"""
High-Performance Feast Online Feature Store Client for Myntra Sense.
Engineered for ultra-low latency feature retrieval (< 5ms P99 SLA) under 20,000+ RPS.
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("FeastOnlineStoreClient")


class SenseOnlineStoreClient:
    def __init__(self, redis_client=None, mock_mode: bool = True):
        self.mock_mode = mock_mode
        self.redis_client = redis_client
        
        # In-memory storage for mock mode
        self._user_profile_store: Dict[str, Dict[str, Any]] = {}
        self._user_realtime_store: Dict[str, Dict[str, Any]] = {}
        self._item_confidence_store: Dict[str, Dict[str, Any]] = {}
        
        # Telemetry metrics
        self.read_latencies_ms: List[float] = []

    def set_user_profile(self, user_id: str, features: Dict[str, Any]):
        """Materialize or write user profile features."""
        if self.mock_mode:
            self._user_profile_store[user_id] = features
        else:
            key = f"feast:user_profile:{user_id}"
            self.redis_client.set(key, json.dumps(features), ex=604800)

    def set_user_realtime_intent(self, user_id: str, features: Dict[str, Any]):
        """Stream write real-time intent features."""
        if self.mock_mode:
            self._user_realtime_store[user_id] = features
        else:
            key = f"feast:user_intent:{user_id}"
            self.redis_client.set(key, json.dumps(features), ex=900)

    def set_item_confidence(self, product_id: str, features: Dict[str, Any]):
        """Materialize catalog item confidence features."""
        if self.mock_mode:
            self._item_confidence_store[product_id] = features
        else:
            key = f"feast:item_conf:{product_id}"
            self.redis_client.set(key, json.dumps(features), ex=604800)

    def get_online_features(
        self,
        user_id: str,
        product_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Unified multi-entity online feature retrieval.
        Fetches:
          1. User Profile Features (size, returns, brand affinity)
          2. User Real-Time Intent Features (active category, search embedding)
          3. Item Confidence Features for each product in product_ids
        Returns combined feature vector with sub-5ms P99 SLA.
        """
        start_t = time.perf_counter()
        
        user_prof = {}
        user_intent = {}
        item_features: Dict[str, Dict[str, Any]] = {}
        
        if self.mock_mode:
            user_prof = self._user_profile_store.get(user_id, self._get_default_user_profile(user_id))
            user_intent = self._user_realtime_store.get(user_id, self._get_default_realtime_intent(user_id))
            
            for pid in product_ids:
                item_features[pid] = self._item_confidence_store.get(pid, self._get_default_item_confidence(pid))
        else:
            # Batch pipeline in Redis via MGET
            keys = [
                f"feast:user_profile:{user_id}",
                f"feast:user_intent:{user_id}",
            ] + [f"feast:item_conf:{pid}" for pid in product_ids]
            
            values = self.redis_client.mget(keys)
            
            user_prof = json.loads(values[0]) if values[0] else self._get_default_user_profile(user_id)
            user_intent = json.loads(values[1]) if values[1] else self._get_default_realtime_intent(user_id)
            
            for idx, pid in enumerate(product_ids):
                val = values[2 + idx]
                item_features[pid] = json.loads(val) if val else self._get_default_item_confidence(pid)

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        self.read_latencies_ms.append(elapsed_ms)
        if len(self.read_latencies_ms) > 10000:
            self.read_latencies_ms.pop(0)
            
        return {
            "user_id": user_id,
            "user_profile": user_prof,
            "realtime_intent": user_intent,
            "items": item_features,
            "retrieval_latency_ms": round(elapsed_ms, 3)
        }

    def get_latency_stats(self) -> Dict[str, Any]:
        if not self.read_latencies_ms:
            return {"count": 0, "p50_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0}
            
        sorted_lats = sorted(self.read_latencies_ms)
        n = len(sorted_lats)
        p50 = sorted_lats[int(n * 0.50)]
        p95 = sorted_lats[min(int(n * 0.95), n - 1)]
        p99 = sorted_lats[min(int(n * 0.99), n - 1)]
        
        return {
            "count": n,
            "p50_ms": round(p50, 4),
            "p95_ms": round(p95, 4),
            "p99_ms": round(p99, 4),
            "sla_p99_under_5ms": p99 < 5.0
        }

    def _get_default_user_profile(self, user_id: str) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "gender_affinity": "UNISEX",
            "primary_apparel_size": "M",
            "secondary_apparel_size": "L",
            "historical_30d_return_rate": 0.05,
            "brand_affinities_json": "{}",
            "avg_order_value_inr": 1200.0,
            "total_lifetime_orders": 0,
            "size_sensitivity_score": 0.5,
            "is_chronic_returner": False,
            "is_cold_start": True
        }

    def _get_default_realtime_intent(self, user_id: str) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "dominant_intent_category": "UNKNOWN",
            "session_dwell_time_seconds": 0,
            "session_pdp_views_count": 0,
            "recent_search_terms": [],
            "top_engaged_brands": [],
            "intent_shift_score": 0.0,
            "wishlist_activity_spike": False,
            "is_active_session": False
        }

    def _get_default_item_confidence(self, product_id: str) -> Dict[str, Any]:
        return {
            "product_id": product_id,
            "authenticity_index": 0.95,
            "is_brand_verified": True,
            "overall_quality_score": 0.85,
            "fabric_sentiment_score": 0.85,
            "color_fastness_score": 0.85,
            "stitch_durability_score": 0.85,
            "size_accuracy_consensus_pct": 90.0,
            "category_30d_return_rate": 0.045,
            "doorstep_pickup_available": True,
            "verified_review_count": 50,
            "average_customer_rating": 4.2
        }
