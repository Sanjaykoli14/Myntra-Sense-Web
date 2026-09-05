"""
Production HTTP REST Server for Myntra Sense Serving Orchestrator.
Exposes endpoints on port 8080.
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from backend.orchestrator.sense_orchestrator import SenseOrchestrator
from backend.api.routes import SenseAPIRoutes

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SenseHTTPServer")

# Global singleton router
orchestrator_instance = SenseOrchestrator()
routes_instance = SenseAPIRoutes(orchestrator_instance)


class SenseHTTPRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, data: dict):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_OPTIONS(self):
        self._send_json(200, {"status": "OK"})

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query_params = parse_qs(parsed.query)
        user_id = query_params.get("user_id", ["USR_10001"])[0]

        if path == "/api/v1/sense/home-picks":
            res = routes_instance.handle_get_home_picks(user_id=user_id)
            self._send_json(200, res)
        elif path.startswith("/api/v1/sense/confidence/"):
            product_id = path.split("/")[-1]
            size = query_params.get("size", [None])[0]
            res = routes_instance.handle_get_confidence(product_id=product_id, user_id=user_id, size=size)
            self._send_json(200, res)
        elif path == "/api/v1/sense/health":
            res = routes_instance.handle_get_health()
            self._send_json(200, res)
        else:
            self._send_json(404, {"error": "Not Found", "path": path})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if path == "/api/v1/sense/compare":
            products = payload.get("products", [])
            user_id = payload.get("user_id", "USR_10001")
            res = routes_instance.handle_post_compare(products=products, user_id=user_id)
            self._send_json(200, res)
        else:
            self._send_json(404, {"error": "Not Found", "path": path})


def start_server(port: int = 8080):
    server = HTTPServer(("0.0.0.0", port), SenseHTTPRequestHandler)
    logger.info(f"🚀 Myntra Sense Orchestrator REST Server listening on http://0.0.0.0:{port}")
    return server


if __name__ == "__main__":
    srv = start_server(8080)
    srv.serve_forever()
