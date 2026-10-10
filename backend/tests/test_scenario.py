"""
AirGuard Decision Engine — Automated Test Suite
Validates benchmark scenario fixture, route contracts, station disambiguation,
least-privilege boundaries, CORS headers, malformed input handling, and fallback resilience.
Standard library unittest (zero third-party dependencies).
"""

import json
import os
import sys
import unittest

# Add backend directory to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from handler import (
    lambda_handler,
    process_request,
    load_fixture,
    ENABLE_LIVE_INGESTION,
    FALLBACK_SCENARIO,
    SCENARIO_FIXTURE_PATH,
    ROUTES_FIXTURE_PATH
)


class TestAirGuardScenarioFixture(unittest.TestCase):
    """Tests the canonical historical benchmark fixture on disk."""

    @classmethod
    def setUpClass(cls):
        with open(SCENARIO_FIXTURE_PATH, "r", encoding="utf-8") as f:
            cls.scenario = json.load(f)

    def test_fixture_provenance_and_scope(self):
        """Verifies scenario ID, timestamp, and historical mode boundaries."""
        self.assertEqual(self.scenario.get("scenario_id"), "lucknow_20261007_2000_ist")
        provenance = self.scenario.get("provenance", {})
        self.assertEqual(provenance.get("timestamp_ist"), "2026-10-07T20:00:00+05:30")
        self.assertEqual(provenance.get("timestamp_utc"), "2026-10-07T14:30:00Z")
        self.assertEqual(provenance.get("mode"), "HISTORICAL_SCENARIO_DEMO")
        self.assertFalse(provenance.get("live_guidance_supported"))
        self.assertIn("latency", provenance.get("ingestion_lag_notice", "").lower())

    def test_station_whitelist_and_exclusion_of_defunct_stations(self):
        """Verifies active station IDs are strictly {7140, 5659, 2456} and defunct stations excluded."""
        stations = self.scenario.get("stations", [])
        station_ids = {s.get("id") for s in stations}
        expected_ids = {7140, 5659, 2456}
        self.assertEqual(station_ids, expected_ids, f"Expected {expected_ids}, got {station_ids}")
        # Explicitly verify defunct stations are excluded
        self.assertNotIn(5604, station_ids, "Defunct station 5604 (Nishant Ganj) must be excluded")
        self.assertNotIn(2463, station_ids, "Defunct station 2463 (Central School) must be excluded")

    def test_station_readings_and_roles(self):
        """Verifies specific pollutant readings and designated roles for each station."""
        stations_by_id = {s["id"]: s for s in self.scenario.get("stations", [])}

        # Station 7140: Gomti Nagar
        st_7140 = stations_by_id[7140]
        self.assertEqual(st_7140["role"], "DESTINATION_MONITOR")
        self.assertEqual(st_7140["readings"]["pm25"], 13.0)
        self.assertEqual(st_7140["readings"]["pm10"], 27.0)

        # Station 5659: Lalbagh
        st_5659 = stations_by_id[5659]
        self.assertEqual(st_5659["role"], "ARTERIAL_CORRIDOR_MONITOR")
        self.assertEqual(st_5659["readings"]["pm25"], 43.1)
        self.assertEqual(st_5659["readings"]["pm10"], 94.3)

        # Station 2456: Talkatora DIC (External background reference, NOT origin monitor)
        st_2456 = stations_by_id[2456]
        self.assertEqual(st_2456["role"], "EXTERNAL_BACKGROUND_MONITOR")
        self.assertEqual(st_2456["distance_from_origin_km"], 3.12)
        self.assertEqual(st_2456["readings"]["pm25"], 26.96)
        self.assertEqual(st_2456["readings"]["pm10"], 74.0)
        self.assertIn("not monitor", st_2456["spatial_relation"].lower())

    def test_cantonment_unmonitored_disclosure(self):
        """Verifies Cantonment corridor is flagged as 88.5% unmonitored with zero synthetic data."""
        routes = self.scenario.get("routes", {})
        route_b = routes.get("route_b", {})
        self.assertEqual(route_b.get("coverage_pct"), 11.5)
        self.assertEqual(route_b.get("unmonitored_pct"), 88.5)
        self.assertIn("unmonitored_disclosure", route_b)
        self.assertIn("88.5%", route_b["unmonitored_disclosure"])

    def test_provisional_metric_status_preserved(self):
        """Verifies route distances and durations are labeled PROVISIONAL, not claimed as verified ground truth."""
        routes = self.scenario.get("routes", {})
        for key in ("route_a", "route_b"):
            route = routes[key]
            self.assertEqual(route.get("distance_status"), "PROVISIONAL")
            self.assertEqual(route.get("coverage_status"), "PROVISIONAL")
            self.assertEqual(route.get("duration_status"), "PROVISIONAL_FREE_FLOW")
            self.assertIn("excluded", route.get("duration_note", "").lower())

    def test_mandatory_health_disclaimer_present(self):
        """Verifies mandatory non-medical disclaimer exists in payload."""
        disclaimer = self.scenario.get("disclaimer", "")
        self.assertTrue(len(disclaimer) > 20)
        self.assertIn("not constitute medical", disclaimer.lower())


