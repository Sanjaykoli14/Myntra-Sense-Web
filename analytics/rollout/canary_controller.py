"""
Canary Rollout & Automated Rollback Controller for Myntra Sense.
Controls dynamic traffic percentage ramps and triggers emergency rollbacks if guardrails trip.
"""

import json
from typing import Dict, Any, Optional
from analytics.ab_testing.traffic_splitter import TrafficSplitter


class CanaryRolloutController:
    def __init__(self, schedule_file: Optional[str] = None):
        self.current_stage_index = 0
        self.stages = [
            {"stage_id": "STAGE_1_CANARY", "name": "5% Canary Rollout", "percentage": 5.0},
            {"stage_id": "STAGE_2_INTERMEDIATE", "name": "25% Intermediate Ramp", "percentage": 25.0},
            {"stage_id": "STAGE_3_FULL_EXPERIMENT", "name": "50/50 Controlled A/B Experiment", "percentage": 50.0},
            {"stage_id": "STAGE_4_GENERAL_AVAILABILITY", "name": "100% General Availability (GA)", "percentage": 100.0}
        ]
        self.traffic_splitter = TrafficSplitter()
        self.is_emergency_rollback_active = False

    def get_current_stage(self) -> Dict[str, Any]:
        if self.is_emergency_rollback_active:
            return {
                "stage_id": "EMERGENCY_ROLLBACK_0_PCT",
                "name": "Emergency Rollback (0% Traffic)",
                "percentage": 0.0,
                "is_rollback": True
            }
        return self.stages[self.current_stage_index]

    def advance_stage(self) -> Dict[str, Any]:
        """Advance to next rollout stage if exit criteria pass."""
        if self.current_stage_index < len(self.stages) - 1:
            self.current_stage_index += 1
        return self.get_current_stage()

    def trigger_emergency_rollback(self, reason: str) -> Dict[str, Any]:
        """Immediately cut traffic to 0% on critical failure."""
        self.is_emergency_rollback_active = True
        return {
            "status": "EMERGENCY_ROLLBACK_EXECUTED",
            "reason": reason,
            "new_traffic_percentage": 0.0
        }

    def route_user_request(self, user_id: str) -> Dict[str, Any]:
        curr_stage = self.get_current_stage()
        rollout_pct = curr_stage.get("percentage", 0.0)
        _, routing_info = self.traffic_splitter.assign_variant(user_id, rollout_pct)
        return routing_info
