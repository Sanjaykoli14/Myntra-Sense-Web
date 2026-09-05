"""
Statistical Significance & Hypothesis Testing Engine for Myntra Sense A/B Testing.
Implements Two-Proportion Z-Test, p-value calculations, and 95% Confidence Intervals.
Validates the statistical significance exit criterion (p < 0.01).
"""

import math
from typing import Dict, Any, Tuple


def standard_normal_cdf(x: float) -> float:
    """Cumulative distribution function for standard normal distribution."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


class StatisticalHypothesisTester:
    def evaluate_two_proportion_z_test(
        self,
        conversions_control: int,
        total_control: int,
        conversions_variant: int,
        total_variant: int,
        alpha: float = 0.01
    ) -> Dict[str, Any]:
        """
        Executes two-sample two-tailed Z-test for difference in conversion proportions:
        H0: p_variant == p_control
        H1: p_variant != p_control
        """
        if total_control == 0 or total_variant == 0:
            return {"status": "ERROR", "message": "Sample size cannot be zero"}

        p_ctrl = conversions_control / float(total_control)
        p_var = conversions_variant / float(total_variant)
        
        # Pooled conversion rate
        p_pooled = (conversions_control + conversions_variant) / float(total_control + total_variant)
        
        # Standard error
        se_pooled = math.sqrt(p_pooled * (1.0 - p_pooled) * ((1.0 / total_control) + (1.0 / total_variant)))
        
        if se_pooled == 0:
            z_stat = 0.0
            p_val = 1.0
        else:
            z_stat = (p_var - p_ctrl) / se_pooled
            # Two-tailed p-value
            p_val = 2.0 * (1.0 - standard_normal_cdf(abs(z_stat)))
            
        # Relative lift
        relative_lift = ((p_var - p_ctrl) / p_ctrl) if p_ctrl > 0 else 0.0
        
        # 95% Confidence Interval for the difference
        se_diff = math.sqrt((p_ctrl * (1.0 - p_ctrl) / total_control) + (p_var * (1.0 - p_var) / total_variant))
        ci_95_lower = (p_var - p_ctrl) - (1.96 * se_diff)
        ci_95_upper = (p_var - p_ctrl) + (1.96 * se_diff)

        is_significant = p_val < alpha

        return {
            "control": {
                "sample_size": total_control,
                "conversions": conversions_control,
                "conversion_rate": round(p_ctrl, 4)
            },
            "variant": {
                "sample_size": total_variant,
                "conversions": conversions_variant,
                "conversion_rate": round(p_var, 4)
            },
            "absolute_diff": round(p_var - p_ctrl, 4),
            "relative_lift_pct": round(relative_lift * 100.0, 2),
            "z_statistic": round(z_stat, 4),
            "p_value": round(p_val, 6),
            "alpha_threshold": alpha,
            "statistically_significant": is_significant,
            "confidence_interval_95": {
                "lower": round(ci_95_lower, 4),
                "upper": round(ci_95_upper, 4)
            },
            "sla_exit_criteria_p_sub_0_01": is_significant
        }
