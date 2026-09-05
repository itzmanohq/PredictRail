import React from 'react';

export default function RoutePanel({ itinerary = [], currentStation, trainInfo }) {
  if (!itinerary || itinerary.length === 0) return null;

  return (
    <div className="card route-panel">
      <div className="card-header">
        <h3 className="card-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
          </svg>
          Railway Route & Delay Propagation Timeline
        </h3>
        <span className="card-badge">{itinerary.length} STOPS MONITORED</span>
      </div>

      <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        <span>&#128646; Route: <strong>{trainInfo?.source_station}</strong> &rarr; <strong>{trainInfo?.destination_station}</strong></span>
        <span>Corridor Length: <strong>{trainInfo?.route_distance_km} km</strong></span>
      </div>

      {/* Stop Progression List */}
      <div className="route-timeline-container">
        {itinerary.map((stop, index) => {
          const isCurrent = stop.station_code === currentStation || stop.is_current_location;
          const isBottleneck = stop.is_bottleneck || (stop.congestion_level && stop.congestion_level.includes('High'));
          const delayMin = stop.final_weather_adjusted_delay_min != null ? stop.final_weather_adjusted_delay_min : (stop.predicted_delay_min || 0.0);

          let delayColor = 'var(--accent-emerald)';
          if (delayMin > 60.0) delayColor = 'var(--brand-red)';
          else if (delayMin > 15.0) delayColor = 'var(--accent-amber)';

          return (
            <div
              key={`${stop.station_code}-${index}`}
              className={`route-stop-item ${isCurrent ? 'current' : ''} ${isBottleneck ? 'bottleneck' : ''}`}
            >
              <div className="route-stop-seq">
                #{stop.sequence || index + 1}
              </div>

              <div className="route-stop-code">
                {stop.station_code}
              </div>

              <div className="route-stop-name" title={stop.station_name}>
                {stop.station_name}
                {isCurrent && (
                  <span style={{ marginLeft: '0.5rem', fontSize: '0.65rem', background: 'var(--brand-red)', color: '#fff', padding: '0.1rem 0.35rem', borderRadius: '3px', fontWeight: '700' }}>
                    CURRENT
                  </span>
                )}
                {isBottleneck && (
                  <span style={{ marginLeft: '0.4rem', fontSize: '0.65rem', background: 'rgba(245, 158, 11, 0.2)', color: 'var(--accent-amber)', padding: '0.1rem 0.35rem', borderRadius: '3px', fontWeight: '600' }}>
                    JUNCTION BOTTLENECK
                  </span>
                )}
              </div>

              <div className="route-stop-eta">
                Sched: {stop.display_scheduled_time || stop.scheduled_arrival || '--'} &rarr; <strong>ETA: {stop.dynamic_eta_time || '--'}</strong>
              </div>

              <div className="route-stop-delay" style={{ color: delayColor }}>
                +{delayMin.toFixed(0)}m
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
