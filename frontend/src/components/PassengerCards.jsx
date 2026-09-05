import React from 'react';
import RecommendationCard from './RecommendationCard';

export default function PassengerCards({
  weatherData,
  crowdData,
  recData,
  activeBudgetFilter,
  onBudgetFilterChange,
  stationCode
}) {
  // Simple weather interpretation
  const temp = weatherData?.temperature_c != null ? `${weatherData.temperature_c}°C` : '--';
  const desc = weatherData?.weather_description || 'Clear conditions';
  const delayAdj = weatherData?.weather_delay_adjustment_min || 0.0;
  const isFogOrRain = (weatherData?.weather_category || '').toUpperCase().includes('RAIN') || 
                      (weatherData?.weather_category || '').toUpperCase().includes('FOG') ||
                      (weatherData?.weather_category || '').toUpperCase().includes('STORM');

  let weatherHeadline = "Weather looks normal for travel today";
  let weatherSubtext = `Clear sky with comfortable temperature around ${temp}. No major weather delay expected.`;
  let weatherBadge = "green";

  if (delayAdj > 10.0 || isFogOrRain) {
    weatherHeadline = "Weather may cause minor delays";
    weatherSubtext = `${desc} detected at ${weatherData?.station_name || stationCode}. Rail speeds may be slightly reduced for safety.`;
    weatherBadge = "orange";
  }

  // Simple crowd interpretation
  const occupancyPct = crowdData?.overall_occupancy_percent ?? 0.0;
  let crowdStatus = "Comfortable (Low Crowd)";
  let crowdBadgeColor = "green";
  let crowdSubtext = "Plenty of nominal seating and space expected across compartments.";

  if (occupancyPct > 80.0) {
    crowdStatus = "Very Crowded";
    crowdBadgeColor = "red";
    crowdSubtext = "High passenger volume expected. Boarding early is strongly recommended.";
  } else if (occupancyPct > 50.0) {
    crowdStatus = "Moderate Crowd";
    crowdBadgeColor = "orange";
    crowdSubtext = "Medium passenger load. Some coaches are more comfortable than others.";
  }

  return (
    <div className="passenger-cards-grid">
      {/* 1. Passenger Weather Advisory Card */}
      <div className="card passenger-info-card">
        <div className="card-header">
          <h3 className="card-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"></path>
            </svg>
            Is weather affecting my train?
          </h3>
          <span className={`badge-status ${weatherBadge}`}>
            {weatherBadge === 'green' ? 'CLEAR TRACKS' : 'WEATHER ALERT'}
          </span>
        </div>

        <div className="passenger-card-body">
          <h4 className="passenger-card-headline">{weatherHeadline}</h4>
          <p className="passenger-card-desc">{weatherSubtext}</p>

          <div className="passenger-weather-pills">
            <span className="weather-pill">🌡 {temp}</span>
            <span className="weather-pill">💧 {weatherData?.relative_humidity_pct ?? 45}% Humidity</span>
            <span className="weather-pill">👁 {weatherData?.visibility_m ? `${(weatherData.visibility_m/1000).toFixed(1)} km Visibility` : 'Good Visibility'}</span>
          </div>
        </div>
      </div>

      {/* 2. Passenger Crowd & Less Crowded Coach Card */}
      <div className="card passenger-info-card">
        <div className="card-header">
          <h3 className="card-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
              <path d="M22 21v-2a4 4 0 0 0-3-3.87"></path>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
            How crowded is my train?
          </h3>
          <span className={`badge-status ${crowdBadgeColor}`}>
            {crowdStatus}
          </span>
        </div>

        <div className="passenger-card-body">
          <div style={{ display: 'inline-block', background: 'rgba(245, 158, 11, 0.15)', color: 'var(--accent-amber)', border: '1px solid rgba(245, 158, 11, 0.3)', padding: '0.15rem 0.5rem', borderRadius: 'var(--radius-sm)', fontSize: '0.68rem', fontWeight: '700', marginBottom: '0.5rem', letterSpacing: '0.04em' }}>
            SYNTHETIC PROTOTYPE DATA
          </div>

          <p className="passenger-card-desc" style={{ marginBottom: '0.75rem' }}>
            {crowdSubtext}
          </p>

          {/* Coach filter and recommendation component */}
          <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '0.75rem' }}>
            <div style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
              Choose your travel class to find the less crowded coach:
            </div>
            <RecommendationCard
              recData={recData}
              crowdData={crowdData}
              activeFilter={activeBudgetFilter}
              onFilterChange={onBudgetFilterChange}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
