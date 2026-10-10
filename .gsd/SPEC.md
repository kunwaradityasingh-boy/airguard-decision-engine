# SPEC.md — Project Specification

> **Status**: `FINALIZED`
> ✅ **Planning Lock Released**: Authorized for implementation.

---

## 1. Vision

**AirGuard Decision Engine** is an environmental decision-support prototype built for the **Environmental Hacks 2026 (Air Track, Built on AWS)**. It provides urban commuters in Lucknow, India with transparent, scientifically grounded scenario comparisons between two primary transit corridors between **Charbagh Railway Station** and **Gomti Nagar**:
1. **Route A (Hazratganj Arterial Corridor):** The traditional urban core transit route.
2. **Route B (Cantonment Bypass Corridor):** The southern green-belt bypass.

The prototype compares monitored ambient air quality observations under a verified historical benchmark snapshot (**October 7, 2026, 19:00:00 to 20:00:00 IST / 14:30:00 UTC**) while explicitly communicating observational coverage, unmonitored segments, and public health boundaries.

---

## 2. Goals & Non-Goals

### Core Goals
1. **Historical Scenario Comparison:** Present side-by-side historical observations of ambient particulate matter ($PM_{2.5}$ and $PM_{10}$) along the two Lucknow transit corridors using verified station readings.
2. **Transparent Monitoring Coverage Disclosures:** Visually and quantitatively delineate monitored versus unmonitored corridor segments using proximity buffers.
3. **Cantonment Corridor Integrity:** Accurately represent the Cantonment corridor as predominantly unmonitored ($88.5\%$ unmonitored under a 1.0 km buffer), applying zero synthetic extrapolation or unvalidated assumptions.
4. **Demonstrable Serverless Architecture:** Provide a lightweight, reliable web application deployable on AWS using least-privilege principles (zero runtime S3 access for compute).
5. **Ethical Communication:** Enforce mandatory scenario provenance banners and non-medical disclaimers; strictly prohibit safety claims.

### Non-Goals (Strictly Out of Scope)
- **Live Real-Time Guidance:** Not supported. Upstream batch ingestion in OpenAQ v3 for Indian regulatory stations exhibits an observed ~80-hour publishing latency, precluding live dispatch.
- **Inhaled Dose / Commuter Exposure Calculations:** Ambient fixed-site monitors do not represent street-level cabin exposure or personal inhalation dosage. Calculating total inhaled pollution is scientifically invalid with available data.
- **Quantitative Overall Route Ranking:** Generating a single synthetic "route score" or labeling one corridor "cleaner" is prohibited. Comparisons are strictly multi-attribute (monitored readings, coverage percentage, unmonitored extent).
- **Synthetic Data Generation:** No Inverse-Distance Weighting (IDW) interpolation or arbitrary traffic reduction multipliers may be applied to unmonitored areas.
- **Medical / Health Safety Advice:** The engine provides relative environmental observations, never medical guarantees, "safe path" designations, or health advice.

---

## 3. Benchmark Dataset & Spatial Grounding

### Verified Historical Snapshot
- **Observation Window:** October 7, 2026, 19:00:00 to 20:00:00 IST (`2026-10-07T14:30:00Z`).
- **Primary Source:** OpenAQ v3 API / AWS S3 OpenAQ Public Archive (`s3://openaq-data-archive/records/csv.gz/locationid={7140,5659,2456}/year=2026/month=10/`).

### Active Station Whitelist
Only three active stations have verified data for the benchmark window:

| Station ID | Name | Operating Agency | Coordinates | Oct 7 2026 20:00 IST Readings | Spatial Role |
|---|---|---|---|---|---|
| **7140** | Gomti Nagar | UPPCB | `26.862194° N, 80.998417° E` | $PM_{2.5}: 13.0\ \mu\text{g/m}^3$<br>$PM_{10}: 27.0\ \mu\text{g/m}^3$ | **Destination Monitor** (Monitors Gomti Nagar endpoint for both routes) |
| **5659** | Lalbagh | CPCB | `26.844621° N, 80.938804° E` | $PM_{2.5}: 43.1\ \mu\text{g/m}^3$<br>$PM_{10}: 94.3\ \mu\text{g/m}^3$ | **Arterial Route Monitor** (Monitors Route A Hazratganj segment) |
| **2456** | Talkatora District Industries Center | CPCB | `26.833997° N, 80.891736° E` | $PM_{2.5}: 26.96\ \mu\text{g/m}^3$<br>$PM_{10}: 74.0\ \mu\text{g/m}^3$ | **External Background Monitor** ($3.12\text{ km}$ W of Charbagh; does NOT monitor origin) |

*Excluded Stations:* Station `5604` (Nishant Ganj) and Station `2463` (Central School) are permanently excluded due to lack of reporting in 2026.

