---
milestone: M01 — Hackathon Demonstrable MVP
version: 0.2.0-draft
updated: 2026-10-11T04:26:00+05:30
---

# ROADMAP.md — AirGuard Decision Engine

> **Current Phase:** Phase 2 — Benchmark Data Fixture & Backend Scenario Engine
> **Phase Status:** 🔄 IN PROGRESS

---

## Must-Haves (from SPEC.md)

- [ ] **MH-1:** Working interactive web map displaying Lucknow corridor, comparing Route A (Hazratganj) and Route B (Cantonment).
- [ ] **MH-2:** Historical benchmark dataset for October 7, 2026 (20:00 IST) covering active stations `7140`, `5659`, and `2456`.
- [ ] **MH-3:** Station 2456 explicitly presented as an external urban/industrial background reference ($3.12\text{ km}$ west of origin), not an origin monitor.
- [ ] **MH-4:** Explicit unmonitored-segment disclosure for Route B ($88.5\%$ unmonitored; zero synthetic data invention).
- [ ] **MH-5:** Mandatory Scenario Playback Banner (`October 7, 2026 20:00 IST`) and persistent Non-Medical Health Disclaimer.
- [ ] **MH-6:** Minimal backend API serving scenario payload with zero runtime S3 permissions.
- [ ] **MH-7:** Automated unit test suite validating schema, station whitelist, and unmonitored flag handling.
- [ ] **MH-8:** Comprehensive README with architecture diagrams, local setup guide, and empirical verification proof.
- [ ] **MH-9:** AWS Cloud deployment (conditional on separate approval and AWS authentication resolution).

---

## Implementation Phases

### Phase 0: Research & Data Feasibility
**Status:** ✅ COMPLETE
**Objective:** Ground data feasibility, determine OpenAQ AWS S3 archive structure, verify historical weather, establish spatial boundaries, and identify live routing constraints.
**Deliverables:** Research paper, audit log in `STATE.md`, DEC-001 through DEC-005.

---

### Phase 1: Requirements Decomposition & Architecture Specification
**Status:** ✅ COMPLETE
**Objective:** Author canonical specification, project roadmap, and architecture design documents under GSD methodology.
**Deliverables:**
- [x] Canonical `.gsd/SPEC.md` (`Status: FINALIZED`)
- [x] Phased `.gsd/ROADMAP.md`
- [x] Architecture document `ARCHITECTURE.md`
- [x] User review and explicit approval received to finalize SPEC

---

### Phase 2: Benchmark Data Fixture & Backend Scenario Engine
**Status:** ✅ COMPLETE
**Objective:** Construct verified benchmark JSON fixtures and implement lightweight serverless API with automated unit tests.
**Depends on:** Phase 1
**Plans:**
- [x] **Plan 2.1:** Create verified scenario fixture (`backend/fixtures/scenario_20261007.json`) bundling Oct 7, 2026 readings (7140, 5659, 2456), route GeoJSON coordinates, Open-Meteo weather context, and provisional 50m densified coverage metrics.
- [x] **Plan 2.2:** Implement lightweight Python backend handler (`backend/handler.py`) providing `GET /api/scenario` and `GET /api/routes` with CORS support and fallback handling.
- [x] **Plan 2.3:** Implement automated unit test suite (`backend/tests/test_scenario.py`) verifying response schema, station whitelisting, unmonitored segment flags, and error responses.

---

### Phase 3: Interactive Frontend Web Application
**Status:** ✅ COMPLETE
**Objective:** Build demonstrable, lightweight web interface with interactive Leaflet map, corridor comparison cards, and ethical guardrail banners.
**Depends on:** Phase 2
**Plans:**
- [x] **Plan 3.1:** Implement core UI layout (`frontend/index.html`, `frontend/style.css`, `frontend/app.js`) with Leaflet CDN, dual route polylines, active station pins, and buffer zones.
- [x] **Plan 3.2:** Implement Mandatory Scenario Playback Banner, Persistent Non-Medical Health Disclaimer, and Qualitative Comparison Matrix displaying the $88.5\%$ unmonitored Cantonment gap.

---

### Phase 4: Local Verification, Testing & Hackathon Packaging
**Status:** ✅ COMPLETE
**Objective:** Execute full test suites, conduct secret scanning, capture visual proof, and author submission-grade documentation.
**Depends on:** Phase 3
**Plans:**
- [x] **Plan 4.1:** Run automated unit tests, malformed input tests, secret scan (GitLeaks/regex check), and capture empirical proof.
- [x] **Plan 4.2:** Capture browser screenshots/recordings of the working UI; author complete `README.md` with setup instructions, architecture diagram, and hackathon judging criteria alignment.

---

### Phase 5: AWS Cloud Deployment (Conditional Separate Gate)
**Status:** ⬜ GATED / AWAITING SEPARATE APPROVAL
**Objective:** Resolve AWS CLI authentication clock skew and deploy serverless stack to AWS for public demo URL.
**Depends on:** Phase 4 + Explicit User Approval + AWS Auth Resolution
**Plans:**
- [ ] **Plan 5.1:** Re-synchronize local system time / refresh AWS credentials to resolve STS `SignatureDoesNotMatch`.
- [ ] **Plan 5.2:** Deploy Lambda function (Function URL or API Gateway) and S3/CloudFront static web assets; verify public HTTPS endpoint.

---

## Progress Summary

| Phase | Status | Plans Completed | Target Completion |
|---|---|---|---|
| **Phase 0: Research & Feasibility** | ✅ COMPLETE | 4/4 | 2026-10-11 |
| **Phase 1: Specification & Architecture** | ✅ COMPLETE | 4/4 | Today |
| **Phase 2: Data Fixture & Backend Engine** | ✅ COMPLETE | 3/3 | Today |
| **Phase 3: Frontend Web Application** | ✅ COMPLETE | 2/2 | Today |
| **Phase 4: Verification & Documentation** | ✅ COMPLETE | 2/2 | Today |
| **Phase 5: Cloud Deployment (Optional Gate)**| ⬜ GATED | 0/2 | Pending Auth Resolution |

---

*Last updated: 2026-10-11*
