"""
Master Phase 1 Verification Runner for Myntra Sense.
Runs Telemetry Ingestion, Flink Streaming, and Feast Online Feature Store benchmarks.
Verifies all Phase 1 Exit Criteria from implementation_plan.md.
"""

import time
import json
from benchmarks.telemetry_latency_test import run_telemetry_and_streaming_verification
from benchmarks.feature_store_benchmark import run_feature_store_benchmark
from feature_store.historical_dataset_generator import generate_synthetic_historical_training_data


def run_full_phase1_verification():
    print("=================================================================")
    print("🚀 STARTING MYNTRA SENSE PHASE 1 VERIFICATION SUITE")
    print("=================================================================\n")
    
    # 1. Telemetry Ingestion & Stream Processing Verification
    print("▶ [1/3] Running Telemetry Ingestion & Flink Stream Window Benchmark...")
    telemetry_results = run_telemetry_and_streaming_verification(num_users=100)
    print(f"  ✓ Events Processed: {telemetry_results['total_events_processed']}")
    print(f"  ✓ Ingestion P95 Latency: {telemetry_results['producer_telemetry']['p95_ms']} ms (SLA < 100ms -> {telemetry_results['producer_telemetry']['sla_status']})")
    print(f"  ✓ Flink Stream P99 Latency: {telemetry_results['streaming_flink_job']['p99_ms']} ms (SLA < 1500ms -> {telemetry_results['streaming_flink_job']['sla_status']})")
    print(f"  ✓ Cache Invalidations Fired: {telemetry_results['streaming_flink_job']['cache_invalidations_triggered']}\n")
    
    # 2. Feast Online Feature Store Benchmark
    print("▶ [2/3] Running Feast Online Feature Store (25,000 requests, 10 items/batch)...")
    feast_results = run_feature_store_benchmark(num_requests=25000, batch_item_count=10)
    print(f"  ✓ Total Requests: {feast_results['total_requests']}")
    print(f"  ✓ Throughput: {feast_results['throughput_rps']} RPS")
    print(f"  ✓ P50 Read Latency: {feast_results['p50_ms']} ms")
    print(f"  ✓ P95 Read Latency: {feast_results['p95_ms']} ms")
    print(f"  ✓ P99 Read Latency: {feast_results['p99_ms']} ms (SLA < 5ms -> {feast_results['sla_status']})\n")
    
    # 3. Offline Training Dataset Generator
    print("▶ [3/3] Generating Offline Historical Training Dataset for Phase 2 GBDT...")
    offline_data = generate_synthetic_historical_training_data(num_samples=500)
    print(f"  ✓ Generated {len(offline_data)} point-in-time training rows with 30-day conversion labels.\n")
    
    all_passed = (
        telemetry_results["producer_telemetry"]["sla_status"] == "PASSED" and
        telemetry_results["streaming_flink_job"]["sla_status"] == "PASSED" and
        feast_results["sla_status"] == "PASSED"
    )
    
    print("=================================================================")
    if all_passed:
        print("✅ PHASE 1 EXIT CRITERIA MET: ALL SLA BENCHMARKS PASSED!")
    else:
        print("❌ SOME PHASE 1 BENCHMARKS FAILED")
    print("=================================================================")
    
    summary = {
        "phase": "Phase 1: Real-Time Ingestion, Telemetry & Feature Store",
        "status": "PASSED" if all_passed else "FAILED",
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "telemetry_and_streaming": telemetry_results,
        "feature_store_benchmark": feast_results,
        "historical_training_samples": len(offline_data)
    }
    
    with open("phase1_verification_report.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("📄 Saved verification report to phase1_verification_report.json")
    return summary


if __name__ == "__main__":
    run_full_phase1_verification()
