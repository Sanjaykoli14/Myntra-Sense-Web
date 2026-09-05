"""
Apache Flink Stream Processing Job Topology for Myntra Sense.
Processes incoming search, PDP view, and wishlist operations into a unified 15-minute sliding session window.
Updates online feature store and issues cache invalidation events.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from streaming.session_accumulator import UserSessionState
from streaming.redis_cache_invalidator import SenseCacheInvalidator

logger = logging.getLogger("FlinkSessionWindowJob")


class FlinkSessionWindowJob:
    def __init__(
        self,
        window_duration_seconds: int = 900,
        intent_shift_threshold: float = 0.40,
        feature_store_sink=None,
        cache_invalidator: Optional[SenseCacheInvalidator] = None
    ):
        self.window_duration_seconds = window_duration_seconds
        self.intent_shift_threshold = intent_shift_threshold
        self.feature_store_sink = feature_store_sink
        self.cache_invalidator = cache_invalidator or SenseCacheInvalidator(mock_mode=True)
        
        # In-memory session state per user (in Flink, this is RocksDB StateBackend)
        self.user_states: Dict[str, UserSessionState] = {}
        self.processed_events_count = 0
        self.stream_processing_latencies_ms: List[float] = []

    def get_or_create_state(self, user_id: str) -> UserSessionState:
        if user_id not in self.user_states:
            self.user_states[user_id] = UserSessionState(
                user_id=user_id,
                window_duration_seconds=self.window_duration_seconds
            )
        return self.user_states[user_id]

    def process_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single streaming event through the window operator.
        Maintains sub-1.5 second end-to-end stream latency SLA.
        """
        start_t = time.perf_counter()
        
        context = event.get("context", {})
        user_id = context.get("user_id") or event.get("user_id", "ANONYMOUS")
        timestamp_ms = event.get("event_timestamp_ms") or int(time.time() * 1000)
        event_type = event.get("event_type", "UNKNOWN")
        
        state = self.get_or_create_state(user_id)
        
        # Route based on event type
        if event_type == "SEARCH":
            state.record_search(
                query_text=event.get("query_text", ""),
                category_id=event.get("inferred_category_id"),
                brands=event.get("inferred_brands", []),
                timestamp_ms=timestamp_ms
            )
        elif event_type == "PDP_VIEW":
            state.record_pdp_view(
                category_id=event.get("category_id", "UNKNOWN"),
                brand_id=event.get("brand_id", "UNKNOWN"),
                dwell_time_ms=event.get("dwell_time_ms", 0),
                timestamp_ms=timestamp_ms
            )
        elif event_type == "WISHLIST_OP":
            state.record_wishlist_op(
                action_type=event.get("action_type", "ADD"),
                category_id=event.get("category_id", "UNKNOWN"),
                brand_id=event.get("brand_id", "UNKNOWN"),
                timestamp_ms=timestamp_ms
            )
            # Wishlist mutations always trigger immediate cache invalidation
            self.cache_invalidator.invalidate_user_recommendations(
                user_id=user_id,
                reason=f"WISHLIST_OP_{event.get('action_type', 'MUTATION')}"
            )
            
        # Check intent shift spike
        shift_score = state.compute_intent_shift_score()
        if shift_score >= self.intent_shift_threshold:
            self.cache_invalidator.invalidate_user_recommendations(
                user_id=user_id,
                reason=f"INTENT_SHIFT_DETECTED_SCORE_{shift_score}"
            )

        # Extract real-time feature vector
        features = state.extract_realtime_feature_vector()
        
        # Sink to Feast Online Store if connected
        if self.feature_store_sink:
            self.feature_store_sink(features)
            
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        self.stream_processing_latencies_ms.append(elapsed_ms)
        self.processed_events_count += 1
        
        return {
            "user_id": user_id,
            "features": features,
            "intent_shift_score": shift_score,
            "processing_latency_ms": round(elapsed_ms, 3)
        }

    def get_latency_stats(self) -> Dict[str, Any]:
        if not self.stream_processing_latencies_ms:
            return {"p50_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0, "count": 0}
            
        sorted_lats = sorted(self.stream_processing_latencies_ms)
        n = len(sorted_lats)
        p50 = sorted_lats[int(n * 0.50)]
        p95 = sorted_lats[min(int(n * 0.95), n - 1)]
        p99 = sorted_lats[min(int(n * 0.99), n - 1)]
        
        return {
            "total_processed": n,
            "p50_ms": round(p50, 4),
            "p95_ms": round(p95, 4),
            "p99_ms": round(p99, 4),
            "sla_stream_latency_sub_1_5s": p99 < 1500.0  # SLA < 1.5s
        }
