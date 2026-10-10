# AirGuard Decision Engine 🛡️

> **Environmental Hacks 2026 — Air Track &bull; Built on AWS**
> *A scientifically bounded decision-support prototype evaluating urban particulate exposure and observational monitoring coverage in Lucknow, India.*

[![Built on AWS](https://img.shields.io/badge/AWS-Serverless-orange?logo=amazon-aws)](ARCHITECTURE.md)
[![Data Source: OpenAQ](https://img.shields.io/badge/Data-OpenAQ%20v3%20Archive-blue)](https://openaq.org)
[![Python 3.11](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://python.org)
[![Zero Build Overhead](https://img.shields.io/badge/Frontend-Zero%20Build%20Overhead-green)](#quickstart-run-locally)
[![Tests Passing](https://img.shields.io/badge/Tests-15%2F15%20Passed-brightgreen)](#automated-testing--verification)
[![Secret Scan](https://img.shields.io/badge/Secret%20Scan-Passed%20(0%20leaks)-brightgreen)](#security--credential-hygiene)

---

## 1. Project Overview

Urban commuters navigating heavily populated metropolitan corridors frequently face air quality uncertainty. Commuters often assume that green-belt or peripheral bypasses provide "cleaner air" compared to congested arterial streets, despite an absence of in-situ air quality monitoring.

**AirGuard Decision Engine** provides transparent, evidence-based scenario evaluations for commuters traveling between **Charbagh Railway Station** and **Gomti Nagar** in Lucknow, Uttar Pradesh. Rather than inventing unmonitored pollution readings or generating misleading "safe route" labels, AirGuard:
1. **Compares verified ambient observations:** Evaluates regulatory particulate levels ($PM_{2.5}$ and $PM_{10}$) along **Route A (Hazratganj Arterial Corridor)** and **Route B (Cantonment Bypass Corridor)**.
2. **Exposes monitoring blind spots:** Delineates observational coverage using a 1.0 km proximity buffer, revealing that **$88.5\%$ of the Cantonment green-belt corridor is completely unmonitored**.
3. **Upholds scientific integrity:** Refuses to apply synthetic Inverse-Distance Weighting (IDW) or arbitrary traffic multipliers to unmonitored corridors.
4. **Enforces non-medical boundaries:** Features mandatory scenario playback banners and clear disclaimers that ambient point monitors do not reflect in-cabin vehicular exposure.

---

## 2. Hackathon Track Alignment

### Air Track
* **Tackles Urban Particulate Exposure:** Focuses on $PM_{2.5}$ and $PM_{10}$, the principal airborne health hazards in Indo-Gangetic Plain transit corridors.
* **Exposes Observational Equity & Coverage Gaps:** Proves that perceived green spaces often lack monitoring infrastructure, preventing commuters from making false health assumptions.
* **Open Environmental Data Provenance:** Grounded in regulatory monitoring from the Central Pollution Control Board (CPCB) and Uttar Pradesh Pollution Control Board (UPPCB), accessed via the public OpenAQ archive.

### Built on AWS
* **Minimal Serverless Architecture:** Clean separation of client assets (Amazon S3 + Amazon CloudFront) and serverless compute (AWS Lambda).
* **Least-Privilege Security Design:** Bundles benchmark fixtures directly inside the Lambda deployment artifact, eliminating the need for runtime S3 read/write permissions (`s3:*`). The Lambda execution role uses strictly `AWSLambdaBasicExecutionRole` (CloudWatch Logs only).
* **Cost-Risk Containment:** $0 projected operating costs within the AWS Free Tier, protected by an explicit 1-day CloudWatch log retention policy and a $1.00 USD billing alarm.

---

## 3. Verified Benchmark Scenario Dataset

Due to an observed ~80-hour upstream regulatory publishing lag in OpenAQ v3 for Indian monitoring stations, real-time live routing is out of scope. AirGuard operates on a verified historical benchmark:

* **Observation Window:** **October 7, 2026, 20:00:00 IST (14:30:00 UTC)**.
* **Source:** OpenAQ AWS S3 Public Archive (`s3://openaq-data-archive/records/csv.gz/locationid={7140,5659,2456}/year=2026/month=10/`).

### Active Regulatory Stations Whitelist

| Station ID | Station Name | Operating Agency | Coordinates | Oct 7 2026 20:00 IST Readings | Spatial Role |
|---|---|---|---|---|---|
| **7140** | Gomti Nagar | UPPCB | `26.862194° N, 80.998417° E` | $PM_{2.5}: 13.0\ \mu\text{g/m}^3$<br>$PM_{10}: 27.0\ \mu\text{g/m}^3$ | **Destination Monitor** (Terminus for both routes) |
| **5659** | Lalbagh | CPCB | `26.844621° N, 80.938804° E` | $PM_{2.5}: 43.1\ \mu\text{g/m}^3$<br>$PM_{10}: 94.3\ \mu\text{g/m}^3$ | **Arterial Corridor Monitor** (~450m from Route A) |
| **2456** | Talkatora District Industries Center | CPCB | `26.833997° N, 80.891736° E` | $PM_{2.5}: 26.96\ \mu\text{g/m}^3$<br>$PM_{10}: 74.0\ \mu\text{g/m}^3$ | **External Background Monitor** ($3.12\text{ km}$ W of Charbagh; does NOT monitor origin) |

*Defunct stations `5604` (Nishant Ganj) and `2463` (Central School) are permanently excluded due to zero reporting in 2026.*

### Ambient Weather Baseline (Open-Meteo)
* **Location:** Lucknow (`26.85° N, 80.92° E`) &bull; Oct 7, 2026 20:00 IST
* **Parameters:** Temp: $24.4^\circ\text{C}$, Relative Humidity: $88\%$, Wind: $7.4\text{ km/h}$ from $112^\circ$ (ESE).
* **Role:** Displayed strictly as macroscale ambient meteorological context.

---

## 4. Corridor Scenario Comparison Summary

> [!IMPORTANT]
> **Provisional Metrics Disclosure:** All route lengths, durations, and coverage percentages are **PROVISIONAL ESTIMATES** derived from open routing APIs and 50-meter equidistant polyline sampling.

```
========================================================================================
CORRIDOR ATTRIBUTE             ROUTE A (HAZRATGANJ ARTERIAL)   ROUTE B (CANTONMENT BYPASS)
========================================================================================
Transit Alignment              Charbagh → Hussainganj →         Charbagh → Cantt Road →
                               Hazratganj → Gomti Nagar        Nehru Road → Gomti Nagar
Route Distance (Provisional)   12.12 km                        14.60 km (+2.48 km)
Free-Flow Time (Provisional)   ~13.0 min                       ~19.5 min (+6.5 min)
Traffic Congestion Note        Historical congestion excluded  Historical congestion excluded
Monitored Distance (1km buffer) 3.47 km                         1.68 km (terminus only)
Observational Coverage %       28.7%                           11.5%
Unmonitored Transit Gap        71.3%                           88.5% (CRITICAL GAP)
Nearby Station Readings        Lalbagh: PM2.5 43.1, PM10 94.3  Gomti Nagar: PM2.5 13.0, PM10 27.0
                               Gomti Nagar: PM2.5 13.0, PM10 27.0 (Zero mid-corridor stations)
========================================================================================
```

---

## 5. System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                              USER / CLIENT                             │
│                  (Modern Web Browser / Mobile Browser)                 │
└──────────────┬───────────────────────────────────────────┬─────────────┘
               │ 1. HTTPS GET (HTML, CSS, JS, Assets)      │ 2. HTTPS GET /api/scenario
               ▼                                           ▼
┌───────────────────────────────┐           ┌────────────────────────────┐
│       AMAZON CLOUDFRONT       │           │         AWS LAMBDA         │
│   (CDN Distribution + OAC)    │           │  (Python 3.11 / Node.js)   │
└──────────────┬────────────────┘           │  (Bundled JSON Fixture)    │
               │ Fetch static files         └──────────────┬─────────────┘
               ▼                                           │
┌───────────────────────────────┐                          │ CloudWatch Logs Only
│       AMAZON S3 BUCKET        │                          ▼
│ (Private Static Web Storage)  │           ┌────────────────────────────┐
│ (No Public Write Access)      │           │    AMAZON CLOUDWATCH       │
└───────────────────────────────┘           │ (1-Day Retention Policy)   │
                                            └────────────────────────────┘
```

### Least-Privilege IAM Analysis
* **Why Lambda Requires ZERO Runtime S3 Access:** The historical scenario fixture (`fixtures/scenario_20261007.json`) and route GeoJSON coordinates are packaged directly inside the Lambda deployment bundle. At runtime, the function reads from `/var/task/fixtures/...` with sub-millisecond local disk access.
* **IAM Policy:** The execution role requires strictly `AWSLambdaBasicExecutionRole` (`logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`). No `s3:*` or `dynamodb:*` permissions are granted.
* **S3 Bucket Policy:** All public access is blocked. The bucket is accessible exclusively by CloudFront via Origin Access Control (OAC).

---

## 6. Quickstart: Run Locally

The prototype requires **zero third-party dependencies** (`pip install` is not needed). It runs on standard Python 3.11+ and any modern web browser.

### Step 1: Start the Backend API Server
In your terminal, navigate to the project directory and start the backend service on port 8000:
```powershell
python backend/handler.py 8000
```
*The API is now active at `http://127.0.0.1:8000/api/scenario`.*

### Step 2: Start the Frontend Static Web Server
In a second terminal window, serve the frontend directory on port 3000:
```powershell
python -m http.server 3000 --directory frontend
```

### Step 3: Open the Web Application
Open your browser and navigate to:
```
http://127.0.0.1:3000
```

---

## 7. API Endpoints Reference

The backend provides three RESTful endpoints with CORS enabled (`Access-Control-Allow-Origin: *`):

| Endpoint | Method | Description | Sample Output |
|---|---|---|---|
| `/api/health` | `GET` | Service liveness probe and mode flag | `{"status": "healthy", "mode": "HISTORICAL_SCENARIO"}` |
| `/api/scenario` | `GET` | Complete benchmark dataset, station readings, weather, and route metrics | Returns canonical scenario JSON |
| `/api/routes` | `GET` | GeoJSON FeatureCollection for Route A, Route B, and station points | Returns RFC 7946 GeoJSON FeatureCollection |

---

## 8. Automated Testing & Verification

The test suite validates data schemas, station whitelisting, unmonitored segment flags, CORS headers, malformed input handling, and fallback resilience using Python's built-in `unittest` framework:

```powershell
python -m unittest discover -s backend/tests -p "test_*.py" -v
```

### Verified Test Results (15/15 Passed):
```
test_fallback_resilience ............................................. ok
test_get_routes_endpoint ............................................. ok
test_get_scenario_endpoint ........................................... ok
test_health_check_endpoint ........................................... ok
test_malformed_query_parameter_returns_400 ........................... ok
test_options_cors_preflight .......................................... ok
test_requesting_live_mode_returns_400 ................................. ok
test_geojson_feature_structure ....................................... ok
test_route_coordinates_validity ...................................... ok
test_cantonment_unmonitored_disclosure ................................ ok
test_fixture_provenance_and_scope .................................... ok
test_mandatory_health_disclaimer_present ............................. ok
test_provisional_metric_status_preserved ............................. ok
test_station_readings_and_roles ...................................... ok
test_station_whitelist_and_exclusion_of_defunct_stations ............. ok

----------------------------------------------------------------------
Ran 15 tests in 0.003s — OK
```

---

## 9. Security & Credential Hygiene

* **Automated Secret Scan:** Executed via `scripts/scan_secrets.py`. Scanned 111 repository files for AWS Access Keys (`AKIA...`), private keys, and OpenAQ API keys. **Result: PASS (0 secrets detected)**.
* **Strix Penetration Assessment:** Marked `NOT VERIFIED` (Strix CLI 1.6.2 is installed locally, but full multi-agent pentest was deferred to prevent consuming external API quotas prior to deployment).
* **Zero Hardcoded Secrets:** No API keys or credentials are stored in code, fixtures, or git history.

---

## 10. Submission Checklist & Recommended Screenshots

To complete your hackathon submission today, capture the following 5 screenshots from your browser at `http://127.0.0.1:3000`:

1. **`01_full_dashboard_overview.png`:** Full viewport displaying the top Historical Scenario Banner (`October 7, 2026, 20:00 IST`), green `Online (API Connected)` indicator, corridor map, comparison panel, and persistent health disclaimer.
2. **`02_route_a_hazratganj_focus.png`:** Click **"Route A (Hazratganj)"** on the map toolbar; click the amber polyline to show the interactive popup with $12.12\text{ km}$ (Provisional), $\approx 13.0\text{ min}$ (Free-flow), and $28.7\%$ coverage.
3. **`03_route_b_cantonment_unmonitored_alert.png`:** Click **"Route B (Cantonment)"**; highlight the dashed green polyline, the popup warning, and the golden alert box showing the **`88.5% Unmonitored Transit Corridor Disclosure`**.
4. **`04_station_2456_spatial_separation.png`:** Click **"Station 2456 (Talkatora)"**; capture the view showing Station 2456 positioned $3.12\text{ km}$ west of Charbagh, with its popup explicitly identifying it as an external background monitor that does NOT monitor origin.
5. **`05_cli_test_and_secret_proof.png`:** Terminal screenshot displaying the 15 passing unit tests (`Ran 15 tests in 0.003s — OK`) and the secret scanner output (`Total Files Scanned: 111 — PASS: ZERO hardcoded secrets`).

---

## 11. Limitations & Scientific Boundaries

1. **Ambient Monitors vs. In-Cabin Exposure:** Point measurements from fixed regulatory stations reflect macroscale urban ambient air quality. They do not account for in-vehicle air filtration, tailpipe infiltration, or microscale roadside emission plumes.
2. **Provisional Metric Approximations:** Route distances and coverage percentages are calculated using 50-meter equidistant node sampling and Euclidean station distance. They do not model street canyons or building barriers.
3. **Traffic Congestion Exclusion:** Travel times reflect nominal free-flow network speeds because verified historical traffic congestion data is unavailable for this date.
4. **No Medical / Health Advice:** AirGuard provides relative particulate observations. It makes no medical claims, provides no health certifications, and never designates corridors as "safe" or "healthy".

---

## 12. Data Licensing & Attributions

* **Air Quality Data:** [OpenAQ](https://openaq.org) v3 Historical Archive (Open Database License - ODbL). Regulatory monitors operated by UPPCB and CPCB.
* **Map Data & Imagery:** &copy; [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors (ODbL). Standard keyless tile service.
* **Weather Data:** [Open-Meteo](https://open-meteo.com) Historical Weather API (Creative Commons Attribution 4.0 International - CC BY 4.0).
