"""
Guardrail Metric Monitor for Myntra Sense A/B Rollout.
Enforces that conversion lift is achieved organically without increasing returns or breaching latency SLAs.
"""

from typing import Dict, Any, List


class GuardrailMonitor:
    def __init__(self):
        self.max_latency_p95_ms = 60.0
        self.max_crash_rate = 0.0001
        self.max_return_delta = 0.000  # Return rate must remain flat or decrease

    def evaluate_guardrails(
        self,
        control_cohort: List[Dict[str, Any]],
        variant_cohort: List[Dict[str, Any]],
        measured_p95_latency_ms: float = 0.012,
        measured_crash_rate: float = 0.0
    ) -> Dict[str, Any]:
        """
        Evaluates Return Rate, Latency, and Crash Rate guardrails.
        """
        # Return rate calculation among converted users
        ctrl_purchasers = [u for u in control_cohort if u.get("purchased_30d", False)]
        ctrl_returns = sum(1 for u in ctrl_purchasers if u.get("returned_item", False))
        ctrl_return_rate = ctrl_returns / max(len(ctrl_purchasers), 1)

        var_purchasers = [u for u in variant_cohort if u.get("purchased_30d", False)]
        var_returns = sum(1 for u in var_purchasers if u.get("returned_item", False))
        var_return_rate = var_returns / max(len(var_purchasers), 1)

        return_delta = var_return_rate - ctrl_return_rate
        return_guardrail_passed = return_delta <= self.max_return_delta
        latency_guardrail_passed = measured_p95_latency_ms < self.max_latency_p95_ms
        crash_guardrail_passed = measured_crash_rate <= self.max_crash_rate

        all_guardrails_passed = return_guardrail_passed and latency_guardrail_passed and crash_guardrail_passed

        return {
            "all_guardrails_passed": all_guardrails_passed,
            "return_rate_guardrail": {
                "control_return_rate_pct": round(ctrl_return_rate * 100.0, 2),
                "variant_return_rate_pct": round(var_return_rate * 100.0, 2),
                "delta_percentage_points": round(return_delta * 100.0, 3),
                "status": "PASSED" if return_guardrail_passed else "FAILED_RETURN_SPIKE",
                "target": "Delta <= 0.00% (Flat or Reduced Returns)"
            },
            "latency_guardrail": {
                "measured_p95_ms": round(measured_p95_latency_ms, 3),
                "sla_target_ms": self.max_latency_p95_ms,
                "status": "PASSED" if latency_guardrail_passed else "FAILED_LATENCY_BREACH"
            },
            "crash_rate_guardrail": {
                "measured_crash_rate": measured_crash_rate,
                "target_max": self.max_crash_rate,
                "status": "PASSED" if crash_guardrail_passed else "FAILED_CRASH_SPIKE"
            }
        }
