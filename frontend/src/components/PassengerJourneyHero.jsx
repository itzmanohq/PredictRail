import React from 'react';

export default function PassengerJourneyHero({
  trainData,
  delayData,
  etaData,
  recData,
  weatherData,
  currentParams
}) {
  if (!trainData) return null;

  const trainNumber = trainData.train_number || currentParams?.trainNumber;
  const trainName = trainData.train_name || 'Indian Railways Express';
  const sourceStation = trainData.source_name || trainData.source_station;
  const destinationStation = trainData.destination_name || trainData.destination_station;

  // Current Location
  const currentLocation = etaData?.current_station_name 
    ? `${etaData.current_station_name} (${etaData.current_station || currentParams?.stationCode})`
    : (currentParams?.stationCode || 'En route');

  // Next Station
  const itinerary = etaData?.upcoming_itinerary || [];
  let nextStationName = 'Approaching Terminus';
  let nextStationCode = '';
  let nextStationEta = '';

  if (itinerary.length > 1) {
    nextStationName = itinerary[1].station_name;
    nextStationCode = itinerary[1].station_code;
    nextStationEta = itinerary[1].dynamic_eta || itinerary[1].scheduled_arrival || '';
  } else if (itinerary.length === 1 && !itinerary[0].is_current_location) {
    nextStationName = itinerary[0].station_name;
    nextStationCode = itinerary[0].station_code;
    nextStationEta = itinerary[0].dynamic_eta || itinerary[0].scheduled_arrival || '';
  }

  // How late is my train?
  const predictedDelay = delayData?.predicted_delay_minutes ?? currentParams?.currentDelay ?? 0.0;
  const isHeavyDelay = predictedDelay > 45.0;

  // When will I reach?
  const expectedTime = etaData?.destination_dynamic_eta || 'Calculating...';

  // Less crowded coach
  const recClass = recData?.recommended_coach_or_class || '2A';
  const recCoachId = recData?.recommended_coach_id || `${recClass}1`;
  const recClassName = recData?.recommended_class_name || `Class ${recClass}`;

  // Weather summary
  const weatherAdj = weatherData?.weather_delay_adjustment_min || 0;
  const weatherIsImpacted = weatherAdj > 5.0;

  return (
    <section className="passenger-journey-hero card">
      <div className="journey-hero-top">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
            <span className="badge-tag" style={{ background: 'rgba(59, 130, 246, 0.2)', color: '#93c5fd', border: '1px solid #3b82f6', letterSpacing: '0.05em' }}>
              YOUR JOURNEY SUMMARY
            </span>
            <span className="journey-route-pill">
              {sourceStation} → {destinationStation}
            </span>
          </div>
          <h1 className="journey-train-title">
            <span className="train-pill-number">{trainNumber}</span> {trainName}
          </h1>
        </div>

        <div className="journey-status-tag">
          {predictedDelay <= 10.0 ? (
            <span className="badge-status green large">
              <span className="live-dot-pulse"></span> RUNNING ON TIME
            </span>
          ) : (
            <span className={`badge-status ${isHeavyDelay ? 'red' : 'orange'} large`}>
              ⏱ RUNNING {Math.round(predictedDelay)} MIN LATE
            </span>
          )}
        </div>
      </div>

      {/* 5-Second Journey Highlights Grid (6 Cards) */}
      <div className="journey-highlights-grid">
        {/* 1. How late is my train? */}
        <div className="journey-highlight-card">
          <div className="card-icon-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            <span className="highlight-card-title">How late is my train?</span>
          </div>
          <div className={`highlight-main-val ${predictedDelay > 45 ? 'text-red' : (predictedDelay > 10 ? 'text-amber' : 'text-green')}`}>
            {predictedDelay <= 10 ? 'On Time' : `+${Math.round(predictedDelay)} mins`}
          </div>
          <p className="highlight-subtitle">
            {predictedDelay <= 10 ? 'No major delay expected' : 'Expected delay along your journey'}
          </p>
        </div>

        {/* 2. Current Location */}
        <div className="journey-highlight-card">
          <div className="card-icon-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z"></path>
              <circle cx="12" cy="10" r="3"></circle>
            </svg>
            <span className="highlight-card-title">Current Location</span>
          </div>
          <div className="highlight-main-val" style={{ fontSize: '1.25rem', color: '#ffffff' }}>
            {currentLocation}
          </div>
          <p className="highlight-subtitle">
            Reported observation station
          </p>
        </div>

        {/* 3. Next Station */}
        <div className="journey-highlight-card">
          <div className="card-icon-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
            <span className="highlight-card-title">Next Station</span>
          </div>
          <div className="highlight-main-val text-green" style={{ fontSize: '1.25rem' }}>
            {nextStationName} {nextStationCode ? `(${nextStationCode})` : ''}
          </div>
          <p className="highlight-subtitle">
            {nextStationEta ? `Expected at ${nextStationEta}` : 'Upcoming scheduled halt'}
          </p>
        </div>

        {/* 4. When will I reach? */}
        <div className="journey-highlight-card">
          <div className="card-icon-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            <span className="highlight-card-title">When will I reach?</span>
          </div>
          <div className="highlight-main-val text-blue">
            {expectedTime}
          </div>
          <p className="highlight-subtitle">
            Destination: <strong>{destinationStation}</strong>
          </p>
        </div>

        {/* 5. Less crowded coach */}
        <div className="journey-highlight-card">
          <div className="card-icon-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
            <span className="highlight-card-title">Less crowded coach</span>
          </div>
          <div className="highlight-main-val text-brand">
            {recClass} <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)' }}>({recCoachId})</span>
          </div>
          <p className="highlight-subtitle">
            {recClassName}
          </p>
        </div>

        {/* 6. Weather Impact */}
        <div className="journey-highlight-card">
          <div className="card-icon-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"></path>
            </svg>
            <span className="highlight-card-title">Is weather affecting it?</span>
          </div>
          <div className={`highlight-main-val ${weatherIsImpacted ? 'text-amber' : 'text-green'}`} style={{ fontSize: '1.25rem' }}>
            {weatherIsImpacted ? 'Weather Alert' : 'Weather Normal'}
          </div>
          <p className="highlight-subtitle">
            {weatherIsImpacted ? 'Minor speed restrictions' : 'Clear conditions on route'}
          </p>
        </div>
      </div>
    </section>
  );
}
