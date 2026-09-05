"""
Prometheus Operational Metrics Exporter for Myntra Sense Serving Cluster.
Exposes standard metrics format for Grafana dashboards & Datadog monitors.
"""

from typing import Dict, Any


class SensePrometheusExporter:
    def format_prometheus_metrics(
        self,
        p99_latency_ms: float,
        cache_hit_ratio: float,
        conversion_lift_pct: float,
        return_rate_delta_pct: float,
        active_variant_rollout_pct: float
    ) -> str:
        """Formats operational metrics into standard Prometheus exposition text."""
        return f"""# HELP myntra_sense_p99_latency_ms P99 Serving latency for Myntra Sense Orchestrator
# TYPE myntra_sense_p99_latency_ms gauge
myntra_sense_p99_latency_ms {p99_latency_ms}

# HELP myntra_sense_cache_hit_ratio Multi-tier cache hit ratio
# TYPE myntra_sense_cache_hit_ratio gauge
myntra_sense_cache_hit_ratio {cache_hit_ratio}

# HELP wishlist_30d_conversion_lift Measured percentage lift in 30-day wishlist conversion
# TYPE wishlist_30d_conversion_lift gauge
wishlist_30d_conversion_lift {conversion_lift_pct}

# HELP post_conversion_return_rate_delta Delta in 30-day post-conversion returns
# TYPE post_conversion_return_rate_delta gauge
post_conversion_return_rate_delta {return_rate_delta_pct}

# HELP myntra_sense_rollout_percentage Percentage of users routed to Sense AI Variant
# TYPE myntra_sense_rollout_percentage gauge
myntra_sense_rollout_percentage {active_variant_rollout_pct}
"""
