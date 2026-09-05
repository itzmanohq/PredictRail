import React, { useEffect, useRef, useState, useCallback } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { getLiveTrainStatus } from '../services/api';
import { filterNearbyTrains } from '../utils/geo';

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
  const liveMarkerRef = useRef(null);

  const [liveData, setLiveData] = useState(null);
  const [loadingLive, setLoadingLive] = useState(false);
  const [liveError, setLiveError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastRefreshedAt, setLastRefreshedAt] = useState(null);
  const [nearbyCount, setNearbyCount] = useState(0);
  const [mapLayers, setMapLayers] = useState({
    showStations: true,
    showBottlenecks: true,
    showNearby: true
  });

  // Fetch real-time live telemetry from RailRadar backend
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
        setLiveError(res?.error || "Live train location is temporarily unavailable");
      }
    } catch (err) {
      console.warn("RailRadar Live Telemetry error:", err);
      setLiveError("Live train location is temporarily unavailable");
    } finally {
      setLoadingLive(false);
    }
  }, [trainNumber, onLiveTelemetryUpdate]);

  // Initial fetch and auto-polling (every 35s to protect API quota)
  useEffect(() => {
    fetchLiveTelemetry(false);

    if (!autoRefresh) return;
    const interval = setInterval(() => {
      fetchLiveTelemetry(false);
    }, 35000);

    return () => clearInterval(interval);
  }, [fetchLiveTelemetry, autoRefresh]);

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      // Create Leaflet map centered on central India
      const map = L.map(mapContainerRef.current, {
        center: [23.5, 82.5],
        zoom: 5,
        zoomControl: false,
        attributionControl: true
      });

      L.control.zoom({ position: 'topright' }).addTo(map);

      // OpenStreetMap Tile Layer (100% Free, No API key)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | RailRadar Live',
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

  // Update map layers, route polyline, live train marker, and stations
  useEffect(() => {
    const map = mapInstanceRef.current;
    const layers = layerGroupRef.current;
    if (!map || !layers) return;

    layers.clearLayers();

    const stops = trainInfo?.stops || [];
    const routeCoords = [];
    const bottleneckCodes = new Set(bottlenecks.map(b => String(b.station_code).toUpperCase()));

    // 1. Plot Route Stations & Build Polyline
    stops.forEach((stop, idx) => {
      const lat = stop.latitude;
      const lon = stop.longitude;
      if (lat != null && lon != null) {
        const pos = [lat, lon];
        routeCoords.push(pos);

        const isOrigin = idx === 0;
        const isDest = idx === stops.length - 1;
        const isSelectedStation = stop.station_code === stationCode;
        const isBottleneck = bottleneckCodes.has(stop.station_code);

        // Marker for Origin / Destination / Selected observation station
        if (isOrigin || isDest || isSelectedStation) {
          const badgeClass = isOrigin ? 'origin-badge' : (isDest ? 'dest-badge' : 'selected-badge');
          const badgeLabel = isOrigin ? 'ORIGIN' : (isDest ? 'DEST' : 'OBSERVED');
          const markerIcon = L.divIcon({
            className: 'custom-station-icon',
            html: `
              <div class="station-pin-marker ${badgeClass}">
                <div class="station-pin-dot"></div>
                <div class="station-pin-label">${stop.station_code} <span class="pin-tag">${badgeLabel}</span></div>
              </div>
            `,
            iconSize: [80, 36],
            iconAnchor: [40, 36]
          });

          const m = L.marker(pos, { icon: markerIcon, zIndexOffset: 200 });
          m.bindPopup(`
            <div class="map-popup-content">
              <h4>${stop.station_name} (${stop.station_code})</h4>
              <p><strong>Status:</strong> ${badgeLabel}</p>
              ${stop.arrival_time ? `<p><strong>Sch. Arrival:</strong> ${stop.arrival_time}</p>` : ''}
              ${stop.departure_time ? `<p><strong>Sch. Departure:</strong> ${stop.departure_time}</p>` : ''}
              <p><strong>Distance:</strong> ${stop.distance_km} km</p>
            </div>
          `);
          layers.addLayer(m);
        } else if (isBottleneck && mapLayers.showBottlenecks) {
          // Busy Railway Junction Warning Marker
          const bInfo = bottlenecks.find(b => b.station_code === stop.station_code);
          const markerIcon = L.divIcon({
            className: 'custom-bottleneck-icon',
            html: `
              <div class="bottleneck-node-marker">
                <span class="hazard-ping"></span>
                <span class="hazard-dot">!</span>
                <span class="hazard-label">${stop.station_code}</span>
              </div>
            `,
            iconSize: [60, 30],
            iconAnchor: [30, 15]
          });
          const m = L.marker(pos, { icon: markerIcon, zIndexOffset: 250 });
          m.bindPopup(`
            <div class="map-popup-content bottleneck-popup">
              <h4>⚠ Busy Railway Junction: ${stop.station_name} (${stop.station_code})</h4>
              <p><strong>Traffic Level:</strong> ${bInfo?.congestion_level || 'Moderate'}</p>
              <p><strong>Junction Delay Risk:</strong> ${bInfo?.bottleneck_score?.toFixed(1) || 'N/A'}/100</p>
            </div>
          `);
          layers.addLayer(m);
        } else if (mapLayers.showStations) {
          // Regular Intermediate Station Node
          const markerIcon = L.divIcon({
            className: 'custom-node-icon',
            html: `<div class="station-dot" title="${stop.station_name} (${stop.station_code})"></div>`,
            iconSize: [10, 10],
            iconAnchor: [5, 5]
          });
          const m = L.marker(pos, { icon: markerIcon, zIndexOffset: 100 });
          m.bindTooltip(`<strong>${stop.station_code}</strong>: ${stop.station_name}`, { direction: 'top', offset: [0, -5] });
          layers.addLayer(m);
        }
      }
    });

    // 2. Draw Railway Route Polyline
    if (routeCoords.length > 1) {
      // Glow underlay track
      const glowTrack = L.polyline(routeCoords, {
        color: 'var(--brand-red, #e11d48)',
        weight: 6,
        opacity: 0.35,
        lineCap: 'round',
        lineJoin: 'round'
      });
      layers.addLayer(glowTrack);

      // Main high-visibility track line
      const mainTrack = L.polyline(routeCoords, {
        color: '#e11d48',
        weight: 3.5,
        opacity: 0.95,
        dashArray: '8, 6',
        lineCap: 'round',
        lineJoin: 'round'
      });
      layers.addLayer(mainTrack);
    }

    // 3. Live Moving Train Position Marker from RailRadar
    const loc = liveData?.data?.currentLocation;
    const isLive = liveData?.data?.isLive ?? false;
    const trainDelay = loc?.delayMinutes ?? liveData?.data?.delayMinutes ?? 0;
    const liveLat = loc?.latitude;
    const liveLon = loc?.longitude;

    if (liveLat != null && liveLon != null) {
      const delayBadge = trainDelay > 15 
        ? `<span class="train-delay-tag red">+${trainDelay}m</span>` 
        : (trainDelay > 0 ? `<span class="train-delay-tag amber">+${trainDelay}m</span>` : `<span class="train-delay-tag green">ON TIME</span>`);

      const liveTrainIcon = L.divIcon({
        className: 'custom-live-train-icon',
        html: `
          <div class="live-train-marker-wrapper">
            <div class="train-pulse-ring"></div>
            <div class="train-live-badge">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <rect width="16" height="16" x="4" y="3" rx="2"></rect>
                <path d="M4 11h16"></path>
                <path d="M12 3v8"></path>
                <path d="m8 19-2 3"></path>
                <path d="m18 22-2-3"></path>
                <circle cx="8" cy="15" r="1"></circle>
                <circle cx="16" cy="15" r="1"></circle>
              </svg>
              <span>${trainNumber}</span>
              ${delayBadge}
            </div>
          </div>
        `,
        iconSize: [120, 48],
        iconAnchor: [60, 24]
      });

      const trainMarker = L.marker([liveLat, liveLon], { icon: liveTrainIcon, zIndexOffset: 500 });
      trainMarker.bindPopup(`
        <div class="map-popup-content live-popup">
          <div class="live-popup-header">
            <span class="live-indicator-dot"></span>
            <strong>LIVE TRAIN POSITION</strong>
          </div>
          <h4 style="margin: 0.3rem 0; color: #fff;">${liveData.data.trainName || `Train ${trainNumber}`}</h4>
          <p><strong>Current Segment:</strong> ${loc.stationName || loc.stationCode || 'En route'}</p>
          <p><strong>Running Delay:</strong> <span style="color: ${trainDelay > 15 ? 'var(--brand-red)' : '#10b981'}; font-weight: 700;">${trainDelay > 0 ? `+${trainDelay} minutes` : 'On Time'}</span></p>
          <p><strong>Next Halt:</strong> ${liveData.data.nextHalt?.stationName || liveData.data.nextHalt?.stationCode || 'Upcoming'}</p>
          ${loc.distanceFromOriginKm ? `<p><strong>Distance from Origin:</strong> ${loc.distanceFromOriginKm.toFixed(1)} km</p>` : ''}
          <p style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.4rem;">Source: RailRadar Live GPS</p>
        </div>
      `);
      layers.addLayer(trainMarker);
      liveMarkerRef.current = trainMarker;
    }

    // 4. Plot Other Active Network Trains (Filtered by Distance Radius <= nearbyRadiusKm)
    let centerLat = liveLat;
    let centerLon = liveLon;

    if (centerLat == null || centerLon == null) {
      const currentStop = stops.find(s => s.station_code === stationCode);
      if (currentStop && currentStop.latitude != null && currentStop.longitude != null) {
        centerLat = currentStop.latitude;
        centerLon = currentStop.longitude;
      } else if (stops.length > 0 && stops[0].latitude != null && stops[0].longitude != null) {
        centerLat = stops[0].latitude;
        centerLon = stops[0].longitude;
      }
    }

    const filteredNearby = (centerLat != null && centerLon != null && liveData?.nearby_trains)
      ? filterNearbyTrains(liveData.nearby_trains, centerLat, centerLon, nearbyRadiusKm, trainNumber)
      : [];

    setNearbyCount(filteredNearby.length);

    if (mapLayers.showNearby && filteredNearby.length > 0) {
      filteredNearby.forEach((nTrain) => {
        const nIcon = L.divIcon({
          className: 'nearby-train-icon',
          html: `
            <div class="nearby-train-badge" title="${nTrain.train_name} (${nTrain.train_number}) — ${nTrain.distance_km} km away">
              <span class="nearby-dot"></span>
              <span>${nTrain.train_number}</span>
            </div>
          `,
          iconSize: [60, 24],
          iconAnchor: [30, 12]
        });

        const nMarker = L.marker([nTrain.latitude, nTrain.longitude], { icon: nIcon, zIndexOffset: 300 });
        nMarker.bindPopup(`
          <div class="map-popup-content">
            <h4>${nTrain.train_name} (${nTrain.train_number})</h4>
            <p><strong>Distance from selected train:</strong> ${nTrain.distance_km} km</p>
            <p><strong>Near:</strong> ${nTrain.station_name || nTrain.station_code}</p>
            <p><strong>Delay:</strong> ${nTrain.delay_minutes > 0 ? `+${nTrain.delay_minutes} min` : 'On Time'}</p>
          </div>
        `);
        layers.addLayer(nMarker);
      });
    }

    // Auto-fit map to route or live location on initial load / train switch
    if (routeCoords.length > 0) {
      map.fitBounds(L.latLngBounds(routeCoords), { padding: [40, 40], maxZoom: 10 });
    }
  }, [trainInfo, liveData, bottlenecks, stationCode, mapLayers, trainNumber, nearbyRadiusKm]);

  // Center on live train
  function handleCenterLiveTrain() {
    const loc = liveData?.data?.currentLocation;
    if (loc?.latitude != null && loc?.longitude != null && mapInstanceRef.current) {
      mapInstanceRef.current.setView([loc.latitude, loc.longitude], 9, { animate: true });
      if (liveMarkerRef.current) {
        liveMarkerRef.current.openPopup();
      }
    }
  }

  // Fit entire railway route
  function handleFitRoute() {
    const stops = trainInfo?.stops || [];
    const valid = stops.filter(s => s.latitude != null && s.longitude != null);
    if (valid.length > 0 && mapInstanceRef.current) {
      const bounds = L.latLngBounds(valid.map(s => [s.latitude, s.longitude]));
      mapInstanceRef.current.fitBounds(bounds, { padding: [40, 40] });
    }
  }

  const liveLoc = liveData?.data?.currentLocation;
  const currentDelay = liveLoc?.delayMinutes ?? liveData?.data?.delayMinutes ?? null;

  return (
    <div className="card live-map-card">
      <div className="card-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <h3 className="card-title" style={{ margin: 0 }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"></polygon>
              <line x1="8" y1="2" x2="8" y2="18"></line>
              <line x1="16" y1="6" x2="16" y2="22"></line>
            </svg>
            Where is my train? (Live Railway Map)
          </h3>
          {liveData?.data?.isLive ? (
            <span className="badge-status green live-gps-pill">
              <span className="live-dot-pulse"></span> LIVE GPS
            </span>
          ) : (
            <span className="badge-status orange">
              SCHEDULED ROUTE
            </span>
          )}
        </div>

        {/* Map Header Action Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            type="button"
            className="btn-map-control"
            onClick={handleCenterLiveTrain}
            disabled={!liveLoc?.latitude}
            title="Pan to live train marker"
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
            title="Fit full route corridor"
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
            title="Force refresh RailRadar telemetry"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"></path>
            </svg>
            {loadingLive ? 'Updating...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Live Status Bar Banner */}
      <div className="map-telemetry-banner">
        <div className="telemetry-col">
          <span className="telemetry-label">Train Service:</span>
          <span className="telemetry-value highlight">{trainNumber} - {trainInfo?.train_name || 'Express'}</span>
        </div>

        <div className="telemetry-col">
          <span className="telemetry-label">Current Position:</span>
          <span className="telemetry-value">
            {liveLoc?.stationName ? `${liveLoc.stationName} (${liveLoc.stationCode})` : (liveError ? 'Live train location is temporarily unavailable' : 'En route')}
          </span>
        </div>

        <div className="telemetry-col">
          <span className="telemetry-label">Live Delay:</span>
          <span className={`telemetry-value ${currentDelay > 15 ? 'text-red' : (currentDelay > 0 ? 'text-amber' : 'text-green')}`}>
            {currentDelay !== null ? (currentDelay > 0 ? `+${currentDelay} min delay` : 'On Time') : 'N/A'}
          </span>
        </div>

        <div className="telemetry-col">
          <span className="telemetry-label">Next Halt:</span>
          <span className="telemetry-value">
            {liveData?.data?.nextHalt?.stationName ? `${liveData.data.nextHalt.stationName} (${liveData.data.nextHalt.stationCode})` : 'Destination'}
          </span>
        </div>
      </div>

      {/* Live Unavailable Notice if error / offline */}
      {liveError && (
        <div className="live-warning-strip">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <span><strong>Notice:</strong> Live train location is temporarily unavailable. Continuing to show scheduled route and busy junctions.</span>
        </div>
      )}

      {/* Leaflet Map Canvas Container */}
      <div className="leaflet-map-wrapper">
        <div ref={mapContainerRef} className="leaflet-map-canvas" />

        {/* Map Legend Overlay with Simple Plain-English Labels & Distance Radius */}
        <div className="map-legend-overlay">
          <div className="legend-item">
            <span className="legend-color-line track"></span>
            <span>Route Track</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon-badge live"></span>
            <span>Selected Train (GPS)</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon-badge bottleneck"></span>
            <span>Busy Railway Junction</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon-badge nearby"></span>
            <span>
              {nearbyCount > 0 
                ? `Other Live Trains (${nearbyCount} within ${nearbyRadiusKm} km)` 
                : `No nearby live trains found within ${nearbyRadiusKm} km`}
            </span>
          </div>
        </div>
      </div>

      {/* Map Footer Controls & Telemetry Footnote */}
      <div className="map-footer">
        <div className="map-layer-toggles">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={mapLayers.showBottlenecks}
              onChange={(e) => setMapLayers(prev => ({ ...prev, showBottlenecks: e.target.checked }))}
            />
            Busy Junctions
          </label>

          <label className="toggle-label">
            <input
              type="checkbox"
              checked={mapLayers.showNearby}
              onChange={(e) => setMapLayers(prev => ({ ...prev, showNearby: e.target.checked }))}
            />
            Nearby Trains ({nearbyRadiusKm} km)
          </label>

          <label className="toggle-label">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-Refresh (35s)
          </label>
        </div>

        <div className="map-footnote">
          {lastRefreshedAt && `Updated: ${lastRefreshedAt.toLocaleTimeString()}`} | Powered by RailRadar & OpenStreetMap
        </div>
      </div>
    </div>
  );
}
