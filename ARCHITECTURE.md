# ARCHITECTURE.md — AirGuard Decision Engine Architecture

> **Status**: `DRAFT / NOT FINALIZED`
> **Milestone**: M01 — Hackathon Demonstrable MVP
> **Target Platform**: Built on AWS (Environmental Hacks 2026, Air Track)

---

## 1. System Overview

**AirGuard Decision Engine** is a serverless decision-support web application designed to demonstrate transparent, scientifically bounded air-quality scenario comparisons in urban Lucknow (Charbagh Railway Station to Gomti Nagar).

The system implements the **Minimal Serverless Architecture (Candidate 1)**:
* A lightweight static web frontend (HTML5/CSS3/JavaScript + Leaflet via CDN) hosted on Amazon S3 and distributed via Amazon CloudFront.
* A serverless Python/Node.js API hosted on AWS Lambda, providing scenario data, route geometries, and qualitative exposure matrices.
* Zero external runtime database or storage dependencies: the verified historical scenario benchmark is bundled directly inside the Lambda deployment artifact.

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

---

## 2. Architecture Alternatives Evaluated

| Architecture Alternative | Description | Pros | Cons | Decision |
|---|---|---|---|---|
| **Candidate 1: Minimal Serverless** *(Recommended)* | S3 + CloudFront (frontend) + Lambda Function URL / API Gateway (backend) | • Clean separation of client and compute<br>• Fully satisfies "Built on AWS"<br>• Scalable, zero idle server cost | • Requires separate backend and frontend deployments | **SELECTED** |
| **Candidate 2: Static-First Single Bundle** | S3 + CloudFront only; scenario JSON served statically as asset | • Simplest possible deployment<br>• Zero compute costs, zero cold starts | • Lacks backend processing flexibility<br>• Does not demonstrate AWS compute capabilities | *Viable Fallback* |
| **Candidate 3: Multi-Service Pipeline** | CloudFront + S3 + API Gateway + Lambda + DynamoDB + EventBridge | • Supports multi-scenario queries<br>• Supports scheduled periodic jobs | • High operational complexity<br>• Cold start latency<br>• Unnecessary for single benchmark scenario | **REJECTED** |

---

## 3. Least-Privilege IAM & Security Architecture

### Why Lambda Requires ZERO Runtime S3 Access
In many serverless designs, Lambda functions retrieve application fixtures or assets from an S3 bucket at runtime. However, following the **Principle of Least Privilege**:
1. The historical benchmark scenario (`scenario_20261007.json`) and route GeoJSON coordinates are static, immutable artifacts for this prototype.
2. These files are packaged directly inside the Lambda deployment zip artifact under `fixtures/`.
3. At runtime, the Lambda handler reads the benchmark payload directly from the local filesystem (`/var/task/fixtures/...`) with sub-millisecond latency.
4. **Conclusion:** The Lambda execution role requires **zero Amazon S3 permissions (`s3:*`) at runtime**.

### IAM Role Specification

#### Lambda Execution Role (`AirGuardLambdaRole`)
* **Managed Policy Attached:** `AWSLambdaBasicExecutionRole` (`arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole`)
* **Explicit Actions Allowed:**
  * `logs:CreateLogGroup`
  * `logs:CreateLogStream`
  * `logs:PutLogEvents`
* **Resource Restriction:** `arn:aws:logs:*:*:log-group:/aws/lambda/airguard-decision-engine:*`
* **Prohibited Permissions:** No `s3:*`, no `dynamodb:*`, no `secretsmanager:*`, no `kms:*`.

