import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { getLiveTrainStatus } from '../services/api';
import { filterNearbyTrains } from '../utils/geo';
import { getStationCoordinates, resolveStopCoordinates } from '../utils/stationCoordinates';

export default function LiveRailwayMap({
  trainNumber,
  stationCode,
  trainInfo,
  bottlenecks = [],
  itinerary = [],
  nearbyRadiusKm = 150,
  onLiveTelemetryUpdate
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layerGroupRef = useRef(null);
  const trainMarkerRef = useRef(null);
  const currentStationMarkerRef = useRef(null);

  const [liveData, setLiveData] = useState(null);
  const [loadingLive, setLoadingLive] = useState(false);
  const [liveError, setLiveError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [lastRefreshedAt, setLastRefreshedAt] = useState(null);
  const [showAllStations, setShowAllStations] = useState(true);
  const [showBottlenecks, setShowBottlenecks] = useState(true);

  // Fetch real-time live telemetry if backend/API is available
  const fetchLiveTelemetry = useCallback(async (isManual = false) => {
    if (!trainNumber) return;
    setLoadingLive(true);
    setLiveError(null);
    try {
      const res = await getLiveTrainStatus(trainNumber, null, isManual);
      if (res && res.success && res.data) {
        setLiveData(res);
        setLastRefreshedAt(new Date());
        if (onLiveTelemetryUpdate) {
          onLiveTelemetryUpdate(res.data, trainNumber);
        }
      } else {
        setLiveError(res?.error || "Real-time GPS is offline; showing estimated journey progress");
      }
    } catch (err) {
      setLiveError("Real-time GPS telemetry unavailable; displaying calculated route progression");
    } finally {
      setLoadingLive(false);
    }
  }, [trainNumber, onLiveTelemetryUpdate]);

  // Initial fetch and optional auto-polling
  useEffect(() => {
    fetchLiveTelemetry(false);

    if (!autoRefresh) return;
    const interval = setInterval(() => {
      fetchLiveTelemetry(false);
    }, 45000);

    return () => clearInterval(interval);
  }, [fetchLiveTelemetry, autoRefresh]);

  // Initialize Leaflet Map Instance
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      // Default center across India
      const map = L.map(mapContainerRef.current, {
        center: [23.5937, 82.9629],
        zoom: 5,
        zoomControl: false,
        attributionControl: true,
        scrollWheelZoom: true
      });

      // Top-right Zoom Controls
      L.control.zoom({ position: 'topright' }).addTo(map);

      // OpenStreetMap Real Geographic Tile Layer (100% Free, No Key Required)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors | PredictRail',
        maxZoom: 18,
        minZoom: 4
      }).addTo(map);

      const layers = L.layerGroup().addTo(map);
      layerGroupRef.current = layers;
      mapInstanceRef.current = map;
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Compute resolved stops list with real geographic coordinates
  const processedStops = useMemo(() => {
    const rawStops = trainInfo?.stops || [];
    if (rawStops.length > 0) {
      return rawStops.map((stop, idx) => {
        const coords = resolveStopCoordinates(stop);
        return {
          ...stop,
          sequence: stop.sequence ?? idx + 1,
          station_code: String(stop.station_code || stop.stationCode || '').toUpperCase(),
          station_name: stop.station_name || stop.stationName || stop.station_code,
          lat: coords ? coords[0] : null,
          lon: coords ? coords[1] : null
        };
      });
    }

    // Fallback for default demo journey if raw stops empty: Dibrugarh -> Guwahati -> Kolkata -> New Delhi
    const demoCodes = ['DBRG', 'GHY', 'HWH', 'NDLS'];
    return demoCodes.map((code, idx) => {
      const coords = getStationCoordinates(code);
      const names = {
        'DBRG': 'Dibrugarh',
        'GHY': 'Guwahati',
        'HWH': 'Howrah Jn (Kolkata)',
        'NDLS': 'New Delhi'
      };
      return {
        sequence: idx + 1,
        station_code: code,
        station_name: names[code] || code,
        lat: coords?.lat ?? null,
        lon: coords?.lon ?? null,
        distance_km: idx * 800
      };
    });
  }, [trainInfo]);

  // Determine current station index & station progress
  const currentStationIdx = useMemo(() => {
    if (!stationCode) return 0;
    const cleanCode = String(stationCode).trim().toUpperCase();
    const idx = processedStops.findIndex(s => s.station_code === cleanCode);
    return idx >= 0 ? idx : 0;
  }, [processedStops, stationCode]);

  // Draw Leaflet Map Layers: Markers, Polylines, Progress & Train Location
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layers = layerGroupRef.current;
    if (!map || !layers) return;

    layers.clearLayers();

    const validStops = processedStops.filter(s => s.lat != null && s.lon != null);
    if (validStops.length === 0) return;

    const bottleneckCodes = new Set(bottlenecks.map(b => String(b.station_code).toUpperCase()));

    // 1. Separate coordinates into Completed Track vs Upcoming Track for mint/green styling
    const passedCoords = [];
    const upcomingCoords = [];
    const fullRouteCoords = [];

    validStops.forEach((stop, idx) => {
      const pos = [stop.lat, stop.lon];
      fullRouteCoords.push(pos);
      if (idx <= currentStationIdx) {
        passedCoords.push(pos);
      }
      if (idx >= currentStationIdx) {
        upcomingCoords.push(pos);
      }
    });

    // 2. Draw Polyline Route Tracks (Mint/Green Design)
    // A. Glow Underlay for entire route
    if (fullRouteCoords.length > 1) {
      const glowTrack = L.polyline(fullRouteCoords, {
        color: '#10b981',
        weight: 7,
        opacity: 0.28,
        lineCap: 'round',
        lineJoin: 'round'
      });
      layers.addLayer(glowTrack);
    }

    // B. Completed route segment (Passed stations -> Current station)
    if (passedCoords.length > 1) {
      const completedTrack = L.polyline(passedCoords, {
        color: '#059669', // Emerald completed track
        weight: 4.5,
        opacity: 0.95,
        lineCap: 'round',
        lineJoin: 'round'
      });
      layers.addLayer(completedTrack);
    }

    // C. Upcoming route segment (Current station -> Destination)
    if (upcomingCoords.length > 1) {
      const upcomingTrack = L.polyline(upcomingCoords, {
        color: '#10b981', // Bright mint track
        weight: 4,
        opacity: 0.9,
        dashArray: '8, 8',
        lineCap: 'round',
        lineJoin: 'round'
      });
      layers.addLayer(upcomingTrack);
    }

    // 3. Render Station Markers with Distinct States
    validStops.forEach((stop, idx) => {
      const pos = [stop.lat, stop.lon];
      const isOrigin = idx === 0;
      const isDest = idx === validStops.length - 1;
      const isCurrent = idx === currentStationIdx;
      const isPassed = idx < currentStationIdx;
      const isUpcoming = idx > currentStationIdx && !isDest;
      const isBottleneck = bottleneckCodes.has(stop.station_code);

      // A. Origin Station Marker
      if (isOrigin) {
        const originIcon = L.divIcon({
          className: 'custom-station-pin-icon',
          html: `
            <div class="station-map-pin origin">
              <span class="pin-ring"></span>
              <span class="pin-dot"></span>
              <div class="pin-label">
                <span class="stn-code">${stop.station_code}</span>
                <span class="stn-badge origin">ORIGIN</span>
              </div>
            </div>
          `,
          iconSize: [90, 42],
          iconAnchor: [45, 38]
        });

        const m = L.marker(pos, { icon: originIcon, zIndexOffset: 250 });
        m.bindPopup(`
          <div class="map-popup-card origin-popup">
            <div class="popup-tag origin">JOURNEY ORIGIN</div>
            <h4>${stop.station_name} (${stop.station_code})</h4>
            <p><strong>Status:</strong> Route Starting Station</p>
            ${stop.departure_time ? `<p><strong>Scheduled Departure:</strong> ${stop.departure_time}</p>` : ''}
            <p><strong>Distance from start:</strong> 0 km</p>
          </div>
        `);
        layers.addLayer(m);
      }

      // B. Destination / Terminus Station Marker
      else if (isDest) {
        const destIcon = L.divIcon({
          className: 'custom-station-pin-icon',
          html: `
            <div class="station-map-pin destination">
              <span class="pin-ring dest"></span>
              <span class="pin-dot dest"></span>
              <div class="pin-label dest">
                <span class="stn-code">${stop.station_code}</span>
                <span class="stn-badge dest">DESTINATION</span>
              </div>
            </div>
          `,
          iconSize: [110, 42],
          iconAnchor: [55, 38]
        });

        const m = L.marker(pos, { icon: destIcon, zIndexOffset: 260 });
        m.bindPopup(`
          <div class="map-popup-card dest-popup">
            <div class="popup-tag dest">JOURNEY TERMINUS</div>
            <h4>${stop.station_name} (${stop.station_code})</h4>
            <p><strong>Status:</strong> Final Destination</p>
            ${stop.arrival_time ? `<p><strong>Scheduled Arrival:</strong> ${stop.arrival_time}</p>` : ''}
            ${stop.distance_km ? `<p><strong>Total Route Distance:</strong> ${stop.distance_km} km</p>` : ''}
          </div>
        `);
        layers.addLayer(m);
      }

      // C. Current Observation Station Marker (Pulsing Highlight)
      else if (isCurrent) {
        const currentIcon = L.divIcon({
          className: 'custom-station-pin-icon',
          html: `
            <div class="station-map-pin current">
              <span class="pin-pulse-wave"></span>
              <span class="pin-pulse-dot"></span>
              <div class="pin-label current">
                <span class="stn-code">${stop.station_code}</span>
                <span class="stn-badge current">CURRENT</span>
              </div>
            </div>
          `,
          iconSize: [100, 44],
          iconAnchor: [50, 40]
        });

        const m = L.marker(pos, { icon: currentIcon, zIndexOffset: 400 });
        m.bindPopup(`
          <div class="map-popup-card current-popup">
            <div class="popup-tag current">OBSERVED STATION</div>
            <h4>${stop.station_name} (${stop.station_code})</h4>
            <p><strong>Status:</strong> Current Selected Station</p>
            ${stop.arrival_time ? `<p><strong>Arrival:</strong> ${stop.arrival_time}</p>` : ''}
            ${stop.departure_time ? `<p><strong>Departure:</strong> ${stop.departure_time}</p>` : ''}
            ${stop.distance_km ? `<p><strong>Distance:</strong> ${stop.distance_km} km</p>` : ''}
          </div>
        `);
        layers.addLayer(m);
        currentStationMarkerRef.current = m;
      }

      // D. Passed Stations (Completed Style)
      else if (isPassed) {
        if (showAllStations || isBottleneck) {
          const passedIcon = L.divIcon({
            className: 'custom-passed-node-icon',
            html: `
              <div class="station-node-passed" title="Passed: ${stop.station_name} (${stop.station_code})">
                <span class="node-check">✓</span>
                <span class="node-hover-code">${stop.station_code}</span>
              </div>
            `,
            iconSize: [18, 18],
            iconAnchor: [9, 9]
          });

          const m = L.marker(pos, { icon: passedIcon, zIndexOffset: 120 });
          m.bindTooltip(`<strong>${stop.station_code}</strong>: ${stop.station_name} (Passed)`, {
            direction: 'top',
            offset: [0, -8],
            className: 'station-tooltip-dark'
          });
          m.bindPopup(`
            <div class="map-popup-card passed-popup">
              <div class="popup-tag passed">PASSED HALT</div>
              <h4>${stop.station_name} (${stop.station_code})</h4>
              <p><strong>Status:</strong> Completed segment</p>
              ${stop.departure_time ? `<p><strong>Sch. Dep:</strong> ${stop.departure_time}</p>` : ''}
            </div>
          `);
          layers.addLayer(m);
        }
      }

      // E. Upcoming Stations & Bottleneck Junctions
      else if (isUpcoming) {
        if (isBottleneck && showBottlenecks) {
          const bInfo = bottlenecks.find(b => String(b.station_code).toUpperCase() === stop.station_code);
          const bottleneckIcon = L.divIcon({
            className: 'custom-bottleneck-icon',
            html: `
              <div class="bottleneck-node-marker">
                <span class="hazard-ping"></span>
                <span class="hazard-dot">!</span>
                <span class="hazard-label">${stop.station_code}</span>
              </div>
            `,
            iconSize: [64, 30],
            iconAnchor: [32, 15]
          });

          const m = L.marker(pos, { icon: bottleneckIcon, zIndexOffset: 220 });
          m.bindPopup(`
            <div class="map-popup-card bottleneck-popup">
              <div class="popup-tag junction">⚠ BUSY JUNCTION</div>
              <h4>${stop.station_name} (${stop.station_code})</h4>
              <p><strong>Traffic Congestion:</strong> ${bInfo?.congestion_level || 'Moderate'}</p>
              <p><strong>Junction Delay Risk:</strong> ${bInfo?.bottleneck_score?.toFixed(1) || 'N/A'}/100</p>
            </div>
          `);
          layers.addLayer(m);
        } else if (showAllStations) {
          const upcomingIcon = L.divIcon({
            className: 'custom-upcoming-node-icon',
            html: `
              <div class="station-node-upcoming" title="${stop.station_name} (${stop.station_code})">
                <span class="node-dot"></span>
                <span class="node-hover-code">${stop.station_code}</span>
              </div>
            `,
            iconSize: [16, 16],
            iconAnchor: [8, 8]
          });

          const m = L.marker(pos, { icon: upcomingIcon, zIndexOffset: 150 });
          m.bindTooltip(`<strong>${stop.station_code}</strong>: ${stop.station_name}`, {
            direction: 'top',
            offset: [0, -8],
            className: 'station-tooltip-dark'
          });
          m.bindPopup(`
            <div class="map-popup-card upcoming-popup">
              <div class="popup-tag upcoming">UPCOMING HALT</div>
              <h4>${stop.station_name} (${stop.station_code})</h4>
              ${stop.arrival_time ? `<p><strong>Sch. Arrival:</strong> ${stop.arrival_time}</p>` : ''}
              ${stop.departure_time ? `<p><strong>Sch. Departure:</strong> ${stop.departure_time}</p>` : ''}
            </div>
          `);
          layers.addLayer(m);
        }
      }
    });

    // 4. Render Current / Estimated Train Position Marker
    let trainLat = null;
    let trainLon = null;
    let isLiveGPS = false;
    let trainDelayMinutes = 0;
    let locationDescription = '';

    const liveLoc = liveData?.data?.currentLocation;
    if (liveLoc?.latitude != null && liveLoc?.longitude != null) {
      trainLat = liveLoc.latitude;
      trainLon = liveLoc.longitude;
      isLiveGPS = Boolean(liveData?.data?.isLive);
      trainDelayMinutes = liveLoc.delayMinutes ?? liveData?.data?.delayMinutes ?? 0;
      locationDescription = liveLoc.stationName || liveLoc.stationCode || 'En route';
    } else {
      // Estimated / Demo Location based on current observation station
      const currentStop = validStops[currentStationIdx] || validStops[0];
      if (currentStop) {
        trainLat = currentStop.lat;
        trainLon = currentStop.lon;
        trainDelayMinutes = trainInfo?.current_delay_minutes || 0;
        locationDescription = `${currentStop.station_name} (${currentStop.station_code})`;
      }
    }

    if (trainLat != null && trainLon != null) {
      const statusLabel = isLiveGPS ? 'LIVE GPS' : 'ESTIMATED LOCATION';
      const badgeClass = isLiveGPS ? 'live-gps' : 'estimated-loc';

      const trainIcon = L.divIcon({
        className: 'custom-train-marker-icon',
        html: `
          <div class="train-marker-bubble ${badgeClass}">
            <div class="train-pulse-ring ${badgeClass}"></div>
            <div class="train-icon-body">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <rect width="16" height="16" x="4" y="3" rx="2"></rect>
                <path d="M4 11h16"></path>
                <path d="M12 3v8"></path>
                <path d="m8 19-2 3"></path>
                <path d="m18 22-2-3"></path>
                <circle cx="8" cy="15" r="1"></circle>
                <circle cx="16" cy="15" r="1"></circle>
              </svg>
              <span class="train-num-text">${trainNumber || 'Express'}</span>
              <span class="train-status-chip ${badgeClass}">${statusLabel}</span>
            </div>
          </div>
        `,
        iconSize: [140, 48],
        iconAnchor: [70, 24]
      });

      const trainMarker = L.marker([trainLat, trainLon], { icon: trainIcon, zIndexOffset: 500 });
      trainMarker.bindPopup(`
        <div class="map-popup-card train-loc-popup">
          <div class="popup-tag ${isLiveGPS ? 'live-gps' : 'estimated'}">
            ${isLiveGPS ? '● LIVE GPS SATELLITE TELEMETRY' : '⏱ ESTIMATED DEMO POSITION'}
          </div>
          <h4>${trainInfo?.train_name || `Train ${trainNumber}`}</h4>
          <p><strong>Position:</strong> ${locationDescription}</p>
          <p><strong>Delay Status:</strong> <span style="color: ${trainDelayMinutes > 15 ? 'var(--brand-red)' : '#10b981'}; font-weight: 700;">${trainDelayMinutes > 0 ? `+${trainDelayMinutes} min` : 'On Time'}</span></p>
          <p style="font-size: 0.72rem; color: var(--text-muted); margin-top: 0.45rem; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 0.35rem;">
            ${isLiveGPS ? 'Source: Real-time Live RailRadar telemetry' : 'Calculated from selected observation station and journey progression'}
          </p>
        </div>
      `);
      layers.addLayer(trainMarker);
      trainMarkerRef.current = trainMarker;
    }

    // Auto-fit bounds on initial render or when train route changes
    if (fullRouteCoords.length > 0) {
      map.fitBounds(L.latLngBounds(fullRouteCoords), { padding: [45, 45], maxZoom: 10 });
    }
  }, [processedStops, currentStationIdx, liveData, bottlenecks, showAllStations, showBottlenecks, trainNumber, trainInfo]);

  // Center on current train / observation station
  function handleCenterTrain() {
    if (trainMarkerRef.current && mapInstanceRef.current) {
      const latLng = trainMarkerRef.current.getLatLng();
      mapInstanceRef.current.setView(latLng, 9, { animate: true });
      trainMarkerRef.current.openPopup();
    } else if (currentStationMarkerRef.current && mapInstanceRef.current) {
      const latLng = currentStationMarkerRef.current.getLatLng();
      mapInstanceRef.current.setView(latLng, 9, { animate: true });
      currentStationMarkerRef.current.openPopup();
    }
  }

  // Fit entire railway route
  function handleFitRoute() {
    const valid = processedStops.filter(s => s.lat != null && s.lon != null);
    if (valid.length > 0 && mapInstanceRef.current) {
      const bounds = L.latLngBounds(valid.map(s => [s.lat, s.lon]));
      mapInstanceRef.current.fitBounds(bounds, { padding: [45, 45] });
    }
  }

  const currentStopObj = processedStops[currentStationIdx] || processedStops[0];
  const originStop = processedStops[0];
  const destStop = processedStops[processedStops.length - 1];

  return (
    <div className="card live-map-card">
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexWrap: 'wrap' }}>
          <h3 className="card-title" style={{ margin: 0 }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon>
              <line x1="8" y1="2" x2="8" y2="18"></line>
              <line x1="16" y1="6" x2="16" y2="22"></line>
            </svg>
            Journey Map
          </h3>
          <span className="badge-status green live-gps-pill">
            <span className="live-dot-pulse"></span>
            {liveData?.data?.isLive ? 'LIVE GPS ACTIVE' : 'REAL GEOGRAPHIC MAP'}
          </span>
        </div>

        {/* Map Header Action Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            type="button"
            className="btn-map-control"
            onClick={handleCenterTrain}
            title="Pan to current train / observation station"
            id="btn-locate-train"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"></circle>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
            Locate Train
          </button>

          <button
            type="button"
            className="btn-map-control"
            onClick={handleFitRoute}
            title="Fit full journey corridor in view"
            id="btn-fit-route"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M15 3h6v6"></path>
              <path d="M9 21H3v-6"></path>
              <path d="M21 3l-7 7"></path>
              <path d="M3 21l7-7"></path>
            </svg>
            Fit Route
          </button>

          <button
            type="button"
            className={`btn-map-control ${loadingLive ? 'rotating' : ''}`}
            onClick={() => fetchLiveTelemetry(true)}
            disabled={loadingLive}
            title="Refresh train telemetry"
            id="btn-refresh-map"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"></path>
            </svg>
            {loadingLive ? 'Updating...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Corridor Telemetry Header Strip */}
      <div className="map-telemetry-banner">
        <div className="telemetry-col">
          <span className="telemetry-label">Train Service:</span>
          <span className="telemetry-value highlight">{trainNumber || '12423'} - {trainInfo?.train_name || 'Rajdhani Express'}</span>
        </div>

        <div className="telemetry-col">
          <span className="telemetry-label">Journey Corridor:</span>
          <span className="telemetry-value">
            {originStop?.station_code || 'DBRG'} &rarr; {destStop?.station_code || 'NDLS'}
          </span>
        </div>

        <div className="telemetry-col">
          <span className="telemetry-label">Observed Station:</span>
          <span className="telemetry-value text-green">
            {currentStopObj?.station_name ? `${currentStopObj.station_name} (${currentStopObj.station_code})` : 'En route'}
          </span>
        </div>

        <div className="telemetry-col">
          <span className="telemetry-label">Position Mode:</span>
          <span className="telemetry-value">
            {liveData?.data?.isLive ? 'Real-Time GPS' : 'Estimated Route Progress'}
          </span>
        </div>
      </div>

      {/* Geographic Leaflet Canvas */}
      <div className="leaflet-map-wrapper">
        <div ref={mapContainerRef} className="leaflet-map-canvas" id="journey-leaflet-canvas" />

        {/* Professional Legend Overlay */}
        <div className="map-legend-overlay">
          <div className="legend-item">
            <span className="legend-color-line passed"></span>
            <span>Passed Track</span>
          </div>
          <div className="legend-item">
            <span className="legend-color-line upcoming"></span>
            <span>Upcoming Track</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot current"></span>
            <span>Observed Station</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot destination"></span>
            <span>Terminus</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot bottleneck"></span>
            <span>Busy Junction</span>
          </div>
        </div>
      </div>

      {/* Map Layer Options & Source Footnote */}
      <div className="map-footer">
        <div className="map-layer-toggles">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={showAllStations}
              onChange={(e) => setShowAllStations(e.target.checked)}
            />
            All Station Nodes
          </label>

          <label className="toggle-label">
            <input
              type="checkbox"
              checked={showBottlenecks}
              onChange={(e) => setShowBottlenecks(e.target.checked)}
            />
            Busy Junctions
          </label>

          <label className="toggle-label">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-Refresh (45s)
          </label>
        </div>

        <div className="map-footnote">
          {lastRefreshedAt && `Updated: ${lastRefreshedAt.toLocaleTimeString()} | `}Real Geographic Coordinates &bull; OpenStreetMap &copy;
        </div>
      </div>
    </div>
  );
}