### Station 2456 Spatial Disambiguation
* Station 2456 is located $3.12\text{ km}$ west of Charbagh Railway Station (`26.8324° N, 80.9221° E`).
* It is outside the $1.0\text{ km}$ route corridor buffer.
* **Specification Rule:** The application must identify Station 2456 as an **External Urban/Industrial Background Reference Monitor**, not as an origin monitor.

### Contextual Weather Baseline
- **Source:** Open-Meteo Historical Weather API (Lucknow coordinates `26.85° N, 80.92° E`).
- **Oct 7, 2026 20:00 IST Observation:**
  - Temperature: $24.4^\circ\text{C}$
  - Relative Humidity: $88\%$
  - Wind Speed: $7.4\text{ km/h}$ from $112^\circ$ (East-Southeast)
- **Role:** Displayed strictly as macroscale ambient meteorological context.

---

## 4. Route Corridor Metrics (Provisional Status & Methodology)

> [!IMPORTANT]
> **Provisional Metric Notice:** All route lengths, travel durations, and coverage percentages listed below are **PROVISIONAL ESTIMATES** derived from open routing APIs and 50-meter path densification sampling. They are not verified ground-truth values and will be finalized upon automated verification.

### Route Comparison Summary

| Attribute | Route A (Hazratganj Corridor) | Route B (Cantonment Corridor) | Delta (Route B vs Route A) | Status |
|---|---|---|---|---|
| **Primary Alignment** | Charbagh → Hussainganj → Hazratganj → 1090 Chauraha → Gomti Nagar | Charbagh → Cantt Road → Nehru Road → VIP Road → Gomti Nagar | Southern bypass | Provisional |
| **Route Distance** | $12.12\text{ km}$ | $14.60\text{ km}$ | $+2.48\text{ km}$ ($+20.5\%$) | **PROVISIONAL** |
| **Estimated Duration** | $\approx 13.0\text{ min}$ (Free-Flow) | $\approx 19.5\text{ min}$ (Free-Flow) | $+6.5\text{ min}$ ($+50.0\%$) | **PROVISIONAL** (Traffic excluded) |
| **Monitored Distance (1.0 km Buffer)** | $3.47\text{ km}$ | $1.68\text{ km}$ | $-1.79\text{ km}$ | **PROVISIONAL** |
| **Monitoring Coverage % (1.0 km Buffer)** | **$28.7\%$** | **$11.5\%$** | **$-17.2\%$** | **PROVISIONAL** |
| **Unmonitored Distance % (1.0 km Buffer)** | $71.3\%$ | **$88.5\%$** | $+17.2\%$ | **PROVISIONAL** |
| **Station Proximity** | Station 5659 (Lalbagh, $0.45\text{ km}$)<br>Station 7140 (Gomti Nagar, $0.20\text{ km}$) | Station 7140 (Gomti Nagar, $0.20\text{ km}$ at terminus only) | Zero mid-corridor stations | Verified |

### 50-Meter Sampling Methodology & Limitations
1. **Procedure:** Route polylines are densified into equidistant sample nodes every 50 meters along the path geometry.
2. **Buffer Distance:** For each 50m sample node, distance to the nearest active station is calculated via the Haversine formula.
3. **Threshold:** If nearest station distance $\le 1.0\text{ km}$, the 50m segment is classified as `MONITORED`; otherwise, `UNMONITORED`.
4. **Coverage Calculation:** $\text{Coverage \%} = \frac{\text{Monitored Segment Length}}{\text{Total Route Length}} \times 100$.
5. **Limitations:**
   - Midpoint/node sampling does not account for continuous microscale roadside emission plumes.
   - Fixed Euclidean buffers do not account for urban street canyons, atmospheric dispersion gradients, or building barriers.
   - Travel duration estimates reflect nominal free-flow network speeds and **exclude historical traffic congestion**, which is unavailable for this date.

---

## 5. System Interfaces & Data Contracts

