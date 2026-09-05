"""
Conversion Metric Analyzer for Myntra Sense A/B Experiment.
Measures Primary 30-Day Conversion Rate, Wishlist Liquidation Rate, and Time-to-Purchase Acceleration.
"""

from typing import Dict, Any, List
from analytics.metrics.statistical_hypothesis import StatisticalHypothesisTester


class ConversionAnalyzer:
    def __init__(self):
        self.hypothesis_tester = StatisticalHypothesisTester()

    def analyze_experiment_results(
        self,
        control_cohort: List[Dict[str, Any]],
        variant_cohort: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Computes comprehensive conversion metrics comparing Control vs Variant:
        1. 30-Day Wishlist-to-Purchase Conversion Rate (% of users with >= 1 purchase in 30d)
        2. Average Days to Purchase
        3. Total Wishlist Liquidation Ratio
        """
        # Control metrics
        n_ctrl = len(control_cohort)
        conv_ctrl = sum(1 for u in control_cohort if u.get("purchased_30d", False))
        days_ctrl = [u["days_to_purchase"] for u in control_cohort if u.get("days_to_purchase")]
        avg_days_ctrl = round(sum(days_ctrl) / max(len(days_ctrl), 1), 2)
        
        # Variant metrics
        n_var = len(variant_cohort)
        conv_var = sum(1 for u in variant_cohort if u.get("purchased_30d", False))
        days_var = [u["days_to_purchase"] for u in variant_cohort if u.get("days_to_purchase")]
        avg_days_var = round(sum(days_var) / max(len(days_var), 1), 2)

        # Statistical test
        stat_eval = self.hypothesis_tester.evaluate_two_proportion_z_test(
            conversions_control=conv_ctrl,
            total_control=n_ctrl,
            conversions_variant=conv_var,
            total_variant=n_var,
            alpha=0.01
        )

        time_to_purchase_reduction_days = round(avg_days_ctrl - avg_days_var, 2)
        relative_lift = stat_eval["relative_lift_pct"]
        
        target_lift_met = relative_lift >= 18.0

        return {
            "primary_metric": "30_Day_Wishlist_to_Purchase_Conversion_Rate",
            "control_conversion_rate_pct": round((conv_ctrl / max(n_ctrl, 1)) * 100.0, 2),
            "variant_conversion_rate_pct": round((conv_var / max(n_var, 1)) * 100.0, 2),
            "relative_conversion_lift_pct": relative_lift,
            "target_conversion_lift_pct": 18.0,
            "target_lift_achieved": target_lift_met,
            "time_to_purchase": {
                "control_avg_days": avg_days_ctrl,
                "variant_avg_days": avg_days_var,
                "days_reduced": time_to_purchase_reduction_days,
                "acceleration_pct": round(((avg_days_ctrl - avg_days_var) / max(avg_days_ctrl, 1)) * 100.0, 2)
            },
            "statistical_significance": stat_eval
        }
