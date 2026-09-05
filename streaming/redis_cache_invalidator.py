"""
Redis Cache Invalidation Service for Myntra Sense.
Handles real-time cache eviction when user intent shifts or wishlist mutations occur.
"""

import time
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("SenseCacheInvalidator")


class SenseCacheInvalidator:
    def __init__(self, redis_client=None, mock_mode: bool = True):
        self.mock_mode = mock_mode
        self.redis_client = redis_client
        self.invalidated_keys: List[str] = []
        self.invalidation_latencies_ms: List[float] = []

    def format_user_cache_keys(self, user_id: str) -> List[str]:
        return [
            f"sense:home_picks:{user_id}",
            f"sense:intent_vector:{user_id}",
            f"sense:shortlist_rank:{user_id}",
        ]

    def invalidate_user_recommendations(self, user_id: str, reason: str = "INTENT_SHIFT") -> Dict[str, Any]:
        """Invalidate all cached recommendations and intent rankings for a user."""
        start_t = time.perf_counter()
        keys_to_evict = self.format_user_cache_keys(user_id)
        
        if self.mock_mode:
            for k in keys_to_evict:
                self.invalidated_keys.append(k)
        else:
            if self.redis_client:
                # Use UNLINK for non-blocking asynchronous eviction
                self.redis_client.unlink(*keys_to_evict)
                
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        self.invalidation_latencies_ms.append(elapsed_ms)
        
        logger.debug(f"Invalidated {len(keys_to_evict)} keys for user={user_id}, reason={reason}, took={elapsed_ms:.3f}ms")
        
        return {
            "user_id": user_id,
            "evicted_keys": keys_to_evict,
            "reason": reason,
            "latency_ms": round(elapsed_ms, 3)
        }

    def process_invalidation_trigger(self, trigger_event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        user_id = trigger_event.get("user_id")
        if not user_id:
            return None
            
        reason = trigger_event.get("reason", "STREAM_INTENT_TRIGGER")
        return self.invalidate_user_recommendations(user_id, reason)
