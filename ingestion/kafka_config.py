"""
Kafka Producer and Consumer configurations for Myntra Sense Telemetry.
High-throughput, low-latency configuration tuned for P95 < 100ms publishing SLA and 50k+ RPS.
"""

from typing import Dict, Any


def get_kafka_producer_config(bootstrap_servers: str = "localhost:9092") -> Dict[str, Any]:
    return {
        "bootstrap.servers": bootstrap_servers,
        "client.id": "myntra-sense-telemetry-producer",
        "acks": "1",  # High throughput for telemetry while ensuring leader acknowledgment
        "enable.idempotence": True,
        "compression.type": "snappy",
        "linger.ms": 5,  # Micro-batching window to optimize throughput without adding perceptible latency
        "batch.size": 65536,  # 64 KB batch buffer
        "buffer.memory": 67108864,  # 64 MB buffer pool
        "max.in.flight.requests.per.connection": 5,
        "retries": 3,
        "retry.backoff.ms": 100,
        "request.timeout.ms": 3000,
        "delivery.timeout.ms": 10000,
    }


def get_flink_consumer_config(bootstrap_servers: str = "localhost:9092", group_id: str = "myntra-sense-flink-session-window") -> Dict[str, Any]:
    return {
        "bootstrap.servers": bootstrap_servers,
        "group.id": group_id,
        "auto.offset.reset": "latest",
        "enable.auto.commit": False,  # Managed by Flink checkpointing for exactly-once guarantees
        "fetch.min.bytes": 1024,
        "fetch.max.wait.ms": 50,
        "max.partition.fetch.bytes": 1048576,  # 1 MB
    }


KAFKA_TOPICS = {
    "SEARCH": "myntra.sense.search_events.v1",
    "PDP_VIEW": "myntra.sense.pdp_views.v1",
    "WISHLIST_OP": "myntra.sense.wishlist_ops.v1",
    "CLICKSTREAM": "myntra.sense.clickstream_events.v1",
    "CACHE_INVALIDATION": "myntra.sense.cache_invalidation_triggers.v1",
}
