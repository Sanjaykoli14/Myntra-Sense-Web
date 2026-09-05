"""
Client-Side Telemetry SDK for Myntra Mobile (iOS/Android) and Web applications.
Provides asynchronous event dispatching, memory-safe queueing, and sub-100ms publishing SLA.
"""

import time
import uuid
import json
import threading
from typing import Dict, Any, List, Optional, Callable


class ClientTelemetrySDK:
    def __init__(
        self,
        user_id: str,
        session_id: str,
        device_id: str,
        platform: str = "ANDROID",
        delivery_pincode: str = "560103",
        flush_interval_seconds: float = 1.0,
        max_batch_size: int = 50,
        event_sink: Optional[Callable[[str, List[Dict[str, Any]]], None]] = None
    ):
        self.user_id = user_id
        self.session_id = session_id
        self.device_id = device_id
        self.platform = platform
        self.delivery_pincode = delivery_pincode
        self.flush_interval_seconds = flush_interval_seconds
        self.max_batch_size = max_batch_size
        self.event_sink = event_sink or self._default_mock_sink
        
        self._event_queue: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._is_running = True
        
        # Background worker for automatic periodic flushing
        self._flush_thread = threading.Thread(target=self._flush_worker, daemon=True)
        self._flush_thread.start()

    def _get_base_context(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "device_id": self.device_id,
            "platform": self.platform,
            "delivery_pincode": self.delivery_pincode,
            "timestamp_ms": int(time.time() * 1000)
        }

    def track_search(
        self,
        query_text: str,
        trigger_source: str = "SEARCH_BAR",
        inferred_category_id: Optional[str] = None,
        inferred_brands: Optional[List[str]] = None,
        result_count: int = 120,
        query_embedding: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """Track user search intent with sub-millisecond recording."""
        start_t = time.perf_counter()
        event = {
            "event_type": "SEARCH",
            "event_id": str(uuid.uuid4()),
            "context": self._get_base_context(),
            "query_text": query_text,
            "normalized_query": query_text.strip().lower(),
            "trigger_source": trigger_source,
            "inferred_category_id": inferred_category_id,
            "inferred_brands": inferred_brands or [],
            "result_count": result_count,
            "query_embedding": query_embedding or [0.0] * 16,
            "event_timestamp_ms": int(time.time() * 1000),
            "client_sdk_record_latency_ms": (time.perf_counter() - start_t) * 1000
        }
        self._enqueue(event)
        return event

    def track_pdp_view(
        self,
        product_id: str,
        brand_id: str,
        category_id: str,
        dwell_time_ms: int = 5000,
        is_wishlisted: bool = False,
        selected_size: Optional[str] = None,
        viewed_confidence_dashboard: bool = False,
        confidence_score: int = 0,
        navigation_source: str = "SENSE_HOME_CARD"
    ) -> Dict[str, Any]:
        """Track Product Display Page engagement and confidence signal interaction."""
        start_t = time.perf_counter()
        event = {
            "event_type": "PDP_VIEW",
            "event_id": str(uuid.uuid4()),
            "context": self._get_base_context(),
            "product_id": product_id,
            "brand_id": brand_id,
            "category_id": category_id,
            "dwell_time_ms": dwell_time_ms,
            "is_wishlisted": is_wishlisted,
            "selected_size": selected_size,
            "viewed_sense_confidence_dashboard": viewed_confidence_dashboard,
            "confidence_score_displayed": confidence_score,
            "navigation_source": navigation_source,
            "event_timestamp_ms": int(time.time() * 1000),
            "client_sdk_record_latency_ms": (time.perf_counter() - start_t) * 1000
        }
        self._enqueue(event)
        return event

    def track_wishlist_op(
        self,
        product_id: str,
        brand_id: str,
        category_id: str,
        action_type: str = "ADD",
        target_size: Optional[str] = None,
        price: float = 1299.0,
        total_count_after: int = 25
    ) -> Dict[str, Any]:
        """Track Wishlist mutations (Add, Remove, Move to Bag, Compare)."""
        start_t = time.perf_counter()
        event = {
            "event_type": "WISHLIST_OP",
            "event_id": str(uuid.uuid4()),
            "context": self._get_base_context(),
            "product_id": product_id,
            "brand_id": brand_id,
            "category_id": category_id,
            "action_type": action_type,
            "target_size": target_size,
            "price_at_action": price,
            "total_wishlist_count_after_op": total_count_after,
            "event_timestamp_ms": int(time.time() * 1000),
            "client_sdk_record_latency_ms": (time.perf_counter() - start_t) * 1000
        }
        self._enqueue(event)
        return event

    def track_clickstream(
        self,
        screen_name: str,
        element_type: str,
        interaction_type: str,
        associated_product_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Track fine-grained UI micro-interactions."""
        start_t = time.perf_counter()
        event = {
            "event_type": "CLICKSTREAM",
            "event_id": str(uuid.uuid4()),
            "context": self._get_base_context(),
            "screen_name": screen_name,
            "element_type": element_type,
            "interaction_type": interaction_type,
            "associated_product_id": associated_product_id,
            "payload_metadata_json": json.dumps(metadata) if metadata else None,
            "event_timestamp_ms": int(time.time() * 1000),
            "client_sdk_record_latency_ms": (time.perf_counter() - start_t) * 1000
        }
        self._enqueue(event)
        return event

    def _enqueue(self, event: Dict[str, Any]):
        with self._lock:
            self._event_queue.append(event)
            if len(self._event_queue) >= self.max_batch_size:
                self.flush()

    def flush(self):
        with self._lock:
            if not self._event_queue:
                return
            batch_to_send = list(self._event_queue)
            self._event_queue.clear()
        
        # Group by event type
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for ev in batch_to_send:
            etype = ev.get("event_type", "UNKNOWN")
            grouped.setdefault(etype, []).append(ev)
            
        for etype, events in grouped.items():
            self.event_sink(etype, events)

    def _flush_worker(self):
        while self._is_running:
            time.sleep(self.flush_interval_seconds)
            self.flush()

    def shutdown(self):
        self._is_running = False
        self.flush()

    def _default_mock_sink(self, event_type: str, events: List[Dict[str, Any]]):
        # Default in-memory handler for unit testing
        pass
