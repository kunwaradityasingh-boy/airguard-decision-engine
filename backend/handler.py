"""
AirGuard Decision Engine — Backend Handler
Provides serverless AWS Lambda handler and standalone local HTTP server.
Zero external package dependencies (Python 3.11+ standard library only).
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Feature Flags
ENABLE_LIVE_INGESTION = False

# Fixtures path resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures")
SCENARIO_FIXTURE_PATH = os.path.join(FIXTURES_DIR, "scenario_20261007.json")
ROUTES_FIXTURE_PATH = os.path.join(FIXTURES_DIR, "routes.geojson")

# Embedded emergency fallback snapshot (ensures resilience if filesystem read fails)
FALLBACK_SCENARIO = {
    "scenario_id": "lucknow_20261007_2000_ist_fallback",
    "fallback": True,
    "provenance": {
        "timestamp_ist": "2026-10-07T20:00:00+05:30",
        "data_source": "OpenAQ v3 Verified Historical Archive (Embedded Fallback)",
        "mode": "HISTORICAL_SCENARIO_DEMO",
        "live_guidance_supported": False
    },
    "stations": [
        {"id": 7140, "name": "Gomti Nagar", "role": "DESTINATION_MONITOR", "readings": {"pm25": 13.0, "pm10": 27.0}},
        {"id": 5659, "name": "Lalbagh", "role": "ARTERIAL_CORRIDOR_MONITOR", "readings": {"pm25": 43.1, "pm10": 94.3}},
        {"id": 2456, "name": "Talkatora DIC", "role": "EXTERNAL_BACKGROUND_MONITOR", "readings": {"pm25": 26.96, "pm10": 74.0}}
    ],
    "disclaimer": "This tool is an environmental scenario demonstration for hackathon evaluation. No medical or health safety claims are made."
}


def load_fixture(filepath: str, fallback_obj: dict) -> dict:
    """Loads a JSON fixture safely from disk with embedded fallback."""
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as exc:
        print(f"[WARN] Error reading fixture {filepath}: {exc}", file=sys.stderr)
    return fallback_obj


def get_cors_headers() -> dict:
    """Returns standard CORS headers."""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Content-Type": "application/json; charset=utf-8"
    }


def process_request(path: str, query_params: dict, http_method: str = "GET") -> tuple[int, dict, dict]:
    """
    Core request router and validator.
    Returns: (status_code, response_data, headers)
    """
    headers = get_cors_headers()

    if http_method == "OPTIONS":
        return 204, {}, headers

    if http_method != "GET":
        return 405, {"error": "Method Not Allowed", "allowed_methods": ["GET", "OPTIONS"]}, headers

    parsed_path = path.rstrip("/") or "/"

    # Health check endpoint
    if parsed_path in ("/health", "/api/health"):
        return 200, {
            "status": "healthy",
            "service": "airguard-decision-engine",
            "mode": "HISTORICAL_SCENARIO",
            "live_ingestion_enabled": ENABLE_LIVE_INGESTION
        }, headers

    # Guard against attempts to request live mode
    if query_params.get("mode", [""])[0].lower() == "live":
        return 400, {
            "error": "Feature Disabled",
            "message": "Live real-time routing is out of scope due to upstream OpenAQ batch latency. Use historical benchmark mode."
        }, headers

    # Validate query parameters against malformed input
    allowed_params = {"format", "route_id", "scenario_id", "mode"}
    invalid_params = set(query_params.keys()) - allowed_params
    if invalid_params:
        return 400, {
            "error": "Bad Request",
            "message": f"Unrecognized query parameter(s): {', '.join(sorted(invalid_params))}",
            "allowed_parameters": sorted(list(allowed_params))
        }, headers

    # Route: GET /api/scenario
    if parsed_path in ("/scenario", "/api/scenario"):
        scenario_data = load_fixture(SCENARIO_FIXTURE_PATH, FALLBACK_SCENARIO)
        scenario_id_param = query_params.get("scenario_id", [None])[0]
        if scenario_id_param is not None:
            expected_id = scenario_data.get("scenario_id", "lucknow_20261007_2000_ist")
            if not scenario_id_param or scenario_id_param != expected_id:
                return 400, {
                    "error": "Bad Request",
                    "message": f"Invalid scenario_id '{scenario_id_param}'. Valid scenario ID: '{expected_id}'.",
                    "valid_scenario_ids": [expected_id]
                }, headers
        return 200, scenario_data, headers

    # Route: GET /api/routes
    if parsed_path in ("/routes", "/api/routes"):
        routes_data = load_fixture(ROUTES_FIXTURE_PATH, {"type": "FeatureCollection", "features": []})
        route_id_filter = query_params.get("route_id", [None])[0]
        if route_id_filter:
            # Filter specific route feature
            filtered_features = [
                f for f in routes_data.get("features", [])
                if f.get("properties", {}).get("id") == route_id_filter or f.get("id") == route_id_filter
            ]
            if not filtered_features:
                return 404, {
                    "error": "Not Found",
                    "message": f"Route '{route_id_filter}' not found. Valid IDs: 'hazratganj_arterial', 'cantonment_bypass'."
                }, headers
            return 200, {"type": "FeatureCollection", "features": filtered_features}, headers
        return 200, routes_data, headers

    # Not found
    return 404, {
        "error": "Not Found",
        "message": f"Endpoint '{parsed_path}' not recognized.",
        "valid_endpoints": ["/api/scenario", "/api/routes", "/api/health"]
    }, headers


# ---------------------------------------------------------------------------
# AWS Lambda Handler
# ---------------------------------------------------------------------------
def lambda_handler(event: dict, context) -> dict:
    """
    AWS Lambda entrypoint.
    Supports API Gateway v1, v2 (HTTP API), and Lambda Function URLs.
    """
    raw_path = event.get("rawPath") or event.get("path") or "/"
    http_method = (
        event.get("requestContext", {}).get("http", {}).get("method")
        or event.get("httpMethod")
        or "GET"
    )
    query_params = event.get("queryStringParameters") or {}
    # Convert query params to dict of lists if strings
    formatted_params = {
        k: [v] if isinstance(v, str) else v
        for k, v in query_params.items()
    } if query_params else {}

    status_code, body, headers = process_request(raw_path, formatted_params, http_method)

    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(body, indent=2 if status_code == 200 else None)
    }


# ---------------------------------------------------------------------------
# Standalone Local HTTP Server (for testing and local demo)
# ---------------------------------------------------------------------------
class LocalRequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        status, body, headers = process_request(self.path, {}, "OPTIONS")
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        query_params = parse_qs(parsed.query, keep_blank_values=True)
        status, body, headers = process_request(parsed.path, query_params, "GET")

        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()

        response_bytes = json.dumps(body, indent=2).encode("utf-8")
        self.wfile.write(response_bytes)

    def _handle_method_not_allowed(self):
        parsed = urlparse(self.path)
        status, body, headers = process_request(parsed.path, {}, self.command)
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            response_bytes = json.dumps(body, indent=2).encode("utf-8")
            self.wfile.write(response_bytes)

    def do_POST(self):
        self._handle_method_not_allowed()

    def do_PUT(self):
        self._handle_method_not_allowed()

    def do_DELETE(self):
        self._handle_method_not_allowed()

    def do_PATCH(self):
        self._handle_method_not_allowed()

    def do_HEAD(self):
        self._handle_method_not_allowed()

    def log_message(self, format, *args):
        # Clean logging
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


def run_local_server(port: int = 8000):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, LocalRequestHandler)
    print(f"AirGuard Decision Engine API running at http://127.0.0.1:{port}/api/scenario")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_local_server(port)
