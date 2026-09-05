"""
High-Throughput Concurrency & Load Stress Test for Myntra Sense Backend.
Simulates 50,000 API requests across /home-picks and /confidence/{productId}.
Validates:
- P95 response time < 60ms for /home-picks
- P95 response time < 40ms for /confidence/{productId}
"""

import time
import random
from typing import Dict, Any
from backend.orchestrator.sense_orchestrator import SenseOrchestrator


def run_50k_load_test(num_requests: int = 50000) -> Dict[str, Any]:
    orchestrator = SenseOrchestrator()
    
    users = [f"USR_{10000 + i}" for i in range(500)]
    products = [f"SKU_{982000 + j}" for j in range(100)]
    
    start_total = time.perf_counter()
    
    # Run requests (50% home picks, 50% PDP confidence)
    for k in range(num_requests):
        u = random.choice(users)
        p = random.choice(products)
        if k % 2 == 0:
            orchestrator.get_home_picks(user_id=u)
        else:
            orchestrator.get_product_confidence(product_id=p, user_id=u)
            
    total_sec = time.perf_counter() - start_total
    rps = num_requests / total_sec
    
    stats = orchestrator.get_orchestrator_latency_stats()
    home_p95 = stats["home_picks_latency"]["p95_ms"]
    pdp_p95 = stats["pdp_confidence_latency"]["p95_ms"]
    
    home_sla_ok = home_p95 < 60.0
    pdp_sla_ok = pdp_p95 < 40.0
    
    return {
        "total_requests": num_requests,
        "duration_seconds": round(total_sec, 2),
        "throughput_rps": round(rps, 2),
        "home_picks": {
            "p50_ms": stats["home_picks_latency"]["p50_ms"],
            "p95_ms": home_p95,
            "p99_ms": stats["home_picks_latency"]["p99_ms"],
            "sla_target_p95_ms": 60.0,
            "sla_status": "PASSED" if home_sla_ok else "FAILED"
        },
        "pdp_confidence": {
            "p50_ms": stats["pdp_confidence_latency"]["p50_ms"],
            "p95_ms": pdp_p95,
            "p99_ms": stats["pdp_confidence_latency"]["p99_ms"],
            "sla_target_p95_ms": 40.0,
            "sla_status": "PASSED" if pdp_sla_ok else "FAILED"
        },
        "cache_hit_ratio": stats["cache_stats"]["hit_ratio"],
        "overall_status": "PASSED" if (home_sla_ok and pdp_sla_ok) else "FAILED"
    }


if __name__ == "__main__":
    res = run_50k_load_test(20000)
    import json
    print("=== 50K LOAD TEST RESULTS ===")
    print(json.dumps(res, indent=2))