#### S3 Bucket Policy (`AirGuardFrontendBucket`)
* Public access is **blocked** at the bucket level (`BlockPublicAcls: true`, `IgnorePublicAcls: true`, `BlockPublicPolicy: true`, `RestrictPublicBuckets: true`).
* Bucket access is granted exclusively to Amazon CloudFront using **Origin Access Control (OAC)**:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "AllowCloudFrontServicePrincipal",
        "Effect": "Allow",
        "Principal": { "Service": "cloudfront.amazonaws.com" },
        "Action": "s3:GetObject",
        "Resource": "arn:aws:s3:::airguard-frontend-*/*",
        "Condition": {
          "StringEquals": {
            "AWS:SourceArn": "arn:aws:cloudfront::ACCOUNT_ID:distribution/DISTRIBUTION_ID"
          }
        }
      }
    ]
  }
  ```

---

## 4. Cost-Risk Analysis & Free Tier Compliance

### AWS Cost Exposure Assessment
| Service | Free Tier Allowance | Prototype Consumption | Projected Cost |
|---|---|---|---|
| **AWS Lambda** | 1,000,000 free requests/month<br>3.2M seconds compute time | < 5,000 requests during judging | **$0.00** |
| **Amazon S3** | 5 GB Standard Storage<br>20,000 GET Requests | < 5 MB static assets<br>< 5,000 GET requests | **$0.00** |
| **Amazon CloudFront** | 1 TB data transfer out/month<br>10,000,000 HTTP requests | < 500 MB data transfer | **$0.00** |
| **Amazon CloudWatch** | 5 GB log ingestion<br>10 custom metrics | < 50 MB log ingestion | **$0.00** |

### Cost Containment Controls
1. **CloudWatch Log Retention:** Log groups configured with an explicit **1-day retention period** (`RetentionInDays: 1`), preventing indefinite accumulation of log storage.
2. **Billing Alert:** CloudWatch Billing Alarm / AWS Budget set at **$1.00 USD** threshold.
3. **No Unmanaged Daemons:** Zero EC2 instances, zero NAT Gateways, zero always-on VPC endpoints.

---

## 5. Component Breakdown & Local Directory Structure

```
airguard-decision-engine/
├── ARCHITECTURE.md            # System architecture (this document)
├── PROJECT_RULES.md           # GSD methodology rules
├── README.md                  # Project overview, setup, and hackathon submission
├── backend/
│   ├── fixtures/
│   │   ├── scenario_20261007.json   # Verified benchmark readings (7140, 5659, 2456)
│   │   ├── routes.geojson           # Verified route geometries (Route A & Route B)
│   │   └── weather_context.json     # Open-Meteo Oct 7, 2026 20:00 IST weather
│   ├── handler.py                   # AWS Lambda serverless handler / local WSGI app
│   └── tests/
│       ├── test_scenario.py         # Schema, whitelist, and fallback unit tests
│       └── test_routes.py           # Geometry and 50m coverage calculation tests
├── frontend/
│   ├── index.html                   # Semantic HTML5 single-page application
│   ├── css/
│   │   └── style.css                # Clean, responsive styles with accessible contrast
│   └── js/
│       ├── app.js                   # Application state, map rendering, and API fetch
│       └── map_config.js            # Leaflet tile layers, markers, and route styling
└── infra/
    └── template.yaml                # AWS SAM / CloudFormation minimal template
```

---

## 6. Data Flow & Communication Protocol

1. **Client Bootstrapping:** User opens the CloudFront URL. Browser downloads `index.html`, `style.css`, and `app.js`. Leaflet JS/CSS libraries are loaded via CDN with Subresource Integrity (SRI) hashes.
2. **Scenario Data Fetch:** `app.js` issues an asynchronous HTTP GET request to `/api/scenario` (Lambda Function URL or local dev server).
3. **Lambda Execution:**
   - Lambda handler receives the request.
   - Verifies input parameters (if any).
   - Reads bundled `fixtures/scenario_20261007.json` from disk.
   - Appends CORS headers (`Access-Control-Allow-Origin: *`, `Access-Control-Allow-Methods: GET`).
   - Returns HTTP 200 with structured JSON response.
4. **Frontend Rendering:**
   - Map initializes centered on Lucknow (`26.8467° N, 80.9462° E`, zoom level 13).
   - Route A polyline rendered (arterial styling).
   - Route B polyline rendered (bypass styling, dashed across unmonitored Cantonment corridor).
   - Station markers rendered (7140, 5659, 2456) with $1.0\text{ km}$ buffer radius rings.
   - Top banner renders **Mandatory Historical Provenance** notice.
   - Bottom drawer renders **Mandatory Non-Medical Health Disclaimer**.
   - Side panel renders **Corridor Comparison Matrix** with explicit $88.5\%$ unmonitored disclosure.
5. **Fallback Handling:** If the API fetch fails (network partition or backend downtime), the client seamlessly switches to an embedded client-side fallback snapshot with an amber `"OFFLINE / LOCAL FIXTURE MODE"` badge.

---

## 7. Security, Privacy & Integrity Controls

1. **Credential Hygiene:** No API keys, AWS credentials, or secrets exist in the codebase. All historical data is public OpenAQ archive data.
2. **Content Security Policy (CSP):** Frontend specifies CSP meta tags restricting script execution to approved CDNs (Leaflet, CartoDB tiles).
3. **No User PII:** The application does not collect, track, or persist any user location, GPS coordinates, or commuter identity.
4. **Data Integrity:** Stations strictly whitelisted to verified IDs `7140`, `5659`, `2456`. Defunct stations `5604` and `2463` are filtered out.

---

*Last updated: 2026-10-11*