### 5.1 Scenario API Response Schema (`GET /api/scenario`)
```json
{
  "scenario_id": "lucknow_20261007_2000_ist",
  "provenance": {
    "timestamp_ist": "2026-10-07T20:00:00+05:30",
    "timestamp_utc": "2026-10-07T14:30:00Z",
    "data_source": "OpenAQ v3 Verified Historical Archive",
    "mode": "HISTORICAL_SCENARIO_DEMO",
    "live_guidance_supported": false
  },
  "weather_context": {
    "source": "Open-Meteo Historical Weather API",
    "temperature_c": 24.4,
    "relative_humidity_pct": 88,
    "wind_speed_kmh": 7.4,
    "wind_direction_deg": 112,
    "wind_direction_cardinal": "ESE"
  },
  "stations": [
    {
      "id": 7140,
      "name": "Gomti Nagar, Lucknow",
      "agency": "UPPCB",
      "coordinates": [26.862194, 80.998417],
      "role": "DESTINATION_MONITOR",
      "readings": { "pm25": 13.0, "pm10": 27.0, "unit": "µg/m³" }
    },
    {
      "id": 5659,
      "name": "Lalbagh, Lucknow",
      "agency": "CPCB",
      "coordinates": [26.844621, 80.938804],
      "role": "ARTERIAL_CORRIDOR_MONITOR",
      "readings": { "pm25": 43.1, "pm10": 94.3, "unit": "µg/m³" }
    },
    {
      "id": 2456,
      "name": "Talkatora District Industries Center",
      "agency": "CPCB",
      "coordinates": [26.833997, 80.891736],
      "role": "EXTERNAL_BACKGROUND_MONITOR",
      "distance_from_origin_km": 3.12,
      "readings": { "pm25": 26.96, "pm10": 74.0, "unit": "µg/m³" }
    }
  ],
  "routes": {
    "route_a": {
      "id": "hazratganj_arterial",
      "name": "Route A — Hazratganj Arterial",
      "distance_km": 12.12,
      "duration_minutes": 13.0,
      "duration_note": "Model-Estimated Free-Flow Duration (Historical Traffic Excluded)",
      "coverage_pct": 28.7,
      "unmonitored_pct": 71.3,
      "monitored_stations": [5659, 7140],
      "geojson": { "type": "Feature", "geometry": { "type": "LineString", "coordinates": [] } }
    },
    "route_b": {
      "id": "cantonment_bypass",
      "name": "Route B — Cantonment Bypass",
      "distance_km": 14.60,
      "duration_minutes": 19.5,
      "duration_note": "Model-Estimated Free-Flow Duration (Historical Traffic Excluded)",
      "coverage_pct": 11.5,
      "unmonitored_pct": 88.5,
      "monitored_stations": [7140],
      "unmonitored_notice": "88.5% of this corridor has no nearby monitoring stations. Exposure cannot be inferred.",
      "geojson": { "type": "Feature", "geometry": { "type": "LineString", "coordinates": [] } }
    }
  },
  "disclaimer": "This tool is an environmental scenario demonstration for hackathon evaluation. It provides relative ambient particulate observations and does not constitute medical, health, or travel safety advice."
}
```

---

## 6. Mandatory UI Components & Behavioral Guardrails

1. **Scenario Playback Banner (Persistent Top Banner):**
   `"HISTORICAL SCENARIO PLAYBACK — October 7, 2026 20:00 IST | OpenAQ Archive Benchmark | Live Guidance: INACTIVE"`
2. **Mandatory Non-Medical Disclaimer (Persistent Footer / Drawer):**
   `"DISCLAIMER: For environmental hackathon demonstration only. Ambient monitor readings do not reflect commuter cabin exposure. No medical or travel safety claims are made."`
3. **Cantonment Corridor Alert Card:**
   `"UNMONITORED SEGMENT NOTICE: 88.5% of Route B (Cantonment) lacks air-quality monitoring stations. In the absence of validated data, air quality cannot be estimated or assumed to be cleaner."`
4. **Provisional Metric Labels:**
   Every display of route distance, estimated travel time, and coverage percentage must carry a `PROVISIONAL` or `ESTIMATED` badge.

---

## 7. Measurable Acceptance Criteria

| Category | Evaluation Target | Pass / Fail Condition | Current Status |
|---|---|---|---|
| **Unit Tests** | Schema & Whitelist | 100% test pass: verifies station IDs `{7140, 5659, 2456}` present, defunct stations excluded, Cantonment flagged unmonitored. | `PENDING IMPLEMENTATION` |
| **Malformed Input** | API Robustness | Passing invalid parameters to API returns HTTP 400 with structured JSON error; zero uncaught 500 crashes. | `PENDING IMPLEMENTATION` |
| **Backend Fallback** | Resilience | If external/remote API fails, backend gracefully serves bundled fixture with `fallback: true` header/payload. | `PENDING IMPLEMENTATION` |
| **Feature Flags** | Scope Locking | Feature flag `ENABLE_LIVE_INGESTION` defaults to `false`. Historical scenario mode cannot be bypassed. | `PENDING IMPLEMENTATION` |
| **Secret Scanning** | Credential Hygiene | Automated scan of all commits and files confirms 0 API keys or AWS credentials present. | `PENDING IMPLEMENTATION` |
| **Security Audit** | Strix Security Scan | Codebase passes Strix security check, or explicitly marked `NOT VERIFIED` if tool is unavailable. | `NOT VERIFIED` |
| **Attribution** | Data Licenses | OpenAQ (ODbL), OpenStreetMap (ODbL), and Open-Meteo (CC BY 4.0) attribution present in UI and README. | `PENDING IMPLEMENTATION` |
| **AWS Deployment** | Live HTTPS Endpoint | Public CloudFront/S3 frontend and Lambda Function URL return HTTP 200 with valid SSL. Marked `NOT VERIFIED` until auth is fixed and deployment approved. | `NOT VERIFIED` |

---

*Last updated: 2026-10-11*
