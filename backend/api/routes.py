"""
REST API Route Handlers for Myntra Sense Backend.
"""

from typing import Dict, Any, List, Optional
from backend.orchestrator.sense_orchestrator import SenseOrchestrator


class SenseAPIRoutes:
    def __init__(self, orchestrator: SenseOrchestrator):
        self.orchestrator = orchestrator

    def handle_get_home_picks(self, user_id: str) -> Dict[str, Any]:
        """GET /api/v1/sense/home-picks"""
        return self.orchestrator.get_home_picks(user_id=user_id)

    def handle_get_confidence(self, product_id: str, user_id: str = "USR_10001", size: Optional[str] = None) -> Dict[str, Any]:
        """GET /api/v1/sense/confidence/{productId}"""
        return self.orchestrator.get_product_confidence(product_id=product_id, user_id=user_id, selected_size=size)

    def handle_post_compare(self, products: List[Dict[str, Any]], user_id: str = "USR_10001") -> Dict[str, Any]:
        """POST /api/v1/sense/compare"""
        return self.orchestrator.compare_products(products=products, user_id=user_id)

    def handle_get_health(self) -> Dict[str, Any]:
        """GET /api/v1/sense/health"""
        stats = self.orchestrator.get_orchestrator_latency_stats()
        return {
            "status": "HEALTHY",
            "service": "myntra-sense-orchestrator",
            "telemetry": stats
        }
