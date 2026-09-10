import React from 'react';

export default function JourneyOverview({
  data,
  currentStationCode
}) {
  if (!data || !data.train) return null;

  const train = data.train;
  const stops = train.stops || [];
  const itinerary = data.dynamic_eta?.upcoming_itinerary || [];
  const currentStation = currentStationCode || data.dynamic_eta?.current_station || 'GHY';
  const isArrived = Boolean(data.is_arrived || data.train_status === 'ARRIVED');
  const delay = data.delay_prediction?.predicted_delay_minutes ?? data.current_delay_minutes ?? 0;

  // Extract key milestone stations (e.g. Origin, Current, Key Intermediates, Terminus)
  let milestoneStops = [];
  if (stops.length > 0) {
    const curIdx = stops.findIndex(s => s.station_code === currentStation);
    const origin = stops[0];
    const dest = stops[stops.length - 1];
    const current = curIdx >= 0 ? stops[curIdx] : stops[0];

    if (isArrived) {
      milestoneStops = [
        {
          code: origin.station_code,
          name: origin.station_name,
          state: 'Departed',
          time: origin.departure_time || origin.arrival_time,
          badgeClass: 'departed'
        },
        {
          code: dest.station_code,
          name: dest.station_name,
          state: 'Arrived',
          time: dest.arrival_time || 'Completed',
          badgeClass: 'destination'
        }
      ];
    } else {
      // Pick an upcoming milestone in between current and dest if available
      let upcomingMilestone = null;
      if (curIdx >= 0 && curIdx < stops.length - 2) {
        const midIdx = Math.floor((curIdx + stops.length - 1) / 2);
        upcomingMilestone = stops[midIdx];
      } else if (stops.length > 2 && stops[1].station_code !== current.station_code) {
        upcomingMilestone = stops[1];
      }

      milestoneStops = [
        {
          code: origin.station_code,
          name: origin.station_name,
          state: 'Departed',
          time: origin.departure_time || origin.arrival_time,
          badgeClass: 'departed'
        },
        {
          code: current.station_code,
          name: current.station_name,
          state: 'Current',
          time: current.departure_time || current.arrival_time,
          badgeClass: 'current'
        }
      ];

      if (upcomingMilestone && upcomingMilestone.station_code !== dest.station_code && upcomingMilestone.station_code !== current.station_code) {
        milestoneStops.push({
          code: upcomingMilestone.station_code,
          name: upcomingMilestone.station_name,
          state: 'Upcoming',
          time: upcomingMilestone.arrival_time || upcomingMilestone.departure_time,
          badgeClass: 'upcoming'
        });
      }

      if (dest.station_code !== current.station_code) {
        milestoneStops.push({
          code: dest.station_code,
          name: dest.station_name,
          state: 'Destination',
          time: data.dynamic_eta?.destination_dynamic_eta || dest.arrival_time,
          badgeClass: 'destination'
        });
      }
    }
  } else {
    // Default demo journey display: Dibrugarh -> Guwahati -> Kolkata -> New Delhi
    milestoneStops = [
      { code: 'DBRG', name: 'Dibrugarh', state: 'Departed', time: '20:10', badgeClass: 'departed' },
      { code: 'GHY', name: 'Guwahati', state: 'Current', time: '05:35', badgeClass: 'current' },
      { code: 'HWH', name: 'Kolkata (Howrah)', state: 'Upcoming', time: '14:20', badgeClass: 'upcoming' },
      { code: 'NDLS', name: 'New Delhi', state: isArrived ? 'Arrived' : 'Destination', time: isArrived ? '0 min' : '11:29 (Day 3)', badgeClass: 'destination' }
    ];
  }

  return (
    <div className="journey-overview-card card">
      <div className="overview-header">
        <div>
          <span className="overview-subhead">Journey Corridor</span>
          <h3 className="overview-title">
            {train.train_number} · {train.train_name}
          </h3>
        </div>
        <div className="overview-status-badge">
          {isArrived ? (
            <span className="status-pill green">
              ✓ Status: ARRIVED (0 min)
            </span>
          ) : delay > 15 ? (
            <span className="status-pill amber">
              +{Math.round(delay)} min delay
            </span>
          ) : (
            <span className="status-pill green">
              Running on time
            </span>
          )}
        </div>
      </div>

      {/* Compact Milestone Timeline */}
      <div className="milestone-timeline-track">
        {milestoneStops.map((stop, idx) => (
          <div key={`${stop.code}-${idx}`} className={`milestone-step ${stop.badgeClass}`}>
            <div className="step-indicator">
              <div className={`step-dot ${stop.badgeClass}`}>
                {stop.badgeClass === 'departed' && '✓'}
                {stop.badgeClass === 'current' && <span className="current-pulse-ring" />}
                {stop.badgeClass === 'destination' && '★'}
              </div>
              {idx < milestoneStops.length - 1 && <div className={`step-connector ${idx === 0 || isArrived ? 'completed' : ''}`} />}
            </div>
            <div className="step-content">
              <span className={`step-badge ${stop.badgeClass}`}>{stop.state}</span>
              <strong className="step-stn-name">{stop.name}</strong>
              <span className="step-time">{stop.time ? (stop.time.includes(':') ? `Sched: ${stop.time}` : stop.time) : stop.code}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Compact Upcoming Halts List (shown when not arrived) */}
      {!isArrived && itinerary.length > 0 && (
        <div className="upcoming-halts-section">
          <h4 className="halts-section-title">Upcoming Halts ({itinerary.length} Stations Ahead)</h4>
          <div className="halts-grid">
            {itinerary.slice(0, 6).map((halt, i) => (
              <div key={`${halt.station_code}-${i}`} className="halt-chip">
                <span className="halt-dot"></span>
                <span className="halt-code">{halt.station_code}</span>
                <span className="halt-name">{halt.station_name}</span>
                <span className="halt-eta">{halt.dynamic_eta || halt.scheduled_arrival || '--:--'}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
