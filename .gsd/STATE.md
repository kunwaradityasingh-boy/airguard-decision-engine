---
updated: 2026-10-11T04:01:00+05:30
---

# Project State — AirGuard Decision Engine

## Current Position

**Milestone:** M01 — Prototype Development
**Current Phase:** Phase 4 — Local Verification, Testing & Packaging
**Phase 0 Status:** ✅ COMPLETE
**Phase 1 Status:** ✅ COMPLETE (SPEC.md FINALIZED, ROADMAP.md, ARCHITECTURE.md)
**Phase 2 Status:** ✅ COMPLETE (Benchmark Fixture, Backend Handler, 15/15 Tests Passed)
**Phase 3 Status:** ✅ COMPLETE (Interactive Leaflet Map, Provenance Banner, Disclaimers)
**Phase 4 Status:** ✅ COMPLETE (Secret Scan Passed, README.md Published, Tiles Verified)
**Phase 5 Status:** ⬜ GATED (Awaiting AWS Authentication Clock Skew Resolution & User Approval)

---

## Project Scope & Constraints (Phase 0 Baseline)

1. **Project Scope:** **Historical Scenario Prototype** utilizing the verified October 7, 2026 benchmark snapshot (`2026-10-07 19:00:00 to 20:00:00 IST`, timestamp `2026-10-07T20:00:00+05:30` / `2026-10-07T14:30:00Z`).
2. **Live Guidance Boundary:** Live real-time route guidance remains **unsupported and out of scope** for this prototype due to upstream ingestion latency in OpenAQ v3.
3. **Approved Benchmark Stations:** Restrict dataset strictly to verified stations:
   - Station `7140`: Gomti Nagar, Lucknow (UPPCB) — Destination monitor
   - Station `5659`: Lalbagh, Lucknow (CPCB) — Hazratganj arterial route monitor
   - Station `2456`: Talkatora District Industries Center, Lucknow (CPCB) — Origin vicinity monitor
4. **Sensor Disambiguation Rule:** Location objects contain multiple historical hardware sensor IDs; ingestion logic must filter by pollutant (`pm25`, `pm10`), inspect `sensorsId`, and match the latest `datetime.utc` (October 7, 2026), discarding legacy readings from 2018/2022.
5. **Cantonment Corridor Policy:** Cantonment contains zero in-situ monitoring stations and must be represented strictly as an **Unmonitored Transit Segment**. No unvalidated Inverse-Distance Weighting (IDW) interpolation or arbitrary traffic reduction multipliers may be applied.
6. **Provenance & Integrity Requirements:**
   - Mandatory Scenario Playback Banner in UI indicating historical observation window and data age.
   - Mandatory Health Disclaimer stating the tool is an environmental demonstration and provides no medical or health safety guarantees.
   - Restrict language to relative particulate exposure indicators; never use terms like "safe route" or "healthy path".
7. **Credential Security Constraint:** OpenAQ API keys must never be echoed, stored in repository files, committed to git, or hardcoded.

---

## Active Decisions Log

| Decision ID | Summary | Status | Date | Affects |
|---|---|---|---|---|
| DEC-001 | Prototype scoped to Historical Scenario Engine (Oct 7, 2026 benchmark) | Approved | 2026-10-11 | Phase 1, Phase 2, All Routing |
| DEC-002 | Station whitelist locked to IDs 7140, 5659, 2456; exclude defunct stations | Approved | 2026-10-11 | Ingestion, Scenario Dataset |
| DEC-003 | Cantonment corridor represented as unmonitored; no IDW or arbitrary heuristics | Approved | 2026-10-11 | UI, Exposure Model |
| DEC-004 | Mandatory provenance banner and health disclaimer; no medical claims | Approved | 2026-10-11 | UI, Documentation |
| DEC-005 | API key security: local machine environment only, never in repo | Approved | 2026-10-11 | Architecture, Dev Setup |

---

## Blockers & Concerns

- **Blockers:** None currently blocking Phase 1 planning.
- **Concerns:**
  - Microscale exposure vs. macroscale ambient monitor readings remains an unverified gap to be highlighted in project documentation.
  - Route graph must handle unmonitored segments without assigning synthetic sensor values.

---

## Next Steps

1. Await explicit user approval to commence Phase 1.
2. In Phase 1: Author requirements decomposition and architecture specification (`SPEC.md` / `ARCHITECTURE.md`).
