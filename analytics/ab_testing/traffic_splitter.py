"""
Deterministic Consistent Hashing Traffic Splitter for Myntra Sense.
Ensures stable user assignment across sessions, mobile apps, and web clients.
"""

import hashlib
from typing import Dict, Any, Tuple
from analytics.ab_testing.experiment_config import EXPERIMENT_CONFIG


class TrafficSplitter:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or EXPERIMENT_CONFIG
        self.salt = self.config.get("salt_key", "default_sense_salt")
        self.variants = self.config.get("variants", {})

    def get_user_hash_bucket(self, user_id: str) -> float:
        """Computes deterministic float bucket in range [0.0, 100.0) for a given user ID."""
        key = f"{self.salt}:{user_id}".encode("utf-8")
        hash_hex = hashlib.md5(key).hexdigest()
        # Take first 8 hex characters and scale to 0.0 - 100.0
        int_val = int(hash_hex[:8], 16)
        bucket = (int_val % 10000) / 100.0
        return round(bucket, 2)

    def assign_variant(
        self,
        user_id: str,
        rollout_percentage: float = 50.0
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Assigns user to 'CONTROL' or 'VARIANT_SENSE' according to rollout ramp.
        If user bucket < rollout_percentage, assign to VARIANT_SENSE, else CONTROL.
        """
        bucket = self.get_user_hash_bucket(user_id)
        
        if bucket < rollout_percentage:
            variant_key = "VARIANT_SENSE"
        else:
            variant_key = "CONTROL"
            
        variant_info = self.variants.get(variant_key, {
            "name": variant_key,
            "features_enabled": {"sense_home_widget": variant_key == "VARIANT_SENSE"}
        })
        
        return variant_key, {
            "user_id": user_id,
            "experiment_id": self.config.get("experiment_id"),
            "variant": variant_key,
            "hash_bucket": bucket,
            "rollout_percentage": rollout_percentage,
            "features": variant_info.get("features_enabled", {})
        }
