"""
A/B Experiment Configurations and Feature Flags for Myntra Sense.
Defines experiment salts, traffic allocation ratios, and targeting constraints.
"""

from typing import Dict, Any


EXPERIMENT_CONFIG: Dict[str, Any] = {
    "experiment_id": "EXP_MYNTRA_SENSE_WISHLIST_CONV_V1",
    "experiment_name": "Myntra Sense — Wishlist 30-Day Conversion Lift",
    "salt_key": "myntra_sense_salt_2026_q3",
    "rollout_percentage": 50.0,  # 50/50 A/B Test in Phase 5
    "variants": {
        "CONTROL": {
            "name": "Standard Wishlist (Control)",
            "allocation_range": (0.0, 50.0),
            "features_enabled": {
                "sense_home_widget": False,
                "pdp_confidence_dashboard": False,
                "shortlist_comparison_matrix": False
            }
        },
        "VARIANT_SENSE": {
            "name": "Myntra Sense AI Engine (Variant)",
            "allocation_range": (50.0, 100.0),
            "features_enabled": {
                "sense_home_widget": True,
                "pdp_confidence_dashboard": True,
                "shortlist_comparison_matrix": True
            }
        }
    },
    "primary_metric": "30_day_wishlist_to_purchase_conversion_rate",
    "target_conversion_lift": 0.18,  # Target >= 18% lift
    "guardrails": {
        "max_acceptable_return_rate_delta": 0.00,  # Must not increase returns
        "max_p95_serving_latency_ms": 60.0,
        "max_crash_rate": 0.0001
    }
}


def get_experiment_config() -> Dict[str, Any]:
    return EXPERIMENT_CONFIG
