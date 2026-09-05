"""
End-to-End Latency and Stream Processing Verification for Phase 1.
Validates:
1. Kafka event publishing latency (< 100ms P95 SLA)
2. Flink stream window processing latency (< 1500ms P99 SLA)
3. Real-time intent shift detection & cache invalidation
"""

import time
import random
from typing import Dict, Any
from ingestion.event_producer import SenseTelemetryProducer
from ingestion.client_telemetry_sdk import ClientTelemetrySDK
from ingestion.mock_event_generator import generate_user_session_events
from streaming.flink_session_window_job import FlinkSessionWindowJob
from streaming.redis_cache_invalidator import SenseCacheInvalidator


def run_telemetry_and_streaming_verification(num_users: int = 100) -> Dict[str, Any]:
    producer = SenseTelemetryProducer(mock_mode=True)
    invalidator = SenseCacheInvalidator(mock_mode=True)
    flink_job = FlinkSessionWindowJob(
        window_duration_seconds=900,
        intent_shift_threshold=0.35,
        cache_invalidator=invalidator
    )
    
    all_events = []
    
    # 1. Generate & Ingest session events across users
    for i in range(num_users):
        uid = f"USR_{10000 + i}"
        session_events = generate_user_session_events(
            user_id=uid,
            event_sink_fn=lambda etype, evs: producer.publish_batch(etype, evs)
        )
        all_events.extend(session_events)

    # Ingestion producer latency stats
    producer_stats = producer.get_latency_stats()
    
    # 2. Process all events through Flink stream window topology
    stream_start = time.perf_counter()
    for ev in all_events:
        flink_job.process_event(ev)
    total_stream_time_sec = time.perf_counter() - stream_start
    
    stream_stats = flink_job.get_latency_stats()
    stream_stats["total_stream_time_sec"] = round(total_stream_time_sec, 3)
    stream_stats["cache_invalidations_triggered"] = len(invalidator.invalidated_keys)
    
    # Evaluate Exit Criteria
    pub_sla_passed = producer_stats.get("p95_ms", 999.0) < 100.0
    stream_sla_passed = stream_stats.get("p99_ms", 9999.0) < 1500.0
    
    return {
        "total_events_processed": len(all_events),
        "producer_telemetry": {
            **producer_stats,
            "sla_target_p95_ms": 100.0,
            "sla_status": "PASSED" if pub_sla_passed else "FAILED"
        },
        "streaming_flink_job": {
            **stream_stats,
            "sla_target_p99_ms": 1500.0,
            "sla_status": "PASSED" if stream_sla_passed else "FAILED"
        },
        "overall_phase1_status": "PASSED" if (pub_sla_passed and stream_sla_passed) else "FAILED"
    }


if __name__ == "__main__":
    res = run_telemetry_and_streaming_verification(50)
    print("=== TELEMETRY & STREAMING LATENCY RESULTS ===")
    import json
    print(json.dumps(res, indent=2))
