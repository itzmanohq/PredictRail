import React from 'react';

export default function PassengerRouteTimeline({
  itinerary = [],
  currentStation,
  trainInfo
}) {
  if (!itinerary || itinerary.length === 0) return null;

  return (
    <div className="card passenger-timeline-card">
      <div className="card-header">
        <h3 className="card-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="12" y1="2" x2="12" y2="22"></line>
            <circle cx="12" cy="6" r="3"></circle>
            <circle cx="12" cy="18" r="3"></circle>
          </svg>
          How is the delay affecting my journey? (Stops Ahead)
        </h3>
        <span className="badge-status blue">
          {itinerary.length} STOPS AHEAD
        </span>
      </div>

      <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '0.85rem' }}>
        Track expected arrival times and busy railway junctions along the upcoming route.
      </p>

      <div className="passenger-timeline-list">
        {itinerary.map((stop, idx) => {
          const isNext = idx === 0;
          const isDest = idx === itinerary.length - 1;
          const delayMin = stop.predicted_delay_minutes ?? 0;
          const isBusyJunction = stop.is_bottleneck || stop.congestion_level === 'High' || stop.congestion_level === 'Critical';

          let delayColor = 'text-green';
          if (delayMin > 30) delayColor = 'text-red';
          else if (delayMin > 10) delayColor = 'text-amber';

          return (
            <div
              key={`${stop.station_code}-${idx}`}
              className={`passenger-timeline-item ${isNext ? 'next-stop' : ''} ${isDest ? 'dest-stop' : ''}`}
            >
              <div className="timeline-node-column">
                <span className={`timeline-dot ${isNext ? 'pulse' : ''} ${isDest ? 'dest' : ''}`}></span>
                {idx < itinerary.length - 1 && <span className="timeline-connector"></span>}
              </div>

              <div className="timeline-content-card">
                <div className="timeline-content-header">
                  <div>
                    <strong className="timeline-stn-name">{stop.station_name}</strong>
                    <span className="timeline-stn-code">({stop.station_code})</span>
                    {isNext && <span className="badge-tag next">NEXT STOP</span>}
                    {isDest && <span className="badge-tag dest">DESTINATION</span>}
                    {isBusyJunction && (
                      <span className="badge-tag junction" title="High traffic railway junction where trains may wait for clearance">
                        ⚠ BUSY JUNCTION
                      </span>
                    )}
                  </div>

                  <div className="timeline-times">
                    <span className="timeline-eta">{stop.dynamic_eta || stop.scheduled_arrival || '--:--'}</span>
                    <span className={`timeline-delay ${delayColor}`}>
                      {delayMin > 0 ? `+${Math.round(delayMin)}m late` : 'On Time'}
                    </span>
                  </div>
                </div>

                <div className="timeline-details-sub">
                  <span>Scheduled: {stop.scheduled_arrival || stop.scheduled_departure || 'N/A'}</span>
                  {stop.distance_km != null && <span>Distance: {stop.distance_km} km</span>}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
