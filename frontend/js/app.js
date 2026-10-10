/**
 * AirGuard Decision Engine — Frontend Application Logic
 * Interactive Leaflet Map & Decision-Support Scenario Dashboard
 * Zero external package build dependencies.
 */

(function () {
  'use strict';

  // Application State
  const state = {
    map: null,
    routeALayer: null,
    routeBLayer: null,
    bufferLayers: L.layerGroup(),
    markerLayers: L.layerGroup(),
    scenarioData: null,
    routesData: null,
    isOfflineMode: false
  };

  // Coordinates
  const LUCKNOW_CENTER = [26.8467, 80.9462];
  const CHARBAGH_ORIGIN = [26.8324, 80.9221];
  const GOMTI_NAGAR_DEST = [26.862194, 80.998417];
  const TALKATORA_STATION = [26.833997, 80.891736];

  // Embedded Fallback Fixture (Used if API is unreachable)
  const FALLBACK_SCENARIO = {
    scenario_id: 'lucknow_20261007_2000_ist_client_fallback',
    provenance: {
      timestamp_ist: '2026-10-07T20:00:00+05:30',
      timestamp_utc: '2026-10-07T14:30:00Z',
      data_source: 'OpenAQ v3 Verified Historical Archive',
      mode: 'HISTORICAL_SCENARIO_DEMO',
      live_guidance_supported: false
    },
    stations: [
      {
        id: 7140,
        name: 'Gomti Nagar, Lucknow',
        agency: 'UPPCB',
        coordinates: { latitude: 26.862194, longitude: 80.998417 },
        role: 'DESTINATION_MONITOR',
        readings: { pm25: 13.0, pm10: 27.0, unit: 'µg/m³' }
      },
      {
        id: 5659,
        name: 'Lalbagh, Lucknow',
        agency: 'CPCB',
        coordinates: { latitude: 26.844621, longitude: 80.938804 },
        role: 'ARTERIAL_CORRIDOR_MONITOR',
        readings: { pm25: 43.1, pm10: 94.3, unit: 'µg/m³' }
      },
      {
        id: 2456,
        name: 'Talkatora District Industries Center',
        agency: 'CPCB',
        coordinates: { latitude: 26.833997, longitude: 80.891736 },
        role: 'EXTERNAL_BACKGROUND_MONITOR',
        distance_from_origin_km: 3.12,
        readings: { pm25: 26.96, pm10: 74.0, unit: 'µg/m³' }
      }
    ]
  };

  const FALLBACK_ROUTES = {
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        id: 'route_a_hazratganj',
        properties: {
          id: 'hazratganj_arterial',
          name: 'Route A — Hazratganj Arterial Corridor',
          distance_km: 12.12,
          duration_minutes: 13.0,
          coverage_pct: 28.7,
          unmonitored_pct: 71.3
        },
        geometry: {
          type: 'LineString',
          coordinates: [
            [80.9221, 26.8324], [80.9255, 26.8348], [80.9315, 26.8385],
            [80.9362, 26.843], [80.9412, 26.8481], [80.947, 26.8505],
            [80.9525, 26.852], [80.96, 26.8528], [80.968, 26.8535],
            [80.9765, 26.8552], [80.985, 26.858], [80.992, 26.8602],
            [80.998417, 26.862194]
          ]
        }
      },
      {
        type: 'Feature',
        id: 'route_b_cantonment',
        properties: {
          id: 'cantonment_bypass',
          name: 'Route B — Cantonment Bypass Corridor',
          distance_km: 14.6,
          duration_minutes: 19.5,
          coverage_pct: 11.5,
          unmonitored_pct: 88.5
        },
        geometry: {
          type: 'LineString',
          coordinates: [
            [80.9221, 26.8324], [80.9248, 26.8282], [80.9285, 26.8235],
            [80.935, 26.819], [80.944, 26.816], [80.953, 26.815],
            [80.962, 26.8185], [80.968, 26.824], [80.974, 26.829],
            [80.982, 26.835], [80.989, 26.843], [80.995, 26.851],
            [80.998417, 26.862194]
          ]
        }
      }
    ]
  };

  /**
   * Initializes the Leaflet map and controls.
   */
  function initMap() {
    state.map = L.map('map', {
      center: LUCKNOW_CENTER,
      zoom: 13,
      zoomControl: true
    });

    // Standard OpenStreetMap Tile Layer (Keyless, Open, Community-Governed)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors'
    }).addTo(state.map);

    // Layer groups for toggleable buffers and markers
    state.bufferLayers.addTo(state.map);
    state.markerLayers.addTo(state.map);

    // Origin and Terminus Markers
    const originIcon = L.divIcon({
      className: 'custom-pin pin-origin',
      html: '<div style="background:#0284c7;color:#fff;border:2px solid #fff;border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;box-shadow:0 2px 6px rgba(0,0,0,0.4);">A</div>',
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });

    const destIcon = L.divIcon({
      className: 'custom-pin pin-dest',
      html: '<div style="background:#059669;color:#fff;border:2px solid #fff;border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;box-shadow:0 2px 6px rgba(0,0,0,0.4);">B</div>',
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });

    L.marker(CHARBAGH_ORIGIN, { icon: originIcon })
      .bindPopup('<strong>Trip Origin:</strong> Charbagh Railway Station<br><small>26.8324° N, 80.9221° E</small>')
      .addTo(state.markerLayers);

    L.marker(GOMTI_NAGAR_DEST, { icon: destIcon })
      .bindPopup('<strong>Trip Destination:</strong> Gomti Nagar<br><small>26.8622° N, 80.9984° E</small>')
      .addTo(state.markerLayers);

    // Add Station Markers and 1km Proximity Buffers
    renderStations();

    // Bind Toolbar Buttons
    setupToolbar();
  }

  /**
   * Renders the 3 active stations and their 1km buffers.
   */
  function renderStations() {
    // Station 7140: Gomti Nagar
    const st7140 = [26.862194, 80.998417];
    addStationMarker(
      st7140,
      'Station 7140 — Gomti Nagar (UPPCB)',
      'DESTINATION_MONITOR',
      'Terminus Monitor (~200m from destination)',
      { pm25: 13.0, pm10: 27.0 },
      '#38bdf8'
    );

    // Station 5659: Lalbagh
    const st5659 = [26.844621, 80.938804];
    addStationMarker(
      st5659,
      'Station 5659 — Lalbagh (CPCB)',
      'ARTERIAL_CORRIDOR_MONITOR',
      'Monitors Route A Hazratganj segment (~450m offset)',
      { pm25: 43.1, pm10: 94.3 },
      '#f97316'
    );

    // Station 2456: Talkatora DIC (External Background Reference)
    const st2456 = [26.833997, 80.891736];
    addStationMarker(
      st2456,
      'Station 2456 — Talkatora DIC (CPCB)',
      'EXTERNAL_BACKGROUND_MONITOR',
      'External urban/industrial background reference (3.12 km W of Charbagh). DOES NOT monitor route origin.',
      { pm25: 26.96, pm10: 74.0 },
      '#a855f7',
      true
    );
  }

  /**
   * Helper to add a station marker and its 1km buffer circle.
   */
  function addStationMarker(coords, name, role, note, readings, color, isBackground) {
    // 1 km Buffer Circle
    const bufferCircle = L.circle(coords, {
      radius: 1000,
      color: color,
      weight: 1.5,
      dashArray: '4, 4',
      fillColor: color,
      fillOpacity: 0.12
    });
    state.bufferLayers.addLayer(bufferCircle);

    // Station Marker Pin
    const marker = L.circleMarker(coords, {
      radius: 8,
      color: '#ffffff',
      weight: 2,
      fillColor: color,
      fillOpacity: 1.0
    });

    const popupContent = `
      <div class="station-popup">
        <h4>${name}</h4>
        <p><strong>Role:</strong> ${role}</p>
        <p>${note}</p>
        <div class="popup-readings">
          <strong>PM<sub>2.5</sub>:</strong> ${readings.pm25} µg/m³ &bull;
          <strong>PM<sub>10</sub>:</strong> ${readings.pm10} µg/m³
        </div>
        ${isBackground ? '<div class="popup-warning">⚠️ Notice: Station 2456 is 3.12 km west of Charbagh and does not monitor route origin.</div>' : ''}
      </div>
    `;

    marker.bindPopup(popupContent);
    state.markerLayers.addLayer(marker);
  }

  /**
   * Renders Route A and Route B GeoJSON polylines.
   */
  function renderRoutes(routesGeoJson) {
    if (!routesGeoJson || !routesGeoJson.features) return;

    routesGeoJson.features.forEach((feature) => {
      if (feature.geometry.type !== 'LineString') return;

      const coords = feature.geometry.coordinates.map((c) => [c[1], c[0]]);
      const props = feature.properties || {};

      if (props.id === 'hazratganj_arterial') {
        state.routeALayer = L.polyline(coords, {
          color: '#f97316',
          weight: 5,
          opacity: 0.95
        }).addTo(state.map);

        state.routeALayer.bindPopup(`
          <strong>Route A — Hazratganj Arterial</strong><br>
          Distance: <strong>12.12 km</strong> <small>(Provisional)</small><br>
          Estimated Duration: <strong>~13.0 min</strong> <small>(Free-flow)</small><br>
          Monitoring Coverage: <strong>28.7%</strong>
        `);
      } else if (props.id === 'cantonment_bypass') {
        state.routeBLayer = L.polyline(coords, {
          color: '#22c55e',
          weight: 5,
          dashArray: '8, 8',
          opacity: 0.95
        }).addTo(state.map);

        state.routeBLayer.bindPopup(`
          <strong>Route B — Cantonment Bypass</strong><br>
          Distance: <strong>14.60 km</strong> <small>(Provisional)</small><br>
          Estimated Duration: <strong>~19.5 min</strong> <small>(Free-flow)</small><br>
          Monitoring Coverage: <strong>11.5%</strong><br>
          <span style="color:#ef4444;font-weight:600;">88.5% Unmonitored Transit Gap</span>
        `);
      }
    });
  }

  /**
   * Toolbar button click handlers.
   */
  function setupToolbar() {
    const btnAll = document.getElementById('btn-focus-all');
    const btnA = document.getElementById('btn-focus-route-a');
    const btnB = document.getElementById('btn-focus-route-b');
    const btnBg = document.getElementById('btn-focus-bg');
    const toggleBuffers = document.getElementById('toggle-buffers');

    function setActiveBtn(activeBtn) {
      [btnAll, btnA, btnB, btnBg].forEach((b) => b && b.classList.remove('active'));
      if (activeBtn) activeBtn.classList.add('active');
    }

    if (btnAll) {
      btnAll.addEventListener('click', () => {
        setActiveBtn(btnAll);
        if (state.routeALayer && state.routeBLayer) {
          const group = L.featureGroup([state.routeALayer, state.routeBLayer]);
          state.map.fitBounds(group.getBounds(), { padding: [30, 30] });
        } else {
          state.map.setView(LUCKNOW_CENTER, 13);
        }
      });
    }

    if (btnA) {
      btnA.addEventListener('click', () => {
        setActiveBtn(btnA);
        if (state.routeALayer) {
          state.map.fitBounds(state.routeALayer.getBounds(), { padding: [40, 40] });
        }
      });
    }

    if (btnB) {
      btnB.addEventListener('click', () => {
        setActiveBtn(btnB);
        if (state.routeBLayer) {
          state.map.fitBounds(state.routeBLayer.getBounds(), { padding: [40, 40] });
        }
      });
    }

    if (btnBg) {
      btnBg.addEventListener('click', () => {
        setActiveBtn(btnBg);
        state.map.setView(TALKATORA_STATION, 14);
      });
    }

    if (toggleBuffers) {
      toggleBuffers.addEventListener('change', (e) => {
        if (e.target.checked) {
          state.map.addLayer(state.bufferLayers);
        } else {
          state.map.removeLayer(state.bufferLayers);
        }
      });
    }
  }

  /**
   * Updates the UI status pill.
   */
  function setStatus(isOnline, text) {
    const indicator = document.getElementById('status-indicator');
    const dot = indicator ? indicator.querySelector('.status-dot') : null;
    const label = document.getElementById('status-text');

    if (dot) {
      dot.className = `status-dot ${isOnline ? 'online' : 'offline'}`;
    }
    if (label) {
      label.textContent = text;
    }
  }

  /**
   * Fetches scenario and route data with seamless fallback.
   */
  async function loadData() {
    // Determine API origin
    let apiBase = '';
    if (window.location.protocol === 'file:') {
      apiBase = 'http://127.0.0.1:8000';
    } else if (window.location.port !== '8000') {
      apiBase = 'http://127.0.0.1:8000';
    }

    try {
      setStatus(true, 'Connecting to API...');

      // Attempt to fetch from backend API
      const [scenarioRes, routesRes] = await Promise.all([
        fetch(`${apiBase}/api/scenario`).catch(() => null),
        fetch(`${apiBase}/api/routes`).catch(() => null)
      ]);

      if (scenarioRes && scenarioRes.ok && routesRes && routesRes.ok) {
        state.scenarioData = await scenarioRes.json();
        state.routesData = await routesRes.json();
        state.isOfflineMode = false;
        setStatus(true, 'Online (API Connected)');
      } else {
        throw new Error('Backend endpoints unavailable');
      }
    } catch (err) {
      console.warn('[AirGuard] Live API unreachable; using verified client-side historical benchmark snapshot.', err);
      state.scenarioData = FALLBACK_SCENARIO;
      state.routesData = FALLBACK_ROUTES;
      state.isOfflineMode = true;
      setStatus(false, 'Local Benchmark Snapshot');
    }

    // Render routes on map
    renderRoutes(state.routesData);
  }

  // App Initialization
  document.addEventListener('DOMContentLoaded', () => {
    initMap();
    loadData();
  });

})();
