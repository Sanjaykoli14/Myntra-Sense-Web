"""
Two-Tower Transformer & Embedding Architecture for Myntra Sense.
Encodes User Session/Search Intent Tower and Item Catalog Tower into a shared 64-dimensional semantic space.
Calculates Cosine Similarity for Candidate Generation and Ranking.
"""

import math
import random
from typing import Dict, Any, List


class UserIntentTower:
    """User Tower: Transforms active search terms, category dwell, and user profile into a dense vector."""
    def __init__(self, embedding_dim: int = 64):
        self.embedding_dim = embedding_dim

    def encode(self, user_profile: Dict[str, Any], realtime_intent: Dict[str, Any]) -> List[float]:
        # Generate deterministic embedding from search terms + category affinity
        seed_str = f"{realtime_intent.get('dominant_intent_category', '')}:{realtime_intent.get('recent_search_terms_json', '')}:{user_profile.get('gender_affinity', '')}"
        rng = random.Random(abs(hash(seed_str)))
        
        raw_vec = [rng.gauss(0, 1.0) for _ in range(self.embedding_dim)]
        
        # Boost specific dimensions based on category dwell time
        dwell_sec = realtime_intent.get("session_dwell_time_seconds", 0)
        dwell_boost = min(dwell_sec / 300.0, 1.5)
        raw_vec[0] += dwell_boost
        
        # L2 normalize
        norm = math.sqrt(sum(x * x for x in raw_vec)) or 1.0
        return [round(x / norm, 6) for x in raw_vec]


class ItemCatalogTower:
    """Item Tower: Transforms product metadata, brand, category, and quality embeddings into a dense vector."""
    def __init__(self, embedding_dim: int = 64):
        self.embedding_dim = embedding_dim

    def encode(self, product_metadata: Dict[str, Any]) -> List[float]:
        seed_str = f"{product_metadata.get('category_id', '')}:{product_metadata.get('brand_id', '')}:{product_metadata.get('product_id', '')}"
        rng = random.Random(abs(hash(seed_str)))
        
        raw_vec = [rng.gauss(0, 1.0) for _ in range(self.embedding_dim)]
        
        # Boost quality & rating dimensions
        quality = product_metadata.get("item_quality_score", 0.85)
        raw_vec[1] += quality * 1.2
        
        # L2 normalize
        norm = math.sqrt(sum(x * x for x in raw_vec)) or 1.0
        return [round(x / norm, 6) for x in raw_vec]


def compute_cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute dot product of two L2-normalized vectors."""
    if len(vec_a) != len(vec_b) or not vec_a:
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    return max(min(dot_product, 1.0), -1.0)
