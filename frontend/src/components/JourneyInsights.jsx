import React from 'react';

export default function JourneyInsights({
  data,
  activeBudgetFilter = 'ALL',
  onBudgetFilterChange
}) {
  if (!data) return null;

  const delayData = data.delay_prediction || {};
  const etaData = data.dynamic_eta || {};
  const weatherData = data.weather || {};
  const crowdData = data.crowd || {};
  const recData = data.compartment_recommendation || {};
  const train = data.train || {};

  // 1. Predicted Delay
  const predictedDelay = delayData.predicted_delay_minutes ?? 0;
  const delayText = predictedDelay <= 10 ? 'On Time' : `+${Math.round(predictedDelay)} min`;
  const delayDetail = predictedDelay <= 10 
    ? 'Running on schedule along current corridor' 
    : `Expected arrival delay at ${delayData.station_name || 'station'}`;

  // 2. Estimated Arrival
  const arrivalTime = etaData.destination_dynamic_eta || '11:29 AM';
  const arrivalDetail = `Terminus: ${train.destination_name || etaData.destination || 'New Delhi'}`;

  // 3. Weather Risk
  const weatherTemp = weatherData.temperature_c != null ? `${Math.round(weatherData.temperature_c)}°C` : '28°C';
  const weatherAdj = weatherData.weather_delay_adjustment_min || 0;
  const weatherRisk = weatherAdj > 10 ? 'High' : (weatherAdj > 3 ? 'Moderate' : 'Low');
  const weatherDetail = `${weatherTemp} · Clear track visibility`;

  // 4. Crowd Level
  const crowdLevel = crowdData.overall_crowd_level || recData.crowd_level || 'Moderate';
  const crowdPercent = Math.round(crowdData.overall_occupancy_percent || recData.occupancy_percent || 54);
  const crowdDetail = `~${crowdPercent}% estimated passenger occupancy`;

  // 5. Journey Progress
  const stops = train.stops || [];
  const totalStops = stops.length || 20;
  const upcomingCount = etaData.upcoming_stops_count ?? (totalStops - 2);
  const passedStops = Math.max(1, totalStops - upcomingCount);
  const progressPercent = Math.round((passedStops / Math.max(1, totalStops)) * 100);
  const progressDetail = `Completed ${passedStops} of ${totalStops} corridor stations`;

  // 6. Smart Recommendation
  const recClass = recData.recommended_coach_or_class || '2A';
  const recCoachId = recData.recommended_coach_id || `${recClass}1`;
  const recTitle = `Consider ${recData.recommended_class_name || `AC ${recClass}`}`;
  const recDetail = `Coach ${recCoachId} is least crowded for this route`;

  return (
    <div className="journey-insights-container">
      {/* 6 Clean Compact Insight Cards */}
      <div className="insights-grid">
        {/* Card 1: Predicted Delay */}
        <div className="insight-card card">
          <div className="insight-card-top">
            <div className={`insight-icon-box ${predictedDelay > 20 ? 'amber' : 'green'}`}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
            </div>
            <span className="insight-label">Predicted Delay</span>
          </div>
          <div className={`insight-value ${predictedDelay > 20 ? 'text-amber' : 'text-green'}`}>
            {delayText}
          </div>
          <p className="insight-detail">{delayDetail}</p>
        </div>

        {/* Card 2: Estimated Arrival */}
        <div className="insight-card card">
          <div className="insight-card-top">
            <div className="insight-icon-box blue">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="16" y1="2" x2="16" y2="6"></line>
                <line x1="8" y1="2" x2="8" y2="6"></line>
                <line x1="3" y1="10" x2="21" y2="10"></line>
              </svg>
            </div>
            <span className="insight-label">Estimated Arrival</span>
          </div>
          <div className="insight-value text-blue">
            {arrivalTime}
          </div>
          <p className="insight-detail">{arrivalDetail}</p>
        </div>

        {/* Card 3: Weather Risk */}
        <div className="insight-card card">
          <div className="insight-card-top">
            <div className="insight-icon-box cyan">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"></path>
              </svg>
            </div>
            <span className="insight-label">Weather Risk</span>
          </div>
          <div className="insight-value text-cyan">
            {weatherRisk}
          </div>
          <p className="insight-detail">{weatherDetail}</p>
        </div>

        {/* Card 4: Crowd Level */}
        <div className="insight-card card">
          <div className="insight-card-top">
            <div className="insight-icon-box purple">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
            </div>
            <span className="insight-label">Crowd Level</span>
          </div>
          <div className="insight-value text-purple">
            {crowdLevel}
          </div>
          <p className="insight-detail">{crowdDetail}</p>
        </div>

        {/* Card 5: Journey Progress */}
        <div className="insight-card card">
          <div className="insight-card-top">
            <div className="insight-icon-box green">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <circle cx="12" cy="12" r="10"></circle>
                <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>
              </svg>
            </div>
            <span className="insight-label">Journey Progress</span>
          </div>
          <div className="insight-value text-green">
            {progressPercent}%
          </div>
          <div className="progress-bar-track">
            <div className="progress-bar-fill" style={{ width: `${progressPercent}%` }} />
          </div>
          <p className="insight-detail">{progressDetail}</p>
        </div>

        {/* Card 6: Smart Recommendation */}
        <div className="insight-card card">
          <div className="insight-card-top">
            <div className="insight-icon-box lime">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
              </svg>
            </div>
            <span className="insight-label">Smart Recommendation</span>
          </div>
          <div className="insight-value text-brand" style={{ fontSize: '1.25rem' }}>
            {recTitle}
          </div>
          <p className="insight-detail">{recDetail}</p>
        </div>
      </div>

      {/* Smart Coach Options & Budget Selector */}
      {recData.ranked_options && recData.ranked_options.length > 0 && (
        <div className="coach-options-card card">
          <div className="coach-card-header">
            <div>
              <h4 className="coach-section-title">Coach Density Breakdown</h4>
              <span className="coach-section-subtitle">Real-time estimated crowd levels per class</span>
            </div>

            <div className="budget-pills">
              {['ALL', 'AC', 'NON_AC'].map(filter => (
                <button
                  key={filter}
                  type="button"
                  className={`budget-filter-pill ${activeBudgetFilter === filter ? 'active' : ''}`}
                  onClick={() => onBudgetFilterChange && onBudgetFilterChange(filter)}
                >
                  {filter === 'NON_AC' ? 'Non-AC' : filter}
                </button>
              ))}
            </div>
          </div>

          <div className="coach-chips-grid">
            {recData.ranked_options.map((opt) => (
              <div key={opt.class_code} className={`coach-chip-item ${opt.class_code === recData.recommended_coach_or_class ? 'winning' : ''}`}>
                <div className="coach-chip-top">
                  <span className="coach-class-code">{opt.class_code}</span>
                  <span className={`crowd-pill ${opt.crowd_level.toLowerCase()}`}>{opt.crowd_level}</span>
                </div>
                <div className="coach-class-name">{opt.class_name}</div>
                <div className="coach-occupancy-bar">
                  <div className={`occupancy-fill ${opt.crowd_level.toLowerCase()}`} style={{ width: `${Math.round(opt.occupancy_percent)}%` }} />
                </div>
                <div className="coach-stats-line">
                  <span>{Math.round(opt.occupancy_percent)}% full</span>
                  <span>{opt.estimated_passengers}/{opt.estimated_capacity} seats</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
