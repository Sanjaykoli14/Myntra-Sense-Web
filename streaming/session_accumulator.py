"""
Stateful 15-Minute Sliding Session Window Processor for Myntra Sense.
Aggregates real-time intent shifts, search terms, and category dwell time.
"""

import time
import math
from typing import Dict, Any, List, Optional


class UserSessionState:
    def __init__(self, user_id: str, window_duration_seconds: int = 900):
        self.user_id = user_id
        self.window_duration_seconds = window_duration_seconds  # 15 minutes = 900s
        
        # Stateful accumulators
        self.search_queries: List[Dict[str, Any]] = []
        self.category_dwell_ms: Dict[str, int] = {}
        self.brand_interactions: Dict[str, int] = {}
        self.pdp_views_count: int = 0
        self.last_active_category: Optional[str] = None
        self.previous_dominant_category: Optional[str] = None
        self.last_event_timestamp_ms: int = 0
        self.wishlist_ops_in_window: int = 0

    def purge_expired_events(self, current_time_ms: int):
        """Sliding window eviction: discard events older than 15 minutes."""
        cutoff_ms = current_time_ms - (self.window_duration_seconds * 1000)
        self.search_queries = [
            q for q in self.search_queries if q.get("timestamp_ms", 0) >= cutoff_ms
        ]

    def record_search(self, query_text: str, category_id: Optional[str], brands: List[str], timestamp_ms: int):
        self.purge_expired_events(timestamp_ms)
        self.last_event_timestamp_ms = max(self.last_event_timestamp_ms, timestamp_ms)
        
        self.search_queries.append({
            "query": query_text,
            "category_id": category_id,
            "timestamp_ms": timestamp_ms
        })
        
        if category_id:
            self._update_category_focus(category_id, dwell_ms_add=3000)
        for b in brands:
            self.brand_interactions[b] = self.brand_interactions.get(b, 0) + 2

    def record_pdp_view(self, category_id: str, brand_id: str, dwell_time_ms: int, timestamp_ms: int):
        self.purge_expired_events(timestamp_ms)
        self.last_event_timestamp_ms = max(self.last_event_timestamp_ms, timestamp_ms)
        self.pdp_views_count += 1
        
        self._update_category_focus(category_id, dwell_ms_add=dwell_time_ms)
        self.brand_interactions[brand_id] = self.brand_interactions.get(brand_id, 0) + 1

    def record_wishlist_op(self, action_type: str, category_id: str, brand_id: str, timestamp_ms: int):
        self.purge_expired_events(timestamp_ms)
        self.last_event_timestamp_ms = max(self.last_event_timestamp_ms, timestamp_ms)
        self.wishlist_ops_in_window += 1
        self._update_category_focus(category_id, dwell_ms_add=5000)
        self.brand_interactions[brand_id] = self.brand_interactions.get(brand_id, 0) + 3

    def _update_category_focus(self, new_category: str, dwell_ms_add: int):
        self.category_dwell_ms[new_category] = self.category_dwell_ms.get(new_category, 0) + dwell_ms_add
        if self.last_active_category and self.last_active_category != new_category:
            self.previous_dominant_category = self.last_active_category
        self.last_active_category = new_category

    def get_dominant_category(self) -> Optional[str]:
        if not self.category_dwell_ms:
            return None
        return max(self.category_dwell_ms.items(), key=lambda x: x[1])[0]

    def compute_intent_shift_score(self) -> float:
        """
        Calculates an Intent Shift Index (0.0 to 1.0).
        High score indicates user shifted interest (e.g. from formal shoes to summer kurtas),
        which requires an immediate cache invalidation and recommendation re-ranking.
        """
        if not self.previous_dominant_category or not self.last_active_category:
            return 0.0
            
        if self.previous_dominant_category == self.last_active_category:
            return 0.0
            
        prev_dwell = self.category_dwell_ms.get(self.previous_dominant_category, 0)
        curr_dwell = self.category_dwell_ms.get(self.last_active_category, 0)
        total_dwell = sum(self.category_dwell_ms.values())
        
        if total_dwell == 0:
            return 0.0
            
        shift_ratio = curr_dwell / float(total_dwell)
        return min(round(shift_ratio, 3), 1.0)

    def extract_realtime_feature_vector(self) -> Dict[str, Any]:
        """Output ready for Feast Online Store ingestion."""
        dominant_cat = self.get_dominant_category() or "UNKNOWN"
        top_brands = sorted(self.brand_interactions.items(), key=lambda x: x[1], reverse=True)[:3]
        recent_queries = [q["query"] for q in self.search_queries[-3:]]
        
        return {
            "user_id": self.user_id,
            "session_active_window_sec": self.window_duration_seconds,
            "dominant_intent_category": dominant_cat,
            "session_dwell_time_seconds": sum(self.category_dwell_ms.values()) // 1000,
            "session_pdp_views_count": self.pdp_views_count,
            "recent_search_terms": recent_queries,
            "top_engaged_brands": [b[0] for b in top_brands],
            "intent_shift_score": self.compute_intent_shift_score(),
            "wishlist_activity_spike": self.wishlist_ops_in_window > 0,
            "feature_computed_at_ms": int(time.time() * 1000)
        }