class TestAirGuardRoutesGeoJson(unittest.TestCase):
    """Tests the GeoJSON routes fixture."""

    @classmethod
    def setUpClass(cls):
        with open(ROUTES_FIXTURE_PATH, "r", encoding="utf-8") as f:
            cls.geojson = json.load(f)

    def test_geojson_feature_structure(self):
        """Verifies GeoJSON contains LineStrings for Route A and B, plus Points for 3 stations."""
        self.assertEqual(self.geojson.get("type"), "FeatureCollection")
        features = self.geojson.get("features", [])
        feature_ids = {f.get("id") for f in features}
        self.assertIn("route_a_hazratganj", feature_ids)
        self.assertIn("route_b_cantonment", feature_ids)
        self.assertIn("station_7140", feature_ids)
        self.assertIn("station_5659", feature_ids)
        self.assertIn("station_2456", feature_ids)

    def test_route_coordinates_validity(self):
        """Verifies coordinates are valid longitude/latitude pairs within Lucknow bounding box."""
        for feat in self.geojson.get("features", []):
            geom = feat.get("geometry", {})
            coords = geom.get("coordinates", [])
            if geom.get("type") == "LineString":
                self.assertGreater(len(coords), 5, "LineString must have multiple vertices")
                for lon, lat in coords:
                    self.assertTrue(80.80 <= lon <= 81.10, f"Longitude {lon} out of Lucknow bounds")
                    self.assertTrue(26.75 <= lat <= 26.95, f"Latitude {lat} out of Lucknow bounds")
            elif geom.get("type") == "Point":
                lon, lat = coords
                self.assertTrue(80.80 <= lon <= 81.10, f"Station lon {lon} out of bounds")
                self.assertTrue(26.75 <= lat <= 26.95, f"Station lat {lat} out of bounds")


class TestAirGuardBackendHandler(unittest.TestCase):
    """Tests the Lambda / HTTP backend handler logic."""

    def test_health_check_endpoint(self):
        """Verifies /api/health returns healthy status."""
        event = {"rawPath": "/api/health", "requestContext": {"http": {"method": "GET"}}}
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body.get("status"), "healthy")
        self.assertEqual(body.get("service"), "airguard-decision-engine")
        self.assertFalse(body.get("live_ingestion_enabled"))

    def test_get_scenario_endpoint(self):
        """Verifies /api/scenario returns HTTP 200 and scenario payload."""
        event = {"rawPath": "/api/scenario", "requestContext": {"http": {"method": "GET"}}}
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Access-Control-Allow-Origin", response["headers"])
        self.assertEqual(response["headers"]["Access-Control-Allow-Origin"], "*")
        body = json.loads(response["body"])
        self.assertEqual(body.get("scenario_id"), "lucknow_20261007_2000_ist")

    def test_get_routes_endpoint(self):
        """Verifies /api/routes returns HTTP 200 and GeoJSON FeatureCollection."""
        event = {"rawPath": "/api/routes", "requestContext": {"http": {"method": "GET"}}}
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(body.get("type"), "FeatureCollection")
        self.assertEqual(len(body.get("features", [])), 5)

    def test_malformed_query_parameter_returns_400(self):
        """Verifies unrecognized query parameters return HTTP 400 Bad Request."""
        event = {
            "rawPath": "/api/scenario",
            "queryStringParameters": {"malformed_injected_param": "test"},
            "requestContext": {"http": {"method": "GET"}}
        }
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)
        body = json.loads(response["body"])
        self.assertEqual(body.get("error"), "Bad Request")
        self.assertIn("malformed_injected_param", body.get("message"))

    def test_requesting_live_mode_returns_400(self):
        """Verifies attempting to request live mode is blocked with HTTP 400."""
        event = {
            "rawPath": "/api/scenario",
            "queryStringParameters": {"mode": "live"},
            "requestContext": {"http": {"method": "GET"}}
        }
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)
        body = json.loads(response["body"])
        self.assertIn("Feature Disabled", body.get("error"))

    def test_options_cors_preflight(self):
        """Verifies OPTIONS returns HTTP 204 with CORS headers."""
        event = {"rawPath": "/api/scenario", "requestContext": {"http": {"method": "OPTIONS"}}}
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 204)
        self.assertEqual(response["headers"]["Access-Control-Allow-Origin"], "*")

    def test_fallback_resilience(self):
        """Verifies load_fixture returns fallback object when given nonexistent file."""
        fallback = load_fixture("nonexistent_path_xyz.json", FALLBACK_SCENARIO)
        self.assertTrue(fallback.get("fallback"))
        self.assertEqual(len(fallback.get("stations", [])), 3)


if __name__ == "__main__":
    unittest.main()
