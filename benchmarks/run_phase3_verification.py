"""
Master Phase 3 Verification Runner for Myntra Sense Backend Serving.
Runs:
1. Shortlist Comparison Matrix generation & taxonomy validation tests.
2. Circuit Breaker & 100% Graceful Degradation tests.
3. 50,000 API Requests High-Throughput Latency Benchmark.
"""

import time
import json
from benchmarks.circuit_breaker_test import run_circuit_breaker_verification
from benchmarks.stress_test_50k_rps import run_50k_load_test
from backend.comparison.comparison_service import ComparisonService


def run_full_phase3_verification():
    print("=================================================================")
    print("🚀 STARTING MYNTRA SENSE PHASE 3 (BACKEND & APIS) VERIFICATION")
    print("=================================================================\n")
    
    # 1. Comparison Service Verification
    print("▶ [1/3] Testing Shortlist Comparison Matrix & Winner Badges...")
    comp_service = ComparisonService()
    test_products = [
        {"product_id": "SKU_1", "brand": "Roadster", "category_id": "MEN_CASUAL_SHIRTS", "price": 1199, "confidenceScore": 92, "fit_match_pct": 98, "fabricRating": 4.8},
        {"product_id": "SKU_2", "brand": "Highlander", "category_id": "MEN_CASUAL_SHIRTS", "price": 899, "confidenceScore": 86, "fit_match_pct": 92, "fabricRating": 4.4},
        {"product_id": "SKU_3", "brand": "WROGN", "category_id": "MEN_CASUAL_SHIRTS", "price": 1699, "confidenceScore": 89, "fit_match_pct": 94, "fabricRating": 4.6},
    ]
    matrix_output = comp_service.generate_comparison_matrix(test_products)
    print(f"  ✓ Products Compared: {matrix_output['comparedCount']}")
    print(f"  ✓ Best Fit Winner: {matrix_output['winnerSummary']['bestFitSku']} (SKU_1)")
    print(f"  ✓ Best Value Winner: {matrix_output['winnerSummary']['bestValueSku']} (SKU_2)")
    print(f"  ✓ Matrix Generation Latency: {matrix_output['latency_ms']} ms\n")
    
    # 2. Circuit Breaker & Graceful Degradation Test
    print("▶ [2/3] Verifying Circuit Breakers & 100% Graceful Degradation on Outages...")
    cb_results = run_circuit_breaker_verification()
    print(f"  ✓ Fallback Executions: {cb_results['total_fallback_calls']}")
    print(f"  ✓ Graceful Degradation Ratio: {cb_results['graceful_degradation_ratio']}")
    print(f"  ✓ Status: {cb_results['status']} ✅\n")
    
    # 3. High-Throughput Load & Concurrency Stress Test
    print("▶ [3/3] Running High-Concurrency Stress Test (50,000 API calls)...")
    load_results = run_50k_load_test(num_requests=50000)
    print(f"  ✓ Total Requests: {load_results['total_requests']} in {load_results['duration_seconds']}s")
    print(f"  ✓ Throughput: {load_results['throughput_rps']} RPS")
    print(f"  ✓ Home Picks P95 Latency: {load_results['home_picks']['p95_ms']} ms (SLA < 60ms -> {load_results['home_picks']['sla_status']} ✅)")
    print(f"  ✓ PDP Confidence P95 Latency: {load_results['pdp_confidence']['p95_ms']} ms (SLA < 40ms -> {load_results['pdp_confidence']['sla_status']} ✅)")
    print(f"  ✓ Cache Hit Ratio: {load_results['cache_hit_ratio'] * 100:.1f}%\n")
    
    all_passed = (
        matrix_output["status"] == "SUCCESS" and
        cb_results["status"] == "PASSED" and
        load_results["overall_status"] == "PASSED"
    )
    
    print("=================================================================")
    if all_passed:
        print("✅ PHASE 3 EXIT CRITERIA MET: APIS, RESILIENCE & SLAs VALIDATED!")
    else:
        print("❌ SOME PHASE 3 BENCHMARKS FAILED")
    print("=================================================================")
    
    report = {
        "phase": "Phase 3: Backend Serving Orchestration & APIs",
        "status": "PASSED" if all_passed else "FAILED",
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "comparison_matrix_test": matrix_output,
        "circuit_breaker_test": cb_results,
        "stress_test_results": load_results
    }
    
    with open("phase3_verification_report.json", "w") as f:
        json.dump(report, f, indent=2)
        
    print("📄 Saved verification report to phase3_verification_report.json")
    return report


if __name__ == "__main__":
    run_full_phase3_verification()
